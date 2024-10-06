# Setup

```bash
pip install -r requirements.txt
```

# Running the app

```bash
flask run --debug
```

# Test queries

```bash
curl -X POST http://localhost:5000/api/projects -H 'Content-Type: application/json' -d '{"query": "projects launched by prestige after 2022"}'

curl -X POST http://localhost:5000/api/projects -H 'Content-Type: application/json' -d '{"query": "projects launched by prestige after 2023 in varthur"}'
```
