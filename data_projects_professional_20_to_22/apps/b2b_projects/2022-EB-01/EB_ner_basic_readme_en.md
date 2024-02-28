## EB NER Basic Flow
The basic flow of the EB NER project is as follows:

1. **Client delivers .tsv / .txt files to Flitto** --> Flitto generates a token work file .xlsx and delivers it to the PM
    - Set the .ini path
    ```
    ner_og_directory = path for .tsv / .txt files (e.g., sneakers_71_FR_20211201-20220302.csv.5k.tokenized.txt)
    ```
    ```
    python eb_ner_initial_tokenize.py
    ```

2. **PM requests additional QA creation for the tagged Excel** --> Data Team
    - Structural state check required before additional QA creation
    - Set the .ini path
    ```
    ner_og_directory = path for .tsv / .txt files
    worked_file = tagged .xlsx file requested for QA (e.g., ./Sneakers_FR_5k_tokenized_checked.xlsx)
    ner_tagset = tagset .xlsx delivered by the client (e.g., ./Sneakers FR Tags.xlsx)
    ner_delivery_path = output path
    ```
    - Check the requested Excel file before execution (verify unnecessary columns / check for blanks in columns A, B, C)
    ```
    python eb_ner_tagging_qa_compile.py
    ```

3. **There are three output files:**
    a. Sneakers_FR_5k_tokenized_checked_delivery.tsv (Delivery .tsv file)
    b. Sneakers_FR_5k_tokenized_checked_delivery.xlsx (Delivery .tsv converted to .xlsx)
    c. Sneakers_FR_5k_tokenized_checked_errors.xlsx (Auto-correction log and error type log)
    
    - Check the file c. Sneakers_FR_5k_tokenized_checked_errors.xlsx in the path
    - Use filter to find rows without 'auto:' logs and manually correct them in the worked_file, ./Sneakers_FR_5k_tokenized_checked.xlsx
    ```
    # Rerun
    python eb_ner_tagging_qa_compile.py
    # Repeat until the Sneakers_FR_5k_tokenized_checked_errors.xlsx file contains only rows with 'auto:'.
    ```

4. **Generate additional QA file using _delivery.xlsx file**
    - Set the .ini path
    ```
    additional_qa = path for Sneakers_FR_5k_tokenized_checked_delivery.xlsx file (structurally corrected file)
    ```
    ```
    python eb_ner_multi_tag_additional_qa.py
    # Deliver the output file Sneakers_FR_5k_tokenized_checked_additional_qa.xlsx to the PM.
    ```

5. **After inspecting/modifying Sneakers_FR_5k_tokenized_checked_delivery_additional_qa.xlsx, PM requests delivery preparation** --> Data Team
    - Repeat steps 2 and 3
    ```
    python eb_ner_tagging_qa_compile.py
    # Deliver Sneakers_FR_5k_tokenized_checked_delivery.tsv, Sneakers_FR_5k_tokenized_checked_delivery.xlsx files to the PM.
    ```