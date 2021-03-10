# Tuo sun 11.22.2020


############################################
import requests
import json
import pandas as pd


def get_api_json_to_dict(url):
    page = requests.Session().get(url)
    j = json.loads(page.content)
    return j

def get_appid_fast(save_path='spider_data'):
    appid_url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    j = get_api_json_to_dict(appid_url)
    df = pd.DataFrame.from_dict(j['applist']['apps'])
    df = df.sort_values(['appid'])
    df.to_csv(save_path+"/appid_list.csv", index_label="ID")

def get_appid(save_path='spider_data'):
    appid_url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    j = get_api_json_to_dict(appid_url)
    df = pd.DataFrame.from_dict(j['applist']['apps'])
    df = df.sort_values(['appid'])
    abandon_letters = ['®', '©', '™']
    appid_list_name = df['name']

    for i in range(len(appid_list_name)):
        for letter in abandon_letters:
            try:
                appid_list_name[i] = appid_list_name[i].replace(letter, '')
            except AttributeError:
                continue
    df.to_csv(save_path+"/appid_list.csv", index_label="ID")


class steam_conment_api(object):
    def __init__(self):
        self.review_url_head = 'https://store.steampowered.com/appreviews/'
        self.review_url_tail = '?json=1&start_offset=0&language=all&purchase_type=all&num_per_page=0'
        self.result_df = pd.DataFrame(columns=['id',
                                               'review_score',
                                               'review_score_desc',
                                               'total_positive',
                                               'total_negative'])
        self.restart_count = 0

    def get_comment_id(self, app_id):
        app_id = str(app_id)
        output_dict = {}
        json_dict = get_api_json_to_dict(self.review_url_head+app_id+self.review_url_tail)
        if json_dict['success']:
            output_dict['id'] = app_id
            output_dict['review_score'] = json_dict['query_summary']['review_score']
            output_dict['review_score_desc'] = json_dict['query_summary']['review_score_desc']
            output_dict['total_positive'] = json_dict['query_summary']['total_positive']
            output_dict['total_negative'] = json_dict['query_summary']['total_negative']
        return output_dict

    def get_comment_from_list(self, id_list):
        print('steamAPI.py:', len(id_list), 'in total')
        self.restart_system()

        for one_id in id_list[self.restart_count:]:
            if self.restart_count % 50==0:
                print(self.restart_count)
            one_dict = self.get_comment_id(one_id)
            self.result_df = self.result_df.append([one_dict], ignore_index=True)
            self.restart_count += 1

    def restart_system(self):
        if len(self.result_df) != 0:
            print('Restarted! Continue getting comment data from last checkpoint')
        else:
            self.restart_count = 0

