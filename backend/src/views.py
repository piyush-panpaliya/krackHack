from .models import Ticket
from . import db
from .controllers import getAllServices, getService
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
import json
import os
import datetime
from .discord import webhook
from dotenv import load_dotenv
load_dotenv()

# from flask_login import login_required, current_user

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
  return redirect(url_for('views.servicesRoute'))


@views.route('/services', methods=['GET'])
def servicesRoute():
  return render_template("index.html", services=None, loggedIn=session.get("user", None) != None)


@views.route('/service/<name>', methods=['GET'])
def serviceRoute(name):
  # work on sanitization
  if not name.isalpha():
    return "err! wrong input"
  sanitizedName = name.replace("{", "").replace("}", "")
  return render_template("service.html", service=None, loggedIn=session.get("user", None) != None)


@views.route('/api/update', methods=['GET'])
def updateStatusManually():
  # this function expects a JSON from the INDEX.js file
  password = request.args.get("pass")
  return "chle ja bhai"


@views.route('/ticket', methods=['GET', 'POST'])
def newTicket():

    # user = session['user']
    # print(user)
  if session.get("user", None) != None:
    user = session['user']

    if request.method == 'POST':
      content = request.form['content']
      title = request.form['title']
      new_ticket = Ticket(content=content, title=title,
                          email=user["email"], oauth_id=user["sub"])
      try:
        db.session.add(new_ticket)
        db.session.commit()
        webhook(
          "ticket", {"content": content, "title": title, "email": user["email"]})
        return redirect('/ticket')

      except:
        return 'errorrrr'

    return render_template('ticket.html')
  else:

    session["next"] = "/ticket"
    return redirect(url_for("auth.login"))
