#!/usr/bin/env python3
from transutil.transutil import TranslateUtil

util = TranslateUtil("/Users/dustise/Downloads/k8s-repo.yaml",
                     "")

util.copy_version("kubernetes", "1.12", "1.14", "zh")

