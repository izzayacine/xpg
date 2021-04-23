# -*- coding:utf-8 -*-
#
#   Contrastive explanation
#   Author: Xuanxiang Huang, Yacine Izza
#
# ==============================================================================
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

import resource


#
# ==============================================================================
class Abductive(object):
    """
        Abductive eXplanation ( AXp ) or PI-explanation.
    """

    def __init__(self, features, Horn=True, verb=1):
        self.features = features
        self.verbose = verb
        if Horn:
            self.enc = None

    def explain(self, xpg, fixed=None):
        """
            Compute one abductive explanation (AXp) by traversing.

            :param xpg: given an XpGraph
            :param fixed: a list of features declared as fixed.
            :return: one abductive explanation,
                        each element in the return AXp is a feature index.
        """

        ######################################################
        def traverse(xpg, fix):
            """
                Compute one abductive explanation (AXp) by traversing the XpGraph.
            """

            univ = [not f for f in fix]

            for i in range(xpg.nv):
                if fix[i]:
                    fix[i] = not fix[i]
                    univ[i] = not univ[i]
                    if xpg.path_to_zero(univ):
                        # i-th feature must be fixed
                        fix[i] = not fix[i]
                        univ[i] = not univ[i]

            # axp is a subset of fixed features, and it is minimal
            expl = [i for i in range(len(fix)) if fix[i]]
            assert len(expl), 'AXp cannot be an empty-set!'
            return expl
        ######################################################

        def slv_horn(xpg, fix):
            """
                Compute one abductive explanation (AXp) by solving the Horn encoding
                of the XpGraph.
            """

            # Horn encoding
            if self.enc is None:
                self.enc = horn_encoding(xpg, self.verbose)
            Horn, soft = self.enc

            # if fix[i] == true then i-th feature in soft is fixed, i.e. u_i = 0;
            # otherwise fix[i] == false then i-th feature in soft is universal, i.e. u_i = 1
            assump = [-soft[i] if fix[i] else soft[i] for i in range(xpg.nv)]

            with Solver(name="glucose3", bootstrap_with=Horn) as slv:
                # simple deletion-based linear search
                for i in range(xpg.nv):
                    if fix[i]:
                        # try to make i-th feature universal
                        assump[i] = -assump[i]
                        fix[i] = not fix[i]
                        if not slv.solve(assumptions=assump):
                            # i-th feature must be fixed
                            assump[i] = -assump[i]
                            fix[i] = not fix[i]

            # axp is a subset of fixed features, and it is minimal
            expl = [i for i in range(len(fix)) if fix[i]]
            assert len(expl), 'AXp cannot be an empty-set!'
            return expl
        ######################################################

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime

        if not fixed:
            fixed = [True for _ in range(xpg.nv)]

        if 'enc' not in dir(self):
            expl = traverse(xpg, fixed)
        else:
            expl = slv_horn(xpg, fixed)
        assert len(expl), 'AXp cannot be an empty-set!'

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime - time

        if self.verbose:
            feats_output = [self.features[i] for i in range(len(fixed)) if fixed[i]]
            if self.verbose == 1:
                print(f"AXp: {expl}")
            else:
                print(f"AXp: {expl} ({feats_output})")
            print("Runtime: {0:.3f}".format(time))

        return expl

#
# ==============================================================================
def horn_encoding(xpg, verb=0):
    """
        Hordn Encodings of a given XpGraph.
        :param xpg: given XpGraph
        :return: horn encoding of the XpGraph which is a set of hard-clauses (i.e. must be SAT),
                    and a set of soft-clauses denoting feature vars (i.e. can be SAT or UNSAT)
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

    def print_lits(lits):
        """
            Print lits and its name in PySAT.
            :param lits: given list of literals
            :return: none
        """
        print(lits, '=>', ["{0}{1}".format("-" if p < 0 else "", vpool.obj(abs(p))) for p in lits])
        #########################################

    if verb > 1:
        print('Encode XpGraph into Horn formulas ...')

    G = xpg.graph
    Horn = CNF()
    for nd in G.nodes:
        if not G.out_degree(nd):
            if G.nodes[nd]['target']:
                Horn.append([new_var('b_{0}'.format(nd))])
            else:
                Horn.append([-new_var('b_{0}'.format(nd))])
        else:
            var_n = new_var('b_{0}'.format(nd))
            u = new_var('u_{0}'.format(G.nodes[nd]['var']))
            for chd in G.successors(nd):
                var_c = new_var('b_{0}'.format(chd))
                if G.edges[nd, chd]['label']:
                    Horn.append([-var_n, var_c])
                else:
                    Horn.append([-var_n, -u, var_c])

    Horn.append([new_var('b_{0}'.format(xpg.root))])

    # soft is a list of pysat variables, i-th element denotes i-th feature index,
    # u_i > 0 means universal, u_i < 0 means fixed
    soft = [new_var(f'u_{i}') for i in range(xpg.nv)]

    return Horn, soft
