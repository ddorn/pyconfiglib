import os
from configlib import config


def test_needs_to_be_done():
    conf = config.Config()
    conf.__save__()
    conf.__show__()
    conf.__print_list__()

    os.remove(conf.__config_path__)  # cleanup

def test_singleton():
    conf1 = config.Config()
    conf2 = config.Config()

    assert conf1 is conf2
