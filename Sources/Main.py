# -*- coding: utf-8 -*-
import os.path
from typing import List

from Sources.Builder import Builder


def build_main(args: List[str]) -> int:
    output_path = os.path.join(os.path.dirname(__file__), "..", "OutPut", "DataPack")
    builder = Builder(output_path)
    builder.clean_output()
    builder.init_dirs()
    builder.init_mcmeta()

    builder.delete_structure("obelisk")
    builder.delete_structure("abandonedcity")

    return 0
