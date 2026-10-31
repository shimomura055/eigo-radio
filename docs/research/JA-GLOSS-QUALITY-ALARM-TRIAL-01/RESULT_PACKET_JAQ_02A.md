# RESULT_PACKET JAQ_02A (JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02A: Trial実行前のラベル凍結)

- 状態: 完了(API 0・Luna呼出0・Production変更0・STOP非該当[stop_scope_check rc=0])。Opusレビュー逐語=OPUS_REVIEW_01.md、基準=ADJUDICATION_RUBRIC_01.md、裁定記録=ADJUDICATION_01.md、凍結=labels_frozen_01.json(sha256 e98e830d3da315507c3fc9832cdbae4f76c3e6a9d375762612761e8180833a85)、T3'規則=T3PRIME_RULES_02.md、事前登録v2=TRIAL_PLAN_02.md。
- 件数(normal/problem/exclude): T2 71=70/1/0、T4 14=13/1/0、運用プール261=249/12/0、計346=332/14/0。severity: major 5(すべてユーザー既知の型)・minor 9。類型: 3=4、4=5、5=5(1,2,6=0)。
- κ=0.964(観測一致345/346)。不一致1件(BL-332 forced to log in)は第3判定でnormal。同一裁定者・同一セッションのため独立性は限定的(ADJUDICATION_01 §3)。
- 有病率(プール): 全体4.6%(12/261、Wilson 2.6〜7.9%)、dev項目除く3.7%(8/216、1.9〜7.1%)。Family別X4.3%/Y2.7%/Z3.1%(dev除く、区間広い)。
- T3'=16件(類型2〜5各4、dev8/held-out8、major12/minor4)。items.jsonは131件(tier=T3P)。
- Fable抜き取り20件(seed=20261101): ADJUDICATION_01 §6、blindシート=adjudication/spot_check_20_blind.md。
- 最終成果物: docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/ 配下(上記)。commit hash=(下の報告に記載)。
(1) 既存仕様整合: TRIAL_PLAN_01.md:27-34,56-57(置換)/EVAL_SET_01.md:37,40/OPUS_REVIEW_01.md/CURRENT_SPEC不変更。承認済み生成仕様(er003_key_words_gloss_alignment.py:152-156のjapanese_gloss規則)と整合(rubric §7-4)。
(2) 未承認機能の既定値: 本委任はProductionコード・Prompt・flagを一切追加していない(Trial文書・評価データのみ)。Grep: git diffはdocs/research配下とOPEN_ITEMS.md(OPEN-636追記のみ)。
(3) 失敗終了時の成果物: 失敗終了なし。ラベル凍結済みで、Trial(02B)は未実行。ユーザー原文の要求(Trial実行前の事前登録・ラベル凍結)に適合。実害ありうる点: 裁定が同一モデルのため、抜き取り確認で補う。
(4) 撤去/残置: TRIAL_PLAN_01の『警告が出たT2・プールの事後ブラインド裁定』(§5-2)を廃止(v02で置換)。T4『ラベル保留』を14件裁定で解消。残存Grep: TRIAL_PLAN_01.md は履歴として残置(v02が優先と本文冒頭に記載)。
判定整合: 重大NG=なし
判断候補(いずれも既存範囲内でFable判断、D=新規の重要判断ではない。区分はB/C): (a) P-a'でPrecision80%に要る誤警告率が正常208件中約1.6件以下と厳しい(TRIAL_PLAN_02.md:36-37、区分B。基準は動かさず未達ならUSER_DECISION_REQUIRED)。(b) T1のseverityをrubric適用後(held-out major 0→2)にするか(ADJUDICATION_01.md:71、区分B)。(c) ガードAの分母=major限定(TRIAL_PLAN_02.md:31、区分B。全件版はガードBで併記)。(d) 裁定の独立性が限定的な点(ADJUDICATION_01.md:51、区分C: Fableの抜き取り20件で補う)。
