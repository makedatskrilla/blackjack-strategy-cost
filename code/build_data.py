"""Builds the CSV files in ../data from bjcalc.py. Run from the repo root: python code/build_data.py"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bjcalc as b
from chart import code

UPS = [2,3,4,5,6,7,8,9,10,11]
UPNAME = {u: ("A" if u == 11 else str(u)) for u in UPS}
CNAME = UPNAME
ACTION = {"H": "Hit", "S": "Stand", "Dh": "Double, otherwise hit",
          "Ds": "Double, otherwise stand", "P": "Split"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

def state(c1, c2):
    return b.add(*b.add(0, 0, c1), c2)

def r4(x):
    return "" if x is None else f"{x:.4f}"

# 1. Strategy table with the EV of every option
rows = []
def emit(htype, label, c1, c2, pair):
    t, s = state(c1, c2)
    for u in UPS:
        o = b.ev_two_card_options(t, s, u)
        sp = b.ev_split(pair, u) if pair else None
        rows.append([htype, label, UPNAME[u], code(t, s, u, pair=pair), ACTION[code(t, s, u, pair=pair)],
                     r4(o["S"]), r4(o["H"]), r4(o["D"]), r4(sp)])
reps = {5:(2,3),6:(2,4),7:(2,5),8:(2,6),9:(2,7),10:(2,8),11:(2,9),12:(2,10),13:(3,10),
        14:(4,10),15:(5,10),16:(6,10),17:(7,10),18:(8,10),19:(9,10),20:(10,10)}
# Hard 5 to 19 (two-card non-pair hands). In an infinite deck only the total matters.
for t in range(5, 20):
    emit("hard", f"Hard {t}", *reps[t], None)
for x in range(2, 10):
    emit("soft", f"Soft {11+x} (A,{x})", 11, x, None)
for r in UPS:
    emit("pair", f"Pair {CNAME[r]},{CNAME[r]}", r, r, r)
with open(os.path.join(OUT, "basic-strategy.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["hand_type", "player_hand", "dealer_upcard", "action_code", "action",
                "ev_stand", "ev_hit", "ev_double", "ev_split"])
    w.writerows(rows)

# 2. Mistake costs
def freq_hard_nonpair(total):
    p = 0.0
    for c1 in UPS:
        for c2 in UPS:
            if c1 == c2: continue
            t, s = state(c1, c2)
            if t == total and s == 0:
                p += b.P[c1] * b.P[c2]
    return p
def freq_soft(x):
    return 2 * b.P[11] * b.P[x]
def freq_pair(r):
    return b.P[r] ** 2
def p_situation(handp, u):
    return handp * b.P[u] * (1 - b.p_dealer_bj(u))

NAME = {"S": "Stand", "H": "Hit", "D": "Double", "P": "Split"}
mistakes = [
    # (label, kind, arg, upcard, wrong action)
    ("Standing on hard 16 against a 10", "hard", 16, 10, "S"),
    ("Standing on hard 15 against a 10", "hard", 15, 10, "S"),
    ("Standing on hard 12 against a 2", "hard", 12, 2, "S"),
    ("Hitting hard 12 against a 4", "hard", 12, 4, "H"),
    ("Hitting hard 13 against a 2", "hard", 13, 2, "H"),
    ("Standing on hard 14 against a 7", "hard", 14, 7, "S"),
    ("Standing on hard 16 against a 7", "hard", 16, 7, "S"),
    ("Hitting hard 16 against a 6", "hard", 16, 6, "H"),
    ("Hitting instead of doubling hard 11 against a 6", "hard", 11, 6, "H"),
    ("Hitting instead of doubling hard 10 against a 9", "hard", 10, 9, "H"),
    ("Hitting instead of doubling hard 9 against a 4", "hard", 9, 4, "H"),
    ("Doubling hard 10 against a 10", "hard", 10, 10, "D"),
    ("Doubling hard 11 against an ace", "hard", 11, 11, "D"),
    ("Standing on soft 17 (A,6) against a 7", "soft", 6, 7, "S"),
    ("Standing on soft 18 (A,7) against a 10", "soft", 7, 10, "S"),
    ("Standing on soft 18 (A,7) against a 9", "soft", 7, 9, "S"),
    ("Standing instead of doubling soft 18 (A,7) against a 6", "soft", 7, 6, "S"),
    ("Hitting instead of doubling soft 15 (A,4) against a 5", "soft", 4, 5, "H"),
    ("Not splitting aces against a 10 (hitting)", "pair", 11, 10, "H"),
    ("Not splitting 8s against a 10 (standing)", "pair", 8, 10, "S"),
    ("Not splitting 8s against a 10 (hitting)", "pair", 8, 10, "H"),
    ("Splitting 10s against a 6", "pair", 10, 6, "P"),
    ("Splitting 10s against a 10", "pair", 10, 10, "P"),
    ("Splitting 5s against a 6", "pair", 5, 6, "P"),
    ("Splitting 4s against a 10", "pair", 4, 10, "P"),
    ("Not splitting 9s against a 9 (standing)", "pair", 9, 9, "S"),
    ("Splitting 9s against a 7", "pair", 9, 7, "P"),
    ("Not splitting 2s against a 7 (hitting)", "pair", 2, 7, "H"),
]
mrows = []
for label, kind, arg, u, wrong in mistakes:
    if kind == "hard":
        c1, c2 = reps[arg]
        pair = None
        hp = freq_hard_nonpair(arg)
        hand = f"Hard {arg}"
    elif kind == "soft":
        c1, c2 = 11, arg
        pair = None
        hp = freq_soft(arg)
        hand = f"Soft {11+arg} (A,{arg})"
    else:
        c1, c2 = arg, arg
        pair = arg
        hp = freq_pair(arg)
        hand = f"Pair {CNAME[arg]},{CNAME[arg]}"
    t, s = state(c1, c2)
    o = b.ev_two_card_options(t, s, u)
    if pair: o["P"] = b.ev_split(pair, u)
    right = b.best(o)
    assert right != wrong, label
    cost = o[right] - o[wrong]
    ps = p_situation(hp, u)
    mrows.append([label, hand, UPNAME[u], NAME[right], NAME[wrong], r4(o[right]), r4(o[wrong]),
                  f"{cost*100:.2f}", f"{ps:.6f}", f"{ps*cost*100:.3f}", f"{ps*cost*1000:.2f}"])
# Insurance and even money
pi = b.P[11]
ins_cost = 0.5 * (1 - 3 * b.P[10])  # half-bet insurance, pays 2:1
mrows.append(["Taking insurance (half bet) against an ace", "Any non-blackjack hand", "A",
              "No insurance", "Insurance", "", "", f"{ins_cost*100:.2f}", f"{pi:.6f}", f"{pi*ins_cost*100:.3f}", f"{pi*ins_cost*1000:.2f}"])
em_cost = 1.5 * (1 - b.P[10]) - 1.0
mrows.append(["Taking even money with a blackjack against an ace", "Blackjack", "A",
              "Decline", "Even money", f"{1.5*(1-b.P[10]):.4f}", "1.0000", f"{em_cost*100:.2f}",
              f"{pi*2*b.P[11]*b.P[10]:.6f}", f"{pi*2*b.P[11]*b.P[10]*em_cost*100:.3f}", f"{pi*2*b.P[11]*b.P[10]*em_cost*1000:.2f}"])
with open(os.path.join(OUT, "mistake-costs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mistake", "player_hand", "dealer_upcard", "correct_play", "mistake_play",
                "ev_correct", "ev_mistake", "cost_pct_of_bet", "probability_per_round",
                "added_house_edge_pct_points", "cost_per_1000_rounds_in_bets"])
    w.writerows(mrows)

# 3. Whole-game house edge for simple strategies
def policy_game_ev(play):
    """play(c1,c2,up) -> EV conditioned on no dealer BJ."""
    ev = 0.0
    for u in UPS:
        pbj = b.p_dealer_bj(u)
        for c1 in UPS:
            for c2 in UPS:
                pr = b.P[u] * b.P[c1] * b.P[c2]
                if sorted((c1, c2)) == [10, 11]:
                    v = (1 - pbj) * 1.5
                else:
                    v = -pbj + (1 - pbj) * play(c1, c2, u)
                ev += pr * v
    return ev

from functools import lru_cache
def make_fixed(rule):
    @lru_cache(None)
    def ev(t, s, u):
        if t > 21: return -1.0
        if not rule(t, s, u): return b.ev_stand(t, u)
        e = 0.0
        for c in UPS:
            t2, s2 = b.add(t, s, c)
            e += b.P[c] * ev(t2, s2, u)
        return e
    return lambda c1, c2, u: ev(*state(c1, c2), u)

basic = lambda c1, c2, u: max(b.options((c1, c2), u).values())
mimic = make_fixed(lambda t, s, u: t < 17)                       # hit below 17, stand on all 17s
never_bust = make_fixed(lambda t, s, u: (t <= 11) if s == 0 else (t <= 17))  # never risk a bust on hard hands
# Basic strategy but never doubling or splitting
nods = lambda c1, c2, u: b.ev_hit_best(*state(c1, c2), u)
ev_basic = policy_game_ev(basic)
srows = [
    ["Basic strategy (charts on this page)", ev_basic],
    ["Basic strategy plus insurance on every dealer ace", ev_basic - b.P[11] * ins_cost * 1.0],
    ["Basic hit and stand only, never double or split", policy_game_ev(nods)],
    ["Never bust: stand on hard 12 or more, hit soft 17 or less", policy_game_ev(never_bust)],
    ["Mimic the dealer: hit below 17, stand on 17 or more, no doubles or splits", policy_game_ev(mimic)],
]
with open(os.path.join(OUT, "strategy-house-edge.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["strategy", "house_edge_pct", "loss_per_1000_bet_units"])
    for name, ev in srows:
        w.writerow([name, f"{-ev*100:.2f}", f"{-ev*1000:.1f}"])
print("done")
