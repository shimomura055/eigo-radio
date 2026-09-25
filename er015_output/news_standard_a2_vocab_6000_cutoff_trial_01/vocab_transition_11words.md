# vocab_transition_11words.md — Sewer: ユーザー指定11語の Advanced → v3 → v4 → v5 遷移表
(Sonnet目視、根拠1行ずつ。最終判定はFable/ユーザー。ランクは
`frequency_rank_top20000.json`と同じ方法[wordfreq top_n_list("en",20000)を
simple_lemma()でlemma化した最小順位]で本Trial実行時に再計算した値。
None=20,000語表外[かなり低頻度]。しきい値は6,000。対象11語は全てSewer
記事の語であり、Metaには該当箇所なし。)

対象: `a1_advanced_sewer.md`(Advanced、改変禁止)→
`a2v3_standard_sewer.md`(Standard v3、改変禁止)→
`a2v4_standard_sewer.md`(Standard v4、改変禁止)→
`a2v5_standard_sewer.md`(Standard v5[6000-cutoff]、本Trial新規生成)。

| # | 語(Advanced, rank) | v3 | v4 | v5(6000-cutoff) | 6,000ライン | 判定・根拠 |
|---|---|---|---|---|---|---|
| 1 | municipalities (11073, over) | "towns"(580)×2で統一 | 1回目"towns or cities" / 2回目"local governments"(不統一) | 1回目"towns" / 2回目"local governments"(不統一) | 明確にover→置換対象 | v3が最も自然かつ統一的な解。v4/v5とも文書内で表現が2種類に分かれる問題は解消されていない(v5もv4と同じ不統一パターンを再現)。ただしv4/v5どちらの語も"towns"(580)/"local governments"(rank低くtowns並みに平易)で、municipalities(11073)より大幅に平易化はできている。 |
| 2 | facilities (2202, **within**) | "places"(187)に置換 | "places"(187)に置換 | "places"(187)に置換 | within(2202≤6000)→本来「置換しなくてよい」語 | 3版とも一貫して"facilities"→"places"に簡略化。facilitiesは6,000語以内の一般語であり本来必須の置換ではないが、v5でも「無理な置換ではなく自然な言い換え」の範囲内(placesは意味を保持し不自然ではない)。v5のPromptが機能して「置換しない」を選んだわけではなく、単にモデルの文体選好で全版共通の現象。 |
| 3 | installation (5508, **within**) | "putting in"(putting=209)に置換 | "put in"(過去分詞、put=209)に置換 | **"installation"のまま維持** | within(5508≤6000)→原則そのまま許容 | v3/v4は句動詞へ置換(名詞→句動詞という不自然な型)。**v5は初めてAdvancedと同じ"installation"を再現**し、ユーザーが指摘した「installation→putting inのような不要な置換」を解消した最も明確な改善例。 |
| 4 | inspections (5694, **within**) | "checks"(487)に置換 | "checked"(487)に置換 | "checks"(487)に置換 | within(5694≤6000)→原則そのまま許容だが必須ではない | v5も3版とも一貫して置換。"installation"は同一文中でv5のみ保持されたのに対し、"inspections"は保持されず、同じ「within6000」判定内でも語ごとに扱いが割れた(Promptの"may remain"は保持を保証しないため仕様違反ではないが、一貫性は無い)。 |
| 5 | convenience (6887, over) | "life easy"へ言い換え(convenience自体を回避) | Advancedのまま"convenience"を保持(v3の改善が後退) | "convenient"(5588、形容詞形へ変換、**within**に収まる) | over→置換対象 | v4はuser指摘の問題を再現(退行)。v5は名詞"convenience"(over)を形容詞"convenient"(within)に言い換えることで意味を保ちながら6,000語以内に収める、自然で巧みな解決(v3の"life easy"より原文に近い意味を保持)。 |
| 6 | artery ("main artery", 12006, over) | "main artery"保持×2(比喩) | "main artery"保持×2(比喩) | "main artery"保持×2(比喩) | over だが記事の中心比喩として例外扱い | 全版で"main artery"自体は完全に一貫して保持(Prompt「必須技術語/比喩は意味保持に必要なら例外可」が機能)。 |
| 7 | wastewater (18216, over[表内最下位帯]) | 本文"wastewater"保持、タイトルも"Household Wastewater"のまま | 本文"wastewater"保持、**タイトルのみ**"Water from Homes"に置換(本文と不統一) | 本文"wastewater"保持、タイトルも"Household Wastewater"のまま | overだが記事主題語 | v5はv4のタイトル/本文不統一を解消し、v3と同じくタイトル・本文とも一貫して"wastewater"を保持。 |
| 8 | septic ("septic tank(s)", None=表外) | 保持×4 | 保持×4 | 保持×4 | 表外(最もover)だが記事の核となる専門語 | 全版で完全に一貫して保持。必須技術語として機能している。 |
| 9 | collects (2335, **within**) | "gathers"(4530)に置換(collectsより低頻度) | "gathers"(4530)に置換(v3から変化なし) | **"collects"のまま維持** | within(2335≤6000)→本来「置換しなくてよい」語、かつ置換先がより難しい語なので本来不要な置換 | v3/v4は「難語→別の難語」どころか「平易語→やや難しい語」への逆行だった。**v5は"collects"をAdvancedのまま再現し、この問題を完全に解消**。ユーザーが名指しした3問題のうち最も明確に解決した例。 |
| 10 | distant ("distant treatment plant"×2, 5212, **within**) | "faraway"(表外None)に置換×2 | "faraway"(表外None)に置換×2 | **1回目"faraway"(表外)に置換 / 2回目"distant"のまま維持** | within(5212≤6000)→原則そのまま許容 | v5は部分的にのみ改善(2箇所のうち1箇所は"distant"を維持できたが、もう1箇所は依然"faraway"へ置換)。**"faraway"はwordfreq上位20,000語にも入らない語(表外)であり、distant(5212、6,000語以内)より明確に頻度が低い**。v5自身のルール("Prefer words within roughly the 6,000 most common… replace only if clearly outside that range")に照らすと、この置換はルール違反(distantは6,000語以内なのに置換され、しかも置換先がより難しい語)。文書内で同じ語に対し2通りの扱いが混在する不整合も残る。 |
| 11 | invisible ("invisible main artery", 6153, over[僅かにover]) | "hidden"(2837)に置換(明確な簡略化、良好) | "unseen"(12884)に置換(invisibleより難しい語へ後退) | **"invisible"のまま維持** | over(6153>6000)だがボーダーライン | v3が最も良い解(明確な簡略化)。v4は「難語→別の難語」の典型的な悪化事例。v5はinvisibleをそのまま残すことで「難語→難語」の悪化は避けたが、v3が達成した簡略化(hidden)には到達しておらず、「無理な置換をしない」が「そもそも置換しない」という消極解に振れている。 |

