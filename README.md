# README for SLC Registration Flask App

by Austin Poor

## Description
This is my solution help Sarah Lawrence College students stay on top of their course registration – as the conference project for my Databases course. (At SLC, a conference project is sort of like a year- or semester-long mini-senior-thesis.)

The current method for registration requires students to collate the information from different sources to find course description, professor information, meeting times, and professor interview times. ([Think the scene in the movie Day at the Races where Chico Marx is selling Groucho Marx the books.](https://www.youtube.com/watch?v=DqypaqLEfM8))

My solution allows students to search for courses and add them to a cart, where they can see conflicts between courses and generate possible schedules based on their classes.


## Instructions to Run the Program
* Navigate to the project folder
* Make sure you have Python 3 installed as well as the Flask library
    * rewquirements.txt included in the repo
* Run the flask app with: `python flask_app.py`
* The terminal should print something like this:
``` 
 * Serving Flask app "flask_app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 289-740-940
 ```
* In your browser, navigate to the URL that flask tells you to (in this case it is `http://127.0.0.1:5000/`)
* Now the app is running! Enter search terms to find classes
* On the `/results` page, toggle the heart button next to a class to add it to your cart
* Once you're done adding (or removing) from your cart, press the button at the top of the table to commit the changes – that will take you to your cart.
* From the `/cart` page, you can view or remove your saved classes, view coures conflicts, and create schedules, by pressing the `Generate Schedules` button at the top of the cart table.
* The `/schedules` page shows all possible (conflict free) 3-course schedules.
* Your cart will be stored temporarily but to *save* your cart, you have to create an account. You can navigate to the `/signin` or `/signup` page.
* There is also a `sign out` option, if you'd like to switch accounts or if you just don't feel like being signed in anymore.

## Future Improvements
(In no particular order)
* Clean up the data & make the code more robust – For the sake of time, I've built the program to work for the general case of 5-credit classes, with a unique course-id, and with a single meeting at a given time (ie not classes with multiple rooms booked at any given time, component classes, year-long classes which change location/time from semester to semester, etc.).
* Optional Classes – Similar to the idea above, allow the program to take into account certain times of class meetings like group conferences for lectures, where students can pick one out of however many options. This could potentially open up some more options for students when generating schedules.
* Style – There's minimal styling and I think I could make it look a bit nicer.
* Updating without reloading – For certain things like adding classes to a cart, it would be nice to have a way to update the data without having to *commit* the change. This could potentially be done with AJAX or I've also found a way to do this with Flask called Flask-SocketIO (which uses the Javascript Socket.IO library). I unfortunately didn't have enough time to test and incorporate it.
* Class weighting – Allow the user to weight classes (either individually or in tiers) so that schedules could be given scores and ranked. Another interesting option would be to allow users to create some type of rules for building schedules. For example: 
    * "*Pick one class from this group and fill it in with classes from this other group*"
    * or "*Build schedules from these classes as long as I can get class A. Otherwise, build scheduels from these other classes.*"
* Adding course descriptions – To allow the site to serve as a one-stop-shop for SLC students during registration, it would be great if I could add in course descriptions. When students search for classes, maybe they could click on the table row to open the course description in a pop-up (think a *quick view* option in online shopping, where you can see the item without leaving the search results page).
* Tags / Search by description / Related courses – Once I have the course description information, I can add the ability to search by terms in the course descriptions or show *related courses* based on tags.
* More schedule control – Add the ability to interact with the schedule to block out times when building schedules. For example:
    * "*I have an internship on Wednesdays in the city, from 10 AM to 5 PM, so don't put any classes during that time.*"
    * or "*I'm not a morning person. Don't put any classes before 11 AM.*"
* Incorporate distribution requirements – Allow users to enter their course history so that the schedule builder can account for credit requirements in each area as well as lecture requirements.

A little more pie-in-the-sky…
* If the site got enough active users, metric information could be provided. For example, when a user searches for a class, the site could tell them how popular a class is among other users of the site.
* Show some possible predictions of next-year's courses based on when and how often courses have been offered in the past. For example:
    * "*Class X has been offered every other fall semester for the past 4 years.*"
    * or "*This is the first time this class has been offered.*"


## Testing & Known Bugs
I've tested the program as I built it. I don't know that I would say that it's really a *finished* product, and there's still more I'd like to add, so I haven't really tested this version *super* thoroughly. That being said, I don't *think* there are really any major bugs – other than those that are kind of addressed in the "Future Improvements" section.
