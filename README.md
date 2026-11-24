# tiny-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/mintforge-lab/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/mintforge-lab/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A chess engine in at most 4 KB of Python: `main.py` is 3,921 bytes, Python 3.13 standard library only. It uses PeSTO tapered evaluation and PVS alpha-beta search (transposition table, null move, LMR, quiescence), budgeted in nodes rather than time, so replays play the same moves. Practice Elo 1654 on the dev-grade trial.

## Run it

```sh
# from inside the unpacked tiny-chess-01 kit (needs Docker)
node cli/makefun.mjs grade-local --kit . --bot ../tiny-chess --driver docker
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=83m70awq&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
