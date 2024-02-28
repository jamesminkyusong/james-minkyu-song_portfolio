from cmath import pi
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import streamlit as st
from libs.df_utils import df_to_b64
from libs.ui_utils import draw_title
from libs.file_utils import file_download, file_upload
from libs.mt import MT
from config import Config


def get_src_colname(df):
    st.subheader('Explore Current File')
    colname = st.radio('Select Column to Translate', df.columns)

    return colname


def translate_samples(mt, df, src_colname, src_lang_code, dst_lang_code):
    translate_f = lambda text: mt.send(src_lang_code, dst_lang_code, text)
    df['mt_' + src_colname] = df[src_colname].apply(translate_f)

    return df


def make_mt_col(mt, df, src_colname, src_lang_code, dst_lang_code):
    mt_result = list()
    progressbar = st.progress(0)
    progress_markdown = st.empty()
    progress_num = st.empty()

    for i, row in df.iterrows():
        mt_result.append(mt.send(src_lang_code, dst_lang_code,  row[src_colname]))

        progress_percent = (100 * (i+1)) // len(df)
        progress_markdown.markdown(f'{int(progress_percent)}% 완료 ({(i+1):,} / {len(df):,})')
        progressbar.progress(progress_percent)

    df['mt_' + src_colname] = mt_result

    return df


def get_lang_code():
    cL, cR = st.columns([1,1])
    lang_name_and_code = {
        '독일어': 'de',
        '러시아어': 'ru',
        '말레이시아어': 'ms',
        '베트남어': 'vi',
        '스페인어': 'es',
        '아랍어': 'ar',
        '영어': 'en',
        '이탈리아어': 'it',
        '인도네시아어': 'id',
        '일본어': 'ja',
        '중국어': 'zh',
        '태국어': 'th',
        '포르투갈어': 'pt',
        '프랑스어': 'fr',
        '한국어': 'ko',
        '힌디어': 'hi'
    }

    with cL:
        src_lang_code = st.selectbox("Source Lang", lang_name_and_code.keys())
        src_lang_code = lang_name_and_code[src_lang_code]
    with cR:
        dst_lang_code = st.selectbox("Translated Lang",  lang_name_and_code.keys())
        dst_lang_code = lang_name_and_code[dst_lang_code]

    return src_lang_code, dst_lang_code


def get_noti_permission():
    if st.button('Notification'):
        st.components.v1.html(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8" />
                <title></title>
            </head>
            <body>
                <script type="text/javascript">
                    window.onload = function () {
                        if (window.Notification) {
                            Notification.requestPermission();
                        }
                    }
                </script>
            </body>
            </html>
            """
        )
    else:
        st.info('👆 If you want to receive a notification, please click the button above.')


def push_noti():
    st.components.v1.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title></title>
        </head>
        <body>
            <script type="text/javascript">
                window.onload = function () {
                    if (Notification.permission !== 'granted') {
                        alert('notification is disabled');
                    }
                    else {
                        new Notification('MT completed!', {
                            icon: 'https://commons.wikimedia.org/wiki/File:Flitto_sns_profile.png',
                            body: 'Access this page to download!',
                        });
 
                    }
                }
            </script>
        </body>
        </html>
        """
    )


def btn_check_mt(mt, df, src_colname, src_lang_code, dst_lang_code):
    if st.button('Translate Samples'):
        if src_lang_code == dst_lang_code:
            st.exception('The source language and destination are the same')

        samples_df = translate_samples(mt, df[:3], src_colname, src_lang_code, dst_lang_code)
        st.dataframe(samples_df[[src_colname, f'mt_{src_colname}']])
    else:
        st.info('👆 Take a look at this sample and proceed if you are satisfied')


def btn_make_mt(mt, uploaded_file, df, src_colname, src_lang_code, dst_lang_code):
    if st.button('Translate ALL'):
        try:
            st.write(make_mt_col(mt, df, src_colname, src_lang_code, dst_lang_code))
            b64 = df_to_b64(df)
            
            file_download(
                b64,
                uploaded_file.name.split('.')[0] + '_mt',
                'xlsx',
                'Download',
            )

            push_noti()
        except:
            st.exception('There was an error in the translation process. Please check the file format and try again.')
    else:
        st.info('👆 Take a look at this sample and proceed to translate everything if you are satisfied!')


def main():
    config = Config()
    mt = MT(config)

    draw_title('File Translater Tool')
    st.write('EN ⟷ KO is Flitto, Others are Google Translate. Contact the Data Team for more specified usage.')

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    st.subheader('Upload Files')
    uploaded_df, uploaded_file = file_upload()

    st.subheader('Notification Setting')
    get_noti_permission()

    src_colname = get_src_colname(uploaded_df)
    st.write(uploaded_df.head(3))

    st.subheader('Select Language to Translate')
    src_lang_code, dst_lang_code = get_lang_code()

    btn_check_mt(mt, uploaded_df, src_colname, src_lang_code, dst_lang_code)
    btn_make_mt(mt, uploaded_file, uploaded_df, src_colname, src_lang_code, dst_lang_code)


if __name__ == '__main__':
    main()
