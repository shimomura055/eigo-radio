# IMPLEMENTATION_DESIGN_01: 多語同音救済(L1)のProduction実装設計(Opus独立レビュー用・11-3条件A/C)

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_06 [A-1] / 2026-10-22 / API 0・JPY0
Status: `APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS`(**PRODUCTION_WIREDではない**)。承認原文=`docs/pm/delegation_log/2026-10-22_PNMH-PRODUCTION-WIRING-AND-PRONUNCIATION-SUPPLY-PLAN-02_USER.md`§1・§2。
A-1の成果=本設計書+未配線module(`er094_multiword_homophone_01.py`)+test(`er094_multiword_homophone_01_test_01.py`、24 test PASS、結果=`A1_unit_test_result_01.txt`)。**Production既存ファイルは未編集**(`git diff HEAD`の追跡済み.py差分0)。

## (a) 新module(実装済み・未配線)
- `er094_multiword_homophone_01.py`: Trial v3の`multiword_span_equivalent_v3`(出典`proto_multiword_span_01.py`)の純関数移植。入口=`multiword_homophone_candidate(canon_span, asr_span, entity_like)`(例外はfail-closed=非救済)。
- 承認済み安全条件(拡張なし): 片側1語のみ(1:n/n:1)・最大3語・全token小文字英字のみ・数値/否定語は拒否・複数語側1文字token禁止・canonical側3字未満禁止(G5)・複数語側2字tokenは閉じた機能語集合`FW2`のみ(V8、`Bi-us`型NG維持)・entity_likeは代表発音(CMU先頭variant)のみ・CMU辞書外/variant直積>64は判定不能=非救済・ストレス記号無視。
- 再利用: CMU取得は既存`er008_asr_variant_hardening_15_homophone_en._phone_variants`(先頭=代表発音の順序も同一)。entity_like判定は`val.protected_check`内の既存変数`entity_like`をそのまま渡す(再実装なし)。数値/否定は`val._NEGATION_WORDS`/`val._is_number`を**遅延import**(循環import回避)。
- Trialからの差分は(1)hp._phone_variants経由、(2)ガード判定のまとめ方のみ(判定結果同一。41ケースとTrial `after_v3`の全件一致をtestで固定)。

## (b) 配線点(最小diff案。A-2で実施、Opusレビュー後)
**事実(コード確認)**: Primary転写もSecondary転写も、判定は`val.classify_asr_match`→`val.protected_check`(`er006_preprod_hardening_01_validation.py` 1:1 homophone入口 L750付近、`homophone_candidate = bool(result_h)`の直後)に集約される。Secondary側(`er006_secondary_asr_01.py` `_step_alternate_pass` L571、受理判定 L993付近)は`is_homophone_candidate_mismatch(cls)`=`content_word_diffs[].homophone_candidate`を読むだけで、Secondary転写の分類自体も同じ`classify_asr_match`を通る。したがって**配線点は`protected_check`の1箇所**で、Primary/Secondary両転写に同一関数が効く(Trialのpatch点も同箇所。委任文の「2箇所」はこの1箇所から両経路へ伝播する)。Secondary側コードの編集は不要=将来KPに`force_secondary`が入っても自動で同一関数を通る。

```
# val.protected_check 内、L750付近(既存2行の直後に追加。条件は既存と同階層)
                if not homophone_candidate and _mw.multiword_homophone_candidate(canon_span, asr_span, entity_like):
                    homophone_candidate = True
                    multiword_hit = True       # additive根拠(下記)
```

+ ファイル冒頭近傍に`import er094_multiword_homophone_01 as _mw`(er094は import 時に val を参照しないため循環なし)。`result.content_word_diffs.append({...})`へ`"multiword_homophone": multiword_hit`をadditiveキーで追加(`entity_like_source`と同方式。既存キー・分類ロジックは無変更)。**1:1経路・既存`homophone_arpabet_equivalent`は無変更**。n:m一致時の戻り値ラベルは既存`HOMOPHONE_EQUIVALENT`系(Trial実測どおり)。
- 他の`protected_check`呼出: L1090(classify本体)、L1292(否定のみ確認)。その他の直接呼出はTrial/評価script(Production経路外)。Store再判定(`rejudge_with_current_judge`)等も`classify_asr_match`経由で同じ関数を通る。
- A-2の静的testで「`protected_check`が`_mw.multiword_homophone_candidate`を1回だけ呼ぶ」「他のProduction .pyが`er094`を直接importしない」を固定。

## (c) rollback
- `er094_multiword_homophone_01.MULTIWORD_HOMOPHONE_ENABLED`(module定数、既定True=承認済み仕様のため既定ON)をFalseにすると常にFalse=現行とバイト一致(unit testで41ケース現行一致を確認済み)。**env/flag読取・mode引数・設定dict経由のON/OFFは設けない**(隠れON経路を作らない)。
- 撤去: 配線2行+import+additiveキーを戻すのみ。

