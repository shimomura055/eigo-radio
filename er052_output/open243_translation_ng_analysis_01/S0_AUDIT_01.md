# S0_AUDIT_01: 再分類(STAGE1_RECLASSIFY)による除外の監査(OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_02)

作成日 2026-10-08。API支出 ¥0(既存artifactのみ読取。LLM呼び出しなし)。所見は事実のみ。採否・推奨はFableが判断する。
再現スクリプト(同ディレクトリ、読取のみ): `_s0_scan.py`(dump収集)→`_s0_extract.py`(除外候補抽出)→`_s0_events.py`(53事象との突合)→`_s0_summary14.py`(要約14世代)→`_s0_write_audit.py`(本ファイル生成)。判断を伴う分類は「判定: 手動」と根拠を付記。

## 0. 要旨(事実のみ)

1. 承認構成(STAGE1_RECLASSIFY=True・FLOOR_MODE=number_only)で動いた Checker 実行 133 件(重複除去後、全てスイッチdumpで確認)の初回 Stage 1 で、再分類の対象になった model 候補 1389 claim のうち **1011 claim(SUPPORTED 372 / NO_FACT_CLAIM 639)が `excluded=true`** で Stage 2 に渡らなかった。このうち Stage 1 が `changed_actor=true` を立てていたものは **38 claim**(SUPPORTED/actor_match=match 27)。
2. ANALYSIS_01 の翻訳段由来/増幅 26事象のうち、初回再分類で除外された Stage 1 候補と文一致したのは **5事象**(EV-25 重大, EV-06, EV-07, EV-10, EV-19)。「候補化なし 10/24」のうち **3事象**(EV-06, EV-07, EV-10)は「Stage 1 が候補にしたが再分類が除外」であり、残り7事象(EV-32/35/38/02/45/48/01)は Stage 1 の model 候補に当該文が出ていない。「ACCEPTABLE 残存 8」のうち再分類で初回除外された文は EV-19 の1事象。
3. M3(E0: changed_actor 付き候補を再分類除外から保護)で救済され得る事象の上限は **2事象(EV-25 重大1・EV-06 軽微1)**。保護対象を「unsupported_new_claim 以外のフラグ付き」へ広げた場合の上限は 5事象(上記5件すべてが該当)。いずれも「Stage 2 に渡る」ことの上限であり、Stage 2 が BLOCKING にするとは限らない(§2-5の注記)。
4. 要約 MAJOR 14世代の一次分類(判定: 手動、attempt1 の指摘基準): 明確な誤り 5 / 境界例 7 / 過剰判定の疑い 2。STOP した8世代の「最終 MAJOR」基準では 明確な誤り 1 / 境界例 4 / 過剰判定の疑い 3。
5. FLOOR_MODE: Trial A/B の Checker 実行 57 件(all6 38 + factlock/runs 19)の switch dump 全件が `FLOOR_MODE=number_only`・`STAGE1_RECLASSIFY=True`・`PRECHECK_MODE=number_only`、dump の sha256 が各 run の `provenance.switch_dump_sha256` と一致、`switches_equal_e2e02=True`。ANALYSIS_01 の「直接には確認していない(未確認)」は解消(§4)。
6. EV-28(callers): EN deviation check は当該要約を指摘せず(LEDGER_COMPLIANT)、Checker の Stage 1 が r3+r5 で候補化、Stage 2 一次 ACCEPTABLE → 第2意見 BLOCKING → 書換え(§5)。再分類は L1 を CANDIDATE のまま維持した。

## 1. (a) 再分類による除外の集計

### 1-1. 収集範囲と構成の判定根拠

- 収集: `er052_output/**/checker/**/*.json` と `er052_output/**/runs/*.json` のうち、トップレベルに `stage1_coverage` を持つ Checker 実行 dump = 254 ファイル。`checker/after_instances/*.json` は `checker/runs/*.json` と同内容の複製のため除き、run単位で重複除去して **133 実行**(`_s0_perdump.json`)。除外候補の件数は(run, 単位ID)で一意(`s0_excluded_candidates.jsonl` 1,011行=一意)。
- 構成の判定根拠: 各 dump に対し、同ディレクトリまたは最も近い親ディレクトリの `approved_switches_dump*.json` を探し、`switches.STAGE1_RECLASSIFY is True` かつ `switches.FLOOR_MODE == "number_only"` を確認。133/133 が該当(dump 無しの実行は0)。Trial A/B 57 実行は run 直下の `checker/approved_switches_dump_after_p01.json` と `provenance.switch_dump_sha256` の一致も確認(§4)。
- 注意: Checker dump 自身の `switches` キーには `STAGE1_RECLASSIFY`/`FLOOR_MODE` が出力されない(実行時dumpの対象外)。構成は別ファイルの switch dump で確認した。
- 133 実行の内訳(出典dir別): all6_writer_redesign_necessity_01/runs 38, factlock_writer_trial_01/sweep_01 29, factlock_writer_trial_01/runs 19, open233_control_checker_polysemy_trial_01/runs 18, open233_allfact_note_e2e_02/runs 10, open233_prod_e2e_02(個別file) 9, open233_polysemy_trial_04/runs 5, open233_meta_allfact_note_ent_01/runs 2, open238_precheck_fix_trial_01(個別file) 2, open233_ledger_clarity_p_trial_01(個別file) 1。
- 133 実行は同一記事の再実行・別Trialを含む(記事単位の重複除去はしていない)。Trial A/B(all6 + factlock/runs)57実行だけの集計を併記する。

### 1-2. 集計(初回 Stage 1 の `candidate_filter.verdicts`、出典 `stage1_coverage.candidate_filter`)

| 項目 | 全133実行 | Trial A/B 57実行 | その他76実行 |
|---|---|---|---|
| Checker実行数 | 133 | 57 | 76 |
| 再分類の対象 claim 数(model由来) | 1389 | 499 | 890 |
| 除外された claim 数(excluded=true) | 1011 | 379 | 632 |
|   うち SUPPORTED | 372 | 130 | 242 |
|   うち NO_FACT_CLAIM | 639 | 249 | 390 |
| changed_actor=true で除外 | 38 | 8 | 30 |
|   うち actor_match=match | 27 | 5 | 22 |
|   うち最終EN本文にその文が残存(判定: 文字列一致) | 19 | 2 | 17 |
| changed_actor を含む実行数 | 28 | 8 | 20 |
| フラグが全て false の除外 | 6 | 4 | 2 |
| unsupported_new_claim 以外のフラグ付きの除外 | 656 | 239 | 417 |

