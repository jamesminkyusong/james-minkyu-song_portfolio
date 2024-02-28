import json
import os
import re
from configparser import ConfigParser
from string import ascii_uppercase

import pandas as pd
import requests
from konlpy.tag import Okt
from textacy import preprocessing

okt = Okt()


def parsers():
    c_parser = ConfigParser()
    c_parser.read("ss_ner.ini")
    return c_parser


def replace_emojis(sentence):
    replaced_sentence = preprocessing.replace.emojis(sentence, " ")
    return replaced_sentence


def replace_incomp_char(sentence: str) -> str:
    og_sentence = sentence
    pattern_list = ["[ㅏ-ㅣ]", "[ㄱ-ㅎ]", "[\^]"]
    for pattern in pattern_list:
        new_sentence = re.sub(pattern, "", sentence)
        new_sentence = (" ").join(new_sentence.split())
        check_sentence = re.sub("[^\w]", "", new_sentence)
        if len(check_sentence) != 0:
            sentence = new_sentence
        else:
            return og_sentence
    return sentence


def add_punc(sentence: str) -> str:
    sentence = sentence.strip()
    if sentence.endswith("?") or sentence.endswith(".") or sentence.endswith("!"):
        sentence = sentence + sentence[-1]
    else:
        sentence = sentence + "."
    return sentence


def replace_punc_start(sentence):
    konum = "[가-힣ㄱ-ㅎㅏ-ㅣ0-9-]"
    check_punc_start = re.search(konum, sentence)
    if check_punc_start is not None:
        start_loc = check_punc_start.span()[0]
        if start_loc != 0:
            sentence = sentence[start_loc:]
    return sentence


def single_trim(sentence):
    sentence = str(sentence)
    sentence_split = sentence.split()
    trimmed_sentence = (" ").join(sentence_split)
    return trimmed_sentence


def prepare_sample_df(df):
    df["processed_content"] = df.Content.map(replace_emojis)
    df["processed_content"] = df.processed_content.map(replace_incomp_char)
    df["processed_content"] = df.processed_content.map(add_punc)
    df["processed_content"] = df.processed_content.map(replace_punc_start)
    df["final_input_etri"] = (
        " | " + df["CID-Speaker-SID"] + ": " + df["processed_content"]
    )
    return df


def prepare_etri_batch_str(df):
    in_etri_list = df["final_input_etri"].values.tolist()
    final_st = ""
    for st in in_etri_list:
        final_st += st
    return final_st


def etr_ner_api(u, k, text_lines):
    if len(text_lines) > 10000:
        raise ValueError("input string too long")
    head = {"Content-Type": "application/json; charset=UTF-8"}
    requestJson = {
        "access_key": k,
        "argument": {"analysis_code": "ner", "text": text_lines},
    }

    r = requests.post(u, data=json.dumps(requestJson), headers=head)
    print(r)
    r_dict = r.json()
    r_dict_list = r_dict["return_object"]["sentence"]

    return r_dict_list


def write_json(json_data, out_path, f_name, sentence_no):
    json_to_write = json.dumps(json_data, ensure_ascii=False)
    sentence_pad = str(sentence_no + 1).zfill(5)
    final_name_path = os.path.join(out_path, sentence_pad + "_" + f_name)
    with open(final_name_path, "w", encoding="UTF-8-sig") as jsonfile:
        jsonfile.write(json_to_write)
    sentence_no += 1
    return sentence_no


def rough_write_chat_json(etr_result, curr_json_path):
    sentence_count = 0
    for r in etr_result:
        sentence_count = write_json(r, curr_json_path, "sentence.json", sentence_count)
    return sorted(os.listdir(curr_json_path))


