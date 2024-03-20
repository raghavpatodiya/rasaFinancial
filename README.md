# rasaFinancial

## How to test ?

- `pip install -r requirements.txt`: Install requirements.
- `rasa train`: Train your Rasa model using your configured pipeline and data.
- `rasa shell`: Test your trained model in the command-line shell as well as interact with your model via Flask.
- `rasa run actions`: Run custom actions defined in actions.py alongside your Rasa server.
- `docker run -p 8000:8000 rasa/duckling`: To run Duckling on Docker.
- run `app.py` with Flask's built-in server.
- run `loc_calculator.py` to activate LOC Counter.

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
