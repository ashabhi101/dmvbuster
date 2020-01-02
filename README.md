# DMV Buster

This is a fork of [Stalk-the-DMV](https://github.com/thisisandreeeee/stalk-the-DMV). 
![demo](https://raw.githubusercontent.com/thisisandreeeee/stalk-the-DMV/master/demo.gif)

I'm a college student trying to grab an appointment for a behind-the-wheel test. Unfortunately, appointments are literally booked out three months in advance. There are occasional openings when someone cancels, but these are hard to find and usually snatched up instantly. I went looking for bots online to automate this appointment search for me, but none of them work ever since the DMV deployed a ReCaptcha on the appointment finder page. 

To solve this, I integrated the automated captcha-solving extension [Buster](https://github.com/dessant/buster) with [Stalk-the-DMV](https://github.com/thisisandreeeee/stalk-the-DMV), and added an automatic appointment scheduling feature. This bot will search through a list of DMV offices, logging down available appointments, and if an appointment is within a specified number of days, it'll automatically schedule it for you.

Features:
* Bypasses reCaptcha
* If the appointment is within `numDays` (you can adjust this in `settings.py`), the bot will schedule the appointment for you.
* Saves an appointment confirmation screenshot as `appt_confirmation.png` and registers your phone number for appointment notifications from the DMV.
* Found appointments will be stored in an SQLite databse if it's not already stored in the database and sent to your Slack channel. 
* Moreover, the bot will recognize if the earliest appointment for a specific DMV office is within 14 days, and tag the users within the slack channel to bring the information immediately to attention. 


## Installation and Usage
Grab your local copy.
```
git clone https://github.com/jerrylin3321/dmvbuster.git
```
Install the dependencies, which includes python libraries.
```
pip install -r requirements.txt
```
Install ChromeDriver from [here](http://chromedriver.storage.googleapis.com/2.23/chromedriver_mac64.zip). Move the file to the same directory as `main.py` and unzip it. 

Obtain a [slack token](https://api.slack.com/docs/oauth-test-tokens). I would create a new Slack workspace, and inside, create a channel called `#dmv` for this. Then, create a config file - this should be kept hidden! In the current directory, enter the following:
```
echo "SLACK_TOKEN='your-token-here'" >> creds.py
```
Don't forget to replace the string above with your own slack token. When that is done, open `settings.py` and update it with your information.
```python
SLACK_CHANNEL = '#dmv' # this should be the slack channel which you want to send messages to
URL = 'https://www.dmv.ca.gov/wasapp/foa/driveTest.do' # the url for the DMV web form

LOCATIONS = ['WATSONVILLE', 'GILROY', 'CAPITOLA', 'HOLLISTER', 'SALINAS', 'SEASIDE', "LOS BANOS", 'MODESTO']
#Names must exactly match office names in the drop-down menu

PROFILE = {
    'firstName': 'IAN',
    'lastName': 'MCEWAN',
    'birthMonth': '06',
    'birthDay': '21',
    'birthYear': '1948',
    'dl_number': 'Y1234567',
    'areaCode': '999',
    'telPrefix': '123',
    'telSuffix': '4567',
    'numDays': '14' #If the bot finds an appointment within numDays days, it will schedule the appointment; otherwise, it'll just record it and send to Slack
    # format: (area-code) telPrefix-telSuffix
}

```
Run the bot.
```
python main.py
```

## So what exactly does it do?
The bot will run once every 15 minutes, provided that the current time is during the day. It checks whether there are any available appointments at the predefined locations, and posts the earliest appointment in the slack channel.

## Cool features
- If the next appointment is coming up real soon, we want to know ASAP. The bot will recognize if the earliest appointment for a specific DMV office is within 14 days, and tag the users within the slack channel to bring the information immediately to attention. All other appointments will still be posted in the slack channel, but users will not be tagged.
- Everytime a new appointment is found at an office, the data will be stored in an SQLite database if it does not already exist within the database. Then, whenever a bot wishes to send a notification on a new appointment to the channel, it checks the database to ensure that it has not already notified users of an existing appointment.
- All actions within the script are being logged, which makes it extremely easy to debug in the case that something goes awry.
- Selenium enables us to mimic the actual action of a human. To view this with a GUI, go to `scraper.py` and swap out the following two lines.
```python
browser = webdriver.PhantomJS('phantomjs') # phantomjs is a headless browser which lets us run the script in a CLI environment
browser = webdriver.Chrome('./chromedriver') # replace the above line with this, which instantiates with a chrome driver instead
```
If you do not have the chromedriver file installed, enter the following into your terminal (OSX only, with wget installed) while in the same directory as `main.py`.
```
wget http://chromedriver.storage.googleapis.com/2.23/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
rm chromedriver_mac64.zip
```

## Notes
* If you already have an appointment scheduled, this bot will override the appointment! If you've already booked an appointment, you should make sure to set `numDays` correctly so that you can find a closer appointment than your current one. 
