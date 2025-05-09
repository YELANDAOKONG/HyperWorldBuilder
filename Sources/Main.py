# -*- coding: utf-8 -*-
import json
import os.path
from typing import List

from Sources.Builder import Builder


def build_main(args: List[str]) -> int:
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack")
    builder = Builder(output_path)
    builder.clean_output()
    builder.init_dirs()
    builder.init_mcmeta()

    builder.delete_structure("obelisk")
    builder.delete_structure("abandonedcity")

    # data = builder.map_decision_tree(os.path.join(os.path.dirname(__file__), "..", "Imports", "BigGlobe", "data", "bigglobe", "worldgen", "bigglobe_decision_tree"),  "bigglobe:overworld/biome/test_cave")
    # print(json.dumps(data, indent=4))

    return 0

def build_debug(args: List[str]) -> int:
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPackDebug")
    builder = Builder(output_path)
    builder.clean_output()
    builder.init_dirs()
    builder.init_mcmeta()

    builder.delete_structure("obelisk")
    builder.delete_structure("abandonedcity")
    return 0