## (d) Family x パーツ x 経路の配線表
共通点=`val.classify_asr_match`→`protected_check`。通常入口=`secondary_asr.evaluate_attempt_with_cascade[_detail]`(内部で`classify_asr_match`)。再判定=`classify_asr_match`直接。呼出行はコード確認済み(2026-10-22)。

| 経路 | 呼出ファイル:行 | Family X | Family Z | 備考 |
|---|---|---|---|---|
| KP英語phrase 初回/再試行(narration) | `er003_v1_repro01_main_generate.py:356` `evaluate_attempt_with_cascade` | X KP | `er063_family_z_audio_01.py:827`(primary)/`:836`(ENGLISH_LOCK fallback)=`repro01.generate_narration_snippet_verified_strict` | KP 4 slot構成も同関数 |
| 本文/Dialogue/見出し等 英語segment(minimal fallback含む) | `er003_v1_crosslevel_audio_02_common.py:378` `evaluate_attempt_with_cascade`(`_run_a2_minimal_fallback_attempt` L327) | X runner | `er063:804` `crosslevel.generate_english_segment_with_fallback` | `force_secondary=True`は_minimal_fallbackのみ(unified judge L75) |
| 6%減速後再検証 | `er003_v1_n3_01_tts_generate.py:144` `evaluate_attempt_with_cascade_detail` | X | `er063:778/788` | |
| Charon英語/Voice | `er003_v1_sing01_voice01_generate.py:246` | X | `er063:795` | |
| News narration | `er003_v1_sing01_news_tail_fix.py:209` | X | `er063:774` | |
| B Family voices | `er012_b_family_voices_production_01.py:553` | (B系) | - | 開発対象外Familyだが同関数 |
| resume(N8 A2/B1) | `er008_n8_a2_resume_01.py:41` / `er008_n8_b1_resume_01.py:47` `classify_asr_match`直接 | X | - | |
| Store/継承再判定(J11/K2) | `er019_family_x_validation_inheritance_01.py:233` `rejudge_with_current_judge`(L284/295/302→`unified_judge` L307) | X継承 | Z継承(`er063:726` `guard_entry`は値ガードのみ=本機能に無関係) | 過去NGの保存転写が再判定でPASSになりうる(1:1 F1と同方針) |
| 日本語 | `er007_*`/ja_secondary | 対象外 | 対象外 | EN専用 |

A-2で**配線表のgrep検証(全呼出行が`classify_asr_match`に到達)**と、各行を実際に通す統合testを行う。共通関数を直しただけで配線完了とはせず、X/Z各々の正式関数で発火証拠を取ってから、Family別に`PRODUCTION_WIRED`とする(一方のみなら他方は未完了として追跡)。

## (e) 挙動変化4点の扱い
| 点 | 内容 | 扱い・test |
|---|---|---|
| NX1 | `two->to`数値ゲート例外と多語同音の共存で新規PASS | 許容(1:1でも既にPASS)。ケースNX1で値を固定 |
| M1 | 矛盾拒否(他の内容語差が残ればNG) | 全差分が同音のときのみPASS(M3/CS1/CS2が不変NG) |
| CS・F1迂回 | connected-speech層/F1再判定経路 | CS1/CS2/CS3で他差分残存時NG維持。F1も同関数(表d) |
| F1残差1:1限定 | 既存F1は1:1のみ | 変更なし |

41ケースunit(`SentenceLevelInMemory`)でbefore/afterを固定。PASS->NG 0、NOT_PASS期待の誤PASS 0。

