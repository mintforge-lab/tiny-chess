import json, os, urllib.request

# 10x12 board, a8=21 h1=98; side to move is uppercase, board flipped each move
N, E, S, W = -10, 1, 10, -1
DIRS = {'P': (N, N + N, N + W, N + E), 'N': (-19, -8, 12, 21, 19, 8, -12, -21),
        'B': (N + E, S + E, S + W, N + W), 'R': (N, E, S, W)}
DIRS['Q'] = DIRS['K'] = DIRS['B'] + DIRS['R']
RAYS = [(d, 'kp' if d in (N + E, N + W) else 'k', 'qb' if d in DIRS['B'] else 'qr') for d in DIRS['Q']]
LINE = {d * t for d in DIRS['Q'] for t in range(1, 8)}

# PeSTO tables, mg then eg for P N B R Q K, a8..h1: char = value / 4 + 76
T = r'''LLLLLLLLdn[d]lTIJNRT\ZRGHONQROPFELKOPNNFFKKJMMTICLGFHRVFLLLLLLLLLLLLLLLLxwtnqmu{dea]ZY`aTROMLMPPONKJJJMLMNJLLKLJONNNOLLJLLLLLLLL"6D@[4H1:B^UR\NH@[U\al^WJPQYU]PRIMPOSQQJFJONQPRHE?IKLPHG2G>DHEGF>BIEDE<3FJFLJFF?FGNNLJGBHMRRRONHHJPRPPMHFKLPNKGFBGJKLGFAE?FHFH@<EM8CFBNJFPHIT[P@HUWVUXULKMQXUUNLJOORTONMLPPPPSPNMPPLNQTLDKHGIIBGHGIJJJHFJKNIKIKHLJLLLNLMKNONPNMLJMOQNNKJIKNNOMJHHHJLMJHEFJFKJHKHTVTY\NTWSTZ\`]RWKQRUPW[PFINRRUJGCFILNJNFAFHHMLKDAHGJLOJ:GILPPNCFONPPOONMOOOOKMNMNNNMMKKKMMOLLLLLMMNMKJJIKLKLJIJHJJLLJJIKJLMLKIMGELSO[WWWFBKLHZSZIHNNSZXZEEHHLPLLJFJJLKMKHLILKLPMCJOLNPKLLHJNHFD@JRRSSQNQHQTVZRTLGNNXXUQNMRRWZVZUHSQXTTVRHEPNNPNMFFDHHFCDDEFAKDGB<RPH>DLOSLGJJKBEJRLHGNRFHGIEDFHC@LEB@AD?HHF@ADHELNJ<AHNNHUO>NERP:CHHIPMHIPPPPVRONPRPQWWOJRRSRTRMHKQRSRNIGKOQRPNJEIMOPMKH?DGIEHFA'''
MG = (82, 337, 365, 477, 1025, 0)
EG = (94, 281, 297, 512, 936, 0)
B = 1 << 18  # packed score = mg + eg * B
HB, MK = B >> 1, B - 1
PHASE = {'n': 1, 'b': 1, 'r': 2, 'q': 4}
VAL = dict(zip('.pnbrqkPNBRQK', (0, 1, 3, 3, 5, 9, 99, 1, 3, 3, 5, 9, 99)))
MATE = 99999


def mr(j):
    return 110 - j + j % 10 * 2


PST, OPP = {}, {}
for n, p in enumerate('PNBRQK'):
    PST[p], OPP[p.lower()] = [0] * 120, [0] * 120
    for k in range(64):
        x = MG[n] + (ord(T[n * 128 + k]) - 76) * 4 + (EG[n] + (ord(T[n * 128 + 64 + k]) - 76) * 4) * B
        q = 21 + k // 8 * 10 + k % 8
        PST[p][q] = OPP[p.lower()][mr(q)] = x


def put(b, k, c):
    return b[:k] + c + b[k + 1:]


def flip(b):
    return ''.join([b[k:k + 10] for k in range(110, -1, -10)]).swapcase()


# position: board, packed score, phase, our castling (a, h), theirs, ep square
START = ('         \n' * 2 + ''.join(' ' + r + '\n' for r in ['rnbqkbnr', 'p' * 8] + ['.' * 8] * 4 + ['P' * 8, 'RNBQKBNR'])
         + '         \n' * 2, 0, 24, (1, 1), (1, 1), 0)


