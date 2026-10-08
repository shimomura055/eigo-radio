# COUNTERMEASURES_01: EN化段のNG(軽微・重大)に対する対策案(実装しない・優先順位を付けない)

管理ID: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_01 / 日付 2026-10-08 / Status: PROPOSED(案の整理のみ。Productionへの採用は`APPROVED_FOR_PRODUCTION`が必要で、人間ユーザーだけが承認できる)
根拠は同ディレクトリの `ANALYSIS_01.md`(以下「分析」)。件数は全て分析の表に出典がある。判断はFable/Opus/ユーザー。

前提(分析の要点):
- 翻訳段由来/増幅は26事象(軽微24・重大2)。型は数8・主体7・因果3・付け足し3・範囲2・強さ1・時制1・訳語1。箇所は本文17・末尾要約9(文あたり 15% vs 1.1%)。
- EN deviation checkは当該26事象のうち5事象のみ指摘(全MINOR)。Checkerは候補化14/24、書き換え4。両方が素通りした事象は10/24。
- EN STOP(translation起源MAJOR)8世代は全て末尾要約。要約MAJORの再生成成功は6/14、本文は10/10。コード上、要約の再生成にはmust-fixが渡らない(分析4-2)。
- コスト換算に使った確認済み単価: `er005_output/cost_baseline_01/pricing_snapshot.json`(PROJECT_INTERNAL_RECORD)の gpt-6-luna 入力 $0.1/1Mトークン・出力 $0.5/1Mトークン、USD_JPY=160(`er003_v1_n3_01_advanced_adaptation_generate.py` L365)。トークン数は `gpt6_wiring_e2e_01/run_02/raw_usage_log.jsonl` の実測(translation call 入力1,377・出力2,079、in_one_line call 入力652・出力128、deviation check call 入力3,837・出力590)。以下の「¥」は、この実測トークンと単価からの換算(概算)で、追加callの実測ではない。

## 案の一覧(優先順位なし)

| 案 | 狙う型(分析の件数) | 変更箇所 | 規模 | 追加費用の見込み | 主な副作用 |
|---|---|---|---|---|---|
| A. EN翻訳の入力に台帳+保持指示を追加 | 数8・主体(省略補完)2・係り受け1・指示対象1 | `FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION`、`generate_family_x_faithful_translation`、`_run_writer_stage_once` | M | 入力 +約2〜3k tokens(概算) = 約¥0.03〜0.05/本 | 逐語転記/sha固定テスト更新、JAに無い台帳情報の混入 |
| B. 「In one line」の生成方式見直し | 要約9事象+EN STOP 8世代 | `generate_family_x_in_one_line`、`_run_writer_stage_once` | S〜L(B1〜B4で異なる) | B1 ¥0(むしろ削減)、B2 約¥0.06〜0.07/本、B3 JA writer追加callは未測定 | 製品構造(Contract)変更はB1/B4のみ要承認 |
| C. JA↔EN決定論チェック(数・固有名詞・時制) | 数8・時制1・(固有名詞/数値は今回0件) | 新規モジュール(検査のみ)、runner呼び出し | M | ¥0/本(API無し) | 誤検知、台帳なしで単複正否は不明 |
| D. EN deviation checkの分類器・origin判定改修 | 主体(EV-25型)・数・originの誤分類(3事象) | `DEVIATION_PROMPT_TEMPLATE`、`ORIGIN_INSTRUCTION_TEMPLATE`、(任意)追加call | M(プロンプトのみならS〜M) | プロンプトのみ: トークン増は微小(未測定)。追加call: 約¥0.11/本 | MAJOR増→STOP率上昇、フラグ定義変更の波及 |
| E. Checker側の見逃し対策(第2意見の変更ではなくStage 1入力の補強) | EV-25型(重大)・数 | Checker Stage 1候補生成(`er052_open233_self_recovery_flow_runner_01.py`)、EN deviation check→Checker連携 | M〜L | Stage 2は1claimあたり約¥0.03(実測 ¥0.4459/14claim) | Checkerの書き換えが増える、Opus条件A該当 |
| F. タイトル・固有名詞/用語の訳語固定 | 訳語1+タイトル(保留1)+指示対象 | 台帳→用語表、翻訳prompt | M | 入力微増(未測定) | n不足(根拠が薄い) |
| G1. JA側で集合名詞を台帳表記へ固定(上流) | 数(幹部)5事象 | JA writer prompt(役職は台帳表記) | S〜M | JA再生成を伴わない運用なら¥0。検証にJA writer callが必要(未測定) | JA文体、JA側Production変更 |
| G2. 要約再生成へのmust-fix受け渡し(B2の最小形) | EN STOP 8世代 | `generate_family_x_in_one_line`に引数追加、runner | S | 再生成時のみ入力 +数百tokens(概算 ¥0.01以下/回) | ほぼ無し(原因仮説の検証が先) |
| G3. EN deviation checkのtranslation起源MINORを記録(観測のみ) | 全般(測定不足の解消) | audit/telemetry | S | ¥0 | 無し |

