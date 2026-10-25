# OPUS_REVIEW_REQUEST_02 (条件A: 案A Production配線設計のレビュー依頼。実装前)

管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_03。依頼者=Fable(本ファイルはSonnetが用意した依頼素案。Opusへ渡すのはFable)。
発火条件: `PM_GOVERNANCE.md` 11-3 条件A(Production配線という処理フロー/Seed契約の設計)。**Production file編集・有料run(『告げ口心臓』正式再生成)はこのレビュー後のFable Goまで開始しない(委任_04)。**
前提: 案Aは2026-10-25にユーザーがAPPROVED_FOR_PRODUCTIONとして正式承認済み(UDR #192、原文=`docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER_02.md`)。したがって「採用可否」ではなく**配線設計の妥当性・漏れ・副作用**のレビュー。Opusは採用可否を宣言しない。

## (a) 論点(7点。各に判断材料の所在を付す)
1. **(a) 配線箇所の網羅**: 初回経路と、retry/fallback/regeneration/resume(`--regenerate-stage`、`ensure_stage`再利用、部分run、LLM技術retry)で、R0/R1/R2/Stdのいずれも**同一builder・同一narration_voice**でPromptが作られるか。見落としている経路(別runner、旧stage `text`/`keyphrase`のLEGACY、`er026` runner内のPrompt直書き)は無いか。→ `WIRING_DESIGN_01.md` §1-1(W1-W7)・§1-3(経路表)。runnerのコード変更は0(`validate_source_essentials`と`run_writer_chain`を通るため)という判断の当否。
2. **(b) Seed必須化と既存作品の扱い(3状態目を作らない)**: 必須化の位置を`Essentials.__init__`(W4)と`validate_source_essentials`(W5)の2か所にし、置換条件を既存の`essentials is not None`(W3)に一致させた設計は、「essentialsありでvoice無し」の第3状態をPrompt builderに到達させないか。Melos(`ESSENTIALS_EXEMPT_STORIES`)は従来どおり=byte同一で`in third person`がベース文言として残る(§1-4)。この扱い(判断B)は承認文「三人称固定指示の撤去」の趣旨に整合するか、代替(Melosにもessentialsを課す/汎用句に置換)は不要か。さらに**S-1(Seed変更で既存run dirのplan/support/kp再実行がProvenance seed_sha不一致でSTOP)**を受容する(M3)か、provenance付替え手順(M4)を先に設けるべきか(`WIRING_DESIGN_01.md` §2)。
3. **(c) 旧固定文言の完全撤去とkey_roles指示との整合**: 撤去後のGrep残存(`REVISE_USER_TMPL`:141の1か所=Melos専用経路)と`Key people`行の"refer to this person by role or relationship, without a name"(`er062_family_z_writer_01.py`:425)が一人称の語り手を三人称化させない設計(W1の汎用1句をKey people行より前に置く)は十分か。R0の`_R0_NAME_SENT`・`_R0_PRES_LAST`等に人称を暗示する文が残っていないか(Grep結果: `third`は`_CONVERSION_SUBSTITUTIONS`:131の`simple third-person English`置換のみ。Seedに該当文言が無い限り発火しない[Melos旧Seed用]。一人称Seedへの流用禁止を手順書化する扱いで足りるか)。
4. **(d) 既存作品の副作用確認をPrompt byte一致+Trial結果再利用で済ませる妥当性**: 賢者/開いた窓/猿の手/告げ口心臓の4作品はProduction組立がTrial実送信Promptとbyte一致(§0、`wiring_proto_cmp_*_01.py`)。LLM出力の副作用はTrial Phase 2(各1サンプル、猿の手の段落数+8は事前基準未達で未確定)の再利用。**『二十年後』はTrial対象外**でnarration_voiceはSonnet起案(Trial未検証)。この再利用で「必要十分な回帰」と言えるか、『二十年後』のみ追加の無料確認(Prompt構造検査のみ)で足りるか、有料の追加確認が必要か(推奨は有料追加なし)。
5. **(e) runtime evidenceの十分性**: 正式runで残る証跡(`writer/*_prompt.txt`全文dump、`provenance.json`のprompt_sha256/essentials_sha256/actual_model_id/routing_key、seed_check `source_essentials.narration_voice`、`cp_checklist.md`のnarration行)で、「narration_voiceが各工程へ渡った」ことを事後に機械確認できるか(`WIRING_DESIGN_01.md` §1-3)。追加ログ(例: provenanceへnarration_voice自体の記録)は必要か、不要か(新ログ=新機構を増やさない方針)。
6. **(f) 撤退容易性**: 採用commit単一のrevert(Writer 3か所+Seed 5件の両置き場+SEED_PROVENANCE+test)と`seed_STALE_20261025.json`退避で足りるか。公開物差替え(`user_test/family_z_tell_tale_heart_01/`)は別commitとして撤退可能か。
7. **(g) X/Yへの波及なし**: `er062_family_z_writer_01.py`はZ専用で、`er111_pn_entity_table_trial_01.py`は`key_roles`のみ参照。他Familyのwriter/runnerが`Essentials`/`build_revise_prompt`を共有していないか(Grep: `build_essentials|Essentials(|source_essentials`の呼出元一覧は`WIRING_DESIGN_01.md`作成時にZ runner・Z test・Trial dev runner・er111のみ)。

## (b) 背景・事実(最小限)
- 案Aの内容と検証: `ADOPTION_NOTE_01.md`、`PHASE1_RESULT_01.md`(1a/1b/1c)、`PHASE2_RESULT_01.md`(賢者/開いた窓/猿の手)、`FABLE_EVAL_01.md`(VALIDATED=Trial範囲)、`OPUS_REVIEW_01.md`(Trial設計時の条件A、修正1-5反映済み)。
- 本設計の要点(`WIRING_DESIGN_01.md`): Writer 3か所(描画1行・REVISE置換1か所・必須検査)+W4/W6の補助、Seed 5件を**Production seed置き場とer026_seedsの両方**へ追記(告げ口心臓のみ`free_to_cut`もdev_seed文へ差替え)、runner変更0、追加LLM 0・新Validator 0・新retry 0。
- 先行検証: Production Seed+記入予定voiceで組んだ4作品のR0/R1/R2/StdがTrial dumpとbyte一致(Production file未編集、scratchpad上のコピーに適用)。
- 費用: 配線はAPI 0。『告げ口心臓』正式再生成は約40円(UDR #193承認済み、7-7で案件300円以下のAI自律範囲)。

### 読むファイル(この順で十分)
`WIRING_DESIGN_01.md` → `ADOPTION_NOTE_01.md` → `er062_family_z_writer_01.py` 130-142・384-433・447-491・533-558・718-795行 → `er026_family_z_fiction_production_runner_01.py` 1306-1360・1421・1697行 → `wiring_proto_patch_01.py`(設計差分の機械的な写し)。

## (c) 参照すべき既存仕様のGrep確認欄(Sonnet記入)
- 修正版B(原作忠実性包括対策v1)=PRODUCTION_WIRED(2026-10-23、OPEN-465/464)。本配線はその`source_essentials`契約へ1キー(`narration_voice`)を追加する拡張。新Validator・LLM検査・retry・HRは追加しない(2026-10-12決定③④)。
- `docs/pm/PM_GOVERNANCE.md` 11-7(未承認機能の限定例外)は**不適用**: 案AはAPPROVED_FOR_PRODUCTION済みのため、単一flag・DefaultOffIsolationの例外枠ではなく通常のProduction配線として扱う(ただし欄なしSeedでseed_check停止=fail-closedで未設定時のAPI呼出0)。

## (d) 重大度の分類依頼
必須修正 / 推奨 / 参考に分け、特に論点2(S-1とMelos扱い)と論点4(二十年後)について「実装前に直す/受容して記録/次委任」のどれかを明示してほしい。