フラグ別件数(除外 claim あたり、複数フラグは重複計上):

| Stage 1 フラグ | 全133実行 | Trial A/B | その他 |
|---|---|---|---|
| changed_fact | 339 | 107 | 232 |
| changed_scope | 272 | 87 | 185 |
| changed_causality | 160 | 59 | 101 |
| changed_certainty | 105 | 34 | 71 |
| changed_number | 4 | 1 | 3 |
| changed_actor | 38 | 8 | 30 |
| changed_negation | 28 | 8 | 20 |
| changed_comparison | 76 | 29 | 47 |
| changed_time | 30 | 2 | 28 |
| unsupported_new_claim | 886 | 335 | 551 |

注: `unsupported_new_claim` を含む除外が大半(886/1,011)。`changed_number=true` で除外された claim は全体4件(dump単位の `n_excluded_with_changed_number` は entry 数で数えるため合計が異なる)。

### 1-3. 再検査(recheck)・出口(exit)の再分類(件数のみ。claim単位の verdict は dump に保存されていない)

- 初回(上表): 全体 1011 claim。再検査・出口の再分類 `n_excluded_claims` の合計: 全体 出口 263 / 再検査 36、Trial A/B 出口 75 / 再検査 7(出典: `recheck_exit_check.log[].reclassify`、`cycles[].recheck_coverage`)。`candidate_filter.verdicts`(claim単位)は初回のみ。再検査・出口の changed_actor 内訳は取得不能(未確認)。

### 1-4. changed_actor=true で除外された 38 claim(全件、`s0_excluded_candidates.jsonl` と同一)

