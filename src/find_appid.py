from src.steamAPI import steam_conment_api
from src import nlp_functions
from requests.exceptions import ProxyError, ConnectionError

import warnings

warnings.filterwarnings('ignore')
punctuation_or_useless_word = ['\'s', '’s', '!', ',', ';', ':', '?', '"', '\'', '-', '--', 'pc', '#', 'steam', 'edition',
                               'episode', 'multiplayer', 'single-player', 'final', 'campaign', 'pack', 'next', 'game']


def get_comment_with_restart_system(appid_list):
    steamapi = steam_conment_api()
    while True:
        try:
            steamapi.get_comment_from_list(appid_list)
        except ProxyError:
            print('ProxyError detected.')
            continue
        except ConnectionError:
            print('ConnectionError detected.')
        else:
            break

    return steamapi.result_df


def get_name_mapping(website, if_find_by_count_letter=True, save_path='spider_data'):
    '''
    find similar name in website
    :param website:
    :param if_find_by_count_letter:
    :param save_path:
    :return:
    '''
    if website == 'ign':
        data = nlp_functions.read_ign_data(save_path=save_path)
    elif website == 'pc_gamer':
        data = nlp_functions.read_pc_gamer_data(save_path=save_path)
    elif website == 'ign_cross':
        data = nlp_functions.read_ign_data_cross(save_path=save_path)
    elif website == 'pc_gamer_cross':
        data = nlp_functions.read_pc_gamer_data_cross(save_path=save_path)

    data_no_same = nlp_functions.find_all_same(str(website) + "_steam.csv", 1, data, write_file=True, save_path=save_path)
    data_no_same['name_old'] = data_no_same['name']
    data_no_same['similar_name_list_old'] = tuple(data_no_same['similar_name_list'])
    name_data_no_same = data_no_same['name']
    for i in range(len(name_data_no_same)):
        name_data_no_same[i] = nlp_functions.change_roman_number(name_data_no_same[i])
    data_no_same['name'] = name_data_no_same

    similar_name_data_no_same = data_no_same['similar_name_list']
    rebuild_nonroman = []
    for i in range(len(similar_name_data_no_same)):
        one_rebuild_nonroman = []
        for j in range(len(similar_name_data_no_same[i])):
            one_rebuild_nonroman.append(nlp_functions.change_roman_number(similar_name_data_no_same[i][j]))
        rebuild_nonroman.append(one_rebuild_nonroman)
    data_no_same['similar_name_list'] = rebuild_nonroman
    data_no_same = nlp_functions.find_all_same(str(website) + "_steam.csv", 2, data_no_same, write_file=True, save_path=save_path)
    if if_find_by_count_letter:
        nlp_functions.find_by_count_letter(str(website) + "_steam.csv", data_no_same, save_path=save_path)


def main(save_path='spider_data'):
    get_name_mapping('ign', save_path=save_path)
    get_name_mapping('pc_gamer', save_path=save_path)
    get_name_mapping('ign_cross', save_path=save_path)
    get_name_mapping('pc_gamer_cross', save_path=save_path)