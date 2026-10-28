# FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02B(Fable→Sonnet worker、2026-10-28)

注記: 下記「ユーザー原文」ブロックは同内容が`2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md`に逐語保存済みのため、本ファイルでは該当ブロックを省略しその旨を示す(それ以外の委任本文は逐語)。

管理ID FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02B「ユーザー原文の保存+テーマ候補の再検証・絞り込み(5件の前段)+既存Family Y制作物への発言小町影響確認(API 0)+情報源レジストリ草案」。並行worker 委任_02A が利用規約精査(`TERMS_REVIEW_01.md`)を実施中=規約判定はあなたは行わず、02Aの結果待ちの前提で候補を整理する(最終5件の確定とSSOT反映はFableが委任_03で指示)。
**ファイル範囲**: `docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md`(下記ユーザー原文を**逐語**保存、最初に)、同`_委任_02B.md`(本文逐語)、`docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/THEME_SHORTLIST_01.md`・`KOMACHI_IMPACT_CHECK_01.md`・`SOURCE_REGISTRY_DRAFT_01.md`・`sources_domestic/`/`sources_overseas/`への追加証跡・`BUDGET_LOG_02B.md`・`stop_check_02B.json`、`docs/pm/RESULT_PACKET_FYDR2B.md`。SSOT・ACTIVE_TASK・Production code・既存成果物の変更禁止(小町由来素材も削除・変更しない。ユーザー決定①「既存成果物を無断で変更・削除しない」)。LLM不使用、API 0。発言小町・Redditの新規取得は禁止。Family A/B/C不可。
開始時 `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/stop_check_02B.json`(rc=3で停止)。

## ユーザー原文(逐語)
(省略: `2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md`に逐語保存)

## 手順
1. `THEME_SHORTLIST_01.md`: 既存の国内10・海外10(`DOMESTIC_THEMES_01.md`/`OVERSEAS_THEMES_01.md`)から、発言小町のみを根拠とするもの(T4/T5/T8/T10)と小町根拠を除くと3視点が崩れるものを除外し、残りを§3の優先順位1〜6で採点(各1〜5、根拠付き)。上位8件程度を候補とし、各候補について「採用する情報源(サイト+実投稿URL+投稿日時)」「確認済みの実在意見(抜粋要約)」「3 Voice候補(【確認】=投稿から読める事実/【構成案】=AI構成)」「面白さ」「評価(リアリティ・3軸独立性・日本関連性)」を§5Bの表形式で。小町根拠を他サイト(知恵袋/増田/ガルちゃん/ママスタ/HN等)の実投稿で代替できる場合は代替投稿を**本文取得して**証跡に追加(新規取得は小町・Reddit以外、礼儀的レート)。上位候補は「規約判定待ち」と明記(02Aの結果で確定)。
2. `KOMACHI_IMPACT_CHECK_01.md`(read-only、API 0): 既存Family Y制作物(`docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/`のSOURCE_LOG_02/PROVENANCE_04/PERSONAS_05/THEME_DATA_02.json、`er121_output/family_y_production_01/`配下の記事・Trial成果、公開ページ`user_test/`のY記事)について、発言小町由来の素材が(a)どの成果物のどの箇所に使われたか(URL・投稿IDの対応)、(b)公開済み/Trialのみ/未公開の別、(c)Persona・原稿に逐語の転載があるか(抜粋照合)を表にする。**削除・変更はしない。**Fable判断用に「影響あり/なし/不明」と対応案(記録のみ/再制作/非公開化等の選択肢と費用)を提示。
3. `SOURCE_REGISTRY_DRAFT_01.md`: §2の10項目で国内/海外を分けた情報源レジストリ草案(規約欄は「02A TERMS_REVIEW_01参照・判定待ち」とし断定しない。発言小町=利用不可(ユーザー決定①)、Reddit=対象外(ユーザー決定②、将来利用可能性の記録)、アクセス不能サイト=「アクセス不能」、低優先=「低優先度」と区別)。既存のFamily Y Research工程・Persona設計思想・Production仕様(CURRENT_SPEC Grep「Family Y」、`docs/research/FAMILY-Y-VOICES-DESIGN-01/`の手順書)との参照整合点(どの文書からこのレジストリを参照させるか)を列挙(編集はしない)。
4. `BUDGET_LOG_02B.md`、`docs/pm/RESULT_PACKET_FYDR2B.md`(≤15行)。
5. Git: `git diff --cached --name-only`空確認→自分のファイルのみ明示`git add … && git commit -m "FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02B: ユーザー決定保存+テーマ候補再検証+小町影響確認+レジストリ草案(API 0)"`を1コマンド、`git add -A`禁止、他workerファイル不可。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 候補上位8(テーマ+主情報源+3視点1行)、小町影響の結論、レジストリ草案の構成、commit sha、判断候補。
