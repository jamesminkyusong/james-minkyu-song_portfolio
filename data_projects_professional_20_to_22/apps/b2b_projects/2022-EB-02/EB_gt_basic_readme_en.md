## EB GT Basic Flow
The basic flow of the EB GT project is as follows:

1. Client -- .xlsx folder delivery --> Flitto --> Tags that can be automatically filled are entered.

2. B2B PM -- Request for QA Tableview creation of the tagged Excel folder --> Data Team
    - This process involves reading all the Excel files in the folder, swapping rows <-> columns, and then creating a single integrated file.
    - .ini path setting
        - gt_tv_directory = requested folder path
        - empty_files_directory = original folder delivered by the client
        - fixed_out_dir = folder to be newly created if there are automatically corrected files
        - output_directory = path to create the output tableview.xlsx
    ```
    python eb_gt_qa_tableview.py -oname (enter output file name)
    ```

3. QA completion through the created Tableview ---> Request for delivery preparation
    
    a. For batch modification requests
    ```
    # Execute after modifying eb_gt_fix_cells.py

    python eb_gt_fix_cells.py

    # Overwrite the created files in the delivery preparation folder
    ```
   
    b. After batch modification is complete -> Delivery preparation
   - .ini path setting
   - gt_delivery_folder = delivery preparation request folder path 
   - gt_delivery_out = original folder delivered by the client path
       ```
       python eb_gt_delivery.py
    
       # After completion, deliver the output folder to the B2B side
       ```