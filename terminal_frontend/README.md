# Overview
This README explains how to run the terminal frontends for Suggest Anything.

It assumes use of the dev branch of both core-recommendar and chancog.

```console
cd core-recommender/terminal_frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


# Installations
Clone the dev branch of core-recommender:

git clone -b dev https://github.com/Channel-Cognition/core-recommender

Make a virtual environment (the syntax will vary slightly by OS and terminal; the following steps are for Windows cmd):

```console
cd core-recommender/terminal_frontend
python -m venv venv
venv\Scripts\activate
```

Use pip to install the dev branch of chancog:

```console
pip install git+https://github.com/Channel-Cognition/chancog@dev
```

Add a .env file in the active directory (/terminal_frontend) with the necessary variables defined.

# Run a frontend
To run the non-asynchronous terminal frontend:

```console
python run_terminal_frontend.py
```

To run the asynchronous terminal frontend:

```console
python run_async_terminal_frontend.py
```