import os
from configparser import ConfigParser
from datetime import datetime
import pandas as pd


def parsers():
    c_parser = ConfigParser()
    c_parser.read("ss_ner.ini")
    return c_parser


def store_insert_dfs(grouped_df):
    g_df_cols = grouped_df.columns.tolist()
    last_tag_count = int(g_df_cols[-1][-1])  # 얼마나 많이 token 분리를 작업자가 했는지 파악 (tag 8)
    insert_tag_dict = {i: "" for i in range(2, last_tag_count + 1)}
    for i in range(2, last_tag_count + 1):
        cols_list = grouped_df.columns.tolist()[0:2]
        tok_n = "Tokens " + str(i)
        tag_n = "Tags " + str(i)

        cols_list.append(tok_n)
        cols_list.append(tag_n)
        # 각 sid 의 df 에서 sid, text, token n, tag n 형태로 만들어준다
        g_df_to_insert = grouped_df[cols_list]
        # tag 가 있는지 확인
        g_df_to_insert = g_df_to_insert[g_df_to_insert[cols_list[-2]] != ""]
        if len(g_df_to_insert) != 0:
            idx_df = []
            idx_df.append(g_df_to_insert.index[0])
            idx_df.append(g_df_to_insert)
            insert_tag_dict[i] = idx_df
        to_del = []
        for k, v in insert_tag_dict.items():
            if v == "":
                to_del.append(k)
        for del_k in to_del:
            del insert_tag_dict[del_k]
        sorted_insert_dict = dict(
            sorted(insert_tag_dict.items(), key=lambda item: (item[1][0], item[0]))
        )
        sorted_insert_dict = dict((k, v[1]) for k, v in sorted_insert_dict.items())
    return sorted_insert_dict


def insert_row(idx, df, df_insert):
    dfA = df.loc[
        : idx - 1,
    ]
    dfB = df.loc[
        idx:,
    ]

    df = dfA.append(df_insert).append(dfB).reset_index(drop=True)

    return df


def insert_into_grouped_df(og_df, stored_dict, count):
    # 나중에 insert 할때에 df index 에 추가해 줄 카운트
    for tdf in stored_dict:
        insert_df = stored_dict.get(tdf)
        if len(insert_df) > 0:
            change = insert_df.columns[-2:]  # 현재는 마지막 2 개 col name = Token n , Tags n
            insert_df = insert_df.rename(
                columns={change[0]: "token", change[1]: "Tags 1"}
            )
            og_df = insert_row(insert_df.index[0] + count, og_df, insert_df)
            count += 1
    return og_df, count


def realign_token_df(df):
    fixed_df = pd.DataFrame()
    grouped = df.groupby(by=["SID"], sort=False)
    for g in grouped:
        g_df = g[1]
        g_df = g_df.reset_index(drop=True)
        idx_count = 1
        new_df = g_df.copy()
        for r in g_df.index.tolist():
            row = g_df.loc[[r]]
            insert_dfs_dict = store_insert_dfs(row)
            new_df, idx_count = insert_into_grouped_df(
                new_df, insert_dfs_dict, idx_count
            )
        new_df = new_df.drop(columns=new_df.columns[4:])
        fixed_df = fixed_df.append(new_df, ignore_index=True)
    fixed_df.rename(columns={"token": "Tokens", "Tags 1": "Tags"}, inplace=True)
    fixed_df = fixed_df.astype(str)
    return fixed_df


def conditions_df(df):  # adding conditions to deal with span_tags
    # shift tags up once
    df["shifted_tags_up"] = df["Tags"].shift(-1)
    # shift tags down once
    df["shifted_tags_down"] = df["Tags"].shift(1)
    df["tags_bool"] = (
        df["Tags"] != ""
    )  # dealing with empty string == empty string error
    df["span_tags"] = df.eval(
        "Tags != '' and (Tags == shifted_tags_up or Tags == shifted_tags_down)"
    )
    # not empty but not span = single tag
    df["single_tags"] = df.eval("(tags_bool == True and span_tags== False)")
    return df


