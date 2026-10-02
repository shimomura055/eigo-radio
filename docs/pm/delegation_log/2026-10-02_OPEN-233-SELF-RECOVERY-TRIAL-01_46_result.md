<!-- 抽出元transcript: agent-a8401b13fe2a002ff.jsonl(subagents配下。指定の.outputは0バイトで抽出不能だったため同内容のsubagent transcriptを使用)。抽出日時: 2026-10-02T21:37:24。本文(最後のassistantメッセージ)は改変していない。 -->

## 委任_46 報告(read-onlyの事実確認。コード・SSOT・設計書・ACTIVE_TASK/RESULT_PACKETは未編集、API費用¥0、git操作なし)

### 1. 結論
- 問A-4: 「Also, some calls needed user information to continue.」は **「判断が分かれる」**。分かれ目は記事の「some calls needed」(一部の電話で実際に必要だった=発生の断定)と、Ledgerの`conditions`「電話の遂行にユーザー情報が必要となる場合」(条件)の差。確度(条件→発生)の差は具体的に指せるが、数値・主体・否定・比較・時期は変わらず、記事側も直後の文で「might accidentally be shared」と留保している。BLOCKING相当かどうかも分かれる。Stage 2の字面の基準(矛盾/別原因/notes禁止の断定)では「矛盾」とまでは言えずQUALITY寄り。一方、設計書は正解ラベルとしてMUSE-HC-010(Meta-1)をSafety-critical=BLOCKING維持にしている(§4-21、§7-0-iter29)。したがって「見逃しが本物の見逃しか」は、設計書のV4原則(条件付きの可能性→既成事実への断定をBLOCK候補にする)を採るか否かで決まる。
- 問A-5: meta_run03_standardの23実行(rep22は並行タスク作成中のため集計外)で、文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終わったのは **5実行**(rep16 s1/s2、rep18 s1/s2、rep21 s2)。固定Stage 1を使った7実行に限ると1実行(rep21 s2)のみ。他の4実行は、Stage 1(fresh)がそもそもこの文を出さなかった実行。
- 問B: P2a+P2b 34行を重複排除すると **23種類**。「元のまま残り・一度もBLOCKINGで指摘されず・解消」の上限は、種類×実行の組で202組、実行単位では**70実行**(対象7記事の延べ106実行中)。ただし種類は互いに入れ子(同じ文の部分文字列等)があり、この数は「見逃しがあった場合に誤って合格になった可能性の上限」であって、実際に逸脱だった数ではない。上位5種類の個別判定は、逸脱であると言えたものが0、判断が分かれるが2(Oil prices系)、逸脱ではないが3(neg1の3文)。
- 問C-4: 「英語見出しだけ直すと日本語タイトルに誤りが残る経路」は **成立する**。`derive_japanese_title`は英語記事を一切入力にしない。これを前提にした対策候補は6章末に記載。

### 2. 問A

**A-1 Ledger(逐語)**。出所は`er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/standard_attempt1.json`の`prompt`内のLedger(Checkerが実際に見たもの)。`research_ledger/fact_ledger_draft.json`と一致。
```
[VERIFIED] MUSE-HC-010: Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。
  scope: 人間の契約スタッフがMuse経由の電話を担当するテスト
  conditions: 電話の遂行にユーザー情報が必要となる場合
  date_or_period: 2026年9月中旬〜2026年9月22日
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 懸念の存在を示す事実。実際の大規模な情報漏えいが発生したと断定しない。 (channelnewsasia.com ...)
```
draft.jsonにはさらに `source_type: RELIABLE_SECONDARY_NEWS`、`support_level: DIRECTLY_STATED`、`ambiguity: 実際にどの種類・量の個人情報が契約スタッフへ共有されたかについて、一般的な範囲は公表されていない。` がある。

隣接fact(同内容に触れるもの):
- `MUSE-HC-015`(逐語抜粋) notes_for_writer: 「公式の製品設計上の説明と、実験時の実際の情報共有運用を混同しない。」
- `MUSE-HC-003`(逐語抜粋) notes_for_writer: 「Meta自身の設計説明。人間コンシェルジュ実験における請負業者への情報共有範囲を直接説明する資料ではない。」
- 「実際にユーザー情報が必要になった電話があった」と述べるfactは、Ledger全体に無い(Grepとブロック走査で確認)。

