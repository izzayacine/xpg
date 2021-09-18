# -*- coding:utf-8 -*-
#
#   Xplanation Graph, explaining graph-based classifier
#   Author: Xuanxiang Huang, Yacine Izza
#
# ==============================================================================

from pysat.formula import IDPool
from pysat.solvers import Solver

from queue import Queue
import networkx as nx

from xpg import Abductive
from xpg import Contrastive

import resource
import numpy as np


#
# ==============================================================================
def check_one_axp(xpg, axp):
    """
        Check if given axp is an AXp.

        :param xpg: xpg model.
        :param axp: potential abductive explanation.
        :return: true if given axp is an AXp
                    else false.
    """
    univ = [True] * xpg.nv
    for i in axp:
        univ[i] = not univ[i]

    if xpg.path_to_zero(univ):
        return False

    for i in range(len(univ)):
        if not univ[i]:
            univ[i] = not univ[i]
            if xpg.path_to_zero(univ):
                univ[i] = not univ[i]
            else:
                return False
    return True


class XpGraph(object):
    """
        eXplanation Graph model, an abstract model of graph-based classifier.
    """

    def __init__(self, graph, root, nvars, features=None, targets=None, y_pred=None, verb=0):
        self.graph = graph
        self.root = root
        self.nv = nvars
        self.features = features
        self.classes = targets
        self.y_pred = y_pred
        self.verbose = verb

   

    @classmethod
    def from_file(cls, filename):
        """
            Load XpG model from .xpg format file.

            :param filename: file in .xpg format.
            :return: XpG model.
        """

        with open(filename, 'r') as fp:
            lines = fp.readlines()
        # filtering out comment lines (those that start with '#')
        lines = list(filter(lambda l: (not (l.startswith('#') or l.strip() == '')), lines))

        features = []
        index = 0
        assert (lines[index].strip().startswith('NN:'))
        n_nds = (lines[index].strip().split())[1]
        index += 1

        assert (lines[index].strip().startswith('Root:'))
        root = (lines[index].strip().split())[1]
        index += 1

        assert (lines[index].strip().startswith('T:'))
        n_t = len(lines[index][2:].strip().split())
        index += 1

        assert (lines[index].strip().startswith('TDef:'))
        index += 1

        t_nds = []
        while not lines[index].strip().startswith('NT:'):
            nd, t = lines[index].strip().split()
            t_nds.append(tuple((int(nd), {'target': int(t)})))
            index += 1

        assert (lines[index].strip().startswith('NT:'))
        n_nt = len(lines[index][3:].strip().split())
        index += 1

        assert (lines[index].strip().startswith('NTDef:'))
        index += 1

        edges = []
        while not lines[index].strip().startswith('NV:'):
            nd, chd, label = lines[index].strip().split()
            edges.append(tuple((int(nd), int(chd), {'label': int(label)})))
            index += 1

        assert (lines[index].strip().startswith('NV:'))
        nvars = (lines[index].strip().split())[1]
        index += 1

        assert (lines[index].startswith('VarDef:'))
        index += 1

        nt_nds = []
        while index < len(lines):
            string = lines[index].strip().split()
            nd = string[0]
            feature = ' '.join(string[1:])
            if feature not in features:
                nt_nds.append(tuple((int(nd), {'var': len(features)})))
                features.append(feature)
            else:
                nt_nds.append(tuple((int(nd), {'var': features.index(feature)})))
            index += 1

        G = nx.DiGraph()
        G.add_nodes_from(t_nds)
        G.add_nodes_from(nt_nds)
        G.add_edges_from(edges)
        return cls(G, int(root), int(nvars), features=features)

    def path_to_zero(self, univ):
        """
            Check whether there is a consistent path to desired terminal 0.

            :param univ: a list of features declared as universal.
            :return: true if there is a path to 0 else false.
        """

        G = self.graph
        # BFS (Breadth-first search)
        q = Queue()
        q.put(self.root)
        while not q.empty():
            nd = q.get()
            if not G.out_degree(nd):
                if not G.nodes[nd]['target']:
                    return True
            else:
                if univ[G.nodes[nd]['var']]:
                    for s in G.successors(nd):
                        q.put(s)
                else:
                    for s in G.successors(nd):
                        if G.edges[nd, s]['label']:
                            q.put(s)
                            break
                    else:
                        assert False, 'dead end branch'
        return False

    def decision_path(self):
        """
            Get decision path which consistent with given instance of XpG.

            :return: list of nodes in decision path.
        """

        p = []
        r = self.root
        G = self.graph
        while G.out_degree(r):
            for s in G.successors(r):
                if G.edges[r, s]['label']:
                    p.append(r)
                    r = s
                    break
            else:
                assert False, 'dead end branch'
        assert len(p)
        return p