def reverse_traverse_fix_splits(json_files_list, odir, useless_dir):
    reversed_check_jsons = list(reversed(json_files_list))
    for n, j in enumerate(reversed_check_jsons):
        if j.startswith(".") or j.startswith("~"):
            continue
        with open(os.path.join(odir, j), "r", encoding="UTF-8-sig") as json_file:
            j_json = json.load(json_file)
        processed_sentence = j_json.get("text")
        processed_sentence = processed_sentence.strip()
        if not processed_sentence.startswith("|"):
            previous_file = reversed_check_jsons[n + 1]
            with open(
                os.path.join(odir, previous_file), "r", encoding="UTF-8-sig"
            ) as previous_json:
                p_json = json.load(previous_json)
            for p in p_json:
                json_obj = p_json.get(p)
                split_json_obj = j_json.get(p)
                if isinstance(json_obj, float):
                    final_obj = str(json_obj) + ", " + str(split_json_obj)
                elif isinstance(json_obj, str):
                    final_obj = str(json_obj) + " " + str(split_json_obj)
                elif isinstance(json_obj, list):
                    for sjo in split_json_obj:
                        json_obj.append(sjo)
                    final_obj = json_obj
                p_json[p] = final_obj
            # print(p_json)
            with open(
                os.path.join(odir, previous_file), "w", encoding="UTF-8-sig"
            ) as updatedfile:
                updatedfile.write(json.dumps(p_json, ensure_ascii=False))
            os.rename(os.path.join(odir, j), os.path.join(useless_dir, j))
    return sorted(os.listdir(odir))


def final_fix_sentence(fixed_list, odir):
    final_files_list = []
    for j in fixed_list:
        if j.startswith(".") or j.startswith("~"):
            continue
        with open(os.path.join(odir, j), "r", encoding="UTF-8-sig") as json_file:
            j_json = json.load(json_file)
        processed_sentence = j_json.get("text")
        processed_sentence = processed_sentence.strip()
        # print(processed_sentence)
        rename_id = processed_sentence[
            processed_sentence.find("|") + 1 : processed_sentence.find(":")
        ]
        only_sentence = processed_sentence[processed_sentence.find(":") + 1 :]
        rename_id = rename_id.strip()
        rename_id = rename_id + ".json"
        only_sentence = only_sentence.strip()

        j_json["text"] = only_sentence
        with open(os.path.join(odir, j), "w", encoding="UTF-8-sig") as final_file:
            final_file.write(json.dumps(j_json, ensure_ascii=False))
        os.rename(os.path.join(odir, j), os.path.join(odir, rename_id))
        final_files_list.append(rename_id)
    return final_files_list


def create_josa(only_sentence, sid_sentence):
    pos_out = list(map(okt.pos, only_sentence))

    to_compare_pos = remove_punc_pos(pos_out)
    split_text = list(map(lambda x: x.strip().split(" "), only_sentence))
    split_text_1 = list(map(lambda x: x.strip().split(" "), only_sentence))

    fixed_josa_split = find_josa(to_compare_pos, split_text, split_text_1)
    rearranged_josa = rearrange_josa(fixed_josa_split)
    spanned_text, spanned_sid = span_sentences(sid_sentence, rearranged_josa)
    rearranged_josa_span = []
    for rj in rearranged_josa:
        rearranged_josa_span.extend(rj)
    return spanned_sid, spanned_text, rearranged_josa_span


def rearrange_josa(fj_split):
    rearranged = []
    for fjs in fj_split:
        if len(fjs) == 1 and fjs[0] == "":
            pass
        else:
            rearranged.append(fjs)
    return rearranged


def span_sentences(sid_list, rearr_sent):
    only_text_span = []
    only_sid_span = []
    for n, r in enumerate(rearr_sent):
        for _ in range(len(r)):
            sid_sentence = sid_list[n]
            sid = str(sid_sentence[: sid_sentence.find("_")])
            text = str(sid_sentence[sid_sentence.find("_") + 1 :])
            only_text_span.append(text)
            only_sid_span.append(sid)
    return only_text_span, only_sid_span


def remove_punc_pos(pos_results: list):
    work_pos = pos_results.copy()
    edited_pos = []
    for pos_result in work_pos:
        for n, p in enumerate(pos_result):
            if p[1] == "Punctuation":
                # print(p)
                pos_result.pop(n)
        edited_pos.append(pos_result)
    return edited_pos


