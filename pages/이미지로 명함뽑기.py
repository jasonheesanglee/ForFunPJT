import re
from datetime import datetime
import pandas as pd
import streamlit as st
from BBobgi import BBobgi

st.set_page_config(
    page_title='자동 명함뽑기',
    page_icon='💵'
)

api_button=None
sss = False
switch = False
switch_2 = True
target_list = None


st.title('이미지로 명함뽑기!')
st.sidebar.title('방식 설정')
openai_api_key = st.sidebar.text_input(label='OpenAI API Key를 입력해주세요.')
api_button=None
if openai_api_key:
    api_button = st.sidebar.button('키 입력 완료')
bbobgi = BBobgi(openai_api_key)

def get_all_images(list_names:list, list_images:list):
    name_time = {}
    for name, image in map(list_names, list_images):
        image_output = bbobgi.image_extract_time(image)
        name_time[name] = image_output
    return name_time

def df_col_list(file_, df):
    col_name = st.sidebar.text_input(
        f'{file_.name.split(".")[0]} 문서 내 대상이 될 컬럼명을 적어주세요!',
        placeholder='컬럼명'
    )
    if col_name:
        return list(df[col_name])
    else: 
        return list()

def upload_files(accept_multiple_files:bool=False, sidebar:bool=False, add_string:str=''):
    if sidebar:
        files = st.sidebar.file_uploader(
            f'{add_string}파일을 선택해 주세요.',
            accept_multiple_files=accept_multiple_files
        )
    else:
        files = st.file_uploader(
            f'{add_string}파일을 선택해 주세요.',
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
            if list_of_col:
                list_of_names.extend(list_of_col)
            else:
                st.warning('좌측에 컬렴명을 입력해 주세요!')
                return list_of_names

        elif file_.name.endswith('.txt'):
            list_of_names.extend(bbobgi.extract_name_list(file_.read().decode('utf-8')))
    return list_of_names

st.session_state['names'] = {}

col1, col2 = st.columns(2)
if api_button:
    with col1:
        st.header('문서 업로드')
        initial_time = st.text_input(label='설문조사를 내보낸 날짜와 시간', placeholder='%m%d_%H%M의 형식으로, 예시: 0525_1530')

        st.write('현재 CSV, XLSX, TXT 파일만 지원합니다.')
        st.write('이 부분은 필수가 아닙니다.')
        files = upload_files(accept_multiple_files=True, sidebar=False, add_string='외부인원을 제외하려면 내부인원만 나열된 ')
        if files:
            for file_ in files:
                file_name = file_.name
                if not (file_name.endswith('txt') or file_name.endswith('csv') or file_name.endswith('xlsx')):
                    switch=True
            if switch == True:
                st.error('업로드 실패! csv, xlsx, txt 파일만 지원합니다ㅠㅠ')
            else:
                st.success('업로드 성공!')

        else:
            st.warning('업로드 대기 중...')
        compare_list = extract_name_list(files)
        st.write('')
        st.write('')
        st.write('')
        st.write('이름이 많으면 많을수록 뽑힐 확률이 늘어납니다!')
        st.write('이미지 파일들을 선택해주세요!')
        
        
        files_ = upload_files(accept_multiple_files=True, sidebar=False, add_string='png, jpg, jpeg ')
        if files_:
            for file_ in files_:
                file_name = file_.name
                extension = file_name.split('.')[-1]
                title = file_name.split('.')[0].split('/')[-1]
                
                if extension != 'png' or extension != 'jpg' or extension != 'jpeg':
                    switch_2=False
                    st.error('png, jpg, jpeg 파일만 지원합니다ㅠㅠ')
                
                if not re.match('[ㄱ-ㅎ가-힇]', title.split('_')[0]) and datetime.strptime("_".join(title.split('_')[1:]), '%m%d'):
                    switch_2=False
                    st.error('파일명은 "성함_월일" 양식과 동일해야 합니다. ex) 홍길동_0520')

                else:
                    if openai_api_key:
                        user_name, extracted_time = bbobgi.image_extract_time(file_, openai_api_key)
                        if extracted_time.split('_')[0] != title.split('_')[-1]:
                            st.write(f'{file_}은 날짜가 다릅니다. 유효하지 않습니다.')
                        elif int(extracted_time.split('_')[-1]) < int(initial_time):
                            st.write(f'{file_}은 설문조사 시작 시간보다 이른 시간입니다. 유효하지 않습니다.')
                        else:
                            if st.session_state['names']:
                                sss = True
                                if extracted_time.split('_')[0] in st.session_state['names']:
                                    st.session_state['names'][extracted_time.split('_')[0]].append(user_name)
                                else: # extracted_time.split('_')[0] not in st.session_state['names']:
                                    st.session_state['names'][extracted_time.split('_')[0]] = [user_name]
                                # else:
                                    # st.session_state['names'][extracted_time.split('_')[0]] = [user_name]
                    else:
                        st.error('좌측에서 OpenAI API Key를 입력해주세요.')

            if switch_2 == False:
                st.error('업로드 실패!')
            else:
                st.success('업로드 성공!')
        else:
            st.warning('업로드 대기 중...')

    with col2:
        st.header('명함을 뽑아볼까요?')
        st.write('왼쪽 업로드를 마치고 여기를 봐주세요!',)
        if sss:
            target_list = st.session_state['names'][extracted_time.split('_')[0]]

        n_input = st.text_input('뽑을 명함의 수를 숫자로 적어주세요.', placeholder='1')
        in_button = st.button('명함 뽑기!')
        try:
            n = int(n_input)
        except ValueError:
            st.error("Please enter a valid number for the count of names to draw.")
            n = 0

        cont = st.container(height=300, border=True)
        if target_list and in_button:
            if n!= '' and switch_2:
                if not switch:
                    manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list, compare_list)
                    choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)
                    cont.write(', '.join(choose_n))

                else:
                    manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list)
                    choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)
                    cont.write(', '.join(choose_n))