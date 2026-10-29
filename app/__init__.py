#===========================================================
# ChoreBuster
# By Ned Waite
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
import random
import string
from app.helpers import *

# Create the app
app = Flask(__name__)

#===========================================================
# App Routes Handlers
#===========================================================
#-----------------------------------------------------------
# Signup Page
#-----------------------------------------------------------
@app.get("/user/new")
def show_signup_form():
    return render_template("pages/user_form.jinja")

#-----------------------------------------------------------
# Family create Page
#-----------------------------------------------------------
@app.get("/family/create")
def show_signup_family_form():
    return render_template("pages/family_form.jinja")

#-----------------------------------------------------------
# Login Page
#-----------------------------------------------------------
@app.get("/user/login")
def show_login_form():
    return render_template("pages/login_page.jinja")

#-----------------------------------------------------------
# Join family page
#-----------------------------------------------------------
@app.get("/family/join")
@login_required
def show_join_family():
    return render_template("pages/join_family.jinja")

#-----------------------------------------------------------
# New Message Page
#-----------------------------------------------------------
@app.get("/chore/new")
def show_chores_form():
    return render_template("pages/chore_form.jinja")

#-----------------------------------------------------------
# Edit a Message Page
#-----------------------------------------------------------
@app.get("/chore/edit")
def edit_message_form():
    return render_template("pages/chore_edit.jinja")

#-----------------------------------------------------------
# Handle user signup
#-----------------------------------------------------------
@app.post("/user")
def add_user():
    forename = request.form.get('forename', '').strip()
    surname  = request.form.get('surname', '').strip()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:

        # Check if username already exists
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        # Create the password hash
        password_hash = generate_password_hash(password)

        # Create the user
        sql = """
            INSERT INTO users (forename, surname, username, password_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (forename, surname, username, password_hash)
        db.execute(sql, params)

        flash("Account created", "success")
        return redirect("/user/login")


#-----------------------------------------------------------
# Handle create family
#-----------------------------------------------------------
@app.post("/family/create")
@login_required
def create_a_family():
    family_name = request.form.get('family_name', '').strip()
    if not family_name:
        flash("Please enter a family name", "error")
        return redirect("/family/create")
    
    with connect_db() as db:
        # Check whether the family name already exists
        sql = "SELECT id FROM family WHERE family_surname=?"
        params = (family_name,)
        family = db.execute(sql, params).fetchone()

        if family:
            flash(f"Family name '{family_name}' already exists", "error")
            return redirect("/family/create")

        # Get the logged-in user's ID
        user_id = session["user"]["id"]

        # Check whether the user already belongs to a family
        sql = "SELECT id FROM family_members WHERE user_id=?"
        params = (user_id,)
        member = db.execute(sql, params).fetchone()

        if member:
            flash("You already belong to a family", "error")
            return redirect("/")

        # Generate a family code
        family_code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

        # Create the family
        sql = """
            INSERT INTO family (family_surname, family_code)
            VALUES (?, ?)
        """
        params = (family_name, family_code)
        db.execute(sql, params)

        # Get the new family's ID
        family_id = db.execute(
            "SELECT id FROM family WHERE family_code=?",
            (family_code,)
        ).fetchone()["id"]

        # Add the user to the family as the owner
        sql = """
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (?, ?, ?)
        """
        params = (family_id, user_id, "owner")
        db.execute(sql, params)

    # Update the user's session role
    session["user"]["role"] = "owner"

    flash(f"Family created! Your family code is {family_code}", "success")
    return redirect("/home_logged")

#-----------------------------------------------------------
# Handle user login
#-----------------------------------------------------------
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT users.id, users.forename, users.surname, users.password_hash,
            family_members.role
            FROM users
            LEFT JOIN family_members ON users.id = family_members.user_id
            WHERE users.username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/user/login")

        if not check_password_hash(user["password_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/user/login")

        session["logged_in"] = True
        session["user"] = {
            "id":       user["id"],
            "username": username,
            "forename": user["forename"],
            "surname":  user["surname"],
            "role":     user["role"],
        }
        flash("Login successful", "success")
        return redirect("/home_logged")

#-----------------------------------------------------------
# Join family
#-----------------------------------------------------------
@app.post("/family/join")
@login_required
def join_family():
    family_code = request.form.get('family_code', '').strip().upper()
    with connect_db() as db:
        # Find the family
        sql = """
            SELECT id
            FROM family
            WHERE family_code=?
        """
        params = (family_code,)
        family = db.execute(sql, params).fetchone()

        if not family:
            flash("Invalid family code", "error")
            return redirect("/family/join")

        # Check if the user is already in a family
        sql = """
            SELECT id
            FROM family_members
            WHERE user_id=?
        """
        params = (session["user"]["id"],)
        current_family = db.execute(sql, params).fetchone()

        if current_family:
            flash("You are already in a family", "error")
            return redirect("/family")

        # Add the user to the family
        sql = """
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (?, ?, ?)
        """
        params = (
            family["id"],
            session["user"]["id"],
            "member"
        )
        db.execute(sql, params)

        # Update the user's session
        session["user"]["role"] = "member"

        flash("You have joined the family!", "success")
        return redirect("/family")
#-----------------------------------------------------------
# Handle user logout
#-----------------------------------------------------------
@app.get("/logout")
def logout():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")

#-----------------------------------------------------------
# New Chore Page
#-----------------------------------------------------------
@app.get("/chore/new")
def show_chore_form():
    return render_template("pages/chore_form.jinja")

#-----------------------------------------------------------
# Home page not logged in
#-----------------------------------------------------------
@app.get("/")
def show_home_page():
    return render_template("pages/home_page_not_logged.jinja")

#-----------------------------------------------------------
# Home page logged in
#-----------------------------------------------------------
@app.get("/home_logged")
def show_home_page_logged_in():
    with connect_db() as db:
        sql = """
            SELECT 
            *
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        return render_template("pages/home_page_logged_in.jinja", users=users)
    
