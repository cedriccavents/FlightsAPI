import pandas as pd
import requests
from typing import Union

class SkyScannerAPI:
    """ class to implement Skyscanner API requests
    """
    def __init__(self, API_KEY):
        self.api_key = API_KEY

    def builder(self, endpoints, querystring: dict[str, Union[str, any]] = {}):
        """
        """
        # base url
        url = f"https://flights-sky.p.rapidapi.com/{endpoints}"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "flights-sky.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        return response

    def config(self) -> pd.DataFrame:
        response = self.builder("get-config")
        res = pd.DataFrame(response.json()['data'])
        return res.sort_values(by='country').reset_index(drop=True)

    def get_airports(self):
        raise NotImplemented

    def get_roundtrip(self, from_id, to_id, depart_dt, return_dt, cabin) -> pd.DataFrame:
        # parameters
        querystring = {
            "fromEntityId": from_id,
            "toEntityId": to_id,
            "departDate": depart_dt,
            "returnDate": return_dt,
            "adults": "1",
            "cabinClass": cabin,
            "currency": "GBP",
            "market": "UK",
            "locale": "en-GB"}

        response = self.builder('flights/search-roundtrip', querystring)
        data = response.json()['data']

        # format data
        retours = data['itineraries']
        res = []
        for k in range(len(retours)):
            res.append(
                [
                    retours[k]['price']['raw'],

                    # first leg
                    retours[k]['legs'][0]['origin']['name'],
                    retours[k]['legs'][0]['destination']['name'],
                    retours[k]['legs'][0]['departure'],
                    retours[k]['legs'][0]['arrival'],
                    retours[k]['legs'][0]['durationInMinutes'],
                    len(retours[k]['legs'][0]['segments'])-1,
                    retours[k]['legs'][0]['carriers']['marketing'][0]['name'],

                    # second leg
                    retours[k]['legs'][1]['origin']['name'],
                    retours[k]['legs'][1]['destination']['name'],
                    retours[k]['legs'][1]['departure'],
                    retours[k]['legs'][1]['arrival'],
                    retours[k]['legs'][1]['durationInMinutes'],
                    len(retours[k]['legs'][1]['segments'])-1,
                    retours[k]['legs'][1]['carriers']['marketing'][0]['name'],
                ]
            )

        res = pd.DataFrame(
            res,
            columns=
            [
                'raw_price', '1_airport', '1_destination', '1_departure', '1_arrival', '1_duration',
                '1_stops', '1_airline', '2_airport', '2_destination', '2_departure', '2_arrival', '2_duration',
                '2_stops', '2_airline'
            ])

        return res.sort_values(by='raw_price', ascending=True)