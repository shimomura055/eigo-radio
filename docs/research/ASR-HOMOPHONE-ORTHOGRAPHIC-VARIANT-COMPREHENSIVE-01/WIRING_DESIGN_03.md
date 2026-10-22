# WIRING_DESIGN_03(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_03、2026-10-23。設計のみ・Production .py変更0・API費用0)

Status(本書時点): er109 v1 = `APPROVED_FOR_PRODUCTION`(Family X/Zのみ、ユーザー正式決定2026-10-23、原文=`docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER_02.md`)。配線**設計済み・Opus条件Aレビュー待ち・未実装**。`PRODUCTION_WIRED`ではない。`er109_asr_orthographic_equivalence_01.py`は未配線・`ORTHOGRAPHIC_EQUIVALENCE_ENABLED=False`のまま(本委任で変更しない)。
前提資料: `DESIGN_PROPOSAL_01.md` / `DESIGN_ADDENDUM_02.md`(§3 P-06設計・§4 P-10・§5 旧11-7条件) / `VALIDATION_02.md` / `OPUS_REVIEW_MANDATORY_01.md`(OF-AHO-P-01〜12)。
表記: 【事実】=今回Grep/実行で確認した事実(file:line)。【設計】=本書の提案。【推測】=未確認の見込み。

## 0. 結論(先に)
1. **推奨機構 = (b) X/Z runner run-scope + 単一flag(PNAP前例と同型)**。新規薄いmodule `er109_xz_scope_01.py`(`run_scope`/`is_active_for_run()`/`decision()`/`explain_protected()`)を作り、X/Z TTS段3関数(X b1b・X a2・Z `run_tts_stage`)にdecoratorを1行ずつ付ける。共有Validator(`val.classify_asr_match`)・共有leaf・KP票生成関数の**既定挙動は無変更**で、共有判定経路(adapter/judge/KP voter/再利用guard)の数点が`is_active_for_run()`がTrueのときだけer109を呼ぶ。scope外(A/B/C・単体呼出・scope未設定)は全点で`False`短絡=従来コードパスのまま。
2. 配線点は **adapter 2点(Primary chain末尾・`_secondary_accept`) + judge 3点(Primary PASS最終ゲート・Secondary値/否定事前チェック・KP票warning合成) + KP voter 1点(`er104 _classify`) + 再評価 2点(`rejudge_with_current_judge`のprimary/accept_fn) + 再利用guard 1点(scope外でのer109受理音声ブロック)**。いずれも「不合格時のみ追加で1回呼ぶ」。
3. P-06(最終ゲートのSpan単位解除)は、er109が`EquivalenceResult.spans`を返し、judgeが「値DIFFの各pair・否定カウント差がすべて同値span内で説明できる場合のみ解除」。説明できないDIFF・否定脱落・AMBIGUOUS(根拠なき曖昧表層)は従来どおりNG。
4. ②`no↔know`は`PASS_WITH_WARNING`(警告ラベル`ORTHO_NEGATION_WORD_HOMOPHONE`)。**新台帳を作らず**、既存`asr_judgement.warnings`→`er078_pass_with_warning_registry_01`の事後試聴リストで追跡。決定的規則(数・記号・綴り連結)は警告なし。
5. A/B/C不変の保証 = (i)構造(scope module importの静的限定・scope外短絡)+(ii)`er104_nonkp_before_after_01.py`方式の**保存行署名の前後sha一致**(scope OFF)+(iii)scope ON時にPASS→NG 0。
6. 旧11-7「既定OFF例外」は正式採用で役割終了。配線後は「flag=True(rollbackスイッチ)かつX/Z scope内のみ有効、A/B/C無効」が正式状態。旧`DefaultOffIsolation`型test(flag既定False・Productionからimport 0)は**撤去し**、A/B/C Isolation test・rollback test・scope漏れ静的testに置換。
7. 設計上A/B/Cのコードに**触れずに**実現できる(§J)。ただし1点、**既に反映済みのB不具合3件(d9e36f54a)は共有Validator経由でA/B/Cにも効いている**(本委任の対象外・変更しない、§J-2)。

---
## A. X/Z限定の有効化機構

### A-1. 英語ASR判定の呼出点(全数。X/Z/A・B・C別)
【事実】根拠=`er078_asr_unified_wiring_allowlist_01.json`(phase=post_wiring、entry_count 35、callee合計38呼出)+`er078_asr_unified_wiring_static_audit_01.py:ENTRYPOINTS`(8 entrypoint)+各runnerのimport/直接呼出Grep。**EN判定のみ**がer109の対象(JA 4呼出=`er007_ja_secondary_asr_01`は対象外・無変更)。

**(1) 判定入口(leaf→EN adapter `er006_secondary_asr_01.evaluate_attempt_with_cascade[_detail]`)7点**

| ID | 呼出点(file:line) | 対象 | X | Z | A/B/C |
|---|---|---|---|---|---|
| J1 | `er003_v1_sing01_voice01_generate.py:246` `generate_charon_english` | 本文/Topic intro/Comment等 | ○(runner:953,970) | ○(er063:821) | 共有leaf |
| J2 | `er003_v1_sing01_news_tail_fix.py:209` `generate_news_narration_wide_margin` | Full Story/In One Line | ○(runner:1005) | ○(er063:800) | 共有leaf |
| J3 | `er003_v1_crosslevel_audio_02_common.py:378` `_run_a2_minimal_fallback_attempt`(build_attempt_ctx:209) | A2英語segment(fallback) | ○(runner:1359経由) | ○(er063:830) | 共有leaf |
| J4 | `er012_b_family_voices_production_01.py:553` `generate_voice_body_wide_margin` | 本文(B voice) | × | ○(er063:816-818、Z対話clip) | B(本来の呼出元) |
| J5 | `er003_v1_repro01_main_generate.py:363` `generate_narration_snippet_verified_strict`(KP英語は`vote_required`、KP解説は通常) | KP英語phrase/英語解説/phrase_repeat | ○(runner:798、K2 store、`generate_key_phrase_explanation_en_verified`) | ○(er063:853,868,888) | A/B/C KP(vote無し) |
| J6 | `er003_v1_sing01_point_headings_aoede.py:129` | Point見出し | ○import(runner:51。実呼出はA2/B1の見出し) | × | 共有leaf |
| J7 | `er003_v1_n3_01_tts_generate.py:144` `_post_slowdown_unified_judge`(A2 6%減速後再検証) | A2本文 | ×(runner未参照) | ○(er063 apply_a2_slowdown_postprocess) | A/B |