#-----------------------------------------------------------
# Chores page - show all chores
#-----------------------------------------------------------
@app.get("/chores")
def show_all_chores():
    with connect_db() as db:
        sql = """
            SELECT
                chores.id AS mid,
                chores.title,
                chores.body,
                chores.priority,
                chores.due_time,
                chores.complete,
                users.id AS uid,
                users.forename
            FROM chores

            JOIN users ON chores.user_id = users.id

            JOIN family_members ON users.id = family_members.user_id

            WHERE family_members.family_id = (
                SELECT family_id
                FROM family_members
                WHERE user_id = ?
            )
        """

        params = (session["user"]["id"],)
        chores = db.execute(sql, params).fetchall()

        return render_template("pages/chore_list.jinja", chores=chores)
#-----------------------------------------------------------
# Add a new chore
#-----------------------------------------------------------
@app.post("/chore")
@login_required
def add_chore():
    if session["user"]["role"] != "owner":
        flash("Only the family owner can create chores", "error")
        return redirect("/chores")
                        
    # Get form data
    title    = request.form.get('title', '').strip()
    body     = request.form.get('body', '').strip()
    priority = int(request.form.get("priority"))
    due_time = request.form.get('due_time', '').strip()

    # Validate data
    if not title:
        flash("Title is required", "error")
        return redirect("/chore/new")
    
    if not body:
        flash("Body is required", "error")
        return redirect("/chore/new")
    
    if not priority:
        flash("Priority is required", "error")
        return redirect("/chore/new")
    
    if not due_time:
        flash("Due time is required", "error")
        return redirect("/chore/new")
    
    if priority < 1 or priority > 5:
        flash("Priority should be between 1 and 5", "error")
        return redirect("/chore/new")

    if len(title) > 40:
        flash("Title is too long (max 40 chars)", "error")
        return redirect("/chore/new")
    if len(body) > 100:
        flash("Body is too long (max 40 chars)", "error")
        return redirect("/chore/new")

    # Escape text inputs
    title = html.escape(title)
    body = html.escape(body)
    due_time = html.escape(due_time)

    # User id is in the session
    user_id = session["user"]["id"]

    # Add to the database
    with connect_db() as db:
        sql = """
            INSERT INTO chores (user_id, title, body, priority, due_time)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (user_id, title, body, priority, due_time)
        db.execute(sql, params)

        flash(f"Chore added")
        return redirect("/chore/new")

#-----------------------------------------------------------
# Edit chore
#-----------------------------------------------------------
@app.get("/chore/edit/<int:id>")
@login_required
def edit(id):
    with connect_db() as db:
        sql = """
            SELECT
                chores.id     AS mid,
                chores.title,
                chores.body,
                chores.priority,
                chores.due_time,
                users.id        AS uid,
                users.forename

            FROM chores
            JOIN users ON chores.user_id = users.id
            WHERE chores.id=?
    """
        params = [id]
        chore = db.execute(sql, params).fetchone()
        return render_template("pages/chore_edit.jinja", chore=chore)

#-----------------------------------------------------------
# Post Edit
#-----------------------------------------------------------
@app.post("/chore/edit/<int:id>")
@login_required
def edit_post(id):
    title = request.form.get("title", "").strip()
    body  = request.form.get("body", "").strip()
    priority = request.form.get("priority", "").strip()
    due_time = request.form.get("due_time", "").strip()

    with connect_db() as db:
        sql = """
            UPDATE chores
            SET title=?, body=?, priority=?, due_time=?
            WHERE id=?
        """
        params = [title, body, priority, due_time, id]
        db.execute(sql, params)

        flash("Message updated", "success")
        return redirect("/chores")

#-----------------------------------------------------------
# Delete a chore
#-----------------------------------------------------------
@app.get("/chore/delete/<int:id>")
@login_required
def delete(id):
    with connect_db() as db:
        sql = """
            SELECT user_id
            FROM chores
            WHERE id=?
        """
        params = (id,)
        chore = db.execute(sql, params).fetchone()

        if chore and chore["user_id"] == session["user"]["id"]:
            sql = """
                DELETE FROM
                chores
                WHERE id=?
            """
            params = [id]
            db.execute(sql, params)
            flash("The chore has been deleted", "success")

        return redirect("/chores")

# #-----------------------------------------------------------
# # A complete chore
# #-----------------------------------------------------------
@app.get("/complete/<int:id>")
def complete_chore(id):
    with connect_db() as client:
        sql = "UPDATE chores SET complete=1 WHERE id=?"
        values = [id]
        client.execute(sql, values)
    return redirect("/chores")
    
# #-----------------------------------------------------------
# # A incomplete chore
# #-----------------------------------------------------------
@app.get("/incomplete/<int:id>")
def incomplete_chore(id):
    with connect_db() as client:
        sql = "UPDATE chores SET complete=0 WHERE id=?"
        values = [id]
        client.execute(sql, values)
    return redirect("/chores")

#-----------------------------------------------------------
# Family page - Show all users in family
#-----------------------------------------------------------
@app.get("/family")
@login_required
def show_all_users_in_family():
    with connect_db() as db:
        sql="""
            SELECT
                family.family_surname AS family_name, family.family_code,
                users.forename, users.surname,
                family_members.role
                
            FROM family_members
            JOIN users ON family_members.user_id = users.id
            JOIN family ON family_members.family_id = family.id
            WHERE family_members.family_id = (
                SELECT family_id
                FROM family_members
                WHERE user_id=?
            )
        """
        params = (session["user"]["id"],)
        families = db.execute(sql, params).fetchall()

        return render_template("pages/family_list.jinja", families=families)

#-----------------------------------------------------------
# Leave family
#-----------------------------------------------------------
@app.get("/family/leave")
@login_required
def leave_family():
    with connect_db() as db:
        sql = """
            SELECT id, role
            FROM family_members
            WHERE user_id=?
        """
        params = (session["user"]["id"],)
        family_member = db.execute(sql, params).fetchone()

        if not family_member:
            flash("You are not in a family", "error")
            return redirect("/home_logged_in")

        sql = """
            DELETE FROM family_members
            WHERE id=?
        """
        params = (family_member["id"],)
        db.execute(sql, params)

        session["user"]["role"] = None

        flash("You have left the family", "success")
        return redirect("/home_logged")
#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

