# IMPLEMENTATION_DESIGN_01: 固有名詞発音の新方針(アラーム受理+TTS発音供給)のFamily X/Z配線設計(委任_01)

管理ID: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 / Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(Production既存ファイル未編集)。Opus条件A(新しい処理フロー: 固有名詞不一致の受理分岐+アラーム経路+Ledger→TTS供給)のレビュー対象。調査=`INVESTIGATION_01.md`、衝突=`CONFLICTS_01.md`。
未配線module: `er103_proper_noun_alarm_policy_01.py`(受理判定・アラーム記録・run層derive)、`er103_pronunciation_tts_supply_01.py`(Ledger階層→綴り置換供給)。test=`er103_proper_noun_alarm_policy_test_01.py`(51件PASS)。

## 1. 設計の骨子(1枚)
1. **受理は「最後の最後」**: Tier3/CMU Case A/homophone/M1/CS Equivalence/Secondary許容集合/統一judgeの全層を通って`NG_BOTH`(`secondary_not_accepted`)で終わった場合にだけ、adapterが固有名詞専用の最終救済を1回評価する(既存救済が解決すればそちらが先=挙動不変)。
2. **受理=leafにはPASS(status OK)として返す**。したがってretry loop・HR queue・HR Lock(`record_outcome`が`RESOLVED`)・`approve_regenerate`のいずれも経由しない(承認操作不要の要件が構造的に満たされる)。新しいHR関連の分岐やLock状態は作らない。
3. **追加API 0**: 受理判定は既に取得済みのPrimary/Secondary転写の再分類だけ(純関数)。Stage 1の調査(`_resolve_unresolved_entity_for_review`)は現行と同じ条件で1語につき高々1回(Ledger/否定記録キャッシュ済みなら0回)呼ぶ=**HR packageの代わりにアラームの根拠欄へ載せる**(用途変更、重複なし)。
4. **初回attemptで受理して再試行しない**(原文②)。既存のattempt上限・Tier3/M1/Cascade/Secondary呼出は先に1回適用済みの状態で判定する。受理により、固有名詞だけの不一致で最大3回回っていたTTS+ASR+Azureが1回に減る(費用減方向)。
5. **範囲は承認どおり狭く**: 英語ナレーション5 role(FULL_STORY[Z対話clip含む]/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE)のみ、Family X/Z runnerのscope内のみ、KP(`dual_required`/KEY_PHRASE)・見出し・日本語・一般語・数値/否定・語の脱落・音声欠落・Secondary障害は従来どおり。
6. アラームは**`audit/`配下の運営者用ファイルのみ**に書き、公開ページ生成には渡さない(§6)。既存`PASS_WITH_WARNING`事後試聴リストは無変更・別区分。
7. TTS供給は既存の綴り置換思想を踏襲し、A階層自動/B階層は`human_approved`のみ/ESTIMATEDは供給しない(§8)。**Family A/B/C共有の`er003_v1_n3_01_tts_generate.py`は編集しない**(X/Zのtext整形点の直後に1関数を挟む)。

## 2. 受理条件(機械的定義)

