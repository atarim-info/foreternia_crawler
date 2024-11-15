# Task: Build a web crawler that gets data from a secure forum

You need to create a crawler that scans, downloads and saves into files.
Fetch as many documents as possible from this URL: https://foreternia.com/community/announcement-forum
## Requirements:
- Python 3.9+
- Use concurrency / threading (up to 2 connections at the same time)
- Use Typer in order to create a simple CLI.

Data structure:
    - The files will be saved in the ./data/ directory
    - Each unique thread will have a filename prefix (chosen by you).
    - Each post will be a JSON file with the page link, title, published time and content.

## Pre-requisites
You must have following software on your machine,
- Python 3.x or beyond
- pipenv package installed

## Setup (Local)
Installa python packages referred in application.
```
pipenv install
```
Activates virualenv.
```
pipenv shell
pipenv sync
```
## Run Tests
Test locally
```
pytest tests/
```

## Run Application
Start applciation locally
```
python src/app.py
```

## Create Docker image

```
docker build -t crawler:latest .
```