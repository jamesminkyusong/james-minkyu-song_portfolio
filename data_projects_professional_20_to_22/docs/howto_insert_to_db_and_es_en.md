When purchasing corpora from external sources or constructing new corpora, we update them in the DB and Elasticsearch for future use.

## 1. Quality Check

Refer to [howto_find_bad.md](https://github.com/flitto/data_mgmt/blob/develop/docs/howto_find_bad.md) to check the quality of the corpus.

## 2. Registering Partners and Projects

If it involves a new language, a new partner, or a new project, first enter the information in the DB's languages, partners, and projects.

## 3. Registering in DB and Elasticsearch

Preview the Excel file.

```shell
cd apps/db/excel_to_db; ./excel_to_db.py --preview -p PATH -i INPUT_FILES --col_indices COL_INDICES --col_names COL_NAMES --project_id PROJECT_ID
```

Test in the development environment before directly updating the production environment to ensure there are no issues.

```shell
cd apps/db/excel_to_db; ./excel_to_db.py -p PATH -i INPUT_FILES --col_indices COL_INDICES --col_names COL_NAMES --project_id PROJECT_ID
```

If there are no issues, update the production environment.

```shell
cd apps/db/excel_to_db; ./excel_to_db.py --prod -p PATH -i INPUT_FILES --col_indices COL_INDICES --col_names COL_NAMES --project_id PROJECT_ID
```

## 4. Examples

### 1) Registering a New Corpus

1. Excel file example
```
sid | en                                | fr                                          | tag
----+-----------------------------------+---------------------------------------------+-----
1   | I could be a teacher, or a nurse, | Je pourrais être professeur, ou infirmière, | IT
    | or a computer programmer.         | ou programmeur informatique.                |
2   | How do you protect computers from | Comment protèges tu des ordinateurs contre  | IT
    | a sudden power outage?            | les pannes soudaines de courant?            |
3   | It can be repaired at the Apple   | Cela peut être réparé au SAV d'Apple.       | Travel
    | service center.                   |                                             |
```

2. Previewing the Excel file
```shell
cd apps/db/excel_to_db; ./excel_to_db.py --preview --env DEVELOPMENT -p ~/project/corpus_raw/b2b_projects/2020/2020-MS-01/1st_delivery/xlsx -i 2020-MS-01_en_fr_16000.xlsx --col_indices 1 2 --col_names en fr --project_id 54
```

3. Updating the development environment
```shell
cd apps/db/excel_to_db; ./excel_to_db.py -p ~/project/corpus_raw/b2b_projects/2020/2020-MS-01/1st_delivery/xlsx -i 2020-MS-01_en_fr_16000.xlsx --col_indices 1 2 --col_names en fr --project_id 54
```

4. Updating the production environment
```shell
cd apps/db/excel_to_db; ./excel_to_db.py --prod -p ~/project/corpus_raw/b2b_projects/2020/2020-MS-01/1st_delivery/xlsx -i 2020-MS-01_en_fr_16000.xlsx --col_indices 1 2 --col_names en fr --project_id 54
```

### 2) Adding a New Language to an Existing Parallel Corpus

1. Excel file example
```
sid | group_id | en_id    | en                                    | es
----+----------+----------+---------------------------------------+-------------------------------------------
1   | 8920887  | 8935037  | The items enumerated by Mrs Rothe are | Los artículos enumerados por la Sra. Rothe
    |          |          | targets, not yet mandatory.           | son objetivos, aún no son obligatorios.
2   | 8920434  | 11470801 | Mr Martin, you have just answered it  | Sr. Martin, acaba de responderlo por mí.
    |          |          | for me.                               |
3   | 8918895  | 20715853 | This part of the brain is called the  | Esta parte del cerebro se llama córtex
    |          |          | anterior cingulate gyrus.             | del cíngulo anterior.
```

2. Previewing the Excel file
```shell
cd apps/db/excel_to_db; ./excel_to_db.py --preview --env DEVELOPMENT -p ~/project/corpus_raw/excel_to_db -i en2es.xlsx --col_indices 1 4 --col_names group_id es --group_col_name group_id --project_id 54
```

3. Updating the development environment

```
refer to 4-1-3 
```

4. 상용 환경 업데이트
```
refer to 4-1-4
```
