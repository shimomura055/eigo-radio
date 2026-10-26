## 管理ID

KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02(Opus OPUS_REVIEW_03のM1〜M4是正+R1〜R7反映→Production配線(既定ON)→test→X/Y/Z Std/Adv runtime evidence+既知事例replay。PRODUCTION_WIRED判定はFable)。並行タスク衝突確認: 並行Agentなし(本委任のみ)。あなたの所有=`er125_kp_rescue_production_01.py`(+test)、`er105_kp_fulltext_selector_01.py`、`er119_kp_candidates_01.py`、`er003_v1_n3_01_scaffold_generate.py`(H3)、`er105_kp_rule_compliance_test_01.py`、`er105_kp_fulltext_selector_01_test_01.py`、`er119_*_test_*.py`(必要分)、`data/kp_idiom_lexicon_01/denylist.txt`、`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/**`、evidence用新規run dir(下記)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_{DELEGATION_02,OPUS_REQUEST_03}.md`(+check.json)、`docs/pm/RESULT_PACKET_KPRW2.md`。**編集禁止**: `er119_kp_prompt_2v_01.py`等のsha固定Prompt、`er119_kp_human_review_cli_01.py`、既存run dir(AI島`run_ai_01`・redelivery_fee `run_01`/`run_voice_puck_ev_01`・公開dir)、Family別runner(`er019/er121/er026/er062/er063`)のKP以外。SSOT編集権なし。git index.lock競合時は10秒待って再実行(最大3回)。pathspec付きcommit。

## 前委任(委任_01)の受入記録(Gate 7)
- 当初目的(ユーザー原文§1逐語): 「**Gate除外救済方式：PRODUCTION_WIREDまで完了**」。§3「コード配線やDEVテストのみでPRODUCTION_WIREDと判断しない。」
- 委任_01成果物: 量化詞guard是正(6133aa6d6)、`er125`+53 test、辞書10,674見出し、DESIGN_03/SPEC_LEDGER_01/IDIOM_LEXICON_01/OPUS_REVIEW_REQUEST_03/TEST_PLAN_01/BUDGET_PLAN_02(1701dfc4d)。11件: 9件救済形・#1短縮/#8 CMU不採用。回帰: er125 53/er105 52/er123 154/er003 1910/er119 131(+HEAD既存2失敗)。
- 証拠: `rescue_eval_prod_01.json`、`quant_parity_01.json`、`idiom_exception_listing_01.json`。
- 一致・不一致: 設計・DEV=一致。未配線・runtime evidenceなし=本委任で完了。判定=部分受入(設計・DEV ACCEPTED)。判定整合: 重大NG=なし。
- QDC: JPY0、改善見込み高、次の一手=本委任(見積21〜31円)。
- Opusレビュー(OPUS_REVIEW_03、条件A): **条件付き可**(M1〜M4是正をtestで固定すれば配線とevidenceへ進んでよい。R1〜R7推奨)。Fable照合: Claude案とOpusの結論は一致、承認済み仕様範囲内、新原則なし、新トレードオフなし → Fable判断で次工程へ進む(11-3)。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(ユーザーAPPROVED_FOR_PRODUCTION 2026-10-26)+runtime evidence。到達上限Status=EVIDENCE_COLLECTED(Family別)。PRODUCTION_WIRED判定はFable。
- 禁止: 承認済み品質規則の緩和、Human NG復活、5語超の短縮救済・本文にない語の追加・CMU分解救済、AI島HR候補の変更(`run_ai_01`の`candidates_sha256`不変をtestで固定)、公開ページ変更、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。起動間隔150秒以上、同一run dir 5分3回禁止。
- 費用: 上限¥40(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日(JST)既使用約JPY552/残約JPY448/本委任見積JPY21〜31(根拠: BUDGET_PLAN_02=X/Y/Z各1記事×2レベルのKP候補生成fresh 6 level-run×約1.6円+救済発生時のgloss再整合・QA再判定約0.5〜1円/件+既知事例replay数件)/改善見込み高/承認区分: C。
- Opus独立技術レビューGate(11-3): 条件A=実施済み(OPUS_REVIEW_03)。本委任はその是正反映。設計を変える新事実が出た場合はFableへ報告(再レビューはFable判断)。
- 修正範囲の線引き(11-8): 範囲内=承認済み救済方式の配線とOpus M/Rの是正・test・evidence。範囲外=縮約形R5是正(OPEN追記のみ)、`a can of beans`型の既存guard問題、候補数仕様変更。
- 時間見込み: 約3h(M1〜M4+R 60分/配線4箇所+test 45分/evidence 6 run+replay 60分[150秒規律]/文書化・commit 15分)。並列化: evidence runのX/Y/Zは別run dirなので、起動間隔150秒を守りつつインターリーブ可(各run dirで5分3回を超えない)。test実行はevidence待ち中に。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。KP stageのみ。runnerがTTSへ進まないstage指定を厳守)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。(KP stage限定起動で、TTS/本文生成が走らないことを事前に`--help`/dry-runで確認)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_DELEGATION_02.md` をN=667から順に試し、先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02」で始まるものを採用。同じ方法でN=666付近の先頭「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 OPUS_REVIEW_03」をOpus依頼文として`..._OPUS_REQUEST_03.md`へ保存(`--index -1`不可)。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_USER.md`(保存済み。§2採用表・§3検証要件12項目を受入基準に使う)。

## Opus OPUS_REVIEW_03の所見(逐語要約。全文はFableが下記「Opus所見全文」に貼る。`OPUS_REVIEW_03.md`としてあなたが保存)

### Fable決定(全件採用)
- **M1(H2が重複Gateを迂回)**: H2で救済成功時、救済後句の正規化keyで`seen`を再照合。重複なら救済せず元reasonを維持。`wc`・`hits`・rec欄は救済後句で再計算。test追加。
- **M2(H1/H2が環境変数だけで全経路に効く)**: Fable採用=**推奨案**: `generate_candidates`開始時にcontextvarをセットし、H1・H2は`rescue_enabled() and 文脈有効`のときだけ発火。旧経路(`er062:1364 run_kp_with_outer_retry_fulltext`、`er121:538-551`旧kp_fnアダプタ、run_selection_gateの他呼出元)で救済されないことをtestで固定(golden不変)。DESIGN_03 §1・台帳OF-KPRS-M2の記載は事実どおり維持。
- **M3(外側retry条件)**: `n_auto<3 and (gate_dropped or 救済済みかつauto不可の候補あり)`へ。auto不可の救済候補はF1累積除外に**入れない**(再選定されればHR候補として残す)。Fable判断: 旧M5の「救済失敗のみF1累積」は維持。test追加。
- **M4(既存test改訂の漏れ)**: `er105_kp_rule_compliance_test_01.py:100`(`can of worms` blocked assert)と`:61-67 test_idiom_exceptions_are_not_wired`を「旧規則の撤去」として改訂(`will be missed`/`could not bear`/`time is money`/`is money`が引き続き拒否されるassertは残す)。改訂理由をtest docstringとFIX_01に記録。`test_rescue_flow_not_wired_in_er105`も改訂。
- **R1**: denylistへ卑語・俗語4件(`have one's shit together`/`have someone by the balls`/`have the hots for`/`have several seats`)を予防追加。`flags.idiom_exception`は既存guardが実際に拒否した句だけに付ける。
- **R2**: `kp_candidates.json`のdoc単位に辞書sha・`lexicon_status`・`rescue_enabled`・er125 `SCHEMA`を記録。resume時に現在値と違えばlogのみ(停止しない)。
- **R3**: evidenceでQA再判定のkey一致率をrevertとM1に分けて計測。revertで一致率≈0ならrevertのQA callを省く案を報告(本委任では変更しない)。
- **R4**: `verify_persisted_rescue`に`rescued_key == validator_args.key == item.key_phrase`一致確認+保存済み引数でのvalidator再実行(API 0、報告のみ)を追加。
- **R5**: AI島`run_ai_01`のresume統合test(`ensure_kp_review`に「呼ばれたら例外を出すgenerate_fn」を渡す、固定fixture、skipしない)を追加。
- **R6**: 選定段`apply_exclusions`で元の句も照合(Human NG similar判定を元句にも)。安い場合のみ実装、重ければFIX_01に理由を書いて見送り。
- **R7**: 縮約形R5の非対称(ASCII `can't`主語付き受理/curly核へ救済)をOPEN文案に追記。
- **環境変数kill switch**: 許容。testで`EIGO_KP_RESCUE`を明示固定(monkeypatchでON/OFF両方)。
- **SPEC_LEDGER追記**: QA再判定の限界(救済後keyの自己比較で4項目はほぼPASS、変換の正しさは決定論validator+M1限定で担保)を明記。

