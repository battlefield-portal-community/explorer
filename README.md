# Explorer
Centralized Database of all Available Experiences in portal,
blockly data will not be stored in this database unless shared by the creator.


# Architecture

## Experience Hoarder
The module that will be responsible for hoarding experiences from the portal. 
It will be a long-running process that will keep hoarding experiences from the portal and storing them in the database.
Uses a self-hosted instance of GameTools API to hoard experiences.
Has no public facing API, only internal API for the GameTools API to communicate with the database.
Data stored in the database will be used by the [Public API](./api) module to serve a REST API.

![[Architecture](https://excalidraw.com/#json=zJN6t5B1rot8v6FtEyd8G,yvyZF2LtlwYL15NjnyYb_Q)](./data/experience_horder_arch.png)

# Terminology
- **Experience**: A single experience on https://portal.battlefield.com/
- **code**: A unique identifier for an experience, i.e. the Share Code or Experience Code
  - `AA1D3K`
  - Wherever the word "code" is used it will mean either the Share Code or Experience Code.

## API
A fastapi instance that will query the database and serve a REST API to the public.
### Todo
- [ ] Add more details
- [ ] Add API documentation
- [ ] Add API schema

## Frontend
A frontend to interact with the API. 
### Todo
- [ ] Add more details
- [ ] decide on the tech stack


## Local Development
### Prerequisites
- populate the `.env` file with the required environment variables
  - ```
    DB_CONNECTION_URL=
    MESSAGE_BROKER_URL=
    POSTGRES_DB=
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    ```
- Install docker-compose
- run `docker-compose -f docker-compose -f <app>/docker-compose.yml up -d` to start the respective app.
