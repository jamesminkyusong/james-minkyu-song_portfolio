## Basic Flow
The basic flow of the AL project is as follows:

1. srt → xlsx (Basic verification: log check required)
    ```
    # After setting the path
    
    python srt_to_excel.py -ilang (Choose one from EN/FR/ZH)
    

    ali_work_folder    
    │
    └───srts
    │   └───EN
    │       └───work
    │       └───done
    │   └───FR
    │       │   ...
    │   └───ZH
    │       │   ...
    │   
    └───xlsxout
        │   output_1.xlsx
        │   output_2.xlsx
        │   ...       

    ```
2. xlsx → txt (Pre-Delivery verification: log check required)
    ```
    python excel_to_txt.py -idir (input folder path) -odir (output folder path)

    # Check the log for issues (filename: line number, issue: timecode/blank/etc.)

    # Similarly, check the log

    # For the .xlsx files in -idir to automatically change their output .txt filenames, they must follow the format below: 
    # NO_LANG_IDID_.xlsx NO = 1 or 2, LANG = EN/FR/ZH, ID = 4 digit number 
    # ex) 1_FR_0388_.xlsx, 2_ZH_0521_.xlsx
    # EN_1_FR0388_ENFRPT.xlsx -> 1_FR_0388_.xlsx or 1_FR_0388_FRENPT.xlsx (Only one "_" after 1_ES_0388, because rfind("_") is used)
    # New_2_ZH0772_ZHENFRPT.xlsx -> 2_ZH0772_.xlsx or 2_ZH0772_ZHENFRPT.xlsx
    # 1_EN_0023.xlsx -> 1_EN_0023_.xlsx or 1_EN_0023_ENFRPT.xlsx 
    # For NO_LANG_IDID_.xlsx, it doesn't matter whether there are language codes after the underscore or not.
    # In cases where a different language code is prefixed before NO, just delete it.

    ```
## Re-Delivery Flow
The flow for redelivery of the AL project is as follows:

1. New srt → New xlsx (Basic verification: log file check required)
    ```
    # Same as before

    python srt_to_excel.py -ilang (Choose one from EN/FR/ZH)
    
    
    ``` 
2. Delivered xlsx vs New xlsx
    If passed: Overwrite the new Timecode onto the delivered file → preserves translated corpus, only modifies timecode
    If failed: Two categories 1. Files of different lengths 2. Files of same length but different original text (add 2 columns for inspection)
    ```
    # Additional process for redelivery
    # New xlsx is the output file from step 1
    # Path setting required (Path for delivered Excel, path for newly created Excel, output pass/fail folder path)

    python re_ali_verify.py
    
    # Deliver the pass/fail + new xlsx folder from step 1 to the responsible PM

    ali_work_folder    
    │
    └─── srts
    │   │ ...
    │
    └─── xlsxout
        │   output_1.xlsx
        │   output_2.xlsx
        │   ...     

    # Create a new folder with files requested today in the xlsxout folder
    # ex) 0414_rework_request  
    
    0414_rework_request (New folder)
    │
    │   output_1.xlsx
    │   output_2.xlsx
    │   ...

    ali_redeliv_original (Delivered folder)
    │
    │   old_xlsx_1
    │   old_xlsx_2
    │   ...

    0414_rework_out (output_folder)
    │
    └─── pass
    │   │ ...
    │
    └─── fail
    │   │ ...
    ```
    
3. pass/fail → B2B modification → re-transfer to the data team in a deliverable state
    ```
    python excel_to_txt.py -idir (input folder path) -odir (output folder path)

    # Proceed as in [2. xlsx → txt] of the basic process (File name format related readme updated)
 
    ```