### Opus所見全文
(以下、OPUS_REVIEW_03の全文をそのまま`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/OPUS_REVIEW_03.md`へ保存すること)

結論: 条件付きでProduction配線(委任_02)へ進んでよい。条件は、配線前に必須の4件(M1〜M4)を委任_02の中で是正し、testで固定すること。設計の核は承認文の範囲内で、fail-closed(失敗時は救済しない安全側)も成立しています。ただし配線仕様に、Gateの迂回、仕様文との乖離、test計画の漏れが残っています。

論点1 慣用句の一般機構 → 問題なし(推奨R1・R2あり)。25件の目視結果: 卑語・侮蔑語・ことわざの断片・名詞主語の完全文は含まれていません。学習価値がやや低いのは`can of corn`(野球の俗語)、`could not get elected dogcatcher`(米国の政治慣用句)、`have done with`(やや古風)の3件です。ただし本機構は「誤った除外を外すだけ」で、候補へ押し込むものではありません。選定LLM・本文一致・QAを通る必要があるため、許容範囲と判断します。気づいた点: `can of worms`/`can of corn`は名詞の`can`が`aux_start`として通っています。構造条件ではなく辞書一致で救われている例です。結果は正しい(既存guardの誤判定を是正する方向)ですが、`a can of beans`は引き続き拒否されます。これは既存guardの問題であり、本件の範囲外です。構造条件の抜け: `shan't`/`needn't`がない、`cannot`/`can not`/`can't`を相互に変換しない、2語以上の主語は除去しない、`oneself`は対象外。いずれも救済が減る方向で、誤受理リスクはありません。2語以上の主語を除去しない点はOpus-02 M3に整合しています。sha再ピン: コード定数とmeta.jsonの二重ピンで、不一致時は空表=例外なしになります(`er125:93-105`)。不一致でも「旧挙動に戻る」だけなので品質面は安全ですが、劣化に気づけません(→R2)。OF-KPRW-R1: 116件のうち、現時点では判断を変えない卑語・俗語4件(`have one's shit together`/`have someone by the balls`/`have the hots for`/`have several seats`)を予防的にdenylistへ追加することを推奨します。将来R5の是正やhave役割判定の変更で有効になる可能性があるためです。あわせて`annotate_candidate`(`er125:578-581`)の`flags.idiom_exception`は、既存guardが実際に拒否した句だけに付けてください。現状は`have a say`等にも付き、HRが誤解します。

