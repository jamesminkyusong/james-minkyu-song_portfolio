import os
import csv
from configparser import ConfigParser
from eb_ner_initial_tokenize import eb_txt_reader
import pandas as pd


def parsers():
    c_parser = ConfigParser()
    c_parser.read("eb_ner_config.ini")
    return c_parser


def fix_queries_by_index(df, idx):
    token_before = df["token"].iloc[idx - 1]
    query_bbefore = df["query"].iloc[idx - 2]

    query_before = df["query"].iloc[idx - 1]
    try:
        query_after = df["query"].iloc[idx + 1]
    except:
        print(df["query"].iloc[0])
        return df
    try:
        query_aafter = df["query"].iloc[idx + 2]
    except:
        print(df["query"].iloc[0])
        return df
    token_after = df["token"].iloc[idx + 1]
    if query_before == query_after:
        df.iat[idx, 0] = query_before
    elif query_bbefore == query_aafter:
        df.iat[idx, 0] = query_before
    else:
        qb_split = query_before.split()
        qa_split = query_after.split()
        if len(qb_split) == 1 or len(qa_split) == 1:
            print(df["query"].iloc[0])
            return df
        if qb_split[-2] == token_before:
            df.iat[idx, 0] = query_before
        elif qa_split[1] == token_after:
            df.iat[idx, 0] = query_after
        else:
            pass
    return df


def check_token_span_token(worked_df, errors_list):
    token_list = worked_df["token"].tolist()
    span_list = worked_df["span_token"].tolist()

    for n, t in enumerate(token_list):
        if t != span_list[n]:
            errors_list.append([n, f"token: {t}, span: {span_list[n]}"])
    return errors_list


def check_queries_to_og(og_txt_list, df, errors_list):
    query_worked = df["query"].drop_duplicates().tolist()
    for n, f in enumerate(query_worked):
        if f not in og_txt_list:
            print(f"not working : {f}")
            check_idx = df[df["query"] == f].index.tolist()
            for cidx in check_idx:
                df = fix_queries_by_index(df, cidx)
            errors_list.append([query_worked[n], "query not in og_query"])
    query_worked = df["query"].drop_duplicates().tolist()
    for n, f in enumerate((pd.Series(og_txt_list).drop_duplicates().tolist())):
        if f != query_worked[n]:
            print(f)
            check_idx = df[df["query"] == f].index.tolist()
            for cidx in check_idx:
                df = fix_queries_by_index(df, cidx)
            errors_list.append([query_worked[n], "query different from og_query"])

    return worked_df, errors_list


def sentence_match(grouped_df, sentence, errors_list):
    sentence = (" ").join(sentence.split())
    g_df_token = grouped_df["token"].tolist()
    sentence_token_list = []
    for g in g_df_token:
        sentence_token_list.append(str(g))
    sentence_check = (" ").join(sentence_token_list)
    if sentence != sentence_check:
        print(sentence_check)
        errors_list.append([sentence, "sentence does not match tokens"])
    return errors_list


def check_sentences_query_token(df, errors_list):
    gb = df.groupby("query", sort=False)
    wq = [gb.get_group(y) for y in gb.groups]
    for q_df in wq:
        chunks = []
        sentence = q_df["query"].iloc[0]
        sentence_token_count = len(sentence.split())
        if len(q_df) != sentence_token_count:
            if len(q_df) % sentence_token_count == 0:
                chunks = [
                    q_df[x : x + sentence_token_count]
                    for x in range(0, len(q_df), sentence_token_count)
                ]
        if len(chunks) != 0:
            for c in chunks:
                errors_list = sentence_match(c, sentence, errors_list)
        else:
            errors_list = sentence_match(q_df, sentence, errors_list)
    return errors_list


def fix_tags(fix_tags_keys, error_lower_no_space):
    og_error_t = error_lower_no_space
    for ft in fix_tags_keys:
        if len(ft) < len(error_lower_no_space):
            error_lower_no_space = error_lower_no_space[: len(ft)]
        else:
            pass
        if ft.find(error_lower_no_space) != -1:
            error_lower_no_space = ft
            return error_lower_no_space
        else:
            error_lower_no_space = og_error_t
    return error_lower_no_space


