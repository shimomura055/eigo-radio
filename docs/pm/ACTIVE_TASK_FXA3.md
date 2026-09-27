管理ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01(Stage 3b: Hormuz記事のruntime実行)
Status: 完了。scaffold/tts/assemble実行済み(¥120.66、Guardrail¥150以内)。
  所有runnerファイルの変更は不要だった(スラッシュ入りslugは既存
  derive_out_dir()でそのまま処理可能、事前dry-run確認済み)。
  A2/B1BともAudio Validation Gateがepisode assemblyをBLOCK(想定どおり)。
UDR-blocking: なし
UDR-deferred: なし
APPROVED未配線: なし
STOP条件: A2 full_story_part2/B1B full_story_part2/B1B kp2_japanese(rank2)
  の3件がHUMAN_REVIEW_REQUIRED(既存retry/cool-down/Local Rewrite全て
  exhausted)。テキスト書き換え・Gate回避は行っていない。選択肢(a)/(b)は
  REPORT.md §Stage 3b/4参照、Sonnet単独では選択・実装しない。
次アクション: Fable/ユーザーが3件STOPPEDの対応方針([a]再生成 or [b]人手
  Human Review Lock承認)を判断
未回答報告: なし
報告単位Status: Stage 3b Hormuz=REPORTED(詳細はRESULT_PACKET_FXA3.md/
  REPORT.md §Stage 3b)

## 入力
- article: er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/{a2,b1b}/article.md
- runner: er019_family_x_audio_production_runner_01.py(所有ファイル、変更なし)
- 費用Guardrail: ¥150(実績¥120.66)
- 出力: er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/
