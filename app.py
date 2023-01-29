import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dudu.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show homepage"""

    user = session.get("user_id")


    if request.method == "POST":

        # Get list of lists
        lists = db.execute("SELECT DISTINCT list FROM todo WHERE user_id = ?", user)

        # If user clicks on a list
        list = request.form.get("list")
        if list:

            tasks = db.execute("SELECT * FROM todo WHERE user_id = ? AND list = ?", user, list)
            count = (db.execute("SELECT COUNT(*) FROM todo WHERE user_id = ? AND list = ? AND done = False", user, list))[0]["COUNT(*)"]

            return render_template("list.html", lists=lists, tasks=tasks, list=list, count=count)

        # If user checks checkbox
        done = request.form.get("done")
        if done:

            # Set task to done if task is not done
            test = db.execute("SELECT * FROM todo WHERE name_id = ?", done)
            if test[0]["done"] == False:
                db.execute("UPDATE todo SET done=True WHERE name_id = ?", done)

            # Set task to not done if task is done
            else:
                db.execute("UPDATE todo SET done=FALSE WHERE name_id = ?", done)

            list = (db.execute("SELECT list FROM todo WHERE name_id = ?", done))[0]["list"]
            tasks = db.execute("SELECT * FROM todo WHERE user_id = ? AND list = ?", user, list)
            count = db.execute("SELECT COUNT(*) FROM todo WHERE user_id = ? AND list = ? AND done = False", user, list)[0]["COUNT(*)"]

            # Return page with list previously opened
            return render_template("list.html", lists=lists, tasks=tasks, list=list, count=count)

        delete = request.form.get("delete")
        if delete:

            # Get info for page before deleting
            list = (db.execute("SELECT list FROM todo WHERE name_id = ?", delete))[0]["list"]
            tasks = db.execute("SELECT * FROM todo WHERE user_id = ? AND list = ? AND NOT name_id = ?", user, list, delete)

            # Delete task from db
            db.execute("DELETE FROM todo WHERE name_id = ?", delete)

            count = db.execute("SELECT COUNT(*) FROM todo WHERE user_id = ? AND list = ? AND done = False", user, list)[0]["COUNT(*)"]
            display = db.execute("SELECT COUNT(*) FROM todo WHERE user_id = ? AND list = ?", user, list)[0]["COUNT(*)"]

            if display != 0:
                # Return page with list previously opened
                return render_template("list.html", lists=lists, tasks=tasks, list=list, count=count)

                # If last task
            else:
                return redirect("/")

    else:

        lists = db.execute("SELECT DISTINCT list FROM todo WHERE user_id = ?", user)
        return render_template("index.html", lists=lists)


@app.route("/about")
def about():
    """Show info on website"""
    return render_template("about.html")


@app.route("/addlist", methods=["GET", "POST"])
def addlist():
    """Add new list of tasks"""

    user = session.get("user_id")
    list = request.form.get("list")
    name = request.form.get("name")
    due = request.form.get("due")

    if request.method == "POST":

        # Check if name of list is keyed in
        if not list:
            error = "Please input name of list"
            return render_template("addlist.html", error=error)

        # Check if list is already present
        row = db.execute("SELECT list FROM todo WHERE user_id = ? AND list = ?", user, list)
        if row == 0:
            error = "List is already present!"
            return render_template("addlist.html", error=error)

        # Check if name of task is keyed in
        if not name:
            error = "Please input name of task"
            return render_template("addlist.html", error=error)

        # Check if due date is keyed in
        elif not due:
            error = "Please select a due date"
            return render_template("addlist.html", error=error)

        # Add list and task into db
        db.execute("INSERT INTO todo (user_id, name, list, due) VALUES (?, ?, ?, ?)", user, name, list, due)

        return redirect("/")

    else:

        return render_template("addlist.html")


@app.route("/addtask", methods=["GET", "POST"])
def addtask():
    """Add task to current lists"""

    user = session.get("user_id")
    name = request.form.get("name")
    list = request.form.get("list")
    due = request.form.get("due")
    lists = db.execute("SELECT DISTINCT list FROM todo WHERE user_id = ?", user)

    if request.method == "POST":

        # Check if default list is not selected
        if list == "Current lists":
            error = "Please select a list"
            return render_template("addtask.html", error=error, lists=lists)

        # Check if task is keyed in
        elif not name:
            error = "Please input name of task"
            return render_template("addtask.html", error=error, lists=lists)

        # Check if date is keyed in
        elif not due:
            error = "Please select a due date"
            return render_template("addtask.html", error=error, lists=lists)

        # Add task to db
        db.execute("INSERT INTO todo (user_id, name, list, due) VALUES (?, ?, ?, ?)", user, name, list, due)

        return redirect("/")

    else:

        # Return list of lists for dropdown
        return render_template("addtask.html", lists=lists)


@app.route("/edituser", methods=["GET", "POST"])
def edituser():
    """Edit username"""

    if request.method == "POST":

        user = session.get("user_id")
        new = request.form.get("username")
        password = request.form.get("password")

        if not new:
            error = "Must provide new username"
            return render_template("edituser.html", error=error)

        if not password:
            error = "Must provide password"
            return render_template("edituser.html", error=error)

        # Check if password is correct
        rows = db.execute("SELECT * FROM users WHERE id = ?", user)
        if not check_password_hash(rows[0]["hash"], password):
            error = "Invalid password"
            return render_template("edituser.html", error=error)

        # Query database for new username
        rows = db.execute("SELECT * FROM users WHERE username = ?", new)

        # Ensure username exists
        if len(rows) != 0:
            error = "Username is not available"
            return render_template("edituser.html", error=error)

        db.execute("UPDATE users SET username=? WHERE id = ?", new, user)

        error = "Username updated!"
        return render_template("edituser.html", error=error)

    else:

        return render_template("edituser.html")


@app.route("/editpass", methods=["GET", "POST"])
def editpass():
    if request.method == "POST":

        new1 = request.form.get("password")
        new2 = request.form.get("confirmation")
        old = request.form.get("old")
        user = session.get("user_id")

        # Check if password is keyed in
        if not new1 or not new2 or not old:
            error = "Must provide password"
            return render_template("editpass.html", error=error)

        # Ensure password submitted is the same
        elif new1 != new2:
            error = "Passwords do not match"
            return render_template("editpass.html", error=error)

        # Check if password is correct
        rows = db.execute("SELECT * FROM users WHERE id = ?", user)
        if not check_password_hash(rows[0]["hash"], old):
            error = "Invalid password"
            return render_template("editpass.html", error=error)

        hash = generate_password_hash(new1, method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash=? WHERE id = ?", hash, user)

        # Success message
        error = "You successfully changed your password!"

        return render_template("editpass.html", error=error)

    else:

        return render_template("editpass.html")


@app.route("/delete", methods=["GET", "POST"])
def delete():
    """Delete account"""

    if request.method == "POST":

        user = session.get("user_id")

        # Check if password is keyed in
        if not request.form.get("password"):
            error = "Must provide password"
            return render_template("delete.html", error=error)

        # Check if password is correct
        rows = db.execute("SELECT * FROM users WHERE id = ?", user)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid password"
            return render_template("delete.html", error=error)

        # Delete all tasks
        db.execute("DELETE FROM todo WHERE user_id = ?", user)

        # Delete user
        db.execute("DELETE FROM users WHERE id = ?", user)

        # Logs user out
        session.clear()

        return redirect("/")

    else:

        return render_template("delete.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid username and/or password"
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'POST':

        # Ensure new username was submitted
        if not request.form.get("username"):
            error = "Must provide apology"
            return render_template("register.html", error=error)

        # Query database for new username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists
        if len(rows) != 0:
            error = "Username is not available"
            return render_template("register.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("register.html", error=error)

        elif not request.form.get("confirmation"):
            error = "Must provide password"
            return render_template("register.html", error=error)

        # Ensure password submitted is the same
        elif request.form.get("password") != request.form.get("confirmation"):
            error = "Passwords do not match"
            return render_template("register.html", error=error)

        # Add new user in users table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:

        return render_template("register.html")