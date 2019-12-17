import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    UPLOADED_IMAGES_DEST = os.path.join(basedir, 'static/images')
    UPLOAD_FOLDER = os.path.join(basedir, 'static/images')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = '\xb0w5K\xfc9s/\xbd2\x9fjF@\xb8\xcd\x97\x87}\xeb\xa9\x82\x95\\'
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    MAIL_SERVER = 'mail.dreamroomltd.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'iws@dreamroomltd.com'
    MAIL_PASSWORD = 'password@aA'
    IWS_MAIL_SUBJECT_PREFIX = '[IWS]'
    IWS_MAIL_SENDER = 'IWS <noreply@iws.com>'
    IWS_ADMIN = 'tabot.kevin@gmail.com'
    ADMIN = 'tabot.kevin@gmail.com'
    TEMPLATE_AUTO_RELOAD = True
