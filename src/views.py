from . import db
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from . import login_required
from .models import User, Comment, Club, Society, Approval, Ticket
from dotenv import load_dotenv
load_dotenv()

level = ["clubmember", "sec", "sfa", "cfa", "csap", "dean"]


def getApproval(amount, budgetUsed):
  if amount < 15000 and 15000 - budgetUsed >= amount:
    return ["sec", "sfa", "cfa"]
  elif amount < 50000 or 15000 - budgetUsed < amount:
    return ["sec", "sfa", "cfa", "csap"]
  return ["sec", "sfa", "cfa", "csap", "dean"]


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required(None)
def home():
  if session["user"]["level"] in ["clubmember", "sec"]:
    return redirect('/tickets')
  return redirect(url_for('views.approve'))


@views.route('/approve/<id>', methods=['GET', 'POST'])
@login_required(None)
def approveTicket(id):
  user = session['user']
  if user["level"] in ["clubmember", "sec"]:
    return redirect('/tickets')
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')

  approval = Approval.query.filter_by(ticket=id).first()
  if not approval or approval.level != user.level:
    return redirect('/approve')

  if request.method == 'POST':
    if request.form['status']:
      if not approval.pastApproved:
        return render_template('approve.html', ticket=approval.ticket, error="Ticket not approved at lower level")
      status = request.form['status']
      remark = request.form['remark']
      try:
        approval.status = status
        approval.remark = remark
        if status == True:
          # get approval below and set pastApproved to True or if on to set status to True of ticket itself
          if approval.level == approval.upto:
            approval.ticket.status = True
          else:
            nextLevel = level[level.index(approval.level) + 1]
            nextApproval = Approval.query.filter_by(
                ticket=approval.ticket, level=nextLevel).first()
            nextApproval.pastApproved = True
        db.session.commit()
      except Exception as e:
        db.session.rollback()
        return render_template('approve.html', ticket=approval.ticket, error="Error in approving ticket")
    else:
      comment = request.form['comment']
      try:
        comment = Comment(ticket=approval.ticket, user=user, text=comment)
        db.session.add(comment)
        db.session.commit()
        return redirect('/approve/' + id)
      except:
        db.session.rollback()
        return render_template('approve.html', ticket=ticket, error="Error in adding comment")
  comments = Comment.query.filter_by(ticket=id).all()
  return render_template('approve.html', approval=approval, comments=comments)


@views.route('/approve', methods=['GET', 'POST'])
@login_required(None)
def approve():
  user = session['user']
  if user["level"] in ["clubmember", "sec"]:
    return redirect('/tickets')
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')

  if user.level in ["csap", "dean"]:
    approvals = Approval.query.filter_by(
      level=user.level).all()
  elif user.level in ["sfa", "sec"]:
    clubs = Club.query.filter_by(society=user.society).all()
    club_ids = [club.id for club in clubs]
    approvals = Approval.query.filter(
        Approval.level == user.level, Approval.club.in_(club_ids)).all()
  elif user.level == "cfa":
    approvals = Approval.query.filter_by(
      level=user.level, club=user.club).all()
  return render_template('approve.html', approvals=approvals)


@views.route('/ticket/<id>', methods=['GET', 'POST'])
@login_required(["clubmember", "sec"])
def ticket(id):
  user = session['user']
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')
  if user.level == "sec":
    clubs = Club.query.filter_by(society=user.society).all()
  else:
    clubs = [user.club]
  ticket = Ticket.query.filter_by(id=id).first()

  if ticket == None or (ticket.club.id not in [club.id for club in clubs]):
    return redirect('/tickets')

  if request.method == 'POST':
    text = request.form['comment']
    try:
      comment = Comment(ticket=ticket, user=user, text=text)
      db.session.add(comment)
      db.session.commit()
      return redirect('/ticket/' + id)
    except:
      db.session.rollback()
      return render_template('ticket.html', ticket=ticket, error="Error in adding comment")
  return render_template('ticket.html', ticket=ticket)


@views.route('/tickets', methods=['GET', 'POST'])
@login_required(["clubmember", "sec"])
def tickets():
  user = session['user']
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')
  if user.level == "clubmember":
    society = user.club.society
  else:
    society = Society.query.filter_by(fa=user.id).first()

  if request.method == 'POST':

    amount = request.form['amount']
    info = request.form['info']
    priority = request.form['priority']

    if user.level == "sec":
      club = request.form['club']
      club = Club.query.filter_by(id=club).first()
    else:
      club = user.club
    approvalsFrom = getApproval(amount, society.budgetUsed)
    try:
      ticket = Ticket(club=club, amount=amount,
                      info=info, priority=priority)
      db.session.add(ticket)
      if user.level == "sec":
        approvalsFrom.remove("sec")
      for approvalBy in approvalsFrom:
        approvals = Approval(ticket=ticket, status=False,
                             level=approvalBy, club=club, upto=approvalsFrom[-1])
        db.session.add(approvals)

      db.session.commit()
    except Exception as e:
      db.session.rollback()
    return redirect('/tickets')

  if user.level == "sec":
    clubs = Club.query.filter_by(society=society).all()
    club_ids = [club.id for club in clubs]
    tickets = Ticket.query.filter(Ticket.club.in_(club_ids)).all()
  else:
    tickets = Ticket.query.filter_by(club=user.club).all()
  return render_template('tickets.html', tickets=tickets)


@views.route('/admin/approve-user', methods=['GET', 'POST'])
@login_required("admin")
def approveUser():
  user = session['user']
  if request.method == 'POST':
    try:
      user_id = request.form['id']
      user = User.query.filter_by(id=user_id).first()
      user.approved = True
      db.session.commit()
    except Exception as e:
      db.session.rollback()
    return redirect('/admin/approve-user')

  users = User.query.filter_by(approved=False).all()
  return render_template('approve-user.html', users=users)
