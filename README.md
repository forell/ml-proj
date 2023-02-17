(A Mediocre Attempt at) Train Delay Prediction
==============================================

This repository contains:
- a list of relevant resources (data, tools) in [`resources.md`](/resources.md),
- a set of data processing utility scripts in [`data_processing`](/data_processing),
- some preprocessed data that's annoying or time-consuming to obtain in [`data`](/data),
- finally, the script that performs regression on the processed data: [`reg.py`](/reg.py).

Data Processing
---------------

### IMGW

The `czystapogoda.py` script can download and process data made available by
the [IMGW](https://danepubliczne.imgw.pl), and will attempt to cache the source
zip files locally. It outputs data to stdout in the JSON Lines format, with one
JSON object for each measurement.

For example, to process the 2022 data for the two stations in Wrocław and
Częstochowa, you can run:
```sh
python3 data_processing/czystapogoda.py –-download 2022_{424,550}_s.zip > weather.jsonl
```

[The file naming rules are described here](https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/Opis.txt).
Notably, the format is different for `$(date +%Y)`.

### IPA

Train delay data can be obtained from
[InfoPasażer Archiver](http://ipa.lovethosetrains.com/).
```sh
wget http://ipa.lovethosetrains.com/ipa_21_22.7z
```

Since this dataset doesn't include station coordinates, they need to be
obtained separately based on the station names, e.g. from OpenStreetMap. As
that may require downloading and processing a lot of data to eventually extract
a tiny fraction of it, or perhaps alternatively making many API requests,
preprocessed coordinate data is available as
[`data/railway_stations.csv`](/data/railway_stations.csv).

Nonetheless, scripts to perform these steps manually on OSM data are available:
- [`extract_stations_from_ipa.py`](/data_processing/extract_stations_from_ipa.py)
- [`preprocess_osm_data.sh`](/data_processing/preprocess_osm_data.sh)
- [`train_station_coords.py`](/data_processing/train_station_coords.py)

For possible data sources and dependencies you may want to check out
[`resources.md`](/resources.md).

Finally, the [`train_parser.py`](/data_processing/train_parser.py) script can
be used to flatten IPA data into a simple list of coordinates, dates and
delays. Assuming `ipa_21_22` is the extracted IPA data, you can produce a CSV
file with the delays as follows:
```sh
python3 data_processing/train_parser.py ipa_21_22 delays.csv
```

### Combining The Data

To combine weather and delay data into _X_ and _y_:
```sh
python data_processing/combine.py -x data/X.csv -y data/y.csv \
    -d delays.csv -w weather.jsonl
```
Note: The script won't work correctly if a date mentioned in `delays.csv` is
not actually present in `weather.jsonl` for some weather station that otherwise
appears in it, or if there is no data available for this data at all.

Regression
----------

Regression on prepared data has been implemented in [`reg.py`](/reg.py).
As of now experimentation is most easily performed by editing this file.

TODO: Anybody feel like making a Jupyter Notebook or similar with helpful
visualisations and examples with output? Maybe upload some fully digested
data for regression somewhere as well.
