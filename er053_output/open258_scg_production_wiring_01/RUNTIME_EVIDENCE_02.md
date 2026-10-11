# RUNTIME_EVIDENCE_02 (委任_03、C2/推奨4実装後の最小再確認)

実行日: 2026-10-11 / worktree `C:/Users/tensh/eigo-radio-scg` / script `runtime_scg_02.py`(`runtime_scg_01.py`と同一、証跡出力先と累計算出のみ変更) / 生証跡 `runtime_evidence_02.jsonl`。実Primary(OpenAI `gpt-4o-mini-transcribe`、既存Production Primary route固定=本番ライン評価のため最新世代原則の意図的例外)+実Azure Speech STT(japanwest)、Production関数`evaluate_attempt_ja_with_cascade_detail`を保存済みMETA attempt1 wavへ実呼出。新規TTS 0。費用は登録単価換算の見積。

| case | 結果 | 費用(円) |
|---|---|---|
| a(META wav、Production関数) | 4回実行中2回でPrimaryが「出現」(TCM)->SCG発火->Secondary「出演」->`SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`(PASS維持)。残り2回はPrimaryが「出演」と正しく転写(SCG不発火、根拠に数えない) | 0.46 x2 + 0.049 x2 |
| e(kill switch JA_SCG_ENABLED=0) | 5回実行(1回はPrimary正答で不再現)のうち4回で、Primary「出現」(TCM)->scg_result=DISABLED_BY_FLAG・Azure 0回・verified=False(従来動作)を4回確認 | 0.149 x4 + 0.049 x1 |

本委任の見積合計 約1.66円。累計(委任_02の2.64円+本委任)約4.30円/予算5円(超過なし)。注: Primary ASRは実行ごとに結果が揺れるため再実行が発生し、目標の約0.6円を超えた(eの4回実行は不要な重複だった)。
同形異音語NGを示す保存済み音声はなく、C2の同形異音語・推奨4の否定は fixture/mock(Phase 0 fixture回帰+新規17test)のみで確認(新規TTSは禁止のため)。
