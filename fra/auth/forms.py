__author__ = 'CRUCIFIX'

from flask_wtf import Form
from wtforms.fields import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, email, equal_to, length, regexp
from wtforms import ValidationError
from ..models import User, Role


class LoginForm(Form):
    email = StringField('Email', validators=[
                        DataRequired(), email(), length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    first_name = StringField('First Name', validators=[regexp('^[A-Za-z]')])
    last_name = StringField('Last Name', validators=[regexp('^[A-Za-z]')])
    email = StringField('Email', validators=[
                        DataRequired(), length(1, 64), email()])
    phone = StringField('Phone number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(
    ), equal_to('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
                             DataRequired(), equal_to('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[
                        DataRequired(), email(), length(1, 64)])
    submit = SubmitField('Submit')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[
                        DataRequired(), length(1, 64), email()])
    password = PasswordField('New Password', validators=[DataRequired(), equal_to('password2',
                                                                                  message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[
                        DataRequired(), length(1, 64), email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