| # | run | 単位 | 文(claim, 先頭120字) | verdict | actor_match | related_fact | Stage 1 の issue(先頭110字) | 最終EN本文 | 構成 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | all6_writer_redesign_necessity_01/hormuz/b2__all6__r1 | S6.2 | At the time, attacks by the United States and Iran and a sea blockade continued, and concerns about tanker safety remain | SUPPORTED | match | HF-009 | Ledgerは「米・イラン間の攻撃」としているが、記事は攻撃を米国とイランがそれぞれ行ったと読める形にしており、主体を特定・変更している。 | 文字列不一致 | A/B |
| 2 | all6_writer_redesign_necessity_01/hormuz/b3__all6__r1 | S5.1 | During that time, concerns about attacks by the United States and Iran, a blockade at sea, and tanker safety continued. | SUPPORTED | match | HF-009 | Ledgerは米国とイランの間の攻撃などへの懸念が続いたとしているが、記事は攻撃の主体を「米国とイラン」としており、双方が攻撃を行ったという意味に読める。 | 文字列不一致 | A/B |
| 3 | all6_writer_redesign_necessity_01/meta/b1__baseline__r1 | S8.3 | What AI calls truly need is not only human-like responses, but also a clear notice that humans are there when they are. | NO_FACT_CLAIM | n_a | MUSE-HC-014,MUSE-HC-012 | AI電話に必要なものについての規範的提言であり、人間のような応答との比較も含め、Ledgerに裏付けがありません。 | 文字列不一致 | A/B |
| 4 | all6_writer_redesign_necessity_01/meta/b2__baseline__r1 | S5.5 | Even so, if humans are involved in a service that uses AI, users need to be clearly told who is speaking and what inform | NO_FACT_CLAIM | n_a | MUSE-HC-010,MUSE-HC-014 | 人間が関与するAIサービスでユーザーに何を伝えるべきかという規範的な主張は、Ledgerにありません。 | 文字列不一致 | A/B |
| 5 | all6_writer_redesign_necessity_01/meta/b3__baseline__r1 | S9.1 | In addition, in one case in which Meta was asked to negotiate internet and cable bills, employees reported that a human  | SUPPORTED | match | MUSE-HC-011 | Ledgerでは従業員がMuseに料金交渉を依頼した事例だが、記事は「Meta was asked」とし、依頼を受けた主体をMetaに変えている。 | 残存 | A/B |
| 6 | all6_writer_redesign_necessity_01/space_weapons/b2__baseline__r2 | S2.2 | An official article from a U.S. government agency records this as the first time the United States acknowledged deployin | SUPPORTED | match | F-001 | Ledgerが初回の認定主体としているSpace Forceを、記事はUnited States全体に広げている。 | 残存 | A/B |
| 7 | factlock_writer_trial_01/hormuz/b4__factlock__r1 | S1.1 | In this news story, the lead role on the policy stage changed hands the next day. | SUPPORTED | n_a | HF-007 | 翌日に変わったのは償還料案の扱いであり、政策上の主導権や役割が別の主体に移ったとはLedgerに記載されていません。 | 文字列不一致 | A/B |
| 8 | factlock_writer_trial_01/space_weapons/b2__factlock__r1 | S2.4 | We know the culprit’s name, but we still cannot see the key details of their profile. | SUPPORTED | match | F-001 | 「culprit（犯人）」と呼ぶことで、配備を認めた主体を不正行為の犯人として位置づけていますが、その評価はLedgerにありません。 | 文字列不一致 | A/B |
| 9 | factlock_writer_trial_01/sweep_01/meta/b2__S4__r1 | S4.1 | A Meta vice president responsible for the service admitted that starting a test in which contractors made calls without  | SUPPORTED | match | MUSE-HC-012 | ロールバックと「ミス」の認定は支えられていますが、Ledgerの主体はMetaのSuperintelligence Labs部門の副社長です。「サービスを担当する副社長」とする肩書き、およびユーザーに適切に知らせなかった | 文字列不一致 | 他 |
| 10 | open233_allfact_note_e2e_02/ai_control/nb/p2/rep1 | S1.2 | An AI that was supposed to be isolated got out into the outside world and entered real systems. | SUPPORTED | match | EVID-008,EVID-009,EVID-011 | 隔離環境からAIが自力で「外へ出た」という言い方は、環境の設定ミスによるインターネット接続・アクセスを、AI自身の脱出行為のように表現している。 | 残存 | 他 |
| 11 | open233_allfact_note_e2e_02/ai_control/nb/p2/rep1 | S1.3 | Just hearing this makes it feel as if the AI made a plan, broke out of prison, and escaped on its own. | NO_FACT_CLAIM | n_a | EVID-008 | AIが計画し、脱獄し、自力で逃げたかのような印象を示す。Ledgerは実環境での脱出計画やそのような意図を裏付けていない。 | 残存 | 他 |
| 12 | open233_allfact_note_e2e_02/ai_control/nb/p2/rep2 | S2.1 | Anthropic had AI agents solve a fictional game of capture the flag. | SUPPORTED | match | EVID-008 | The Ledger says Claude models were operating on capture-the-flag tasks in third-party environments, but does n | 残存 | 他 |
| 13 | open233_allfact_note_e2e_02/meta/nb/p2/rep1 | L1 | Meta’s AI calling test sometimes relied on undisclosed human contractors, raising privacy concerns for users. | SUPPORTED | match | MUSE-HC-010,MUSE-HC-012 | 「undisclosed human contractors」は一部テストの内容と関連するが、「raising privacy concerns for users」は懸念を示した主体をユーザーに置き換え、テストがユーザ | 残存 | 他 |
| 14 | open233_allfact_note_e2e_02/meta/nb/p2/rep2 | S1.1 | Was the person on the other end of the call an AI or a human? | NO_FACT_CLAIM | n_a | MUSE-HC-006 | 質問は電話の相手側がAIか人間かという点を示唆しますが、Ledgerが示しているのは電話をかけた側が人間の契約スタッフだった一部事例です。 | 残存 | 他 |
| 15 | open233_allfact_note_e2e_02/meta/nb/p2/rep2 | S1.2 | This time, at least in some cases, it was a human. | SUPPORTED | match | MUSE-HC-006 | 「it」は直前の「電話の相手側の人」を指す読み方があり、Ledgerが述べる人間は電話をかけた側です。行為者・対象が曖昧または異なります。 | 残存 | 他 |
| 16 | open233_allfact_note_e2e_02/meta/nb/p2/rep2 | S9.4 | That was the problem. | NO_FACT_CLAIM | n_a | MUSE-HC-012 | 「それ」が人間の担当者に知らされていなかったことを指すなら、その問題設定はLedgerに支えられていません。 | 残存 | 他 |
| 17 | open233_allfact_note_e2e_02/sewer/nb/p2/rep1 | S7.4 | Even so, falling revenue caused by population decline and rising costs to renew old facilities make sewerage services mo | SUPPORTED | match | F-002,F-003 | 維持管理・更新費の将来推計を、時期や推計としての限定なしに上昇中の事実として述べ、さらにサービス運営を難しくする因果関係を加えています。 | 文字列不一致 | 他 |
| 18 | open233_allfact_note_e2e_02/sewer/nb/p2/rep2 | S4.1 | So Matsuyama City decided not to use the same method across the whole city, but to change its approach to fit how homes  | SUPPORTED | match | F-010,F-003,F-007 | 文頭の“So”により、直前の国土交通省による一般的説明が松山市の方針変更の直接の理由であると結び付けているが、その関係はLedgerに明記されていない。 | 文字列不一致 | 他 |
| 19 | open233_control_checker_polysemy_trial_01/ai_control/rep1 | S5.1 | What is more, the standard protections used when accessing a public site were not in place. | SUPPORTED | match | EVID-008,EVID-009 | Ledgerが述べるのは評価環境に標準的なサイバーセーフガードがなかったことです。公開サイトへアクセスする際の標準保護がなかった、と対象を限定した説明までは確認できません。 | 残存 | 他 |
| 20 | open233_control_checker_polysemy_trial_01/meta/nb/rep10 | S6.1 | This is easy for those of us who are used to automated voices and chat to understand. | NO_FACT_CLAIM | n_a |  | 「自動音声やチャットに慣れている」という読者についての主張はLedgerにありません。 | 文字列不一致 | 他 |
| 21 | open233_control_checker_polysemy_trial_01/meta/nb/rep2 | S3.3 | The system lets AI handle troublesome calls for the user. | SUPPORTED | match | MUSE-HC-004,MUSE-HC-006 | システムが「厄介な」電話をAIに処理させるという性質・対象範囲はLedgerにありません。人間が担当した電話が一部あった事実とも区別されていません。 | 残存 | 他 |
| 22 | open233_control_checker_polysemy_trial_01/meta/nb/rep2 | S8.1 | A Meta executive in charge admitted that this was a “mistake.” | SUPPORTED | match | MUSE-HC-012 | LedgerではMetaのSuperintelligence Labs部門の副社長が説明したとされています。「executive in charge」はその人物をテスト全体の責任者とする含みがあり、主体・役割が一致すると | 残存 | 他 |
| 23 | open233_control_checker_polysemy_trial_01/meta/nb/rep2 | L1 | During testing, Meta’s AI phone agent sometimes had human contractors make calls without properly telling users. | SUPPORTED | match | MUSE-HC-012 | 人間の契約スタッフが一部の電話を担当し、適切な開示がなかったことは支えられますが、誰に説明しなかったのかを「users」と特定する根拠はLedgerにありません。 | 残存 | 他 |
| 24 | open233_control_checker_polysemy_trial_01/meta/nb/rep3 | S1.3 | AI even handles the phone call itself. | SUPPORTED | match | MUSE-HC-006,MUSE-HC-004 | Ledgerは電話機能の依頼内容と一部の電話を人間が担当したことを述べるが、AIが電話そのものを処理するという一般的な断定は支えていない。 | 残存 | 他 |
| 25 | open233_control_checker_polysemy_trial_01/meta/nb/rep3 | S3.3 | The test had begun without people being properly told about it. | SUPPORTED | match | MUSE-HC-012 | Ledgerは適切な開示なしにテストが始まったとするが、「人々に適切に伝えられていなかった」と開示の相手を広く特定することまでは明示していない。 | 残存 | 他 |
| 26 | open233_control_checker_polysemy_trial_01/meta/nb/rep3 | S5.3 | This is one individual report, but it means there were cases where a conversation ended the moment people learned it was | SUPPORTED | match | MUSE-HC-009 | 個別報告である点は保たれているが、「人々がAIだと知った瞬間に会話が終わった」と時間的・因果的に一般化しており、Ledgerが述べる個別の従業員報告より強い。 | 残存 | 他 |
| 27 | open233_control_checker_polysemy_trial_01/meta/nb/rep4 | S7.1 | Later, the vice president of Meta's artificial intelligence division admitted that starting this test without a proper e | SUPPORTED | match | MUSE-HC-012 | Ledger上の役職はMetaのSuperintelligence Labs部門の副社長です。「Meta's artificial intelligence division」とする組織の特定が異なります。 | 文字列不一致 | 他 |
| 28 | open233_control_checker_polysemy_trial_01/meta/nb/rep6 | S4.3 | It was almost as if the AI was looking for a human to stand in for it. | NO_FACT_CLAIM | n_a | MUSE-HC-006,MUSE-HC-008,MUSE-HC-009 | AIが人間を代役として探していたかのような目的・意図はLedgerで確認されていません。 | 残存 | 他 |
| 29 | open233_control_checker_polysemy_trial_01/meta/nb/rep7 | S6.2 | When contract workers handled the calls, users' sensitive information could unintentionally be shared with contract work | SUPPORTED | match | MUSE-HC-010 | 従業員が示した懸念としての報告ではなく、情報共有の可能性を記事の直接的な記述として提示している。 | 文字列不一致 | 他 |
| 30 | open233_meta_allfact_note_ent_01/meta/nb/p2/rep1 | T | # I Asked AI to Make a Call, but Humans Were Making Some of the Calls | SUPPORTED | match | MUSE-HC-006,MUSE-HC-004 | 「I Asked」は話者本人がAIに電話を依頼したという個人的な出来事を加えているが、Ledgerにその事実はない。 | 文字列不一致 | 他 |
| 31 | open233_prod_e2e_02|meta_run03_advanced.json | S7.1 | News reports also cited an employee’s report that human staff made inappropriate comments about race during calls to neg | SUPPORTED | match | MUSE-HC-011 | Ledgerが記録するのはインターネット・ケーブル料金交渉の1件についての従業員報告です。記事は複数の電話でスタッフが不適切発言をしたかのように範囲を広げています。 | 文字列不一致 | 他 |
| 32 | open233_prod_e2e_02|neg3_hormuz_prodrunner_b1b.json | S2.1 | On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement. | SUPPORTED | match | HF-002 | Ledgerは米国が償還を求めると投稿したことを確認していますが、誰が支払義務を負うかなどの制度設計は示されていません。「貨物が償還を提供すべき」とすると支払義務者を特定した表現になります。 | 文字列不一致 | 他 |
| 33 | open233_prod_e2e_02|neg7_meta_prodrunner_b1b.json | S2.2 | So it sounds like a simple story: you make a request, and AI takes care of the call. | NO_FACT_CLAIM | n_a | MUSE-HC-006 | 「So」で前文から結び付け、AIが依頼された電話を引き受けるという単純化した説明を導いているが、Ledgerは電話の一部を人間の契約スタッフが担当したとする。 | 文字列不一致 | 他 |
| 34 | open233_prod_e2e_02|neg7_meta_prodrunner_b1b.json | S3.5 | It was like an AI-led play with a hidden supporting actor. | NO_FACT_CLAIM | n_a | MUSE-HC-006 | 「AI-led play」と「hidden supporting actor」は比喩だが、AIが電話を主導し人間が隠れた補助役だったという関係はLedgerに明記されていない。 | 文字列不一致 | 他 |
| 35 | open233_prod_e2e_02|neg7_meta_prodrunner_b1b.json | S5.3 | It was that testing began without clearly telling users about it. | SUPPORTED | match | MUSE-HC-012 | Ledgerは適切な開示なしでテストを開始したとするが、「users」に事前に明確に伝えなかったという対象・具体的状況までは特定していない。 | 文字列不一致 | 他 |
| 36 | open233_prod_e2e_02|neg7_meta_prodrunner_b1b.json | R:S2.1+S2.2 | So it sounds like a simple story: you make a request, and AI takes care of the call. | NO_FACT_CLAIM | n_a | MUSE-HC-006 | 「So」が、Museに電話機能があることから「依頼すればAIが電話を処理する」という単純な筋書きを導いている。しかし、Ledgerは電話の一部を人間の契約スタッフが担当したとするため、この結び付けと一般化は支えられない。 | 文字列不一致 | 他 |
| 37 | open238_precheck_fix_trial_01/replay/fixed|meta_run03_advanced.json | S2.1 | Anthropic had AI agents solve a fictional game of capture the flag. | SUPPORTED | match | EVID-008,EVID-009 | Ledgerは第三者の評価環境でClaudeモデルがCTFタスクを実行していたとするが、Anthropic自身がエージェントに課題を解かせたように主体を変えている。 | 残存 | 他 |
| 38 | open238_precheck_fix_trial_01/runtime_evidence/run|meta_run03_advanced.json | S2.1 | Anthropic had AI agents solve a fictional game of capture the flag. | SUPPORTED | match | EVID-008,EVID-009 | Anthropic is presented as arranging the task, whereas the ledger describes third-party evaluation environments | 残存 | 他 |