## A. EN翻訳の入力に台帳と保持指示を追加

- 狙う型: 「日本語の数無標」8事象(幹部5・機関2・従業員1)、「主語省略の誤補完」2事象(EV-25 Meta was asked、EV-45 anyone)、係り受け1事象(EV-10)、指示対象1事象(EV-18 the feature)。根拠: 現行の翻訳callは日本語本文のみを受け取り台帳を持たない(分析4-1)。「副社長」と書かれたJAは9/9で誤り0、「幹部」は6/9で複数形になった(分析3-2)。
- 変更箇所: (1) `FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION`(`er003_v1_n3_01_advanced_adaptation_generate.py` L526-)に「Ledgerにある単数/複数・主体・対象をJAの意味の範囲で保つ」「日本語で主体・数が省略されている場合は、台帳が示す値を超えて補完しない」等の保持指示を追加、(2) `generate_family_x_faithful_translation`のシグネチャに台帳引数を追加、(3) `_run_writer_stage_once`が既に持つ`ledger_text`を渡す。
- 規模: M。プロンプト定数は`er045`の逐語転記でsha同一性テスト(`er019_family_x_new_structure_wiring_01_test_01.py`)があり、変更時にテスト更新が必要。Trial(DEV)で効果確認 → ユーザー承認 → 配線の順。
- 追加費用: 翻訳callの入力が約1,377 → 約4k tokens(台帳分は run_02 の deviation check 入力3,837 tokens から記事・テンプレート分を除いた概算2〜3k。台帳単体のtoken数は未測定)。換算で +約¥0.03〜0.05/本(出力は不変の想定)。
- 副作用: (i)台帳の情報がJA本文に無いのに英語へ入る(JA/EN不一致、unsupported_new_claim)。例えばJAが「幹部」なのにENだけ"a vice president"になる。(ii)「逐語翻訳」という設計(er045)との整合。(iii)台帳の誤りや曖昧語が英語へ波及。
- 検証方法: 既存のJA R2(`ja_writer/revision2.md`、EN本文のある59記事分と、STOPで未完のrunのJA R2)を入力に、現行プロンプトとA案プロンプトでENを生成し、(a)数・主体の型を `ANALYSIS_01.md` の26事象のJA対応文に対して機械的に突合、(b)盲検LLM判定(判定者の再現性が27%と低いため、複数判定者または固定チェックリスト併用)で比較。翻訳call 1本あたり入力約4k・出力約2.1k tokensの換算で約¥0.23/本、59本で約¥14(概算。判定コストは未測定)。

## B. 「In one line」要約の生成方式

要約は日本語に対応文が無く、英語記事だけから別callで生成され(入力は英語本文のみ・指示は「12-18語・最重要の1点・新しい事実を足さない」)、台帳にもJAにも直接は照合されない(分析4-1)。EN STOPの全8世代、盲検NGの末尾要約9事象がここに集中する。

