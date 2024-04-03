#!/usr/bin/env python3

import ast
import csv
import datetime
import json
import os
import re
import urllib.parse
from typing import TypedDict

import requests

jwt = os.environ['API_READ_ACCESS_TOKEN']
headers = {"accept": "application/json", "Authorization": f'Bearer {jwt}'}

ryot_json = []

class SeenHistory(TypedDict):
    show_season_number: int
    show_episode_number: int
    progress: int
    ended_on: str

def compute_seen_history(tmdb_id: str, s_e: list[int]) -> SeenHistory:
    # s_e contains the last watched season (index 0) and the last watched episode (index 1)
    # Here we would actually need to find how many seasons there are and how many episodes per season
    # We keep setting the episodes to progress = 100 until we match the season and episode stored in
    # s_e list.
    # The method should rather return a list of SeenHistory
    history: SeenHistory = {
        "show_season_number": s_e[0],
        "show_episode_number": s_e[1],
        "progress": 0,
        "ended_on": ""
    }
    now = datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds')

    show_url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?language=en-US'
    response = requests.get(show_url, headers=headers)
    res = response.json()
    last_season, last_episode = res["last_episode_to_air"]["season_number"], res["last_episode_to_air"]["episode_number"]
    if last_season == s_e[0] and last_episode == s_e[1]:
        history["progress"] = 100
        history["ended_on"] = now
        return history

    return history

in_another_file = set()
processed = {}
with open('tracking-prod-records-v2.csv', newline='') as csvfile:
    linereaeder = csv.DictReader(csvfile)
    for row in linereaeder:
        if row['series_name'] != '' and row["series_name"] not in processed and row["series_name"]:
            if row['most_recent_ep_watched'] != '':
                mapElem = row['most_recent_ep_watched']
                mapElem = mapElem.replace("[", "{").replace("]", "}").replace("map", "").replace(" ", ", ")
                mapElem = re.sub(r'(\d{4}-\d\d-\d\dT\d\d):(\d\d):(\d\dZ)', r'\1.\2.\3', mapElem)
                mapElem = re.sub(r'([A-Za-z0-9_\-\+\.]+):([A-Za-z0-9_\-\+\.<>:]+)', r'"\1":"\2"', mapElem)
                d = ast.literal_eval(mapElem)
                processed[row["series_name"]] = [int(d["s_no"]), int(d["ep_no"])]
                if row["series_name"] in in_another_file:
                    in_another_file.remove(row["series_name"])
            else:
                in_another_file.add(row["series_name"])

with open('seen_episode_source.csv', newline='') as csvfile:
    linereaeder = csv.DictReader(csvfile)
    for row in linereaeder:
        show_name = row["tv_show_name"]
        if show_name not in processed:
            processed[show_name] = [int(row["episode_season_number"]), int(row["episode_number"])]
            in_another_file.remove(show_name)
            continue
        season = int(row["episode_season_number"])
        episode = int(row["episode_number"])
        if processed[show_name][0] < season:
            processed[show_name][0] = season
        if processed[show_name][1] < episode:
            processed[show_name][1] = episode


for show, s_e in processed.items():    
    escaped = urllib.parse.quote(show)
    url = f'https://api.themoviedb.org/3/search/tv?query={escaped}&include_adult=false&language=en-US&page=1'

    response = requests.get(url, headers=headers)
    res = response.json()
    if "results" not in res or len(res["results"]) == 0:
        print(f'{show} not found')
        continue
    matching_series = list(filter(lambda series: series["name"] == show, res["results"]))
    if len(matching_series) == 0:
        print(f'{show} not found')
        continue

    tmbd_id = matching_series[0]["id"]
    if tmbd_id == 0:
        print(f'{show} has no TMDB ID')
        continue

    ryot_json.append({
        "collections": [],
        "identifier": tmbd_id,
        "lot": "Show",
        "reviews": [],
        "source": "Tmdb",
        "source_id": tmbd_id,
        # To fix, call compute_seen_history
        "seen_history": []
    })

with open('ryot_data.json', 'w') as rf:
    json.dump(ryot_json, rf)

# What remains in in_another_file is probably the series we set "To watch"
# for to_watch in in_another_file:
#     print(f'To start watching {to_watch}')