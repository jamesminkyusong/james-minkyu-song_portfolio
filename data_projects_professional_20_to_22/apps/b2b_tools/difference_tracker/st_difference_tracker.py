import difflib
import string
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st
import xlsxwriter


def contains_whitespace(s):
    return True in [c in s for c in string.whitespace]


def check_edit_pairs(original_sentence, edited_sentence):
    # print(original_sentence)
    # print(edited_sentence)
    diffs = difflib.unified_diff(
        original_sentence, edited_sentence, n=len(original_sentence)
    )
    final_string_list = []
    for n, d in enumerate(diffs):
        if n < 3:
            continue
        if d.startswith("+"):
            to_create = ["new", d[1:]]
        elif d.startswith("-"):
            to_create = ["rem", d[1:]]
        else:
            to_create = ["nothing", d[1:]]
        final_string_list.append(to_create)

    return final_string_list


def add_original_values(checkpoint_col, original_df, edited_df):
    for new_cols in edited_df.columns[checkpoint_col:]:
        og_column = original_df[new_cols].tolist()
        column_to_find = new_cols[: new_cols.rfind("_")]
        check_og_val = []
        for n, pf in enumerate(og_column):
            if not pf:
                check_og_val.append("")
            else:
                check_og_val.append(original_df[column_to_find].iloc[n])
        edited_df[f"{column_to_find}_original"] = check_og_val
    return edited_df


def find_difference_list(edited_df):
    og_finds = [c for c in edited_df.columns if c.endswith("_original")]
    all_diffs = []
    for og_col in og_finds:
        col_diffs = []
        edited = og_col[: og_col.rfind("_original")]
        for i, og in enumerate(edited_df[og_col]):
            if i == 0:
                col_diffs.append(edited + "_diffs")
            if og == "":
                col_diffs.append("")
            else:
                edited_val = edited_df[edited].iloc[i]
                if isinstance(og, np.int64):
                    col_diffs.append([["rem", str(og)], ["new", str(edited_val)]])
                else:
                    need_organize_diffs = check_edit_pairs(og, edited_val)
                    final_diffs = organize_diffs(need_organize_diffs)
                    col_diffs.append(final_diffs)
        all_diffs.append(col_diffs)
    return all_diffs


def organize_diffs(unorganized_diffs):
    final_seq = []
    adding_str = ""
    for idx, ud in enumerate(unorganized_diffs):
        if idx == 0:
            continue
        else:
            curr_format = ud[0]
            curr_diff = ud[1]
            prev_fd = unorganized_diffs[idx - 1]
            prev_format = prev_fd[0]
            adding_str = prev_fd[1]
            if curr_format != prev_format:
                final_seq.append([prev_format, adding_str])
            else:
                adding_str += curr_diff
                unorganized_diffs[idx][1] = adding_str
    if final_seq[-1][1] == adding_str:
        pass
    else:
        final_seq.append([prev_format, adding_str])
    return final_seq


def juxtapose_dfs(original_df, edited_df):
    last_og_col = len(edited_df.columns)
    bool_df = original_df != edited_df
    for x in bool_df:
        if len(bool_df[bool_df[x]]) != 0:
            edited_df[f"{x}_edited"] = bool_df[x]
            original_df[f"{x}_edited"] = bool_df[x]
    if len(edited_df.columns) == last_og_col:
        print("Both files are identical")
    else:
        edited_df = add_original_values(last_og_col, original_df, edited_df)
        diff_recorded = find_difference_list(edited_df)

    return edited_df, diff_recorded


"""
# Difference Tracker v1

"""
"""
----------------------------------------------------------------
#### Please upload the ORIGINAL excel file you want to compare.
"""

uploaded_file_1 = st.file_uploader("Choose the ORIGINAL XLSX file", type="xlsx")
if uploaded_file_1:
    df_og = pd.read_excel(uploaded_file_1)
    df_og = df_og.fillna("")
    st.dataframe(df_og)

"""
----------------------------------------------------------------
#### Please upload the EDITED excel file you want to compare.
"""

uploaded_file_2 = st.file_uploader("Choose the EDITED XLSX file", type="xlsx")
if uploaded_file_2:
    df_edited = pd.read_excel(uploaded_file_2)
    df_edited = df_edited.fillna("")
    st.dataframe(df_edited)

"""
----------------------------------------------------------------
#### This is the comparison between the first file and the second file.
"""

if uploaded_file_2 is not None:
    final_df = None
    final_df, all_diffs = juxtapose_dfs(df_og, df_edited)
    final_df = final_df.astype(str)
    st.dataframe(final_df)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()

    for col_idx, col in enumerate(final_df):
        col_loc = string.ascii_uppercase[col_idx]
        for cidx, cell in enumerate(final_df[col].tolist()):
            if cidx == 0:
                worksheet.write(col_loc + str(cidx + 1), col)
            worksheet.write(col_loc + str(cidx + 2), cell)

    start_diff = len(final_df.columns)

    rem = workbook.add_format({"color": "red", "font_strikeout": True})
    new = workbook.add_format({"color": "blue"})
    for n, diffs in enumerate(all_diffs):
        col_loc = string.ascii_uppercase[start_diff + n]
        for didx, diff in enumerate(diffs):
            if didx == 0:
                worksheet.write(col_loc + str(didx + 1), diff)
                continue
            if diff == "":
                continue
            else:
                print(diff)
                final_sequence = []
                for fmt, d in diff:
                    if fmt == "new":
                        final_sequence.append(new)
                        final_sequence.append(d)
                    elif fmt == "rem":
                        final_sequence.append(rem)
                        final_sequence.append(d)
                    else:
                        final_sequence.append(d)
                worksheet.write_rich_string(col_loc + str(didx + 1), *final_sequence)
    workbook.close()

    """
    ----------------------------------------------------------------
    #### The differences have been tracked! Press to download the excel file! 
    """
    filename = st.text_input("Please input the final name of the result excel file : ")
    if filename.find(".xlsx") == -1:
        filename = filename + ".xlsx"
    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel",
    )
