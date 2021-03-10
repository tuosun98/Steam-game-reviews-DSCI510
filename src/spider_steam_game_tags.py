# Tuo sun 11.27.2020


############################################
import pandas as pd
from src.util import Tree_spider
from requests.exceptions import ProxyError


class steam_tag_spider(object):
    def __init__(self, save_path='spider_data'):
        self.appid_list = pd.read_csv(save_path+"/appid_used.csv").appid.astype(str)
        self.url_list = ['https://store.steampowered.com/app/'+appid for appid in self.appid_list]
        self.all_tag = []
        self.game_tags = []
        self.restart_count = 0
        self.failed = 0

    def get_game_tags(self):

        for url in self.url_list[self.restart_count:]:
            if self.restart_count % 50 == 0:
                print('steam_tags_spider: ', self.restart_count, 'Finished.', self.failed, 'failed in total')
            app_tag = [url[35:]]
            try:
                website = Tree_spider(url)
                website.set_spider_path(['body', 'div', 13, 6, 'div', -2, -6, 3, 'div', 'div', 'div', 7, 'div', 3])
                a_list = website.get_info(website.content).find_all("a")
            except IndexError:
                print('Index:', self.restart_count, ' Failed to get tags in ', url)
                print('Store page does not exist. Skipped this appid. ')
                self.game_tags.append(app_tag)
                self.failed += 1
                self.restart_count += 1
                continue
            except AttributeError:
                print('TypeError in' ,self.restart_count)
                self.game_tags.append(app_tag)
                self.restart_count += 1
            else:
                for a in a_list:
                    app_tag.append(a.string[14:-12])
                self.game_tags.append(app_tag)
                self.restart_count += 1

    def restart_system(self):
        if len(self.game_tags) != 0:
            print('Restarted! Continue getting game tag data from last checkpoint')
        else:
            self.restart_count = 0


def get_game_list_with_restart_system(save_path='spider_data'):
    steam_tag = steam_tag_spider(save_path=save_path)
    while True:
        try:
            steam_tag.get_game_tags()
        except ProxyError:
            print('ProxyError detected.')
            steam_tag.restart_system()
            continue
        else:
            break
    file = open(save_path+'/tag_data.txt', 'w')
    file.write(str(steam_tag.game_tags))
    file.close()
