import os
from flask import g,render_template,flash,redirect,url_for,request,send_file,session
from flask_login import login_user, logout_user, current_user, login_required
from scambio import app,db,login_manager
from models import User, correctLogin, prodcats, category, product
from forms import RegistrationForm, LoginForm


@app.route('/')
def home():
    if current_user.is_anonymous:
        return render_template("cover.html")
    return redirect(url_for('dashboard'))

@app.route('/register',methods=['POST','GET'])
def register():
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).count() == 0:
            user = User(form.fullname.data,form.email.data,form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('You registered Successfully')
            return redirect(url_for('login'))
        else:
            flash('Email already registered')
    return render_template('register.html',title="Register",form=form)

@app.route('/login',methods=['POST','GET'])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = load_user(form.email.data)
        if correctLogin(user,form.password.data):
            login_user(user)
            session['id']=user.id
            session['email']=form.email.data
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('signin.html',title="Login",form=form)

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

@app.route('/createad',methods=['POST','GET'])
@login_required
def createad():
    if "submit" in request.form.keys():
        cats = request.form.getlist("cats")

        return "done"
    return render_template('createad.html',title="Create Ad",categories=category.query.all())

@app.route('/itemdetails')
def itemdetails():
    pass

@app.route('/additem')
def additem():
    pass

@app.route('/myitems')
def myitems():
    pass

@app.route("/dashboard")
@login_required
def dashboard():
    return "dashboard"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
