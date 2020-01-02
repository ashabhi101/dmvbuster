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
* All actions within the script are being logged, which makes it extremely easy to debug in the case that something goes awry.


## Installation and Usage
1. Grab your local copy.
```
git clone https://github.com/jerrylin3321/dmvbuster.git
```
2. Install the dependencies, which includes python libraries.
```
pip install -r requirements.txt
```
3. Install ChromeDriver from [here](http://chromedriver.storage.googleapis.com/2.23/chromedriver_mac64.zip). Move the file to the same directory as `main.py` and unzip it. 

4. Obtain a [slack token](https://api.slack.com/docs/oauth-test-tokens). I would create a new Slack workspace, and inside, create a channel called `#dmv` for this. Then, create a config file - this should be kept hidden! In the current directory, enter the following:
```
echo "SLACK_TOKEN='your-token-here'" >> creds.py
```
Don't forget to replace the string above with your own slack token. 

5. When that is done, open `settings.py` and update it with your information.
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
6. Run the bot.
```
python main.py
```

## How does this work?
The bot uses Selenium, an automated testing Python library. It iterates through the list of DMV locations given, searching one location every 120 seconds and checking if there are any appointments at the specified location. If there are, it will log this in a database, and send it to a Slack channel. If the appointment is within `numDays`, the bot will schedule it for you, enter your phone number in to receive appointment reminders, and take a screenshot `appt_confirmation.png`. 

#### How does it solve Captchas?
It uses Buster, a Chrome extension, to bypass the reCaptcha. Buster uses speech-to-text algorithms to translate the audio reCaptcha into text. However, reCaptcha has algorithms in place that somehow detect the use of Buster. There are two errors that may occur:

1. It asks you to solve multiple audio captchas. It will say "Multiple solutions required."
2. It will tell you that it's detected automated queries from your computer. 
3. It will tell you that it is "unable to connect to reCaptcha." 

These are normal. For the first error, the bot will use Buster to solve another reCaptcha. Upon encountering the second or third error, the bot will simply exit the reCaptcha and reattempt a new reCaptcha. The bot will continue to do this until you've successfully reached the appointment finder page. This process may take upwards of 10+ tries, but eventually, reCaptcha will allow you to access the next page. 

Occasionally, there will be a Selenium error not covered by these three cases. In this case, the bot will simply quit this iteration and, after 120 seconds, restart and search the next location.

## Notes
* If you already have an appointment scheduled, this bot will override the appointment! If you've already booked an appointment, you should make sure to set `numDays` correctly so that you can find a closer appointment than your current one. 
* I tried running this in headless ChromeDriver, but headless ChromeDriver doesn't support extensions like Buster, which is critical for solving reCaptcha. 
* Debugging tips: use the logs. Also, Selenium has a handy screenshot function - use `driver.save_screenshot('debugging.png')`. 
