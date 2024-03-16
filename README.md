# rasaFinancial

## Commands

- `pip install -r requirements.txt`: install requirements
- `rasa init`: Initialize a new Rasa project.
- `rasa train`: Train your Rasa model using your configured pipeline and data.
- `rasa shell`: Test your trained model in the command-line shell.
- `rasa run`: Run the Rasa server to interact with your model via REST API.
- `rasa run --enable-api`: Run the Rasa server with HTTP API enabled.
- `rasa run actions`: Run custom actions defined in actions.py alongside your Rasa server.
- To run Duckling on Docker:
- `docker ps`: List all active Docker containers.
- `docker kill [container_name]`: Kill a specific Docker container.
- `rasa train nlu`: Train the NLU (Natural Language Understanding) model only, focusing on intents.
- `rasa shell nlu`: Test the NLU model by checking intent confidence scores for a given query.
- To run an older model:
- `rasa data validate`: Validate your domain, NLU, and story data for any conflicts or inconsistencies.
- `rasa test`: Run tests on your Rasa model and evaluate the results.
