## NV PPG BLEU Score Calculation Flow
The basic flow of calculating NV PPG BLEU scores is as follows:

1. **NV PM delivers a folder containing .xlsx files for similarity check to the Data Team.**

2. **Proceed with BLEU similarity check:**
    - Set the .ini path
    ```
    bleu_in = requested folder path (e.g., ././nv_ppg/i/bleu_0419_multi/i)
    bleu_out = output path (e.g., ././nv_ppg/i/bleu_0419_multi/o)
    error_rate_xlsx = path for the Excel file summarizing the error rate so far (e.g., ././nv_ppg/_nv_fl_mt_comparison.xlsx)
    ```
    - Check the file name format for extracting src and dst in each file. It's necessary to review the separate_langs() function.
    ```
    python nv_calculate_bleu.py
    # The similarity results for each file are saved in the output path, and one file summarizing the similarity of all files (_BLEU_comparison_final.xlsx) is created.
    ```

3. **If the similarity score in _BLEU_comparison_final.xlsx exceeds 60 points, the similarity result file for that file is sent.**
    - For example, if the similarity score for the en-th file is 70 points, the bleu_enth_{}.xlsx file is delivered to the PM.

This streamlined process ensures a systematic approach to verifying and communicating BLEU scores for project files, ensuring transparency and efficiency in quality assessments.