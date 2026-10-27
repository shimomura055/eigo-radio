# VERIFY_04 — 完成版の受入材料(委任_06)
run=`er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`、公開=`user_test/family_y_production_redelivery_fee_03/`。
| 項目 | 結果 | 根拠 |
|---|---|---|
| Style Gate | Std PASS(18/18評価、欠落0)・Adv PASS(15/15) | `gate_summary.json`。`y_profile_blocked`=[]、`x_gate_blocked_after_filter`=[] |
| Style実測=承認 | 全件 `match=true`、profile `fx_20261017` | `a2/audit/style_actual_vs_approved.json`(rows 18, all_match)、`b1b/...`(rows 15, all_match)。Y_ROLE_COVERAGE完全一致 |
| Audio Validation | 全segment status OK(非OKなし) | `{a2,b1b}/audit/tts_generation_results.json` |
| クリッピング | Std peak 0.9701 / Adv peak 0.9231、clip(>=0.999)0サンプル。headroom安全弁 未発動 | `*/audit/headroom_report.json`、wav実測 |
| 長い無音 | 最長 Std 1.59s / Adv 1.46s(段落境界等)、異常長停止なし | wav実測(振幅<0.003の連続) |
| 通し音声 | Std 337.21s / Adv 314.88s。`std_full.mp3`=337.21s・`adv_full.mp3`=314.88s(wavと一致) | soundfile実測 |
| timeline | Std 47要素(Intro 0.0s〜Outro 331.07+6.14=337.21s)、Adv 43要素(〜314.88s)。末尾と総尺が一致 | `*/audit/timeline.json` |
| Adv Comment 2 | なし(timeline内0件、`removed_by_spec`維持) | timeline実測 |
| 原稿 | 26個の台本ブロック(Std+Adv計)が`_02`完成版と**完全同一**(空白・停止マーカー除去後) | 機械比較。closing_record final_sha256 `26745165…`(案B固定) |
| Key Phrase・訳・学習内容 | `_02`と同一(本文以外の差分は秒数・停止マーカーのみ) | ページ本文diff。KP source gate 3/3 PASS |
| Voice表 | Voice 1=Puck / 2=Zephyr / 3=Schedar、ナレーター=Aoede(Std)・Charon(Adv解説)。`voice_assignment.json` match=true | `run/voice_assignment.json`、results実測。`_02`(run_voice_puck_ev_01)と同一 |
| preview(Std) | HR PASS(ユーザー承認、take 1、sha `ac3f7467…`) | `HR_APPROVAL_STD_PREVIEW_01.md` |
| page_verify | ok=true、違反0 | `page_verify_local.json`、`_03`上で`evaluate_page_verify`再実行=[] |
| 長い停止マーカー | ≥700msの検出: Std/Adv計18件(旧`_02`は33件。Style適用で減少) | ページ表示 |
| 費用 | 0円(spent 32.0908不変) | `COST_03.md` |
