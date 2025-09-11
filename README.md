# barista-api

This project consists of the creation of an API to manage different beverages, including cocktail recipes and other alcohol-based drinks. The global market has allowed for a wide variety of alcoholic beverages. As such, the consumer might feel overwhelmed when trying to figure out what could align with their taste. This project aims to tackle this issue.

With this API, the user will be able to create new items based on their favorite drinks. In addition, the user can review a drink as many times as they wish, since personal taste might change over time. On top of that, a drink might be prepared differently. Maybe a different gin was used for a Gin Fizz, or maybe the portions were altered. Because of that, the user can review the drink again and add a description of what changed in the newest experiment. The user can review every experiment, giving a score from 0 to 5 stars.

**NOTE: This API is planned for personal use only. This is not going to be a social media to share different cocktails and mixology ideas. If you wish to use this API, you must run it on your own server**

## Tech Stack

The following list of technologies with tech already in use in current version and planned to add as the project goes on. List might be subject to change.

- Python 3.13
  - fastapi
  - boto3
- Docker
- AWS
  - Lambda
  - API Gateway

## Run locally

Please use Docker to run the project locally. You will neeed two external docker images

- minio : S3 implementation locally
- dynamodb local : DynamoDB implementation locally

### Run with Docker

This is the recommended way to test and add new features. With Docker installed, just run docker compose up to run the docker compose orchestration.

In order to test it you must have the local [DynamoDB Docker Image](https://hub.docker.com/r/amazon/dynamodb-local) and the [MinioIO Docker Image](https://hub.docker.com/r/minio/minio).

```Shell
docker compose up --build
```

You can use NoSQL Work Bench to check the data of DynamoDB. Don't forget to create the tables. This database run locally in port 8000.

To test the api you can you the browser for the GET requests, use Postman or Swagger in the url [http:http://localhost:8080/docs](http:http://localhost:8080/docs)

You can access minio GUI with the url http://localhost:9090/login

# Testing

Unit and Feature test where added in folder tests/.

To run test simply start the docker compose and in the beggining the tests will run.

# Env

A set of environment variables are necessary to run the project locally. Copy .env.example file to .env and create your own variables. You don't need to have valid access keys to run locally. Just create a random set of characters. For aws_secret_access_key, make sure to be at least 8 characters long, as minio requires it.

Please make sure to create the DynamoDB table in DynamoDB-local and the minio bucket in minio GUI. Set the name of both in the .env file for connection.

# Endpoints

These are the current endpoints in the API

- Beverages

  - GET /beverages -> get all beverages, can filter by beverage type
  - GET /beverages/pk/{pk}/sk/{sk} -> get beverage
  - POST /beverages -> add beverage to bd
  - PUT /beverages/pk/{pk}/sk/{sk} -> edit beverage
  - DELETE /beverages/pk/{pk}/sk/{sk} -> delete beverage

- Beverate Types
  - GET /beverage_types -> get list of beverage types

# Project Ideas:

- ✅ CRUD operations with different beverages
- ✅ Filter between kind of beverage (Cocktail, Gin, etc)
- ✅ Obtain default image if no image is set for beverage
- ✅ Allow to review beverages
- ✅ Add images to each reviews
- ❌ Set default image to cocktail from list of reviews
