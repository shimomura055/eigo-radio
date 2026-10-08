# FACTLOCK-ASTRA-E2E-TRIAL-01 委任_02 結果(B3注記仕様 v1 作成、2026-10-09、API支出¥0、git操作なし)

## 1. 成果物とテスト
- `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1.md`(§0〜§9)
- `er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01.py`(決定論検証、LLM不使用)
- `er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01_test.py`(13件、`.venv/Scripts/python.exe -X utf8 -m unittest b3_annotation_check_01_test`でOK実測。うち2件は既存のホルムズ/宇宙兵器の過去注記版を実ファイルで検査)
- `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1_OPUS_POINTS.md`
- `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02.md`(委任文全文)、同`.md_check.json`(check_delegation_prompt: FAIL=固定ブロックE-1/D-1/G-1/F-1・Grep一覧・実行コマンド節の欠落。指示どおり続行)

## 2. 仕様の要点(ユーザー8項目)
1. 何を【事実N】にするか: 台帳fact IDの境界。brief項目が既定の単位、異なる台帳factを根拠とする複数文のときだけ文境界で分割。出現順に連番。
2. 複数要素: 要素(主体・行為・時期…)では割らない。1文内・1台帳fact内は分けない。限定文は直前の事実に属する。1項目最大3事実。
3. 重要数値: 台帳`numeric_value`にある(E1)、または`date_or_period`にありStorylineに出る(E2)ものだけが中核適格。他は周辺。
4. 数字が主役: 上限=max(3,min(6,floor(n/2)))、全件中核は禁止。閾値の根拠は弱い(新6で初測定)。
5. 名称内番号: 数値扱いせず中核不可(name_embedded/ordinal/year)。印は【周辺数値】(案A継続。印なし案は論点)。台帳ID形式は印なし。
6. 台帳由来: 台帳外の肯定的主張は注記せず記事ごとSTOP、限定文は残して記録。台帳IDは注記に併記せずサイドカーに保存。
7. 迷った場合: 分けない/周辺/名称内番号側/ID全列挙、全て`annotation_notes`に記録。
8. 照合: strip後の原文一致(md+JSON)、台帳紐付け、数値の台帳照合と分類漏れ検出、連番、二重注記(A/B)と機械的解決規則。

## 3. 旧4への適用例と過去注記の食い違い(§7、例示のみ)
計4件: META 0 / ホルムズ 0 / 宇宙 1(2021年11月15日 中核→周辺)/ ミニバッグ 3(2026年9月・2026年10月 中核→周辺、段落→箇条書きのレイアウト差)。型=中核適格性3件+レイアウト1件。宇宙・ミニバッグは過去より中核が減る。

## 4. Opusに出す論点
OPUS_POINTS.md に8件: E1/E2妥当性、上限式、名称内番号の印、分割単位、二重注記の解決規則の偏り、注記者の汚染層、レイアウト例外、STOP条件の過剰性。

## 5. 未確認事項・Fable判断が必要な点
- 新6の台帳が`numeric_value`・`date_or_period`欄を出すか(ミニバッグ台帳には`numeric_value`が無い=確認済み)。
- Writerプロンプトの「中核は最大3」記載の有無。上限4〜6が通るか未確認。
- 現行runnerが再利用分岐でmdとJSONのどちらを読むか。JSON本文はmdと文面が異なりうる(all6 hormuzで確認)。
- harnessは箇条書き行頭の【事実N】のみ読む(確認済み)。ミニバッグの段落形式はレイアウト例外Lが必要。
- 注記者を新規worker 2名にするか(旧4の過去注記者は汚染層)。
- 台帳外の肯定的主張が見つかった記事をSTOPする設計は、旧4の確認範囲では発生していないが全体の発生率は未確認。
- 過去のTrial結果との直接比較は、注記が変わる宇宙・ミニバッグでは不可。

## 6. 所要時間・API支出
API支出¥0(生成・検証にLLM不使用)。所要時間は計測していない。既存ファイル編集なし、git操作なし。
