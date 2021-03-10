# Steam-game-reviews-DSCI510
Write Python crawlers to get thousands of  game scores from sites and use steam RESTful APIs to get user ratings. Use tools of natural language processing to match similar game names to avoid impact of game nickname. Build Machine Learning model to predict user rating of the game, and The accuracy achieved 0.86

# Major “gotchas”:

### The following gotchas are all about getting the data remotely

### ProxyError:
There may be `ProxyError` during crawling IGN and PCgamer, and getting json from steamAPI.
The program include a restart system. During `ProxyError`, it is able to restart the spiders to retry from cheakpoint instead of run the code again. However, it cannot handle exception like `ConnectionError`, which means the computer is completely disconnected with Internet.

**Please ensure the computer network in good connection.**

### Multi core operation：

To find similar name in steam appid api is not that easy. It need to compare every name in `appid_list.csv` which have 100,000 lines of data. For 2000 games in IGN and 2000 games in PC gamer. It needs 20,000,000 calculation. It cost about 20 hours in a single core in Intel i9-9900k with 4.7GHz overclock. In order to reduce running time. 
I import multiprocessing pack. You can input the number of threads you want to use when you try the python program.

**Please input a appropriate number of threads you want to enable for this project.**

<font color="#dd0000">**Warning:**</font><font color="#dd0000"> For a single thread, this program may need more than 20 hours to process</font><br />

# Packages：

A `environment.yml` file is created at directory

to install `imblrean`, open a terminal at python envs and input `conda install -c glemaitre imbalanced-learn` at python envs

to install `xgboost`, open a terminal at python envs and input `anaconda search -t conda xgboost` to search xgboost and input `conda install -c  anaconda py-xgboost` to install

`nltk` if first import nltk, please input `nltk.download()` at python console

`selenium` use firefox web browser to get IGN which is a dynamic web page. You should download geckodiver for your operating systems such as MacOS or Win10.
The following have a basic tutor for selenium.
https://stackoverflow.com/questions/42204897/how-to-set-up-a-selenium-python-environment-for-firefox 

If fail to run the following cells, please run `conda install ipykernel` at the terminal
and input `python -m ipykernel install --user --name final_project_510 --display-name "env510"`

(final_pro_510 should be the name of the virtual environment and press Kernel above the page and change the kernel.)

## 4. The following is a picture show the structure of the files in this project：
orange blocks are scripts

blue blocks are data files
![title](src/Project_description.png)

