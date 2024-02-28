
import pandas as pd
from zipfile import ZipFile
import io
import base64

def file_to_df(uploaded_file, file_type):
    '''
    uploaded_file: streamlit 을 통해 업로드 된 파일
    file_type: 업로드된 file 형식 
    '''
    if file_type == 'xlsx':
        df = pd.read_excel(uploaded_file)

    elif file_type == 'csv':
        df = pd.read_csv(uploaded_file)

    elif file_type == 'tsv':
        df = pd.read_csv(uploaded_file, sep='\t')
  
    elif file_type == 'json':
        df = pd.read_json(uploaded_file)

    else:
        return pd.DataFrame()

    df = df.fillna("")

    return df


def df_to_file_method(df, download_file_type, download_header_type):
    #file 형식에 따른 분기 처리
    if download_file_type == 'xlsx':
        towrite = io.BytesIO()
        method_to_download = df.to_excel(towrite,  index=False, header=download_header_type)
        towrite.seek(0)

        method_to_download = towrite.read()

    elif download_file_type == 'csv':
        method_to_download = df.to_csv(index=False, header=download_header_type)

    elif download_file_type == 'tsv':
        method_to_download = df.to_csv(index=False, sep='\t', header=download_header_type)

    elif download_file_type == 'json':

        if download_header_type:
            method_to_download = df.to_json()
        else:
            method_to_download = df.to_json(orient='values')

    return method_to_download


def df_to_b64(df, download_file_type = 'xlsx', download_header_type = True):

    method_to_download = df_to_file_method(df, download_file_type, download_header_type)
    try:
        if download_file_type == 'xlsx':
            b64 = base64.b64encode(method_to_download).decode()
        else: 
            b64 = base64.b64encode(method_to_download.encode()).decode()

    except:
        b64 = None

    return b64


def _split_df(df, file_split_size, file_split_num):
    dfs = list()

    for i in range(file_split_num):
        if i == file_split_num - 1:
            dfs.append(df[i*file_split_size:])            
        else:
            dfs.append(df[i*file_split_size: (i+1)*file_split_size])

    return dfs


def df_split_zip_b64(df, file_extension_type, download_header_type, file_split_size, file_split_num):
    dfs = _split_df(df, file_split_size, file_split_num)
    zipObj = ZipFile('splited_data', 'w')
    
    for i in range(len(dfs)):

        method_to_download = df_to_file_method(dfs[i], file_extension_type, download_header_type) 
        zipObj.writestr(f'splited_data_{i}.{file_extension_type}', method_to_download)

    zipObj.close()
    ZipfileDotZip = "splited_data"

    with open(ZipfileDotZip, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()

    return b64