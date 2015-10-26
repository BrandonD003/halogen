Halogen
=======

Description
-----------

Install
-------

    $ virtualenv halogen
    $ source halogen/bin/activate.csh
    $ pip install -r requirements.txt
    $ pip install -e ./

Run
---

    $ python bin/runserver.py --db <db_name>

Go to http://localhost:5000 in your browser

Notes
-----

This hasn't been tested recently. Care should be taken


Relevant Documentation
----------------------

 - [Flask's "AJAX with jQuery"](http://flask.pocoo.org/docs/patterns/jquery/)
 - [Flask's MethodView class](http://flask.pocoo.org/docs/views/#method-based-dispatching)
 - [Flask's URL Routing](http://flask.pocoo.org/docs/api/#url-route-registrations)
 - [WTForms's Field class](http://wtforms.simplecodes.com/docs/1.0.2/fields.html#the-field-base-class)
 - [jQuery's .ajax() method](http://api.jquery.com/jQuery.ajax/)
