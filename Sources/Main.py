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
    configured_feature = path.join(output_path, "data", "bigglobe", "worldgen", "configured_feature")
    os.makedirs(tree_dir, exist_ok=True)
    os.makedirs(path.join(tree_dir, "biome"), exist_ok=True)
    os.makedirs(path.join(tree_dir, "surface_state"), exist_ok=True)
    os.makedirs(column_value_dir, exist_ok=True)
    os.makedirs(configured_feature, exist_ok=True)
    os.makedirs(path.join(configured_feature, "overworld"), exist_ok=True)
    os.makedirs(path.join(configured_feature, "overworld", "flowers"), exist_ok=True)


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


    test_hot = {
        "condition": {
            "type": "world_trait_threshold",
            "min": 0.5,
            "max": 0.75,
            "trait": "bigglobe:temperature_at_surface"
        },
        "if_true": "bigglobe:overworld/surface_state/lavender_field",
        "if_false": "bigglobe:overworld/surface_state/lavender_field"
    }
    lavender_field_surface_state = {
        "result": {
            "type": "constant",
            "value": {
                "surfaceState": "minecraft:grass_block",
                "subsurfaceState": "minecraft:dirt"
            }
        }
    }
    with open(path.join(tree_dir, "surface_state", "test_hot.json"), "w") as f:
        json.dump(lavender_field_surface_state, f, indent=4)
    with open(path.join(tree_dir, "surface_state", "lavender_field.json"), "w") as f:
        json.dump(test_hot, f, indent=4)



    # "double base = continentalness * 0.2"
    # "double variation = 16.0 + raw_erosion_64 * 8.0"
    raw_erosion = {
        "type": "bigglobe:script",
        "params": {
            "type": "double",
            "is_3d": False
        },
        "script": [
            "double computeHeight(double cont, double noise:",
            "double base = cont * 0.2L",
            "double variation = 8.0L + noise * 4.0L",
            "return(min(base * variation, 64.0L))",
            ")",
            "double height = computeHeight(continentalness, raw_erosion_64)",
            "if (continentalness < 0.0L: height *= max(0.0L, 1.0L + continentalness * 2.0L))",
            "return(height)"
        ]
    }
    with open(path.join(column_value_dir, "raw_erosion.json"), "w") as f:
        json.dump(raw_erosion, f, indent=4)


    flowers = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "flowers",
            "distance": 32,
            "variation": 32,
            "spawn_chance": 1,
            "randomize_chance": 0.2,
            "randomize_radius": {
                "type": "uniform",
                "min": 12,
                "max": 24
            },
            "noise": {
                "type": "abs",
                "grid": {
                    "type": "sum",
                    "layers": [
                        {
                            "type": "smooth",
                            "scale": 32,
                            "amplitude": 0.25
                        },
                        {
                            "type": "smooth",
                            "scale": 16,
                            "amplitude": 0.25
                        },
                        {
                            "type": "smooth",
                            "scale": 8,
                            "amplitude": 0.25
                        },
                        {
                            "type": "smooth",
                            "scale": 4,
                            "amplitude": 0.25
                        }
                    ]
                }
            },
            "entries": [
                {
                    "weight": 80,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/height_adjusted_foliage",
                                "min": 0.4,
                                "mid": 0.5,
                                "max": 0.6
                            },
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/height_adjusted_temperature",
                                "min": 0.7,
                                "mid": 0.75,
                                "max": 0.8
                            },
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/hilliness",
                                "min": 0,
                                "max": 0.4,
                                "smooth_max": True
                            }
                        ]
                    },
                    "radius": {
                        "type": "uniform",
                        "min": 48,
                        "max": 96
                    },
                    "state": "biomesoplenty:tall_lavender[half=lower]"
                },
                {
                    "defaults": {
                        "restrictions": {
                            "type": "and",
                            "restrictions": [
                                {
                                    "type": "range",
                                    "property": "bigglobe:overworld/height_adjusted_foliage",
                                    "min": 0.3,
                                    "mid": 0.5,
                                    "max": 0.7
                                },
                                {
                                    "type": "range",
                                    "property": "bigglobe:overworld/height_adjusted_temperature",
                                    "min": 0.6,
                                    "mid": 0.75,
                                    "max": 0.9
                                }
                            ]
                        }
                    },
                    "variations": [
                        {
                            "weight": 1020,
                            "radius": {
                                "type": "uniform",
                                "min": 32,
                                "max": 128
                            },
                            "state": "biomesoplenty:lavender"
                        },
                        {
                            "weight": 402,
                            "radius": {
                                "type": "uniform",
                                "min": 24,
                                "max": 96
                            },
                            "state": "biomesoplenty:tall_lavender[half=lower]"
                        },
                        {
                            "weight": 15,
                            "radius": {
                                "type": "uniform",
                                "min": 16,
                                "max": 32
                            },
                            "state": "minecraft:cornflower"
                        },
                        {
                            "weight": 10,
                            "radius": {
                                "type": "uniform",
                                "min": 12,
                                "max": 24
                            },
                            "state": "minecraft:allium"
                        },
                        {
                            "weight": 10,
                            "radius": {
                                "type": "uniform",
                                "min": 12,
                                "max": 24
                            },
                            "state": "minecraft:azure_bluet"
                        },
                        {
                            "weight": 8,
                            "radius": {
                                "type": "uniform",
                                "min": 12,
                                "max": 24
                            },
                            "state": "minecraft:oxeye_daisy"
                        },
                        {
                            "weight": 5,
                            "radius": {
                                "type": "uniform",
                                "min": 8,
                                "max": 16
                            },
                            "state": "minecraft:grass"
                        },
                        {
                            "weight": 5,
                            "radius": {
                                "type": "uniform",
                                "min": 8,
                                "max": 16
                            },
                            "state": "minecraft:tall_grass[half=lower]"
                        },
                        {
                            "weight": 3,
                            "radius": {
                                "type": "uniform",
                                "min": 8,
                                "max": 16
                            },
                            "state": "minecraft:dandelion"
                        },
                        {
                            "weight": 2,
                            "radius": {
                                "type": "uniform",
                                "min": 8,
                                "max": 16
                            },
                            "state": "minecraft:poppy"
                        }
                    ]
                }
            ]
        }
    }
    with open(path.join(configured_feature, "overworld", "flowers", "flowers.json"), "w") as f:
        json.dump(flowers, f, indent=4)


    return 0

