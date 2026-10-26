# OPUS_REVIEW_03: Production配線前の独立技術レビュー(PM_GOVERNANCE 11-3 条件A)全文

管理ID: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 / 2026-10-26 / 依頼文=`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_OPUS_REQUEST_03.md`
(以下、委任_02の委任文に逐語で貼られたOpus所見全文。Fable決定[全件採用]は委任_02本文に記載。)

## Fable決定(全件採用)
- M1(H2が重複Gateを迂回): H2で救済成功時、救済後句の正規化keyで`seen`を再照合。重複なら救済せず元reasonを維持。`wc`・`hits`・rec欄は救済後句で再計算。test追加。
- M2(H1/H2が環境変数だけで全経路に効く): `generate_candidates`開始時にcontextvarをセットし、H1・H2は`rescue_enabled() and 文脈有効`のときだけ発火。旧経路(`er062:1364`、`er121:538-551`旧kp_fnアダプタ、run_selection_gateの他呼出元)で救済されないことをtestで固定(golden不変)。
- M3(外側retry条件): `n_auto<3 and (gate_dropped or 救済済みかつauto不可の候補あり)`。auto不可の救済候補はF1累積除外に入れない。旧M5の「救済失敗のみF1累積」は維持。test追加。
- M4(既存test改訂の漏れ): `er105_kp_rule_compliance_test_01.py:100`と`:61-67 test_idiom_exceptions_are_not_wired`と`test_rescue_flow_not_wired_in_er105`を「旧規則の撤去」として改訂。`will be missed`/`could not bear`/`time is money`/`is money`が引き続き拒否されるassertは残す。
- R1: denylistへ卑語・俗語4件(`have one's shit together`/`have someone by the balls`/`have the hots for`/`have several seats`)を予防追加。`flags.idiom_exception`は既存guardが実際に拒否した句だけに付ける。
- R2: `kp_candidates.json`のdoc単位に辞書sha・`lexicon_status`・`rescue_enabled`・er125 `SCHEMA`を記録。resume時に現在値と違えばlogのみ(停止しない)。
- R3: evidenceでQA再判定のkey一致率をrevertとM1に分けて計測。revertで一致率≈0ならrevertのQA callを省く案を報告(本委任では変更しない)。
- R4: `verify_persisted_rescue`に`rescued_key == validator_args.key == item.key_phrase`一致確認+保存済み引数でのvalidator再実行(API 0、報告のみ)を追加。
- R5: AI島`run_ai_01`のresume統合test(`ensure_kp_review`に「呼ばれたら例外を出すgenerate_fn」を渡す、固定fixture、skipしない)を追加。
- R6: 選定段`apply_exclusions`で元の句も照合。安い場合のみ実装。
- R7: 縮約形R5の非対称(ASCII `can't`主語付き受理/curly核へ救済)をOPEN文案に追記。
- 環境変数kill switch: 許容。testで`EIGO_KP_RESCUE`を明示固定。
- SPEC_LEDGER追記: QA再判定の限界を明記。

## Opus所見全文

結論: 条件付きでProduction配線(委任_02)へ進んでよい。条件は、配線前に必須の4件(M1〜M4)を委任_02の中で是正し、testで固定すること。設計の核は承認文の範囲内で、fail-closed(失敗時は救済しない安全側)も成立しています。ただし配線仕様に、Gateの迂回、仕様文との乖離、test計画の漏れが残っています。

論点1 慣用句の一般機構 → 問題なし(推奨R1・R2あり)。25件の目視結果: 卑語・侮蔑語・ことわざの断片・名詞主語の完全文は含まれていません。学習価値がやや低いのは`can of corn`(野球の俗語)、`could not get elected dogcatcher`(米国の政治慣用句)、`have done with`(やや古風)の3件です。ただし本機構は「誤った除外を外すだけ」で、候補へ押し込むものではありません。選定LLM・本文一致・QAを通る必要があるため、許容範囲と判断します。気づいた点: `can of worms`/`can of corn`は名詞の`can`が`aux_start`として通っています。構造条件ではなく辞書一致で救われている例です。結果は正しい(既存guardの誤判定を是正する方向)ですが、`a can of beans`は引き続き拒否されます。これは既存guardの問題であり、本件の範囲外です。構造条件の抜け: `shan't`/`needn't`がない、`cannot`/`can not`/`can't`を相互に変換しない、2語以上の主語は除去しない、`oneself`は対象外。いずれも救済が減る方向で、誤受理リスクはありません。2語以上の主語を除去しない点はOpus-02 M3に整合しています。sha再ピン: コード定数とmeta.jsonの二重ピンで、不一致時は空表=例外なしになります(`er125:93-105`)。不一致でも「旧挙動に戻る」だけなので品質面は安全ですが、劣化に気づけません(→R2)。OF-KPRW-R1: 116件のうち、現時点では判断を変えない卑語・俗語4件(`have one's shit together`/`have someone by the balls`/`have the hots for`/`have several seats`)を予防的にdenylistへ追加することを推奨します。将来R5の是正やhave役割判定の変更で有効になる可能性があるためです。あわせて`annotate_candidate`(`er125:578-581`)の`flags.idiom_exception`は、既存guardが実際に拒否した句だけに付けてください。現状は`have a say`等にも付き、HRが誤解します。

