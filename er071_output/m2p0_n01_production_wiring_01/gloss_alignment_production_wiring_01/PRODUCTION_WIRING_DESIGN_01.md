# PRODUCTION_WIRING_DESIGN_01 (KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_01、2026-10-15)

Status: **DESIGN(設計のみ。Opus条件C待ち)**。`APPROVED_FOR_PRODUCTION`(ユーザー2026-10-15、修正版corrected)。`PRODUCTION_WIRED`は宣言しない。本委任でProductionコード・Prompt・flag既定値・test・runnerは一切変更していない(費用JPY0、有料API 0)。
根拠資料(再利用、再計測なし): `gloss_alignment_correction_01/{DESIGN_DRAFT_01,VALIDATION_03,INVESTIGATION_01,HR_RESOLVE_PROCEDURE_01,OPUS_REVIEW_01_VERBATIM}.md`、`gloss_alignment_default_off_01/VALIDATION_OFF_01.md`。
行番号は2026-10-15時点の実コード(HEAD 7857394b5)。事実=コード読取、推定/未確認は§13に分離。

## §0 超サマリ(非エンジニア向け)
1. 現状: 承認された「修正版gloss再整合」と、旧版(legacy)が**同じファイルに同居**し、`mode`という切替で使い分けている。Production既定は旧版・かつflagはOFF。
2. 良い知らせ: 完成禁止の仕組み(TTS保留・解説LLM停止・assemble拒否・ページ省略・HR報告書・Zのstage停止・解消後の再開)は**既に実装済みで、correctedの時だけ動く形**で入っている。配線の本体は「modeの分岐を消して、correctedだけを残し、既定をONにする」作業。
3. 入口は1か所: 全経路(X/Z、Std/Adv、retry、fallback、再生成)は `run_key_phrase_canonicalization`(scaffold L683-746)を通る。runnerがglossを直接再整合する箇所はない。
4. **OPEN-359**: 「Family Xが`NG_REVIEW_REQUIRED`を見ない」は**事実**(er019に該当語0件、L408で別のstatusを読む)。ただし**gloss不整合KPの流出経路にはならない**。glossのHR状態は「KPファイル本体」に書かれ、TTS・assemble・ページはその本体を直接読んで止まるため(根拠§6)。よってOPEN-359を直さなくても、今回の完成禁止Gateは迂回されない。ただし「冗長/記号NGのKP集合」が素通りする別問題は残る(最小修正案§6、範囲拡大になるためFable判断)。
5. 撤去対象(旧版): 関数11個+分岐1+定数9個+引数6系統+test約26件+Trial/証跡script参照7ファイル(§2)。`mode`概念ごと廃止を推奨。
6. 既定ON: `GLOSS_ALIGNMENT_ENABLED`を"1"へ。緊急OFFの環境変数は残す(承認済み仕様の無効化なので警告表示と記録を必須にする)。
7. 追加実装が必要な小さな穴(§4): (a)X Advanced解説のキャッシュがglossを見ない (b)Zのgloss規則preflightがrun開始時でない (c)Xのrun summaryに「KP段の最終status」が載らない(=OPEN-359の修正位置と同じ)。
8. 費用: 通常+0.014〜0.08円/記事セット(70円目標の約0.02〜0.11%)。Production実測は委任_02(出典§10)。TTSを含むE2Eの費用は**未確認**(§7で上限案とともに提示)。
9. 失敗注入は、本番コードに何も足さず「テスト用ハーネスが公式runnerを呼び、OpenAIクライアントの応答だけ差し替える」方式を推奨(§7-2)。
10. Fableが決めること: OPEN-359を今回どこまで直すか、Z kp stage署名の互換方針、旧Trial script群を壊れたまま残すか(§11)。

## §1 現状配線図(事実)

### 1-1 flag / mode / legacy / corrected の分岐点(`er003_key_words_gloss_alignment.py`=以下ga、`er003_v1_n3_01_scaffold_generate.py`=sc)
| 項目 | 場所 | 内容 |
|---|---|---|
| flag | ga:45 `GLOSS_ALIGNMENT_ENABLED`(env `EIGO_KP_GLOSS_ALIGNMENT`、既定"0"、**import時に1回評価**) / ga:48-51 `flag_enabled()` | 唯一のkill switch(KGA委任_03) |
| mode定数 | ga:506-510 `GLOSS_ALIGNMENT_MODE_LEGACY/CORRECTED/MODES`、`GLOSS_ALIGNMENT_MODE = legacy`(Production既定) | ga:531-535 `resolve_mode` |
| 分岐1(dispatch) | ga:416-427 `align_glosses(..., fallback_mode, mode, mapping_gate)`: `resolve_mode(mode)==corrected`なら`_align_glosses_corrected`(ga:861-896)、それ以外はlegacy本体(ga:428-456) | |
| 分岐2 | sc:724-726 schema(corrected時のみ`GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED`) | |
| 分岐3 | sc:732-738 corrected: `align_glosses(..., enabled=gloss_align.flag_enabled(), mode=...)` / legacy: `align_glosses(...)`(enabled未指定=ga:428で`GLOSS_ALIGNMENT_ENABLED`参照) | **ここが「唯一の入口」** |
| 分岐4 | sc:743-744 correctedのみ`gloss_alignment_unresolved_ranks`をresultへ | |
| 分岐5 | sc:807-842 `run_key_phrases`: corrected=最終artifactへHR報告(`emit_human_review_notice`、sc:828)+`result["gloss_alignment_human_review_events"]`+`status=STOPPED_GLOSS_ALIGNMENT_FAILED`(sc:834、既存`status`が無い場合のみ)、legacy=fallback event+NOTICE.md(sc:836-842) | |
| 分岐6 | sc:849/902-903 `_run_key_phrases_impl`がmodeを`run_key_phrase_canonicalization`へ受け渡し(legacy時は従来のcall形) | |
| X runner | er019:345 `run_theme_scaffold(..., gloss_alignment_mode="legacy")`、L404-406 `_gm_kwargs`(legacy時は渡さない)、L424-426 correctedのみsummaryへ`gloss_alignment_human_review_events`/`gloss_alignment_mode` | **CLIにgloss option無し**(VALIDATION_OFF_01 offcheck_01.json)→Productionは常にlegacy |
| Z runner | er026:929 `E2EContext.gloss_alignment_mode="legacy"`、L1166-1175 `_kp_fn_for_ctx`(corrected時のみ`canon_fn=partial(sc.run_key_phrase_canonicalization, gloss_alignment_mode="corrected")`)、L1234/1243/1249/1259-1262 correctedのみ(snapshot再開・`_gloss_hr_gate`・snapshot消費・kp_expl署名にgloss含有) | |
| Trial script | `er071_gloss_alignment_correction_01_trial.py`(先頭で`os.environ["EIGO_KP_GLOSS_ALIGNMENT"]="1"`)、`..._t3_mock.py`(modeを引数で渡す25箇所) | Production file→er071への`import`は**0件**(§8) |

### 1-2 gloss再整合が呼ばれる位置(Standard/Advanced × X/Z)
- **唯一の呼出元**: `sc.run_key_phrase_canonicalization`(sc:683-746)内 sc:731-738の`gloss_align.align_glosses`。`rg "align_glosses\("`で runner(er019/er026)・他productionからの直呼びは **0件**(Trial/test除く)。
- Family X(Std=a2/Adv=b1b、`main()`内`levels = ["a2","b1b"] if args.level == "both"`): `run_theme_scaffold`(er019:343、L406)→`sc.run_key_phrases`(sc:806)→`_run_key_phrases_impl`(sc:849、redundancy/symbol NG retryループ L879-950、上限`KEY_PHRASE_REDUNDANCY_RETRY_MAX`=2[er003_v1_n3_01_articles_generate.py:840])→`run_key_phrase_canonicalization`(sc:902-905)→align。
- Family Z(Std=a2/Adv=b1b): `stage_kp`(er026:1222)→`w62.run_kp_stage`(er062:931)→`kp_fn`=`w62.run_kp_with_outer_retry`(er062:971、canonicalization INVALIDで外側retry通算3、redundancy retry別カウント上限2)→`canon_fn`(既定`sc.run_key_phrase_canonicalization`、er062:978/1003)→align。**Zは`run_key_phrases`を通らない**(preflight・HR報告はstage_kp側で別実装)。
- その他の`run_key_phrase_canonicalization`/`run_key_phrases`呼出元(Production外のLegacy runner/Trial script、`rg -l`で約65ファイル。VALIDATION_OFF_01 §1表と同一集合): 既定ON化で同様に再整合が走る(消費側の完成禁止はX/Zのみ。§11論点6)。
- KP段の結果artifact: `keywords_canonicalized.json`(X: `<theme>/<level>/key_phrases/`、Z: `<run>/key_phrases/<level>/`→`<run>/<level>/key_phrases/`へcopy[er026:1153-1161])。itemごとに`gloss_alignment_status`(ALIGNED/FAILED_HUMAN_REVIEW_REQUIRED/HUMAN_RESOLVED)が書かれる。**消費側は全てこのartifactを直接読む**(§5、§6の根拠)。

