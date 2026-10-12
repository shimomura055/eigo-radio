# GIT-SECRET-REPAIR-01 (COFFEE-MELOS-CLOSEOUT-AND-IMPROVEMENT-20261012-01 作業4)

2026-10-12 / 課金0 / 秘密の値は記録しない。

## 保護(作業開始時の記録)
- origin/main = 1ad64232。未push commit(古い順): cd3f86f8(39 files, 委任_10保全) -> 28a1e8e9(21 files, 委任_11本体)。他agentのcommitは作業開始時点で無し。
- 混入: cd3f86f8 内 er026_output/family_z_production_e2e_01/melos/evidence_10/dbg3_1791786050.log 764行目(env_value:SPEECH_KEY)。他のevidence_10/*.log・evidence_11/*は検出0。

## 実施
- 作業ツリー/indexは触らず、plumbing(一時index+commit-tree)で元tree(blob)から再作成。該当blobのみ `***REDACTED***` 置換。author/date/messageは踏襲+「(redacted re-commit)」。
- 再作成: cd3f86f8 -> e9e5d0a3, 28a1e8e9 -> 4dcd8b92 (初回に28a1e8e9側treeへ秘密が残っていたのを検出し再作成)。
- scan: `python tools/secret_scan_01.py --rev e9e5d0a3 4dcd8b92` -> scanned_files=60 hits=0。
- 再発防止: tools/secret_scan_01.py, er_secret_mask_01.py(+test), er026/er062/er063 mainでstream masking, .gitignore `**/evidence_*/**/*.log`, PM_GOVERNANCE 26-X。
- 注意: 既にtracked済みのevidence_*/*.logはgitignoreでは外れない(scan clean確認済み)。
