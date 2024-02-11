from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from .models import Club


class TicketForm(FlaskForm):
  info = StringField('Information', validators=[
      DataRequired()])
  amount = IntegerField('Amount', validators=[
      DataRequired()])
  priority = SelectField('Priority', choices=[
                         ('1', '1'), ('2', '2'), ('3', '3')])
  file = FileField('Choose a File')
  club = SelectField('Club', choices=[])
  submit = SubmitField('Submit')


class ApprovalForm(FlaskForm):
  remark = StringField('Remark')
  accept = SubmitField('Accept')
  decline = SubmitField('Decline')
  comments = StringField('Comments')
  comment_btn = SubmitField('Comment')


class PromoteForm(FlaskForm):
  position = SelectField('Position',
                         choices=[('clubmember', 'Member'), ('cfa', 'Club FA'), ('sfa', 'Society FA'), ('secretary', 'Secretary'), ('chairsap', 'ChairSAP'), ('deanstudents', 'Dean Students')])
  submit = SubmitField('Promote')


class MemberApproveForm(FlaskForm):
  accept = SubmitField('Accept')
  decline = SubmitField('Decline')
