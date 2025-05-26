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
    import_path = os.path.join(os.path.dirname(__file__), "..", "Imports", "BigGlobe")
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPackDebug")
    output_file = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPackDebug.zip")
    builder = Builder(output_path)
    builder.clean_output()
    builder.init_dirs()
    builder.init_mcmeta()

    builder.delete_structure("obelisk")
    builder.delete_structure("abandonedcity")

    sources_decision_tree_dir = path.join(import_path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree")
    all_decision_tree_dir = path.join(output_path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree")
    tree_dir = path.join(output_path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree", "overworld")
    column_value_dir = path.join(output_path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "overworld")
    configured_feature = path.join(output_path, "data", "bigglobe", "worldgen", "configured_feature")
    tags = path.join(output_path, "data", "bigglobe", "tags")
    worldgen_tags = path.join(output_path, "data", "bigglobe", "tags", "worldgen")
    configured_feature_tags = path.join(output_path, "data", "bigglobe", "tags", "worldgen", "configured_feature")
    os.makedirs(tree_dir, exist_ok=True)
    os.makedirs(path.join(tree_dir, "biome"), exist_ok=True)
    os.makedirs(path.join(tree_dir, "surface_state"), exist_ok=True)
    os.makedirs(column_value_dir, exist_ok=True)
    os.makedirs(configured_feature, exist_ok=True)
    os.makedirs(path.join(configured_feature, "overworld"), exist_ok=True)
    os.makedirs(path.join(configured_feature, "overworld", "flowers"), exist_ok=True)


    # 是否直接劫持 test_warm 决策树 (此选项控制是否使用 Write Raw 修改决策树)
    option_write_custom_decision_tree = False
    # 是否应用自定义 raw_erosion 列值 (将导致问题)
    option_write_raw_erosion = False


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
    if option_write_custom_decision_tree:
        builder.write_raw(path.join(tree_dir, "biome", "lavender_field.json"), lavender_field)
        builder.write_raw(path.join(tree_dir, "biome", "test_warm.json"), test_warm)


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
    if option_write_custom_decision_tree:
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
    if option_write_raw_erosion:
        builder.write_raw(path.join(column_value_dir, "raw_erosion.json"), raw_erosion)

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
    #builder.write_raw(path.join(configured_feature, "overworld", "flowers", "flowers.json"), flowers, delete_exists=True)

    lavender_field_flowers = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "lavender_field_flowers",
            "distance": 16, # 24 / 16   # 减少距离使花朵生成点更靠近
            "variation": 16, # 24 / 16   # 较小的变化值使分布更均匀
            "spawn_chance": 1.0, # 1.0 / 1.0   # 确保每个可能的点都生成花朵
            "randomize_chance": 0.15, # 0.125 / 0.15    # 保持一定的随机性
            "randomize_radius": {"type": "uniform", "min": 16.0, "max": 32.0},
            "noise": {
                "type": "abs",
                "grid": {
                    "type": "sum",
                    "layers": [
                        {"type": "smooth", "scale": 32, "amplitude": 0.25},
                        {"type": "smooth", "scale": 16, "amplitude": 0.25},
                        {"type": "smooth", "scale": 8, "amplitude": 0.25},
                        {"type": "smooth", "scale": 4, "amplitude": 0.25}
                    ]
                }
            },
            "entries": [
                {
                    "weight": 100.0,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/foliage",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/temperature",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            }
                        ]
                    },
                    "radius": {"type": "uniform", "min": 64.0, "max": 128.0},
                    "state": "biomesoplenty:tall_lavender[half=lower]"
                },
                {
                    "defaults": {
                        "restrictions": {
                            "type": "and",
                            "restrictions": [
                                {
                                    "type": "threshold",
                                    "property": "bigglobe:overworld/foliage",
                                    "min": -0.5,
                                    "max": 0.0
                                },
                                {
                                    "type": "range",
                                    "property": "bigglobe:overworld/temperature",
                                    "min": -0.5,
                                    "mid": 0.0,
                                    "max": 0.5
                                }
                            ]
                        }
                    },
                    "variations": [
                        {
                            "weight": 120.0,
                            "radius": {
                                "type": "uniform",
                                "min": 64.0,
                                "max": 128.0
                            },
                            "state": "biomesoplenty:lavender"
                        },
                        {
                            "weight": 3.0, "radius": {
                                "type": "uniform",
                                "min": 8.0,
                                "max": 16.0
                            },
                            "state": "minecraft:azure_bluet"
                        },
                        {
                            "weight": 2.0, "radius": {
                                "type": "uniform",
                                "min": 8.0,
                                "max": 16.0
                            },
                            "state": "minecraft:oxeye_daisy"
                        }
                    ]
                }
            ]
        }
    }
    builder.write_raw(path.join(configured_feature, "overworld", "flowers", "lavender_field_flowers.json"), lavender_field_flowers, delete_exists=True)

    surface_flowers = {
        "replace": False,
        "values": [
            "bigglobe:overworld/flowers/lavender_field_flowers"
        ]
    }
    builder.write_raw(path.join(configured_feature_tags, "overworld", "surface_flowers.json"), surface_flowers, delete_exists=True)

    ### --------- &BEGIN 决策树区域 ---------

    overworld_tree = builder.map_decision_tree(sources_decision_tree_dir, "bigglobe:overworld/biome/test_cave")
    islands_tree = builder.map_decision_tree(sources_decision_tree_dir, "bigglobe:islands/biome/test_cave")

    lavender_field_node = {
        "result": {
            "type": "constant",
            "value": "biomesoplenty:lavender_field"
        }
    }

    # TODO...
    # 后续迁移模块到 Sources.MainFiles包中

    ### --------- &END 决策树区域 ---------


    builder.pack_zip(output_file, delete_exists=True)
    return 0


