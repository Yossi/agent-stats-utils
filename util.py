import pymysql # pip install pymysql
# pymysql.install_as_pymysql()
# import pymysql
import logging

import warnings
warnings.filterwarnings('error', category=pymysql.Warning)

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
            self.connection = pymysql.connect(**self.credentials)
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

    except pymysql.OperationalError:
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
import platform
from ftfy import fix_text # pip install ftfy
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import gmail_user, gmail_pwd

def mail(to, subject, text, attach=False, host=False):
    # to needs to be a list
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = ", ".join(to) if len(to[0])-1 else to
    if host:
        subject = platform.node() + ' ' + subject
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
