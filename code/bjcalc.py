"""Infinite-deck blackjack EV calculator.
Rules: dealer stands on soft 17, blackjack pays 3:2, dealer peeks for blackjack,
double on any first two cards, double after split, one split (no resplit),
split aces get one card each, no surrender.
All EVs for player decisions are conditioned on the dealer not having blackjack."""
from functools import lru_cache

RANKS = [2,3,4,5,6,7,8,9,10,11]  # 11 = ace
P = {r: 1/13 for r in RANKS}
P[10] = 4/13

def add(total, soft, card):
    """Add a card to (total, soft). soft = number of aces counted as 11 (0/1)."""
    if card == 11:
        total += 11
        soft += 1
    else:
        total += card
    while total > 21 and soft:
        total -= 10
        soft -= 1
    return total, soft

@lru_cache(None)
def dealer_dist(total, soft):
    """Final dealer distribution from state. Keys 17..21 and 22 (bust)."""
    if total > 21:
        return {22: 1.0}
    if total >= 17:
        return {total: 1.0}
    out = {}
    for c in RANKS:
        t, s = add(total, soft, c)
        for k, v in dealer_dist(t, s).items():
            out[k] = out.get(k, 0) + v * P[c]
    return out

@lru_cache(None)
def dealer_final(up):
    """Dealer final distribution given upcard, conditioned on no dealer blackjack."""
    t0, s0 = add(0, 0, up)
    out = {}
    tot = 0
    for c in RANKS:
        if (up == 11 and c == 10) or (up == 10 and c == 11):
            continue
        t, s = add(t0, s0, c)
        tot += P[c]
        for k, v in dealer_dist(t, s).items():
            out[k] = out.get(k, 0) + v * P[c]
    return {k: v / tot for k, v in out.items()}

def p_dealer_bj(up):
    return P[10] if up == 11 else (P[11] if up == 10 else 0.0)

@lru_cache(None)
def ev_stand(total, up):
    if total > 21:
        return -1.0
    d = dealer_final(up)
    ev = 0.0
    for k, v in d.items():
        if k == 22 or k < total:
            ev += v
        elif k > total:
            ev -= v
    return ev

@lru_cache(None)
def ev_hit_best(total, soft, up):
    """EV of the best play (hit or stand only) from a state."""
    if total > 21:
        return -1.0
    return max(ev_stand(total, up), ev_hit(total, soft, up))

@lru_cache(None)
def ev_hit(total, soft, up):
    ev = 0.0
    for c in RANKS:
        t, s = add(total, soft, c)
        ev += P[c] * (-1.0 if t > 21 else ev_hit_best(t, s, up))
    return ev

@lru_cache(None)
def ev_double(total, soft, up):
    ev = 0.0
    for c in RANKS:
        t, s = add(total, soft, c)
        ev += P[c] * 2 * ev_stand(t, up)
    return ev

def ev_two_card_options(total, soft, up):
    """Stand, hit, double EVs for a two-card hand (not a split decision)."""
    return {"S": ev_stand(total, up), "H": ev_hit(total, soft, up), "D": ev_double(total, soft, up)}

@lru_cache(None)
def ev_split(rank, up):
    """EV of splitting a pair of `rank` (one split, DAS, split aces one card)."""
    ev_hand = 0.0
    t0, s0 = add(0, 0, rank)
    for c in RANKS:
        t, s = add(t0, s0, c)
        if rank == 11:
            v = ev_stand(t, up)  # one card only, 21 is not a blackjack
        else:
            o = ev_two_card_options(t, s, up)  # no resplit, DAS allowed
            v = max(o.values())
        ev_hand += P[c] * v
    return 2 * ev_hand

def options(hand, up):
    """hand = (c1, c2). Returns dict of action -> EV (conditioned on no dealer BJ)."""
    c1, c2 = hand
    t, s = add(*add(0, 0, c1), c2)
    o = ev_two_card_options(t, s, up)
    if c1 == c2:
        o["P"] = ev_split(c1, up)
    return o

def best(o):
    return max(o, key=o.get)

def game_ev():
    """Overall player EV per initial hand with basic strategy (no insurance)."""
    ev = 0.0
    for up in RANKS:
        pbj = p_dealer_bj(up)
        for c1 in RANKS:
            for c2 in RANKS:
                pr = P[up] * P[c1] * P[c2]
                player_bj = sorted((c1, c2)) == [10, 11]
                if player_bj:
                    v = pbj * 0 + (1 - pbj) * 1.5
                else:
                    o = options((c1, c2), up)
                    v = pbj * (-1) + (1 - pbj) * max(o.values())
                ev += pr * v
    return ev
