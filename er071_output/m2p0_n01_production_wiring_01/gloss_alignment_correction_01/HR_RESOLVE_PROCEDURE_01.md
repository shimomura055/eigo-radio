# HR_RESOLVE_PROCEDURE_01: gloss再整合Human Review待ちの解消手順(1ページ)

対象: Trial専用`mode=corrected`でKP日本語glossの再整合がitem単位2回失敗し、`gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED`になったKey Phrase。Production既定(legacy)では発生しない。Human Review Lock・`human_review_queue.jsonl`は使わない(音声HR統計を汚さない)。

## 何が起きているか
- 報告書: `<KP段出力dir>/GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json`(+`.md`)。必須項目=article/level/rank・最終英語KP・現在gloss・失敗理由・全attempt結果・再生成候補(提案gloss/欠落語/参考:候補表現+旧gloss/KP再生成)。
  - Family X: `<theme>/<level>/key_phrases/`。Family Z: `<run>/key_phrases/<level>/`(+`<run>/gloss_alignment_human_review_events.json`)。
- 停止: Family X=当該levelのKP segment全体(5rank分の英語/日本語/B1解説)が`STOPPED_GLOSS_ALIGNMENT_FAILED`(0 API call)、Gateがassemblyを拒否、本文・support・他levelは継続。Family Z=`stage_kp`が`FamilyZE2EStop`(stage単位)。
- **最終KPは短い候補へ戻していません。** 参考候補(display_phraseと旧gloss)は人間判断でのみ採用(KPを短くすると意味が失われる)。

## 解消(人間がglossを確定する)
1. 報告書.mdの「再生成候補」を読み、承認済みgloss規則(平易で自然・括弧禁止・算用数字禁止・`…`禁止・「～」は辞書的に自然な範囲で可)に沿うglossを決める。
2. 次を実行(記号違反なら書込まずに拒否される):
   ```
   .venv\Scripts\python.exe -c "import er003_key_words_gloss_alignment as ga; ga.resolve_gloss(r'<keywords_canonicalized.jsonのパス>', <rank>, '<確定gloss>', '<記録者>')"
   ```
   - パス: Family X=`<theme>/<level>/key_phrases/keywords_canonicalized.json`、Family Z=`<run>/key_phrases/<level>/keywords_canonicalized.json`。
   - 効果: `japanese_gloss`/`japanese_gloss_tts`を更新、`gloss_alignment_status=HUMAN_RESOLVED`、記録者・時刻・旧glossを`gloss_alignment_human_resolution`と`GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl`に記録。HR待ちでないitemは書き換えられない。
3. 該当rankすべてを解消したら、止まったstageを**同じコマンドで再実行**する。
   - Family X: `--stage tts`(必要なら続けて`--stage assemble`)。解消前に生成された「解説」等は存在しない(0 API callで保留されていた)。
   - Family Z: 同じ`--stage kp`(または`--stage all`)。**選定は再実行されない**(HR停止時に保存した`gloss_alignment_pending_result.json`を復元し、人間確定値入りの最新artifactを採用。再開後に`.consumed.json`へ改名)。解説(`kp_expl_b1b`)のsigにはglossが含まれるため、解説は人間確定glossを入力に生成される。
4. gloss解消ではなくKPを変えたい場合: 既存経路でKPを再生成する(Zは`--regenerate-stage kp_<level>`。この場合snapshotは使われず選定から再実行)。1レベル1回の運用上限(`--scaffold-only kp`のQ5(iv))に注意。

## 注意
- 解消済みのglossで解説(`kp_expl_b1b`)を既に生成していた場合(corrected以外の旧run由来など): sigが変わるため`ensure_stage`が`FamilyZProvenanceMismatchStop`で止まる。`--regenerate-stage kp_expl_b1b`を明示する(自動再生成しない)。
- 報告の書込/再読検証に失敗した場合は`GlossAlignmentNotificationError`でstageが停止する(「通知失敗だが継続」はしない)。
- 本機構はTrial専用。Productionで有効にするか(既定ON/OFF)、機械検査をgate化するかはユーザー判断(未承認)。
