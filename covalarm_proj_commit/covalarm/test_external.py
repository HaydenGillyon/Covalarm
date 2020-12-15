"""This module tests the external services used by the Covalarm program.

It exports the following test functions:
test_covid19_service
test_news_service
test_weather_service
"""
from covalarm import get_covid19_data, get_news, get_weather

def test_covid19_service():
    data = get_covid19_data()
    assert data
    assert data['totalPages'] > 0

def test_news_service():
    data = get_news()
    assert data['totalResults'] > 0

def test_weather_service():
    data = get_weather()
    assert data['cod'] == 200

if __name__ == '__main__':
    test_covid19_service()
    test_news_service()
    test_weather_service()