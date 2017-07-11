import os
from flask import g,render_template,flash,redirect,url_for,request,send_from_directory,session
from flask_login import login_user, logout_user, current_user, login_required
from scambio import app,db,login_manager
from models import User, correctLogin, categories, category, product,deals
from forms import RegistrationForm, LoginForm
from werkzeug.utils import secure_filename


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
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html',title="Login",form=form)

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','gif'])
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def uploadfile(submitted):
    if submitted and allowed_file(submitted.filename):
        filename = secure_filename(submitted.filename)
        submitted.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return filename

@app.route('/createad',methods=['POST','GET'])
@login_required
def createad():
    if "submit" in request.form.keys():
        # add categories
        cats = request.form.getlist("cats")
        catspre = []
        already =category.query.all()
        for i in cats:
            f=1
            for j in already:
                if j.category == i:
                    catspre.append(j)
                    f=0
                    break
            if f:
                catspre.append(category(category=i))
        db.session.add_all(catspre)
        # create a model and redirect
        newproduct = product()
        newproduct.owner = current_user
        newproduct.identifier = request.form['identifier']
        newproduct.description = request.form['description']
        newproduct.imagelocation = uploadfile(request.files['pic'])
        newproduct.categories = catspre
        newproduct.available = True
        db.session.add(newproduct)
        db.session.commit()
        return redirect(url_for('explore'))
    return render_template('createad.html',title="Create Ad",categories=category.query.all())

@app.route('/images/<path>')
def images(path):
    return send_from_directory('images',path)

@app.route('/makedeal',methods=['POST','GET'])
@login_required
def makedeal():
    if "submit" in request.form.keys():
        #update the product status
        #notify the deal maker
        deal = deals.query.filter(deals.id == request.form['dealid']).first()
        deal.offerfor.available = False
        deal.confirm = True
        db.session.add(deal)
        db.session.commit()
        
    if product.query.filter(product.id == request.args.get('id')).filter(product.available == True).count()!=0:
        if 'yes' in request.form.keys():
            if deals.query.filter(deals.offerforid==request.args.get('id')).filter(deals.offerbyid==current_user.id).count() ==0:
                newdeal = deals() 
                newdeal.offerfor=product.query.filter(product.id==request.form['prodid']).first()
                newdeal.offerby=current_user
                db.session.add(newdeal)
                db.session.commit()
                flash("Deal offered successfully")
                return redirect(url_for('explore'))
        return render_template('makedeal.html',title="Make Deal")
    return redirect(url_for('explore'))
        
@app.route('/explore',methods=['POST','GET'])
def explore():
    if 'submit' in request.form.keys():
        a = product.query.join(product.categories).filter(product.available == True).filter(category.category.in_(request.form.getlist('cats'))).filter(product.identifier.ilike("%"+request.form['keyword']+"%")).all()
        return render_template('exploreads.html',title="Explore Ads",products=a,cats=category.query.all())

    return render_template('exploreads.html',title="Explore Ads",products=product.query.filter(product.available == True).all(),cats=category.query.all())


@app.route("/dashboard")
@login_required
def dashboard():
    if "page" in request.args.keys():
        if request.args.get('page') == 'offers' and "prodid" in request.args.keys():
            dealos = deals.query.join(deals.offerby).join(deals.offerfor).filter(deals.offerforid == request.args.get('prodid')).all()
            return render_template('offers.html',title='Offers',deals=dealos)
        elif request.args.get('page') == 'replies':
            replies = deals.query.filter(deals.offerby == current_user).filter(deals.confirm==True).all()
            return render_template('replies.html',title="Replies",replies=replies)
    return render_template('myads.html',title='My Products',products=product.query.filter(product.owner==current_user).all())

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