- B1. 要約の生成を停止する(Contractから `## In one line` を外す)。変更: `ADVANCED_CONTRACT_SUFFIX_LINES`、`_run_writer_stage_once`、音声の `parts["in_one_line"]` 利用(`er012_e_family_entertainment_two_level_runner_01.py` L798/L856)、分割関数。規模L。要約は製品構造(Standard/Advanced共通のContract)の一部であり、削除は**製品仕様変更**でユーザー承認必須。費用は逆に減る(in_one_line call 約¥0.02/本、入力652・出力128 tokensの換算)。副作用: 番組の結びの文が無くなる。検証: 構造Gate・音声分割のregression。
- B2. 要約の入力に日本語本文+台帳+「対象を狭めない/広げない」指示を追加し、語数指定を緩める(例: 12-18語を目安のみにする)。変更: `FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE`(L552-)、`generate_family_x_in_one_line`のシグネチャ。規模S〜M。追加費用: 入力 +約4k tokens(JA本文約1.5k+台帳約2〜3k、概算) = 約¥0.06〜0.07/本。副作用: 台帳の語が要約に入り「新しい事実」扱いになる可能性、語数制約緩和で音声が長くなる。根拠: 要約の誤りは修飾語の脱落(human concierge feature → "AI phone feature"/"Muse's test")、因果化(kept prices high)、受け手/かけ手(callers)など、圧縮で起きる(分析3-2)。
- B3. 要約をJA側で生成する(JA writerの出力に日本語の1文を含め、JA Fact Check(台帳照合)を通し、ENは忠実英訳する)。変更: JA writer契約・JA Fact Check・翻訳。規模L。追加費用: JA writer側のcall/トークン増は未測定。副作用: JA側Productionの構造変更で承認必須。利点: 要約も台帳照合の対象になり、主体・数・範囲の検査が既存のJA経路(Fact Lock系を含む)で効く。
- B4. 要約を台帳照合の対象に明示化(現行のEN deviation checkは本文と同じ記事全体を見るため、要約専用の質問を追加)。変更: `DEVIATION_PROMPT_TEMPLATE`に要約専用の追加指示(「`## In one line`の各語がLedgerのfact範囲を超えて限定/拡大していないか個別に確認」)、またはsummary専用の別call。規模S(プロンプトのみ)〜M(別call)。別callなら約¥0.11/本(換算)。副作用: 現状の生成時検査は要約MAJORを既に捕捉できているため(attempt1で14世代)、改善は「検出」ではなく「再生成の成功率」側にある(→G2)。
- 共通の検証: 要約MAJORが出た14世代(STOP 8・回復6、`ANALYSIS_01.md` 3-4)のJA R2・台帳を再利用し、要約だけを現行/B2/B4で再生成してdeviation checkのMAJOR率を比較(換算で約¥0.1〜0.2/call × 14〜30件 = 約¥1〜6、概算)。

## C. JA↔EN文対応の決定論チェック

- 狙う型: 数(単複)8、時制1("There are now")。固有名詞・数値の不一致は今回の盲検NGに0件(「ホルムズ」「Meta」「20%」はEN側で保たれていた)ため、効果の見込みは数・時制に限る。
- 方式: Family X翻訳は「JAと同じ段落数・同じ順序」を契約している(分析4-1)ため段落単位の対応が取れる。(1)JAの「数無標語リスト」(幹部/機関/従業員/関係者/当局/専門家 等)と、ENの対応語の複数形(executives/agencies/employees/officials 等)を検出し、「JAが単複を明示していないのにENが複数形」を警告として記録、(2)数字の正規化(漢数字・"1,500"・"千五百")の一致、(3)"now"/"currently"/"today"等の時間副詞の付加検出、(4)JAに無い固有名詞の追加検出。
- 規模: M(新規モジュール+単体テスト。runner配線は別途)。API呼び出し無し = ¥0/本。
- 副作用: 台帳なしでは複数形の正否が判断できない(例: 台帳が複数の従業員なら "employees" が正しい)。まず「警告ログのみ」で運用し、誤検知率を測るのが安全。Gate化すると再生成コストとSTOP率に影響。
- 検証方法: 既存59組のJA R2/ENを入力にオフライン再生(¥0)。26事象(うち数8・時制1)に対する再現率と、JA由来27事象・正しい複数形での誤検知率を測る。

## D. EN deviation checkの分類器・origin判定の改修

- 狙う型: (1)主体の入替(EV-25: `changed_actor`の定義が「発言主体・調査主体」に限られ、依頼主体は`changed_number`でMINORに分類された)、(2)数(単複)の扱い、(3)origin判定(「幹部→executives」3事象が `ja_source` とされた)。根拠: `changed_actor`がtrueの指摘は79件中12件で全て`ja_source`、translation起源は0件(分析2-4)。
- 変更箇所(いずれも`er003_v1_en_direct_vfl_01_generate.py`): 
  - D1. `changed_actor`の定義を「発言主体・調査主体・依頼主体・行為主体・受け手/かけ手(誰が・誰に)を台帳と異なるものにしている」へ拡張(L521、JSON schema・床規則`FLOOR_FLAGS`・`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`への波及を確認する必要あり)。
  - D2. 主体入替の専用質問を追加(「各動詞の主語・目的語・受け手を列挙して台帳の同じfactと比較」)。別callにするなら約¥0.11/本(換算)、既存callへの追記なら出力トークン増のみ(未測定)。
  - D3. `ORIGIN_INSTRUCTION_TEMPLATE`(L672-)に「日本語が単複・主語を明示しておらず、英語で一方に確定させた場合はtranslation」を追記し、`ja_source`誤判定による「JA再確認STOP」への誤誘導を防ぐ。
  - D4. 数(単複)を`changed_number`のMAJORとして扱うか、MINORのまま再生成せず自動修正(C案の置換)するか。MAJOR化すると「幹部」型(67%)の記事がmust-fix再生成の対象になり、1回再生成後に残ればSTOPするため、STOP率が上がる可能性が高い。
