#===========================================================
# PROJECT NAME HERE
# By YOUR NAME HERE
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
# Signup Page
#-----------------------------------------------------------
@app.get("/user/new/family")
def show_signup_family_form():
    return render_template("pages/user_form_family.jinja")

#-----------------------------------------------------------
# Login Page
#-----------------------------------------------------------
@app.get("/user/login")
def show_login_form():
    return render_template("pages/login_page.jinja")

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
    family_code = request.form.get('family_code', '').strip().upper()
    points = "0"

    with connect_db() as db:
        # Check that the family code exists
        sql = """
            SELECT id
            FROM family
            WHERE family_code=?
        """
        params = (family_code,)
        family = db.execute(sql, params).fetchone()

        if not family:
            flash("Family code does not exist", "error")
            return redirect("/user/new")

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
            INSERT INTO users (forename, surname, username, password_hash, points)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (forename, surname, username, password_hash, points)
        db.execute(sql, params)

        # Get the newly created user's ID
        user_id = db.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        ).fetchone()["id"]

        # Add the user to the family
        sql = """
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (?, ?, ?)
        """
        params = (family["id"], user_id, "member")
        db.execute(sql, params)

        flash("Account created", "success")
        return redirect("/user/login")


#-----------------------------------------------------------
# Handle user signup with Family
#-----------------------------------------------------------
@app.post("/user/family")
def add_user_family():
    forename = request.form.get('forename', '').strip()
    surname  = request.form.get('surname',  '').strip()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    family_name = request.form.get('family_name', '').strip()
    points = "0"

    with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        password_hash = generate_password_hash(password)

        # Create the user
        sql = """
            INSERT INTO users (forename, surname, username, password_hash, points)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (forename, surname, username, password_hash, points)
        db.execute(sql, params)

        # Get the new user's ID
        user_id = db.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        ).fetchone()["id"]

        # Generate a family code
        family_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Create the family
        sql = """
            INSERT INTO family (surname, family_code)
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

        flash(f"Family created! Your family code is {family_code}", "success")
        return redirect("/user/login")
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
            JOIN family_members ON users.id = family_members.user_id
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
        return redirect("/")
    
#-----------------------------------------------------------
# Handle user logout
#-----------------------------------------------------------

@app.get("/logout")
def logout():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/home_not_logged")

#-----------------------------------------------------------
# New Chore Page
#-----------------------------------------------------------
@app.get("/chore/new")
def show_chore_form():
    return render_template("pages/chore_form.jinja")

#-----------------------------------------------------------
# Home page not logged in
#-----------------------------------------------------------
@app.get("/home_not_logged")
def show_home_page():

        flash("Test message")
        flash("Test SUCCESS message", "success")
        flash("Test INFO message", "info")
        flash("Test WARNING message", "warning")
        flash("Test ERROR message", "error")

        return render_template("pages/home_page_not_logged.jinja")

#-----------------------------------------------------------
# Home page logged in
#-----------------------------------------------------------
@app.get("/")
def show_home_page_logged_in():
    with connect_db() as db:
        sql = """
            SELECT 
            *
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        flash("Test message")
        flash("Test SUCCESS message", "success")
        flash("Test INFO message", "info")
        flash("Test WARNING message", "warning")
        flash("Test ERROR message", "error")

        return render_template("pages/home_page_logged_in.jinja", users=users)


#-----------------------------------------------------------
# Chore page - Show all chores
#-----------------------------------------------------------
@app.get("/chores")
def show_all_chores():
    with connect_db() as db:
        sql = """
            SELECT 
                chores.id       AS mid,
                chores.title,
                chores.body,
                chores.due_time,
                chores.points,
                chores.complete,
                chores.pinned,
                users.id        AS uid,
                users.forename
            
            FROM chores
            JOIN users ON chores.user_id = users.id
            ORDER BY pinned DESC
        """
        params = ()
        chores = db.execute(sql, params).fetchall()

        return render_template("pages/chore_list.jinja", chores=chores)


#-----------------------------------------------------------
# Handle user chore
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
    due_time = request.form.get('due_time', '').strip()
    points   = request.form.get('points', '').strip()

    # Validate data
    if not title:
        flash("Title is required", "error")
        return redirect("/chore/new")
    
    if not body:
        flash("Body is required", "error")
        return redirect("/chore/new")
    
    if len(body) > 200:
        flash("Body is too long (max 200 chars)", "error")
        return redirect("/chore/new")

    if len(title) > 40:
        flash("Title is too long (max 40 chars)", "error")
        return redirect("/chore/new")

    # Escape text inputs
    title = html.escape(title)
    body = html.escape(body)

    # User id is in the session
    user_id = session["user"]["id"]

    # Add to the database
    with connect_db() as db:
        sql = """
            INSERT INTO chores (user_id, title, body, due_time, points)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (user_id, title, body, due_time, points)
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

#-----------------------------------------------------------
# Family page - Show all users in family
#-----------------------------------------------------------
@app.get("/family")
@login_required
def show_all_users_in_family():
    with connect_db() as db:
        sql="""
            SELECT
                family.surname AS family_name,
                family.family_code,
                users.forename,
                users.surname,
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
    
# #-----------------------------------------------------------
# # Leave family
# #-----------------------------------------------------------
# @app.get("/family/leave")
# @login_required
# def leave_family():
#     with connect_db() as db:
#         sql = """
#             SELECT id, role
#             FROM family_members
#             WHERE user_id=?
#         """
#         params = (session["user"]["id"],)
#         family_member = db.execute(sql, params).fetchone()

#         if not family_member:
#             flash("You are not in a family", "error")
#             return redirect("/home_logged_in")

#         if family_member["role"] == "owner":
#             flash("The family owner cannot leave the family", "error")
#             return redirect("/family")

#         sql = """
#             DELETE FROM family_members
#             WHERE id=?
#         """
#         params = (family_member["id"],)
#         db.execute(sql, params)

#         flash("You have left the family", "success")
#         return redirect("/")
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

