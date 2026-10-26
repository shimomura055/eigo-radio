## 管理ID
KP-GATE-EXCLUSION-RESCUE-DESIGN-02 Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A、前回KP-GATE-EXCLUSION-RESCUE-DESIGN-01のOpusレビュー[M1〜M6/R1〜R4、`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`]は前提として反映済み。**設計が実質的に変わった部分のみ**をレビュー)。read-only、JPY0。

## 性質/到達上限Status/禁止事項
レビューのみ。所見はFableが照合しPM判断する。ユーザー原文の要点: 「適切に修正できる候補は救済してHuman Reviewに残す」「単に『現行規則違反だから不可』で止めないこと」「区分1=承認済み仕様への準拠修正(過剰除外・実装不具合)/区分2=既存ルール変更が必要でユーザー判断を要する/区分3=救済すべきでない」「単にコードで対応が難しいという理由だけで区分3にしないこと」「誤った原形を作るリスクには必要十分な検査を設ける」。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: read-onlyのため委任文保存・checkはFable側。T-2: TTSなし。T-3: Capなし(JPY0)。

## レビュー依頼
正本=`C:\Users\tensh\eigo-radio\docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\OPUS_REVIEW_REQUEST_02.md`(Q1〜Q4、全文Read)。これに加えFableが重点確認を求める点:
(a) **区分1/区分2の境界判定**: ①副詞guard(`er105:662 _guard_ok`、承認文P-04「先頭またはto直後の動詞」には無い内部条件)を外して`studied separately→study separately`を通すことは「承認済み規則への準拠修正(区分1)」か「受理面の拡大(区分2)」か。②lexical have(`_FINITE_AUX_WORDS`に`have`が含まれ、P-04(3)の`has/had→have`がdead path)の役割判定導入は区分1か区分2か。OPEN-152(`OPEN_ITEMS.md:328`付近、USER_DECISION_REQUIRED/Non-blocking)の記録との整合。③過去形表への`rang`補完は区分1でよいか。
(b) **誤原形リスクの検査が必要十分か**: 三重検査(LLM提案語・CMU実在・前方活用一致)+文脈条件。実データ315種で単調性違反0・新規受理3、`bound to the protein`誤受理を検出し`bound`除外、`hoped→hop`をtestで防止。抜け(例: 不規則動詞の同形異義、名詞/形容詞と同形の語)はないか。
(c) **LLM評価者(gpt-6-luna、3回多数決)を設計の検証に使ったこと**の妥当性と、Production運用では決定論のみで閉じるか(LLM評価はProductionに持ち込まない設計か)。
(d) **語数超過A1(連続部分列短縮+演算子語保持規則)**: `too soon to wave a flag→too soon`が「意味保持」と言えるか、「機能語だけ禁止」等の規則で低価値救済(`bear`、`too soon`)が増えないか、HR提示の在り方。A2(スロット一般化`too soon to do`)を区分3推奨(独立評価reject 7/8)とした妥当性。
(e) **慣用句例外**(`can't be helped`: 法助動詞を含む慣用句を辞書裏付けで受理、Wiktionary CC BY-SAのvendoring条件)の設計上の懸念と代替案。
(f) **本文再アンカー**(`catch their interest→catches their interest`)が「本文対応」を保つ決定論か。
(g) 付随不具合候補: 有限助動詞トークン正規表現がカーリー`’`とASCII`'`で挙動が異なる(`can’t`除外/`can't`通過)。11-8分類(修正へ進む)の妥当性。
(h) `redelivery fee`(CMU分解=推測による代替合格に当たるため区分2非推奨)の判定の妥当性。

## 事前指定Read一覧
1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/{OPUS_REVIEW_REQUEST_02,DESIGN_01,PATTERN_DESIGN_01,RESCUE_TABLE_01,CASE_ANALYSIS_01,LOOP_LOG_01}.md`(DESIGN_01/PATTERN_DESIGN_01/RESCUE_TABLE_01は全文、他は該当節)。
2. `er123_kp_rescue_dev_01.py`: Grep `def |have_role|_guard|triple|monoton|OPERATOR|anchor|idiom|wiktionary`→該当関数。
3. `er105_kp_fulltext_selector_01.py` :560-700(guard・活用表)、`er003_key_words_min_unit.py` :240-290(`_FINITE_AUX_WORDS`・正規表現)。
4. `docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md` :100-130(P-04原文)。`CURRENT_SPEC.md` :1990-2003。`OPEN_ITEMS.md` Grep `OPEN-152`。

## 報告(出力形式)
Q1〜Q4+(a)〜(h)ごとに「問題なし/要修正(修正案)/ユーザー判断要」+根拠(ファイル:行)。区分1/2/3の最終分類に対する意見(11件それぞれ1行)。M(必須修正)/R(推奨)番号付き一覧(10件以内)。最終行に5行以内の要約。