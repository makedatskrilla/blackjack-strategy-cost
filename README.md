# Blackjack basic strategy and what each mistake costs

Computed blackjack basic strategy charts, the expected value of every option behind them, and the cost of common mistakes in percent of the bet.

Live page: https://makedatskrilla.github.io/blackjack-strategy-cost/

## Rule set

Infinite deck, dealer stands on soft 17, blackjack pays 3:2, dealer peeks for blackjack, double on any first two cards, double after split, one split per hand, one card to each split ace, no surrender.

With basic strategy the house edge under these rules is 0.57% of the initial bet.

## Files

| File | What it holds |
| --- | --- |
| `data/basic-strategy.csv` | 330 rows. Every hard total from 5 to 19, soft 13 to 20 and every pair against every upcard, with the best play and the expected value of stand, hit, double and split. |
| `data/mistake-costs.csv` | 30 common mistakes. Right play, wrong play, both expected values, cost in percent of the bet, chance of the situation per round and the added house edge if the mistake is made every time. |
| `data/strategy-house-edge.csv` | Whole-game house edge for five playing styles, from basic strategy to copying the dealer. |
| `code/bjcalc.py` | The calculator. Exact recursion over an infinite deck, no simulation. |
| `code/build_data.py` | Rebuilds all three CSV files. |
| `code/chart.py` | Prints the charts in a terminal. |

Expected values are in units of the initial bet and assume the dealer has already checked for blackjack.

## Rebuild

```
python code/build_data.py
```

Needs Python 3 and nothing else.

## Checks

- Stand, hit and double values match the Wizard of Odds infinite deck table to four decimals: https://wizardofodds.com/games/blackjack/appendix/1/
- Split values differ because that table resplits up to four hands.
- The charts match the Wizard of Odds 4 to 8 deck chart for a dealer who stands on soft 17 with double after split, except soft 13 against a 5 and soft 15 against a 4, which are hits with an infinite deck: https://wizardofodds.com/games/blackjack/strategy/4-decks/

## Related

- Kaggle dataset: https://www.kaggle.com/datasets/makedatskrilla/blackjack-basic-strategy-and-mistake-costs
- Kaggle notebook: https://www.kaggle.com/code/makedatskrilla/what-each-blackjack-mistake-costs
- House Edge Index, sourced house edge and RTP figures: https://makedatskrilla.github.io/house-edge-index/

## License

Data, code and text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See `LICENSE`.

Long-run expected values only. Not affiliated with any casino and not advice to play.
