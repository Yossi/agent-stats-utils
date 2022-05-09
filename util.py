import pymysql # pip install pymysql
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


import oauth2client
from oauth2client import client, tools, file
from apiclient import errors, discovery
import httplib2
import platform
from ftfy import fix_text # pip install ftfy
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import gmail_sender
import base64

def get_credentials():
    credential_path = 'gmail-python-email-send.json'
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oauth2client.client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/gmail.send')
        flow.user_agent = 'agent-stats-util'
        args = oauth2client.tools.argparser.parse_args()
        args.noauth_local_webserver = True
        credentials = oauth2client.tools.run_flow(flow, store, args)
        logging.info('Storing credentials to ' + credential_path)
    return credentials

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        logging.info('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        logging.error('An error occurred: %s' % error)
        return "Error"

def mail(to, subject, text, attach=False, host=False):
       # to has to be a list

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)


    msg = MIMEMultipart()

    msg['From'] = gmail_sender
    msg['To'] = ", ".join(to) if len(to[0])-1 else to
    if host:
        subject = platform.node() + ' ' + subject
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    if attach:
        part = MIMEApplication(fix_text(text), Name=subject)
        part['Content-Disposition'] = 'attachment; filename="%s.txt"' % subject
        msg.attach(part)

    message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}


    return SendMessageInternal(service, "me", message)

if __name__ == '__main__':
    get_credentials()