def set_initial_tracker(df, idx, sentence, alr_track):
    if alr_track != 0 and alr_track != -1:
        return alr_track
    initial_tracker = 0
    check_idx_list = df.index.tolist()
    check_range = check_idx_list.index(idx)
    if check_range <= 2:  # 5
        check_beg_idx = 0
    else:
        check_beg_idx = check_range - 3
    for i in range(check_beg_idx, check_range):
        try:
            check_token = df["Tokens"].loc[check_idx_list[i]]
            # print( f"{i}: {check_token}")
        except:
            df.to_excel(r"/Users/jamessong/Desktop/IO/in/ss/topics/index_error.xlsx")
            raise ValueError("index?")
        initial_tracker = sentence.find(check_token, initial_tracker)
        # print(f"{check_token}  {initial_tracker}")
    return initial_tracker


def change_token_find(sid, tok, loc, sentence, tracker):
    tok = ("").join(tok.split())
    if loc == -1:
        check_time = tok.count(":")
        if check_time > 1:
            new_token = tok[: tok.rfind(":")]
            new_found_loc = sentence.find(new_token, tracker)
            return change_token_find(sid, new_token, new_found_loc, sentence, tracker)

        elif check_time == 1 and len(tok) == 5 and tok.startswith("0"):
            new_token = tok[1:]
            new_found_loc = sentence.find(new_token, tracker)
            return change_token_find(sid, new_token, new_found_loc, sentence, tracker)

        elif len(tok) > 14 and tok.startswith("2"):
            new_token = tok[: tok.find(" ")]
            if new_token.count("-") > 1:
                new_token = new_token.replace("-", "/")
            new_found_loc = sentence.find(new_token, tracker)
            return change_token_find(sid, new_token, new_found_loc, sentence, tracker)

        else:
            tok = ""
            loc = -1
            return tok, loc
    else:
        return tok, loc


def single_tag_compiler(df, sidx, tag_dict, og_dict, tracker, initial):
    passer = True
    final_sid = df["SID"].iloc[0]
    og_sentence = og_dict.get(final_sid)
    # saving the sentence of each df through the loop
    token = df["Tokens"].loc[sidx]  # find token
    tag = tag_dict.get(df["Tags"].loc[sidx])  # change korean tag to ss tagset
    if tag is None:
        passer = False
        return final_sid, str(df["Tokens"].loc[sidx]), og_dict, tracker, passer
    s_tag = "<" + tag + ">"
    e_tag = "</" + tag + ">"
    if og_sentence[tracker:].count(token) > 1:
        tracker = set_initial_tracker(df, sidx, og_sentence, tracker)
    found_loc = og_sentence.find(token, tracker)
    token, found_loc = change_token_find(
        final_sid, token, found_loc, og_sentence, tracker
    )
    tracker = found_loc
    if token == "" or found_loc == -1:
        passer = False
        return final_sid, str(df["Tokens"].loc[sidx]), og_dict, tracker, passer
    final_sentence = (
        og_sentence[:found_loc]
        + s_tag
        + token
        + e_tag
        + og_sentence[(found_loc + len(token)) :]
    )  # locate the token, insert the beg/end tag and join the rest of the sentence
    og_dict[final_sid] = final_sentence
    tracker = tracker + len(s_tag) + len(e_tag) + len(token)
    # change the original sentence to fixed sentence
    return final_sid, token, og_dict, tracker, passer


def consecutive_ranges(ind_list):  # finds indexes where tags are continuous
    gaps = [[s, e] for s, e in zip(ind_list, ind_list[1:]) if s + 1 < e]
    edges = iter(ind_list[:1] + sum(gaps, []) + ind_list[-1:])
    return list(zip(edges, edges))


def range_fixer(
    df, consc_range
):  # fixes the range from above function if the tags are different
    new_range = []
    for st, en in consc_range:
        check_tag = df["Tags"].loc[st]
        check_st = st
        while check_st <= en:
            compare_tag = df["Tags"].loc[check_st]
            if str(check_tag) == str(compare_tag):
                range_tuple = (st, check_st)
            else:
                new_range.append(range_tuple)
                range_tuple = (check_st, en)
                break
            check_st += 1
        new_range.append(range_tuple)
    return new_range


def final_check_range(df, fixed_rng):
    prev_rng = fixed_rng
    while True:
        check_rng = range_fixer(df, fixed_rng)
        if prev_rng == check_rng:
            return prev_rng
        else:
            return final_check_range(df, check_rng)