### 2-1. 入口(evaluate_alarm_eligibility、`er103_proper_noun_alarm_policy_01.py`)
| ID | 条件 | 根拠・既存との関係 |
|---|---|---|
| G0 | flag有効∧run scope∈{X,Z}∧言語=en∧role∈5ナレーションrole∧`dual_required`=False | `is_active_for_run()`が単一読取関数。scope未設定(A/B/C・単体)は完全に従来どおり。role解決は既存`er020…resolve_narrative_role`(Tier3と同じ5 role) |
| G1 | 統一judgeが`NG_BOTH`∧reason=`secondary_not_accepted` | 実judgeで確認済み(test `RealUnifiedJudgeEntryConditionTest`)。値/否定差=`NG_PROTECTED`/`secondary_*_diff`、除外表=`NG_EXCLUDED`、Secondary障害=`NG_SECONDARY_UNAVAILABLE`は入口で不通過 |
| G2 | Primary分類=`ASR_VALIDATION_UNCERTAIN`∧全diffが`entity_like` | 既存`is_entity_like_mismatch`と同定義(数値/否定差なし・非固有名詞の内容語差なし・TTS_FAILUREでない・canonical側が空の語追加diffはentity_like=Falseで不通過) |
| G3 | Secondary転写あり。Secondary側diffの扱い: Primaryも同じcanonical語句で差がある位置=entity_like(または同名詞+所有格's)であること / **Primaryがcanonicalと一致している位置のSecondary-only diffは「Azure固有の揺れ」として受理判断から除外し`secondary_only_noise`に記録** / ただしSecondary diffがPrimary diffの固有名詞tokenに隣接する語まで巻き込む場合(`melos drank`→`mellow strength`)は、その隣接語がASR側に残っていなければ不受理 | Primary PASS時にSecondaryを参照しない既存設計と整合。Melos「Mellow Strength」型を除外 |
| G4 | Primary diff数<=3 | 文が大きく違う疑いはfail-closed |
| G5 | 各Primary diff: 置換(canonical・ASR とも非空=語の脱落でない)∧canonical全tokenに固有名詞根拠∧句の全tokenが一般語でない∧ASR語数<=canonical語数×2∧ASR側に数値/否定語なし∧despaced類似度>=0.40 | 下記2-3 |

### 2-2. 固有名詞の根拠(`proper_noun_evidence`)
いずれか: (1)Ledger登録語(`ledger_disabled`除外、語単位) (2)CMU未収録語(造語・外来語・ブランド名: Melos/Khaite/Bisnow等) (3)文中(文頭以外)の大文字始まり(`L. Mimoun`のイニシャル後は文末扱いしない) (4)周囲がALLCAPSでない単独ALLCAPS語(ELLE等)。**文頭の大文字だけ(CMU収録語)は根拠にしない**。供給で綴り置換した語(Kate←Khaite)は`supply_map`で固有名詞扱い(`supplied_respelling`)。

### 2-3. 誤分類リスク(一般語を固有名詞として許容してしまう)の評価
| リスク | 防御 | 残存リスク |
|---|---|---|
| 文頭の一般語(Retail等)が`capitalized_flags`でentity_like | 文頭大文字だけでは根拠不足(`R_NOT_PROPER_EVIDENCE`)。全token一般語(CMU∧zipf>=4.0)も不受理(`mini→many`) | 文頭のCMU収録ブランド(Meta/Apple)はLedger未登録だとHR残(取りこぼし側=安全) |
| 一般語に化けた固有名詞(Melos→mellow/mallow) | これは受理対象(canonicalが固有名詞でASRが近い綴りの一般語に聞こえたケース。承認方針の中心) | ASRがcanonical固有名詞を完全に別の一般語へ書き換えた場合は類似度0.40未満で不受理 |
| ASR側の語追加(Melos→Mellow Strength) | ASR語数上限+類似度+G3隣接語規則 | 閾値は暫定(校正88イベント)。Opusレビュー対象 |
| 見出し語/ラベル(`Main Story`、`One Voice:`)の脱落 | 語の脱落は不受理 | なし |
| 数値・否定 | G1/G2/G5の三重で不通過 | なし |
境界例(unit testで固定): 受理=`Melos said.`→`Mello said.`(+Azure`Mellow`)、`Khaite's`→`Kite's`、`Stephen Reicher`→`Steven Reichert`、`Altuzarra`→`also zara`、`Muse`→`use`。不受理=`Melos drank`→`mellow strength`(Secondary隣接語)、`Meink`→`mc`(類似度)、`Mini`→`many`(一般語)、`Toteme and Khaite`→`Toteme`(脱落)、`3`→`5`(数値)、`increase`→`decrease`(非固有名詞)。

### 2-4. 校正結果(API 0、保存HR queue 88イベント)
`INVESTIGATION_01.md` §3。受理45(51%)、不受理43。M1後12イベント中受理1。校正スクリプト=`calibrate_replay_01.py`、結果JSON=`calibrate_replay_01_result.json`。

### 2-5. TTS供給語の扱い
供給語(Khaite→Kate)はcanonical(=TTS入力)に`Kate`として現れ一般語に見える。`register_supply`→`lookup_supply(canonical_text)`で`supply_map`をadapterが取得し、G5で置換後tokenを固有名詞扱い(類似度は原綴り/置換後の近い方)。アラームrecordの固有名詞は原綴り(Khaite)、`tts_input_token`にKate。LR等でtextが変わった場合は一致せず、fail-closed(HR側)。

## 3. 処理順序とadapterの変更(配線設計。**本委任では未編集**)
`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail`の`jr = unified_judge(...)`(:1124)と`result["verified"] = bool(jr.verified)`(:1146)の**後**、`else:`(NG)ブロック内の`_tech_only`算出(:1170)の**前**に1ブロックを挿入する。擬似コード:
```
else:   # not jr.verified
    result["final_status"] = cls.classification; result["classification"] = cls; (既存technical_stop処理)
    _tech_only = (jr.state == NG_SECONDARY_UNAVAILABLE)                               # 既存
    if not _tech_only and pnap.is_active_for_run():                                    # ★新規(単一読取関数)
        lk = pnap_supply.lookup_supply(canonical_text)
        dec = pnap.evaluate_alarm_eligibility(canonical_text=..., primary_cls=cls, secondary_cls=captured.get("cls_s"),
                 primary_text=asr_text, secondary_text=sec.get("text"), judge_state=jr.state, judge_reason_code=jr.reason_code,
                 role=judge_role, lang=lang, dual_required=_dual, ledger_surfaces=<Ledger語集合>, supply_map=lk["supply_map"])
        if dec.accept:
            basis = {noun: <_resolve_unresolved_entity_for_review(noun) の戻り+_stage1_take()の階層/出典> ...}   # 既存関数を同条件で再利用
            recs = pnap.build_alarm_records(dec, ..., supply_info=pnap_supply.supply_info_for(...), ledger_info=basis[...], models=...)
            audit["state"] = pnap.STATE_ALARM; audit["pronunciation_alarm_records"] = recs; audit["pronunciation_alarm"] = pnap.alarm_audit_block(dec, recs)
            result["verified"] = True; result["final_status"] = pnap.STATE_ALARM
            result["classification"] = ClassificationResult("PASS_WITH_PRONUNCIATION_ALARM", cls.normalized_ratio, cls.protected, should_pass=True, should_retry=False, reason=...)
            (既存のHR要求ブロック `if is_last_slot and not _tech_only:` はスキップ)
    if not accepted:  (既存どおり: 最終slotならhuman_review_required=True + pronunciation_lookups)
```
- `result["stop_retrying"]`は従来どおりFalse。`audit["warnings"]`は触らない(PASS_WITH_WARNINGに混ぜない)。
- `evaluate_attempt_with_cascade`(:628-636)は`human_review_required`がFalseなので`_log_human_review`を呼ばない=HR queueに追記されない。
- Cascade OFF(`cascade_enabled=False`)・`dual_required`・JA adapter(`er007_ja_secondary_asr_01.py`)は無変更。
- KPDUAL/Tier3/M1/CS Equivalenceの内側コードは1行も変更しない。**閾値・Prompt・正規表現・辞書の直接編集なし**。

### 3-1. 既存retry/fallback/regeneration/resumeとの整合
| 機構 | 整合 |
|---|---|
| attempt上限(`build_attempt_ctx`のtotal_slots) | 不変。受理はそのattemptで`verified=True`にするだけ。後続のdisfluency/repetition QA/length gate(`final_length_ok`)は従来どおり独立にANDされ、これらがNGなら通常どおり次attemptへ(同一固有名詞の再アラームはrun層derive・共有ログのalarm_idで重複排除) |
| fallback(minimal instruction/ENGLISH_LOCK) | 受理は標準経路・fallback経路のどのslotでも同じadapterで発火。KP 4回構成はKP role除外で無関係 |
| A2 6%減速後再検証 | `_post_slowdown_unified_judge`も同adapter。減速前後でrecord(alarm_id)は別、報告は採用entry(減速後)のみ(CONFLICTS (m)) |
| Local Rewrite(LR) | LRは最終slot NG後の機構。固有名詞のみNGは受理で完了するためLR起動条件に到達しない(LR後の`script_version=v1`再判定は従来どおり) |
| M1 | 先に適用済み。M1が受理すればアラーム経路に入らない |
| resume/Store再利用 | §5-5。保存`asr_judgement`(state=ALARM+records)を継承。再利用ガードは値/否定ガードのみ |
| HR Lock | status OKなので`RESOLVED`。HR Lock関連コード無変更。OPEN-371とは独立(CONFLICTS (g)) |
| 既存`PASS_WITH_WARNING` | 別区分。同一segmentにSECONDARY_CONFIRMED等の警告が無いため通常は競合しない。警告が併存する場合は`audit["warnings"]`に残り事後試聴リストの条件(state==PASS_WITH_WARNING)には載らない(alarm stateが優先) |
| `human_approved`済みsegment | `check_before_generation`が先に停止(HUMAN_APPROVED)。アラーム経路は通らない |

## 4. 新区分 `PASS_WITH_PRONUNCIATION_ALARM`
- `asr_judgement.state`に新値を追加(統一judge自体は変更せず、adapterが監査recordへ設定)。`PASSING_STATES`(judge内)・`er078_pass_with_warning_registry_01.PASSING`は無変更=**事後試聴リスト(公開ページの補助節)に載らない**(test `test_registry_does_not_leak_to_pass_with_warning_listening_list`)。
- 完成状態の定義: 「アラーム付き完成」。確認・承認は完成の必須条件でない。
- 許容集合に追加が必要な箇所(§5-5): 継承再判定の`("PASS","PASS_WITH_WARNING")`3箇所。

## 5. 配線点一覧(X/Z)
| # | 対象 | 変更 | 位置 |
|---|---|---|---|
| 5-1 | adapter | §3のブロック挿入(1か所、X・Z共通) | `er006_secondary_asr_01.py` :1146付近 |
| 5-2 | X runner scope | main/`run_*`冒頭で`pnap.enter_scope("X")` | `er019_family_x_audio_production_runner_01.py`のstage実行入口(B1B :~990 / A2 :~1388の`run_tts_*`冒頭) |
| 5-3 | Z runner scope | `pnap.enter_scope("Z")` | `er026_family_z_fiction_production_runner_01.py` main(:2060-2120)および`er063_family_z_audio_01.run_tts_stage`入口 |
| 5-4 | TTS供給(text整形点の直後) | X: `n3_tts.tts_safe_news_en(text)`(:962,:1361)・`tts_safe_en`系(:910,:927,:1314)の戻りに`_pnap_supply(text)`を適用 / Z: `_norm_for_tts`(`er063:760-768`)の戻りに適用。`_pnap_supply`=`plan_supply(Ledger読取)→apply_supply→register_supply`(flag OFF時は恒等) | 上記行。**共有`er003_v1_n3_01_tts_generate.py`は編集しない** |
| 5-5 | 再利用・継承 | `rejudge_with_current_judge`/`_j11_adopted_judgement`の許容集合`("PASS","PASS_WITH_WARNING")`に`PASS_WITH_PRONUNCIATION_ALARM`を追加(3箇所)し、alarmのときは再判定で値/否定ガードのみ検査して元recordを`asr_judgement_inherited`へ保持 | `er019_family_x_validation_inheritance_01.py:236,305,323` |
| 5-6 | 生成完了hook | `pww_registry.write_listening_list_safe(out_dir)`の直後に`pnap.write_run_alarms_safe(out_dir)`(例外を握りつぶす非ブロッキング版を配線時に追加) | X: `er019:1008, 1397` / Z: `er063:1172-1175` |
| 5-7 | 完成報告 | stage終了時に`audit/operator_alarm_report.md`の内容を標準出力へも出し、RESULT_PACKETへ貼る | 同hook |
| 5-8 | Ledgerスキーマ(additive) | `upsert`の任意キー(`er006_pronunciation_ledger_01.py:192`)に`human_approved`/`human_approved_by`/`human_approved_at`/`tts_respelling`を追加。旧entryは不変 | `er006_pronunciation_ledger_01.py` |
| 5-9 | 運営承認CLI | `er103_pronunciation_approve_cli_01.py`(新規): `--surface --respelling --approved-by`でB階層entryを`human_approved=True`にし、`tts_respelling`を登録。共有ログへ承認履歴 | 新規 |
| 5-10 | flag既定 | 配線時に`PROPER_NOUN_ALARM_POLICY_ENABLED=True`/`TTS_SUPPLY_ENABLED=True`(ユーザー承認済み仕様=既定ON)。起動script/.envでの暗黙ONはしない | 各module |

## 6. アラーム記録・完成報告・非露出
### 6-1. 記録(ユーザー承認③の必須項目を満たす)
record(`build_alarm_records`): `proper_noun`/`location`(wav_path・sha256・原稿文・文脈・近似秒)/`mismatch`(原稿・Primary転写・Secondary転写・類似度・固有名詞根拠)/`pronunciation_basis`(根拠階層・確信度・hint・IPA・出典)/`tts_supply_result`(供給した/しなかった+理由+階層)/`final_state`=`PASS_WITH_PRONUNCIATION_ALARM`・`final_state_ja`=アラーム付き完成/`models`(actual model ID・routing: adapterから`asr_judgement.adapter`と`tts_model_id`を転記)。`alarm_id`=family|article|level|segment|wav sha|noun のsha256(決定的、冪等)。
保存先: (1)`asr_judgement.pronunciation_alarm_records`(原本、tts_generation_results.json内)、(2)run層`<level_dir>/audit/pronunciation_alarms.json`+`operator_alarm_report.md`(`write_run_alarms`が採用entryから再導出・冪等、PWW registryと同方式)、(3)共有ログ`er006_output/audio_retry_cascade_prod_01/pronunciation_alarms.jsonl`(履歴・append-only・alarm_id冪等、配線側が書く。**テストは必ずtempfileで実行**=OPEN-447の混入再発防止)。
### 6-2. 完成報告への掲載
`render_operator_report`が記事完成報告用のMarkdown節(0件でも「0件」と明記)を生成。対象固有名詞・音声箇所・検出した不一致・発音の根拠/確からしさ・TTS発音改善結果・最終状態を含む。RESULT_PACKET/ER-REPORTへ貼る。
### 6-3. 集約表示
同一固有名詞が記事内の複数clipに出る場合(Z Melos)、reportはnoun単位に「Melos × k clip」と集約してclip一覧を併記(record自体はclip単位)。*(配線時に`render_operator_report`へ集約を追加)*
### 6-4. 一般リスナー非表示
- `write_run_alarms`は`<run>/audit/`にしか書かない(test `test_write_run_alarms_writes_only_under_audit_and_is_idempotent`)。
- 公開ページ(`index.html`/`standard.html`/`advanced.html`)の生成関数は`pww_registry`のみを読み、`pronunciation_alarms`を参照しない。配線時に**静的test**を追加: ページ生成module(`er063…build_*`/`er019…`のhtml生成部)のソースに`pronunciation_alarm`/`operator_alarm`の文字列が現れないこと、生成済みHTMLに`PASS_WITH_PRONUNCIATION_ALARM`/`アラーム付き`が含まれないこと(runtime evidenceでも確認)。
- 将来の本番配信: 運営者専用の確認面は別設計(本委任範囲外)。それまではaudit/(非公開)+完成報告のみ。

## 7. 旧ルール・旧検査の整理(撤去/残置/Status整理候補)
| 項目 | 扱い | 理由 |
|---|---|---|
| 固有名詞のみ不一致でのHR投入(`er006:1176-1197`) | **残置(コード無変更)**。到達しなくなる(受理で`verified=True`) | 範囲外(KP/見出し/一般語/G5不通過)のHR経路は必要。撤去すると範囲外が無防備になる |
| Stage 1 HR package表示(`pronunciation_lookups`/`hr_display`) | 残置。受理経路では同じ調査結果を`pronunciation_basis`へ流用(重複排除) | 用途追加、API増なし |
| OPEN-318/327/330/331/335(固有名詞ASR救済系) | **Status整理候補**(閉じる判断はFable/ユーザー): 受入後に各行の役割(HR温存/救済/Verdict記録)と新方針の重なりを確認 | 配線委任で個別Grep→Fable判断 |
| `ASR_VALIDATION_UNCERTAIN`の`stop_retrying`系 | 残置(統一judgeで`stop_retrying=False`固定) | 無影響 |
| 静的辞書`{"Reicher":"Riker"}` | 残置(Family A共有)。供給moduleは二重適用しない | `static_overrides`で検査 |
| テスト | `er006_secondary_asr_01_test.py`等の「entity_like→HR」期待は、flag既定ON化で変わるものが出る可能性 → **scope未設定[A/B/C・単体]では従来どおり**のため既存testは無変更で通る設計(§9で確認) | 回帰 |
Dangling Reference洗い出し(配線後に実施するGrepリスト): `human_review_required`参照元、`pronunciation_lookups`参照元(HR UI/`user_test/human_review.html`)、`ASR_VALIDATION_UNCERTAIN`の出力先、`PASS_WITH_WARNING`の許容集合(`"PASS", "PASS_WITH_WARNING"`の全箇所)。

## 8. TTS発音供給(原文①)
- **方式**: 既存の綴り置換(静的辞書→Ledger駆動)。`plan_supply`(Ledger読取・判断)→`apply_supply`(置換)→`register_supply`(ASR比較canonicalと監査の受け渡し)。A階層=自動、B階層=`human_approved=True`のみ、ESTIMATED/未検証/取得なし=供給しない(実Ledger38件は全て`evidence_tier`未保存のため初期の自動供給は0件)。
- **A階層の判定(暫定、Opus対象)**: `evidence_tier==QUOTE_VERIFIED`(Stage 1のV1'引用実在確認)∧出典ホストが参照辞書/百科(wikipedia/merriam-webster/oxford/cambridge/collins/britannica/ldoce)またはsurface名を含む公式ホスト。媒体(nylon等)はB。
- **respelling**: 人が承認登録した`tts_respelling`を優先。無ければ`pronunciation_hint`が「CMU収録語のみ・<=3語・ハイフン/数字なし」のときだけ機械採用(例`kate`→Kate)。音節表記(`al-tuh-ZAIR-ah`)・非語(実LedgerのKhaite=`KAYT`)は採用しない。
- **Stage 2 Trial知見の期待値反映**: 効くのはKhaite型(綴りに追従する語、8/8)のみ。Meink(A階層でも制御不能)・Altuzarra(ASRが原綴りを書く)は供給しても不一致が残る→**アラーム記録の`tts_supply_result`に「供給したが不一致」と残る**。誤供給は置換後比較で通ってしまう(Meink→Mink)ため、安全性はA/B階層ゲートと人承認に依存する。期待効果は限定的(Khaite型のHR削減、実測2〜3 segment/最大9)であり、本設計の主効果は**アラーム受理による停止解消**。供給は補助。
- **同一語の複数entry**: respellingが食い違う場合は供給しない(`R_CONFLICT`)。`ledger_disabled`/`tts_injection_disabled`/`ja_reading_katakana`は対象外。
- **重複排除**: 供給で解消できる語(Kate置換が効く)は、そもそも不一致が出ず(アラームなし)、効かない場合のみアラームに残る。Stage 1の調査はアラーム根拠の取得として維持。
- **既存style注入(hint注入)**: 無変更で併存(Trial: 効果弱[Khaite 2/8])。二重供給の矛盾は、置換語にhint注入が重ならないよう`pronunciation_hint`注入は原surfaceに対して行われる(置換後textにsurfaceが無い)ため自動的に非発火。

## 9. test計画
| 区分 | 内容 | 状況 |
|---|---|---|
| unit(新module) | 受理境界・範囲ゲート・供給階層・record・derive・非露出(audit限定)・PWW非混入・実judge入口条件 | **51件PASS**(`er103_proper_noun_alarm_policy_test_01.py`) |
| DefaultOffIsolation | flag未設定でAPI 0・出力不変・副作用ファイル0 | PASS(`DefaultOffIsolationTest`、scope未設定ONでも不活性=`RunScopeTest`) |
| wiring(配線委任で作成) | (1)adapter: flag ON×scope X/Z×固有名詞のみ不一致→verified True・HR queue不追記・`human_review_required`False・state ALARM (2)同条件でscope未設定/KP/dual/JA/見出し→従来どおりNG・HR (3)Secondary障害→技術STOP不変 (4)resume/継承でalarm保持 (5)公開ページ文字列に非出現 (6)X/Zの`_pnap_supply`がflag OFFで恒等 |
| Regression(既存、配線前後で同一結果) | `er006_secondary_asr_01_test`/`_m1_wiring_test_01`/`er006_multi_diff_judge_fix_test_01`/`er078_asr_unified_{judge,en_wiring,backcompat_07,wiring_05,06c,06d,06e,10,11,13}_test_01`/`er078_pass_with_warning_registry_01_test_01`/`er011_human_review_lock_01_test_01`/`er097_pronunciation_supply_stage1_01_{test,wiring_test}_01`/`er094_multiword_homophone_01_test_01`/`er026_family_z_*`/`er063_family_z_*`/X runner系(`er019_*`)/validation inheritance系 |
| Validator | 既存の`docs/pm/tools/`の該当checker(user_test page checker等)で公開ページにアラーム非出現 |
| 固定入力 | 校正88イベントを`calibrate_replay_01.py`で再実行し受理45/不受理43が再現(閾値変更時の回帰検出) |
| 単体テスト隔離 | 新テストは共有ログ・HR queue・Ledgerに書かない(tempfileのみ)。配線テストはpath引数で隔離 |

## 10. runtime evidence計画と見積(配線委任で実施)
- 日次: 本日(2026-10-22 JST)の既使用 約JPY800+KPMP進行中(<=150)で上限1,000円に近い → **実行は翌JST日(2026-10-23)以降**を前提(見積と計画のみ本委任で確定)。
- 方針: 正式runnerのsegment限定再実行(X: `--only-segments`、Z: `--only-clips`)で、固有名詞不一致が再現しやすい既存素材を使う。
  - **X**: Khaite/Toteme/Altuzarraを含むFamily X記事(`er019_output/…`のfashion mini-bag記事)の本文1〜2 segment(B1B+A2)。保存データでKhaite含むsegmentは現行TTSで9/10がHR→自然発火率が高い。
  - **Z**: Melos記事の短いclip(`Melos said.`型/`The guards went still when Melos spoke.`型)2〜3 clip。M1後のMelos HRは3イベント/9日=低頻度のため、確率的発火を前提に最大3 clip×3 attemptの上限で設計。
- 見積(Stage 2 Trial実単価: TTS 0.64円/回、OpenAI ASR 0.11円/回、Azure STT 0.29円/回 ⇒ 1 attempt ≒ 1.0〜1.3円。Stage 1調査[Perplexity]は固有名詞1語につき高々1回・既存のキャッシュ/否定記録で2回目以降0):
  | 項目 | 見積(上限) |
  |---|---|
  | X 2 segment × 最大3 attempt × 1.3円 | 約8円 |
  | Z 3 clip × 最大3 attempt × 1.1円 | 約10円 |
  | Stage 1調査(未調査語最大4語 × 約5円と仮定) | 約20円 |
  | 公開ページ生成・再現確認(API 0) | 0円 |
  | **合計(上限、再起動1回分の余裕込み)** | **約80円(案件300円以下)。7-7によりAI自律実行可。日次1,000円は翌JST日で余裕** |
  ※ 調査単価は未確認の仮定。実行前に直近のStage 1実費ログ(`paid_calls`)で再見積する。
- 確認項目(原文§5・§7): 発音情報取得・TTS供給が正式経路で動作 / 不一致時アラーム記録+制作継続 / HRに回らない / 通常ASR・retry・fallback・resumeとの整合 / 固有名詞以外の不一致は従来どおり検査 / アラームが完成報告まで引き継がれる / 公開ページ非露出 / actual model ID・routing / X・Z両方の発火証拠。
- 自然発火しない場合: 既存の保存音声(同一wav)に対し同判定を再実行するAPI 0のreplayでは「発火証拠」に当たらない(正式runner経路のruntime ≠ replay)。再実行は委任文が許す回数内で別素材へ切り替える(同一素材の反復はしない)。

## 11. ロールバック手順
1. `PROPER_NOUN_ALARM_POLICY_ENABLED=False`(単一定数)→ adapterの★ブロックが即不活性(現行とバイト一致、test `DefaultOffIsolationTest`で担保)。HR経路が従来どおり復活。
2. `TTS_SUPPLY_ENABLED=False` → `_pnap_supply`が恒等(置換なし)。Ledgerの追加キーは読まれない。
3. 既に出力された`audit/pronunciation_alarms.*`と共有ログは追記専用の記録で、削除不要(消費者なし)。
4. 追加したLedgerキー(`human_approved`等)は旧コードから無視される(additive)。

## 12. 量産単価・速度への影響
- 追加API呼出 **0**(判定は保存転写の純関数。Stage 1調査は現行と同じ条件・同じ回数、HR package作成を廃止してアラーム根拠へ流用)。
- 固有名詞のみ不一致での再試行(最大3回のTTS+ASR+Azure≒3円/segment)が1回に減る→**量産単価は下がる方向**。HR人手時間も固有名詞のみ不一致分が減る。1日15作品での頻度は未検証(原文§3-3)。
- 追加CPU: 受理判定は文字列処理のみ(ms)。

## 13. Opus条件A レビュー観点への回答
| 観点 | 回答 |
|---|---|
| 新構造の妥当性 | 新規の状態機械・Lock状態・承認フローを作らない。既存`unified_judge`の出力(`NG_BOTH`)を入口に、adapter内の1分岐で`verified=True`へ変換する。leaf以降(Lock/queue/retry)は既存の「status OK」経路そのまま。PASS_WITH_WARNING registryと同方式の再導出(別store・二重管理なし) |
| 既存Gateとの整合 | KP両方PASS(OPEN-440)・数値/否定ガード・M1/Tier3/CS/Secondary許容集合・除外表・技術STOP(OPEN-371)・HR Lock・Family A/B/C不変(run scope)を全て先行/維持。KP固有名詞は実run 132 phraseで0件 |
| 安全条件 | 承認範囲外はfail-closed(role/言語/KP/見出し/脱落/一般語/数値・否定/Secondary障害)。flag既定OFF→配線時のみON(承認済み)。scope未設定は不活性。隔離が破れた場合の失効は11-7に従う(承認済みのため例外適用ではなく通常のProduction配線) |
| 副作用 | 固有名詞の実誤読が常態化しても気づけるよう、アラームを完成報告に必ず載せる。取りこぼしリスク=受理の偽陽性(一般語を固有名詞扱い)→G5の多重防御+暫定閾値(Opus確認)。供給の誤供給リスク→A/B階層ゲート・respelling機械検査 |
| テスト十分性 | §9。入口条件は実judgeで検証済み。配線後は§3の既存回帰+新規wiring/DefaultOff |
| 未解決(Opusに確認したい点) | (1)G3の「Secondary-only diffは除外」が品質上許容か(Primary PASS時はSecondary非参照という既存設計と同型だが、Primary NG後の文脈では緩和度が上がる) (2)閾値0.40/3diff/ASR語数2倍の妥当性 (3)A階層の出典ホスト規則の暫定リスト (4)run scopeを`enter_scope`のprocess内状態で持つ方式(既存`secondary_run_scope`と同型)で十分か |

## 14. 想定リスクと対処
| リスク | 対処 |
|---|---|
| 受理の偽陽性で、一般語の誤読が固有名詞扱いで通る | G5多重防御+校正88件+アラームで必ず可視化。偽陽性が見つかれば閾値は定数で即調整(コード分岐の追加なし) |
| アラーム多発で報告が冗長 | noun単位の集約表示(§6-3) |
| 供給の誤供給で誤発音が固定 | B階層は人承認のみ、機械respellingは「CMU収録語のみ」に限定、衝突時は不供給 |
| runner scopeの設定漏れ | 設定漏れ=不活性(従来動作=HR)で安全側。wiring testでX/Z両runner入口の設定を検証 |
| 継承再判定の許容集合の取りこぼし(§5-5) | 3箇所をGrep(`"PASS", "PASS_WITH_WARNING"`)で網羅し回帰 |

## 15. 委任_02: Opus条件A反映(OF-PNAP-P-01〜15)。§2/§3/§5/§7/§13のうち本節と矛盾する記述は**本節が優先**
Opus全文=`OPUS_REVIEW_COND_A_01.md`。Fable採否=必須7+推奨全て採用(P-09はFable規則)。実装=`er103_proper_noun_alarm_policy_01.py`/`er103_pronunciation_tts_supply_01.py`/`er103_pnap_runner_hooks_01.py`/`er103_pronunciation_approve_cli_01.py`、test=`er103_proper_noun_alarm_policy_test_01.py`(52)+`er103_pnap_wiring_test_01.py`(66)。

| 指摘 | 反映(設計の修正点) |
|---|---|
| P-01 | §2-1 **G1に追加**: `audit["p3_entry"]=="p3_primary_ng"`(adapterは`audit.get("p3_entry")`を渡す)。force_secondary/primary_length_ng/primary_pass_demoted_ambiguous_value由来のNG_BOTHは不受理(`P3_ENTRY_NOT_PRIMARY_NG`)。dualはG0で既に除外 |
| P-02 | §2-2(3)を修正: 文中大文字がCMU収録語の根拠になるのは、**文頭/コロン・引用符・括弧直後/一般語だけのTitle Case連なり/role=TOPIC_INTRO以外**。CMU未収録・Ledger語・単独ALLCAPSは従来どおり根拠。人名句(連なりに語彙外語を含む)は可 |
| P-03 | §2-1 G5に追加: Primary・Secondary両方のASR側句が全token一般語(CMU∧zipf>=4.0)なら不受理(`ASR_SIDES_ALL_GENERAL_WORDS`)。ASR側が一般語に崩れた句は、原稿綴り(despaced)4文字以下なら類似度>=0.5、ASR語数<=原稿語数。低頻度語への崩れ(kite/mellow/totem/mink)は維持 |
| P-04 | G3に追加: Secondaryだけの**非固有名詞**差(entity_like・固有名詞と合成されたspan・所有格'sだけのspanを除く)は<=2件、noiseで内容語2語以上の連続脱落は不受理(`SECONDARY_ONLY_NOISE_LIMIT`)。上限対象を非固有名詞に限定したのは、Khaite文で他の外来語(ELLE/minaudiere)をAzureだけが聞き違える実例(HR queue 10件)をOpus趣旨(非固有名詞差の抑制)から外れずに受理するため |
| P-05 | §5-5を修正: (i)継承は`rejudge_with_current_judge`でアラーム元entryをNG_BOTH後に**現行定数・現行Ledgerで`evaluate_for_adapter`を再評価**(scope外・flag OFF・Secondary転写無し・境界外は再判定NG)。`_j11_adopted_judgement`はALARM時Primary転写。受理時は現runのsegment/wav/shaでrecordを再構築 (ii)`er078_reuse_value_guard_01.guard_entry`(全再利用点の共通ガード)でALARM音声は`is_active_for_run()`外ではblocked=再生成 (iii)auditの`pronunciation_alarm`に`tts_input_text`・`pre_supply_text`・`supply_map`・`supply_decisions`を保存し再判定に使う |
| P-06 | §8を修正: 供給の置換は大文字小文字区別(全小文字登録のみIGNORECASE)。小文字形が一般語(Nice/Muse/Gap等)なら文中の大文字始まりのみ置換(文頭・引用直後は不変) |
| P-07 | §8 A階層を修正: A = QUOTE_VERIFIED ∧ 出典hostが参照辞書/百科またはhostの**ラベル単位**がsurfaceと一致 ∧ (人の`tts_respelling` または hint由来respellingが当該host引用`evidence[].quote`に語として現れる)。Wikipediaも同条件。整合しない/引用なしはB扱い=人承認必須 |
| P-08 | §6を修正: `audit/pronunciation_alarms.json`に`consistency`(ALARM state件数=report件数)を記録、不一致は報告に明示。results未作成の途中失敗は『0件』でなく『アラーム集計失敗』を書く。hookは`run_with_alarm_hook`のfinally(STOP/途中失敗でも実行)でX/Zとも標準出力へも出す。X assembly summaryに`pronunciation_alarm_audit`を埋込、Zは`stage_tts`結果に埋込。記事単位集約=`aggregate_article_alarms`。継承recordは現runのsegment/wavで表示(元の場所は`inherited_from`)。重複排除キー=(entry_key,alarm_id) |
| P-09 | `ALARM_ACCEPT_MIN_SLOT=1`。0円集計`p09_slot_resolution_stats_01.py`: 全run保存分のみ3/10=30%だが生存者バイアス(未解消はHR queueのみに残る)を補正した全体は**3/55=5.5%<25%**→Fable規則で1(初回受理)。結果JSON=`p09_slot_resolution_stats_01_result.json` |
| P-10 | `run_scope()`(context manager、finallyで直前値へ復元)。runnerは`family_scope`/`run_with_alarm_hook`経由 |
| P-11 | 完成報告に「発音供給の適用一覧」節(`applied_supplies()`)。静的辞書(Reicher->Riker)は`static_decisions`で`supply_map`へ登録(置換自体は共有tts_safeが実施、二重適用なし)。Ledger hint注入(`compute_ledger_hits`)は供給前の原文に対する旨を報告に注記 |
| P-13 | 報告に「Human Review残(受理境界の外)」を追加し、固有名詞のみ不一致だが境界外(脱落/一般語化等)の件数を区別。日本語対象外を報告末尾に明記 |
| P-14 | §7の整理: 撤去0。OPEN-318/327/330/331/335は「固有名詞のみHR」部分の範囲縮小注記のみ(Status不変) |
| P-15 | 追加test: 上表の全観点+Store跨ぎ再利用・Z clip ID role・scope解除・`audit/`外に書かない・公開ページbuilderがアラーム語を参照しない |

### 校正(再実行、`calibrate_replay_02.py`/`calibrate_replay_02_result.json`、保存HR queue 88イベント、API 0)
受理 45 -> **40**(45.5%)。差分5件: Muse->use系4件(`ASR_SIDES_ALL_GENERAL_WORDS`)、Khaite->Kate(両ASRがKateと書いた1件=正しい発音の可能性が高いが一般語化ガードで不受理)。不受理内訳(88): SECONDARY_NOT_ENTITY_ONLY 16 / WORD_DELETION 9 / SECONDARY_TEXT_MISSING 9 / P3_ENTRY_NOT_PRIMARY_NG 5(force_secondary由来、従来受理側に混入) / ASR_SIDES_ALL_GENERAL 5 / NO_ENTITY_DIFF 2 / SECONDARY_ONLY_NOISE_LIMIT 1 / CANONICAL_GENERAL 1。Muse系の除外を確認。
