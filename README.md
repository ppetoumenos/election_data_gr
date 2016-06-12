# election_data_gr

Data are aggregated at the municipal unit, municipality, or district level.
Each data point provides votes per party, registered/valid/invalid/blank votes, and number of polling stations.
For the moment there are no results for individual polling stations or for individual candidates.

The data are located in the csv files, whose names follow the format:
<ElectionDate YYYYMMDD>\_<lvl>.csv
lvl is the administrative level -> municipal\_unit, municipality, or district.

The files are encoded in UTF-8.

To collect fresh data from the official election website and reproduce the data in the csv files, run:
python ./parser.py


