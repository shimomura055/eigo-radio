# OPEN-233 見逃し候補23種類の再分類(2026-10-03、委任_51)

- 管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_51)。read-only分析+文書作成(API費用¥0、コード・Prompt・テスト未変更)。
- 目的: ユーザー決定(2026-10-03、`DECISION_LOG.md`末尾エントリ)の例1(K04)=軽微、例2(K10)=問題なし、を基準例として補正した線引き(`docs/pm/open233_materiality_criteria_2026-10-03.md`のFable案)で、委任_46の見逃し型23種類(K01〜K23)を再分類する。**Production採用ではない。`VALIDATED`ではない。**
- 入力: `er052_output/open233_missed_detection_truth_check_01/{cases_01.csv,results_01.json}`(委任_46)、`er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`(委任_44、旧判定)、Ledger原文は各instanceのfixture(`er052_open233_self_recovery_flow_runner_01.py`の`build_target_instances()`の`fixture['ledger_text']`。meta_run03_standardのHC-010ブロックが委任_46 A-1が監査JSON`prompt`から抜いたものと一致することを確認済み)。
- 分類は、Fable案の線引きを**文言のまま**適用した(黙って変えていない)。適用で無理・矛盾が出た箇所は、`docs/pm/open233_materiality_criteria_2026-10-03.md`の「Fable案への指摘」節に書いた。境界(判断が分かれる)種類は各節に明記し、下の感度表で結果への影響を示す。
- 「旧判定」はflow内の最終materiality(BLOCKING)の根拠。23種類すべて、旧判定は最終BLOCKING(LLM判定、決定論floor、または両方)。
- 「見逃し」の数え方(委任_46 B-2): 同instanceの他実行で、その文が最終記事に元のまま残り・一度もBLOCKINGで指摘されず・最終状態が解消(RESOLVED_*/ACCEPTABLE_STAGE1)。STAGE4(人間確認行き)は数えない。

## 1. 全23種類の新判定一覧

| ID | instance / fact | 原文(要約) | 旧判定の根拠 | 新判定 | 見逃し(参考値`n_qualifying`/実行数) |
|---|---|---|---|---|---|
| K01 | bgroup_B4 / HC-006 | A call came from an AI agent … It was a person. | LLMのみ | 問題なし | 2/5 |
| K02 | hormuz_run03_standard / HF-009 | Oil prices moved briefly, then returned to a high level. | LLMのみ | 軽微 | 16/23 |
| K03 | 同 / HF-009 | The fee plan vanished, but oil prices stayed high as tensions … | LLMのみ | 軽微 | 16/23 |
| K04 | meta_run03_standard / HC-010 | some calls needed user information to continue.(例1) | LLMのみ | 軽微(ユーザー決定) | 5/23 |
| K05 | 同 / HC-011 | human staff made inappropriate comments about race during calls. These calls were … | LLM+floor(number) | 軽微(境界) | 9/23 |
| K06 | 同 / HC-011 | It said human staff …(K05の前に「It said」) | LLM+floor(number) | 軽微(境界) | 9/23 |
| K07 | 同 / HC-011 | These calls were about trying to lower internet or cable fees. | LLM+floor(number) | 軽微(境界) | 9/23 |
| K08 | 同 / HC-012 | But sometimes, a human was speaking instead. | floorのみ(actor) | 問題なし | 15/23 |
| K09 | 同 / HC-012 | The problem was telling users who was speaking. | floorのみ(actor) | 問題なし | 15/23 |
| K10 | 同 / HC-012 | They enjoyed AI’s convenience, but a human was on the other end.(例2) | LLMのみ | 問題なし(ユーザー決定) | 13/23 |
| K11 | neg1_meta_b3prod_a2 / HC-012 | A Meta executive admitted the mistake. The test had begun without clearly telling users. | floorのみ(actor、列挙波及) | 軽微 | 19/22 |
| K12 | 同 / HC-012 | A user might think the exchange was with AI, even though a person was involved. | floorのみ(actor) | 問題なし | 19/22 |
| K13 | 同 / HC-012 | The test began without clearly telling users that contract workers would make the calls. | floorのみ(actor) | 問題なし | 19/22 |
| K14 | neg3_hormuz_prodrunner_b1b / HF-003 | トランプ氏は…二割の償還を求めると投稿した。(日本語) | floorのみ(actor) | 問題なし | 11/15 |
| K15 | 同 / HF-009 | During that period, attacks between the United States and Iran … continued. | floorのみ(time) | 問題なし | 7/15 |
| K16 | 同 / HF-009 | …the events driving oil prices—and the prices themselves—quickly returned. | LLM+floor(time) | **重大** | 0/15(見逃し0) |
| K17 | 同 / HF-009 | The fee plan may be replaced, but events continuing … | floorのみ(time) | 軽微 | 7/15 |
| K18 | safety_A2A3 / HF-003 | アメリカが海峡の安全を守るために使う費用を、貨物を運ぶ側に返してもらうという考えです。(日本語) | LLM(+floor) | **重大**(英語の同内容文は検出済み) | 4/13(字面。内容は検出済み) |
| K19 | 同 / HF-009 | Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level. | LLM+floor(comparison) | **軽微(ユーザー決定2026-10-03)**(旧: 重大(境界)) | **7/13**(+STAGE4 5)(旧基準の参考値。新判定=軽微のため見逃しには数えない) |
| K20 | safety_A4 / HC-006 | The idea was practical: when AI struggled, a person could help. | LLMのみ | **重大**(境界) | 0/5(見逃し0) |
| K21 | 同 / HC-006 | 上の文+Keeping a human in reserve seemed safer than leaving everything to AI. | LLMのみ | **重大**(境界) | 0/5(見逃し0) |
| K22 | 同 / HC-006 | when AI struggled, a person could help | LLMのみ | **重大**(境界) | 0/5(見逃し0) |
| K23 | 同 / HC-012 | An AI called. That was what people thought as they spoke. | LLMのみ | 問題なし | 0/5 |

## 2. 集計

### 2-1. 全23種類

| 項目 | 種類数 | 内訳(種類) |
|---|---|---|
| 過剰品質(旧判定BLOCKINGだが新判定が軽微または問題なし) | **18/23**(2026-10-03 K19を軽微へ更新。旧: 17/23) | 軽微9+問題なし9(旧: 軽微8+問題なし9) |
| 真の重大見逃し(新判定が重大、かつ内容として見逃し1実行以上) | **0/23**(旧: 1/23[K19、7実行]。K19は軽微へ更新) | なし |
| 軽微 | **9/23**(旧: 8/23) | K02, K03, K04, K05, K06, K07, K11, K17, K19 |
| 問題なし | **9/23** | K01, K08, K09, K10, K12, K13, K14, K15, K23 |
| 新判定が重大(合計) | 5/23(旧: 6/23) | K16, K18, K20, K21, K22 |
| 新判定が重大だが見逃し0 | 5/23(重大5=すべて見逃し0) | K16, K20, K21, K22(見逃し0)+K18(字面は4実行だが、同内容の英語の文は検出済みで、日本語文が日本語を直さない方針で残る型) |