def multi_tag_compiler(df, tag_range, tag_dict, og_dict, tracker, initial):
    passer = True
    beg, end = tag_range  # range is in list(tuple) format
    final_sid = df["SID"].iloc[0]
    og_sentence = og_dict.get(final_sid)

    beg_token = df["Tokens"].loc[beg]

    end_token = df["Tokens"].loc[end]

    if og_sentence[tracker:].count(beg_token) > 1:
        tracker = set_initial_tracker(df, beg, og_sentence, tracker)
    beg_token_loc = og_sentence.find(beg_token, tracker)
    # print(f"b4 {beg_token} :{beg_token_loc}")
    # find the last token of the span_tag
    end_token_loc = og_sentence.find(end_token, beg_token_loc + 1)
    # 못 찾으면 에러
    beg_token, beg_token_loc = change_token_find(
        final_sid, beg_token, beg_token_loc, og_sentence, tracker
    )
    # print(f"after {beg_token} :{beg_token_loc}")
    end_token, end_token_loc = change_token_find(
        final_sid, end_token, end_token_loc, og_sentence, tracker
    )
    # print(f"{beg_token}:{beg_token_loc}|{end_token}:{end_token_loc}|{tracker}")
    if beg_token == "" or end_token == "" or beg_token_loc == -1 or end_token_loc == -1:
        passer = False
        tokens = (
            "beg: "
            + str(df["Tokens"].loc[beg])
            + " "
            + "end: "
            + str(df["Tokens"].loc[end])
        )
        return final_sid, tokens, og_dict, tracker, passer

    end_token_loc = end_token_loc + len(end_token)
    tracker = beg_token_loc
    token = og_sentence[beg_token_loc:end_token_loc]
    tag = tag_dict.get(df["Tags"].loc[beg])
    if tag is None:
        passer = False
        return (
            final_sid,
            str(df["Tokens"].loc[beg]) + " or " + str(df["Tokens"].loc[end]),
            og_dict,
            tracker,
            passer,
        )

    s_tag = "<" + tag + ">"
    e_tag = "</" + tag + ">"
    final_sentence = (
        og_sentence[:beg_token_loc]
        + s_tag
        + token
        + e_tag
        + og_sentence[end_token_loc:]
    )
    tracker = tracker + len(s_tag) + len(e_tag) + len(token)
    og_dict[final_sid] = final_sentence
    return final_sid, token, og_dict, tracker, passer


def combine_single_multi_tags(df):
    single_idx = df[df["single_tags"]].index.tolist()
    tag_s_type = ["single" for _ in single_idx]
    multi_idx = df[df["span_tags"]].index.tolist()

    range_index = consecutive_ranges(multi_idx)
    fixed_range = range_fixer(df, range_index)
    final_range = final_check_range(df, fixed_range)
    tag_m_type = [["multi", r] for r in final_range]
    # 기존 multi_index 와 zip 할시 mismatch -> range 시작을 딕셔너리 key 로 ovewrite
    multi_idx = [b for b, e in final_range]
    single_idx.extend(multi_idx)
    tag_s_type.extend(tag_m_type)
    total_idx_dict = dict(zip(single_idx, tag_s_type))
    # index 순서대로 작업용 sort
    total_idx_od = dict(sorted(total_idx_dict.items()))
    return total_idx_od


def tag_compiler(fixed_df, tags_dict, og_text_dict):
    need_revise = []
    gb = fixed_df.groupby("SID", sort=False)
    tid = [gb.get_group(x) for x in gb.groups]

    for t in tid:
        tracking = 0
        # first loop = SID 1, second loop SID2 so on
        # group by text from the tokenized file
        over_write_sid = t["SID"].iloc[0]
        t["text"] = og_text_dict.get(over_write_sid)
        cgb = t.groupby("text", sort=False)
        sid = [cgb.get_group(y) for y in cgb.groups]

        for n, s in enumerate(sid):
            s = conditions_df(s)
            od = combine_single_multi_tags(s)
            if len(od) > 0:
                for idx in od:
                    check = []
                    tag_type = od.get(idx)
                    if tag_type == "single":
                        (
                            f_sid,
                            check_tok,
                            og_text_dict,
                            tracking,
                            passfail,
                        ) = single_tag_compiler(
                            s, idx, tags_dict, og_text_dict, tracking, n
                        )
                        if passfail == False:
                            check.append(f_sid)
                            check.append(check_tok)
                            need_revise.append(check)
                    else:
                        multi_range = tag_type[-1]
                        (
                            f_sid,
                            check_tok,
                            og_text_dict,
                            tracking,
                            passfail,
                        ) = multi_tag_compiler(
                            s, multi_range, tags_dict, og_text_dict, tracking, n
                        )
                        if passfail == False:
                            check.append(f_sid)
                            check.append(check_tok)
                            need_revise.append(check)
    return og_text_dict, need_revise


