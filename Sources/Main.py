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

    # Add crop generation support
    add_crop_generation(builder, output_path)

    builder.pack_zip(output_file, delete_exists=True)
    return 0


def add_crop_generation(builder, output_path):
    # Create necessary directories
    configured_feature = os.path.join(output_path, "data", "bigglobe", "worldgen", "configured_feature")
    configured_feature_overworld = os.path.join(configured_feature, "overworld")
    crops_dir = os.path.join(configured_feature_overworld, "crops")
    os.makedirs(crops_dir, exist_ok=True)

    tags_dir = os.path.join(output_path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "overworld")
    os.makedirs(tags_dir, exist_ok=True)

    # Create crop seeds config for various grass types
    crop_seeds = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "crop_seeds",
            "distance": 48,
            "variation": 48,
            "spawn_chance": 0.8,
            "randomize_chance": 0.2,
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
                    "state": "minecraft:grass",
                    "radius": {"type": "uniform", "min": 32.0, "max": 64.0}
                },
                {
                    "weight": 30.0,
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
                    "state": "minecraft:tall_grass[half=lower]",
                    "radius": {"type": "uniform", "min": 24.0, "max": 48.0}
                },
                {
                    "weight": 20.0,
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
                                "min": 0.2,
                                "mid": 0.4,
                                "max": 0.6
                            }
                        ]
                    },
                    "state": "bigglobe:short_grass",
                    "radius": {"type": "uniform", "min": 16.0, "max": 32.0}
                },
                {
                    "weight": 15.0,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/foliage",
                                "min": -0.7,
                                "max": -0.3
                            },
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/temperature",
                                "min": 0.5,
                                "max": 0.9
                            }
                        ]
                    },
                    "state": "bigglobe:charred_grass",
                    "radius": {"type": "uniform", "min": 16.0, "max": 32.0}
                },
                {
                    "weight": 15.0,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/temperature",
                                "min": -0.9,
                                "max": -0.5
                            }
                        ]
                    },
                    "state": "mcwholidays:snowy_grass",
                    "radius": {"type": "uniform", "min": 16.0, "max": 32.0}
                },
                {
                    "weight": 10.0,
                    "restrictions": {
                        "type": "and",
                        "restrictions": [
                            {
                                "type": "threshold",
                                "property": "bigglobe:overworld/temperature",
                                "min": -0.9,
                                "max": -0.5
                            }
                        ]
                    },
                    "state": "mcwholidays:snowy_tall_grass[half=lower]",
                    "radius": {"type": "uniform", "min": 16.0, "max": 24.0}
                }
            ]
        }
    }

    # Create wild crops config
    wild_crops = {
        "type": "bigglobe:flower",
        "config": {
            "seed": "wild_crops",
            "distance": 64,
            "variation": 48,
            "spawn_chance": 0.6,
            "randomize_chance": 0.2,
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
                    "defaults": {
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
                                    "min": -0.2,
                                    "mid": 0.2,
                                    "max": 0.5
                                }
                            ]
                        },
                        "radius": {"type": "uniform", "min": 16.0, "max": 32.0}
                    },
                    "variations": [
                        {"weight": 10.0, "state": "culturaldelights:wild_cucumbers"},
                        {"weight": 10.0, "state": "culturaldelights:wild_corn"},
                        {"weight": 10.0, "state": "culturaldelights:wild_eggplants"},
                        {"weight": 10.0, "state": "expandeddelight:wild_asparagus"},
                        {"weight": 10.0, "state": "expandeddelight:wild_sweet_potatoes"},
                        {"weight": 10.0, "state": "expandeddelight:wild_chili_pepper"},
                        {"weight": 10.0, "state": "expandeddelight:wild_peanuts"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_ribwort"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_nettle"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_emmer"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_corn"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_barley"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_oat"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_carrots"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_beetroots"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_potatoes"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_tomatoes"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_lettuce"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_onions"},
                        {"weight": 10.0, "state": "farm_and_charm:wild_strawberries"},
                        {"weight": 10.0, "state": "farmersdelight:wild_cabbages"},
                        {"weight": 10.0, "state": "farmersdelight:wild_onions"},
                        {"weight": 10.0, "state": "farmersdelight:wild_tomatoes"},
                        {"weight": 10.0, "state": "farmersdelight:wild_carrots"},
                        {"weight": 10.0, "state": "farmersdelight:wild_potatoes"},
                        {"weight": 10.0, "state": "farmersdelight:wild_beetroots"},
                        {"weight": 8.0, "state": "farmersdelight:wild_rice"},
                        {"weight": 8.0, "state": "snowyspirit:wild_ginger"}
                    ]
                },
                {
                    "defaults": {
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
                        "radius": {"type": "uniform", "min": 12.0, "max": 24.0}
                    },
                    "variations": [
                        {"weight": 5.0, "state": "croptopia:artichoke"},
                        {"weight": 5.0, "state": "croptopia:asparagus"},
                        {"weight": 5.0, "state": "croptopia:barley"},
                        {"weight": 5.0, "state": "croptopia:basil"},
                        {"weight": 5.0, "state": "croptopia:bellpepper"},
                        {"weight": 5.0, "state": "croptopia:blackbean"},
                        {"weight": 5.0, "state": "croptopia:blackberry"},
                        {"weight": 5.0, "state": "croptopia:blueberry"},
                        {"weight": 5.0, "state": "croptopia:broccoli"},
                        {"weight": 5.0, "state": "croptopia:cabbage"},
                        {"weight": 5.0, "state": "croptopia:cantaloupe"},
                        {"weight": 5.0, "state": "croptopia:cauliflower"},
                        {"weight": 5.0, "state": "croptopia:celery"},
                        {"weight": 5.0, "state": "croptopia:chile_pepper"},
                        {"weight": 5.0, "state": "croptopia:coffee_beans"},
                        {"weight": 5.0, "state": "croptopia:corn"},
                        {"weight": 5.0, "state": "croptopia:cranberry"},
                        {"weight": 5.0, "state": "croptopia:cucumber"},
                        {"weight": 5.0, "state": "croptopia:currant"},
                        {"weight": 5.0, "state": "croptopia:eggplant"},
                        {"weight": 5.0, "state": "croptopia:elderberry"},
                        {"weight": 5.0, "state": "croptopia:garlic"},
                        {"weight": 5.0, "state": "croptopia:ginger"},
                        {"weight": 5.0, "state": "croptopia:grape"},
                        {"weight": 5.0, "state": "croptopia:greenbean"},
                        {"weight": 5.0, "state": "croptopia:greenonion"},
                        {"weight": 5.0, "state": "croptopia:honeydew"},
                        {"weight": 5.0, "state": "croptopia:hops"},
                        {"weight": 5.0, "state": "croptopia:kale"},
                        {"weight": 5.0, "state": "croptopia:kiwi"},
                        {"weight": 5.0, "state": "croptopia:leek"},
                        {"weight": 5.0, "state": "croptopia:lettuce"},
                        {"weight": 5.0, "state": "croptopia:mustard"},
                        {"weight": 5.0, "state": "croptopia:oat"},
                        {"weight": 5.0, "state": "croptopia:olive"},
                        {"weight": 5.0, "state": "croptopia:onion"},
                        {"weight": 5.0, "state": "croptopia:peanut"},
                        {"weight": 5.0, "state": "croptopia:pepper"},
                        {"weight": 5.0, "state": "croptopia:pineapple"},
                        {"weight": 5.0, "state": "croptopia:radish"},
                        {"weight": 5.0, "state": "croptopia:raspberry"},
                        {"weight": 5.0, "state": "croptopia:rhubarb"},
                        {"weight": 5.0, "state": "croptopia:rice"},
                        {"weight": 5.0, "state": "croptopia:rutabaga"},
                        {"weight": 5.0, "state": "croptopia:saguaro"},
                        {"weight": 5.0, "state": "croptopia:soybean"},
                        {"weight": 5.0, "state": "croptopia:spinach"},
                        {"weight": 5.0, "state": "croptopia:squash"},
                        {"weight": 5.0, "state": "croptopia:strawberry"},
                        {"weight": 5.0, "state": "croptopia:sweetpotato"},
                        {"weight": 5.0, "state": "croptopia:tea_leaves"},
                        {"weight": 5.0, "state": "croptopia:tomatillo"},
                        {"weight": 5.0, "state": "croptopia:tomato"},
                        {"weight": 5.0, "state": "croptopia:turmeric"},
                        {"weight": 5.0, "state": "croptopia:turnip"},
                        {"weight": 5.0, "state": "croptopia:vanilla"},
                        {"weight": 5.0, "state": "croptopia:yam"},
                        {"weight": 5.0, "state": "croptopia:zucchini"}
                    ]
                },
                {
                    "defaults": {
                        "restrictions": {
                            "type": "and",
                            "restrictions": [
                                {
                                    "type": "threshold",
                                    "property": "bigglobe:overworld/foliage",
                                    "min": 0.2,
                                    "max": 0.6
                                },
                                {
                                    "type": "threshold",
                                    "property": "bigglobe:overworld/temperature",
                                    "min": 0.0,
                                    "max": 0.5
                                }
                            ]
                        },
                        "radius": {"type": "uniform", "min": 12.0, "max": 24.0}
                    },
                    "variations": [
                        {"weight": 4.0, "state": "croptopia:almond"},
                        {"weight": 4.0, "state": "croptopia:apricot"},
                        {"weight": 4.0, "state": "croptopia:avocado"},
                        {"weight": 4.0, "state": "croptopia:banana"},
                        {"weight": 4.0, "state": "croptopia:cashew"},
                        {"weight": 4.0, "state": "croptopia:cherry"},
                        {"weight": 4.0, "state": "croptopia:coconut"},
                        {"weight": 4.0, "state": "croptopia:date"},
                        {"weight": 4.0, "state": "croptopia:dragonfruit"},
                        {"weight": 4.0, "state": "croptopia:fig"},
                        {"weight": 4.0, "state": "croptopia:grapefruit"},
                        {"weight": 4.0, "state": "croptopia:kumquat"},
                        {"weight": 4.0, "state": "croptopia:lemon"},
                        {"weight": 4.0, "state": "croptopia:lime"},
                        {"weight": 4.0, "state": "croptopia:mango"},
                        {"weight": 4.0, "state": "croptopia:nectarine"},
                        {"weight": 4.0, "state": "croptopia:nutmeg"},
                        {"weight": 4.0, "state": "croptopia:orange"},
                        {"weight": 4.0, "state": "croptopia:peach"},
                        {"weight": 4.0, "state": "croptopia:pear"},
                        {"weight": 4.0, "state": "croptopia:pecan"},
                        {"weight": 4.0, "state": "croptopia:persimmon"},
                        {"weight": 4.0, "state": "croptopia:plum"},
                        {"weight": 4.0, "state": "croptopia:starfruit"},
                        {"weight": 4.0, "state": "croptopia:walnut"},
                        {"weight": 4.0, "state": "croptopia:cinnamon"},
                        {"weight": 3.0, "state": "croptopia:cinnamon_sapling"}
                    ]
                }
            ]
        }
    }

    # Write configs
    builder.write_raw(os.path.join(crops_dir, "crop_seeds.json"), crop_seeds)
    builder.write_raw(os.path.join(crops_dir, "wild_crops.json"), wild_crops)

    # Add to surface flowers tag
    surface_flowers_tag = {
        "replace": False,
        "values": [
            "bigglobe:overworld/crops/crop_seeds",
            "bigglobe:overworld/crops/wild_crops"
        ]
    }

    # Check if tag file exists
    tag_file_path = os.path.join(tags_dir, "surface_flowers.json")
    if os.path.exists(tag_file_path):
        try:
            with open(tag_file_path, 'r') as f:
                existing_tag = json.load(f)
                if "values" in existing_tag:
                    # Append our values to existing ones
                    existing_tag["values"].extend(surface_flowers_tag["values"])
                    surface_flowers_tag = existing_tag
        except:
            # If there's an error reading the file, we'll just overwrite it
            pass

    builder.write_raw(tag_file_path, surface_flowers_tag)


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

