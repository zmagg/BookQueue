BookQueue is a tool for keeping track of the books you read so you can review them in batches.

You have to initialize your account with a text message, but after that you can add books to your queue via sms or email. Once you've accumulated 6 + 1d6 books, or marked a batch as ready, you'll start getting a daily reminder email until you mark that batch done. You can add new books in the meantime, but they won't be added to your old batch unless you add them yourself.

Books are deleted when you mark their batch done, so you're best off only doing so once you've posted your reviews for that batch on your regular blog or wherever.


Setting up Your Own Instance of BookQueue
-----------------------------------------

To set up your own version of BookQueue, you'll need to register a phone number with Twilio, setup a Heroku app, and get Heroku's free Scheduler and Mailgun addons, and set up a daily task for bin/reminder.py.

First, follow the Heroku setup instructions <a href="https://toolbelt.heroku.com/">here</a>.

Clone this repository using
    git clone git://github.com/DanielleSucher/BookQueue

Then, to set up the database on Heroku, follow these steps within the cloned directory:

    in the command line:
      heroku addons:add heroku-postgresql:dev
      heroku pg:promote HEROKU_POSTGRESQL_COLOR (where COLOR is whatever you got back from the prior command)
      heroku run python
    in the heroku python terminal:
      from app import db
      db.create_all()

In order to use any addon with Heroku, you need to <a href="http://heroku.com/verify">verify</a> your account. Once you've done that you should be able to issue in the command line:

    heroku addons:add heroku-mailgun 

To get to the mailgun control panel, navigate to your Heroku apps dashboard in the website and click on "Mailgun" in the add-ons section. 

You can then create four routes in the mailgun control panel, alternatively you can issue curl requests using the API key found in the Mailgun control panel.

    1) filter: match_header("subject", "(?i)EOB"), action: forward("https://yourapp.herokuapp.com/eob")
    2) filter: match_header("subject", "(?i)DONE"), action: forward("https://yourapp.herokuapp.com/done")
    3) filter: match_header("subject", "(?i)BOOK"), action: forward("https://yourapp.herokuapp.com/book")
    4) filter: match_header("subject", "(?i)LIST"), action: forward("https://yourapp.herokuapp.com/list")

To register a phone number on Twilio, follow the Twilio setup instructions for the Free Trial account. Once your phone number is set up, configure your SMS Request URL to point to your heroku app domain appended with "/sms" (i.e. http://heroku-naming-convention-2348972.herokuapp.com/sms). You can find the domain in your heroku app console.


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
