# cocktail-reviewer-api

This project consists of the creation of an API to manage different beverages, including cocktail recipes and other alcohol-based drinks. The global market has allowed for a wide variety of alcoholic beverages. As such, the consumer might feel overwhelmed when trying to figure out what could align with their taste. This project aims to tackle this issue.

With this API, the user will be able to create new items based on their favorite drinks. In addition, the user can review a drink as many times as they wish, since personal taste might change over time. On top of that, a drink might be prepared differently. Maybe a different gin was used for a Gin Fizz, or maybe the portions were altered. Because of that, the user can review the drink again and add a description of what changed in the newest experiment. The user can review every experiment, giving a score from 0 to 5 stars.

**NOTE: This API is planned for personal use only. This is not going to be a social media to share different cocktails and mixology ideas. If you wish to use this API, you must run it on your own server**

## Planned Tech Stack

The following list of technologies with tech already in use in current version and planned to add as the project goes on. List might be subject to change.

- Python 3.13
  - fastapi
  - boto3
- Docker
- AWS
  - Lambda
  - API Gateway

## Run locally

If you wish to run the project locally you can do it in two ways, either through a python virtual environment (venv) or with Docker. It is recommend to use Docker as this will be the way the project will be uploaded into AWS.

### Run with Docker

This is the recommended way to test and add new features. With Docker installed, just run docker compose up to run the docker compose orchestration.

In order to test it you must have the local [DynamoDB Docker Image](https://hub.docker.com/r/amazon/dynamodb-local).

```Shell
docker compose up --build
```

You can use NoSQL Work Bench to check the data of DynamoDB. Don't forget to add a table named _cocktail-reviewer_. This database run locally in port 8000.

To test the api you can you the browser for the GET requests, use Postman or Swagger in the url [http:http://localhost:8080/docs](http:http://localhost:8080/docs)

# Project Ideas:

- ❌ CRUD operations with different beverages
- ✅ Filter between kind of beverage (Cocktail, Gin, etc)
- ❌ Allow to review beverages
- ❌ Add images to each reviews
