# CLASSIFICATION_01
## B区分(個別判断が必要・今回未削除)
| # | 対象 | 容量 | 用途/リスク | 代替保管 |
|---|---|---|---|---|
| 1 | scratchpad配下の完了済git worktree(wt_* 十数個, 各約3GB, 推定計約28GB〜) | 約28GB | 追跡ファイルのcheckout。wt_cap/wt_fix1/wt_fix2は未push/使用中。完了・push済のものは`git worktree remove`で回収可(委任_02でFable個別承認予定) | origin/main push済なら不要 |
| 2 | hibernate(hiberfil.sys) | 6.6GB | `powercfg /h off`で回収、管理者権限・OS設定 | - |
| 3 | .cache(HuggingFace等) | 2.4GB | モデル再DLコスト | 再DL |
| 4 | ms-playwright | 1.39GB | 再DL可だがテスト影響 | 再DL |
| 5 | er0*_output中間wav(assembled等) | er019 7.3 / er121 4.0 / er026 8.8GB等 | 証跡・再開用の可能性、Git管理下含む | 外部媒体へ退避 |
| 6 | .claude/projects(会話履歴) | 3.7GB | 履歴 | - |
| 7 | Temp 非claude(baseline_repo 0.6GB, b8_pages 0.4GB, tmp* 147MB×9等) | 約2GB | 作成元不明、7日以内/他タスク可能性 | - |
## C区分(削除禁止)
mfa_tool 13.7GB / er*_output(Production・Trial成果) / 音声Store(er006_output/master_audio_store_01) / SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS) / .git 2.5GB / .venv / pagefile 26.8GB / Windows\Installer 3.7GB / 進行中worktree(wt_cap, wt_fix1, wt_fix2)。
