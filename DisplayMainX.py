# -*- coding: utf-8 -*-
import os
import sys
from os import path

import DisplayX

if __name__ == "__main__":
    base_dir = os.path.join("Output", "DataPack")
    output_dir = os.path.join("OutPut", "DecisionTreeImages.Main")

    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Clean and create output directory
    visualizer = DisplayX.BigGlobeDecisionTreeVisualizer(base_dir, truncate_scripts=False)

    # Process all trees
    visualizer.batch_visualize(output_dir=output_dir, split=True, max_depth=8192)
