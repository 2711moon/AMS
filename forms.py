from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Length

class CSRFOnlyForm(FlaskForm):
    pass

class LoginForm(FlaskForm):
    identifier = StringField('Username', validators=[DataRequired()])
    passcode = PasswordField('Password', validators=[DataRequired()])

class AssetForm(FlaskForm):
    category = SelectField('Asset Type', choices=[], validators=[DataRequired()])
    new_type = StringField('Add New Type', validators=[Optional(), Length(max=50)])

    status = SelectField('Status', choices=[
        ('available(p)', 'Available(p)'),
        ('available(g)', 'Available(g)'),
        ('assigned(p)', 'Assigned(p)'),
        ('assigned(g)', 'Assigned(g)'),
        ('repair/faulty', 'Repair/Faulty'),
        ('discard', 'Discard')
    ], validators=[DataRequired()])

    remarks = StringField('Remarks', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save')
