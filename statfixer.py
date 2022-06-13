# Slapped together script to automatically upload a start point for you each week.
# ALPHA SOFTWARE. Not particularly stable, but has worked for me a few times already.
# Have this run a short time after your weekly stats job runs.
# It will upload your most recent datapoint again but with a time stamp in range
# of next week's stat pull. Adds 1 ap because otherwise agent-stats won't take it.

from time import sleep
from webdriver import get_driver # pip install git+https://github.com/Yossi/webdriver#webdriver
from selenium.webdriver.common.by import By
import logging

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

def main():
    try:
        driver = get_driver(HEADLESS)

        driver.implicitly_wait(5)
        driver.set_window_size(1024, 768)
        driver.get('https://www.agent-stats.com/quick_add.php')
        sleep(3)
        logging.info('url loaded')

        if 'Sign in' in driver.find_element(by=By.TAG_NAME, value='BODY').text:
            if HEADLESS:
                driver.save_screenshot('selenium.png')
                # not really how to raise exceptions, but this line crashes and that's the point here
                raise 'You need to login. Set HEADLESS = False and try again.'
            input('Press enter after you have logged in... ')

        driver.get('https://www.agent-stats.com/quick_add.php') # loads up with everything already filled in. basically does exactly what we need

        comment = driver.find_element(by=By.XPATH, value="//input[@name='comment']")
        comment.clear()
        comment.click()
        comment.send_keys('statfixer')

        save = driver.find_element(by=By.XPATH, value="//input[@value='save']")
        save.click()

        #driver.save_screenshot('selenium.png')
        #logging.info('screenshot saved')

    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()
