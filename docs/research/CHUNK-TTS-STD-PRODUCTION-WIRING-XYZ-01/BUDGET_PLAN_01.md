# BUDGET_PLAN_01 — Phase 2(runtime evidence)費用見積

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(2026-10-26)。**本委任の実費は JPY 0(API 0、遮断harness下で外部接続試行0)**。Phase 2は次委任で実行する。承認区分=C(7-7: 承認済みScope内・案件見積300円以下は自律実行可、日次1,000円内)。
当日(JST 2026-10-26)既使用約214円/残約786円(委任文より)。

## 単価の出典(出典のあるもののみ。推測単価は使わない)
| 項目 | 値 | 出典 |
|---|---|---|
| X Adv TTS(1記事・10 chunk) | 2.51〜2.64円/記事 | `CURRENT_SPEC.md:2946`(実測『英国の電車マナー』Adv TTS 2.51円) |
| Y TTS | 約2.92円/take | `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/` BUDGET_LOG_01(委任文経由の出典) |
| Z『告げ口心臓』Std+Adv全TTS+KP | 16.67円(上限目安) | `CURRENT_SPEC.md:2946` |

## 見積(上限側で算定。Stdは各chunkで減速後ASR再検証が加わるため、X/YのStd TTSは出典単価の2倍を上限とみなす保守側の仮定)
| 作業 | 内容 | 見積(円) | 備考 |
|---|---|---|---|
| X Std 1記事(3 part=最大10 chunk) | `--stage tts --only-segments full_story_part1..3`(KP等は再生成しない)+assemble(API 0) | ≤ 6 | 2.64円×2(Std ASR二重)。通算TTS3回の最悪ケースでも chunk分は ≤ 3×(chunk長/part長)で従来と同等 |
| Y Std 複数段落dev入力 1 segment | 2〜3 chunk | ≤ 9 | 2.92円×3 chunk |
| Y Adv 複数段落dev入力 1 segment | 2〜3 chunk | ≤ 9 | 同上 |
| Z Std narrator 1〜2 clip(次委任でZ実装後) | tell_tale 129/139語(各2 chunk) | ≤ 17 | 上限目安16.67円(全体)を超えない |
| 合計(上限) | | **≤ 41円** | 再実行1回分を見ても ≤ 82円 |

## Guardrail
- 案件見積の上限 100円(合計 ≤ 41円の約2.4倍の余裕)。**300円超見込みになったら実行せずFableへ報告**(7-7)。日次1,000円(JST)超過見込みも事前報告(7-9)。作業の分割/日付分割による境界回避はしない。
- 各runは`--budget-jpy`(X: 20、Y/Z: 各runner既定値以下)を明示し、`tools/stop_scope_check_01.py --managed-id CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 --run-dir <run> --out <json>` が rc=3なら新規API呼出をしない。TTSは`TTS_EXECUTION_MODE=STANDARD`を明示(T-2)。
- 再起動は委任文が許可した回数のみ。RESTART_STORM防止のためZの完成段は `--stages provision_shell,gate,assemble,pages,page_verify` を**1起動**(OPEN-480)。

## 量産単価70円/記事セットへの影響(目標3の評価)
追加LLM call 0。TTS総文字数・ASR総音声長はほぼ不変でcall数が増えるのみ(X Std 最大10 chunk)。Advの同構成(CURRENT_SPEC:2946)で追加費用は軽微(Adv TTS 2.51円/記事)。Stdで減速後ASR再検証がchunk数分に分かれる分の増分は、ASR課金が音声長比例のため限定的と見込むが、**実測はPhase 2で確定**する(本見積は上限仮定)。chunk単位の取り直しは再生成範囲を狭めるため、不具合時の再生成費用はむしろ下がる。
