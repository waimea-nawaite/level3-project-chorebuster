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

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            forename      TEXT    NOT NULL,
            surname       TEXT    NOT NULL,
            username      TEXT    NOT NULL,
            password_hash TEXT    NOT NULL,
            points        INTEGER NOT NULL DEFAULT (0)
        )
    """

    SEED_DATA = """
    """


class ChoreTable:

    NAME = "chores"

    SCHEMA = """
        CREATE TABLE chores (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            title    TEXT    NOT NULL,
            body     TEXT    NOT NULL,
            due_time TIME,
            points   INTEGER DEFAULT (0),
            complete INTEGER DEFAULT (0),
            pinned  INTEGER DEFAULT 0,

            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    """

    SEED_DATA = """
        INSERT INTO chores (user_id, title, body, due_time, points, complete, pinned)
        VALUES
            (1, "Meat", "Steak", 15, 6, 0, 1)
    """

class FamilyTable:

    NAME = "family"

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
    UserTable,
    ChoreTable
    # Add more tables here...
]

