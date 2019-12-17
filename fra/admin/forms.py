from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields import StringField, TextAreaField, SubmitField, SelectField, BooleanField, PasswordField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired, email, equal_to, length, regexp
from flask_uploads import UploadSet, IMAGES, configure_uploads
from .. import app
from ..models import Role, Client, ProductArea

images = UploadSet('images', IMAGES)
configure_uploads(app, (images,))


class UserForm(Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password')
    image = FileField('Image', validators=[
                      FileAllowed(images, 'Images Only!')])
    phone = StringField('Phone')
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Confirm')
    allowed = BooleanField('Allowed')
    Submit = SubmitField('Submit')

    def __init__(self, *args, ** kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name) for r in Role.query.all()]


class FeatureForm(Form):
    title = StringField('Title')
    description = TextAreaField('Description', validators=[DataRequired()])
    target_date = DateField('Target Date', validators=[DataRequired()])
    product_area = SelectField('Product area', validators=[
                               DataRequired()], coerce=int)
    priority = IntegerField('Priority', validators=[DataRequired()])
    client = SelectField('Client', validators=[DataRequired()], coerce=int)
    Submit = SubmitField('Submit')

    def __init__(self, *args, ** kwargs):
        super(FeatureForm, self).__init__(*args, **kwargs)
        self.product_area.choices = [(p.id, p.name)
                                     for p in ProductArea.query.all()]
        self.client.choices = [(c.id, c.name) for c in Client.query.all()]
