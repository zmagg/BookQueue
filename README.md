To set up your own version on Heroku, you'll need to get the free Scheduler and Mailgun addons, and set up a daily task for bin/reminder.py.

To set up the database on Heroku, follow these steps:

    in the command line:
      heroku addons:add heroku-postgresql:dev
      heroku pg:promote HEROKU_POSTGRESQL_COLOR (where COLOR is whatever you got back from the prior command)
      heroku run python
    in the heroku python terminal:
      from app import db
      db.create_all()


To set up the Heroku mailgun add-on, first add it, then create three routes in the mailgun admin console:

    1) filter: match_header("subject", "(?i)EOB"), action: forward("https://yourapp.herokuapp.com/eob")
    2) filter: match_header("subject", "(?i)DONE"), action: forward("https://yourapp.herokuapp.com/done")
    3) filter: match_header("subject", "(?i)BOOK"), action: forward("https://yourapp.herokuapp.com/book")


Usage for the Current Live Version
----------------------------------

You may want to whitelist bookqueue@app10659070.mailgun.org to avoid reminder emails getting stuck in your spam filter.


Register your account with your phone number and email address:

    text 917-746-3273 with EMAIL:you@yourdomain.com


Add a book to your queue:

    email bookqueue@app10659070.mailgun.org with subject: BOOK, body: a single line of book info (ie 'Labyrinths by Jorge Luis Borges')
    *or*
    text 917-746-3273 with a single line of book info (ie 'On the Orator by Cicero')


Set all books in your queue as a complete batch ready for reviews:

    email bookqueue@app10659070.mailgun.org with subject: EOB
    *or*
    text 917-746-3273 with EOB


Mark your reviews for your current complete batch done to have that batch deleted and reminders cease:

    email bookqueue@app10659070.mailgun.org with subject: DONE
    *or*
    text 917-746-3273 with DONE
