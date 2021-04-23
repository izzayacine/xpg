#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## XpG
##
##  Created on: March 18, 2021
##      Author: Xuanxiang Huang, Yacine Izza, Alexey Ignatiev, Joao Marques-Silva
##      E-mail: xuanxiang.huang.cs@outlook.com, yacine.izza@gmail.com
##

#
#==============================================================================
from xpg import XpGraph, MarcoXpG

import getopt
import resource
import os
import sys



#
#==============================================================================


def usage():
    """
        Prints usage message.
    """
    print('Usage:', os.path.basename(sys.argv[0]), '[options] eXplanation Graph (XpG)')
    print('Options:')
    print('        -a, --all        List all explanation')
    print('        -h, --help')
    print('        -H, --Horn       Use Horn encoding for computing AXp')
    print('        -s, --save-exp   Save explanation')
    print('        -v, --verb       Be verbose (show comments)')
    print('        -x, --xtype      Explanation type')
    print('                         Available values: AXp, CXp (default: AXp)')

    

#
#==============================================================================
def parse_options():
    """
        Parses command-line options:
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'ahHvx:',
                                   ['all',
                                    'help',
                                    'Horn',
                                    'verb',
                                    'xtype='])
    except getopt.GetoptError as err:
        sys.stderr.write(str(err).capitalize())
        usage()
        sys.exit(1)

    # init 
    all_xp = False
    verb = 1
    xtype = 'AXp'
    horn = False

    for opt, arg in opts:
        if  opt in ('-a', '--all'):
            all_xp = True
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ('-H', '--Horn'):
            horn = True
        elif opt in ('-v', '--verb'):
            verb += 1
        elif opt in ('-x', '--xtype'):
            xtype = str(arg)           
        else:
            assert False, 'Unhandled option: {0} {1}'.format(opt, arg)


    return all_xp, horn, verb, xtype, args

#==============================================================================
if __name__=='__main__':

    all_xp, horn, verb, xtype, files = parse_options()

    if not files:
        exit()

    axp = None
    cxp = None
    all_axp = None
    all_cxp = None

    print("load xpgraph from ",files[0])
    xpG = XpGraph.from_file(files[0])
    marco = MarcoXpG(xpG, verb, horn)

    if all_xp:
        print("list all XPs ...")
        all_axp, all_cxp = marco.enum()
    elif xtype == 'AXp':
        print("find an AXp ...")
        axp = marco.find_axp()
    elif xtype == 'CXp':
        print("find a CXp ...")
        cxp = marco.find_cxp()
    else:
        assert False, 'Unkown option!'



    