(最終EN本文=Checker最終cycleのEN本文に文が正規化一致で含まれるか。判定: 機械的な文字列一致であり、書換えによる不一致と抽出失敗は区別していない。)

全1,011件は `s0_excluded_candidates.jsonl`(フィールド: run_key, key, claim, verdict, actor_match/counterpart_match/scope_match/qualifier_match, reclass_reason, fact_tags, stage1_flags, stage1_issues, related_fact_ids, routes, run_final_state, in_input_text, in_final_text)。

## 2. (b) 盲検NGとの突合

方法: `items.jsonl`(74行=判定。`event_id` で束ねた53事象+event_id無しの保留8判定)の各事象のEN文(`en_sentence_matched` または `ng_text`)を、同一 run の Checker dump の `candidate_filter.verdicts`・`union_candidates`・`stage2_results` と照合(語集合Jaccard≥0.5、または正規化文字列の包含。ANALYSIS_01の `_build.py` と同系統の基準)。出典: `_s0_events.json`。

### 2-1. 翻訳段由来/増幅 26事象(うち Checker あり 24)のうち、初回再分類で除外された文と一致した5事象

| 事象 | 盲検 | 型/箇所 | Stage 1 フラグ(再分類前、文一致候補の和集合) | 再分類 verdict | Stage 2 での扱い(出典 stage2_results) | ANALYSIS_01 での位置づけ | changed_actor |
|---|---|---|---|---|---|---|---|
| EV-25 | 重大 | subject/body | changed_actor | SUPPORTED(actor_match=match) | cycle1:QUALITY(basis=ledger_claim) | 候補化(QUALITY)残存 ※重大 | あり |
| EV-06 | 軽微 | subject/body | changed_actor,changed_fact | SUPPORTED(actor_match=match) | Stage 2 に当該文なし | 候補化なし | あり |
| EV-07 | 軽微 | causal/summary | changed_causality,changed_fact,unsupported_new_claim | SUPPORTED(actor_match=match) | Stage 2 に当該文なし | 候補化なし | なし |
| EV-10 | 軽微 | scope/body | changed_certainty,changed_fact | SUPPORTED(actor_match=match) | Stage 2 に当該文なし | 候補化なし | なし |
| EV-19 | 軽微 | addition/summary | changed_certainty,changed_scope,unsupported_new_claim | SUPPORTED(actor_match=match) | cycle1:ACCEPTABLE(basis=none) | ACCEPTABLE残存 | なし |

