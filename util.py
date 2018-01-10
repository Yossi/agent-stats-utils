import pymysql # pip install pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import logging

import warnings
warnings.filterwarnings('error', category=MySQLdb.Warning)

class CM(object):
    ''' connection manager '''
    def __init__(self):
        self.connection = None

    def set_credentials(self, credentials):
        self.credentials = credentials
        self.close()

    def get_conn(self):
        if not self.connection:
            logging.info('no db connection. creating...')
            self.connection = MySQLdb.connect(**self.credentials)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

cm = CM()

def exec_mysql(sql, retries=2):
    try:
        cur = None # needed in case get_conn() dies
        db = cm.get_conn()
        cur = db.cursor()
        cur.execute(sql)
        rows = [r for r in cur.fetchall()]
        if not rows and not sql.strip().lower().startswith('select'):
            rows = cur.rowcount
        cur.close()
        db.commit()
        return rows

    except MySQLdb.OperationalError as exc:
        if cur:
            cur.close()
        cm.close()
        if retries:
            logging.warning('sql query failed, retrying')
            return exec_mysql(sql, retries-1)
        else:
            raise

    except:
        logging.error(sql)
        raise


#######


import smtplib
from ftfy import fix_text
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import gmail_user, gmail_pwd

def mail(to, subject, text, attach=False):
    # to needs to be a list
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = ", ".join(to) if len(to[0])-1 else to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    if attach:
        part = MIMEApplication(fix_text(text), Name=subject)
        part['Content-Disposition'] = 'attachment; filename="%s.txt"' % subject
        msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
    logging.info((msg['To'], msg['Subject']))


#######


import os
from time import sleep
import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import InvalidElementStateException

def get_html(scoreboard=None, time_span='current'):
    logging.info("get_html({}, {})".format(scoreboard, time_span))

    driver = webdriver.PhantomJS('./phantomjs', service_args=['--cookies-file=cookies.txt'], service_log_path=os.path.devnull)
    logging.info('driver created')

    try:
        driver.set_window_size(1024, 768)
        driver.get('https://www.agent-stats.com/groups.php')
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

        if scoreboard:
            from agent_stats import get_groups # recursive import. be very careful
            group_id = get_groups(scoreboard)[0]
            driver.get('https://www.agent-stats.com/groups.php?group={}&type={}'.format(group_id, time_span))
            #logging.info('saving screenshot')
            #driver.save_screenshot('selenium.png')

        html = driver.page_source

    finally:
        driver.quit()

    logging.info('html acquired')
    return html
