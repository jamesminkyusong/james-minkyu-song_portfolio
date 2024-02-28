import os
from numpy import single
import pandas as pd
from konlpy.tag import Okt
import requests
import json
from configparser import ConfigParser

okt = Okt()


def parsers():
    c_parser = ConfigParser()
    c_parser.read("ss_ner.ini")
    return c_parser


def single_trim(sentence):
    sentence = str(sentence)
    sentence_split = sentence.split()
    trimmed_sentence = (" ").join(sentence_split)
    return trimmed_sentence


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
    for y in etri_result:
        sentence = y["text"]
        sentence = single_trim(sentence)
        if len(y["NE"]) > 0:
            for ne in y["NE"]:
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


def make_multiple_sentences(api_result):
    sentences_separated = [a["text"] for a in api_result]
    return sentences_separated


def in_find_for_list(string_to_find, list_of_strings):
    found_ins = [[n, s] for n, s in enumerate(list_of_strings) if string_to_find in s]
    return found_ins


def create_tagged_df(df, url, key):
    ner_id = []
    ner_range = []
    ner_token = []
    ner_tag = []
    ner_text = []
    only_text = []
    sid_text = []
    to_split = initial_split_token(df)
    for sid_count, ins in enumerate(to_split):
        api_result = etr_ner_api(url, key, ins)
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


def swap_sid(og_df, processed_df):
    final_sid = og_df["Final_SID"].values.tolist()
    token_sid = [str(i + 1) for i in range(len(final_sid))]
    final_sid_dict = dict(zip(token_sid, final_sid))
    token_sid = processed_df["SID"].values.tolist()
    final_token_cid = [final_sid_dict.get(t) for t in token_sid]
    processed_df["SID"] = final_token_cid
    return processed_df


def finalize_df(josa_etr_df):
    final_df = josa_etr_df.copy()
    overwrite_tags = josa_etr_df["Tags 1"].values.tolist()
    for n, o in enumerate(overwrite_tags):
        if o == "":
            overwrite_tags[n] = "해당사항 없음"
    final_df["Tags 1"] = overwrite_tags

    final_df["Tokens 2"] = ""
    final_df["Tags 2"] = "해당사항 없음"
    final_df["Tokens 3"] = ""
    final_df["Tags 3"] = "해당사항 없음"
    final_df["Tokens 4"] = ""
    final_df["Tags 4"] = "해당사항 없음"
    final_df["Tokens 5"] = ""
    final_df["Tags 5"] = "해당사항 없음"
    return final_df


def write_with_dv(df, out_dir, filename):
    all_tags = ["제목", "시작 날짜", "종료 날짜", "시작 시간", "종료 시간", "약속 장소", "해당사항 없음"]

    file_path = os.path.join(out_dir, filename)
    writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", index=False)

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    cell_format = workbook.add_format()
    tags_cell = ["D", "F", "H", "J", "L"]
    for i, j in enumerate(df["Tags 1"]):
        for tc in tags_cell:
            cellno = tc + str(i + 2)

            worksheet.write(cellno, "해당사항 없음", cell_format)
            worksheet.data_validation(cellno, {"validate": "list", "source": all_tags})

    workbook.close()
    print("done")


if __name__ == "__main__":
    configs = parsers()

    URL = configs.get("ET_API_DEFAULT", "url")
    KEY = configs.get("ET_API_DEFAULT", "key2")
    file_path = configs.get("PATHS", "input_directory")
    outputpath = configs.get("PATHS", "output_directory")

    split_df = pd.read_excel(file_path)
    etri_df_2, base_josa_df = create_tagged_df(split_df, URL, KEY)
    done_etr_df = sort_tagged_df(etri_df_2)
    josa_ner_df = cross_check_josa_ner_tags(done_etr_df, base_josa_df)
    josa_ner_df.to_excel(
        os.path.join(outputpath, r"check__eq_tokens_211209.xlsx"), index=False
    )
    josa_ner_df = swap_sid(split_df, josa_ner_df)
    final_done_df = finalize_df(josa_ner_df)
    # final_done_df.to_excel(os.path.join(outputpath, "tagged_done.xlsx"), index=False)
    # write_with_dv(
    #     final_done_df,
    #     outputpath,
    #     "__track2_error_1206_tkn_select_star.xlsx",
    # )
    final_done_df["Tags 1"] = ""

    write_with_dv(final_done_df, outputpath, "__eq_1209_tkn_select_star.xlsx")
