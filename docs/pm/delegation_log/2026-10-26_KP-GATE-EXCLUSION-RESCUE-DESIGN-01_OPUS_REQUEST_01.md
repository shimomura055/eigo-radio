## 管理ID
KP-GATE-EXCLUSION-RESCUE-DESIGN-01 Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A: X/Y/Z共通核への新処理フロー「違反検出→修正→既存Gateで再検査→Human Review候補登録」の設計、実装前)。read-only。

## 性質/到達上限Status/禁止事項
レビューのみ(ファイル編集・実行なし)。費用/日次: JPY0。到達Status: レビュー所見の提出。Fableが所見を照合しPM判断する(Opus所見は採用を自動確定しない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 本レビューはread-onlyのため委任文保存・check実行はFable側で扱う(Opusは実行しない)。
T-2: TTSなし。T-3: Capなし(JPY0)。

## レビュー依頼
依頼文(論点6点・期待出力)は `C:\Users\tensh\eigo-radio\docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\OPUS_REVIEW_REQUEST_01.md` を正本として全文Readし、その6論点に限定して所見を出す(全文再レビュー不要。ただし論点検証に必要な追加探索は妨げない)。

## 事前指定Read一覧
1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_REQUEST_01.md` 全文。
2. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/DESIGN_01.md` 全文(設計本体。段階1〜2、§1(a)〜(d)、§5新規則表、§8 Open Item)。
3. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/RESCUE_ANALYSIS_01.md` §3(AI島2件)と集計節。
4. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/SPEC_CHECK_01.md` §2(活用形→基本形例外とguard)。
5. `er105_kp_fulltext_selector_01.py`: Grep `_guard_ok|_GUARD_DET|postprocess_possessor_roles|run_canonicalization_gate|_token_pair_ok|_verb_base_candidates|role_ok_poss`→該当関数範囲(:560-700, :800-840, :900-960付近を想定)。
6. `er119_kp_candidates_01.py`: Grep `n_auto|gate_dropped|auto_eligible|excluded|_containment|raw_rank|shortfall`→該当範囲(:80-110, :300-360付近)。
7. 必要に応じ `er003_key_words_canonicalization.py` :520-545, :600-700(validator本体)。

## ユーザー指示(原文、要点のみ逐語)
「**今回の目的は、既存候補を安易に捨てず、修正可能なものをHuman Review候補として残す方式を設計すること。** 候補数8件を機械的に達成することが目的ではない。」「一般化によって、元の本文にない意味や不自然な英語を作らない。」「修正後は既存Gateで再検査する。」「学習価値の最終選択はHuman Reviewのユーザー判断に委ねる。」「不要なLLM呼び出し・再生成を避け、可能な修正は低コストで実施する。」「**重要：今回解決したいのは「8件に届かないこと」そのものではなく、「適切に修正できる候補まで捨ててしまうこと」です。**」

## 報告(出力形式)
論点1〜6ごとに「問題なし/要修正(修正案)/ユーザー判断要」+根拠(ファイル:行)。加えて: (A)段階1を「受理面を広げない」と呼んでよいか(=ユーザー承認なしにFable判断で実装候補へ進めてよい範囲か、11-8の範囲内/範囲外の判定への意見) (B)救済候補の`auto_eligible=False`既定が過剰制約かどうか (C)見落としているGate除外経路 (D)M(必須修正)/R(推奨)に番号を付けた一覧(10件以内)。最終行に5行以内の要約。