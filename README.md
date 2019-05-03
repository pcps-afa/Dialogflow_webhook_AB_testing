# Dialogflow_webhook_AB_testing
This is a webhook template for Dialogflow (API v2) that is prepared to do A/B Testing for the "Welcome Intent"

# What you need to do to get this up & running
* Fork this repository
* Create a Heroku account
* In Heroku, create a App (it's free, but it sleeps after 30 minutes of not being used and then takes 12 seconds to wake up)
* In this App, create a "Heroku Postgres" Add-on resource (it's free for up to 10'000 rows)
* In Heroku CLI, connect to that database (exact command for Heroku CLI can be found in "Settings" of the resource in Heroku, just copy+paste)
* Create a table in this database with the following command:
* CREATE TABLE sessions(session_id varchar(255) primary key, aorb varchar(255));
* Copy the connection URI (also found in "Settings" of Heroku resource, looks like postgres://[...]) of this database and paste them into the app.py file, in the getAB Method.
* The only thing that may still need to be edited in app.py is the 
