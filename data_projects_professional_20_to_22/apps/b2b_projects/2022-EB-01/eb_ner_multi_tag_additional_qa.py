import os
import re
from configparser import ConfigParser

import pandas as pd


def parsers():
    c_parser = ConfigParser()
    c_parser.read("eb_ner_config.ini")
    return c_parser


def set_index_for_order(df):
    total_length = len(df)
    initial_order = [
        str(t + 1).zfill(len(str(total_length))) for t in range(total_length)
    ]
    df.insert(0, "order", initial_order)
    return df


def create_custom_lower_column(df):
    pattern = "[^A-Za-z]"
    tokens_lower = df["token"].apply(
        lambda x: x.strip().lower() if isinstance(x, str) else str(x)
    )
    tokens_lower = tokens_lower.apply(
        lambda x: "" if re.sub(pattern, "", x) == "" else x
    )
    return tokens_lower


def get_multi_idx(df, lowered_tokens):
    check = []
    df2 = df.copy()
    df2["token_lower"] = lowered_tokens
    df2 = df2[df2["token_lower"] != ""]
    tgb = df2.groupby(by=["token_lower"], sort=False)
    tid = [tgb.get_group(y) for y in tgb.groups]
    for t in tid:
        multi_tags = t.drop_duplicates(subset="tag")
        if len(multi_tags) == 2:
            tag1 = ("").join(str(multi_tags.iloc[0][3]).lower().split())
            tag2 = ("").join(str(multi_tags.iloc[1][3]).lower().split())
            if (tag1 == "notag" or tag2 == "notag") and (
                tag1 == "obscure" or tag2 == "obscure"
            ):
                continue
            check.extend(t.index)
        else:
            if len(multi_tags) > 2:
                check.extend(t.index)
    df["token_lower"] = lowered_tokens
    df["multi"] = ""
    df.loc[check, "multi"] = "multi"
    return df


def set_values_over_index(df, og_col_loc, index_list, overwrite_vals):
    overwrite_vals = overwrite_vals.tolist()
    for n, i in enumerate(index_list):
        try:
            df.iat[i, og_col_loc] = overwrite_vals[n]
        except:
            print(i, og_col_loc, n)
    return df


def make_ngram_df(df):
    final_ngram_rows = []
    tot_row = len(df)
    for i_row in range(0, tot_row):
        i_token = df.iloc[i_row, 4]
        i_tag = df.iloc[i_row, 5]
        if i_tag != "":
            i_idx = df.iloc[i_row, 0]
            i_ngram = i_token
            i_finaltag = i_tag
            i_count = 1
        else:
            i_ngram = i_ngram + " " + i_token
            i_count += 1
        if i_row + 1 < tot_row:
            i_tag_next = df.iloc[i_row + 1, 5]
            if i_tag_next != "":
                if i_count > 1:
                    final_ngram_rows.append(
                        [i_idx, df.iloc[i_row, 1], i_ngram, i_finaltag, i_count]
                    )
    ngram_df = pd.DataFrame(
        data=final_ngram_rows, columns=["og_idx", "query", "token", "tag", "n_tokens"]
    )
    return ngram_df


def insert_joined_into_og(df, ngram_df):
    lower_col = create_custom_lower_column(ngram_df)
    ngram_df = get_multi_idx(ngram_df, lower_col)
    ngram_df = ngram_df[ngram_df["multi"] != ""]
    og_idx_list = []
    for i in ngram_df["og_idx"]:
        og_idx_list.append(int(i) - 1)

    df["tokens_joined"] = ""
    df["tags_joined"] = ""
    df["n_tokens"] = ""
    df["tokens_joined_lower"] = ""
    df["joined_multi"] = ""

    for i in range(0, 5):
        ngrams_col_loc = i + 2
        og_col_loc = i + 8

        df = set_values_over_index(
            df, og_col_loc, og_idx_list, ngram_df[ngram_df.columns[ngrams_col_loc]]
        )
    return df


if __name__ == "__main__":

    configs = parsers()
    tagged_file = configs.get("QA PATHS", "additional_qa")
    output_path = configs.get("QA PATHS", "ner_delivery_path")

    file_name = tagged_file.split("/")[-1]
    file_name = file_name[: file_name.rfind("_")]
    tagged_df = pd.read_excel(
        tagged_file,
        keep_default_na=False,
    )
    tagged_df = tagged_df.fillna("")
    tagged_df = tagged_df.astype(str)
    tagged_df = set_index_for_order(tagged_df)
    og_tagged_lower = create_custom_lower_column(tagged_df)
    tagged_df = get_multi_idx(tagged_df, og_tagged_lower)
    ngram_df = make_ngram_df(tagged_df)
    tagged_df = insert_joined_into_og(tagged_df, ngram_df)
    tagged_df.to_excel(
        os.path.join(output_path, file_name + "_additional_qa.xlsx"),
        index=False,
    )
