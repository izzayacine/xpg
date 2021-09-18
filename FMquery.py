from xpg.membership import FeatureMembership
from xpg import XpGraph,MarcoXpG


file = "examples/xd6/xd6_0.xpg"
xpG = XpGraph.from_file(file)
feat_mem = FeatureMembership(xpG,verb=2)
marco = MarcoXpG(xpG, Horn=False, verb=3)
all_axp, all_cxp = marco.enum()

bf_axps = []
sat_axps = []

print("\n")
for f_id in range(xpG.nv):
    print(f"brute force: query on feature {f_id}:")
    axps = feat_mem.brute_force(f_id, guess_one=False, verb=1)
    for axp in axps:
        if axp not in bf_axps:
            bf_axps.append(axp)

    if bf_axps:
        for item in bf_axps:
            assert item in all_axp
    else:
        for item in all_axp:
            assert f_id not in item

print("\n")
for f_id in range(xpG.nv):
    print(f"SAT encoding: query on feature {f_id}:")
    axps = feat_mem.cnf_encoding(f_id, guess_one=False, verb=1)
    for axp in axps:
        if axp not in sat_axps:
            sat_axps.append(axp)

    if sat_axps:
        for item in sat_axps:
            assert item in all_axp
    else:
        for item in all_axp:
            assert f_id not in item

print(all_axp)
print(bf_axps)
print(sat_axps)