- 規模: D1/D3 = プロンプトのみでS〜M(ただしschema/床規則への波及確認が必要)。D2=M。
- 副作用: 偽陽性MAJOR増→STOP増(OPEN-233のO3観測の再評価条件に関わる)、既存T-Bゴールドセットの再校正が必要。
- 検証方法: T-Bゴールドセット(23項目×2モデル×2反復=92記録、既存`T-B/items.json`)に、分析の翻訳起源26事象(EV-25を含む)をfixtureとして追加し、`run_deviation_check`のみを再実行(Pipeline全体は動かさない)。T-Bの実績費用は gpt-6-luna分 ¥5.241(`T-B/cost.json`、92記録)。誤検知は「JA由来27事象」「正しい複数形」を陰性fixtureにして測る。

## E. Checker側の見逃し対策(第2意見の変更ではなく、Stage 1の入力補強)

- 事実関係: 委任文の想定「Stage 2のsecond opinionが格下げして素通り」は、記録上は成り立たない。EV-26(executives)とEV-28(callers)では、一次ACCEPTABLEを第2意見が割ってBLOCKINGにし、書き換えにつながった(`second_opinion.split=true`、分析4-3)。EV-25(重大)が素通りした直接要因は、Stage 1が当該文を別事実(MUSE-HC-010、決定論検査`negation_polarity_mismatch`)の理由で候補化し、依頼者の取り違えを課題として立てなかったこと(devの`changed_*`フラグが全てfalse)。なお承認構成では床は`FLOOR_MODE=number_only`(`changed_number`のみ。`er052_open233_self_recovery_flow_runner_01.py` L500、2026-10-06ユーザー承認)で、主体・否定・比較・時期は機械的な強制BLOCKINGの対象外であり、主体型の安全網はStage 2のLLM判定と第2意見に依存する(Trial A/Bの実行が実際にnumber_onlyだったかはdumpに出力が無く未確認)。したがって「主体・否定・因果型で第2意見による格下げを不可にする」案は、EV-25型には効かない。
- E1. EN deviation checkのtranslation起源MINOR(例: EV-25の`changed_number`)を、Checker Stage 1の候補(devフラグ付き)として引き継ぐ。EN deviation checkはEV-25の文を`changed_number=true`で指摘していたため、候補にフラグが載れば、承認構成でも残る数字の床(`changed_number`、number_only)でBLOCKINGへ昇格し、既存の書き換え経路に乗る可能性がある(実装・動作は未検証。EV-25は元の指摘が数の観点で主体の観点ではないため、書き換えhintは「employees reported」側に向き、依頼者の取り違えが直るかは別問題)。変更箇所: runnerのChecker呼び出し(Stage 1入力)とStage 1候補マージ。規模M。追加費用: Stage 2は1claimあたり約¥0.03(実測 `meta_run03_advanced.json` の第2意見batch ¥0.4459/14claim)で、1記事あたり数claim増。副作用: Checkerの書き換え回数が増え、書き換え自体が新たなNGを生む危険、Stage 1→2の既存配線の再テスト。
- E3. 主体・否定型の床(`FLOOR_MODE=legacy_5flags`)の復活。EV-25型は元のdevの`changed_*`が全てfalseだったため復活しても発火せず、効果は期待できない(E1と併用した場合のみ)。また「数字以外の機械的強制重大化の廃止」は2026-10-06にユーザーが承認した決定であり、覆す場合は`USER_DECISION_REQUIRED`。
- E2. Stage 2の評価時に、related_fact_id以外の全台帳factとも照合する(同一文に対し台帳全体を渡す)。規模L。追加費用: Stage 2入力の増加(未測定)。副作用: Checkerの設計変更でOpus独立レビュー(条件A)の対象。
- 検証方法: 重大2件(EV-25・EV-28)と軽微の数型を含むfixtureでCheckerのreplayが必要(API費用あり。Checker 1 run=17 callで約¥5.8、`meta_run03_advanced.json`実測)。EV-25の1件だけならE1で約¥6/回の見込み。