def check_tags(df, tagset, fix_tagset, error_list):
    columns = ["tag", "span_tag"]
    fix_tagset_keys = list(fix_tagset)
    for c in columns:
        df[c] = df[c].apply(lambda x: (" ").join(x.split()))
        tag_col_list = df[c].tolist()
        for n, t in enumerate(tag_col_list):
            if t == "":
                continue
            sentence = df["query"].iloc[n]
            track_error = []
            if t not in tagset:
                track_error.append(t)
                if t.capitalize() in tagset != None:
                    tag_col_list[n] = t.capitalize()
                    error_list.append([sentence, f"auto: {t} --> {t.capitalize()}"])
                    continue
                if (" ").join(t.title().split()) in tagset != None:
                    new_titlized_tag = (" ").join(t.title().split())
                    tag_col_list[n] = new_titlized_tag

                    error_list.append([sentence, f"auto: {t} --> {new_titlized_tag}"])
                    continue
                error_t = ("").join(t.lower().split())
                curr_error_t = error_t
                error_t = fix_tags(fix_tagset_keys, error_t)
                if curr_error_t != error_t:
                    track_error.append(error_t)
                    tracked = (" --> ").join(track_error)
                else:
                    tracked = track_error[0]
                error_list.append([sentence, tracked])
                if error_t not in tagset:
                    error_list.append([sentence, error_t])
                    continue
                else:
                    right_tag = fix_tagset.get(error_t)
                    tag_col_list[n] = right_tag
            else:
                pass
        df[c] = tag_col_list
    return df, error_list


def check_tag_span_tag(df, errors_list):
    no_blanks_df = df[df["span_tag"] != ""]
    tags_list = no_blanks_df["tag"].tolist()
    span_tags_list = no_blanks_df["span_tag"].tolist()

    for n, t in enumerate(tags_list):
        sentence = no_blanks_df["query"].iloc[n]
        if t != span_tags_list[n]:
            errors_list.append([sentence, f"tag: {t}, span_tag:{span_tags_list[n]}"])
    return errors_list


if __name__ == "__main__":
    configs = parsers()
    ner_og_txt_path = configs.get("QA PATHS", "ner_og_directory")
    worked_xl_path = configs.get("QA PATHS", "worked_file")
    ner_tagset_path = configs.get("QA PATHS", "ner_tagset")
    output_path = configs.get("QA PATHS", "ner_delivery_path")

    # save below as comments - keep in mind to fix spacing fix for sneakers delivery)
    # fixing spacing for this sneakers delivery
    # with open(ner_og_txt_path, "r") as txtfile:
    #     txtlines = txtfile.readlines()
    # for n, t in enumerate(txtlines):
    #     space_loc = t.find(" ")
    #     text = t[space_loc + 1 :]
    #     txtlines[n] = text[:-1]
    # first_og_100 = txtlines[100:]

    # og_df = pd.read_csv(ner_og_txt_path, sep="\t", header=None)
    # first_og_100 = og_df[1][0:100].tolist()
    tagset_df = pd.read_excel(ner_tagset_path)
    tagset = tagset_df["Tag"].tolist()

    worked_df = pd.read_excel(worked_xl_path, keep_default_na=False)
    worked_df = worked_df.fillna("")
    worked_df = worked_df.astype("str")

    og_df = eb_txt_reader(ner_og_txt_path)
    queries = og_df[og_df.columns[1]].tolist()
    first_query_loc = queries.index(worked_df[worked_df.columns[0]].iloc[0])
    print(first_query_loc)
    print(worked_df[worked_df.columns[0]].iloc[0])
    last_query_loc = queries.index(worked_df[worked_df.columns[0]].iloc[-1])
    print(last_query_loc)
    print(worked_df[worked_df.columns[0]].iloc[-1])

    first_og_100 = queries[first_query_loc : last_query_loc + 1]

    fix_tags_dict = {}
    for tag in tagset:
        tagset_broken = tag.lower()
        tagset_broken = ("").join(tagset_broken.split())
        fix_tags_dict[tagset_broken] = tag

    file_name = worked_xl_path.split("/")[-1]
    file_name = file_name[: file_name.rfind(".")]
    errors = []
    worked_df, errors = check_queries_to_og(first_og_100, worked_df, errors)
    errors = check_token_span_token(worked_df, errors)
    errors = check_sentences_query_token(worked_df, errors)
    worked_df, errors = check_tags(worked_df, tagset, fix_tags_dict, errors)
    errors = check_tag_span_tag(worked_df, errors)
    # print(errors)
    worked_df.to_csv(
        os.path.join(output_path, file_name + "_delivery.tsv"),
        sep="\t",
        quoting=csv.QUOTE_NONE,
        index=False,
    )
    worked_df.to_excel(
        os.path.join(output_path, file_name + "_delivery.xlsx"), index=False
    )
    pd.DataFrame(data=errors, columns=["reference", "type"]).to_excel(
        os.path.join(output_path, file_name + "_errors.xlsx"), index=False
    )
