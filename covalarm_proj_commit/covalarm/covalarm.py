"""This module is the main body of the Covalarm program.

It exports the following functions:
controller -- handles interactions with users
notif_check -- update data and notification list
check_alarms_daily -- schedule alarms for today
close_notif -- close a notification
cancel_alarm -- cancel an alarm
add_alarm -- add alarm to list and set if for today
is_today -- return true if alarm_time occurs today
set_alarm_today -- schedule an alarm
do_alarm -- activate and announce alarm
update_covid19_data -- update covid19 data
get_covid19_data -- return covid19 information
news_briefing -- update news list and announce it
update_news -- update news data in list
get_news -- return news information
weather_briefing -- update weather data and announce it
update_weather -- update weather data
get_weather -- return weather information
announce -- start tts and say the text
"""
import logging
from time_conversions import hhmm_to_seconds
from time_conversions import current_time_hhmm
from flask import Flask
from flask import request
from flask import render_template
import pyttsx3
import time
import sched
import json
import requests
from uk_covid19 import Cov19API

# Get the config file.
with open('config.json', 'r') as f:
    config = json.load(f)
Format = '%(levelname)s: %(asctime)s, %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    filename=config['system_log'],
    encoding='utf-8',
    format=Format
)
s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
notifications = []
alarms = []
weather = {}
covid19_data = {}
news = []

@app.route('/')
@app.route('/index')
def controller():
    """Handle interactions with users and then return index page."""
    s.run(blocking=False)
    alarm_time = request.args.get('alarm')
    
    if alarm_time:
        add_alarm(alarm_time)
    else:
        close_notif_name = request.args.get('notif')
        cancel_alarm_name = request.args.get('alarm_item')
        if close_notif_name:
            close_notif(close_notif_name)
        elif cancel_alarm_name:
            cancel_alarm(cancel_alarm_name)
    
    return render_template(
                'index.html',
                title='Covalarm Smart Alarm Clock',
                notifications=notifications,
                alarms=alarms,
                image='alarm-robot.png',
                favicon='/static/images/favicon.ico'
           )

def notif_check():
    """Update data and place it into the notifications list.
    
    Repeat regularly by scheduling self for the future. The interval
    between checks is set in the configuration file.
    """
    logging.info('NOTIFICATION CHECK: START')
    
    update_covid19_data()
    update_news()
    update_weather()
    
    notifications.clear()
    notifications.append(covid19_data)
    notifications.append(weather)
    notifications.extend(news)
    
    logging.info('NOTIFICATION CHECK: COMPLETE')
    
    interval = config['notif_check_interval']
    if interval < 30:
        interval = 30
    elif interval > 120:
        interval = 120
    s.enter(interval*60, 3, notif_check)

