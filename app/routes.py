
from datetime import datetime
from app import app, db
from app.email import send_password_reset_mail
from flask import render_template, flash, redirect, url_for, request
from app.forms import EditProfileForm, Emptyform, LoginForm, RegistrationForm, PostForm, ResetPasswordRequestForm , ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from app.email import send_password_reset_mail

@app.route('/',methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    form= PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your latest post.')
        # redirect is used as a standard procedure to cope with the refreshin of the form/page. To avoid duplicate submissions aka Post/Redirect/Get pattern
        return redirect(url_for('index'))
    page = request.args.get('page',1,type=int)

    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title="Home", posts=posts.items, next_url=next_url, prev_url=prev_url) 
   

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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    form = Emptyform()
    return render_template('user.html', user=user,posts = posts, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['POST','GET'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('The changes to your profile have been updated')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title='Edit Profile')


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = Emptyform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User "{username}" could not be found.')
            return redirect(url_for('index'))
        if user==current_user:
            flash('You cannot followe yourself.')
            return redirect('user', username=username)
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
        
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'],False
    )
    next_url = url_for('explore', page = posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page = posts.prev_num) if posts.has_prev else None
    #we are rendering index.html since the pages that we desire are of similar content. Yet, we are not rendering form, since we do not want to write comment but rather to display them. Therefore we are adding a conditional to index.html so it wont't crash after trying to render the form.
    
    return render_template('index.html', posts=posts.items, title='explore', next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['POST','GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
        flash('Look up you email for further instructions')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form = form)

@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    user = User.verify_reset_token_password()
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfuly changed.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
