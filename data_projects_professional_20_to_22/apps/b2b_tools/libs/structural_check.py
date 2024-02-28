import argparse
import os
import re
from configparser import ConfigParser

import fasttext
import gcld3
import langid
import numpy as np
import pandas as pd
from scipy import stats
from textdistance import ratcliff_obershelp, sorensen
from transformers import MarianMTModel, MarianTokenizer


def parsers():
    parser = argparse.ArgumentParser(description="source lang and dst lang")
    parser.add_argument(
        "-src", "--source", type=str, metavar="", required=True, help="input lang"
    )

    parser.add_argument(
        "-dst", "--dest", type=str, metavar="", required=True, help="output lang"
    )

    args = parser.parse_args()
    c_parser = ConfigParser()
    c_parser.read("structural.ini")
    return args, c_parser


def filter_hidden_nan(df):
    df = df.fillna("")
    hidden_df = pd.DataFrame()
    hidden_df["lang_1_hidden"] = df[df.columns[1]] == ""
    hidden_df["lang_2_hidden"] = df[df.columns[2]] == ""
    df["empty"] = hidden_df.any(axis=1)
    return df


def trimmer(df, col_to_map):
    df = df.fillna("")
    trimming = lambda t: (" ").join(str(t).split())
    # df = df.applymap(trimming)
    df[df.columns[col_to_map]] = df[df.columns[col_to_map]].map(trimming)
    return df


def lower_case(df, lang_code):
    if lang_code in ["ko", "zh", "ja"]:
        return df
    else:
        df[lang_code] = df[lang_code].map(lambda s: str(s).lower())
        return df


def manage_dup_bools_single(df, lang_col, dup_col):
    dup_col_name = df.columns[dup_col]
    bool_df = df.copy()
    bool_repl = bool_df[bool_df[dup_col_name]]
    str_exp = f"{lang_col} == ''"
    to_repl_false = bool_repl.query(str_exp)
    to_repl_false = to_repl_false.index.tolist()
    bool_df.loc[to_repl_false, dup_col_name] = False
    df[dup_col_name] = bool_df[dup_col_name]
    return df


def manage_dup_bools_multi(df, lang_col_1, lang_col_2, dup_col_multi):
    dup_col_name = df.columns[dup_col_multi]

    bool_df = df.copy()
    bool_repl = bool_df[bool_df[dup_col_name]]
    str_exp = f"{lang_col_1} == '' & {lang_col_2} == '' "
    to_repl_false = bool_repl.query(str_exp)
    to_repl_false = to_repl_false.index.tolist()
    bool_df.loc[to_repl_false, dup_col_name] = False
    df[dup_col_name] = bool_df[dup_col_name]
    return df


def get_pattern(lang_re_dict, lang):
    try:
        pattern = lang_re_dict.get(lang)
        return pattern
    except:
        print("language not supported yet.")


def add_two_patterns(p1, p2):
    p1_add = p1[:-1]
    p2_add = p2[1:]
    p_final = p1_add + p2_add
    return p_final


def replace_then_trim(df, new_df, col_name, pattern, col_no):
    new_df[col_name] = df[col_name].replace(pattern, "", regex=True)
    new_df = trimmer(new_df, col_no)
    return new_df


def find_all_dups(df, col_1, col_2, lang_re_dict):
    dup_df = pd.DataFrame()
    col_name_1 = df.columns[col_1]
    col_name_2 = df.columns[col_2]
    df = lower_case(df, col_name_1)
    df = lower_case(df, col_name_2)

    neg_pattern = lambda p: p[0] + "^" + p[1:]
    nums_pattern = get_pattern(lang_re_dict, "nums")
    col_1_pattern = get_pattern(lang_re_dict, col_name_1)
    col_1_pattern = add_two_patterns(col_1_pattern, nums_pattern)
    col_1_pattern = neg_pattern(col_1_pattern)
    col_2_pattern = get_pattern(lang_re_dict, col_name_2)
    col_2_pattern = add_two_patterns(col_2_pattern, nums_pattern)
    col_2_pattern = neg_pattern(col_2_pattern)

    dup_df[col_name_1] = df[col_name_1].replace(col_1_pattern, "", regex=True)
    dup_df[col_name_2] = df[col_name_2].replace(col_2_pattern, "", regex=True)
    dup_df = trimmer(dup_df, 0)
    dup_df = trimmer(dup_df, 1)
    dup_df[col_name_1 + "_dups"] = dup_df.duplicated(subset=[col_name_1], keep=False)
    dup_df[col_name_2 + "_dups"] = dup_df.duplicated(subset=[col_name_2], keep=False)
    dup_df["both_dups"] = dup_df.duplicated(subset=[col_name_1, col_name_2], keep=False)
    dup_df = manage_dup_bools_single(dup_df, col_name_1, 2)
    dup_df = manage_dup_bools_single(dup_df, col_name_2, 3)
    dup_df = manage_dup_bools_multi(dup_df, col_name_1, col_name_2, 4)
    dup_df = dup_df.drop(columns=dup_df.columns[0:2])
    df = df.join(dup_df)
    return df


