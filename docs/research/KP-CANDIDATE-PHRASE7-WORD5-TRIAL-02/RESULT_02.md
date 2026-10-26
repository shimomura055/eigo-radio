# RESULT_02 (KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01、2026-10-26)

> **訂正注記(2026-10-26 Fable確認、PM-SSOT-SYNC-14)**: 下記本文の『フレーズ側の差=LLM再実行の揺れ』および『er125不在のためスキップ』は誤り。実際は本日PRODUCTION_WIRED(既定ON)のKP救済機構(`er125_kp_rescue_production_01.py`)が発火した結果(`trial_result.json` `rescued: true`)。詳細・分離数値=`COMPARISON_02.md` §9。本文は改変しない。

自動生成(`make_report_02.py`)。Trial=P7(前回r1の返答を再利用・API 0)→W5(単語最大5)。Gate=Production関数同一適用。順位=最終候補の`ai_rank`(フレーズ→単語の順)。自=自ルーブリックY/B/N(`own_rubric_02.json`、judge前に確定)、judge=gpt-6.1-sol(フレーズは前回judge再利用、単語は今回新規)。③④適合=単語のみ(適合/境界[基本寄り]/不適合[易しい語])。

## ai_island_temple:a2（AIの仮想の島 / Standard）
- P7返答(再利用)=6件、W5返答=5件(生の語: strategy, obstacle, separately, detour, discoveries)、最終 フレーズ6＋単語4、call 4、¥1.509、152.6秒、RQA=REDUNDANCY_PASS
- Gate除外: [call2] detour (duplicate_of_top3)

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | worth paying attention to | 注目する価値がある | Y | Y | — | 定型構文。汎用 |
| 2 | フレーズ | carry over | 次の期間にも引き継がれる | Y | Y | — | 句動詞。汎用・適度 |
| 3 | フレーズ | a useful card to play | 役に立つ手 | B | Y | — | usefulは修飾語。card to play が核(R2過剰) |
| 4 | フレーズ | take a detour | 回り道をする | Y | Y | — | 比喩を含む定番表現 |
| 5 | フレーズ | make a difference | 効果をもたらす | Y | Y | — | 汎用の定番イディオム |
| 6 | フレーズ | one step ahead | 一歩先を行く | Y | Y | — | 定番の比喩表現 |
| 7 | 単語 | Strategy | 作戦 | B | Y | 境界 | 基本寄り+見出し由来の大文字表記 |
| 8 | 単語 | obstacle | 障害物 | Y | Y | 適合 | B1語彙。汎用 |
| 9 | 単語 | separately | 個別に | Y | Y | 適合 | 副詞。Standardでは適度 |
| 10 | 単語 | discovery | 見つけたこと | B | Y | 境界 | 基本寄り(R4やや易) |

## ai_island_temple:b1b（AIの仮想の島 / Advanced）
- P7返答(再利用)=5件、W5返答=5件(生の語: technique, performance, overlook, exploration, detour)、最終 フレーズ5＋単語4、call 4、¥1.74、181.6秒、RQA=REDUNDANCY_PASS
- Gate除外: [call2] detour (duplicate_of_top3)

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | carry over | 持ち越す | Y | Y | — | 句動詞 |
| 2 | フレーズ | a useful card to play | 使える手 | B | N | — | usefulは修飾語(R2過剰) |
| 3 | フレーズ | call on | 人に頼む | Y | Y | — | 句動詞(頼まれる) |
| 4 | フレーズ | look at separately | 分けて考える | B | N | — | 受動の語尾を落とした切り出しでやや不自然 |
| 5 | フレーズ | take a detour | 寄り道をする | Y | Y | — | 比喩を含む |
| 6 | 単語 | technique | やり方 | B | Y | 境界 | 基本寄り |
| 7 | 単語 | performance | 成績 | N | Y | 不適合 | 易しい語。glossも文脈依存 |
| 8 | 単語 | overlook | 見過ごす | Y | Y | 適合 | B2動詞。汎用 |
| 9 | 単語 | exploration | 探索 | Y | Y | 適合 | B2名詞。汎用 |

## uk_train_speaker_playback:a2（英国の電車マナー / Standard）
- P7返答(再利用)=4件、W5返答=5件(生の語: exception, campaign, entertainment, masterpiece, carriage)、最終 フレーズ4＋単語5、call 6、¥1.646、156.2秒、RQA=REDUNDANCY_PASS
- Gate除外: なし

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | draw a line | 一線を引く | Y | Y | — | 比喩の定番 |
| 2 | フレーズ | sound no one asked for | 誰も求めていない音 | B | N | — | 見出し由来でやや記事寄り |
| 3 | フレーズ | given written permission | 書面で許可を与えた | B | — | — | 過去分詞givenが余剰。written permissionが核 |
| 4 | フレーズ | reach for one's wallet | 自分の財布に手を伸ばす | Y | Y | — | 定番表現 |
| 5 | 単語 | exception | 例外 | Y | Y | 適合 | B1名詞。汎用 |
| 6 | 単語 | campaign | キャンペーン | B | Y | 境界 | 基本寄り(R4やや易) |
| 7 | 単語 | entertainment | 楽しみ | B | Y | 境界 | 基本寄り(R4やや易) |
| 8 | 単語 | masterpiece | 傑作 | Y | Y | 適合 | B2名詞。汎用 |
| 9 | 単語 | carriage | 客車 | B | Y | 境界 | 基本寄り・英国寄りの意味 |

