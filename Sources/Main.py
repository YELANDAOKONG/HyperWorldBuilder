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

    # 创建薰衣草平原结果节点
    lavender_field_node = {
        "result": {
            "type": "constant",
            "value": "biomesoplenty:lavender_field"
        }
    }
    overworld_tree["bigglobe:overworld/biome/lavender_field"] = lavender_field_node
    islands_tree["bigglobe:islands/biome/lavender_field"] = lavender_field_node

    # 创建魔法值条件节点
    test_lavender_field_node = {
        "condition": {
            "type": "world_trait_threshold",
            "trait": "bigglobe:magicalness",
            "min": 0.2,
            "max": 0.4,
            "smooth_min": True,
            "smooth_max": True
        },
        "if_true": "bigglobe:overworld/biome/lavender_field",
        "if_false": "bigglobe:overworld/biome/temperate_plains"
    }
    overworld_tree["bigglobe:overworld/biome/test_lavender_field"] = test_lavender_field_node

    # 修改主世界温带平原的引用
    # 找到 temperate_test_wasteland 节点并修改其 if_false 分支
    if "bigglobe:overworld/biome/temperate_test_wasteland" in overworld_tree:
        wasteland_node = overworld_tree["bigglobe:overworld/biome/temperate_test_wasteland"]
        if isinstance(wasteland_node, dict) and "if_false" in wasteland_node:
            # 只替换指向 temperate_plains 的引用
            if wasteland_node["if_false"] == "bigglobe:overworld/biome/temperate_plains":
                wasteland_node["if_false"] = "bigglobe:overworld/biome/test_lavender_field"

    # 为浮岛创建相同的魔法值条件节点，注意路径要使用islands命名空间
    islands_test_lavender_field_node = {
        "condition": {
            "type": "world_trait_threshold",
            "trait": "bigglobe:magicalness",
            "min": 0.2,
            "max": 0.4,
            "smooth_min": True,
            "smooth_max": True
        },
        "if_true": "bigglobe:islands/biome/lavender_field",
        "if_false": "bigglobe:islands/biome/temperate_plains"  # 修正：使用islands路径
    }
    islands_tree["bigglobe:islands/biome/test_lavender_field"] = islands_test_lavender_field_node

    # 修改群岛温带平原的引用
    # 找到 temperate_test_wasteland 节点并修改其 if_false 分支
    if "bigglobe:islands/biome/temperate_test_wasteland" in islands_tree:
        islands_wasteland_node = islands_tree["bigglobe:islands/biome/temperate_test_wasteland"]
        if isinstance(islands_wasteland_node, dict) and "if_false" in islands_wasteland_node:
            # 只替换指向 temperate_plains 的引用，使用正确的islands路径
            if islands_wasteland_node["if_false"] == "bigglobe:islands/biome/temperate_plains":  # 修正：检查islands路径
                islands_wasteland_node["if_false"] = "bigglobe:islands/biome/test_lavender_field"

    # 写回决策树
    builder.write_decision_tree(overworld_tree, all_decision_tree_dir)
    builder.write_decision_tree(islands_tree, all_decision_tree_dir)

    # 验证
    builder.verify_decision_tree(overworld_tree, all_decision_tree_dir)
    builder.verify_decision_tree(islands_tree, all_decision_tree_dir)



    builder.pack_zip(output_file, delete_exists=True)
    return 0

