from fra import app, db
from fra.models import User, Role, Client, ProductArea

with app.app_context():
    Role.insert_roles()
    Client.insert_clients()
    ProductArea.insert_product_areas()
    admin_role = Role.query.filter_by(name='Administrator').first()
    user_role = Role.query.filter_by(name='User').first()
    admin_user = User(first_name='Administrator', last_name='Iws', email='admin@iws.com', phone='+237674886850', password='password',
                      image='default.jpg', role=admin_role, confirmed=True, allowed=True)
    normal_user = User(first_name='User', last_name='Iws', email='user@iws.com', phone='+237674886850', password='password',
                       image='default.jpg', role=user_role)
    db.session.add_all([admin_user, normal_user])
    db.session.commit()
