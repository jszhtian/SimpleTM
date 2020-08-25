from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SimpleTM import SimpleTM
from config import Config


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[Length(min=3, max=25)])
    password = PasswordField('密码', validators=[Length(min=4, max=35)])
    confirm = PasswordField('确认密码', validators=[
        EqualTo('password', message='与之前输入的密码不匹配')
    ])
    submit = SubmitField('注册')

    def validate_username(self, username):
        db = SimpleTM(Config.dbFileName)
        u = db.QueryUser(username.data)
        if u:
            raise ValidationError('用户名已被使用')

class NewGameForm(FlaskForm):
    gid = StringField('项目名称', validators=[Length(min=3, max=40)])
    description = StringField('项目描述', validators=[Length(min=0, max=300)])