- 重大(5)+軽微(9)+問題なし(9)=23。過剰品質18=旧判定BLOCKING23−重大5。(旧: 重大6+軽微8+問題なし9、過剰品質17)
- K18を字面どおり(日本語文が元のまま残った実行数)で数えると、真の重大見逃しは1種類(K18。旧: K18・K19の2種類)。内容として見逃された重大は0(旧: K19のみ)(K18の根拠は種類別の節参照)。
- 過剰品質17種類のうち、LLM判定自体はACCEPTABLE/QUALITYなのにfloor(決定論)だけがBLOCKINGへ引き上げたのは8種類(K08, K09, K11, K12, K13, K14, K15, K17)。LLM判定がBLOCKINGで過剰だったのは9種類(K01, K02, K03, K04, K05, K06, K07, K10, K23)。floorは変更しない方針(Fable案、ユーザー指示)のため事実の記録のみ。

### 2-2. ユーザーの「20」への対応づけ(一意には決まらない)

ユーザーは「残り18種類」「/20」と書いたが、23種類との対応づけは次の2案があり、**どちらも「例1・例2を含め20、残り18」を同時には満たさない**ため一意に決まらない。Fable判断を仰ぐ。

- **対応案A(数が「20」に一致)**: 23種類から、同じ文の入れ子であるK20・K21・K22(safety_A4、同一箇所)を除いた20種類。例1=K04、例2=K10を含み、残り18種類=K01〜K03、K05〜K09、K11〜K19、K23。

  | 項目 | 値 |
  |---|---|
  | 過剰品質 | **18/20**(旧: 17/20) |
  | 真の重大見逃し | **0/20**(旧: 1/20[K19]。字面どおり数えるとK18のみ1/20、旧: 2/20) |
  | 軽微 | **9/20**(旧: 8/20) |
  | 問題なし | **9/20** |
  | 重大だが見逃し0 | 2/20(K16、K18[内容は検出済み]) |

- **対応案B(数が「18」に一致)**: 見逃しが1実行以上あった種類(委任_46 B-2の`kinds_with_qualifying`=18)。K16、K20〜K23を除く18種類で、例1・例2もここに含まれる(残りは16種類)。

  | 項目 | 値 |
  |---|---|
  | 過剰品質 | **17/18**(旧: 16/18) |
  | 真の重大見逃し | **0/18**(旧: 1/18[K19]。字面どおりならK18のみ1/18、旧: 2/18) |
  | 軽微 | **9/18**(K02〜K07、K11、K17、K19。旧: 8/18) |
  | 問題なし | **8/18**(K01、K08、K09、K10、K12〜K15) |

### 2-3. 感度(境界の判断が結果へ与える影響、全23種類ベース)

| 条件 | 真の重大見逃し |
|---|---|
| 本書の分類(基準、2026-10-03ユーザー決定でK19=軽微に更新済み) | 0種類(旧基準: 1種類[K19]) |
| (旧)K19を軽微とする見方 | 0種類(ユーザー決定により、この見方が正式な判定になった) |
| K05〜K07を重大とする見方(単数→複数形を(1)数量の変更として字面どおり当てる) | 3種類(K05・K06・K07[各9実行]。K19は軽微に更新済み。旧: 4種類[K19を含む])。K05・K06・K07は同じ文の入れ子で実質1箇所 |
| K18を字面どおり数える | 1種類(K18。旧: 2種類[K18、K19]) |
| K20〜K22を軽微とする見方(Stage 2 production rubricの「動機の帰属=QUALITY」) | 見逃し数は変わらない(いずれも見逃し0)。過剰品質が17→20に増える |

## 3. 種類ごとの再分類


### K01  bgroup_B4 / MUSE-HC-006  → 新判定: **問題なし**((ii)場面描写・導入(hook))

