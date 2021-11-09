# MijnErfpacht API Client

A REST API which discloses the MijnErfpacht REST API.

### Testing

1. Clone repo
2. Create a virtual env and activate
3. Run `pip install -r app/requirements.txt`
4. `cd app`
5. Run `python -m unittest`

### Updating dependencies

Direct dependencies are specified in `requirements-root.txt`. These should not have pinned a version (except when needed)

- `pip install -r requirements-root.txt`
- `pip freeze > requirements.txt`
