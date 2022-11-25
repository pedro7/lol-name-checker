from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests import HTTPError, get
from urllib.parse import quote

class Checker:
    def __init__(self, key : str, server : str):
        server = server.upper()
        servers = \
        {
            'BR':   ['br1', 'americas'],
            'EUNE': ['eun1', 'europe'],
            'EUW':  ['euw1', 'europe'],
            'LAN':  ['la1', 'americas'],
            'LAS':  ['la2', 'americas'],
            'NA':   ['na1', 'americas'],
            'OCE':  ['oc1', 'sea'],
            'RU':   ['ru', 'asia'],
            'TR':   ['tr1', 'europe'],
            'JP':   ['jp1', 'asia'],
            'KR':   ['kr', 'asia']
        }
        self.__key = key
        self.__server = servers[server][0]
        self.__region = servers[server][1]

    def check_name(self, name):
        if len(name) < 3 or len(name) > 16:
            return 'The name must have 3 to 16 characters'
        try:
            name_availability_datetime = self.get_name_availability_datetime(name)
        except HTTPError as err:
            if (err.response.status_code == 404):
                return 'The name is available for new/existent accounts!'
            elif (err.response.status_code == 403):
                return 'Invalid or expired key'
            elif (err.response.status_code == 429):
                return 'Exceeded number of requests'
            else:
                raise
        if (name_availability_datetime > datetime.now()):
            return f'The name will be available at: {name_availability_datetime}. Exactly {name_availability_datetime - datetime.now()} from now!'
        else:
            return 'The name is available for existent accounts!'

    def get_name_availability_datetime(self, name):
        summoner_dto = self.__get_summoner_dto(name)
        last_match_timestamp = self.__get_last_match_timestamp(summoner_dto['puuid'], summoner_dto['id'])
        return self.__get_name_cleanup_datetime(last_match_timestamp, summoner_dto['summonerLevel'])

    def __get_summoner_dto(self, name):
        try:
            summoner_dto = get(f'https://{self.__server}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{quote(name)}?api_key={self.__key}')
            summoner_dto.raise_for_status()
        except HTTPError:
            raise
        return summoner_dto.json()

    def __get_last_match_timestamp(self, puuid, id):
        last_lol_match_timestamp = self.__get_last_lol_match_timestamp(puuid, id)
        last_tft_match_timestamp = self.__get_last_tft_match_timestamp(puuid)
        if last_lol_match_timestamp >= last_tft_match_timestamp:
            return last_lol_match_timestamp
        else:
            return last_tft_match_timestamp

    def __get_last_lol_match_timestamp(self, puuid, id):
        try:
            last_lol_match_id = self.__get_last_lol_match_id(puuid)
        except (HTTPError, IndexError):
            return self.__get_last_played_champion_timestamp(id)
        lol_match_info = self.__get_lol_match_info(last_lol_match_id)
        try:
            return lol_match_info['gameEndTimestamp']
        except KeyError:
            return lol_match_info['gameStartTimestamp'] + lol_match_info['gameDuration']

    def __get_last_lol_match_id(self, puuid):
        try:
            last_lol_match_id = get(f'https://{self.__region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={self.__key}')
            last_lol_match_id.raise_for_status()
        except HTTPError:
            raise
        try:
            return last_lol_match_id.json()[0]
        except IndexError:
            raise IndexError('account has no lol matches played')

    def __get_last_played_champion_timestamp(self, id):
        try:
            champion_mastery_dto = get(f'https://{self.__server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={self.__key}')
            champion_mastery_dto.raise_for_status()
        except HTTPError:
            raise
        last_played_champion_timestamp = 0
        for champion in champion_mastery_dto.json():
            if(champion['lastPlayTime'] > last_played_champion_timestamp):
                last_played_champion_timestamp = champion['lastPlayTime']
        return last_played_champion_timestamp

    def __get_lol_match_info(self, match_id):
        try:
            lol_match_dto = get(f'https://{self.__region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.__key}')
            lol_match_dto.raise_for_status()
        except HTTPError:
            raise
        return lol_match_dto.json()['info']

    def __get_last_tft_match_timestamp(self, puuid):
        try:
            last_tft_match_id = self.__get_last_tft_match_id(puuid)
        except IndexError:
            return 0
        return self.__get_tft_match_info(last_tft_match_id)['game_datetime']

    def __get_last_tft_match_id(self, puuid):
        try:
            last_tft_match_id = get(f'https://{self.__region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={self.__key}')
            last_tft_match_id.raise_for_status()
        except HTTPError:
            raise
        try:
            return last_tft_match_id.json()[0]
        except IndexError:
            raise IndexError('account has no tft matches played')

    def __get_tft_match_info(self, tft_match_id):
        try:
            tft_match_dto = get(f'https://{self.__region}.api.riotgames.com/tft/match/v1/matches/{tft_match_id}?api_key={self.__key}')
            tft_match_dto.raise_for_status()
        except HTTPError:
            raise
        return tft_match_dto.json()['info']

    def __get_name_cleanup_datetime(self, last_game_timestamp, level):
        if level >= 30:
            return datetime.fromtimestamp(int(last_game_timestamp / 1000)) + relativedelta(months=+30)
        elif level <= 6:
            return datetime.fromtimestamp(int(last_game_timestamp / 1000)) + relativedelta(months=+6)
        else:
            return datetime.fromtimestamp(int(last_game_timestamp / 1000)) + relativedelta(months=+level)