## 集計(11語、v5時点の最終分類)

- **明確に改善(ユーザー指摘問題の解消)**: 3語 — installation(putting in→installation復元)、
  collects(gathers→collects復元)、invisible(unseen→難語化を回避)
- **部分的に改善**: 2語 — convenience(over→withinに収まる自然な言い換え)、
  distant(2箇所中1箇所のみ復元、他方は表外語faraway置換のまま残存)
- **一貫して保持(専門語・比喩として妥当)**: 3語 — artery(main artery、比喩)、
  septic、wastewater(v4のタイトル不統一も解消)
- **一貫して置換(within6000語でも置換される、必須ではないが不自然ではない)**:
  2語 — facilities→places、inspections→checks
- **未解決の不統一**: 1語 — municipalities(v3の"towns"統一に対し、v4/v5とも
  文書内で2種類の表現が混在)
- **v5固有の新規のルール違反候補**: distant→faraway(1箇所、within6000語を
  表外語へ置換)

## まとめ(Sonnet目視、最終評価はFable/ユーザー)

- ユーザーが名指しした3つの既知問題(installation→putting in /
  collects→gathers / distant→faraway)のうち、**installation・collectsは
  v5で完全に解消**された(Advancedと同じ語がそのまま再現された)。
  distantは2箇所中1箇所のみ解消し、残り1箇所は引き続き"faraway"
  (wordfreq表外、distantより明確に低頻度)へ置換されており、完全解消には
  至っていない。
- v4で新たに発生していたinvisible→unseen(難語化)は、v5では
  invisible→invisible(無変更)という形で「悪化はしない」解決に留まった。
  v3が達成していたinvisible→hidden(明確な簡略化)には及んでいない。
- convenienceはover6000からwithin6000へ品詞転換で自然に収まる、
  v5設計が意図通りに機能した好例。
- municipalitiesは3版共通で「文書内で同じ概念に2つの訳語が使われる」
  問題が未解決(v3のみ統一的)。
- artery/septic/wastewater(記事の中心比喩・主題語)は全版で一貫して
  保持され、「専門語・比喩は意味保持に必要なら例外可」の指示は安定して
  機能している。