論点2 HRなし経路のβ(QA再判定) → 問題なし(推奨R3)。(a) 承認済みtemplate・schemaは無変更で、promptへ渡るのは4キーだけです(`er003:363-371`)。Prompt変更には当たりません。ただし`display_phrase=救済後key`のため、元の表層形→救済後keyの変換を評価する4項目(`qa_meaning_or_usage_unchanged`/`qa_core_meaning_preserved`/`qa_no_semantic_role_loss`/`qa_not_over_minimized`)は自己比較になり、ほぼ必ずPASSします。変換の正しさは、最終Gateと同一引数の決定論validatorと、M1の{display語, LLM語}限定だけで担保されます。「単位としての評価」と割り切るなら妥当ですが、SPEC_LEDGERにこの限界を明記してください。(b) 救済後keyと返却keyが不一致ならNOT_REJUDGEDになり、HRでのみ採用可です(`er125:504`)。安全側として十分です。ただしrevertでは、同じ入力に対してLLMが前回と同じ原形化keyを返す可能性が高いです。その場合、β下でもrevert救済は事実上HRでのみ採用可になる見込みです。(c) 選定段の救済(D1・慣用句の核)に追加条件を付けない判断は妥当です。OF-KPRW-R3: 委任_02のevidenceで、key一致率をrevertとM1に分けて計測してください。revertで一致率がほぼ0なら、revertではQA callを省いて費用を削ることも検討してください。

