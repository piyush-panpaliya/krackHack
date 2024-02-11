from . import db
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from . import login_required
from .models import User, Comment, Club, Society, Approval, Ticket
from .forms import TicketForm, ApprovalForm, CommentForm

from dotenv import load_dotenv
load_dotenv()

level = ["clubmember", "sec", "cfa", "sfa", "csap", "dean"]


def getApproval(amount, budgetUsed):
  if amount < 15000 and 15000 - budgetUsed >= amount:
    return ["sec", "sfa", "cfa"]
  elif amount < 50000 or 15000 - budgetUsed < amount:
    return ["sec", "cfa", "sfa", "csap"]
  return ["sec", "cfa", "sfa", "csap", "dean"]


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
  # societies = ["sntc", "cult"]
  # Tclubs = ["kp", "gdsc", "saic"]
  # Cclubs = ["drama", "dance", "music"]
  # for s in societies:
  #   society = Society(name=s, budgetUsed=0)
  #   db.session.add(society)
  # db.session.commit()
  # sntc = Society.query.filter_by(name="sntc").first()
  # cult = Society.query.filter_by(name="cult").first()
  # for c in Tclubs:
  #   club = Club(name=c, society_id=sntc.id)
  #   db.session.add(club)
  #   # sntc.clubs.append(club)
  # for c in Cclubs:
  #   club = Club(name=c, society_id=cult.id)
  #   db.session.add(club)
  #   # cult.clubs.append(club)
  # db.session.commit()
  # return ""
  if not session.get('user', None):
    clubs = Club.query.all()
    societies = Society.query.all()
    return render_template('index.html', stylesheet=url_for('static', filename='style.css'), clubs=clubs, societies=societies)
  print(session['user'])
  if session["user"]["level"] in ["clubmember", "sec"]:
    return redirect('/tickets')
  return redirect(url_for('views.approve'))


@views.route('/approve/<id>', methods=['GET', 'POST'])
@login_required(None)
def approveTicket(id):
  user = session['user']
  if user["level"] in ["clubmember"]:
    return redirect('/tickets')
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')

  approval = Approval.query.filter_by(ticket_id=id, level=user.level).first()
  print(approval)
  if not approval or approval.level != user.level:
    return redirect('/approve')
  noSubmit = False
  if approval.remark and approval.remark.split(":")[0] in ["ACCEPTED", "DECLINED"]:
    noSubmit = True
  form = ApprovalForm()

  commentform = CommentForm()
  if request.method == 'POST' and commentform.is_submitted() and commentform.data["comment_btn"]:
    print(commentform.data, "cmnt formmmmm")
    comment = commentform.data["comments"]
    try:
      comment = Comment(ticket=approval.ticket, user=user, text=comment)
      db.session.add(comment)
      db.session.commit()
      return redirect("/approve/" + str(approval.ticket_id))
    except:
      db.session.rollback()
      return render_template('approve.html', approval=ticket, error="Error in adding comment")

  if request.method == "POST" and form.is_submitted():
    if not approval.pastApproved:
      return render_template('approve.html', form=form, approval=approval, error="Ticket not approved at lower level")
    status = form.data["accept"]
    remark = form.data["remark"]
    try:
      approval.status = status
      ticket = Ticket.query.filter_by(id=id).first()
      if status == True:
        approval.remark = 'ACCEPTED: ' + remark
        ticket.remark = "approved by " + user.level
        if approval.level == approval.upto:
          approval.ticket.status = True
        else:
          nextLevel = level[level.index(approval.level) + 1]
          nextApproval = Approval.query.filter_by(
              ticket=approval.ticket, level=nextLevel).first()
          nextApproval.pastApproved = True
      else:
        approval.remark = 'DECLINED: ' + remark
        ticket.remark = "declined by" + user.level

      db.session.commit()
    except Exception as e:
      db.session.rollback()
      print(e)
      return render_template('approve.html', approval=approval, error="Error in approving ticket")
    return redirect("/approve/" + str(approval.ticket_id))

  comments = Comment.query.filter_by(ticket_id=id).all()
  return render_template('approve.html', approval=approval, comments=comments, noSubmit=noSubmit, form=form, form2=commentform, stylesheet=url_for('static', filename='approval.css'))


