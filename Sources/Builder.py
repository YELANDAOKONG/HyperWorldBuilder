# -*- coding: utf-8 -*-
import json
import os
import os.path as path
import tomllib
import logging
import zipfile

import colorlog


def get_decision_tree_node_file_path(base_path, node_id):
    """
    将决策树节点ID转换为文件路径。

    Args:
        base_path: 决策树文件的基础目录路径（通常是bigglobe_decision_tree目录）
        node_id: 节点标识符，可以是相对路径或带命名空间的完整路径

    Returns:
        str: 对应节点的完整文件路径
    """
    if ":" in node_id:  # 处理命名空间格式 (namespace:path)
        namespace, rel_path = node_id.split(":", 1)
        # 忽略命名空间，直接使用相对路径部分
        rel_path = rel_path.replace("/", os.sep)
        return path.join(base_path, f"{rel_path}.json")
    else:
        # 纯相对路径
        return path.join(base_path, f"{node_id}.json")


class Builder:
    color_char = "\u00A7"

    version = "5.0.0"  # Big Globe Version
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
            path.join(self.path, "data", "bigglobe", "tags", "worldgen", "biome", "has_structure"),
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

    def pack_zip(self, output_path: str, delete_exists: bool = False):
        if delete_exists:
            if path.exists(output_path):
                self.logger.info(f"Deleting existing datapack: {output_path}")
                os.remove(output_path)

        self.logger.info(f"Packing datapack to {output_path}")
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(str(file_path), str(os.path.relpath(str(file_path), self.path)))
        self.logger.info(f"Datapack packed to {output_path}")

    ################################################################################

    def write_raw(self, file_path: str, data: dict, delete_exists: bool = True):
        full_path = path.join(self.path, file_path)
        dir_path = path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)
        if delete_exists and path.exists(full_path):
            self.logger.info(f"Deleting existing file: {full_path}")
            os.remove(full_path)

        with open(full_path, "w") as f:
            json.dump(data, f, indent=4)
        self.logger.info(f"Wrote file: {full_path}")

    ################################################################################

    def delete_structure(self, name: str):
        data = {
            "replace": True,
            "values": []
        }
        basic_path = path.join(self.path, "data", "bigglobe", "tags", "worldgen", "biome", "has_structure")

        # Split the name into directory components if path separators exist
        name_parts = name.split('/')
        file_name = name_parts[-1] + ".json"

        # Combine any subdirectories with the basic path
        if len(name_parts) > 1:
            dir_path = path.join(basic_path, *name_parts[:-1])
        else:
            dir_path = basic_path

        # Create directories if they don't exist
        if not path.exists(dir_path):
            self.logger.info(f"Creating directory structure: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)

        # Create the full file path
        file_path = path.join(dir_path, file_name)

        # Write the file
        self.logger.info(f"Writing empty structure file: {file_path}")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        self.logger.info(f"Structure \'{name}\' has been deleted/emptied")

    def map_decision_tree(self, script_path: str, root_node: str):
        """
        将决策树映射到内存中的可修改数据结构。

        Args:
            script_path: bigglobe_decision_tree目录的路径
            root_node: 根节点的名称/标识符

        Returns:
            dict: 包含完整决策树网络的字典，键为节点ID，值为节点数据
        """
        self.logger.info(f"Mapping decision tree from root node: {root_node}")

        # 构建根节点文件路径
        root_tree_path = get_decision_tree_node_file_path(script_path, root_node)
        if not path.exists(root_tree_path):
            self.logger.error(f"Root tree file not found: {root_tree_path}")
            raise FileNotFoundError(f"Root tree file not found: {root_tree_path}")

        # 存储所有树节点的映射
        tree_map = {}

        # 递归加载和解析决策树
        def resolve_tree_node(node_id):
            # 如果节点已经解析过，直接返回
            if node_id in tree_map:
                return tree_map[node_id]

            # 确定节点文件路径
            node_path = get_decision_tree_node_file_path(script_path, node_id)

            # 检查文件是否存在
            if not path.exists(node_path):
                self.logger.warning(f"Tree node file not found: {node_path}")
                return None

            # 加载节点数据
            try:
                with open(node_path, "r") as f:
                    node_data = json.load(f)

                # 存储到映射中
                tree_map[node_id] = node_data

                # 如果是条件节点，递归解析引用的子节点
                if "condition" in node_data:
                    # 处理if_true分支
                    if "if_true" in node_data:
                        resolve_tree_node(node_data["if_true"])

                    # 处理if_false分支
                    if "if_false" in node_data:
                        resolve_tree_node(node_data["if_false"])

                    # 处理复合条件中可能嵌套的条件
                    condition = node_data["condition"]
                    if condition["type"] in ["and", "or"] and "conditions" in condition:
                        # 递归检查嵌套条件中可能引用的决策树
                        for nested_condition in condition["conditions"]:
                            if isinstance(nested_condition, dict) and "type" in nested_condition and nested_condition[
                                "type"] == "decision_tree":
                                if "tree" in nested_condition:
                                    resolve_tree_node(nested_condition["tree"])

                    # 处理not条件
                    elif condition["type"] == "not" and "condition" in condition:
                        nested_condition = condition["condition"]
                        if isinstance(nested_condition, dict) and "type" in nested_condition and nested_condition[
                            "type"] == "decision_tree":
                            if "tree" in nested_condition:
                                resolve_tree_node(nested_condition["tree"])

                return node_data

            except Exception as e:
                self.logger.error(f"Failed to parse tree node {node_id}: {e}")
                return None

        # 从根节点开始解析
        resolve_tree_node(root_node)

        self.logger.info(f"Successfully mapped decision tree with {len(tree_map)} nodes")
        return tree_map























