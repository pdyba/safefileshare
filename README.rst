safefileshare
=============

Simple app to share files protected by password.

KickStarted with:  https://github.com/pydanny/cookiecutter-django/

:License: MIT


Specks

1. Transfer files and URL addresses in a secure way.
2. For logged-in users the form accepting the file or the URL that we want to protect.
After sending it to the user, the generated new unique address (within the application) and the generated password should be displayed.
The generated link should be valid for 24 hours.
This part should be covered by tests.
3. After clicking generated link, you should see a form that allows you to enter your password.
If it is compatible with the password generated in the database, then the user is redirected to a protected URL or to download process of the protected file.
The number of correct password additions should be counted for each link.
4. For each logged-in user, the User Agent from which he made the last query, should be remembered, i.e.
refreshed with each request sent, to any sub-page within the system (User Agent is available in the request header).
5. It should also be possible to manage the application using the admin panel,
in particular changing the password assigned to the element.
6. The application also provides APIs similar to created forms,
a secured part for adding new elements, and an unsecured one to enter the password.
7. In addition, a secured endpoint should be created to provide information
on the number of items of each type, added every day, that have been visited at least once (see example).

Tech: Django + Django Rest + Django forms


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Docker
^^^^^^
To run docker use:

::

    $ docker-compose -f local.yml build
    $ docker-compose -f local.yml up



Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy safefileshare

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.


Heroku
^^^^^^

See detailed `cookiecutter-django Heroku documentation`_.

.. _`cookiecutter-django Heroku documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html



Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html



