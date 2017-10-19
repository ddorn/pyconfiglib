import os
from configlib import config


def test_needs_to_be_done():
    conf = config.Config()
    conf.__save__()
    conf.__show__()
    conf.__print_list__()

    os.remove(conf.__config_path__)  # cleanup