論点2 HRなし経路のβ(QA再判定) → 問題なし(推奨R3)。(a) 承認済みtemplate・schemaは無変更で、promptへ渡るのは4キーだけです(`er003:363-371`)。Prompt変更には当たりません。ただし`display_phrase=救済後key`のため、元の表層形→救済後keyの変換を評価する4項目(`qa_meaning_or_usage_unchanged`/`qa_core_meaning_preserved`/`qa_no_semantic_role_loss`/`qa_not_over_minimized`)は自己比較になり、ほぼ必ずPASSします。変換の正しさは、最終Gateと同一引数の決定論validatorと、M1の{display語, LLM語}限定だけで担保されます。「単位としての評価」と割り切るなら妥当ですが、SPEC_LEDGERにこの限界を明記してください。(b) 救済後keyと返却keyが不一致ならNOT_REJUDGEDになり、HRでのみ採用可です(`er125:504`)。安全側として十分です。ただしrevertでは、同じ入力に対してLLMが前回と同じ原形化keyを返す可能性が高いです。その場合、β下でもrevert救済は事実上HRでのみ採用可になる見込みです。(c) 選定段の救済(D1・慣用句の核)に追加条件を付けない判断は妥当です。OF-KPRW-R3: 委任_02のevidenceで、key一致率をrevertとM1に分けて計測してください。revertで一致率がほぼ0なら、revertではQA callを省いて費用を削ることも検討してください。

論点3 既定ON・配線4箇所 → 要修正(M2・M4)。(a) A/B/C経路への波及はありません。validatorは`allow_inflection_normalization=False`の場合に旧関数を使い(`er003:629-633`)、H1は通りません。(b) M6は保たれます。H1は1関数(`er105:941`)の中にあり、er125の`_gate`も同じvalidatorを経由するためです。OF-KPRW-M2(漏れ): H1とH2は環境変数`EIGO_KP_RESCUE`だけで有効になります。そのため`validate_and_resolve`と全文選定validatorを使う全経路に効きます。対象は`er062:1364 run_kp_with_outer_retry_fulltext`(Zの`_kp_fn_for_ctx`の既定、`er026:1717`)、Yの旧`kp_fn`アダプタ(`er121:538-551`)、run_selection_gateを使う全呼出元です。一方、DESIGN_03 §1と台帳OF-KPRS-M2は「旧候補なし経路は挙動不変(バイト同一)」と記載しており、事実と食い違います。またこれらの経路ではH4が無いため、救済メタも旗も残りません。修正案(推奨): `generate_candidates`が開始時にcontextvarをセットし、H1・H2は`rescue_enabled() and 文脈有効`のときだけ発火するようにします。旧経路で救済されないことをtestで固定してください。代案: 旧経路にも適用すると決めるなら、DESIGN・台帳の記載を訂正し、旧経路でのgoldenとtestを追加してください。(c) 環境変数のkill switchは許容します。読取りは1関数のみで、既定はON、OFFにしても承認済みの旧挙動に戻るだけです。ただし外部依存が増えるので、R2の記録と、testでの環境変数の固定が必要です。testは現状環境変数を固定しておらず(`test_:290-297`はdelのみ)、シェルに`EIGO_KP_RESCUE=0`が残っていると結果が変わります。(d) ZのSRC D1・人称整合はH3の後段にあり、救済後itemにも通常どおり適用されます(`er119:271-282`)。Yの本番経路(`er121:569`)は`generate_candidates`を経由するので適用されます。OF-KPRW-M4(test改訂の漏れ): H1を配線すると、既存の次の2件が確実に失敗します。`er105_kp_rule_compliance_test_01.py:100`(`can of worms`がblockedであることをassert)、同`:61-67 test_idiom_exceptions_are_not_wired`。DESIGN §3に挙がっている改訂対象は`test_rescue_flow_not_wired_in_er105`だけです。上の2件を「旧規則の撤去」として改訂対象に明記し、`will be missed`/`could not bear`/`time is money`/`is money`が引き続き拒否されることは残してください。test緩和に見えないよう、改訂理由を記録してください。

