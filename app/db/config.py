#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

# Add more table classes here...

class UserTable:

    name = "users"

    SCHEMA = """
        CREATE TABLE users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            username      TEXT    NOT NULL,
            password_hash TEXT    NOT NULL,
            points        INTEGER NOT NULL
        )
    """

    SEED_DATA = """
        INSERT INTO users (name, username, points)
        VALUES
            ("Bob", "BOBBY", 20)
    """


class ChoreTable:

    name = "chores"

    SCHEMA = """
        CREATE TABLE chores (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            title    TEXT    NOT NULL,
            due_time TIME    NOT NULL,
            points   INTEGER DEFAULT (0),
            complete INTEGER DEFAULT (0)
        )
    """

    SEED_DATA = """
        INSERT INTO chores (title, due_time, points, complete)
        VALUES
            ("Meat", 15, 6, 0)
    """

class FamilyTable:

    name = "family"

    SCHEMA = """
        CREATE TABLE family (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            surname TEXT    NOT NULL,
            user_id INTEGER NOT NULL
        )
    """



#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    NoteTable,
    # Add more tables here...
]

