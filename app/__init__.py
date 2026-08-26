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
    surname  = request.form.get('surname',  '').strip()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    points = "0"

    with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        password_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (forename, surname, username, password_hash, points)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (forename, surname, username, password_hash, points)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
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
            SELECT id, forename, surname, password_hash
            FROM users
            WHERE username=?
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
        }

        flash("Login successful", "success")
        return redirect("/home_logged_in")
    
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

        flash("Test message")
        flash("Test SUCCESS message", "success")
        flash("Test INFO message", "info")
        flash("Test WARNING message", "warning")
        flash("Test ERROR message", "error")

        return render_template("pages/home_page_not_logged.jinja")

#-----------------------------------------------------------
# Home page logged in
#-----------------------------------------------------------
@app.get("/home_logged_in")
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
                chores.id,
                chores.title,
                chores.body,
                chores.due_time,
                chores.points,
                chores.complete,
                chores.pinned
            
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
def add_chore():
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

