#!/bin/bash

set -e

if [ ! command -v python3 &> /dev/null ]; then
    echo "Python3 is not installed. Please install Python3 to generate man pages."
    exit 1
fi

python3 das-cli/src/setup.py --command-packages=click_man.commands man_pages --target $(CURDIR)/man
