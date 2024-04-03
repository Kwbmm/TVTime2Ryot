# TVTime2Ryot
An import script to convert your TVTime data to a Ryot compatible JSON

# Requirements and install

  - Python 3
  - TheMovieDB API key -> to be set in `.env` (the file will be gen during install)
  - Your TVTime data. You can reach TVTime and ask them to give you the data thanks to GDPR

About your TVTime data: you will receive a lot of CSV files. We only need 3 of them: `seen_episode_source.csv`, `traking-prod-records-v2.csv` and (maybe) `tracking-prod-records.csv`.

Install by running `make install`. It will create a virtual environment and download the external require libraries.

# Runnig the script

  1. `source .venv/bin/activate`
  2. `./main.py`

It will output a file called `ryot_data.json` that you can import in Ryot.

Currently, the script is not complete. 2 points remain to be solved:

  - Method `compute_seen_history` needs to be finished according to the comments I left
  - Is `tracking-prod-records.csv` file useful for anything? It doesn't seem so to me