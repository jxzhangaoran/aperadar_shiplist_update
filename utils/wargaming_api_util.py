import datetime
import os
from typing import Dict

import requests
import yaml
from tqdm import tqdm

from utils import parent_directory


class WarGamingApiUtil:

    def __init__(self):
        with open(os.path.join(parent_directory, "config.yaml"), 'r') as file:
            config = yaml.safe_load(file)
            self.appid = config['wargaming']['appid']
            self.wg_host = config['wargaming']['host']

    # 返回结果格式: {'date': '20241128', 'version': '13.11.0'}
    def get_game_base_info(self) -> Dict[str, str]:
        params = {
            'application_id': self.appid,
            'fields': 'game_version,ships_updated_at'
        }
        response = requests.get(self.wg_host + "wows/encyclopedia/info/", params=params)
        api_result = response.json()
        if api_result['status'] != 'ok':
            raise Exception('get_game_base_info failed, api result status is: ' + api_result['status'])

        api_data = api_result['data']
        ships_updated_at = api_data['ships_updated_at']
        game_version = api_data['game_version']
        date_time = datetime.datetime.fromtimestamp(ships_updated_at)
        formatted_date = date_time.strftime('%Y%m%d')
        result = {'date': formatted_date, 'version': game_version}

        return result

    # 获取所有船只数据
    def get_all_ships(self) -> Dict[str, Dict[str, object]]:
        # 存储所有船只数据，key为船只id
        all_ships = {}

        # 首先获取英语船名
        self.fill_ships_info(ships=all_ships, lang='en', name_locale_key='name_en-us')

        # 再获取简体中文船名
        self.fill_ships_info(ships=all_ships, lang='zh-cn', name_locale_key='name_zh-cn')

        return all_ships

    def fill_ships_info(self, ships: Dict[str, Dict[str, object]], lang: str, name_locale_key: str):
        url = self.wg_host + "/wows/encyclopedia/ships/"
        page_no = 1
        page_total = 1

        ships_process = None

        while page_no <= page_total:
            params = {
                'application_id': self.appid,
                'language': lang,
                'fields': 'nation,type,name,tier',
                'limit': 100,
                'page_no': page_no
            }

            response = requests.get(url, data=params)
            api_result = response.json()
            if api_result['status'] != 'ok':
                raise Exception('get_all_ships failed, api result status is: ' + api_result['status'])

            api_meta = api_result['meta']
            page_total = api_meta['page_total']
            ships_data = api_result['data']

            if ships_process is None:
                ships_process = tqdm(iterable=range(int(api_meta['total'])),
                                     colour="GREEN",
                                     desc="Fetching ship data for language {}...".format(lang))
            for ship_id, props in ships_data.items():
                if ships.get(ship_id) is None:
                    ships[ship_id] = {}
                ships[ship_id][name_locale_key] = props['name']
                ships[ship_id]["nation"] = props["nation"]
                ships[ship_id]["tier"] = props["tier"]
                ships[ship_id]["type"] = props["type"]
                ships_process.update(1)
            page_no = page_no + 1

        ships_process.close()


if __name__ == '__main__':
    wg_util = WarGamingApiUtil()
    print(wg_util.get_all_ships())