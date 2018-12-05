# MijnErfpacht API Client

## Introduction

Ontsluiting van de REST API van MijnErfpacht.

Beoogde work flow van de applicatie:

       +--------------+
       |              |
       |   Frontend   |
       |              |
       +--------------+
           ^      |
           |      | req       +------------------------+
           |      |           |                        |
           |      +---------> |   TMA middleware       |
     res   |                  |   (adds a SAML token   |
           |                  |   holding the BSN)     |
           |      +---------+ |                        |
           |      |           +------------------------+
           |      v
       +----------------------------------+
       |                                  |
       |   API                            |
       |   (asks the MijnErfpacht         |
       |   for if the BSN has erfpacht)   |
       |                                  |
       +----------------------------------+
           ^      |
           |      |
           |      |
     res   |      |   req (including encrypted BSN)
           |      |
           |      |
           |      v
       +----------------------+
       |                      |
       |   MijnErfpacht API   |
       |   (responds with     |
       |   boolean)           |
       |                      |
       +----------------------+

## Local development

1. Clone repo and 'cd' in
2. Create a virtual env and activate
3. Run command 'pip install -r app/requirements.txt'
4. Set environment variables:
   - export FLASK_APP=app/api/server.py
   - export MIJN_ERFPACHT_ENCRYPTION_VECTOR=<Find on Rattic -> MijnErfpacht encryption vector>
   - export MIJN_ERFPACHT_ENCRYPTION_KEY=<Find on Rattic -> MijnErfpacht encryption key>
   - export MIJN_ERFPACHT_API_KEY=<Find on Rattic -> MijnErfpacht API key>
5. Make sure there is a tma-cert.txt in the '/app/api' directory which holds the TMA Certificate

### Requirements

- Access to the Amsterdam secure Gitlab
- Access to Rattic

### Testing

1. Clone repo and 'cd' in
2. Create a virtual env and activate
3. Run command 'pip install -r app/requirements.txt'
4. Set environment variables: export FLASK_APP=app/api/server.py
5. Run command 'python -m unittest'
