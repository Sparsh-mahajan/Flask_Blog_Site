from datetime import datetime
from authlib.jose import JsonWebToken as jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy import PrimaryKeyConstraint
from flaskblog import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id':self.id})

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], max_age = 300)
        try:
            user_id = s.loads(token)['user_id']
        except SignatureExpired:
            return None
        return User.query.get(user_id)      

    def __repr__(self):
        return f"User( '{self.username}', '{self.email}, '{self.image_file}' )"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # passing in the datetime.utcnow function instead of a call to the function. 
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    def __repr__(self):
        return f"Post( '{self.title}', '{self.date_posted}' )"

