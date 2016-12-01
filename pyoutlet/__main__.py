# -*- coding: utf-8 -*-
"""
Minimal controler for 433Mhz RF Wireless Power Outlets
FROM:   http://timleland.com/wireless-power-outlets/
        https://github.com/timleland/rfoutlet

"""
import argparse
from pyoutlet import turn_on_outlet, turn_off_outlet, OUTLETS, PATH_CODES_OUTLETS


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

    ok = False
    if args.info:
        print('\n** PYOUTLET JSON config in "{}"\n--> * {}\n'
              .format(PATH_CODES_OUTLETS,
                      '\n    * '.join(['{:20} -> ON:{}, OFF:{}'.format(d['label'], d['on'], d['off'])
                                       for d in OUTLETS])))
        ok = True
    elif args.operation.lower() == 'on':
        ok = turn_on_outlet(args.outlet, verbose=True)
    elif args.operation.lower() == 'off':
        ok = turn_off_outlet(args.outlet, verbose=True)

    if not ok:
        print('OPERATION ERROR !?\n')
        parser.print_help()


if __name__ == '__main__':
    main()
