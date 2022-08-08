from covid_news_handling import news_API_request

def test_news_API_request():
    covid_news = news_API_request()
    assert covid_news