FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_01B-20261023

# 委任_01B: Family Y(Voices型)設計のための **旧Family B Voices固有仕様・品質NG履歴の棚卸し**(read-only・API費用0・Production変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_01B.md`(N≈320〜330、先頭行MARKER一致確認)。
2. ユーザー指示原文は並行の委任_01Aが `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md` に保存する(本委任では保存しない。参照が必要なら§1の要約で足りる)。
3. ACTIVE_TASK.md・SSOT(OPEN_ITEMS等)は本委任では編集しない(01Aと後続統合委任が行う)。

## 1. ユーザー指示の要点(Fable要約。原文は01Aの保存先)
- Family Y=Voices型の新規設計。**Family Xを技術・品質・Production仕様の基盤**とし、**旧Family BのVoices編集思想**を取り込む(旧B Production経路の改修・転用ではない)。
- 確定済み基本設計(再承認不要): 本文5パート固定=①リード文(テーマ・問題提起・導入)②Voice 1 ③Voice 2 ④Voice 3 ⑤Tension+Closing(独立Closing廃止・Tensionへ統合)。**3 Voices固定**(2V/4V不採用、可変構造の実装不要)。賛成・反対・中立である必要はなく、経験・価値観・利害・優先順位の異なる3視点。
- Voice編集思想(旧B承認済みを継承): "Research is backstage. People are on stage." 各Voiceは独立した人物として一人称で経験・感情・価値観・主観から発言。調査報告・統計・外部Evidenceの説明者にならない/視点・人物像・立場の独自性/迷い・葛藤は許容/他Voiceが担う反論まで抱え込まない/主観的意見の自由と客観的事実の正確性の両立/検証可能な数値・制度・他者の具体的行動・出来事を創作しない。旧B後期に承認済みのVoice立場境界・Fact Safety対策を継承。
- Tension: 旧Bの「共通前提→分岐点→非対称性」を基本継承し、3 Voicesの違いを浮き彫りにして自然に締める。再要約・反復・冗長なClosing相当は避ける。
- 調査対象§3-B: 3 Voicesの人物・視点設計方法/Voice間の独自性・立場境界/一人称・主観の扱い/Fact Safety・Fact Attribution/Analytical Leakage Check/Tensionの役割/旧Bで品質NGを生んだ構造的原因/後期にユーザーが承認した改善策/残存する構造的品質リスク。**承認済み最終仕様・途中Trial仕様・不採用案を明確に区別**。
- 4分類: A=X/Z承認済み共通仕様(継承)/B=旧B承認済みVoices固有仕様(整合確認して継承設計)/C=旧Bの旧仕様・不採用・不要な独自実装(継承しない)/D=Family Y固有の新設計(ユーザー判断)。
- §6 検討すべき品質リスク: (1)Voiceが解説者化(2)3 Voicesの立場・論点重複(3)他Voiceの中心主張の取り込み(4)VoiceとTension+Closingの論点重複(5)体験談内の事実創作(6)構造起因NGの反復。既存承認済み対策を優先、新Validator増設を目的化しない。
- DESIGN/RESEARCH ONLY。Trial・Production変更・API費用・未承認採用は禁止。

## 2. 本委任(01B)の範囲 = 旧Family B Voices固有仕様の棚卸し
成果物: `docs/research/FAMILY-Y-VOICES-DESIGN-01/INVENTORY_OLD_B_VOICES_01.md`
調査の起点: `er012_b_family_voices_production_01.py`、`er012_b_family_voices_a2_production_01.py`、関連Prompt/brief、`ER-*_REPORT.md`のB関連、CURRENT_SPEC「Family B」「Voices」「Tension」「Closing」「Analytical Leakage」「Fact Attribution」「Fact Safety」「立場境界」「一人称」節、DECISION_LOG/DECISION_LOG_HISTORY、OPEN_ITEMS/OPEN_ITEMS_HISTORY、`docs/pm/delegation_log/`のBユーザー指示、UDR。**全文読込禁止(Grep→該当節のみ)**。
各項目を「最終承認済み仕様(Status・日付・出典・原文引用の要点)/Trialのみ・不採用案(区別して列挙)/実装の所在/Family Yへの継承分類案(B継承 or C不継承、理由)」で表にする。
1. 旧Bの記事構造の変遷(Voices数、Closing、Tensionの有無・位置、Preview/Comment/KP/In One Lineの構成)と最終承認版。
2. 3 Voicesの人物・視点設計方法(人物像の決め方、視点の多様性確保、賛否中立以外の軸、ペルソナ生成Prompt、Voice間の割り当て)。
3. Voice間の独自性・立場境界(重複禁止規則、他Voiceの主張取り込み禁止、迷い・葛藤の許容、境界Validator/Checkの有無と性能)。
4. 一人称表現・主観的意見の扱い(規則、NG例、承認済みの言い回し境界)。
5. Fact Safety・Fact Attribution(体験談内の数値・制度・他者行動・出来事の創作禁止、Ledgerとの関係、Attributionの書き方、Fact Checker)。
6. Analytical Leakage Check(目的、判定規則、閾値、誤検知・見逃しの履歴、最終Status)。
7. Tensionの役割(「共通前提→分岐点→非対称性」の原文、長さ、Voiceとの重複禁止)、Closingの扱いの履歴。
8. **旧Bで品質NGを生んだ構造的原因**の一覧(事例・failure mode・発生頻度・原因分析・出典)、後期にユーザーが承認した改善策(原文・日付・効果の実測)、なお残存する構造的リスク(ユーザー/Fable/Opusが指摘したもの)。§6の(1)〜(6)に対応付ける。
9. 旧Bの費用・尺・retry実績(1記事セットの実測コスト、生成回数、再試行率、HR率。出典付き。無ければ「未確認」)。
10. 旧B固有の複雑な仕組み(独自実装・独自Validator・独自fallback)で、Family Yに不要と考えられるもの(理由付き、C分類候補)。

## 3. 制約
- Production/Prompt/SSOT変更禁止、API費用0、Trial禁止、A/B/Cコードは読取のみ(§27-3)。
- 推測と事実を分け、出典のない主張は「未確認」。承認済み(ユーザー原文あり)とClaude/Fable内部判断を区別。
- 所要目安: 60〜90分。commitは自分の成果物(INVENTORY_OLD_B_VOICES_01.md、delegation_log 1件)のみ明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。

## 4. 報告(docs/pm/RESULT_PACKET_FYD1B.md、同内容を最終報告で)
(1)成果物path・raw URL (2)項目別の要点(各1〜2行) (3)§6品質リスク(1)〜(6)ごとの「旧B原因/承認済み対策/残存リスク」要約表 (4)B継承候補とC不継承候補の一覧 (5)未確認事項 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。