### 2-2. 「候補化なし 10/24」の内訳(判定: 機械+一部手動)

ANALYSIS_01 §3-4 の「候補化なし」は union_candidates(再分類後)と stage2_results のどちらにも文が無い事象。10事象の内訳:

| 区分 | 件数 | 事象 |
|---|---|---|
| Stage 1 の model 候補になったが再分類が除外(SUPPORTED) | 3 | EV-06(changed_actor+changed_fact), EV-07(causality+fact+unsupported), EV-10(certainty+fact) |
| Stage 1 の model 候補に当該文が出ていない(verdicts・candidates に文一致なし) | 7 | EV-32, EV-35, EV-38, EV-02, EV-45, EV-48, EV-01 |

### 2-3. 「ACCEPTABLE 残存 8」のうち再分類で落ちた事象

ACCEPTABLE のみで最終本文に残った8事象(EV-19, 30, 23, 50, 51, 08, 52, 04)のうち、初回再分類で除外された文と一致したのは **EV-19 のみ**(フラグ changed_certainty/changed_scope/unsupported_new_claim。changed_actor なし)。EV-19 は stage2_results に `detected_by=stage1_llm`・cycle1 ACCEPTABLE として別経路で存在(経路はコード未確認。同一fact_idの兄弟location展開の可能性があるが未確認)。他7事象(EV-30/23/50/52 は changed_actor 付き)は再分類で CANDIDATE 維持されて Stage 2 に渡り、Stage 2 が ACCEPTABLE と判定した。

### 2-4. 重大 EV-25 の経路補正(ANALYSIS_01 §3-4 への事実追記)

ANALYSIS_01 は EV-25 を「候補化 Stage2=QUALITY → 最終文残存(Stage 1 は別事実 HC-010 を理由に候補化)」としていた。dump 照合の結果:

- 当該文(単位 S9.1)は Stage 1(r3)の model 候補で `changed_actor=true`、issue 文は「Ledgerでは従業員がMuseに料金交渉を依頼した事例だが、記事は「Meta was asked」とし、依頼を受けた主体をMetaに変えている」、related_fact_id=MUSE-HC-011(出典: `b3__baseline__r1/checker/runs/meta_run03_advanced.json` の `stage1_coverage.per_route.r3.candidates`)。
- 再分類 verdict は `SUPPORTED`、actor_match/counterpart_match/scope_match/qualifier_match=`match`、`excluded=true`、reason=「インターネット・ケーブル料金交渉の1件で、従業員が契約スタッフの人種に関する不適切発言を報告したというLedgerと一致する」(出典: `stage1_coverage.candidate_filter.verdicts`)。
- union_candidates(10件)に S9.1 は無い。一方 cycle1 の stage2_results(15件)には同文が `detected_by=stage1_llm`・`related_fact_id=MUSE-HC-010`・materiality=QUALITY で存在する。つまり Stage 2 の評価は **HC-010 に対するもの**で、HC-011・changed_actor の観点は評価されていない(経路は同一fact_idの兄弟location展開と推定、コード未確認)。

### 2-5. M3(E0)で救済され得る事象数(上限)

| 保護条件 | 上限事象数(翻訳段由来/増幅 26事象中) | 事象 |
|---|---|---|
| changed_actor=true の候補を除外から保護(M3の定義) | **2** | EV-25(重大), EV-06(軽微) |
| unsupported_new_claim 以外のいずれかのフラグ付きを保護 | 5 | EV-25, EV-06, EV-07, EV-10, EV-19 |

- 上限の意味: 「Stage 2 に候補として渡る事象数」の上限。Stage 2 の判定(BLOCKING/QUALITY/ACCEPTABLE)は未検証。EV-25 は既に別観点(HC-010)で Stage 2 に渡って QUALITY → 第2意見 ACCEPTABLE となっており、changed_actor 観点で Stage 2 に渡った場合の結果は dump からは分からない。
- 26事象に含まれないJA由来・保留の除外一致: EV-33, EV-46, EV-21, EV-20(JA由来、軽微)と保留 TB-060(NO_FACT_CLAIM)。
- 逆方向のコスト(保護した場合に Stage 2 へ追加で渡る claim 数の上限): 除外1,011 claim のうち changed_actor=true は38(全体の3.8%)、Trial A/B 57実行では 379中8。unsupported_new_claim 以外のフラグ付きを保護する場合は 656(全体)/239(A/B)。

## 3. (c) 要約 MAJOR 14世代の精査(判定: 手動)

対象: ANALYSIS_01 §2-4/§3-4 の「attempt1 で translation 起源 MAJOR が要約に出た 14世代」(出典: 各 run の `b1b/audit/deviation_checks/*attempt*.json`、`a2/` は standard、`deviation_check.json`=最終)。STOP=最終検査でも MAJOR が残った8世代(G02, G03, G06, G07, G08, G09, G12, G14)、解消=6世代(G01, G04, G05, G10, G11, G13)。台帳は各 run の `research_ledger/verified_fact_ledger.txt` の該当 fact。分類基準: 明確な誤り=台帳の本文/notes_for_writer/scope/conditions に明示的に反する、または台帳に無い事実・語を足している / 境界例=台帳に直接の禁止はないが、台帳の確認範囲より具体的・広い表現で解釈が割れる / 過剰判定の疑い=記述が台帳と矛盾せず、指摘が台帳に明記のない細部(例: 開示の相手が「users」)を理由にしている。

### 3-1. 14世代の一覧