X到達=J1,J2,J3,J5,(J6)=4〜5。Z到達=J1,J2,J3,J4,J5,J7=6。A/B/C=共有leaf経由で全点に到達しうる(**変更しない対象**)。

**(2) adapter内部(EN)5点**(全Family共通。ここがer109の配線点になる=scope判定でX/Zのみ有効)
`er006_secondary_asr_01.py`: `val.evaluate_attempt`×2(:908 `cascade_enabled=False`枝・:936 本枝)・`val.classify_asr_match`(:1086 非ラテンKP層)・`_secondary_accept`内`val.classify_asr_match`(:1174)・wrapper(:582,:632)。library内部2点: `er006_preprod_hardening_01_validation.py:1466 evaluate_attempt`・`aggregate_entity_only_phonetic_corroboration`。

**(3) 統一judge(`er078_asr_unified_judge_01.unified_judge`)**: Primary PASS最終ゲート(:443-472)・Primary NG P1短絡(:478-490)・Secondary値/否定事前チェック(:599)・許容集合判定(:605)・`finish_vote`(:559)。

**(4) KP 3-ASR票**: `er104_kp_three_asr_vote_01.py:232 _classify`(`val.classify_asr_match`+`_step_alternate_pass`)→`make_voter`(:244、Whisper票は`whisper_vote`:354経由)。Primary/Secondary票は(2)(3)のadapter/judge経由。KP再利用は`er104_kp_vote_reuse_01.py:150 kp_vote_reuse_ok`→:173 `evaluate_vote`(本番adapter経由・API 0)。

**(5) 保存転写の再評価(API 0)**: `er019_family_x_validation_inheritance_01.py:254 rejudge_with_current_judge`(classify:305,316,323)←`er078_reuse_value_guard_01.py:46 guard_entry`←(Store `er006_master_audio_store_01.py:130-132` / X runner `_reuse_guard_blocks`:653,:688,:736,:753 / Z `er063:729-743` / 継承`try_inherit_from_cached`:190,:206 / C `er013 runner:444`)。X専用tool: `er019_family_x_clobber_restore_03.py:75`、継承module `rebuild_state`:394,`rebuild_state_multi`:484。

件数サマリ: 判定入口 X=4〜5/Z=6/A,B,C=7(共有)、再評価入口 X=5(Store・X runner・継承・clobber_restore・rebuild)/Z=2(Store・er063)/C=1(er013:444、変更しない)。adapter/judge/KP voter内部の配線点は全Family共通のコードだが**scope判定でX/Zのみ有効**。

### A-2. 候補機構の比較と推奨

| 評価軸 | (a) 明示引数(`family`/`scope`をctx・関数引数で渡す) | **(b) run-scope(PNAP型、推奨)** | (c) X/Z専用ラッパー(共有関数無変更) |
|---|---|---|---|
| A/B/C挙動のバイト同一 | ctx未指定=従来。ただし共有leaf7点・Store・K2・KP関数すべてへ引数追加=A/B/C用ファイルを編集 | 共有関数は`is_active_for_run()`短絡のみ。scope未設定=従来コード。**A/B/Cのファイルは編集しない**(adapter/judge/er104/inheritance/guardは共有だが分岐はFalseで素通り) | 呼出元(共有leaf内)でadapterを呼んでいるため、ラッパーに差し替えるには結局leafを編集 |
| Store再利用・X引継ぎ・Zの確実なX/Z文脈 | Store/`guard_entry`/`rejudge`はctxを持たない→新引数のthreadingが必要(漏れ=X/Z側fail-open) | 再利用もstage関数の**内側**で実行されるため文脈が自動継承(X:runner:688,736,753、Z:er063:729)。stage外のX専用tool(clobber_restore/rebuild)は明示`run_scope("X")` | 再利用経路にラッパーを差し込めない(共有`guard_entry`) |
| flag既定値・起動script/.env | 同左 | `ORTHOGRAPHIC_EQUIVALENCE_ENABLED`=module定数(rollback用)。env/引数/dictから変更不可。`.env`に該当語0【事実】。scopeは`ValueError`で{X,Z}以外を拒否 | 同左 |
| rollback | 引数削除は多数ファイル | **定数1行をFalse**、または3 decoratorを外す | ラッパー切替 |
| Dangling | 引数の撤去漏れ | scope module 1つ。AST testで参照点を固定 | 二重実装化 |
| 保守性/前例 | 新方式 | **承認済み・稼働中の前例**: `er103_proper_noun_alarm_policy_01.py:42-79`(`APPROVED_SCOPES={"X","Z"}`・`run_scope`・`is_active_for_run()`)+`er103_pnap_runner_hooks_01.py:78 family_scope`+reuse guardのscope外ブロック(`er078_reuse_value_guard_01.py:51-57`) | 低 |

**推奨=(b)**。理由: (i)A/B/C用ファイルを1行も編集せずに済み(27-7適合)、(ii)Store/継承/KP再利用を含む全再評価経路が同じ`is_active_for_run()`で揃い、(iii)PNAPとして既に承認・稼働している同一パターン(rollbackの前例・Opus指摘P-11/F2でも「(b)ならPNAPのrun-scope方式で」と明記)。
欠点と対処: (1)scope漏れ(X/Z入口にdecoratorが無いとer109が無効=従来どおりでfail-safe)→静的test+動的test。(2)scopeはprocess内状態→PNAPと同じ`try/finally`のcontext manager、TTS段はスレッド並列化なし【事実: Grep ThreadPoolExecutorはer104 Whisper転写のみ】ので全呼出に伝播。process globalを採用し`contextvars`は使わない(Whisperのworker threadで文脈が切れる恐れを避けるため。転写のみで判定はmain thread)。(3)Zが内部でBの`generate_voice_body_wide_margin`(J4)を呼ぶ→scopeは**実行文脈(Z run)**であり関数の出自ではないため、Z内のJ4はer109有効、A/B自身のrunは無効(意図どおり)。

