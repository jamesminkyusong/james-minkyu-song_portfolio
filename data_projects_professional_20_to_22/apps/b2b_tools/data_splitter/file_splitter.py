import os
import pandas as pd


def splitter(df, split_len):
    split_up = [
        df[i * split_len : (i + 1) * split_len]
        for i in range((len(df) + split_len - 1) // split_len)
    ]
    if len(split_up) > 1:
        if len(split_up[-1]) <= split_len // 2:
            to_append = split_up[-1]
            before_append = split_up[-2]
            split_up[-2] = before_append.append(to_append, ignore_index=True)
            split_up = split_up[:-1]
    return split_up


def file_namer(f_name, splitted):
    excel_name = f_name[: f_name.rfind(".")]
    final_names = [
        excel_name
        + "_"
        + str(i).zfill(len(str(len(splitted))))
        + "_"
        + str(len(splitted[i - 1]))
        + ".xlsx"
        for i in range(1, len(splitted) + 1)
    ]
    return excel_name, final_names


def split_and_save(idir, odir, split_by, save_by):
    for f in sorted(os.listdir(idir)):
        if f.startswith("~") or f.startswith(".") or not f.endswith(".xlsx"):
            print(f"{f} is not supported file type")
            continue
        df_to_split = pd.read_excel(os.path.join(idir, f))
        df_to_split = df_to_split.fillna("")
        split_by = int(split_by)
        split_up_dfs = splitter(df_to_split, split_by)
        folder_name, final_names = file_namer(f, split_up_dfs)
        if save_by == "y":
            curr_dir = os.path.join(odir, folder_name)
            os.mkdir(curr_dir)
        else:
            curr_dir = out_dir
        for n, split_file in enumerate(final_names):
            split_up_dfs[n].to_excel(os.path.join(curr_dir, split_file), index=False)
        print(f"{f} split complete.")
    print(f"All files split complete.")


if __name__ == "__main__":
    print("Select input folder directory: ")
    today_dir = input()
    today_dir = today_dir.strip()
    print("input directory is set at: " + today_dir)
    print()

    print("Select output folder directory: ")
    out_dir = input()
    out_dir = out_dir.strip()
    print("output directory is set at: " + out_dir)
    print()

    print("Select row split unit : ")
    split_length = input()

    print("Do you want to create an output folder for each file?")
    print("y/n")
    save_by_folder = input()
    print()

    print(f"File splitting will begin. The file will split by each {split_length} rows.")
    if save_by_folder == "y":
        print(f"Output files will be saved in each separate folder under : {out_dir}")
    elif save_by_folder == "n":
        print(f"Output files will be saved under : {out_dir}")
    else:
        raise ValueError("Please restart the program. There is an error in the input.")

    split_and_save(today_dir, out_dir, split_length, save_by_folder)

# how to create .exe file for distribution
# pip install pyinstaller
# # after cd to the folder where this script exists
# pyinstaller --onefile file_splitter.py
