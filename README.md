# VDI 4657 - Webtool
Complementary Webtool to guideline VDI 4657 - Planning and integration of energy storage systems in energy building systems - Eletrical storage, see: https://www.vdi.de/richtlinien/details/vdi-4657-blatt-3-planung-und-integration-von-energiespeichern-in-gebaeudeenergiesystemen-elektrische-stromspeicher-ess

**First release planned for Q1/2023**

# Development

## Prepare environment
Download or clone repository:

- `git clone https://github.com/RE-Lab-Projects/PIEG-Strom-Webtool.git`

Create the environment:

- `conda env create --name vdi4657.app`

Activate enviroment

- `conda activate vdi4657.app`

Install dependencies with pip

- `pip install -r requirements.txt`

## Run code

- `python src/app.py`

Open http://127.0.0.1:8050 in your browser
