import streamlit as st
from libs.ui_utils import draw_title
from libs.file_utils import file_download, file_upload, get_file_type
from libs.df_utils import df_to_b64


def main():
    draw_title('File Type Converter')

    st.subheader('Upload Files')
    uploaded_df, uploaded_file = file_upload()

    if uploaded_df.empty:
        st.exception('This File Type is not supported.')

    else:
        st.subheader('What type of conversion?')
        file_header_type, file_format_type = get_file_type()

        if st.button('Change File Type'):
            try:
                b64 = df_to_b64(uploaded_df, file_format_type, file_header_type)

                file_download(
                    b64,
                    uploaded_file.name.split('.')[0],
                    file_format_type,
                    f"Download to {file_format_type}",
                )
            except:
                st.exception('Something went wrong. Please try again or consult the Data Team.')
        else:
            st.info('👆 Begin Conversion!')


if __name__ == '__main__':
    main()