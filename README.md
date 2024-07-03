# Krashen-based GPT-Powered Language Learning
A GPT-powered implementation of the "i+1" input hypothesis for second language acquisition originally formulated by Stephen Krashen [1].

[1] Krashen, Stephen. "Second language acquisition." Second Language Learning 3.7 (1981): 19-39.

### The feedback loop
1. GPT generates some foreign language words, narrowed in scope to a specific part of speech and context.
2. GPT generates a foreign language sentences using those words, according to a difficulty based on the user level.
3. Prompt the user for a translation.
4. Uses GPT to comparer the translation to the generated sentence.
5. If correct, pull from the pool of words again and return to Step 2.
6. If sentences built with the words are consistently answered correctly, remove them from the pool of choices.
7. Once the word pool is depleted, wait a set amount of time before adding more words to the pool and starting over.
8. Difficulty and word pool gradually increases.

## Features
- GPT-powered generation of sentences
- Tiered introduction of different parts of speech (e.g., nous, verbs, etc.)
- Progressive difficulty
- GPT-powered translation checking
	- No more stumbling on rigid answers 
- SQLite3 database for saving progress
- GPT-powered backend supports multiple languages (Spanish, French, German, Japanese, Chinese, Korean, etc.)

## Todo:
- Formally implement spaced repetition algorithm
- Add a UI for users to manually modify their word lists
- Add a UI to modify settings like batch size and intervals between learning
- Easy 1-click installation scripts
- Languages with punctuated words (e.g., J'aime) still causes some problems
- There's currently no variability in progression without score decay

## Installation and Running
Currently only runs locally with Flask and redis.

Install [Flask](https://flask.palletsprojects.com/en/3.0.x/), [redis](https://redis.io/), and the [OpenAI API](https://platform.openai.com/docs/quickstart)

You will need an OpenAI API key to run this.

## Changelog
Jul/2/2024: Initial release with support for practice from Spanish, French, German, Italian, Dutch, Portuguese, Chinese, Japanese, Korean, Russian, Arabic, and Turkish to English. Progression to higher levels not thoroughly tested, but the basic process of the program works.

### Author
Written by [Dan Fu](https://dfu99.github.io)
