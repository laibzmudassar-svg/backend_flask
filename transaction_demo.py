from app import app
from extensions import db
from models.user_model import User

with app.app_context():
    try:
        # Start an explicit transaction
        new_user = User(name="Rollback Test", email="rollback@example.com", password_hash="fake")
        db.session.add(new_user)

        # Simulate a failure mid-transaction
        raise Exception("Simulated failure before commit")

        db.session.commit()  # never reached
    except Exception as e:
        db.session.rollback()
        print(f"Transaction rolled back due to: {e}")

    # Verify the user was NOT actually saved
    check = User.query.filter_by(email="rollback@example.com").first()
    print(f"User exists after rollback? {check is not None}")