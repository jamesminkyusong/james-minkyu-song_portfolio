
import streamlit as st
import re
import uuid
from .df_utils import file_to_df
from .ui_utils import draw_loading

extension_f = lambda orig_file: orig_file.rsplit('.', 1)[-1].lower()


def file_download(data_b64, download_filename, download_type, button_text):
    '''
    작업이 끝난 후 파일 형식에 맞게 다운로드 버튼 생성
    '''
    if data_b64 == None:
        st.exception('작업이 실패하였습니다.')
    else:           
        button_uuid = str(uuid.uuid4()).replace("-", "")
        button_id = re.sub("\d+", "", button_uuid)

        custom_css = f""" 
            <style>
                #{button_id} {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    background-color: rgb(255, 255, 255);
                    color: rgb(38, 39, 48);
                    padding: .25rem .75rem;
                    position: relative;
                    text-decoration: none;
                    border-radius: 4px;
                    border-width: 1px;
                    border-style: solid;
                    border-color: rgb(230, 234, 241);
                    border-image: initial;
                }} 
                #{button_id}:hover {{
                    border-color: rgb(246, 51, 102);
                    color: rgb(246, 51, 102);
                }}
                #{button_id}:active {{
                    box-shadow: none;
                    background-color: rgb(246, 51, 102);
                    color: white;
                    }}
            </style> """

        dl_link = (
            custom_css
            + f'<a download="{download_filename}.{download_type}" id="{button_id}" href="data:file/txt;base64,{data_b64}">{button_text}</a><br><br>'
        )
        st.success('성공! 다운로드 버튼이 나올 때까지 기다려 주세요.')
        st.markdown(dl_link, unsafe_allow_html=True)


def file_upload():
    '''
    변환 하고자 하는 파일 upload 버튼 생성
    '''
    uploaded_file = st.file_uploader(
        "upload file",
        type=['xlsx', 'csv', 'tsv', 'json']
    )

    if uploaded_file is not None:
        try:
            uploaded_file_type = extension_f(uploaded_file.name) #xlsx, csv, tsv, json
            uploaded_df = file_to_df(uploaded_file, uploaded_file_type)
            file_container = st.expander("업로드된 파일 미리보기")
            file_container.write(uploaded_df)
        except:
            st.info(
                f"""
                    데이터를 표시할 수 없습니다.
                """
            )
    else:
        st.info(
            f"""
                👆  xlsx, csv, tsv, json 형식의 파일을 업로드 해주세요!
            """
        )
        st.stop()

    return uploaded_df, uploaded_file


def get_file_type():
    cL, cR = st.columns([1,1])

    with cL:
        file_header_type = st.radio("헤더 유무 선택: ", ('포함', '미포함'))

    with cR:
        file_extension_type = st.radio("파일 형식 선택: ", ( 'xlsx', 'csv', 'tsv', 'json'), on_change=draw_loading)

    file_header_type = _val_header_type(file_header_type)
    return file_header_type, file_extension_type


def _val_header_type(file_header_type):
    if file_header_type == '포함':
        file_header_type = True
    else:
        file_header_type = False

    return file_header_type
