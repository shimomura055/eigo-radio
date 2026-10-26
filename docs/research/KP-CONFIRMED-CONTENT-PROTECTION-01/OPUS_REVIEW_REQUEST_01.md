# OPUS_REVIEW_REQUEST_01: 独立技術レビュー依頼(条件A=新しい横断契約の設計)

管理ID: KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01。対象設計: `DESIGN_01.md`(確定レコード+fail-closed Gate)。根拠事実: `CURRENT_FLOW_01.md`・`RISK_MAP_01.md`。計画: `TEST_PLAN_01.md`・`EVIDENCE_PLAN_01.md`。承認根拠: `docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md:16-29,37-41`。API 0・コード未編集の設計段階。Opus台帳(`docs/pm/OPUS_FINDINGS_LEDGER.md`)へ指摘の追記・Fable採否の記録を要する(11-5)。

## 観点(各項に「採用/修正/不採用+理由」で回答してほしい)
1. **確定レコードの正本性**: 正本=`<kp_dir>/confirmed_selection.json`+ミラー=`<run>/<lv>/audit/`の二重化は妥当か(片方だけの改変検出 vs 二重管理の複雑さ)。`kp_human_review.json`(状態機械)との責務分離(レコード=凍結値、review=状態/NG/履歴)に重複・矛盾はないか。`content_sha256`の対象(protected)と除外(reference/comment)の線引き。
2. **fail-closed Gateの位置**: G1を`require_final_consistent`末尾(全consumer入口)へ1箇所追加する案で、TTS/Gate/assemble/pages/Part 1/Part 2の前に必ず通るか。見落としている消費者(`part1_items`直呼び、`--stage tts_*`単独起動、Y/Zのassets copy直読み)はないか。違反を例外サブクラス(`KpReviewInconsistent`派生)で送出し既存のrc=3 STOPに乗せる方式の副作用。待機(rc=4)扱いにすべき種別はあるか。
3. **INTEGRITY_VIOLATIONとCONFIRMED_CONTENT_ISSUEの分離**: 「artifact<レコードのずれ=AIがレコード値へ復元してよい(明示コマンド)」「確定内容の品質問題=黙って直さず修正案提示+ユーザー再確認」の線引きは、USER_02「黙って変更せず、修正案を提示して再確認」に照らして正しいか。`confirm-restore`をAI単独で実行してよいか。
4. **救済(er125)・補完・再選定・gloss再整合との優先順位**: 確定後これらを呼ばない(候補生成内のみ)事実(R-12〜R-14)の確認。再生成が必要な経路(STALE/revoke)で確定itemを`pinned`入力にする案(`generate_fn`の`pinned_items`)は、外側retry・候補全体置換(`kcand:355-362`)・Redundancy QAと整合するか。`protect_on_stale`で「全表現が新本文で逐語一致なら再バインド」とする基準(既存validatorの再利用)は十分か。
5. **LRとハイライトの整合**: KP segmentのLR非適用(`er020:128-130`)に頼る設計と、本文narration側のLRが確定KPの出現位置を変え得る点(書面不変・音声のみ)。警告記録のみ(BLOCKしない)で足りるか、LR候補選定に保護spanを足すべきか(LR承認仕様への影響、tighten-onlyでも仕様変更に当たるか)。将来の本文ハイライト(③)の入力契約と`unresolved`の扱い。
6. **resume・regenerateの読み戻し**: 旧candidates doc/reviewの読戻しと確定レコードの不一致(shaずれ)をINTEGRITY扱いとする判断。`finalize_kp`のidempotent(署名一致で再書込しない)とG0の関係。`--regenerate-stage`の各Family差(Y/Zのみ、Xは該当なし)の取りこぼし。
7. **Part 2(文法)の解説凍結**: 確定時点で`explanation_md`全文を保存し`finalize_stage`が生成せず採用する案。HR CLI経路(ユーザー未閲覧の生成後凍結)とフォーム経路(ユーザー閲覧済み)の区別(`explanation_source`)、`explain_signature`の`frozen:`分岐、`ref_ja`不一致を再生成でなくISSUEにする扱い。prompt/model更新は既存確定へ遡及しない契約。
8. **A/B/C不変・現行HR CLI互換**: 新moduleのisolation(`er119_isolation_test_01.py ALLOWED`追加)、flag既定ON(承認済み仕様)+kill switchの扱いの妥当性(「未承認機能は既定OFF」原則との整合: 本件は承認済み追加指示)、HR CLI経路(select/AUTO/declare-absent)でも同じ保護が効くことと、AUTOの`auto_declared`を「ユーザー確定でない」とする区別。旧run互換(review/レコード無し=no-op)。
9. **evidence十分性**: `EVIDENCE_PLAN_01`(Family別1記事ずつ、変更試行BLOCK+正常系実走+resume/regenerate/STALE+Part 2凍結、<=¥10/Family)でPRODUCTION_WIRED受入に十分か。不足する検証(例: 公開URL版ページ、フォーム->取込->後続の通しE2E)はあるか。
10. **未消費区分の扱い(R-25〜27)**: ③・Stdの②/③・文法2件目を`unconsumed[]`に保存し黙って捨てない設計は、USER_02「ユーザーが確定した区分を勝手に変更しない」と整合するか。消費側拡張は別判断としてよいか。

## 事実として確認済み(再調査不要、`CURRENT_FLOW_01.md`/`RISK_MAP_01.md`参照)
- 現行の整合検査はcandidate_id集合のみ(`require_final_consistent:1044`)で内容(訳)は未比較(R-06)。
- Z `_gloss_person_gate:1882`が確定後に訳を上書きし得る(R-01)、STALEで確定が消える(R-03)、Part 2解説は確定後生成でprompt/model/ref_jaで再生成され得る(R-09)。
- 救済/補完/gloss再整合は候補生成内で確定後に呼ばれない(R-12〜14)。KP segmentはLR非対象。

## 期待する回答形式
各観点の採否、重大/中/軽の所見、実装時の必須修正、追加すべきtest。Fableは照合のうえ11-3に従い次工程へ進む(Opusレビュー自体はユーザー承認Gateではない。Production採用は人間ユーザーのみ)。
