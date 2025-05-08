# -*- coding: utf-8 -*-
import json
import os
import os.path as path
import tomllib

class Builder:
    color_char = "\u00A7"

    version = "4.11.1" # Big Globe Version
    version_pack_format = 15 # Minecraft Data Pack Format
    version_pack_description = "&6Hyper World &aCompatibility &bPack"

    def __init__(self, output_path):
        self.path = output_path

    def handle_color(self, strs: str) -> str:
        return strs.replace("&", self.color_char).replace(self.color_char + self.color_char, "&")

    def clean_output(self):
        for root, dirs, files in os.walk(self.path):
            for f in files:
                file_path = os.path.join(root, f)
                os.remove(file_path)
            for d in dirs:
                dir_path = os.path.join(root, d)
                os.rmdir(dir_path)
        if not path.exists(self.path):
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
            path.join(self.path, "data", "bigglobe", "worldgen", "bigglobe_feature_dispatchers"),
            # More dirs here
        ]
        for p in paths:
            if not path.exists(p):
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




















