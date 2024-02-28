When modifications or deletions are needed for an existing corpus, they are reflected in both the DB and Elasticsearch.

## 1. Operation Code

```shell
D    : Delete corpus
D_A  : Delete all corpora within the group containing the corpus
U_D  : Update domain
U_L  : Update language
U_T  : Update text
U_LT : Update language and text
```

## 2. Examples

#### 1. Excel File

```shell
sid   | group_id | de_id    | de                                                           | opcode | lang_code | tag_id_col_id
------+----------+----------+--------------------------------------------------------------+--------+-----------+--------------
491   | 8735987  | 3846757  | Tag 21, Tag 23, Tag 25.                                      | D_A    |           |
9660  | 8335580  | 28589343 | People call it Economy Class Syndrome.                       | U_D    |           | 6
28065 | 8317175  | 28550885 | Your pager number is 000-0000-0000, right?                   | U_T    |           |
39941 | 8305299  | 28526097 | Gil-Dong Hong, 000000-0000000.                               | D      |           |
51863 | 8293377  | 28501146 | The phone number is 000-0000-0000 and the fax number is 000-0000-0000. | U_L    | de        |
76433 | 8268807  | 28449718 | The twin room costs $100 per day.                           | U_LT   | de        |
```

#### 2. Update Development Environment
```shell
$ cd apps/texts/refine_cms
$ ./update_corpus.py \
    -i ~/project/corpus_raw/texts/mono/corpus_de.xlsx \
    --lang_code de \
    --opcode_col_i 5 \
    --group_id_col_i 2 \
    --corpus_id_col_i 3 \
    --text_col_i 4 \
    --new_lang_code_col_i 6 \
    --tag_id_col_i 7 \
    --dev
```

#### 3. Update Production Environment
```shell
$ cd apps/texts/refine_cms
$ ./update_corpus.py \
    -i ~/project/corpus_raw/texts/mono/corpus_de.xlsx \
    --lang_code de \
    --opcode_col_i 5 \
    --group_id_col_i 2 \
    --corpus_id_col_i 3 \
    --text_col_i 4 \
    --new_lang_code_col_i 6 \
    --tag_id_col_i 7 \
    --prod
```