- **原文**(逐語、英語記事): `A call came from an AI agent. That was what it seemed. But while the conversation continued, the voice on the other end was not AI. It was a person.`
  - 前後(参考): 直前「Ring, ring…」、直後「Meta had run a test that produced exactly this kind of surprise. … in some calls made through Muse, trained human contract workers …」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=bgroup_B4):
  ```
[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 P2aは同じfact別箇所が先に指摘済みの型。
- **新判定**: 問題なし。線引きの項目: (ii)場面描写・導入(hook)
- **新判定の理由**: 冒頭の場面描写。「AIだと思った電話の相手が人だった」は、HC-006(一部の電話を訓練を受けた人間の契約スタッフが担当)から自然に導けるhook演出(設計書§0-2「確認済みFactから自然に導けるHook演出」)。数値・当事者・時期・出来事を新たに加えておらず、直後に「in some calls」でscopeが付く。
- **本当に重大な誤解になるか**: ならない。読者が信じても「一部の電話は人が担当した」という事実と同じ理解になる。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 5実行中、元のまま残り・未指摘・解消=2実行(残るが指摘あり=0、残るがSTAGE4=0)

### K02  hormuz_run03_standard / HF-009  → 新判定: **軽微**((b)対象の一般化(Brent原油先物→oil prices))

- **原文**(逐語、英語記事): `Oil prices moved briefly, then returned to a high level.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=hormuz_run03_standard):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
- **旧判定**: P2a行×3(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 同じ文が3行(複数run/cycle)。
- **新判定**: 軽微。線引きの項目: (b)対象の一般化(Brent原油先物→oil prices)
- **新判定の理由**: 値動きの内容(一時的に上げ幅が縮小した後、高い水準へ戻った)はHF-009と一致し、notes_for_writer(「撤回後に原油価格が全面的に下落したとは書かない」)にも反しない。違いは「Brent先物」が「oil prices」に一般化されている点のみ。設計書§0-2/§7-0-iter27は「原則許容候補」(BLOCKしない)としており、Fable案の区分では(b)=軽微に当たる。
- **本当に重大な誤解になるか**: ならない。国際指標の動きを「原油価格」と読んでも核心(一時縮小→高水準へ戻った)は変わらない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=16実行(残るが指摘あり=2、残るがSTAGE4=2)

### K03  hormuz_run03_standard / HF-009  → 新判定: **軽微**((b)対象の一般化(Brent→oil prices))

- **原文**(逐語、英語記事): `The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=hormuz_run03_standard):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。
- **新判定**: 軽微。線引きの項目: (b)対象の一般化(Brent→oil prices)
- **新判定の理由**: K02と同じ一般化。「as tensions … continued」の因果接続は、HF-009が`causal_strength: CAUSAL_STATED_BY_SOURCE`かつ`conditions`に米・イラン間の攻撃・海上封鎖・タンカー懸念の継続を明記しており、Ledgerと同じ方向で矛盾しない。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=16実行(残るが指摘あり=0、残るがSTAGE4=2)

### K04  meta_run03_standard / MUSE-HC-010  → 新判定: **軽微**((a)条件→発生(ユーザー決定の例1))

- **原文**(逐語、英語記事): `some calls needed user information to continue.`
  - 前後(参考): 直前「They did not realize it. That was happening behind the scenes.」、直後「That information might accidentally be shared with contract workers at a call center. Meta employees pointed this out inside the company as a privacy concern.」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-010: Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。
  scope: 人間の契約スタッフがMuse経由の電話を担当するテスト
  conditions: 電話の遂行にユーザー情報が必要となる場合
  date_or_period: 2026年9月中旬〜2026年9月22日
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 懸念の存在を示す事実。実際の大規模な情報漏えいが発生したと断定しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×4(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 floorは発動せず、`FLOOR_FLAGS`(actor/number/negation/comparison/time)にも該当しない。設計書の正解ラベルはMeta-1(Safety-critical、BLOCKING維持)。
- **新判定**: 軽微。線引きの項目: (a)条件→発生(ユーザー決定の例1)
- **新判定の理由**: ユーザー決定(2026-10-03)で「重大ではない。軽微な品質問題として許容」と確定した例1そのもの。条件(電話の遂行にユーザー情報が必要となる場合)を「some calls needed」と発生の形で書いているが、核心の主張(情報が契約スタッフへ共有されうる)は直後の「might」で留保され、懸念の主体もMeta従業員のまま。
- **本当に重大な誤解になるか**: ならない(ユーザー決定)。読者が信じても「一部の電話でユーザー情報が必要になった」程度で、情報漏えいの発生とは受け取らない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=5実行(残るが指摘あり=1、残るがSTAGE4=2)

### K05  meta_run03_standard / MUSE-HC-011  → 新判定: **軽微**((c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる))

- **原文**(逐語、英語記事): `human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.`
  - 前後(参考): 直前「News reports also cited one employee’s report.」、直後「However, this is only one report. It would be wrong to say all contract workers did this.」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-011: Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。
  scope: インターネット・ケーブル料金交渉の1件として報道された事例
  conditions: 人間の契約スタッフが電話を担当したケース
  numeric_value: 1件の従業員報告 (numeric_scope: 報道で紹介された個別事例)
  date_or_period: 2026年9月時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 従業員の報告として記録する。契約スタッフ全体の行動や実験全体の性質へ一般化しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×2(LLM判定=BLOCKING, floor=floor:changed_number)。LLM判定もBLOCKING、かつfloorも発動(二重)。 floor=changed_number(Ledgerの`numeric_value`が「1件の従業員報告」で、記事が複数形「calls」)。
- **新判定**: 軽微。線引きの項目: (c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる)
- **新判定の理由**: HC-011の`numeric_value`は「1件の従業員報告」。記事は「one employee’s report」「only one report」「It would be wrong to say all contract workers did this」と、件数・帰属・非一般化(notes_for_writer)をすべて保っている。「during calls」「These calls」の複数形だけが、Ledgerの「1件の事例」より粗い。Fable案(1)「数量の変更」を字面どおり当てると重大になりうるが、同じ段落で報告が1件と固定されているため核心は保たれると判断した(境界)。
- **本当に重大な誤解になるか**: ならない可能性が高い。読者が「複数の通話があった」と読んでも、直後に「報告は1件のみ・契約スタッフ全体へ一般化しない」と明記されている。ただし「1件の通話」→「複数の通話」の差は残る(境界、Fable判断)。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=9実行(残るが指摘あり=0、残るがSTAGE4=2)

### K06  meta_run03_standard / MUSE-HC-011  → 新判定: **軽微**((c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる))

- **原文**(逐語、英語記事): `It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.`
  - 前後(参考): 直前「News reports also cited one employee’s report.」、直後「However, this is only one report. It would be wrong to say all contract workers did this.」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-011: Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。
  scope: インターネット・ケーブル料金交渉の1件として報道された事例
  conditions: 人間の契約スタッフが電話を担当したケース
  numeric_value: 1件の従業員報告 (numeric_scope: 報道で紹介された個別事例)
  date_or_period: 2026年9月時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 従業員の報告として記録する。契約スタッフ全体の行動や実験全体の性質へ一般化しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×2(LLM判定=BLOCKING, floor=floor:changed_number)。LLM判定もBLOCKING、かつfloorも発動(二重)。 floor=changed_number(Ledgerの`numeric_value`が「1件の従業員報告」で、記事が複数形「calls」)。(文頭に「It said」が付く型)
- **新判定**: 軽微。線引きの項目: (c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる)
- **新判定の理由**: HC-011の`numeric_value`は「1件の従業員報告」。記事は「one employee’s report」「only one report」「It would be wrong to say all contract workers did this」と、件数・帰属・非一般化(notes_for_writer)をすべて保っている。「during calls」「These calls」の複数形だけが、Ledgerの「1件の事例」より粗い。Fable案(1)「数量の変更」を字面どおり当てると重大になりうるが、同じ段落で報告が1件と固定されているため核心は保たれると判断した(境界)。
- **本当に重大な誤解になるか**: ならない可能性が高い。読者が「複数の通話があった」と読んでも、直後に「報告は1件のみ・契約スタッフ全体へ一般化しない」と明記されている。ただし「1件の通話」→「複数の通話」の差は残る(境界、Fable判断)。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=9実行(残るが指摘あり=0、残るがSTAGE4=2)

### K07  meta_run03_standard / MUSE-HC-011  → 新判定: **軽微**((c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる))

- **原文**(逐語、英語記事): `These calls were about trying to lower internet or cable fees.`
  - 前後(参考): 直前「News reports also cited one employee’s report.」、直後「However, this is only one report. It would be wrong to say all contract workers did this.」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-011: Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。
  scope: インターネット・ケーブル料金交渉の1件として報道された事例
  conditions: 人間の契約スタッフが電話を担当したケース
  numeric_value: 1件の従業員報告 (numeric_scope: 報道で紹介された個別事例)
  date_or_period: 2026年9月時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 従業員の報告として記録する。契約スタッフ全体の行動や実験全体の性質へ一般化しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×1(LLM判定=BLOCKING, floor=floor:changed_number)。LLM判定もBLOCKING、かつfloorも発動(二重)。 floor=changed_number(Ledgerの`numeric_value`が「1件の従業員報告」で、記事が複数形「calls」)。(後半の文のみ)
- **新判定**: 軽微。線引きの項目: (c)語句の粗さ(境界あり: (1)数量の単数→複数形に当たるかの判断が分かれる)
- **新判定の理由**: HC-011の`numeric_value`は「1件の従業員報告」。記事は「one employee’s report」「only one report」「It would be wrong to say all contract workers did this」と、件数・帰属・非一般化(notes_for_writer)をすべて保っている。「during calls」「These calls」の複数形だけが、Ledgerの「1件の事例」より粗い。Fable案(1)「数量の変更」を字面どおり当てると重大になりうるが、同じ段落で報告が1件と固定されているため核心は保たれると判断した(境界)。
- **本当に重大な誤解になるか**: ならない可能性が高い。読者が「複数の通話があった」と読んでも、直後に「報告は1件のみ・契約スタッフ全体へ一般化しない」と明記されている。ただし「1件の通話」→「複数の通話」の差は残る(境界、Fable判断)。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=9実行(残るが指摘あり=2、残るがSTAGE4=2)

### K08  meta_run03_standard / MUSE-HC-012  → 新判定: **問題なし**((iii)同義の言い換え/(i)Ledgerから導かれる状況)

- **原文**(逐語、英語記事): `But sometimes, a human was speaking instead.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=ACCEPTABLE, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=ACCEPTABLE)。
- **新判定**: 問題なし。線引きの項目: (iii)同義の言い換え/(i)Ledgerから導かれる状況
- **新判定の理由**: HC-006(一部の電話を人間の契約スタッフが担当)・HC-012(開示なし)から導かれる状況の描写。主体は「a human」で、新しい人物・数値・出来事はない。LLM判定(ACCEPTABLE)と一致。floorの発動は主体の言い換えへの機械的な反応と考えられる。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=15実行(残るが指摘あり=0、残るがSTAGE4=7)

