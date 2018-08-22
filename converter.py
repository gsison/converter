# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:04:14 2018

@author: Gabriel Sison
"""

import csv
import networkx as nx
import simplejson as json


def stringformat(var):
    try:
        return "\"" + var + "\""
    except TypeError:
        if isinstance(var, bool):
            return str(var).lower()
        else:
            return str(var)


def pgxjsonfile(G, out, nlabels, elabel, eprops, fformat):
    with open("{}.json".format(out), 'w') as outfile:
        out = {}
        out["format"] = fformat
        out["edge_label"] = "true"
        props = []
        for u, v, d in G.edges(data=True):
            edatadict = d
            break
        for prop in eprops:
            propdict = {"name": prop}
            val = edatadict[prop]
            if isinstance(val, bool):
                propdict["type"] = "boolean"
            elif isinstance(val, int):
                propdict["type"] = "integer"
            elif isinstance(val, float):
                propdict["type"] = "double"
            elif isinstance(val, str):
                propdict["type"] = "string"
            props.append(propdict)
        out["edge_props"] = props
        out["vertex_labels"] = str(bool(nlabels)).lower()
        out["edge_label"] = str(bool(elabel)).lower()
        props = []
        for node in G:
            ndatadict = G.node[node]
            break
        print(ndatadict)
        for prop in sorted(ndatadict.keys()):
            if prop in nlabels:
                continue
            propdict = {"name": prop}
            val = ndatadict[prop]
            if isinstance(val, bool):
                propdict["type"] = "boolean"
            elif isinstance(val, int):
                propdict["type"] = "integer"
            elif isinstance(val, float):
                propdict["type"] = "double"
            elif isinstance(val, str):
                propdict["type"] = "string"
            props.append(propdict)
        out["vertex_props"] = props
        json.dump(out, outfile)
        return out


def NxtoPgx(G, out, nlabels=["ntype"],
            elabel="etype", eprops=["weight"], pgxtype="elist"):
    """
    Outputs a PGX representation of a given networkX graph.
    """
    if pgxtype == "elist":
        return NxtoPgxEdgelist(G, out, nlabels=nlabels,
                               elabel=elabel, eprops=eprops)
    else:
        raise ValueError("Unsupported Output Type")


def NxtoPgxEdgelist(G, out, nlabels=["ntype"],
                    elabel="etype", eprops=["weight"]):
    with open(out+".elst", "w") as outfile:
        for node in G:
            line = stringformat(node) + ' * '
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
        for u, v, d in G.edges(data=True):
            line = "{} {}".format(stringformat(u), stringformat(v))
            line += " \"{}\"".format(d[elabel])
            for key in sorted(d.keys()):
                if key is not elabel:
                    line += " {}".format(stringformat(d[key]))
            outfile.write(line)
    jsonout = pgxjsonfile(G, out, nlabels, elabel, eprops, "edge_list")
    return jsonout


if __name__ == "__main__":
    with open("Jollibee_Stores.csv", 'r') as infile:
        reader = csv.reader(infile)
        runs = 0
        G = nx.DiGraph()
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
    NOUT = NxtoPgx(G, "happybug", eprops=['etype'])
