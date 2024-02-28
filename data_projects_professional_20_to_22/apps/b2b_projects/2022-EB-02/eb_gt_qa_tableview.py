import argparse
import os
from configparser import ConfigParser

import pandas as pd


def parsers():
    c_parser = ConfigParser()

    parser = argparse.ArgumentParser(description="gt_tableview: input output filename")
    parser.add_argument(
        "-oname",
        "--outname",
        type=str,
        metavar="",
        required=True,
        help="final name of the tableview file",
    )
    args = parser.parse_args()
    c_parser.read("gt_config.ini")
    return args, c_parser


def qa_df(df, filename_s, standard_row_names, standard_shape):
    if df[0].values.tolist() != standard_row_names:
        print(f"{filename_s}: row_names wrong")
        df = df.iloc[0 : standard_shape[0], 0 : standard_shape[1] + 1]
    else:
        pass
    df.insert(0, "File Name", filename_s)
    standard_top = df[:2]
    standard_top = standard_top.iloc[:, :3]
    standard_top_files = standard_top["File Name"]
    standard_top_items = standard_top[0]
    standard_top_values = standard_top[1]
    standard_bottom = df.iloc[:, 1:8]
    standard_bottom = standard_bottom[2:]
    standard_bottom = standard_bottom.T.fillna("")

    standard_bottom.insert(0, "0", standard_top_files)
    standard_bottom.insert(1, "1", standard_top_items)
    standard_bottom.insert(2, "2", standard_top_values)
    df = standard_bottom.fillna("")
    df[df.columns[0]] = filename_s.loc[0]
    return df


def compile_df(indir, std_dir, ogs, fixed_dir):
    standard = pd.read_excel(std_dir, header=None)
    if standard.iloc[0][0] != "Item Title":

        ####################################################
        standard_og_file = std_dir.split("/")[-1]
        standard_og_file = standard_og_file[: standard_og_file.rfind("_")] + ".xlsx"
        std_og_df = pd.read_excel(os.path.join(ogs, standard_og_file), header=None)
        std_og_df = std_og_df.fillna("")
        std_item_title = std_og_df.iloc[0]
        standard.loc[-1] = std_item_title
        standard.index = standard.index + 1
        standard = standard.sort_index()
        ####################################################
    else:
        pass

    standard_row = standard[0].values.tolist()
    standard_shpe = standard.shape
    worklist = os.listdir(indir)
    for n, f in enumerate(worklist):
        if f.startswith(".") or f.startswith("~"):
            continue
        # print(f)
        filename_s = pd.Series(data=f)
        filepath = os.path.join(indir, f)
        if n == 0:
            master_df = pd.read_excel(filepath, header=None)
            if master_df.iloc[0][0] != "Item Title":
                ###################################
                og_file = f[: f.rfind("_")] + ".xlsx"
                og_df = pd.read_excel(os.path.join(ogs, og_file), header=None)
                og_df = og_df.fillna("")
                item_title = og_df.iloc[0]
                master_df.loc[-1] = item_title
                master_df.index = master_df.index + 1
                master_df = master_df.sort_index()
                master_df.to_excel(os.path.join(fixed_dir, f), index=False, header=None)
                ###################################
            master_df = qa_df(master_df, filename_s, standard_row, standard_shpe)
        else:
            adding_df = pd.read_excel(filepath, header=None)
            if adding_df.iloc[0][0] != "Item Title":
                ###################################
                og_file = f[: f.rfind("_")] + ".xlsx"
                og_df = pd.read_excel(os.path.join(ogs, og_file), header=None)
                og_df = og_df.fillna("")
                item_title = og_df.iloc[0]
                adding_df.loc[-1] = item_title
                adding_df.index = adding_df.index + 1
                adding_df = adding_df.sort_index()
                adding_df.to_excel(os.path.join(fixed_dir, f), index=False, header=None)
            ###################################
            adding_df = qa_df(adding_df, filename_s, standard_row, standard_shpe)
            master_df = master_df.append(adding_df, ignore_index=True)
    return master_df


def add_blank_details(table_view_df):
    all_values = table_view_df.values.tolist()

    tag_counts = []
    blank_bool = []
    for n, row in enumerate(all_values):
        if n == 0:
            tag_counts.append("tag_counts")
            blank_bool.append("blank_row")
            continue

        row_type = row[3]
        if (
            row_type == "Entity Tags"
            or row_type == "Image"
            or row_type == "Conflict Resolution Value"
            or row_type == "Resolution Comment"
        ):
            tag_counts.append("***")
            blank_bool.append("***")
        else:
            curr_row = row[4:]
            curr_row = list(map(lambda x: (" ").join(str(x).split()), curr_row))
            tag_counts.append(int(len(curr_row) - curr_row.count("")))
            if len(curr_row) == curr_row.count(""):

                blank_bool.append(True)
            else:
                blank_bool.append(False)
    table_view_df["tag_counts"] = tag_counts
    table_view_df["blank_row"] = blank_bool
    return table_view_df


if __name__ == "__main__":
    __args, configs = parsers()

    directory = configs.get("QA PATHS", "gt_tv_directory")
    original_path = configs.get("QA PATHS", "empty_files_directory")
    fixed_path = configs.get("QA PATHS", "fixed_out_dir")
    outputpath = configs.get("QA PATHS", "output_directory")
    standard_f = os.path.join(directory, sorted(os.listdir(directory))[3])

    final_qa_df = compile_df(directory, standard_f, original_path, fixed_path)
    final_qa_df = add_blank_details(final_qa_df)
    final_qa_df.to_excel(
        os.path.join(outputpath, __args.outname + ".xlsx"), index=False, header=None
    )
