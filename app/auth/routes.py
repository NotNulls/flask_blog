from app import db
from app.auth import bp
from flask import redirect, render_template, url_for, request, flash
from flask_login import current_user, logout_user, login_user
from werkzeug.urls import url_parse
from app.auth.forms import LoginForm, RegistrationForm,\
     ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.email import send_password_reset_mail


@bp.route('/login', methods= ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash (f'Login request for user {str(User.query.filter_by(username=user.username).first())[5::]}, remember_me: {form.remember_me.data}')
        # user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect (url_for('auth.login'))
        #login_user is an option form login module where it holds a walue of a 'next' argument until we go through with the login function
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        #line below is making sure that the whole url is relative and that the redirection goes within the app, not some other site
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In',form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registrated')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title="Register", form=form)


@bp.route('/reset_password_request', methods=['POST','GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
        flash('Look up you email for further instructions')
        return redirect(url_for('auth.login'))
    return render_template('auth.reset_password_request.html', title='Reset Password', form = form)


@bp.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated():
        return redirect(url_for('main.index'))
    user = User.verify_reset_token_password()
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfuly changed.')
        return redirect(url_for('auth.login'))
    return render_template('auth.reset_password.html', form=form)

