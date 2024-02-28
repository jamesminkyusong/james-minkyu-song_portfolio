import os
import pandas as pd
from configparser import ConfigParser
from fractions import Fraction
from scipy.stats.mstats import gmean
from nltk.translate.bleu_score import (
    brevity_penalty,
    modified_precision,
)
import concurrent.futures
import deepcut
from janome.tokenizer import Tokenizer
from datetime import datetime

pd.options.mode.chained_assignment = None  # default='warn'


def parsers():
    c_parser = ConfigParser()
    c_parser.read("bleu_mt.ini")
    return c_parser


def splitter(sentence):
    list_sentence = sentence.strip().split()
    return list_sentence


def geoms(df):
    p_1 = df["p1"]
    p_2 = df["p2"]
    p_3 = df["p3"]
    p_4 = df["p4"]
    p_list = [p_1, p_2, p_3, p_4]
    p_list = [i for i in p_list if i != float(0)]
    if len(p_list) == 0:
        geomean = float(0)
    else:
        geomean = gmean(p_list)
    return geomean


# 이하 2는 hypothesis 열, 3 은 target 열이라고 보면 된다
def brev_penalty(df):
    len_hyp = len(str(df[2]))
    len_targ = len(str(df[3]))
    brev = brevity_penalty(len_hyp, len_targ)
    return brev


def precisions(df, n):
    hyp = [splitter(str(df[2]))]
    targ = splitter(str(df[3]))
    precise = modified_precision(hyp, targ, n)
    precise = float(Fraction(precise))
    return precise


def chunks(listlike, num):
    avg = len(listlike) / float(num)
    chunk = []
    last = 0.0

    while last < len(listlike):
        chunk.append(listlike[int(last) : int(last + avg)])
        last += avg
    return chunk


def deal_na_values(df):
    df.dropna(subset=["hypothesis"], inplace=True)
    df.dropna(subset=["target"], inplace=True)
    add_later_df = df[df.columns[4:]]
    df = df[df.columns[:4]]
    return df, add_later_df

    # na처리. 아래부터 다른 언어들 bleu 산출과 진행 방식이 다름.


def mk_bleu_logic(df):
    df, add_later_df = deal_na_values(df)
    # 혹시 모를 남은 na나 번역 안된 값 처리
    # 기존 방법은 precisions 함수 내에서 행단위로 작업하면서 hyp열과 targ 열을 토큰 해주고 바로 작업한다.
    df["p1"] = df.apply(precisions, n=1, axis=1)
    df["p2"] = df.apply(precisions, n=2, axis=1)
    df["p3"] = df.apply(precisions, n=3, axis=1)
    df["p4"] = df.apply(precisions, n=4, axis=1)  # n-gram 4 까지

    df["geom_mean"] = df.apply(geoms, axis=1)
    df["brev_pen"] = df.apply(brev_penalty, axis=1)

    df["bleu_emulated"] = (df["geom_mean"] * df["brev_pen"]) * 100
    return df, add_later_df


# cf 방법은 빠른 처리를 위하여 1개 열을 8개로 분할후,
# (예: [a,b,c... ,o,p] -> [[a, b], ... ,[o,p]]
# 열에 대한 8개 파트를 다 토크나이징을 동시에 처리한다.
# 그 후 해당 열을 리스트화해서 돌려 받는다.
# 작업이 끝나는 순서대로 다시 돌려 받으니, 작업 시작 전 chunk_index 를 부여 해주면서
# 소팅 작업을 하면 tokenizing이 된 리스트가 df의 열로 추가 가능.
# 추가 이후에는 modified_precisions 및 geom-means적용
def pre_cf_df(df):
    df, add_later_df = deal_na_values(df)
    # th와 jp 는 한개 함수로 묶을 수 있을거 같다.
    # chunking 을 위한 hypothesis 리스트화
    hyp_to_chunk = df["hypothesis"].values.tolist()
    # chunking 을 위한 targe/혹은 번역물 리스트화 (끝 자리 index. maybe use -1)
    targ_to_chunk = df[df.columns[len(df.columns) - 1]].values.tolist()

    # 8개로 분할, 8 코어
    chunked_hyp = chunks(hyp_to_chunk, 8)
    chunked_targ = chunks(targ_to_chunk, 8)
    return df, chunked_hyp, chunked_targ, add_later_df


def cf_ja_hyp(chunkcount, hyp_chunked):
    split_up = []
    ja_t = Tokenizer()  # janome.Tokenizer.tokenize 는 가본 아웃풋이 리스트가 아니다.
    split_up.append(chunkcount)
    for line in hyp_chunked[chunkcount]:
        hyp = [[h for h in ja_t.tokenize(str(line), wakati=True)]]
        split_up.append(hyp)
    return split_up


def cf_ja_targ(chunkcount, targ_chunked):
    split_up = []
    ja_t = Tokenizer()
    split_up.append(chunkcount)
    for line in targ_chunked[chunkcount]:
        targ = [t for t in ja_t.tokenize(str(line), wakati=True)]
        split_up.append(targ)
    return split_up


