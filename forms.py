from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SimpleTM import SimpleTM
from config import Config


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=3, max=25)])
    password = PasswordField('Password', validators=[Length(min=4, max=35)])
    confirm = PasswordField('Repeat Password', validators=[
        EqualTo('password', message='Password must match')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        db = SimpleTM(Config.dbFileName)
        u = db.QueryUser(username.data)
        if u:
            raise ValidationError('User name already been taken')