#
# ==============================================================================
class MarcoXpG(object):
    """
       MARCO, computing one/all explanation for graph-based classifiers.
    """

    def __init__(self, xpg: XpGraph, verb=0, Horn=True):
        self.xpg = xpg
        self.axp = Abductive(xpg.features, Horn, verb)
        self.cxp = Contrastive(xpg.features, verb)
        self.verbose = verb
              

    def find_axp(self, fixed=None):
        """
            Find one abductive explanation (Axp).

            :param fixed: a list of features declared as fixed.
            :param horn: using Horn encoding (True) or graph traverse (False).
            :return: one abductive explanation,
                        each element in the return Axp is a feature index.
        """
        if fixed:
            fix = fixed.copy()
        else:
            fix = None
        return self.axp.explain(self.xpg, fix)


    def find_cxp(self, universal=None):
        """
            Find one contrastive explanation (Cxp).

            :param universal: a list of features declared as universal.
            :return: one contrastive explanation,
                        each element in the return Cxp is a feature index.
        """
        if universal:
            univ = universal.copy()
        else:
            univ = None
        return self.cxp.explain(self.xpg, univ)

    def enum(self):
        """
            Enumerate all (abductive and contrastive) explanations, using MARCO algorithm.

            :return: a list of all Axps, a list of all Cxps.
        """

        #########################################
        vpool = IDPool()

        def new_var(name):
            """
                Inner function,
                Find or new a PySAT variable.
                See PySat.

                :param name: name of variable
                :return: index of variable
            """
            return vpool.id(f'{name}')
        #########################################
        if self.verbose:
            self.axp.verbose -= 1
            self.cxp.verbose -= 1

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime

        slv = Solver(name="glucose3")

        # declare variables in pysat variable pool,
        # i of u_i denote i-th variable
        for i in range(self.xpg.nv):
            new_var(f'u_{i}')
        # initially all features are fixed
        universal = [False for _ in range(self.xpg.nv)]

        all_axp = []
        all_cxp = []

        while slv.solve():
            model = slv.get_model()
            for lit in model:
                # extract i from u_i
                name = vpool.obj(abs(lit)).split(sep='_')
                # lit > 0 means u_i universal, lit < 0 means u_i fixed
                universal[int(name[1])] = False if lit < 0 else True
            if self.xpg.path_to_zero(universal):
                cxp = self.find_cxp(universal)
                slv.add_clause([-new_var(f'u_{i}') for i in cxp])
                all_cxp.append(cxp)
            else:
                # get fixed features by flipping value of each element in universal
                fixed = [not i for i in universal]
                axp = self.find_axp(fixed)
                slv.add_clause([new_var(f'u_{i}') for i in axp])
                all_axp.append(axp)

        # delete the SAT solver
        slv.delete()

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime - time

        if self.verbose:
            print()
            print('Num of AXp:', len(all_axp))
            print('Num of CXp:', len(all_cxp))
            print('Total Explanation:', len(all_cxp) + len(all_axp))
            print("Runtime: {0:.3f}".format(time))

        return all_axp, all_cxp



