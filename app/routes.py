from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {"username": "Miguel"}

    posts = [
        {
        'author': {'username':'John'},
        'body' : 'Beautifgul day in Portugal!'
        },
        {
            'author' : {'username':'Susan'},
            'body':'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title="Home", posts=posts) 
   

@app.route('/login', methods= ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash (f'Login request for user {str(User.query.filter_by(username=user.username).first())[5::]}, remember_me: {form.remember_me.data}')
        # user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect (url_for('login'))
        #login_user is an option form login module where it holds a walue of a 'next' argument until we go through with the login function
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        #line below is making sure that the whole url is relative and that the redirection goes within the app, not some other site
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registrated')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)