### K09  meta_run03_standard / MUSE-HC-012  → 新判定: **問題なし**((i)開示がなかったことから導かれる推論)

- **原文**(逐語、英語記事): `The problem was telling users who was speaking.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=QUALITY, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=QUALITY)。
- **新判定**: 問題なし。線引きの項目: (i)開示がなかったことから導かれる推論
- **新判定の理由**: 「問題は、誰が話しているかを利用者に伝えることだった」は、HC-012(適切な開示なしでテストを開始、ミスと認めた)から直接導かれる要約。新しい具体的事実を加えない。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=15実行(残るが指摘あり=0、残るがSTAGE4=7)

### K10  meta_run03_standard / MUSE-HC-012  → 新判定: **問題なし**((i)開示がなかったことから導かれる利用者の認識の推論(ユーザー決定の例2))

- **原文**(逐語、英語記事): `They enjoyed AI’s convenience, but a human was on the other end.`
  - 前後(参考): 直前「They could not tell if it was AI or a person.」、直後「They did not realize it.」(英語記事本文)。ユーザー決定の例2は、この文と直後の「They did not realize it.」の2文を1組にしたもの。K10の原文は前半の文のみ。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=meta_run03_standard):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 P2a。
- **新判定**: 問題なし。線引きの項目: (i)開示がなかったことから導かれる利用者の認識の推論(ユーザー決定の例2)
- **新判定の理由**: ユーザー決定(2026-10-03)で「問題なしとして許容」と確定した例2の前半。開示がなかったというLedger事実から、利用者の状態・認識を推論した描写で、新しい具体的事実を加えていない。
- **本当に重大な誤解になるか**: ならない(ユーザー決定)。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 23実行中、元のまま残り・未指摘・解消=13実行(残るが指摘あり=2、残るがSTAGE4=3)

### K11  neg1_meta_b3prod_a2 / MUSE-HC-012  → 新判定: **軽微**((b)対象の一般化(副社長→executive)+(iii)同義の言い換え(適切な開示なし→without clearly telling users))

- **原文**(逐語、英語記事): `A Meta executive admitted the mistake. The test had begun without clearly telling users.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg1_meta_b3prod_a2):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×1(LLM判定=ACCEPTABLE, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=ACCEPTABLE)。委任_46は「列挙された複製claimへのfloor波及」と判定(委任_35で是正済みと設計書に記載、是正後は未再測定)。
- **新判定**: 軽微。線引きの項目: (b)対象の一般化(副社長→executive)+(iii)同義の言い換え(適切な開示なし→without clearly telling users)
- **新判定の理由**: 「副社長→executive」はA5-1型(設計書§7-0-iter29がQUALITYと再ラベル)と同型の役職の一般化。「without clearly telling users」は「適切な開示なし」の言い換えで、Ledgerは開示対象を限定していない。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 22実行中、元のまま残り・未指摘・解消=19実行(残るが指摘あり=0、残るがSTAGE4=2)

### K12  neg1_meta_b3prod_a2 / MUSE-HC-012  → 新判定: **問題なし**((i)推論(「might」の条件付き一般論))

- **原文**(逐語、英語記事): `A user might think the exchange was with AI, even though a person was involved.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg1_meta_b3prod_a2):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×1(LLM判定=QUALITY, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=QUALITY)。K11と同じ列挙波及。
- **新判定**: 問題なし。線引きの項目: (i)推論(「might」の条件付き一般論)
- **新判定の理由**: 「A user might think the exchange was with AI, even though a person was involved.」は留保付きの一般的な推論で、新しい具体的事実・数値・主体を加えない。HC-012(開示なし)から自然に導かれる。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 22実行中、元のまま残り・未指摘・解消=19実行(残るが指摘あり=0、残るがSTAGE4=2)

### K13  neg1_meta_b3prod_a2 / MUSE-HC-012  → 新判定: **問題なし**((iii)同義の言い換え)

- **原文**(逐語、英語記事): `The test began without clearly telling users that contract workers would make the calls.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg1_meta_b3prod_a2):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2b行×1(LLM判定=ACCEPTABLE, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=ACCEPTABLE)。K11と同じ列挙波及。
- **新判定**: 問題なし。線引きの項目: (iii)同義の言い換え
- **新判定の理由**: HC-012のconditions「適切な開示なしで契約スタッフが電話を担当していたテスト」とほぼ同義。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 22実行中、元のまま残り・未指摘・解消=19実行(残るが指摘あり=0、残るがSTAGE4=2)

### K14  neg3_hormuz_prodrunner_b1b / HF-003  → 新判定: **問題なし**((iii)同義の言い換え(日本語文))

