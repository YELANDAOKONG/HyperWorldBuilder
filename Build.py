# -*- coding: utf-8 -*-
import sys

import Sources.Main as Main

if __name__  == "__main__":
    code = Main.build_main(sys.argv)
    sys.exit(code)