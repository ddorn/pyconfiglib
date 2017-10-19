def test_needs_to_be_done():
    from configlib import config
    conf = config.Config()
    conf.__save__()
    conf.__show__()
    conf.__print_list__()