## §2 legacy撤去範囲

### 2-1 撤去対象(`er003_key_words_gloss_alignment.py`)
| 種別 | 対象(行) |
|---|---|
| 関数(11) | `build_user_message`(168-191)、`kp_has_slot_word`(234)、`gloss_has_unjustified_slot`(239)、`validate_alignment_response`(245-278)、`run_alignment_gate`(294-316)、`revert_to_candidate_allowed`(319-334)、`apply_alignment`(337-404)、`build_gloss_alignment_fallback_record`(407-413)、`write_failed_notice`(462-480)、`format_failed_stdout`(483-491)、`resolve_mode`(531-535) |
| 分岐(1) | `align_glosses`のlegacy本体(428-456)+dispatch(424-427)→`align_glosses`をcorrected本体(現`_align_glosses_corrected`)へ置換 |
| 定数(9) | `FALLBACK_KEEP_KP`/`FALLBACK_REVERT_IF_SAFE`/`GLOSS_ALIGNMENT_FALLBACK_MODE`(53-55)、`SLOT_TOKENS`(57)、`_TILDE_RE`(58)、`GLOSS_ALIGNMENT_NOTICE_FILENAME`(459)、`GLOSS_ALIGNMENT_MODE_LEGACY/CORRECTED/MODES`+`GLOSS_ALIGNMENT_MODE`(506-510) |
| schema | legacy `GLOSS_ALIGNMENT_JSON_SCHEMA`(62-87)は`make_alignment_fn`既定値(ga:212)とcorrected schemaのdeepcopy元(ga:631)。**corrected schemaを直接定義して唯一のschemaにする**(schema内容・`name`文字列は無変更=VALIDATEDのAPI request bytes維持) |
| scaffold(sc) | 引数`gloss_alignment_mode`(684/807/849)、`resolve_mode`呼出(691/812)、分岐(724-726/732-738/743-744/816-817/821-842)、`_canon_kwargs`(902-903)。`run_key_phrases`の「legacy: fallback event/NOTICE」節(836-842)削除、corrected節(821-835)を無条件化 |
| X runner(er019) | `gloss_alignment_mode`引数(345)、`_gm_kwargs`(404-406)、summaryの条件付き出力(424-426)→無条件(`gloss_alignment_mode`キーは削除) |
| Z runner(er026) | `E2EContext.gloss_alignment_mode`(929)、`_kp_fn_for_ctx`のcorrected節(1170-1174)→素の`w62.run_kp_with_outer_retry`(canon_fn既定でalignが走る)、stage_kp内の`== "corrected"`条件4箇所(1234/1243/1249/1259)を無条件化 |
| test(`er003_test_key_words_gloss_alignment.py` 79件、`def test_`概数) | 削除: `Alignment`15(うちslot/fallback/revert系)、`ScaffoldWiring`1、`ScaffoldIntegration`3、`NoticeFiles`1、`ModeSeparation`4、`ScaffoldCorrected`のlegacy2 = **約26**。書換え(既定ON反転・mode引数除去): `DefaultOffIsolation`8、`PromptReuse`1、`ScaffoldCorrected`のmode引数2 = **約11**。無変更で残る: **約42**(TargetSelection7/RulesExtraction4/AddedWords4/ItemValidation7/ItemLevelRetry6/PromptCorrected4/HumanReviewReport5/ResolveGloss2等)。行数は委任_02で確定 |
| Trial/証跡script参照 | `er071_gloss_alignment_correction_01_t3_mock.py`(25参照、**modeを引数で渡す**→TypeError化)、`er071_gloss_alignment_01_replay.py`(4)、`..._census.py`(2)、`er071_completion_04_gloss_realign.py`(2)、`..._census_replay.py`(1)、`er071_gloss_alignment_correction_01_offline_audit.py`(2)、`..._offline_audit_02.py`(2)= **7ファイル**。方針: **T3 mockの27シナリオは保守対象のtestへ移植**(完成禁止の回帰証拠として必須。移植先は委任_02で決定、新管理機構は作らない)。それ以外の6ファイルは過去証跡の再現用で、legacy関数削除後は再実行不能になることを`HISTORICAL`注記(各ファイル冒頭1行)で明示し、修正しない |

### 2-2 残す物
`flag_enabled()`(ga:48)、corrected本体(`run_alignment_gate_corrected`/`apply_alignment_corrected`/`validate_item_corrected`/`build_user_message_corrected`/`check_added_word_mappings`/`added_content_words`/`collect_unresolved`/`build_hr_entries`/`validate_hr_report`/`emit_human_review_notice`/`format_hr_stdout`/`resolve_gloss`)、`select_alignment_targets`+`_extra_tokens`+`kp_adds_words_beyond_display`(対象選定、無変更)、`load_approved_gloss_rules`/`preflight`/`rules_sha256`/`make_alignment_fn`/`_usage_cost`/`DEVELOPER_MESSAGE`、`STATUS_*`/`STOPPED_STATUS`/`HR_*`定数、A'停止構造(§5)。
**内部helper名の`_corrected`接尾辞は委任_02では変えない**(関数名変更はVALIDATED挙動に影響しないが、Trial/testの参照面積を増やすだけ。接尾辞の整理は別作業。ただし「legacy」という語はコード・コメントから消す)。`mapping_gate`引数(既定False、Productionは渡さない)は残し、付随事項1(記録のみ)をtest `Production callers never pass mapping_gate=True` で固定。

### 2-3 `GLOSS_ALIGNMENT_MODE`は廃止(modeの概念自体を消す)
理由: (1)ユーザー§3A「旧legacyを撤去し、correctedと誤って共存しないようにする」=切替自体が共存の温床。(2)modeが残ると、Productionが誤って`legacy`で動く(引数ミス・Z `E2EContext`既定)経路が残り、完成禁止Gateを持たない旧挙動(fail-open)が復活しうる。(3)現状もmodeは「envでは切替えない・Python引数のみ」で、運用上の切替手段が無い=廃止しても運用機能は失われない。副作用: Zの`kp_expl_b1b`署名(§4 R6)と、Trial script 7本の再現性(2-1)。

### 2-4 撤去残置検出Grep(委任_02用、全て0件を期待。除外=`er071_output/`・docs・`*.md`・本design)
```
rg -n "GLOSS_ALIGNMENT_MODE|gloss_alignment_mode|resolve_mode\(|FALLBACK_KEEP_KP|FALLBACK_REVERT_IF_SAFE|GLOSS_ALIGNMENT_FALLBACK_MODE|SLOT_TOKENS|kp_has_slot_word|gloss_has_unjustified_slot|revert_to_candidate_allowed|build_gloss_alignment_fallback_record|write_failed_notice|format_failed_stdout|GLOSS_ALIGNMENT_NOTICE|gloss_alignment_fallback|validate_alignment_response|run_alignment_gate\(|apply_alignment\(|(?<!_)build_user_message\(.*gloss" --glob "er003*.py" --glob "er019*.py" --glob "er026*.py" --glob "er062*.py" --glob "!er071*"
rg -n -i "legacy" er003_key_words_gloss_alignment.py
rg -n "== \"corrected\"|'corrected'|\"corrected\"" --glob "er003_key_words_gloss_alignment.py" --glob "er003_v1_n3_01_scaffold_generate.py" --glob "er019_family_x_audio_production_runner_01.py" --glob "er026_family_z_fiction_production_runner_01.py"
rg -n "GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED|_align_glosses_corrected" --glob "*.py" --glob "!er071*"   # 唯一schemaへ統合後は0
```
(2行目: コメント含め`legacy`は0。Production外の他モジュールの「legacy」語は対象外のため、gloss_alignment.pyのみ。)

