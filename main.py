import json
import os
import time
from typing import Dict

from fan_he_xie import FanHeXie
from utils.wargaming_api_util import WarGamingApiUtil


class ApeRadarShipListUpdator:

    def __init__(self):
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.resources_dir = os.path.join(self.current_directory, "resources")
        self.output_dir = os.path.join(self.current_directory, "output")

    def get_newest_ship_info(self, need_fan_he_xie=True) -> Dict[str, Dict[str, object]]:
        wg_api = WarGamingApiUtil()

        # 1、从WG官方API获取游戏版本信息
        game_base_info = wg_api.get_game_base_info()

        # 2、从WG官方API获取原始船名列表
        ship_list = wg_api.get_all_ships()

        # 3、反和谐
        if need_fan_he_xie:
            fhx = FanHeXie()
            ship_list = fhx.fan_he_xie_ships(ship_list)

        # 4、最终结果，符合海猴雷达要求的格式
        final_ship_info_data = {
            "version": game_base_info['version'],
            "date": game_base_info['date'],
            "ships": ship_list
        }

        return final_ship_info_data

    def output_ship_list_file(self, ship_info: Dict[str, Dict[str, object]]):
        file_name = 'ships_{}_{}_{}.json'.format(ship_info['version'], ship_info['date'], int(time.time() * 1000))
        file_path = os.path.join(self.output_dir, file_name)

        json_data = json.dumps(ship_info, ensure_ascii=False, indent=4)

        with open(file_path, 'w') as file:
            file.write(json_data)
            print("ship list file output to: {}".format(os.path.abspath(file_path)))


if __name__ == '__main__':
    worker = ApeRadarShipListUpdator()

    data = worker.get_newest_ship_info()

    worker.output_ship_list_file(data)
