# PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01(準備段階、¥0、read-only+雛形作成)

管理ID: `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01`。実施日: 2026-09-12。
ユーザー承認原文(2026-09-12): 「Token効率 Phase 2について(A)提案通り実施します。
進めてください。」対象はOPEN_ITEMS.md OPEN-142行「Phase 2 Trial設計案」
(Before=Discovery Trial-11のOpus L2実測、After=Discovery Trial-12完了後の
Opus L2解釈をcontext packet+progressive disclosure方式で実施)。
**本タスクはTrial-12完了前の準備段階のみ**(Before基準確定・rubric固定・
雛形作成・手順書作成)。Trial-12生成物は読み取りのみで書き込みは行っていない。
Production採用・SSOT編集・Git操作・API支出・Opus起動は行っていない。

## 要点(5行)

1. **Before基準**: 実際の「Discovery Trial-11 Opus L2レビュー」本体は
   `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md`
   (25,234字、論点5件+Sonnet/Fable見落とし10件)が実在し、これを論点網羅性の
   一次資料として採用した。ただし本レビューのOpus実読込文字数は
   `er011_output/pm_agent_read_audit_01/`ではrotation失効により未計測
   (delegation文字数8,568字のみ判明)。定量比較(読込文字数)の代替として、
   ユーザー指示どおり`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`
   (Opus実測135,397字、22呼出、Read/Grep内訳あり)を代替Before値として採用し、
   T3報告の3V Phase1実測(約45.2万字)を参考列とする。
2. **必須論点チェックリスト**をユーザー指定10項目とTrial-11レビュー実際の
   論点構成を突合して固定した(3節)。Support/Key Phraseは今回のTrial-11
   レビューでは明示的に扱われていない論点であることを検出した(既知gapとして
   Afterのチェック対象に明記)。
3. **雛形** `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`(新規、
   SSOTではない、未記入状態2,637字)を作成した。(a)論点(限定)/(b)主要数値表・
   要点/(c)Production code該当行範囲のみ/(d)Sonnet要約/(e)progressive
   disclosure指示文/(f)自己計測欄、の6構成。
4. **After実行手順**(4節)をFable向けに固定した。Trial-12完了後、Sonnetが
   packetを生成→Fableがpacketのみをopus-consultantへ渡す→
   `er011_pm_agent_read_audit_01.py`で読込文字数を再集計→Before/After表を作成。
5. **Status**: 準備完了、closeout=**進行中(After待ち)**。STOP条件(5節)に
   該当する事象は本タスク中は発生していない。

---

## 1. Before基準の確定

### 1-1. 一次資料(質的基準): Trial-11 Opus L2レビュー本体

`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md`
(2026-09-10実施、25,234字)が実在し、全文を確認した。構成は以下のとおり:

- 要点(5行)
- 論点1: N=1×2テーマからの一般化における因果解釈の誤りリスク(対照アーム欠如、
  題材依存の交絡、REVIEW率逆行の見落とし)
- 論点2: B1B Ledger Deviation MAJOR 2件とLocal Rewriteの自動解消の妥当性
  (事実面は妥当だが、near-duplicate発生・scope混合・Rewrite後QA未通過・
  語数増分という副作用を指摘)
- 論点3: Fact Checker advisory 3件の重み(1件はstale、残り2件は人手修正推奨)
- 論点4: A2 294語の短さ(比較対象の取り違え、Point One tolerance超過、
  音声尺への影響推定)
- 論点5: 次のN増し設計への示唆(対照アーム必須、題材の型分散、規模目安、
  観測指標、避けるべき設計)
- Sonnet/Fableが見落としている可能性のある点(10項目: パイプライン順序の
  構造的blind spot、Evidence Compressionの数値逆転、B1B語数上限接近、
  A2 tolerance超過、2テーマの型の酷似、house phraseの再出現、音声上の重複、
  comparison.html未生成、保険文regexの検出範囲、既知gap再確認)

この実在レビューを**論点網羅性チェックの一次資料**として3節のrubricに用いる。

### 1-2. 定量基準(読込文字数比較用): 代替値の採用と制約の明記

