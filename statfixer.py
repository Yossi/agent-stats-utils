# Slapped together script to automatically upload a start point for you each week.
# ALPHA SOFTWARE. Not particularly stable, but has worked for me a few times already.
# Have this run a short time after your weekly stats job runs.
# It will upload your most recent datapoint again but with a time stamp in range
# of next week's stat pull. Adds 1 ap because otherwise agent-stats won't take it.

from time import sleep
import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import InvalidElementStateException
import logging
import datetime

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%H:%M:%S")
driver = webdriver.PhantomJS('./phantomjs', service_args=['--cookies-file=cookies.txt'])

try:
    driver.set_window_size(1024, 768)
    driver.get('https://www.agent-stats.com/export.php')
    logging.info('url loaded')
    
    if 'Sign in with your Google Account' in driver.find_element_by_tag_name("BODY").text:
        print('Sign in with your Google Account')
        print('If you do this wrong, shit will explode (or not work)')
        try:
            driver.find_element_by_id("Email").clear()
            driver.find_element_by_id("Email").send_keys(input('Email: '))
            driver.find_element_by_id("next").click()
            sleep(1)
        except InvalidElementStateException:
            pass
        driver.find_element_by_id("Passwd").clear()
        driver.find_element_by_id("Passwd").send_keys(getpass.getpass())
        driver.find_element_by_id("signIn").click()

        if '2-Step Verification' in driver.find_element_by_tag_name("BODY").text:
            driver.find_element_by_id("totpPin").clear()
            driver.find_element_by_id("totpPin").send_keys(input('Enter your 2FA code: '))
            #driver.find_element_by_id("trustDevice").click()
            driver.find_element_by_id("submit").click()

    data = driver.find_elements_by_tag_name("tr")[-1].text # needs more brains than simply "the last one"
    
    temp = data.split()
    now = datetime.datetime.now()
    temp[0] = now.strftime('%Y-%m-%d')
    temp[1] = now.strftime('%H:%M:%S')
    temp[2] = str(int(temp[2])+1)
    temp[-1] = '"statfixer"'
    data = ' '.join(temp)
    print(data)
    driver.get('https://www.agent-stats.com/import.php')
    textarea = driver.find_element_by_tag_name('textarea')
    textarea.click()
    textarea.send_keys(data)
    driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/form/input').click()

    driver.save_screenshot('selenium.png')
    logging.info('screenshot saved')

finally:
    driver.quit()
