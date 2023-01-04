from app import db,loginManager as login
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
from app.search import add_index,remove_index,query_index


#heere we define a followers and followed association table

followers = db.Table('followers',
db.Column('follower_id',db.Integer(),db.ForeignKey('user.id')),
db.Column('followed_id',db.Integer(),db.ForeignKey('user.id')))

#define the model class we will use in the application
class User(UserMixin,db.Model):
    # we define an  id 
    id= db.Column(db.Integer,primary_key=True)
    #we define a username
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    #define relationship many to many
    followed = db.relationship('User',secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id== id),
    backref=db.backref('followers',lazy='dynamic'), lazy='dynamic')

    

    #define a method to follow or unfollow user
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    #define a function that fetch posts of followed user
    def followed_posts(self):
        followed = Post.query.join(followers,(followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    

    #define a function to generate a hash password
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    #define a function to check a hash password
    def check_password(self,password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash,password)
    
    #define a fuction to get the user token
    def get_reset_password_token(self,expires_in=600):
        return jwt.encode({
            'reset_password':self.id, 'exp': time() + expires_in
        },current_app.config['SECRET_KEY'],algorithm='HS256')
    
    @staticmethod 
    def verify_reset_password(token):
        try:
            id = jwt.decode(token,current_app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def __repr__(self):
        return '<User {} {} >'.format(self.username,self.password_hash)

    #create a function to set the user profile
    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)



class SearchableMixin(object):
    @classmethod
    def search(cls,expression,page,per_page):
        ids,total = query_index(cls.__tablename__,expression,page=page,per_page=per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        then  = []
        for i in range(len(ids)):
            then.append((ids[i],i))
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(then,value=cls.id)), total

    @classmethod
    def before_commit(cls,session):
        session._changes = {
            'add':list(session.new),
            'update':list(session.dirty),
            'delete':list(session.deleted)
        }
    
    @classmethod
    def after_commit(cls,session):
        for obj in session._changes['add']:
            if isinstance(obj,SearchableMixin):
                add_index(obj.__tablename__,obj)
        for obj in session._changes['update']:
            if isinstance(obj,SearchableMixin):
                add_index(obj.__tablename__,obj)
        for obj in session._changes['delete']:
            if isinstance(obj,SearchableMixin):
                remove_index(obj.__tablename__,obj)
        
        session._changes = None
    
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_index(cls.__tablename__,obj)
    

db.event.listen(db.session, 'before_commit',SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit',SearchableMixin.after_commit)
        
#we define the post model class
class Post(SearchableMixin,db.Model):
    __searchable__ = ["body"]
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lang = db.Column(db.String(5))
    
    def __repr__(self) -> str:
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))        