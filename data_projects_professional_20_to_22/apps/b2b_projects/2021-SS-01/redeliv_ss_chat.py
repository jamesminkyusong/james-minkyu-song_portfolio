import pandas as pd
import os
from bs4 import BeautifulSoup
from ss_compile_tags_chat import merge_confirm_tags

pd.options.mode.chained_assignment = None  # default='warn'


def prepare_work_from_delivery(delivered_df):
    delivered_dixs = delivered_df["Dialogue num"][delivered_df["Dialogue num"] != ""]
    delivered_dix_start_idx = delivered_df[
        delivered_df["Dialogue num"] != ""
    ].index.tolist()
    delivered_dix_end_idx = delivered_dix_start_idx[1:]
    delivered_dix_end_idx.append(len(delivered_df))

    dix_df_range = list(zip(delivered_dix_start_idx, delivered_dix_end_idx))
    delivered_dix_range_dict = dict(zip(delivered_dixs, dix_df_range))
    need_fix_dixs = delivered_df["Dialogue num"][
        (delivered_df["Dialogue num"] != "") & (delivered_df["fixed"] != "")
    ].tolist()

    return need_fix_dixs, delivered_dix_range_dict


def pull_fixed_dixs(delivered_df, dix, delivered_dix_range_dict):
    start_idx, end_idx = delivered_dix_range_dict.get(dix)
    dix_df = delivered_df[start_idx:end_idx]
    return dix_df, start_idx, end_idx


def re_confirm_logic(base_deliv_df):
    final_dict_col = []
    confirm_tags_to_merge = []
    confirm_tags_dict = dict()
    confirm_dict = dict()
    unconfirm_dict = dict()
    for line in base_deliv_df["Utterance"].tolist()[:-4]:
        soup = BeautifulSoup(line, "html.parser")
        tags_in_line = [tag.name for tag in soup.find_all()]
        prev_loc = 0
        for tag in tags_in_line:
            if tag == "confirm":
                for u in unconfirm_dict:
                    confirm_dict[u] = unconfirm_dict.get(u)
                unconfirm_dict = dict()

                first_loc = line.find(tag, prev_loc)
                second_loc = line.find(tag, first_loc + 1)
                token_tagged = line[first_loc + len(tag) + 1 : second_loc - 2]
                prev_loc = second_loc + len(tag) + 1
                confirm_tags_dict["confirm"] = token_tagged
            else:
                first_loc = line.find(tag, prev_loc)
                second_loc = line.find(tag, first_loc + 1)
                token_tagged = line[first_loc + len(tag) + 1 : second_loc - 2]
                prev_loc = second_loc + len(tag) + 1
                unconfirm_dict[tag] = token_tagged
        confirm_tags_to_merge.append(confirm_tags_dict.copy())
        if len(confirm_dict) > 0:
            final_dict_col.append(
                (",\n").join([f"{k}: {v}" for k, v in confirm_dict.copy().items()])
            )
        else:
            final_dict_col.append("")
    final_dict_col.append(final_dict_col[-1])
    final_dict_col.append("")
    final_dict_col.append("")
    final_dict_col.append("")

    final_dict_col = merge_confirm_tags(confirm_tags_to_merge, final_dict_col)
    base_deliv_df["State"] = final_dict_col
    return base_deliv_df


def apply_new_tags(base_deliv_df):
    og_b_deliv_df = base_deliv_df.copy(deep=True)
    add_meta = og_b_deliv_df[-3:]
    new_dix_df = re_confirm_logic(base_deliv_df)
    new_dix_df = new_dix_df[:-3]
    new_dix_df = new_dix_df.append(add_meta, ignore_index=True)
    return new_dix_df


def insert_new_df(delivered_df, new_df, start_idx, end_idx):
    if start_idx == 0:
        to_add_df_2 = delivered_df[end_idx:]
        delivered_df = pd.concat([new_df, to_add_df_2])
    elif end_idx == len(delivered_df):
        to_add_df_1 = delivered_df[:start_idx]
        delivered_df = pd.concat([to_add_df_1, new_df])
    else:
        to_add_df_1 = delivered_df[:start_idx]
        to_add_df_2 = delivered_df[end_idx:]
        delivered_df = pd.concat([to_add_df_1, new_df, to_add_df_2])
    return delivered_df


if __name__ == "__main__":
    delivery_fixed_df = pd.read_excel(
        r"/Users/jamessong/Downloads/try_ss_fix.xlsx"
    )  # path to excel file with new changes
    delivery_fixed_df = delivery_fixed_df.fillna("")
    fixed_dix_list, dix_range_dict = prepare_work_from_delivery(delivery_fixed_df)
    for n, fixed_dix in enumerate(fixed_dix_list):
        print(
            f"{str(n+1).zfill(len(str(len(fixed_dix_list))))}/{len(fixed_dix_list)} : {fixed_dix}"
        )
        fixing_df, beg_idx, end_idx = pull_fixed_dixs(
            delivery_fixed_df, fixed_dix, dix_range_dict
        )
        changes_applied_dix_df = apply_new_tags(fixing_df)
        delivery_fixed_df = insert_new_df(
            delivery_fixed_df, changes_applied_dix_df, beg_idx, end_idx
        )
    delivery_fixed_df.to_excel(
        r"/Users/jamessong/Downloads/try_ss_fix_4pm.xlsx", index=False
    )  # path to new delivery excel file
