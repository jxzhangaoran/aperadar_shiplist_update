import copy
import json
import os
from typing import Dict

from tqdm import tqdm

from utils.translate_util import TranslateUtil


class FanHeXie:

    def __init__(self):
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.resources_dir = os.path.join(self.current_directory, "resources")
        self.output_dir = os.path.join(self.current_directory, "output")
        self.local_dict = self.load_local_dict()

    # 加载本地翻译字典文件到内存
    def load_local_dict(self) -> Dict[str, str]:
        result_dict = {}
        with open(os.path.join(self.resources_dir, "en2cn.txt"), 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                parts = line.split('|||')
                if len(parts) == 2:
                    key, value = parts
                    result_dict[key.strip()] = value.strip()
        return result_dict

    # 反和谐逻辑
    # 1、如果Lookup_example=True，则首先尝试从旧版本的船名列表文件中读取name_zh-cn，如果有值则直接覆盖；
    # 2、否则，根据船只属性判断是否需要反和谐，过滤出需要反和谐的船只列表；
    # 3、执行反和谐
    def fan_he_xie_ships(self, ships: Dict[str, Dict[str, object]], lookup_example=True) \
            -> Dict[str, Dict[str, object]]:
        with open(os.path.join(self.resources_dir, "ships_example.json"), 'r') as f:
            ships_old_version = json.load(f)['ships']

        new_ships = {}
        if lookup_example:
            for ship_id, props in ships.items():
                if props is None or ship_id is None:
                    continue
                ship_old_version = ships_old_version.get(ship_id)
                if ship_old_version is not None:
                    ships[ship_id]["name_zh-cn"] = ship_old_version["name_zh-cn"]
                else:
                    new_ships[ship_id] = props
        else:
            new_ships = copy.deepcopy(ships)

        need_fan_he_xie_ships = {}
        for ship_id, props in new_ships.items():
            if self.need_fan_he_xie(props):
                need_fan_he_xie_ships[ship_id] = props

        trans = TranslateUtil()
        fan_he_xie_result_ships = copy.deepcopy(need_fan_he_xie_ships)
        fan_he_xie_process = tqdm(iterable=range(len(fan_he_xie_result_ships)),
                                  colour="BLUE",
                                  desc="反和谐进行中...")
        for ship_id, props in fan_he_xie_result_ships.items():
            fan_he_xie_result = self.do_fan_he_xie(trans, str(props['name_en-us']))
            if fan_he_xie_result is not None:
                fan_he_xie_result_ships[ship_id]['name_zh-cn'] = fan_he_xie_result
            fan_he_xie_process.update(1)

        fan_he_xie_process.close()
        print("====== 反和谐结果 ======")
        print(json.dumps(fan_he_xie_result_ships, indent=4, ensure_ascii=False))

        result_ships = copy.deepcopy(ships)
        for ship_id, props in fan_he_xie_result_ships.items():
            result_ships[ship_id] = props

        return result_ships

    # 判断是否需要反和谐的规则
    # 默认【日本】 + 【泛亚巡洋、驱逐、潜艇】需要反和谐
    def need_fan_he_xie(self, ship_props: Dict[str, object]) -> bool:
        if ship_props is None:
            return False
        if ship_props["nation"] == "japan":
            return True
        if ship_props["nation"] == "pan_asia" and ship_props["type"] in ["Destroyer", "Cruiser", "Submarine"]:
            return True
        return False

    # 反和谐执行逻辑为：优先从本地映射字典读取翻译，若找不到对应数据，则调用翻译API实时翻译
    def do_fan_he_xie(self, trans: TranslateUtil, name_en: str) -> str:
        local_translate = self.local_dict.get(name_en)
        if local_translate is not None:
            return local_translate
        return trans.translate(query=name_en, from_lang='en', to_lang='zh')


if __name__ == '__main__':
    ships = {
        "3425613520": {
            "name_en-us": "Azuma B",
            "nation": "japan",
            "tier": 9,
            "type": "Cruiser",
            "name_zh-cn": "猉 (黑)"
        },
        "3550394064": {
            "name_en-us": "Yari",
            "nation": "japan",
            "tier": 10,
            "type": "Cruiser",
            "name_zh-cn": "犀"
        },
        "3765352144": {
            "tier": 5,
            "type": "Cruiser",
            "name_en-us": "Yahagi",
            "nation": "japan",
            "name_zh-cn": "狸"
        },
        "3667834576": {
            "tier": 8,
            "type": "Cruiser",
            "name_en-us": "Atago B",
            "nation": "japan",
            "name_zh-cn": "犬 (黑)"
        },
        "4290688720": {
            "tier": 4,
            "type": "Cruiser",
            "name_en-us": "Yūbari",
            "nation": "japan",
            "name_zh-cn": "狐"
        },
        "3540956880": {
            "tier": 9,
            "type": "Cruiser",
            "name_en-us": "Chikuma II",
            "nation": "japan",
            "name_zh-cn": "獴"
        }
    }

    fan_he_xie = FanHeXie()
    result = fan_he_xie.fan_he_xie_ships(ships, lookup_example=False)
    print(json.dumps(result, ensure_ascii=False, indent=4))
