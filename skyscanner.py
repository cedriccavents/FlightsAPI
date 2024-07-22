import pandas as pd
import requests

def get_config() -> pd.DataFrame:
    """ Skyscanner configurations
    """
    url = "https://skyscanner80.p.rapidapi.com/api/v1/get-config"

    headers = {
        "x-rapidapi-key": "1cddf2f72cmsh326dd619b4969bap1f2cd3jsn4f2dd0f86530",
        "x-rapidapi-host": "skyscanner80.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    res = pd.DataFrame(response.json()['data'])
    return res.sort_values(by='country').reset_index(drop=True)

configs = get_config()

def get_airports_by_location(location_name: str) -> pd.DataFrame:
    """ airports by location
    """
    url = "https://skyscanner80.p.rapidapi.com/api/v1/flights/auto-complete"

    querystring = {
        "query": location_name,
        "market": "UK",
        "locale": "en-GBP"}

    headers = {
        "x-rapidapi-key": "1cddf2f72cmsh326dd619b4969bap1f2cd3jsn4f2dd0f86530",
        "x-rapidapi-host": "skyscanner80.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()['data']
    res = []
    for k in range(len(data)):
        res.append(
            [
                data[k]['id'],
                data[k]['presentation']['title'],
                data[k]['presentation']['suggestionTitle']
            ]
        )
    return pd.DataFrame(res, columns=['id', 'title', 'suggestionTitle'])

def get_roundtrip(from_id: str, to_id: str, depart_dt: str,  return_dt: str, cabin_class: str) -> pd.DataFrame:

    url = "https://skyscanner80.p.rapidapi.com/api/v1/flights/search-roundtrip"

    querystring = {
        "fromId": from_id,
        "toId": to_id,
        "departDate": depart_dt,
        "returnDate": return_dt,
        "adults": "1",
        "cabinClass": cabin_class,
        "currency": "USD",
        "market": "US",
        "locale": "en-US"}

    headers = {
        "x-rapidapi-key": "1cddf2f72cmsh326dd619b4969bap1f2cd3jsn4f2dd0f86530",
        "x-rapidapi-host": "skyscanner80.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()['data']
    retours = data['itineraries']
    res = []
    for k in range(len(retours)):
        res.append(
            [
                retours[k]['id'],
                retours[k]['price']['raw'],

                # first leg
                retours[k]['legs'][0]['origin']['name'],
                retours[k]['legs'][0]['destination']['name'],
                retours[k]['legs'][0]['departure'],
                retours[k]['legs'][0]['arrival'],
                retours[k]['legs'][0]['durationInMinutes'],
                retours[k]['legs'][0]['carriers']['marketing'][0]['name'],

                # second leg
                retours[k]['legs'][1]['origin']['name'],
                retours[k]['legs'][1]['destination']['name'],
                retours[k]['legs'][1]['departure'],
                retours[k]['legs'][1]['arrival'],
                retours[k]['legs'][1]['durationInMinutes'],
                retours[k]['legs'][1]['carriers']['marketing'][0]['name'],
            ]
        )

    res = pd.DataFrame(
        res,
        columns=
        [
            'id', 'raw_price', '1_airport', '1_destination', '1_departure', '1_arrival', '1_duration',
            '1_airline', '2_airport', '2_destination', '2_departure', '2_arrival', '2_duration',
            '2_airline'
        ])
    return res.sort_values(by='raw_price', ascending=True)

# example
get_roundtrip(
    "eyJzIjoiTE9ORCIsImUiOiIyNzU0NDAwOCIsImgiOiIyNzU0NDAwOCJ9",
    "eyJzIjoiSEtUIiwiZSI6IjEwNDEyMDM3OCIsImgiOiIyNzU0MjA2OSJ9",
    "2024-12-10",
    '2024-12-21',
    "economy"
).to_csv(
    r'trips_London_to_Thailand.csv', index=None
)