def deal_ratio_zeros(ratio_series):
    for n, x in enumerate(ratio_series):
        if x == np.inf:
            ratio_series[n] = 0
    return ratio_series


def find_ratio(df, col_1, col_2):
    column_1 = df[df.columns[col_1]]
    column_2 = df[df.columns[col_2]]
    word_count = lambda x: len(str(x).split())
    column_1_word_count = column_1.map(word_count)
    column_2_word_count = column_2.map(word_count)
    ratio = column_1_word_count / column_2_word_count
    ratio = deal_ratio_zeros(ratio)
    ratio_z = np.abs(stats.zscore(ratio))
    ratio_outliers = [True if z >= 3 else False for z in ratio_z]
    df["len_ratio"] = ratio_outliers
    return df


def ko_weird_check(df, lang_re_dict):
    ko_df = pd.DataFrame()
    neg_pattern = lambda p: p[0] + "^" + p[1:]
    jaeum_pattern = lang_re_dict.get("ko_2")
    jaeum_pattern = neg_pattern(jaeum_pattern)

    moeum_pattern = lang_re_dict.get("ko_1")
    moeum_pattern = neg_pattern(moeum_pattern)

    ko_df = replace_then_trim(df, ko_df, "ko", jaeum_pattern, 0)
    ko_df["jaeum_check"] = ko_df["ko"] != ""
    ko_df = replace_then_trim(df, ko_df, "ko", moeum_pattern, 0)
    ko_df["moeum_check"] = ko_df["ko"] != ""
    ko_df = ko_df.drop(columns=ko_df.columns[0])
    df["jaeum_moeum"] = ko_df.any(axis=1)

    return df


# bool_fixed
def wrong_lang_sub(lang_num_pattern, punc_pattern, sentence):
    new_sentence = re.sub(lang_num_pattern, "", sentence)
    new_sentence = re.sub(punc_pattern, "", new_sentence)
    new_sentence = (" ").join(new_sentence.split())
    if len(new_sentence) > 0:
        return False
    else:
        return True


def wrong_lang(df, col_1, col_2, lang_re_dict):
    wrong_lang_df = pd.DataFrame()
    langcode_1 = df.columns[col_1]
    langcode_2 = df.columns[col_2]
    lang_pattern_1 = lang_re_dict.get(langcode_1)
    lang_pattern_2 = lang_re_dict.get(langcode_2)
    nums_pattern = lang_re_dict.get("nums")
    lang_pattern_1 = add_two_patterns(lang_pattern_1, nums_pattern)
    lang_pattern_2 = add_two_patterns(lang_pattern_2, nums_pattern)
    puncs_pattern = lang_re_dict.get("puncs")
    wrong_lang_df["wrong_lang_1"] = df[langcode_1].map(
        wrong_lang_sub(lang_pattern_1, puncs_pattern)
    )
    wrong_lang_df["wrong_lang_2"] = df[langcode_1].map(
        wrong_lang_sub(lang_pattern_2, puncs_pattern)
    )

    # wrong_lang_df = replace_then_trim(df, wrong_lang_df, langcode_1, lang_pattern_1, 0)
    # wrong_lang_df = replace_then_trim(df, wrong_lang_df, langcode_2, lang_pattern_2, 1)
    wrong_word_count = lambda w: True if len(w) > 0 else False
    wrong_lang_df[f"not_{langcode_1}_length"] = wrong_lang_df[langcode_1].map(
        wrong_word_count
    )
    wrong_lang_df[f"not_{langcode_2}_length"] = wrong_lang_df[langcode_2].map(
        wrong_word_count
    )
    wrong_lang_df = wrong_lang_df.drop(columns=wrong_lang_df.columns[0:2])
    df = df.join(wrong_lang_df)
    return wrong_lang_df


def fasttext_detect(sentence, pretrained_m):
    detected = pretrained_m.predict(sentence)
    detected_lang = detected[0][0]
    detected_lang = detected_lang[detected_lang.rfind("_") + 1 :]
    return detected_lang


def gcld3_detect(sentence):
    detector = gcld3.NNetLanguageIdentifier(min_num_byes=0, max_num_bytes=1000)
    result = detector.FindLanguage(text=sentence)
    detected = result.language
    # ld_prob = result.probability
    return detected


def langid_detect(sentence, src, dst):
    langid.set_languages([src, dst])
    detect_tuple = langid.classify(sentence)
    detected = detect_tuple[0]
    return detected


def triple_detect(sentence, src, dst, pretrained_m):
    fasttext_res = fasttext_detect(sentence, pretrained_m)
    gcld3_res = gcld3_detect(sentence)
    langid_res = langid_detect(sentence, src, dst)
    results = [fasttext_res, gcld3_res, langid_res]
    for r in results:
        if results.count(r) >= 2:
            return True
    return False


