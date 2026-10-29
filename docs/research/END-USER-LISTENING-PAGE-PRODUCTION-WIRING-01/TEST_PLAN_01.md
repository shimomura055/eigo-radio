# TEST_PLAN_01(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_01。実装後に実施。本委任では未実行)

設計=`WIRING_DESIGN_01.md`。test file案=`er135_enduser_page_01_test_01.py`(unit/integration)、`er135_enduser_page_verify_01.py`(Playwright)。DefaultOffIsolation型は不要(承認済み・flagなし)。既存testの失敗集合はOPEN-588の14件と同一であること(増加0)を回帰基準にする。

## 1. unit(API 0・音声/ASRはfixtureまたはキャッシュ)
| ID | 内容 | 期待 |
|---|---|---|
| T-ADP-1 | X/Y/Z実ページfixture(月reselect・fee_03・melos_02)から`extract_article`: 行数==`<tr>`数、kind未知label=STOP | 3 Family×Std/Advで一致、未知labelは停止 |
| T-ADP-2 | 文分割: 引用符閉じ/略語/小文字継続/日本語/Z複数div(`"…," said X.`) | 期待文数・sid連番、本文連結==dev行テキスト |
| T-ADP-3 | 開発者向け専用要素除去: ⏸・rpt-*・凡例・aux・#pww・制作情報 | 残存0(LR/Fallback付きfixtureで確認) |
| T-ADP-4 | 太字(lk1/lk2/lk3, strong)保持と対象語特定(emphasize相当) | devと同一語が太字、英文不変 |
| T-ADP-5 | glossary: display_spec付き=assert全通過、無し=生成なし+build_infoに『適用対象外』 | 両分岐 |
| T-ADP-6 | KP英語区間: 4ブロック/5ブロック(Z Adv KP2相当)/3ブロック(STOP)/ASR不一致(STOP) | 規則通り |
| T-TR-1 | X訳割当: 段落数一致OK/不一致=STOP/manuscript無し=訳なし | 3分岐 |
| T-TR-2 | Y `details.ja`採用、Z訳なし、英語Comment/In One Line=訳なし | `ja_source`2値のみ |
| T-LEARN-1 | 文法 SELECTED/ZERO、ニュアンス ADOPTED/REJECTED/NONE の組合せ(NXW02C evidence fragment fixture) | 採用のみコーナー出現、0件/不採用は見出し・空枠なし、各最大1 |
| T-LEARN-2 | 引用英文内太字(学習ブロックの対象語)が正式データで機能 | 342チェック同等 |
| T-NOTICE-1 | Y注記: devにあり⇔Endにあり、文言==`PAGE_NOTICE_JA`、X/Zは出ない | 一致 |
| T-VAL-NEG | validator負例: placeholder field/`dev_translation_unapproved`/`=====`/⏸/`rpt-`/絶対path/音声sha不一致/文数不一致を1つずつ注入 | 全てSTOP、`enduser/`未生成 |
| T-ASSET-DIFF | production asset vs DEV rev01-e app.js/style.css/index.html の差分が許可リスト(§A末尾の除去項目)のみ | 許可外hunk 0 |

## 2. 同期(ローカルASR。キャッシュ使用、費用0)
| ID | 内容 | 期待 |
|---|---|---|
| T-SYNC-REG | DEV 3記事(AI島Std/Adv・月Adv、151文)で直接整列の境界 vs DEV最終sync | 中央値/最大差を記録。DEV検証指標(単調・重なり0・Chunk既知ギャップ16件一致・スナップ不能0)を再達成 |
| T-SYNC-P0 | **Phase-0**: Y(fee_03 Std/Adv)・Z(melos_02/NXW z copy)実音声で同期→ゲート(1)-(5)の合否と分布(token match最小、低信頼度境界数、文間ポーズ最小) | 結果をWD §6に追記し閾値T確定。**不合格Familyは設計見直し(Fableへ報告)** |
| T-SYNC-CACHE | 同一mp3sha再実行でASR呼出0、1 mp3差替えで当該segmentのみ再計算 | ASR呼出数==変更segment数 |
| T-SYNC-FAIL | モデル不在/ASR例外/ゲート違反/トークン一致率閾値割れの注入 | `EnduserPageStop`、`enduser/`未生成(古い`enduser/`は削除)、dev index.html sha不変 |
| T-SYNC-OFFSET | episode_offset_check(全編mp3内位置)を全行で | ずれ<=0.05s |

