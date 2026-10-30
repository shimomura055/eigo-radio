# RESULT_PACKET ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_04 (2026-10-30)
結果: Z生成訳不成立2part(メロスadv_14 25文/雪女std_11 18文)の是正コード完了・scratch copyで2part訳完成(coverage 1.0)。公開dirは未変更(競合制約により再produceは本委任外)。費用約¥0.17/Cap¥8。
(1) 既存仕様整合: INTEGRATION_03_01.md:15「部分jaは作らない」維持。§5「緩和は検査の精緻化」=照合基準・Prompt・閾値は不変(retry追加のみ)。er135_enduser_translate_01.py MAX_VERIFY_ROUNDS・RETRY_NOTE_VERIFY_HINT。
(2) 未承認機能の既定値: 新機能なし。既存の承認済みGate(対訳照合)の前にretry1回を足しただけ(既存retry/RETRY_NOTE方式と同型)。照合迂回なし。
(3) 失敗終了時の成果物: 再照合もNGなら従来どおり当該partは英語のみ(null、非キャッシュ)=現行公開dirと同じ。成果物=docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/EVIDENCE_04.md、evidence_04/。目的適合: 訳の表示/ハイライトを未完了のまま放置しない要求に対し、コード是正+新訳(delta)は用意済み、公開反映のみ未実施(Fable判断で委任_02後)。
(4) 撤去/残置: 撤去なし。Grep: `verify_ng` は er135_enduser_translate_01.py に残置(判定自体は不変)。
判定整合: 重大NG=なし
診断: 旧NGは真のNG(英文に無い具体化。偽NGではない)。原因=照合NG段落を再翻訳しない設計。詳細はEVIDENCE_04.md。
## 公開反映手順(委任_02完了後。他workerのer135_enduser_page*/assets/user_testの変更が確定してから)
1. 対象: `user_test/family_z_melos_kphr_evidence_r3`(Adv adv_14)、`user_test/family_z_yuki_onna_01`(Std std_11)。
2. 各produceのcache_dir(`er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3/enduser_sync_cache/`、`.../yuki_onna/run_yo_prod_01/enduser_sync_cache/`)の `ja_generated.json` の `entries` に、`evidence_04/ja_generated_delta_{melos,yuki}.json` の entries を追記(キーは英語文sha=衝突なし。既存entryは変更しない)。この方式ならproduceはAPI 0(ASR・埋め込みもcache命中)。あるいはdeltaを使わず、修正済みコードでproduceすればretry付きで未命中1段落のみ約¥0.1生成。
3. 再produce(正式CLI、既存の同引数。Z 2dirのみ)。完了後 `tools/ejh03b_diff_gate_01.py <2dir>` で承認済み訳・英文不変を確認、`build_info.generated_translation.failures==[]`、`translation_coverage` story translated==blocks、`verify_consistency`PASS、liveで当該partに`.tr`/`.jhl`が出ること。
