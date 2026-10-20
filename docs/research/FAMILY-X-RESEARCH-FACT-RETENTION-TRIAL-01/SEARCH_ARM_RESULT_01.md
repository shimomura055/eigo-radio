# XRFR 検索込み腕 採点(機械)

## 方式別集計(retention=出典が明示している項目のうちLedger(Dは検証後/E0・Aはdraft view)に保持された割合)

| 方式 | runs | expected観測 | 保持 | retention | gold(KEY)expected/保持 | 検索回数(Researcher) | 平均検索 | 検証検索 | Researcher費用JPY | 総費用JPY | 時間s | in tok | out tok | Fact数 | 未判定フラグ | UNSUPPORTED |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E0 | 2 | 16 | 6 | 0.375 | 12/4 | [15, 4] | 9.5 | [None, None] | 16.989 | 16.989 | 126.5 | 71827 | 7992 | 8.0 | 0 | 0 |
| A | 2 | 15 | 7 | 0.467 | 11/4 | [14, 7] | 10.5 | [None, None] | 18.768 | 18.768 | 117.8 | 80132 | 8580 | 7.0 | 0 | 0 |
| D | 2 | 12 | 6 | 0.5 | 8/3 | [9, 10] | 9.5 | [5, 5] | 17.07 | 26.335 | 116.4 | 72528 | 8864 | 8.5 | 0 | 0 |

## run別 項目(expected=引用出典が明示 / retained=Ledger)

- A/s1 (facts=6, 検索14, 引用12件/取得可12件): SA:OK SC:OK M-A2:OK M-B1:MISS(draftに無し) M-B2:MISS(draftに無し) M-B3:MISS(draftに無し) M-B4:OK
- A/s2 (facts=8, 検索7, 引用6件/取得可6件): SA:OK SC:MISS(draftに無し) M-A1:OK M-A2:OK M-B1:MISS(draftに無し) M-B2:MISS(draftに無し) M-B3:MISS(draftに無し) M-B4:MISS(draftに無し)
- D/s1 (facts=9, 検索9, 引用9件/取得可9件): SA:OK SC:OK M-A1:OK M-A2:MISS(draftに無し) M-B1:OK M-B2:MISS(draftに無し) M-B3:MISS(draftに無し) M-B4:MISS(draftに無し)
- D/s2 (facts=8, 検索10, 引用6件/取得可6件): SA:OK SC:MISS(draftに無し) M-A1:OK M-B1:MISS(draftに無し)
- E0/s1 (facts=10, 検索15, 引用9件/取得可8件): SA:OK SC:MISS(draftに無し) M-A1:OK M-A2:OK M-B1:MISS(draftに無し) M-B2:MISS(draftに無し) M-B3:MISS(draftに無し) M-B4:MISS(draftに無し)
- E0/s2 (facts=6, 検索4, 引用12件/取得可12件): SA:OK SC:MISS(draftに無し) M-A1:OK M-A2:OK M-B1:MISS(draftに無し) M-B2:MISS(draftに無し) M-B3:MISS(draftに無し) M-B4:MISS(draftに無し)

## 引用出典の取得状況

