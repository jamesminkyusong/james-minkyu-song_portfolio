The process below was carried out to remove some duplicates that occurred due to the addition of new refinement rules while building the database (DB) and Elasticsearch, and also because there was a lot of traffic to Elasticsearch, preventing access at times. Regular checks are necessary as the same issue may arise in the future.

## 1. Extraction

Extract texts from the DB to Excel.
```
output: mono_LANG_CODE_[0-9]*.xlsx
```

```shell
$ cd apps/db_to_excel; ./exec_mono_all.sh
or
$ cd apps/db_to_excel; ./exec_mono.sh LANG_CODE
```

Example output: mono_fr_1.xlsx
```
sid | group_id | fr_id    | fr                                      | fr_source         | tag
----+----------+----------+-----------------------------------------+-------------------+----
2   | 8921113  | 30124341 | Voilà ce vers quoi nous nous dirigeons. | 2020_MEGADIC_ENFR | nan
9   | 8921106  | 30124326 | Je le finirai dans une heure.           | 2020_MEGADIC_ENFR | nan
```

## 2. Refinement

Refine the extracted texts from the DB, and save only the sentences that changed after refinement to Excel.
```
input: mono_LANG_CODE_[0-9]*.xlsx (output of step 1)
output: mono_LANG_CODE_cleaned_only.xlsx
```

```shell
$ cd apps/texts/manipulate_excel; ./exec_leave_cleaned_only.sh LANG_CODE
```

Example output: mono_fr_cleaned_only.xlsx
```
sid | group_id | fr_id    | fr                              | fr_source            | tag | fr_cleaned
----+----------+----------+---------------------------------+----------------------+-----+-----------
1   | 8652681  | 7506855  | Où êtes-vous?                   | 2017_ETRI_ENDEFRRUES | nan | Y
3   | 8558623  | 7476621  | Combien coûte un ticket de bus? | 2017_ETRI_ENDEFRRUES | nan | Y
```
  
## 3. Merging Duplicate Text Groups

If different texts become identical after refinement, the groups are merged in the DB. If group A is the latest and group B is the previous one, and if there are languages in B that are not in A, the `group_id` of those texts is changed from B to A. The remaining languages in B are already in A, so the group with `group_id` B is deleted from `parallel_corpus`.
```
input: mono_LANG_CODE_[0-9]*.xlsx (output of step 1)
output: dup_mono_LANG_CODE.xlsx
```

```shell
$ cd apps/texts/refine_cms; ./exec_merge.sh LANG_CODE
```

Example output: dup_mono_fr.xlsx
```
group_id_x | fr_id_x  | fr                       | group_id_y | fr_id_y
-----------+----------+--------------------------+------------+--------
3492766    | 11720506 | Comment puis-je y aller? | 681000     | 7478977
3492721    | 2254364  | Où est-ce?               | 3398935    | 7477524
```
  
## 4. Updating Refined Texts

The refined texts are updated back into the DB and Elasticsearch.
```
input: mono_LANG_CODE_cleaned_only.xlsx (output of step 2)
```

```shell
$ cd apps/texts/refine_cms; ./exec_cleaning.sh LANG_CODE
```