- **原文**(逐語、日本語記事): `トランプ氏は、アメリカがホルムズ海峡の安全確保に使う費用について、海峡を通るすべての貨物に二割の償還を求めると投稿した。`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg3_hormuz_prodrunner_b1b):
  ```
[VERIFIED] HF-002: ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。
  scope: ホルムズ海峡を通じて輸送される「すべての貨物」
  conditions: 米国が海峡の安全と警備を提供するための費用の償還として提示。投稿は手続きと体制づくりを直ちに開始するとした。
  numeric_value: 20% (numeric_scope: 投稿上の償還率。課税標準または算定基礎は明記されていない。)
  date_or_period: 2026-07-13 10:16 EDT
  notes_for_writer: 7月13日の提案が先で、7月14日の撤回・置換が後。7月14日の出来事を7月13日の価格上昇の原因として扱わない。
  ```
  ```
[VERIFIED] HF-003: 7月13日の20％償還料の投稿および同日の発言では、徴収主体、支払義務者、評価方法、徴収通貨、免除、執行方法、法的根拠などの具体的制度設計は示されなかった。
  scope: ホルムズ海峡の貨物通航に対する米国の償還料案
  numeric_value: 20% (numeric_scope: 提案された率のみが示され、算定・徴収方法は未提示)
  date_or_period: 2026-07-13
  notes_for_writer: 「米国が20％通航料を導入した」と確定形で書かず、「提案した」「徴収方針を表明した」とする。
  ```
- **旧判定**: P2a行×1(LLM判定=ACCEPTABLE, floor=floor:changed_actor)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_actor(LLM判定=ACCEPTABLE)。日本語文のclaim。
- **新判定**: 問題なし。線引きの項目: (iii)同義の言い換え(日本語文)
- **新判定の理由**: HF-002は「トランプ大統領は…同海峡を通るすべての貨物に20％の率で償還を求めると投稿した」。原文は主体(トランプ氏)・対象(すべての貨物)・率(二割)・動詞(投稿した)ともHF-002と一致し、notes_for_writer(HF-003「提案した」「表明した」とする)にも沿う。floorの発動は誤発火と考えられる。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 15実行中、元のまま残り・未指摘・解消=11実行(残るが指摘あり=1、残るがSTAGE4=3)

### K15  neg3_hormuz_prodrunner_b1b / HF-009  → 新判定: **問題なし**((iii)同義の言い換え)

- **原文**(逐語、英語記事): `During that period, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg3_hormuz_prodrunner_b1b):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
- **旧判定**: P2b行×1(LLM判定=ACCEPTABLE, floor=floor:changed_time)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_time(LLM判定=ACCEPTABLE)。
- **新判定**: 問題なし。線引きの項目: (iii)同義の言い換え
- **新判定の理由**: HF-009のconditionsに「米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた」とあり、記事の文はその言い換え。「During that period」は直前の「at the time of publication」の流れでLedgerのdate_or_period(撤回発表後の取引時間中)を指す。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 15実行中、元のまま残り・未指摘・解消=7実行(残るが指摘あり=1、残るがSTAGE4=3)

### K16  neg3_hormuz_prodrunner_b1b / HF-009  → 新判定: **重大**((4)時期の変更(設計書§0-2 BLOCK候補「継続していた出来事→一度消えて戻った出来事」に明示的に該当))

- **原文**(逐語、英語記事): `The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.`
  - 前後(参考): 「## In one line」の要約行(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg3_hormuz_prodrunner_b1b):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
- **旧判定**: P2b行×1(LLM判定=BLOCKING, floor=floor:changed_time)。LLM判定もBLOCKING、かつfloorも発動(二重)。 floor=changed_time。
- **新判定**: 重大。線引きの項目: (4)時期の変更(設計書§0-2 BLOCK候補「継続していた出来事→一度消えて戻った出来事」に明示的に該当)
- **新判定の理由**: HF-009のconditionsは、撤回発表以外にも米・イラン間の攻撃・海上封鎖・タンカー懸念が「継続していた」と記す。記事は「the events driving oil prices … quickly returned」と、出来事が一度消えて戻ったように書いている。Ledgerの時間経過(継続)と異なる。
- **本当に重大な誤解になるか**: 中程度。地政学的な緊張が一度収まり再燃したと誤解させうる(要約行のため目に留まりやすい)。ただし記事全体の主題(料金案は退場、原油高は居残り)は保たれる。
- **見逃しの有無**(新判定が重大): 同instance 15実行中、元のまま残り・未指摘・解消=0実行(残るが指摘あり=1、残るがSTAGE4=0)。見逃し0(`n_qualifying`=0): 同instance全15実行で、元のまま残った場合は常にBLOCKINGで指摘されている。

### K17  neg3_hormuz_prodrunner_b1b / HF-009  → 新判定: **軽微**((c)語句の粗さ(確定した事実を「may」で弱めた一般論))

- **原文**(逐語、英語記事): `The fee plan may be replaced, but events continuing at the same time do not simply disappear backstage because of one announcement.`
  - 前後(参考): 「The lesson is that …」に続くまとめの文(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=neg3_hormuz_prodrunner_b1b):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
- **旧判定**: P2b行×1(LLM判定=QUALITY, floor=floor:changed_time)。LLM判定はBLOCKINGではないが、決定論floorがBLOCKINGへ引き上げた(floor起因)。 floor=changed_time(LLM判定=QUALITY)。
- **新判定**: 軽微。線引きの項目: (c)語句の粗さ(確定した事実を「may」で弱めた一般論)
- **新判定の理由**: 「The fee plan may be replaced」は、Ledger(HF-007)で確定している置換の発表を、教訓としての一般論の形で「may」と弱めた言い回し。後半「events continuing at the same time do not simply disappear」は、継続を述べておりHF-009のconditionsと一致する。新しい事実の追加はなく、言い回しの精度が落ちている程度。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 15実行中、元のまま残り・未指摘・解消=7実行(残るが指摘あり=1、残るがSTAGE4=3)

### K18  safety_A2A3 / HF-003  → 新判定: **重大**((2)当事者の特定(Ledgerが「支払義務者は未提示」とする点を特定)/(6)Ledgerに無い具体的事実。既存のStage 2 rubric V6が「貨物を運ぶ側が支払う」を例示してBLOCKINGと明記済み、Safety-critical A2A3-0に対応)

- **原文**(逐語、日本語記事): `アメリカが海峡の安全を守るために使う費用を、貨物を運ぶ側に返してもらうという考えです。`
  - 前後(参考): 日本語記事の1文。英語記事の対応文は「The idea was that those carrying the cargo would repay the money the United States spends to keep the strait safe.」(Safety-critical A2A3-0、`SAFETY_CRITICAL_CLAIM_DEFS`の「repay the money」)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A2A3):
  ```
