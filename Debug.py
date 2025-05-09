# -*- coding: utf-8 -*-
import os
import sys
import time
import tempfile
import shutil
import logging
import colorlog
import re
from typing import List, Set
from datetime import datetime

# Import the builder module
try:
    # from Sources.Builder import Builder
    import Sources.Main as Main
except ImportError:
    print("Failed to import Builder module. Make sure Sources/Builder.py exists")
    exit(1)


def setup_logger():
    """Setup and return a colored logger"""
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

    logger = logging.getLogger('datapack_monitor')
    logger.setLevel(logging.INFO)
    # Remove any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    logger.addHandler(handler)
    # Prevent log propagation to root logger
    logger.propagate = False

    return logger


# Set of processed directories to avoid reprocessing
processed_dirs = set()
logger = setup_logger()


def build_datapack(datapack_path: str) -> bool:
    """
    Build a Minecraft datapack

    Args:
        datapack_path: Path to the datapack source directory

    Returns:
        bool: True if build was successful, False otherwise
    """
    try:
        logger.info(f"Building datapack from: {datapack_path}")

        # Set up output path as specified
        output_path = os.path.join(os.path.dirname(__file__), "OutPut", "DataPack")

        # Create builder instance and build the datapack
        # builder = Builder(output_path)
        # builder.clean_output()
        # builder.init_dirs()
        # builder.init_mcmeta()
        code = Main.build_main(sys.argv)

        # Additional build steps can be added here

        logger.info("Build completed successfully")
        return True
    except Exception as e:
        logger.error(f"Build failed: {str(e)}")
        return False


def copy_to_target(source_dir: str, world_dir: str) -> bool:
    """
    Copy built datapack to target directory within the world folder

    Args:
        source_dir: Source directory containing the built datapack
        world_dir: The Minecraft world temporary directory

    Returns:
        bool: True if copy was successful, False otherwise
    """
    try:
        # Create a DataPack directory within the world folder
        target_dir = os.path.join(world_dir, "DataPack")

        # Check if target directory already exists - if it does, it means
        # we've already processed this world folder
        if os.path.exists(target_dir):
            logger.info(f"DataPack directory already exists in {world_dir}, skipping copy")
            return True

        # Create the target directory
        os.makedirs(target_dir, exist_ok=True)
        logger.info(f"Created DataPack directory in {world_dir}")

        # Copy the entire DataPack content
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

                # Copy file
                shutil.copy2(src_file, tgt_file)
                logger.info(f"Copied {src_file} to {tgt_file}")

        logger.info(f"Successfully copied datapack to {target_dir}")
        return True
    except Exception as e:
        logger.error(f"Copy failed: {str(e)}")
        return False


def is_minecraft_world_folder(path: str) -> bool:
    """
    Check if a folder is a Minecraft world temp folder

    Args:
        path: Path to check

    Returns:
        bool: True if it's a Minecraft world folder
    """
    try:
        if not os.path.isdir(path):
            return False

        # Check if folder name matches pattern mcworld-<numbers>
        folder_name = os.path.basename(path)
        if re.match(r"mcworld-\d+", folder_name):
            logger.debug(f"Found potential Minecraft world folder: {folder_name}")

            # Check if we've already processed this directory
            if path in processed_dirs:
                logger.debug(f"Already processed {path}, skipping")
                return False

            # Check if DataPack directory already exists
            datapack_dir = os.path.join(path, "DataPack")
            if os.path.exists(datapack_dir):
                logger.debug(f"DataPack directory already exists in {path}, marking as processed")
                processed_dirs.add(path)
                return False

            return True

        return False
    except Exception as e:
        logger.error(f"Error checking if folder is a Minecraft world: {str(e)}")
        return False


def scan_temp_directory(temp_dir: str) -> None:
    """
    Scan temporary directory for new Minecraft world folders

    Args:
        temp_dir: Temporary directory to scan
    """
    try:
        # List all directories in the temporary directory
        for item in os.listdir(temp_dir):
            try:
                full_path = os.path.join(temp_dir, item)

                # Check if it's a directory and a Minecraft world folder we haven't processed
                if os.path.isdir(full_path) and is_minecraft_world_folder(full_path):
                    logger.info(f"Detected new Minecraft world folder: {full_path}")

                    # Mark as processed before building to avoid race conditions
                    processed_dirs.add(full_path)

                    # Build the datapack
                    if build_datapack(full_path):
                        # Get source directory where datapack was built
                        source_dir = os.path.join(os.path.dirname(__file__), "OutPut", "DataPack")

                        # Copy to a DataPack folder within the world directory
                        copy_to_target(source_dir, full_path)
            except Exception as e:
                logger.error(f"Error processing item {item}: {str(e)}")
                continue  # Continue with next item
    except Exception as e:
        logger.error(f"Error scanning temporary directory: {str(e)}")


def main():
    try:
        # Directory to monitor (system temporary directory)
        watch_dir = tempfile.gettempdir()

        logger.info(f"Starting to monitor temporary directory: {watch_dir}")
        logger.info(f"Looking for Minecraft world folders matching pattern 'mcworld-*'")

        while True:
            try:
                # Scan temporary directory for new Minecraft worlds
                scan_temp_directory(watch_dir)

                # Wait before next scan
                time.sleep(2)  # Scan every 2 seconds
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                # Continue running despite errors
                time.sleep(5)  # Wait a bit longer after an error
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.critical(f"Critical error in main function: {str(e)}")
        # Even for critical errors, restart the main loop
        time.sleep(10)
        main()  # Restart the main function


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        # Sleep before exiting to ensure the error message is seen
        time.sleep(10)