def gen(pos, caps=0):
    b, ep, wc = pos[0], pos[5], pos[3]
    for i, p in enumerate(b):
        if not p.isupper():
            continue
        for d in DIRS[p]:
            j = i + d
            while 1:
                q = b[j]
                if q.isspace() or q.isupper():
                    break
                if p == 'P':
                    if d in (N, N + N):
                        if q != '.' or d == N + N and (i < 81 or b[i + N] != '.'):
                            break
                    elif q == '.' and j != ep:
                        break
                    if not caps or q != '.' or j < 30 or j == ep:
                        yield i, j
                    break
                if not caps or q != '.':
                    yield i, j
                if q != '.' or p in 'NK':
                    break
                j += d
        if p == 'K' and not caps:
            if wc[0] and b[91:95] == 'R...':
                yield i, i - 2
            if wc[1] and b[96:99] == '..R':
                yield i, i + 2


def move(pos, i, j, pr='Q'):
    b, s, ph, wc, bc, ep = pos
    p, q = b[i], b[j]
    s += PST[p][j] - PST[p][i]
    if q != '.':
        s += OPP[q][j]
        ph -= PHASE.get(q, 0)
    b = put(put(b, i, '.'), j, p)
    e = 0
    if i == 91: wc = 0, wc[1]
    if i == 98: wc = wc[0], 0
    if j == 21: bc = 0, bc[1]
    if j == 28: bc = bc[0], 0
    if p == 'K':
        wc = 0, 0
        if abs(j - i) == 2:
            r, t = (91, 94) if j < i else (98, 96)
            b = put(put(b, r, '.'), t, 'R')
            s += PST['R'][t] - PST['R'][r]
    elif p == 'P':
        if j < 30:
            b = put(b, j, pr)
            s += PST[pr][j] - PST[p][j]
            ph += PHASE[pr.lower()]
        elif j == ep:
            b = put(b, j + S, '.')
            s += OPP['p'][j + S]
        elif j - i == N + N:
            e = mr(i + N)
    return flip(b), -s, ph, bc, wc, e


def ev(pos):
    # tapered eval + tempo
    s, ph = pos[1], min(pos[2], 24)
    m = ((s + HB) & MK) - HB
    return (m * ph + ((s - m) >> 18) * (24 - ph)) // 24 + 8


def att(b, k):
    # is our square k attacked?
    for d in DIRS['N']:
        if b[k + d] == 'n':
            return 1
    for d, f, s in RAYS:
        j = k + d
        q = b[j]
        if q in f:
            return 1
        while q == '.':
            j += d
            q = b[j]
        if q in s:
            return 1
    return 0


class Stop(Exception):
    pass


nodes = hard = 0
tt, rep, hist = {}, set(), {}
killers = [[0, 0] for _ in range(99)]


def qs(pos, a, b):
    global nodes
    nodes += 1
    if nodes > hard:
        raise Stop
    bd = pos[0]
    st = ev(pos)
    if st >= b:
        return st
    a = max(a, st)
    ms = []
    for i, j in gen(pos, 1):
        q = bd[j]
        if q == 'k':
            return MATE
        if j < 30 or st + VAL[q] * 100 + 200 > a:  # delta pruning
            ms.append((VAL[q] * 10 - VAL[bd[i]], i, j))
    ms.sort(reverse=True)
    for _, i, j in ms:
        s = -qs(move(pos, i, j), -b, -a)
        if s > a:
            if s >= b:
                return s
            a = s
    return a