**A-2 記事側(cycle1のEN本文、監査JSONの記事と完全一致を確認)**
```
They did not realize it.
That was happening behind the scenes.
>> Also, some calls needed user information to continue.
That information might accidentally be shared with contract workers at a call center.
Meta employees pointed this out inside the company as a privacy concern.
```
日本語(翻訳元)記事の対応文と前後(逐語):
- 「AIの便利さを楽しんでいたら、いつの間にか電話の向こうに人間がいた。」
- 「そんな舞台裏です。」
- >>「さらに、電話を進めるために利用者の情報が必要になる場合、その情報がコールセンターの契約スタッフに意図せず共有される可能性もあります。」
- 「Metaの従業員は、この点をプライバシー上の懸念として社内で示しました。」
- 「報道では、インターネットやケーブル料金を交渉する電話で、…」

日本語は条件形(「必要になる場合」)で、英語の「some calls needed」が条件を発生の断定へ変えている。固定fixtureのStage 1出力(`deviations`)は related_fact_id が MUSE-HC-012 と MUSE-HC-011 の2件のみで、HC-010は含まない(確認済み)。

**A-3 この文を指摘したRecheck 4回(逐語)**。4回とも `severity=MAJOR`、`origin=translation`、`related_fact_id=MUSE-HC-010`、`llm_materiality=BLOCKING`、最終`BLOCKING`、`floor_reason=None`、`floor_cited_reason=None`、`auto_downgraded=false`、`stage2_route=body`、`basis=ledger_conditions`、`rewrite_kind=narrow_scope`、`qualifier_present=true`。

| run/cycle | claim_in_article | trueのboolフラグ | issue(逐語) |
|---|---|---|---|
| iter8 s1 c2 | Some calls needed user information to continue. | changed_fact, changed_certainty, unsupported_new_claim | The article says some calls actually needed user information, whereas the Ledger records a privacy concern conditional on user information being needed; it does not establish that this occurred in some calls. |
| rep19 s1 c2 | “some calls needed user information to continue.” | 同上3つ | The Ledger describes a concern that information could be needed for a call and might be shared; it does not establish that some calls actually required user information. The English wording turns a conditional into an asserted occurrence. |
| rep20 s1 c2 | “Some calls needed user information to continue.” | changed_fact, changed_certainty | This asserts that user information was needed in some calls. The Ledger records a concern about possible sharing in cases where user information is needed, but does not establish that this occurred in some calls. |
| rep21 s1 c3 | “Some calls needed user information to continue.” | changed_fact, changed_certainty, unsupported_new_claim | The Ledger describes a privacy concern in the event that user information is needed to carry out a call; it does not establish that some calls actually required such information. |

- 補足: 4回ともフラグは`changed_actor/number/negation/comparison/time`(runner `FLOOR_FLAGS`、452〜455行)を含まない。したがって決定論的floorは発動せず、BLOCKINGはStage 2のLLM判定(`ledger_conditions`)だけで決まっている。disclosure_gap降格(`apply_disclosure_gap_downgrade`、2040〜2066行)は否定表現の語を要するため該当しない(降格の適用なし)。
- explanation(iter8 s1)逐語: 「“Some calls needed” presents the condition as an actual occurrence. The following “might” hedges possible sharing, but does not hedge the claim that some calls needed the information.」
- 参考: rep22 s2 c2も同様に指摘している(並行タスク作成中のため集計外)。

指摘しなかった4回(文は再検査対象本文に存在)。いずれもHC-010の指摘は1件も無く、別の文で出ている。
- iter8 s2 c2(8件): HC-011 BLOCKING「“These calls were about trying to lower internet or cable fees.”」/HC-007 BLOCKING「“They enjoyed AI’s convenience, ... They did not realize it.”」/HC-011 BLOCKING「It said human staff made inappropriate comments about race during one call.」/HC-011 BLOCKING「However, this is only one case.」/HC-007 QUALITY「People asking Muse to call might think AI was calling.」/HC-007 QUALITY「If no one explained this clearly, users could not know.」/HC-007 BLOCKING「They could not tell if it was AI or a person.」/HC-007 QUALITY「Some calls through Meta’s AI assistant were actually handled by humans, but users were not properly told.」
- rep20 s2 c2(1件): HC-012 BLOCKING「“They could not tell if it was AI or a person” and “They did not realize it.”」
- rep21 s1 c2(2件): HC-012 QUALITY「“They enjoyed AI’s convenience, ...”」/HC-011 BLOCKING「“These calls were about trying to lower internet or cable fees.”」
- rep21 s2 c2(1件): HC-012 QUALITY「“They enjoyed AI’s convenience, ...”」
(これで「文が存在するRecheck 8回中4回指摘」と一致。)

