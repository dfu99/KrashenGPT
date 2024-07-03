from app import app, gpt, src, db
from flask import render_template, session, redirect, url_for, send_from_directory
import os, random
from datetime import datetime, timedelta

def user_exists():
    """
    Use the USER_LEVEL key to see if a user has already been created
    :return: True if user exists, False if user does not exist
    """
    try:
        assert "USER_LEVEL" in session.keys()
        return True
    except AssertionError:
        return False


# Home page
@app.route('/', methods=["GET", "POST"])
def home():
    """
    Every time we load the homepage, we check the status of the current batch
    If the current batch is finished, and it's not time for a new batch, we send the user to completion of the current bash
    """
    ### Debugging for each state
    # print("User exists:", not user_exists())
    # print("Language not in user level keys", session['LANGUAGE'] not in session['USER_LEVEL'].keys())
    # print("Database is empty", db.db_is_empty(session['LANGUAGE']))
    # print("Batch not completed and within threshold", src.is_batch_within_threshold(session["batch"]))
    # print("Time for new batch", src.is_time_for_new_batch(session["last_batch_time"][session["LANGUAGE"]]))

    # Check the system state
    if not user_exists():
        # Check if this is the user's first ever visit to the page
        print("[INFO] User does not exist. Import default configuration settings.")
        src.setup()
    if session['LANGUAGE'] not in session['USER_LEVEL'].keys():
        # Check if this is the user's first time testing on the selected language
        print(f"[INFO] User has not worked on {session['LANGUAGE']} before. Looking for for an existing database or will initialize one if it does not exist.")
        src.initiate()
        src.load_new_batch()
    elif db.db_is_empty(session['LANGUAGE']):
        # Check if the database has been lost, deleted, or corrupted
        print("[INFO] The database is missing. Initializing a new one and adding an initial batch of words.")
        src.initiate()
        src.load_new_batch()
    # The following are daily checkpoints
    elif src.is_batch_within_threshold(session["batch"][session["LANGUAGE"]]):
        # is_batch_within_threshold: Checks if the batch is still within the learning threshold
        # Keep working on the same batch, regardless of time
        print("[INFO] Continuing to work on same batch.")
        pass
    elif src.is_time_for_new_batch(session["last_batch_time"][session["LANGUAGE"]], session["BATCH_INTERVAL"]):
        # is_time_for_new_batch: Checks the interval since the last batch was created
        print("[INFO] Previous batch is finished and delay has expired. Opening new batch.")
        src.close_last_batch()
        # Make a new batch. If this occurs on the same day as the last batch, user gets to work on another batch
        src.load_new_batch()
    else:
        # Otherwise, user has completed their batch. Redirect to completion page.
        # Evaluate when the next batch will load
        print("[INFO] Batch is done. Time delay to next batch not yet reached. Loading completion.")
        new_batch_time = datetime.strptime(session["last_batch_time"][session["LANGUAGE"]], '%d/%m/%y %H:%M:%S.%f') + timedelta(hours=session["BATCH_INTERVAL"])
        new_batch_time = new_batch_time.strftime('%d %b %Y %I:%M %p')        
        return render_template('complete.html', new_batch_time = new_batch_time)

    # Generate a new target text from the batch
    batch = session['batch'][session["LANGUAGE"]]
    words = []
    # Pick a word from each part of speech in the batch
    for p in batch.keys():
        pwords = batch[p]
        try:
            words.append((p, random.choice(pwords)))
        except IndexError:
            # As the batch list is progressively shortened, some might be empty, thus skipped
            # It should never be the case that both batch lists are empty
            # That should be caught ahead of time by is_batch_within_threshold
            pass
    
    session["tested_words"] = words
    target_text = session['target_text'] = gpt.get_new_text([w[1] for w in words], session["DIFFICULTY"], session["LANGUAGE"])
    
    # Load it to the page
    return render_template('index.html',
                           target_text = target_text)


@app.route('/next-text')
def next_text():
    """
    Handles a redirect back to the homepage once a correct answer has been supplied
    """
    # Update score of each word that was in the generated sentence
    # Remove the word from the batch list if it has been practiced enough
    print("[INFO] Score update:", session['scores'][session["LANGUAGE"]])
    for t in session["tested_words"]:
        p = t[0]
        w = t[1]
        session['scores'][session["LANGUAGE"]][p][w] += 1
        # Limit the number of times a word will appear in today's batch
        if session['scores'][session["LANGUAGE"]][p][w] >= session["REPETITIONS"]:
            # Remove it from the batch
            try:
                session["batch"][session["LANGUAGE"]][p].remove(w)
            except ValueError:
                pass

    return redirect(url_for('home'))


@app.route('/switch/<language>')
def switch_language(language):
    session["LANGUAGE"] = language
    return redirect(url_for('home'))

@app.route('/favicon.ico') 
def favicon():
    """
    Puts an icon on the tab in the browser
    """
    return send_from_directory(os.path.join(app.root_path, 'static/graphics'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')