MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29(課題①: 盲検05eのFableラベル保存→Stage 2確定集計(strict/lenient)→Trial結果報告書→X2pのProduction配線設計案(Opus条件Cレビュー用)。API 0・Production変更0)

## 1. 05eラベル(Key未開封で確定)を `TRIAL_05/fable_labels_05e.json` に保存、注記を `FABLE_BLIND_RESULT_05.md` 「05e」節へ逐語保存。
```
{"1:A":"PASS","2:A":"PASS","3:A":"PASS","4:A":"PASS","5:A":"PASS","6:A":"PASS","7:A":"PASS","8:A":"PASS","9:A":"PASS","10:A":"PASS","11:A":"PASS","12:A":"PASS","13:A":"PASS","14:A":"PASS","15:A":"PASS","16:A":"PASS","17:A":"PASS","18:A":"PASS","19:A":"PASS","20:A":"THIN","21:A":"PASS"}
```
Fable注記: 20:A「売れ行きは逆に下がった」は本文の文脈(他が上がる中で菓子が下がった)を補った説明でフレーズの意味(逆方向へ動く)より狭く、方向まで断定しているためTHIN。16:A「期待をひっくり返す」は文脈語「期待」を含むが本文での用法に合致しPASS。19:A「財布を出してお金を払おうとする」は見出し語の someone's を訳出していないが行為の意味を運びPASS。4:A「AIの裏に人がいると明かす」は比喩の指すこと(人間だと判明)を運びPASS。

## 2. Stage 2確定集計
- `report --labels fable_labels_05.json --labels_c fable_labels_05c.json --labels_d fable_labels_05d.json --labels_e fable_labels_05e.json`(必要なら `--labels_e` を実装)。non-R 54KPで、X2p対B0の**strict**(B0の良い方のrep基準)と**lenient**を算出: PASS→FAIL、PASS→THIN、THIN→PASS、FAIL→PASS の件数と該当KP・文字列。Cp_t4との比較も併記。
- 事前宣言基準(Stage 2: strict PASS→FAIL 0、PASS→THIN≦2/54)への適合可否を事実として記載。
- `TRIAL_RESULT_05.md` を確定版に(Stage 1 R/held-out、Stage 2、Before/After代表例表[B0文字列→X2p文字列、ラベル]、残存THIN一覧、新規悪化一覧、費用台帳合計、reasoning_tokens所見、Fable判定の揺れ7/10)。

## 3. ユーザー採否判断用の資料 `ADOPTION_PROPOSAL_01.md`(ユーザー§2-5の6項目)
 1. 根本原因(主因=意味生成callに「本文での意味を確定する段」が無い。増悪因子=文脈限定句。型=具体名詞を含み字義読みが文法的に成立し直訳が比喩の意味を運ばない新造/断片化比喩)。
 2. 採用候補の仕組み(X2p: 同一call内で `meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`→gloss、文脈限定句を「本文での用法に合わせる」へ置換、yes経路の定訳優先、意味全体を運ぶ規則。追加call 0、Production schema互換)。
 3. Before/After(R 12出力: B0 FAIL 10/12→X2p FAIL 0・THIN 1、held-out 10KP悪化0、Stage 2 54KP strict/lenient)。
 4. 残存NG・新規悪化(THIN一覧とその性質)。
 5. X/Y/Z共通仕様への影響(gloss生成は共通module、Zのrepair/再整合経路[current glossあり]には現状未適用=配線設計で扱う、A/B/C旧ラインは新規生成経路を通らない[Grep済]、Y=共通module経由で自動適用だがProduction経路なし)。
 6. 量産単価・速度への影響(X2p実測 0.13〜0.19円/call vs B0 0.057円/call、記事あたり+0.1〜0.3円、call数不変、推論token増による所要時間差を実測から)。

## 4. 配線設計案 `WIRING_DESIGN_06.md`(実装はしない。Opus条件Cレビュー用)
- 変更箇所: `er003_key_words_gloss_alignment.py` の Prompt(文脈限定句3箇所の置換、few-shot例「fall into」の扱い)、schema(新欄3つを `japanese_gloss` の前に挿入、Production必須欄維持)、validator(新欄の検証・既存規則不変)、Z repair/再整合経路(current glossあり)への適用方針(適用/非適用の選択と理由)、混在batchの扱い、A/B/C非適用の担保、flag要否(採用後は既定ON=Production Prompt変更。Trial中はDEVのみ)、revert単位(単一commit)、test計画(WC)、runtime evidence計画(X/Z正式KP段をDEV注入textで、新規TTS 0)、CURRENT_SPEC更新箇所(gloss規則の「他の文脈でも再利用できる訳」原則の変更=**ユーザー承認事項**として明示)。
- `OPUS_REVIEW_REQUEST_08.md`(条件C: 採用提案前。論点=Prompt変更の副作用[N層の説明文化・直訳調]、Z repair経路の扱い、schema互換、A/B/C隔離、評価の十分性[1 rep・Fable単独評価・揺れ7/10]、単価)。Fableが起動。

## 5. 記録・Git
- OPEN-474へ1行、DECISION_LOG(Fable: Stage 2集計結果と次工程=Opus条件C→UDR)。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_29.md`(先頭MARKER一致、0始まり)。commit前に `git status` でindex確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。
- 報告 `docs/pm/RESULT_PACKET_KPGM29.md`: Stage 2 strict/lenient表、基準適合の事実、ADOPTION_PROPOSAL要約、WIRING_DESIGN_06要点、4行、判定整合行。VALIDATED判定はFable。