### A-3. 新module `er109_xz_scope_01.py`(新規ファイル。次委任で実装)
```
APPROVED_SCOPES = frozenset({"X", "Z"})
_RUN_SCOPE: str | None = None
def enter_scope(family)  # ValueError if family not in APPROVED_SCOPES
@contextmanager run_scope(family)        # try/finally で必ず復元(PNAP run_scope と同形)
def current_scope() -> str | None
def is_active_for_run() -> bool          # 唯一の読取関数: er109.is_enabled() and _RUN_SCOPE in APPROVED_SCOPES
def family_scope(family)                 # TTS段decorator。functools.wraps、wrapper.__er109_scoped__=True。入れ子は外側scopeを再利用
@dataclass(frozen) OrthoDecision: equivalent, verdict("PASS"|"PASS_WITH_WARNING"), warning_labels(tuple[str]), eq(EquivalenceResult), audit(dict)
def decision(canonical, text) -> OrthoDecision | None   # inactive / lang!=en / None・空 / not equivalent → None。(canonical,text)でLRUメモ(純関数、API 0)
def explain_protected(dec, vgr, neg_diff, canonical, text) -> ProtectedExplanation   # §C
def ortho_label() -> "ORTHOGRAPHIC_EQUIVALENT_MATCH" ; BASIS = "ORTHOGRAPHIC_EQUIVALENT_MATCH"
```
- **flag**: 既存の`er109.ORTHOGRAPHIC_EQUIVALENCE_ENABLED`/`er109.is_enabled()`を**単一flagとして継続使用**(新flagを増やさない)。次委任で`True`化(正式採用=rollbackスイッチ)。flag名は変えない(audit出力`flag_enabled`・既存testとの整合)。`er109_asr_orthographic_equivalence_01.py`本体は**純関数のまま**(scope/stateを持たない。`evaluate()`はflagを見ない)。`er109_xz_scope_01`はer109を関数内で遅延import。
- **Warningラベル写像**(judgeの大文字ラベル規約`W_*`に合わせる): `negation_word_homophone`→`ORTHO_NEGATION_WORD_HOMOPHONE`、`non_representative_variant_match`→`ORTHO_NON_REPRESENTATIVE_VARIANT`。警告が空=state `PASS`(警告なし)。
- 起動script/.env: 該当語0【事実:`.env` grep 0、`*.bat/*.ps1/*.sh`検索0】。暗黙ONの経路を作らない(env読取を実装しない)。

### A-4. 有効化(scope入口)の変更箇所(次委任)
| 対象 | 変更 | 根拠 |
|---|---|---|
| X b1b TTS段 `er019_family_x_audio_production_runner_01.py:883-886 generate_family_x_b1_segments` | decorator`@er109_scope.family_scope("X")`を`@secondary_run_scope.with_secondary_run`の下に1行追加 | 既存decorator並び(:883-885)と同形 |
| X a2 TTS段 同:1228-1231 `generate_family_x_a2_segments` | 同上 | 同 |
| Z `er063_family_z_audio_01.py:1136-1150 run_tts_stage` | `dry_run=False`分岐で`_run_tts_stage_impl`を`with er109_scope.run_scope("Z")`で包む(PNAP hook呼出の外側または内側。PNAP flag OFFでも有効にするため**PNAP hookとは独立**) | PNAPのflag OFF時はhookが素通し(`er103_pnap_runner_hooks_01.py:28-31`)なので、PNAPに相乗りしない |
| Z fiction runner `er026_family_z_fiction_production_runner_01.py` | 変更なし(`er063.run_tts_stage`経由) | 【事実】er026はer063をimport |
| X専用tool: `er019_family_x_validation_inheritance_01.py`の`rebuild_state`(:394)/`rebuild_state_multi`(:484)/`main`(:561)、`er019_family_x_clobber_restore_03.py`のmain | 入口で`with er109_scope.run_scope("X")`(**`rejudge_with_current_judge`自体には入れない**: `guard_entry`経由でA/B/C再利用が呼ぶため) | `rejudge`は共有(A/B/C reuse経由)なのでscopeは呼出側X専用moduleで設定 |
| KP再判定tool `er104_stored_audio_reeval_02.py`・`er107/er108`系 | 診断用途=無変更(scope外=従来判定)。必要時のみCLI引数で`--scope X`を明示 | 診断が本番判定を変えないため |
| A/B/C runner(`er012_b_*`,`er013_*`,`er012_e_*`,`er003_v1_n3_01_tts_generate`のA/B入口) | **変更なし**(scope module非import。静的testで固定) | 27-7 |

### A-5. A/B/C不変の証明方法(受入条件)
1. **構造(静的AST test)**: (i)`er109_xz_scope_01`をimportするProduction .pyは固定リスト(adapter・judge・er104 voter・inheritance・reuse guard・X runner・er063・clobber_restore)のみ。A/B/C runner(上表)・`er012_*`,`er013_*`のimport 0。(ii)`family_scope`/`run_scope`の呼出は`"X"`/`"Z"`リテラルのみ。(iii)`is_active_for_run()`以外のer109読取関数をProductionが呼ばない。(iv)`er109_asr_orthographic_equivalence_01`は`er109_xz_scope_01`以外のProduction fileからimportされない。
2. **実行(署名一致)**: `er104_nonkp_before_after_01.py`方式を踏襲し、保存ペア(`pairs_02.jsonl` 4,032+保存`*tts_generation_results*.json` attempt 4,879行+Azure 225)を**scope未設定(=A/B/C相当)**でadapter(`evaluate_attempt_with_cascade_detail`、mock Secondary/Whisper無呼出)へ通し、行ごとの署名(verified/state/reason/warnings/steps/final_status/aj keys)を配線前commit(`KP3V_OVERLAY`方式でbaseline .pyを先頭に置く)と配線後で比較。**全行sha一致(差分0)**を受入条件にする。追加でstore再利用(`guard_entry`)・`rejudge_with_current_judge`・KP voter(`make_voter`)も同形で署名比較。
3. **X/Z scope ON**: 同じ行集合で**PASS→NG 0**、NG→PASS行を全列挙(`stored_onoff_compare_02.json`の期待値19行[X10・Z0・A/B/C相当9]と整合。A/B/C相当9行は「scope外では変化しない」ことを2で証明、scope内=X/Z runで同入力が来た場合の挙動として別記)。

