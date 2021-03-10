# Tuo sun 11.20.2020


############################################
import pandas as pd
from src.util import Tree_spider
import datetime


class Spider_ign(Tree_spider):
    """
    Parent class is Tree_spider. All the data from this website can be get through one url.
    Load dynamic website through Tree_spider. Get score from every game and the number of comment
    and release data from every game review. Save them into csv file.
    """
    def __init__(self, url, static=True, time_step=0.2, scroll_time=300, save_path='spider_data', quick_start=False):
        """
        Spider path:                  html
                                       |
                                      body
                                       |
                                      div
                                       |
                                      div
                                       |
                                      main
                                       |
                                    contents[2]
         ______________________________|_____________________________________________
         |               |                          |               |               |
        (game set 0)    (game set 1)     ...       (game set -3)   (game set -2)   (game set -1)
         |
         contents[0]
         |___________________________________________________________________________________________________________
         |                                                              |
         div (should have 'data-id' as a key)                           div (should have 'data-id' as a key)       ...
         game1                                                          game2
         |_____________________________________________________
         |                                                    |
         contents[0]                                          contents[1]
         |                                                    |
         div                                                  contents[0]
         |                                    ________________|______________________________________________
         div                                  |                               |                             |
         |                                    h3                              div (the number of comments)  contents[1]
         contents[0]                          |                               |                             |
         |                                    div                             contents[0]                   div
         figure                               |                               |                             |
         |                                    span                            string(review release time)   contents[2]
         div                                  |                                                             |
         |                                    string (the name of game1)              string(the number of comments)
         span
         |
         span
         |
         string (the score of game1)
        """
        if quick_start:
            self.quick_start = True
            self.target = ['Yakuza: Like a Dragon Review', 'Crusader Kings 3 Review', 'Dirt 5 Review']
            super(Spider_ign, self).__init__(url, static=static, time_step=0.2, scroll_time=20)
        else:
            self.quick_start = False
            super(Spider_ign, self).__init__(url, static=static, time_step=time_step, scroll_time=scroll_time)
        self.result_df = pd.DataFrame(columns=['name', 'ign_score', 'release_date_ign', 'comments'])
        self.main_path = ['body', 'div', 'div', 'main', 2]
        self.set_path = ['section', 1]
        self.game_list = []
        self.save_path = save_path


    def get_games(self):
        """
        There are many game sets in the website. Each one contains several of games.
        """
        self.set_spider_path(self.main_path)
        game_sets = [child for child in self.get_info(self.content).children if child.name == 'div']
        for one_set in game_sets:
            self.set_spider_path(self.set_path)
            games = [child for child in self.get_info(one_set).children if list(child.attrs.keys())[0] == 'data-id']
            for one_game in games:
                self.game_list.append(one_game)


    def game_div_info(self, div_tag):
        """
        Get the information from the path.
        """
        score_path = [0, 0, 'div', 'div', 0, 'figure', 'div', 'span', 'span', 'string']
        name_path = [0, 1, 0, 'h3', 'div', 'span', 'string']
        time_comment_path = [0, 1, 0, 'div']

        self.set_spider_path(score_path)
        score = self.get_info(div_tag)

        self.set_spider_path(name_path)
        name = self.get_info(div_tag)

        self.set_spider_path(time_comment_path)
        time_comment = list(self.get_info(div_tag).children)
        set_time = time_comment[0].string
        comments = time_comment[1].div.contents[2].string if len(time_comment) == 2 else 0
        if set_time[-1] == 'd':
            today = datetime.date.today()
            days = int(set_time[:-1])
            set_time = str((today - datetime.timedelta(days=days)).strftime('%b %d, %Y'))
        if set_time[-1].isalpha():
            today = datetime.date.today()
            set_time = str(today.strftime('%b %d, %Y'))

        return {'name': name, 'ign_score': score, 'release_date_ign': set_time, 'comments': comments}

    def get_result_df(self):
        """
        Record the data into a Dataframe
        """
        self.get_games()
        for one_game in self.game_list:
            if self.quick_start:
                add_dict = self.game_div_info(one_game)
                if add_dict['name'] in self.target:
                    self.result_df = self.result_df.append([add_dict], ignore_index=True)
            else:
                self.result_df = self.result_df.append([self.game_div_info(one_game)], ignore_index=True)

    def write_csv(self):
        """
        convert pandas.Dataframe to csv file
        """
        self.result_df.to_csv(self.save_path + "/ign_data.csv", index_label="ID")


def main_ign_spider(save_path='spider_data'):
    ign = Spider_ign('https://www.ign.com/reviews/games/pc', static=False, time_step=0.2, scroll_time=300, save_path=save_path)
    ign.get_result_df()
    print('print first five rows of the spider result:')
    print(ign.result_df.head(5))
    ign.write_csv()
    print('Saved')


if __name__ == '__main__':
    main_ign_spider()