def parse_infos(info_sid):
    recipient = ""
    struct = ""
    info = info_sid[: info_sid.find("_")]
    sentence_id = info_sid[info_sid.find("_") + 1 :]
    topic_id = info_sid[info_sid.find("_") + 1 : info_sid.rfind("_")]
    message_type = info[0]
    struct_type = info[1]
    recip_type = info[2]
    if message_type == "C":
        recipient = ""
        struct = "Chatting Unstructured"
    elif message_type == "N":
        if recip_type == "M":
            recipient = "Multiple"
        elif recip_type == "S":
            recipient = "Single"
        else:
            print(info_sid)
            raise ValueError("SID INFO wrong Format")

        if struct_type == "S":
            struct = "Structured"
        elif struct_type == "U":
            struct = "Unstructured"
        else:
            print(info_sid)
            raise ValueError("SID INFO wrong Format")
    else:
        print(info_sid)
        raise ValueError("SID INFO wrong Format")
    return recipient, struct, sentence_id, topic_id


def make_delivery_df(tagged_dict, topic_dict):
    final_data = []
    for k in tagged_dict:
        row_data = []
        tagged_text = tagged_dict.get(k)
        st, recip, sid, tid = parse_infos(k)

        topic = topic_dict.get("Topic " + tid)
        final_topic = f"#CSS-01 ({topic})"
        final_text = final_topic + "\n" + tagged_text
        row_data.append(sid)
        row_data.append(recip)
        row_data.append(st)
        row_data.append(final_text)
        final_data.append(row_data)
    final_df = pd.DataFrame(
        data=final_data, columns=["Topic_SID", "Recipients", "Structural", "Content"]
    )
    return final_df


if __name__ == "__main__":
    out_name = datetime.strftime(datetime.now(), "%m%d")
    out_name = out_name + "_notice_data_tagged.xlsx"
    configs = parsers()
    tagged_dir = configs.get("PATHS", "SRL_tagged_file")
    topics_set_dir = configs.get("PATHS", "topics_set_file")
    og_dir = configs.get("PATHS", "original_file")
    out_dir = configs.get("PATHS", "delivery")
    tags_dict = {
        "시작 시간": "start_time",
        "종료 시간": "end_time",
        "시작 날짜": "start_date",
        "종료 날짜": "end_date",
        "약속 장소": "location",
        "제목": "title",
    }
    topics_set_df = pd.read_excel(topics_set_dir, dtype=str)
    topics_set_dict = dict(
        zip(topics_set_df["Topic Number"], topics_set_df["세부 Topic"])
    )
    token_df = pd.read_excel(tagged_dir)
    print(tagged_dir)
    og_content = pd.read_excel(og_dir)

    token_df = token_df.fillna("")
    token_df = token_df.replace("해당사항 없음", "")
    fixed_token_df = realign_token_df(token_df)

    og_content = og_content[
        og_content["Final_SID"].isin(fixed_token_df["SID"].drop_duplicates().tolist())
    ]
    sid_og_text = dict(zip(og_content.Final_SID, og_content.Content))
    final_tagged_dict, revision = tag_compiler(fixed_token_df, tags_dict, sid_og_text)
    revision_df = pd.DataFrame(data=revision, columns=["Topic_SID", "tokens"])
    revision_df.to_excel(os.path.join(out_dir, "failed_sid_1.xlsx"), index=False)
    delivery_df = make_delivery_df(final_tagged_dict, topics_set_dict)
    delivery_df.to_excel(os.path.join(out_dir, out_name), index=False)
