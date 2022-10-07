from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField,PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from app.models import User

class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember_me = BooleanField(label='Remember me')
    submit = SubmitField(label='Sign in')

class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    password2 = PasswordField(label='Repeat Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField(label='Register')

    #validating if there is any other user with this name and last name
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(message='Please use a different username.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Please user a different email address.')

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

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Submit Password Reset')


    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Re-enter Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Request')