def find_josa(pos_list, split_list, split_list1):
    exception_count = 0
    for n, pos_sentence_result in enumerate(pos_list):
        # print(pos_sentence_result)
        for (
            c,
            pos_tup,
        ) in enumerate(pos_sentence_result):
            pos_tok, pos_tag = pos_tup
            if pos_tag == "Josa" or pos_tag == "Foreign":
                try:
                    if c - 1 != -1:
                        before_josa = pos_sentence_result[c - 1][0]
                        joined_before_josa = before_josa + pos_tup[0]
                        found_in_split = in_find_for_list(
                            joined_before_josa, split_list[n]
                        )
                        if len(found_in_split) >= 1:

                            insert_count = 1
                            # split_list[n]
                            for idx_loc, found in found_in_split:
                                insert_val = found[: len(found) - len(pos_tok)]
                                if insert_count == 1:
                                    split_list[n][idx_loc] = insert_val

                                else:
                                    split_list[n][idx_loc + insert_count] = insert_val
                                split_list[n].insert((idx_loc + insert_count), pos_tok)
                                insert_count += 1
                        else:
                            continue
                except:
                    exception_count += 1
                    print(f"exception: {exception_count}")
                    split_list[n] = split_list1[n]

    for final_idx, s in enumerate(split_list):
        # print(f"{s}: {split_list1[final_idx]}")
        josa_split_join = ("").join(s)
        before_split_join = ("").join(split_list1[final_idx])
        if josa_split_join != before_split_join:
            split_list[final_idx] = split_list1[final_idx]
            print(f"{josa_split_join} : {before_split_join}")
    return split_list


def only_ne_tags(
    sid_track,
    sid_text_list,
    etri_result,
    ne_id,
    ne_range,
    ne_token,
    ne_tag,
    ne_text,
    only_sentence,
):

    sentence = etri_result["text"]
    sentence = single_trim(sentence)
    sentence = sentence[:-1]
    if len(etri_result["NE"]) > 0:
        for ne in etri_result["NE"]:
            # print(f"{ne['id']}: {ne['text']}")
            ne_id.append(ne["id"])
            ne_range.append((ne["begin"], ne["end"]))
            ne_token.append(ne["text"])
            ne_tag.append(ne["type"])
            ne_text.append(sentence)
    else:
        ne_id.append("")
        ne_range.append(("", ""))
        ne_token.append("")
        ne_tag.append("")
        ne_text.append(sentence)
    sid_sentence = str(sid_track) + "_" + sentence
    sid_text_list.append(sid_sentence)
    only_sentence.append(sentence)
    return ne_id, ne_range, ne_token, ne_tag, ne_text, only_sentence, sid_text_list


def insert_row(idx, df, df_insert):
    dfA = df.iloc[
        :idx,
    ]
    dfB = df.iloc[
        idx:,
    ]

    df = dfA.append(df_insert).append(dfB).reset_index(drop=True)

    return df


def split_more(df, master_df):
    additional_index_count = 0
    for i in df.index:
        row_to_fix = df.loc[i].copy()
        split_token = row_to_fix["ne_token"].split()
        for s in split_token:
            row_to_fix["ne_token"] = s

            master_df = insert_row(i + additional_index_count, master_df, row_to_fix)
            additional_index_count += 1
    return master_df, df


def initial_split_token(df):
    to_split = df["Content"].values.tolist()
    to_split = list(map(lambda s: s.replace("\u200b", " "), to_split))
    to_split = list(map(lambda s: s.replace("=", "-"), to_split))

    # to_split = list(map(lambda s: s.replace("'", " "), to_split))
    # to_split = list(map(lambda s: s.replace("‘", " "), to_split))
    # to_split = list(map(lambda s: s.replace("’", " "), to_split))
    # to_split = list(map(lambda s: s.replace("<", " "), to_split))
    # to_split = list(map(lambda s: s.replace(">", " "), to_split))
    to_split = list(map(lambda x: (" ").join(x.split()), to_split))

    return to_split


def etr_ner_api(u, k, text_lines):
    head = {"Content-Type": "application/json; charset=UTF-8"}

    requestJson = {
        "access_key": k,
        "argument": {"analysis_code": "ner", "text": text_lines},
    }

    r = requests.post(u, data=json.dumps(requestJson), headers=head)
    r_dict = r.json()
    r_dict_list = r_dict["return_object"]["sentence"]

    return r_dict_list


def in_find_for_list(string_to_find, list_of_strings):
    found_ins = [[n, s] for n, s in enumerate(list_of_strings) if string_to_find in s]
    return found_ins


