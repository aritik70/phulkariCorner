from app import app  # noqa: F401
from routes import *  # noqa: F401

# Initialize admin user and sample data
with app.app_context():
    from routes import create_admin_user
    create_admin_user()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