**A-4 判定: 「判断が分かれる」**
- 根拠(DEVIATION_PROMPT_TEMPLATEの10種フラグに照らす):
  - 読みA(逸脱): Ledgerの`conditions`は懸念が成立する前提(電話の遂行にユーザー情報が必要となる場合)であり、「実際にそういう電話があった」とは書いていない。記事は「some calls needed」で発生を断定している。changed_certainty(仮説→断定)に当たる確度差を、具体的に指せる。
  - 読みB(逸脱ではない): `conditions`をこの懸念の適用範囲の記述と読めば、「some calls needed user information」はその範囲に当たる呼の記述にすぎない。新しい数値・人物・出来事は無く、notes_for_writerが禁じる「大規模な情報漏えいの発生」の断定もしていない。直後に「might accidentally be shared」「Meta employees pointed this out … as a privacy concern」と留保・帰属が残る。
  - 分かれ目の語句: 記事「some calls needed」(過去形・存在) ⇔ Ledger「必要となる場合」(条件)。
- BLOCKING相当か: Stage 2の字面の基準(`MATERIALITY_RUBRIC`、stage2_production 37〜46行)では「Ledgerのconditions等と**矛盾**する/別原因・別主体/notes禁止の断定」がBLOCKINGで、この文は矛盾とまでは言えず、「矛盾しないがLedgerが保証していない」ためQUALITYに近い。ただし「迷えばBLOCKING(fail-closed)」(同46行)があり、LLM判定がBLOCKINGになりうる。上記A-3のとおりfloorは発動しない。
- 設計書の正解ラベル: 設計書にMUSE-HC-010の記載あり。§4-21(1404〜1427行)と§7-0-iter29(3543〜3555行)で「条件付きの可能性→既成事実への断定」を独立原則(V4)として追加し、Meta-1(MUSE-HC-010「needed user information to continue」)をSafety-critical(BLOCKING維持)に残している(runner `SAFETY_CRITICAL_CLAIM_DEFS`、5676〜5679行にも"Meta-1"として登録)。§7-1(3633行)もMeta_run03_standardをBLOCKING(rubric基準1)としている。一方、同じfactのcertainty強化の別claim「A4-2」はQUALITYへ再ラベルされている(3465〜3468行)。つまり、設計書ラベルの上ではこの文は「BLOCKINGとして拾うべき」側にある。これはFableの正解ラベルであり、私の判定ではない。上の判定は、Ledger文言と記事文言の突き合わせによる私の判断。

**A-5 meta_run03_standard全実行(iter5〜rep21、23実行)**。対象文は「Also, some calls needed user information to continue.」。「最終EN記事」は、記録されたRewrite後の本文のうち最後のもの。無ければ元記事。「文残存」は完全一致(空白正規化のみ)。

| 実行 | Stage1 | 最終状態 | 文が元のまま残る | HC-010をBLOCKING指摘 | 最終記事の該当箇所 |
|---|---|---|---|---|---|
| iter5 s1 | fresh | RESOLVED_REWRITE | 否 | c1 | Also, if a call needed user information, it might reach contract workers... |
| iter5 s2 | fresh | RESOLVED_REWRITE | 否 | c1 | If a call needed user information, it might be shared by mistake... |
| iter6 s1 | fresh | STAGE4 | 否 | c1 | Also, some calls might need user information to continue. |
| iter6 s2 | fresh | STAGE4 | 否 | c1 | (該当文なし) |
| iter7 s1/s2 | fresh | RESOLVED_REWRITE | 否 | c1 | Also, some calls might need user information to continue. |
| iter8 s1 | 固定 | STAGE4 | 否 | c2 | Also, Meta employees worried that, if a call needed ... |
| iter8 s2 | 固定 | STAGE4 | 残る | 無し | 元のまま |
| rep9 s1/s2 | fresh | RESOLVED_REWRITE / _THEN_DOWNGRADE | 否 | c1 | ...could need / might need ... |
| rep11 s1 | fresh | STAGE4 | 否 | c1 | ...might need... |
| rep11 s2 | fresh | RESOLVED_REWRITE_THEN_DOWNGRADE | 否 | c1 | ...might need... |
| rep12 s1/s2 | fresh | RESOLVED_REWRITE | 否 | c1 | ...might/could need... |
| rep16 s1/s2 | fresh | RESOLVED_STAGE2_DOWNGRADE | **残る** | **無し** | 元のまま(Rewrite無し) |
| rep18 s1/s2 | fresh | ACCEPTABLE_STAGE1 | **残る** | **無し** | 元のまま(Stage 2到達せず) |
| rep19 s1 | 固定 | STAGE4 | 否 | c2 | Also, a call might need user information to continue. |
| rep20 s1 | 固定 | RESOLVED_REWRITE_THEN_DOWNGRADE | 否 | c2 | If a call needed user information, it might be shared by mistake... |
| rep20 s2 | 固定 | STAGE4 | 残る | 無し | 元のまま |
| rep21 s1 | 固定 | STAGE4 | 残る | c3 | 元のまま |
| rep21 s2 | 固定 | RESOLVED_REWRITE_THEN_DOWNGRADE | **残る** | **無し** | 元のまま(Rewriteは別の箇所) |