## uk_train_speaker_playback:b1b（英国の電車マナー / Advanced）
- P7返答(再利用)=6件、W5返答=5件(生の語: uninvited, nationwide, automatically, recommendations, carriage)、最終 フレーズ6＋単語5、call 4、¥1.622、172.8秒、RQA=REDUNDANCY_PASS
- Gate除外: なし

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | draw a line | 線引きをする | Y | Y | — | 比喩の定番 |
| 2 | フレーズ | blanket ban | 全面的な禁止 | Y | Y | — | コロケーション |
| 3 | フレーズ | due to be shared | 伝えられる予定 | B | Y | — | be due toが核。shared付きでやや過剰 |
| 4 | フレーズ | reach for one's wallet | 自分の財布を取り出そうとする | Y | Y | — | 定番表現 |
| 5 | フレーズ | written permission | 書面での許可 | Y | Y | — | コロケーション |
| 6 | フレーズ | face a fine | 罰金を科される | Y | Y | — | コロケーション |
| 7 | 単語 | Uninvited | 求められていない | Y | Y | 適合 | B2形容詞 |
| 8 | 単語 | nationwide | 全国的な | Y | Y | 適合 | B2形容詞/副詞。汎用 |
| 9 | 単語 | automatically | 必ず | B | Y | 境界 | 基本寄り |
| 10 | 単語 | recommendations | おすすめ | B | Y | 境界 | 基本寄り(R4やや易)。複数形 |
| 11 | 単語 | carriage | 列車の車両 | B | Y | 境界 | 基本寄り・英国寄りの意味 |

## monkeys_paw:a2（猿の手 / Standard）
- P7返答(再利用)=6件、W5返答=5件(生の語: fate, funeral, scraped, twisted, dragged)、最終 フレーズ6＋単語5、call 6、¥1.92、186.3秒、RQA=REDUNDANCY_PASS
- Gate除外: なし

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | back to life | 生き返る | Y | Y | — | 定番表現 |
| 2 | フレーズ | to blame | 責任がある | Y | Y | — | be to blame の核 |
| 3 | フレーズ | take hold of | つかむ | Y | Y | — | 定番表現 |
| 4 | フレーズ | pulling free | 振りほどく | B | — | — | pull freeの現在分詞形のまま(切り出しがやや不自然) |
| 5 | フレーズ | break the silence | 沈黙を破る | Y | Y | — | 定番表現 |
| 6 | フレーズ | rise into the night | 夜に響き渡る | B | N | — | 描写的で再利用は限定的 |
| 7 | 単語 | fate | 運命 | Y | Y | 適合 | 汎用名詞 |
| 8 | 単語 | funeral | 葬式 | B | Y | 境界 | 基本寄り(R4やや易) |
| 9 | 単語 | scrape | こすれて音を立てる | Y | Y | 適合 | B2動詞。汎用 |
| 10 | 単語 | twist | ねじれる | Y | Y | 適合 | 多義の汎用動詞 |
| 11 | 単語 | drag | 引きずる | Y | Y | 適合 | B2動詞。汎用 |

## monkeys_paw:b1b（猿の手 / Advanced）
- P7返答(再利用)=7件、W5返答=5件(生の語: compensation, interferes, snatched, deserted, burial)、最終 フレーズ7＋単語4、call 6、¥2.138、220.2秒、RQA=REDUNDANCY_PASS
- Gate除外: [call2] interferes (duplicate_of_top3)

| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |
|---|---|---|---|---|---|---|---|
| 1 | フレーズ | accept no responsibility | 責任を負わない | Y | — | — | 定番のコロケーション |
| 2 | フレーズ | pay off the house | 家のローンを払い終える | B | N | — | pay offが核。目的語が記事固有(R2過剰) |
| 3 | フレーズ | interfere with fate | 運命を変えようとする | B | Y | — | interfere withが核。fateは目的語で余剰気味 |
| 4 | フレーズ | pulled free | 振りほどく | B | — | — | pull freeの過去形のまま(切り出しがやや不自然) |
| 5 | フレーズ | caught in the machinery | 機械に巻き込まれる | B | Y | — | 記事固有の文脈寄り |
| 6 | フレーズ | wail of loss | 失った悲しみを表す叫び声 | B | Y | — | 描写的でやや記事固有 |
| 7 | フレーズ | shake one's husband awake | 自分の夫を揺すって起こす | N | B | — | 記事固有の断片(R3) |
| 8 | 単語 | compensation | 補償金 | Y | Y | 適合 | 汎用名詞 |
| 9 | 単語 | snatch | さっとつかみ取る | Y | Y | 適合 | 動詞 |
| 10 | 単語 | deserted | 人けのない | Y | Y | 適合 | 形容詞。汎用 |
| 11 | 単語 | burial | 埋葬 | Y | Y | 適合 | B2名詞 |

