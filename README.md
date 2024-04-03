# rasaFinancial

## How to test ?

- `pip install -r requirements.txt`: Install requirements.
- `rasa train`: Train your Rasa model using your configured pipeline and data.
- `rasa shell`: Test your trained model in the command-line shell as well as interact with your model via Flask.
- `rasa run actions`: Run custom actions defined in actions.py alongside your Rasa server.
- `docker run -p 8000:8000 rasa/duckling`: To run Duckling on Docker.
- run `app.py` with Flask's built-in server.
- run `loc_calculator.py` to activate LOC Counter.
- Set up PostgreSQL & PgAdmin4, then from the query tool run these queries:
- `CREATE USER username WITH PASSWORD 'password';`
- `CREATE DATABASE db_name;`
- `GRANT ALL PRIVILEGES ON DATABASE db_name TO username;`
- `GRANT ALL PRIVILEGES ON SCHEMA public TO username;`
- To connect to Database from Flask app:
- `flask db init`
- `flask db migrate -m "Initial migration"`
- `flask db upgrade`
- To check if Database is connected:
- `SELECT * FROM "user";`
- `SELECT * FROM "reported_conversations";`

## .env file format

- `ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key`
- `DB_USERNAME=username`
- `DB_PASSWORD=password`
- `DB_NAME=db_name`
- `SECRET_KEY=your_secret_key` get your secret key using this command `print(os.urandom(24))`
- `MAIL_USERNAME=your_project_email_id`
- `MAIL_PASSWORD=your_google_app_password` to get this, create a google app.
- `ROOT_DIRECTORY=path_to_your_root_directory` for LOC Counter

## General Commands

- `rasa init`: Initialize a new Rasa project.
- `rasa run`: Run the Rasa server to interact with your model via REST API.
- `rasa run --enable-api`: Run the Rasa server with HTTP API enabled.
- `docker ps`: List all active Docker containers.
- `docker kill [container_name]`: Kill a specific Docker container.
- `rasa train nlu`: Train the NLU (Natural Language Understanding) model only, focusing on intents.
- `rasa shell nlu`: Test the NLU model by checking intent confidence scores for a given query.
- `rasa shell -m models\older-model-name`: To run an older model.
- `rasa data validate`: Validate your domain, NLU, and story data for any conflicts or inconsistencies.
- `rasa test`: Run tests on your Rasa model and evaluate the results.
