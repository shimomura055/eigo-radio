MARKER: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04 (2026-10-24, Fable→sonnet-worker)

# 管理ID: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04(ユーザー決定: OPEN-482 Closeout確定 / OPEN-489 自律解決→Production / OPEN-487 原因究明・設計(実装はOpusレビュー後) / OPEN-488 影響調査 / Open Item運用の再発防止をPM_GOVERNANCEへ整合)
# ユーザー指示原文は末尾§Zに逐語。**最初に** `docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_USER.md` として逐語保存。

## Fable方針
- 原則(ユーザー§7): 既存承認仕様の不具合で委任範囲内に解決可能なら、登録・報告で止めず原因究明→修正→検証→Production反映→SSOTまで進める。ユーザー判断は仕様変更・品質基準変更・重大QCDトレードオフ・予算/範囲超過のみ。
- **OPEN-489**(`between nine and eleven` 誤NG): 数詞語runが `and` をまたいで失敗する局所的な解析不具合の可能性が高い。本委任で原因究明→修正(各層1関数1ブロック以内)→同じ影響分析gate(TEST_MATRIX拡張・replay PASS→NG 0・合成負例NG維持)→全回帰→runtime evidence(既存entry再判定、新規TTS 0)→commit→SSOTまで**完遂**(Opusレビューは不要と判定: 判定構造の変更ではなく解析の不具合。ただし修正が `_try_clock_pair`/年号読み/`one hundred and ten` と干渉する場合はその整合をTEST_MATRIXで固定)。
- **OPEN-487**(`one hundred thirty people`↔`1:30 people` 誤PASS): 原因は value_guard の UNKNOWN(kind_mismatch)が最終Gateで非阻止であること(委任_02の所見)。UNKNOWNの扱いを変えるのは最終Gateの作用変更で影響が広いため、**本委任では原因究明・方式候補(例: kind_mismatchのうち「number↔time」など明確に別種の組だけDIFF化/time atom側の文脈(people等の単位後続)で時刻解釈を外す/桁連結・年号との衝突確認)・TEST_MATRIX・replayベースラインまで**作り、`OPUS_REVIEW_REQUEST_02.md` を用意(Fableが起動)。実装は委任_05。
- **OPEN-488**(24時間表記・分00〜09): §5の調査5点を実施し、「既存仕様の不具合/仕様外の拡張/実害なし」のいずれかに分類して根拠を示す。既存Productionの入力・ASR結果(全Family保存entry)から該当表現の発生件数・誤NG/誤PASS/再生成/HR有無を実測。487/489との共通化可能性。不具合と判明し小修正で済むなら本委任で修正(gate付き)、拡張ならQCD影響を整理してユーザー判断案、実害なしなら根拠を記録。
- **OPEN-482 Closeout**: PRODUCTION_WIRED証拠(委任_02/03)とSSOT/Gitの整合を最終確認し、`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/CLOSEOUT_482_01.md`(PM Closeout Mandatory Check含む)→OPEN-482をCLOSED(2026-10-24ユーザー承認)。487/488/489は独立追跡。
- **再発防止(§7)**: `docs/pm/PM_GOVERNANCE.md` の該当節(Open Item運用/4原則「不具合は委任範囲内で自律的に解決」/Closeout)をGrepし、「Open Item登録は作業完了でも停止理由でもない。既存仕様の不具合で委任範囲内なら登録後そのまま修正へ進む(分類→修正→検証→反映→SSOT追跡)」を既存書式で最小追記(新規節・重複工程は作らない)。`.claude/agents/sonnet-worker.md` の報告ルールにも1行(「新規OPEN登録時は『修正へ進む/ユーザー判断要/実害なし』の分類を必ず付し、修正へ進む場合は同一委任内で着手または次委任案を書く」)。DECISION_LOGに記録。
- 費用: 新規TTS原則0(必要時X/Z各1clip≤3円、理由記録)。日次10-24 約300円/1,000円。ACTIVE_TASK自分の行。並行agent: KP委任_27/_28、Family Y委任_20が走行中(er105/er003/er112/er110系)。er021/er006/er078を触るのは本委任のみだが、全回帰中に他agentの一時状態で落ちるtestは単独再実行で確認。telemetry等の追跡ファイルへの自動追記は復元・stageしない(OPEN-490)。
- Git: commit前に `git status` でindex確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。489実装は単一commit。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_04.md`(先頭MARKER一致、0始まり)。
- 報告 `docs/pm/RESULT_PACKET_ATN4.md`: 482 Closeout確認/489(原因・修正・TEST_MATRIX・replay・回帰・evidence・commit)/487(原因・候補・ベースライン・Opus依頼文)/488(調査5点・分類・根拠・推奨)/再発防止の更新箇所、各項目のProduction Status・QCD・残課題、4行、判定整合行、使用モデル(LLM呼出0見込み)。

## 成果物の置き場
`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/`: `OPEN489_ROOT_CAUSE_01.md`、`TEST_MATRIX_03.md`、`REPLAY_03.md`、`RUNTIME_EVIDENCE_02.md`、`OPEN487_DESIGN_01.md`、`OPUS_REVIEW_REQUEST_02.md`、`OPEN488_IMPACT_01.md`、`CLOSEOUT_482_01.md`。

## §Z ユーザー指示原文(逐語)
# ASR数値・時刻表現｜OPEN-482 Closeout／OPEN-487・488・489対応指示

## 1. ユーザー決定

以下の方針を正式承認する。

| Open Item | 判断 | 対応 |
|---|---|---|
| OPEN-482 | Close承認 | 完了記録を確定 |
| OPEN-487 | 自律解決 | 原因究明→修正→検証→Production Wiring |
| OPEN-489 | 自律解決 | 原因究明→修正→検証→Production Wiring |
| OPEN-488 | 影響調査 | 必要性・実害・対応範囲を調査し、対応方針を整理 |

**重要：既存承認仕様の不具合について、対応が必要なことが自明であり、委任・予算範囲内で解決可能な場合、発見・登録・報告だけで作業を止めることを禁止する。**

ユーザーに判断を求めるのは、仕様変更・品質基準変更・重大なQCDトレードオフ・承認範囲や予算の超過など、実際にユーザー決定が必要な場合に限る。

---

## 2. OPEN-482｜Closeout

既存の修正・検証・Fable受入結果に基づき、OPEN-482をCloseする。

- PRODUCTION_WIREDの証拠とSSOT／Gitの整合を最終確認する。
- OPEN-487・488・489は独立項目として追跡する。
- 487〜489が残っていることを理由に482のCloseを遅らせない。

## 3. OPEN-487｜異なる数値表現の誤PASS

**問題：** `one hundred thirty people` と `1:30 people` が一致扱いになる。

これは本来異なる内容の表現を誤PASSさせる品質不具合である。

### 対応

1. どの正規化・数値比較処理によって誤って一致するのかを究明する。
2. 時刻・通常数値・年号などの区別を含め、既存仕様との整合を確認する。
3. 個別文字列の例外登録ではなく、根本原因に対する修正を行う。
4. 正常系・異常系・境界ケースでTrial検証する。
5. 誤PASSを解消し、既存の正常な音声を誤NGにしないことを確認する。
6. 既存承認仕様の修正範囲内で解決可能なら、Family X/Zおよび同じ共通moduleを利用するFamilyへのProduction反映まで自律的に進める。

## 4. OPEN-489｜正しい数値表現の誤NG

**問題：** `between nine and eleven` が誤NGになる。

正しい音声を誤って不合格にし、不要な再生成やHuman Reviewにつながる可能性がある。

### 対応

1. 誤NGの原因となる検査層・判定条件を特定する。
2. 接続詞 `and` を含む数値表現と既存の数値正規化仕様との関係を調査する。
3. 個別例外に依存しない修正を立案・実装する。
4. 数値範囲・通常の数値・時刻・年号・金額などとの衝突を確認する。
5. 回帰検査で既存正常判定を維持し、異常判定を誤PASSさせないことを確認する。
6. 既存承認仕様の修正範囲内で、関連FamilyのProduction Wiringまで完了する。

### OPEN-487・489共通

両件とも、**原因究明→対策立案→Trial→評価→修正・再検証**の自己ループで進める。

最初の修正案が失敗した場合、同じ対策の反復に固執せず、判定構造や前提から見直すこと。

OPEN-482の修正内容との整合も確認する。

## 5. OPEN-488｜24時間表記・分00〜09の未対応

**問題：** 24時間表記や `ten oh five` などが、既存の数値・時刻判定で十分に扱われていない。

本件はOPEN-487・489と異なり、現段階では既存仕様の不具合か、未対応範囲の拡張かを区別する必要がある。

### 調査内容

1. 現行仕様が想定する時刻表現の対応範囲を確認する。
2. 既存Productionの入力・ASR結果から、該当する表現の発生状況と実害を調べる。
3. 誤NG・誤PASS・不要なTTS再生成・Human Reviewの有無を確認する。
4. 対応する場合の技術的難易度、既存判定への影響、量産単価への影響を見積もる。
5. OPEN-487・489の修正と共通化できる部分がないか確認する。

### 調査後の扱い

- **既存承認仕様を満たしていない不具合と判明した場合：** 承認済み範囲内で自律的に修正・検証・Production反映する。
- **既存仕様外の新機能・判定範囲の拡張が必要な場合：** 対策案とQCD影響を整理し、ユーザー判断を求める。
- **実害がなく対応不要と判断する場合：** その根拠を示し、OPEN_ITEMSに記録する。独断で新仕様を追加しない。

単に「未対応である」と報告して終了しないこと。

## 6. Production受入・QCD

OPEN-487・489および修正対象となった488について、正式Production反映には以下を必須とする。

- Familyごとの正式経路への配線とruntime evidence
- retry／fallback／regeneration／resumeとの整合
- Primary／Secondary ASR、同音救済、数値正規化、最終Gateとの整合
- 必須Regression・Validator・integration test PASS
- 誤PASS・誤NGの新規発生がないこと
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
- Git反映
- Fableによる独立受入

共通moduleを使うA/B/Cなどの旧ラインも、影響範囲から除外しないこと。

必要十分な品質に達した時点で完成とし、追加の磨き込みは行わない。

作業は可能な範囲で並列化し、既存の音声・ASR結果を再利用して不要なTTS生成や費用を抑える。

開発費はプロジェクト全体の日次上限1,000円（JST）で管理し、上限到達が見込まれる場合は早めに報告する。無断超過は禁止。

## 7. 再発防止｜Open Item運用の是正

**今回の最重要なPM運用改善事項。**

不具合を発見した場合、以下を標準動作とする。

1. 発見・影響確認
2. 既存承認仕様の不具合か、新仕様が必要な課題かを分類
3. 既存仕様の不具合で、委任範囲内で解決可能なら、そのまま原因究明・修正・検証へ進む
4. 必要なProduction反映・回帰確認・SSOT更新まで追跡
5. ユーザー判断が本当に必要な場合だけ、問題・選択肢・QCD影響を報告する

**Open Itemへの登録は作業完了でも、作業停止の理由でもない。**

今回のOPEN-487・489のように、修正が必要なことが明白な不具合を登録・報告するだけで止まる運用を再発させない。

この原則を既存PM_GOVERNANCEと照合し、必要な範囲で運用記録を整合させる。重複する管理工程や過剰な検査は増やさない。

## 8. 最終報告

OPEN-482のCloseout、OPEN-487・489の解決結果、OPEN-488の影響調査結果を、それぞれ区別して報告すること。

各項目について、原因・対応・検証結果・Production Status・QCD・残課題を簡潔に示す。

**既存不具合は、報告することではなく、解決することが仕事である。**