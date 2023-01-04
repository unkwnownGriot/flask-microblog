from flask import redirect,render_template,url_for,flash,request
from werkzeug.urls import url_parse
from flask_login import login_user,logout_user,current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm,ResetPasswordRequest,ResetPasswordForm ,\
      ResetPasswordRequest,RegistrationForm
from app.models import User
from app.auth.email import send_password_reset_mail


@bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) :
            flash(_('Invalid username or password '))
            return redirect(url_for('auth.login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)        
    return render_template('auth/login.html',title=_('Sign In'),form=form)


@bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password_request.html',form=form,title=_('Reset Password'))

@bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('maim.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations you are now register!'))
        return redirect(url_for('main.index'))
    return render_template('register.html',title=_('Register'),form=form)


@bp.route('/reset_passord/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user= User.verify_reset_password(token=token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))