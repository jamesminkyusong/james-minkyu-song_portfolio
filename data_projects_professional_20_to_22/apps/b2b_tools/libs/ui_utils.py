import streamlit as st


def draw_title(title_name):
    st.set_page_config(page_icon="✂️", page_title= title_name)
    st.title(title_name)


def draw_loading():
    return st.spinner(text='작업중...')
