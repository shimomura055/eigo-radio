FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01-委任_04-20261023

# 委任_04: er109 v1 正式採用(APPROVED_FOR_PRODUCTION、X/Zのみ)の **Production配線・テスト・runtime evidence・SSOT**

## 0. 先に行うこと(T-0)
1. 本委任文の逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_委任_04.md`。Nは約311〜320から先頭行がMARKER一致のものを探し、一致確認を報告に記す。
2. Opusレビュー結果(下記§2)を `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/OPUS_REVIEW_COND_A_WIRING_02.md` に逐語保存し、`docs/pm/OPUS_FINDINGS_LEDGER.md` に OF-AHO-W-M01〜M13 を起票(Status=OPEN→実装後にIMPLEMENTED_VERIFIED)。
3. `check_delegation_prompt.py`検証結果をRESULT_PACKETへ(FAILでもブロックしない。理由を記録)。
4. `docs/pm/ACTIVE_TASK.md`: 別agent(FAMILY-Z-VOICE-PRODUCTION-WIRING-01、『開いた窓』有料run含む)が並行中。編集直前に再読込し、OPEN-459の「並行タスク」1行だけ更新。

## 1. 前提(Fable判断)
- ユーザー正式決定の原文: `docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER_02.md`(X/Zのみ、A/B/Cはコード修正・挙動変化・Trial・検証run禁止、再承認不要、Wiring費用40円以内基本)。
- 設計: `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/WIRING_DESIGN_03.md`(機構(b) run-scope、配線点7、P-06 Span解除、②記録、E-2 Storeブロック、E-4 HR再判定、テスト計画G、evidence計画H)。
- Opus条件Aレビュー: **条件付きGO**。設計(b)・層順P1・`kp_vote_check_v1`据え置き・HR Lock自動解除なし、は承認。must-fix M1〜M12+test置換(a)〜(f)を**実装前に設計へ反映し、すべて実装・検証すること**(§2に全文)。Fableは設計とOpusが実質一致・既存承認範囲内と判断し、実装へ進める。
- J-2(B不具合3件 d9e36f54a がA/B/Cにも効いている件)のFable分類: ユーザーが2026-10-22に「不具合修正は自律」と承認した範囲の、承認済み規則の是正であり、今回のX/Z限定指示(10-23)より前に反映済み。巻き戻し自体がA/B/Cのコード変更になるため**現状維持**。最終報告・SSOTに事実として記載(提案ではない)。
- rollback(flag False)時にX/Z内のer109受理entryがStoreでブロックされ再生成費用が出る性質は、設計書・SSOTに記録(Opus指摘)。

## 2. Opusレビュー全文(逐語保存用)
```
(ここにFableが受領したOpusレビュー本文をそのまま貼る。以下、要点のみ再掲。全文は本委任文の末尾§9にある)
```
→ 全文は§9参照。保存は§9の内容で行う。

## 3. 実装範囲(Production、X/Zのみ有効)
A. **scope module** `er109_xz_scope_01.py`: `run_scope`(context manager)/`family_scope`(decorator)のみ公開、`enter_scope`/`leave_scope`非公開(M3)。`is_active_for_run()`=scope∈{X,Z} かつ `er109.is_enabled()`。env/argparse/設定dict読取なし(5-b)。例外・STOP時のscope復元(ScopeLeak test)。`current_scope()`公開(test用)。
B. **入口decorator**: X b1b・X a2・Z `run_tts_stage` の3入口+X専用tool(Store再評価/引継ぎ)に`family_scope("X"/"Z")`(リテラルのみ)。X/Zから届く全ASR入口(J1,J2,J3,J5,(J6) / Z: J1〜J5,J7、Z→J4(Bの`generate_voice_body_wide_margin`)/J7経路含む)がscope内側であることを静的+動的(spy)testで固定(M6)。
C. **配線点7**(すべて`is_active_for_run()`で短絡、スコープ外は従来コードパスのまま、不合格時のみ加算): adapter 2(Primary chain末尾 `er006:1126`直後/`_secondary_accept`)、judge 3(Primary PASS最終ゲート/Secondary値・否定事前チェック`:599`/KP票警告合成)、KP voter 1(`er104 _classify`、`lang`を渡し英語のみ M5)、再評価2(`rejudge_with_current_judge` primary・accept_fn)、Storeブロック1(`guard_entry` `:57`直後・`kp_vote_gate_follows` skipより前、`ortho_contributed(aj)`で判定、`asr_judgement`/`asr_judgement_inherited`両対象 M1)。
D. **P-06 Span解除**(M7〜M10): 否定差解除はjudgeと同じ`neg_count`で数が違う各spanが`negation_word_homophone`警告を持つ場合のみ、解除時は必ずPASS_WITH_WARNING(M7)/値DIFF pairをspan内出現に1対1割当、`[.,:/]\d`隣接は境界外、src/hyp両方ありは同一span必須、対応表を`span_unlock.detail`に記録(M8)/Primaryは`gate_text`==decision判定対象のときのみ解除、Secondaryは`svg`/`sneg`/`stext`で判定(M9)/Secondary解除は`outcome.accepted is None`かつ`ORTHO_LABEL`受理のみ、Secondary ortho合格にはORTHO警告も付与、G3に「AMBIGUOUS(`Point 2.`)はSecondaryでもNG」追加(M10)。`APPROVED_EQUIVALENCE_BASES`には入れない。
E. **②no↔know**: PASS_WITH_WARNING、ラベル`ORTHO_NEGATION_WORD_HOMOPHONE`/`ORTHO_NON_REPRESENTATIVE_VARIANT`、記録`asr_judgement.orthographic_equivalence`(additive)、事後試聴は`er078_pass_with_warning_registry_01`の`_entry()`へadditiveキー1つ(キー無しならA/B/C出力同一)。
F. **KP3V**: `kp_vote_check_v1`据え置き、`build_vote_audit`に`ortho_layer_version`/`ortho_scope`/票ごと`ortho_applied`・`ortho_warnings`追加(M11)。S/W票警告の再計算は同じ転写文字列で(test固定)。
G. **メモ化**: LRUは`er109.evaluate`のみ、scope/flag確認はメモ外(M4)。
H. **例外時**: 各配線点でer109例外→「同値ではない」(従来の厳しい判定)+audit記録、runは止めない(should-fix採用)。
I. **HR Lock再判定**(M12): er011(A/B/C共有)は編集しない。X/Z専用CLIでデータのFamilyをoutput root allowlistで確認(X/Z以外拒否、`--scope`指定なし M2)、候補を`audit/er109_hr_rejudge_candidates.json`+別追記ログへ(Opus指定の最小情報: 識別/attemptごとのsha一致・保存転写・新旧判定/根拠spans/実行記録/候補区分PASS・PASS_WITH_WARNING・INSUFFICIENT_EVIDENCE)。表記は「再生成承認候補」。自動解除なし。`approve_regenerate`には`approved_by="user:er109_rejudge:<candidate_id>"`を渡すだけ。本委任ではCLIの実装+既存HR Lock済みX/Z entryに対する**候補列挙の実行(読取のみ、解除はしない)**まで。
J. **診断tool**: `er104_stored_audio_reeval_02`/er107/er108等の`--scope`指定は設けない(M2)。
K. **A/B/C不変**: A/B/Cファイルは1行も編集しない。`er006_preprod_hardening_01_validation`はer109/scope moduleをimportしない(5-a)。

## 4. テスト(すべて新規/更新、全PASSが受入条件)
- 単体: 決定的ケース(`one's↔1's` PASS、`I said no↔know` PASS_WITH_WARNING、`two↔one` NG、`not`脱落 NG、`can't↔can` NG、`don't↔do` NG、`lead↔led` NG、`Take part↔Take apart` NG、`St.↔Street` NG、`Point to↔Point 2.` 本文P3降格・SecondaryでもNG、同一文で`one's→1's`+別の実数値差 NG、否定語がspan内外にまたがる NG)。
- 隔離: (a)共有Validator非import、(b)env/CLI/設定読取なし+`.env`/起動script該当語0、(c)flag Trueでもscope未設定なら全配線点でer109呼出0(spy)、(d)**golden署名の常設回帰test**(配線前HEADで固定したfixture: 19行+A/B/C相当9行+§C-4表+各経路代表行。scope未設定=完全一致、scope X/Z=期待どおり変化)、(e)AST allowlist(リポジトリ全体、`run_scope`/`family_scope`呼出点、リテラル"X"/"Z"のみ)、M1ブロック(層・印の種類ごと、J1〜J7でmanifest `asr_judgement`に印が残る)、rollback(flag False→X/Zでも従来出力+Store内ortho entryブロック)、ScopeLeak、(f)既存`er078_asr_unified_wiring_static_audit_01`・`er104_kp_vote_*`・`er094 StaticChecks`・er109純関数の通信/書込なしtest維持。pytest autouse fixtureで各test前後`current_scope() is None`(should-fix採用)。
- 大規模不変: `er104_nonkp_before_after_01.py`方式で保存4,879行+pairs 4,032の行署名を配線前baselineと比較(adapter/`guard_entry`/`rejudge`/`make_voter`)。scope未設定=全行sha一致、X/Z ON=PASS→NG 0。**差分が出たら実施せずSTOP報告**。
- 旧`ProductionIsolation`(DefaultOffIsolation型)のうち「valにer109記述なし」は残し、「既定OFF」「未配線」前提のものだけ撤去(識別子は設計書A-6)。
- 全回帰: `run_project_regression.py`単独実行(pytest系は別枠)で自分起因の新規失敗0(直近基準 failed 0/errors 0、`docs/research/TEST-HYGIENE-02/REGRESSION_BASELINE_01.md`の前提条件で)。

## 5. 作業の隔離と直列化(重要)
- 並行する『開いた窓』有料runが走っている間に、main作業ツリーのProduction .pyを書き換えない(子プロセス起動で新コードが混入し得る)。**実装・単体/統合testはgit worktree(例 `../eigo-radio_wt_aho`、HEADから)で行い**、worktreeの前提(.env、`mfa_tool` junction、未追跡資産)は`REGRESSION_BASELINE_01.md`の手順に従う。golden fixtureは配線前HEADのworktreeで先に採取。
- main作業ツリーへの反映・commit・全回帰・runtime evidence(H1〜H3、TTS/ASR実呼出)は、**FZVW agentの有料runが完了していること**を確認してから(確認方法: `docs/pm/ACTIVE_TASK.md`のFZVW行、`Get-Process python`のcommand line、`er026_output/family_z_production_e2e_01/the_open_window/`配下の最新run進行状況)。進行中なら待機(最大60分、5分間隔で再確認)し、待機中はworktree側のtest・SSOT草稿・設計書追記を進める。60分を超えても終わらなければ、worktree側の成果をcommitせずに現状をRESULT_PACKETへ書いて報告(Fableが調整)。
- worktreeは作業後に削除(mfa_tool junction解除を先に)。

## 6. runtime evidence(計画H、見積約13.5円、上限40円。超過見込みならSTOP)
- H1 X: coffee_prices a2 KP段(`pump one's fist`)→ `one's↔1's`がP+Sで通るか/票・spans・warnings・scopeの記録。H2 X: 本文2〜3 segment(既存記事・既存run dirの最小段。可能なら`no`を含むsegmentを選ぶ。無ければH5の決定的検証で補う)。H3 Z: melos最小段(KP段+`seize`含む3clip)。H4: 保存wavの継承経路(X引継ぎ・Z再利用)でのscope内再評価(0円)。H5: 決定的ケース(0円)。
- 各runで`TTS_EXECUTION_MODE=STANDARD`、STOPセンチネル確認(rc=0)、有料runの再起動禁止、HR Lock/STOP迂回禁止、**`melos`受入済みpage(`user_test/family_z_melos_02`)・『開いた窓』成果物を上書きしない**(新run dirを使う)。
- evidenceは `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/RUNTIME_EVIDENCE_04.md` にX/Z別・①②別で(actual routing・flag・scope・判定basis・warnings・Store/再評価の一貫性・費用出典)。未観測の項目は「未観測」と明記(完了扱いにしない)。

