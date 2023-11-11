status-map
~~~~~~~~~~

|version-badge| |pyversion-badge| |license-badge| |CI-badge| |cov-badge|

Handle status maps and status transitions easily.

I fork this project to add the possibility to add conditions to the transitions. Is a basic implementation, but works for me.

This is a Fork of: https://github.com/lamenezes/status-map
Thanks to the original author for the great work!
-----------------

How to use
==========

Install
-------

status-map is available on PyPI:

.. code-block:: bash

    $ pip install status-map-validator


Basic Usage
-----------

Define your status map by creating a dict containing all the status and its possible transitions.

E.g. we can define a task workflow as follows:

.. code-block:: python

    from status_map import StatusMap

    status_map = StatusMap({
        'todo': ['doing'],
        'doing': ['todo', 'done'],
        'done': [],  # assuming a task once finished can't go back to other status
    })

.. code-block:: python

    from status_map import StatusMap

    def condition_draft_to_pending():
        pass
    
    def condition_pending_to_approved():
        pass
    
    status_map = StatusMap({
        'draft': {"pending": {"validation": [condition_draft_to_pending]}},
        'pending': {"approved": {"validation": [condition_pending_to_approved], "canceled": {}}},
        'approved': ["done", "canceled"],
    })


We can validate if a status transition is valid:

.. code-block:: python

    >> status_map.validate_transition(from_status='todo', to_status='done')
    Traceback (most recent call last):
    ...
    status_map.exceptions.TransitionNotFoundError: transition from todo to done not found


Passing an inexistent status raises an exception:

.. code-block:: python

    >> status_map.validate_transition('todo', 'foo')
    Traceback (most recent call last):
    ...
    status_map.exceptions.StatusNotFoundError: to status foo not found


The validation raises a different exception if the to_status has already appeared before:

.. code-block:: python

    >> status_map.validate_transition('done', 'todo')
    Traceback (most recent call last):
    ...
    status_map.exceptions.PastTransitionError: transition from done to todo should have happened in the past

It is also possible to obtain conditions that were set in a transition:

.. code-block:: python

    >> status_map.get_conditions('draft', 'pending')
    func = <function __main__.condition_draft_to_pending()>
    func()

    >> status_map.get_conditions('pending', 'approved')
    method = <function __main__.condition_pending_to_approved()>
    func()


Setting up for local development
--------------------------------

We use poetry_ to manage dependencies, so make sure you have it installed.

Roll up your virtual enviroment using your favorite tool and install development dependencies:

.. code-block:: bash

    $ poetry install

Install pre-commit hooks:

.. code-block:: bash

    $ pre-commit install


Run tests by evoking pytest:

.. code-block:: bash

    $ pytest

That's it! You're ready from development.


.. _poetry: https://github.com/sdispater/poetry

.. |version-badge| image:: https://badge.fury.io/py/status-map.svg
    :target: https://pypi.org/project/status-map/

.. |pyversion-badge| image:: https://img.shields.io/badge/python-3.6,3.7,3.8,3.9,3.10-blue.svg
    :target: https://github.com/lamenezes/status-map

.. |license-badge| image:: https://img.shields.io/github/license/lamenezes/status-map.svg
    :target: https://github.com/lamenezes/status-map/blob/master/LICENSE

.. |CI-badge| image:: https://circleci.com/gh/lamenezes/status-map.svg?style=shield
    :target: https://circleci.com/gh/lamenezes/status-map

.. |cov-badge| image:: https://codecov.io/gh/lamenezes/status-map/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/lamenezes/status-map
