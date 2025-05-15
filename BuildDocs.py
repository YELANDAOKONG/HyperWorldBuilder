# -*- coding: utf-8 -*-
import os
import sys
import json
import shutil
import logging
import colorlog
from pathlib import Path
from datetime import datetime

from DisplayTextX import BigGlobeDecisionTreeVisualizer


class DocumentationBuilder:
    def __init__(self, base_dirs=None, output_dir="docs"):
        """
        Initialize the documentation builder.

        Args:
            base_dirs: Dictionary of paths to the Big Globe mod files directories
                       with keys: 'root', 'main', 'debug' (default: None)
            output_dir: Output directory for the documentation (default: docs)
        """
        self.base_dirs = base_dirs or {}
        self.output_dir = Path(output_dir)
        self.files_dir = self.output_dir / "files"
        self.origin_dir = self.output_dir / "origin"  # New directory for original JSON files

        # Set up colorful logging
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

        self.logger = logging.getLogger('doc_builder')
        self.logger.setLevel(logging.INFO)
        # Remove any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        # Prevent log propagation to root logger
        self.logger.propagate = False

        # Create visualizer instances for each base directory
        self.visualizers = {}
        for name, dir_path in self.base_dirs.items():
            if dir_path:
                self.visualizers[name] = BigGlobeDecisionTreeVisualizer(dir_path, truncate_scripts=False)

    def clean_output_directory(self):
        """Clean the entire output directory by removing all its contents"""
        if self.output_dir.exists():
            self.logger.info(f"Cleaning output directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)

        # Create output, files, and origin directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.origin_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created output directories: {self.output_dir}, {self.files_dir}, and {self.origin_dir}")

    def build_documentation(self):
        """Build the full documentation"""
        self.clean_output_directory()

        # Create a dictionary to track which builds were successful
        build_statuses = {name: False for name in self.visualizers}

        # Process each build type
        for name, visualizer in self.visualizers.items():
            if name in self.base_dirs and self.base_dirs[name]:
                # Copy original JSON files
                self.logger.info(f"Copying original JSON files for {name}...")
                source_dir = Path(self.base_dirs[name])
                target_dir = self.origin_dir / name
                self._copy_original_json_files(source_dir, target_dir)

                # Create a temporary directory for the visualizations
                temp_dir = Path(f"temp_visualizations_{name}")
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir()

                # Generate HTML visualizations
                self.logger.info(f"Generating HTML visualizations for {name}...")
                visualizer.batch_export_trees(output_dir=temp_dir, format="beautified_html")

                # Copy files to docs directory and build directory structure
                target_dir = self.files_dir / name
                self.logger.info(f"Copying files to {target_dir}...")

                # First copy all files
                self._copy_files(temp_dir, target_dir)

                # Clean up temporary directory
                shutil.rmtree(temp_dir)
                self.logger.info(f"Files for {name} successfully copied")

                # Mark this build as successful
                build_statuses[name] = True

        # Create directory indexes for all build types
        for name in self.visualizers:
            if build_statuses[name]:
                self._create_directory_indexes(self.files_dir / name, name)
                self._create_json_directory_indexes(self.origin_dir / name, name)

        # Generate main index page
        self.logger.info("Generating main index page...")
        self._create_main_index(build_statuses)

        self.logger.info(f"All documentation successfully built in {self.output_dir}")

    def _copy_original_json_files(self, source_dir, target_dir):
        """
        Copy original JSON files from the source directory to the target directory.

        Args:
            source_dir: Source directory containing the original files
            target_dir: Target directory to copy files to
        """
        # Track the number of JSON files copied
        json_count = 0

        # Look for decision tree files specifically
        decision_tree_dir = source_dir / "data" / "bigglobe" / "worldgen" / "bigglobe_decision_tree"
        if decision_tree_dir.exists():
            for root, _, files in os.walk(decision_tree_dir):
                root_path = Path(root)

                # Get relative path from the decision tree directory
                try:
                    rel_path = root_path.relative_to(decision_tree_dir)
                except ValueError:
                    # This is the decision tree directory itself
                    rel_path = Path("")

                current_target_dir = target_dir / "data" / "bigglobe" / "worldgen" / "bigglobe_decision_tree" / rel_path
                current_target_dir.mkdir(parents=True, exist_ok=True)

                # Copy JSON files
                for file in files:
                    if file.endswith(".json"):
                        source_file = root_path / file
                        target_file = current_target_dir / file
                        shutil.copy2(source_file, target_file)
                        json_count += 1

        self.logger.info(f"Copied {json_count} JSON files from {source_dir} to {target_dir}")

    def _copy_files(self, source_dir, target_dir):
        """
        Copy files from the source directory to the target directory.

        Args:
            source_dir: Source directory containing the visualizations
            target_dir: Target directory to copy files to
        """
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Collect and copy all files
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)

            # Skip empty directories
            if not files and not dirs:
                continue

            # Get relative path from the source directory
            try:
                rel_path = root_path.relative_to(source_dir)
                current_target_dir = target_dir / rel_path
            except ValueError:
                # This is the source directory itself
                current_target_dir = target_dir

            # Create the target directory
            current_target_dir.mkdir(parents=True, exist_ok=True)

            # Copy files
            for file in files:
                if file.endswith(".html") and file != "index.html":
                    source_file = root_path / file
                    target_file = current_target_dir / file
                    shutil.copy2(source_file, target_file)

    def _create_directory_indexes(self, base_dir, build_type):
        """
        Create index.html files for the directory structure.

        Args:
            base_dir: Base directory to start from
            build_type: The type of build (root, main, or debug)
        """
        # Create a dictionary to store the directory structure
        dir_structure = self._scan_directory_structure(base_dir)

        # Create index files for each directory
        for dir_path, (subdirs, files) in dir_structure.items():
            target_dir = base_dir / dir_path if dir_path else base_dir

            # Create the index file content
            index_content = self._generate_tree_view_index(
                dir_path,
                subdirs,
                files,
                base_dir,
                build_type
            )

            # Write the index file
            index_file = target_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)

            self.logger.info(f"Created tree view index for {build_type}/{dir_path or 'root directory'}")

    def _scan_directory_structure(self, base_dir):
        """
        Scan a directory to create a structure map.

        Args:
            base_dir: Base directory to scan

        Returns:
            Dictionary mapping relative paths to tuples of (subdirectories, files)
        """
        dir_structure = {}

        for root, dirs, files in os.walk(base_dir):
            root_path = Path(root)

            # Get relative path from the base directory
            try:
                rel_path = root_path.relative_to(base_dir)
                rel_path_str = str(rel_path) if rel_path.parts else ""
            except ValueError:
                # This is the base directory itself
                rel_path_str = ""

            # Filter out index.html files
            html_files = [f for f in files if f.endswith(".html") and f != "index.html"]

            # Collect subdirectories (excluding hidden directories)
            subdirs = [d for d in dirs if not d.startswith('.')]

            # Add to structure
            dir_structure[rel_path_str] = (subdirs, html_files)

        return dir_structure

    def _generate_tree_view_index(self, current_dir, subdirs, html_files, base_dir, build_type):
        """
        Generate HTML content for a tree view index file.

        Args:
            current_dir: Current directory path (relative to base_dir)
            subdirs: List of subdirectories in this directory
            html_files: List of HTML files in this directory
            base_dir: Base directory path
            build_type: The type of build (root, main, or debug)

        Returns:
            String containing the HTML content for the index file
        """
        # Determine directory name for display
        if current_dir:
            dir_display = Path(current_dir).name
            title = f"BigGlobe Decision Trees - {build_type.capitalize()} - {dir_display}"
            heading = f"Decision Trees in {dir_display}"
        else:
            title = f"BigGlobe Decision Trees - {build_type.capitalize()}"
            heading = f"BigGlobe Decision Trees - {build_type.capitalize()}"

        # Generate paths for navigation
        current_path = Path(current_dir) if current_dir else Path()

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-color: #4a6da7;
            --secondary-color: #8aa9d6;
            --accent-color: #ffb200;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --success-color: #28a745;
            --info-color: #17a2b8;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --folder-color: #ffd700;
            --folder-hover: #f0c800;
            --file-color: #4caf50;
            --file-hover: #388e3c;
            --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-main);
            line-height: 1.6;
            color: var(--dark-color);
            background-color: var(--light-color);
            padding: 0;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .container {{
            width: 100%;
            margin: 0;
            padding: 0;
            flex: 1;
        }}

        header {{
            background-color: var(--primary-color);
            color: white;
            padding: 1.5rem;
            margin-bottom: 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-image: linear-gradient(135deg, var(--primary-color) 0%, #2a4073 100%);
        }}

        header h1 {{
            margin: 0;
            font-size: 2rem;
            color: white;
        }}

        h1, h2, h3 {{
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}

        .breadcrumb {{
            background-color: white;
            padding: 1rem;
            margin-bottom: 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .breadcrumb a {{
            background-color: var(--secondary-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
            text-decoration: none;
            font-weight: 500;
        }}

        .breadcrumb a:hover {{
            background-color: var(--primary-color);
            text-decoration: none;
        }}

        .card {{
            background-color: white;
            padding: 1.5rem;
            margin-bottom: 0;
            box-shadow: none;
        }}

        /* Tree View Styling */
        .tree {{
            margin: 1rem 0;
        }}

        .tree-item {{
            list-style-type: none;
            margin-bottom: 0.5rem;
        }}

        .tree-folder, .tree-file {{
            display: block;
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .tree-folder {{
            background-color: var(--folder-color);
            cursor: pointer;
        }}

        .tree-folder:hover {{
            background-color: var(--folder-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .tree-file {{
            background-color: var(--file-color);
        }}

        .tree-file:hover {{
            background-color: var(--file-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .tree-icon {{
            margin-right: 0.5rem;
        }}

        .tree-toggle {{
            float: right;
            transition: transform 0.3s ease;
            font-size: 1.2rem;
        }}

        .tree-children {{
            display: none;
            padding-left: 1.5rem;
            margin-top: 0.5rem;
            border-left: 2px solid #eee;
        }}

        .tree-children.open {{
            display: block;
            animation: fadeIn 0.5s ease;
        }}

        /* Depth colors */
        .tree-folder.depth-0 {{ background-color: #5d93e1; }}
        .tree-folder.depth-0:hover {{ background-color: #4a7ec3; }}

        .tree-folder.depth-1 {{ background-color: #7e57c2; }}
        .tree-folder.depth-1:hover {{ background-color: #6944a8; }}

        .tree-folder.depth-2 {{ background-color: #ec407a; }}
        .tree-folder.depth-2:hover {{ background-color: #d63467; }}

        .tree-folder.depth-3 {{ background-color: #ff7043; }}
        .tree-folder.depth-3:hover {{ background-color: #e56238; }}

        .tree-folder.depth-4 {{ background-color: #ffca28; }}
        .tree-folder.depth-4:hover {{ background-color: #e6b623; }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        footer {{
            margin-top: 0;
            padding: 1rem;
            text-align: center;
            color: var(--dark-color);
            font-size: 0.9rem;
            background-color: white;
            box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
        }}

        .json-link {{
            margin-top: 1rem;
            display: block;
            padding: 0.75rem;
            background-color: var(--warning-color);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            transition: all 0.3s;
        }}

        .json-link:hover {{
            background-color: #e0a800;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{heading}</h1>
        </header>

        <main>
            <div class="breadcrumb">
                <a href="{('../' * len(current_path.parts))}../../index.html">Main Index</a>
                {f'<a href="{("../" * len(current_path.parts))}index.html">{build_type.capitalize()} Root</a>' if current_dir else ""}
                {self._generate_breadcrumb_path(current_path)}
                <a href="{('../' * len(current_path.parts))}../../origin/{build_type}/{'data/bigglobe/worldgen/bigglobe_decision_tree/' + current_dir if current_dir else ''}index.html">View Original JSON Files</a>
            </div>

            <div class="card">
                <h2>Directory Structure</h2>
                <div class="tree">
"""

        # Generate the tree view
        if subdirs or html_files:
            html += self._generate_tree_content(subdirs, html_files, current_path, 0)
        else:
            html += "                    <p>No files found in this directory.</p>"

        html += """
                </div>
            </div>
        </main>

        <footer>
            <p>Generated by BigGlobe Decision Tree Documentation Builder on """ + datetime.now().strftime(
            "%Y-%m-%d %H:%M") + """</p>
        </footer>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers to all folder items
            document.querySelectorAll('.tree-folder').forEach(folder => {
                folder.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Toggle the next sibling (tree-children container)
                    const children = this.nextElementSibling;
                    if (children && children.classList.contains('tree-children')) {
                        children.classList.toggle('open');

                        // Toggle the icon
                        const toggleIcon = this.querySelector('.tree-toggle');
                        if (toggleIcon) {
                            if (children.classList.contains('open')) {
                                toggleIcon.innerHTML = '<i class="fas fa-chevron-down"></i>';
                            } else {
                                toggleIcon.innerHTML = '<i class="fas fa-chevron-right"></i>';
                            }
                        }
                    }
                });
            });

            // Automatically open the current path
            const pathParts = window.location.pathname.split('/');
            const currentDir = pathParts[pathParts.length - 2] || '';

            if (currentDir) {
                document.querySelectorAll(`.tree-folder[data-path="${currentDir}"]`).forEach(folder => {
                    folder.click();
                });
            }
        });
    </script>
</body>
</html>
"""
        return html

    def _generate_breadcrumb_path(self, current_path):
        """Generate breadcrumb navigation for the current path"""
        if not current_path.parts:
            return ""

        breadcrumbs = []
        current_parts = []

        for part in current_path.parts:
            current_parts.append(part)
            path_to_here = '/'.join(current_parts)
            back_steps = len(current_path.parts) - len(current_parts)

            breadcrumbs.append(f'<a href="{("../" * back_steps)}index.html">{part}</a>')

        return ' / '.join(breadcrumbs)

    def _generate_tree_content(self, subdirs, files, current_path, depth=0):
        """
        Recursively generate HTML for the tree view.

        Args:
            subdirs: List of subdirectories
            files: List of files
            current_path: Current path object
            depth: Current depth in the tree

        Returns:
            HTML string for this level of the tree
        """
        html = ""

        # Add folders first
        for subdir in sorted(subdirs):
            subdir_path = current_path / subdir if current_path.parts else Path(subdir)

            html += f"""
                <div class="tree-item">
                    <div class="tree-folder depth-{min(depth, 4)}" data-path="{subdir}">
                        <i class="fas fa-folder tree-icon"></i>
                        {subdir}
                        <span class="tree-toggle"><i class="fas fa-chevron-right"></i></span>
                    </div>
                    <div class="tree-children">
                        <div class="tree-item">
                            <a href="{subdir}/index.html" class="tree-file">
                                <i class="fas fa-compass tree-icon"></i>
                                Navigate to {subdir}
                            </a>
                        </div>
                    </div>
                </div>
"""

        # Add files
        for file in sorted(files):
            file_name = file.replace('.html', '')

            html += f"""
                <div class="tree-item">
                    <a href="{file}" class="tree-file">
                        <i class="fas fa-file-alt tree-icon"></i>
                        {file_name}
                    </a>
                </div>
"""

        return html

    def _create_json_directory_indexes(self, base_dir, build_type):
        """
        Create index.html files for browsing original JSON files.

        Args:
            base_dir: Base directory to start from
            build_type: The type of build (root, main, or debug)
        """
        # Early return if directory doesn't exist
        if not base_dir.exists():
            self.logger.warning(f"Origin directory for {build_type} does not exist, skipping JSON index creation")
            return

        # First, we need to create the decision tree directory path if it doesn't exist
        decision_tree_dir = base_dir / "data" / "bigglobe" / "worldgen" / "bigglobe_decision_tree"
        if not decision_tree_dir.exists():
            self.logger.warning(
                f"Decision tree directory for {build_type} does not exist, skipping JSON index creation")
            return

        # Create a dictionary to store the directory structure
        json_structure = self._scan_json_directory_structure(decision_tree_dir)

        # Create index files for the base directory
        base_index_content = self._generate_json_base_index(build_type)
        base_index_file = base_dir / "index.html"
        with open(base_index_file, 'w', encoding='utf-8') as f:
            f.write(base_index_content)
        self.logger.info(f"Created base JSON index for {build_type}")

        # Create the data directory index
        data_dir = base_dir / "data"
        data_index_content = self._generate_json_navigation_index("data", build_type, ["bigglobe"])
        os.makedirs(data_dir, exist_ok=True)
        data_index_file = data_dir / "index.html"
        with open(data_index_file, 'w', encoding='utf-8') as f:
            f.write(data_index_content)

        # Create the bigglobe directory index
        bigglobe_dir = data_dir / "bigglobe"
        bigglobe_index_content = self._generate_json_navigation_index("bigglobe", build_type, ["worldgen"])
        os.makedirs(bigglobe_dir, exist_ok=True)
        bigglobe_index_file = bigglobe_dir / "index.html"
        with open(bigglobe_index_file, 'w', encoding='utf-8') as f:
            f.write(bigglobe_index_content)

        # Create the worldgen directory index
        worldgen_dir = bigglobe_dir / "worldgen"
        worldgen_index_content = self._generate_json_navigation_index("worldgen", build_type,
                                                                      ["bigglobe_decision_tree"])
        os.makedirs(worldgen_dir, exist_ok=True)
        worldgen_index_file = worldgen_dir / "index.html"
        with open(worldgen_index_file, 'w', encoding='utf-8') as f:
            f.write(worldgen_index_content)

        # Create index files for each directory in the decision tree
        for dir_path, (subdirs, json_files) in json_structure.items():
            target_dir = decision_tree_dir / dir_path if dir_path else decision_tree_dir

            # Create JSON file viewers for each file
            for json_file in json_files:
                json_path = target_dir / json_file
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)
                        formatted_json = json.dumps(json_content, indent=2)

                    viewer_content = self._generate_json_viewer(
                        json_file,
                        formatted_json,
                        build_type,
                        str(dir_path) if dir_path else ""
                    )

                    viewer_path = target_dir / f"{json_file}.html"
                    with open(viewer_path, 'w', encoding='utf-8') as f:
                        f.write(viewer_content)
                except Exception as e:
                    self.logger.error(f"Error creating JSON viewer for {json_path}: {e}")

            # Create the directory index
            index_content = self._generate_json_directory_index(
                dir_path,
                subdirs,
                json_files,
                build_type
            )

            index_file = target_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)

            self.logger.info(f"Created JSON directory index for {build_type}/{dir_path or 'decision tree root'}")

    def _scan_json_directory_structure(self, base_dir):
        """
        Scan a directory to create a structure map of JSON files.

        Args:
            base_dir: Base directory to scan

        Returns:
            Dictionary mapping relative paths to tuples of (subdirectories, json_files)
        """
        dir_structure = {}

        for root, dirs, files in os.walk(base_dir):
            root_path = Path(root)

            # Get relative path from the base directory
            try:
                rel_path = root_path.relative_to(base_dir)
                rel_path_str = str(rel_path) if rel_path.parts else ""
            except ValueError:
                # This is the base directory itself
                rel_path_str = ""

            # Filter for JSON files only
            json_files = [f for f in files if f.endswith(".json")]

            # Collect subdirectories (excluding hidden directories)
            subdirs = [d for d in dirs if not d.startswith('.')]

            # Add to structure
            dir_structure[rel_path_str] = (subdirs, json_files)

        return dir_structure

    def _generate_json_base_index(self, build_type):
        """
        Generate a base index file for the JSON files.

        Args:
            build_type: The type of build (root, main, or debug)

        Returns:
            HTML content for the base index file
        """
        title = f"Original JSON Files - {build_type.capitalize()}"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-color: #4a6da7;
            --secondary-color: #8aa9d6;
            --accent-color: #ffb200;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --success-color: #28a745;
            --info-color: #17a2b8;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --folder-color: #ff9800;
            --folder-hover: #f57c00;
            --file-color: #9c27b0;
            --file-hover: #7b1fa2;
            --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-main);
            line-height: 1.6;
            color: var(--dark-color);
            background-color: var(--light-color);
            padding: 0;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .container {{
            width: 100%;
            margin: 0;
            padding: 0;
            flex: 1;
        }}

        header {{
            background-color: var(--warning-color);
            color: white;
            padding: 1.5rem;
            margin-bottom: 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-image: linear-gradient(135deg, var(--warning-color) 0%, #e0a800 100%);
        }}

        header h1 {{
            margin: 0;
            font-size: 2rem;
            color: white;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }}

        .breadcrumb {{
            background-color: white;
            padding: 1rem;
            margin-bottom: 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .breadcrumb a {{
            background-color: var(--secondary-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
            text-decoration: none;
            font-weight: 500;
        }}

        .breadcrumb a:hover {{
            background-color: var(--primary-color);
            text-decoration: none;
        }}

        .card {{
            background-color: white;
            padding: 1.5rem;
            margin: 0;
        }}

        .navigation {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}

        .nav-item {{
            background-color: var(--folder-color);
            color: white;
            padding: 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .nav-item:hover {{
            background-color: var(--folder-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .nav-icon {{
            margin-right: 0.5rem;
            font-size: 1.2rem;
        }}

        footer {{
            margin-top: 0;
            padding: 1rem;
            text-align: center;
            color: var(--dark-color);
            font-size: 0.9rem;
            background-color: white;
            box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
        }}

        .trees-link {{
            margin-top: 1rem;
            display: block;
            padding: 1rem;
            background-color: var(--primary-color);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .trees-link:hover {{
            background-color: #395885;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Original JSON Files - {build_type.capitalize()}</h1>
        </header>

        <div class="breadcrumb">
            <a href="../../index.html">Main Index</a>
            <a href="../../files/{build_type}/index.html">View Decision Trees</a>
        </div>

        <div class="card">
            <h2>BigGlobe JSON Files</h2>
            <p>Browse the original JSON files for the BigGlobe mod.</p>

            <div class="navigation">
                <a href="data/index.html" class="nav-item">
                    <i class="fas fa-folder nav-icon"></i>data
                </a>
            </div>

            <a href="../../files/{build_type}/index.html" class="trees-link">
                <i class="fas fa-sitemap"></i> View Decision Tree Visualizations
            </a>
        </div>

        <footer>
            <p>Generated by BigGlobe Decision Tree Documentation Builder on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _generate_json_navigation_index(self, current_dir, build_type, subdirs):
        """
        Generate a navigation index file for JSON directories.

        Args:
            current_dir: Current directory name
            build_type: The type of build
            subdirs: Subdirectories to include in the navigation

        Returns:
            HTML content for the navigation index
        """
        title = f"Original JSON Files - {build_type.capitalize()} - {current_dir}"

        # Create breadcrumb path
        breadcrumbs = []
        path_parts = current_dir.split('/')

        # Add main index and origin root
        breadcrumbs.append(f'<a href="{("../" * len(path_parts))}../../index.html">Main Index</a>')
        breadcrumbs.append(f'<a href="{("../" * len(path_parts))}index.html">{build_type.capitalize()} Root</a>')

        # Add path components
        current_path = []
        for i, part in enumerate(path_parts):
            if part:  # Skip empty parts
                current_path.append(part)
                back_steps = len(path_parts) - i - 1
                breadcrumbs.append(f'<a href="{("../" * back_steps)}index.html">{part}</a>')

        breadcrumb_html = ' / '.join(breadcrumbs)

        # Generate HTML
        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                :root {{
                    --primary-color: #4a6da7;
                    --secondary-color: #8aa9d6;
                    --accent-color: #ffb200;
                    --light-color: #f8f9fa;
                    --dark-color: #343a40;
                    --success-color: #28a745;
                    --info-color: #17a2b8;
                    --warning-color: #ffc107;
                    --danger-color: #dc3545;
                    --folder-color: #ff9800;
                    --folder-hover: #f57c00;
                    --file-color: #9c27b0;
                    --file-hover: #7b1fa2;
                    --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}

                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: var(--font-main);
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: var(--light-color);
                    padding: 0;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}

                .container {{
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    flex: 1;
                }}

                header {{
                    background-color: var(--warning-color);
                    color: white;
                    padding: 1.5rem;
                    margin-bottom: 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    background-image: linear-gradient(135deg, var(--warning-color) 0%, #e0a800 100%);
                }}

                header h1 {{
                    margin: 0;
                    font-size: 2rem;
                    color: white;
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                }}

                .breadcrumb {{
                    background-color: white;
                    padding: 1rem;
                    margin-bottom: 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}

                .breadcrumb a {{
                    background-color: var(--secondary-color);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    transition: background-color 0.3s;
                    text-decoration: none;
                    font-weight: 500;
                }}

                .breadcrumb a:hover {{
                    background-color: var(--primary-color);
                    text-decoration: none;
                }}

                .card {{
                    background-color: white;
                    padding: 1.5rem;
                    margin: 0;
                }}

                .navigation {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1rem;
                    margin: 1rem 0;
                }}

                .nav-item {{
                    background-color: var(--folder-color);
                    color: white;
                    padding: 1rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}

                .nav-item:hover {{
                    background-color: var(--folder-hover);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}

                .nav-icon {{
                    margin-right: 0.5rem;
                    font-size: 1.2rem;
                }}

                footer {{
                    margin-top: 0;
                    padding: 1rem;
                    text-align: center;
                    color: var(--dark-color);
                    font-size: 0.9rem;
                    background-color: white;
                    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
                }}

                .trees-link {{
                    margin-top: 1rem;
                    display: block;
                    padding: 1rem;
                    background-color: var(--primary-color);
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}

                .trees-link:hover {{
                    background-color: #395885;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Original JSON Files - {current_dir}</h1>
                </header>

                <div class="breadcrumb">
                    {breadcrumb_html}
                    <a href="{("../" * len(path_parts))}../../files/{build_type}/index.html">View Decision Trees</a>
                </div>

                <div class="card">
                    <h2>Directories</h2>

                    <div class="navigation">
        """

        # Add navigation items for subdirectories
        for subdir in subdirs:
            html += f"""
                        <a href="{subdir}/index.html" class="nav-item">
                            <i class="fas fa-folder nav-icon"></i>{subdir}
                        </a>
        """

        html += f"""
                    </div>

                    <a href="{("../" * len(path_parts))}../../files/{build_type}/index.html" class="trees-link">
                        <i class="fas fa-sitemap"></i> View Decision Tree Visualizations
                    </a>
                </div>

                <footer>
                    <p>Generated by BigGlobe Decision Tree Documentation Builder on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                </footer>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_json_directory_index(self, current_dir, subdirs, json_files, build_type):
        """
        Generate HTML content for a JSON directory index file.

        Args:
            current_dir: Current directory path (relative to decision_tree_dir)
            subdirs: List of subdirectories in this directory
            json_files: List of JSON files in this directory
            build_type: The type of build (root, main, or debug)

        Returns:
            String containing the HTML content for the index file
        """
        # Determine directory name for display
        if current_dir:
            dir_display = Path(current_dir).name
            title = f"JSON Files - {build_type.capitalize()} - {dir_display}"
            heading = f"JSON Files in {dir_display}"
        else:
            title = f"JSON Files - {build_type.capitalize()} - decision_tree"
            heading = f"BigGlobe Decision Tree JSON Files"

        # Generate paths for navigation
        current_path = Path(current_dir) if current_dir else Path()
        path_parts = current_path.parts

        # Create breadcrumb path
        breadcrumbs = []

        # Add main index and origin root
        breadcrumbs.append(f'<a href="{("../" * len(path_parts))}../../../index.html">Main Index</a>')
        breadcrumbs.append(f'<a href="{("../" * len(path_parts))}../../index.html">{build_type.capitalize()} Root</a>')

        # Add data/bigglobe/worldgen path
        if len(path_parts) == 0:  # We are at the decision_tree root
            breadcrumbs.append('<a href="../../../data/index.html">data</a>')
            breadcrumbs.append('<a href="../../index.html">bigglobe</a>')
            breadcrumbs.append('<a href="../index.html">worldgen</a>')

        # Add current path components
        current_parts = []
        for i, part in enumerate(path_parts):
            current_parts.append(part)
            back_steps = len(path_parts) - i - 1
            breadcrumbs.append(f'<a href="{("../" * back_steps)}index.html">{part}</a>')

        # Generate HTML
        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                :root {{
                    --primary-color: #4a6da7;
                    --secondary-color: #8aa9d6;
                    --accent-color: #ffb200;
                    --light-color: #f8f9fa;
                    --dark-color: #343a40;
                    --success-color: #28a745;
                    --info-color: #17a2b8;
                    --warning-color: #ffc107;
                    --danger-color: #dc3545;
                    --folder-color: #ff9800;
                    --folder-hover: #f57c00;
                    --file-color: #9c27b0;
                    --file-hover: #7b1fa2;
                    --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}

                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: var(--font-main);
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: var(--light-color);
                    padding: 0;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}

                .container {{
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    flex: 1;
                }}

                header {{
                    background-color: var(--warning-color);
                    color: white;
                    padding: 1.5rem;
                    margin-bottom: 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    background-image: linear-gradient(135deg, var(--warning-color) 0%, #e0a800 100%);
                }}

                header h1 {{
                    margin: 0;
                    font-size: 2rem;
                    color: white;
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                }}

                .breadcrumb {{
                    background-color: white;
                    padding: 1rem;
                    margin-bottom: 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}

                .breadcrumb a {{
                    background-color: var(--secondary-color);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    transition: background-color 0.3s;
                    text-decoration: none;
                    font-weight: 500;
                }}

                .breadcrumb a:hover {{
                    background-color: var(--primary-color);
                    text-decoration: none;
                }}

                .card {{
                    background-color: white;
                    padding: 1.5rem;
                    margin: 0;
                }}

                .file-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 1rem;
                    margin-top: 1rem;
                }}

                .file-item {{
                    background-color: var(--file-color);
                    color: white;
                    padding: 1rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                }}

                .file-item:hover {{
                    background-color: var(--file-hover);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}

                .folder-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 1rem;
                    margin: 1rem 0;
                }}

                .folder-item {{
                    background-color: var(--folder-color);
                    color: white;
                    padding: 1rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                }}

                .folder-item:hover {{
                    background-color: var(--folder-hover);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}

                .file-icon, .folder-icon {{
                    margin-right: 0.8rem;
                    font-size: 1.2rem;
                }}

                footer {{
                    margin-top: 0;
                    padding: 1rem;
                    text-align: center;
                    color: var(--dark-color);
                    font-size: 0.9rem;
                    background-color: white;
                    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
                }}

                .trees-link {{
                    margin-top: 1rem;
                    display: block;
                    padding: 1rem;
                    background-color: var(--primary-color);
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}

                .trees-link:hover {{
                    background-color: #395885;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}

                .empty-message {{
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 6px;
                    font-style: italic;
                    color: #6c757d;
                    text-align: center;
                    margin: 1rem 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>{heading}</h1>
                </header>

                <div class="breadcrumb">
                    {' '.join(breadcrumbs)}
                    <a href="{("../" * (len(path_parts) + 3))}files/{build_type}/{'index.html' if not current_dir else current_dir + '/index.html'}">View Decision Trees</a>
                </div>

                <div class="card">
        """

        # Add directories section if any
        if subdirs:
            html += """
                    <h2><i class="fas fa-folder-open"></i> Directories</h2>
                    <div class="folder-grid">
        """

            for subdir in sorted(subdirs):
                html += f"""
                        <a href="{subdir}/index.html" class="folder-item">
                            <i class="fas fa-folder folder-icon"></i>
                            {subdir}
                        </a>
        """

            html += """
                    </div>
        """

        # Add files section if any
        if json_files:
            html += """
                    <h2><i class="fas fa-file-code"></i> JSON Files</h2>
                    <div class="file-grid">
        """

            for json_file in sorted(json_files):
                html += f"""
                        <a href="{json_file}.html" class="file-item">
                            <i class="fas fa-file-code file-icon"></i>
                            {json_file}
                        </a>
        """

            html += """
                    </div>
        """

        # If no files or directories
        if not subdirs and not json_files:
            html += """
                    <div class="empty-message">
                        <i class="fas fa-info-circle"></i> No JSON files or directories found in this location.
                    </div>
        """

        # Add link to decision tree visualization
        tree_path = current_dir if current_dir else ""
        html += f"""
                    <a href="{("../" * (len(path_parts) + 3))}files/{build_type}/{'index.html' if not current_dir else current_dir + '/index.html'}" class="trees-link">
                        <i class="fas fa-sitemap"></i> View Decision Tree Visualizations
                    </a>
                </div>

                <footer>
                    <p>Generated by BigGlobe Decision Tree Documentation Builder on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                </footer>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_json_viewer(self, json_filename, json_content, build_type, dir_path):
        """
        Generate HTML content for viewing a JSON file.

        Args:
            json_filename: Name of the JSON file
            json_content: Formatted JSON content
            build_type: The type of build (root, main, or debug)
            dir_path: Directory path relative to the decision tree directory

        Returns:
            String containing the HTML content for the JSON viewer
        """
        escape_html = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"',
                                                                                                          "&quot;").replace(
            "'", "&#39;")
        escaped_json = escape_html(json_content)

        # Calculate path for decision tree visualization
        tree_id = (dir_path + "/" if dir_path else "") + json_filename.replace(".json", "")
        visualization_path = f"../../../../files/{build_type}/{'index.html' if not dir_path else dir_path + '/index.html'}"

        # Calculate number of back steps for breadcrumbs
        path_parts = dir_path.split('/') if dir_path else []
        back_steps = len(path_parts)

        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>JSON Viewer - {json_filename}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
            <script>hljs.highlightAll();</script>
            <style>
                :root {{
                    --primary-color: #4a6da7;
                    --secondary-color: #8aa9d6;
                    --accent-color: #ffb200;
                    --light-color: #f8f9fa;
                    --dark-color: #343a40;
                    --success-color: #28a745;
                    --info-color: #17a2b8;
                    --warning-color: #ffc107;
                    --danger-color: #dc3545;
                    --folder-color: #ff9800;
                    --folder-hover: #f57c00;
                    --file-color: #9c27b0;
                    --file-hover: #7b1fa2;
                    --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    --code-background: #f8f9fa;
                }}

                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: var(--font-main);
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: var(--light-color);
                    padding: 0;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}

                .container {{
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                }}

                header {{
                    background-color: var(--file-color);
                    color: white;
                    padding: 1.5rem;
                    margin: 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    background-image: linear-gradient(135deg, var(--file-color) 0%, var(--file-hover) 100%);
                }}

                header h1 {{
                    margin: 0;
                    font-size: 2rem;
                    color: white;
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                }}

                header h1 .file-icon {{
                    margin-right: 0.8rem;
                }}

                .breadcrumb {{
                    background-color: white;
                    padding: 1rem;
                    margin: 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}

                .breadcrumb a {{
                    background-color: var(--secondary-color);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    transition: background-color 0.3s;
                    text-decoration: none;
                    font-weight: 500;
                }}

                .breadcrumb a:hover {{
                    background-color: var(--primary-color);
                    text-decoration: none;
                }}

                .code-container {{
                    background-color: var(--code-background);
                    padding: 0;
                    margin: 0;
                    overflow: auto;
                    flex: 1;
                    position: relative;
                }}

                pre {{
                    margin: 0;
                    padding: 1rem;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 14px;
                    overflow-x: auto;
                    tab-size: 2;
                }}

                code {{
                    white-space: pre;
                    display: block;
                }}

                .actions {{
                    position: sticky;
                    top: 0;
                    right: 0;
                    display: flex;
                    justify-content: flex-end;
                    padding: 0.5rem;
                    background-color: rgba(255, 255, 255, 0.9);
                    border-bottom: 1px solid #ddd;
                    z-index: 100;
                }}

                .action-button {{
                    background-color: var(--primary-color);
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    margin-left: 0.5rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    transition: background-color 0.3s;
                }}

                .action-button:hover {{
                    background-color: #395885;
                }}

                .action-icon {{
                    margin-right: 0.5rem;
                }}

                .line-numbers {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    background-color: #f1f1f1;
                    padding: 1rem 0.5rem;
                    color: #888;
                    text-align: right;
                    user-select: none;
                    border-right: 1px solid #ddd;
                }}

                footer {{
                    padding: 1rem;
                    text-align: center;
                    color: var(--dark-color);
                    font-size: 0.9rem;
                    background-color: white;
                    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
                }}

                .trees-link {{
                    display: inline-block;
                    background-color: var(--primary-color);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    font-weight: 500;
                    text-decoration: none;
                    transition: background-color 0.3s;
                    margin-left: 0.5rem;
                }}

                .trees-link:hover {{
                    background-color: #395885;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1><i class="fas fa-file-code file-icon"></i> {json_filename}</h1>
                </header>

                <div class="breadcrumb">
                    <a href="{("../" * (back_steps + 3))}index.html">Main Index</a>
                    <a href="{("../" * (back_steps + 1))}index.html">{build_type.capitalize()} Root</a>
                    <a href="{("../") * back_steps if back_steps > 0 else ""}index.html">
                        {dir_path if dir_path else "decision_tree root"}
                    </a>
                    <a href="{visualization_path}" class="trees-link">
                        <i class="fas fa-sitemap"></i> View Tree Visualization
                    </a>
                </div>

                <div class="code-container">
                    <div class="actions">
                        <button onclick="copyToClipboard()" class="action-button">
                            <i class="fas fa-copy action-icon"></i> Copy
                        </button>
                        <a href="{visualization_path}" class="action-button">
                            <i class="fas fa-sitemap action-icon"></i> View Tree
                        </a>
                    </div>
                    <pre><code class="language-json">{escaped_json}</code></pre>
                </div>

                <footer>
                    <p>Generated by BigGlobe Decision Tree Documentation Builder</p>
                </footer>
            </div>

            <script>
                function copyToClipboard() {{
                    const codeElement = document.querySelector('code');
                    const textArea = document.createElement('textarea');
                    textArea.value = codeElement.textContent;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);

                    // Show feedback
                    const button = document.querySelector('.action-button');
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check action-icon"></i> Copied!';
                    setTimeout(() => {{
                        button.innerHTML = originalText;
                    }}, 2000);
                }}
            </script>
        </body>
        </html>
        """
        return html

    def _get_version_info(self):
        """Get version information from Imports/Versions.json"""
        version_file = Path("Imports/Versions.json")
        version_info = {"minecraft": "Unknown", "mod": "Unknown"}

        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    versions = json.load(f)
                if "BigGlobe" in versions:
                    version_info = versions["BigGlobe"]
            except Exception as e:
                self.logger.error(f"Error reading version file: {e}")

        return version_info

    def _create_main_index(self, build_statuses):
        """
        Create the main index.html file.

        Args:
            build_statuses: Dictionary of build statuses
        """
        # Get version information
        version_info = self._get_version_info()

        # Create HTML content
        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BigGlobe Decision Trees Documentation</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                :root {{
                    --primary-color: #4a6da7;
                    --secondary-color: #8aa9d6;
                    --accent-color: #ffb200;
                    --light-color: #f8f9fa;
                    --dark-color: #343a40;
                    --success-color: #28a745;
                    --info-color: #17a2b8;
                    --warning-color: #ffc107;
                    --danger-color: #dc3545;
                    --disabled-color: #6c757d;
                    --json-color: #9c27b0;
                    --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}

                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: var(--font-main);
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: var(--light-color);
                    padding: 0;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}

                .container {{
                    width: 100%;
                    padding: 20px;
                    flex: 1;
                }}

                header {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    background-image: linear-gradient(135deg, var(--primary-color) 0%, #2a4073 100%);
                }}

                header h1 {{
                    margin: 0;
                    font-size: 2.5rem;
                    color: white;
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                }}

                .version-info {{
                    margin-top: 1rem;
                    display: inline-block;
                    background-color: rgba(255, 255, 255, 0.2);
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    backdrop-filter: blur(4px);
                }}

                h1, h2, h3 {{
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                }}

                .build-options {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }}

                .build-card {{
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s, box-shadow 0.3s;
                    position: relative;
                }}

                .build-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                }}

                .build-header {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 1.2rem;
                    font-size: 1.3rem;
                    font-weight: bold;
                    text-align: center;
                    background-image: linear-gradient(135deg, var(--primary-color) 0%, #2a4073 100%);
                }}

                .build-content {{
                    padding: 1.5rem;
                }}

                .build-description {{
                    margin-bottom: 1.5rem;
                    color: #555;
                }}

                .build-button {{
                    display: inline-block;
                    width: 100%;
                    background-color: var(--success-color);
                    color: white;
                    text-align: center;
                    padding: 1rem;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 1rem;
                }}

                .build-button:hover {{
                    background-color: #218838;
                    text-decoration: none;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                }}

                .build-button.disabled {{
                    background-color: var(--disabled-color);
                    cursor: not-allowed;
                    pointer-events: none;
                    opacity: 0.7;
                }}

                .json-button {{
                    display: inline-block;
                    width: 100%;
                    background-color: var(--json-color);
                    color: white;
                    text-align: center;
                    padding: 1rem;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}

                .json-button:hover {{
                    background-color: #7b1fa2;
                    text-decoration: none;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                }}

                .json-button.disabled {{
                    background-color: var(--disabled-color);
                    cursor: not-allowed;
                    pointer-events: none;
                    opacity: 0.7;
                }}

                .documentation-info {{
                    background-color: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    position: relative;
                    overflow: hidden;
                }}

                .documentation-info::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 8px;
                    height: 100%;
                    background-color: var(--primary-color);
                }}

                footer {{
                    margin-top: 2rem;
                    padding: 1.5rem;
                    text-align: center;
                    color: var(--dark-color);
                    font-size: 0.9rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
                }}

                /* Badges */
                .badge {{
                    display: inline-block;
                    padding: 0.3rem 0.6rem;
                    border-radius: 30px;
                    margin-right: 0.5rem;
                    font-size: 0.8rem;
                    font-weight: bold;
                    color: white;
                }}

                .badge-mc {{
                    background-color: var(--info-color);
                }}

                .badge-mod {{
                                background-color: var(--success-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>BigGlobe Decision Trees Documentation</h1>
            <div class="version-info">
                <span class="badge badge-mc">Minecraft {version_info['minecraft']}</span>
                <span class="badge badge-mod">BigGlobe {version_info['mod']}</span>
            </div>
        </header>

        <main>
            <div class="documentation-info">
                <h2><i class="fas fa-info-circle"></i> Documentation Overview</h2>
                <p>This documentation provides a visual representation of BigGlobe's decision trees used in world generation. 
                   Decision trees define how various features and biomes are generated throughout the world.</p>
                <p>Select one of the build options below to explore the decision trees or view the original JSON files.</p>
            </div>

            <div class="build-options">
"""

        # Add cards for each build type
        build_types = {
            'root': {
                'title': 'Root Build',
                'description': 'Base BigGlobe mod decision trees from the original mod files.',
                'icon': 'fa-seedling'
            },
            'main': {
                'title': 'Main Build',
                'description': 'Decision trees from the main data pack, includes any customizations.',
                'icon': 'fa-cube'
            },
            'debug': {
                'title': 'Debug Build',
                'description': 'Decision trees from the debug data pack, includes development configurations.',
                'icon': 'fa-bug'
            }
        }

        for build_type, info in build_types.items():
            is_enabled = build_statuses.get(build_type, False)
            button_class = "build-button" if is_enabled else "build-button disabled"
            json_button_class = "json-button" if is_enabled else "json-button disabled"

            html += f"""
                <div class="build-card">
                    <div class="build-header">
                        <i class="fas {info['icon']} mr-2"></i> {info['title']}
                    </div>
                    <div class="build-content">
                        <div class="build-description">
                            <p>{info['description']}</p>
                        </div>
                        <a href="{'files/' + build_type + '/index.html' if is_enabled else '#'}" class="{button_class}">
                            {('<i class="fas fa-sitemap mr-2"></i> View Visualizations') if is_enabled else ('<i class="fas fa-ban mr-2"></i> Not Available')}
                        </a>
                        <a href="{'origin/' + build_type + '/index.html' if is_enabled else '#'}" class="{json_button_class}">
                            {('<i class="fas fa-file-code mr-2"></i> View JSON Files') if is_enabled else ('<i class="fas fa-ban mr-2"></i> Not Available')}
                        </a>
                    </div>
                </div>
"""

        # Close container and add footer
        html += f"""
            </div>
        </main>

        <footer>
            <p>Generated by BigGlobe Decision Tree Documentation Builder on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        </footer>
    </div>
</body>
</html>
"""

        # Write the index file
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html)

        self.logger.info(f"Created main index file at {index_file}")


def main():
    """Main execution function"""
    import argparse

    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="BigGlobe Decision Tree Documentation Builder")
    parser.add_argument("--root", action="store_true",
                        help="Build documentation from Imports/BigGlobe (default if no options specified)")
    parser.add_argument("--main", action="store_true", help="Build documentation from Output/DataPack")
    parser.add_argument("--debug", action="store_true", help="Build documentation from Output/DataPackDebug")
    parser.add_argument("--output", default="docs", help="Output directory for documentation (default: docs)")

    args = parser.parse_args()

    # If no build options specified, default to root
    if not (args.root or args.main or args.debug):
        args.root = True

    # Prepare base directories dictionary
    base_dirs = {
        'root': os.path.join("Imports", "BigGlobe") if args.root else None,
        'main': os.path.join("Output", "DataPack") if args.main else None,
        'debug': os.path.join("Output", "DataPackDebug") if args.debug else None
    }

    # Create documentation builder and build docs
    builder = DocumentationBuilder(base_dirs, args.output)
    builder.build_documentation()


if __name__ == "__main__":
    main()


