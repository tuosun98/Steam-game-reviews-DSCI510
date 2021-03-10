# Tuo sun 11.21.2020


############################################
import pandas as pd
from src.util import Tree_spider
import json
from requests.exceptions import ProxyError


class pc_gamer_spider(object):
    """
    Parent class is Tree_spider. Getting the data need two steps
        Get the url list which contains each game review in pc_gamer about 2000
        Get game information from url list (this will take lots of time).

    The name of game and the url (contains the score and release date) will be recorded into pandas.Dataframe
    The name of game, review release date and the game score will be recorded into pandas.Dataframe
    """
    def __init__(self, save_path='spider_data', quick_start=False):
        """

        """
        self.month_website_list = []
        self.json2list()
        self.game_website_df = pd.DataFrame(columns=['name', 'website'])
        self.result_df = pd.DataFrame(columns=['name', 'score', 'release_date_pc_gamer'])
        self.restart_count = 0
        self.save_path = save_path
        self.quick_start = quick_start

    def quick_start_url_list(self):
        self.month_website_list = ['https://www.pcgamer.com/dirt-5-review/',
                                   'https://www.pcgamer.com/yakuza-like-a-dragon-review/',
                                   'https://www.pcgamer.com/crusader-kings-3-review/']
        self.game_website_df = self.game_website_df.append([{'name': 'Dirt 5', 'website': self.month_website_list[0]}], ignore_index=True)
        self.game_website_df = self.game_website_df.append([{'name': 'Yakuza: Like a Dragon', 'website': self.month_website_list[1]}], ignore_index=True)
        self.game_website_df = self.game_website_df.append([{'name': 'Crusader Kings 3', 'website': self.month_website_list[2]}], ignore_index=True)
        self.game_website_df.to_csv(self.save_path+"/pc_gamer_url_list.csv", index_label="ID")

    def quick_start_get_info(self):
        self.get_game_info()
        self.write_csv()

    def json2list(self):
        """
        convert json file to a list of url segmented by month. Each url contains a set of games.
        """
        month_base_website = 'https://www.pcgamer.com/reviews/archive/'
        with open("src/pcgamer_month.json", 'r') as f:
            month_tails = json.loads(f.read())
        for year in month_tails:
            for month in month_tails[year][::-1]:
                self.month_website_list.append(month_base_website + '/' + year + '/' + str(month))

    def get_game_list(self):
        """
        Get the game url from every game-set url list.
        Each game-set include some games.
        And recorded them into pandas.Dataframe

        This method have a restart system. If the exception is raised due to HTTP connection.
        Call the method again, the method will restart before the website which caused exception.
        """
        self.restart_system('website')
        for url in self.month_website_list[self.restart_count:]:
            print(url)
            website = Tree_spider(url)
            website.set_spider_path(['body', 13, 5, 'div', 5, 'ul'])
            a_list = website.get_info(website.content).find_all("a")
            for a in a_list:
                    self.game_website_df = self.game_website_df.append([{'name': a.string, 'website': a['href']}], ignore_index=True)
            self.restart_count += 1

    def get_game_info(self, start=0, length=9999999):
        """
        Get the game review data from  game url list
        And recorded them into pandas.Dataframe

        This method have a restart system. If the exception is raised due to HTTP connection.
        Call the method again, the method will restart before the website which caused exception.
        :param start: set the start index                                       (Used for Multithreading url)
        :param length: the number of url you are going to load for this time    (Used for Multithreading url)
        """
        if len(self.game_website_df) == 0:
            self.game_website_df = pd.read_csv(self.save_path + '/pc_gamer_url_list.csv')
        self.restart_system('game_info')
        for url in self.game_website_df.website[start+self.restart_count:]:
            if self.restart_count >= length:
                self.restart_count += 0
                break
            if self.restart_count % 50 == 0:
                print(self.restart_count)
            try:
                one_game_spider = Spider_pc_gamer(url)
                one_game_spider.set_spider_path(one_game_spider.main_path)
                game_header = one_game_spider.get_info(one_game_spider.content)

                one_game_spider.set_spider_path(one_game_spider.name_path)
                name = one_game_spider.get_info(game_header)

                one_game_spider.set_spider_path(one_game_spider.score_path)
                score = one_game_spider.get_info(game_header)

                one_game_spider.set_spider_path(one_game_spider.date_path)
                date = one_game_spider.get_info(game_header)
            except AttributeError:
                continue

            info_dict = {'name': name, 'score': score, 'date': date}
            self.result_df = self.result_df.append([info_dict], ignore_index=True)
            self.restart_count += 1

        if length != 9999999:
            self.result_df.to_csv(self.save_path + "/pc_gamer_game_data.csv", index_label="ID", mode='a', header=0)

    def restart_system(self, re_type):
        if re_type == 'website':
            if len(self.game_website_df) != 0:
                print('Restarted! Continue getting game url list from last checkpoint')
            else:
                self.restart_count = 0
        elif re_type == 'game_info':
            if len(self.result_df) != 0:
                print('Restarted! Continue getting single game data from last checkpoint')
            else:
                self.restart_count = 0

    def write_website_csv(self):
        self.game_website_df.to_csv(self.save_path+"/pc_gamer_url_list.csv", index_label="ID")

    def write_csv(self):
        self.result_df.to_csv(self.save_path+"/pc_gamer_game_data.csv", index_label="ID")


class Spider_pc_gamer(Tree_spider):
    def __init__(self, url):
        super(Spider_pc_gamer, self).__init__(url)
        self.main_path = ['body', 13, 'article', 'div', 'header']
        self.score_path = ['div', 'div', 'span', 'string']
        self.name_path = [3, 'h1', 'string']
        self.date_path = [3, 'p', 'time', 'string']


def get_single_game_info_with_restart_system(start=0, length=9999999, save_path='spider_data'):
    if length == 9999999:
        print('Trying get the whole game data by single terminal. This may cost several hours')
    pc_gamer = pc_gamer_spider(save_path=save_path)

    while True:
        try:
            pc_gamer.get_game_info(start=start, length=length)
        except ProxyError:
            print('ProxyError detected.')
            continue
        else:
            break

    print('Done for one processy!')
    print('print first five rows of the spider result:')
    print(pc_gamer.result_df.head(5))
#    if input('Do you want to save game url list? [y/N]') == 'y':
#       pc_gamer.write_csv()
#      print('Saved')


def get_game_list_with_restart_system(save_path='spider_data'):
    pc_gamer = pc_gamer_spider(save_path=save_path)
    while True:
        try:
            pc_gamer.get_game_list()
        except ProxyError:
            print('ProxyError detected.')
            continue
        else:
            break

    pc_gamer.write_website_csv()
    print('Saved')


def main_pcgamer_spiders(start=0, length=9999999):
    get_game_list_with_restart_system()
    get_single_game_info_with_restart_system(start=start, length=length)


if __name__ == '__main__':
    main_pcgamer_spiders(start=0, length=9999999)
