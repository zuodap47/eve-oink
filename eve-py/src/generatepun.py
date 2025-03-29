# -*- coding: utf-8 -*-
from gltl2gpar import get_max_prior
import subprocess as sp

'''This function generates an input file for PGSolver from the TTPG igraph structure'''
def ttpg2gm(TTPG, pl):
    max_idt = TTPG[pl].vcount()  # The highest occurring identifier
    max_prior = get_max_prior(TTPG[pl])  # Get the maximum priority value

    # Initialize the content for the output file
    tofile = 'parity ' + str(max_idt) + ';'

    for v in TTPG[pl].vs:
        # Determine ownership: 1 if 'itd' is True, otherwise 0
        own = 1 if v['itd'] else 0

        # Construct the list of successors
        for num, suc in enumerate(v.successors()):
            if num == 0:
                suc_list = str(suc.index)
            else:
                suc_list = suc_list + ',' + str(suc.index)

        # Append the node information to the output file content
        tofile = tofile + '\n' + str(v.index) + ' ' + str((2 * max_prior) - v['prior']) + ' ' + str(own) + ' ' + suc_list + ';'

    # Write the generated content to a file
    f = open('/home/mirror/eve-parity-master/eve-py/temp/ttpg_' + pl, 'w')
    f.write(tofile)
    f.close()


'''This function computes the Punishment Set (Pun_i) using Oink'''
def compute_pun(pl_name, PUN, TTPG):
    '''Convert TTPG to Oink format'''
    ttpg2gm(TTPG, pl_name)

    '''Invoke Oink to compute Pun_i'''
    oink_cmd = [
        '/usr/local/bin/oink',  # Ensure the correct path to the Oink executable
        '--solver', 'fpi',      # Use the "fpi" solver (other solvers can be used)
        '--timeout', '300',     # Set a timeout of 300 seconds
        '--print',              # Print the output to the terminal
        '../temp/ttpg_%s' % pl_name  # Input file path for TTPG
    ]

    try:
        # Execute the Oink command
        process = sp.Popen(oink_cmd, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf8')
        out, err = process.communicate()

        # Print errors if any
        if err:
            print("Oink error:", err)

        ttpg_results = {}
        out_lines = out.splitlines()

        # Parse Oink output
        for line in out_lines:
            words = line.split(" ")
            if words[0] == "Player":
                pl = words[1]
            for c in words:
                try:
                    if c[0] == "{":
                        ttpg_results[int(pl)] = line
                except IndexError:
                    pass

        # Process and store results
        try:
            PUN[pl_name] = list(map(int, ttpg_results[0].strip()[1:-1].replace(' ', '').split(',')))
        except (ValueError, KeyError):
            PUN[pl_name] = []

    except FileNotFoundError:
        print(f"Error: The Oink executable file was not found. Please check the path {oink_cmd[0]}")
        PUN[pl_name] = []

    return PUN