論点3 既定ON・配線4箇所 → 要修正(M2・M4)。(a) A/B/C経路への波及はありません。validatorは`allow_inflection_normalization=False`の場合に旧関数を使い(`er003:629-633`)、H1は通りません。(b) M6は保たれます。H1は1関数(`er105:941`)の中にあり、er125の`_gate`も同じvalidatorを経由するためです。OF-KPRW-M2(漏れ): H1とH2は環境変数`EIGO_KP_RESCUE`だけで有効になります。そのため`validate_and_resolve`と全文選定validatorを使う全経路に効きます。対象は`er062:1364 run_kp_with_outer_retry_fulltext`(Zの`_kp_fn_for_ctx`の既定、`er026:1717`)、Yの旧`kp_fn`アダプタ(`er121:538-551`)、run_selection_gateを使う全呼出元です。一方、DESIGN_03 §1と台帳OF-KPRS-M2は「旧候補なし経路は挙動不変(バイト同一)」と記載しており、事実と食い違います。またこれらの経路ではH4が無いため、救済メタも旗も残りません。修正案(推奨): `generate_candidates`が開始時にcontextvarをセットし、H1・H2は`rescue_enabled() and 文脈有効`のときだけ発火するようにします。旧経路で救済されないことをtestで固定してください。代案: 旧経路にも適用すると決めるなら、DESIGN・台帳の記載を訂正し、旧経路でのgoldenとtestを追加してください。(c) 環境変数のkill switchは許容します。読取りは1関数のみで、既定はON、OFFにしても承認済みの旧挙動に戻るだけです。ただし外部依存が増えるので、R2の記録と、testでの環境変数の固定が必要です。testは現状環境変数を固定しておらず(`test_:290-297`はdelのみ)、シェルに`EIGO_KP_RESCUE=0`が残っていると結果が変わります。(d) ZのSRC D1・人称整合はH3の後段にあり、救済後itemにも通常どおり適用されます(`er119:271-282`)。Yの本番経路(`er121:569`)は`generate_candidates`を経由するので適用されます。OF-KPRW-M4(test改訂の漏れ): H1を配線すると、既存の次の2件が確実に失敗します。`er105_kp_rule_compliance_test_01.py:100`(`can of worms`がblockedであることをassert)、同`:61-67 test_idiom_exceptions_are_not_wired`。DESIGN §3に挙がっている改訂対象は`test_rescue_flow_not_wired_in_er105`だけです。上の2件を「旧規則の撤去」として改訂対象に明記し、`will be missed`/`could not bear`/`time is money`/`is money`が引き続き拒否されることは残してください。test緩和に見えないよう、改訂理由を記録してください。

論点2・3にまたがる指摘 → 要修正(M1)。OF-KPRW-M1(H2が重複Gateを迂回): `validate_and_resolve`の`seen`(重複検出)は元の句で登録されます(`er105:239-242`)。救済後の句は重複判定を通りません。例えばLLMが`catch their interest`(本文に連続一致しない)と`caught their interest`を同時に返すと、D1救済で同じ句が2件になります。「重複」は承認済みのblocking条件です。`word_count`・`declared_word_count_mismatch`も元の句の値のまま残ります。修正案: H2で救済が成功したら、救済後の句の正規化keyで`seen`を再照合します。重複なら救済せず、元のreasonを維持します。`wc`・`hits`・rec欄は救済後の句で再計算してください。testを1件追加してください。

