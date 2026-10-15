# KP_GLOSS_ALIGNMENT_HR_RESOLVE_01: gloss再整合Human Review待ちの解消手順(現行・1ページ)

現行化: KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_02(2026-10-15、OF-KGCPW-14)。原本(履歴)=`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/HR_RESOLVE_PROCEDURE_01.md`(Trial専用時点の記述。変更しない)。

対象: Production(Family X/Z、Standard/Advanced)でKP日本語glossの再整合(修正版・既定ON)がitem単位2回失敗し、`gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED`(旧版が書いた`FAILED`も同様に扱う)になったKey Phrase。Human Review Lock・`human_review_queue.jsonl`は使わない(音声HR統計を汚さない)。

## 前提(運用)
- 既定ON。kill switchは**プロセス環境変数`EIGO_KP_GLOSS_ALIGNMENT=0|false|off|no`のみ**(import時に1回評価。`.env`経由は保証しない)。OFFは承認済み仕様の無効化であり、起動時に`[GLOSS-ALIGN][WARN] DISABLED ...`が出る。実効値(ON/OFFと取得元)はX/Zともrun開始時のstdout・summary(X: `scaffold_run_summary.json`/`entry_point.json`、Z: `gloss_alignment_flag.json`)に記録される。
- Xのrc: 最終的にいずれかのlevelにHR未解決が残るとrc=2。Zは`FamilyZE2EStop`でrc=2。

## 何が起きているか
- 報告書: `<KP段出力dir>/GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json`(+`.md`)。必須項目=article/level/rank・最終英語KP・現在gloss・失敗理由・全attempt結果・再生成候補(提案gloss/欠落語/参考:候補表現+旧gloss/KP再生成)。
  - Family X: `<theme>/<level>/key_phrases/`。Family Z: `<run>/key_phrases/<level>/`(+`<run>/gloss_alignment_human_review_events.json`)。
- 停止: Family X=当該levelのKP segment全体(5rank分の英語/日本語/B1解説)が`STOPPED_GLOSS_ALIGNMENT_FAILED`(0 API call)、Gateがassemblyを拒否、`--level both`では健全なlevelのassembleは続行しHR levelは`EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT`として記録。Family Z=`stage_kp`が`FamilyZE2EStop`(stage単位)。HR停止時にもKP assetsは(HR状態のまま)配備されるため、`--stage tts_*`単独起動でも通過しない。
- **最終KPは短い候補へ戻していません。** 参考候補(display_phraseと旧gloss)は人間判断でのみ採用(KPを短くすると意味が失われる)。
- 「ON化前・未評価」停止: gloss再整合の対象(KPが候補より語を足したitem)なのに`gloss_alignment_status`が無いKP成果物(再整合工程の導入前に作られたもの)は、再利用時に停止する(対象0件の成果物は通過)。停止理由に`--regenerate-stage kp_<lv>`(Z)/KP成果物削除後に再生成(X)を要求する旨が出る。これはHRではなく再生成で解消する。

## 解消(人間がglossを確定する)
1. 報告書.mdの「再生成候補」を読み、承認済みgloss規則(平易で自然・括弧禁止・算用数字禁止・`…`禁止・「～」は辞書的に自然な範囲で可)に沿うglossを決める。
2. 次を実行(記号違反なら書込まずに拒否される):
   ```
   .venv\Scripts\python.exe -c "import er003_key_words_gloss_alignment as ga; ga.resolve_gloss(r'<keywords_canonicalized.jsonのパス>', <rank>, '<確定gloss>', '<記録者>')"
   ```
   - パス: Family X=`<theme>/<level>/key_phrases/keywords_canonicalized.json`、Family Z=`<run>/key_phrases/<level>/keywords_canonicalized.json`(Zは配備済みの`<run>/<level>/key_phrases/keywords_canonicalized.json`も、次のstage_kp再実行で最新に更新される)。
   - 効果: `japanese_gloss`/`japanese_gloss_tts`を更新、`gloss_alignment_status=HUMAN_RESOLVED`、記録者・時刻・旧glossを`gloss_alignment_human_resolution`と`GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl`に記録。HR待ちでないitemは書き換えられない。旧版の`FAILED`も解消対象。
3. 該当rankすべてを解消したら、止まったstageを**同じコマンドで再実行**する。
   - Family X: `--stage tts`(必要なら続けて`--stage assemble`)。最終stdoutの`[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL]`行は、artifactのHR未解決が無くなれば出なくなる(報告書ファイルは履歴として残る)。
   - Family Z: 同じ`--stage kp`(または`--stage all`)。**選定は再実行されない**(HR停止時に保存した`gloss_alignment_pending_result.json`を復元し、人間確定値入りの最新artifactを採用。再開後に`.consumed.json`へ改名)。`--regenerate-stage kp_<lv>`を付けて再実行しても、未消費のsnapshotがあれば優先して復元される(人間の確定値を捨てて選定をやり直さない)。解説(`kp_expl_b1b`)のsigにはgloss再整合のstatusを持つitemがあればglossが含まれるため、解説は人間確定glossを入力に生成される。
4. gloss解消ではなくKPを変えたい場合: 既存経路でKPを再生成する(Zは未消費snapshot(`gloss_alignment_pending_result.json`)を削除したうえで`--regenerate-stage kp_<level>`。選定から再実行)。1レベル1回の運用上限(`--scaffold-only kp`のQ5(iv))に注意。

## 注意
- 解消済みのglossで解説(`kp_expl_b1b`)を既に生成していた場合: sigが変わるため`ensure_stage`が`FamilyZProvenanceMismatchStop`で止まる。`--regenerate-stage kp_expl_b1b`を明示する(自動再生成しない)。Xの解説text cacheは、statusを持つartifactではgloss/key_phraseが前回と一致するときだけ再利用される。
- 報告の書込/再読検証に失敗した場合は`GlossAlignmentNotificationError`でstageが停止する(「通知失敗だが継続」はしない)。
- 完成禁止の保証(HR時にTTS/assemble/ページへ進まない)はFamily X/Zのみ。A/B/C等のその他の呼出元は既定ONで再整合は走るが、消費側の関所は無い(HR時は旧glossのまま完成しうる=従来と同じ。SSOTに明記)。
