# -*- coding: utf-8 -*-
"""
Minimal controler for 433Mhz RF Wireless Power Outlets
FROM:   http://timleland.com/wireless-power-outlets/
        https://github.com/timleland/rfoutlet

"""
import argparse
from pyoutlet import Switcher


def _args_parser():
    """
    Argument parser

    """
    p = argparse.ArgumentParser(description="\033[1m\033[5m\033[32m{}\033[0m\n\n".format('PYOUTLET'),
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('operation', nargs='?', action='store', help='Turn ON/OFF operation')
    p.add_argument('outlet', nargs='?', action='store', help='Outlet label or #')
    p.add_argument('-i', '--info', action='store_true', help='︎ℹ️  Show outlets CODES and labels')
    return p


def main():
    """
    CLI main method

    """
    parser = _args_parser()
    args = parser.parse_args()

    switch = Switcher()
    ok = False
    if args.info:
        print(switch)
        print('JSON configuration for "homebridge-rcswitch-gpiomem":\n{}\n'.format(switch.homebridge_accessories))
        ok = True
    elif args.operation.lower() == 'on':
        ok = switch.turn_on_outlet(args.outlet, verbose=True)
    elif args.operation.lower() == 'off':
        ok = switch.turn_off_outlet(args.outlet, verbose=True)

    if not ok:
        print('OPERATION ERROR !?\n')
        parser.print_help()


if __name__ == '__main__':
    main()
