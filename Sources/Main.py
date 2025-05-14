# -*- coding: utf-8 -*-
import json
import os.path
from os import path
from typing import List

from Sources.Builder import Builder


def build_main(args: List[str]) -> int:
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack")
    output_file = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack.zip")
    builder = Builder(output_path)
    builder.clean_output()
    builder.init_dirs()
    builder.init_mcmeta()

    builder.delete_structure("obelisk")
    builder.delete_structure("abandonedcity")

    # data = builder.map_decision_tree(os.path.join(os.path.dirname(__file__), "..", "Imports", "BigGlobe", "data", "bigglobe", "worldgen", "bigglobe_decision_tree"),  "bigglobe:overworld/biome/test_cave")
    # print(json.dumps(data, indent=4))

    builder.pack_zip(output_file, delete_exists=True)
    return 0

def build_debug(args: List[str]) -> int:
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPackDebug")
    output_file = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPackDebug.zip")
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
    builder.write_raw(path.join(tree_dir, "biome", "lavender_field.json"), lavender_field)
    #builder.write_raw(path.join(tree_dir, "biome", "test_warm.json"), test_warm)


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
    builder.write_raw(path.join(tree_dir, "surface_state", "test_hot.json"), test_hot)
    builder.write_raw(path.join(tree_dir, "surface_state", "lavender_field.json"), lavender_field_surface_state)



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
    #builder.write_raw(path.join(column_value_dir, "raw_erosion.json"), raw_erosion)

    flowers = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "flowers",
            "distance": 64,
            "variation": 64,
            "spawn_chance": 1.0,
            "randomize_chance": 0.125,
            "randomize_radius": {
                "type": "uniform",
                "min": 16.0,
                "max": 32.0
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
                    "weight": 50.0,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/height_adjusted_foliage",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/height_adjusted_temperature",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/hilliness",
                                "min": 0.0,
                                "max": 0.5,
                                "smooth_max": False
                            },
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/magicalness",
                                "min": -0.5,
                                "max": 0.0
                            }
                        ]
                    },
                    "radius": {
                        "type": "uniform",
                        "min": 32.0,
                        "max": 64.0
                    },
                    "state": "biomesoplenty:tall_lavender[half=lower]"
                },
                {
                    "defaults": {
                        "restrictions": {
                            "type": "and",
                            "restrictions": [
                                {
                                    "type": "threshold",
                                    "property": "bigglobe:overworld/height_adjusted_foliage",
                                    "min": -0.5,
                                    "max": 0.0
                                },
                                {
                                    "type": "range",
                                    "property": "bigglobe:overworld/height_adjusted_temperature",
                                    "min": -0.5,
                                    "mid": 0.0,
                                    "max": 0.5
                                },
                                {
                                    "type": "threshold",
                                    "property": "bigglobe:overworld/magicalness",
                                    "min": -0.5,
                                    "max": 0.0
                                }
                            ]
                        }
                    },
                    "variations": [
                        {
                            "weight": 50.0,
                            "radius": {
                                "type": "uniform",
                                "min": 32.0,
                                "max": 64.0
                            },
                            "state": "biomesoplenty:lavender"
                        },
                        {
                            "weight": 30.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "biomesoplenty:tall_lavender[half=lower]"
                        },
                        {
                            "weight": 20.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:azure_bluet"
                        },
                        {
                            "weight": 20.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:oxeye_daisy"
                        },
                        {
                            "weight": 15.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:cornflower"
                        },
                        {
                            "weight": 10.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:poppy"
                        },
                        {
                            "weight": 10.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:allium"
                        },
                        {
                            "weight": 10.0,
                            "radius": {
                                "type": "uniform",
                                "min": 24.0,
                                "max": 48.0
                            },
                            "state": "minecraft:dandelion"
                        },
                        {
                            "weight": 5.0,
                            "radius": {
                                "type": "uniform",
                                "min": 16.0,
                                "max": 32.0
                            },
                            "state": "minecraft:grass"
                        },
                        {
                            "weight": 5.0,
                            "radius": {
                                "type": "uniform",
                                "min": 16.0,
                                "max": 32.0
                            },
                            "state": "minecraft:tall_grass[half=lower]"
                        }
                    ]
                }
            ]
        }
    }
    builder.write_raw(path.join(configured_feature, "overworld", "flowers", "flowers.json"), flowers, delete_exists=True)


    builder.pack_zip(output_file, delete_exists=True)
    return 0

