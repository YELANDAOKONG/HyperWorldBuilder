# -*- coding: utf-8 -*-
import os
import sys
from os import path

import DisplayTextX

if __name__ == "__main__":
    base_dir = os.path.join("Output", "DataPack")
    output_json = os.path.join("OutPut", "DecisionTreeJson.Main")
    output_html = os.path.join("OutPut", "DecisionTreeHtml.Main")
    output_markdown = os.path.join("OutPut", "DecisionTreeMarkdown.Main")

    os.makedirs(output_json, exist_ok=True)
    os.makedirs(output_html, exist_ok=True)
    os.makedirs(output_markdown, exist_ok=True)

    # Create visualizer with option to show full scripts instead of truncating them
    visualizer = DisplayTextX.BigGlobeDecisionTreeVisualizer(base_dir, truncate_scripts=False)

    visualizer.batch_export_trees(output_dir=output_json, format="json")
    visualizer.batch_export_trees(output_dir=output_html, format="html")
    visualizer.batch_export_trees(output_dir=output_markdown, format="markdown")
