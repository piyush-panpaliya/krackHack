from flask import Blueprint, session, url_for, redirect, request
from .models import User, Society, Club
from . import db, google
import os

auth = Blueprint('auth', __name__)


# Routes
@auth.route('/login')
def login():
  if session.get('user'):
    return redirect(url_for('views.home'))
  session['level'] = request.args.get("level")
  if request.args.get("level", None):
    session['id'] = request.args.get("id")
  session['level'] = request.args.get("level")
  s = 'https' if os.environ.get('ENV', 'dev') == 'prod' else 'http'
  return google.authorize_redirect(url_for('auth.authorize', _external=True, _scheme=s))


@auth.route('/authorize')
def authorize():
  token = google.authorize_access_token()
  user_info = token['userinfo']
  user = User.query.filter_by(oauth_id=user_info['sub']).first()
  print(user_info['email'])
  if not user:
    try:
      if session.get('id'):
        if session.get('level') in ["sec", "sfa"]:
          society = Society.query.filter_by(id=int(session["id"])).first()
          print(society.id)
          user = User(oauth_id=user_info['sub'],
                      email=user_info['email'], approved=False, level=session["level"], society_id=society.id)
          db.session.add(user)
        else:
          club = Club.query.filter_by(id=int(session["id"])).first()
          user = User(oauth_id=user_info['sub'],
                      email=user_info['email'], approved=False, level=session["level"], club_id=int(session["id"]), club=club)
          print(user)
          db.session.add(user)
      else:
        user = User(oauth_id=user_info['sub'],
                    approved=False, level=session["level"], email=user_info['email'])
        db.session.add(user)
      db.session.commit()
    except:
      db.session.rollback()
      session.pop('level', None)
      session.pop('user', None)
      return redirect(url_for('views.home'))

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
