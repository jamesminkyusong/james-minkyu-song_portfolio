import argparse
import os
import pandas as pd
import logging
import re


parser = argparse.ArgumentParser(description="Excel to text for delivery")
parser.add_argument(
    "-idir", "--input", type=str, metavar="", required=True, help="input directory"
)

parser.add_argument(
    "-odir", "--output", type=str, metavar="", required=True, help="output directory"
)

args = parser.parse_args()

logging.basicConfig(
    filename=r"C:\Users\flitto\Desktop\vswd\logfiles\ali_excel_txt.log",
    level=logging.INFO,
)

# 구글시트에서 받은 파일명 id와 납품파일명 포맷의 전처리
# rename_csv = pd.read_csv(
#     r"C:\Users\flitto\Desktop\vswd\delivery\ali\excel_to_deliveryname.csv",
#     header=None,
#     dtype=str,
#     encoding="utf-8",
# )
# rename_csv.dtypes
# rename_csv[rename_csv.columns[2]] = rename_csv[rename_csv.columns[2]].str.zfill(4)
# excel_name = (
#     rename_csv[rename_csv.columns[0]]
#     + "_"
#     + rename_csv[rename_csv.columns[1]]
#     + rename_csv[rename_csv.columns[2]]
#     + ".xlsx"
# )

# rename_csv = rename_csv.drop(rename_csv.columns[0:3], axis=1)
# rename_csv.insert(0, "excel name", excel_name)
# rename_csv.columns = ["excel_name", "txt_name"]
# rename_csv.to_csv(
#     "fixed_excel_to_deliveryname.csv", index=False, header=True, encoding="utf-8"
# )

# 파일명 마스터 시트
fixed_rename_df = pd.read_csv(
    r"C:\Users\flitto\Desktop\vswd\delivery\ali\fixed_excel_to_deliveryname.csv",
    encoding="utf-8",
)

# 내부 관리용 파일명 양식에서 -> 납품 파일명으로 양식 변환을 위한 dict 생성
name_dict = dict(zip(fixed_rename_df["excel_name"], fixed_rename_df["txt_name"]))


def empty_cells(df):
    return sum([df[x].isna().sum() for x in df]) > 0


def tc_reformat(tc, fname):
    tc = ("").join(tc.split())
    end_col = tc.rfind(":")

    if len(tc[end_col + 1 :]) > 3:
        pass
    else:
        tc = tc[:end_col] + "," + tc[end_col + 1 :]
    tc = time_code_check(tc, fname)

    return tc


def time_code_check(tc, file_name):
    tc = ("").join(str(tc).split())
    try:
        if tc[-4] != "," or len(tc) != 12:
            logging.warning(
                f"Operation: Textify       File: {file_name}: {tc: <30} ERROR TYPE: tc error"
            )
            # raise ValueError("Timecode in wrong format.")
    except:
        logging.warning(
            f"Operation: Textify       File: {file_name}: {tc: <30} ERROR TYPE: tc error"
        )
        # raise ValueError("Timecode in wrong format.")
    return tc


def replace_for_comparison(tc):
    tc = tc.replace(":", "")
    tc = tc.replace(",", ".")
    tc = float(tc)
    return tc


def tc_qc(timecode_beg, timecode_end, file_name):
    timecode_beg = timecode_beg.tolist()
    timecode_end = timecode_end.tolist()
    for n, b in enumerate(timecode_beg):
        e = timecode_end[n]
        if b.find(",") != -1 and e.find(",") != -1:
            if n == 0:
                fixed_prev_e = float(0)
            else:
                prev_e = timecode_end[n - 1]
                fixed_prev_e = replace_for_comparison(prev_e)
            fixed_b = replace_for_comparison(b)
            fixed_e = replace_for_comparison(e)
            try:
                if fixed_b >= fixed_e:
                    logging.warning(
                        f"Operation: Textify       File: {file_name: <40} ERROR TYPE: timecode1 {n+1}  {b, e}"
                    )
                if fixed_prev_e > fixed_b:
                    logging.warning(
                        f"Operation: Textify       File: {file_name: <40} ERROR TYPE: timecode2 {n+1}  {fixed_prev_e, fixed_b}"
                    )
            except:
                logging.warning(
                    f"Operation: Textify       File: {file_name: <40} ERROR TYPE: timecode3 {n+1}  {b, e}"
                )
        else:
            logging.warning(
                f"Operation: Textify       File: {file_name: <40} ERROR TYPE: timecode3 {n+1}  {b, e}"
            )


