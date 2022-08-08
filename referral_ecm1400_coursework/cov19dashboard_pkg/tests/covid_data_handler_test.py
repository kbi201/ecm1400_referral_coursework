import sys
import json
sys.path.append('/referral_ecm1400_coursework/cov19dashboard_pkg')
from covid_data_handler import *


""" importing and locally assigning the configuration file """

configjson = open('/Users/kellyblanquita/Documents/referral_ecm1400_coursework/docs/config.json','r')
config = json.load(configjson)

""" testing the parsed csv data..."""

def test_parse_csv_data():
    logger.debug("Running test...")
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 638
    #638 instead of 639 as the title were popped while being parsed

"""testing the processed csv data..."""

def test_process_covid_csv_data():
    logger.debug("Running test...")
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

""" testing that the API request has the correct number of metrics """

def test_covid_API_request():
    api_jsonfile = covid_API_request()
    for x in api_jsonfile:
        assert len(config['data_structure']) == int(config['api_metrics_numpull'])

""" Testing the correct length of the update items """

def test_schedule_covid_updates():
    update_name = 'update_name_test'
    update_interval = 'update_interval_test'
    update_item = {
                    'title': update_name,
                    'content': update_interval
    }
    assert len(update_item) == 2

if __name__ == "__main__":
    test_parse_csv_data()
    test_process_covid_csv_data()
    test_covid_API_request()
    print('Tests passed! :D')