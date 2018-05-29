# check-tickets

PyCon CZ tickets checker / Kontrolor správnosti PyCon CZ lístků

## What? Why?

Read [this Pyvec Slack message](https://pyvec.slack.com/archives/C12MPETE1/p1527553169000070).

## Installation

```sh
$ git clone https://github.com/pyvec/check-tickets.git ~/check-tickets
$ cd ~/check-tickets
$ python3 -m venv venv
$ . ./venv/bin/activate
(venv)$ pip install -r requirements.txt
```

## Usage

```sh
(venv)$ python check-tickets.py test_fixtures/tickets.csv test_fixtures/waitlists.csv
```

## Tests

Not ready yet. There are some fixtures in the `test_fixtures` directory and there is `pytest` and `pylama` in the requirements, but in the end having tests seemed like a way too ambitious plan for now.