## §3 既定ON設計
- 変更: ga:45 `os.environ.get("EIGO_KP_GLOSS_ALIGNMENT", "1")`。判定は「`0/false/off/no`でOFF、それ以外ON」へ**反転して明示**(現行は`("1","true","on","yes")`がON=未設定でOFF。既定ON化で未設定→ON、`0`等→OFF。typoの`flase`等はON=安全側[承認済み仕様が動く側])。
- **緊急OFF(kill switch)は残すことを推奨**。理由: (1)モデル障害・API仕様変更時にコード変更なしで量産を止めずに済む。(2)現行の`flag_enabled()`+テスト+隔離確認(KGA)の資産をそのまま使える。(3)撤去すると「ONしか無い」ためtestのOFFケースが消え、Opus台帳OF-235の整合が崩れる。
- OFFは「**承認済み仕様の無効化**」である。運用条件(委任_02で実装・testする最小差分):
  1. OFFで起動したrunはstdoutの冒頭に`[GLOSS-ALIGN][WARN] DISABLED by EIGO_KP_GLOSS_ALIGNMENT=0 (承認済み仕様の無効化)`を1行出す(現状ga:428/866のDISABLEDは無言)。
  2. `gloss_alignment_status=DISABLED`をX summary level別に記録(現状Xはsummaryに載せない: VALIDATION_OFF_01 §3-1「限界」)。**DISABLEDをevidenceのPASSに数えない**。
  3. OFFの使用はDECISION_LOGに記録(委任文で明示許可された場合のみ)。
- **環境変数の読込時機に注意(事実+未確認)**: flagは`import ga`時(L45)に1回評価。`load_dotenv()`は`make_alignment_fn`内(ga:200)とer003_v1_en_direct_vfl_01_generate.py:39(import時)、er026:1713。**`.env`にEIGO_KP_GLOSS_ALIGNMENT=0を書いても、ga import後にdotenvが読まれる経路ではOFFにならない可能性がある**(未確認: Xのimport順)。kill switchは「プロセス環境変数で指定」と定め、`.env`で指定しないことを運用文書に書く。必要なら`flag_enabled()`をcall時評価に変える(2行)が、testがmodule属性をmonkeypatchしている(`_explicit_on`)ため委任_02では**変更しない**(論点7)。
- ON/OFFの揺れ確認(事実): `.env`にEIGO_KP_GLOSS_ALIGNMENT無し(`rg`)、起動script(.ps1/.bat/.sh)に設定無し(`ls *.ps1 *.bat *.sh`=該当0、`rg EIGO_KP_GLOSS_ALIGNMENT`はga/test/er071 Trial 2本/過去delegation_log checkのみ)、X/Z CLIにoption無し。Trial script(er071 2本)の明示`=1`は新既定と同値で無害。

## §4 後続経路の整合表(ユーザー§3B)
凡例: 走る=gloss再整合が呼ばれる / 走らない / 不要。根拠は関数:行。「X」「Z」はFamily、Std=a2、Adv=b1b。**「追加」=委任_02で実装が必要**。

| 経路 | Family X Std / Adv | Family Z Std / Adv | fail-open防止の根拠(古いglossへ流れない) | 対象外KPを変更しない根拠 |
|---|---|---|---|---|
| **R1 初回** | 走る(両level): `run_theme_scaffold`L343→`run_key_phrases`→canonicalization→align。Std/Adv同一コード。**追加**: 分岐撤去(§2) | 走る(両level): `stage_kp`L1222→`run_kp_with_outer_retry`→canon_fn→align。**追加**: `_gloss_hr_gate`/snapshot再開の無条件化 | HR時: itemに`FAILED_HUMAN_REVIEW_REQUIRED`を**artifactへ永続化**(ga:apply_alignment_corrected)→TTS/assemble/ページが`collect_unresolved(kp)`で拒否(§5)。ALIGN_PASS時のみ新gloss採用 | `select_alignment_targets`(ga:121)=`kp_extends_beyond_candidate`または追加語ありのitemのみ。対象外はLLM入力に含まれず、`apply_alignment_corrected`でmerged無変更(`items.append(it)`)。census 1,129 item中7(0.6%)が対象(DESIGN_DRAFT_01 §3.4) |
| **R2a KP段retry**(X: redundancy/symbol NG再選定、sc:879-950。Z: outer retry[canonicalization INVALID通算3]+redundancy retry上限2、er062:971-1038) | 走る(attempt毎に新KP集合へ再整合)。最終attemptのartifactが上書きで残る | 同左 | 新selection=新KP+新gloss→再整合が必要で、attempt毎にcanonicalizationを通るため必ず走る。HR報告は最終artifactに1回だけ(`run_key_phrases`はsc:828、Zは`_gloss_hr_gate`L1209):中間attemptのHRは孤児報告にならない(OF-KGDC-04) | 同上。最悪コール数: X (2+1)attempt×2=6、Zは外側3+redundancy2相当で≤12(`0.114/call`[VALIDATION_03 §3]×12≈1.4円。DESIGN_DRAFT_01の絶対最悪1.7円/記事セットと整合) |
| **R2b TTS retry cascade / Local Rewrite / audio retry** | 不要: gloss文字列は変えない。HR時はKP segmentが`generate`を呼ばれないのでcascadeに入らない | 同左(HR時は`load_level_inputs`L1283-1296で`FamilyZE2EStop`、TTS前) | 音声retryはgloss確定**後**の工程で、`canonical_text`(=`ja_gloss_tts`)は確定glossのまま(X: er019:1311、Z: er063:487) | glossに触れない |
| **R3 fallback** | M2→Strategy L fallback(selection段、sc:run_key_phrase_selection内)は**canonicalization/alignの前**に完了→alignは最終itemに走る。gloss旧fallback(KP短縮)はlegacyと共に撤去済み=**KPを短い候補へ戻す経路が無くなる**(ユーザー方針C) | 同左(Zは`selection fallback`+alignの順) | fallback後のKPにもalign。失敗はHR(KPは維持、旧gloss保持+blocking status) | 同上 |
| **R4 regeneration** | `--scaffold-only kp`は「KP成果物が既にあればSTOP」(er019:`_kp_already_generated`L334-340、Q5(iv))=自動再生成なし。KP再生成は成果物削除を伴う人手判断で、再実行時はR1と同じ(alignが走る) | `--regenerate-stage kp_a2/kp_b1b`(er026:1234-1235)は`regenerate=True`→**snapshotを使わず選定から**(L1234`ctx.regenerate_stage != f"kp_{lv}"`)→align走る。`ensure_stage`が`kp_expl_b1b`をstale化(er062:520)→明示`--regenerate-stage kp_expl_b1b`が要る | 再生成の都度align。stale解説は自動再利用されない(Z)。**X側のstale解説は下記R6** | 同上 |
| **R5 cache再利用(音声)** | KP wav: `_generate_or_reuse_kp`(er019:601)は`canonical_text==expected_text`(Std ja: `ja_gloss_tts`、L1310)でのみ再利用→glossが変われば再生成。Master Audio StoreはEnglish KP(`ensure_key_phrase_english_component`、gloss無関係)のみ | Z clip: `generate_or_reuse_z`(er063:577)の`reuse_key`に`canonical_text`のsha含む→gloss変化で再生成 | glossが音声に紐づく全cacheが**gloss文字列(=TTS入力)をキーに含む**ので、新glossは旧音声を再利用できない | 同左 |
| **R6 cache再利用(Adv英語解説text)** | **穴(追加)**: `_resolve_kp_explanations_text`(er019:912-934)のcache署名は`display_phrase`のリストのみ。glossは解説LLMの入力(L929)なのに署名に無い→「gloss変更後に旧gloss入力の解説textを再利用」しうる(HR解消後・再整合後の再実行)。**追加**: 署名にglossを含める。互換案=cached bundleに`gloss_signature`が**無い旧bundle**は従来どおり再利用(旧run互換)、**新bundleは`gloss_signature`一致も要求**(≈6行) | **穴(追加、互換方針要判断)**: `kp_expl_b1b`署名(er026:1259-1262)はcorrected時のみglossを含み、legacy時はdisplayのみ。mode廃止で「常にgloss含有」にすると既存Melos run(run_e2e_02等)の`kp_expl_b1b`が`FamilyZProvenanceMismatchStop`化する。互換案=`items`のうち`gloss_alignment_status`を持つitemが1つでもあればgloss含有署名、無ければdisplayのみ(pre-ON artifactは従来署名)。ただし「対象無しrun」はstatusが付かない(NO_TARGETS)ためpre-ONと区別不能→この場合もdisplayのみ署名=glossが変わっていないので安全。**論点4でOpusに確認** | 解説はgloss変更rankだけでなく5件まとめて再生成される(既存仕様、W4)。対象外KPのgloss自体は不変 |
| **R7 pre-ON成果物の再利用**(ON切替前に作ったKP artifact/Z kp stage) | X: 新scaffoldでartifact再生成(上書き)。pre-ON artifactは`gloss_alignment_status`未記録で「未評価」と区別不能 | Z: `ensure_stage("kp_*")`は入力(本文)shaのみで再利用→**pre-ONのkp結果はalignされないまま再利用される** | 量産run凍結(ACTIVE_TASK)で新規生成のみに限定。pre-ON runを再開する場合は`--regenerate-stage kp_*`が必要(費用発生)。**Production既存完成物(Melos run_e2e_01/02等)のgloss整合は本管理IDの対象外**(ユーザー§3Bの対象は新規生成経路)→残存リスクとして報告(論点5) | - |
| **R8 HR解決後の再開** | `resolve_gloss(<theme>/<level>/key_phrases/keywords_canonicalized.json, rank, gloss, 記録者)`(ga:1068)→`--stage tts`再実行(er019、HR_RESOLVE_PROCEDURE_01 手順3)。KP選定は再実行されない(artifactを直接読む)。**追加**: なし(既存) | 同じ`--stage kp`再実行。`_load_gloss_hr_resume`(er026:1181)がsnapshot(`gloss_alignment_pending_result.json`)を復元し`resolve_gloss`後の最新artifactを採用、再開後`.consumed.json`へ改名(L1249-1252)。**追加**: 無条件化のみ | `resolve_gloss`は`FAILED_HR/HUMAN_RESOLVED`のitemだけ書換え可(ga:1068以降の状態検査)。ALIGNED等のitemは`GlossResolveRejected` | HR待ちでないitemは書換え拒否 |

