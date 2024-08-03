from flask_mail import Mail, Message

class MailSender:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.mail = None

    def init_app(self, app):
        self.mail = Mail(app)

    def send(self, subject, sender, recipients, body, html=None, bcc=None):
        if self.mail is None:
            raise RuntimeError('Mail has not been initialized. Call init_app() first.')

        # If bcc is not provided, default to sender's address
        if bcc is None:
            bcc = [sender]

        msg = Message(subject=subject,
                      sender=sender,
                      recipients=recipients,
                      body=body,
                      html=html,
                      bcc=bcc)
        self.mail.send(msg)
