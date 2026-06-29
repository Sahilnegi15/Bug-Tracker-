from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt


app = Flask(__name__, template_folder="templates")


app.config["SECRET_KEY"] = "you"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugtracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------
# Models
# ----------------------

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    severity = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Open")

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id")
    )


bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="Tester"
    )



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ----------------------
# Routes
# ----------------------

@app.route("/")
@login_required
def dashboard():

    project_count = Project.query.count()
    bug_count = Bug.query.count()

    open_bugs = Bug.query.filter_by(
        status="Open"
    ).count()

    return render_template(
        "dashboard.html",
        projects=project_count,
        bugs=bug_count,
        open_bugs=open_bugs
    )

@app.route("/projects")
def projects():

    all_projects = Project.query.all()

    return render_template(
        "projects.html",
        projects=all_projects
    )

@app.route("/project/add", methods=["GET", "POST"])
def add_project():

    if request.method == "POST":

        project = Project(
            name=request.form["name"],
            description=request.form["description"]
        )

        db.session.add(project)
        db.session.commit()

        return redirect(url_for("projects"))

    return render_template("add_project.html")

@app.route("/bugs")
def bugs():

    all_bugs = Bug.query.all()

    return render_template(
        "bugs.html",
        bugs=all_bugs
    )

@app.route("/bug/add", methods=["GET", "POST"])
def add_bug():

    projects = Project.query.all()

    if request.method == "POST":

        bug = Bug(
            title=request.form["title"],
            description=request.form["description"],
            severity=request.form["severity"],
            project_id=request.form["project_id"]
        )

        db.session.add(bug)
        db.session.commit()

        return redirect(url_for("bugs"))

    return render_template(
        "add_bug.html",
        projects=projects
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        hashed_password = bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password_hash=hashed_password,
            role="Tester"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if user and bcrypt.check_password_hash(
            user.password_hash,
            request.form["password"]
        ):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))




if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)