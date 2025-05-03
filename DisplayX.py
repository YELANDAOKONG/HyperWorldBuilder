#-*- coding: utf-8 -*-
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


class BigGlobeDecisionTreeVisualizer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.decision_tree_dir = self.base_dir / "data" / "bigglobe" / "worldgen" / "bigglobe_decision_tree"
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_counter = 0
        self.resolved_trees = {}

    def get_file_path(self, tree_id):
        # Convert namespace:path format to file path
        if ":" in tree_id:
            namespace, path = tree_id.split(":", 1)
            path = path.replace("/", os.sep)
            return (self.base_dir / "data" / namespace / "worldgen" / "bigglobe_decision_tree" / path).with_suffix(".json")
        else:
            # For relative paths
            return self.decision_tree_dir / f"{tree_id}.json"

    def load_decision_tree(self, tree_id):
        file_path = self.get_file_path(tree_id)
        if not file_path.exists():
            print(f"Warning: File not found for tree ID {tree_id} at {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file {file_path}")
            return None
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def process_tree(self, tree_id, parent_id=None, edge_label=None):
        # Check if we've already processed this tree
        if tree_id in self.resolved_trees:
            child_id = self.resolved_trees[tree_id]
            if parent_id is not None:
                self.G.add_edge(parent_id, child_id, label=edge_label or "")
            return child_id

        tree_data = self.load_decision_tree(tree_id)
        if tree_data is None:
            # Create a placeholder node for missing trees
            node_id = f"node_{self.node_counter}"
            self.node_counter += 1
            self.G.add_node(node_id)
            self.node_labels[node_id] = f"Missing: {tree_id}"
            self.node_colors[node_id] = "gray"

            if parent_id is not None:
                self.G.add_edge(parent_id, node_id, label=edge_label or "")

            self.resolved_trees[tree_id] = node_id
            return node_id

        # Create a node for this tree
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        self.G.add_node(node_id)

        if parent_id is not None:
            self.G.add_edge(parent_id, node_id, label=edge_label or "")

        self.resolved_trees[tree_id] = node_id

        # Process based on node type
        if "result" in tree_data:
            # Result node
            result_type = tree_data["result"].get("type", "unknown")
            result_value = "..."

            if result_type == "constant":
                result_value = tree_data["result"].get("value", "...")
            elif result_type == "scripted":
                script = tree_data["result"].get("script", "...")
                result_value = f"script: {script[:30]}..." if len(script) > 30 else f"script: {script}"

            self.node_labels[node_id] = f"Result: {result_type}\n{result_value}"
            self.node_colors[node_id] = "lightgreen"

        elif "condition" in tree_data:
            # Condition node
            condition_type = tree_data["condition"].get("type", "unknown")

            condition_desc = self.get_condition_description(tree_data["condition"])
            self.node_labels[node_id] = f"Condition: {condition_type}\n{condition_desc}"
            self.node_colors[node_id] = "lightblue"

            # Process if_true branch
            if "if_true" in tree_data:
                self.process_tree(tree_data["if_true"], node_id, "True")

            # Process if_false branch
            if "if_false" in tree_data:
                self.process_tree(tree_data["if_false"], node_id, "False")
        else:
            # Unknown node type
            self.node_labels[node_id] = f"Unknown: {tree_id}"
            self.node_colors[node_id] = "orange"

        return node_id

    def get_condition_description(self, condition):
        condition_type = condition.get("type", "unknown")

        if condition_type == "threshold":
            column_value = condition.get("column_value", "?")
            min_val = condition.get("min", "?")
            max_val = condition.get("max", "?")
            return f"{column_value}: {min_val} to {max_val}"

        elif condition_type == "world_trait_threshold":
            trait = condition.get("trait", "?")
            min_val = condition.get("min", "?")
            max_val = condition.get("max", "?")
            return f"{trait}: {min_val} to {max_val}"

        elif condition_type == "script":
            script = condition.get("script", "")
            return f"script: {script[:30]}..." if len(script) > 30 else f"script: {script}"

        elif condition_type in ["and", "or"]:
            count = len(condition.get("conditions", []))
            return f"{count} conditions"

        elif condition_type == "not":
            inner_condition = condition.get("condition", {})
            inner_type = inner_condition.get("type", "?")
            return f"NOT {inner_type}"

        return condition_type

    def visualize_tree(self, root_tree_id, output_file=None, figsize=(15, 10)):
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the tree
        self.process_tree(root_tree_id)

        # Create visualization
        plt.figure(figsize=figsize)

        # Use a hierarchical layout from NetworkX
        # Replaced pygraphviz with pure NetworkX layout algorithms
        try:
            pos = nx.nx_pydot.pydot_layout(self.G, prog="dot")
        except:
            # Fallback to NetworkX's built-in layout algorithms
            print("Using fallback layout algorithm - for better layout install pydot")
            pos = nx.spring_layout(self.G, seed=42)

            # For better hierarchical layout, also consider these:
            # pos = nx.kamada_kawai_layout(self.G)
            # pos = nx.planar_layout(self.G)

        # Draw nodes with custom colors
        node_color_list = [self.node_colors.get(node, "gray") for node in self.G.nodes()]
        nx.draw_networkx_nodes(self.G, pos, node_color=node_color_list, node_size=2000, alpha=0.8)

        # Draw edges
        nx.draw_networkx_edges(self.G, pos, arrows=True, arrowsize=20)

        # Draw labels
        nx.draw_networkx_labels(self.G, pos, labels=self.node_labels, font_size=8, font_family="sans-serif")

        # Draw edge labels
        edge_labels = {(u, v): d["label"] for u, v, d in self.G.edges(data=True) if "label" in d}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=8)

        plt.axis("off")
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Tree visualization saved to {output_file}")
        else:
            plt.show()

        return self.G, pos  # Return graph and positions for further customization

    def batch_visualize(self, start_dir=None, output_dir="tree_visualizations"):
        """Visualize all decision trees in a directory"""
        if start_dir is None:
            start_dir = self.decision_tree_dir
        else:
            start_dir = Path(start_dir)

        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Find all JSON files in the directory and subdirectories
        for root, _, files in os.walk(start_dir):
            root_path = Path(root)
            for file in files:
                if file.endswith(".json"):
                    file_path = root_path / file
                    relative_path = file_path.relative_to(self.decision_tree_dir)
                    tree_id = str(relative_path.with_suffix(""))

                    # Create output directory structure
                    tree_output_dir = output_dir / relative_path.parent
                    os.makedirs(tree_output_dir, exist_ok=True)

                    output_file = tree_output_dir / f"{file.replace('.json', '.png')}"
                    print(f"Visualizing {tree_id}...")
                    try:
                        self.visualize_tree(tree_id, output_file)
                    except Exception as e:
                        print(f"Error visualizing {tree_id}: {e}")


# Example usage
if __name__ == "__main__":
    # Update this path to your Minecraft root or extracted Big Globe mod directory
    base_dir = "Imports/BigGlobe"

    visualizer = BigGlobeDecisionTreeVisualizer(base_dir)

    # Visualize a specific tree (e.g., the biome root)
    # visualizer.visualize_tree("overworld/biome/test_cave", "OutPut/BiomeTree.png")

    # Or batch visualize all trees
    visualizer.batch_visualize(output_dir="OutPut/DecisionTreeImages")
