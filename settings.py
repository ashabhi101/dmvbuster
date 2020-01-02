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

