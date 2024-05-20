import re
import json
import base64
import random
from openai import OpenAI
import pandas as pd # type: ignore
from collections import defaultdict
import streamlit as st

try:
    api_key = st.secrets['OPENAI_API']
except:
    with open('config.json', 'r') as f:
        conf = json.load(f)
        api_key=conf['OPENAI_API']    

class BBobgi:
    def __init__(self, openai_api_key=api_key):
        self.pattern = '[^ㄱ-ㅎ가-힇a-zA-Z]'
        self.openai = OpenAI(api_key=openai_api_key)

    def extract_name_list(self, str_of_names:str) -> list:
        list_of_names = []
        str_of_names = str_of_names.replace('\n', ' ')
        str_of_names = str_of_names.replace('\t', ' ')
        str_of_names = str_of_names.replace(',', ' ')

        track = str_of_names.split()
        for name in track:
            name = re.sub(self.pattern, '', name)
            if name == '':
                continue
            list_of_names.append(name)

        return list_of_names

    def encode_img(self, image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def image_extract_time(self, image_path):
        image = self.encode_img(image_path)
        user_name = image_path.split('.')[0].split('/')[-1].split('_')[0]

        response = self.openai.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role':'system', 'content':'You are an expert in detecting date and time in any number formats and languages. \
                 You will be helping the user to detect date and time from the given image. \
                 You need to return the output in {%m%d_%H%M} format. \
                 Return : %m%d_%H%M'},
                {
                'role': 'user',
                'content':[
                    {'type': 'text',
                    'text':
                    '''Please detect date and time from this image.
                    Image is a screenshot of the final page of the google forms.
                    The date can be in any format, any language, but what we need is a month, date and time.
                    '''},
                    {'type':'image_url',
                    "image_url": {'url': f'data:image/png;base64,{image}'},
                    },
                ],
                },
            ],
            temperature=0.0,
        )
        pattern = r"\b(\d{4}_\d{4})\b"
        date_time = re.findall(pattern, response.choices[0].message.content)
        if date_time:
            return user_name, date_time[0]
        else:
            return user_name, 'Error'



    def count_manjokdo_complete_per_student(self, target_list:list, entire_list_of_candidates:list=None):
        '''
        path_to_csv : path to csv file.
        col_name : name of student.
        n : number of winners.
        Track : Target_Track
        '''

        manjokdo_dict = defaultdict(int)
        if entire_list_of_candidates:
            for name in target_list:
                name = re.sub(self.pattern, '', name)
                if name not in entire_list_of_candidates:
                    continue
                else:
                    manjokdo_dict[name] += 1
        else:
            for name in target_list:
                name = re.sub(self.pattern, '', name)
                manjokdo_dict[name] += 1
        return manjokdo_dict

    def choose_n_students(self, manjokdo_dict, n):
        BBobgi_tong = []
        
        for key, value in manjokdo_dict.items():
            for i in range(value):
                BBobgi_tong.append(key)

        random.shuffle(BBobgi_tong)
        final_lists = []
        count = 0

        while count != n:
            final = random.choice(BBobgi_tong)
            if final_lists!=[] and final in final_lists:
                continue
            else:
                final_lists.append(final)
                count += 1
        return final_lists

    

