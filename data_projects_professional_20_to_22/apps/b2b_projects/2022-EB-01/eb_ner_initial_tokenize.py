import os
import pandas as pd
from configparser import ConfigParser


def parsers():
    c_parser = ConfigParser()
    c_parser.read("eb_ner_config.ini")
    return c_parser


def eb_txt_reader(tsv_file_path):
    queries = []
    try:
        df = pd.read_csv(tsv_file_path, sep="\t", header=None)
        dropped_df = df.dropna()
        if len(df) != len(dropped_df) or len(df.columns) < 2:
            raise ValueError("wrong tsv format")
        else:
            df = df.rename(columns={0: "ebay_id", 1: "query"})
    except:
        with open(tsv_file_path, "r") as text:
            for t in text:
                sid = t[: t.find(" ")]
                query = t[t.find(" ") + 1 :]
                query = query.replace("\n", "")
                sid = int(sid)
                queries.append([sid, query])
        df = pd.DataFrame(data=queries, columns=["ebay_id", "query"])
    return df


def base_tokenize(df):
    queries = df["query"].tolist()
    dups_q = df["query"][df["query"].duplicated(keep="first")].tolist()
    for n, q in enumerate(queries):
        each_data = []
        q_split = q.split()

        for qs in q_split:
            if q in dups_q:
                each_data.append([str(q), str(qs), "", str(qs), "", "dup"])
            else:
                each_data.append([str(q), str(qs), "", str(qs), "", ""])
        if n == 0:
            master_df = pd.DataFrame(
                data=each_data,
                columns=["query", "token", "tag", "span_token", "span_tag", "dups"],
            )
        else:
            append_df = pd.DataFrame(
                data=each_data,
                columns=["query", "token", "tag", "span_token", "span_tag", "dups"],
            )
            master_df = master_df.append(append_df, ignore_index=True)
    return master_df


if __name__ == "__main__":
    configs = parsers()
    ner_og_txt_path = configs.get("QA PATHS", "ner_og_directory")
    df = eb_txt_reader(ner_og_txt_path)

    tokenized_done = base_tokenize(df)
    out_file = ner_og_txt_path.split("/")[-1]
    out_file = out_file[: out_file.rfind(".")]
    out_file = out_file + ".xlsx"
    out_path = ("/").join(ner_og_txt_path.split("/")[:-1])
    tokenized_done.to_excel(
        os.path.join(out_path, "tokenized_" + out_file), index=False
    )
