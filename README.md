# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/onlybountyy-hub/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/onlybountyy-hub/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

**THE WORLD TODAY — Sunday 22 November 2026.** One page that sums up one day's world news, drawn as a newspaper front page. Every story on the page happened, or was first reported, on Sunday 22 November 2026; each was verified against at least two independent wire reports before it earned its place (see `SOURCES.md`, which also lists the tempting stories rejected because they belonged to earlier days).

The hero: **COP31 collapses in Antalya** — after a record 44 hours of overtime, the UN climate summit ended with no deal when the EU and its allies rejected a final text that never mentioned fossil fuels. Around it, eleven more of the day's stories: sea drones sink the Russian corvette *Merkury* at Benghazi; a drone levels a block of flats in Dymer, near Kyiv; Democrats clinch 258 House seats, their largest majority since 1992; Poland confirms all three objects on its soil were Russian Kh-101 missiles; settlers torch West Bank villages; missiles over the Gulf again; drones hit a UN building in Khartoum; 37 workers missing in a Banten candy-factory fire; tear gas on the highway in Gazipur; Nepal's PM opens his India visit; and Liverpool 4–0 Manchester United in Mauricio Pochettino's first game in charge. A "Day in Numbers" box keeps the figures honest.

The page is drawn programmatically (`build_image.py`, Pillow) in a flat newspaper style — no photographs, no copied artwork. `main.ts` validates the finished `entry.png` against the gate limits (≤ 1 MiB, ≤ 1024×1024) and copies it to the output directory.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=q6ckzx1w&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>

<sub>Referral: [make.fun/r/q6ckzx1w](https://make.fun/r/q6ckzx1w)</sub>