## 7. SSOT/Git
- CURRENT_SPEC(該当節): 正式状態「X/Zで有効・A/B/Cで無効」、配線点、Span解除規則、②警告方針、rollback性質、旧「未承認・既定OFF」記述の置換。OPEN-459=Status候補`PRODUCTION_WIRED`(X/Z・①②別。Fable受入後に確定するので、報告では「候補」と書き、SSOTには`WIRED_PENDING_FABLE`で記載)。DECISION_LOG配線エントリ。OF-AHO-P-06/10/11・W-M01〜M13更新。REPORT_LEDGER。
- commitは論理単位(scope+配線+test / golden fixture / runtime evidence / SSOT)。明示add、`git push origin HEAD:main`、secret_scan `--staged` hits=0。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 8. 報告(docs/pm/RESULT_PACKET_AHO4.md、同内容を最終報告で)
(1)Status候補(X/Z・①②別) (2)実装(ファイル:行、配線点7、scope module、M1〜M12対応表) (3)runtime evidence要約(X/Z別、観測/未観測) (4)テスト・回帰数値・署名一致結果 (5)A/B/C不変の証拠 (6)HR再判定候補列挙の結果(件数・区分) (7)費用(出典) (8)commit・raw URL・SSOT (9)未解決・残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。

## 9. Opusレビュー全文(逐語)
総合判定: 条件付きGO。機構(b)(run-scope)の選択、層順P1、KP3Vのversion据え置き、HR Lockを自動解除しない方針は妥当。must-fix 12件を実装前に反映。
論点1 X/Z限定の隔離機構(b) — 条件付きGO。根拠: PNAPと同型(`er103_proper_noun_alarm_policy_01.py:42-79`)。process global可(Whisper票`make_voter`はmain thread `er104:354`、worker threadは転写のみ`:315-318`)。Secondary cacheは転写のみで許容判定は毎回`accept_fn`(`er006:808-812`、judge`:605-608`)→scope依存結果がcache経由で漏れない。共有Storeのブロックは必須: scope外で再判定するとer109受理entryは多くの場合`secondary_not_accepted`になり`guard_entry`は`REJUDGE_NG_NOT_PROTECTED`で再利用を止めない(`er078_reuse_value_guard_01.py:84-88`)→E-2がなければA/B/Cへ流入。KP英語Store keyは`+vote1`接尾辞で分離(`er104_kp_vote_reuse_01.py:278-284`)。rollback(flag False)でX/Z内のer109受理entryもブロック→再生成(費用が出る点を記録)。
must-fix M1: `ortho_contributed(aj)`(`orthographic_equivalence.applied`/primary・secondary label=ORTHO_LABEL/vote内いずれかの票label=ORTHO_LABEL/warningsにORTHO_*のいずれか)、`asr_judgement`と`asr_judgement_inherited`両対象、挿入位置`:51-57`直後・`kp_vote_gate_follows` skip(`:58`)より前、J1〜J7でmanifest`asr_judgement`(`er006_master_audio_store_01.py:227`)に印が残ることをtest。M2: 診断tool(`er104_stored_audio_reeval_02`/er107/er108)の`--scope X`撤回、HR再判定CLI含めscopeはデータ側Family(X/Z出力rootのallowlist)を確認して決め、違えば拒否。M3: `enter_scope`/`leave_scope`非公開、`run_scope`/`family_scope`のみ、リポジトリ全体`.py`(root直下tool・`docs/research`含む)のAST testで呼出点を固定リスト管理。M4: LRUメモは`er109.evaluate`のみ、scope/flag確認はメモ外。M5: `make_voter`の`lang`を`_classify`に渡し`lang=="en"`のみer109。M6: `er078_asr_unified_wiring_static_audit_01.ENTRYPOINTS`中X/Zから届くもの(X=J1,J2,J3,J5,(J6)、Z=J1〜J5,J7、Z→J4・J7含む)が全て3 decorator/X専用toolのscope内側であることを静的+動的(spy)testで固定。
should-fix: pytest autouse fixtureで各test前後`current_scope() is None`/X/Z stage内でASRを呼ぶsubprocessが無いことをGrep記録/`er011_*`・`er014_output/*`・`er026_output/*`運用scriptはscope外=従来判定とrunbookに1行/各配線点でer109例外→非同値扱い+audit記録、runは止めない。
論点2 P-06 span解除(C-3) — 条件付きGO。根拠: `evaluate`は不一致区間を全て同値と判定できた場合のみequivalent(`er109:725-760`)。「`one's→1's`+別の実数値差」は数値差区間が`phoneme_differs`→文全体NOT_EQUIVALENTで解除段階に来ない。解除規則はer109誤判定時の最後の防壁。
M7: judge側`_val._NEGATION_WORDS`(`er006_preprod_hardening_01_validation.py:415-419`、`cant/wont/dont/isnt…`含む)とer109側`NEGATION_WORDS`(`er109:464`)・`_span_warnings`の`endswith("n't")`(`:615-622`)が不一致(アポストロフィ無し・曲線`’`)。規則: 各同値spanにjudgeと同じ`neg_count`を適用し、両側で数が違うspanは必ず`negation_word_homophone`警告を持つこと。1つでも無ければ解除しない。否定差を解除した場合は最終状態を必ずPASS_WITH_WARNING。M8: (a)DIFF各pairをspan内の別々の出現に1対1割当 (b)境界正規表現`(?<![0-9A-Za-z])x(?![0-9A-Za-z])`は`1`を`1.5`/`1,000`に一致させる→前後`[.,:/]\d`を境界外として除外 (c)src/hyp両非Noneのpairは同一span必須 (d)対応を`span_unlock.detail`に全記録。M9: Primary最終ゲートは`gate_text = pr.adopted_text or pr.text`(judge`:427-428`)、er109判定はadapterの`asr_text`→`explain_protected`は`gate_text`==decision判定対象のときのみ解除。Secondaryは必ず`svg`/`sneg`/`stext`、Primaryのガード結果流用禁止。M10: Secondary解除は`outcome.accepted is None`かつ`_secondary_accept`戻り値`ORTHO_LABEL`のみ。provider事前`accepted`・M1/homophone等ORTHO以外受理は従来`NG_BOTH(secondary_value_diff/negation_diff)`。`outcome.accepted`事前ありをtest固定。Secondary ortho合格には`:654`の`W_SECONDARY_CONFIRMED`に加えORTHO警告。
確認済み: 値ガードAMBIGUOUSは本文P3降格、Secondary表層不一致なら`:629`でNG_BOTH→`Point to↔Point 2.`はSecondary orthoで通らない。G3に「Secondaryも`Point 2.`ならNG」追加。PASS→NGなし(ortho合格後の説明不能DIFF/否定差は`final_gate_*`NG、従来も`p1_*`NG、どちらもprotected prefix)。should-fix代替: マスク方式(両側同値spanを同一placeholderに置換後`_protected`再実行、DIFF・否定差なし・新AMBIGUOUSなしのみ解除。AMBIGUOUSは解除しない側)。M8で十分なら必須ではない。
論点3 層順と票警告合成(P1) — GO(1条件)。根拠: P1なら既存ラベル・警告の勝敗不変。Azure層後でも発火率0.4%で費用影響無視可。Primary ortho合格は`rescue_layers`に入らず`primary_rescued_by_secondary`False(`er006:1146`)。警告合成はPASS票中ORTHO票から(`tally`上PASS票は勝った組`row`に含まれる`er104:150-177`)。Primary完全一致+Secondary ortho合格でも警告が付き試聴リスト微増、許容。version据え置き正しい(`er104_kp_vote_reuse_01.py:82,172,308`、`:172`はversion不一致で保存Whisper転写を捨てる→互換破壊・費用増)。M11: `build_vote_audit`に`ortho_layer_version`(=er109 `LAYER_VERSION`)、`ortho_scope`、票ごと`ortho_applied`/`ortho_warnings`。should-fix: S/W票警告の`decision`再計算は同じ転写文字列(test固定)。
論点4 HR Lock再判定(E-4) — 条件付きGO。M12: `approve_regenerate`(`er011_human_review_lock_01.py:474-501`)は`reason`固定文上書き・引数`approved_by`のみ、er011はA/B/C共有で編集禁止。根拠はX/Z側候補file(`audit/er109_hr_rejudge_candidates.json`)+別追記ログ、`approve_regenerate`には`approved_by="user:er109_rejudge:<candidate_id>"`。「再生成承認候補」表記。CLIのscopeはM2どおり。最小情報: 識別(theme_id/level/segment_id、canonical原文+sha256、lockのstate/reason/updated_at)、attemptごと(番号、wav_path、記録sha vs 現在sha一致[不一致・欠落は候補外]、P/S(KPはW)保存転写、旧判定state/reason、新判定state/reason/warnings)、根拠(er109 version・spans[canon/asr/rule/why/warnings]、値・否定ガード結果、span_unlock.detail)、実行記録(判定codeのcommit hash、scope、候補区分PASS/PASS_WITH_WARNING[事後試聴必須]/INSUFFICIENT_EVIDENCE)。KPで3票揃わなければINSUFFICIENT_EVIDENCE。
論点5 旧11-7既定OFF隔離の撤去 — 条件付きGO。must-fix test: (a)`er006_preprod_hardening_01_validation`がer109・scope moduleをimportしない(旧ProductionIsolationの「valにer109記述なし」は残す) (b)scope module・er109に`os.environ`/`argparse`/設定dict読取なし、`.env`・起動script該当語0 (c)flag Trueでもscope未設定なら全配線点(adapter2・judge3・voter・rejudge・guard)でer109呼出0(spy) (d)golden署名を常設回帰test化(配線前fixture: 19行[A/B/C相当9行含む]・§C-4表・各経路代表数百行、scope未設定=完全一致、scope X/Z=期待どおり変化、`run_project_regression.py`で毎回) (e)M3 allowlist AST、M1ブロック(層・印種類ごと)、M4 rollback(flag False→X/Zでも従来出力+Store内ortho entryブロック)、ScopeLeak(例外・STOP時復元) (f)既存`er078_asr_unified_wiring_static_audit_01`(新ASR呼出0)・`er104_kp_vote_*`・`er094 StaticChecks`・er109純関数の通信/書込なしtest維持。
範囲外: §J-2(B不具合修正のA/B/C波及)はFable分類。er109アルゴリズム再レビューなし。