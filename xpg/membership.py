# -*- coding:utf-8 -*-
#
#   Feature Membership
#   Author: Xuanxiang Huang
#
# ==============================================================================
import itertools
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
from xpg import XpGraph, check_one_axp


#
# ==============================================================================
class FeatureMembership(object):
    """
        Feature membership query. Compute an AXp containing given feature
        or enumerating all AXps containing given feature.
    """

    def __init__(self, xpg: XpGraph, verb=0):
        self.xpg = xpg
        self.verbose = verb

    def brute_force(self, feat_id, guess_one=False, verb=0):
        """
            Answer feature membership query by brute force.
            This is the BASELINE.
            :param feat_id: given feature index
            :param guess_one: return one AXp or all AXps containing thsi feature.
            :param verb: verbose level
            return AXps if exists else None
        """
        feat_list = [i for i in range(self.xpg.nv)]
        feat_list.remove(feat_id)
        axps = []

        if verb:
            print('Feature Membership of XpG by brute force ...')

        for n in range(self.xpg.nv):
            possible_set = list(itertools.combinations(feat_list, n))
            for item in possible_set:
                assert feat_id not in item
                tmp = list(item)
                tmp.append(feat_id)
                tmp.sort()
                axp = tmp.copy()
                if check_one_axp(self.xpg, axp):
                    if self.verbose:
                        feats_output = [self.xpg.features[i] for i in axp]
                        if self.verbose == 1:
                            print(f"AXp: {axp}")
                        else:
                            print(f"AXp: {axp} ({feats_output})")
                    if axp not in axps:
                        axps.append(axp)
                    if guess_one:
                        break
        return axps

    def cnf_encoding(self, feat_id, guess_one=False, verb=0):
        """
            Encoding Feature membership into CNF formula
            :param feat_id: given feature id
            :param guess_one: return one AXp or
                                all AXps associated with this feature.
            :param verb: verbose level
            :return: AXps containing feat_id if exists.
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

        if verb:
            print('Feature Membership of XpG into CNF formulas ...')

        G = self.xpg.graph
        cnf = CNF()
        neg_leaf0 = []

        ##################### for 0-th replica #####################
        for chd in G.nodes:
            #############################################
            if chd is self.xpg.root:
                continue
            if not G.out_degree(chd) and G.nodes[chd]['target']:
                continue
            if not G.out_degree(chd) and not G.nodes[chd]['target']:
                neg_leaf0.append(new_var(f'n_0_{chd}'))
            #############################################
            var_c = new_var(f'n_0_{chd}')
            parent = []
            for nd in G.predecessors(chd):
                var_n = new_var(f'n_0_{nd}')
                u = new_var('u_{0}'.format(G.nodes[nd]['var']))
                r = new_var(f'r_0_{nd}_{chd}')
                parent.append(r)
                if G.edges[nd, chd]['label']:
                    # r_nd_chd <-> nd
                    cnf.append([-r, var_n])
                    cnf.append([-var_n, r])
                else:
                    # r_nd_chd <-> nd /\ u
                    cnf.append([-var_n, -u, r])
                    cnf.append([-r, var_n])
                    cnf.append([-r, u])
            # chd <-> r_nd1_chd \/ r_nd2_chd
            cnf.append([-var_c] + parent)
            for item in parent:
                cnf.append([-item, var_c])
        # n_root <-> 1
        cnf.append([new_var(f'n_0_{self.xpg.root}')])
        # eval(S) <-> /\ -neg_leaf1 /\ -neg_leaf2
        cnf.append(neg_leaf0 + [new_var('ev_0')])
        for item in neg_leaf0:
            cnf.append([-new_var('ev_0'), -item])
        # eval(S) <-> 1
        cnf.append([new_var('ev_0')])
        cnf.append([-new_var(f'u_{feat_id}')])

        ##################### for k-th replica #####################
        for k in range(1, self.xpg.nv+1):
            neg_leaf = []
            for chd in G.nodes:
                #############################################
                if chd is self.xpg.root:
                    continue
                if not G.out_degree(chd) and G.nodes[chd]['target']:
                    continue
                if not G.out_degree(chd) and not G.nodes[chd]['target']:
                    neg_leaf.append(new_var(f'n_{k}_{chd}'))
                #############################################
                var_c = new_var(f'n_{k}_{chd}')
                parent = []
                for nd in G.predecessors(chd):
                    var_n = new_var(f'n_{k}_{nd}')
                    u = new_var('u_{0}'.format(G.nodes[nd]['var']))
                    r = new_var(f'r_{k}_{nd}_{chd}')
                    parent.append(r)
                    if G.edges[nd, chd]['label']:
                        # r_nd_chd <-> nd
                        cnf.append([-r, var_n])
                        cnf.append([-var_n, r])
                    else:
                        if k-1 == G.nodes[nd]['var']:
                            cnf.append([-r, var_n])
                            cnf.append([-var_n, r])
                        else:
                            # r_nd_chd <-> nd /\ u
                            cnf.append([-var_n, -u, r])
                            cnf.append([-r, var_n])
                            cnf.append([-r, u])
                # chd <-> r_nd1_chd \/ r_nd2_chd
                cnf.append([-var_c] + parent)
                for item in parent:
                    cnf.append([-item, var_c])
            # n_root <-> 1
            cnf.append([new_var(f'n_{k}_{self.xpg.root}')])
            # eval(S) <-> /\ -neg_leaf1 /\ -neg_leaf2
            cnf.append(neg_leaf + [new_var(f'ev_{k}')])
            for item in neg_leaf:
                cnf.append([-new_var(f'ev_{k}'), -item])
            # -u_i <-> -eval(S)_k
            cnf.append([new_var(f'u_{k-1}'), -new_var(f'ev_{k}')])
            cnf.append([new_var(f'ev_{k}'), -new_var(f'u_{k-1}')])

        axps = []
        with Solver(name="glucose3", with_proof=True, bootstrap_with=cnf) as slv:
            while slv.solve():
                model = slv.get_model()
                assert model
                axp = []
                for lit in model:
                    # extract i from u_i
                    name = vpool.obj(abs(lit)).split(sep='_')
                    if name[0] == 'u':
                        # lit > 0 means u_i universal, lit < 0 means u_i fixed
                        if lit < 0:
                            axp.append(int(name[1]))
                axp.sort()
                if axp:
                    assert check_one_axp(self.xpg, axp), f"{axp} is NOT an AXp"
                if self.verbose:
                    feats_output = [self.xpg.features[i] for i in axp]
                    if self.verbose == 1:
                        print(f"AXp: {axp}")
                    else:
                        print(f"AXp: {axp} ({feats_output})")
                axps.append(axp)
                if not guess_one:
                    slv.add_clause([new_var(f'u_{i}') for i in axp])
                else:
                    break

            return axps
