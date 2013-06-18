BookQueue is a tool for keeping track of the books you read so you can review them in batches.

You have to initialize your account with a text message, but after that you can add books to your queue via sms or email. Once you've accumulated 6 + 1d6 books, or marked a batch as ready, you'll start getting a daily reminder email until you mark that batch done. You can add new books in the meantime, but they won't be added to your old batch unless you add them yourself.

Books are deleted when you mark their batch done, so you're best off only doing so once you've posted your reviews for that batch on your regular blog or wherever.


Setting up Your Own Instance of BookQueue
-----------------------------------------

To set up your own version on Heroku, you'll need to register a phone number with Twilio and get Heroku's free Scheduler and Mailgun addons, and set up a daily task for bin/reminder.py.

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
    4) filter: match_header("subject", "(?i)LIST"), action: forward("https://yourapp.herokuapp.com/list")




Usage
-----

You may want to whitelist the email address you set up in order to avoid reminder emails getting stuck in your spam filter.


Register your account with your phone number and email address:

    text your Twilio phone number with EMAIL:you@yourdomain.com


Add a book to your queue:

    email your app with subject: BOOK, body: a single line of book info (ie 'Labyrinths by Jorge Luis Borges')
    *or*
    text your Twilio phone number with a single line of book info (ie 'On the Orator by Cicero')


Set all books in your queue as a complete batch ready for reviews:

    email your app with subject: EOB
    *or*
    text your Twilio phone number with EOB


Mark your reviews for your current complete batch done to have that batch deleted and reminders cease:

    email your app with subject: DONE
    *or*
    text your Twilio phone number with DONE

Get a list of all of your books:

    email your app with subject: LIST
    *or*
    text your Twilio phone number with LIST
