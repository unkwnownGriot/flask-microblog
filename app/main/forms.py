from flask import request
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import data_required,Length,ValidationError
from app.models import User,Post
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField(_l('username'),validators=[data_required()])
    about_me = TextAreaField(_l('About me'),validators=[Length(min=0,max=140)])
    submit = SubmitField(_l('Register'))

    def __init__(self, original_username,*args,**kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self,username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Please use a different username'))
            
class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something...'),validators=[data_required(),Length(min=1,max=140)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'),validators=[data_required()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata']= request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf':False}
        
        super(SearchForm,self).__init__(*args,**kwargs)

    