# Place Name Disambiguation

This repo contains some scripts that enable collecting NER-entities and geocodes for a corpus in a folder, along ideas proposed in
> Ardanuy, M. C., & Sporleder, C. (2017, June). Toponym disambiguation in historical documents using semantic and geographic features. In Proceedings of the 2nd international conference on digital access to textual cultural heritage (pp. 175-180).

The main entry point is `extract.py`, whereas `icab_parser.py` is a helper script that is not part of `extract.py`s workflow.

## Setup

Setup a virtualenv with Python 3.4 (or higher > untested):

```bash
virtualenv .env -p python3.4 --prompt "(pnd) "
```

activate the virtualenv:

```bash
source .env/bin/activate (.env/Scripts/activate on Windows)
```

install requirements:

```python
pip install -r requirements.txt
```

## `extract.py`

`Extract.py` expects certain parameters, to get an overview of these, go:

```python
python extract.py --help
```

Note to self: document these parameters here once the script is in a more final state.

One thing is important to note:
Before `extract.py` can do anything for you, you need to make sure you have exported some authentication details required to collect geocodes. In particular, you need a [API Key for Google]() and [a username for GeoNames](http://www.geonames.org/export/web-services.html). More information on what is needed exactly can be found in the documentation of [the magnificent geocoder library](https://geocoder.readthedocs.io/index.html), which is used here (in `geocoding.py`) to collect geocode data.

Make sure you have the acccounts and keys and export them as environment variables before calling `extract.py`. For example:

```bash
export GOOGLE_API_KEY=<your_api_key>
```

## `icab_parser.py`

`icab_parser.py` is a very basic parser made to extract the text from the `.sgm` (XML-like) files of the [I-CAB](http://ontotext.fbk.eu/icab.html) corpus.
