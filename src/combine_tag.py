import pandas as pd


def combine_tag(save_path='spider_data'):
    '''
    join the tag table with reviews table by using appid as key
    :param save_path:
    :return: write the final data csv file, data.csv


    '''
    with open(save_path+"/tag_data.txt", 'r') as f:
        a = eval(f.read())

    tags = []
    for appid_tag in a:
        tags += appid_tag[1:]
    tags = set(tags)
    tag_for_id = {'appid': []}
    for tag_binary in tags:
        tag_for_id[tag_binary] = []

    for appid_tag in a:
        if appid_tag[1:]:
            tag_for_id['appid'].append(str(appid_tag[0]))
            for tag_binary in tags:
                if tag_binary in appid_tag[1:]:
                    tag_for_id[tag_binary].append(1)
                else:
                    tag_for_id[tag_binary].append(0)

    tag_df = pd.DataFrame(tag_for_id)
    reviews_df = pd.read_csv(save_path+"/reviews_data.csv", dtype={'appid': 'str'})
    all_data = pd.merge(tag_df, reviews_df, left_on='appid', right_on='appid')
    all_data = all_data[(all_data.total_positive + all_data.total_negative) >= 10]
    all_data.to_csv(save_path+"/data.csv", mode='w', index=False)