# --------------------------- &BEGIN 辅助方法区域 ---------------------------


def add_crop_generation(builder, output_path):
    # Create necessary directories
    configured_feature = os.path.join(output_path, "data", "bigglobe", "worldgen", "configured_feature")
    configured_feature_overworld = os.path.join(configured_feature, "overworld")
    crops_dir = os.path.join(configured_feature_overworld, "crops")
    os.makedirs(crops_dir, exist_ok=True)

    tags_dir = os.path.join(output_path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "overworld")
    os.makedirs(tags_dir, exist_ok=True)

    # Extended crops configuration based on your existing crops.json pattern
    extended_crops = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "extended_crops",
            "distance": 64,
            "variation": 64,
            "spawn_chance": 0.125,
            "randomize_chance": 0.125,
            "randomize_radius": {"type": "uniform", "min": 24.0, "max": 48.0},
            "noise": {
                "type": "abs",
                "grid": {
                    "type": "sum",
                    "layers": [
                        {"type": "smooth", "scale": 32, "amplitude": 0.25},
                        {"type": "smooth", "scale": 16, "amplitude": 0.25},
                        {"type": "smooth", "scale": 8, "amplitude": 0.25},
                        {"type": "smooth", "scale": 4, "amplitude": 0.25}
                    ]
                }
            },
            "entries": {
                "defaults": {
                    "radius": {"type": "uniform", "min": 24.0, "max": 48.0},
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/foliage",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/temperature",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/hilliness",
                                "min": 0.5,
                                "max": 0.0,
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
                    "under": {
                        "place": "minecraft:farmland",
                        "replace": [
                            "minecraft:dirt",
                            "minecraft:coarse_dirt",
                            "minecraft:grass_block",
                            "minecraft:podzol",
                            "bigglobe:overgrown_podzol"
                        ]
                    }
                },
                "variations": [
                    {"weight": 20.0, "state": "minecraft:wheat"},
                    {"weight": 10.0, "state": "minecraft:carrots"},
                    {"weight": 10.0, "state": "minecraft:potatoes"},
                    {"weight": 5.0, "state": "minecraft:beetroots"},
                    {"weight": 3.0, "state": "farmersdelight:cabbages"},
                    {"weight": 3.0, "state": "farmersdelight:tomatoes"},
                    {"weight": 2.0, "state": "farm_and_charm:tomato_crop_body"},
                    {"weight": 2.0, "state": "farm_and_charm:lettuce_crop"},
                    {"weight": 2.0, "state": "farm_and_charm:oat_crop"},
                    {"weight": 2.0, "state": "farm_and_charm:barley_crop"},
                    {"weight": 1.0, "state": "culturaldelights:cucumbers"},
                    {"weight": 1.0, "state": "culturaldelights:eggplants"},
                    {"weight": 1.0, "state": "culturaldelights:corn_upper"},
                    {"weight": 1.0, "state": "culturaldelights:wild_cucumbers"},
                    {"weight": 1.0, "state": "culturaldelights:wild_corn"},
                    {"weight": 1.0, "state": "culturaldelights:wild_eggplants"},
                    {"weight": 1.0, "state": "farm_and_charm:corn_crop"},
                    {"weight": 1.0, "state": "farm_and_charm:wild_ribwort"},
                    {"weight": 1.0, "state": "farm_and_charm:wild_nettle"},
                    {"weight": 1.0, "state": "farm_and_charm:wild_emmer"},
                    {"weight": 1.0, "state": "farm_and_charm:wild_corn[half=lower]"},
                    {"weight": 1.0, "state": "expandeddelight:sweet_potatoes_crop"},
                    {"weight": 1.0, "state": "expandeddelight:peanut_crop"},
                    {"weight": 1.0, "state": "brewery:hops_crop"},
                    {"weight": 1.0, "state": "supplementaries:flax"},
                    {"weight": 1.0, "state": "snowyspirit:wild_ginger"},
                    {"weight": 1.0, "state": "expandeddelight:asparagus_crop"},
                    {"weight": 1.0, "state": "expandeddelight:chili_pepper_crop"},
                    {"weight": 0.5, "state": "minecraft:pumpkin_stem"},
                    {"weight": 0.5, "state": "minecraft:melon_stem"},
                ]
            }
        }
    }

    # Wild crops configuration - simpler approach
    wild_crops = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "wild_crops",
            "distance": 64,
            "variation": 64,
            "spawn_chance": 0.0625,
            "randomize_chance": 0.125,
            "randomize_radius": {"type": "uniform", "min": 16.0, "max": 32.0},
            "noise": {
                "type": "abs",
                "grid": {
                    "type": "sum",
                    "layers": [
                        {"type": "smooth", "scale": 32, "amplitude": 0.25},
                        {"type": "smooth", "scale": 16, "amplitude": 0.25},
                        {"type": "smooth", "scale": 8, "amplitude": 0.25},
                        {"type": "smooth", "scale": 4, "amplitude": 0.25}
                    ]
                }
            },
            "entries": {
                "defaults": {
                    "radius": {"type": "uniform", "min": 16.0, "max": 32.0},
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/foliage",
                                "min": 0.0,
                                "max": 0.5
                            },
                            {
                                "type": "range",
                                "property": "bigglobe:overworld/temperature",
                                "min": -0.5,
                                "mid": 0.0,
                                "max": 0.5
                            }
                        ]
                    }
                },
                "variations": [
                    {"weight": 10.0, "state": "farmersdelight:wild_cabbages"},
                    {"weight": 10.0, "state": "farmersdelight:wild_onions"},
                    {"weight": 10.0, "state": "farmersdelight:wild_tomatoes"},
                    {"weight": 10.0, "state": "farmersdelight:wild_carrots"},
                    {"weight": 10.0, "state": "farmersdelight:wild_potatoes"},
                    {"weight": 10.0, "state": "farmersdelight:wild_beetroots"},
                    {"weight": 5.0, "state": "farmersdelight:wild_rice"}
                ]
            }
        }
    }

    # Write the configurations
    builder.write_raw(os.path.join(crops_dir, "extended_crops.json"), extended_crops)
    builder.write_raw(os.path.join(crops_dir, "wild_crops.json"), wild_crops)

    # Update surface flowers tag conservatively
    surface_flowers_tag = {
        "replace": False,
        "values": [
            "bigglobe:overworld/crops/extended_crops",
            "bigglobe:overworld/crops/wild_crops"
        ]
    }

    tag_file_path = os.path.join(tags_dir, "surface_flowers.json")
    if os.path.exists(tag_file_path):
        try:
            with open(tag_file_path, 'r') as f:
                existing_tag = json.load(f)
                if "values" in existing_tag:
                    existing_tag["values"].extend(surface_flowers_tag["values"])
                    surface_flowers_tag = existing_tag
        except:
            pass

    builder.write_raw(tag_file_path, surface_flowers_tag)

# --------------------------- &END 辅助方法区域 ---------------------------


