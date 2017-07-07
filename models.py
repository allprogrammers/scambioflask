from werkzeug.security import generate_password_hash, check_password_hash
from scambio import db

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(30))
    email = db.Column(db.String(100),unique=True,index=True)
    password_hash = db.Column(db.String(100))
    products = db.relationship('product',backref='user')

    def __init__(self,fullname,email,password):
        self.fullname = fullname
        self.email = email
        self.password = password

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return self.email

def correctLogin(user,password):
    return user is not None and user.verify_password(password)

prodcats = db.Table('prodcats',db.Column('catid',db.Integer,db.ForeignKey('category.id')),db.Column('prodid',db.Integer,db.ForeignKey('product.id')))

class category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(30),unique=True)
    products = db.relationship('product',secondary = prodcats, backref=db.backref('prodcats',lazy='dynamic'))

    def __init__(self,category):
        self.category = category

#class prodcat(db.Model):
#    __tablename__ = "prodcat"
#    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#    prodid = db.Column(db.Integer, db.ForeignKey('products.id'))
#    catid = db.Column(db.Integer, db.Foreignkey('categories.id'))

class product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productby = db.Column(db.Integer,db.ForeignKey('user.id'))
    identifier = db.Column(db.String(50))
    description = db.Column(db.String(500))
    imagelocation = db.Column(db.String(100))