### A-6. 旧11-7「既定OFF例外」の整理
- 正式採用(`APPROVED_FOR_PRODUCTION`、ユーザー2026-10-23)により、`DESIGN_ADDENDUM_02.md` §5の5条件(新コード経路+単一flag・直接編集禁止・DefaultOff test・暗黙ON禁止・OPEN_ITEMS記録)は**限定例外の適用対象でなくなる**。配線後の正式状態: `ORTHOGRAPHIC_EQUIVALENCE_ENABLED=True`(rollbackスイッチ)+X/Z scope内のみ有効+A/B/C無効。`OPEN_ITEMS` OPEN-459から「未承認・既定OFF」記述を、PRODUCTION_WIRED到達時に**撤去**。
- test置換: 撤去=`er109_asr_orthographic_equivalence_01_test.py`の`ProductionIsolation`(flag既定False・Production file import 0・valにer109記述なし)。置換=(1)`XzScopeStaticTest`(上§A-5-1) (2)`OutOfScopeByteIdenticalTest`(scope未設定で全配線点が従来出力) (3)`RollbackTest`(flag False→X/Zでも従来出力) (4)`ScopeLeakTest`(例外・STOP時のfinally復元)。純関数module自体の「通信/ファイル書込なし」testは維持。
- 残存Grep対象(次委任で実施): `ORTHOGRAPHIC_EQUIVALENCE_ENABLED = False`/`未承認・既定OFF`/`DefaultOffIsolation`(er109関連)。

---
## B. 各票への適用点
共通原則: **既存判定が不合格のときだけ**、末尾で`er109_xz_scope.decision(canonical, transcript)`を1回呼ぶ(API 0・純関数・メモ化)。合格ならPASS票を追加。以後の最終ゲート(§C)・警告(§D)は共通。

| 票 | 配線点(次委任で編集) | 挿入内容 | 記録先 |
|---|---|---|---|
| **Primary(OpenAI)** | `er006_secondary_asr_01.py:1106-1126`の`if not verified:`ブロックの**直後**(`# ---- 統一judge ----`:1127の直前)。CMU alternate/M1(:1106-1125、`cascade_eligible`内)の外側に独立ブロックを追加 | `if (not verified) and lang=="en" and xz.is_active_for_run(): d = xz.decision(canonical_text, asr_text); if d: verified=True; result["verified"]=True; result["final_status"]=ORTHO_LABEL; layers.append("orthographic_er109"); primary_warnings += d.warning_labels` | `PrimaryResult`: `label`=ORTHO_LABEL・`equivalence_basis`=ORTHO_BASIS(**`APPROVED_EQUIVALENCE_BASES`には入れない**。丸ごとskipさせないため)・`signals["er109_decision"]=d`(同一process内オブジェクト)。judge audit: `audit["orthographic_equivalence"]=d.audit+{site:"primary"}` |
| **Secondary(Azure)** | `er006_secondary_asr_01.py:1172-1188 _secondary_accept`。`_m1_note_reject(...)`:1187の直前(M1不成立後)に追加 | `d = xz.decision(canon, stext); if d: captured["ortho"]=d; return True, ORTHO_LABEL` | `audit["secondary"]["label"]`=ORTHO_LABEL(既存)+`audit["orthographic_equivalence"]`のsite="secondary" |
| **Whisper(KP票)** | `er104_kp_three_asr_vote_01.py:232-241 _classify`。`alt = S._step_alternate_pass(cls)`:238の後 | `d = xz.decision(canonical, text); if d: return True, ORTHO_LABEL`(`make_voter`:244経由で**P/S/W票の再評価・Whisper票・`kp_vote_reuse_ok`の保存証跡再判定**すべてに効く) | `Voter.label`=ORTHO_LABEL(`kp_vote_check_v1`の既存`label`欄に入る。version据え置き) |
| 本文/英語解説 | 上のPrimary/Secondary(adapter共通)。KP英語のみ`vote_required`(3票)、本文・英語解説・phrase_repeatは通常(P→必要ならS) | 同上 | 同上 |

- **KP3V `kp_vote_check`との整合**: 票単位で適用し、多数決(`tally()`)は無変更。Primary票は`vote["primary_pass"]=True`(ortho合格は"Azure転写に依存した救済"ではないので`primary_rescued_by_secondary`にしない=OpenAI自身のPASS)。S票は`_secondary_accept`のORTHO合格を`s_pass`に反映。W票は`_classify`。
- **警告合成(KP)**: `finish_vote`(`er078 judge:559`)の`w2`に、PASS票のうちlabel==ORTHO_LABELの票の`decision().warning_labels`を加える(P票は`pr.warning_labels`経由で既に入る。S/W票はjudge内で`xz.decision(canon, voter.text)`を再取得して追加)。これで`no↔know`が3票のどの票由来でも`PASS_WITH_WARNING`になる。
- **値/否定ガード(KP)**: KP英語は2026-10-22のユーザー承認で既に保護解除(`er078 judge:449-460`「vote_guard_lifted」・`:480`以降P1短絡skip・`:599`のS票チェックskip)。§Cのspan解除は**非KP(本文・英語解説等)のみ**に作用し、KPは従来の解除済み状態を維持(KPの`AMBIGUOUS`票分類維持も従来どおり)。
- **配線しない箇所**: `val.classify_asr_match`本体・`val.evaluate_attempt`・Tier1/Tier3/M1/CS equivalence層・`er094`・`homophone_en`は**無変更**(共有Validatorへ手を入れない)。層の順序は「既存全層→最後にer109」(P1案、既存ラベルの勝敗が一切変わらない)。代替P2(Azure/Whisperを呼ぶCS-equivalence層/Tier3/非ラテン層より前に置く)は費用削減の余地があるが、既存ラベル・警告の勝敗が変わるため**採らない**(er109ヒットは稀=保存4,879行で19行[0.4%]、費用差は無視できる)。

---
## C. 最終保護Gate(`er078_asr_unified_judge_01`)のSpan単位解除(P-06)
### C-1. 受け渡しデータ
`EquivalenceResult.spans: list[SpanRecord(canon_span: list[str], asr_span: list[str], equivalent: bool, rule, why, warnings)]`(`er109:508-536`)を、`OrthoDecision.eq`としてadapter→judgeへ渡す。経路=`PrimaryResult.signals["er109_decision"]`(Primary)、Secondaryはjudge内で`xz.decision(canon, stext)`を再取得(純関数・メモ化済み=Primary/Secondary間のstate共有なし、`captured`への依存を作らない)。取得できない/None→**解除しない**(fail-closed、従来のゲート)。

