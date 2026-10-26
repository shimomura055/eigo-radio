# OPUS_REVIEW_REQUEST_01 — 条件A: Standard(6%減速)×Chunk分割(+0.2秒)の合成(新しい処理フロー)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(2026-10-26)。read-only・API 0のレビューを依頼する。**Fable起動用の依頼文**(本委任はOpusを起動していない)。
同内容の再レビューは不要(11-3)。前回の `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md`(M1〜M4・I1〜I11・R1〜R4)で解決済みの論点は再掲しない。新規なのは『Stdの6%減速との合成』だけ。

## 実装状況(レビュー対象は設計+実装済みdiff)
本委任は委任文の条件(合成方式が『chunkごとに既存の減速処理をそのまま適用→0.2秒挿入→連結』で新規後処理・閾値なし)を満たしたため実装済み。**実装前待ちではなく、実装後レビュー**として依頼する(内容が変わらなければ再利用可)。差分: `er117_chunk_tts_production_01.py`(Std用helperの追加のみ、plannerは無変更)、`er019_family_x_audio_production_runner_01.py`(X Std)、`er121_family_y_structure_01.py`/`er121_family_y_audio_01.py`(Y Std)、test。Z(`er063`)は未実装(設計=`DESIGN_01.md`§6)。

## 読むべきもの
1. `DESIGN_01.md`(特に§2合成方式、§3既存減速検証のchunk成立根拠、§4 Gate、§6 Z設計、§8一貫性)
2. `SPEC_LEDGER_01.md`(要求項目と旧『Std除外』test撤去の一覧)
3. `FIX_01.md`(差分要約、test結果、clean worktree前後比較)
4. コード: `er117_chunk_tts_production_01.py` の `std_chunk_slowdown_violations`/`std_parent_slowdown_fields`/`drop_cached_std_chunks_without_slowdown`/`attach_chunk_meta(level=)`、`er019…` の `_generate_x_body_part_chunked_a2`/`_x_std_chunk_slowdown_blocked`/`generate_family_x_a2_segments`/`load_family_x_a2_sources`/`apply_family_x_a2_gain`/`stage_assemble_family_x_a2`、`er121…audio` の `_generate_y_body_segment_chunked_a2`/`generate_y_a2_segments`/`check_std_slowdown`/`_load_y_body_chunks`

## 重点確認してほしい論点
1. **合成方式の妥当性**: 『chunkごとに既存の減速→減速後のchunk wavを減速対象外の4800サンプル無音で連結』。連結後減速を採らない根拠(合成長検査の不成立、ゼロ連続長4569≠4800)は十分か。Stdのmargin(各側0.16〜0.35秒)が減速で約6%伸びるため、可聴ポーズはAdvより境界あたり約0.02〜0.04秒長い。この差を仕様内(追加ポーズ=0.2秒の承認)として許容してよいか、Phase 2で何を実測すべきか。
2. **Gateの穴と補い方**: 共有Gate `_segment_missing_mandatory_a2_slowdown` は chunk idを対象外(`A2_SLOWDOWN_TARGET_SEGMENTS`に無い)かつ親は`slowdown_applied`を持たず誤ブロックされる。共有moduleを変更せず、(a)親に『全chunk減速済みのときだけTrue』の集約値を持たせ (b)X組立前Gate/Y style gateでchunk単位の減速証跡を追加検査、とした。この集約が『親が減速済みと偽る』抜け道にならないか(親wav=減速後chunkの生連結を`verify_raw_parent`が整数サンプルで保証する前提)。人間承認で減速欠落を迂回できない設計は適切か。
3. **retry/resume/regeneration**: chunkごとに通算TTS3回(`generate_a2_segment_with_slowdown`無変更)。減速証跡のないcache chunkを再利用しない(`drop_cached_std_chunks_without_slowdown`)。Y用のchunk id判定は`is_chunk_id`引数で渡す(er117の`parse_chunk_id`はYのidを知らない)。legacy Std結果(親のみ)の従来経路維持(`effective_plan`、Xのみ。Yは1段落契約で該当なし)。穴はないか。
4. **Adv不変**: goldenは実装前HEAD(bb578265c)で凍結(X Adv run 2件・Y Adv run 2件)。`CHUNK_PLANNER_VERSION`を上げていない。`attach_chunk_meta`/`evidence_record`のAdv出力が従来とバイト同一であるtestで十分か。X Std追加でAdv関数のソースに触れていない確認方法の妥当性。
5. **Yの不発火の扱い**: Y本文は各Voice 1段落のため、Std/Advとも実記事では分割0。ユーザー原文は『文境界分割や本文契約の変更を追加承認したものではない』。本実装は新規則なし。複数段落入力でのみ発火することをtest(合成入力)で示し、正式runtimeは次委任とした。これが原文の要求(発火検証+不発火の事実記録)を満たす計画か。
6. **Z次委任との整合**: `er117.plan_z_clip`の`level != "b1b"`と`er063:598`の`level == "b1b"`は同時に撤去、`verify_std_english_slowdown`のchunk id除外(`_CLIP_ID_RE`)の拡張、`slowdown_applied: None`の親表示の集約化(DESIGN §6)。見落としはないか。原文『約70語を目安』と実装閾値100語(k=ceil(語数/100))の関係の再照合が必要か。
7. **旧『Std除外』を期待値に固定していたtestの撤去**(SPEC_LEDGER §4)が、Z Stdの固定test(`er117_z_chunk_wiring_test_01.py:130-132,202`、本委任では維持)と矛盾しないか。

## 回答形式(前回と同じ)
判定(承認/条件付き/差戻し)+実装前後に必須の修正(M番号)+推奨(R番号)+ユーザー判断が必要な事項の有無(承認済み仕様の範囲で収まるか)。
