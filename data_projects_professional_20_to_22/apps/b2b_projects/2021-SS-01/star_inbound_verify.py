import os
import pandas as pd
from textacy import preprocessing
import argparse
from configparser import ConfigParser
import requests
import json
import re


def parsers():
    c_parser = ConfigParser()
    c_parser.read("ss_ner.ini")
    return c_parser


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


def write_json(json_data, out_path, f_name, sentence_no):
    json_to_write = json.dumps(json_data, ensure_ascii=False)
    sentence_pad = str(sentence_no + 1).zfill(5)
    final_name_path = os.path.join(out_path, sentence_pad + "_" + f_name)
    with open(final_name_path, "w", encoding="UTF-8-sig") as jsonfile:
        jsonfile.write(json_to_write)
    sentence_no += 1
    return sentence_no


# emoticons or > used as indicator raises False
# no full bracket pair in sentence = False
def bracket_pairs(sentence):
    sentence = sentence.replace(":)", "")
    sentence = sentence.replace(":(", "")

    return_bool = True
    only_brackets_sentence = re.sub(
        r"[^(|)|\[|\]|\{|\}]", "", sentence
    )  # r"[^(|)}<|>|\[|\]|\{|\}]"
    pair_dict = {"(": ")", "<": ">", "[": "]", "{": "}"}
    if len(only_brackets_sentence) > 0:
        brackets_to_check = ("").join(set(only_brackets_sentence))
        if len(brackets_to_check) % 2 != 0:
            return_bool = False
            return return_bool
        else:
            brackets_to_check = brackets_to_check.replace(")", "")
            brackets_to_check = brackets_to_check.replace(">", "")
            brackets_to_check = brackets_to_check.replace("]", "")
            brackets_to_check = brackets_to_check.replace("}", "")
        store_count = 0
        for b in brackets_to_check:
            open_count = sentence.count(b)
            close_count = sentence.count(pair_dict.get(b))
            store_count += open_count
            store_count += close_count
            if open_count != close_count:
                return_bool = False
        if len(only_brackets_sentence) != store_count:
            return_bool = False
    return return_bool


def single_trim(sentence):
    sentence = str(sentence)
    sentence_split = sentence.split()
    trimmed_sentence = (" ").join(sentence_split)
    return trimmed_sentence


def preserve_line_break_trim(sentence):
    sentence = str(sentence)
    if sentence.find("\t") != -1:
        print(sentence)
    sentence_split = sentence.split("\n")
    for n, s in enumerate(sentence_split):
        if s != "":
            single_trimmed = single_trim(s)
            sentence_split[n] = single_trimmed
    final_sentence = ("\n").join(sentence_split)
    return final_sentence


def replace_emojis(sentence):
    replaced_sentence = preprocessing.replace.emojis(sentence, " ")
    return replaced_sentence


def replace_keywords(sentence, keyword_list, repl_word):
    for k in keyword_list:
        if sentence.find(k) != -1:
            sentence = sentence.replace(k, repl_word)
    return sentence


def check_cancel_change(sentence):
    cc_keywords = ["변경", "취소", "연장", "연기"]
    for c in cc_keywords:
        if sentence.find(c) != -1:
            return False
    return True


def prepare_dt_ti(df, u, k, o_path):
    final_sid = df["Final_SID"].values.tolist()
    content = df["Content"].values.tolist()

    for n, ko in enumerate(content):
        curr_json_path = os.path.join(o_path, final_sid[n])
        os.mkdir(curr_json_path)
        etr_result = etr_ner_api(u, k, ko)
        sentence_count = 0
        for r in etr_result:
            sentence_count = write_json(
                r, curr_json_path, "sentence.json", sentence_count
            )


def check_json_dt_ti(parent_folder):
    all_dt_ti = []
    dt_ti_len = []
    dt_ti_pass = []
    for folder in sorted(os.listdir(parent_folder)):
        if folder.startswith(".") or folder.startswith("~"):
            continue
        else:
            sentence_folder = os.path.join(parent_folder, folder)
            dt_ti_bucket = []
            for s_json in sorted(os.listdir(sentence_folder)):
                if s_json.startswith(".") or s_json.startswith("~"):
                    continue
                with open(
                    os.path.join(sentence_folder, s_json), "r", encoding="UTF-8-sig"
                ) as json_file:
                    j_json = json.load(json_file)
                    ner = j_json.get("NE")
                    if len(ner) > 0:
                        for ne in ner:
                            ne_type = ne.get("type")
                            ne_text = ne.get("text")
                            if ne_type.startswith("DT") or ne_type.startswith("TI"):
                                dt_ti_bucket.append(ne_text)

            if len(dt_ti_bucket) > 0:
                dt_ti_len.append(len(dt_ti_bucket))
                dt_ti_str = ("\t").join(dt_ti_bucket)
                dt_ti_pass.append(True)
            else:
                dt_ti_str = ""
                dt_ti_len.append(0)
                dt_ti_pass.append(False)
            all_dt_ti.append(dt_ti_str)
    return dt_ti_pass, all_dt_ti, dt_ti_len


def verify_dt_ti(df, u, k, o_path):
    prepare_dt_ti(df, u, k, o_path)
    dt_ti_bool, dt_ti_tags, dt_ti_length = check_json_dt_ti(o_path)
    return dt_ti_bool, dt_ti_tags, dt_ti_length


if __name__ == "__main__":
    everything_but_ko = "[^가-힣ㄱ-ㅎㅏ-ㅣ+]"
    adv_keywords = [
        "[WEB 발신]",
        "[WEB발신]",
        "[Web 발신]",
        "[Web발신]",
        "[web 발신]",
        "[web발신]",
        "(광고)",
        "( 광고 )",
    ]
    configs = parsers()

    URL = configs.get("ET_API_DEFAULT", "url")
    KEY = configs.get("ET_API_DEFAULT", "key")
    file_path = configs.get("PATHS", "first_inbound_dir")
    json_odir = configs.get("PATHS", "json_outdir")
    outputpath = configs.get("PATHS", "output_directory")

    check_df = pd.read_excel(file_path)
    check_df = check_df.fillna("")

    check_df["Content"] = check_df["Content"].map(replace_emojis)
    check_df["Content"] = check_df["Content"].apply(
        replace_keywords, args=(adv_keywords, "")
    )
    check_df["Content"] = check_df["Content"].map(preserve_line_break_trim)
    check_content_dups = check_df["Content"].replace(everything_but_ko, "", regex=True)
    check_df["unique"] = ~check_content_dups.duplicated()

    check_df["bracket_pairs_pass"] = check_df["Content"].map(bracket_pairs)

    check_df["change_cancel_pass"] = check_df["Content"].map(check_cancel_change)
    (
        check_df["DateTime_pass"],
        check_df["DateTime_count"],
        check_df["DateTime_tokens"],
    ) = verify_dt_ti(check_df, URL, KEY, json_odir)

    check_df.to_excel(
        os.path.join(outputpath, "dt_checked_select_star_deliv_1208_correct_sid.xlsx"),
        index=False,
    )
