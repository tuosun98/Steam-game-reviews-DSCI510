# 11.24.2020 Tuo sun: a lot of print function need to be update
##################
#from spiders.spider_ign_new import main_ign_spider
from src import spider_ign_new, spider_pcgame, spider_steam_game_tags, modeling
from src.steamAPI import get_appid, get_appid_fast
from requests.exceptions import ProxyError
from selenium.common.exceptions import WebDriverException
import multiprocessing
import subprocess
import argparse
import pandas as pd
from src import combine_tag, find_appid, data_combine, find_comment
import warnings


warnings.filterwarnings('ignore')


def arg_parses():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="\'remote\' for accessing data remotely\n \'local\' for accessing data locally",
                        type=str)
    parser.add_argument("--grade", action="store_true",
                        help="This flag is for quick start of the model",)
    args = parser.parse_args()
    return args


def main_threading(item, thread_name):
    # subprocess.run(["ffmpeg -i",filemane, "-c copy",new_file_name,".mp4"])
    #     # subprocess.run(["echo",thread_name + item])
    subprocess.Popen(["python", "-i", item, "-c", "copy", item + ".mp4"])


def spider_multiprocessing(number_of_process, function_name, save_path='spider_data'):
    """
    three part of spiders need to use spider_threading
    get single game data from game url list (pcgamer)
    find steam appid of games in pcgamer
    find steam appid of games in ign
    """
    number_of_process = int(number_of_process)
    default_length = 2100
    length = round(2100/number_of_process)+1
    starts = [length * i for i in range(number_of_process)]
    print(length, 'for each process')

    i = 0
    process = []
    while i < number_of_process:
        process.append(multiprocessing.Process(target=function_name, kwargs=({'start': starts[i], 'length': length, 'save_path': save_path})))
        i+=1
    return process