[VERIFIED] HF-002: ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。
  scope: ホルムズ海峡を通じて輸送される「すべての貨物」
  conditions: 米国が海峡の安全と警備を提供するための費用の償還として提示。投稿は手続きと体制づくりを直ちに開始するとした。
  numeric_value: 20% (numeric_scope: 投稿上の償還率。課税標準または算定基礎は明記されていない。)
  date_or_period: 2026-07-13 10:16 EDT
  notes_for_writer: 7月13日の提案が先で、7月14日の撤回・置換が後。7月14日の出来事を7月13日の価格上昇の原因として扱わない。
  ```
  ```
[VERIFIED] HF-003: 7月13日の20％償還料の投稿および同日の発言では、徴収主体、支払義務者、評価方法、徴収通貨、免除、執行方法、法的根拠などの具体的制度設計は示されなかった。
  scope: ホルムズ海峡の貨物通航に対する米国の償還料案
  numeric_value: 20% (numeric_scope: 提案された率のみが示され、算定・徴収方法は未提示)
  date_or_period: 2026-07-13
  notes_for_writer: 「米国が20％通航料を導入した」と確定形で書かず、「提案した」「徴収方針を表明した」とする。
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=floor:changed_actor); P2a行×1(LLM判定=BLOCKING, floor=なし)。LLM判定もBLOCKING、かつfloorも発動(二重)。(2行のうち1行はfloor=changed_actor併発、もう1行はLLMのみ)。日本語文のclaim(origin=ja_source)。
- **新判定**: 重大。線引きの項目: (2)当事者の特定(Ledgerが「支払義務者は未提示」とする点を特定)/(6)Ledgerに無い具体的事実。既存のStage 2 rubric V6が「貨物を運ぶ側が支払う」を例示してBLOCKINGと明記済み、Safety-critical A2A3-0に対応
- **新判定の理由**: HF-003は「徴収主体、支払義務者…は示されなかった」と記す。文は「貨物を運ぶ側に返してもらう」と支払う側を特定している。HF-002(すべての貨物に償還を求める)から読み取れる範囲ではあるが、Ledgerが明示的に未提示としている点を埋めており、既存の設計書V6 rubricの例示そのもの。
- **本当に重大な誤解になるか**: 小〜中。「貨物を運ぶ側が払う」は素直な読みと近く、実害は大きくないが、Ledgerが禁じる具体化に当たる。
- **見逃しの有無**(新判定が重大): 同instance 13実行中、元のまま残り・未指摘・解消=4実行(残るが指摘あり=0、残るがSTAGE4=3)。字面どおりの数: 4実行(iter8 s2、rep9 s1、rep10 s1、rep10 s2)で日本語文が元のまま未指摘のまま解消。ただし、これは日本語側の文の話であり、同じ内容の英語の文(A2A3-0)は、全13実行のcycle 1でBLOCKING指摘されている(iter8 s2のみStage 2がQUALITYへ降格=V6是正前。rep9以降は全てBLOCKING)。内容として見逃されたのではなく、日本語本文は修正しない方針(ユーザー判断2026-10-03§3)のもとで残る型。このため「真の重大見逃し」には数えない(字面どおりに数えると2種類)。

### K19  safety_A2A3 / HF-009  → 新判定: **軽微(ユーザー決定2026-10-03、委任_55で更新)**。旧: 重大(境界)。以下の旧判定文は残す: **重大**((4)比較・方向の変更(設計書§0-2 BLOCK候補「上昇→下落(方向反転)」)/(5)notes_for_writerが示す観測範囲を超える)

- **原文**(逐語、英語記事): `Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level.`
  - 前後(参考): 直前「But the market reacted differently.」、直後「Soon, however, they returned to a high level.」(英語記事本文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A2A3):
  ```
[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
  scope: 国際指標Brent原油先物の短時間の値動き
  conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
  numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
  date_or_period: 2026-07-14、撤回発表後の取引時間中
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。
  ```
  ```
[VERIFIED] HF-011: Brent原油先物は7月14日に1.43ドル、1.7％上昇し、1バレル84.73ドルで清算された。これは2営業日連続で6月12日以来の高い清算値だった。
  scope: Brent原油先物の当日清算値と前日比
  conditions: 20％償還料案は同日の取引時間中に撤回されたが、海上封鎖、米・イラン間の攻撃、タンカー被害などの供給懸念は継続していた。
  numeric_value: $84.73/バレル、前日比 +$1.43、+1.7% (numeric_scope: 7月14日のBrent原油先物清算値。日中高値ではない)
  date_or_period: 2026-07-14清算時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 7月14日は撤回があったにもかかわらず日次清算値は上昇した。これだけから撤回が価格を上昇させた、または下落させなかったと因果推論しない。
  ```
- **旧判定**: P2b行×1(LLM判定=BLOCKING, floor=floor:changed_comparison)。LLM判定もBLOCKING、かつfloorも発動(二重)。 floor=changed_comparison(`iter6 s1` cycle 2で1回のみ指摘)。設計書の正解(Production Checker現行出力のgold)でもMAJOR(changed_comparison)。
- **新判定**: 重大。線引きの項目: (4)比較・方向の変更(設計書§0-2 BLOCK候補「上昇→下落(方向反転)」)/(5)notes_for_writerが示す観測範囲を超える
- **新判定の理由**: HF-009は「Brent先物が一時的に上げ幅を縮小した」と記し、notes_for_writerは「観測されたのは一時的な上げ幅縮小と、その後の回復」と指定。HF-011ではBrentは7月14日に1.7％上昇して清算された。記事の「prices began to fall」は、上昇が続く中の上げ幅縮小を、価格そのものの下落へ変えている。
- **本当に重大な誤解になるか**: 中程度。「撤回後に原油価格が下がり始めた」と読ませる。市場の方向を誤認させうるが、直後に「soon returned to a high level」と続くため、全体の主張(高値に戻った)は変わらない。判断が分かれる境界(軽微とする見方もありうる)。
- **見逃しの有無**(新判定が重大): 同instance 13実行中、元のまま残り・未指摘・解消=7実行(残るが指摘あり=0、残るがSTAGE4=5)。7実行(iter5 s1/s2、iter6 s2、iter8 s2、rep9 s1、rep10 s1/s2)で文が元のまま残り、一度もBLOCKINGで指摘されず、人間確認なしで解消。これ以外に、STAGE4行きで人間確認になった5実行がある。

### K20  safety_A4 / MUSE-HC-006  → 新判定: **重大**((4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり)

