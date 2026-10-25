# OPEN333_E4_APPLY_PLAN_01(E4のProduction適用計画。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_13、2026-10-26)
**本書は計画のみ。Productionファイルは編集していない(本委任)。** 適用はOpus短縮レビュー(`OPUS_REVIEW_REQUEST_02_OPEN333_E4.md`)後の別委任。区分=承認済み不具合是正(11-8。新仕様でも新しい合格条件でもない)。設計=`OPEN333_E4_DESIGN_01.md`、評価=`OPEN333_E4_EVAL_01.md`。

## 1. 変更箇所(推奨=E4のみ)
| file | 内容 | 行数見込み |
|---|---|---|
| `er011_ja_asr_variant_layer_01.py` | rollback定数 `CANDIDATE_E_CASCADE_DIFF_RETURN = True`(`:394-395`のE3定数の隣、コメントに目的・OFF=HEAD)。`try_rescue_before_resolver` の Candidate E分岐、`_rej`判定(`:373-383`)の後・`return _pass("PHONETIC_MATCH", "(…Candidate E)…")`(`:380`)の前に、`protected.content_diffs` の cascade_eligible 差分が残るとき `protected.candidate_e_cascade_diffs` を記録して既存の `_cascade(...)`(`:304-306`)を返す。cascade判定の例外は `_cascade` を返す(fail-closed) | +約14 |
| `er007_ja_secondary_asr_01.py` | adapterが `protected.candidate_e_cascade_diffs` を `asr_judgement.candidate_e_cascade_return` へ読取専用で複写(M-6同形、`:552`の`_ce_rej`取得と`:746-748`のaudit書込の隣。判定不変、該当が無ければfield無し) | +約4 |
| `er007_ja_asr_validator_01.py` | コメントのみ(`:366-386`の数字差経路注記に、E4でcascade差を持つEをCascadeへ戻す旨を追記) | +約4(コメント) |
| test | 新規 `er011_ja_asr_variant_layer_candidate_e_cascade_return_test_01.py`(§5) | 新規 |
| docs | `OPEN333_E4_APPLY_RESULT_01.md`、`open333_e4_prod_parity_01.*`、runtime発火出力、OPEN-333行・CURRENT_SPEC Variant Layer節・DECISION_LOG追記 | — |
rollback定数: `CANDIDATE_E_CASCADE_DIFF_RETURN`。**env/flag/引数/起動scriptで切替不可**(E3と同じ。test `test_constants_not_read_from_env_or_args`相当で関数ソースに`environ`/`getenv`が無いことを固定)。既定=True(是正有効)。承認済み不具合是正のため11-7の隔離flag対象外。

## 2. fail-closed と方向性
- 変更は『PASS→ASR_VALIDATION_UNCERTAIN』のみ。`_pass`の返却条件を狭める(PASS集合は縮む)。新しい`return _pass`は作らない。
- 例外・要素欠落: `d.get("cascade_eligible", True)`(欠落=cascade扱い)、判定中の例外は `_cascade`(PASSにしない)。定数False=HEAD完全一致。
- 既存のretry/fallback/Gate: UNCERTAIN後は既存の統一judge(P1/P2/P3、`er078_asr_unified_judge_01.py:639-662`)・Cascadeの許容集合・再生成上限・HR Lockをそのまま使う。Gate・上限は無変更。
- 構造的な遮断: Primary UNCERTAINからの`ORTHOGRAPHIC_VARIANT_CONFIRMED`は、E4で返す結果が必ず non-cascade 差分を含むため `_orthographic_reading_confirmed`(`er007_ja_secondary_asr_01.py:361-383`)がFalse→開かない。`try_upgrade_voicing_cascade`(`er011:525-`)も `_is_pure_phonetic_uncertain_cascade` がFalse→開かない。評価で受理変化0。

## 3. 監視(M-6同形)
- field `asr_judgement.candidate_e_cascade_return = {"diffs": [[canonical, asr], …], "note": …}`(該当時のみ)。
- 集計: `open333_first_run_tally_01.py <run_dir>` を拡張(`candidate_e_cascade_return` 件数とpair、同runでのCascade採用[PASS_WITH_WARNING/secondary_confirmed]とNG_BOTH件数)。読取専用・API 0。
- 閾値: 1run(1記事セット)で当該field **3件超**ならFableへ報告(自動rollbackしない)。想定=実データ頻度0.59%/セグメントから、1記事セット(約十数セグメント)で0〜1件。
- 期待値の追跡: Cascade後のAzure一致率(PASS_WITH_WARNING/NG_BOTH比)を最初の3〜5 runで集計し、再生成増の実測に置き換える。

