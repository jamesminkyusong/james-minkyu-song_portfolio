import os
import pandas as pd


ipath = r"/Users/jamessong/Desktop/IO/in/ebay/gt/0422/i"
opath = r"/Users/jamessong/Desktop/IO/in/ebay/gt/0422/after"

count = 0
for f in sorted(os.listdir(ipath)):
    if f.startswith(".") or f.startswith("~"):
        continue
    df = pd.read_excel(os.path.join(ipath, f), header=None, keep_default_na=True)
    df = df.fillna("")
    if count == 0:
        tag_subject = df[0].tolist()
        to_fix_index_1 = tag_subject.index("Number of Gemstones")  # 바꿔줘야 되는 태그 카테고리 입력
        # to_fix_index_2 =tag_subject.index('') # 2개 이상이면 동일하게 추가
        index_list = [to_fix_index_1]  # to_fix_index_2, to_fix_index_3....  도 있으면 추가
        count += 1
    fixed = False
    for idx in index_list:
        for i in range(1, 6):
            check_val = df.iloc[idx][i]
            if str(check_val) == "0" or str(check_val) == "0.0":  # 일괄 변경 요청 받은 키워드 확인
                check_val = str(check_val).replace("0", "")  # 바꿔줄 값 설정
                if check_val.startswith("|"):
                    check_val = check_val[1:]
                    print(f"check fixed file {f}")
                if check_val.endswith("|"):
                    check_val = check_val[:-1]
                    print(f"check fixed file {f}")
                df.iat[idx, i] = check_val
                fixed = True
    if not fixed:
        pass
    else:
        df.to_excel(os.path.join(opath, f), index=False, header=None)
