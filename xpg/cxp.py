# -*- coding:utf-8 -*-
#
#   Contrastive explanation
#   Author: Xuanxiang Huang, Yacine Izza
#
#==============================================================================

import resource


#
#==============================================================================
class Contrastive:
    """
        Contrastive eXplanation ( CXp )
    """

    def __init__(self, features, verb=1):
        self.features = features
        self.verbose = verb

    def explain(self, xpg, universal=None):
        """
            Compute one contrastive explanation (CXp).

            :param xpg: given an XpGraph
            :param universal: a list of features declared as universal.
            :return: one contrastive explanation,
                        each element in the return CXp is a feature index.
        """

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime

        if not universal:
            path = xpg.decision_path()
            univ = [True for _ in range(xpg.nv)]
            for n in path[:-1]:
                univ[xpg.graph.nodes[n]['var']] = False
        else:
            univ = universal

        for i in range(len(univ)):
            # simple deletion-based linear search
            if univ[i]:
                # try to fix i-th feature
                univ[i] = False
                if not xpg.path_to_zero(univ):
                    # i-th feature must be universal
                    univ[i] = True

        # cxp is a subset of universal features, and it is minimal
        expl = [i for i in range(len(univ)) if univ[i]]
        assert len(expl), 'CXp cannot be an empty-set!'

        time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + \
               resource.getrusage(resource.RUSAGE_SELF).ru_utime - time

        if self.verbose:
            feats_output = [self.features[i] for i in range(len(univ)) if univ[i]]
            if self.verbose == 1:
                print(f"CXp: {expl}")
            else:
                print(f"CXp: {expl} ({feats_output})")
            print("Runtime: {0:.3f}".format(time))

        return expl

