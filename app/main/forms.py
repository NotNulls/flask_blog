from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    about_me = TextAreaField(label='About me', validators=[Length(min=0,max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username = self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class Emptyform(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField(label='Write something', validators=[DataRequired(),Length(min=0,max=150)])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])


class MessageForm(FlaskForm):
    message = TextAreaField(label='Message', validators=[DataRequired(),Length(min=0, max=140)])
    submit = SubmitField('Send')

