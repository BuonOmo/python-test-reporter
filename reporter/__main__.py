#!/usr/bin/env python

import sys

from .components.runner import Runner


def run():
    runner = Runner()

    sys.exit(runner.run())
