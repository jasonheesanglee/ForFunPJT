import os
import re

from datetime import datetime
import pandas as pd
import streamlit as st
import PIL
from BBobgi import BBobgi
# from streamlit import type_util


st.set_page_config(
    page_title='자동 명함뽑기',
    page_icon='💵'
)

target_list = None
extracted_switch = False

st.title('이미지로 명함뽑기!')
st.sidebar.title('방식 설정')

openai_api_key = st.sidebar.text_input(label='OpenAI API Key를 입력해주세요.', type='password', disabled=False)
if 'api_switch' not in st.session_state:
    st.session_state['api_switch'] = False

api_button = st.sidebar.button('키 입력 완료')
if api_button:
    st.session_state['api_switch'] = True
elif st.session_state['api_switch'] == True:
    api_button = True

if 'in_button' not in st.session_state:
    st.session_state['in_button'] = False

if 'switch_2' not in st.session_state:
    st.session_state['switch_2'] = {}

if 'names' not in st.session_state:
    st.session_state['names'] = {}

bbobgi = BBobgi(openai_api_key)

##############################################################################################################
##############################################################################################################
##############################################################################################################

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


def save_image(image:PIL.Image, file_name:str):
    if 'image_storage' not in st.session_state:
        st.session_state['image_storage'] = []
    image.save(file_name)
    st.session_state['image_storage'].append(file_name)


def clear_image_hist():
    st.session_state['image_storage'] = []

def upload_files(accept_multiple_files:bool=False, sidebar:bool=False, add_string:str='', type=None):
    if sidebar:
        if type:
            files = st.sidebar.file_uploader(
                f'{add_string}파일을 선택해 주세요.',
                accept_multiple_files=accept_multiple_files,
                type=type
            )
        else:
            files = st.sidebar.file_uploader(
                f'{add_string}파일을 선택해 주세요.',
                accept_multiple_files=accept_multiple_files
            )
    else:
        if type:
            files = st.file_uploader(
                f'{add_string}파일을 선택해 주세요.',
                accept_multiple_files=accept_multiple_files,
                type=type
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
        file_name = file_.name.lower()
        if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_)
            else:
                df = pd.read_excel(file_)

            list_of_col = df_col_list(file_, df)
            if list_of_col:
                list_of_names.extend(list_of_col)
            else:
                st.warning('컬렴명을 입력해 주세요!')
                return list_of_names

        elif file_name.endswith('.txt'):
            list_of_names.extend(bbobgi.extract_name_list(file_.read().decode('utf-8')))
    return list_of_names

##############################################################################################################
##############################################################################################################
##############################################################################################################


compare_list=None
switch = False

initial_time = st.sidebar.text_input(label='설문조사를 내보낸 날짜와 시간, %m%d_%H%M의 형식으로', placeholder='예시: 0525_1530')
if initial_time:
    initial_date = initial_time.split('_')[0]
    initial_time = initial_time.split('_')[1]

    if initial_date not in st.session_state['names'].keys():
        st.session_state['names'][initial_date] = []
    
st.sidebar.write('현재 CSV, XLSX, TXT 파일만 지원합니다.')
st.sidebar.write('이 부분은 필수가 아닙니다.')
files = upload_files(accept_multiple_files=True, sidebar=True, add_string='외부인원을 제외하려면 내부인원만 나열된 ')
if files:
    for file_ in files:
        file_name = file_.name
        extension = file_name.split('.')[-1]
        if extension.lower() not in ['txt', 'csv', 'xlsx']:
            switch=True
    if switch == True:
        st.sidebar.error('업로드 실패! csv, xlsx, txt 파일만 지원합니다ㅠㅠ')
    else:
        st.sidebar.success('업로드 성공!')

else:
    st.sidebar.warning('업로드 대기 중...')
compare_list = extract_name_list(files)




