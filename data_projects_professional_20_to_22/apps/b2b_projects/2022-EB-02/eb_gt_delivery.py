import os
from configparser import ConfigParser

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

# Golden Tagging 납품을 위한 형식 최대한 자동 수정 해주는 .py


def parsers():
    c_parser = ConfigParser()
    c_parser.read("gt_config.ini")
    return c_parser


def drop_cols(gt_df, col):  # sneakers 카테고리는 M열까지 13열이 있다. :. col= 13
    gt_df = gt_df.fillna("")
    len_gt_col = len(gt_df.columns)  # QA / 필요없는값이 엑셀기준 M열 이후로 들어오면 M열 이후의 값을 삭제
    colstodrop = list(range(col, len_gt_col))
    checking_gt = gt_df.drop(colstodrop, axis=1)
    return checking_gt


def trimmer(df):
    notouch = df.iloc[0:1, :]
    fixpart = df.iloc[1:]
    for cols in fixpart:
        fixpart[cols] = fixpart[cols].apply(
            lambda x: " ".join(x.strip().split()) if isinstance(x, str) else x
        )
        # 열 단위로 excel trim 기능 적용
        # strip 한 단어를 default 기준으로 나누어주고 다시 space 하나로 join 해준다.
    df = notouch.append(fixpart)
    return df


def fix_bars(df):
    notouch = df.iloc[0:1, :]
    fixpart = df.iloc[1:]
    fixpart = fixpart.replace(r"ǀ", r"|", regex=True)
    #'|'.join(map(lambda word: word.strip(), text.split('|'))) 를 변형
    # 위 주석 코드를 열 단위로 실행 가능 할수 있게, apply 를 써주고,
    # lambda j를 통해 map기능과 lambda word 에 사용할수 있는
    # '|' 로 split 된 인자를 만들어 준 후 strip, join 을 실행 하면서 불필요 공백을 제거해준다
    for cols in fixpart:
        fixpart[cols] = fixpart[cols].apply(
            lambda j: "|".join(map(lambda word: word.strip(), str(j).split("|")))
        )
    df = notouch.append(fixpart)
    return df


if __name__ == "__main__":
    configs = parsers()

    folderdir = configs.get("QA PATHS", "gt_delivery_folder")
    outdir = configs.get("QA PATHS", "gt_delivery_out")

    for files in os.listdir(folderdir):
        if files.startswith(".") or files.startswith("~"):
            continue
        filename, ext = os.path.splitext(files)
        df = pd.read_excel(os.path.join(folderdir, files), header=None)
        df = drop_cols(df, 13)
        df = trimmer(df)
        df = fix_bars(df)
        df.to_excel(os.path.join(outdir, files), header=None, index=False)
