import smtplib
import logging
import oauth2client
from oauth2client import client, tools, file
from apiclient import errors, discovery
import httplib2
import platform
from ftfy import fix_text # pip install ftfy
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from secrets import gmail_sender
try:
    simple_mail = False
    from secrets import gmail_app_password
    simple_mail = True
except:
    pass


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

    if simple_mail:
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_sender, gmail_app_password)
        mailServer.sendmail(gmail_sender, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
    else:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
        message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        return SendMessageInternal(service, "me", message)

if __name__ == '__main__':
    get_credentials()