論点4 retry/resume一貫性 → 要修正(M3、推奨R4・R5)。OF-KPRW-M3: 外側retryの条件は`n_auto<3 and gate_dropped`です(`er119:334`)。canonicalization段で救済されたがauto不可の候補(NOT_REJUDGEDまたはQA FAIL。revertでは多発する見込み)はdroppedに入らないため、`n_auto<3`でもretryが発動しません。結果としてHRなし経路では、救済前ならretryで得られた3件目のauto候補を失います。「救済成功で候補が足りればretryしない」という意図と、実装が食い違っています。修正案: retryの条件を`n_auto<3 and (gate_dropped or 救済済みかつauto不可の候補あり)`にします。auto不可の救済候補はF1累積除外に入れない(再選定されればHR候補として残す)ことを推奨します。費用増は承認済みの`max_outer`内に収まります。F1累積へ入れるか(=旧M5)はFable判断で構いません。(b) canonicalization Gate内のretryを消費しない設計は妥当です。resume時の古い救済結果: 読み戻しを優先し、古い救済結果が残ることは許容します。理由はHR候補の不変性を優先すべきだからです。ただしドリフトを検知できるようにしてください(→R2)。OF-KPRW-R2: `kp_candidates.json`のdoc単位で次を記録し、resume時に現在値と違えばlogに残すだけにしてください(停止はしない)。辞書sha、`lexicon_status`、`rescue_enabled`の値、er125の`SCHEMA`。OF-KPRW-R4: `verify_persisted_rescue`(`er125:616-623`)はsha自己整合だけを見ています。誰でもshaを再計算できるので、手編集の検出力は弱いです。`rescued_key == validator_args.key == item.key_phrase`の一致確認と、保存済み引数でのvalidator再実行(決定論・API 0、報告のみ)を追加してください。OF-KPRW-R5: 既存run(AI島`run_ai_01`)のtestは、ファイルが無いとskipします(`test_:639`)。またannotateしか見ていません。委任_02では、`ensure_kp_review`に「呼ばれたら例外を出すgenerate_fn」を渡すresume統合testを、固定fixtureで追加してください。OF-KPRW-R6: 選定段の`apply_exclusions`(`er105:498`)は救済後の句しか照合しません。H4の`ng_blocked`で最終的には捕まりますが、早い段階で元の句も照合すればcanonicalizationの費用を節約できます。Human NGの「similar」判定も元の句には効いていません。

論点5 Fable解釈 → 問題なし(承認範囲内)。「6語以上を意味のない短縮で救済しない」を「短縮救済は一切しない」と解釈した点は、承認範囲の拡大ではありません。新しい仕組みを入れない保守側の解釈で、承認行の主文「5語以下 制限維持」とも整合します。ただし、ユーザーが提示した事例のうち`too soon to wave a flag`は救済されないまま残ります。完了報告ではこの事実を明示してください。判断を求める必要はありません。

論点6 見落とし → 問題なし(推奨R7)。量化詞限定詞guard(`er105:1022-1032`)は、既存条件で不受理だった場合にだけ追加判定する単調な追加です。活用一致を必須とし、名詞・分詞は除外表で弾いています。副作用は見当たりません。OF-KPRW-R7: R5(縮約形)を後続へ回す判断は妥当です。R5を是正するとguardが厳しくなり、例えばASCIIの`can't afford`のような辞書にない句が新たに拒否されます。これは独立した影響測定が必要な挙動変更です。現状では、ASCIIの`it can't be helped`が主語付きのまま受理され、曲線引用符の場合だけ核へ救済されるという非対称が残ります。OPENにこの非対称を追記してください。

次に進めるか: 条件付き可: M1、M2、M3、M4を委任_02で是正し、testで固定すれば、配線とruntime evidenceへ進んでよい。R1〜R7は同じ委任内での対応を推奨しますが、blockingではありません。
(Opus所見全文ここまで)

## 実施事項

