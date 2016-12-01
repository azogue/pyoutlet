# -*- coding: utf-8 -*-
"""
Minimal controler for 433Mhz RF Wireless Power Outlets
FROM:   http://timleland.com/wireless-power-outlets/
        https://github.com/timleland/rfoutlet

"""

if __name__ == '__main__':
    import os
    import sys

    # this_path =
    # os.chdir(this_path)
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

    from pyoutlet import turn_on_outlet, turn_off_outlet, OUTLETS

    help_msg = '''\033[0m\033[1m\033[34mPYOUTLET usage:\n\t* python pyoutlet ON XXXX\n\t* python pyoutlet OFF XXXX
    where XXXX is the outlet label or the outlet index (from 1 to 5).
    ** Outlet labels are: "{}"\033[0m
    Try again...\n'''.format('", "'.join([v['label'] for v in OUTLETS]))

    if len(sys.argv) == 3:
        if sys.argv[1].lower() == 'on':
            f = turn_on_outlet
        elif sys.argv[1].lower() == 'off':
            f = turn_off_outlet
        else:
            print(help_msg)
            sys.exit(2)
        ok = f(sys.argv[2], verbose=True)
        if not ok:
            print('OPERATION ERROR !?')
    else:
        print(help_msg)