## 3. integration / Regression
| ID | 内容 | 期待 |
|---|---|---|
| T-INT-X/Y/Z | 既存完成run(月reselect/fee_03/melos_02)の`pages`再実行(X=listening page CLI、Y/Z=`--stages …pages,page_verify`相当をcopy-runで)でdevとEndが両方生成 | rc=0、`enduser/`一式、`build_info`整合、API 0(usage/cost_log行数不変) |
| T-NUANCE-EV | NXW02C copy-run(X nxm1/nxm2、Y nxw_y1/y2、Z nxz2/3/4)でニュアンス採用/不採用/0件×Std/Adv | 採用levelのみ表示、他は非表示(6組合せの表を作成) |
| T-REG-DEV | hook前後で開発者向け`index.html`と全mp3のsha256一致、DEV URL(`user_test/dev_enduser_page_01`)不変 | 差分0 |
| T-REG-SUITE | er019 page系・er120_nuance_display(11)・er128_nuance_hr(37)・er121 runner・er026 runner・er063・stop系の既存test | 旧失敗集合(OPEN-588)と同一 |
| T-RETRY | pages 2回連続実行(冪等)・segment mp3差替え後の再実行(当該のみ再計算)・enduser失敗→修正→再実行・publish後dev更新のstale検出 | WD §8の表どおり |
| T-COST | `build_info.cost`: api_calls==0、前後のcost集計不変、wall時間記録 | 量産単価増分0円/セット |
| T-DEV-PARITY | 同一記事(AI島/月)でProduction生成JSONとDEV JSONの差が期待差のみ(placeholder除去・訳11ブロック除去・nuance/grammar正式化・source/path) | 期待外差0 |

## 4. ブラウザ(Playwright。local→live)
`er135_enduser_page_verify_01.py <BASE_URL>`(DEV `verify_rev_e_01.py`/`verify_rev_d_01.py`系を記事非依存化して継承)。6組合せ(X/Y/Z×Std/Adv)で:
- 1文ハイライト追従(再生位置と対象英文の対応)・文クリック再生・シーク後追従・パート間連続再生・停止/再開・Std/Adv切替整合
- 「▶ ここから再生」+黒系■停止、KP英語のみ再生、Vocabulary/Grammar/ニュアンス表示、引用英文太字、学習コーナー色(淡黄/青/緑)、「覚えておきたい表現」→「日本語訳」順
- 記事切替UIなし、`[DEV]`表示なし、Y注記、PC(1280)とスマホ(390x844)
- console error 0・HTTP 4xx/5xx 0・リンク切れ0・音声欠落0
- 実機iOS Safari/Android Chrome: **未実施(模擬のみ)**を結果表に明記。Chromium mobile emulation+WebKit(インストール確認後)は『模擬』。
- 証跡: `docs/research/END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01/`の`verify_result_*.json`・`shots_*`(新置き場は作らず当該研究dir内)。

## 5. PRODUCTION_WIRED判定への対応(U§9)
| 条件 | 本計画での担保 |
|---|---|
| 1 X/Y/Z・Std/Advの正式初回経路に実装 | WD §2 hook + T-INT-X/Y/Z |
| 2 2種ページが正式経路から生成 | T-INT、新規記事の初回run(次の完成候補)でも確認 |
| 3 正式runtimeの発火証拠 | `build_info`+runner stdout+live URL |
| 4 必須test・Regression | §1-§3 |
| 5 retry/fallback/regeneration/resume整合 | T-RETRY、WD §8 |
| 6 DEV仮データ・未承認翻訳の混入なし | T-VAL-NEG、T-DEV-PARITY |
| 7 CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新 | WP-F |
| 8 Git反映 | commit/push(自分のfileのみ明示add) |
| 9 Dangling/重要Open Itemなし | 公開copy手順・完成報告テンプレ・DEV URL方針をWP-Fで確定 |
| 10 Fable独立受入 | Fable |
