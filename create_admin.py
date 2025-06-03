from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if admin:
        print("Admin user already exists!")
    else:
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password("adminpassword")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")