Trial-11レビュー本体は実在するが、`er011_output/pm_agent_read_audit_01/
per_agent_task_summary.json`の`by_mgmt_id`には
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01`の
Opus実読込データが存在しない(Phase 1監査が明記した制約どおり、subagent
転記ファイルがrotationで失効しているため)。判明しているのはFableの
委任文(delegation)文字数8,568字のみ。

ユーザー指示(タスク文1)に従い、Before基準の定量値は以下の代替値を用いる:

| 項目 | `FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`(代替Before) | `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`(参考、別系統) | 3V Phase1(参考、`PM-TOKEN-EFFICIENCY-T3-CLAUDE-DEV-TOKEN-REASSESSMENT-01_REPORT.md`過去再掲) |
|---|---|---|---|
| Opus実読込文字数 | 135,397字 | 82,628字 | 約452,000字(コード8ファイル379,435字+Sonnet REPORT本文72,789字) |
| 概算token | 61,544 | 37,558 | 約205,000 |
| Read呼出回数 | 22(full 5・partial 8) | 27(full 7・partial 6) | 未内訳(全文ダンプ型) |
| 内訳(文字数) | report 73,388 / ssot_huge 34,862 / production_code 14,893 / other_md 10,101 / grep 15,451 | report 25,464 / trial_output 40,201 / production_code 14,569 / grep 7,301 | コード全文ダンプ型(REPORT横断参照が少ない) |
| Fable→Opus委任文字数 | 2,764字 | 5,838字 | 未計測 |
| タスク内重複(同一ファイル再読込) | 39,763字 | 16,075字 | 未計測 |

**制約の明記**: 上記代替値は「Discovery Trial-11 Opus L2レビュー」そのものの
実測ではなく、同時期・同系統(Discovery Focus Module検討)の別管理IDでの
Opus実測である。Trial-11本体の実際の入力規模とは異なる可能性があるため、
After比較時は「対象管理ID完全一致のBefore/After」ではなく「同系統タスクの
代表値としてのBefore/After」であることをFable報告時に明記すること
(過去再掲・代替値であることを隠さない)。

---

## 2. Opusレビュー品質rubric: 必須論点チェックリスト

ユーザー指定の観察10項目と、Trial-11レビュー実際の論点構成(1節)を突合した。

| # | ユーザー指定観察項目 | Trial-11レビューでの該当箇所 | Afterで確認すべきこと |
|---|---|---|---|
| 1 | Full Story/Point構成 | 論点4(A2の4ブロック構成・Point Value QA 12項目) | 構成要素の有無だけでなく、各ブロックのtolerance逸脱まで見ているか |
| 2 | Pointの言い換え回避 | 論点4(Point Value QA「Full Storyの言い換えでないか」)、見落とし7(見出しと本文の言い換え重複) | QA結果のPASSを鵜呑みにせず、実文面の言い換え重複を目視確認しているか |
| 3 | Pointごとの発見の差 | 論点5(題材の型分散)、見落とし5(2テーマで型が酷似) | 定量指標がない領域(多様性)を「目視で確認した」と明言しているか |
| 4 | 保険文 | 論点1(a)(題材依存で0件を説明)、論点2(caveat密度は別概念)、見落とし9(regexの検出範囲限定) | 「保険文0件」を無条件の改善根拠として扱っていないか |
| 5 | Ledger Deviation/Local Rewrite挙動 | 論点2全体(事実面妥当だが副作用あり) | Rewrite前後で語数・near-duplicate・後続QA未通過の有無を確認しているか |
| 6 | Fact Checker | 論点3(件数の正確性、stale advisoryの区別) | advisory件数を鵜呑みにせず、最終本文に該当するかを個別確認しているか |
| 7 | Point Overlap/Value QA | 論点1(b)(f)、論点4、見落とし2(Evidence Compressionの数値逆転) | QA PASSの範囲外(記事間多様性、数値具体性の逆転)まで見ているか |
| 8 | Support/Key Phrase | **Trial-11レビューでは明示的に扱われていない**(gap) | Afterでは対象Trialの成果物にSupport/KPが含まれる場合、この論点をpacketの(a)へ明示的に追加すること。含まれない/対象外の場合はその旨をrubric不適用として記録する |
| 9 | A2/B1成立性 | 論点4(A2 294語・tolerance超過)、見落とし3・4(B1B語数上限接近、A2 Point One超過) | soft range PASSだけでなく、tolerance逸脱(非gate)まで拾っているか |
| 10 | 音声工程 | 論点4(尺の推定)、見落とし7(音声上の重複) | 実測値と推定値を区別しているか、尺のhard gate有無を確認しているか |

**品質判定基準(Afterの合否基準)**: 上記10項目のうち、対象外と明記された
項目(該当なし)を除き**欠落ゼロ**。かつ、各論点についてTrial-11レビューと
同等の根拠深度(ファイル名+行範囲の引用、推定値と実測値の区別、QA結果PASSの
額面どおりの受け取りを避ける姿勢)があること。根拠引用が「参照した」とだけ
書かれ具体的な行範囲がない場合は品質低下とみなす。

---

## 3. context packet雛形

`docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`(新規作成、SSOTではない、
既存ルールを上書きしない旨を雛形冒頭に明記)。構成は(a)論点(限定)/
(b)主要数値表・要点(Sonnet REPORT全文でなく転記のみ)/(c)Production
code・spec該当行範囲のみ/(d)Sonnet要約/(e)progressive disclosure指示文
(Opusが追加ファイルを読む前に理由・対象を宣言し、最終メッセージで読込文字数を
自己申告)/(f)入力文字数の自己計測欄。未記入状態の雛形自体の文字数は
Python `len()`実測で2,637字。

---

## 4. After実行手順書(Fable向け)

Trial-12(`FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12`)
完了後、以下の順で実施する。

1. **Sonnetがpacket生成**: 対象タスクのSonnet REPORT完成後、Sonnetが
   `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`を埋めて
   `er011_output/discovery_generalization_wake_before_alarm_trial_12/
   opus_context_packet.md`として保存する。2節の必須論点チェックリスト
   (該当外を除く)を(a)論点セクションへ具体化して転記する。(f)自己計測欄の
   文字数を実測(Python `len()`)で記入する。
2. **Fableの委任文**: opus-consultantへは`opus_context_packet.md`の**内容を
   貼り付けるか、Read対象として同ファイルパスのみを渡す**(元REPORT全文・
   `comparison_vs_towels_trial_11.json`等の生成物全文・巨大SSOT全文を
   追加で渡さない)。委任文自体にも「読むべきはpacketのみ、追加が必要な場合は
   progressive disclosure手順に従うこと」を明記する。
3. **読込文字数の再集計**: `er011_pm_agent_read_audit_01.py`を再実行し、
   当該管理ID(Opus L2レビュー分)のOpus実読込文字数・委任文文字数・
   タスク内重複・Agent間重複を1節と同一手法で集計する。
4. **Before/After表の作成**: 以下の型でREPORT追記(または新規
   `_AFTER`サフィックスREPORT)へまとめる。

   | 項目 | Before(代替値、1節) | After(Trial-12実測) | 削減率 | 品質影響(2節rubric欠落有無) |
   |---|---|---|---|---|
   | Opus実読込文字数 | | | | |
   | Fable→Opus委任文字数 | | | | |
   | タスク内重複文字数 | | | | |
   | Agent間重複文字数 | | | | |
   | 総読込文字数(delegation含む) | | | | |
   | 論点欠落件数(2節10項目中) | 0(基準) | | — | |
   | 作業時間 | | | | |
   | compact回数 | | | | |

5. 比較後、STOP条件(5節)に抵触しないことを確認し、closeoutを
   `進行中`→`完了`へ更新する(このタスクでは行わない)。

---

## 5. STOP条件・データ欠落・限界

**STOP条件(該当した場合はユーザー判断を仰ぐ)**:
- context packet方式で2節の必須論点(該当外を除く)に欠落が生じた場合。
- packet方式が「重要contextの削減」を要求する結果になった場合(禁止事項に
  抵触するため即STOP)。
- 現行Agent構成(sandwich-pm/opus-consultant等)の変更が必要と判明した場合。

**データ欠落・限界**:
- Trial-11 Opus L2レビュー本体の実際のOpus読込文字数は未計測(1-2節に明記)。
  Afterとの比較は「同系統タスクの代表値」であり管理ID完全一致ではない。
- After実測はTrial-12完了後でなければ取得できないため、本REPORTは
  Before/rubric/雛形/手順の確定のみで、Before/After表は空欄のまま提出する。
- 2節の「Support/Key Phrase」はTrial-11レビューで扱われていない論点であり、
  Afterで対象外と判定される可能性がある(その場合も「対象外と判定した」旨の
  明記を品質基準に含める)。

**Status**: 準備段階完了。Closeout = **進行中(Trial-12完了・After実測待ち)**。

---

## 6. After: packet生成(2026-09-12、管理ID`PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01`のAfter段階、¥0)

Trial-12(`FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT.md`、15,230字)完了を受け、4節の手順どおりSonnetがcontext packetを作成した。

- **成果物**: `er011_output/discovery_generalization_wake_before_alarm_trial_12/opus_context_packet.md`(Python `len()`実測**15,211字**)。
- **内訳(自己計測、packet末尾(f)節と同一)**: (a)論点2,860字/(b)主要数値表・要点5,122字/(c)spec・code該当行範囲3,606字/(d)Sonnet要約778字/(e)progressive disclosure指示文1,666字/(f)自己計測欄自体約520字(数値記載の自己参照性により合計とはわずかに非加算)。
- **Before代替値との比較**: 1節のBefore代替値(`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`のOpus実読込文字数135,397字)に対し、本packet15,211字は**約11.2%**(削減率約88.8%、ただしBeforeは管理ID完全一致ではなく同系統タスクの代表値である制約は1節記載のとおり)。
- **2節rubric(必須論点チェックリスト10項目)との対応**: packet(a)節で10項目全てを具体化して転記した(該当外の項目なし、Support/Key PhraseはTrial-12では成果物が存在したため対象に含めた)。
- **packet作成中の新規所見1(Trial-12自体の見落とし再現、opusへの申し送り事項としてpacket(a)②⑨・(b)に記載済み)**: Trial-12 REPORT本文はA2 `point_one`(79語)のtolerance/target上限超過に一切言及していないが、`comparison_vs_towels_trial_11.json`の実測データにはこの超過が記録されており、これはTrial-11 Opus L2レビュー「見落とし4」(同種の超過をTrial-11 REPORTが報告していなかった点)と同一パターンの再現に見える。
- **packet作成中の経緯記録(RECONCILE-03、指示違反ではなく正常な並行進行)**: packet作成着手時点(検索実施時刻)では`REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03_REPORT.md`は存在しなかった(検索で不存在を確認済み)。そのためSonnetは代替として限定的なコード確認(`er003_v1_n3_01_tts_generate.py`の`tts_safe_number_words_en()`)を行い、「ハイフン複合数は既存修正の対象外」という未検証仮説をpacketへ暫定記載した。その後、packet作成作業の途中(15:37頃)に別途進行していた`RECONCILE-03`タスクの報告物が新規に生成されたため、Sonnetがこれを検知し読み込み、packet(a)③・(c)・(d)を**確定した根本原因(トークン境界の非対称性、暫定仮説より一段深い原因)へ全面的に差し替えた**。最終packetはSonnetの暫定仮説ではなく、RECONCILE-03の確定結果のみを記載している(暫定仮説は残していない)。
- **未実施(本タスクの範囲外、次ステップ)**: `er011_pm_agent_read_audit_01.py`によるOpus実読込文字数の再集計(opus-consultant起動後)、Before/After比較表(4節4項)の作成。opus-consultant自体の起動もSTOPしている(本タスクではAPI支出・Opus起動を行っていない)。
- **Status更新**: 本タスク(context packet生成)は完了。Closeout全体は引き続き**進行中(opus-consultant起動・読込文字数再集計・Before/After表作成待ち)**。

---

## 7. After測定(2026-09-12、管理ID`PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01-AFTER-MEASUREMENT`のSonnet実測、¥0・read-only)

opus-consultant(Discovery Trial-12のL2解釈、context packet+progressive disclosure方式)完了を受けた実測。**判定語(VALIDATED/REJECTED等)はここでは確定しない。以下は判定材料の提示のみで、採用可否はFable/ユーザー判断に委ねる。**

### 7-1. Opus出力REPORTの保存

Opusの最終メッセージ本文(subagent転記`a3fa46502208135e8.output`は0バイトで**消失していた**ため、Fable本体セッション`294958fe-da6e-491c-8a02-4f864d8195c8.jsonl`内の`queue-operation`(task-notification、`<result>`タグ)に埋め込まれた確定結果テキストから機械抽出。HTMLエンティティ化されていた`&lt;`/`&gt;`のみ`<`/`>`へ復元し、それ以外は一字も改変していない)を
`FAMILY-A-DISCOVERY-GENERALIZATION-TRIAL-12-OPUS-L2-INTERPRETATION-01_REPORT.md`として保存した。

**データ欠落の明記**: Opus自身のRead/Grep/Glob呼び出し単位の生ログ(`er011_pm_agent_read_audit_01.py`が本来集計する対象)は、`.output`ファイルが0バイトだったため**実測不能**。これは既知のagentId再利用/rotation挙動(本Phase1監査`PM-TOKEN-EFFICIENCY-AGENT-READ-DUPLICATION-AUDIT-01_REPORT.md`2節が指摘した「保持期限切れ」と同型の制約)であり、本タスクの操作ミスではない。代わりに以下を実測の代替とした。
- **packet本体**: `er011_output/discovery_generalization_wake_before_alarm_trial_12/opus_context_packet.md`をPython `len()`で直接実測 → **15,211字**(Opus自己申告と完全一致)。
- **追加開示(progressive disclosure)分**: Opus最終メッセージ末尾「追加開示ログ」表の自己申告(6件、約8,250字)。各対象ファイルの実サイズ(`os.path.getsize`)を突合したところ、いずれも自己申告値が実ファイルサイズ以下(部分読込・Grep範囲読込との整合)であり、**過大申告の兆候はない**(下表)。

| 対象 | 自己申告(概算) | 実ファイルサイズ | 整合性 |
|---|---|---|---|
| `a2/parts.json` | 約1,900字 | 2,099 bytes | 整合(ほぼ全文相当) |
| `b1b/parts.json` | 約2,300字 | 2,438 bytes | 整合(ほぼ全文相当) |
| `er011_open121_repetition_qa_production_01.py`(360-429行) | 約2,600字 | 全体29,371 bytes | 整合(部分読込、行範囲と符合) |
| `er008_disfluency_qa_18.py`(44-45行、Grep -A8) | 約400字 | 全体6,334 bytes | 整合(Grep範囲読込) |
| `er003_v1_n3_01_tts_generate.py`(576/582行、Grep) | 約200字 | 全体58,348 bytes | 整合(Grep範囲読込) |
| Trial-11 towels `{a2,b1b}/parts.json`(Grep、4フィールドのみ) | 約800字 | 各2,065/2,936 bytes | 整合(Grep範囲読込) |

このため、Opus実読込文字数は「**15,211字(機械実測)+ 約8,250字(自己申告、file-sizeとの整合確認済)= 約23,450字**」を、生ログ消失下でのAfter値として採用する。

### 7-2. `er011_pm_agent_read_audit_01.py`再実行結果

既存スクリプトを再実行した(`er011_output/pm_agent_read_audit_01/{per_call.jsonl, per_agent_task_summary.json, summary.md}`更新、746レコード)。上記の理由により**Opus自身の読込は本スクリプトのper_call集計には現れない**(該当agentId行が0バイトのため対象外)。一方、Fableの委任文(Agent tool_use入力)は本体セッションjsonlから直接特定できたため、以下は本体jsonlからの直接抽出値(単発呼び出し、mgmt_id持ち越し混入なし)を採用する。

| 呼び出し | セッション内line番号 | 起動時刻(UTC) | 完了時刻(UTC) | 所要時間 | 委任文字数(単発) |
|---|---|---|---|---|---|
| Before: Trial-11 Opus L2レビュー起動(`a146ec25-...jsonl`) | line 707 | 2026-09-10T00:46:56.914Z | 2026-09-10T00:55:34.304Z | 約8分38秒 | **2,338字** |
| After: Trial-12 Opus L2解釈起動(`294958fe-...jsonl`) | line 1292 | 2026-09-12T06:43:24.823Z | 2026-09-12T06:49:33.050Z | 約6分9秒 | **1,583字** |

参考(`er011_pm_agent_read_audit_01.py`の管理ID別集計、mgmt_id持ち越しにより同一管理ID配下の複数Agent呼出が合算されている点に注意。単発値としては上表を正とする): Before側の管理ID集計は`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01`で8,568字(2 calls)、After側は`FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12`で5,363字(2 calls、うちpacket生成Sonnetへの委任文も含まれるためOpus単体の値ではない)。

所要時間の差(約29%短縮)は、モデル負荷・API応答速度等の交絡要因を排除できていないため、**参考値であり、packet方式の効果と断定しない**。

### 7-3. Before/After表

| 項目 | Before | After | 削減率 | 品質影響 |
|---|---|---|---|---|
| Opus実読込文字数(代替Before基準、`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`実測135,397字) | 135,397字 | 約23,450字(15,211字機械実測+約8,250字自己申告) | **約82.7%減**(残存約17.3%) | 7-4節参照 |
| Opus実読込文字数(旧基準、3V Phase1実測、約452,000字、参考再掲) | 約452,000字 | 約23,450字 | 約94.8%減(残存約5.2%) | 同上 |
| Fable→Opus委任文字数(単発、mgmt_id持ち越し混入なし) | 2,338字 | 1,583字 | 約32.3%減 | — |
| Fable→Opus委任文字数(script集計、mgmt_id持ち越し混入あり、参考) | 8,568字(2 calls) | 5,363字(2 calls、他Agent委任含む) | 参考値(直接比較不可) | — |
| Agent間重複読込(packet生成Sonnet↔Opus) | 未計測(Phase1同様rotation失効) | **定量化不能**(Opus生ログ消失のため`er011_pm_agent_read_audit_01.py`の重複検知が適用不可)。定性的には、Opusが追加開示した`a2/b1b parts.json`は同ファイルをpacket生成Sonnet(`a30e396facfba8f18.output`)も参照済みの可能性が高い(packet(b)節数値表の元データであるため) | 判定不能 | — |
| 総読込文字数(Opus読込+delegation) | 137,735字(135,397+2,338) | 25,033字(23,450+1,583) | 約81.8%減 | 7-4節参照 |
| 論点欠落件数(2節rubric10項目中) | 0(基準) | **0**(10項目すべてに判定・根拠を明記、7-4節) | — | 欠落なしを確認 |
| 所要時間(Opus起動〜完了通知) | 約8分38秒 | 約6分9秒(約29%短縮、参考値・交絡因子未排除) | 参考 | — |
| compact回数 | 不明(取得手段なし) | 該当なし(本タスク中にcompactは発生していない) | — | — |

### 7-4. 品質チェック(Trial-11 Opus L2レビュー「見落とし①〜⑩」との機械照合)

`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md`171-183行の「Sonnet/Fableが見落としている可能性のある点」①〜⑩に対し、Trial-12 Opus出力に「見落としN」という明示番号引用がGrepで存在するか(○=明示引用あり/×=明示引用なし)、および内容として同一論点に言及しているか(判断を伴う補足、テーマ一致の有無)を分けて示す。

| # | Trial-11見落とし内容 | 明示番号引用(Grep機械照合) | 内容としての言及(補足) |
|---|---|---|---|
| ① | Fact CheckerがLocal Rewrite出力を見ない構造的blind spot | ○(論点2⑥「Trial-11見落とし①」) | advisory 0件はRewrite 0件のため今回非発火、gap残存と明記 |
| ② | Evidence Compressionの数値具体性逆転(B1B<A2) | ○(論点2⑦・論点5-4「Trial-11見落とし②」) | 新規事例(front-right/front)を追加発見 |
| ③ | B1B 419語/soft上限420語(語数上限接近) | ×(明示引用なし) | 内容としても**同一指標の再現は言及なし**。ただし異なる指標(B1B point_two 64語のtarget超過)を新規発見として提示(論点5-2) |
| ④ | A2 Point One 71語がtolerance上限70語を超過 | ○(要点2・論点2⑨・論点5-4、複数箇所) | 本レビューの**最重要論点**として展開(79語へ悪化、13%超過と定量化) |
| ⑤ | 2テーマの型の酷似(ズームアウト構成) | ○(要点3・論点5-4「見落とし⑤⑥」) | in_one_line/heading定型句の実文比較で新規実証 |
| ⑥ | house phraseの再出現("quiet lesson") | ○(要点3・論点5-4・追加開示ログ「見落とし⑤⑥」) | "meeting point"への型置換を新規確認 |
| ⑦ | 音声で目立つ細かい重複2件(人手修正候補) | ×(明示引用なし) | 内容としては近接論点あり: near-duplicate件数増加(A2 0→1、B1B 1→2)と記事QA/音声QAの層間閾値不整合(論点2⑩)を新規発見として展開。ただしTrial-11の具体的2件との直接対応付けはなし |
| ⑧ | comparison.html未生成 | ×(明示引用なし) | 内容としては言及あり(論点4表(5)・論点5-5「不明/未確認」) |
| ⑨ | 保険文regexが独立caveat文を検出しない | ○(要点なし、論点2④・論点5-4「Trial-11見落とし⑨」) | 実文面のcaveat文を複数引用して再確認 |
| ⑩ | (自認済み)費用A2/B1B分離不可・Precheck Layer1有無差・JAPANESE_TITLES未登録 | ×(該当なし/対象外) | Trial-12の論点ではなく妥当な非言及 |

**集計**: 明示番号引用6/10(①②④⑤⑥⑨)、内容としての言及は⑧を加えて7/10相当、③⑦は同一指標としての再現言及なし(③は異なる指標で代替、⑦は近接概念で代替)。**Phase 2 rubric(本REPORT2節)の必須10項目(観察項目1〜10、Trial-11見落としとは別建ての比較軸)については、Trial-12 Opus出力の論点2が①〜⑩全項目に判定と根拠を明記しており欠落ゼロ**(2節の品質判定基準を満たす)。

**特記(タスク指示により明記)**: 見落とし④(A2 point_one語数超過)は、Trial-11では71語→今回79語で**悪化方向に再現**しており、Trial-12 Opus出力はこれを「N=2/2で同方向に再現した系統的signal」(要点2)として最重要論点に格上げしている。

### 7-5. packet不足点9件(テンプレート改善候補、`docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`は未編集)

Opus最終メッセージ末尾の「packet不足点(Phase 2改善用)」をそのまま候補として列挙する(採否・テンプレート編集はユーザー判断待ち、本タスクでは実施していない)。

1. 記事本文(`parts.json`相当)が未転記(観察項目②④⑦⑧の判定に本文読込が必要だった。最も費用対効果が高い改善点との自己評価)。
2. tolerance/targetの実数値がpacketに欠落(booleanのみで、超過幅を逆算する必要があった)。
3. near-duplicate pairの実文がpacketに未転記(ratio数値のみで、どの2文かは本文読込が必要だった)。
4. Support/Key Phraseの成果物本文が未転記(論点2⑧を検証不能として保留せざるを得なかった)。
5. `(?<!-)`の帰属箇所がpacket内で誤り(TTS前処理側`er003_v1_n3_01_tts_generate.py:582`が正、OPEN-121実装ではない)。
6. レベル間表記差(A2 "twenty-four-hour" vs B1B "24-hour")がpacket未記載(failure modeのレベル依存性の核心だった)。
7. Trial-11の`in_one_line`/headingがpacket未転記(型/house phrase継続性判定に比較対象の実文が必要だった)。
8. comparison.html生成有無がpacket未記載。
9. (軽微)費用按分単位(¥78.98がテーマ単位かレベル単位か)がpacket上曖昧。

### 7-6. Closeout

本タスク(After実測)は完了。**判定(VALIDATED/REJECTED/採用可否)はFableが行う**。Sonnetは上記7-3表(削減率)・7-4表(品質照合)・7-5(packet改善候補)を判定材料として提示するに留める。Opus生ログ消失によりAgent間重複読込の定量化ができなかった点、および削減率がBefore代替値(管理ID完全一致ではない)基準である点は、判定時に明記すべき制約として申し送る。