def check_alarms_daily():
    """Schedule alarms that are in the list for the current day.
    
    Schedule self for 00:00 the next day to check alarms then too.
    """
    today_alarms = [i for i in alarms if is_today(i['time'])]
    
    logging.info('-VVV- ALARM CHECK: ' + str(today_alarms))
    
    for alarm in today_alarms:
        event_object = set_alarm_today(alarm)
        alarm.update({'event_object' : event_object})
        logging.info('Next alarm: ' + str(alarm))
    
    logging.info('-^^^- ALARM CHECK OVER')
    
    prev = int(time.time() // 86400)
    next = prev + 1
    s.enterabs(next*86400, 1, check_alarms_daily)

def close_notif(notif_name):
    """Remove notification from list.
    
    Arguments:
    notif_name -- title of notification to close
    """
    global notifications
    notifications = [
        i for i in notifications if not (i['title'] == notif_name)
    ]
    logging.info('CLOSED NOTIFICATION: ' + notif_name)

def cancel_alarm(alarm_name):
    """Remove alarm from list and cancel in scheduler.
    
    Arguments:
    alarm_name -- title of alarm to cancel
    """
    for alarm in alarms:
        if alarm['title'] == alarm_name:
            s.cancel(alarm['event_object'])
            alarms.remove(alarm)
            break
    logging.info('CANCELLED ALARM: ' + alarm_name)

def add_alarm(alarm_time):
    """Fetch alarm details and add to list.
    
    Will also set alarm if it occurs today.
    Arguments:
    alarm_time -- time of alarm to add
    """
    alarm_label = request.args.get('two')
    include_news = request.args.get('news')
    include_weather = request.args.get('weather')
    
    alarm = {'title' : alarm_label, 'time' : alarm_time}
    
    alarm_text = ('The alarm "' + alarm_label + '" is set for '
                  + alarm_time[-5:-3] + ':' + alarm_time[-2:]
                  + ' on ' + alarm_time[:10] + '.')
    
    if include_news:
        alarm.update({'include_news' : True})
        alarm_text = alarm_text + ' Includes a news update.'
    else:
        alarm.update({'include_news' : False})
        
    if include_weather:
        alarm.update({'include_weather' : True})
        alarm_text = alarm_text + ' Includes a weather update.'
    else:
        alarm.update({'include_weather' : False})
    
    alarm.update({'content' : alarm_text})
    
    if is_today(alarm_time):
        event_object = set_alarm_today(alarm)
        alarm.update({'event_object' : event_object})
    
    alarms.append(alarm)
    logging.info('ADD ALARM TO LIST: ' + alarm_label)

def is_today(alarm_time):
    """Return true if the alarm time occurs today.
    
    Arguments:
    alarm_time -- time of alarm
    """
    date = time.strftime('%Y-%m-%d', time.gmtime())
    return date == alarm_time[:10]

def set_alarm_today(alarm):
    """Set the given alarm for the time specified inside it.
    
    Arguments:
    alarm -- alarm to set
    """
    alarm_time = alarm['time']
    
    alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
    alarm_label = alarm['title']
    
    # Log alarm set.
    logging.info('ALARM SET: ' + alarm_label + ' ' + alarm_hhmm)
    
    # Convert alarm_time to a delay.
    delay = hhmm_to_seconds(alarm_hhmm) - hhmm_to_seconds(current_time_hhmm())
    return s.enter(int(delay), 2, do_alarm, [alarm])

def do_alarm(alarm):
    """Activate and announce the alarm, along with selected details.
    
    Arguments:
    alarm -- alarm to activate
    """
    logging.info('DO ALARM: START')
    update_covid19_data()
    
    logging.info('BEGIN GENERAL BRIEFING')
    announce(
        'It is ' + time.strftime('%H:%M', time.gmtime()) + ','
        ' and this alarm is ' + alarm['title'] + '. '
        + covid19_data['content']
    )
    
    if alarm['include_weather'] == True:
        weather_briefing()
    if alarm['include_news'] == True:
        news_briefing()
    
    alarms.remove(alarm)
    logging.info('DO ALARM: FINISH')

def update_covid19_data():
    """Update the covid-19 data held in 'covid19_data'.
    
    Access Cov19API and get data before placing it into the global
    dictionary, 'covid19_data'.
    """
    logging.info('UPDATE DATA: Covid19')
    raw_data = get_covid19_data()
    if (not raw_data) or (raw_data['totalPages'] == 0):
        if not 'content' in covid19_data.keys():
            covid19_data.update({
                'title' : 'Covid-19 Data',
                'content' : 'The Covid-19 data could not be fetched.'
            })
        
        logging.debug('Function get_covid19_data returned'
                      ' no covid data. Returning...')
        return
    
    data = raw_data['data'][0]
    covid19_data.update(data)
    cases = data['newCasesByPublishDate']
    cumulative = data['cumCasesByPublishDate']
    message = (
        'Covid-19 data for ' + data['areaName'] + ' on ' + data['date'] + '.'
        ' New cases by publish date: ' + str(cases) + '.'
        ' Cumulative cases by publish date: '
        + str(cumulative) + '.'
    )
    
    boundaries = config['case_boundaries']
    lower = boundaries['lower']
    higher = boundaries['higher']
    if cases < lower:
        message = (message + ' Cases are lower than ' + str(lower)
                   + ', so the risk level is low.')
    elif cases >= higher:
        message = (message + 'Cases are higher than ' + str(higher)
                   + ', so the risk level is high.')
    else:
        message = (message + ' Cases are between ' + str(lower)
                   + ' and ' + str(higher)
                   + ', so the risk level is medium.')
    
    covid19_data.update({'title' : 'Covid-19 Data', 'content' : message})
    logging.info('UPDATE DATA: Covid19 - Complete!')

def get_covid19_data():
    """Return the covid-19 information for the region in config."""
    logging.debug('Get Covid-19 data...')
    filter = [
    'areaType=' + config['location']['covid19_regtype'],
    'areaName=' + config['location']['covid19_loc'],
    ]
    structure = {
        'date' : 'date',
        'areaName' : 'areaName',
        'newCasesByPublishDate' : 'newCasesByPublishDate',
        'cumCasesByPublishDate' : 'cumCasesByPublishDate'
    }
    api = Cov19API(
            filters=filter,
            structure=structure,
            latest_by='newCasesByPublishDate'
          )
    try: 
        raw_data = api.get_json()
    except uk_covid19.exceptions.FailedRequestError:
        logging.error('Request to get covid-19 data failed.')
        return
    
    return raw_data

def news_briefing():
    """Announce news items after updating the news list."""
    logging.info('BEGIN NEWS BRIEFING')
    update_news()
    announcement = (
    'Here is your news update for '
    + config['location']['news_country'] + '.'
    )
    
    news_limit = config['news_limit']
    count = 1
    for i in news:
        if not ('.' in i['content'][-1]
                or '!' in i['content'][-1]
                or '?' in i['content'][-1]):
            continue
        
        announcement = announcement + ' ' + i['content']
        
        count += 1
        if count > news_limit:
            break
    
    announce(announcement)

def update_news():
    """Update the news data held in 'news'.
    
    Access News API and get articles before placing them into the
    global list, 'news'.
    """
    logging.info('UPDATE DATA: News')
    news_dict = get_news()
    
    if news_dict['totalResults'] == 0:
        if not news:
            article = {
                'title' : 'No news could be obtained.',
                'content' : ('The news service may be down'
                             ' or another error has occured.')
            }
            news.append(article)
        
        logging.debug('Function get_news returned'
                      ' no articles. Returning...')
        return
    
    articles = news_dict['articles']
    news_list = []
    for article in articles:
        description = str(article['description']).lower()
        title = str(article['title']).lower()
        trusted_source = config['trusted_source']
        used = False
        
        if not article['source']['name'] or not article['description']:
            continue
        
        if article['source']['name'] == trusted_source:
            used = True
            
            content = trusted_source + ': ' + article['description']
            
            article_trim = {
                'title' : article['title'],
                'content' : content,
                'description' : article['description'],
                'source' : trusted_source
            }
            news_list.append(article_trim)

        covid_words = [
            'lockdown', 'covid', 'quarantine', 'symptoms',
            'pandemic', 'coronavirus', 'virus', 'covid-19',
            'vaccine', 'antibody', 'treatment', 'health'
        ]
        if not used:
            for word in covid_words:
                if word in description or word in title:
                    content = (
                        article['source']['name'] + ': '
                        + article['description']
                    )
                    
                    article_trim = {
                        'title' : article['title'],
                        'content' : content,
                        'description' : article['description'],
                        'source' : article['source']['name']
                    }
                    news_list.append(article_trim)
                    break
    
    news.clear()
    news.extend(news_list)
    logging.info('UPDATE DATA: News - Complete!')

def get_news():
    """Return the news information for the country in config."""
    logging.debug('Get news data...')
    news_key = config['API_keys']['news']
    base_URL = config['base_URLs']['news']
    country = config['location']['news_country']
    complete_URL = base_URL + 'country=' + country + '&apiKey=' + news_key
    response = requests.get(complete_URL)
    return response.json()

def weather_briefing():
    """Announce info on the weather after updating the weather data."""
    logging.info('BEGIN WEATHER BRIEFING')
    update_weather()
    announcement = (
        'Here is your weather update for ' + str(weather['location']) + '. '
        + weather['content']
    )
    announce(announcement)

def update_weather():
    """Update the weather data held in 'weather'.
    
    Access OpenWeatherMap API and get data before placing it into the
    global dictionary, 'weather'.
    """
    logging.info('UPDATE DATA: Weather')
    x = get_weather()
    
    if x['cod'] != 200:
        if not weather['content']:
            weather.update({
                'title' : 'No weather data could be obtained.',
                'content' : 'The weather service may be down.'
            })
        
        logging.debug("Function get_weather didn't return code 200.")
        return
    
    # Get temperatures and convert from kelvin to degrees Celsius.
    y = x['main']
    current_temp = round(y['temp'] - 273.15, 1)
    current_feelslike_temp = round(y['feels_like'] - 273.15, 1)
    
    z = x['weather']
    weather_description = z[0]['description']
    
    location = x['name']
    
    weather.update({
        'title' : 'Weather Info at ' + time.strftime('%H:%M', time.gmtime()),
        'temp' : current_temp,
        'feels_like' : current_feelslike_temp,
        'weather_desc' : weather_description,
        'location' : location
    })
    content = (
        'The current weather in ' + weather['location'] + ' is '
        + weather['weather_desc'] + '.'
        ' The temperature is ' + str(weather['temp']) + '°C,'
        ' but feels like ' + str(weather['feels_like']) + '°C.'
    )
    weather.update({'content' : content})
    logging.info('UPDATE DATA: Weather - Complete!')

def get_weather():
    """Return the weather information for the city in config."""
    logging.debug('Get weather data...')
    # Get the latest weather data.
    base_URL = config['base_URLs']['weather']
    weather_key = config['API_keys']['weather']
    location = config['location']['weather_city']
    complete_URL = base_URL + 'appid=' + weather_key + '&q=' + location
    response = requests.get(complete_URL)
    return response.json()

def announce(announcement):
    """Initialise tts engine and then say the text provided.
    
    Arguments:
    announcement -- the text to announce
    """
    logging.debug('ANNOUNCEMENT: START')
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()
    logging.debug('ANNOUNCEMENT: FINISH')

if __name__ == '__main__':
    logging.info('INITIALISE: Beginning initialisation...')
    notif_check()
    check_alarms_daily()
    logging.info('INITIALISE: Initialisation complete. Starting Flask...')
    app.run()