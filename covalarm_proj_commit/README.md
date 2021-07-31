# Covalarm: The Smart, Covid-Aware Alarm Clock
## Introduction
This program runs both the server and the client webpage on the same machine, and so it has an easy-to-use menu, as well as lots of customisability to the user's needs.
Covalarm allows you to set alarms just like any other alarm clock, but it can also present you with helpful information that may allow you to plan your day better, or even your week!
The data that Covalarm can access and present to you is in 3 forms:
1. Covid-19 Statistics
2. Covid-19 Related/Headline News
3. The Weather

The Covid-19 data and the weather can also be localised to your region, as will be explained in the Configuration section.

This package is maintained in the following github repository: https://github.com/HaydenGillyon/Covalarm

## Prerequisites
This program was built and works on Python 3.9.0.
The packages you will need to have installed for Covalarm to function are as follows:
* [Flask 1.1.2](https://pypi.org/project/Flask/)
* [pyttsx3 2.90](https://pypi.org/project/pyttsx3/)
* [requests 2.25.0](https://pypi.org/project/requests/)
* [uk-covid19 1.2.0](https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/)

## Configuration
For the program to work you will need to sign up for API keys from the following:
* [News API](https://newsapi.org/)
* [OpenWeatherMap API](https://openweathermap.org/)

Then place these into the config.json file under API_keys. (Weather goes in 'weather', and news goes in 'news'.)

The rest of the details can be left at default and the program will work. However, the following are more things that you can change:
1. If the version or URLs for the APIs change, you can change the links in 'base_URLs'. The option for the OpenWeatherMap API is 'weather', leaving 'news' for the News API.
2. Location:
    1. Pick a city you would like weather for and place it next to 'weather_city'. (Default Exeter.)
    2. Put the country you want news for in 'news_country', in shortened form. (Default gb.)
    3. Put the region type and location you would like Covid-19 data for in 'covid19_regtype' and 'covid19_loc' respectively. (Default 'region' for NHS Region, and 'South West'.)
3. In 'case_boundaries', put the boundaries for case numbers that below which you would consider to be low risk and above which you would consider to be high risk in 'lower' and 'higher' respectively.
4. You can change the source for which you would like to get more news from (even non-Covid articles) in 'trusted_source'.
5. You can change the amount of news articles that will be added to alarm updates and notifications in 'news_limit'.
6. You can change how often in minutes Covalarm will check for new data in 'notif_check_interval'. The minimum is 30 minutes and the maximum is 120 minutes.
7. Finally, you can alter the name of the file the program will log system and error events to. (Default is 'sys.log'.)

## Author
Copyright &copy; 2020 Hayden J R Gillyon
