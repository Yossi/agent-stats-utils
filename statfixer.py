# Slapped together script to automatically upload a start point for you each week.
# ALPHA SOFTWARE. Not particularly stable, but has worked for me a few times already.
# Have this run a short time after your weekly stats job runs.
# It will upload your most recent datapoint again but with a time stamp in range
# of next week's stat pull. Adds 1 ap because otherwise agent-stats won't take it.

from time import sleep
from selenium import webdriver
import logging
import datetime
import pickle
import os
import requests
import platform
from zipfile import ZipFile
from io import BytesIO

try:
    input = raw_input
except NameError:
    pass

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')

try:
    # once you have your profile and this is able to smoothly post a data point without 
    # intervention, you can change this to True in secrets.py and go setup cron to run the script
    from secrets import HEADLESS
except:
    HEADLESS = False

options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
options.add_argument("user-data-dir=profile/")
if HEADLESS:
    options.add_argument('headless')
    options.add_argument('disable-gpu')

try:
    driver = webdriver.Chrome('./chromedriver', chrome_options=options)
    current_version = driver.capabilities['chrome']['chromedriverVersion']
    latest_version = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text.strip()
    if not current_version.startswith(latest_version):
        driver.quit() # need to release the file lock
        logging.info('chromedriver out of date. attempting to update')
        arch = {'Linux': 'linux64', 'Darwin': 'mac64', 'Windows': 'win32'}[platform.system()] # these are the only options available
        logging.info('%s detected', arch)
        url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_{}.zip'.format(latest_version, arch)
        logging.info('downloading...')
        zip_file = ZipFile(BytesIO(requests.get(url).content))
        for name in zip_file.namelist():
            if name.startswith('chromedriver'):
                logging.info('unzipping...')
                with open(name, 'wb') as out:
                    out.write(zip_file.read(name))
                logging.info('ready')
                break
        driver = webdriver.Chrome('./chromedriver', chrome_options=options) # reopen with fresh new chromedriver

    driver.implicitly_wait(5)
    driver.set_window_size(1024, 768)
    driver.get('https://www.agent-stats.com/export.php')
    sleep(3)
    logging.info('url loaded')
    
    if 'Sign in' in driver.find_element_by_tag_name('BODY').text:
        if HEADLESS:
            driver.save_screenshot('selenium.png')
            # not really how to raise exceptions, but this line crashes and that's the point here
            raise 'You need to login. Set HEADLESS = False and try again.'
        input('Press enter after you have logged in... ')
    
    data = driver.find_elements_by_tag_name("tr")[-1].text # needs more brains than simply "the last one"
    
    temp = data.split()
    now = datetime.datetime.now()
    temp[0] = now.strftime('%Y-%m-%d')
    temp[1] = now.strftime('%H:%M:%S')
    temp[2] = str(int(temp[2])+1)
    temp[-1] = '"statfixer"'
    data = ' '.join(temp)
    logging.info(data)
    driver.get('https://www.agent-stats.com/import.php')
    textarea = driver.find_element_by_tag_name('textarea')
    textarea.click()
    textarea.send_keys(data)
    driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/form/input').click()

    #driver.save_screenshot('selenium.png')
    #logging.info('screenshot saved')

finally:
    driver.quit()
