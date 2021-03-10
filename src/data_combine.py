import pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize
import datetime
import json
import csv
import nltk
try:
    stopwords = stopwords.words('english')
except LookupError:
    nltk.download()
    stopwords = stopwords.words('english')

punctuation = ['!', ',', ';', ':', '?', '"', '\'', '-']


def game_name_diff(name1, name2):
    '''
    This function will calculate a common rate for two names.
    It will abandon stopwords and punctuation
    The common rate is something like f1-score (something like harmonic-mean)
                     2 * the_rate_of_common_words_in_name_1   *    the_rate_of_common_words_in_name_2
    common_rate = -------------------------------------------------------------------------------------
                     the_rate_of_common_words_in_name_1    +    the_rate_of_common_words_in_name_2
    :param name1: name word 1
    :param name2: name word 2
    :return: floats
    '''
    name1_token = [word for word in word_tokenize(name1.lower()) if word not in punctuation and word not in stopwords]
    name2_token = [word for word in word_tokenize(name2.lower()) if word not in punctuation and word not in stopwords]
    common = len(set(name1_token) & set(name2_token))
    if common == 0:
        return 0
    else:
        common_rate = (2 * (common / len(name1_token)) * (common / len(name2_token))) / (
                    (common / len(name1_token)) + (common / len(name2_token)))
        return common_rate


def find_appid(name, data_frame):
    """
    find similar name for given name.

    :param name: a pd.series with names
    :param data_frame: a pd.dataframe with name column
    :return: This will a list of list with the length len(name)
    """

    data_frame['same_rate'] = data_frame['name'].apply(lambda x: game_name_diff(x, name))
    data_frame = data_frame.sort_values(['same_rate'], ascending=False)
    return data_frame.loc[data_frame.same_rate > 0.5]['name']


def get_similar_name_ign(start=0, length=999999, save_path='spider_data'):
    '''

    :param start: the start index (used for multiprocessing)
    :param length: the length index (used for multiprocessing)
    :param save_path:
    :return: write similar_relation.csv file
    This file is something like:
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    ...
    '''
    i = 0
    appid_list = read_appid_list(save_path=save_path)
    ign_data = read_ign_data(save_path=save_path)
    similar_list = []
    for index, row in ign_data.iloc[start:].iterrows():
        if i >= length:
            break
        similar_list.append(list(find_appid(row['name'], appid_list)))
        i += 1
        if i % 10 == 0:
            print('IGN ', start, ' to ', start+length, ': ', i, 'finished')
    print('Done for one process')
    if save_path=='quick_start_file':
        with open(save_path+'/similar_relation.csv', 'w', encoding='utf-8')as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[start], delimiter=' ')
            writer.writerow({start: ([start] + similar_list)})
    else:
        with open(save_path+'/similar_relation.csv', 'a', encoding='utf-8')as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[start], delimiter=' ')
            writer.writerow({start: ([start] + similar_list)})


def get_similar_name_pc(start=0, length=999999, save_path='spider_data'):
    '''

    :param start: the start index (used for multiprocessing)
    :param length: the length index (used for multiprocessing)
    :param save_path:
    :return: write similar_relation.csv file
    This file is something like:
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    [first_game_index, [similar_name_for_first_game], [similar_name_for_second_game],...]
    ...
    '''
    i = 0
    appid_list = read_appid_list(save_path=save_path)
    pc_game_data = read_pc_gamer_data(save_path=save_path)

    similar_list = []
    for index, row in pc_game_data.iloc[start:].iterrows():
        if i >= length:
            break
        similar_list.append(list(find_appid(row['name'], appid_list)))
        i += 1
        if i % 10 == 0:
            print('PC_gamer ', start, ' to ', start+length, ': ', i, 'finished')
    print('Done for one process')
    if save_path=='quick_start_file':
        with open(save_path+'/similar_relation_pc.csv', 'w', encoding='utf-8')as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[start], delimiter=' ')
            writer.writerow({start: ([start] + similar_list)})
    else:
        with open(save_path+'/similar_relation_pc.csv', 'a', encoding='utf-8')as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[start], delimiter=' ')
            writer.writerow({start: ([start] + similar_list)})


def get_similar_name_cross(save_path='spider_data'):
    '''
    cross method to get similar names between website. This function is designed for get as many rows as possible
    :param save_path:
    :return: will save a csv file like:
    ['ign', [similar name list for first game in pc gamer], [similar name list for second game in pc gamer]...]
    ['pc gamer', [similar name list for first game in ign], [similar name list for second game in ign]...]
    '''
    i = 0
    ign_data = read_ign_data(save_path=save_path)
    pc_game_data = read_pc_gamer_data(save_path=save_path)
    similar_list = []
    for index, row in pc_game_data.iterrows():
        similar_list.append(list(find_appid(row['name'], ign_data)))
        i += 1
        if i % 100 == 0:
            print('IGN cross', i, 'finished. Around 2000 for each')
    for index, row in ign_data.iterrows():
        similar_list.append(list(find_appid(row['name'], pc_game_data)))
        i += 1
        if i % 100 == 0:
            print('PC gamer cross', i, 'finished. Around 2000 for each')

    with open(save_path+'/similar_relation_cross.csv', 'w', encoding='utf-8')as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['names'])
        writer.writerow({'names': (['pc_gamer'] + similar_list[:len(pc_game_data)])})
        writer.writerow({'names': (['ign'] + similar_list[len(pc_game_data):])})


def read_appid_list(save_path='spider_data'):
    appid_list = pd.read_csv(save_path+'/appid_list.csv', dtype={'ID': 'str', 'appid': 'str', 'name': 'str'})
    appid_list = appid_list.drop(labels='ID', axis=1)
    appid_list = appid_list.dropna()
    return appid_list


def read_ign_data(save_path='spider_data'):
    ign_data = pd.read_csv(save_path+'/ign_data.csv')
    ign_data['name'] = ign_data['name'].apply(lambda x: x[:-7] if x[-6:] == 'Review' else x)
    return ign_data


def read_pc_gamer_data(save_path='spider_data'):
    pc_game_data = pd.read_csv(save_path+'/pc_gamer_game_data.csv')
    pc_game_data['name'] = pc_game_data['name'].apply(lambda x: x[:-7] if x[-6:] == 'review' else x)
    return pc_game_data


