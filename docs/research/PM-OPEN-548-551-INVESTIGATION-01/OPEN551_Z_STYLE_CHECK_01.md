# OPEN-551 Z側Style実測照合の網羅確認(read-only、API 0、JPY0)

管理ID: PM-OPEN-548-551-INVESTIGATION-01 委任_01 / 2026-10-26。調査script=`tools/z_style_measured_survey_01.py`・`tools/z_fallback_survey_01.py`(既存auditを読むだけ)。

## 結論(先頭)
- **定義の照合は網羅されている**: Zの6共通role(FULL_STORY[Adv/Std]・PREVIEW・SUPPORT_JA×2・KP_EN・KP_JA・KP_EXPL_EN)のStyle文は`fx_20261017`のsha256と全件一致(今回再計算、MATCH 8/8、例外6role=ADV_EN_COMMENT/TOPIC_INTRO_EN/JAPANESE_TITLE/DIALOGUE×2/SHELLは`CROSS_FAMILY_COMMON_STYLE_MAP`で理由付き。`er063_family_z_audio_01.py:268-282`、drift test `er063_family_z_common_style_wiring_01_test_01.py`)。
- **実測の照合は不足している**: Zの`run_audio_gate`(`er063:1899-1930`)は実送信prefixと承認値の照合をしない。Zは`resolve_run_profile`/`m3_assembly_gate`を呼ばない(Grep: 呼出元はXの`er019_family_x_audio_production_runner_01.py:2403,3388`とtru_ev toolのみ)。Yで導入した「実測値==承認値、checked空はFAIL」(PREVENTION_01 (a)、Y)に相当する検査がZに無い。
- 既存Z記事で「audit上で不一致が確認できた」のは**1clip**(猿の手Std `full_story_part1_c10`、Style脱落のfallbackが無承認で採用)。他に不一致の記録はないが、roleの大半は**実測が記録されていない**ため「一致」とも言えない(下表)。

## 事実1: 「照合」が何に対して行われているか
- `style_record.json`(`er063:677-723`): `expected_style_record`は`FAMILY_Z_ROLE_STYLE`定義そのものから作る。既存recordとの比較は「定義と記録の一致」であり、実送信prefixとは無関係。目的は旧Style run混在の防止(課金前STOP)で、これは有効。
- 各entryの`style.style_prefix_sha256`(`:1253`)は`style_prefix_sha256(style_text_for(spec))`、つまり**意図値**を書いている。`effective_style_prefix_sha256`もDialogueは定数`p9a.ENGLISH_STYLE_PREFIX`のsha(`:1284-1289`)で実測ではない(ctx採用時のみ`dialogue_tts.ctx_style_sha256`)。
- 実測は`entry["attempts"][*].style_prefix_sha256`(`extract_attempt_evidence`、`:1148-1170`、generatorの`attempts_log[*].style_prefix`由来)。generator側の記録有無でroleにより異なる。
- Gate側(`:1899`): M2存在assert・速度・音声品質・共有gate(KP source等)のみ。`checked`空でPASSになる経路: Style観点の検査自体が無いので「検査0件でPASS」が常時成立。

## 事実2: 実測の有無(`tools/z_style_measured_survey_01.py`、各作品の最新正式run)
分類=採用attempt列の最終attemptの`style_prefix_sha256`を、`FAMILY_Z_ROLE_STYLE`の期待shaと比較。

| role | 実測の有無 | 結果 |
|---|---|---|
| NARRATOR_FULL_STORY_STD(a2) | あり | 全run一致。猿の手1件のみ`MISMATCH+fallback`(後述) |
| KP_EN(a2/b1b)・KP_EXPL_EN(b1b) | あり | 全件一致 |
| TOPIC_INTRO_EN | a2のみあり(一致)、b1bは**null** | — |
| **NARRATOR_FULL_STORY_ADV(b1b)・ADV_EN_PREVIEW・ADV_EN_COMMENT** | **null(未記録)** | 照合不能(Adv生成generator`generate_news_narration_wide_margin`の`attempts_log`で`style_prefix_sha256`がnull(原因はgenerator側の記録欠落と推定、generator内部は未精査)。`instruction_type=english_style_prefix_wide_margin`の名のみ) |
| **STD_JA_PREVIEW・STD_JA_COMMENT・JAPANESE_TITLE・KP_JA(Std日本語)** | **null(未記録)** | 同上(日本語roleは意図値の自己一致のみ=Yで直した盲点と同型) |
| DIALOGUE_STD/ADV | 実測なし(override無し=既定Dialogue Style) | 既定Dialogue Styleはユーザー§2B/2026-10-19決定③で例外。意図どおりだがshaの実測記録なし |
| SHELL | 対象外(既存Master資産、TTSなし) | — |

