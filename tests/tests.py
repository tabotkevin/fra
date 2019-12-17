#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from fra import app, db
from fra.models import User, Feature, Client, ProductArea, Role, Permission
from flask import url_for
import json


class TestCase(unittest.TestCase):
    default_admin_email = 'admin@iws.com'
    default_user_email = 'user@iws.com'
    default_password = 'password'

    def setUp(self):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing.sqlite'
        self.app.config['SERVER_NAME'] = 'localhost:5000'
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_password_hashing(self):
        u = User(email=self.default_user_email, password=self.default_password)
        self.assertFalse(u.verify_password('dog'))
        self.assertTrue(u.verify_password('password'))

    def test_user_roles(self):
        admin_role = Role(name='Administrator',
                          permissions=Permission.ADMINISTER, default=False)
        user_role = Role(
            name='User', permissions=Permission.USER, default=True)

        db.session.add_all([admin_role, user_role])
        db.session.commit()

        admin = User(email=self.default_user_email,
                     password=self.default_password, role=admin_role)
        user = User(email=self.default_admin_email,
                    password=self.default_password, role=user_role)

        db.session.add_all([admin, user])
        db.session.commit()

        self.assertEqual(admin.role.name, 'Administrator')
        self.assertEqual(user.role.name, 'User')
        self.assertEqual(admin.role.permissions, 0x80)
        self.assertEqual(user.role.permissions, 0x02)

    def test_user_confirmed_allowed(self):
        u1 = User(first_name='John', email='john@example.com',
                  password='password', confirmed=True, allowed=False)
        u2 = User(first_name='Susan', email='susan@example.com',
                  password='password', confirmed=False, allowed=True)
        u3 = User(first_name='Mary', email='mary@example.com',
                  password='password', confirmed=True, allowed=True)

        self.assertTrue(u1.confirmed)
        self.assertFalse(u1.allowed)
        self.assertFalse(u2.confirmed)
        self.assertTrue(u2.allowed)
        self.assertTrue(u3.confirmed)
        self.assertTrue(u3.allowed)

    def test_users_features(self):
        # create two users
        u1 = User(first_name='John', email='john@example.com',
                  password='password')
        u2 = User(first_name='Susan', email='susan@example.com',
                  password='password')
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertEqual(u1.features.all(), [])
        self.assertEqual(u2.features.all(), [])
        self.assertEqual(u1.features.count(), 0)
        self.assertEqual(u1.first_name, 'John')
        self.assertEqual(u2.features.count(), 0)
        self.assertEqual(u2.first_name, 'Susan')

        # create two clients
        c1 = Client(name='Client A')
        c2 = Client(name='Client B')
        db.session.add_all([c1, c2])
        # create two product area
        p1 = ProductArea(name='Policies')
        p2 = ProductArea(name='Billing')
        db.session.add_all([p1, p2])

        # create four features
        now = datetime.utcnow()
        f1 = Feature(title="feature 1", description='description 1', priority=1, target_date=now + timedelta(
            seconds=1), product_area=p1, client=c1, user=u1, created_on=now + timedelta(seconds=1))
        f2 = Feature(title="feature 2", description='description 2', priority=2, target_date=now + timedelta(
            seconds=2), product_area=p1, client=c1, user=u1, created_on=now + timedelta(seconds=2))
        f3 = Feature(title="feature 3", description='description 3', priority=1, target_date=now + timedelta(
            seconds=3), product_area=p2, client=c2, user=u2, created_on=now + timedelta(seconds=3))
        f4 = Feature(title="feature 4", description='description 4', priority=2, target_date=now + timedelta(
            seconds=4), product_area=p2, client=c2, user=u2, created_on=now + timedelta(seconds=4))
        db.session.add_all([f1, f2, f3, f4])
        db.session.commit()

        self.assertEqual(u1.features.count(), 2)
        self.assertEqual(u1.features.first().title, 'feature 1')
        self.assertEqual(f1.client.name, 'Client A')
        self.assertEqual(f1.product_area.name, 'Policies')
        self.assertEqual(f1.priority, 1)

        self.assertEqual(u2.features.count(), 2)
        self.assertEqual(u2.features.first().title, 'feature 3')
        self.assertEqual(f3.client.name, 'Client B')
        self.assertEqual(f4.priority, 2)

    def test_auth_routes(self):
        u1 = User(first_name='John', email='john@example.com',
                  password='password')
        login_data = {
            'email': 'john@example.com',
            'password': 'password',
            'csrf_token': '1557881955##4875390aa66d1776fd18b9155d9865300afeeea6'
        }

        reg_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '+23487548332',
            'email': 'john@example.com',
            'password': 'password',
            'password2': 'password',
            'csrf_token': '1557881732##878f9ae73802b1081c5269ee0c9372607820ef2f'

        }

        login_get = self.client.get(url_for('auth.login'))
        self.assertEquals(login_get.status_code, 200)
        register_get = self.client.get(url_for('auth.register'))
        self.assertEquals(register_get.status_code, 200)
        logout_get = self.client.get(url_for('auth.logout'))
        self.assertEquals(logout_get.status_code, 302)
        unconfirmed_get = self.client.get(url_for('auth.unconfirmed'))
        self.assertEquals(unconfirmed_get.status_code, 302)
        unallowed_get = self.client.get(url_for('auth.unallowed'))
        self.assertEquals(unallowed_get.status_code, 302)
        confirm_get = self.client.get(url_for('auth.resend_confirmation'))
        self.assertEquals(confirm_get.status_code, 302)
        confirm_token_get = self.client.get(
            url_for('auth.confirm', token='fake-token'))
        self.assertEquals(confirm_token_get.status_code, 302)
        change_password_get = self.client.get(
            url_for('auth.change_password'))
        self.assertEquals(change_password_get.status_code, 302)
        password_reset_request_get = self.client.get(
            url_for('auth.password_reset_request'))
        self.assertEquals(password_reset_request_get.status_code, 200)
        password_reset_get = self.client.get(
            url_for('auth.password_reset', token='fake-token'))
        self.assertEquals(password_reset_get.status_code, 200)
        change_email_request_get = self.client.get(
            url_for('auth.change_email_request'))
        self.assertEquals(change_email_request_get.status_code, 302)
        change_email_get = self.client.get(
            url_for('auth.change_email', token='fake-token'))
        self.assertEquals(change_email_get.status_code, 302)

        login = self.client.post(
            url_for('auth.login'), data=login_data, follow_redirects=True)
        self.assertEquals(login.status_code, 200)

        register = self.client.post(
            url_for('auth.register'), data=reg_data, follow_redirects=True)
        self.assertEquals(login.status_code, 200)

    def test_main_routes(self):
        home_get = self.client.get(url_for('main.home'))
        self.assertEquals(home_get.status_code, 302)

    def test_admin_routes(self):
        home_get = self.client.get(url_for('admin.home'))
        self.assertEquals(home_get.status_code, 403)
        welcome_get = self.client.get(url_for('admin.welcome'))
        self.assertEquals(welcome_get.status_code, 302)
        features_get = self.client.get(url_for('admin.features'))
        self.assertEquals(features_get.status_code, 302)
        create_user_get = self.client.get(url_for('admin.create_user'))
        self.assertEquals(home_get.status_code, 403)
        users_get = self.client.get(url_for('admin.users'))
        self.assertEquals(users_get.status_code, 403)
        edit_user_get = self.client.get(url_for('admin.edit_user', id=1))
        self.assertEquals(features_get.status_code, 302)
        delete_user_get = self.client.get(url_for('admin.delete_user', id=1))
        self.assertEquals(delete_user_get.status_code, 403)
        create_feature_get = self.client.get(url_for('admin.create_feature'))
        self.assertEquals(create_feature_get.status_code, 302)
        edit_feature_get = self.client.get(url_for('admin.edit_feature', id=1))
        self.assertEquals(edit_feature_get.status_code, 302)
        delete_feature_get = self.client.get(
            url_for('admin.delete_feature', id=1))
        self.assertEquals(delete_feature_get.status_code, 302)


if __name__ == '__main__':
    unittest.main(verbosity=2)
