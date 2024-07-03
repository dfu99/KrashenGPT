from itertools import combinations
import random

def get_pos_level(user_level, parts):
    """
    Choose parts of speech based on user level
    """
    # How many parts of speech to generate depends on the number of cycles
    # Each cycle is the size of the number of parts of speech
    # On the first cycle, list is truncated
    all_combos = []
    for i in range( int(user_level/len(parts))+1 ):
        all_combos.append(random.choice(parts[:user_level+1]))

    return all_combos