""" Imports """

import sched
import time
import json
import logging
import pandas as pd
from flask import Flask
from flask import request
from flask import render_template
from uk_covid19 import Cov19API
from covid_news_handling import news, remove_article, update_news


configjson = open('docs/config.json', 'r')
config = json.load(configjson)


""" Setting up logging """

LOG_FORMAT = '%(asctime)s :: %(name)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s'
logging.basicConfig(filename="system.log", level=logging.DEBUG, format=LOG_FORMAT,
                    datefmt='%d/%m/%Y %I:%M:%S %p', filemode="w")


logger = logging.getLogger(__name__)

""" call for scheduler assigning to var """


s = sched.scheduler(time.time, time.sleep)

""" Functions to conver time """


def minutes_to_seconds(minutes: str) -> int:
    return int(minutes)*60


def hours_to_minutes(hours: str) -> int:
    return int(hours)*60


def hhmm_to_seconds(hhmm: str) -> int:
    if len(hhmm.split(':')) != 2:
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])


def timeto_wait(input_time: int) -> int:
    local_time = time.localtime()
    hours, mins, seconds = (
        (local_time[3])*(60**2)), (local_time[4]*60), local_time[5]
    current_time = hours + mins + seconds
    logger.debug('- Calculate seconds until event')
    time_to = input_time - current_time
    logger.info('The inputed time is '+input_time+'.')
    return time_to


update = []

""" Function to schedule covid updates """


def schedule_covid_updates(update_name: str, update_interval: int) -> None:

    update_name = request.args.get('two')
    update_interval = request.args.get('update')
    covid_arg = request.args.get('covid-data')
    news_arg = request.args.get('news')
    repeat = request.args.get('repeat')
    update_item = {
                    'title': update_name,
                    'content': update_interval
    }
    secs_until = 1
    update.append(update_item)
    if covid_arg:
        s.enter(secs_until, 1, covid_update, argument=(
            config['location'], config['nation']))
        s.run(blocking=False)
        logger.debug('Covid data update queued...')
    if news_arg:
        s.enter(secs_until, 1, update_news, kwargs={
                'key_word': config['keywords']})
        s.run(blocking=False)
        logger.debug('News articles update queued...')
    if repeat and covid_arg:
        s.enter(secs_until, 1, covid_update, argument=(
            config['location'], config['nation']))
        s.enter(86400, 1, covid_update())
        s.run(blocking=False)
        logger.debug('Covid data update, with repeat queued...')
    if repeat and news_arg:
        s.enter(secs_until, 1, update_news, kwargs={
                'key_word': config['keywords']})
        s.enter(86400, 1, update_news())
        s.run(blocking=False)
        logger.debug('News articles update, with repeat, queued...')
    if repeat is None:
        s.enter(secs_until+1, 1, remove_sched_event, argument=(update_item,))
        logger.debug('Attempting to remove scheduled event...')

    return None

# ---------------------------------------------------------------------------------------------


def parse_csv_data(csv_filename: str) -> list:
    """ Function to parse csv data """
    logger.debug('Opening and reading .csv file...')
    try:
        csv_data = open(csv_filename)
    except FileNotFoundError as d:
        logger.error(d, 'File not found in current package.')
    else:
        data_list = []
        covid_csv_data = csv_data.readlines()
        # removing title row
        covid_csv_data.pop(0)
        logger.debug('Creating list of strings for rows in file...')
        for data_item in covid_csv_data:
            data_item = data_item.strip().lower()
            data_list.append(data_item)
        logger.info('List successfully created!')
    return data_list


""" Data processesing function """


