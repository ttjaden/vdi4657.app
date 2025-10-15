# VDI 4657 - Webtool
Complementary Webtool to guideline VDI 4657 - Planning and integration of energy storage systems in energy building systems - Eletrical storage, see:
- Link to guideline: [https://www.vdi.de/richtlinien/details/vdi-4657-blatt-3-planung-und-integration-von-energiespeichern-in-gebaeudeenergiesystemen-elektrische-stromspeicher-ess](https://www.vdi.de/richtlinien/details/vdi-4657-blatt-3-planung-und-integration-von-energiespeichern-in-gebaeudeenergiesystemen-elektrische-stromspeicher-ess)
- Link to Webtool: [https://www.vdi.de/mitgliedschaft/vdi-richtlinien/unsere-richtlinien-highlights/vdi-4657/vdi-4657-webtool](https://www.vdi.de/mitgliedschaft/vdi-richtlinien/unsere-richtlinien-highlights/vdi-4657/vdi-4657-webtool)

# Production use
Use as a docker container with preferred webserver as proxy

- `docker run -dp 8050:8050 ttjaden/vdi4657.app`

# Development

## Prepare environment
Download or clone repository:

- `git clone https://github.com/ttjaden/vdi4657.app.git`

Create the environment:

- `conda env create --name vdi4657.app`

Activate enviroment

- `conda activate vdi4657.app`

Install dependencies with pip

- `pip install -r requirements.txt`

## Run code

- `python src/app.py`

Open http://127.0.0.1:8050 in your browser