- [200] chars=6857 avail=True https://dppa.un.org/en/news/yemen-has-returned-to-full-scale-war-special-envoy-warns <- A|mey|s1, D|mey|s1, E0|mey|s2
- [200] chars=3527 avail=True https://oananews.org/node/713861 <- A|mey|s1, A|mey|s2
- [200] chars=6335 avail=True https://www.sabanew.net/story/ar/154267?ocid=Nabd_App <- A|mey|s1
- [200] chars=6857 avail=True https://dppa.un.org/en/news/yemen-has-returned-to-full-scale-war-special-envoy-warns?utm_source=openai <- A|mey|s1, E0|mey|s2
- [200] chars=3527 avail=True https://oananews.org/node/713861?utm_source=openai <- A|mey|s1
- [200] chars=6335 avail=True https://www.sabanew.net/story/ar/154267?ocid=Nabd_App&utm_source=openai <- A|mey|s1
- [200] chars=3129 avail=True https://apnews.com/article/mideast-saudi-medina-houthis-october-15-2026-ffa2a29fe8f91f400b0b75067d269ad3 <- A|mey|s2, D|mey|s1
- [200] chars=4536 avail=True https://apnews.com/article/yemen-houthis-saudi-arabia-strikes-threats-307d49abfe63ff66c99c318d94ca3e15 <- A|mey|s2, E0|mey|s2
- [200] chars=5501 avail=True https://apnews.com/article/yemen-houthis-saudi-fighting-6afad4ec4c22dcccd379152ea87cb0e2 <- A|mey|s2, D|mey|s1, D|mey|s2, E0|mey|s2
- [200] chars=9388 avail=True https://dppa.un.org/en/node/136980 <- A|mey|s2
- [200] chars=2994 avail=True https://apnews.com/article/mideast-israel-palestinians-houthis-october-18-2026-793087dde3cb4435c6b771bae28faff3 <- D|mey|s1, D|mey|s2, E0|mey|s1, E0|mey|s2
- [200] chars=3119 avail=True https://apnews.com/article/yemen-houthis-saudi-arabia-aden-attacks-c39ea48032c0e8a76558b0296bb25244 <- D|mey|s1
- [200] chars=7650 avail=True https://osesgy.unmissions.org/en/news/statement-by-un-special-envoy-for-yemen-hans-grundberg-on-latest-attacks-against-saudi <- D|mey|s1, D|mey|s2, E0|mey|s2
- [200] chars=1479 avail=True https://org.petra.gov.jo/Include/InnerPage.jsp?ID=91288&lang=en&name=en_news <- D|mey|s2
- [200] chars=3450 avail=True https://apnews.com/article/saudia-arabia-yemen-houthi-rebels-explosions-ed4dcdad5cfd4b08033b1af5cf81dca5 <- E0|mey|s1
- [200] chars=12466 avail=True https://osesgy.unmissions.org/en/node/136978 <- E0|mey|s1
- [200] chars=209 avail=False https://press.un.org/en/2026/sc16479.doc.htm <- E0|mey|s1
- [200] chars=3025 avail=True https://www.presidentalalimi.net/en/news2064.html <- E0|mey|s1
- [200] chars=7650 avail=True https://osesgy.unmissions.org/en/news/statement-by-un-special-envoy-for-yemen-hans-grundberg-on-latest-attacks-against-saudi?utm_source=openai <- E0|mey|s2
- [200] chars=4536 avail=True https://apnews.com/article/307d49abfe63ff66c99c318d94ca3e15 <- E0|mey|s2
- [200] chars=2994 avail=True https://apnews.com/article/793087dde3cb4435c6b771bae28faff3 <- E0|mey|s2
- [200] chars=5501 avail=True https://apnews.com/article/6afad4ec4c22dcccd379152ea87cb0e2 <- E0|mey|s2
- [200] chars=1050 avail=True https://spa.gov.sa/N2701372 <- A|mey|s1
- [200] chars=2487 avail=True https://www.spa.gov.sa/ar/N2695829 <- A|mey|s1
- [200] chars=2705 avail=True https://www.spa.gov.sa/en/w2697151 <- A|mey|s1, A|mey|s2, D|mey|s1, D|mey|s2, E0|mey|s1, E0|mey|s2
- [200] chars=2487 avail=True https://spa.gov.sa/ar/N2695829?utm_source=openai <- A|mey|s1
- [200] chars=2705 avail=True https://www.spa.gov.sa/en/w2697151?utm_source=openai <- A|mey|s1, E0|mey|s2
- [200] chars=1050 avail=True https://spa.gov.sa/N2701372?utm_source=openai <- A|mey|s1
- [200] chars=826 avail=True https://www.spa.gov.sa/N2698672 <- D|mey|s1
- [200] chars=1786 avail=True https://www.spa.gov.sa/en/N2705390 <- D|mey|s1, E0|mey|s1
- [200] chars=936 avail=True https://www.spa.gov.sa/en/N2698603 <- D|mey|s2
- [200] chars=1311 avail=True https://www.spa.gov.sa/en/N2697547?type=news&uuid=N2697547 <- E0|mey|s1
- [200] chars=1120 avail=True https://www.spa.gov.sa/en/w2698805 <- E0|mey|s1

## 創作候補フラグ

- S|A|mey|s1|F004: watch:us_israel_others -> SUPPORTED
- S|A|mey|s2|F006: watch:coalition -> SUPPORTED
- S|A|mey|s2|F007: watch:coalition,watch:saudi_aggressor -> SUPPORTED
- S|A|mey|s2|F008: watch:saudi_aggressor -> SUPPORTED
- S|D|mey|s1|YEM-2026-10-09-UN-WAR-ASSESSMENT: motive_causal_marker -> SUPPORTED
- S|D|mey|s1|SAU-2026-10-15-MEDINA-MISSILE: watch:coalition,watch:saudi_aggressor -> SUPPORTED
- S|D|mey|s1|SAU-2026-10-19-ONGOING-ATTACKS-STATEMENT: watch:us_israel_others -> SUPPORTED
- S|D|mey|s2|YEM-SAU-2026-003: watch:coalition -> SUPPORTED
- S|D|mey|s2|YEM-SAU-2026-008: causal_stated_by_source -> SUPPORTED
- S|E0|mey|s1|YEM-20261010-COALITION-01: watch:coalition -> SUPPORTED
- S|E0|mey|s1|SAU-20261015-MEDINA-01: watch:coalition,watch:saudi_aggressor -> SUPPORTED
- S|E0|mey|s1|SAU-20261019-STATEMENT-01: watch:us_israel_others -> SUPPORTED
- S|E0|mey|s2|F05: watch:saudi_aggressor -> SUPPORTED