def create_tagged_df(df, json_dir):
    ner_id = []
    ner_range = []
    ner_token = []
    ner_tag = []
    ner_text = []
    only_text = []
    sid_text = []
    to_split = initial_split_token(df)
    cid_list = df["CID-Speaker-SID"].values.tolist()
    for sid_count, ins in enumerate(to_split):
        json_file = cid_list[sid_count] + ".json"
        with open(
            os.path.join(json_dir, json_file), "r", encoding="UTF-8-sig"
        ) as previous_json:
            api_result = json.load(previous_json)
        (
            ner_id,
            ner_range,
            ner_token,
            ner_tag,
            ner_text,
            only_text,
            sid_text,
        ) = only_ne_tags(
            sid_count + 1,
            sid_text,
            api_result,
            ner_id,
            ner_range,
            ner_token,
            ner_tag,
            ner_text,
            only_text,
        )
    spanned_sids, spanned_sentences, spanned_josa = create_josa(only_text, sid_text)
    etri_df = pd.DataFrame(
        data=list(zip(ner_id, ner_range, ner_text, ner_token, ner_tag)),
        columns=["ne_id", "mor_id_range", "text", "ne_token", "ne_tag"],
    )
    josa_df = pd.DataFrame(
        data=list(zip(spanned_sids, spanned_sentences, spanned_josa)),
        columns=["SID", "text", "token"],
    )
    return etri_df, josa_df


def sort_tagged_df(tagged_df):
    tagged_df = tagged_df[tagged_df["ne_token"] != ""]
    tagged_df = tagged_df[
        tagged_df["ne_tag"].str.startswith("OG")
        | tagged_df["ne_tag"].str.startswith("DT")
        | tagged_df["ne_tag"].str.startswith("LC")
        | tagged_df["ne_tag"].str.startswith("TI")
    ]
    tagged_df = tagged_df.reset_index(drop=True)
    to_split_more = tagged_df[tagged_df["ne_token"].map(str.split).map(len) > 1]

    done_tagged_df, to_split_more = split_more(to_split_more, tagged_df)
    to_remove_after_insert = to_split_more["ne_token"].values.tolist()
    done_tagged_df = done_tagged_df[
        ~done_tagged_df["ne_token"].isin(to_remove_after_insert)
    ]
    done_tagged_df = done_tagged_df.reset_index(drop=True)
    return done_tagged_df


def cross_check_josa_ner_tags(done_tagged_df, josa_df):
    josa_df["Tags 1"] = ""
    for g in done_tagged_df.groupby(by=["text"], sort=False):
        tag_col = []
        for g_row in g:
            if isinstance(g_row, str):
                continue
            g_text = g_row["text"].iloc[0]
            g_tag = g_row["ne_tag"].values.tolist()
            g_token = g_row["ne_token"].values.tolist()
            g_token_tag_dict = dict(zip(g_token, g_tag))
            reference_df = josa_df[josa_df["text"] == g_text]
            for r_token in reference_df["token"].values.tolist():
                if g_token_tag_dict.get(r_token) is not None:
                    tag_col.append(g_token_tag_dict.get(r_token))
                else:
                    tag_col.append("")
            reference_df["Tags 1"] = tag_col
            josa_df.iloc[reference_df.index] = reference_df
    return josa_df


def swap_cid(og_df, processed_df):
    final_cid = og_df["CID-Speaker-SID"].values.tolist()
    token_sid = [str(i + 1) for i in range(len(final_cid))]
    final_cid_dict = dict(zip(token_sid, final_cid))
    token_sid = processed_df["SID"].values.tolist()
    final_token_cid = [final_cid_dict.get(t) for t in token_sid]
    processed_df["SID"] = final_token_cid
    return processed_df


def ner_sets(in_dir):
    ner_tags = pd.read_excel(in_dir, sheet_name=1)
    all_ner = ner_tags["Total"].values.tolist()
    calendar = ner_tags["DT"].dropna().values.tolist()
    time_l = ner_tags["TI"].dropna().values.tolist()
    place = ner_tags["LC/LCP/LCG/OGG/AF"].dropna().values.tolist()

    return all_ner, calendar, time_l, place