- 「文が元のまま残り・一度も指摘されず・解消(人間確認なし)で終わった」実行 = **5**(rep16 s1/s2、rep18 s1/s2、rep21 s2)。固定Stage 1の7実行(iter8 s1/s2、rep19 s1、rep20 s1/s2、rep21 s1/s2)に限ると1。
- 元のまま残るが一度も指摘されない7実行のうち、STAGE4(人間確認行き)の2実行(iter8 s2、rep20 s2)は除外。
- 副次的な事実: 指摘された16実行(うち12は`fresh`のcycle 1で指摘)では、Rewrite後の文はすべて「might/could need」や「if a call needed」に弱められている。
- rep22(並行タスクが生成中)の参考値は、現時点でs1〜s4が存在し、s1/s3/s4は文が残り未指摘、s2は指摘あり。生成途中のため上の集計には含めない。

### 3. 問B

**B-1** 委任_44の`cases_detail_01.csv`のP2a+P2b = 34行(P2a 18+P2b 16)。キーは(instance, fact, 外側引用符除去・空白/大小/曲線引用符を正規化したclaim)で重複排除 → **23種類**(K01〜K23)。34行の合計と一致(種類ごとの`n_rows`合計=34)。

**B-2/B-3 種類ごとの件数**(「該当」=元のまま残り・一度もBLOCKING指摘なし・最終が解消(RESOLVED_*/ACCEPTABLE_STAGE1)。「確認不能」=0件)。判定規則は`check_01.py`冒頭に記載。

| ID | 記事 | fact | 該当文(要約) | P2行 | 該当実行/同記事の全実行 | 残るが指摘あり | 残るがSTAGE4 |
|---|---|---|---|---|---|---|---|
| K01 | bgroup_B4 | HC-006 | A call came from an AI agent...It was a person. | 1 | 2/5 | 0 | 0 |
| K02 | hormuz_run03_standard | HF-009 | Oil prices moved briefly, then returned to a high level. | 3 | 16/23 | 2 | 2 |
| K03 | 同 | HF-009 | The fee plan vanished, but oil prices stayed high as tensions... | 1 | 16/23 | 0 | 2 |
| K04 | meta_run03_standard | HC-010 | some calls needed user information to continue. | 4 | 5/23 | 1 | 2 |
| K05 | 同 | HC-011 | human staff made inappropriate comments about race during calls. These calls... | 2 | 9/23 | 0 | 2 |
| K06 | 同 | HC-011 | It said human staff made ... (K05の前に「It said」) | 2 | 9/23 | 0 | 2 |
| K07 | 同 | HC-011 | These calls were about trying to lower internet or cable fees. | 1 | 9/23 | 2 | 2 |
| K08 | 同 | HC-012 | But sometimes, a human was speaking instead. | 1 | 15/23 | 0 | 7 |
| K09 | 同 | HC-012 | The problem was telling users who was speaking. | 1 | 15/23 | 0 | 7 |
| K10 | 同 | HC-012 | They enjoyed AI’s convenience, but a human was on the other end. | 1 | 13/23 | 2 | 3 |
| K11 | neg1_meta_b3prod_a2 | HC-012 | A Meta executive admitted the mistake. The test had begun without clearly telling users. | 1 | 19/22 | 0 | 2 |
| K12 | 同 | HC-012 | A user might think the exchange was with AI, even though a person was involved. | 1 | 19/22 | 0 | 2 |
| K13 | 同 | HC-012 | The test began without clearly telling users that contract workers would make the calls. | 1 | 19/22 | 0 | 2 |
| K14 | neg3_hormuz_prodrunner_b1b | HF-003 | トランプ氏は、…二割の償還を求めると投稿した。(日本語) | 1 | 11/15 | 1 | 3 |
| K15 | 同 | HF-009 | During that period, attacks between the United States and Iran... | 1 | 7/15 | 1 | 3 |
| K16 | 同 | HF-009 | The fee plan left the stage, but the events driving oil prices... | 1 | 0/15 | 1 | 0 |
| K17 | 同 | HF-009 | The fee plan may be replaced, but events continuing... | 1 | 7/15 | 1 | 3 |
| K18 | safety_A2A3 | HF-003 | アメリカが海峡の安全を守るために使う費用を、…(日本語) | 2 | 4/13 | 0 | 3 |
| K19 | 同 | HF-009 | Just after the charge plan disappeared, prices began to fall. Soon, however... | 1 | 7/13 | 0 | 5 |
| K20〜K22 | safety_A4 | HC-006 | The idea was practical: when AI struggled...(入れ子3種) | 1+2+1 | 0/5 | 各1 | 各1 |
| K23 | 同 | HC-012 | An AI called. That was what people thought as they spoke. | 3 | 0/5 | 1 | 0 |

