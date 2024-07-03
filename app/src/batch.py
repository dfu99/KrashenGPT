from datetime import datetime, timedelta
from flask import session
from app import db, src
import random


def is_time_for_new_batch(last_batch_time, batch_interval):
    """
    Compares the current time to the last time a batch was generated
    """
    interval = timedelta(hours=batch_interval)
    # Check if we should load a new batch based on the time since the last batch was loaded
    last_batch_time = datetime.strptime(last_batch_time, '%d/%m/%y %H:%M:%S.%f')
    current_time = datetime.now()
    if current_time - last_batch_time > interval:
        return True
    else:
        return False


def is_batch_within_threshold(batch):
    """
    Checks if we have finished working on this batch
    Every time we finish a word, it will be removed from the batch choies
    A completely empty batch list indicates completion
    """
    if all(len( batch[x] )==0 for x in batch.keys()):
        return False
    return True


def close_last_batch():
    """
    Clears the existing batch and updates its SQL database scores
    """
    language = session["LANGUAGE"]

    # Make a database access object
    lang_db = db.language_database(language)

    # Save the results back into the database
    for p in session['scores'][session["LANGUAGE"]].keys():
        for w in session['scores'][session["LANGUAGE"]][p].keys():
            # Update the parts of speech table
            lang_db.inc_vocab_score(p, w)
            # Update the merged table
            lang_db.inc_vocab_score('merged', w)

    # Check user level up conditions
    mean_score = lang_db.mean_score()
    if mean_score > session["LEVELING_RATE"]:
        session["USER_LEVEL"][session["LANGUAGE"]] += 1


def load_new_batch():
    # Load some of the params we will be using
    new_batch_size = session["NEW_BATCH_SIZE"]
    language = session["LANGUAGE"]
    batch_size = session["BATCH_SIZE"]
    current_level = session["USER_LEVEL"][language]

    # Make a database access object
    lang_db = db.language_database(language)

    # Adds to the database
    # Pick out a few parts of speech to focus on
    session["tested_parts"] = tested_parts = src.get_pos_level(current_level, session["PARTS_OF_SPEECH"])
    # Context depends on the chosen part of speech
    contexts = [random.choice(session["CONTEXTS"][p]) for p in tested_parts]
    # Make the database and tables, then generate the first batch
    lang_db.grow_batch(tested_parts, contexts, new_batch_size)

    # Queries from the database
    # Make today's practice set
    batch, scores = lang_db.get_batch(batch_size)
    session["batch"][session["LANGUAGE"]] = batch
    session["scores"][session["LANGUAGE"]] = scores
    # Save the time
    last_batch_time = datetime.now()
    session["last_batch_time"][session["LANGUAGE"]] = last_batch_time.strftime('%d/%m/%y %H:%M:%S.%f')
    