def remove_breaks(str_or_list):  # 각 줄마다 있는 \n 제거
    if isinstance(str_or_list, str):
        script = re.sub("[\n]", "", str_or_list)  # 한 숫자에 한줄의 transcription만 있으면 그냥 제거
        return script


def reshape_df(df):
    input_lang = df[df.columns[0]][0]
    input_lang = str(input_lang).lower()
    if input_lang == "en" or input_lang == "fr":
        # en/fr = lang1, line1, tc1, tc2, lang2, translation2, lang3, translation3
        if len(df.columns) != 8:
            df = df.drop(columns=df.columns[8:])
    elif input_lang == "zh":
        # zh -> ENFRPT
        if len(df.columns) != 10:
            df = df.drop(columns=df.columns[10:])
    else:
        print("wrong input lang")
    return df


def textify(input_wd, output_wd):
    # index 값을 변수로 저장해줘라, 나중에 보면 햇갈릴수있으니.

    for xl in os.listdir(input_wd):
        no_lang_excel = xl[: xl.rfind("_")] + xl[xl.rfind(".") :]
        final_txt = name_dict.get(no_lang_excel)
        if final_txt == None:
            final_txt = xl[: xl.rfind(".")]
        final_txt = final_txt + ".txt"
        final_txt = os.path.join(output_wd, final_txt)
        print(f"{input_wd}\{xl}")
        print(final_txt)
        og_df = pd.read_excel(f"{input_wd}\{xl}")
        xlsx_df = reshape_df(og_df)
        # 비어있으면 해당 파일에 대한 작업 중단.
        if empty_cells(xlsx_df):
            logging.warning(
                f"Operation: Textify       File: {xl: <40} ERROR TYPE: Empty Cells"
            )
            raise ValueError("Empty cell in input excel file.")

        for col in xlsx_df:
            xlsx_df[col] = xlsx_df[col].apply(lambda x: re.sub("[\n]+", " ", str(x)))
            xlsx_df[col] = xlsx_df[col].apply(lambda x: re.sub("[\t]+", " ", str(x)))
            # xlsx_df[col] = xlsx_df[col].apply(lambda x: re.sub("[--]+", " ", str(x)))
        # xlsx_df = xlsx_df.fillna("")  # 납품파일이므로 nan 있는지 비교하고,

        xlsx_df[xlsx_df.columns[2]] = xlsx_df[xlsx_df.columns[2]].apply(
            tc_reformat, args=(xl,)
        )
        xlsx_df[xlsx_df.columns[3]] = xlsx_df[xlsx_df.columns[3]].apply(
            tc_reformat, args=(xl,)
        )
        tc_qc(xlsx_df[xlsx_df.columns[2]], xlsx_df[xlsx_df.columns[3]], xl)
        timecode = xlsx_df[xlsx_df.columns[2]] + " --> " + xlsx_df[xlsx_df.columns[3]]
        xlsx_df = xlsx_df.drop(xlsx_df.columns[2:4], axis=1)
        xlsx_df.insert(2, "TimeCode", "TimeCode")
        xlsx_df.insert(3, "start_end", timecode)
        if empty_cells(xlsx_df) > 0:
            logging.warning(
                f"Operation: Textify       File: {xl: <40} ERROR TYPE: Empty Cells"
            )
            raise ValueError("Empty cell in input excel file.")
        else:
            xlsx_df.to_csv(
                final_txt, header=None, index=None, sep="|", encoding="utf-8-sig"
            )
        pass_len_final(final_txt, og_df)


def pass_len_final(f_txt, df):
    check_txt = pd.read_csv(f_txt, sep="|", header=None)
    check_lines = len(check_txt)
    if check_lines != len(df):
        print("length mismatch...")
        logging.warning(
            f"Operation: Textify       File: {f_txt: <60} ERROR TYPE: Length Mismatch"
        )
        raise ValueError("Empty cell in input excel file.")
    else:
        pass


if __name__ == "__main__":
    textify(args.input, args.output)