def calculate_full_string_similarity(df, dst_col, mt_col):
    dst_list = df[df.columns[dst_col]].values.tolist()
    mt_list = df[df.columns[mt_col]].values.tolist()
    final_sim = []
    for n, d in enumerate(dst_list):
        mt_res = mt_list[n]
        sim_rate_1 = sorensen.similarity(d, mt_res)
        sim_rate_2 = ratcliff_obershelp(d, mt_res)
        avg_sim = ((sim_rate_1 * 100) + (sim_rate_2 * 100)) / 2
        final_sim.append(avg_sim)
    return final_sim


def load_MarianMT_models(src, dst):
    model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
    try:
        model = MarianMTModel.from_pretrained(model_name)
        tokenizer = MarianTokenizer.from_pretrained(model_name)
    except:
        print(f"{src} -> {dst} not found... trying: {dst} -> {src}")
        try:
            new_src = dst
            dst = src
            src = new_src
            model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
            model = MarianMTModel.from_pretrained(model_name)
            tokenizer = MarianTokenizer.from_pretrained(model_name)
        except:
            raise ValueError("No opus-mt model found")
    return model, tokenizer, src, dst


def Marian_MT(text, tok, mod):
    batch = tok.prepare_seq2seq_batch(src_texts=[text])
    gen = mod.generate(**batch)
    words = tok.batch_decode(gen, skip_special_tokens=True)
    return words[0]


def mt_sim_check(df, mt_src, mt_dst):
    sim_df = pd.DataFrame()
    marian_model, marian_tok, final_src, final_dst = load_MarianMT_models(
        mt_src, mt_dst
    )
    sim_df[final_src] = df[final_src]
    sim_df[final_dst] = df[final_dst]
    sim_df["mt_" + final_dst] = sim_df[mt_dst].map(
        lambda text: Marian_MT(text, marian_tok, marian_model)
    )
    sim_df["sim_rate"] = calculate_full_string_similarity(
        sim_df, final_dst, "mt_" + final_dst
    )
    return sim_df


if __name__ == "__main__":

    args, configs = parsers()
    input_file = configs.get("PATHS", "file_to_check")  # ko es
    input_file_name = input_file[input_file.rfind("/") + 1 :]
    model_directory = configs.get("PATHS", "model_dir")
    out_dir = configs.get("PATHS", "output_path")
    src = args.source  # ko
    dst = args.dest  # es

    patterns_dict = {
        "en": "[A-Za-z]",
        "ko": "[가-힣ㄱ-ㅎㅏ-ㅣ]",
        "ko_1": "[ㅏ-ㅣ]",
        "ko_2": "[ㄱ-ㅎ]",
        "es": "[A-Za-zÀ-ÿ]",
        "zh": "[\u4e00-\u9fff]",
        "hanja": "[一-龥]",
        "nums": "[0-9]",
        "puncs": "[^\w]",
    }

    fasttext_model = fasttext.load_model("model_directory")

    og_df = pd.read_excel(input_file)

    trimmed_df = trimmer(og_df, 1)
    trimmed_df = trimmer(trimmed_df, 2)
    trimmed_df = filter_hidden_nan(trimmed_df)
    trimmed_df = ko_weird_check(trimmed_df, patterns_dict)
    # trimmed_df = wrong_lang(trimmed_df, 1, 2, patterns_dict)
    trimmed_df = find_all_dups(trimmed_df, 1, 2, patterns_dict)
    trimmed_df = find_ratio(trimmed_df.fillna(""), 1, 2)
    trimmed_df["lang1_detect"] = trimmed_df[src].apply(
        lambda det: triple_detect(det, src, dst, fasttext_model)
    )
    trimmed_df["lang2_detect"] = trimmed_df[src].apply(
        lambda det: triple_detect(det, src, dst, fasttext_model)
    )

    work_df_bools = trimmed_df.drop(
        columns=trimmed_df.columns[:3]
    )  # drop sid, src, dst
    final_bools = work_df_bools.any(axis=1)
    trimmed_df[src] = og_df[src]
    trimmed_df[dst] = og_df[dst]
    pass_df = trimmed_df[~final_bools]
    fail_df = trimmed_df[final_bools]

    sim_checked_df = mt_sim_check(trimmed_df, src, dst)
    sim_checked_df = sim_checked_df.sort_values(by=["sim_rate"])

    pass_df.to_excel(
        os.path.join(out_dir, "pass_" + input_file_name),
        index=False,
    )
    fail_df.to_excel(
        os.path.join(out_dir, "fail_" + input_file_name),
        index=False,
    )

    sim_checked_df.to_excel(
        os.path.join(out_dir, "sim_check_" + input_file_name),
        index=False,
    )