- **原文**(逐語、英語記事): `The idea was practical: when AI struggled, a person could help.`
  - 前後(参考): K20=前半の1文のみ、K21=前半+「Keeping a human in reserve seemed safer than leaving everything to AI.」、K22=前半の節のみ(入れ子の3種類、同一箇所)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A4):
  ```
[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
  ```
[VERIFIED] MUSE-HC-013: Metaの広報担当者Daniel Robertsは、従業員の反応は「圧倒的に肯定的」だったと述べ、テストの目的を、安全・プライバシー保護を実装し、公開前に機能を改善するためのフィードバック収集だと説明した。
  scope: Meta従業員を対象とした人間コンシェルジュ機能のテスト
  conditions: Meta広報担当者によるReutersへの説明
  date_or_period: 2026年9月22日
  notes_for_writer: Meta広報担当者の説明として記録する。客観的なユーザー満足度の測定値とは扱わない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 入れ子3種類の同一箇所。
- **新判定**: 重大。線引きの項目: (4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり
- **新判定の理由**: HC-006は「一部の電話を、AIではなく訓練を受けた人間の契約スタッフが担当した」ことを記すだけで、「AIが苦戦したとき人が助ける」という設計の意図は無い(HC-013は、テストの目的を安全・プライバシー保護の実装と改善のためのフィードバック収集と説明)。記事はMetaの設計の動機と、「人を控えに置くほうが安全に思えた」という判断を追加している。設計書のB4-a(AIフォールバック機構の新規主張)と同型。
- **本当に重大な誤解になるか**: 中程度。「MetaはAIが苦戦する場面の保険として人を置いた」と読ませる(実際の目的はフィードバック収集)。ただし「seemed」と留保があり、核心の事実(一部の電話を人が担当)は保たれる。判断が分かれる境界(現行のStage 2 production rubricは「動機の帰属」をQUALITYとしており、§0-2/B4-aと食い違う)。
- **見逃しの有無**(新判定が重大): 同instance 5実行中、元のまま残り・未指摘・解消=0実行(残るが指摘あり=1、残るがSTAGE4=1)。見逃し0(`n_qualifying`=0): 同instance全5実行で、文が元のまま残った場合は常にBLOCKINGで指摘されている。

### K21  safety_A4 / MUSE-HC-006  → 新判定: **重大**((4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり)

- **原文**(逐語、英語記事): `The idea was practical: when AI struggled, a person could help. Keeping a human in reserve seemed safer than leaving everything to AI.`
  - 前後(参考): 同一箇所(K20/K21/K22は入れ子の3種類)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A4):
  ```
[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
  ```