- 上限: 種類×実行の組 **202組**、実行単位では**70実行**(7記事の延べ106実行中)。K05/06/07、K20/21/22などは入れ子で、組の合計は重複を含む。最終状態別の内訳(組): RESOLVED_REWRITE 74、RESOLVED_REWRITE_THEN_DOWNGRADE 55、RESOLVED_STAGE2_DOWNGRADE 48、ACCEPTABLE_STAGE1 25。
- 注意: 日本語2種類(K14、K18)の最終JA本文は、JAが変更されなかった実行では元記事と同じと推定している(runnerはJA本文を変更時のみ記録、5378〜5380行付近)。
- 上位5種類(該当実行数の多い順、同数は同順位。5位以内の境界に同数なし): K11、K12、K13(各19)、K02、K03(各16)。

**上位5種類の判定**(Ledgerと記事の突き合わせによる私の判定。Ledger原文は監査JSONのpromptから確認)
- K11「A Meta executive admitted the mistake. The test had begun without clearly telling users.」: **逸脱ではない**。Ledger HC-012は「MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め…」。「副社長→executive」は同一組織内の役職の一般化(設計書§7-0-iter29がA5-1をQUALITY扱いにした型と同型)。「without clearly telling users」は「適切な開示なし」の言い換え。違いが指せるとすれば開示を受ける側が「users」である点だが、Ledgerは開示対象を限定していない。Stage 2のLLM独立判定は ACCEPTABLE。BLOCKINGは、列挙された複製claim(`detected_by_enumeration`)にfloor(`changed_actor`)が掛かった結果(iter7 s1 c2のみ)。この波及は委任_35(§6-16)で是正済みと設計書に記載(私は是正後の挙動を再測定していない)。
- K12「A user might think the exchange was with AI, even though a person was involved.」: **逸脱ではない**(「might」の条件付き一般論で、新しい具体的事実・数値・主体を加えない)。Stage 2 LLM判定はQUALITY、BLOCKINGはK11と同じfloor。
- K13「The test began without clearly telling users that contract workers would make the calls.」: **逸脱ではない**(HC-012の「適切な開示なしで契約スタッフが電話を担当していたテスト」とほぼ同義)。Stage 2 LLM判定はACCEPTABLE、BLOCKINGは同じfloor。
- K02「Oil prices moved briefly, then returned to a high level.」: **判断が分かれる**。Ledger HF-009のscopeは「国際指標Brent原油先物の短時間の値動き」で、記事は「Oil prices」と一般化している(changed_scopeとして具体的に指せる)。一方、値動きの内容(一時的な上げ幅縮小の後に高水準へ戻った)はLedgerと一致し、notes_for_writer「撤回後に原油価格が全面的に下落したとは書かない」に反しない。設計書§7-0-iter27(1480〜1488行)は、Brent先物→oil pricesのこの一般化を「原則許容候補」とし、正解ラベルをACCEPTABLE/QUALITYへ改めている(2026-10-01ユーザー指示)。分かれ目: 「Oil prices」⇔「Brent原油先物」。現行ラベルではBLOCKING相当ではない。
- K03「The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.」: **判断が分かれる**。K02と同じ「oil prices」の一般化に加え、「as tensions ... continued」の因果的な接続がある。HF-009は`causal_strength: CAUSAL_STATED_BY_SOURCE`で`conditions`に米・イラン間の攻撃・海上封鎖・タンカー懸念の継続が明記されているため、因果の方向は矛盾しない。分かれ目は「oil prices」。現行ラベルではBLOCKING相当ではない。

