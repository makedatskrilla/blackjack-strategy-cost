import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bjcalc as b
UPS = [2,3,4,5,6,7,8,9,10,11]
def code(t, s, up, pair=None):
    o = b.ev_two_card_options(t, s, up)
    if pair:
        o["P"] = b.ev_split(pair, up)
    a = b.best(o)
    if a == "D":
        return "Dh" if o["H"] >= o["S"] else "Ds"
    return a
def hard(t):
    return [code(t,0,u) for u in UPS]
def soft(x):  # A + x
    t,s = b.add(*b.add(0,0,11), x)
    return [code(t,s,u) for u in UPS]
def pair(r):
    t,s = b.add(*b.add(0,0,r), r)
    return [code(t,s,u,pair=r) for u in UPS]
if __name__ == "__main__":
    print("up   ", UPS)
    for t in range(5,18): print("H%-3d"%t, hard(t))
    for x in range(2,10): print("A,%d "%x, soft(x))
    for r in [2,3,4,5,6,7,8,9,10,11]: print("P%-3d"%r, pair(r))
