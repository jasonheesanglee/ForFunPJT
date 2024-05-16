import pytz
from PIL import Image
import streamlit as st
import time
from datetime import datetime
import pandas as pd
from BBobgi import BBobgi
bbobgi = BBobgi()

def df_col_list(file_, df):
    col_name = st.sidebar.text_input(
        f'{file_.name.split(".")[0]} 문서 내 대상이 될 컬럼명을 적어주세요!',
        placeholder='이름'
    )
    return list(df[col_name])

def upload_files(accept_multiple_files=False, sidebar=None, add_string=''):
    if sidebar:
        files = st.sidebar.file_uploader(
            f'{add_string}파일을 선택해 주세요.\n\
            현재 CSV, XLSX, TXT 파일만 지원합니다.',
            accept_multiple_files=accept_multiple_files
        )
    else:
        files = st.file_uploader(
            f'{add_string}파일을 선택해 주세요.\n\
            현재 CSV, XLSX, TXT 파일만 지원합니다.',
            accept_multiple_files=accept_multiple_files
        )
    return files

def extract_name_list(files):
    list_of_names = []
    for file_ in files:
        if file_.name.endswith('.csv') or file_.name.endswith('.xlsx'):
            if file_.name.endswith('.csv'):
                df = pd.read_csv(file_)
            else:
                df = pd.read_excel(file_)

            list_of_col = df_col_list(file_, df)
            list_of_names.extend(list_of_col)

        if file_.name.endswith('.txt'):
            with open(file_, 'r') as f:
                text = f.read()
                f.close()
            list_of_names.extend(bbobgi.extract_name_list(text))
    return list_of_names

st.set_page_config('자동 명함뽑기', page_icon='💵')

st.title('명함뽑기')
st.header('이름이 많으면 많을수록 뽑힐 확률이 늘어납니다!')

st.sidebar.title('환경설정')
files = upload_files(accept_multiple_files=True, sidebar=True, add_string='외부인원을 제외하려면 내부인원만 나열된 ')
out_button = st.sidebar.button('내부인원 확정!')
# col1, col2 = st.columns(2)
compare_list = extract_name_list(files)
n = st.text_input('뽑을 명함의 수를 숫자로 적어주세요.', placeholder=1)    
files = upload_files(accept_multiple_files=True, sidebar=False)
in_button = st.button('명함통 확정!')
target_list = extract_name_list(files)

# with col1:
if out_button and in_button:
        manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list, compare_list)
        choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)
elif in_button:
    manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list)
    choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)









# file_ = st.file_uploader('이름들이 들어있는 명함통 파일을 넣어주세요!')
# col_name = st.text_input('대상이 될 이름이 들어있는 컬럼명을 입력해주세요!')
# if file_ is not None:
#     df = pd.read_csv(file_)

# if
# count_manjokdo_complete_per_student(target_list)
# 