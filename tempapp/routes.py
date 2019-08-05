from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from tempapp import app, db, bcrypt, mail
from tempapp.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                           NewRecordForm, RequestResetForm, ResetPasswordForm, RenameRecordForm)
from tempapp.models import User, Record, OldRecord


@app.route("/")
@app.route("/info")
def info():
    return render_template('info.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('info'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = NewRecordForm()
    if form.validate_on_submit():
        record = Record(temp=form.temp.data, notes=form.notes.data, author=current_user)
        db.session.add(record)
        db.session.commit()
        flash(f'Temperature added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', title='Input temp', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/record_update/<record_id>", methods=['GET', 'POST'])
@login_required
def record_update(record_id):
    record = Record.query.get_or_404(record_id)
    if record.author != current_user:
        abort(403)
    form = NewRecordForm()
    if form.validate_on_submit():
        record.temp = form.temp.data
        record.notes = form.notes.data
        db.session.commit()
        flash(f'Record updated', 'success')
        return redirect(url_for('dashboard'))
    else:
        form.temp.data = record.temp
        form.notes.data = record.notes
    return render_template('record_update.html', title='Input temp', form=form)

@login_required
@app.route("/archivise")
def archivise():

    temps = str(list(x.temp for x in Record.query.filter_by(author=current_user)))
    notes = str(list(x.notes for x in Record.query.filter_by(author=current_user)))
    date_list = list(x.date_posted for x in Record.query.filter_by(author=current_user))
    date_begin = date_list[0]
    date_end = date_list[-1]
    old_record = OldRecord(temps=temps, notes=notes, date_begin=date_begin, date_end=date_end, author=current_user)
    db.session.add(old_record)
    db.session.commit()
    db.session.query(Record).filter_by(author=current_user).delete()
    db.session.commit()
    return redirect(url_for('dashboard'))

@login_required
@app.route("/old_records", methods=['GET', 'POST'])
def old_records():
    old_records = OldRecord.query.filter_by(author=current_user)
    form = RenameRecordForm()
    return render_template('old_records.html', title='archivised', old_records=old_records, form=form)


@login_required
@app.route("/rename_record/<record_id>", methods=['GET', 'POST'])
def rename_record(record_id):
    form = RenameRecordForm()
    if form.validate_on_submit():
        record = OldRecord.query.filter_by(id=record_id).first()
        record.name = form.record_name.data
        db.session.commit()
        flash(f'Record name updated', 'success')
        return redirect(url_for('old_records'))