## (f) 検証計画(A-2)
1. **unit**: A-1完了(24 PASS)。A-2で配線後に同testを「メモリpatch」から「実コード」に切替えて再実行。
2. **4,032ペア再適用**: `measure_v2_01.py`のpairs_02(golden 193行・HR queue含む)を配線後の実コードで再判定。合格=`measure_v2_result_01.json`と一致(変化4件=byus->buy us、PASS->NG 0、新規誤PASS 0)。
3. **無効時バイト一致**: `MULTIWORD_HOMOPHONE_ENABLED=False`で全ペア現行判定と一致。
4. **静的test**: protected_check呼出1回・Production .pyからer094の直接importなし。
5. **X/Z正式経路の発火証拠(API 0)**: 表(d)の各行について、Production関数のASR取得seamにだけ保存転写`buy us`を差し込み、実Production関数(KP/segment/減速後/resume/再判定)が`multiword_homophone=True`でPASSすること、`Bi-us`/`bios`でNG維持を確認。実行model_id・routing・Validator判定を記録。
6. **実音声(API有)**: (X)記事Bの`byUs`含むsegmentをProduction関数で再生成1本(`TTS_EXECUTION_MODE=STANDARD`)、(Z)Z runnerのProduction関数で`byUs`を含む短い英語segment 1本。Store/HR Lockを汚さない専用run_id・出力dir、既存Production成果物は上書きしない。実ASRが`buy us`を返す保証はなく(Trialでは`byus`/`by us`/`bias`が多い)、実音声の主目的は「配線後の正式関数が正常終了し、判定・ラベル・model_id・routingが記録されること」。発火の主証拠は5。実音声で`buy us`が出なかった事実は隠さず報告する。
7. **`Bi-us`実音声負例1本**: (g')。
8. **PASS条件維持**: 現行承認仕様(Primary PASSならSecondary不要、CURRENT_SPEC:2818)の判定順序を変えていないこと。`er078_*`既存回帰test群の全PASSで確認。KPの両方PASSは実装しない(g)。
9. **費用見積**(出典=`TRIAL_RESULT_01.md` §3: 13クリップのTTS+ASR実測6.32円=約0.5円/クリップ、`er093_output/pnmh_trial_01/paid_calls.jsonl`): A-2想定=X 1本+Z 1本+Bi-us候補約6本+再ASR 約8〜10クリップ -> **約5円(目安上限JPY30)**。量産単価への影響=判定のみ追加でAPI呼出増0・原価増0(不要retry減による微減はありうるが未測定)。

## (g) KP両方PASS条件との関係
- 承認済み正式仕様=Primary PASSならSecondary不要(CURRENT_SPEC:2818、全Section共通・KP含む。`docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/SPEC_IMPL_MATRIX_01.md`)。ユーザー原文§2「承認済み仕様に食い違いがある場合は勝手に仕様を変更しない」により、**KP両方PASSは実装しない**(OPEN-440ユーザー回答待ち・未承認)。本実装は現行判定順序を変えない。
- 干渉しない理由: 配線点`protected_check`は「その転写が同音候補か」を決めるだけで、Primary/Secondary間のAND/OR(unified judge)には触れない。将来OPEN-440で`force_secondary`等が入っても、Secondary転写も同じ`classify_asr_match`を通るため、多語救済はPrimary/Secondary双方で同一に働く。
- OPEN-440実装が承認された場合は、本配線のレビュー・Regression・runtime確認を合同化する(ユーザー原文§2)。

## (g') `Bi-us`実音声負例の構成と「意図した発音が生成された」確認方法
Trialは構成失敗(TTSが`bias`と読んだ)。A-2で以下を行う。
1. 候補TTS入力(各1回、Trialと同じ`gemini-3.8-flash-lite-tts`・voice): `Bi-us` / `Bi us` / `Bi, us.` / `Bye-us`(対照) / `B I us` / `be-us`。
2. 各wavにPrimary(OpenAI)+Secondary(Azure)転写。**採用条件(2語分離の確認)**: (i) focal区間が`bias`/`by us`/`buy us`でなく、第1音節が/i:/系(`bee us`/`be us`/`Bi-us`等)と読める転写を両ASRまたは一方が返す。(ii) ローカル確認: 既存ローカルASR(`er056_en_asr_local_wav_check_01.py`系)の転写+語境界で2語区切りの有無を確認。(iii) 候補の転写一覧をFableへ提示し採用を確定。
3. **ASRが`by us`へ正規化した場合**: 新規則でPASSになりうる。これは既知の限界(音素列のみでは`by us`と`bi us`を転写上区別できない。DESIGN_OPTIONS §4-3、ケースBI3)であり、**隠さず報告**してFableが判断。意図した発音が確認できない候補は負例PASSの証拠にしない。
4. 負例採用基準=意図発音確認済みwavで、Validatorが`NOT_PASS`(V8で拒否)になること。

## Opusレビューで特に見てほしい論点
1. 配線点が`protected_check`1箇所でPrimary/Secondary両転写・全Family経路に届くという事実認定(表d)の抜け(`protected_check`を通らない英語Production判定経路の有無)。
2. `entity_like`をそのまま渡す設計の妥当性(canonical側の大文字始まり語由来。小文字の一般語は全variant比較になる点)。
3. 再判定(Store/K2/resume)で過去NGの保存転写がPASSに変わる挙動の許容(1:1 F1と同方針とみなしてよいか、HR Lock済みentryの扱い)。
4. additiveキー`multiword_homophone`が既存telemetry/HR queueスキーマ・`content_word_diffs`を読む集計を壊さないか。
5. `Bi-us`負例の成立条件(ASRが`by us`へ正規化する限界)の扱い、`bias`⇔`by us`許容(BI3)を含むリスク受容。