## 4. proto↔Production一致(全キー)
`eval_open333_prod_parity_01.py` 同形の `open333_e4_prod_parity_01.py` を新規作成(既存は凍結物のため流用せずコピー):
- 4通り: `head`(適用前のgit HEADスナップショット)/`off`(作業ツリー+新定数False)/`on`(作業ツリー既定ON)/`proto`(headスナップショット+`proto_open333_fix_06`の`E4`、または`proto_open333_fix_05`の`E3V_E4`)。**HEADはE3適用済みの現行HEAD**(E3は4通りすべてON)。
- 入力: `open333_e4_eval_01.out.json` の全行(実データ1,327+sweep69+E4行242)+Secondary対(保存103+全Primary転写1,203)。キー=Primary段classify + 正式adapter state/reason/label + Secondary受理sim。
- 合格: `on`≡`proto` 差0(全キー)、`off`≡`head` 差0(OFF=HEAD)、`on` vs `head` の差は『PASS→Cascade』のみ(74件+実データ4行)で、非PASS→PASS 0。

## 5. 回帰・test
- 新規test(ネットワーク遮断harness`netblock_harness_01`+`.venv`): (a)走れメロス→走レメラス型がUNCERTAINになる (b)ctrl(名一致)がPASSのまま (c)定数False=HEAD完全一致 (d)env/引数で切替不可 (e)`candidate_e_cascade_diffs`記録とadapterの複写 (f)cascade判定の例外・欠落でPASSにならない (g)非数値entryと数値entryの両方 (h)E3拒否が先に効く(順序)。
- 既存の回帰: 委任_12と同じ43 file(er007 JA系・er066・er078全test・static audit・er109・er011 JA/KP/repetition系・er009/er025/er038)。**既知の8失敗[er007_ja_secondary 2・er109 5・static audit inventory 1]以外の新規失敗0**を確認。直接呼出元の確認: `er003_v1_n3_01_tts_generate.py` が `classify_ja_asr_match` を直接呼ぶ箇所(`ASR_VALIDATION_UNCERTAIN`の既存扱いに従う)で、E4後のUNCERTAINが既存の分岐で処理されること。
- 注意: `er011_ja_asr_variant_layer_candidate_e_full_diff_test_01.py` 等、E分岐のPASSを期待する既存testがE4で変わる場合は『前提変更』として最小限更新し、理由を記録(委任_12のr5 measurement/kana_unify更新と同じ扱い)。

## 6. 保存転写注入による発火確認(API 0)
`open333_runtime_fire_01.py` 同形の `open333_e4_runtime_fire_01.py`: 保存転写1,327行を**正式adapter**(Azureはstub・socket guard)へ注入し、ON/OFFで (a)E経由PASS件数 (b)`candidate_e_cascade_return`発火件数(期待=実データ4行、OFFで0) (c)Azure応答注入[原稿どおり→PASS_WITH_WARNING/誤り→NG_BOTH]の2通りを記録。有料Trialは行わない。

## 7. SSOT
OPEN-333行に『E4適用済み(Status、初回run集計待ち)』を1文追記、`CURRENT_SPEC.md` Variant Layer節(`:2196`付近)にE4の1段落、`DECISION_LOG.md` に適用エントリ、`docs/pm/delegation_log/` に委任文を逐語保存。**PRODUCTION_WIREDではなく『承認済み不具合是正の適用』と記す**(新仕様採用ではない)。ユーザー判断の候補は発生しない見込み(E4-Nを採る場合のみA4接触のため判断候補D)。

## 8. 付録: E4-Nを採る場合(推奨しない)
`er011` の `_candidate_e_number_entry_rejections`(`:418-462`)が返す拒否要素に `cascade_eligible`(replaceかつ entity_like[`javal._is_katakana_or_acronym`両側] または 濁点のみ差[`javal._reading_equal_allowing_voicing`])を足し、E分岐の `if _rej:`(`:373`)で『全拒否が unexplained_non_numeric_diff かつ cascade_eligible かつ 値ガード由来の拒否なし』なら `_cascade(...)` を返す(約+25行)。rollback定数 `CANDIDATE_E_NUMBER_ENTRY_CASCADE_RETURN`。ただし評価どおり実効は **数値entryのA4_C2_HOMOGRAPH除外の解除**であり、安全条件A4に触れるため **適用前にユーザー判断(判断候補D)が要る**。proto: `proto_open333_fix_06.py`(`E4N`/`E4_E4N`)。

## 9. 適用順(推奨)
1. Opus短縮レビュー(論点3〜5件)→Fable照合。2. 別委任でE4を適用(定数+分岐+adapter field+test)。3. proto↔Production一致・回帰・runtime発火。4. SSOT追記+commit/push。5. 正式runで`open333_first_run_tally_01.py`集計。E4-Nは正式runの実測を見て再検討。
