from selenium import webdriver
from selenium.webdriver.support.ui import Select
from settings import PROFILE, URL
from logger import Logger
import time
from datetime import datetime

class Scraper:
    def __init__(self):
        self.logger = Logger()
        self.logger.log("New instance of scraper created")

        #--- ChromeDriver options
        options = webdriver.ChromeOptions()
        options.add_argument('--load-extension=buster')
        browser = webdriver.Chrome('./chromedriver', chrome_options=options)
        #-------

        browser.get(URL)
        self.browser = browser
        self.logger.log("Navigated to url")
        time.sleep(5)

    def i_want_an_appointment_at(self, location):
        self.logger.log("Start appointment searching process")
        browser = self.form_fill_and_submit(self.browser, location)
        browser.switch_to_default_content()
        appt = self.get_appointment(browser)
        if appt == None:
            return None
        if appt.find('Sorry') != -1: #i.e. if "sorry" appears in the string
            return None
        return appt

    def form_fill_and_submit(self, browser, location):
        dropdown = browser.find_element_by_id("officeId")
        Select(dropdown).select_by_visible_text(location)
        browser.find_element_by_xpath('//*[@id="DT"]').click()
        browser.find_element_by_xpath('//*[@id="firstName"]').send_keys(PROFILE['firstName'])
        browser.find_element_by_xpath('//*[@id="lastName"]').send_keys(PROFILE['lastName'])
        browser.find_element_by_xpath('//*[@id="birthMonth"]').send_keys(PROFILE['birthMonth'])
        browser.find_element_by_xpath('//*[@id="birthDay"]').send_keys(PROFILE['birthDay'])
        browser.find_element_by_xpath('//*[@id="birthYear"]').send_keys(PROFILE['birthYear'])
        browser.find_element_by_xpath('//*[@id="dl_number"]').send_keys(PROFILE['dl_number'])
        browser.find_element_by_xpath('//*[@id="areaCode"]').send_keys(PROFILE['areaCode'])
        browser.find_element_by_xpath('//*[@id="telPrefix"]').send_keys(PROFILE['telPrefix'])
        browser.find_element_by_xpath('//*[@id="telSuffix"]').send_keys(PROFILE['telSuffix'])
        browser.find_element_by_xpath('//*[@id="findOffice"]/fieldset/div[5]/input[2]').click()
        self.logger.log("Form filled and submitted for office %s" % location)
        return browser

    def get_appointment(self, browser):
        time.sleep(3)
        try:
            self.bust_captcha(browser)
        except Exception as e:
            print (e)
            self.logger.log("Couldn't solve this captcha, will skip this iteration. Selenium occasionally bugs out.")

        try:
            element = browser.find_element_by_xpath('//*[@id="formId_1"]/div/div[2]/table/tbody/tr/td[2]/p[2]/strong').get_attribute('innerHTML')
            self.logger.log("Valid appointment xpath found")
            date = self.parse_date(element)
            tdelta = (date - datetime.now()).days
            if (tdelta <= int(PROFILE['numDays'])): #If appt is less than 'numDays' in the future, schedule it
                browser.find_element_by_xpath('//*[@id="app_content"]/div/a[1]').click()
                time.sleep(5)
                if len(browser.find_elements_by_xpath('//*[@id="app_content"]/div[1]/table/thead/tr/th[1]')) > 0:
                    browser.find_element_by_xpath('//*[@id="ApptForm"]/button').click()
                    time.sleep(5)
                browser.find_element_by_css_selector('#sms_method').click()
                browser.find_element_by_xpath('//*[@id="notify_smsTelArea"]').send_keys(PROFILE['areaCode'])
                browser.find_element_by_xpath('//*[@id="notify_smsTelPrefix"]').send_keys(PROFILE['telPrefix'])
                browser.find_element_by_xpath('//*[@id="notify_smsTelSuffix"]').send_keys(PROFILE['telSuffix'])
                browser.find_element_by_xpath('//*[@id="notify_smsTelArea_confirm"]').send_keys(PROFILE['areaCode'])
                browser.find_element_by_xpath('//*[@id="notify_smsTelPrefix_confirm"]').send_keys(PROFILE['telPrefix'])
                browser.find_element_by_xpath('//*[@id="notify_smsTelSuffix_confirm"]').send_keys(PROFILE['telSuffix'])
                browser.find_element_by_xpath('//*[@id="ApptForm"]/fieldset/div[11]/button').click()
                time.sleep(5)
                browser.find_element_by_xpath('//*[@id="ApptForm"]/fieldset/div[9]/button').click()
                time.sleep(5)
                browser.save_screenshot('appt_confirmation.png')
                self.logger.log("Appointment for " + date + " at office " + location + " scheduled")
            else:
                browser.close()
            return element
        except Exception as e:
            self.logger.log("No valid appointment xpath found")
            pass
        try:
            element = browser.find_element_by_xpath('//*[@id="formId_1"]/div/div[2]/table/tbody/tr/td[2]/p').get_attribute('innerHTML')
            self.logger.log("No available appointments")
            browser.close()
            return element
        except:
            self.logger.log("Invalid xpath - no element found.")
            pass
        return None

    def bust_captcha(self, browser): #Bypasses captcha
        on_audio_page = False
        while browser.current_url != "https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do":
            frame = browser.find_element_by_css_selector('body > div:nth-child(8) > div:nth-child(2) > iframe')
            browser.switch_to.frame(frame)
            if len(browser.find_elements_by_xpath('/html/body/div/div/div[1]/div[2]/div')) > 0: #If "you're sending automated queries" error appears
                self.automated_queries(browser)
                on_audio_page = False
                time.sleep(0.5)
            if browser.current_url != "https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do": #Sometimes pressing the continue button won't prompt a Captcha
                if on_audio_page == True:
                    browser.find_element_by_css_selector('#recaptcha-reload-button').click() #Refreshes the Audio Captcha if Buster can't solve it
                    time.sleep(2)
                    if len(browser.find_elements_by_xpath('/html/body/div/div/div[1]/div[2]/div')) > 0: #Sometimes the automated-queries error appears after you refresh the audio captcha
                        self.automated_queries(browser)
                        on_audio_page = False   

                buster_button = browser.find_element_by_xpath('//*[@id="solver-button"]')
                buster_button.click()
                browser.switch_to.default_content()
                on_audio_page = True
                time.sleep(7) 

    def automated_queries(self, browser): #Continually exits and reenters the Captcha to avoid the "automated queries" error
        while len(browser.find_elements_by_xpath('/html/body/div/div/div[1]/div[2]/div')) > 0:
            browser.find_element_by_css_selector('#reset-button').click()
            time.sleep(1)
            browser.switch_to.default_content()
            browser.find_element_by_xpath('//*[@id="findOffice"]/fieldset/div[5]/input[2]').click()
            time.sleep(2)

            if self.is_alert_present(browser): #Sometimes an alert "Cannot Connect to ReCAPTCHA" pops up. is_alert_present() dismisses the alert
                time.sleep(1)
                browser.find_element_by_xpath('//*[@id="findOffice"]/fieldset/div[5]/input[2]').click()
                time.sleep(1)
            if browser.current_url != "https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do": #Sometimes pressing the continue button won't prompt a Captcha
                frame = browser.find_element_by_css_selector('body > div:nth-child(8) > div:nth-child(2) > iframe')
                browser.switch_to.frame(frame)

    def is_alert_present(self, browser): #Dismisses alert
        try:
            alert = browser.switch_to_alert()
            alert.accept()
            browser.switch_to.default_content()
            return True
        except Exception:
            print("No alert found")
            browser.save_screenshot("no_alert" + datetime.now().strftime("%H:%M:%S") + ".png")
            return False

    def parse_date(self, date): #Parses string to datetime
        array = date.split()
        word_date = array[0] + " " + array[1] + " " + array[2]
        datetime_date = datetime.strptime(word_date, "%b %d, %Y")
        return datetime_date

