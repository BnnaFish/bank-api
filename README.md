# bank-api

Sandbox project with simple bank service api.
The idea is to test fresh SQLAlchemy 2.0 with asynchronous interface.

# Model

3 simple entities:

- user: name, last, email
- wallet: bank account with current integer balance with UUID
- transaction: DEPOSIT or WITHDRAW certain amount for a given wallet

# API

- user POST
- wallet POST GET
- transaction POST GET
- transactions GET - filter by created time


# HowTo

To run tests just:

``` bash
make dc.test_integration
```

linters:

``` bash
make flake8
make mypy
```

Other options placed in Makefile

# HowTo make it production ready
- remove Base.metadata.drop_all in startups/databases. This is just a simplification for tests. In real productions it will drop all data in DB.
- add migrations via e.g. Alembic
- add Sentry
- add Prometheus
- add logger instead of print
- add OAuth or jwt session manager to authorize user in real bank service