### C-2. judge側の変更点(`er078_asr_unified_judge_01.py`、`lang=="en"`かつ`is_active_for_run()`のみ)
1. **Primary PASS最終ゲート(:443-472)**: `approved = pr.equivalence_basis in APPROVED_EQUIVALENCE_BASES`は**変更しない**(ORTHO_BASISは含まれない)。`elif vote is not None:`(KP)の後、`else:`(非KP)内で、`pvg.kind == DIFF or pneg`のときに限り、`pr.equivalence_basis == ORTHO_BASIS and xz.is_active_for_run()`なら`ex = xz.explain_protected(dec, pvg, pneg, canon, gate_text)`;`ex.explained`なら`audit["final_gate"] = {"applied": True, "value_guard": ..., "span_unlock": ex.detail}`でNG_PROTECTEDを**返さない**。説明できなければ従来どおり`NG_PROTECTED(final_gate_value_diff / final_gate_negation_diff)`。`AMBIGUOUS`は従来どおりP3降格(解除しない)。
2. **Secondary事前チェック(:599)**: `if vote is None and (svg.kind == DIFF or sneg):`の中で、`_ex_s = xz.explain_protected(...)`を計算。説明可能なら`NG_BOTH`を返さず先へ進み(`_ortho_s`として保持)、許容集合判定(:605)後に**`label != ORTHO_LABEL`なら従来どおり`NG_BOTH(secondary_value_diff / secondary_negation_diff)`**を返す(ORTHO以外の許容経路[M1/homophone等]が値差ありの転写を通す挙動を新たに許さない=既存条件を拡張しない)。
3. **Primary NG P1短絡(:480-490)**: ortho合格Primaryは`pr.passed=True`なので本枝に入らない。ortho不成立のPrimary NGは従来どおりP1(`p1_value_diff`/`p1_negation_diff`)。
4. audit: `audit["orthographic_equivalence"] = {"applied": True, "site": "primary"|"secondary", "decision": d.audit, "span_unlock": {...}}`(additive。ortho不使用なら**キー自体を作らない**=A/B/Cの`aj keys`署名不変)。

### C-3. `explain_protected`の規則(厳格版。`er109_stored_onoff_compare_01.py:62`のモデルを**token境界一致に強化**)
- 前提: `dec.eq.equivalent==True` かつ `dec.eq.version==LAYER_VERSION`。
- **値DIFF**: `vgr.pairs`のうち`verdict==DIFF`の各pairについて、`(p.src is None or token_in_span(p.src, s.canon_span))` かつ `(p.hyp is None or token_in_span(p.hyp, s.asr_span))` を満たす`s.equivalent==True`のspanが存在し、かつ`p.src`/`p.hyp`の少なくとも一方が非None。`token_in_span(x, units)`=正規表現`(?<![0-9A-Za-z])<escape(x.lower())>(?![0-9A-Za-z])`を各unit surface(小文字)に適用(`'1'`が`"21's"`にヒットしない)。1pairでも未説明なら不可。
- **否定差**: `neg_diff==True`のとき、judgeと同一の`negation_diff`内部カウンタ(`expand_standard_contractions`+`can not→cannot`正規化後の`_NEGATION_WORDS`)で`Counter(canon)−Counter(同値span内canon)`と`Counter(text)−Counter(同値span内asr)`を比較し**等しく**、かつ減算が負にならない場合のみ解除(span外の否定語数が両側で一致=否定脱落・付加はspan外では必ず不一致)。
- **AMBIGUOUS**: 解除しない(`vgr.kind==AMBIGUOUS`は従来どおり降格。例: `Point to`↔`Point 2.`は本文でP3、KPでは票)。
### C-4. 検証済みの道筋(【事実: 今回実行、API 0】`er109.evaluate`+`uj._protected`)
| canonical / asr | er109 | 値ガード | 否定差 | 結論 |
|---|---|---|---|---|
| `Pump one's fist.` / `Pump 1's fist.` | equivalent, PASS | DIFF `(src=None,hyp='1')` | False | pair hyp`1`がasr_span`["1's"]内→**解除→PASS**(`one's↔1's`) |
| `I said no.` / `I said know.` | equivalent, PASS_WITH_WARNING(`negation_word_homophone`) | NO_VALUES | True | span外の否定数が0=0→**解除→PASS_WITH_WARNING**(②) |
| `We have two cats.` / `We have one cats.` | **NOT_EQUIVALENT**(phoneme_differs) | DIFF `('2','1')` | False | ortho不成立→従来NG(実数値差) |
| `I did not go.` / `I did go.` | NOT_EQUIVALENT(one_side_empty) | NO_VALUES | True | NG(否定脱落) |
| `I can't go.` / `I can go.` | NOT_EQUIVALENT(phoneme_differs) | - | True | NG(`can't/can`非救済) |
| `He is lead.` / `He is led.` | NOT_EQUIVALENT(incomparable・同形異音語) | - | False | NG |
| `I'll go` / `ill go`、`Take part`/`Take apart` | NOT_EQUIVALENT | - | - | NG |
| `Point to` / `Point 2.` | equivalent, PASS | **AMBIGUOUS** | False | 本文=P3降格(解除しない)/KP=票として評価 |
(次委任でこの表を`OrthoWiringDeterministicTest`として固定する。)

---
## D. ② `no ↔ know`: `PASS_WITH_WARNING`・警告記録・事後試聴追跡
- 判定: er109が`negation_word_homophone`警告を返す(`_span_warnings`:615-622、unit surfaceがNEGATION_WORDSまたは`n't`終わり)。写像=`ORTHO_NEGATION_WORD_HOMOPHONE`。`PrimaryResult.warning_labels`(Primary)/judge内追加(Secondary・KP S/W票)→`done()`(`er078 judge:405-419`)が`state==PASS and warnings`を`PASS_WITH_WARNING`へ変換(既存機構、LR_REWRITTENと同じ経路)。
- **内部記録(新台帳なし)**: `asr_judgement`(=`JudgeResult.audit_record`、`tts_generation_results.json`のsegment/attemptに既存保存)に`warnings`(ラベル)+`orthographic_equivalence`(additive: version・stress_mode・flag_enabled・span毎の`canon/asr/rule/matched_variants/representative_match/heteronym_guard/warnings`=`EquivalenceResult.audit()`:538-544が既に出力)。根拠(warning label・どのspan・なぜ同音か)はこの1ブロックで復元可能。
- **事後試聴**: 既存`er078_pass_with_warning_registry_01.derive_listening_list`(:77-95)が`asr_judgement.state=="PASS_WITH_WARNING"`の採用音声を`warning_labels`込みで列挙(dedup=sha+labels)。完成hook`write_listening_list_safe`で`pass_with_warning_listening_list.{json,html}`が再導出される(X/Z/legacyページ節に接続済み)。**追加は`_entry()`(:51-75)の1箇所**: `judgement.get("orthographic_equivalence")`がある場合のみ`entry["orthographic_equivalence"]={rules, spans(canon/asr), warnings}`を加える(キー無し=A/B/C出力バイト同一)。再利用/継承された音声は`asr_judgement_inherited`(元のWARNINGを継承、OF-AUW-15)で同様に載る。
- 決定的規則(数・記号・綴り連結・contraction)=警告なし`PASS`(Opus Q6維持)。警告対象は(1)否定語同音(no/know) (2)代表発音以外のvariantでのみ一致(`ORTHO_NON_REPRESENTATIVE_VARIANT`)のみ。
- 非救済: `can't/can`・`don't/do`・`not`脱落は`NOT_EQUIVALENT`(§C-4)+最終ゲートの否定保護がspan外で効く。