### 4. 問C

**C-1 `derive_japanese_title`の入力**(`er019_family_x_audio_production_runner_01.py` 133〜147行)
```
133 def derive_japanese_title(source_dir: str) -> dict:
135     evidence_path = f"{source_dir}/ja_writer/runtime_evidence.json"
136     if os.path.exists(evidence_path):
138         title = evidence.get("title")
139         if title: return {"japanese_title": title, ...}
141     for name in ("revision2.md", "revision1.md", "original.md"):
142         p = f"{source_dir}/ja_writer/{name}"
144             first_line = load_text(p).splitlines()[0].strip()
```
- 入力は`source_dir/ja_writer/`配下のJA writer成果物だけ。優先は`runtime_evidence.json`の`title`(JA writerが`_extract_title`で生成、`er019_family_x_ja_writer_o_r1_r2_01.py` 503行)、無ければ`revision2.md`→`revision1.md`→`original.md`の1行目。**英語記事(a2/b1b)も英語見出しも入力ではない**。呼び出しは1852行(`main`)、A2の`japanese_title`セグメント(933〜947行)で使われ、`if "a2" in levels`のときだけ必要(1854行)。
- Trial runner(`er052_open233_self_recovery_flow_runner_01.py`)には`japanese_title`/`derive_japanese_title`の処理は無い(Grep 0件)。接続した場合にこの関数の入力になりうるのは、JA側の`ja_text_after_rewrite`を`ja_writer/`のファイル(特に`runtime_evidence.json`の`title`)へ書き戻した場合だけ。EN側の`en_text_after_rewrite`(見出し含む)は入力にならない。さらに`runtime_evidence.json`の`title`が優先されるため、`revision*.md`を書き換えても、`title`を更新しない限りタイトルは変わらない。
- 未確認: hormuz run_03では`runtime_evidence.json`の`title`「二十パーセントの料金案、翌日には退場。それでも原油は高値に戻った」と、`revision2.md`1行目/EN生成の元になったJA記事の1行目「料金案は退場、原油高は居残り」が一致しない。どちらが出荷されたかは、この委任の範囲では確定していない(derive_japanese_title上は`title`が優先)。

**C-2 EN見出しを違反箇所に含むBLOCKING指摘**(iter5〜rep21の全instance、最終materiality=BLOCKINGの346行。委任_41の`claims_detail_01.csv`のBLOCKING 261+85=346と一致)
- 厳密(claim文字列が見出しの全部/一部と重なる): **6行**
  - bgroup_B4 MUSE-HC-012: 1(iter5 s1 c3)
  - bgroup_B4 MUSE-HC-006: 2(iter5 s2 c2、iter6 s1 c3)
  - neg1_meta_b3prod_a2 MUSE-HC-006: 2(iter6 s1 c2、c3)
  - hormuz_run03_standard HF-009: 1(rep9 s1 c3)
  - 6行すべてStage 2のLLM判定もBLOCKING(floor無し)。最終状態: iter5 s2のみRESOLVED_REWRITE_THEN_DOWNGRADE、他はSTAGE4。
- 補助(見出しを`same_fact_id_locations`として列挙: 9行(hormuz 7、neg1 2)、見出しを位置語「headline」だけで指す: 2行(うち1行は上と重複))。合計で「見出しに触れる」のは**16行**/346行。
- 未確認: claim文字列が記事に確定できない34行は、見出しが含まれている可能性を排除できない。日本語claim 3行は日本語記事の1行目との重なりを判定したが、JA本文が記録されている記事ではヒット0(neg1のJA本文は記録なし)。

