from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    TextField, PasswordField,
    IntegerField, BooleanField, SelectField,
    SubmitField
)
from wtforms.validators import (
    Required, EqualTo, ValidationError,
    IPAddress, Length, NumberRange
)

from netui.models import User


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])


class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password', validators=[Required()])
    new_password = PasswordField('New Password', validators=[Required()])
    repeat_password = PasswordField(
        'Repeat New Passowrd',
        validators=[
            Required(), EqualTo(
                'new_password', message="Your passwords do not match"
            )
        ]
    )

    def __init__(self, **kwargs):
        super(ChangePasswordForm, self).__init__(**kwargs)
        self.user = kwargs['user']

    def validate_old_password(self, field):
        if not self.user.check_password(field.data):
            raise ValidationError('incorrect old password')


class NetworkForm(Form):
    ip_addr = TextField('IP address: ', validators=[
        Required(), IPAddress(message='wrong IPv4 format')])
    subnet_mask = TextField('Subnet mask: ', validators=[
        Required(), IPAddress(message='wrong IPv4 format')])
    gateway = TextField('Gateway: ', validators=[
        Required(), IPAddress(message='wrong IPv4 format')])
    dns = TextField('DNS: ', validators=[
        Required(), IPAddress(message='wrong IPv4 format')])
    dynamic = BooleanField('DHCP? ', default=True)
    submit = SubmitField(u'Modify')


class APListForm(Form):
    ssid = TextField('SSID: ', validators=[Required()])
    security = SelectField('Security: ', choices=[
        ('Public', 'Public'),
        ('WEP', 'WEP'),
        ('WPA', 'WPA')]
    )
    psk = TextField('PSK: ')
    priority = IntegerField('Priority: ', validators=[NumberRange(0, 255)])


class SQLiteFileForm(Form):
    db_file = FileField(
            'Database file: ', validators=[
            FileRequired(),
            FileAllowed(['sqlite'], 'SQLite3 format')
        ])


class DummyForm(Form):
    pass