| 世代 | run | 結果 | attempt1 の要約文(MAJOR) | 台帳の該当行 | 指摘(attempt1、JA先頭150字) / フラグ | 一次分類(attempt1基準) | 根拠(判定: 手動) |
|---|---|---|---|---|---|---|---|
| G01 | all6_writer_redesign_necessity_01/meta/b1__all6__r2 | 解消(attempt2でCOMPLIANT) | Meta paused Muse’s calling feature after contract workers made calls without users being told humans were involved. | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | ロールバックの対象を人間コンシェルジュ機能からMuseの電話機能全体へ広げています。 [changed_scope] | 明確な誤り | notes_for_writer「「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う」に対し、要約が「Muse’s calling feature」を paused としている |
| G02 | all6_writer_redesign_necessity_01/meta/b2__all6__r2 | STOP | Meta’s AI call tests used human contractors without properly informing users // Meta’s AI call tests used human contractors without properly informing users, prompting the company to pause the feature. | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | Ledgerは適切な開示がなかったとするが、誰に開示されなかったかまでは特定していない。記事は対象をユーザーに限定している。 [changed_scope] // 「prompting」は、開示不足が機能の一時停止を引き起こしたという因果関係を加えている。Ledgerはミスの認定とロールバックを記録しているが、その因果関係までは明示していない。 [changed_causality] | 境界例 | 台帳に開示相手の記載がなく "users" 限定を指摘(軽め)、"prompting" は因果を断定(台帳は「ミスと認め、ロールバック」を並記するだけ) |
| G03 | all6_writer_redesign_necessity_01/meta/b3__all6__r1 | STOP | “Meta’s AI phone feature unexpectedly used human contractors, prompting privacy concerns and a rollback of the feature.” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | 人間の契約スタッフを使ったこと自体がロールバックを引き起こしたように読める。Ledgerが示すのは、適切な開示なしに契約スタッフが電話をするテストを始めたことを「ミス」と認め、人間コンシェルジュ機能をロールバックしたという内容。 [changed_causality] | 境界例 | "unexpectedly" "prompting privacy concerns and a rollback" は因果と感情の断定で台帳に無い。ただし事実の取り違えではなく表現の強さ |
| G04 | all6_writer_redesign_necessity_01/meta/b3__all6__r2 | 解消(attempt2でCOMPLIANT) | In one line: “Meta paused its phone AI feature after contract workers sometimes made calls without proper disclosure.” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | 「人間コンシェルジュ機能」のロールバックを、電話AI機能全体の停止と読める形に広げています。Ledgerが確認しているのは人間コンシェルジュ機能のロールバックであり、電話機能全体の停止ではありません。 [changed_fact,changed_scope] | 明確な誤り | "paused its phone AI feature" は notes_for_writer「「サービス全体を停止した」とは書かない」に反する |
| G05 | all6_writer_redesign_necessity_01/space_weapons/b3__baseline__r1 | 解消(attempt2でCOMPLIANT) | The United States confirmed its first orbital weapons deployment, but the specific system remains unknown. | F-001: [VERIFIED] F-001: 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mi / scope: 米空軍・米宇宙軍 / conditions: 敵対的な相手の行動から統合軍を防護する用途と説明 / notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。 | F-001は、米国が軌道上兵器の配備を初めて公式に認めたことを保証するが、その配備自体が米国にとって史上初だったとは保証していない。『its first orbital weapons deployment』は、初めての公式確認を初めての配備へと変更している。 [changed_fact,unsupported_new_claim] | 明確な誤り | 台帳は「Space Forceが宇宙に兵器を配備したことを初めて認めた発言」(初の公式確認)。要約 "confirmed its first orbital weapons deployment" は初の配備と読め、notes_for_writerの範囲を超える |
| G06 | factlock_writer_trial_01/hormuz/b1__factlock__r2 | STOP | In one line: “oil prices stayed high amid safety fears.” | HF-009: [VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。 / scope: 国際指標Brent原油先物の短時間の値動き / conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。 / notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。 | Brent先物について確認された値動きを、原油価格全般の動きとして表現しています。 [changed_scope] | 境界例 | 台帳 scope は「国際指標Brent原油先物」。要約は "oil prices" と一般化。要約としては自然だが台帳 scope より広い |
| G07 | factlock_writer_trial_01/meta/b1__factlock__r1 | STOP | “without users being properly informed” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | Ledgerは適切な開示がなかったことを確認していますが、開示を受ける主体がユーザーだったとは明記していません。この表現は開示対象を特定する新たな事実を加えています。 [changed_fact,unsupported_new_claim] | 過剰判定の疑い | 断片 "without users being properly informed" のみを指摘。台帳は「適切な開示なし」(相手の記載なし)。"users" は台帳 MUSE-HC-010 の "user information" と整合し、矛盾はしない |
| G08 | factlock_writer_trial_01/meta/b1__factlock__r2 | STOP | “Meta paused its human-run AI calls after realizing users weren’t told they were speaking to contractors.” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | 「適切な開示なしにテストを開始した」というLedgerの記述を、利用者には契約スタッフと話していることが伝えられていなかった、とより断定的に具体化している。適切な開示がなかったことだけでは、契約スタッフであることが一切伝えられていなかったとは確定できない。 [changed_certainty,unsupported_new_claim] | 境界例 | "realizing"(内心の断定)と "weren’t told they were speaking to contractors" は台帳の「適切な開示なし」より具体的 |
| G09 | factlock_writer_trial_01/meta/b4__factlock__r1 | STOP | “In Meta’s Muse test, human contractors made some calls instead of AI, and users weren’t properly told.” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | Ledgerは契約スタッフが電話を担当するテストに適切な開示がなかったとするものの、誰に開示されていなかったかは特定していません。記事はその対象を「users」と特定しています。 [changed_scope,unsupported_new_claim] | 過剰判定の疑い | "users weren’t properly told" の "users" 特定のみが指摘理由(G07と同型) |
| G10 | factlock_writer_trial_01/sweep_01/hormuz/b4__S2__r1 | 解消(attempt2でCOMPLIANT) | “Trump dropped his proposed fee for ships crossing Hormuz” | HF-002: [VERIFIED] HF-002: ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。 / scope: ホルムズ海峡を通じて輸送される「すべての貨物」 / conditions: 米国が海峡の安全と警備を提供するための費用の償還として提示。投稿は手続きと体制づくりを直ちに開始するとした。 / notes_for_writer: 7月13日の提案が先で、7月14日の撤回・置換が後。7月14日の出来事を7月13日の価格上昇の原因として扱わない。 | The summary describes the proposal as a fee for ships, while the Ledger specifies a proposed 20% reimbursement on all cargo passing through the strait [changed_scope] | 境界例 | 台帳 HF-002 は「すべての貨物に20%の償還」。要約 "fee for ships crossing Hormuz" は対象が貨物→船と読める。ただし「費用の徴収案」という大意は一致 |
| G11 | factlock_writer_trial_01/sweep_01/meta/b2__S11__r1 | 解消(attempt2でCOMPLIANT) | Meta paused its AI phone feature after contract workers handled calls without users being told. | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | この要約は、ロールバックされた対象を人間コンシェルジュ機能に限定せず、MuseのAI電話機能全体が一時停止されたとも読めます。Ledgerが確認しているのは人間が電話を代行する機能のロールバックです。 [changed_scope] | 明確な誤り | "paused its AI phone feature" は G04 と同型で、notes_for_writer「「サービス全体を停止した」とは書かない」に反する |
| G12 | factlock_writer_trial_01/sweep_01/meta/b2__S3__r1 | STOP | “Meta paused Muse’s human concierge feature after failing to tell users that human contractors might handle their calls.” | MUSE-HC-012: [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 / scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6 | Ledgerはテスト開始時に適切な開示がなかったとするものの、誰への開示が欠けていたかは特定していません。記事の要約は「利用者に伝えていなかった」と対象を特定し、原文の問いかけを確定した事実として述べています。 [changed_fact,changed_scope,changed_certainty,unsupported_new_claim] | 境界例 | "failing to tell users that human contractors might handle their calls" は開示の内容を具体化(台帳は「適切な開示なし」)。台帳に無い断定を含む |
| G13 | factlock_writer_trial_01/sweep_01/space_weapons/b3__S10__r1 | 解消(attempt2でCOMPLIANT) | For the first time, the U.S. acknowledged deploying weapons in orbit, but their capabilities and targets remain unknown. | F-001: [VERIFIED] F-001: 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mi / scope: 米空軍・米宇宙軍 / conditions: 敵対的な相手の行動から統合軍を防護する用途と説明 / notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。 | 「能力が不明」とする範囲が広すぎます。Ledgerでは、具体的なシステムや攻撃能力は不明とされる一方、統合軍を敵対的な相手の行動から防護できる兵器として説明されています。 [changed_fact,changed_scope] | 境界例 | "capabilities and targets remain unknown": 台帳 notes は「具体的なシステム名・攻撃能力・標的は推測で補わない」で、"capabilities" 一般を unknown とするのは範囲が広い解釈 |
| G14 | gpt6_wiring_e2e_01/run_01 | STOP | “Meta paused its AI phone assistant test” | MUSE-HC-07: [VERIFIED] MUSE-HC-07: MetaのSuperintelligence Labs担当副社長は、適切な説明をしないまま契約業者が電話をかけるテストを始めたのは問題だったと認め、機能を当面ロールバックしたと社内投稿で述べたとReutersが報じた。 / scope: human concierge／human agent callsの社内テスト / conditions: ロールバックは「当面」と報じられた。恒久的な中止や将来の再開の有無を示すものではない / notes_for_writer: 「永久に中止」とはしない。記事時点の「当面ロールバック」と、Meta広報担当者の「適切な説明を用意できるまでは公開展開しない」という発言を区別する。 / scope: 人間が電話を処理した一部の社内テスト / conditions: 副社長の社内投稿による説明。AI単独の場合は「より低い割合」とされるが、比較対象の具体的な数値・試験条件は報道に記載なし / notes_for_writer: 「人間の介入で成功率が95～98%に上がった」と一般化しない。記事が伝えるのは、社内投稿で人間担当時にその範囲の成功率が示されたという報告。 | 全体のAI電話アシスタントのテストを中断したように読めますが、Ledgerで確認されているのは人間担当者が関与する電話機能の当面のロールバックです。 [changed_scope] | 明確な誤り | "paused its AI phone assistant test" は台帳 scope「human concierge／human agent callsの社内テスト」の機能ロールバックを、AI電話アシスタント全体のテスト中断と読める形にしている |

### 3-2. STOP した8世代の「最終 MAJOR」の再分類(判定: 手動)

| 世代 | 最終の要約文(MAJOR、`deviation_check.json`) | 指摘(JA先頭150字) / フラグ | 最終基準の分類 |
|---|---|---|---|
| G02 | Meta paused its human-concierge feature after contract workers made calls without properly informing users. | Ledgerは適切な開示がなかったことを記録していますが、誰に開示されなかったかは特定していません。記事は、ユーザーへの説明がなかったと対象を限定しています。 [changed_scope] | 過剰判定の疑い(最終: "paused its human-concierge feature" と対象は台帳通りで、指摘は "users" の特定のみ) |
| G03 | Meta rolled back Muse’s calling feature after some calls were secretly handled by contract workers, not AI. | この一文は、ロールバック対象を人間コンシェルジュ機能より広いMuseの電話機能全体として述べ、契約スタッフが電話を担当したことがロールバックにつながったかのようにまとめています。また、「secretly」はLedgerにない含意です。 [changed_fact,changed_scope,changed_causality,unsupported_new_claim] | 明確な誤り(最終: "secretly" は台帳に無い語、"Muse’s calling feature" はnotes_for_writerに反する) |
| G06 | In one line: “Oil prices stayed high despite the shift from a proposed Hormuz fee to investment deals, as shipping-safety fears persisted.” | Brent先物の値動きを、原油価格全般の動きとして表現しています。 [changed_scope] | 境界例(最終も同じ指摘) |
| G07 | “Meta paused a calling feature after human contractors made calls without properly informing users.” | 適切な開示がなかった相手を「users」と特定していますが、Ledgerは開示対象を明記していません。 [changed_fact,changed_scope,unsupported_new_claim] | 過剰判定の疑い(最終も "users" 指摘) |
| G08 | “Meta paused a phone-call feature after human contractors called people without clearly disclosing they were human.” | Ledgerが確認しているのは、適切な開示なしに契約スタッフが電話を担当するテストを開始したことと、人間コンシェルジュ機能をロールバックしたことです。利用者に契約スタッフが人間だと明確に伝えられていなかった、とまでは確認されていません。 [changed_fact,changed_certainty,unsupported_new_claim] | 境界例(最終: "without clearly disclosing they were human" は「適切な開示なし」の言い換えとも「人間と明示していない」への具体化とも読める) |
| G09 | Meta’s AI calling test used human contractors without proper disclosure, so the company rolled back that feature. | The word “so” presents the lack of disclosure as the cause of the rollback, while the Ledger reports the admission and rollback without explicitly est [changed_causality] | 境界例(最終: "so the company rolled back" の因果。台帳はミスを認め当面ロールバックと並記、因果は明示せず) |
| G12 | Meta paused Muse’s human concierge feature after concerns that users weren’t told contractors might access sensitive information. | Ledgerは適切な開示がなかったことを記録していますが、誰への開示が欠けていたかは特定していません。この要約は、利用者への説明が欠けていたことを懸念の対象として特定しています。 [changed_scope] | 過剰判定の疑い(最終: "concerns that users weren’t told contractors might access sensitive information" は懸念の形で、指摘は "users" 特定のみ) |
| G14 | In one line: “Meta paused its AI phone feature after some calls were handled by human contractors without a clear explanation.” | 「AI phone feature」とすることで、当面ロールバックされた対象を人間担当者が関与する電話機能からAI電話機能全体へ広げています。 [changed_scope] | 境界例(最終: "paused its AI phone feature after some calls were handled by human contractors" は MUSE-HC-07 に G04 のような明示の禁止notesがない) |

**内訳**: attempt1 基準(14世代)= {'明確な誤り': 5, '境界例': 7, '過剰判定の疑い': 2}。STOP 8世代の最終MAJOR基準 = {'過剰判定の疑い': 3, '明確な誤り': 1, '境界例': 4}。

- 事実: 要約の主要な指摘語は "AI phone feature / calling feature"(ロールバック対象の範囲、G01/G03/G04/G11/G14)と "users"(開示相手、G02/G07/G09/G12)の2系統(判定: 手動の集計)。
- 事実: 台帳 MUSE-HC-012 の notes_for_writer(「サービス全体を停止した」とは書かない)は G01/G04/G11 で直接の根拠になった。MUSE-HC-07(G14)にはこの notes がない。
- 注意: 分類は1名(LLM)の手動判定。境界例・過剰判定の疑いのうち3件は `S0_USER_CHECK.md` に抜いた。

## 4. (d) FLOOR_MODE の確認

- 対象: Trial A の Checker 実行(all6: `er052_output/all6_writer_redesign_necessity_01/runs/*/control/*/checker/`)38 実行、Trial B の追加分(factlock: `er052_output/factlock_writer_trial_01/runs/*/control/*/checker/`)19 実行。
- 確認方法: 各 run の `checker/approved_switches_dump_after_p01.json` の `switches` を読取り、sha256 を計算して、同 run の `checker/runs/*.json` の `provenance.switch_dump_sha256` と比較。
- 結果: 57/57 で `FLOOR_MODE="number_only"`、`STAGE1_RECLASSIFY=true`、`PRECHECK_MODE="number_only"`、sha256 一致、`provenance.switches_equal_e2e02=true`。(同 dump に `FLOOR_VERIFY_MODE="off"`・`CAUSAL_FLOOR=false`・`STAGE2_DOWNGRADE_VERIFY=false`・`STAGE2_SECOND_OPINION=true` も含まれる: 代表 run `meta/b3__baseline__r1` の dump で目視確認。)
- 判定: Trial A/B の Checker は FLOOR_MODE=number_only で動いた(直接確認)。承認構成 `OPEN233_APPROVED_FLOW_SWITCHES`(`er052_open233_self_recovery_flow_runner_01.py` L497-522)との全キー突合は行っていない(主要3キーのみ全件確認)。

## 5. (e) EV-28 の証跡照合(Opus未照合分)

対象: EV-28(TA-034、重大、meta/b3 baseline r1)=`er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1`。

1. EN 文: 末尾要約 "Meta’s AI phone calls sometimes relied on human contractors, but callers were not clearly told who was speaking."(`b1b/article.md`)。JA対応文なし(要約は別callでEN記事から生成)。
2. EN deviation check(`b1b/audit/deviation_checks/advanced_attempt1.json`、`deviation_check.json`): overall_status=LEDGER_COMPLIANT。指摘は2件のみ(MINOR/ja_source の "Meta executives"、MINOR/translation の EV-25 "employees reported" [changed_number])。**要約 "callers" への指摘は無い**(検出なし)。
3. Checker Stage 1(`checker/runs/meta_run03_advanced.json`): 単位 L1 が `model_r3`+`model_r5` の両経路で候補化。flags: changed_fact, changed_certainty, **changed_actor**, unsupported_new_claim。related_fact_ids=MUSE-HC-012, MUSE-HC-014。issue(要旨): 「適切な開示なし」を「通話相手に話者が誰かを明確に伝えていなかった」という具体的主張にしている。
4. 再分類(同 dump `candidate_filter.verdicts`): L1 は `CANDIDATE`(excluded=false、actor_match=match)。**再分類で除外されなかった**。
5. Stage 2 cycle1: 一次 `llm_materiality=ACCEPTABLE`(basis=none)→ 第2意見(`STAGE2_SECOND_OPINION`)が `BLOCKING`(basis=ledger_scope)で split → 最終 `materiality=BLOCKING`、`floor_reason=s1_second_opinion_blocking`。rewrite_hint に「開示されなかった相手を発信者ではなく、電話を受ける側(people being called / call recipients)として記述」が入った。
6. 書換え: cycle1 の rewrite(`replace_with_ledger_value`、`e1_minimal_word_edit`、guard_ok=true)で、最終要約は "…but people being called were not given proper disclosure."。cycle2・cycle3 の再評価は ACCEPTABLE(第2意見も ACCEPTABLE)。final_state=`RESOLVED_REWRITE_THEN_DOWNGRADE`。
7. 結論(事実): EV-28 は EN deviation check をすり抜け、Checker が Stage 1 で changed_actor 付きで候補化し、再分類は除外せず、Stage 2 一次 ACCEPTABLE を第2意見が BLOCKING にして救済した経路。ANALYSIS_01 の記述と一致。EV-25 との差は「再分類が除外したか否か」(EV-28=維持、EV-25=SUPPORTED で除外)。

## 6. 未確認事項・限界

- 再検査・出口の再分類の claim 単位 verdict は dump に無い(件数のみ)。
- 133実行は記事の重複(同一記事・別Trial)を含む。独立標本数ではない。
- 「M3で救済され得る」は Stage 2 へ渡る上限であり、救済(BLOCKING化)の確率ではない。
- EV-25/EV-19 が Stage 2 に載った経路(兄弟location展開)はコード未確認。
- 要約14世代の一次分類は手動判定(1名)。ユーザー確認3件の結果次第で分類が変わり得る。
- 14世代には Trial A/B 57実行の外(`gpt6_wiring_e2e_01` の G14)を含む。
