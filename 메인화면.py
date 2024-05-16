import PIL.Image
import streamlit as st
import PIL

st.set_page_config(
    page_title='자동 명함뽑기',
    page_icon='💵'
)
st.title('자동 명함뽑기')
st.sidebar.success('명함뽑을 방식을 골라주세요!')
st.image('picknamecard.png')