def process_covid_csv_data(covid_csv_data: str) -> int:
    logger.debug("Beginning to process csv covid data...")
    csv_data_split = []
    # last7days_cases :: index value = [6]
    new_cases_by_specimen = []
    # current_hospital_cases :: index value = [5]
    hospital_cases = []
    # total_deaths :: index value = [4]
    total_deaths_list = []
    try:
        for data_row in covid_csv_data:
            data_row = data_row.split(',')
            if data_row[4] == '':
                data_row[4] = 0
            total_deaths_list.append(data_row[4])
            if data_row[5] == '':
                data_row[5] = 0
            hospital_cases.append(data_row[5])
            if data_row[6] == '':
                data_row[6] = 0
            new_cases_by_specimen.append(data_row[6])
            csv_data_split.append(data_row)
        logging.info(
            "Covid csv data successfully split, interated through, and organised into lists.")
    except IndexError:
        logging.error("Error with interating the file.")
    except Exception:
        logging.error("Error occured.")
    else:
        # last7day_cases
        new_cases_by_specimen = [int(float(i)) for i in new_cases_by_specimen]
        last7_days = new_cases_by_specimen[2:9]
        last7days_cases = sum(last7_days)
        logger.info("Last 7 day cases calculated.")
        # current_hospital_cases
        hospital_cases = [int(float(i)) for i in hospital_cases]
        current_hospital_cases = hospital_cases[0]
        logger.info("Current hospital cases calculated.")
        # total_deaths
        total_deaths_list = [int(float(i)) for i in total_deaths_list]
        index = 0
        try:
            for i in total_deaths_list:
                if total_deaths_list[index] == 0:
                    index += 1
            else:
                total_deaths = total_deaths_list[index]
                logger.info("Total deaths calculated.")
        except IndexError:
            logger.error('Error occured, showing output as 0.')
            total_deaths = 0
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str = 'Exeter', location_type: str = 'ltla') -> None:
    location_filters = [
        f"areaType={location_type}",
        f"areaName={location}"
    ]
    data_structure = config['data_structure']

    logger.debug("Processing the covid api request...")
    try:
        api = Cov19API(filters=location_filters, structure=data_structure)
        json_data = api.get_json(save_as=f"{location}.json", as_string=True)
        logger.info("Json file with COVID19 api data made.")
        return json_data
    except Exception:
        logger.critical("Failed to make json file :(")


""" Change the API json files received from covid_API_request to csv """


def jsonto_csv(location: str) -> json:
    json_filename = location + '.json'
    with open(json_filename, 'r') as f:
        location_dict = json.load(f)
        data_i_want = location_dict['data'][:]
    new_json_filename = 'new_' + location + '.json'
    with open(new_json_filename, 'w') as f:
        json.dump(data_i_want, f, indent=2)
    with open(new_json_filename, encoding='utf-8') as inputfile:
        df = pd.read_json(inputfile)
    df.to_csv(location+'.csv', encoding='utf-8', index=False)


def covid_update(location: str = 'Exeter', nation: str = 'England') -> int:
    covid_API_request(f'{location}', 'ltla')
    covid_API_request(f'{nation}', 'nation')
    jsonto_csv(f'{location}')
    jsonto_csv(f'{nation}')
    local7day_infections = process_covid_csv_data(
        parse_csv_data(config['location']+'.csv'))[0]
    national7day_infections = process_covid_csv_data(
        parse_csv_data(config['nation']+'.csv'))[0]
    national_hospitalcases = str(process_covid_csv_data(
        parse_csv_data(config['nation']+'.csv'))[1])
    national_deathstotal = str(process_covid_csv_data(
        parse_csv_data(config['nation']+'.csv'))[2])
    return local7day_infections, national7day_infections, national_hospitalcases, national_deathstotal


def remove_sched_event(update_item) -> None:
    try:
        update.remove(update_item)
        logger.debug('Article removed.')
    except IndexError:
        logger.warning('Index error occured while trying to remove article.')
    return None


""" Update news on opening dashboard"""

news.append(update_news())

""" Update data on opening dashboard """

covid_update()

"""
        ---------------------------FLASK APP---------------------------

Running on: http://127.0.0.1:5000/index

"""

app = Flask(__name__)


@app.route('/index')
def covid_dashboard():
    if request.args.get('two'):
        logger.debug('Dashboard updates...')
        update_name = request.args.get('two')
        update_interval = request.args.get('update')
        schedule_covid_updates(update_interval, update_name)
    s.run(blocking=False)
    remove_article()
    return render_template('index.html',
                           title='Daily update',
                           news_articles=news,
                           location=config['location'],
                           nation_location=config['nation'],
                           image='coronavirus.png',
                           favicon='coronavirus.png',
                           updates=update,
                           local_7day_infections=covid_update()[0],
                           national_7day_infections=covid_update()[1],
                           hospital_cases='Hospital cases: '
                           + covid_update()[2],
                           deaths_total='Deaths total: ' + covid_update()[3]
                           )


if __name__ == '__main__':
    app.run(debug=True)
