MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_25 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_25(課題①: 追加盲検05cのFableラベル保存→再集計→Fable判断に基づくX2'(THIN対策)1回のTrial→盲検表05d。DEV er112のみ・Production変更0)

## 0. Fable判断(Stage 1集計の評価)
- X2(本文での意味→素朴訳→伝達判定→gloss)は hard-core 4KP×3repで**字義訳・誤訳 0/12(B0は10/12)**、held-out 10KPで悪化0。事前宣言基準のうち「THIN≦B0+1」のみ不達(THIN 4、B0はTHIN 0だがFAIL 10のため基準が実質機能していない)。Fable評価: 主目的(字義訳の根絶)は達成、副作用=意味の**狭まり/移動**(`an unseen clock`→「時間差」、`sound no one asked for`→「誰も聞きたくない音」)が残る。VALIDATEDにはせず、**THIN対策を1回だけ**改善Trialする(同じPrompt変更の反復ではなく、原因=`meaning_in_text_en`が部分的側面に絞られる・素朴訳からの意味移動、に対する規則追加)。
- Cp: 平均品質は良いがrep間の揺れで字義訳2/12が残り不達。X2'がCpと同等以上なら案A系で確定、劣ればCp最適化版を再検討。
- 予算: 本委任の有料部分約3円(X2' R 7KP×3rep=21call+held-out 10call ≒ 31call×0.13円≒4.0円上限)。案件累計約279→約283円(<300円、7-7のFable自律、個別枠は既に0.47円超過中=累計で約4.5円超過見込み、報告で明示)。Stage 2はX2'の盲検結果を見てから(本委任では実行しない)。
- `PER_CALL_ARM` のCp 0.26円の一時値は0.20円へ戻す(残置しない)。

## 1. 05cラベル保存・再集計(API 0)
`TRIAL_05/fable_labels_05c.json` に以下を保存(Key未開封で確定)、`FABLE_BLIND_RESULT_05.md` に「05c」節として注記も逐語保存→ `report --labels fable_labels_05.json --labels_c fable_labels_05c.json` を実行し、Cpのheld-out・R確定値を記録。
```
{"1:A":"PASS","1:B":"PASS","2:A":"PASS","3:A":"PASS","4:A":"PASS","5:A":"PASS","6:A":"PASS","7:A":"PASS","8:A":"THIN","9:A":"PASS"}
```
Fable注記: 3:A「境界線を引く」は日本語で区別の慣用表現として機能しPASS(「線を引く」単独はFAIL_LITの従来判定と区別)。8:A「苦しみの中にある戻り道」は物語解釈を含み本文だけでは検証できないためTHIN(05の7:Bと同基準)。
- control一致率7/10(不一致3件はいずれも前回より緩い方向)を `FABLE_BLIND_RESULT_05.md` に「Fable判定の揺れ(緩化方向)」として明記。集計は前回ラベル維持で正しい。

## 2. X2'(THIN対策)の設計と実行
- X2'=X2に次の規則を追加(他は不変、`TRIAL_DESIGN_06.md` に差分を記録):
  (i) `meaning_in_text_en` は「フレーズ全体が本文で表す意味」を1文で書き、本文の一側面(例: 価格差の時間差)に絞らない。比喩の場合は比喩が指す一般的な意味(what it stands for)を書く。
  (ii) glossは `meaning_in_text_en` の**全体**を運ぶ訳にし、`naive_ja` の語を置き換える際に動作主・動詞の意味を移さない(asked for=頼む/求める を 聞きたい に変えない等。例は原文のKPを使わず一般例で)。
  (iii) glossの長さ上限・説明文化禁止は従来どおり。
- 対象: R(hard-core 4KP+co-KP 3)×3rep、held-out 10KP×1rep(05と同一セット、`--nheld 10` を明示)。arm名 X2p。費用pilot(0.20円/call)→本実行。台帳更新、ACTIVE_TASK有料run記録、10-24日次累計(約290.6円→)。
- 決定論集計(gloss==naive_ja率、文字数比、説明文型語尾)を実行。
- 盲検表 `fable_blind_05d.md`(新出文字列のみ、既出はラベル継承、arm伏せ、key別ファイル `fable_blind_05d_key.json`)。**VALIDATED判定はしない**。

## 3. 記録・Git
- `TRIAL_RESULT_05.md` 更新(Stage 1確定表[Cp含む]、X2'の差分と費用)、OPEN-474へ1行、DECISION_LOG(Fable判断: X2=字義訳0・THIN残→X2' 1回・予算)。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_25.md`(先頭MARKER一致、0始まり)。
- commit前に `git status` でindexに他agentのstage済みファイルが無いことを確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。
- 報告 `docs/pm/RESULT_PACKET_KPGM25.md`: Cp確定値、X2'の費用・出力数・決定論集計、盲検表05dの場所、Stage 2準備状況(54KP、約3.6円)、4行、判定整合行、使用モデル(gpt-6-luna effort=high、25節例外)。