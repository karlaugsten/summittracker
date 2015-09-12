== Setup ==
requires Python2.7
1. Install virtual env
pip install virtualenv
2. Create virtual env
python -m virtualenv env
2. Install dependencies
env/bin/pip install -r requirements.txt
3. Add secrets
create a secrets.py file with a variable mongo_db_connection_string
Please ask me for the connection string, or create your own mongodb
3. Run the server locally
env/bin/python runserver.py
