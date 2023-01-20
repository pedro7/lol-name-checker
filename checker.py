from datetime import datetime
from dateutil.relativedelta import relativedelta
from re import search
from requests import get
from urllib.parse import quote


class Checker:
    def __init__(self, server, key=None):
        platforms = {
            'BR': 'br1', 'EUNE': 'eun1', 'EUW': 'euw1', 'LAN': 'la1', 'LAS': 'la2', 'NA': 'na1', 'OCE': 'oc1',
            'RU': 'ru', 'TR': 'tr1', 'JP': 'jp1', 'KR': 'kr', 'PH': 'ph2', 'SG': 'sg2', 'TW': 'tw2', 'TH': 'th2',
            'VN': 'vn2'
        }
        self._platform = platforms[server.upper()]
        self._server = server
        self._key = key

    def get_name_availability(self, name):
        if self._key:
            return self._get_name_availability_with_key(name)
        else:
            return self._get_name_availability_without_key(name)

    def _get_name_availability_with_key(self, name):
        summoner_data = self._get_summoner_data(name)
        return self._get_cleanup_date(summoner_data['summonerLevel'], summoner_data['revisionDate'])

    def _get_summoner_data(self, name):
        summoner_data = get(
            f'https://{self._platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{quote(name)}?'
            f'api_key={self._key}'
        )
        summoner_data.raise_for_status()
        return summoner_data.json()

    @staticmethod
    def _get_cleanup_date(level, timestamp):
        if level >= 30:
            return datetime.fromtimestamp(timestamp / 1000) + relativedelta(months=30)
        elif level <= 6:
            return datetime.fromtimestamp(timestamp / 1000) + relativedelta(months=6)
        else:
            return datetime.fromtimestamp(timestamp / 1000) + relativedelta(months=level)

    def _get_name_availability_without_key(self, name):
        lolnames_gg_html = self._get_lolnames_gg_html(name)
        last_game, cleanup_date = self._get_name_availability_data(lolnames_gg_html)
        return self._build_name_availability(last_game, cleanup_date)

    def _get_lolnames_gg_html(self, name):
        return get(f'https://lolnames.gg/en/{self._server}/{format(name)}/', headers={'User-Agent': 'N'}).text

    @staticmethod
    def _get_name_availability_data(html):
        last_game = search('Last game: [^<]*', html)
        if last_game:
            last_game = last_game.group()[23:]
        else:
            raise ValueError('last game not found')
        cleanup_date = search('Cleanup date [^:]*: [^<]*', html).group().strip()[-11:]
        return [last_game, cleanup_date]

    @staticmethod
    def _build_name_availability(last_game, cleanup_date):
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10,
            'Nov': 11, 'Dec': 12
        }
        return datetime(
            int(cleanup_date[7:11]), months[cleanup_date[3:6]], int(cleanup_date[:2]), int(last_game[:2]),
            int(last_game[3:5]), int(last_game[6:8])
        )
