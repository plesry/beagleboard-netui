from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from flask.ext.login import UserMixin

from netui import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(20))
    ip_addr = db.Column(db.String(20))
    subnet_mask = db.Column(db.String(20))
    gateway = db.Column(db.String(20))
    dns = db.Column(db.String(20))
    dynamic = db.Column(db.Boolean)

    def __init__(self, device, dynamic, ip_addr, subnet_mask, gateway, dns):
        self.device = device
        self.dynamic = dynamic
        self.ip_addr = ip_addr
        self.subnet_mask = subnet_mask
        self.gateway = gateway
        self.dns = dns

    def __repr__(self):
        return '<Interface %r>' % self.device


class APList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssid = db.Column(db.String(255))
    security = db.Column(db.String(255))
    psk = db.Column(db.String(255))
    priority = db.Column(db.Integer)

    def __init__(self, ssid, security, psk, priority):
        self.ssid = ssid
        self.security = security
        self.psk = psk
        self.priority = priority

    def __repr__(self):
        return '<WiFi_AP %r>' % self.ssid

    def _output_dict(self):
        d = dict()
        d['ssid'] = self.ssid
        d['type'] = self.security
        d['psk'] = self.psk
        d['priority'] = self.priority

        return d
