from . import db
from datetime import datetime


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  oauth_id = db.Column(db.String(50), unique=True, nullable=False)
  level = db.Column(db.String(100), nullable=False)
  approved = db.Column(db.Boolean, default=False, nullable=False)

  comments = db.relationship('Comment', backref='user')
  club_id = db.Column(db.BigInteger, db.ForeignKey('club.id'), nullable=True)
  society_id = db.Column(db.BigInteger, db.ForeignKey(
      'society.id'), nullable=True)
  society = db.relationship('Society', backref='user',
                            uselist=True, foreign_keys=[society_id])

  def __repr__(self):
    return f"<User id:{self.id} email:{self.email} level:{self.level} approved:{self.approved}... member of: {self.memberOf}>"


class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
  text = db.Column(db.String(2000), nullable=False)
  date_updated = db.Column(db.DateTime, default=datetime.utcnow)

  ticket_id = db.Column(db.BigInteger, db.ForeignKey(
      'ticket.id'), nullable=False)

  def __repr__(self):
    return f"<Comment id:{self.id} user:{self.user} ticket:{self.ticket}... date created: {self.date_created}>"

# tickets done


class Ticket(db.Model):
  id = db.Column(db.BigInteger, primary_key=True)
  priority = db.Column(db.Integer, nullable=False)
  amount = db.Column(db.BigInteger, nullable=False, default=0)
  approvals = db.relationship('Approval', backref='ticket')
  status = db.Column(db.Integer, nullable=False)
  remark = db.Column(db.String(2000), nullable=False)
  info = db.Column(db.String(2000), nullable=False)

  club_id = db.Column(db.BigInteger, db.ForeignKey('club.id'), nullable=False)
  Comments = db.relationship('Comment', backref='ticket')

# clubs done


class Club(db.Model):
  id = db.Column(db.BigInteger, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  society_id = db.Column(db.BigInteger, db.ForeignKey(
    "society.id"), nullable=True)

  tickets = db.relationship('Ticket', backref='club')
  approvals = db.relationship('Approval', backref='club')
  secretary_id = db.Column(
      db.BigInteger, db.ForeignKey('user.id'), nullable=False)
  members = db.relationship('User', backref='club',
                            foreign_keys='User.club_id')

  def __repr__(self):
    return f"<Club id:{self.id} name:{self.name} level:{self.level} approved:{self.approved}... members: {self.members}>"

# society done


class Society(db.Model):
  id = db.Column(db.BigInteger, primary_key=True)
  clubs = db.relationship('Club', backref='society')
  name = db.Column(db.String(100), nullable=False)
  budgetUsed = db.Column(db.BigInteger, nullable=False)

# approvals done


class Approval(db.Model):
  id = db.Column(db.BigInteger, primary_key=True)
  status = db.Column(db.Boolean, default=False, nullable=False)
  remark = db.Column(db.String(2000), nullable=False, default="")
  pastApproved = db.Column(db.Boolean, default=False, nullable=False)
  level = db.Column(db.String(100), nullable=False)
  upto = db.Column(db.String(100), nullable=False)
  club_id = db.Column(db.BigInteger, db.ForeignKey(
      'club.id'), nullable=False)
  ticket_id = db.Column(db.BigInteger, db.ForeignKey(
      'ticket.id'), nullable=False)

  def __repr__(self):
    return f"<Approval id:{self.id} ticket:{self.ticket} status:{self.status}... level: {self.level} pastApproved: {self.pastApproved}>"
