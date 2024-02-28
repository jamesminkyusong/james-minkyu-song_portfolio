from multiprocessing.sharedctypes import Value
import pandas as pd
from pydantic import ByteSize
import streamlit as st
import string
from textacy import preprocessing
from io import BytesIO
import xlsxwriter


def replace_emojis(sentence):
    replaced_sentence = preprocessing.replace.emojis(sentence, " ")
    return replaced_sentence


def replace_spaces(sentence):
    sentence = str(sentence)
    sentence_split = sentence.split()
    if len(sentence_split) == 1:
        sentence_joined = sentence.strip()
    else:
        sentence_joined = ("").join(sentence_split)
    return sentence_joined


def st_read_excel(input_statement):
    df = None
    up_file = st.file_uploader(input_statement, type="xlsx")
    if up_file:
        df = pd.read_excel(up_file, keep_default_na=False)
        df = df.fillna("")
        df = df.astype(str)
        df = df.rename(columns=lambda x: x.strip())
    if df is not None:
        st.dataframe(df)
    return df


def checkbox_container(s, data):

    if data[0] not in st.session_state.keys():
        dummy_data = data
        st.session_state["dummy_data"] = dummy_data
    else:
        dummy_data.extend(data)
    checkbox_count = len(data)
    checkboxes = [1 for _ in range(checkbox_count)]
    for n, x in enumerate(st.columns(checkboxes)):
        with x:
            st.checkbox(data[n], key=f"dynamic_checkbox_{s}_" + data[n])


def get_selected_checkboxes(s):
    return [
        i.replace(f"dynamic_checkbox_{s}_", "")
        for i in st.session_state.keys()
        if i.startswith(f"dynamic_checkbox_{s}_") and st.session_state[i]
    ]


def check_more_dups(df, col):
    if col in ["sid", "no", "No", "SID", "Sid"]:
        df[col + "_dups"] = df[col].duplicated(keep=False)
        return df
    lowered_src = df[col].apply(lambda x: x.casefold())
    lowered_src = lowered_src.apply(
        lambda x: x.translate(str.maketrans("", "", string.punctuation))
    )
    lowered_src = lowered_src.map(replace_emojis)
    lowered_src = lowered_src.map(replace_spaces)
    additional_dups = lowered_src.duplicated(keep=False)
    if len(df[additional_dups]) > 0:
        df[col + "_dups"] = additional_dups
    return df


def check_if_export(df, og_col):
    if len(og_col) == len(df.columns):
        st.write("NO Duplicates Found!")
        return None, None
    else:
        dups_bool = df[df.columns[len(og_col) :]]
        final_dups_bool = dups_bool.any(axis=1)
        no_dups_df = df[~final_dups_bool]
        all_dups_df = df[final_dups_bool]
        no_dups_df = no_dups_df[no_dups_df.columns[: len(og_col)]]
        return no_dups_df, all_dups_df


"""
# Duplicates Finder

"""
"""
----------------------------------------------------------------
#### Do you want to find duplicates in ONE file or TWO files?
"""

col0, col1, col2, col3 = st.columns([1, 1, 1, 1])
with col1:
    res1 = st.checkbox("ONE")
with col2:
    res2 = st.checkbox("TWO")

df_1 = None
df_2 = None
if res1:
    df_1 = st_read_excel("Choose the XLSX file")
elif res2:
    df_1 = st_read_excel("Choose the first XLSX file")

    df_2 = st_read_excel("Choose the second XLSX file")
    if df_1 is not None and df_2 is not None:
        df_1["file_track"] = "first"
        df_2["file_track"] = "second"
        try:
            df_1 = df_1.append(df_2, ignore_index=True)
        except:
            st.write("check if column name matches")
            raise ValueError("Column Name Does not Match")
else:
    pass


if df_1 is not None:
    og_df_cols = df_1.columns.tolist()
    check_df_cols = df_1.columns.tolist()
    if "file_track" in check_df_cols:
        check_df_cols.remove("file_track")
    """
    ----------------------------------------------------------------
    #### Which columns would you like to check for duplicates?
    """
    selected_cols = None
    checkbox_container("check2", check_df_cols)
    # st.write("You selected:")
    # st.write(get_selected_checkboxes("check2"))
    selected_cols = get_selected_checkboxes("check2")
    if selected_cols is not None:
        cols = sorted(
            [[df_1.columns.to_list().index(c), c] for c in selected_cols],
            key=lambda x: x[0],
        )
        for i, col in cols:
            pure_dup = df_1[col].duplicated(keep=False)
            if len(df_1[pure_dup]) > 0:
                # df_1[col + "_pure_dups"] = pure_dup
                df_1 = check_more_dups(df_1, col)
            else:
                pass
        dups_rmvd_df, all_dups_df = check_if_export(df_1, og_df_cols)

        if dups_rmvd_df is not None and all_dups_df is not None:
            output1 = BytesIO()
            output2 = BytesIO()

            workbook1 = xlsxwriter.Workbook(output1, {"in_memory": True})
            worksheet1 = workbook1.add_worksheet()

            workbook2 = xlsxwriter.Workbook(output2, {"in_memory": True})
            worksheet2 = workbook2.add_worksheet()

            for col_idx, col in enumerate(dups_rmvd_df):
                col_loc = string.ascii_uppercase[col_idx]
                for cidx, cell in enumerate(dups_rmvd_df[col].tolist()):
                    if cidx == 0:
                        worksheet1.write(col_loc + str(cidx + 1), col)
                    worksheet1.write(col_loc + str(cidx + 2), cell)
            workbook1.close()

            for col_idx, col in enumerate(all_dups_df):
                col_loc = string.ascii_uppercase[col_idx]
                for cidx, cell in enumerate(all_dups_df[col].tolist()):
                    if cidx == 0:
                        worksheet2.write(col_loc + str(cidx + 1), col)
                    worksheet2.write(col_loc + str(cidx + 2), cell)
            workbook2.close()

            filename1 = st.text_input(
                "Please input the final name of NO DUPS excel file: "
            )
            if filename1.find(".xlsx") == -1:
                filename1 = filename1 + ".xlsx"
            st.download_button(
                label="Download Excel workbook",
                data=output1.getvalue(),
                file_name=filename1,
                mime="application/vnd.ms-excel",
            )
            filename2 = st.text_input(
                "Please input the final name of the ONLY DUPS excel file: "
            )
            if filename2.find(".xlsx") == -1:
                filename2 = filename2 + ".xlsx"
            st.download_button(
                label="Download Excel workbook",
                data=output2.getvalue(),
                file_name=filename2,
                mime="application/vnd.ms-excel",
            )
