# -*- coding: utf-8 -*-
import json
import os.path
from os import path
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


    tree_dir = path.join(output_path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree", "overworld")
    column_value_dir = path.join(output_path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "overworld")
    os.makedirs(tree_dir, exist_ok=True)
    os.makedirs(path.join(tree_dir, "biome"), exist_ok=True)
    os.makedirs(column_value_dir, exist_ok=True)

    lavender_field = {
        "result": {
            "type": "constant",
            "value": "biomesoplenty:lavender_field"
        }
    }
    test_warm = {
        "condition": {
            "type": "world_trait_threshold",
            "min": -0.125,
            "max":  0.125,
            "trait": "bigglobe:temperature_at_surface"
        },
        "if_true": "bigglobe:overworld/biome/lavender_field",
        "if_false": "bigglobe:overworld/biome/lavender_field"
    }
    with open(path.join(tree_dir, "biome", "lavender_field.json"), "w") as f:
        json.dump(lavender_field, f, indent=4)
    with open(path.join(tree_dir, "biome", "test_warm.json"), "w") as f:
        json.dump(test_warm, f, indent=4)

    raw_erosion = {
        "type": "bigglobe:script",
        "params": {
            "type": "double",
            "is_3d": False
        },
        "script": [
            "double base = continentalness * 0.2",
            "double variation = 16.0 + raw_erosion_64 * 8.0",
            "return (base * variation)"
        ]
    }
    with open(path.join(column_value_dir, "raw_erosion.json"), "w") as f:
        json.dump(raw_erosion, f, indent=4)


    return 0