col1, col2 = st.columns(2)
if st.session_state['api_switch']:
    with col1:
        st.header('문서 업로드')
        st.write('이름이 많으면 많을수록 뽑힐 확률이 늘어납니다!')
        st.write('이미지 파일들을 선택해주세요!')
        if st.session_state['in_button'] == True:
            st.success('명함뽑기 버튼을 눌러 이미지 업로드는 비활성화 되었습니다!')
        else:
            files_ = upload_files(accept_multiple_files=True, sidebar=False, add_string='png, jpg, jpeg ', type=['jpg', 'png', 'jpeg'])
            if files_:
                for idx, file_ in enumerate(files_):
                    file_name = file_.name
                    extension = file_name.split('.')[-1]
                    title_file = file_name.split('.')[0]

                    title_user = title_file.split('_')[0]
                    title_date = title_file.split('_')[1]
                    
                    if extension.lower() not in ['png', 'jpg', 'jpeg']:
                        st.session_state['switch_2'][file_name] = False
                        st.error(f'png, jpg, jpeg 파일만 지원합니다ㅠㅠ {file_name}을 수정/제거해주세요')


                    elif re.match(r"^[가-힣]+_", title_file):
                        st.session_state['switch_2'][file_name] = False
                        st.error(f'파일명은 "성함_월일" 양식과 동일해야 합니다. ex) 홍길동_0520, {file_name}를 수정해주세요')

                    else:
                        try:
                            datetime.strptime(title_date, '%m%d')
                        except ValueError:
                            st.session_state['switch_2'][file_name] = False
                            st.error('파일명은 "성함_월일" 양식과 동일해야 합니다. 월-일. ex) 홍길동_0520')

                        else:
                            content = PIL.Image.open(file_)
                            save_image(file_name=file_name, image=content)
                            img_path = st.session_state['image_storage'][-1]
                            user_name, extracted_time = bbobgi.image_extract_time(img_path)
                            if extracted_time != None:
                                extracted_date = extracted_time.split('_')[0]
                                extracted_time = extracted_time.split('_')[1]

                                if initial_date != title_date:
                                    st.write(f'{file_name}에서 검출된 날짜: {extracted_date}은/는 날짜가 다릅니다. 유효하지 않습니다.')
                                    
                                elif int(extracted_time) < int(initial_time):
                                    st.write(f'{file_name}에서 검출된 시간: {extracted_time}은/는 설문조사 시작 시간보다 이른 시간입니다. 유효하지 않습니다.')
                                else:
                                    if extracted_date in st.session_state['names']:
                                        st.session_state['switch_2'][file_name] = True
                                        st.session_state['names'][extracted_date].append(user_name)
                                    else: 
                                        st.session_state['switch_2'][file_name] = True
                                        st.session_state['names'][extracted_date] = [user_name]

                            else:
                                st.write(f'{file_name}에서 날짜와 시간이 확인되지 않습니다. 유효하지 않습니다.')

                            
                st.success(f'{list(st.session_state["switch_2"].values()).count(True)}개 업로드 성공!')
                if False in st.session_state['switch_2'].values():
                    st.error(f'{", ".join([k for k,v in st.session_state["switch_2"].items() if v==False])} 업로드 실패!')
                
            else:
                st.warning('업로드 대기 중...')

    with col2:
        st.header('명함을 뽑아볼까요?')
        st.write('왼쪽 업로드를 마치고 여기를 봐주세요!',)
        if initial_time:
            try:
                target_list = st.session_state['names'][initial_date]
            except KeyError:
                target_list = []


        n_input = st.text_input('뽑을 명함의 수를 숫자로 적어주세요.', placeholder='1')
        in_button = st.button('명함 뽑기!')
        try:
            n = int(n_input)
        except ValueError:
            st.error("Please enter a valid number for the count of names to draw.")
            n = 0
        cont = st.container(height=300)
        if target_list and in_button:
            st.session_state['in_button'] = True
            if n != '':
                if True in st.session_state['switch_2'].values():
                    if not switch:
                        manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list, compare_list)
                        choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)
                        if choose_n:
                            cont.write(', '.join(choose_n))
                        else:
                            cont.warning('비교군에 맞는 대상자가 없습니다!')

                    else:
                        manjokdo_done = bbobgi.count_manjokdo_complete_per_student(target_list)
                        choose_n = bbobgi.choose_n_students(manjokdo_dict=manjokdo_done, n=n)
                        if choose_n != []:
                            cont.write(', '.join(choose_n))
                        else:
                            cont.warning('대상자가 없습니다!')
                else:
                    cont.warning('날짜, 시간이 제대로 검출된 파일이 없습니다. 본 페이지를 새로고침 해주세요')
            else:
                cont.warning('뽑을 명함의 수를 적어주세요!')

        elif target_list == []:
            cont.warning('검출된 대상자가 없습니다.')
        elif not in_button:
            cont.error('명함 뽑기! 버튼을 눌러주세요!')
        else:
            cont.write(target_list)
            cont.write(st.session_state)