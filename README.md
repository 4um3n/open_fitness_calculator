# OpenFitnessCalculator Django App

This is OpenFitnessCalculator Django app that uses [OpenFoodRepoAPI](https://www.foodrepo.org/api-docs/swaggers/v3#/) to search for food. 

You can view a working version of this app [here](https://openfitnesscalculator.tk/).

Running this app on your local machine in development will work as
well.


## Building
It is best to use the python `python3-venv` tool to build locally:

<pre>
$ touch .env # put your environment variables here: <a href="https://github.com/4um3n/open_fitness_calculator/blob/main/example.env" >example</a>
$ mkdir -p venv
$ python3 -m venv .venv/
$ source venv/bin/activate
$ source .env
$ pip3 install -r requirements.txt
$ python manage.py runserver
</pre>

Then visit `http://localhost:8000` to view the app.


## Tests

To run the tests, `cd` into the directory where `manage.py` is:
```sh
(venv) 
$ python manage.py test
```


## Get involved!

I am happy to receive bug reports, fixes, documentation enhancements,
and other improvements.

Please report bugs via the
[github issue tracker](https://github.com/4um3n/open_fitness_calculator/issues).

Master [git repository](https://github.com/4um3n/open_fitness_calculator):

* `git clone https://github.com/4um3n/open_fitness_calculator.git`

## Licensing

This library is MIT-licensed.

