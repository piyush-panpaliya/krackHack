from flask import Blueprint, session, url_for, redirect, request
from .models import User
from . import db, google


auth = Blueprint('auth', __name__)


# Routes
@auth.route('/login')
def login():
  session['level'] = request.args.get("level")
  return google.authorize_redirect(url_for('auth.authorize', _external=True, _scheme='http'))


@auth.route('/authorize')
def authorize():
  token = google.authorize_access_token()
  user_info = token['userinfo']
  user = User.query.filter_by(oauth_id=user_info['sub']).first()
  print(user_info['email'])
  if not user:
    user = User(oauth_id=user_info['sub'], approved=False, level="dean")
    db.session.add(user)
    db.session.commit()

  session['user'] = {
      'id': user.id,
      'oauth_id': user.oauth_id,
      'level': user.level,
      'approved': user.approved
  }
  return redirect(url_for('views.home'))


@auth.route('/logout')
def logout():
  session.pop('user', None)
  return redirect(url_for("views.home"))
