# Ai-Assistant-API

AI Assistant API for answering questions using OpenAI.

## Demo

<img src="demo.gif" width="700">

## Features

1. PostgreSQL database running in Docker

2. Endpoints: `/`, `/register`, `/login`, `/me`, `/chat` and `/clear`

3. Openai api with model chat gpt

4. REST API built with Fast api

5. You can communicate with an Ai-Assistant

6. Persistent chat history

7. Deploy my web site: https://ai-assistant-api-gx5a.onrender.com/docs

## Stack

Python 3.12,Docker,Postgresql,Git bash,Sqlalchemy,Openai api,Fast API,python-dotenv

## Project structure

```text
app/
├── routers/
├── models/
├── schemas/
├── crud/
├── database.py
├── config.py
└── main.py
```

## Installation

git bash

```
git clone https://github.com/dil2324/Ai-Assistant-API
cd your_project
pip install -r requirements.txt
copy .env.example .env

docker compose up --build

uvicorn app.main:app --reload

```

## Deploy to Render

The repository includes `render.yaml`, which creates three resources: a FastAPI
web service, a Vite static site, and PostgreSQL. Create a **Blueprint** in
Render from this repository and provide `OPENAI_API` when prompted.

After the first deploy, copy the public URLs shown by Render and set these
environment variables in the corresponding services:

```text
ai-chat-frontend / VITE_API_URL = https://<your-api>.onrender.com
ai-chat-api / FRONTEND_URL = https://<your-frontend>.onrender.com
```

Redeploy both services after saving the variables. `VITE_API_URL` is embedded
in the static frontend during its build; `FRONTEND_URL` tells FastAPI which
browser origin is allowed to call the API.