---
## E. Store再利用・既存音声・HR Lock・resume
1. **再評価経路で同じ原則**: `rejudge_with_current_judge`(`er019 inheritance:254`)のEN枝2点を変更。(i)`:305-311`: `res = classify(...)`が`not res.should_pass`かつ`xz.is_active_for_run()`で`xz.decision(tts_input, asr_text)`があれば`primary = PrimaryResult(passed=True, text=asr_text, label=ORTHO_LABEL, equivalence_basis=ORTHO_BASIS, warning_labels=d.warning_labels, signals={"er109_decision": d})`。(ii)`:322-324 accept_fn`: `r2.should_pass`でなければ`d2 = xz.decision(canon, stext)`→`(True, ORTHO_LABEL)`。判定本体は同じ`unified_judge`なので§Cのspan解除も同一に効く。`guard_entry`(`er078_reuse_value_guard_01.py:46`)・Store(`er006_master_audio_store_01.py:130-132`)・X runner(:653,:688,:736,:753)・Z(`er063:729-743`)は**stage関数内=scope内**なので追加変更なし。KP再利用は`kp_vote_reuse_ok`→`evaluate_vote`が本番adapter+`make_voter`を通る(§B)ので自動的に揃う。
2. **scope外での受理音声の流入ブロック(PNAP前例の踏襲)**: X/Zでer109受理(`asr_judgement.orthographic_equivalence.applied==True`)された音声が共有Master Audio StoreからA/B/Cのrunへ再利用されると、scope外判定と食い違う(Opus F2指摘)。`guard_entry`の`:51-57`(PNAP 範囲外ブロック)の直後に同形で追加: entryの`asr_judgement`/`asr_judgement_inherited`に`orthographic_equivalence.applied`があり、かつ`not xz.is_active_for_run()`なら`blocked=True, reason="ORTHOGRAPHIC_EQUIVALENT_AUDIO_OUT_OF_SCOPE"`(再生成へ回す)。**A/B/Cの挙動はer109導入前と同じ**(er109で生まれたentryだけを使わない)。【設計・Opus確認点】ブロックは新規entryにだけ作用し、既存の全Store entryには作用しない(キーが無い=従来)。
3. **既存音声(過去にNG/HR)の扱い**: 引継ぎ・Storeは上記1で再判定され、span解除後に合格すれば再利用可(従来はprotected diffで`blocked`=再生成)。
4. **HR Lock済みsegmentの明示再判定(P-10)**: 自動解除しない。新規CLI(次委任、既定dry-run・API 0): `er109_hr_lock_rejudge_01.py --level-dir <dir> [--apply-candidates]`が`audit/…review_lock_state`(`er011_human_review_lock_01._lock_store_path`:155)の`last_attempts_log`(保存転写+wav sha、:425-447)を`run_scope("X"|"Z")`内で現行judge+er109により再判定→`PASS`(警告なし)の全attemptがある場合のみ`audit/er109_hr_rejudge_candidates.json`へ「解除候補」を出力(`PASS_WITH_WARNING`は事後試聴付きの候補、全NGは何もしない)。解除=既存`approve_regenerate`(:474、人間の明示操作)のみ。解除理由・判定version・操作者をlock recordの既存`reason`/`approved_by`に追記。保存データでHR/STOPに至った該当は3 segment(`stored_onoff_compare_02.json`)。
5. **resume**: 再実行で同stage関数に再入するためscope再設定(finallyで毎回復元)。`status==OK`の既存entryは再判定せず保持(stored `asr_judgement`のまま)。`status!=OK`は再生成(判定は新規にer109込み)。STOP/技術STOP(Secondary/Whisper障害)の再開時も同じ経路。resume前後で同一入力に同一判定になること(メモ化は純関数なので不変)をtestで固定。

---
## F. 短文・er094経路(VALIDATION_02留意点)
【事実】er109の`_judge_span`は語数が異なる全語spanで承認済みer094条件(`val._mw_homophone.multiword_span_equivalent_v3`、`er109:638-651`)を再利用。er094の安全条件(片側1語・最大3語・FW2・G5など)はer109内でそのまま適用され、spanが同値でも**他のspanが全て同値でなければ文全体は同値にならない**(`evaluate`:705-760)。
- **到達性**: X/Zでも1語・短文KP(KP英語の12.6%が1語、OPEN-459記載)がadapterへ到達する。短文の`ratio<0.4`は`TTS_FAILURE`分類(retry)だが、er109は分類に依存せず「不合格(`not verified`)」のみで評価されるため、`one`↔`1`型の短文を救済できる。他方、`MIN_CANON_TOKEN_LEN`/FW2/1文字token禁止がer094側で維持され、欠落・付加(片側空span)は同値にならない(§C-4)。
- **X/Zでの扱い**: 追加の特別扱いなし。er094の既存経路は`classify_asr_match`内(無変更)、er109経由のer094再利用はscope内のみ。VALIDATION_02の`third places↔third place is`型(A/B/C相当2行)はX/Z runで同入力が来た場合のみ救済対象(保存データではXで0)。
- テスト: 短文/1語KPで`seize/sees`(B修正済・scope無関係)・`one/won`(heteronym→NG)・`are/or`(NG)・`take part/take tart`(NG)を固定。

