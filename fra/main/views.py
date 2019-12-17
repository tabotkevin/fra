from flask import render_template, redirect, url_for, abort, flash, request, g, jsonify
from flask_login import login_required, current_user
from . import main
from .. import lm


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@main.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('admin.welcome'))
