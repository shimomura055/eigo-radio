# 委任_A1 OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02: Phase A(P2のNote転記修正)+Phase B(E2E N=10実行)。上限¥300。

## 管理ID
OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02(A1)。DEV runnerの転記規則を「notes内容全体」へ最小修正し、5テーマ×2rep。

## 性質/到達上限Status/禁止事項
DEV修正+Trial実行(有料)。評価・SSOT・Closeoutは別委任。Production/Checker構成/Note文言変更なし。

E-1: 上限¥300、¥250超見込みでSTOP。
D-1: er052_output/open233_allfact_note_e2e_02/cost.json にrun別・phase別記録。
G-1: Trial限定。
F-1: fail-closed。

## 事前指定Read一覧
nb DEV runner、test_nb_dev_01.py、前Trial(ALLFACT-NOTE-ENT-01)の台帳生成script、phase2_readme。
読込のみで実装前提を確認した。

## 事前指定Grep一覧+追記位置・更新位置の手順
Grepは不使用(runner/検証scriptの直接確認のみ)。SSOT追記は本委任の範囲外(別委任)。

## 実行コマンド全文
`bash er052_output/open233_allfact_note_e2e_02/tools/launch.sh meta 1 phase1 8`(phase1/phase2、全10run同形式)、driver.sh、gen_ledgers.py、check_brief_transfer.py、build_manifest.py。
コマンド詳細は runs/manifest.json の各runに記録。

## SSOT追記文
なし(本委任でSSOT編集せず。評価後の別委任で追記)。
詳細証跡は er052_output/open233_allfact_note_e2e_02/ 配下。

## Git
Phase A checkpoint 1fefd10f のみpush。Phase B成果物は未commit(評価後の別委任)。
個別add、git add -A不使用。

## 報告
docs/pm/RESULT_PACKET.md に要約。manifestは er052_output/open233_allfact_note_e2e_02/runs/manifest.json。
