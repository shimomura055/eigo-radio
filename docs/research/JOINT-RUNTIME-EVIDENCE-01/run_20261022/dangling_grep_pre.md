# 合同runtime evidence 集計(er106)
- schema: `er106_joint_runtime_evidence_01/v1` / generated_at: 2026-10-22T17:25:08
- X run: `None` / Z run: `None`
- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO

## Family X: `None` (levels=None)
- run dirが存在しない

## Family Z: `None` (levels=None)
- run dirが存在しない

## (e) STOP・HR・共有log
- STOPセンチネル(現在): ['C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md']
- 前後差分: snapshot未指定
- Ledger対象語照合: {}

## Dangling Reference grep(Production .py、testは別掲)
- KPFT: db_hybrid経路: production=0 test=0 []
- KPFT: m2_fallback: production=0 test=2 []
- KPFT: KP_ARTICLE_COST_CAP: production=0 test=0 []
- KP3V: 旧dual識別子(撤去対象): production=22 test=3 ['er078_asr_unified_judge_01.py:27', 'er096_kp_dual_pass_01.py:5', 'er096_kp_dual_pass_01.py:12', 'er096_kp_dual_pass_01.py:14', 'er096_kp_dual_pass_01.py:16', 'er096_kp_dual_pass_01.py:18', 'er096_kp_dual_pass_01.py:22', 'er096_kp_dual_pass_01.py:38']
- KP3V: 維持する容器名/telemetry名(情報。0件でなくてよい): production=39 test=4 ['er019_family_x_audio_production_runner_01.py:767', 'er019_family_x_audio_production_runner_01.py:771', 'er019_family_x_audio_production_runner_01.py:772', 'er063_family_z_audio_01.py:747', 'er063_family_z_audio_01.py:751', 'er063_family_z_audio_01.py:752', 'er063_family_z_audio_01.py:1022', 'er063_family_z_audio_01.py:1023']

## KPFT(KP全文選定+3件化) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KPFT-ALL | MISSING | MISSING | X run dirが存在しない / Z run dirが存在しない |

## KP3V(3-ASR多数決) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KP3V-ALL | MISSING | MISSING | X run dirが存在しない / Z run dirが存在しない |
| KP3V-J Whisper正式runtime発火(X/Zいずれか) | (合同) | (合同) | NOT_FIRED: X=False Z=False。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06) |

## PNAP(固有名詞アラーム) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| PNAP-ALL | MISSING | MISSING | X run dirが存在しない / Z run dirが存在しない |
| PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9) | (合同) | (合同) | NOT_FIRED: alarms X=None Z=None |

## 総括
- KPFT: {'MISSING': 2}
- KP3V: {'MISSING': 2, 'NOT_FIRED': 1}
- PNAP: {'MISSING': 2, 'NOT_FIRED': 1}
