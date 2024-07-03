from flask import session
from app import app, db

def initiate():
    """
    Initiate runs when the SQL language database for the current user and language are empty
    """
    # Add a key for the language in the user level dict
    session["USER_LEVEL"][session["LANGUAGE"]] = 0
    # Make the database and set up a merged table
    # Batch are built from the merged table, but saved per their part of speech
    # I don't know if this separation will be useful in the future
    lang_db = db.language_database(session["LANGUAGE"])
    lang_db.make_sql_table('merged')


def assert_session_variable(key):
    """
    Verify if the key exists
    """
    try: 
        assert key in session.keys()
        return True
    except AssertionError:
        return False


def setup():
    """
    Setup initiates a user's profile upon their very first use of the page, ever
    Pull saved user configurations
    """
    user_variables_list = ['USER_LEVEL', 'BATCH_SIZE', 'NEW_BATCH_SIZE', 'BATCH_INTERVAL', 'DIFFICULTY', 'LANGUAGE', 'CONTEXTS', 'PARTS_OF_SPEECH', 'REPETITIONS', 'LEVELING_RATE']
    for user_key in user_variables_list:
        if assert_session_variable(user_key):
            pass
        else:
            session[user_key] = app.config[user_key]
    session["batch"] = {}
    session["scores"] = {}
    session["last_batch_time"] = {}