@views.route('/approve', methods=['GET', 'POST'])
# @login_required(None)
def approve():
  user = session['user']
  if user["level"] in ["clubmember"]:
    return redirect('/tickets')
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')
  if user.level in ["csap", "dean"]:
    approvals = Approval.query.filter_by(
      level=user.level).all()
  elif user.level in ["sfa", "sec"]:
    clubs = Club.query.filter_by(society_id=user.society_id).all()
    club_ids = [club.id for club in clubs]
    approvals = Approval.query.filter(
        Approval.level == user.level, Approval.club_id.in_(club_ids)).all()
  elif user.level == "cfa":
    approvals = Approval.query.filter_by(
      level=user.level, club=user.club).all()
  print(approvals)
  return render_template('approvals.html', approvals=approvals)


@views.route('/ticket/<id>', methods=['GET', 'POST'])
# @login_required(["sec", "clubmember"])
def ticket(id):
  user = session['user']
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')
  if user.level == "sec":
    clubs = Club.query.filter_by(society_id=user.society_id).all()
  else:
    clubs = [user.club]
  ticket = Ticket.query.filter_by(id=id).first()
  if ticket == None or (ticket.club_id not in [club.id for club in clubs]):
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
  comments = Comment.query.filter_by(ticket_id=id).all()

  return render_template('ticket.html', ticket=ticket, stylesheet=url_for('static', filename='status.css'), comments=comments)


@views.route('/tickets', methods=['GET', 'POST'])
# @login_required(["clubmember", "sec"])
def tickets():
  if not session.get('user', None) or session['user']['level'] not in ["clubmember", "sec"]:
    return redirect('/')
  user = session['user']
  user = User.query.filter_by(id=user["id"]).first()
  if not user:
    return redirect('/logout')
  if user.level == "clubmember":
    club = Club.query.filter_by(id=user.club_id).first()
    society = Society.query.filter_by(id=club.society_id).first()
  else:
    society = Society.query.filter_by(id=user.society_id).first()
  form = TicketForm()
  if request.method == "POST" and form.is_submitted():
    amount = form.amount.data
    info = form.info.data
    priority = form.priority.data
    if user.level == "sec":
      club = form.club.data
      club = Club.query.filter_by(id=club).first()
    else:
      club = user.club
    approvalsFrom = getApproval(amount, society.budgetUsed)
    try:
      ticket = Ticket(club=club, amount=amount, status=False, remark="",
                      info=info, priority=priority)
      db.session.add(ticket)
      if user.level == "sec":
        approvals = Approval(ticket=ticket, status=False,
                             level="sec", club=club, upto=approvalsFrom[-1], pastApproved=True, remark="ACCEPTED: Approved by sec")
        ticket.remark = "ACCEPTED: Approved by sec"
        approvalsFrom.remove("sec")
      for approvalBy in approvalsFrom:
        approvals = Approval(ticket=ticket, status=False,
                             level=approvalBy, club=club, upto=approvalsFrom[-1], pastApproved=approvalsFrom.index(approvalBy) == 0)
        db.session.add(approvals)

      db.session.commit()
    except Exception as e:
      print(e)
      db.session.rollback()
    return redirect('/tickets')
  if user.level == "sec":
    clubs = Club.query.filter_by(society_id=society.id).all()
    club_ids = [club.id for club in clubs]
    tickets = Ticket.query.filter(Ticket.club_id.in_(club_ids)).all()
    clubs = Club.query.all()
    club_choices = [(str(club.id), club.name) for club in clubs]
    form.club.choices = club_choices
  else:
    tickets = Ticket.query.filter_by(club_id=user.club_id).all()
    del form.club

  return render_template('tickets.html', tickets=tickets, form=form, stylesheet=url_for('static', filename='ticket.css'), sec=(user.level == "sec"))


@views.route('/admin/approve-user', methods=['GET', 'POST'])
@login_required(["admin"])
def approveUser():
  user = session['user']
  user = User.query.filter_by(id=user["id"]).first()
  user.approved = True
  if request.method == 'POST' and user.level == "admin":
    try:
      user_id = request.form['id']
      approve = request.form['approved'] == 'true'
      user = User.query.filter_by(id=user_id).first()
      user.approved = approve
      db.session.commit()
    except Exception as e:
      print(e)
      db.session.rollback()
    return redirect('/admin/approve-user')

  users = User.query.filter(User.approved == False,
                            User.level != 'admin').all()
  return render_template('approve-user.html', users=users)
