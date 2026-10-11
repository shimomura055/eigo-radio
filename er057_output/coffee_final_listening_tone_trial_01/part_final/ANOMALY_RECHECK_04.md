# ANOMALY_RECHECK_04(委任_04、無料ローカル解析のみ・API不使用・検知器/閾値不変)
対象: Advanced新完成版(`final_04/Coffee_Advanced_final_v2.wav`)と新規K2 KP英語5件(`kp_adv_k2/`)。Standardと他segmentは音声不変のため委任_03の`ANOMALY_RECHECK_03.md`が有効。生データ`anomaly_recheck_04.json`、script `er057_tone_trial_final_recheck_04.py`(既存検知器`er057_audio_anomaly_detect_trial_01`を無改変で使用)。
- 新K2 KP英語5件(segment単体): 候補**0件**(全5件)。
- Advanced完成版assembled: 委任_03の候補17件(うち固定音源含む)→新18件。差分は**1件のみ新規: Key Phrase 2(price tag) ブロック内 3.055秒 `spec_jump` low(flux_z 8.1)**。委任_03の候補は全て新版にも残存(消失0)。
- **新規medium以上の候補: 0件**(KP部・全編とも)。自動検知のみを根拠とする再生成は行っていない(low候補1件はユーザー試聴での確認事項として記録)。
- clip(音割れ) 0件、headroom安全弁 未発動(peak 0.95935<=0.98)、内部1秒超の無音は KP4 内 1.02秒のみ(KP block内の既定pause帯。委任_03版はKP1 1.04・KP2 1.03・KP4 1.03秒)。QAは`qa_04.json`。
- assembler回帰: assembler(`er019` run純関数+`er003` assemble)・Standard音声は委任_03から不変のため、委任_03の`regression_check_03.json`(既存音声のみ組立=既存完成版とbyte-identical再確認)を再利用(指示14-6、新規回帰は未実施)。Advanced再組立は、KP 5 roleのsha以外が全て委任_03と一致(`adv_provenance_diff_04.json`)。
