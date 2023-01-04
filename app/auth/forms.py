from flask_wtf  import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField
from wtforms.validators import data_required,Email,ValidationError,EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('username'),validators=[data_required()])
    password = PasswordField(_l('password'),validators=[data_required()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Sign in'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('username'),validators=[data_required()])
    email = StringField(_l('email'),validators=[data_required(),Email()])
    password = PasswordField(_l('password'),validators=[data_required()])
    repeat_password = PasswordField(_l('repeat password'),validators=[data_required(),EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('This Username is already used'))

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('This email address already exist'))



class ResetPasswordRequest(FlaskForm):
    email = StringField(_l('Email'),validators=[data_required(),Email()])
    submit = SubmitField(_l('Submit'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('password'),validators=[data_required()])
    password2 = PasswordField(_l('Repeat password'),validators=[data_required(),EqualTo('password')])
    submit = SubmitField(_l('Submit'))
    