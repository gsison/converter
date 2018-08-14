# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:04:14 2018

@author: Gabriel Sison
"""

import csv
import networkx as nx


def stringformat(var):
    try:
        return "\"" + var + "\""
    except TypeError:
        return str(var)


def NxtoPgx(G, out, nlabels=["ntype"], nprops=None,
            elabels=["etype"], eprops=["weight"], pgxtype="elist"):
    """
    Outputs a PGX representation of a given networkX graph.
    """
    if pgxtype == "elist":
        NxtoPgxEdgelist(G, out, nlabels=nlabels, nprops=nprops,
                        elabels=elabels, eprops=eprops)
    else:
        raise ValueError("Unsupported Output Type")


def NxtoPgxEdgelist(G, out, nlabels=None, nprops=None,
                    elabels=None, eprops=["weight"]):
    with open(out+".ogv", "w") as outfile:
        for node in G:
            line = str(node) + ' * '
            propdict = G.node[node]
            runs = 0
            for label in nlabels:
                if len(nlabels) == 1:
                    vlabel = stringformat(propdict[label])
                    line += vlabel + " "
                elif len(nlabels) > 1:
                    if not runs:
                        line += "{"
                    vlabel = stringformat(propdict[label])
                    line += vlabel + " "
                    runs += 1
                    if runs == len(nlabels):
                        line = line[:-1] + "}"
                for key in sorted(propdict.keys()):
                    if key in nlabels:
                        continue
                    line += ' ' + stringformat(propdict[key])
                line += '\n'
            outfile.write(line)
        for edge in G:
            pass


with open("Jollibee_Stores.csv", 'r') as infile:
    reader = csv.reader(infile)
    runs = 0
    G = nx.MultiDiGraph()
    for row in reader:
        if not runs:
            runs += 1
            continue
        nodeattrs = {'code': row[0], 'kind': 'store',
                     'name': row[1], 'rbu': int(row[2]), 'own': row[3],
                     'ntype': row[4], 'lat': float(row[5]),
                     'long': float(row[6]), 'bfast': bool(row[7]),
                     'emd': bool(row[8]), 'dt': bool(row[9]),
                     'jeds': bool(row[10]), 'jpp': bool(row[11]),
                     'bos': bool(row[12])}
        G.add_node(row[0], **nodeattrs)

with open('JB_sno_dmatrix_bank.csv', 'r') as infile:
    reader = csv.reader(infile)
    runs = 0
    JBnames = []
    for row in reader:
        if not runs:
            for name in row[4:]:
                JBnames.append(name.strip())
            runs += 1
            continue
        name = 'Bank{}'.format(str(runs).zfill(5))
        runs += 1
        nodeattrs = {'code': name, 'name': row[0], 'lat': float(row[1]),
                     'long': float(row[2]), 'ntype': row[3]}
        G.add_node(name, **nodeattrs)
        for ind, val in enumerate(row[4:]):
            val = float(val)
            G.add_edge(name, JBnames[ind], distance=val, etype='Distance')
            G.add_edge(JBnames[ind], name, distance=val, etype='Distance')
