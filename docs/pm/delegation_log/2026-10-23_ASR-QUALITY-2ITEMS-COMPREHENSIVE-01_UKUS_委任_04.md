FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-UKUS-委任_04-PRODUCTION-IMPL-20261023

# 委任_04(②UKUS): Opus条件Cレビュー(必須OF-UKUS-W-01〜04、推奨05〜10)を反映してProduction実装→test/回帰→X runtime evidence。Z evidence(c12 speciality再生成)は後続のB工程委任で取得(本委任ではZ実行しない)。APPROVED_FOR_PRODUCTION(UDR #168)に基づく正式実装。費用上限10円(X evidence)。

## 前提読込
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/{WIRING_DESIGN_01,DESIGN_02,TRIAL_RESULT_01,OPUS_REVIEW_01}.md`、`docs/pm/RESULT_PACKET_ASRQ_UKUS3.md`、受入条件=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` §2。Trial実装 `er111_ukus_*`。

## T-0・Git運用(厳守)
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_UKUS_委任_04.md`(index 371以降、先頭MARKER一致)。
2. **Opusレビュー本文を保存**: 下記所見を `UKUS/OPUS_REVIEW_02_COND_C.md`(Fable転記と明記)。
3. ACTIVE_TASK自分の行のみ(並行: ①RET実装[er103系+er078_reuse_value_guard :51-57直後+er019継承 :347-390+allowlist]、FX-KP 委任_05、FAMILY-Y 委任_08[有料run中の可能性])。**pythonプロセスは自分が起動したPIDのみ終了可、イメージ名一括kill禁止。commitは `git commit --only -- <path…>` でpath限定、直前に `git diff --cached --name-status` で意図しないD/Aが無いことを確認。一時index/commit-tree禁止。共有ファイル(er078/er019/allowlist/SSOT)は編集直前に最新化→自分のhunkのみ→即commit→push。競合時はrebaseせずFableへ報告。TTS実行前に他行「有料run(TTS)進行中」を確認・待機。**

## Fable判定(記録用)
Opus総合判定=「必須修正4点を反映すれば実装可、再設計不要」。一致: 統合点1か所、hook変更不要、RET表非参照、flag設計、対表git mv+sha照合、Trial撤去順序、LAYER_VERSION扱い。対立点4(同等性検証の網羅sweep/c12は `reuse_blocked` 印+checkpoint・provenance考慮/`ukus_contributed` の検出範囲とキー/Xは陽性証拠を取る)は検証・安全の技術修正→**Fable判断で実装へ進む**。PRODUCTION_WIREDはFable受入後(X/Z双方のevidence必須)。T-K(両層ON相互作用test)は①②の後からcommitする側の必須test+B工程前のFable受入項目。

## Opus所見(逐語要約)
- W-01[必須] 同等性差分testの強化: 保存6,137行のNG→PASSはc12のみ、合成27件では救済経路を検査できない。構造差(span粒度: Trialは合格同数語spanも位置別分解、Production案は不合格spanのみ/rules: contraction含むn:n span同居時)。修正: (1)Trial撤去前に全active 6,361対を両方向で文に埋め込んだ網羅sweep(API 0)でTrial⇔Production比較。文型=文頭/文中小文字/文頭+次語大文字/所有格・複数・ハイフン複合/v1救済spanが前後に同居/数・否定spanとの同居/n:n複数位置混在/CMU未登録位置(jewellery型)/`_canon_entity_flags` 長さ不一致、`er111_ukus_trial_eval_01.py` のcase生成流用 (2)比較項目固定: `equivalent`・`reason`・`warnings`(集合)・`ukus_pairs` 完全一致、`rules` は集合比較し差分は全件列挙・分類保存、`spans` は比較対象外と明記 (3)`reason` の `all_diff_spans_phoneme_equal_or_ukus_variant`(Trial:232)を移植 (4)W1文言「1:1 span」→「同数・全unitがword(Trial:177 positional条件)」、救済は各位置を既存位置別判定→不合格位置だけ対表(Trial:197-227と同一)、`bad` 分岐の救済もpositional span限定。CMU未登録位置のbadチェック除外は承認済み(OF-01/02)どおり移植可、音素注入なし・対表完全一致のみをsweepで確認。
- W-02[必須] c12解除手順: (1)`_merge_checkpoint`(er063:1325)が `tts_checkpoint.json` のc12を再注入し得る→checkpoint不在/該当キー不在の確認を手順に追加 (2)`writer/provenance.json` の `audio_text_deviations` にforte記録が残る→削除せず「superseded」注記追記またはRUNTIME_EVIDENCEで明示 (3)累積カウンタ: c12は `state=RESOLVED`、`cumulative_tts_attempts=4`、上限15・1回3なので発火しない、RESOLVEDはブロックしない、attemptファイルは自動採番→実装時は `canonical_text_sha256` が現行TTS入力hashと一致することのみ確認 (4)**推奨代替: segmentsキー削除でなく既存の `reuse_blocked` 印をc12 entryに付ける**(er078:46-49で常にblock、er063:764-768で再生成、旧理由は `reuse_value_guard_blocked_previous` に自動記録。印の値に理由[ユーザー指示B]・日付・保全コピーpath)。失敗時は保全コピーから復元。
- W-03[必須] `ukus_contributed` の検出漏れ: UKUS flagだけOFFのrollback時、再判定NG(非保護差)はblockされない(er078:92-96)→W11が唯一の防壁。修正: (1)`asr_judgement` と `asr_judgement_inherited` 両方を見る(Zは再利用時inheritedへ移す er063:786-787) (2)`orthographic_equivalence.sites[*]` 全site(primary/secondary/KP票)の `er109.rules` を走査 (3)判定キー統一: `"ukus_spelling_variant" in rules` または `ukus_pairs` 非空 (4)fail-closed: `ortho_contributed`=True・versionが `*_ukus*`・siteのer109 audit無し→UKUS寄与ありとしてblock (5)配置は `kp_vote_gate_follows` 早期return(:66)より前・既存ortho判定(:63)直後 (6)T-E5に「inheritedのみ」「KP票site」「audit欠落」を追加。
- W-04[必須] T-K(両方ON相互作用test)の割当: 後からcommitする側の委任の必須test+B工程run前のFable受入項目。内容=PNAP供給後canonicalでの判定/固有名詞差+綴り差同居文が両方ONでもNG維持(G2限界、既知別案件)/②OFF/ONで①署名不変・①OFF/ONで②判定不変。
- W-05[推奨] golden: `pre_wiring_signatures_*`・`manifest.pre_wiring_commit` の既存行は触らない。合成行追加時は新行のpre署名だけ配線前commit overlayで採り、既存行再計算がfixtureとバイト同一を確認。現HEAD(v1)のX/Z署名を中間baselineとし、v2との差分を「version文字列のみ/新規UKUS PASS/PASS→NG 0」の3分類で全件確認。T-Iの「flag OFF→従来署名」はversion文字列正規化後に比較。
- W-06[推奨] HR rejudge dirty検査対象に `er109_ukus_pairs_v1.json` も追加。
- W-07[推奨] run単位evidence/summaryに `ukus_active`・表sha・LAYER_VERSION を記録。表sha不一致は失敗状態をcache(lru_cacheは例外をcacheしない→毎回1.5MB再ロード)、sha照合testを常設回帰に。
- W-08[推奨] X陽性証拠: 「非発火の記録」では弱い。(1)X正式TTS段のdecorator付き入口から、米綴り化しやすいUK専用語を複数含む文(organisation/centre/colour/programme)2〜3文を実行し最初の発火で止める(上限約3clip・約3円) (2)API 0でV6行列(Primary/Secondary/KP票/継承/Store guard×X)をhook差し替えなしの実コードで再実行。Zで発火しない場合(TTSがspecialityと読みASRもそのまま)は保全attempt1〜3の実転写をZ scopeで再判定(API 0)を予備証拠と明記。
- W-09[推奨] c12は `pron_differs=true` である旨をB報告の最終試聴確認点として明記(Gate・基準変更ではない)。
- W-10[推奨] test更新: `er109_xz_isolation_01_test_01.py:248` のspy、`er109_xz_scope_01_test_01.py:140-144,156,466,472` が `_evaluate_cached` 2引数前提→`ukus=` を渡してよいのは `_evaluate_cached` のみとするAST test新設と同時更新。
- 情報: W-11 LAYER_VERSION副作用の根拠妥当(機能比較は xz:131,214 のみ、保存値参照は監査用)。W-12 P-06安全性妥当だが T-Dで value_guard数語彙・`negation_counter` に表の語が該当しないことも検査(`nought→naught` はactive)。W-13 flag構成は既存 `ORTHOGRAPHIC_EQUIVALENCE_ENABLED` と同型で承認済み、11-7対象外、27-3整合。W-14 ①との干渉は近接hunk・allowlist・SSOTのみ、後からcommitする側がrebaseせず両方の行を残して全回帰(※本プロジェクトではrebase禁止→最新化後に自分のhunkを再適用)。W-15 offline tool(`er109_stored_*`)は既定Falseでv1を測り続ける→Production挙動の証拠には `decision()` をscope内で通す。

## 実装
1. `WIRING_DESIGN_02.md`(OF反映差分表)。
2. 新module `er109_ukus_spelling_01.py`(Trialからコピー改名、Production名)、対表 `git mv er111_ukus_pairs_v1.json er109_ukus_pairs_v1.json`(内容不変、sha照合fail-closed+失敗状態cache)、builder改名 `er109_ukus_pairs_build_01.py`。
3. `er109_asr_orthographic_equivalence_01.py`: `evaluate(..., ukus=False)`、opcodeループ内positional救済(W-01(4)、各位置=既存位置別判定→不合格のみ対表、CMU未登録位置のbad除外、音素注入なし)、`SpanRecord(rule="ukus_spelling_variant")`、`reason` 移植、`ukus_pairs`/`pron_differs` audit(適用時のみ)、`LAYER_VERSION`→`er109_orthographic_equivalence_v2_ukus01`。
4. `er109_xz_scope_01.py`: flag `UKUS_SPELLING_EQUIVALENCE_ENABLED=True`(親flag従属)、`is_ukus_active_for_run()`、`_evaluate_cached` cache keyにflag、run単位summary記録(W-07)。`er078_reuse_value_guard_01.py`: `ukus_contributed`(W-03、:63直後)。`er109_hr_lock_rejudge_01.py`: dirty対象に新module+pairs json。
5. golden: W-05の手順でX/Z `post_wiring_changed_*` 再作成、scope無し不変。
6. test: 網羅sweep(W-01、Trial⇔Production、結果json+rules差分分類保存)、Trial 27件移植、固有名詞除外、P-06構造test(W-12拡張)、hook別c12 OFF=NG→ON=PASS(保存転写、API 0)、cache/AST(`ukus=` は `_evaluate_cached` のみ、Productionから `er111_*` import 0)、DefaultOnScope型、T-E5(W-03 3ケース)、version正規化比較(T-I)、sha照合常設、W-10 test更新。**T-K**: ①RETが先にcommit済みなら本委任で実施、未commitなら「①側で実施」とRESULT_PACKETに明記(Fableが①委任へ回す)。既存er109系全PASS。
7. **Trial撤去**: sweep結果保存後に `er111_ukus_spelling_trial_01.py`・`_test_01`・`er111_ukus_trial_eval_01.py`・`er111_ukus_trial_cases_01.py` を撤去(git rm、path限定commit)、allowlist整理。`BR_AM_SPELLING_PAIRS` は凍結残置。
8. **全回帰** `run_project_regression.py` 単独実行、failed/errors分類、自分起因0。
9. **X runtime evidence**(≤10円): W-08(1)=X正式TTS段のdecorator付き入口で、既存X runの単一segmentを `--only-segments` で再生成するのではなく(本文改変不可)、**正式TTS段関数を本物のscope設定経由で呼ぶ実run**(ASR-HOMOPHONE委任_02cで用いた「正式TTS段関数実run」方式と同じ。UK専用語を含む検証用segment text 2〜3文、隔離run_dir、Store書込は隔離)で発火を取る。最初の発火で停止、上限3clip。加えてW-08(2)=V6行列のAPI 0再実行(hook差し替えなし)。発火時のevidence: `ukus_spelling_variant` rule、`ukus_pairs`、PASS(warningsなし)、HR 0、Store guard挙動、run summary `ukus_active`。
10. SSOT: OPEN-471 Status=`IMPLEMENTED_X_EVIDENCE_DONE_PENDING_Z_EVIDENCE_AND_FABLE`、CURRENT_SPEC(ASR包括対策er109節へv2 UKUS層追記: 配線点・flag・PASS→NG 0保証・pron_differs残存リスク。PRODUCTION_WIRED表記はFable受入後)、DECISION_LOG、REPORT_LEDGER。
11. 証跡 `UKUS/RUNTIME_EVIDENCE_01.md`(X分+Z手順[c12 `reuse_blocked` 印方式・checkpoint確認・provenance superseded注記・pron_differs明示])、`UKUS/IMPLEMENTATION_01.md`。

## 禁止
Z stage実行・c12再生成(B工程)、`er103`系編集(①担当)、A/B/C共有Validator編集、受理境界の緩和、Tier-2同値化、warnings経由PASS_WITH_WARNING化、10円超過、rebase/force push/一時index、本文(canonical)改変による発火誘導(検証用segmentは隔離run_dirのみ)。

## 報告(docs/pm/RESULT_PACKET_ASRQ_UKUS4.md)
(1)OF反映表 (2)変更ファイル一覧(file:line) (3)test結果(sweep結果・rules差分分類・golden・全回帰) (4)X evidence(証拠区分) (5)Z手順(B工程向け) (6)T-K実施有無 (7)費用・時間 (8)commit・raw URL・SSOT (9)残存リスク + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。