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
        """Clean the output files directory by removing all its contents"""
        # Clean files directory
        if self.files_dir.exists():
            self.logger.info(f"Cleaning files directory: {self.files_dir}")
            shutil.rmtree(self.files_dir)

        # Create output and files directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created output directories: {self.output_dir} and {self.files_dir}")

    def build_documentation(self):
        """Build the full documentation"""
        self.clean_output_directory()

        # Create a dictionary to track which builds were successful
        build_statuses = {name: False for name in self.visualizers}

        # Process each build type
        for name, visualizer in self.visualizers.items():
            # Create a temporary directory for the visualizations
            temp_dir = Path(f"temp_visualizations_{name}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()

            # Generate HTML visualizations
            self.logger.info(f"Generating HTML visualizations for {name}...")
            visualizer.batch_export_trees(output_dir=temp_dir, format="html")

            # Copy files to docs directory and build indexes
            target_dir = self.files_dir / name
            self.logger.info(f"Copying files to {target_dir}...")
            self._copy_and_index_files(temp_dir, target_dir, name)

            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            self.logger.info(f"Documentation for {name} successfully built")

            # Mark this build as successful
            build_statuses[name] = True

        # Generate main index page
        self.logger.info("Generating main index page...")
        self._create_main_index(build_statuses)

        self.logger.info(f"All documentation successfully built in {self.output_dir}")

    def _copy_and_index_files(self, source_dir, target_dir, build_type):
        """
        Copy files from the source directory to the target directory
        and create index files for each directory.

        Args:
            source_dir: Source directory containing the visualizations
            target_dir: Target directory to copy files to
            build_type: The type of build (root, main, or debug)
        """
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Create a dictionary to track directory structure
        dir_structure = {}

        # Collect all files
        for root, _, files in os.walk(source_dir):
            root_path = Path(root)

            # Skip empty directories
            if not files:
                continue

            # Get relative path from the source directory
            try:
                rel_path = root_path.relative_to(source_dir)
                current_target_dir = target_dir / rel_path
            except ValueError:
                # This is the source directory itself
                rel_path = Path()
                current_target_dir = target_dir

            # Create the target directory
            current_target_dir.mkdir(parents=True, exist_ok=True)

            # Add to directory structure
            if str(rel_path) not in dir_structure:
                dir_structure[str(rel_path)] = []

            # Copy files and add to directory structure
            html_files = []
            for file in files:
                if file.endswith(".html") and file != "index.html":
                    source_file = root_path / file
                    target_file = current_target_dir / file
                    shutil.copy2(source_file, target_file)
                    html_files.append(file)

            dir_structure[str(rel_path)] = html_files

        # Create index files for each directory
        self._create_directory_indexes(dir_structure, target_dir, build_type)

    def _create_directory_indexes(self, dir_structure, base_target_dir, build_type):
        """
        Create index.html files for each directory.

        Args:
            dir_structure: Dictionary mapping directory paths to lists of HTML files
            base_target_dir: Base target directory
            build_type: The type of build (root, main, or debug)
        """
        # Get all directories sorted by depth
        dirs = sorted(dir_structure.keys(), key=lambda x: len(Path(x).parts))

        # Process each directory
        for dir_path in dirs:
            dir_files = dir_structure[dir_path]
            target_dir = base_target_dir / dir_path

            # Create the index file content
            index_content = self._generate_directory_index(
                dir_path,
                dir_files,
                dirs,
                base_target_dir,
                build_type
            )

            # Write the index file
            index_file = target_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)

            self.logger.info(f"Created index file for {build_type}/{dir_path or 'root directory'}")

    def _generate_directory_index(self, current_dir, html_files, all_dirs, base_target_dir, build_type):
        """
        Generate HTML content for a directory index file.

        Args:
            current_dir: Current directory path
            html_files: List of HTML files in this directory
            all_dirs: List of all directories
            base_target_dir: Base target directory
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

        # Find subdirectories of the current directory
        current_path = Path(current_dir)
        subdirs = []
        for dir_path in all_dirs:
            path = Path(dir_path)
            if path != current_path and len(path.parts) == len(current_path.parts) + 1:
                if str(path).startswith(str(current_path) + os.sep) or (not current_path.parts and path.parts):
                    subdirs.append(path)

        # Create breadcrumb navigation
        breadcrumbs = []
        # Add link to main index
        relative_path = "../" * (len(current_path.parts) + 1)
        breadcrumbs.append(f'<a href="{relative_path}index.html">Main Index</a>')

        # Add link to build type index
        if current_path.parts:
            breadcrumbs.append(f'<a href="../index.html">Back to {build_type.capitalize()} Root</a>')

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }}

        header {{
            background-color: var(--primary-color);
            color: white;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
            border-radius: 8px;
            margin-bottom: 1.5rem;
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
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }}

        .directory-list, .file-list {{
            list-style-type: none;
            padding-left: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }}

        .directory-list li, .file-list li {{
            padding: 0;
            border-radius: 8px;
            overflow: hidden;
        }}

        .directory-list a, .file-list a {{
            display: block;
            padding: 1rem;
            color: var(--dark-color);
            text-decoration: none;
            font-weight: 500;
            transition: background-color 0.3s;
        }}

        .directory-list a {{
            background-color: var(--info-color);
            color: white;
        }}

        .file-list a {{
            background-color: var(--success-color);
            color: white;
        }}

        .directory-list a:hover, .file-list a:hover {{
            filter: brightness(1.1);
            text-decoration: none;
        }}

        .directory-icon, .file-icon {{
            margin-right: 10px;
            font-size: 1.2em;
        }}

        footer {{
            margin-top: 2rem;
            padding: 1rem;
            text-align: center;
            color: var(--dark-color);
            font-size: 0.9rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
        }}

        @media (max-width: 768px) {{
            .directory-list, .file-list {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{heading}</h1>
        </header>

        <main>
"""
        # Add breadcrumb navigation if available
        if breadcrumbs:
            html += f"""
            <div class="breadcrumb">
                {' '.join(breadcrumbs)}
            </div>
"""

        # Add subdirectories section if available
        if subdirs:
            html += f"""
            <div class="card">
                <h2>Subdirectories</h2>
                <ul class="directory-list">
"""
            for subdir in sorted(subdirs, key=lambda x: str(x)):
                subdir_name = subdir.name
                html += f'                    <li><a href="{subdir_name}/index.html"><span class="directory-icon">📁</span>{subdir_name}</a></li>\n'
            html += """
                </ul>
            </div>
"""

        # Add files section if available
        if html_files:
            html += f"""
            <div class="card">
                <h2>Decision Tree Files</h2>
                <ul class="file-list">
"""
            for file in sorted(html_files):
                if file != "index.html":
                    file_name = file.replace('.html', '')
                    html += f'                    <li><a href="{file}"><span class="file-icon">🌲</span>{file_name}</a></li>\n'
            html += """
                </ul>
            </div>
"""

        # Close container and add footer
        html += f"""
        </main>

        <footer>
            <p>Generated by BigGlobe Decision Tree Documentation Builder on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        </footer>
    </div>
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
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
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
        }}

        header h1 {{
            margin: 0;
            font-size: 2.5rem;
            color: white;
        }}

        .version-info {{
            margin-top: 1rem;
            display: inline-block;
            background-color: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 4px;
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
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .build-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }}

        .build-header {{
            background-color: var(--primary-color);
            color: white;
            padding: 1rem;
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
        }}

        .build-content {{
            padding: 1.5rem;
        }}

        .build-description {{
            margin-bottom: 1rem;
        }}

        .build-button {{
            display: inline-block;
            width: 100%;
            background-color: var(--success-color);
            color: white;
            text-align: center;
            padding: 0.8rem;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}

        .build-button:hover {{
            background-color: #218838;
            text-decoration: none;
        }}

        .build-button.disabled {{
            background-color: var(--disabled-color);
            cursor: not-allowed;
            pointer-events: none;
        }}

        .documentation-info {{
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>BigGlobe Decision Trees Documentation</h1>
            <div class="version-info">
                Minecraft: {version_info['minecraft']} | BigGlobe: {version_info['mod']}
            </div>
        </header>

        <main>
            <div class="documentation-info">
                <h2>Documentation Overview</h2>
                <p>This documentation provides a visual representation of BigGlobe's decision trees used in world generation. 
                   Decision trees define how various features and biomes are generated throughout the world.</p>
                <p>Select one of the build options below to explore the decision trees.</p>
            </div>

            <div class="build-options">
"""

        # Add cards for each build type
        build_types = {
            'root': {
                'title': 'Root Build',
                'description': 'Base BigGlobe mod decision trees'
            },
            'main': {
                'title': 'Main Build',
                'description': 'Decision trees from the main data pack'
            },
            'debug': {
                'title': 'Debug Build',
                'description': 'Decision trees from the debug data pack'
            }
        }

        for build_type, info in build_types.items():
            is_enabled = build_statuses.get(build_type, False)
            button_class = "build-button" if is_enabled else "build-button disabled"

            html += f"""
                <div class="build-card">
                    <div class="build-header">{info['title']}</div>
                    <div class="build-content">
                        <div class="build-description">
                            <p>{info['description']}</p>
                        </div>
                        <a href="{'files/' + build_type + '/index.html' if is_enabled else '#'}" class="{button_class}">
                            {'View Documentation' if is_enabled else 'Not Available'}
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
