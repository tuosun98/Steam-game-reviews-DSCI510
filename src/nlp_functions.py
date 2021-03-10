import csv
import pandas as pd
import datetime
from nltk.corpus import stopwords
from nltk import word_tokenize
from src.data_combine import game_name_diff
import collections
import nltk
import warnings


warnings.filterwarnings('ignore')
stopwords = stopwords.words('english')
punctuation_or_useless_word = ['\'s', '’s', '!', ',', ';', ':', '?', '"', '\'', '-', '--', 'pc', '#', 'steam', 'edition',
                               'episode', 'multiplayer', 'single-player', 'final', 'campaign', 'pack', 'next', 'game']


def read_appid_list(save_path='spider_data'):
    appid_list = pd.read_csv(save_path+'/appid_list.csv', dtype={'ID': 'str', 'appid': 'str', 'name': 'str'})
    appid_list = appid_list.drop(labels='ID', axis=1)
    return appid_list


def token(word):
    word_token = [word for word in word_tokenize(word.lower()) if word not in punctuation_or_useless_word and word not in stopwords]
    word_token.sort()
    return word_token


def game_name_have_number(string):
    try:
        for i in string:
            if i.isdigit():
                return 1
        return 2
    except TypeError:
        return 'wrong'


def read_ign_data(save_path='spider_data'):
    ign_data = pd.read_csv(save_path+'/ign_data.csv')
    ign_data['name'] = ign_data['name'].apply(lambda x: x.replace(' Review', '') if 'Review' in x else x)
    ign_data['release_date_ign'] = ign_data['release_date_ign'].apply(
        lambda x: datetime.datetime.strptime(x, "%b %d, %Y"))
    ign_data['similar_name_list'] = read_relation_similar('ign', save_path=save_path)
    ign_data = ign_data.drop_duplicates(subset=['name']).reset_index(drop=True)
    return ign_data


def read_pc_gamer_data(save_path='spider_data'):
    pc_gamer_data = pd.read_csv(save_path+'/pc_gamer_game_data.csv')
    pc_gamer_data['name'] = pc_gamer_data['name'].apply(lambda x: x.replace(' review', '') if 'review' in x else x)

    pc_gamer_data['release_date_pc_gamer'] = pc_gamer_data['date'].apply(
        lambda x: datetime.datetime.strptime(x, "%d %B %Y"))
    pc_gamer_data = pc_gamer_data.drop(labels='date', axis=1)
    pc_gamer_data['similar_name_list'] = read_relation_similar('pc_gamer', save_path=save_path)
    pc_gamer_data = pc_gamer_data.drop_duplicates(subset=['name']).reset_index(drop=True)
    return pc_gamer_data



def read_ign_data_cross(save_path='spider_data'):
    ign_data = pd.read_csv(save_path+'/ign_data.csv')
    ign_data['similar_name_list'] = read_relation_similar_cross('ign', save_path=save_path)
    ign_data['name'] = ign_data['name'].apply(lambda x: x.replace(' Review', '') if 'Review' in x else x)
    ign_data = ign_data.drop_duplicates(subset=['name']).reset_index(drop=True)
    return ign_data


def read_pc_gamer_data_cross(save_path='spider_data'):
    pc_gamer_data = pd.read_csv(save_path+'/pc_gamer_game_data.csv')
    pc_gamer_data['name'] = pc_gamer_data['name'].apply(lambda x: x.replace(' review', '') if 'review' in x else x)
    pc_gamer_data = pc_gamer_data.drop(labels='date', axis=1)
    pc_gamer_data['similar_name_list'] = read_relation_similar_cross('pc_gamer', save_path=save_path)
    pc_gamer_data = pc_gamer_data.drop_duplicates(subset=['name']).reset_index(drop=True)
    return pc_gamer_data


def read_relation_similar_cross(website_name, save_path='spider_data'):
    abandon_letters = ['®', '©', '™']
    similar_name_dict = {}
    with open(save_path+'/similar_relation_cross.csv', newline='', encoding='gb18030', errors='ignore') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if not row:
                continue
            one_row = eval(row[0])
            similar_name_dict[one_row[0]] = one_row[1:]

    similar_name_list = similar_name_dict[website_name]
    for i in range(len(similar_name_list)):
        for j in range(len(similar_name_list[i])):
            for letter in abandon_letters:
                similar_name_list[i][j] = similar_name_list[i][j].replace(letter, '')

    return similar_name_list



