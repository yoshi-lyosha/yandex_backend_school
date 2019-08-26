### How to start
```bash
uvicorn app.main:app --reload
```

or by docker-compose
```bash
docker-compose build
docker-compose up
```


### Run test
```bash
PYTHONPATH=${PWD} SERVER_HOST=localhost SERVER_PORT=8000 pytest -v --tb=short app/tests/ -x
```