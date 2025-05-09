# -*- coding: utf-8 -*-
import sys

import Sources.Main as Main

if __name__  == "__main__":
    args = sys.argv.copy()
    if "--debug" in args:
        args.remove("--debug")
        code = Main.build_debug(args)
    else:
        code = Main.build_main(args)
    sys.exit(code)