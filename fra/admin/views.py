from flask import render_template, redirect, url_for, abort, flash, request, g, jsonify
from flask_login import login_required, current_user
from .. import lm, app
from . import admin
from .forms import UserForm, FeatureForm
from .. import db
from ..models import User, Role, Client, Feature, ProductArea
from werkzeug.utils import secure_filename
from ..decorators import admin_required
from datetime import datetime
import os
import json


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@admin.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    return redirect(url_for('admin.welcome'))


@admin.route('/welcome')
@login_required
def welcome():
    return render_template('admin/index.html')


@admin.route('/create_user', methods=['GET', 'POST'])
@admin_required
@login_required
def create_user():
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        phone = form.phone.data
        image = form.image.data
        if image:
            image = str(secure_filename(image.filename))
            date = "{:%I%M%S%f%d%m%Y}".format(datetime.now())
            image = date + image
            form.image.data.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'users/' + image))
        role = Role.query.get(int(form.role.data))
        confirmed = form.confirmed.data
        allowed = form.allowed.data
        user = User(first_name=first_name, last_name=last_name, email=email,  role=role,
                    phone=phone, password=password, confirmed=confirmed, allowed=allowed)
        user.set_image(image)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('admin.users'))
    return render_template('admin/create_user.html', form=form)


@admin.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    query = User.query
    pagination = query.order_by(User.created_on.desc()).paginate(
        page, per_page=20, error_out=False)
    users = pagination.items
    return render_template('admin/users.html', users=users, pagination=pagination)


@admin.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        password = form.password.data
        user.phone = form.phone.data
        user.confirmed = form.confirmed.data
        user.allowed = form.allowed.data
        image = form.image.data
        if image:
            image = str(secure_filename(image.filename))
            date = "{:%I%M%S%f%d%m%Y}".format(datetime.now())
            image = date + image
            form.image.data.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'users/' + image))
            user.set_image(image)
        user.role = Role.query.get(int(form.role.data))
        if password:
            user.password = password
        db.session.add(user)
        db.session.commit()
        flash('User Edited successfully')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', form=form, user=user)


@admin.route('/delete_user/<int:id>')
@admin_required
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('admin.users'))


@admin.route('/create_feature', methods=['GET', 'POST'])
@login_required
def create_feature():
    form = FeatureForm()
    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        target_date = form.target_date.data
        product_area = ProductArea.query.get(int(form.product_area.data))
        priority = int(form.priority.data)
        client = Client.query.get(int(form.client.data))

        if Feature.priority_exists(client, priority):
            Feature.adjust_priorities(client, priority)
        feature = Feature(title=title, description=description, target_date=target_date,
                          product_area=product_area, priority=priority,  client=client, user=current_user)
        db.session.add(feature)
        db.session.commit()
        flash('Feature created successfully')
        return redirect(url_for('admin.features'))
    return render_template('admin/create_feature.html', form=form)


@admin.route('/edit_feature/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_feature(id):
    feature = Feature.query.get_or_404(id)
    if current_user.role.name != 'Administrator' and current_user != feature.user:
        flash('You do not have permision to edit this feaature')
        return redirect(url_for('admin.features'))
    form = FeatureForm(obj=feature)
    if request.method == 'POST' and form.validate_on_submit():
        client = Client.query.get(int(form.client.data))
        priority = int(form.priority.data)
        if Feature.priority_exists(client, priority):
            Feature.adjust_priorities(client, priority)
        feature.title = form.title.data
        feature.description = form.description.data
        feature.target_date = form.target_date.data
        feature.product_area = ProductArea.query.get(
            int(form.product_area.data))
        feature.priority = priority
        feature.client = client
        db.session.add(feature)
        db.session.commit()
        flash('Feature updated successfully')
        return redirect(url_for('admin.features'))
    return render_template('admin/edit_feature.html', form=form, feature=feature)


@admin.route('/features')
@login_required
def features():
    page = request.args.get('page', 1, type=int)
    query = Feature.query
    pagination = None
    if current_user.role.name == 'Administrator':
        pagination = query.order_by(Feature.created_on.desc()).paginate(
            page, per_page=20, error_out=False)
    else:
        pagination = query.filter_by(user=current_user).order_by(Feature.created_on.desc()).paginate(
            page, per_page=20, error_out=False)
    features = pagination.items
    return render_template('admin/features.html', features=features, pagination=pagination)


@admin.route('/delete_feature/<int:id>')
@login_required
def delete_feature(id):
    feature = Feature.query.get_or_404(id)
    if current_user.role.name == 'Administrator' or current_user == feature.user:
        db.session.delete(feature)
        db.session.commit()
        flash("Feature deleted successfully")
    else:
        flash("You do not have permision to delete this feaature")
    return redirect(url_for('admin.features'))
