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
import pickle

try:
    input = raw_input
except NameError:
    pass

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%H:%M:%S")

# once you have your cookies and this is able to smoothly post a data point without 
# intervention, you can change this to True and go setup cron to run the script
HEADLESS = False #True

options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
if HEADLESS:
    options.add_argument('headless')
    options.add_argument('disable-gpu')
driver = webdriver.Chrome(chrome_options=options)
driver.implicitly_wait(5)

try:
    driver.set_window_size(1024, 768)
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        driver.get('https://www.agent-stats.com')
        for cookie in cookies:
            #print(cookie)
            driver.add_cookie(cookie)
    except FileNotFoundError:
        pass

    driver.get('https://www.agent-stats.com/export.php')
    sleep(3)
    logging.info('url loaded')
    
    if 'Sign in' in driver.find_element_by_tag_name("BODY").text:
        print('Sign in with your Google Account')
        print('If you do this wrong, shit will explode (or not work)')
        try:
            email = driver.find_element_by_xpath("//input[@type='email']")
            email.clear()
            email.send_keys(input('Email: '))
            driver.find_element_by_id("identifierNext").click() # replace these clicks with an enter press?
            sleep(1)
        except InvalidElementStateException:
            pass

        password = driver.find_element_by_xpath("//input[@type='password']")
        password.clear()
        password.send_keys(getpass.getpass().strip())
        driver.find_element_by_id("passwordNext").click()

        input('Press enter to continue. Complete the two-factor song and dance first (if applicable).')
        
        pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
    
    data = driver.find_elements_by_tag_name("tr")[-1].text # needs more brains than simply "the last one"
    
    temp = data.split()
    now = datetime.datetime.now()
    temp[0] = now.strftime('%Y-%m-%d')
    temp[1] = now.strftime('%H:%M:%S')
    temp[2] = str(int(temp[2])+1)
    temp[-1] = '" statfixer "' # agent-stats bug cuts off first and last char
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