---
## G. テスト計画(次委任で実装)
**単体(新規 `er109_xz_scope_01_test_01.py` ほか)**
- G1 scope: `enter_scope`のValueError("A"/"B"/"C"/"Y"/小文字拒否)、`run_scope`の入れ子/例外時復元、`family_scope`の`__er109_scoped__`、flag False→`is_active_for_run()` False、`current_scope()`漏れなし。
- G2 既定挙動不変: scope未設定で`decision()`は常にNone、adapter/judge/voter/rejudge/guard_entryが従来と同一出力(§A-5-2の署名一致)。
- G3 決定的ケース(scope=X/Z): `one's↔1's` PASS(span解除)、`no↔know` PASS_WITH_WARNING(+ラベル)、`twenty percent↔20%` 既存経路維持(重複実装なし=他層で先に合格、ortho未発火)、`1` vs `2` NG、`don't`→`do`/`can't`→`can` NG、否定脱落NG、同形異音語(lead/led)NG、曖昧略語(St/Dr/Mt/#)NG、oronym NG、`Point to↔Point 2.` 本文P3降格、KPは票。
- G4 span説明: token境界(`1`が`21's`にヒットしない)、span外のDIFF/否定差は不可、`dec.eq.version`不一致は不可、decisionがNone/例外のとき従来ゲート(fail-closed)。
**統合**: KP3V(P/S/W各票でortho合格・警告合成・`kp_vote_check_v1`に`label`が残る・ortho由来S+WでSECONDARY_CONFIRMED+ORTHO警告)、Store再利用(in-scope再判定でreuse/out-of-scopeでORTHO受理音声ブロック/既存entry不変)、X引継ぎ(`rejudge`)、Z(`run_tts_stage`)、resume(再入で判定一致)、HR再判定CLI(dry-run既定・自動解除なし・scope外では候補0)。
**不変性**: A/B/C署名sha一致(§A-5-2)、X/Z ON時PASS→NG 0、AST静的test(§A-5-1)、`er078_asr_unified_wiring_static_audit_01`再生成(新ASR呼出=0、allowlist差分なし)、`er104_kp_vote_wiring_test_01`/`er104_kp_vote_guard_lifted_test_01`/`er094 StaticChecks`/`er078 ja_wiring`の維持。
**Dangling**: 撤去識別子(`DefaultOffIsolation`型・`ORTHOGRAPHIC_EQUIVALENCE_ENABLED = False`・`未承認・既定OFF`)のGrep、`ORTHO_LABEL`/`ORTHO_BASIS`の参照が`VALID_CLASSIFICATIONS`等の閉集合に未登録でも落ちないことの確認(`ORTHO_LABEL`は`val.ClassificationResult.classification`ではなくadapterの`final_status`/judge label。`_PRIMARY_WARNING_BY_CLASSIFICATION`・registry・Store・継承で参照される箇所を全数Grepしtestで固定)。
**全回帰**: `run_project_regression.py`(現baseline failed 0/errors 0、6,872 passed=commit 2771b49a9。`er109_*`が`er094 StaticChecks`/`er078 ja_wiring allowlist`/`er104 allowlist`に影響した前例があるため、新module追加時にallowlistを同時更新)。

---
## H. runtime evidence計画(費用上限40円、見積は出典付き)
方針: **正式経路の実行証拠 + 決定的ケース検証の組合せ**。自然発火を得るための記事生成の繰り返しはしない(ユーザー原文§4)。
| # | Family | 内容 | 目的 | 見積 | 出典 |
|---|---|---|---|---|---|
| H1 | X | 正式入口 `generate_family_x_a2_segments` のKP段(coffee_prices a2、`Pump one's fist`を含むKP)を1回 | scope(X)が正式入口で設定され、KPの3票・値ガード解除・ortho判定がadapterから通ること(自然発火すれば`orthographic_equivalence`記録) | 約0.8円 | 同一構成の実測 0.79円(`KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/RUNTIME_EVIDENCE_01.md` §3) |
| H2 | X | 正式入口 `generate_family_x_b1_segments` を`--only-segments`相当で本文2〜3 segment(small_bag等、数字・序数を含む文) | 非KP本文の最終ゲート(span解除経路)がscope内で稼働 | 約8円 | 同形run 7.93円(`PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/RUNTIME_EVIDENCE_02.md` X: full_story_part2,3) |
| H3 | Z | 正式入口 `er063.run_tts_stage` melos最小段(KP + `seize`含むsegment) | scope(Z)・Z票・warning記録 | 約4.7円 | Z KP 1.45円(RUNTIME_EVIDENCE_01 §3)+Z 3 clip 3.22円(RUNTIME_EVIDENCE_02) |
| H4 | X/Z | **決定的検証(API 0)**: 保存wav+保存転写(coffee kp1 Azure`Pump 1's fist`・hormuz `Act 1 was 20%`・`brace oneself for`/`Brace oneself 4.`・Z `seize/sees`)を、**H1〜H3の正式stage関数の内側で`_ONLY_SEGMENTS`/継承経路**から再評価(scope=X/Zが実際に設定されている状態で`try_inherit_from_cached`→`guard_entry`→`rejudge`が走る) | 実際のrouting・flag・basis・警告記録を、再現不能な自然発火に依存せず取得 | 0円(ローカルWhisperのみ) | `stored_onoff_compare_02.json`・`new_pass_listen_list_02.json` |
| H5 | 全 | 決定的ケース(§C-4の表)をX/Z scope内の本物のadapter+judge+mock Secondaryで実行し、期待判定を記録 | 新規救済と誤PASS防止の証拠 | 0円 | - |
合計見積 **約13.5円(≤40円)**。モデル=最新原則(`PM_GOVERNANCE.md` 25節): TTS=`gemini-3.8-flash-lite-tts`(X/Z runner既定)、Primary ASR=`gpt-4o-mini-transcribe`、Secondary=Azure STT(既存Production)。新規モデル選定なし。
**直列化の明記(必須)**: H1〜H3(TTS/ASRを実際に呼ぶrun)は、並行する『開いた窓』run(`FAMILY-Z-VOICE-PRODUCTION-WIRING-01`、`--stage all` resume)と **Master Audio Store manifest(`er006_output/master_audio_store_01/manifest.json`)・`raw_usage_log.jsonl`が競合**するため、**別agentのrun完了(`ACTIVE_TASK.md`のStatus解除)を待って直列実行**する。それまでにできる並列作業(実装・単体/統合test・署名比較・H4/H5の準備)は先行。STOP確認(`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`、rc=3で即停止)を各run前に実行。

---
## I. SSOT更新計画
| 対象 | 更新内容 | 時点 |
|---|---|---|
| `OPEN_ITEMS.md` OPEN-459 | Status=`APPROVED_FOR_PRODUCTION_WIRING_DESIGN_PENDING_OPUS`(X/Zのみ、A/B/C対象外)。「次=Opus条件A→実装委任_04」追記。実装後=`PRODUCTION_WIRED`(X/Z別)で「未承認・既定OFF」記述を撤去 | 本委任(Status)/実装委任(撤去) |
| `DECISION_LOG.md` | 1エントリ: ユーザー正式決定2026-10-23(原文所在`…_USER_02.md`)+配線設計の骨子(機構(b)・A/B/C対象外) | 本委任 |
| `CURRENT_SPEC.md` | ASR節に「er109 v1: `APPROVED_FOR_PRODUCTION`(X/Zのみ)・配線設計済み/未実装」節を追記(§C span解除・§D警告・§E scope外ブロックの仕様記述)。`PRODUCTION_WIRED`到達時にStatus更新 | 本委任(設計記録)/実装委任(Status) |
| `docs/pm/USER_DECISION_REGISTER_01.md` | 新規行 #156=判断済み(2026-10-23、er109採用3点: ①包括対策②`no↔know`③A/B/C対象外確認)。原文path+sha256 | 本委任 |
| `docs/pm/OPUS_FINDINGS_LEDGER.md` OF-AHO-P-06/P-10/P-11 | 設計反映済み(`DESIGNED_IN_WIRING_03`)。P-11は「適用条件が正式採用で変わった(限定例外→X/Z scope+rollback flag)」旨を付記。実装・test後に`IMPLEMENTED_VERIFIED` | 本委任(設計)/実装委任 |
| `docs/pm/REPORT_LEDGER.md` | 報告1行(RESULT_PACKET_AHO3) | 本委任 |
| 撤去(実装委任で実施) | er109旧「既定OFF」記述、`ProductionIsolation`/DefaultOff test、`DESIGN_ADDENDUM_02` §5の読み替え注記 | 実装委任 |

---
## J. リスク・未決
1. **A/B/Cへ変更が及ぶ設計か**: 推奨(b)では**及ばない**(A/B/C用ファイル未編集、scope外は全点短絡、署名sha一致で保証)。共有コードのうちer109を呼ぶ分岐はX/Z scope内でのみ実行される。及ぶ可能性があるのは(i)`guard_entry`のscope外ブロック(§E-2: er109で生まれたentryのみが対象で、既存entryに作用しない)と(ii)registry `_entry()`のadditiveキー(キー無し=出力同一)。いずれもA/B/Cの既存出力を変えないことを署名比較で確認する。もし署名差分が出た場合は**実施せずSTOPして報告**する(ユーザー原文§2)。
2. **既存の事実(本委任の対象外・変更しない)**: B不具合3件の最小修正(d9e36f54a、`er078_asr_value_guard_01._en_atom_text`の複合序数・`60 %`、`val._homophone_swap_only_bypass_ratio_gate`)は**共有Validator**で、既にA/B/CにもNG→PASS方向のみで効いている(`bfix_before_after_01.json`: 前後比較12,342件PASS→NG 0・NG→PASS 26、うちA/B/C相当1行)。承認済み規則の不具合是正(`PM_GOVERNANCE.md` 11-8)であり本委任のscope拡張ではないが、「A/B/Cに効かせない」原文の趣旨との関係はFableが分類すること(報告のみ。A/B/Cへの展開提案はしない)。
3. **scope漏れ(X/Z側fail-safe)**: 入口にdecoratorが無ければer109が無効(=従来)になるだけで誤PASSはない。静的/動的testで3入口+X専用tool 3点を固定。X/Zで新しく追加されるstage入口は将来追加時にtestが落ちる。
4. **KP票の質**: `Act 1 was 20%`型の4本はWhisper転写が別のITN差を持ち(VALIDATION_02 §4)、KPでWhisperがtie-breakする場合は票が割れてNGになる。これはer109の問題ではなく票の仕様どおり。非KPはP単独(+必要ならS)。
5. **Opus確認点(§8)**: P1案(層順)・scope外ブロック・span説明規則・fail-closed・KP警告合成。
6. **未確認**: Whisper small以外のモデルでのortho合格率、1日15作品規模の発火頻度(保存4,879行で0.4%)、`PASS_WITH_WARNING`事後試聴リストの運用負荷(+19行/4,879行規模)。
7. **許容集合の網羅**: 本設計が編集する共有ファイルは `er006_secondary_asr_01.py`・`er078_asr_unified_judge_01.py`・`er104_kp_three_asr_vote_01.py`・`er019_family_x_validation_inheritance_01.py`・`er078_reuse_value_guard_01.py`・`er078_pass_with_warning_registry_01.py`・X runner/Z・X専用tool。いずれも「X/Z scopeでのみ分岐が動く加算」で、既存Prompt・正規表現・閾値・辞書の直接編集は**ない**。

## Opusレビューで特に見てほしい論点(3〜5点)
1. **機構(b)の妥当性とscope漏れ/混入リスク**: process global(PNAP同型)で足りるか。Z内でのB関数(J4)呼出が正しくZ文脈で有効になる設計でよいか。共有Master Storeでscope外に流れるentryを`guard_entry`でブロックする方針(§E-2)はPNAP前例と整合するか。
2. **P-06のspan説明規則(§C-3)**: token境界一致+span外の否定カウント一致で十分か。`src=None`(付加)型DIFFの扱い、複数span・数の読み語彙混在での過解除の余地。Secondaryで`label!=ORTHO`のとき従来NGに戻す条件(§C-2-2)の過不足。
3. **層順(P1: 全既存層の後)とKP票での警告合成(§B)**: S/W票由来のortho合格でも`ORTHO_*`警告がjudgeに入る設計、Primary票がAzure依存救済でない扱い、`kp_vote_check_v1`のversion据え置きでよいか。
4. **HR Lock再判定の運用(§E-4)**: 自動解除なし・候補列挙のみ・解除は既存`approve_regenerate`、で十分か。
5. **正式採用後のtest置換(§A-6)**: DefaultOffIsolation撤去→A/B/C署名一致+rollback+scope静的testへの置換で、11-7の隔離要件(旧)を実質的に上回るか。
