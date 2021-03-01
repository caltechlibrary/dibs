'''
email.py: email utilities for DIBS
'''

from   decouple import config
import smtplib

from .date_utils import human_datetime

if __debug__:
    from sidetrack import log


# Constants used throughout this file.
# .............................................................................

# Body of email message sent to users
_EMAIL = '''From: {sender}
To: {user}
Subject: {subject}

You started a digital loan through Caltech DIBS at {start}.

  Title: {item.title}
  Author: {item.author}

  The loan period ends at {end}
  Web viewer: {viewer}

Information about loan policies can be found at {info_page}

Thank you for using Caltech DIBS. We hope the experience is a pleasant one.
Please don't hesitate to send us feedback using our anonymous feedback form
at {feedback}
'''


# Exported functions.
# .............................................................................

def send_email(user, item, start, end, base_url):
   try:
       subject = f'Caltech DIBS loan for "{item.title}"'
       viewer = f'{base_url}/view/{item.barcode}'
       info_page = f'{base_url}/info'
       body = _EMAIL.format(item      = item,
                            start     = human_datetime(start),
                            end       = human_datetime(end),
                            viewer    = viewer,
                            info_page = info_page,
                            user      = user,
                            subject   = subject,
                            sender    = config('MAIL_SENDER'),
                            feedback  = config('FEEDBACK_URL'))
       if __debug__: log(f'sending mail to {user} about loan of {item.barcode}')
       mailer  = smtplib.SMTP(config('MAIL_HOST'))
       mailer.sendmail(config('MAIL_SENDER'), [user], body)
   except Exception as ex:
       if __debug__: log(f'unable to send mail: {str(ex)}')
