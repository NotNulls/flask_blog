from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField,PasswordField, EmailField
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