def search(pos, a, b, d, ply, nul=1):
    global nodes
    bd = pos[0]
    if bd in rep:
        return 0
    k = bd.index('K')
    chk = att(bd, k)
    d += chk
    if d < 1:
        return qs(pos, a, b)
    nodes += 1
    if nodes > hard:
        raise Stop
    pv = b - a > 1
    tm = None
    e = tt.get(pos)
    if e:
        ed, es, ef, tm = e
        if ed >= d and not pv and (ef == 0 or ef > 0 and es >= b or ef < 0 and es <= a):
            return es
    st = ev(pos)
    if not pv and not chk:
        if d < 4 and st - 90 * d >= b:  # reverse futility
            return st
        if nul and d > 2 and st >= b and pos[2]:  # null move
            s = -search((flip(bd), -pos[1], pos[2], pos[4], pos[3], 0), -b, 1 - b, d - 3 - d // 6, ply + 1, 0)
            if s >= b:
                return s
    ep = pos[5]
    kl = killers[ply]
    ms = []
    for i, j in gen(pos):
        q = bd[j]
        m = i, j
        if q == 'k':
            return MATE
        o = (1 << 30 if m == tm else (1 << 28) + VAL[q] * 10 - VAL[bd[i]] if q != '.' or bd[i] == 'P' and j < 30
             else 1 << 27 if m in kl else hist.get(m, 0))
        ms.append((o, m))
    ms.sort(reverse=True)
    rep.add(bd)
    best, bm, n, a0 = -MATE, None, 0, a
    for o, m in ms:
        i, j = m
        p = bd[i]
        quiet = bd[j] == '.' and not (p == 'P' and (j < 30 or j == ep))
        if n and quiet and not chk and o < 1 << 27 and d < 3 and st + 120 * d <= a:  # futility
            continue
        c = move(pos, i, j)
        if p == 'K' or chk or j == ep or i - k in LINE:  # may expose our king: verify
            if p == 'K' and abs(j - i) == 2 and (chk or att(bd, (i + j) // 2)):
                continue
            f = flip(c[0])
            if att(f, f.index('K')):
                continue
        n += 1
        if n == 1:
            s = -search(c, -b, -a, d - 1, ply + 1)
        else:
            r = (1 + (n > 8) + (d > 6)) if d > 2 and n > 3 and quiet and not chk else 0  # late move reduction
            s = -search(c, -a - 1, -a, d - 1 - r, ply + 1)
            if s > a and (r or s < b):
                s = -search(c, -b, -a, d - 1, ply + 1)
        if s > best:
            best, bm = s, m
            if s > a:
                a = s
                if s >= b:
                    if quiet:
                        if kl[0] != m:
                            kl[1], kl[0] = kl[0], m
                        hist[m] = hist.get(m, 0) + d * d
                    break
    rep.discard(bd)
    if not n:
        return ply - MATE if chk else 0
    tt[pos] = d, best, 1 if best >= b else -1 if best <= a0 else 0, bm
    return best


def sq(j, white):
    j = j if white else mr(j)
    return 'abcdefgh'[j % 10 - 1] + str(10 - j // 10)


def think(g):
    global nodes, hard, rep, tt, hist, killers, pool
    pos, seen = START, set()
    for n, u in enumerate(g['moves']):
        seen.add(pos[0])
        i, j = [(10 - int(u[k + 1])) * 10 + ord(u[k]) - 96 for k in (0, 2)]
        if n % 2:
            i, j = mr(i), mr(j)
        pos = move(pos, i, j, u[4:].upper() or 'Q')
    seen.add(pos[0])
    white = len(g['moves']) % 2 == 0
    ms = [m for m in gen(pos) if sq(m[0], white) + sq(m[1], white) + 'q' * (pos[0][m[0]] == 'P' and m[1] < 30) in g['legal_moves']]
    if len(ms) < 2:
        return ms[0], white
    if len(tt) > 300000:
        tt = {}
    hist = {}
    killers = [[0, 0] for _ in range(99)]
    # node budget from a trial-wide pool, as if every game left ran to 200 plies
    left = (201 - g['plies']) // 2 + 96 * (g['games'] - g['game'])
    hard = min(CAP, pool // left)
    nodes = 0
    best = ms[0]
    try:
        for d in range(1, 99):
            rep = set(seen)
            a = -MATE - 1
            for n, m in enumerate(ms):
                c = move(pos, *m)
                s = -search(c, -a - 1, -a, d - 1, 1) if n else a + 1
                if s > a:
                    s = -search(c, -MATE - 1, -a, d - 1, 1)
                if s > a:
                    a, best = s, m
                    ms.insert(0, ms.pop(n))
            if nodes > hard // 3 or a > MATE - 99:
                break
    except Stop:
        pass
    pool -= nodes
    return best, white


pool, CAP = 30_000_000, 160_000
URL = os.environ['MAKEFUN_ENV_URL']


def post(path, o):
    r = urllib.request.Request(URL + path, json.dumps(o).encode(), {'content-type': 'application/json'})
    return json.load(urllib.request.urlopen(r))


g = post('/game', {})
while g['status'] != 'done':
    if g['status'] == 'your_move':
        u = g['legal_moves'][0]
        try:
            m, white = think(g)
            u = sq(m[0], white) + sq(m[1], white)
            u += 'q' * (u + 'q' in g['legal_moves'])
        except Exception:
            pass
        g = post('/move', {'game': g['game'], 'move': u})
    else:
        tt = {}
        g = post('/game', {})
