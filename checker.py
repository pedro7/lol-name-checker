from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests import HTTPError, get
from urllib.parse import quote

class Checker:
    def __init__(self, key, server):
        servers = {'BR': 'br1', 'EUNE': 'eun1', 'EUW': 'euw1', 'LAN': 'la1', 'LAS': 'la2', 'NA': 'na1', 'OCE': 'oc1', 'RU': 'ru', 'TR': 'tr1', 'JP': 'jp1', 'KR': 'kr'}
        self._key = key
        self._server = servers[server.upper()]

    def check_name(self, name):
        if len(name) < 3 or len(name) > 16:
            return 'The name must have 3 to 16 characters'
        try:
            name_availability_datetime = self.get_name_availability_datetime(name)
        except HTTPError as err:
            status_code = err.response.status_code
            if (status_code == 404):
                return 'The name is available for new/existent accounts!'
            elif (status_code == 403):
                return 'Invalid or expired key'
            elif (status_code == 429):
                return 'Exceeded number of requests'
            else:
                raise
        if (name_availability_datetime > datetime.now()):
            return f'The name will be available at: {name_availability_datetime}. Exactly {name_availability_datetime - datetime.now()} from now!'
        else:
            return 'The name is available for existent accounts!'

    def get_name_availability_datetime(self, name):
        summoner_dto = self._get_summoner_dto(name)
        return self._get_name_cleanup_datetime(summoner_dto['revisionDate'], summoner_dto['summonerLevel'])

    def _get_summoner_dto(self, name):
        try:
            summoner_dto = get(f'https://{self._server}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{quote(name)}?api_key={self._key}')
            summoner_dto.raise_for_status()
        except HTTPError:
            raise
        return summoner_dto.json()

    def _get_name_cleanup_datetime(self, name_timestamp, level):
        if level >= 30:
            return datetime.fromtimestamp(name_timestamp / 1000) + relativedelta(months=+30)
        elif level <= 6:
            return datetime.fromtimestamp(name_timestamp / 1000) + relativedelta(months=+6)
        else:
            return datetime.fromtimestamp(name_timestamp / 1000) + relativedelta(months=+level)
