.. _contributing:

============
Contributing
============

Contributions are welcome. If you want to contribute, you can join the #enms channel in the networktocode slack (http://networktocode.herokuapp.com/).

For developers
--------------

eNMS uses :

- Black for python code formatting
- Flake8 to make sure that the python code is PEP8-compliant
- Mypy for python static type hinting
- Prettier for javascript code formatting
- Eslint to make sure the javascript code is compliant with google standards for javascript
- Pytest for the test suite.

There is a dedicated ``requirements_dev.txt`` file to install these python libraries:

::

 pip install -r requirements_dev.txt

Before opening a pull request with your changes, you should make sure that:

::

 # your code is black compliant
 # Black is a code formatting enforcement tool; see (https://github.com/ambv/black)
 black --check --verbose .

 # your code is PEP8 (flake8) compliant (python)
 flake8 --config linting/.flake8 .

 # your code is mypy compliant
 # Mypy is a adds static type hinting to Python for the whole project; see (http://mypy-lang.org/)
 mypy --config-file linting/mypy.ini .

 # your code is prettier compliant (javascript)
 npm run prettier

 # your code is eslint compliant (javascript)
 npm run lint
 
 # all the tests are passing
 pytest

If one of these checks fails, so will Travis CI after opening the pull request.

The CI/CD and PR processes are the same, because when you open a PR, this automatically triggers Travis.
Pre-commit is included in the dev requirements, and a pre-commit hook is available, so that each time you commit, it fails if the commit is not black-compliant AND flake8-compliant, AND it automatically reformats your code to be black-compliant (and then you have to recommit).

If you are updating the documentation, you can build a local version of the docs:

::

 # build a local version of the docs
 cd /docs
 make html
