"""
Utility functions for sending notifications.
"""

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_email(context):
    """
    Send the notification email.
    """
    current_app.logger.debug('Sending email with context: {}'.format(context))
    subject = context['subject'].format(**context)
    body = render_template(context['body'], **context)
    msg = Message(
        subject,
        recipients=context['to'],
    )
    msg.body = body
    current_app.logger.info('Sending email to {!r} with subject {!r}'.format(
        context['to'], subject,
        ))
    mail.send(msg)


def send_notifications(data):
    """
    Wrapper method to send out notifications.
    """
    pr_data = data['pull_request']
    repo = data['repository']['full_name']
    watch_config = data['watch_config']

    action = data['action']
    if action == 'synchronize':
        action = 'updated'
    elif action == 'closed' and pr_data['merged'] is True:
        action = 'merged'

    context = {
        'repo': repo,
        'number': data['number'],
        'patterns': ", ".join(watch_config['patterns']),
        'action': action,
        'merged': pr_data['merged'],
        'creator': pr_data['user']['login'],
        'to': watch_config['recipients'],
        'subject': watch_config['subject'],
        'body': watch_config['body'] if 'body' in watch_config else 'email_body.txt',
        'pr_url': pr_data['_links']['html']['href'],
        'modified_files': data['modified_files'],
        'pr': pr_data,
    }
    send_email(context)
