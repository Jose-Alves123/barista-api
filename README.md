# cocktail-reviewer-api

This project consists of the creation of an API to manage different beverages, including cocktail recipes and other alcohol-based drinks. The global market has allowed for a wide variety of alcoholic beverages. As such, the consumer might feel overwhelmed when trying to figure out what could align with their taste. This project aims to tackle this issue.

With this API, the user will be able to create new items based on their favorite drinks. In addition, the user can review a drink as many times as they wish, since personal taste might change over time. On top of that, a drink might be prepared differently. Maybe a different gin was used for a Gin Fizz, or maybe the portions were altered. Because of that, the user can review the drink again and add a description of what changed in the newest experiment. The user can review every experiment, giving a score from 0 to 5 stars.

**NOTE: This API is planned for personal use only. This is not going to be a social media to share different cocktails and mixology ideas. If you wish to use this API, you must run it on your own server**

<hr/>

## Planned Tech Stack

The following list of technologies with tech already in use in current version and planned to add as the project goes on. List might be subject to change.

- Python 3.13
  - fastapi
  - boto3
- Docker
- AWS
  - Lambda
  - API Gateway

<hr/>

## Run locally

If you wish to run the project locally you can do it in two ways, either through a python virtual environment (venv) or with Docker. It is recommend to use Docker as this will be the way the project will be uploaded into AWS.

### Run with venv

Follow the following steps if you wish to run the project with a python3 venv. The server will be running in localhost:8000

```Shell
# inside the project root

python -m venv ./.venv # create venv

source ./.venv/bin/activate # start venv

pip install -r ./requirements.txt # add dependencies

fastapi dev main.py # start running server
```

### Run with Docker

This is the recommended way to test and add new features. With Docker installed, follow this series of commands

```Shell
docker build -t cocktail-reviewer-api .

docker run -dp 8001:8001  cocktail-reviewer-api
```
