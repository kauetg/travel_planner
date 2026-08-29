from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from bson import ObjectId
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


class User(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.email = doc["email"]
        self.name = doc.get("name", "")


@login_manager.user_loader
def load_user(user_id):
    db = current_app.db
    doc = db.users.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = current_app.db
        doc = db.users.find_one({"email": email})

        if doc and check_password_hash(doc["password_hash"], password):
            login_user(User(doc), remember=True)
            return redirect(url_for("home.index"))

        flash("Invalid email or password.")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
