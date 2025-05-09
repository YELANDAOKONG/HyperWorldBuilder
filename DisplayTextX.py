# -*- coding: utf-8 -*-
import os
import json
import sys
import logging
import colorlog
import shutil
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt


class BigGlobeDecisionTreeVisualizer:
    def __init__(self, base_dir, truncate_scripts=True):
        """
        Initialize the decision tree visualizer.

        Args:
            base_dir: Path to the Big Globe mod files directory
            truncate_scripts: Whether to truncate long script content in display (default: True)
        """
        self.base_dir = Path(base_dir)
        self.decision_tree_dir = self.base_dir / "data" / "bigglobe" / "worldgen" / "bigglobe_decision_tree"
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}  # New attribute to track node paths
        self.node_counter = 0
        self.resolved_trees = {}
        self.truncate_scripts = truncate_scripts

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

        self.logger = logging.getLogger('visualizer')
        self.logger.setLevel(logging.INFO)
        # Remove any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        # Prevent log propagation to root logger
        self.logger.propagate = False

    def clean_output(self, output_dir):
        """
        Clean output directory before generating new visualizations.

        Args:
            output_dir: Directory to clean
        """
        self.logger.info(f"Cleaning output directory: {output_dir}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            self.logger.info(f"Output directory {output_dir} cleaned")
        self.logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    def get_file_path(self, tree_id):
        """
        Convert tree ID to a file path.

        Args:
            tree_id: String ID of the decision tree

        Returns:
            Path object for the corresponding JSON file
        """
        # Convert namespace:path format to file path
        if ":" in tree_id:
            namespace, path = tree_id.split(":", 1)
            path = path.replace("/", os.sep)
            return (self.base_dir / "data" / namespace / "worldgen" / "bigglobe_decision_tree" / path).with_suffix(
                ".json")
        else:
            # For relative paths
            return self.decision_tree_dir / f"{tree_id}.json"

    def load_decision_tree(self, tree_id):
        """
        Load a decision tree JSON file.

        Args:
            tree_id: String ID of the decision tree

        Returns:
            Parsed JSON data or None if file not found/invalid
        """
        file_path = self.get_file_path(tree_id)
        if not file_path.exists():
            self.logger.warning(f"File not found for tree ID {tree_id} at {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in file {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return None

    def process_tree(self, tree_id, parent_id=None, edge_label=None):
        """
        Process a decision tree and add it to the graph.

        Args:
            tree_id: String ID of the decision tree
            parent_id: ID of the parent node (if any)
            edge_label: Label for the edge from parent to this node

        Returns:
            ID of the node created for this tree
        """
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
            self.node_paths[node_id] = tree_id  # Store the path for this node

            if parent_id is not None:
                self.G.add_edge(parent_id, node_id, label=edge_label or "")

            self.resolved_trees[tree_id] = node_id
            return node_id

        # Create a node for this tree
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        self.G.add_node(node_id)
        self.node_paths[node_id] = tree_id  # Store the path for this node

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
                # Handle class type constants which are objects
                if isinstance(result_value, dict):
                    result_value = f"Object with {len(result_value)} fields"
            elif result_type == "scripted":
                script = tree_data["result"].get("script", "...")
                # Only truncate if the option is enabled
                if self.truncate_scripts and len(script) > 30:
                    result_value = f"script: {script[:30]}..."
                else:
                    result_value = f"script: {script}"

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
        """
        Generate a description for a condition node.

        Args:
            condition: The condition object from the decision tree

        Returns:
            A string describing the condition
        """
        condition_type = condition.get("type", "unknown")

        if condition_type == "threshold":
            column_value = condition.get("column_value", "?")
            min_val = condition.get("min", "?")
            max_val = condition.get("max", "?")
            smooth_min = "smooth" if condition.get("smooth_min", True) else "sharp"
            smooth_max = "smooth" if condition.get("smooth_max", True) else "sharp"
            return f"{column_value}: {min_val} to {max_val} ({smooth_min}/{smooth_max})"

        elif condition_type == "world_trait_threshold":
            trait = condition.get("trait", "?")
            min_val = condition.get("min", "?")
            max_val = condition.get("max", "?")
            smooth_min = "smooth" if condition.get("smooth_min", True) else "sharp"
            smooth_max = "smooth" if condition.get("smooth_max", True) else "sharp"
            return f"{trait}: {min_val} to {max_val} ({smooth_min}/{smooth_max})"

        elif condition_type == "script":
            script = condition.get("script", "")
            # Only truncate if the option is enabled
            if self.truncate_scripts and len(script) > 30:
                return f"script: {script[:30]}..."
            else:
                return f"script: {script}"

        elif condition_type in ["and", "or"]:
            conditions = condition.get("conditions", [])
            count = len(conditions)
            if count <= 3:  # For a small number of conditions, show their types
                condition_types = [c.get("type", "?") for c in conditions]
                return f"{condition_type.upper()} {', '.join(condition_types)}"
            else:
                return f"{condition_type.upper()} {count} conditions"

        elif condition_type == "not":
            inner_condition = condition.get("condition", {})
            inner_type = inner_condition.get("type", "?")
            return f"NOT {inner_type}"

        return condition_type

    def get_node_levels(self):
        """
        Calculate the level of each node in the graph for hierarchical layout.

        Returns:
            Dictionary mapping node IDs to their level in the tree
        """
        levels = {}

        # Find root nodes
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        # Use BFS to calculate levels
        for root in root_nodes:
            queue = [(root, 0)]
            visited = {root}

            while queue:
                node, level = queue.pop(0)
                levels[node] = level

                for neighbor in self.G.neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, level + 1))

        return levels

    def scale_layout(self, pos, scale=1.0):
        """
        Scale a layout to reduce node overlap.

        Args:
            pos: Position dictionary from a layout algorithm
            scale: Factor by which to scale the layout

        Returns:
            Scaled position dictionary
        """
        return {node: (x * scale, y * scale) for node, (x, y) in pos.items()}

    def visualize_tree(self, root_tree_id, output_file=None, figsize=(30, 20)):
        """
        Visualize a decision tree.

        Args:
            root_tree_id: ID of the root decision tree
            output_file: Path to save the visualization image (optional)
            figsize: Size of the figure in inches (width, height)

        Returns:
            The graph and positions dictionary
        """
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}  # Initialize node paths dictionary
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the tree
        self.logger.info(f"Processing decision tree: {root_tree_id}")
        self.process_tree(root_tree_id)

        # Create visualization
        plt.figure(figsize=figsize)
        plt.suptitle(f"Decision Tree: {root_tree_id}", fontsize=16)

        # Use a hierarchical layout from NetworkX
        try:
            pos = nx.nx_pydot.pydot_layout(self.G, prog="dot")
            self.logger.info("Using pydot layout algorithm")
        except:
            # Fallback to NetworkX's built-in layout algorithms
            self.logger.warning("Using fallback layout algorithm - for better layout install pydot")
            try:
                # Try multipartite layout based on node levels
                levels = self.get_node_levels()
                pos = nx.multipartite_layout(self.G, subset_key=lambda node: levels.get(node, 0))
                self.logger.info("Using multipartite layout algorithm")
            except:
                # Last resort: spring layout
                self.logger.warning("Using spring layout algorithm as last resort")
                pos = nx.spring_layout(self.G, k=2.0, iterations=100, seed=42)

        # Scale layout to reduce overlap
        pos = self.scale_layout(pos, scale=3.0)

        # Find root nodes (those with no incoming edges)
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        # Draw edges with improved visibility
        nx.draw_networkx_edges(self.G, pos, arrows=True, arrowsize=20, width=1.5,
                               edge_color='gray', alpha=0.6, connectionstyle='arc3,rad=0.1')

        # Prepare node lists for drawing
        normal_nodes = [n for n in self.G.nodes() if n not in root_nodes]

        # Draw normal nodes
        normal_node_sizes = [max(2000, len(self.node_labels.get(node, "")) * 100) for node in normal_nodes]
        normal_node_colors = [self.node_colors.get(node, "gray") for node in normal_nodes]
        if normal_nodes:  # Check if list is not empty
            nx.draw_networkx_nodes(self.G, pos, nodelist=normal_nodes,
                                   node_color=normal_node_colors,
                                   node_size=normal_node_sizes, alpha=0.8)

        # Draw root nodes with special styling
        if root_nodes:  # Check if list is not empty
            root_node_sizes = [max(3000, len(self.node_labels.get(node, "")) * 120) for node in root_nodes]
            nx.draw_networkx_nodes(self.G, pos, nodelist=root_nodes,
                                   node_color='red', node_shape='*',
                                   node_size=root_node_sizes, alpha=0.9)

        # Add path and ROOT to the labels of nodes
        node_labels = {}
        for node in self.G.nodes():
            label = self.node_labels.get(node, "")
            path = self.node_paths.get(node, "")

            # Format the label with path
            if node in root_nodes:
                node_labels[node] = f"ROOT\nPath: {path}\n{label}"
            else:
                node_labels[node] = f"Path: {path}\n{label}"

        # Draw labels with improved readability
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=9,
                                font_weight='bold', font_family="sans-serif")

        # Draw edge labels
        edge_labels = {(u, v): d["label"] for u, v, d in self.G.edges(data=True) if "label" in d}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=9)

        plt.axis("off")
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            self.logger.info(f"Tree visualization saved to {output_file}")
        else:
            plt.show()

        return self.G, pos

    def split_and_visualize(self, root_tree_id, output_prefix, max_depth=2):
        """
        Split a large tree into smaller subtrees and visualize each separately.

        Args:
            root_tree_id: ID of the root decision tree
            output_prefix: Prefix for output file paths
            max_depth: Maximum depth for each subtree

        Returns:
            Number of subtrees created
        """
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}  # Initialize node paths dictionary
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the entire tree
        self.logger.info(f"Processing tree for splitting: {root_tree_id}")
        self.process_tree(root_tree_id)

        # Find root nodes
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        if not root_nodes:
            self.logger.warning("No root nodes found in the graph")
            return 0

        # Create a subgraph starting from each root node
        subtree_count = 0
        for i, root in enumerate(root_nodes):
            # Extract the subgraph with limited depth
            nodes = [root]
            visited = {root}
            current_depth = 0
            frontier = list(self.G.neighbors(root))

            while frontier and current_depth < max_depth:
                current_depth += 1
                next_frontier = []
                for node in frontier:
                    if node not in visited:
                        visited.add(node)
                        nodes.append(node)
                        next_frontier.extend(self.G.neighbors(node))
                frontier = next_frontier

            subgraph = self.G.subgraph(nodes).copy()

            # Skip empty subgraphs
            if len(subgraph) <= 1:
                continue

            # Create output file path
            output_file = f"{output_prefix}_{i + 1}.png" if output_prefix else None

            # Visualize the subgraph
            plt.figure(figsize=(20, 15))
            plt.suptitle(f"Decision Tree: {root_tree_id} (Subtree {i + 1})", fontsize=16)

            try:
                pos = nx.nx_pydot.pydot_layout(subgraph, prog="dot")
            except:
                self.logger.warning(f"Falling back to spring layout for subtree {i + 1}")
                pos = nx.spring_layout(subgraph, k=2.0, iterations=100, seed=42)

            pos = self.scale_layout(pos, scale=2.0)

            # Find root nodes in this subgraph
            sub_root_nodes = [n for n in subgraph.nodes() if subgraph.in_degree(n) == 0]
            normal_nodes = [n for n in subgraph.nodes() if n not in sub_root_nodes]

            # Draw edges
            nx.draw_networkx_edges(subgraph, pos, arrows=True, arrowsize=20, width=1.5,
                                   edge_color='gray', alpha=0.6, connectionstyle='arc3,rad=0.1')

            # Draw normal nodes
            if normal_nodes:
                normal_node_sizes = [max(2000, len(self.node_labels.get(node, "")) * 100) for node in normal_nodes]
                normal_node_colors = [self.node_colors.get(node, "gray") for node in normal_nodes]
                nx.draw_networkx_nodes(subgraph, pos, nodelist=normal_nodes,
                                       node_color=normal_node_colors,
                                       node_size=normal_node_sizes, alpha=0.8)

            # Draw root nodes with special styling
            if sub_root_nodes:
                root_node_sizes = [max(3000, len(self.node_labels.get(node, "")) * 120) for node in sub_root_nodes]
                nx.draw_networkx_nodes(subgraph, pos, nodelist=sub_root_nodes,
                                       node_color='red', node_shape='*',
                                       node_size=root_node_sizes, alpha=0.9)

            # Add path and ROOT to the labels of nodes
            sub_labels = {}
            for node in subgraph.nodes():
                label = self.node_labels.get(node, "")
                path = self.node_paths.get(node, "")

                # Format the label with path
                if node in sub_root_nodes:
                    sub_labels[node] = f"ROOT\nPath: {path}\n{label}"
                else:
                    sub_labels[node] = f"Path: {path}\n{label}"

            # Draw labels
            nx.draw_networkx_labels(subgraph, pos, labels=sub_labels, font_size=9,
                                    font_weight='bold', font_family="sans-serif")

            # Draw edge labels
            sub_edge_labels = {(u, v): d["label"] for u, v, d in subgraph.edges(data=True) if "label" in d}
            nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=sub_edge_labels, font_size=9)

            plt.axis("off")
            plt.tight_layout()

            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches="tight")
                self.logger.info(f"Subtree {i + 1} visualization saved to {output_file}")
            else:
                plt.show()

            plt.close()
            subtree_count += 1

        self.logger.info(f"Created {subtree_count} subtree visualizations")
        return subtree_count

    def batch_visualize(self, start_dir=None, output_dir="tree_visualizations", split=False):
        """
        Visualize all decision trees in a directory.

        Args:
            start_dir: Starting directory (defaults to decision_tree_dir)
            output_dir: Directory to save visualization images
            split: Whether to split large trees into subtrees
        """
        if start_dir is None:
            start_dir = self.decision_tree_dir
        else:
            start_dir = Path(start_dir)

        output_dir = Path(output_dir)

        # Clean output directory before starting
        self.clean_output(output_dir)

        # Find all JSON files in the directory and subdirectories
        tree_count = 0
        self.logger.info(f"Starting batch visualization from {start_dir}")
        for root, _, files in os.walk(start_dir):
            root_path = Path(root)
            for file in files:
                if file.endswith(".json"):
                    file_path = root_path / file
                    try:
                        relative_path = file_path.relative_to(self.decision_tree_dir)
                        tree_id = str(relative_path.with_suffix(""))

                        # Create output directory structure
                        tree_output_dir = output_dir / relative_path.parent
                        os.makedirs(tree_output_dir, exist_ok=True)

                        output_file = tree_output_dir / f"{file.replace('.json', '.png')}"
                        self.logger.info(f"Visualizing tree: {tree_id}")

                        if split:
                            # Split and visualize the tree
                            prefix = str(tree_output_dir / file.replace('.json', ''))
                            self.split_and_visualize(tree_id, prefix)
                        else:
                            # Visualize the entire tree
                            self.visualize_tree(tree_id, output_file)

                        tree_count += 1
                    except Exception as e:
                        self.logger.error(f"Error visualizing {file_path}: {e}")

        self.logger.info(f"Processed {tree_count} decision trees")

    def export_tree_as_markdown(self, root_tree_id, output_file=None):
        """
        Export a decision tree as a Markdown file with hierarchical structure.

        Args:
            root_tree_id: ID of the root decision tree
            output_file: Path to save the Markdown file (optional)

        Returns:
            Markdown content as string
        """
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the tree
        self.logger.info(f"Processing tree for Markdown export: {root_tree_id}")
        self.process_tree(root_tree_id)

        # Find root nodes
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        if not root_nodes:
            self.logger.warning("No root nodes found in the tree")
            return "No root nodes found in the tree."

        # Generate markdown
        markdown = f"# Decision Tree: {root_tree_id}\n\n"

        for root in root_nodes:
            markdown += self._node_to_markdown(root)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            self.logger.info(f"Markdown tree saved to {output_file}")

        return markdown

    def _node_to_markdown(self, node_id, depth=0):
        """
        Recursively convert a node and its children to Markdown.

        Args:
            node_id: ID of the node to convert
            depth: Current depth in the tree (for indentation)

        Returns:
            Markdown representation of the node and its children
        """
        indent = "  " * depth
        label = self.node_labels.get(node_id, 'Unknown Node').replace('\n', ' - ')
        path = self.node_paths.get(node_id, '')

        # Mark root nodes with special indicator and include path
        if self.G.in_degree(node_id) == 0:
            markdown = f"{indent}- **[ROOT] Path: `{path}`**\n{indent}  **{label}**\n"
        else:
            markdown = f"{indent}- **Path: `{path}`**\n{indent}  **{label}**\n"

        for _, child, data in self.G.out_edges(node_id, data=True):
            edge_label = data.get("label", "")
            child_markdown = self._node_to_markdown(child, depth + 1)

            if edge_label:
                markdown += f"{indent}  - *{edge_label}*:\n{child_markdown}"
            else:
                markdown += child_markdown

        return markdown

    def export_tree_as_html(self, root_tree_id, output_file=None):
        """
        Export a decision tree as an HTML file with collapsible tree structure.

        Args:
            root_tree_id: ID of the root decision tree
            output_file: Path to save the HTML file (optional)

        Returns:
            HTML content as string
        """
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the tree
        self.logger.info(f"Processing tree for HTML export: {root_tree_id}")
        self.process_tree(root_tree_id)

        # Find root nodes
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        if not root_nodes:
            self.logger.warning("No root nodes found in the tree")
            return "<p>No root nodes found in the tree.</p>"

        # Generate HTML
        html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Decision Tree: {root_tree_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            .tree-node {{
                margin: 10px 0;
            }}
            .node-content {{
                padding: 5px;
                border-radius: 4px;
                display: inline-block;
            }}
            .result-node {{
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
            }}
            .condition-node {{
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
            }}
            .missing-node {{
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
            }}
            .root-node {{
                font-weight: bold;
                border: 2px solid #dc3545;
                position: relative;
            }}
            .root-node::before {{
                content: "ROOT";
                position: absolute;
                top: -15px;
                left: 5px;
                background-color: #dc3545;
                color: white;
                padding: 0 5px;
                font-size: 0.8em;
                border-radius: 3px;
            }}
            .edge-label {{
                margin-left: 10px;
                font-style: italic;
                color: #6c757d;
            }}
            .children {{
                margin-left: 30px;
                border-left: 1px solid #ddd;
                padding-left: 10px;
            }}
            .collapsible {{
                cursor: pointer;
                padding: 5px;
                width: 100%;
                text-align: left;
                outline: none;
            }}
            .active, .collapsible:hover {{
                background-color: #f1f1f1;
            }}
            .content {{
                display: block;
            }}
            .node-path {{
                color: #6c757d;
                font-family: monospace;
                font-size: 0.9em;
                margin-bottom: 3px;
                display: block;
            }}
        </style>
        <script>
            function toggleCollapse(element) {{
                var content = element.nextElementSibling;
                if (content.style.display === "none") {{
                    content.style.display = "block";
                }} else {{
                    content.style.display = "none";
                }}
            }}
        </script>
    </head>
    <body>
        <h1>Decision Tree: {root_tree_id}</h1>
        <div class="tree-container">
    """

        for root in root_nodes:
            html += self._node_to_html(root)

        html += """
        </div>
    </body>
    </html>
    """

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            self.logger.info(f"HTML tree saved to {output_file}")

        return html

    def _node_to_html(self, node_id):
        """
        Recursively convert a node and its children to HTML.

        Args:
            node_id: ID of the node to convert

        Returns:
            HTML representation of the node and its children
        """
        label = self.node_labels.get(node_id, "Unknown Node").replace('\n', '<br>')
        node_color = self.node_colors.get(node_id, "gray")
        path = self.node_paths.get(node_id, "")

        # Determine node type based on color
        if node_color == "lightgreen":
            node_class = "result-node"
        elif node_color == "lightblue":
            node_class = "condition-node"
        elif node_color == "gray":
            node_class = "missing-node"
        else:
            node_class = ""

        # Add root-node class for root nodes
        is_root = self.G.in_degree(node_id) == 0
        if is_root:
            node_class += " root-node"

        # Start node
        html = f'<div class="tree-node">\n'

        # Node content (collapsible if it has children)
        if list(self.G.successors(node_id)):
            html += f'<button class="collapsible node-content {node_class}" onclick="toggleCollapse(this)">'
            html += f'<span class="node-path">Path: {path}</span>{label}</button>\n'
        else:
            html += f'<div class="node-content {node_class}">'
            html += f'<span class="node-path">Path: {path}</span>{label}</div>\n'

        # Add children if any
        children = list(self.G.out_edges(node_id, data=True))
        if children:
            html += f'<div class="content children">\n'

            for _, child, data in children:
                edge_label = data.get("label", "")
                if edge_label:
                    html += f'<div class="edge-label">{edge_label}:</div>\n'
                html += self._node_to_html(child)

            html += '</div>\n'

        html += '</div>\n'

        return html

    def export_tree_as_json(self, root_tree_id, output_file=None):
        """
        Export a decision tree as a JSON file with full structure.

        Args:
            root_tree_id: ID of the root decision tree
            output_file: Path to save the JSON file (optional)

        Returns:
            JSON object representing the tree
        """
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.node_colors = {}
        self.node_paths = {}
        self.node_counter = 0
        self.resolved_trees = {}

        # Process the tree
        self.logger.info(f"Processing tree for JSON export: {root_tree_id}")
        self.process_tree(root_tree_id)

        # Find root nodes
        root_nodes = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]

        if not root_nodes:
            self.logger.warning("No root nodes found in the tree")
            return {"error": "No root nodes found in the tree"}

        # Create JSON structure
        tree_json = {
            "tree_id": root_tree_id,
            "nodes": {},
            "root_nodes": [str(n) for n in root_nodes]
        }

        # Build nodes dictionary
        for node in self.G.nodes():
            label = self.node_labels.get(node, "Unknown Node")
            node_type = "unknown"
            path = self.node_paths.get(node, "")

            if "Result:" in label:
                node_type = "result"
            elif "Condition:" in label:
                node_type = "condition"
            elif "Missing:" in label:
                node_type = "missing"

            # Get children with edge labels
            children = []
            for _, child, data in self.G.out_edges(node, data=True):
                edge_label = data.get("label", "")
                children.append({
                    "node_id": str(child),
                    "edge_label": edge_label
                })

            tree_json["nodes"][str(node)] = {
                "label": label,
                "path": path,
                "type": node_type,
                "is_root": node in root_nodes,
                "children": children
            }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tree_json, f, indent=2)
            self.logger.info(f"JSON tree saved to {output_file}")

        return tree_json

    def batch_export_trees(self, start_dir=None, output_dir="tree_exports", format="html"):
        """
        Export all decision trees in a directory as HTML, Markdown, or JSON files.

        Args:
            start_dir: Starting directory (defaults to decision_tree_dir)
            output_dir: Directory to save exported files
            format: Export format, either "html", "markdown", or "json"
        """
        if start_dir is None:
            start_dir = self.decision_tree_dir
        else:
            start_dir = Path(start_dir)

        output_dir = Path(output_dir)

        # Clean output directory before starting
        self.clean_output(output_dir)

        # Find all JSON files in the directory and subdirectories
        tree_count = 0
        self.logger.info(f"Starting batch export in {format} format from {start_dir}")
        for root, _, files in os.walk(start_dir):
            root_path = Path(root)
            for file in files:
                if file.endswith(".json"):
                    file_path = root_path / file
                    try:
                        relative_path = file_path.relative_to(self.decision_tree_dir)
                        tree_id = str(relative_path.with_suffix(""))

                        # Create output directory structure
                        tree_output_dir = output_dir / relative_path.parent
                        os.makedirs(tree_output_dir, exist_ok=True)

                        # Choose format and export
                        if format.lower() == "html":
                            output_file = tree_output_dir / f"{file.replace('.json', '.html')}"
                            self.logger.info(f"Exporting tree as HTML: {tree_id}")
                            self.export_tree_as_html(tree_id, output_file)
                        elif format.lower() == "json":
                            output_file = tree_output_dir / f"{file.replace('.json', '_tree.json')}"
                            self.logger.info(f"Exporting tree as JSON: {tree_id}")
                            self.export_tree_as_json(tree_id, output_file)
                        else:
                            output_file = tree_output_dir / f"{file.replace('.json', '.md')}"
                            self.logger.info(f"Exporting tree as Markdown: {tree_id}")
                            self.export_tree_as_markdown(tree_id, output_file)

                        tree_count += 1
                    except Exception as e:
                        self.logger.error(f"Error exporting {file_path}: {e}")

        self.logger.info(f"Processed {tree_count} decision trees")



if __name__ == "__main__":
    base_dir = "Imports/BigGlobe"

    if not os.path.exists("OutPut") or not os.path.isdir("OutPut"):
        os.makedirs("OutPut")

    # Create visualizer with option to show full scripts instead of truncating them
    visualizer = BigGlobeDecisionTreeVisualizer(base_dir, truncate_scripts=False)

    visualizer.batch_export_trees(output_dir="OutPut/DecisionTreeJson", format="json")
    visualizer.batch_export_trees(output_dir="OutPut/DecisionTreeHtml", format="html")
    visualizer.batch_export_trees(output_dir="OutPut/DecisionTreeMarkdown", format="markdown")