def read_relation_similar(website, save_path='spider_data'):
    abandon_letters = ['®', '©', '™']
    similar_name_dict = {}
    if website == 'ign':
        with open(save_path+'/similar_relation.csv', newline='', encoding='gb18030', errors='ignore') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if not row:
                    continue
                one_row = eval(row[0])
                similar_name_dict[one_row[0]] = one_row[1:]
    elif website == 'pc_gamer':
        with open(save_path+'/similar_relation_pc.csv', newline='', encoding='gb18030', errors='ignore') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if not row:
                    continue
                one_row = eval(row[0])
                similar_name_dict[one_row[0]] = one_row[1:]
    sorted_keys = sorted(similar_name_dict)
    similar_name_list = []
    for key in sorted_keys:
        similar_name_list += similar_name_dict[key]
    for i in range(len(similar_name_list)):
        for j in range(len(similar_name_list[i])):
            for letter in abandon_letters:
                similar_name_list[i][j] = similar_name_list[i][j].replace(letter, '')

    return similar_name_list


def name_and_similar_name(data):
    similar_dict = {}
    data_name = data.name
    data_similar_list = data.similar_name_list
    for i in range(len(data_name)):
            similar_dict[data.name[i]] = data_similar_list[i]
    return similar_dict


def change_roman_number(word):
    word = word.replace(' III', ' 3')
    word = word.replace(' II', ' 2')
    word = word.replace(' IV', ' 4')
    word = word.replace(' VI', ' 6')
    word = word.replace(' V ', ' 5')
    word = word.replace(' V:', ' 5')
    word = word.replace(' VIII', ' 8')
    word = word.replace(' VII', ' 7')
    word = word.replace(' IX', ' 9')
    word = word.replace(' X', ' 10')
    return word


def find_all_same(save_file_name, time, data, write_file=False, save_path='spider_data'):
    similar_dict = name_and_similar_name(data)

    similar_rate = []
    for key in similar_dict:
        similar_rate.append(list(map(lambda x: round(game_name_diff(key, x), 2), similar_dict[key])))
    data['rate'] = similar_rate

    all_same = []
    same_names = []
    for row_index in range(len(data)):
        if data.iloc[row_index].similar_name_list:
            one_name = token(data.iloc[row_index]['name'])
            one_similar_list = list(map(token, data.iloc[row_index].similar_name_list))
            if one_name in one_similar_list:
                if time == 1:
                    same_names.append(data.iloc[row_index].similar_name_list[one_similar_list.index(one_name)])
                elif time == 2:
                    same_names.append(data.iloc[row_index].similar_name_list_old[one_similar_list.index(one_name)])

                all_same.append(True)
            else:
                all_same.append(False)
        else:
            all_same.append('no_similar')

    data['if_same'] = all_same

    data_no_same = data.drop(index=data[data['if_same'] == 'no_similar'].index)
    if write_file:
        if time == 1:
            df_to_write = data.loc[data['if_same'] == True]['name'].to_frame()
            df_to_write['steam_name'] = same_names
            df_to_write.to_csv(save_path+"/" + save_file_name, index_label="ID", mode='w')
        elif time == 2:
            df_to_write = data.loc[data['if_same'] == True]['name_old'].to_frame()
            df_to_write['steam_name'] = same_names
            df_to_write.to_csv(save_path+"/" + save_file_name, index_label="ID", mode='a', header=0)
    data_no_same = data_no_same.drop(index=data_no_same[data['if_same'] == True].index).reset_index(drop=True)
    return data_no_same


def find_by_count_letter(save_file_name, data, max_diff=0, save_path='spider_data'):
    similar_df_dict = {'name': [], 'steam_name': []}
    for i in range(len(data)):
        min_num_diff = 99999
        if len(data.iloc[i]['name'].split(' ')) == 1:
            continue
        name_digit = [letter for letter in data.iloc[i]['name'] if letter.isdigit()]
        name_letter = [letter.lower() for letter in data.iloc[i]['name'] if letter.isalpha() or letter.isdigit()]
        for k in range(100):
            # digit difference is not all allowed
            name_letter += name_digit
        similar_list = data.iloc[i]['similar_name_list']
        name_count = collections.Counter(name_letter)
        for similar_name in similar_list:
            if '-' in similar_name:
                continue
            similar_name_digit = [letter for letter in similar_name if letter.isdigit()]
            if sorted(similar_name_digit) != sorted(name_digit):
                continue
            similar_name_letter = [letter.lower() for letter in similar_name if letter.isalpha() or letter.isdigit()]

            similar_name_count = collections.Counter(similar_name_letter)
            num_diff = sum((name_count-similar_name_count).values())
            if min_num_diff > num_diff:
                min_num_diff = num_diff
                best_similar_name = similar_name
        if min_num_diff <= max_diff:
            similar_df_dict['name'].append(data.iloc[i]['name'])
            similar_df_dict['steam_name'].append(best_similar_name)
    similar_df = pd.DataFrame(similar_df_dict)

    similar_df.to_csv(save_path+"/"+save_file_name, index_label="ID", mode='a', header=0)

    data = data.drop(index=data[data['name'].isin(similar_df['name'])].index)

    return data


