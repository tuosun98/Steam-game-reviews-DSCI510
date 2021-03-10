import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import warnings
import numpy as np

warnings.filterwarnings('ignore')


def data_clean(save_path='spider_data'):
    '''
    read the data.csv and do some pandas process.
    This function will delete game if the time difference of reviews of the game from ign and pc gamer is more than one year
    This will also create labels and split the data
    :param save_path:
    :return: return training and testing data for the model
    '''

    count_restrict = 40
    screen_by_release_data = True

    data = pd.read_csv(save_path+"/data.csv", dtype={'appid': 'str',
                                                      'review_score': 'int',
                                                      'total_positive': 'int',
                                                      'total_negative': 'int',
                                                      'ign_score': 'float64',
                                                      'ign_comments': 'int',
                                                      'pc_gamer_score': 'int'})
    binary_columns = data.columns[1:-12]
    data.loc[:, binary_columns] = data.loc[:, binary_columns].astype(int)
    false_columns = data.loc[:, binary_columns].sum()>count_restrict
    true_columns = false_columns[false_columns == True].index
    false_columns = false_columns[false_columns == False].index
    data = data.drop(labels=false_columns, axis=1)

    data.ign_release_data = pd.to_datetime(data.ign_release_data)
    data.pc_gamer_release_data = pd.to_datetime(data.pc_gamer_release_data)
    data['time_delta'] = (data.pc_gamer_release_data - data.ign_release_data)
    data['time_delta'] = data['time_delta'].apply(lambda x: x.days)
    data = data.drop(labels=['pc_gamer_release_data', 'ign_release_data'], axis=1)
    if screen_by_release_data:
        data = data[data['time_delta'] <= 365]

    data = data.drop(labels=['review_score_desc', 'total_positive', 'total_negative'], axis=1)
    data.review_score[data.review_score == 4] = 0
    data.review_score[data.review_score == 5] = 0
    data.review_score[data.review_score == 6] = 1
    data.review_score[data.review_score == 7] = 1
    data.review_score[data.review_score == 8] = 2
    data.review_score[data.review_score == 9] = 2


    X = data.drop(labels=['appid', 'name', 'review_score'], axis=1)
    y = data.review_score
    X, y = SMOTE().fit_sample(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        stratify=y,
                                                        test_size=0.3,
                                                        random_state=123)
    return X_train, X_test, y_train, y_test


def model_xgb(X_train, X_test, y_train, y_test):
    xgb = XGBClassifier(objective='multi:softmax')
    xgbfit = xgb.fit(X_train, y_train)
    y_predict = xgbfit.predict(X_test)
    k = 0
    for i in range(len(y_predict)):
        if y_predict[i] == y_test[i]:
            k += 1
    print('Accuracy: ', k/len(y_predict))


