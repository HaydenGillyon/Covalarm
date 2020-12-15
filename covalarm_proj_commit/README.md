# Covalarm: The Smart, Covid-Aware Alarm Clock
## Introduction
This program runs both the server and the client webpage on the same machine, and so it has an easy-to-use menu, as well as lots of customisability to the user's needs.
Covalarm allows you to set alarms just like any other alarm clock, but it can also present you with helpful information that may allow you to plan your day better, or even your week!
The data that Covalarm can access and present to you is in 3 forms:
1. Covid-19 Statistics
2. Covid-19 Related/Headline News
3. The Weather

The Covid-19 data and the weather can also be localised to your region, as will be explained in the Configuration section.

## Prerequisites
This program was built and works on Python 3.9.0.
The packages you will need to have installed for Covalarm to function are as follows:
* [Flask 1.1.2](https://pypi.org/project/Flask/)
* [pyttsx3 2.90](https://pypi.org/project/pyttsx3/)
* [requests 2.25.0](https://pypi.org/project/requests/)
* [uk-covid19 1.2.0](https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/)

