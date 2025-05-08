# -*- coding: utf-8 -*-
import json
import os
import os.path as path
import tomllib
import logging
import colorlog


class Builder:
    color_char = "\u00A7"

    version = "4.11.1"  # Big Globe Version
    version_pack_format = 15  # Minecraft Data Pack Format
    version_pack_description = "&6Hyper World &aCompatibility &bPack"

    def __init__(self, output_path):
        self.path = output_path

        # Configure colorlog with custom colors for different message components
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(cyan)s[%(asctime)s]%(reset)s %(log_color)s%(levelname)s%(reset)s - %(blue)s%(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'bold_green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'message': {
                    'INFO': 'white',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red',
                    'DEBUG': 'cyan'
                }
            }
        ))

        self.logger = logging.getLogger('builder')
        self.logger.setLevel(logging.INFO)
        # Remove any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        # Prevent log propagation to root logger
        self.logger.propagate = False

    def handle_color(self, strs: str) -> str:
        return strs.replace("&", self.color_char).replace(self.color_char + self.color_char, "&")

    def clean_output(self):
        self.logger.info(f"Cleaning output directory: {self.path}")
        if path.exists(self.path):
            import shutil
            shutil.rmtree(self.path)
            self.logger.info(f"Output directory {self.path} cleaned")
        self.logger.info(f"Creating output directory: {self.path}")
        os.makedirs(self.path)

    def init_dirs(self):
        paths = [
            self.path,
            path.join(self.path, "data"),
            path.join(self.path, "data", "minecraft"),
            path.join(self.path, "data", "minecraft", "tags"),
            path.join(self.path, "data", "minecraft", "worldgen"),
            path.join(self.path, "data", "bigglobe"),
            path.join(self.path, "data", "bigglobe", "tags"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "bigglobe_feature_dispatchers"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "bigglobe_feature_dispatchers", "islands"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "bigglobe_feature_dispatchers", "overworld"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "bigglobe_overrider"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "biome"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "configured_feature"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "end"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "islands"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "nether"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "configured_feature", "overworld"),
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "structure"),
            path.join(self.path, "data", "bigglobe", "worldgen"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_column_value"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "end"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "islands"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "nether"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_column_value", "overworld"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree", "end"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree", "islands"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_decision_tree", "overworld"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers", "end"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers", "islands"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers", "nether"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers", "overworld"),
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_overrider"),
            # More dirs here
        ]
        for p in paths:
            if not path.exists(p):
                self.logger.info("Creating directory: %s", p)
                os.makedirs(p)

    def init_mcmeta(self):
        data = {
            "pack": {
                "pack_format": self.version_pack_format,
                "description": self.handle_color(self.version_pack_description)
            }
        }
        with open(path.join(self.path, "pack.mcmeta"), "w") as f:
            json.dump(data, f, indent=4)

    def init(self):
        self.init_dirs()
        self.init_mcmeta()
