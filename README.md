# Tumelo Take Home

## Installing
- install python 3.12
- install sqlite
- run `pip install poetry`
- run `poetry install`

An sqlite db is provided but if you wish to recreate it, run:
- run `python -m scripts.createDb`
- run `python -m scripts.loadDataToDb`

## Running
- run `make run`
- api docs can be found at `/redoc`

## Testing
- `make e2e-test`
- `make lint`
- `make type-check`