**C-3 日本語1行目(逐語)と判定**
- bgroup_B4: EN見出し「I Thought It Was an AI Call—But There Was a Person Inside? Meta’s Unexpected Muse Test」/JA1行目「AIからの電話だと思ったら…中に“人”がいた？　MetaのMuseで起きたまさかの展開」(ja_writerの`title`と同一)。
- neg1_meta_b3prod_a2: EN見出し「We Thought It Was AI—But There Was a Person Inside Meta’s Muse」/JA1行目は上と同一。
- 指摘の内容: Stage 2は「受け手が実際にAIだと思った/驚いたという認識はLedger(HC-006=訓練を受けた契約スタッフが一部の電話を担当、HC-012=開示なし)に無い」と判定(rewrite_hint逐語: 「受け手がAIだと思っていた、または実際に驚いたという認識は確認されていないため、その含意を外し…」)。このhintはJA見出しを引用して指示している。
- 判定: **入っている**(同じ「AIだと思ったら中に人がいた」という前提)。ただし日本語は疑問形・「〜たら」の形で、neg1の英語見出し(「We Thought…」の断言形)より断定は弱い。ここの分かれ目(断定の強さ)は「判断が分かれる」。そもそもこの前提がLedger逸脱かどうかも、書き手の物語的な掴み(hook)との境界にある(neg1は設計書のnegative候補=正常記事ラベル)。
- hormuz_run03_standard: EN見出し「The Fee Plan Leaves, But High Oil Prices Stay」(指摘は「High Oil Prices Stay」部分、Brent先物→oil pricesの一般化、changed_scope)/JA1行目(JA原文)「料金案は退場、原油高は居残り」/出荷用`title`「二十パーセントの料金案、翌日には退場。それでも原油は高値に戻った」。判定: JA「原油高」・出荷用「原油」も同じ一般化で **入っている**。ただし上のK02/K03と同じく、現行の正解ラベルでは許容側(§7-0-iter27)。

**C-4 結論**
- 英語見出しだけを直した場合に日本語タイトルへ誤りが残る経路は**成立する**(根拠はC-1: タイトルは英語記事を入力にしない。かつ`runtime_evidence.json`の`title`が優先される)。実害の有無は上記の「入っている」2系統(Meta Muse見出し、hormuz見出し)で、出荷用日本語タイトルにも同じ構図が実在する。ただし、これがLedger逸脱として扱うべきかは、上記の判断が分かれる点に依存する。hormuzはJA r2がJA側のfact-checkで`LEDGER_COMPLIANT`(`ja_r2_attempt1.json`)。B4/neg1のrun_01には`ja_writer/audit/deviation_checks/`が存在せず、JA側の合格は未確認。
- 対策の候補(実装はしない)。追加LLM呼び出しの要否/Production正式path変更の要否:
  1. 英語見出しを書き換えた記事のみ、日本語タイトルを英語見出しから作り直す: LLM要(翻訳または生成1回)/Production変更要(`derive_japanese_title`の入力変更と呼び出し側)。
  2. 英語見出しを書き換えた記事は日本語タイトルを人間確認へ回す: LLM不要/Production変更は不要の可能性が高い(Trial側のフラグで止める運用なら)。ただしProductionへ接続するなら停止点の追加が必要。
  3. 日本語タイトル(`runtime_evidence.json`の`title`)に、JA側のfact-check(`ja_writer`の既存deviation check)を適用済みかを確認し、未適用のrunだけ適用: 既存機構の再利用でLLM要(1回)/Production変更は要確認。
  4. 英語見出しは見出し専用の最小Rewrite(見出しのみ)に限定し、日本語タイトルは触らず記録だけ残す(ユーザー原則「日英整合だけを理由に日本語へ遡らない」に沿う): LLM不要/Production変更不要。ただし実害(上記「入っている」)は残る。
  5. 英語見出しをRewrite対象から外す(見出しは指摘対象外、または見出し専用の事前Checkへ): LLM不要/Trial runner側の変更のみ(Production変更不要)。ただし本文の同じ誤りは別途拾う必要がある。
  どの候補を採るかは、日本語タイトルがLedger逸脱として扱われる基準(Meta Muse見出しの「前提」とhormuzの「原油高」の扱い)を先に決める必要がある。

