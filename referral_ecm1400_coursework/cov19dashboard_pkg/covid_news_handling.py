
""" Imports """

import requests
import json
import logging
from flask import request

""" Importing and locally assigning the configuration file """

configjson = open('docs/config.json', 'r')
config = json.load(configjson)

""" Setting up logging """

log_FORMAT = '%(asctime)s :: %(name)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s'
logging.basicConfig(filename="system.log", level=logging.DEBUG, format=log_FORMAT,
                    datefmt='%d/%m/%Y %I:%M:%S %p', filemode="w")

""" Application code for logger """

logger = logging.getLogger(__name__)

news = []
removed_news = []
articles_fromapi = []

""" Retrieving API articles """


def news_API_request(covid_terms='Covid COVID-19 coronavirus'):
    base_url = 'https://newsapi.org/v2/everything?'
    complete_url = base_url + 'q=' + \
        covid_terms + '&apiKey=' + config['API_KEY']
    covid_news = requests.get(complete_url).json()
    return covid_news


""" Removing articles"""


def remove_article() -> None:
    if request.args.get('notif'):
        for article in news:
            index = news.index(article)
            if article is not None:
                if article['title'] == request.args.get('notif'):
                    logger.debug('Beginning to remove news article...')
                    try:
                        removed_news.append(article["title"])
                        news.pop(index)
                        logger.info(
                            'Article ' + request.args.get('notif') + ' removed.')
                    except IndexError:
                        logger.error('IndexError occured.')
    return news, removed_news


""" Update news function """


def update_news(key_word: str = 'Covid COVID-19 coronavirus') -> None:
    logger.debug('Beginning to update news...')
    news_api = news_API_request(f'{key_word}')
    articlesfrom_api = news_api['articles']
    for article in articlesfrom_api:
        news.append({
            'title': article['title'],
            'content': article['content']
            })
        articles_fromapi.append(article)
        logger.info('News article appended.')
    if len(news) > 10:
        del news[10:]
    if len(news) < 10:
        news.append({
            'title': article['title'],
            'content': article['content']
            })


api_articles = news_API_request(covid_terms='Covid COVID-19 coronavirus')
articles = api_articles['articles']
index = 0
