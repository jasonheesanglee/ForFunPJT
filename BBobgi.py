import re
import random
import pandas as pd # type: ignore
from collections import defaultdict


class BBobgi:
    def __init__(self):
        self.pattern = '[^ㄱ-ㅎ가-힇a-zA-Z]'

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

    def shuffle_list(self, BBobgi_tong:list):
        
        return shuffled

    def choose_n_students(self, manjokdo_dict, n):
        BBobgi_tong = []
        
        for key, value in manjokdo_dict.items():
            for i in range(value):
                BBobgi_tong.append(key)
        print(BBobgi_tong)

        random.shuffle(BBobgi_tong)
        final_lists = []
        count = 0
        while count != n:
            final = random.choice(BBobgi_tong)
            if final in final_lists:
                continue
            else:
                final_lists.append(final)
                count += 1
        return final_lists