### 5. 検算・限界・未確認
- 検算: P2a+P2b 34行 = 種類別n_rows合計34(一致)。BLOCKING行346 = 委任_41のBLOCKING(stage1 261+recheck 85)と一致。meta_run03_standard 23実行 = A5の行数、最終状態別内訳(RESOLVED_REWRITE 7、STAGE4 8、THEN_DOWNGRADE 4、STAGE2_DOWNGRADE 2、ACCEPTABLE_STAGE1 2)の合計23と一致。A-3の「文が存在するRecheck 8回中4回指摘」は委任_44の記述と一致。
- 確認できたこと: Ledger原文、記事・JA文、Recheck出力(4回+4回)、各実行の最終状態、見出し指摘の件数、コード行。
- 推測・限界:
  - 該当実行数は「元のまま残り・未指摘・解消」の機械照合で、実際に逸脱だったかの数ではない(上限)。同じ記事でもiter/repでStage 1・Stage 2のPrompt・規則が異なり、古い実行は現行の挙動を表さない(特に委任_35のfloor是正前)。
  - 種類は入れ子があり、組の合計は重複を含む。種類の代表文字列は元記事に存在する形(大小は元記事に合わせる)で、claimがさらに別の句を含む場合の照合は代表文字列のみ。
  - 日本語2種類(K14、K18)の最終JA本文は、JAが変更されなかった実行では元記事と同じと推定(runnerのJA記録は変更時のみ、コード上の挙動からの推定で、記録からの直接確認ではない)。
  - rep22は並行タスクが生成中(s1〜s4が既に存在)のため集計外。数値は進行で変わる。
  - 見出しのC-2は、claim確定不能の34行を含まない。A-4/B判定は読み方の判断を含み、Production採用判断ではない。
  - DEVIATION_PROMPT_TEMPLATE本体(502〜601行)は`Read`せず、同じテンプレートの展開済みprompt(監査JSON内)で定義を確認した。
- 新しい仕様候補・改善案: 実装せず、C-4の候補1〜5として記載のみ。

### 6. 読んだファイル・追加Read・T-0・成果物
- 読んだファイル(範囲): `er052_output/open233_cycle_new_issue_analysis_01/analyze_01.py`(全文)、同`cases_detail_01.csv`(P2a/P2b行をスクリプトで)、`er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`(deviationsのみ)、`er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`・`unverified35_classification_01.csv`(必要行)、`er052_open233_self_recovery_stage2_production_01.py` 28〜86行、`er052_open233_self_recovery_flow_runner_01.py` 448〜458/1745〜1773/2030〜2066/5225〜5245/5660〜5700行付近、`er019_family_x_audio_production_runner_01.py` 125〜165/1835〜1885行、`docs/pm/design_open233_self_recovery_flow_01.md` 816〜828/930〜948/1400〜1430/2935〜2965/3171〜3216/3395〜3452/3460〜3560/3618〜3673行、各instance JSON(スクリプトで該当フィールドのみ)。
- 一覧外のRead/確認(理由): ①`er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/standard_attempt1.json`・`research_ledger/fact_ledger_draft.json`(Ledgerの所在特定。Grepでは`er052_output`を除く全体にヒットが多く、Checkerが実際に見たLedgerを確認するため)、②`er019_output/family_x_b3_production_wiring_01/run_01/{a2,b1b}/audit/...`、`hormuz/run_03/{a2,ja_writer}`等(C-3の日本語1行目・出荷用タイトル確認)、③`er050_gpt6_checker_comparison_trial_01.py`・`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`の該当行(fixtureの出所特定)、④`er019_family_x_ja_writer_o_r1_r2_01.py` 200〜206/503行付近(titleの生成元確認)。
- T-0: 委任文を`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md`へ全文保存し、`check_delegation_prompt.py`を実行。結果は **FAIL**(reasons: 「実行コマンドに引数実値/絶対パスが無い行: ``` | ``` | ``` | ```」=コードフェンス行の誤検出と思われる。警告: TTSを伴う委任文ではないが「差分再生成/--budget」言及なし)。委任文の指示どおり記録のみで作業は継続。
- 作成ファイル(すべて未追跡のまま残置、git add/commitなし):
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md`
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md_check.json`
  - `C:\Users\tensh\eigo-radio\er052_output\open233_missed_detection_truth_check_01\check_01.py`
  - `C:\Users\tensh\eigo-radio\er052_output\open233_missed_detection_truth_check_01\results_01.json`
  - `C:\Users\tensh\eigo-radio\er052_output\open233_missed_detection_truth_check_01\cases_01.csv`
  (実行コマンドは委任文どおり`.venv\Scripts\python.exe ...\check_01.py`で、終了コード0を確認済み。)