import os
import json
import random
from configparser import ConfigParser
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup


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
        ref_n = "Refer Value " + str(i)
        cols_list.append(tok_n)
        cols_list.append(tag_n)
        cols_list.append(ref_n)
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
            change = insert_df.columns[-3:]  # 현재는 마지막 2 개 col name = Token n , Tags n
            insert_df = insert_df.rename(
                columns={
                    change[0]: "token",
                    change[1]: "Tags 1",
                    change[-1]: "Reference Value 1",
                }
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
        new_df = new_df.drop(columns=new_df.columns[5:])
        fixed_df = fixed_df.append(new_df, ignore_index=True)
    fixed_df.rename(
        columns={"token": "Tokens", "Tags 1": "Tags", "Refer Value 1": "Ref_Val"},
        inplace=True,
    )
    fixed_df = fixed_df.astype(str)
    return fixed_df


def conditions_df(df):  # adding conditions to deal with span_tags
    # shift tags up once
    df["shifted_tags_up"] = df["Tags"].shift(-1)
    df["shifted_refs_up"] = df["Ref_Val"].shift(-1)
    # shift tags down once
    df["shifted_tags_down"] = df["Tags"].shift(1)
    df["shifted_refs_down"] = df["Ref_Val"].shift(1)

    df["tags_bool"] = (
        df["Tags"] != ""
    )  # dealing with empty string == empty string error
    df["span_tags"] = df.eval(
        "Tags != '' and (Tags == shifted_tags_up or Tags == shifted_tags_down) and (Ref_Val == shifted_refs_up or Ref_Val == shifted_refs_down)"
    )
    # not empty but not span = single tag
    df["single_tags"] = df.eval("tags_bool == True and span_tags== False")

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
    tag_m_type = [["multi", r] for r in fixed_range]
    # 기존 multi_index 와 zip 할시 mismatch -> range 시작을 딕셔너리 key 로 ovewrite
    multi_idx = [b for b, e in fixed_range]
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
        # print(og_text_dict)
        tracking = 0
        # first loop = SID 1, second loop SID2 so on
        # group by text from the tokenized file
        cgb = t.groupby("text", sort=False)
        sid = [cgb.get_group(y) for y in cgb.groups]

        for n, s in enumerate(sid):
            s = conditions_df(s)
            od = combine_single_multi_tags(s)
            # print(od)
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


def base_delivery_df_chat(f, og_ss_df, final_tagged):
    f = f[: f.rfind(".")]
    f = f[-7:]
    f = f.replace("_", "-")
    f = f"DIX-{f}"
    final_df = pd.DataFrame()
    sid = []
    cat = []
    meta_store = []
    time = []
    user = []
    content = []
    og_ss_df = og_ss_df.set_index(["SID"])

    for n, k in enumerate(final_tagged):
        og_sid = k[:7]
        meta_df = og_ss_df.loc[og_sid]
        meta_data = meta_df.to_dict(orient="records")
        meta = meta_data[n]
        if n == 0:
            sid.append(f)
            cat.append("dialogue")
            content.append(final_tagged.get(k))
            time.append(meta.get("Time"))
            user.append(meta.get("User"))
            for mn, mk in enumerate(meta):
                if mn != 0 and mn != 1:
                    meta_store.append(f"{mk}: {meta.get(mk)}")
        else:
            sid.append("")
            cat.append("")
            time.append(meta.get("Time"))
            user.append(meta.get("User"))
            content.append(final_tagged.get(k))
    sid.append("")
    sid.append("")
    sid.append("")
    sid.append("")
    cat.append("goal")
    cat.append("users-info")
    cat.append("")
    cat.append("")
    time.append("ground-truth")
    time.append("users-info")
    time.append("")
    time.append("")
    user.append("final")
    user.append(user[-3])
    user.append(user[-3])
    user.append("relation-info")
    content.append("ground-truth")
    content.append("users-info")
    content.append("users-info")
    content.append("users-info")

    final_df["Dialogue num"] = sid
    final_df["Cateogry"] = cat
    final_df["Time"] = time
    final_df["User"] = user
    final_df["Utterance"] = content
    final_df["State"] = ""
    return f, final_df, meta_store


def check_end_confirm(f, df, confirm_list, fixed_files_list):
    check_last_confirm = df[0:-4]
    to_append_after = df[-4:]
    user = check_last_confirm["User"].loc[len(check_last_confirm) - 2]
    time = check_last_confirm["Time"].loc[len(check_last_confirm) - 1]

    conversation = check_last_confirm["Utterance"].tolist()
    for c in reversed(conversation):
        soup = BeautifulSoup(c, "html.parser")
        tags_in_line = [tag.name for tag in soup.find_all()]
        if len(tags_in_line) > 0:
            if c.find("confirm") == -1:
                final_row = [["", "", time, user, random.choice(confirm_list), ""]]
                final_row_df = pd.DataFrame(
                    data=final_row, columns=check_last_confirm.columns
                )
                check_last_confirm = check_last_confirm.append(
                    final_row_df, ignore_index=True
                )
                fixed_df = check_last_confirm.append(to_append_after, ignore_index=True)
                fixed_files_list.append(f)
                return fixed_df, fixed_files_list
            elif c.find("confirm") != -1 and len(tags_in_line) > 1:
                final_row = [["", "", time, user, random.choice(confirm_list), ""]]
                final_row_df = pd.DataFrame(
                    data=final_row, columns=check_last_confirm.columns
                )
                check_last_confirm = check_last_confirm.append(
                    final_row_df, ignore_index=True
                )
                fixed_df = check_last_confirm.append(to_append_after, ignore_index=True)
                fixed_files_list.append(f)
                return fixed_df, fixed_files_list
            else:
                return df, fixed_files_list


def sort_relation(rel_meta):
    final_rel_dict = {"relation-info": []}
    rel_meta = list(map(lambda s: s.split(":"), rel_meta))
    prev_id = ""
    for r, v in rel_meta:
        if "_" in r and "name" not in r:
            curr_id = r[: r.find("_")]
            if curr_id != prev_id:
                final_rel_dict[curr_id] = list()
                user_list = final_rel_dict.get(curr_id)
                final_r = r[r.find("_") + 1 :] + ":"
                user_list.append(final_r + str(v))
            else:
                if v == " M":
                    v = " male"
                elif v == " F":
                    v = " female"
                user_list = final_rel_dict.get(curr_id)
                final_r = r[r.find("_") + 1 :] + ":"
                user_list.append(final_r + str(v))
                final_rel_dict[curr_id] = user_list
            prev_id = curr_id
        else:
            final_r = r + ":"
            if "freq" in r:
                final_r = "how-often-meet:"
            user_list = final_rel_dict.get("relation-info")

            user_list.append(final_r + str(v))

    return final_rel_dict


def merge_confirm_tags(confirm_tags_list, final_col):
    confirm_tags_list.insert(0, dict())
    for idx, c_dict in enumerate(confirm_tags_list):
        if len(c_dict) == 0:
            continue
        c_tagged_token = c_dict.get("confirm")
        to_concat = f",\nconfirm: {c_tagged_token}"
        adding_confirm = final_col[idx]
        if adding_confirm == "":
            continue
        adding_confirm += to_concat
        final_col[idx] = adding_confirm
    return final_col


def confirm_logic(base_deliv_df, meta_store):
    rel_dict = sort_relation(meta_store)
    final_dict_col = []
    confirm_tags_to_merge = []
    confirm_tags_dict = dict()
    confirm_dict = dict()
    unconfirm_dict = dict()
    for line in base_deliv_df["Utterance"].tolist()[:-4]:
        if line == "" or line.startswith("relation"):
            continue
        soup = BeautifulSoup(line, "html.parser")
        tags_in_line = [tag.name for tag in soup.find_all()]
        prev_loc = 0
        for tag in tags_in_line:
            if tag == "confirm":
                for u in unconfirm_dict:
                    confirm_dict[u] = unconfirm_dict.get(u)
                unconfirm_dict = dict()

                first_loc = line.find(tag, prev_loc)
                second_loc = line.find(tag, first_loc + 1)
                token_tagged = line[first_loc + len(tag) + 1 : second_loc - 2]
                prev_loc = second_loc + len(tag) + 1
                confirm_tags_dict["confirm"] = token_tagged
            else:
                if tag == "co-reference":
                    continue
                    # need to add support for co-refernece
                    # depending on ss response
                first_loc = line.find(tag, prev_loc)
                second_loc = line.find(tag, first_loc + 1)
                token_tagged = line[first_loc + len(tag) + 1 : second_loc - 2]
                prev_loc = second_loc + len(tag) + 1
                unconfirm_dict[tag] = token_tagged
        confirm_tags_to_merge.append(confirm_tags_dict.copy())
        if len(confirm_dict) > 0:
            final_dict_col.append(
                (",\n").join([f"{k}: {v}" for k, v in confirm_dict.copy().items()])
            )
        else:
            final_dict_col.append("")
    final_dict_col.append(final_dict_col[-1])
    final_dict_col.append((",\n").join(rel_dict.get("A")))
    final_dict_col.append((",\n").join(rel_dict.get("B")))
    final_dict_col.append((",\n").join(rel_dict.get("relation-info")))

    final_dict_col = merge_confirm_tags(confirm_tags_to_merge, final_dict_col)
    base_deliv_df["State"] = final_dict_col
    return base_deliv_df


def prep_excel_for_json(excel_df, tokenized_text_df):
    og_token_texts = tokenized_text_df["text"].tolist()
    og_token_texts.append("")
    og_token_texts.append("")

    excel_df["og_text"] = og_token_texts
    col_names = excel_df.columns.tolist()
    rearr_col_names = col_names[:3]
    rearr_col_names.append(col_names[-1])
    rearr_col_names.extend(col_names[3:-1])
    excel_df = excel_df[rearr_col_names]
    excel_df = excel_df.rename(
        columns={
            excel_df.columns[2]: "role",
            excel_df.columns[3]: "text",
            excel_df.columns[4]: "tagged_text",
            excel_df.columns[5]: "book",
        }
    )
    return excel_df


def json_goal(excel_df):
    goal = excel_df["text"].loc[len(excel_df) - 2]
    goal_dict = {"css": {"book": goal}}
    return goal_dict


def prepare_log(excel_df):
    all_log = excel_df[excel_df.columns[2:5]].to_dict(orient="records")
    all_log = all_log[:-2]
    log_arr_dict = (
        []
    )  # each row = role: name, text: og_text, tagged_text: tagged, metadata: css: book
    for log in all_log:
        log_arr_dict.append(log)
    return log_arr_dict


def organize_references_to_search(fixed_tok_df, og_sentence):
    ref_tok_val = fixed_tok_df[fixed_tok_df["text"] == og_sentence][
        fixed_tok_df["Tags"] == "참조"
    ]
    ref_tok_list = list(map(list, zip(ref_tok_val.Tokens, ref_tok_val.Ref_Val)))
    for rn, ref_tok in enumerate(ref_tok_list):
        change_to_list = []
        if ref_tok[1].find("|") != -1:
            change_to_list = ref_tok[1].split("|")
        else:
            change_to_list.append(ref_tok[1])
        ref_tok_list[rn][1] = change_to_list
    return ref_tok_list


def reverse_traverse_refs(fixed_tok_df, ref_tok_list, og_sentence):
    text_list = fixed_tok_df.text.tolist()
    upto_confirm_idx = text_list.index(og_sentence)
    upto_confirm_df = fixed_tok_df[:upto_confirm_idx]
    upto_confirm_df = upto_confirm_df.iloc[::-1]
    tok_tag_ref = list(zip(upto_confirm_df["Tokens"], upto_confirm_df["Tags"]))
    co_ref = []
    for r in ref_tok_list:
        ref = r[0]
        ref_vals = r[1]
        co_ref_dict = {"indicator": ref, "target-info": ""}
        target_co_ref = []
        for ref_val in ref_vals:
            # print(ref_val)
            target_co_ref_dict = dict()
            for og_token, og_tag in tok_tag_ref:
                if og_token == ref_val and og_tag != "":
                    target_co_ref_dict["reference-tag"] = chat_tags_dict.get(og_tag)
                    target_co_ref_dict["reference-value"] = og_token
                    # print(target_co_ref_dict)
                    target_co_ref.append(target_co_ref_dict)
                    break
        co_ref_dict["target-info"] = target_co_ref
        co_ref.append(co_ref_dict)
    return co_ref


def json_log(excel_df, fixed_tok_df):
    log_arr_dict = prepare_log(excel_df)
    for n, booking in enumerate(excel_df["book"][:-2]):
        metadata_final = {"css": {"book": {}}}
        if booking == "":
            log_arr_dict[n]["metadata"] = metadata_final

        else:
            tagged_sentence = excel_df["tagged_text"].loc[n]
            if tagged_sentence.find("co-reference") != -1:
                original_sentence = excel_df["text"].loc[n]
                # print(original_sentence)
                ref_tag_list = organize_references_to_search(
                    fixed_tok_df, original_sentence
                )
                co_ref = reverse_traverse_refs(
                    fixed_tok_df, ref_tag_list, original_sentence
                )
                metadata_final["css"]["book"]["co-reference"] = co_ref
            prep_for_dict = booking.split("\n")
            final_prep = [p.split(":") for p in prep_for_dict]
            for kv in final_prep:
                k = kv[0]
                v = kv[1]
                v = (" ").join(v.split())
                metadata_final["css"]["book"][k] = v
            log_arr_dict[n]["metadata"] = metadata_final
    return log_arr_dict


def json_rel(excel_df):
    rel_info = excel_df["tagged_text"].loc[len(excel_df) - 1]
    # print(excel_df["tagged_text"])
    rel_info_split = rel_info.split("\n")
    # print(rel_info_split)
    user_dict = dict()
    for r in rel_info_split:
        if r.startswith("relation"):
            relationship = r
        elif r.startswith("frequency"):
            freq = r
        elif r.startswith("A_name"):
            a_name = r
        elif r.startswith("A_age"):
            a_age = r
        elif r.startswith("A_gender"):
            a_gend = r
        elif r.startswith("A_hometown"):
            a_home = r
        elif r.startswith("A_residence"):
            a_loc = r
        elif r.startswith("B_name"):
            b_name = r
        elif r.startswith("B_age"):
            b_age = r
        elif r.startswith("B_gender"):
            b_gend = r
        elif r.startswith("B_hometown"):
            b_home = r
        elif r.startswith("B_residence"):
            b_loc = r
        else:
            pass

    each_user_dict = dict()
    each_user_dict["age"] = a_age
    each_user_dict["gender"] = a_gend
    each_user_dict["hometown"] = a_home
    each_user_dict["residence"] = a_loc
    user_dict[a_name] = each_user_dict

    each_user_dict["age"] = b_age
    each_user_dict["gender"] = b_gend
    each_user_dict["hometown"] = b_home
    each_user_dict["residence"] = b_loc
    user_dict[b_name] = each_user_dict

    rel_dict = dict()
    rel_dict["relation"] = relationship
    rel_dict["how-often-meet"] = freq
    user_dict["relation-info"] = rel_dict
    return user_dict


def final_json(excel_df, tokenized_text_df, fixed_tok_df, final_json):
    # final_json = dict()
    final_sid = excel_df[excel_df.columns[0]].loc[0]
    excel_df = prep_excel_for_json(excel_df, tokenized_text_df)
    goal_dict = json_goal(excel_df)
    log_dict = json_log(excel_df, fixed_tok_df)
    users_info_dict = json_rel(excel_df)
    final_json[final_sid] = dict()
    final_json[final_sid]["goal"] = goal_dict
    final_json[final_sid]["log"] = log_dict
    final_json[final_sid]["user-info"] = users_info_dict
    json_to_write = json.dumps(final_json, ensure_ascii=False)
    return json_to_write


if __name__ == "__main__":
    out_name = datetime.strftime(datetime.now(), "%m%d")
    # out_name_json = out_name + "_notice_data_tagged.json"
    out_name_confirms = out_name + "_confirms_added.xlsx"
    out_name = out_name + "_chatting_data_tagged.xlsx"
    configs = parsers()
    og_dir = configs.get("PATHS", "og_file_chat")
    tagged_folder = configs.get("PATHS", "SRL_chat_tagged_folder")
    chat_set_dir = configs.get("PATHS", "chat_set_file")
    confirms_dir = configs.get("PATHS", "confirms")
    out_dir = configs.get("PATHS", "delivery")

    chat_tags = pd.read_excel(chat_set_dir)
    chat_tags = chat_tags.fillna("")
    chat_tags_dict = dict(zip(chat_tags.Total, chat_tags.Slots))

    confirms_excel = pd.read_excel(confirms_dir)
    confirms_list = confirms_excel["confirm"].tolist()
    og_df1 = pd.read_excel(og_dir)
    # json_out = dict()
    confirms_added = []
    deliveries = []
    for n, f in enumerate(sorted(os.listdir(tagged_folder))):
        if f.startswith(".") or f.startswith("~"):
            continue

        sid_f = f[:7]
        text_df = og_df1[og_df1["SID"] == f[-12:-5]]
        # print(text_df)
        tagged_dir = os.path.join(tagged_folder, f)
        token_df = pd.read_excel(tagged_dir)
        print(tagged_dir)

        token_df = token_df.fillna("")
        token_df = token_df.replace("해당사항 없음", "")

        og_text_df = token_df.drop_duplicates(subset="SID")
        sid_og_text = dict(zip(og_text_df.SID, text_df.text))
        fixed_token_df = realign_token_df(token_df)

        final_tagged_dict, revision = tag_compiler(
            fixed_token_df, chat_tags_dict, sid_og_text
        )
        revision_df = pd.DataFrame(data=revision, columns=["Topic_SID", "tokens"])

        og_df = pd.read_excel(og_dir)
        og_df = og_df.drop(columns=["text"])

        dix, b_deliv_df, relation_meta = base_delivery_df_chat(
            f, og_df, final_tagged_dict
        )

        b_deliv_df, confirms_added = check_end_confirm(
            f, b_deliv_df, confirms_list, confirms_added
        )
        delivery_df = confirm_logic(b_deliv_df, relation_meta)
        delivery_df.to_excel(os.path.join(out_dir, dix + ".xlsx"), index=False)
        deliveries.append(delivery_df)
        if len(revision_df) > 0:
            revision_df.to_excel(
                os.path.join(out_dir, f"{dix}_failed_sid.xlsx"),
                index=False,
            )

    confirms_fixed = pd.DataFrame(data=confirms_added, columns=["confirm_added"])
    confirms_fixed.to_excel(os.path.join(out_dir, out_name_confirms), index=False)
    for n, d in enumerate(deliveries):
        if n == 0:
            master_df = d
        else:
            master_df = master_df.append(d, ignore_index=True)
    master_df.to_excel(os.path.join(out_dir, out_name), index=False)
