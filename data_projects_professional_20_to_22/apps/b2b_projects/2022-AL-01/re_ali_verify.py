import os
import pandas as pd
import string
from configparser import ConfigParser


def get_only_valid_excels(path):
    translated_files = sorted(os.listdir(path))
    translated_excels = []
    for tf in translated_files:
        if tf.endswith(".xlsx") and not tf.startswith("~"):
            translated_excels.append(tf)
    return translated_excels


def find_original_in_folder(og_path, rework_path):
    rework_files = os.listdir(rework_path)
    translated_excels = get_only_valid_excels(og_path)
    found_list = []
    not_found_list = []
    for r in rework_files:
        found_status = False
        og_r = r
        if r.startswith("."):
            continue
        if r[:2].isalpha():
            r = r[3:]
        r = r[: r.rfind("_")]
        if r.startswith("_"):
            r = r[1:]
        print(r)
        for te in translated_excels:
            if te.find(r) != -1:
                found_list.append(
                    [os.path.join(rework_path, og_r), os.path.join(og_path, te)]
                )
                found_status = True
        if found_status == False:
            not_found_list.append(og_r)
    if len(not_found_list) > 0:
        print(not_found_list)
        raise ValueError("Some files were not found")
    else:
        return found_list


def change_source_for_comparison(df):
    df_source = df[df.columns[1]]
    df_source = df_source.apply(lambda x: ("").join(str(x).lower().split()))
    df_source_to_compare = df_source.apply(
        lambda y: y.translate(str.maketrans("", "", string.punctuation))
    )
    return df_source_to_compare


def overwrite_tcs(updated_df, old_df):
    new_tc_start = updated_df[updated_df.columns[2]]
    new_tc_end = updated_df[updated_df.columns[3]]
    old_df[old_df.columns[2]] = new_tc_start
    old_df[old_df.columns[3]] = new_tc_end
    return old_df


def compare_sources(updated_df, old_df, move_status):
    old_df = overwrite_tcs(updated_df, old_df)
    new_df_source = change_source_for_comparison(updated_df)
    old_df_source = change_source_for_comparison(old_df)
    source_compare_bool = old_df_source == new_df_source
    if len(old_df[source_compare_bool]) != len(old_df):
        move_status = "fail_new"
        old_df["new_subtitile"] = updated_df[updated_df.columns[1]]
        old_df["check_edits"] = ~source_compare_bool
    else:
        move_status = "pass"
    return old_df, move_status


def compare_lengths_and_sources(
    updated_file, updated_df, old_file, old_df, errors_list, move_loc
):
    if len(updated_df) != len(old_df):
        errors_list.append(
            [
                updated_file,
                old_file,
                f"{len(updated_df)} != {len(old_df)} length_mismatch",
            ]
        )
        return old_df, errors_list, move_loc
    else:
        old_df, move_loc = compare_sources(updated_df, old_df, move_loc)
        if move_loc == "fail_new":
            diff_len = len(old_df[old_df["check_edits"]])
            errors_list.append(
                [updated_file, old_file, f"{diff_len} source line(s) are mismatch"]
            )
        return old_df, errors_list, move_loc


def compare_new_to_origin(found_files_dir_paired, pass_path, fail_path):
    errors_all = []
    for re_worked, old_deliv in found_files_dir_paired:
        move_loc = "fail_move"
        new_filename = re_worked.split("/")[-1]
        old_filename = old_deliv.split("/")[-1]
        new_df = pd.read_excel(re_worked)
        new_df = new_df.fillna("")
        old_df = pd.read_excel(old_deliv)
        old_df = old_df.fillna("")
        old_df, errors_all, move_loc = compare_lengths_and_sources(
            new_filename, new_df, old_filename, old_df, errors_all, move_loc
        )
        if move_loc == "fail_move":
            os.rename(re_worked, os.path.join(fail_path, "fail_lm_" + new_filename))
        elif move_loc == "fail_new":
            old_df.to_excel(
                os.path.join(fail_path, "fail_sm_" + new_filename), index=False
            )
        else:
            old_df.to_excel(
                os.path.join(pass_path, "pass_" + new_filename), index=False
            )
    return errors_all


if __name__ == "__main__":
    translated_path = (
        r"/Users/jamessong/Downloads/alibaba_check/etc_out/xlsx"  # 전체 원본 폴더
    )
    rework_path = r"/Users/jamessong/Downloads/alibaba_check/re_works/re_04_2_en"  # (xlsx로 변환된) 요청 받은 폴더
    p_path = r"/Users/jamessong/Desktop/IO/try1/p"  # 통과 파일 (tc overwrite 되있음)
    f_path = r"/Users/jamessong/Desktop/IO/try1/f"  # fail 파일 (lm = length mismatch, sm = source transcription mismatch)

    files_found_dirs = find_original_in_folder(translated_path, rework_path)
    errors_list = compare_new_to_origin(files_found_dirs, p_path, f_path)
    if len(errors_list) > 0:
        error_df = pd.DataFrame(errors_list)
        error_df.to_excel(os.path.join(f_path, "errors_redeliv_ali.xlsx"), index=False)
