
from flask import Flask, redirect, url_for, session
from os import path
import secrets
import datetime
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"

oauth = OAuth()
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url=CONF_URL,
    client_kwargs={'scope': 'openid profile email'},
)


def login_required(user_level):
  def decorator(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
      if 'user' not in session:
        return redirect(url_for('views.home'))
      user_info = session.get('user')
      if user_level == None:
        return view_func(*args, **kwargs)
      if user_info.get('level', '') in user_level:
        return redirect(url_for('auth.login'))
      return view_func(*args, **kwargs)
    return wrapped_view
  return decorator


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'okbhai'
  # app.config['SECRET_KEY'] = secrets.token_hex(20)
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  db.init_app(app)
  oauth.init_app(app)

  from .views import views
  from .auth import auth

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')

  with app.app_context():
    db.create_all()
    scheduler = BackgroundScheduler()

    def cronCall():
      from .models import Society
      societies = Society.query.all()
      for s in societies:
        s.budgetUsed = 0
      db.session.commit()
    scheduler.add_job(cronCall, 'interval', hours=30 * 24, id='main')

  return app


def create_database(app):
  if not path.exists('instance/' + DB_NAME):
    db.create_all(app=app)
    print('Created Database!')