**追加実装セル(委任_02)**: R1(X/Z無条件化)、R6(X解説署名・Z解説署名の互換方針)、および§3の警告出力/DISABLED記録、Zのpreflight(下記)。
- Zのgloss規則preflight: `run_key_phrases`はrun開始時に`gloss_align.preflight()`を呼ぶ(sc:814、OF-229「抽出失敗はrun開始時に即時停止」)が、**Zは`run_key_phrases`を通らない**ため、抽出失敗は最初の対象itemのalign時(selection+canonicalization費用発生後)に出る。**追加**: `stage_kp`の冒頭に`ga.preflight()`1行(≈1行)。

## §5 完成禁止経路の実装対応表(ユーザー§3C)
| # | 要求 | 既存実装(関数・行) | 判定 |
|---|---|---|---|
| 1 | 2回失敗→非OK status | item: `apply_alignment_corrected`(ga:814-858)が`gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED`をartifactへ永続化。`run_key_phrases`: `status=STOPPED_GLOSS_ALIGNMENT_FAILED`(sc:833-834、`status`未設定時のみ)。segment: `_gloss_alignment_stopped_entry`(er019:525-534、0 API call) | **既存で満たす**(分岐撤去は§2) |
| 2 | Audio Validation Gateで完成禁止 | `verify_episode_audio_validation_gate`(assemble:469-)が`tts_generation_results.json`のkey_phrases非許可status(`AUDIO_GATE_ALLOWED_STATUSES`=VALIDATED/HUMAN_APPROVED、assemble:89,495)をblock。さらにGateが`tts_generation_results.json`無しで即return(assemble:472-473)するfail-openを塞ぐ`_assert_no_gloss_alignment_hr`(er019:1551-1563、呼出1582=B1/1790=A2) | **既存で満たす** |
| 3 | Zは既存`FamilyZE2EStop` | `_gloss_hr_gate`(er026:1199-1219)+`load_level_inputs`(L1283-1296、tts/provision_shell/gate/assembleの共有入力) | **既存で満たす**(`== "corrected"`条件撤去のみ) |
| 4 | Advanced B1英語解説の流出防止 | X: `_generate_key_phrase_segments_b1`が解説LLM(`_resolve_kp_explanations_text`)の**前**にHR判定して`_gloss_alignment_stopped_kp_results`(er019:966-971、0 API call)。Z: `stage_kp`のrunnerが`_gloss_hr_gate`で`FamilyZE2EStop`→`kp_expl_b1b`のrunner_ex(L1259-1275)に到達しない | **既存で満たす** |
| 5 | ページ表示への流出防止 | X: `_build_level_table`(er019:2008-2010)がHRなら省略+assemble未完了なら省略(L2002-2005)。Z: `build_pages`(er063:1405)はassemble済みtimeline/tts結果から作る(`build_page_rows` L1361)→assemble前に`FamilyZE2EStop` | **既存で満たす**(多重防御) |
| 6 | HR報告書 | `emit_human_review_notice`(ga:1013-1053、書込→再読検証→fail-closed[`GlossAlignmentNotificationError`])。X: sc:828、Z: er026:1209 | **既存で満たす** |
| 7 | run summary event | X: `scaffold_run_summary.json` level別`gloss_alignment_human_review_events`(er019:424-426、correctedのみ→無条件化)。Z: `<run>/gloss_alignment_human_review_events.json`(er026:1212-1215)。`event`にreport_sha256・downstream説明あり | **既存で満たす**(X summaryの「mode」キー削除とDISABLED記録は§3) |
| 8 | 最終stdout | X: `print_gloss_hr_final_line`(er019:2342-2362、main末尾L2520)。Z: `emit`時に`format_hr_stdout`をprint+`FamilyZE2EStop`メッセージ | **既存で満たす**(Zのmain終了時stdoutにFamilyZE2EStop文言が出るかは**未確認**、委任_02のevidenceで観測) |
| 9 | runのSTOP status | Z: `FamilyZE2EStop`→rc=2。X: **summaryにKP段のrun-level status(`STOPPED_GLOSS_ALIGNMENT_FAILED`/`NG_REVIEW_REQUIRED`)が載らず**、`key_phrases_status`はcanonicalizationのstatusのみ(er019:408、418)。rcは0。 | **追加必要(最小)**: summary level別に`kp_run_status=kp.get("status")`を記録(≈2行)。Xでrc非0にするかは**論点3**(既存M2 fallbackもrc 0で報告のみ) |

**集計: 既存で満たす8 / 追加必要1(X run-level status記録)**。注: 「既存」は"correctedモード時のみ動作"が実態で、無条件化(§2)が前提。消費側の拒否判定は全て`collect_unresolved(kp)`(ga:899)=状態をartifactに持つ構造(OF-KGDC-01〜02の推奨構造)。
T3 mock(27シナリオ、VALIDATION_03 §3-2、`trial_t3_rerun_02/T3_RESULTS.json`)が検証したのは上表の1〜8のmock再現(実API・実TTS 0)。実LLMが自然に2回失敗した例は0/145(前回88+今回57)=HR経路はmock/失敗注入のみで実証済み。