論点2・3にまたがる指摘 → 要修正(M1)。OF-KPRW-M1(H2が重複Gateを迂回): `validate_and_resolve`の`seen`(重複検出)は元の句で登録されます(`er105:239-242`)。救済後の句は重複判定を通りません。例えばLLMが`catch their interest`(本文に連続一致しない)と`caught their interest`を同時に返すと、D1救済で同じ句が2件になります。「重複」は承認済みのblocking条件です。`word_count`・`declared_word_count_mismatch`も元の句の値のまま残ります。修正案: H2で救済が成功したら、救済後の句の正規化keyで`seen`を再照合します。重複なら救済せず、元のreasonを維持します。`wc`・`hits`・rec欄は救済後の句で再計算してください。testを1件追加してください。

論点4 retry/resume一貫性 → 要修正(M3、推奨R4・R5)。OF-KPRW-M3: 外側retryの条件は`n_auto<3 and gate_dropped`です(`er119:334`)。canonicalization段で救済されたがauto不可の候補(NOT_REJUDGEDまたはQA FAIL。revertでは多発する見込み)はdroppedに入らないため、`n_auto<3`でもretryが発動しません。結果としてHRなし経路では、救済前ならretryで得られた3件目のauto候補を失います。「救済成功で候補が足りればretryしない」という意図と、実装が食い違っています。修正案: retryの条件を`n_auto<3 and (gate_dropped or 救済済みかつauto不可の候補あり)`にします。auto不可の救済候補はF1累積除外に入れない(再選定されればHR候補として残す)ことを推奨します。費用増は承認済みの`max_outer`内に収まります。F1累積へ入れるか(=旧M5)はFable判断で構いません。(b) canonicalization Gate内のretryを消費しない設計は妥当です。resume時の古い救済結果: 読み戻しを優先し、古い救済結果が残ることは許容します。理由はHR候補の不変性を優先すべきだからです。ただしドリフトを検知できるようにしてください(→R2)。OF-KPRW-R2: `kp_candidates.json`のdoc単位で次を記録し、resume時に現在値と違えばlogに残すだけにしてください(停止はしない)。辞書sha、`lexicon_status`、`rescue_enabled`の値、er125の`SCHEMA`。OF-KPRW-R4: `verify_persisted_rescue`(`er125:616-623`)はsha自己整合だけを見ています。誰でもshaを再計算できるので、手編集の検出力は弱いです。`rescued_key == validator_args.key == item.key_phrase`の一致確認と、保存済み引数でのvalidator再実行(決定論・API 0・報告のみ)を追加してください。OF-KPRW-R5: 既存run(AI島`run_ai_01`)のtestは、ファイルが無いとskipします(`test_:639`)。またannotateしか見ていません。委任_02では、`ensure_kp_review`に「呼ばれたら例外を出すgenerate_fn」を渡すresume統合testを、固定fixtureで追加してください。OF-KPRW-R6: 選定段の`apply_exclusions`(`er105:498`)は救済後の句しか照合しません。H4の`ng_blocked`で最終的には捕まりますが、早い段階で元の句も照合すればcanonicalizationの費用を節約できます。Human NGの「similar」判定も元の句には効いていません。

論点5 Fable解釈 → 問題なし(承認範囲内)。「6語以上を意味のない短縮で救済しない」を「短縮救済は一切しない」と解釈した点は、承認範囲の拡大ではありません。新しい仕組みを入れない保守側の解釈で、承認行の主文「5語以下 制限維持」とも整合します。ただし、ユーザーが提示した事例のうち`too soon to wave a flag`は救済されないまま残ります。完了報告ではこの事実を明示してください。判断を求める必要はありません。

論点6 見落とし → 問題なし(推奨R7)。量化詞限定詞guard(`er105:1022-1032`)は、既存条件で不受理だった場合にだけ追加判定する単調な追加です。活用一致を必須とし、名詞・分詞は除外表で弾いています。副作用は見当たりません。OF-KPRW-R7: R5(縮約形)を後続へ回す判断は妥当です。R5を是正するとguardが厳しくなり、例えばASCIIの`can't afford`のような辞書にない句が新たに拒否されます。これは独立した影響測定が必要な挙動変更です。現状では、ASCIIの`it can't be helped`が主語付きのまま受理され、曲線引用符の場合だけ核へ救済されるという非対称が残ります。OPENにこの非対称を追記してください。

次に進めるか: 条件付き可: M1、M2、M3、M4を委任_02で是正し、testで固定すれば、配線とruntime evidenceへ進んでよい。R1〜R7は同じ委任内での対応を推奨しますが、blockingではありません。