## F. タイトル・固有名詞/用語の訳語固定

- 狙う型: 訳語選択(タイトル"Phone-Answering"=保留1件、"the feature"の指示対象=EV-18)。ただし盲検NGに算入されたタイトル由来は0件で、**根拠はn不足**(分析3-1)。
- 変更箇所: 台帳(またはResearcher出力)に`en_term`(英訳固定語)を持たせ、翻訳promptへ「次の語はこの英訳を使う」を追加。台帳スキーマ変更を避ける軽量案は、台帳中の固有名詞・クォート語(例: human concierge)を抽出してpromptへ「そのまま保つ」と指示する(語彙ルールv2の例外C[固有名詞/引用された呼称]と同型、`ADVANCED_VOCAB_RULE_V2_BLOCK`)。
- 規模: M(軽量案はS〜M)。追加費用: 入力微増(未測定)。副作用: 台帳側の表記が不適切だとそのまま固定される。
- 検証方法: EV-18型/タイトルのfixtureでA案と同じオフライン再生成。

## G. 解析から導かれるその他の案

- G1. **JA側で集合名詞を台帳表記へ固定する(上流対策)**。「副社長」と書いたJA 9記事は"vice president"になり誤り0、「幹部」と書いた9記事のうち6記事が複数形(分析3-2)。JA writerのプロンプトに「役職・組織は台帳の表記を使い、「幹部」「関係者」「機関」等の数が不明な集合名詞に置き換えない」を追加する。規模S〜M(JA writerはProduction構成のため変更は承認必須)。追加費用: ¥0(プロンプト文言のみ。検証でJA writerを再生成する費用は未測定。参考として run_02 の ja_r2 call は入力8,734・出力1,145 tokens=換算 約¥0.23/call、キャッシュ分は未控除)。副作用: JAの文体が硬くなる、台帳の表記が長い場合に聴きにくくなる。EN段の数の誤りの8事象中、幹部5事象に効く(機関2・従業員1には別の語を台帳表記へ)。
- G2. **要約の再生成にMAJOR指摘(must-fix)を渡す**。現状は翻訳callにだけ渡り(`generate_family_x_faithful_translation(..., must_fix=...)`)、`generate_family_x_in_one_line`は`must_fix`を受け取らない(分析4-2)。要約MAJOR 14世代のうち再生成で回復6・STOP 8のため、仮説は「同じ誤りを再生成している」。変更は`generate_family_x_in_one_line`への引数追加とrunnerの呼び出し2か所(L391, L424)で規模S。追加費用: 再生成時のみ入力 +数百tokens(概算 ¥0.01以下/回)。副作用: ほぼ無し。ただし回復率改善は仮説であり、検証(STOP 8世代のJA R2・台帳を使った要約再生成、1件約¥0.1〜0.2の換算)が先。B2と併用が自然。
- G3. **観測の追加(translation起源MINORをtelemetryへ)**。現状、translation起源MINORは再生成にも修正にも回らず、`deviation_check.json`に残るのみ(分析4-2)。EV-25はこの経路で素通りした。起源・フラグ・箇所をrunごとに集計できる形(`writer_run_summary.json`等への追記)にすると、対策効果の測定が容易になる(¥0・規模S)。
- G4. **評価設計の注意**。盲検判定は判定者間の一致が27%と低く(分析§0の6)、上記の効果検証を「盲検LLM判定だけ」で行うと誤差が大きい。固定チェックリスト(分析の26事象の型・文)を使う機械的突合、判定者2名以上、重大候補のユーザー確認の併用が望ましい。

## 制約・未確認事項

- 費用は全て換算(トークン実測×確認済み単価)で、追加call/追加入力の実測ではない。台帳単体のトークン数、翻訳callへ台帳を加えた場合の実測は未実施。
- 各案の効果量は未検証。分析のn(26事象、重大2)が小さく、案ごとの削減見込み件数は出していない。
- A・B・D・Eは新しい構造・処理フローを含み得るため、必須のOpus独立レビュー(条件A。正本`docs/pm/PM_GOVERNANCE.md` 11-3節)の対象になり得る(判断はFable)。Production採用は`APPROVED_FOR_PRODUCTION`が必要で、人間ユーザーだけが承認できる。
- 既存のretry/fallback/Gate(JA再確認STOP、must-fix再生成1回、Checker cycle上限等)は、本書のいずれの案でも変更前提にしていない(D4とG2は挙動に影響するため、変更する場合は別途承認が必要)。