def cf_th_hyp(chunkcount, hyp_chunked):
    split_up = []
    split_up.append(chunkcount)
    for line in hyp_chunked[chunkcount]:
        hyp = [deepcut.tokenize(str(line))]  # deepcut.tokenize는 가본 아웃풋이 리스트이다.
        split_up.append(hyp)
    return split_up


def cf_th_targ(chunkcount, targ_chunked):
    split_up = []
    split_up.append(chunkcount)
    for line in targ_chunked[chunkcount]:
        targ = deepcut.tokenize(str(line))
        split_up.append(targ)
    return split_up


def cf_splitter(cf_function, src_chunked):
    need_sort_split = []
    end_iter = len(src_chunked) + 1
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [
            executor.submit(cf_function, exec_count - 1, src_chunked)
            for exec_count in range(1, end_iter)
        ]
        for f in concurrent.futures.as_completed(results):
            need_sort_split.append(f.result())

    return need_sort_split


def sort_final(needing_sort):
    needing_sort.sort(key=lambda x: x[0])  # 추가해준 chunk_count 대로 정렬해준다
    # 현재 상태는 [ [list1] , [list2] ... , [list8] ] 각 리스트 안에 tokenize 된 리스트들 존재
    needing_sort_2 = []
    for s in needing_sort:
        needing_sort_2.append(s[1:])  # chunk_count 제거
    final_sort = [
        fin for n in needing_sort_2 for fin in n
    ]  # list comprehension with nested forloop
    # to change  [ [list1] , [list2] ... , [list8] ] -> [list1, list2,... ,list8]

    return final_sort


def cf_precisions(df, n):
    precise = modified_precision(df[4], df[5], n)
    # 그냥 precisions과 index 가 다른 이유는 cf는 tokenize 된 열들을 df 에 추가 하기 때문
    precise = float(Fraction(precise))
    return precise


def cf_bleu(ns_h, ns_t, df):
    sorted_splitted_h = sort_final(ns_h)
    sorted_splitted_t = sort_final(ns_t)
    df["hyp_split"] = sorted_splitted_h
    df["targ_split"] = sorted_splitted_t

    df["p1"] = df.apply(cf_precisions, n=1, axis=1)
    df["p2"] = df.apply(cf_precisions, n=2, axis=1)
    df["p3"] = df.apply(cf_precisions, n=3, axis=1)
    df["p4"] = df.apply(cf_precisions, n=4, axis=1)

    df["geom_mean"] = df.apply(geoms, axis=1)
    df["brev_pen"] = df.apply(brev_penalty, axis=1)
    df["bleu_emulated"] = (df["geom_mean"] * df["brev_pen"]) * 100
    return df


def store_means(df, filename, error_rate_df, src, dst):
    error_rate_keys = list(zip(error_rate_df.src, error_rate_df.dst))

    stored_means = []
    rawmean = df["bleu_emulated"].mean()
    df_lowsdropped = df[~(df["bleu_emulated"] <= 10)]
    droppedmean = df_lowsdropped["bleu_emulated"].mean()
    stored_means.append(filename)
    stored_means.append(len(df))
    stored_means.append(rawmean)
    stored_means.append(len(df_lowsdropped))
    stored_means.append(droppedmean)
    try:
        max_error = error_rate_df["Max Error"].loc[error_rate_keys.index((src, dst))]
        avg_error = error_rate_df["Average Error"].loc[
            error_rate_keys.index((src, dst))
        ]
        stored_means.append(max_error)
        stored_means.append(avg_error)
        stored_means.append(droppedmean + max_error)
        stored_means.append(droppedmean + avg_error)
    except:
        stored_means.append("")
        stored_means.append("")
        stored_means.append("")
        stored_means.append("")

    return stored_means


def separate_langs(dirlist):
    sep_list = []
    can_work_langs = []
    th = []
    ja = []
    for f in dirlist:
        if f.startswith(".") or f.startswith("~"):
            continue
        first_under = f.find(".")
        check_dst_thja = f[first_under + 2 : f.find("_", first_under + 1)][2:]
        # first_under = f.find("_")
        # check_dst_thja = f[first_under + 1 : f.find("_", first_under + 1)][2:]
        src = f[first_under + 2 : f.find("_", first_under + 1)][:2]
        # check_thja = f[f.rfind("2") :]
        if "th" in check_dst_thja.lower():
            th.append([f, src, check_dst_thja])
        elif "ja" in check_dst_thja.lower():
            ja.append([f, src, check_dst_thja])
        else:
            can_work_langs.append([f, src, check_dst_thja])
    sep_list.append(can_work_langs)
    sep_list.append(ja)
    sep_list.append(th)
    return sep_list


def insert_presaved_columns(df, add_later_df):
    first_position = 4
    for a in add_later_df.columns:
        df.insert(first_position, a, add_later_df[a])
        first_position += 1
    return df


