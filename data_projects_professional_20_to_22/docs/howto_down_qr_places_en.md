Save the image information registered in QR Places to Excel and download the images.

## 1. Extraction

Extract texts from the DB to Excel.
```
output: qr_LANG_CODE.xlsx or qr_LANG_CODE_image_only.xlsx
```

```shell
To save all information including images and translations
$ cd apps/images; ./db_to_excel.py -p ~/project/corpus_raw/images/qr_places -o qr_en.xlsx --lang_code en
To save only image information
$ cd apps/images; ./db_to_excel.py -p ~/project/corpus_raw/images/qr_places -o qr_en_image_only.xlsx --lang_code en --image_only
```

Example output: qr_en.xlsx
```
sid | item_id | qr_tr_id | like_cnt | orig_lang_code | tr_lang_code
----+---------+----------+----------+----------------------------------------------------------------------------
| image_url                                                                 | image_width | image_height | orig
+---------------------------------------------------------------------------+-------------+--------------+-----
| tr
+--------------------------------------------------------------------------------------------------------------
1   | 9753    | 41196    | 0        | en             | zh           |
| https://flittosg.s3.amazonaws.com/qr_place/2017/11/24/124538222942817.png | 800         | 1043         |
| 1. Open the app (Flittos) 2. Take a photo of what you want to translate 3. Check the translation result
2   | 9753    | 41188    | 0        | en             | ja           |
| https://flittosg.s3.amazonaws.com/qr_place/2017/11/24/124538222942817.png | 800         | 1043         |
| 1. Launch the app 2. Take a photo 3. See the translation
```

Example output: qr_en_image_only.xlsx
```
sid | item_id | orig_lang_code | image_url
----+---------+----------------+----------------------------------------------------------------------------
1   | 9753    | en             | https://flittosg.s3.amazonaws.com/qr_place/2017/11/24/124538222942817.png
2   | 9768    | en             | https://flittosg.s3.amazonaws.com/qr_place/2017/11/26/197358329967890.png
```

## 2. Save Images

Read the Excel file and save the images.
```
input: qr_LANG_CODE_image_only.xlsx (output of step 1)
```

```shell
$ cd apps/images; ./downloader.py -p ~/project/corpus_raw/images/qr_places -i qr_en_image_only.xlsx --id_col_i 2 --url_col_i 4
```