## §6 OPEN-359(Family X `NG_REVIEW_REQUIRED`素通り疑い)の実コード確認(受入条件)
### 6-1 疑いは**事実**
- `sc._run_key_phrases_impl`は、redundancy/symbol NGがretry上限(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`=2)で尽きたとき、artifact(`keywords_canonicalized.json`はcanonicalizationが既に書込済み)を残したまま`status="NG_REVIEW_REQUIRED"`を返す(sc:928-932)。
- X runner `run_theme_scaffold`(er019:408)は`kp_status = (kp["canonicalization"] or {}).get("status") ...`だけを読み、**top-levelの`kp["status"]`を見ない**。`rg -n "NG_REVIEW_REQUIRED|OUTER_RETRY_EXHAUSTED" er019_family_x_audio_production_runner_01.py`=**0件**。scaffold→tts→assembleは次のstageでartifactを直接読む(er019:784-796,1154-1159,1387,1648)ため、NG_REVIEW_REQUIREDでもTTS・assembleへ進める。Z `stage_kp`はL1239で`NG_REVIEW_REQUIRED/OUTER_RETRY_EXHAUSTED`を`FamilyZE2EStop`化(対照)。
### 6-2 gloss不整合KPが完成版へ流出しうる経路か → **今回の完成禁止Gateは迂回されない**(実コード根拠)
1. gloss再整合は`run_key_phrase_canonicalization`(sc:731-746)で**redundancy QAの前**に走り、結果(`gloss_alignment_status`と旧gloss)は同じ関数がredundancy QAの前に`keywords_canonicalized.json`へ書き込む(sc:745-746)。
2. 外側のNG_REVIEW_REQUIRED時点でartifactは**最終attemptのもの**(各attemptが上書き)で、HR itemが残っていればそのまま永続化されている。
3. X消費側は全て**artifactのitem status**を直接読む(`collect_unresolved(kp)`: TTS B1 er019:967、A2 L1282、assemble `_assert_no_gloss_alignment_hr` L1582/1790、ページ L2009)。`kp["status"]`(runの戻り値)には依存しない。→ NG_REVIEW_REQUIREDで戻り値statusが無視されても、HR itemは別経路で止まる。
4. HR報告書・eventは`run_key_phrases`の末尾(sc:821-835)で`final_merged`(=最終canonicalization)に対し、NG_REVIEW_REQUIRED時も出る(`if events and "status" not in result`は`status`を上書きしないだけでeventは載る)。
5. 反例探索: (a)`canonicalization`が非PASSで`merged`が無い→artifactが書かれず`kp=None`でKP segment自体を生成しない(er019:796,1159)/assemble `BLOCKED_KP_SCAFFOLD_MISSING`(L1575)。(b)retry途中のattemptでcanonicalization非PASSになり古いattemptのartifactが残る→残るのは**gloss整合済み(またはHR)** のartifactで、gloss不整合のまま通るartifactは生まれない(整合/HRのどちらか)。(c)flag OFF(kill switch)=仕様無効化(§3)。(d)alignの対象選定漏れ(`select_alignment_targets`が拾わない不整合)=選定段責務(ユーザー付随事項3の類推)。
結論: **OPEN-359は"gloss HR"の完成禁止Gateを迂回しない**。ユーザー§5太字の条件「OPEN-359未解決のままFamily Xで**不整合KP(gloss)**が完成版に流出しうる」は、コード上は成立しない。ただし**証明はtestで固定する**必要がある(委任_02: 「NG_REVIEW_REQUIRED+HR item」の組合せでX TTS/assembleが止まるintegration test)。
### 6-3 別問題として残るもの(gloss無関係)
redundancy NG/記号NG(`symbol_flagged`)のままKP集合がXでTTS・完成へ進む(音声化禁止記号を含むKPが読み上げに到達しうる)。これはOPEN-359本来の問題で、gloss再整合の受入条件ではない。
### 6-4 最小修正案(KP関所と同位置、範囲拡大になるため**Fable判断**)
- 位置: `run_theme_scaffold`のKP呼出直後(er019:406-409)。
- 案: (a)`kp_top_status = kp.get("status")`をlevel別summaryに記録(§5-9の追加と共通、≈2行)。(b)top-level statusが`{NG_REVIEW_REQUIRED, KP_ARTICLE_COST_CAP_EXCEEDED, STOPPED_GLOSS_ALIGNMENT_FAILED}`のとき、artifact(`keywords_canonicalized.json`)の最上位に`kp_stage_status`を追記(read-modify-write、≈6行)。(c)`_gloss_alignment_hr_unresolved(kp)`(er019:517)を「HR itemまたは`kp_stage_status`が非OK」で非空を返すよう一般化(≈4行)し、`_gloss_alignment_stopped_entry`のreasonを分岐(≈4行)。消費側(TTS B1/A2・assemble・ページ)は同じ関数を呼ぶので追加呼出なし。
- 見積り: 本番差分 **≈20行**(er019のみ)、testは新規≈60行(NG_REVIEW_REQUIRED単独・HRとの組合せ・解消後)。影響: X Std/Advの"冗長/記号NG"KPが止まるようになる=**Zと同じ挙動**。既存testへの影響: `er019*`421件のうち`key_phrases_status`/scaffold summary形に依存するtestがあれば更新(未確認、委任_02で`rg`確認)。
- **推奨**: 今回の受入条件(gloss)は6-2で満たされるため、(a)のみを委任_02に含め(HR/STOP status記録と同一箇所・≈2行)、(b)(c)はOPEN-359本体として別承認(Fable/ユーザー判断)。(b)(c)を今回含めると「採用範囲を広げない」(ユーザー§3末尾)に抵触しうる。

## §7 Runtime evidence計画(委任_02用、まだ実行しない)
前提(全run共通): 起動前に`docs/pm/delegation_log/*STOP_NOTICE*`・`<run>/STOP`・`er026_output/family_z_production_e2e_01/STOP_ALL`確認(`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run>`、本委任でも`--out`付きで実行[rc=0、stop=false])。再起動は委任文が明示許可した回数のみ。X/Zの`TTS_EXECUTION_MODE=STANDARD`を全TTS起動に明示(T-2、Batchは使わない)。本委任のflag確認: `GLOSS_ALIGNMENT_ENABLED`既定ON(§3実装後)。

### 7-1 取得項目
(provenance区分: fresh=今回新規取得 / reuse=既存証跡の再利用 / synthetic=mock・失敗注入・合成入力 / production_formal_path=Production正式runner関数・CLIを通過。**E2E自己確認=Yは「fresh Production初回pathを含むKP→TTS→assembleまで通した」場合のみ**)
| # | 項目 | 実行案 | provenance | 期待される観測値 | 費用 |
|---|---|---|---|---|---|
| E1 | X Std(a2)正式runnerでKP段・実LLM発火 | `env TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --level a2 --stage scaffold --scaffold-only kp --out-dir <新規evidence_x/run_a2_on_01> --budget-jpy 3`(入力=既存Coffee run dirから`entry_point.json`/`plan_run_result.json`/`a2/{a2_support_texts,parts,segment_plan}.json`/`a2/audit`のみcopy、VALIDATION_OFF_01 §3-1と同手順) | fresh+production_formal_path。自然target発生は約7%/記事(VALIDATION_03 §5)=**対象無しなら`NO_TARGETS`**(alignタグ0、正常) | `kp_gloss_alignment`タグ件数、`gloss_alignment_status`(ALIGN_PASS/NO_TARGETS)、model_id=`gpt-6-luna`、費用 | **約1.83円**(同手順の過去実測、VALIDATION_OFF_01 §3-1。alignタグ0件のOFF時の値。ON時の追加分は§10) |
| E2 | X Adv(b1b)同上 | 同コマンド`--level b1b`(入力は`b1b/`相当をcopy) | fresh+production_formal_path | 同上+解説LLM入力にgloss | **未確認**(a2のみ実測。b1bの単価は出典無し) |
| E3 | Z Std/Adv KP段(実LLM) | `.../er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run <新規run_kgcpw_z_01> --mode real --stage kp --regenerate-stage kp_a2 [--regenerate-stage不可の場合は別起動]`(KGA委任_03 §6'手順=Melos `run_e2e_02`をcopyした新規run) | fresh+production_formal_path | `a2_result.json`の`gloss_alignment_status`(DISABLED→ALIGN_PASS/NO_TARGETS)、alignタグ、Adv側は`kp_b1b`も再生成する場合のみ | a2のみ**約1.12円**(VALIDATION_OFF_01 §6')。b1b実LLM再生成は**未確認**(別単価) |
| E4 | **自然発火の保証がない**ため、real-LLM alignを確実に1回以上発火させる合成target | harness(§7-2)が`sc.run_key_phrase_selection`と`kc.run_canonicalization_gate`の戻りを**録画済みの既知ペア**(`based on`→`based on interviews`/gloss『～をもとにした』、Coffee KP #4、`completion_03`系の記録)で固定し、**`ga.make_alignment_fn`は本物(実LLM)**でX `run_theme_scaffold`(a2/b1b)・Z `stage_kp`を駆動 | synthetic入力+real LLM align+production_formal_path | 『インタビューをもとにした』へ修正(VALIDATION_03 P1型)、`current_gloss_consistent=true`の整合済み対照item(P2型)は書換0、対象外itemはAPI入力に含まれない、actual model_id/usage/cost_jpy | alignのみ0.114/call(VALIDATION_03 §3)×(Std1+Adv1)×対照ケース数≒**0.5〜1.0円**(算出根拠=単価×call数、未実測) |
| E5 | **異常系**: 2回失敗→HR→完成禁止(X Std/Adv、Z Std/Adv) | harness(§7-2)がOpenAIクライアント境界で`key_phrase_gloss_alignment_corrected`呼出の応答のみ不正JSON/不一致にして2回失敗させる(selection/canonicalizationはE4と同じ録画)。X: `--stage scaffold`→`--stage tts --only-segments <KP segments>`→`--stage assemble`、Z: `--stage kp`(停止)→`--stage tts_*`が`FamilyZE2EStop`か | synthetic(失敗注入)+production_formal_path | HR報告書(json+md、再読検証)、`status=STOPPED_GLOSS_ALIGNMENT_FAILED`、run summary event、最終stdout、**KP segment TTS API 0呼出**(`raw_usage_log.jsonl`にtts/asr 0)、B1解説LLM 0呼出、assemble `EPISODE_BLOCKED_BY_*`、ページ`table省略`、Z `FamilyZE2EStop` | JPY0(応答差替えのため。selection/canonicalizationも録画なら0) |
| E6 | HR解決後の再開 | E5のrunに`ga.resolve_gloss(...)`→X: `--stage tts --only-segments`再実行 / Z: 同`--stage kp`再実行(snapshot復元、選定再実行0) | synthetic+production_formal_path | status=HUMAN_RESOLVED、X: TTS API>0(KP segmentのみ)、Z: 選定API 0・`.consumed.json`、解説sigがglossを含む | TTS部分は**未確認**(下記E7) |
| E7 | **E2E完成確認**(TTS→assemble→ページ) | X: E1/E2のrun dirをcopyした新規dirで、KPのみ再生成→`--stage tts --only-segments`でKP segmentのみTTS→`--stage assemble`→`--stage player`。他segmentは`REUSED_VALIDATED`継承(validation_inheritance)。Z: `run_e2e_02`のcopyで`--regenerate-stage kp_*`後、変化したKP clipのみ再生成(`generate_or_reuse_z`のreuse_key) | fresh+production_formal_path(KP→TTS→assemble)。**E2E自己確認=Y(KP/TTS/assembleがfresh、他segmentはreuse)**。全文fresh再生成はしない(ユーザー§6「全記事再生成を避ける」) | assemble `OK`、ページ生成、KP gloss= ALIGN済みgloss、Playwright(Z `stage_page_verify`は`ER026_SKIP_PAGE_VERIFY`の扱いを確認) | **未確認**。素材: Melos run_e2e_02全体実費JPY62.83(COST_LEDGER_MELOS_01.md §4-§8、Z TTS+再生成込み、出典は同ledger)。KP segmentのみのTTS+ASR単価は出典なし→**委任_02開始時に`--stage tts --dry-run`相当/`E2E_TTS_CLIP_EST_JPY`(=1.0円/clip、er026:827)×clip数で上限を算出しFableへ提示してから実行** |
| E8 | Regression | `er003_test_key_words_gloss_alignment`、er003*(1667件+既存4 failure)、er019*(421)、er026*(86件+既存7)、er030*、er063(59)、`er008_audio_validation_gate_05_test.py`、`er011_*lock*_test`(Lock未使用の確認)。**共有state干渉のため§7-4に従い直列** | fresh | 新規failure 0(VALIDATION_03 §3-2/VALIDATION_OFF_01 §4の既存failure集合との差分で評価) | JPY0 |
| E9 | Std/Advともactual model_id・routing | `raw_usage_log.jsonl`/`cost_log.jsonl`のmodel_id、`routing.SUPPORT_MODEL`/`require_model("A2_SUPPORT"/"B1_SUPPORT")`(sc:719-722)。評価Trialではなく**Production line**(最新モデル原則の適用対象外、VALIDATION_OFF_01 §3-1と同様。本番ラインのモデル選定は別判断)。使用モデル=`gpt-6-luna`(KGA/KGDC実績)、最新性の再確認は未実施 | production_formal_path | alignの`response.model==model`(ga:`GlossAlignmentModelMismatchError`) | - |
| E10 | 量産費・追加時間 | E1〜E4のcost_log集計(`compute_cost_jpy_so_far`)とalign段のtimestamp差 | fresh | 追加費用/記事セット、追加秒(15〜50秒、VALIDATION_03 §5と比較) | - |

### 7-2 失敗注入方式の比較と推奨
| 案 | 内容 | Production差分 | 正式runner通過 | 長所/短所 |
|---|---|---|---|---|
| A | 環境変数/引数で失敗を指示するフックをProductionに追加 | **>0**(Trial専用フックが本番に残る) | ○ | ユーザー方針「Trial専用定義への暗黙依存を認めない」に反する。**不採用** |
| B | harnessが`ga.make_alignment_fn`をmonkeypatch(失敗する`fn`を返す) | 0 | ○(`sc._align_factory`がmodule属性`gloss_align.make_alignment_fn`を実行時参照、sc:726) | 簡単。ただし`make_alignment_fn`自体(`response.model`照合・usage記録)を通らない |
| **C(推奨)** | harnessがOpenAIクライアント境界(`openai.OpenAI`)を差し替え、`text.format.name=="key_phrase_gloss_alignment_corrected"`の`responses.create`のみ不正応答(2回: 不正JSON、または`current_gloss_consistent=true`なのにglossが異なる矛盾)を返し、他の呼出は実クライアントへ委譲(または録画応答) | **0**(harnessはevidence dir配下の新規ファイル) | ○(`make_alignment_fn`〜`run_alignment_gate_corrected`〜`apply_alignment_corrected`〜HR〜消費側の全体を通る) | 実コードのモデル照合・retry・usage記録まで本物。`provenance=synthetic(失敗注入)`と明記して実LLM evidenceと区別 |
Production差分0の確認方法: (1)harness実行の前後で`git diff --stat -- er003_key_words_gloss_alignment.py er003_v1_n3_01_scaffold_generate.py er019_family_x_audio_production_runner_01.py er026_family_z_fiction_production_runner_01.py er062_family_z_writer_01.py er063_family_z_audio_01.py`が空(委任_02の実装コミット後に固定した`sha256`と比較)。(2)harness内に`import er071`が無いこと。(3)harnessは`er071_output/.../gloss_alignment_production_wiring_01/evidence/`配下のみ新規作成。

### 7-3 E2E完成確認の最小run(T-2の4点)
- 条件(T-2): `TTS_EXECUTION_MODE=STANDARD`明示、Batch不使用、既存run dirの差分再生成(KP segmentのみ)、`--budget-jpy`/`--approved-budget-jpy`で上限、起動前STOP確認。
- X: 既存完成run dirをcopyし、KP段のみfresh(E1/E2)→TTSは`--only-segments`でKP segmentのみ→assemble。
- Z: `run_e2e_02`copyで`--regenerate-stage kp_a2`/`kp_b1b`→`stage_tts`は`generate_or_reuse_z`でKP clipのみ再生成→gate/assemble/pages/page_verify(`--local`)。
- 全文fresh生成(writer〜TTS全clip)は**行わない**(費用: run_e2e_02全体JPY62.83が実績上限の目安、COST_LEDGER_MELOS_01.md)。

### 7-4 X/Z並列実行と共有state干渉
- run dir・out_dirは別(X: `er019_output/<slug>/<run>`派生、Z: `er026_output/family_z_production_e2e_01/<story>/<run>`)で衝突しない。
- **共有state(両runnerが書きうるrun外ファイル、`er026_family_z_e2e_integration_test_01.py:26-38`のMONITORED_FILES/DIRS)**: `er006_output/master_audio_store_01/manifest.json`、`.../reuse_telemetry.jsonl`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er006_output/pronunciation_ledger_01/ledger.json`、`er011_output/attempt_history.jsonl`、`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`、`er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl`、`er030_output/kp_backend_telemetry_01/telemetry.jsonl`、`er005_output/cost_baseline_01/cost_summary.json`、dir: `er011_output/local_rewrite_recovery`、`user_test/family_z_melos_01`。KGDC Regressionで実際に干渉(`test_shared_state_files_unchanged_by_mock_run`等、VALIDATION_03 §3-2)。
- 結論: (a)KP段のみ(E1〜E5の非TTS部分)は主に`er030 kp_backend_telemetry`/`er005 cost_summary`への追記のみ(未確認: 書込の有無はコード読取のみ[sc/`er005_*`参照]、実測は委任_02)=X/Z並列可(追記の競合は`jsonl`でも順序のみ)。(b)**TTS段(E6/E7)はmanifest.json/ledger.json/attempt_history等を更新するため、X-TTSとZ-TTSの同時実行は不可**(直列、理由=同一state競合)。(c)**Regression(E8)は他のどのevidence runとも同時に走らせない**(`test_shared_state_files_unchanged_by_mock_run`が観測する共有stateを他runが書換えるため)。並列化の効く範囲=「X KP段」「Z KP段」「harnessの失敗注入(JPY0・TTS無し)」の3本同時。
- 並列短縮見込み: 直列でKP実LLM3本約20〜60秒/本のため合計は数分差。主な律速はTTS E2E(E7)とRegression(E8)の直列。**並列化による短縮は小さい(≈数分)**(推定、実測は委任_02)。

### 7-5 総費用見積り(出典付き。未確認は未確認)
| 項目 | 費用 | 出典 |
|---|---|---|
| E1 X Std KP実LLM | 約1.83円 | VALIDATION_OFF_01 §3-1(同手順の実測) |
| E2 X Adv KP | 未確認 | 実測無し |
| E3 Z Std KP(a2のみ) | 約1.12円 | VALIDATION_OFF_01 §6'(1.1191) |
| E3' Z Adv KP実LLM | 未確認 | 実測無し |
| E4 合成target+実align | 約0.5〜1.0円(算出) | 0.114円/call(VALIDATION_03 §3、平均単価)×call数。実測は委任_02 |
| E5/E6の失敗注入 | 0円 | 応答差替え(selection/canonicalization録画の場合) |
| 通常のalign追加(自然発火時) | +0.014〜0.08円/記事セット、最悪0.57、絶対最悪1.7 | VALIDATION_03 §5 / DESIGN_DRAFT_01 §5 |
| E7 TTS E2E | **未確認** | 参考: Melos run_e2e_02全体 JPY62.83(COST_LEDGER_MELOS_01.md)。KP clip限定の単価は出典なし |
| 合計(KP段+合成+注入、TTS除く) | 約3.5〜7円(E1+E3+E4を足した下限、E2/E3'未確認分を除く) | 上記の合算(未確認分を含まない) |

## §8 Dangling Reference Check(ユーザー§3D)
新仕様・Prompt・Validatorの参照先と、承認済みProduction仕様+正式初回経路での存在確認。
| 参照物 | 実体の場所 | 正式初回経路に存在するか | 確認方法(委任_02で実行) |
|---|---|---|---|
| 承認済みgloss規則 | `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(ga:41)。Production選定Promptの`bk.PROMPT_TEMPLATE_PATH`(er003_b1_p2_keywords.py:39)と**同一path**。DB Hybrid選定も`bk.load_prompt_template()`(er030…:543)で同一テンプレート | ○(事実)。段落抽出ga:134-148、sha256 `447e07cb…`固定test | 既存test(`RulesExtraction.test_sha256_pinned`)+`rg "b1_p2_keywords_l_prompt_template"`で参照先が1テンプレートのみ |
| 課題指示文(correctedのuser/developer message) | `ga.build_user_message_corrected`(ga:645)・`DEVELOPER_MESSAGE`(ga:59) = ga内。Trial script・docs非依存 | ○ | `rg "import er071|from er071"`=Production 0件(本委任で実行済み)。Prompt本文のsha固定test(§9 golden)を追加 |
| schema | ga内`GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED`(ga:631) | ○(統合後は唯一) | §2-4 grep |
| 機械検査(span) | `check_added_word_mappings`(ga:592)、`FUNCTION_WORDS`(ga:541) | ○ | unit test |
| Validator(記号) | `safety.detect_prohibited_symbols`/`kc.convert_display_gloss_to_tts_text`(er003共通、Production既存) | ○ | - |
| HR報告 | `ga.emit_human_review_notice`、`validate_hr_report`、`_render_hr_md`(ga内) | ○ | - |
| resolve | `ga.resolve_gloss`(ga:1068) | ○。ただし**運用手順書はer071_output配下の`HR_RESOLVE_PROCEDURE_01.md`のみ**(Trial成果物置き場) | **Dangling候補**: 手順書をProduction運用文書(例: 既存`docs/`のrunbook相当、または`CURRENT_SPEC`のHR節)から参照できる位置へ移す/リンクする(委任_02) |
| 消費側の関所 | `_gloss_alignment_hr_unresolved`/`_assert_no_gloss_alignment_hr`(er019)、`load_level_inputs`/`_gloss_hr_gate`(er026)=各runner内 | ○ | §5 |
| retry/fallbackだけに存在する仕様 | なし(correctedは共通入口の1か所。retry・regenerationも同一関数を通る) | ○ | §4 R2/R4 |
| Trial専用定義への暗黙依存 | Production→er071の`import`は0件。Trial script→Production依存はあるが逆向き | ○ | `rg -n "import er071|from er071" --glob "*.py" --glob "!er071*"`=0 |
| 旧Trial scriptの壊れた参照 | 7ファイル(§2-1)がlegacy関数を参照 | **検出あり(Production外のみ)** | 委任_02で`HISTORICAL`注記。T3 mockはtestへ移植(移設先) |
| ドキュメント参照 | `HR_RESOLVE_PROCEDURE_01.md`冒頭「Trial専用」「Production既定(legacy)では発生しない」 | **検出あり**(文書の陳腐化) | 委任_03で現行化 |
**Dangling検出: Production→Trial依存0件。ただし運用手順書の置き場(er071_output配下)と旧Trial scriptの壊れ参照を検出**(対処は上表)。

## §9 Opus台帳対応表(台帳本体は編集しない)
状態=`docs/pm/OPUS_FINDINGS_LEDGER.md`列(2026-10-15時点、`awk`抽出)。`CLOSEOUT_CONFIRMED`にするために委任_02で確認すること。
| OF | 現在状態 | 委任_02での確認事項 |
|---|---|---|
| OF-225 BLOCKER(採用位置づけ未確定) | IMPLEMENTED(委任_01) | ユーザー採用(2026-10-15)をDECISION_LOG記録済み(本委任)+corrected唯一化後の正式経路evidence(E1〜E4) |
| OF-226(課題指示文と承認規則の「～」) | IMPLEMENTED/一部置換 | 課題指示文にスロット許可文が無い・承認規則sha不変(既存test)+E4でP3型(『～』正当表現)の書換0 |
| OF-227(fallback(i)の不整合) | IMPLEMENTED/一部置換 | fallback(i)撤去のgrep(§2-4)0件+KPを戻す経路が無いtest |
| OF-228(FAILED通知のみ・Human Review送りなし) | IMPLEMENTED/一部置換 | E5(HR報告・summary・stdout・STOP・下流停止) |
| OF-229(規則抽出堅牢化) | IMPLEMENTED | 既存test + Zのpreflight追加(§4)のtest |
| OF-230(「～」決定論チェック) | IMPLEMENTED/一部置換 | `gloss_has_unjustified_slot`撤去済み(§2-4)+『～』が合否に使われないtest |
| OF-231(有効性の定量根拠) | IMPLEMENTED | VALIDATION_03 §2(P1 6/6等)の再利用+E4の再現 |
| OF-232(費用見積り) | IMPLEMENTED | E10で実測値を§10と比較 |
| OF-233(usageの費用ログ) | IMPLEMENTED | `kp_gloss_alignment`タグ付きraw_usage_log(E1/E4)。canonicalization側記録はOPEN-358別件 |
| OF-234(Z音声test・meの一般化) | IMPLEMENTED | er063 59件PASS(E8) |
| OF-235(承認前の既定ON) | CLOSEOUT_CONFIRMED(既定OFF時点) | 既定ON化後は意味が変わる(承認済みのため)。台帳に「ユーザー採用によりOFF措置は終了、kill switchのみ存続」と追記要(Fable) |
| OF-KGDC-01 BLOCKER(Lock流用fail-open) | IMPLEMENTED/TRIALED | Lock不使用(`rg "human_review_lock|record_outcome" ga`=0)+E5/E7でA2のStopped entry→Gate block |
| OF-KGDC-02 BLOCKER(B1解説/ページ流出) | IMPLEMENTED/TRIALED | E5 Adv: 解説LLM 0呼出・ページ省略 |
| OF-KGDC-03(HR解消後の再開) | IMPLEMENTED/TRIALED | E6(X/Z) |
| OF-KGDC-04(中間attempt/重複HR) | IMPLEMENTED/TRIALED | 最終artifactのみで1報告(R2a)、retry中のHRが孤児にならない |
| OF-KGDC-05(「届いた」の定義) | IMPLEMENTED/TRIALED | E5で報告書再読検証・fail-closed |
| OF-KGDC-06(機械検査は最小・record-only) | IMPLEMENTED/TRIALED | ユーザー付随事項1承認済み。Production callerが`mapping_gate=True`を渡さないtest |
| OF-KGDC-07(P3から規則15行型除外) | IMPLEMENTED/TRIALED | ユーザー付随事項3承認済み(選定段責務) |
| OF-KGDC-08(P7) | EVIDENCED | VALIDATION_03のP7 0/12の再利用 |
| OF-KGDC-09(item単位retry) | IMPLEMENTED/TRIALED | unit test(既存) |
| OF-KGDC-10(真なら不変の比較正規化) | IMPLEMENTED/TRIALED | unit test(既存) |
| **OF-KGDC-11(OPEN-359 X素通り)** | FABLE_DECIDED(別OPEN) | §6の結論をtestで固定(NG_REVIEW_REQUIRED+HR itemでX TTS/assemble停止)。(b)(c)はFable判断 |
| OF-KGDC-12(mode切替でProduction保護) | IMPLEMENTED/TRIALED | **本管理IDでmode廃止=意味が変わる**。「保護はmodeでなくflag(kill switch)+ユーザー採用で担保」へ更新要(Fable) |

## §10 QDC見込み
- **C(量産単価)**: 通常 +0.014〜0.08円/記事セット、最悪約0.6(外側retry込0.57)、絶対最悪約1.7(出典: VALIDATION_03 §5、DESIGN_DRAFT_01 §5/`cost_01.json`)。70円/記事セットに対し **約0.02〜0.11%**(0.014/70=0.02%、0.08/70=0.114%。VALIDATION_03 §5は0.13%と記載=丸め差)、最悪0.86%、絶対最悪2.4%(いずれも算術)。Production実測は委任_02(E10)。
- **D(時間)**: 対象itemがあるlevelのみ+15〜50秒(VALIDATION_03 §5)。対象はitem 0.6%・記事の約7%。Z outer retryの最悪は上記コール数。
- **HR頻度**: 実LLMで2回失敗0/145(前回88+今回57)。95%上限は標本依存で約0.2%/記事level未満(VALIDATION_03 §5)。**実LLMでretry経路は一度も発火していない**=HR経路の実証は失敗注入のみ。
- **Q**: 誤NG最小化=整合済みgloss不変(P2 0/4・P3 0/16・P7 0/12、書換0/32、95%上限8.9%)、不整合検出T2 12/12(合算36/36)。
- 回避すべき悪化: ON化で`kp_gloss_alignment`が常時呼ばれるため、**対象itemがある記事の割合(約7%)が想定より高い場合**はE10でアラート(基準は委任_02開始時にFableが設定)。

## §11 Opus条件Cレビュー用の論点整理(優先順、8項目)
1. **legacy撤去の安全性**(ユーザー§4: 撤去範囲/既存gloss規則との整合): §2の関数11・分岐・定数・引数・test約26件。VALIDATED時の**API request bytes(user/developer message・schema name・内容)が無変更**であることをgolden test(sha)で固定する方針で十分か。`*_corrected`接尾辞を残す判断は妥当か。
2. **完成禁止の網羅性**(§5): 既存実装8+追加1(X run-level status)。Xのrcを非0にしないまま「runのSTOP status」を満たすと言えるか(`print_gloss_hr_final_line`+summary status)。Gate自体のfail-open(assemble:472-473)は`_assert_no_gloss_alignment_hr`で塞いでいるが、他に`tts_generation_results.json`無しで通る経路はないか。
3. **OPEN-359の結論**(§6-2): 「gloss HR gateは迂回されない」の論証(artifact直読み)に反例はないか。(b)(c)を今回含めるか別承認か(「採用範囲を広げない」との整合)。
4. **cache/署名の互換**(§4 R6/R7): X解説署名の`gloss_signature`互換案、Z `kp_expl_b1b`署名の「statusを持つitemがあれば」条件案の妥当性、pre-ON成果物(Z kp stage再利用でalign未実施)の扱い。代替案=署名にalignment versionを含め全再生成(既存Melos完成物のprovenance互換を壊す)。
5. **旧Trial script群の扱い**(§2-1/§8): 壊れたまま`HISTORICAL`注記で残す案 vs T3 mockのみtest移植案 vs 全て保守。
6. **default-ON波及**(§1-2): X/Z以外の約65 scriptが既定ONで再整合を走らせ、消費側ゲートが無い。許容(Production runnerはX/Zのみ)か、`run_key_phrase_canonicalization`に呼出元の明示opt-inが要るか。
7. **kill switch設計**(§3): 残置+警告+記録で十分か。`.env`経由が効かない可能性(未確認)をどう扱うか。import時評価をcall時評価へ変えるべきか(testのmonkeypatch資産との兼ね合い)。
8. **QDC・誤NG**(§10): 実LLMでretry/HR未発火(0/145)のままProductionに出す残存リスク。対象率の想定外上昇時の監視指標。
代替案: Aに「Zの`kp_expl_b1b`署名はmode廃止後も従来署名のまま、gloss変化は`--regenerate-stage kp_expl_b1b`の明示」(署名変更なし)がある。設計者(Sonnet)が不安な点: (i)X TTS B1の`_generate_or_reuse_kp`のcanonical_text照合とexplanation textのcacheの二重管理、(ii)Zのmain終了時stdoutに停止理由が出るか未確認、(iii)テストを26件削除する際の網羅性低下(完成禁止のtestはT3 mock 27件の移植で補うが移植先が未決)。

## §12 委任_02の作業分解と見積り
| # | 作業 | 内容 | 依存 | 見積り | 並列 |
|---|---|---|---|---|---|
| W1 | 実装(ga/sc) | §2撤去、既定ON、警告出力、DISABLED記録 | Opus条件C | 1.0h | W2のtest準備と並列可(同一ファイル編集なし) |
| W2 | 実装(er019/er026) | 無条件化、X summaryに`kp_run_status`、X解説署名`gloss_signature`、Z preflight、Z署名(論点4の決定) | Opus条件C | 0.7h | W1と別ファイルなので並列可 |
| W3 | test | 旧26件削除・11件書換、T3 mock移植、golden sha、NG_REVIEW_REQUIRED+HR組合せ、mapping_gate固定、kill switch | W1/W2 | 1.0h | - |
| W4 | harness作成(§7-2案C) | evidence配下に新規。W1/W2と並列で先行作成可 | 設計のみ | 0.5h | W1/W2と並列 |
| W5 | evidence取得 | E1/E3/E4(KP段並列可)→E5/E6(失敗注入、並列可)→E7(TTS E2E、直列)→E8(Regression、単独直列) | W1-W4 | 1.2h(E7の費用承認待ちを除く) | KP段3本+注入は並列、E7/E8は直列(共有state、§7-4) |
| W6 | SSOT・commit/push | CURRENT_SPEC本文更新・OPEN・台帳対応表の事実整理(台帳遷移はFable) | W5 | 0.3h | - |
合計約3〜4h(委任文見積りと整合)。直列の理由: 実装→test→evidenceの前工程出力依存、E7/E8は共有state競合。

## §13 設計者が本委任で確認できなかった事項(推定と事実の区別)
- **未確認**: (1)Xの`import`順で`load_dotenv`がga importより前か後か(§3、`.env`kill switch可否)。(2)KP段のみ実行で`er030 kp_backend_telemetry`/`er005 cost_summary.json`に実際に書込むか(コード参照は確認、実測なし)。(3)Zのmain終了時stdoutに`FamilyZE2EStop`文言が出るか(`FamilyZE2EStop`→rc=2はMelos証跡で既知)。(4)`er019*`421件中、`key_phrases_status`/summary形に依存するtest(§6-4)。(5)X Advのb1b KP段の実LLM単価、KP clip限定のTTS+ASR単価、Z Adv KP実LLM再生成単価。(6)E4で使う録画済みCoffee KP #4の入力(selection/canonicalization応答)がどのartifactに保存されているか(`completion_03/gloss_check_03.md`系の存在は確認、raw応答の保存有無は未確認→無ければ合成入力でitemを構築し`kc`出力相当を手書きする)。(7)テスト件数はdef test_のgrep概数(79件の分類は読取による推定、委任_02で確定)。(8)最新モデル原則: `gpt-6-luna`が現時点の最上位/推奨系かの再確認は本委任で未実施(KGA/KGDC記載に依拠)。
- **推定**: 並列短縮「数分」、HR頻度上限、worst-caseコール数(コード読取から算出)。
- **事実(コード読取)**: §1の分岐点・§2の撤去対象行・§5既存実装の行・§6の素通り(`rg`0件)とartifact直読みの構造・Production→er071 importが0件・launcher/.envにflag設定が無いこと。
- コード・Prompt・flag・test・runnerは本委任で未変更(`git status --porcelain`の差分は設計文書・SSOT・一時ファイルのみ)。
