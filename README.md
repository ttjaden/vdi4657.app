# PIEG-Strom-Webtool
Cleaned up code, based on Master Thesis of Darima Motta: https://github.com/darimamotta/thesis_7_ver

## Prepare environment
Download or clone repository:

- `git clone https://github.com/RE-Lab-Projects/PIEG-Strom-Webtool.git`

Create the environment:

- `conda env create --name PIEG-Strom-Webtool python=3.9`

Install dependencies with pip

- `pip install -r requirements.txt`

Create admin user with

- `cd thesis`
- `python manage.py createsuperuser`

## Run code

- `python manage.py runserver`

Open http://127.0.0.1:8000 or http://127.0.0.1:8000/admin in your browser