if __name__ == '__main__':

    args = arg_parses()
    if args.grade:
        # Regenerate part csv or json fills has the following steps:
        #     ign_part:
        #         get 3 ign game data from ign website (function main_ign_spider, generate ign_data.csv)
        #     pc_gamer_part:
        #         get 3 pc_gamer data from ign website (function main_ign_spider, generate ign_data.csv)
        #     steam_api_part(appid):
        #         get appid list (function get_appid in steamAPI.py, generate appid_list.csv
        #     combine_part:
        #         find similar appid of game names in ign_data.csv and pc_gamer_game_data.csv
        #         (This will cause a lot of time to processing)
        #     NLP process for combined part:
        #         choose the best appid for game names in IGN and PCgame
        #     steam_api_part(comments):
        #         find comment for games in all three data
        #     combine data:
        #         combine data to generate data.csv
        print('Grade mode activated')
        print('Grade mode detected, multiprocessing function offline')
        save_path = 'data/quick_start_file'

        ###########################################
        #     pc_gamer_part:
        #         read and process pcgamer_month.json (automatically, save a list in instance)
        #         process the list above (method pc_gamer_spider.get_game_list, generate pc_gamer_url_list.csv)
        #         process pc_gamer_url_list.csv (method pc_gamer_spider.get_game_info, generate pc_gamer_game_data.csv)
        #
        #             input: pcgamer_month.json.csv
        #             output: pc_gamer_url_list.csv, ign_data.csv pc_gamer_game_data.csv
        print('Start to get three info from PC gamer')
        pc_gamer = spider_pcgame.pc_gamer_spider(save_path=save_path, quick_start=True)
        pc_gamer.quick_start_url_list()
        while True:
            try:
                pc_gamer.quick_start_get_info()
            except AttributeError:
                print('Bad connection, restart to crawl the website')
            else:
                break

        ###########################################
        #     ign_part:
        #         get ign game data from ign website (function main_ign_spider, generate ign_data.csv)
        #
        #             input: None
        #             output: ign_data.csv
        print('Start to get three info from IGN')
        while True:
            try:
                ign = spider_ign_new.Spider_ign('https://www.ign.com/reviews/games/pc', static=False, time_step=0.2, scroll_time=300,
                                                save_path=save_path, quick_start=True)
                ign.get_result_df()
            except AttributeError or ProxyError:
                print('Bad connection, restart to crawl the website')

            else:
                break
        ign.write_csv()
        print('IGN Saved')

        ###########################################
        #     steam_api_part(appid_list):
        #         get appid list (function get_appid in steamAPI.py, generate appid_list.csv
        #
        #             input: None
        #             output: appid_list.csv
        print('Get appid from steam API. This need about one minute')
        get_appid_fast(save_path=save_path)

        ###########################################
        #     combine_part:
        #         find appid of game names in ign_data.csv and pc_gamer_game_data.csv
        #         (This will cause a lot of time to processing)
        #             input: ign_data.csv, pc_gamer_game_data.csv, appid_list.csv
        #             output: similar_relation.csv, similar_relation_cross.csv, similar_relation.csv
        print('Start to find similar names in steam games for each game in IGN and PC GAMER. This need about one minute')
        data_combine.get_similar_name_ign(save_path=save_path)
        data_combine.get_similar_name_pc(save_path=save_path)
        data_combine.get_similar_name_cross(save_path=save_path)

        ###########################################
        #     NLP process for combined part:
        #         choose the best appid for game names in IGN and PCgame
        #
        #             input: similar_relation.csv, similar_relation_cross.csv, similar_relation.csv
        #             output: pc_gamer_steam.csv, ign_cross_steam.csv, ign_steam.csv
        print('NLP process to select the best similar name for a game name in IGN and PC GAMER')
        find_appid.main(save_path=save_path)

        ###########################################
        #     steam_api_part(comments):
        #         find comment for games in all three data
        #
        #             input: pc_gamer_steam.csv, ign_cross_steam.csv, ign_steam.csv
        #             output: reviews_data.csv
        print('Get comment of all three games through steamAPI')
        find_comment.generate_comment(save_path=save_path)

        ###########################################
        #     steam_tag_spider:
        #         find tag for games in all three data
        #
        #             input: appid_used.csv
        #             output:  tag_data.txt
        print('Get tag of all three games through steam tag spider')
        spider_steam_game_tags.get_game_list_with_restart_system(save_path=save_path)

        ###########################################
        #     combine data:
        #         combine data to generate data.csv
        #
        #             input: tag_data.txt, reviews_data.csv
        #             output: data.csv
        print('Start to combine all the data to generate final dataset: data.csv')
        combine_tag.combine_tag(save_path=save_path)
        print('Finished')

    else:

        if args.source == 'remote':
            # remote arg will get all the data from internet and process data to generate the final datafile data.csv
            save_path = 'data/remote_sourse'


            # This part is for getting the data from internet. It just like regenerate csv or json files in spider_data.
            # All csv or json file create in this part will be saved in filefolder remote_sourse
            # Regenerate all csv or json fills has the following steps:
            #     ign_part:
            #         get ign game data from ign website (function main_ign_spider, generate ign_data.csv)
            #     pc_gamer_part:
            #         read and process pcgamer_month.json (automatically, save a list in instance)
            #         process the list above (method pc_gamer_spider.get_game_list, generate pc_gamer_url_list.csv)
            #         process pc_gamer_url_list.csv (method pc_gamer_spider.get_game_info, generate pc_gamer_game_data.csv)
            #     steam_api_part(appid):
            #         get appid list (function get_appid in steamAPI.py, generate appid_list.csv
            #     combine_part:
            #         find similar appid of game names in ign_data.csv and pc_gamer_game_data.csv
            #         (This will cause a lot of time to processing)
            #     NLP process for combined part:
            #         choose the best appid for game names in IGN and PCgame
            #     steam_api_part(comments):
            #         find comment for games in all three data
            #     combine data:
            #         combine data to generate data.csv

            print('Remote method will get the data from internet and save them at filefolder remote_sourse')
            print('When it finished, the file in the filefolder remote_sourse should be same as filefolder spider_data')
            print('Due to the large scale of data, This 3may cost many hours:')
            print('    Get data from IGN:                                  20 min')
            print('    Get data from Pc gamer:                             3 hours for single terminal (Single Python process)')
            print('    Get appid for each game from steam api:             1 min')
            print('    Use NLP to pair appid from steam with game data :   30 hours for single terminal (Single Python process)')
            print('    Generate data.csv:                                  10 min')
            print('For detail information, please look at spider description.pdf')
            print('\n')
            print('Your CPU have ',  multiprocessing.cpu_count(), ' threads in total')
            print('If you are sure to get the remotely, how many process do you want:')
            print('Input a integer like', multiprocessing.cpu_count()-2)
            number_of_process = input('(or input \'N\' to exit)')
            if number_of_process == 'N':
                exit()

            ###########################################
            #     ign_part:
            #         get ign game data from ign website (function main_ign_spider, generate ign_data.csv)
            #
            #             input: None
            #             output: ign_data.csv
            try:
                spider_ign_new.main_ign_spider(save_path=save_path)
            except WebDriverException:
                firefox_fail = input('Fail to open firefox, do you want to get ign game data locally?[y/N]')
                if firefox_fail == 'y' or  firefox_fail == 'Y':
                    ign_data = pd.read_csv('data/spider_data/ign_data.csv', index=False)
                    ign_data.to_csv(save_path + "/ign_data.csv")
                else:
                    print('Please check firefox')
                    exit()

            ###########################################
            #     pc_gamer_part:
            #         read and process pcgamer_month.json (automatically, save a list in instance)
            #         process the list above (method pc_gamer_spider.get_game_list, generate pc_gamer_url_list.csv)
            #         process pc_gamer_url_list.csv (method pc_gamer_spider.get_game_info, generate pc_gamer_game_data.csv)
            #
            #             input: pcgamer_month.json.csv
            #             output: pc_gamer_url_list.csv, ign_data.csv pc_gamer_game_data.csv
            spider_pcgame.get_game_list_with_restart_system(save_path=save_path)
            headers = pd.DataFrame(columns=['name', 'score', 'release_date_pc_gamer', 'date'])
            headers.to_csv(save_path + "/pc_gamer_game_data.csv", index_label="ID", mode='w')
            threads = spider_multiprocessing(number_of_process, spider_pcgame.get_single_game_info_with_restart_system, save_path=save_path)
            for p in threads:
                p.start()
            for p in threads:
                p.join()
            print('game score from ign and pc gamer is crawled!')
            print('start to get appid list from steam API')

            ###########################################
            #     steam_api_part(appid_list):
            #         get appid list (function get_appid in steamAPI.py, generate appid_list.csv
            #
            #             input: None
            #             output: appid_list.csv
            get_appid(save_path=save_path)
            print('appid_list crawled!')
            print('Start to find appid of games in ign and pcgamer.')
            print("\033[31;1mWarning:\033[0m")
            print('This may cost a large amount of time')
            print('In Intel i9-9900K 8-core 16threads with 4.7GHz overclock, this needs 3 hours to process for 12 threads')
            y_N_steamappid_matching = input('Are you sure to start matching with '+str(number_of_process)+' threading [y/N?]')
            if y_N_steamappid_matching == 'n' or y_N_steamappid_matching == 'N':
                exit()

            ###########################################
            #     combine_part:
            #         find appid of game names in ign_data.csv and pc_gamer_game_data.csv
            #         (This will cause a lot of time to processing)
            #             input: ign_data.csv, pc_gamer_game_data.csv, appid_list.csv
            #             output: similar_relation.csv, similar_relation_cross.csv, similar_relation.csv
            print('Start to found appids of similar names for games in IGN')
            threads = spider_multiprocessing(number_of_process, data_combine.get_similar_name_ign, save_path=save_path)
            for p in threads:
                p.start()
            for p in threads:
                p.join()
            print('appids of similar names in ign games are found.')
            print('Start to found appids of similar names for games in PCgamer')
            threads = spider_multiprocessing(number_of_process, data_combine.get_similar_name_pc, save_path=save_path)
            for p in threads:
                p.start()
            for p in threads:
                p.join()
            print('appids of similar names in Pc gamer games are found.')
            print('Start to found similar names in pc gamer for the games in ign')
            print('cross method for similar name searching is all done')
            data_combine.get_similar_name_cross(save_path=save_path)

            ###########################################
            #     NLP process for combined part:
            #         choose the best appid for game names in IGN and PCgame
            #
            #             input: similar_relation.csv, similar_relation_cross.csv, similar_relation.csv
            #             output: pc_gamer_steam.csv, ign_cross_steam.csv, ign_steam.csv
            print('Start to find most similar name for every game.')
            find_appid.main(save_path=save_path)

            ###########################################
            #     steam_api_part(comments):
            #         find comment for games in all three data
            #
            #             input: pc_gamer_steam.csv, ign_cross_steam.csv, ign_steam.csv
            #             output: reviews_data.csv
            print('Start to get comments from steam API')
            find_comment.generate_comment(save_path=save_path)

            ###########################################
            #     steam_tag_spider:
            #         find tag for games in all three data
            #
            #             input: appid_used.csv
            #             output:  tag_data.txt
            spider_steam_game_tags.get_game_list_with_restart_system(save_path=save_path)

            ###########################################
            #     combine data:
            #         combine data to generate data.csv
            #
            #             input: tag_data.txt, reviews_data.csv
            #             output: data.csv
            print('Start to combine all the data')
            combine_tag.combine_tag(save_path=save_path)
            X_train, X_test, y_train, y_test = modeling.data_clean(save_path=save_path)

            modeling.model_xgb(X_train, X_test, y_train, y_test)
        elif args.source == 'local':
            X_train, X_test, y_train, y_test = modeling.data_clean()
            print('Train set and Test set generate successfully.')
            print('Start to generate the model')
            modeling.model_xgb(X_train, X_test, y_train, y_test)
            print('The accuracy printed')