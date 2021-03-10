import pandas as pd
from src.steamAPI import steam_conment_api
from requests.exceptions import ProxyError, ConnectionError
import datetime


def read_ign_data(save_path='spider_data'):
    """
    read ign data and transfer the date time. Drop duplicates name. Delete useless words(Review).
    :return: ign_data pd.dataframe
    """
    ign_data = pd.read_csv(save_path+'/ign_data.csv')
    ign_data['name'] = ign_data['name'].apply(lambda x: x.replace(' Review', '') if 'Review' in x else x)
    ign_data['release_date_ign'] = ign_data['release_date_ign'].apply(
        lambda x: datetime.datetime.strptime(x, "%b %d, %Y"))
    ign_data = ign_data.drop(labels=['ID'], axis=1)
    ign_data.columns = ['ign_name', 'ign_score', 'ign_release_data', 'ign_comments']
    ign_data = ign_data.drop_duplicates(subset=['ign_name']).reset_index(drop=True)
    return ign_data


def read_pc_gamer_data(save_path='spider_data'):
    """
    read ign data and transfer the date time. Drop duplicates name. Delete useless words(Review).
    Drop error columns named data which is from pc_gamer spider.
    :return: pc_gamer pd.dataframe
    """
    pc_gamer_data = pd.read_csv(save_path+'/pc_gamer_game_data.csv')
    pc_gamer_data['name'] = pc_gamer_data['name'].apply(lambda x: x.replace(' review', '') if 'review' in x else x)
    pc_gamer_data['release_date_pc_gamer'] = pc_gamer_data['date'].apply(
        lambda x: datetime.datetime.strptime(x, "%d %B %Y"))
    pc_gamer_data = pc_gamer_data.drop(labels='date', axis=1)
    pc_gamer_data = pc_gamer_data.drop(labels=['ID'], axis=1)
    pc_gamer_data = pc_gamer_data.drop_duplicates(subset=['name']).reset_index(drop=True)
    pc_gamer_data.columns = ['pc_gamer_name', 'pc_gamer_score', 'pc_gamer_release_data']
    return pc_gamer_data


def get_comment_with_restart_system(appid_list):
    """
    get a comment with a appid_list. If web connection is not stable. The script can restart from checkpoints.
    :param appid_list: Get comment information from appid_list through steam API
    :return: return a dataframe of steam comments.
    """
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

def get_names_data_in_three_set(save_path='spider_data'):
    '''
    Get and process data in three csv file, ign_steam, pc_gamer_steam and ign_cross_steam.
    This function is something like a merge function. It drop useless columns and reindex the rows
    :param save_path:
    :return: a df of games that appears in all three website
    '''

    ign_data = pd.read_csv(save_path+'/ign_steam.csv')
    pc_gamer_data = pd.read_csv(save_path+'/pc_gamer_steam.csv')

    cross_data = pd.read_csv(save_path+'/ign_cross_steam.csv')


    # merge them by steam name
    all_ign_pcgamer_steam_data = pd.merge(ign_data, pc_gamer_data, left_on='steam_name', right_on='steam_name', how='inner')
    all_ign_pcgamer_steam_data = all_ign_pcgamer_steam_data.drop(labels=['ID_x', 'ID_y'], axis=1)
    all_ign_pcgamer_steam_data.columns = ['name_in_ign', 'name_in_steam', 'name_in_pc_gamer']
    all_ign_pcgamer_steam_data = all_ign_pcgamer_steam_data.loc[:, ['name_in_ign', 'name_in_pc_gamer', 'name_in_steam']]


    #ign and pcgamer have them, but they are not in steam appid.
    # steam_name in cross_data is actually game name in pcgamer
    in_ign_pc_gamer_not_in_steam = cross_data.loc[~cross_data.steam_name.isin(all_ign_pcgamer_steam_data.name_in_pc_gamer)]
    in_ign_pc_gamer_not_in_steam.columns = ['ID', 'name_in_pc_gamer', 'name_in_ign']

    steam_pc_gamer_ign = pd.merge(pc_gamer_data, in_ign_pc_gamer_not_in_steam, left_on='name', right_on='name_in_pc_gamer', how='inner')
    steam_pc_gamer_ign = steam_pc_gamer_ign.drop(labels=['ID_x', 'ID_y', 'name_in_pc_gamer'], axis=1)
    steam_pc_gamer_ign.columns = ['name_in_pc_gamer', 'name_in_steam', 'name_in_ign']
    steam_pc_gamer_ign = steam_pc_gamer_ign.loc[:, ['name_in_ign', 'name_in_pc_gamer', 'name_in_steam']]

    steam_ign_pc_gamer = pd.merge(ign_data, in_ign_pc_gamer_not_in_steam, left_on='name', right_on='name_in_ign', how='inner')
    steam_ign_pc_gamer = steam_ign_pc_gamer.drop(labels=['ID_x', 'ID_y', 'name'], axis=1)
    steam_ign_pc_gamer.columns = ['name_in_steam', 'name_in_pc_gamer', 'name_in_ign']
    steam_ign_pc_gamer = steam_ign_pc_gamer.loc[:, ['name_in_ign', 'name_in_pc_gamer', 'name_in_steam']]

    data_names = pd.concat([all_ign_pcgamer_steam_data, steam_pc_gamer_ign, steam_ign_pc_gamer])
    data_names = data_names.drop_duplicates(subset=['name_in_steam']).sort_values(['name_in_steam'])
    return data_names


def read_appid_list(save_path='spider_data'):
    appid_list = pd.read_csv(save_path+'/appid_list.csv', dtype={'ID': 'str', 'appid': 'str', 'name': 'str'})
    appid_list = appid_list.drop(labels='ID', axis=1)
    return appid_list


def generate_comment(save_path='spider_data'):
    '''
    This function will use steam api to get comment for every game in data names
    :param save_path:
    :return: this will a csv file of comments information for every game
    '''
    ign_data = read_ign_data(save_path=save_path)
    pc_gamer_data = read_pc_gamer_data(save_path=save_path)
    data_names = get_names_data_in_three_set(save_path=save_path)
    appid_list = read_appid_list(save_path=save_path)
    appid_useful = appid_list.loc[appid_list.name.isin(data_names.name_in_steam)].dropna()
    appid_useful.to_csv(save_path+"/appid_used.csv", mode='w')
    appids = appid_useful.appid
    appid_useful[["appid"]] = appid_useful[["appid"]].astype(int)
    comments = get_comment_with_restart_system(appids)
    comments[['id']] = comments[['id']].astype(int)
    comments = pd.merge(comments, appid_useful, left_on='id', right_on='appid')
    comments = pd.merge(comments, data_names, left_on='name', right_on='name_in_steam')
    comments = pd.merge(comments, ign_data, left_on='name_in_ign', right_on='ign_name', how='inner')
    comments = pd.merge(comments, pc_gamer_data, left_on='name_in_pc_gamer', right_on='pc_gamer_name', how='inner')
    comments = comments.drop(labels=['name_in_ign', 'name_in_pc_gamer', 'name_in_steam', 'ign_name', 'pc_gamer_name', 'id'], axis=1)
    try:
        comments = comments.drop(labels=['0'], axis=1)
    except KeyError:
        pass

    print(len(comments), 'games in total')
    comments.to_csv(save_path+"/reviews_data.csv", mode='w', index=None)