def write_group_by_cid(df, in_dir, out_dir, starting_no):
    df["grouping_sid"] = df["SID"].apply(lambda x: x[:7])
    gb = df.groupby("grouping_sid", sort=False)
    gid = [gb.get_group(x) for x in gb.groups]
    more_cols = ["Tokens 2", "Tags 2", "Tokens 3", "Tags 3", "Tokens 4", "Tags 4"]
    for g in gid:
        s_no = str(starting_no).zfill(5)
        filename = g["grouping_sid"].iloc[0]
        filename = s_no + "_SRL_messenger_data_" + filename + ".xlsx"
        g = g.drop(columns=g.columns[-1])
        for c in more_cols:
            g[c] = ""
        starting_no += 1
        write_with_dv_chats(g, in_dir, out_dir, filename)


def apply_format(
    df, col, worksheet, all_tags, calendar_tags, time_tags, place_tags, cell_format
):
    columns = df.columns.tolist()
    excel_col_loc = columns.index(col)
    col_d = {i: v for i, v in enumerate(ascii_uppercase)}
    cell_id = col_d.get(excel_col_loc)
    for i, j in enumerate(df[col]):

        cellno = cell_id + str(i + 2)
        if j == "":
            worksheet.data_validation(cellno, {"validate": "list", "source": all_tags})
        elif j.startswith("DT_"):
            worksheet.write(cellno, "날짜관련")
            worksheet.data_validation(
                cellno, {"validate": "list", "source": calendar_tags}
            )
        elif j.startswith("TI_"):
            worksheet.write(cellno, "시간관련")
            worksheet.data_validation(cellno, {"validate": "list", "source": time_tags})
        elif (
            j.startswith("LC_")
            or j.startswith("LCP_")
            or j.startswith("LCG_")
            or j.startswith("OGG_")
            or j.startswith("AF_")
        ):
            worksheet.write(cellno, "장소관련")
            worksheet.data_validation(
                cellno, {"validate": "list", "source": place_tags}
            )
        else:
            print(j)
            worksheet.write_blank(cellno, "", cell_format)
            worksheet.data_validation(cellno, {"validate": "list", "source": all_tags})
    return worksheet


def write_with_dv_chats(df, in_dir, out_dir, filename):
    all_tags, calendar_tags, time_tags, place_tags = ner_sets(in_dir)

    file_path = os.path.join(out_dir, filename)
    writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", index=False)

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    cell_format = workbook.add_format()
    tag_cols = ["Tags 1", "Tags 2", "Tags 3", "Tags 4"]
    for tag in tag_cols:
        worksheet = apply_format(
            df,
            tag,
            worksheet,
            all_tags,
            calendar_tags,
            time_tags,
            place_tags,
            cell_format,
        )
    workbook.close()
    print("done")


if __name__ == "__main__":
    configs = parsers()
    URL = configs.get("ET_API_DEFAULT", "url")
    KEY = configs.get("ET_API_DEFAULT", "key")
    file_path = configs.get("PATHS", "input_chat_directory")
    ner_set_dir = configs.get("PATHS", "set_file")

    json_odir = configs.get("PATHS", "json_chat_outdir")
    outputpath = configs.get("PATHS", "output_chat_directory")
    bin_dir = configs.get("PATHS", "useless_directory")

    chat_df = pd.read_excel(file_path)
    processed_chat_df = prepare_sample_df(chat_df)
    in_etri_str = prepare_etri_batch_str(processed_chat_df)
    etri_result = etr_ner_api(URL, KEY, in_etri_str)
    base_json_files = rough_write_chat_json(etri_result, json_odir)
    split_fixed_files = reverse_traverse_fix_splits(base_json_files, json_odir, bin_dir)
    final_files = final_fix_sentence(split_fixed_files, json_odir)
    chat_df2 = chat_df.copy()
    chat_df2["Content"] = processed_chat_df["processed_content"]

    etri_df_2, base_josa_df = create_tagged_df(chat_df2, json_odir)
    done_etr_df = sort_tagged_df(etri_df_2)
    josa_ner_df = cross_check_josa_ner_tags(done_etr_df, base_josa_df)
    # josa_ner_df.to_excel(
    #     os.path.join(outputpath, r"check_chat_tokens_211209.xlsx"), index=False
    # )
    josa_ner_df = swap_cid(chat_df, josa_ner_df)
    write_group_by_cid(josa_ner_df, ner_set_dir, outputpath, 1)