1. **M1〜M4+R1〜R7の反映**(上記Fable決定どおり)→`FIX_01.md`(各IDの差分:行・test名)。
2. **配線4箇所**(H1 `er105:941`、H2 `er105 validate_and_resolve:225`、H3 `scaffold:475`+`er119:162`、H4 `er119:305`+`rv:829`)を既定ONで実施。契機のcontextvar(M2)。`candidates_sha256`に救済メタ包含。既存run `run_ai_01`のHR候補不変をtestで固定(R5)。
3. **test**: er125(拡張)、er105(rule_compliance改訂+isolation)、er119(配線後の統合: 救済発生/非発生/auto不可→retry/resume読み戻し/旧経路非発火/A/B/C golden 1002不変/敵対的85/実データ133・334対)。回帰: `er125*`、`er105*`、`er123*`、`er119*`、`er003*`(遮断harness・`.venv`)。HEAD既存失敗2件(er119 isolation/grammar_files)は既知として記録(新規失敗0)。環境変数ON/OFF両方を固定。
4. **runtime evidence(fresh、正式初回Production経路のKP stage限定)**: 各Family 1記事×Std/Adv=6 level-run。run dirは新規(既存runの複製で入力を揃え、KP stageのみ起動。TTS/本文生成が走らないことを事前確認)。候補: X=`uk_train_speaker_playback`(新run `__run_kprescue_ev_01`、`er019 --stage kp`相当)、Y=`redelivery_fee`(新run `run_kprescue_ev_01`、`er121 --stage kp`相当。`run_voice_puck_ev_01`/`run_01`不使用)、Z=`melos`(新run `run_kprescue_ev_01`、`er026 --stage kp`相当。`run_fzcw_e1_01`不使用)。各runnerのKP stage引数名は`--help`で確定し全文記録。取得する証拠: (i)救済フロー発火の有無と内容(元句→救済形・理由コード・経路[選定段/canonicalization段]・auto_eligible・QA再判定結果・key一致率[R3: revert/M1別])、(ii)actual model_id・routing・Prompt sha(無変更)、(iii)候補ファイルの救済メタ・doc単位記録(R2)、(iv)同引数再起動で再計算なし・API 0(resume読み戻し)、(v)外側retryの発動有無とM3条件の挙動、(vi)Z SRC D1・人称整合の適用、(vii)費用(cost_log)。救済が1件も発生しないlevel-runは「発火なし(経路到達は確認)」として記録し、**既知事例のreplay**(AI島Std本文で`studied separately`、Z r3本文で`rose above`/`held out`、Y a2本文で`it can’t be helped`等=`case_fixtures_01.json`)を**正式`generate_candidates`経由**(本文とLLM出力を固定fixtureで注入=LLM callはgloss再整合/QA再判定のみ実課金)で各Family少なくとも1件ずつ実行し、救済形がHR候補表に`RESCUED`旗付きで載る/HRなし経路でauto_eligibleが規則どおり決まることを確認。起動前`py tools\stop_scope_check_01.py --managed-id KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 --run-dir <run dir> --out <docs/research/.../stop_check_02_<family>.json>`、150秒規律、各run dir 5分3回禁止。
5. **成果物**: `FIX_01.md`、`WIRING_01.md`(配線箇所:行・contextvar・kill switch)、`EVIDENCE_01.md`+`evidence_01.json`(Family×レベル×項目(i)〜(vii)の表、未検証項目はFamily別に明示)、`COST_01.md`、`OPUS_REVIEW_03.md`(Opus所見全文)、`SPEC_LEDGER_02.md`(QA再判定の限界追記、ユーザー§3の12要件チェックリスト)。

## KPI provenance欄

evidence=fresh(production_formal_path、KP stage限定、新規run dir)+replay(fixture注入=synthetic入力・実gloss/QA call)。E2E自己確認: Yes(KP stageの初回path)、TTS以降は対象外。

## Opus台帳更新

`OF-KPRW-M1〜M4/R1〜R7`の新規行と、`OF-KPRS-M1〜M6/R1〜R4`・`OF-KPRS2`のIMPLEMENTED→EVIDENCED遷移をRESULT_PACKET(9)に文案として記載(台帳編集はFable sync)。

## 事前指定Read一覧

- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/{DESIGN_03,SPEC_LEDGER_01,TEST_PLAN_01,BUDGET_PLAN_02,OPUS_REVIEW_REQUEST_03}.md` 全文、`case_fixtures_01.json`
- `er125_kp_rescue_production_01.py` 全文、`er125_kp_rescue_production_test_01.py`: Grep `def test_|EIGO_KP_RESCUE|skip` → ±10
- `er105_kp_fulltext_selector_01.py`: Grep `def validate_and_resolve|seen|contains_finite_aux_role_based|def apply_exclusions|def run_selection_gate` → ±40
- `er119_kp_candidates_01.py:140-180,260-345`、Grep `def ensure_kp_review|candidates_sha256|def generate_candidates` → ±30
- `er003_v1_n3_01_scaffold_generate.py:460-560`
- `er105_kp_rule_compliance_test_01.py` 全文(改訂対象)
- `er062_family_z_writer_01.py`: Grep `run_kp_with_outer_retry_fulltext` → ±20、`er121_family_y_runner_01.py:535-575`、`er026_family_z_fiction_production_runner_01.py`: Grep `_kp_fn_for_ctx|--stage|stage_kp|def stage_` → ±15、`er019_family_x_audio_production_runner_01.py`: Grep `stage_kp|--stage|kp_review|ensure_kp_review` → ±15
- `docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/CURRENT_BASELINE_01.md`: Grep `uk_train|melos|run|cost` → ±5(KP生成の起動実例・費用実績の参照)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `EIGO_KP_RESCUE` 全repo → 読取り箇所が1関数のみであることを維持
- Grep `run_selection_gate\(|validate_and_resolve\(` 全repo → M2の旧経路一覧をWIRING_01へ
- 成果物は`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/`に追記ファイルとして新規作成

## 実行コマンド全文

- 回帰(遮断harness・`.venv`): `.venv\Scripts\python.exe run_project_regression.py --pattern "er125*_test_*.py"`、`--pattern "er105*_test_*.py"`、`--pattern "er123*_test_*.py"`、`--pattern "er119*_test_*.py"`、`--pattern "er003*_test_*.py"`
- A/B/C golden比較: `.venv\Scripts\python.exe docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\tools\gen_abc_golden_01.py --out C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\abc_golden_check2.json`(引数は`--help`で実値確認)→`abc_golden_01.json`とバイト比較
- evidence(有料・KP stage限定、引数は`--help`で確定し全文記録): 例 `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug uk_train_speaker_playback --run run_kprescue_ev_01 --level both --stage kp --budget-jpy 40`(実名に置換)/`.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_kprescue_ev_01 --stages kp --theme-package <実path> --reuse-manifest <実path> --approved-budget-jpy 40 --tts-execution-mode STANDARD`/`.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --slug melos --run run_kprescue_ev_01 --stage kp --budget-jpy 40`(実名に置換)。同引数再起動で再計算なし・API 0を各1回(150秒以上後)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KPRW2.md`(9)に最終文案: CURRENT_SPEC新節「Key Phrase Gate除外救済方式(APPROVED_FOR_PRODUCTION 2026-10-26、Status=<EVIDENCE_COLLECTED Family別>)」(採用表・不採用[短縮・CMU分解・本文外語]・慣用句一般機構[辞書・sha・fail-closed]・HRあり/なし・resume/retry・kill switch・配線4箇所・evidence path・費用)、OPEN-529=配線済み(Fable判定待ち)、OPEN-530/152/456との関係、縮約形非対称の新規OPEN案(R7)、DECISION_LOG案、Opus台帳案。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: 変更コード(`er125_*`、`er105_kp_fulltext_selector_01.py`、`er119_kp_candidates_01.py`、`er003_v1_n3_01_scaffold_generate.py`、test群)、`data/kp_idiom_lexicon_01/denylist.txt`(+meta更新があれば)、`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/`配下、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_{DELEGATION_02,OPUS_REQUEST_03}.md`(+check.json)。run dir配下は追跡しない(evidenceの写しはjson/mdでdocs側へ)。pathspec付きcommit(2回可: ①是正+配線+test ②evidence)。
- commit message: ①`KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02: Opus M1〜M4/R1〜R7反映+救済フローをX/Y/Z共通KP経路へ配線(既定ON、kill switch、旧経路非発火、A/B/C不変、test)` ②`… X/Y/Z Std/Adv runtime evidence+既知事例replay(KP stage限定、実費<x>円、PRODUCTION_WIRED判定はFable)`
- trailer: `Delegation: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/02`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPRW2.md`: (0)T-0、(1)M1〜M4/R1〜R7の反映表(ID・差分:行・test)、(2)配線箇所とcontextvar/kill switch、(3)test・回帰結果(件数・接続試行0・HEAD既存失敗)、(4)evidence表(Family×レベル×(i)〜(vii)、発火あり/なし/replay、未検証項目をFamily別に明示)、(5)ユーザー§3 12要件チェックリスト(各要件に証拠:path)、(6)実際に救済できたパターンと品質検証結果(11件表の最終+evidenceで新たに救済された句)、(7)費用・量産単価影響(実測)、(8)判断候補(あれば)、(9)SSOT文案・Opus台帳文案、(10)必須4行+「判定整合: 重大NG=<なし|あり>」、(11)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。`too soon to wave a flag`が救済されないまま残る事実を明記。