if __name__ == "__main__":
    configs = parsers()
    out_date = datetime.strftime(datetime.now(), "%m%d")
    wd = configs.get("PATHS", "bleu_in")
    od = configs.get("PATHS", "bleu_out")
    error_rates = configs.get("PATHS", "error_rate_xlsx")
    er_df = pd.read_excel(error_rates)
    er_df = er_df.fillna("")
    cols = [
        "Filename",
        "Length of Rows (with hyp)",
        "Bleu Mean",
        "Length of Rows (Bleu > 10)",
        "Bleu Mean (Adjusted)",
        "Max Error",
        "Avg Error",
        "Bleu_MAX",
        "Bleu_AVG",
    ]  # columns for final bleu summary xlsx
    total_means = []  # list for final bleu summary xlsx
    worklist = separate_langs(os.listdir(wd))  # 일할곳을 3 분류로 나ㅏ눠준다
    nows = worklist[0]
    jas = worklist[1]
    ths = worklist[2]
    for now, src, dst in nows:
        print(now, src, dst)
        mtpe_df = pd.read_excel(os.path.join(wd, now))
        bleu_mtpe_df, add_later_df = mk_bleu_logic(mtpe_df)  # 기존 블루 산출 방법
        # store means 사용 n 값 및 mean 값 저장
        bleu_mtpe_df = bleu_mtpe_df.drop(columns=bleu_mtpe_df.columns[4:10])
        if src == "th" or src == "ja":
            bleu_mtpe_df["wordcount"] = bleu_mtpe_df["target"].apply(
                lambda x: len(str(x).split())
            )
        else:
            bleu_mtpe_df["wordcount"] = bleu_mtpe_df["source"].apply(
                lambda x: len(str(x).split())
            )
        # precisions/geom mean/bleu 산출 추가-> 엑셀
        bleu_mtpe_df = insert_presaved_columns(bleu_mtpe_df, add_later_df)
        total_means.append(store_means(bleu_mtpe_df, now, er_df, src, dst))
        bleu_mtpe_df.to_excel(os.path.join(od, f"__newbleu_{now}"), index=False)

    for ja, src, dst in jas:
        print(ja, src, dst)
        ja_hyp = cf_ja_hyp  # 일본어 hyp 분리: 구조 [ [[문장1]], [[문장2]], ... ]
        ja_targ = cf_ja_targ  # 일본어 targ 분리: 구조 [[문장1], [문장2], ... ]

        mtpe_df = pd.read_excel(os.path.join(wd, ja))
        mtpe_df, ja_chunk_hyp, ja_chunk_targ, add_later_df = pre_cf_df(mtpe_df)

        # nltk 특성상 modified_precisions()를 사용 할때 hyp 는 nested list targ 은 list 여야 된다
        # 소팅 필요
        need_sort_h = cf_splitter(ja_hyp, ja_chunk_hyp)
        need_sort_t = cf_splitter(ja_targ, ja_chunk_targ)

        # cf_bleu()안에서 소팅 처리
        bleu_mtpe_df = cf_bleu(need_sort_h, need_sort_t, mtpe_df)
        bleu_mtpe_df.drop(columns=bleu_mtpe_df.columns[4:13])

        bleu_mtpe_df["wordcount"] = bleu_mtpe_df["source"].apply(
            lambda x: len(str(x).split())
        )

        total_means.append(store_means(bleu_mtpe_df, ja, er_df, src, dst))
        bleu_mtpe_df = insert_presaved_columns(bleu_mtpe_df, add_later_df)

        bleu_mtpe_df.to_excel(os.path.join(od, f"__newbleu_{ja}"), index=False)

    for th, src, dst in ths:
        print(th, src, dst)
        th_hyp = cf_th_hyp
        th_targ = cf_th_targ

        mtpe_df = pd.read_excel(os.path.join(wd, th))
        mtpe_df, th_chunk_hyp, th_chunk_targ, add_later_df = pre_cf_df(mtpe_df)

        need_sort_h = cf_splitter(th_hyp, th_chunk_hyp)
        need_sort_t = cf_splitter(th_targ, th_chunk_targ)

        bleu_mtpe_df = cf_bleu(need_sort_h, need_sort_t, mtpe_df)

        bleu_mtpe_df["wordcount"] = bleu_mtpe_df["source"].apply(
            lambda x: len(x.split())
        )

        total_means.append(store_means(bleu_mtpe_df, th, er_df, src, dst))
        bleu_mtpe_df = insert_presaved_columns(bleu_mtpe_df, add_later_df)
        bleu_mtpe_df.to_excel(os.path.join(od, f"__newbleu_{th}"), index=False)

    # 최종 summary 파일 출력
    means_compiled = pd.DataFrame(total_means)
    means_compiled.columns = cols

    means_compiled.to_excel(
        os.path.join(od, f"{out_date}_BLEU_comparison_final.xlsx"), index=False
    )