[VERIFIED] MUSE-HC-013: Metaの広報担当者Daniel Robertsは、従業員の反応は「圧倒的に肯定的」だったと述べ、テストの目的を、安全・プライバシー保護を実装し、公開前に機能を改善するためのフィードバック収集だと説明した。
  scope: Meta従業員を対象とした人間コンシェルジュ機能のテスト
  conditions: Meta広報担当者によるReutersへの説明
  date_or_period: 2026年9月22日
  notes_for_writer: Meta広報担当者の説明として記録する。客観的なユーザー満足度の測定値とは扱わない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×2(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 入れ子3種類の同一箇所。
- **新判定**: 重大。線引きの項目: (4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり
- **新判定の理由**: HC-006は「一部の電話を、AIではなく訓練を受けた人間の契約スタッフが担当した」ことを記すだけで、「AIが苦戦したとき人が助ける」という設計の意図は無い(HC-013は、テストの目的を安全・プライバシー保護の実装と改善のためのフィードバック収集と説明)。記事はMetaの設計の動機と、「人を控えに置くほうが安全に思えた」という判断を追加している。設計書のB4-a(AIフォールバック機構の新規主張)と同型。
- **本当に重大な誤解になるか**: 中程度。「MetaはAIが苦戦する場面の保険として人を置いた」と読ませる(実際の目的はフィードバック収集)。ただし「seemed」と留保があり、核心の事実(一部の電話を人が担当)は保たれる。判断が分かれる境界(現行のStage 2 production rubricは「動機の帰属」をQUALITYとしており、§0-2/B4-aと食い違う)。
- **見逃しの有無**(新判定が重大): 同instance 5実行中、元のまま残り・未指摘・解消=0実行(残るが指摘あり=1、残るがSTAGE4=1)。見逃し0(`n_qualifying`=0): 同instance全5実行で、文が元のまま残った場合は常にBLOCKINGで指摘されている。

### K22  safety_A4 / MUSE-HC-006  → 新判定: **重大**((4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり)

- **原文**(逐語、英語記事): `when AI struggled, a person could help`
  - 前後(参考): 同一箇所(K20/K21/K22は入れ子の3種類)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A4):
  ```
[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
  ```
[VERIFIED] MUSE-HC-013: Metaの広報担当者Daniel Robertsは、従業員の反応は「圧倒的に肯定的」だったと述べ、テストの目的を、安全・プライバシー保護を実装し、公開前に機能を改善するためのフィードバック収集だと説明した。
  scope: Meta従業員を対象とした人間コンシェルジュ機能のテスト
  conditions: Meta広報担当者によるReutersへの説明
  date_or_period: 2026年9月22日
  notes_for_writer: Meta広報担当者の説明として記録する。客観的なユーザー満足度の測定値とは扱わない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×1(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 入れ子3種類の同一箇所。
- **新判定**: 重大。線引きの項目: (4)因果・動機の創作/(6)Ledgerに無い具体的事実(設計書B4-a「AIフォールバック機構の新規主張」=BLOCKING、§0-2「未確認の…動機の追加」に該当)。境界あり
- **新判定の理由**: HC-006は「一部の電話を、AIではなく訓練を受けた人間の契約スタッフが担当した」ことを記すだけで、「AIが苦戦したとき人が助ける」という設計の意図は無い(HC-013は、テストの目的を安全・プライバシー保護の実装と改善のためのフィードバック収集と説明)。記事はMetaの設計の動機と、「人を控えに置くほうが安全に思えた」という判断を追加している。設計書のB4-a(AIフォールバック機構の新規主張)と同型。
- **本当に重大な誤解になるか**: 中程度。「MetaはAIが苦戦する場面の保険として人を置いた」と読ませる(実際の目的はフィードバック収集)。ただし「seemed」と留保があり、核心の事実(一部の電話を人が担当)は保たれる。判断が分かれる境界(現行のStage 2 production rubricは「動機の帰属」をQUALITYとしており、§0-2/B4-aと食い違う)。
- **見逃しの有無**(新判定が重大): 同instance 5実行中、元のまま残り・未指摘・解消=0実行(残るが指摘あり=1、残るがSTAGE4=1)。見逃し0(`n_qualifying`=0): 同instance全5実行で、文が元のまま残った場合は常にBLOCKINGで指摘されている。

### K23  safety_A4 / MUSE-HC-012  → 新判定: **問題なし**((i)開示がなかったことから導かれる認識の推論(肯定形)/(ii)hook)

- **原文**(逐語、英語記事): `An AI called. That was what people thought as they spoke.`
  - 前後(参考): 英語記事の冒頭(タイトル直後の2文)。
- **Ledger上の事実**(Checkerが見たLedgerブロック、逐語。出所: `build_target_instances()`の`fixture['ledger_text']`、instance=safety_A4):
  ```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
  ```
- **旧判定**: P2a行×3(LLM判定=BLOCKING, floor=なし)。Stage 2のLLM判定だけでBLOCKING(floor不発動、`basis`はLedger条件・範囲との照合)。 3行。
- **新判定**: 問題なし。線引きの項目: (i)開示がなかったことから導かれる認識の推論(肯定形)/(ii)hook
- **新判定の理由**: 「AIから電話が来た、と話しているときは思っていた」は、HC-012(適切な開示なし)から導かれる利用者の認識の描写で、新しい具体的事実を加えない。ユーザー決定の例2(否定形)と同じ型の肯定形で、ユーザー決定で肯定形も問題なしとされた範囲(Fable案(i))に当たる。
- **本当に重大な誤解になるか**: ならない。
- **見逃しの有無**: 対象外(新判定が重大でない)。参考値(委任_46 B-2): 同instance 5実行中、元のまま残り・未指摘・解消=0実行(残るが指摘あり=1、残るがSTAGE4=0)

## 4. 真の重大見逃し(K19)の原因切り分け(ユーザー指示§2。記録の確認のみ、対策の設計はしない)

対象: `safety_A2A3`のK19「Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level.」(HF-009)。同instance13実行(iter5〜iter8、rep9、rep10、rep18。委任_44範囲の全実行)。確認方法: `er052_output/open233_self_recovery_flow_runner_01_*/instances_*/safety_A2A3.json`の各cycleの`stage2_results`、固定Stage 1出力`er051_output/open233_checker_trial_01/trial_02/step1/A2A3/V4A/run_1.json`の`claim_in_article`、fixtureの`baseline_parsed`。

| 問い | 結果 | 確認できたこと/推測 |
|---|---|---|
| 1周目で完全に見逃したのか | **はい(確認済み)** | 現行のinstance定義(`stage1_mode=reuse`)ではsafety_A2A3のStage 1は固定で(iter5〜7当時の定義は未確認)、V4A run_1の`claim_in_article`は「those carrying the cargo would repay…」(HF-003)と「with its distant danger reaching gasoline prices…」の2件のみ。K19は含まれず、13実行すべてのcycle 1でK19の指摘は0件。一方、fixtureの`baseline_parsed`(Production現行のChecker出力)はK19を`MAJOR`(`changed_comparison`)で指摘しているので、同じ文を検出できる検査は存在する。**現行定義どおりなら13実行のStage 1は同一の固定出力なので、cycle 1の見逃しは独立した13回ではなく、1つの出力の見逃しが13回再利用されたもの。** |
| 再検査(Recheck)で拾えたか | 文が残った再検査 約12回中1回のみ | 文が最終記事に残った実行の再検査回数(cycle数−1の合計=11)+iter6 s1 cycle 2(唯一の指摘、`detected_by=stage1_llm`)=約12回(推測を含む: 中間cycleの本文は記録されず、最終記事に残った実行は途中も残っていたと仮定)。指摘は1回(iter6 s1 cycle 2のみ)。 |
| MINORとして拾ったが後でMAJORになったのか | **確認不能** | 13実行はいずれも委任_49より前(MINOR記録の開始前)。MINORの記録が無いため、MINORで拾われていたかは分からない。 |
| Rewriteによって新たに発生したのか | **いいえ(確認済み)** | 日本語原文が起点(`origin=ja_source`、JA「料金案が消えた直後に、価格は下がりかけました」)で、cycle 1の記事本文に存在する。文が残った実行でRewriteされたのは別の箇所(HF-003・gasoline)。 |
| Checkerと判定役(Stage 2)で基準が食い違っているのか | **食い違いの証拠は無い** | Stage 2はCheckerが出力した主張だけを判定する。K19がCheckerから出た唯一の回(iter6 s1 cycle 2)では、Stage 2はLLM判定=BLOCKINGかつfloor(changed_comparison)でBLOCKINGと一致し、Rewriteされて解消した。見逃しは判定役の基準ではなく、Checker(検出)側で起きている。なお、iter8 s2はStage 1が出した2件がStage 2でQUALITYへ降格して`RESOLVED_STAGE2_DOWNGRADE`となったため、K19は検出も判定もされないまま合格した(V6是正前の挙動)。 |

- 要点: 原因は「Checkerの検出漏れ(recall)」。判定役の基準の食い違いでも、Rewriteによる新規発生でもない。同じ性質の問題は、既に委任_49で`meta_run03_standard`(HC-010)の見逃しとして記録済み(合格が1回の検査結果に依存する構造)。
- 対策はここでは設計しない(Fableが別途判断)。K19が真の重大見逃しに残るか(軽微とする見方がある)は、Fableの判断事項。
- **2026-10-03更新(委任_55)**: ユーザー決定により`Just after the charge plan disappeared, prices began to fall.`は軽微。K19は真の重大見逃しではない(旧: 重大(境界))。上記の原因切り分け表は記録として残す。

## 5. 限界・未確認

- 分類はFable案の文言の適用であり、境界の種類(K05〜K07、K16、K18、K19、K20〜K22)は判断が分かれる。感度は2-3節。
- 「見逃し」の数は機械照合(委任_46の方法)で、実際に重大だったかの数ではない。種類は入れ子があり、同じ文の複数種類は実質1箇所。
- 古い実行(iter5〜iter8)は現行のPrompt・floor・rubricと異なる(特に委任_33のV6、委任_35のfloor是正の前)ため、現在の挙動を表さない。
- 日本語2種類(K14、K18)の最終JA本文は、JAが変更されなかった実行では元記事と同じと推定(runnerはJA本文を変更時のみ記録)。
- 委任_46の対象は7記事の既知の実行に限られ、他の記事の見逃しは含まない。

- 委任_57(2026-10-03、Fable判断): 較正のA4-1(safety_A4、MUSE-HC-012「were actually speaking with human staff」ほか)は、例2およびK23と同型のため正解ラベルをACCEPTABLEへ修正(旧: BLOCKING Safety-critical)。Safety-critical登録は6件→5件。詳細は設計書§7-1付近(委任_57)。
