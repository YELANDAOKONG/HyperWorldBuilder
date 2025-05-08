# -*- coding: utf-8 -*-
import os
import time
import tempfile
import shutil
import logging
from typing import List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import the builder module
try:
    from Sources.Builder import Builder
except ImportError:
    logging.error("Failed to import Builder module. Make sure Sources/Builder.py exists")
    exit(1)

# Set of processed directories to avoid reprocessing
processed_dirs = set()


def build_datapack(datapack_path: str) -> bool:
    """
    Build a Minecraft datapack using the Builder

    Args:
        datapack_path: Path to the datapack source directory

    Returns:
        bool: True if build was successful, False otherwise
    """
    try:
        logging.info(f"Building datapack from: {datapack_path}")

        # Call the builder
        output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack")
        builder = Builder(output_path)
        builder.clean_output()
        builder.init_dirs()
        builder.init_mcmeta()

        # Add any additional building steps if needed

        logging.info(f"Build completed successfully")
        return True
    except Exception as e:
        logging.error(f"Build failed: {str(e)}")
        return False


def copy_to_target(source_dir: str, target_dir: str) -> bool:
    """
    Copy built datapack to target directory

    Args:
        source_dir: Source directory containing the built datapack
        target_dir: Target directory to copy to

    Returns:
        bool: True if copy was successful, False otherwise
    """
    try:
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Copy only files that don't exist or are newer
        for root, dirs, files in os.walk(source_dir):
            # Create relative path structure
            rel_path = os.path.relpath(root, source_dir)
            target_root = os.path.join(target_dir, rel_path)

            # Ensure target subdirectory exists
            os.makedirs(target_root, exist_ok=True)

            # Copy each file
            for file in files:
                src_file = os.path.join(root, file)
                tgt_file = os.path.join(target_root, file)

                # Copy if target doesn't exist or source is newer
                if not os.path.exists(tgt_file) or \
                        os.path.getmtime(src_file) > os.path.getmtime(tgt_file):
                    shutil.copy2(src_file, tgt_file)
                    logging.info(f"Copied {src_file} to {tgt_file}")

        return True
    except Exception as e:
        logging.error(f"Copy failed: {str(e)}")
        return False


def is_minecraft_datapack_folder(path: str) -> bool:
    """
    Check if a folder appears to be a Minecraft datapack folder

    Args:
        path: Path to check

    Returns:
        bool: True if it appears to be a Minecraft datapack folder
    """
    # This is a simplistic check - you may need to adjust based on
    # your specific criteria for identifying datapack folders
    if not os.path.isdir(path):
        return False

    # Check for typical datapack structure indicators
    # For example, look for pack.mcmeta or data directory
    # Adjust these checks based on your temp folder structure
    # This is just a placeholder example
    indicators = ['data', 'pack.mcmeta', 'minecraft']
    dir_contents = os.listdir(path)

    return any(indicator in dir_contents for indicator in indicators)


class MinecraftFolderHandler(FileSystemEventHandler):
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def on_created(self, event):
        if not event.is_directory:
            return

        path = event.src_path

        # Check if this is a folder we should process
        if path in processed_dirs:
            return

        if is_minecraft_datapack_folder(path):
            logging.info(f"Detected new Minecraft datapack folder: {path}")
            processed_dirs.add(path)

            # Build the datapack
            if build_datapack(path):
                # Determine source and target paths
                source_dir = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack")

                # Copy to target
                copy_to_target(source_dir, self.target_dir)


def main():
    # Directory to watch (system temp directory)
    watch_dir = tempfile.gettempdir()

    # Target directory to copy built datapacks to
    # Adjust this to your desired target directory
    target_dir = os.path.join(os.path.dirname(__file__), "..", "Minecraft", "datapacks")

    logging.info(f"Starting to monitor temporary directory: {watch_dir}")
    logging.info(f"Will copy built datapacks to: {target_dir}")

    # Create observer
    event_handler = MinecraftFolderHandler(target_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