対象run: the_tell_tale_heart/run_sf_prod_02、the_monkeys_paw/run_sf_prod_01、the_gift_of_the_magi/run_sf_prod_01、the_open_window/run_sf_prod_01、after_twenty_years/run_sf_prod_01、melos/run_e2e_06。全6run×2level同じ傾向(Adv全segmentがnull)。

## 事実3: 不一致が確認できる部位(推測なし、audit記録)
- 猿の手`run_sf_prod_01/a2/audit/tts_generation_results.json`の`full_story_part1_c10`(NARRATOR_FULL_STORY_STD): attempt standard1・2・fallback1がすべて`ASR_VALIDATION_UNCERTAIN`(verified=false)の後、**fallback(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`=`natural, clear, conversational`、PD06を落とす)の音声が`z_adoption=adopted`・`status=OK`で採用**。`asr_judgement.state=PASS`、`audio_text_deviation`(guest→visitor)記録あり。Xの`m3_assembly_gate`なら`STD_FALLBACK_USED_OR_UNKNOWN`で人間承認要求だが、Zには同等Gateが無く承認記録も無い。公開版か否かは本調査で未確認(`run_sf_prod_01`は猿の手の正式run)。
- 他の正式runにfallback採用は無し(`tools/z_fallback_survey_01.py`: sf_prod系は猿の手1件のみ。Melos旧e2e/Trial系runに計~15件=旧run)。
- 関連(別管理): TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01(OPEN-540の統一側)が並行中。fallback採用の扱いはそちらの方針と重なる。

## 比較: Yとの差
| 観点 | Y(委任_02で導入) | Z(現状) |
|---|---|---|
| 承認profileの明示 | `fx_20261017`を`resolve_run_profile`で解決、`audit/style_profile.json` | Z独自表`FAMILY_Z_ROLE_STYLE`+`style_record.json`(定義との照合) |
| 全role網羅(期待集合との完全一致) | `Y_ROLE_COVERAGE==profile overrides`(test) | `CROSS_FAMILY_COMMON_STYLE_MAP`でX profile 6roleを網羅(test有り)=**同等** |
| 実測prefix照合 | `style_actual_vs_approved.json`、checked空はFAIL | **無し**(意図値の自己記録、Adv/JA実測null) |
| fallback採用のBLOCK | `m3_assembly_gate`(fallback_used→人間承認) | **無し** |

## 最小是正案(提案。実装は未着手)
1. **記録**: Advの`generate_news_narration_wide_margin`と日本語系generatorで、attemptの`style_prefix`(sha、既存の`head200`/`sha256`形式)を`attempts_log`へ残す(Stdnarrator・KP_ENは既に残る=同じ形式に揃える)。API影響0。
2. **Gate**: `run_audio_gate`にZ用の`style_actual_vs_approved`を追加(新Gate工程ではなく既存gate関数への1検査): 共通8roleについて(a)採用attemptの実測shaが期待sha(`FAMILY_Z_ROLE_STYLE`)と一致、(b)`checked`が当該levelの共通roleごとに1件以上(空はBLOCK、`Z_STYLE_COVERAGE_EMPTY(role)`)、(c)`fallback_used`が真でStyle脱落(PD06等)はBLOCK→人間承認(既存`record_human_approval`系の流儀)、(d)`audit/style_actual_vs_approved.json`出力。Dialogue/SHELLは例外表の理由付きで検査対象外。
3. **test案**: (i)mockでAdv/JAの実測shaが入りmatch、(ii)期待shaと違うprefixを注入→BLOCK、(iii)checked空→BLOCK、(iv)fallback採用→BLOCK、人間承認で通過、(v)既存Z run fixtureでDefaultOff/出力不変(記録追加以外)、(vi)`CROSS_FAMILY_COMMON_STYLE_MAP`の既存drift testが通る。
4. **影響範囲**: Z音声生成の`attempts_log`記録追加とgate関数。既存公開音声は無変更(過去runはBLOCKでなく「実測未記録」警告扱いにして遡及しない設計を推奨)。TRU(TTS-RETRY-FALLBACK-LR-UNIFICATION)のfallback方針と衝突しないよう、TRU完了後に着手するのが安全。
5. **分類(案)**: B(承認済み仕様=Style一致とYの再発防止方針に対する検査不足)、重要度中(実害は現状1clip、Adv/JA roleは未検証)。Production挙動を変える検査追加なので、TRUと同様にOpus条件A(新しい検査構造)の要否をFableが判断。
