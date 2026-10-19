# TRIAL_DESIGN_01(FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_01、2026-10-19、Phase A、JPY0)

- Status: `B3BG_PHASE_A_DESIGN_AND_HARNESS_READY_PENDING_OPUS`(到達上限Status=案件全体で`VALIDATED`。Production採用・配線は範囲外)。
- 根拠: ユーザー指示原文 `docs/pm/delegation_log/2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_USER.md`(3590文字、sha256 `ac445c55b8525bd10b798188b070d67b5a1e1137747a351ad712d567b4a18d0c`)。委任文 `..._委任_01.md`(T-0 check PASS)。
- 作業開始時のstop_scope_check: rc=0、stop=false(`docs/pm/delegation_log/2026-10-19_B3BG1_stop_check.json`)。
- 有料API呼出: 0。コード(Production)変更: 0。`run_mey_01`配下の書込み: 0(読取のみ)。成果物: `er083_b3_background_fact_trial_01_{lib,run,eval,writer_probe,test_01}.py`、`er083_output/b3_background_fact_trial_01/_dryrun/`(モック出力)。
- 事前観測(Phase B設計に効く事実): 同一Ledger・同一テーマでB3は実行ごとにばらつく。`run_mey_01/_before_regen_01`・`_before_regen_02`の採用は`[F11]`のみ、現行(下限2件配線後の初回選定)は`[F04,F11]`。よってBaselineは1sampleでは基準にならず、**Baseline再走sampleを1本取る**(§5)。

## §1 Ledger前提表(評価条件。仕様文には入れない)

対象: `er019_output/middle_east_yemen_saudi/run_mey_01/research_ledger/verified_fact_ledger.txt`(11件、全て`[VERIFIED]`)。3区分はユーザー§3の区別に従う。凡例: ◎=Fact自身が直接述べる / △=部分的(下記の限定付き) / ×=述べていない(Ledger欠落)。「誰が」は**サウジ側の施設への攻撃**についての攻撃主体の帰属(イエメン国内の事案の帰属と区別)。

| Fact | 内容(要旨) | 誰が(攻撃主体の帰属) | なぜ(動機) | 紛争の背景 |
|---|---|---|---|---|
| F01 | 国連特使: イエメンは全面的な戦闘状態に戻り複数前線で戦闘。サウジの民間・エネルギー施設への攻撃も報告 | × (攻撃主体の記載なし) | × | ◎(戦闘状態・前線。特使の評価として帰属) |
| F02 | GACA: アブハ・リヤド空港が10/6-7に攻撃、死傷者内訳 | × (conditionsに「攻撃主体はこの発表では特定されていない」) | × | × |
| F03 | GACA: リヤド空港で10/8に2件の攻撃、死亡3人 | × (「特定されていない」) | × | × |
| F04 | GACA続報: 10/10の同空港攻撃で死亡12人・負傷309人 | × | × | × |
| F05 | GACA: 10/11午後に同空港へ新たな攻撃 | × (notes「攻撃主体は追加しない」) | × | × |
| F06 | 連合軍報道官: 10/11に空港付近で巡航ミサイルを迎撃 | × (「発射主体は記載されていない」) | × | △(「イエメンで活動する連合軍」の存在のみ) |
| F07 | GACA: 10/11夜にダンマームの空港が攻撃 | × (「記載されていない」) | × | × |
| F08 | エネルギー省関係者: 10/13にアラムコ管理棟が攻撃、小規模火災 | × (「特定されていない」「確認されていない」) | × | × |
| F09 | SABA通信(マリブ県メディア局報告): 10/15にフーシ派がマリブ市内の住宅地域へミサイル9発等 | △(イエメン国内の事案の帰属のみ。イエメン政府系報道機関の報告として。サウジへの攻撃の帰属ではない) | × | △(イエメン国内でも発射が報告) |
| F10 | アデン治安局: 10/16にフーシ派発射のミサイル2発がアデン空港敷地に落下 | △(同上。当局発表として。サウジへの攻撃の帰属ではない) | × | △(同上) |
| F11 | 国連特使: サウジ民間インフラへの継続攻撃を非難、リヤド空港12人死亡、和平努力を一層困難にすると評価 | × | ×(動機ではなく「影響」の評価) | △(和平努力が存在し攻撃が影響するという評価。特使評価として帰属) |

結論(Ledger欠落の明示):
1. **動機(なぜ攻撃するのか)を直接述べるFactは、11件中0件。Ledger欠落**。F11は攻撃の「影響」(和平への悪影響)の評価であり動機ではない。
2. **サウジ側施設への攻撃の主体の帰属を述べるFactも0件**(F02・F03・F05・F06・F07・F08が「特定/記載されていない」と明記)。帰属を述べるのはF09・F10のみで、これはイエメン国内の事案についてイエメン側当局・報道機関の報告を伝えるもの。F09・F10から「サウジへの攻撃の主体」を断定することは、ユーザー§3「一般的な紛争背景から個別の攻撃主体や動機を断定してはならない」に反する。
3. **紛争の背景**は部分的にある(F01=戦闘状態への復帰と複数前線、F11=和平努力の存在、F06=連合軍の存在)。最も「何の流れの一部か」に近いのはF01。
4. 帰結(評価条件): このLedgerでは、ユーザーの狙い「誰が、なぜサウジを攻撃するのか」のうち「なぜ」は**補完不能**(Ledgerに無い)。適切な挙動は「不足を明示し、推測せず、何も補完しない」(ユーザー§3 2段落目)。補完してよいLedger内の前提は、せいぜい紛争の背景(F01)。したがって評価では「F01が補完されること」を**期待の上限**とし、F09/F10の採用はサウジ攻撃の帰属に使われる限り減点とする(§4 軸4)。特定Fact IDの採用は強制しない。

## §2 仕様候補C1〜C3(一般化された文言のみ。全文は`er083_b3_background_fact_trial_01_lib.py`の`CANDIDATE_NOTES`)

### 2-0 共通設計
- 不変: `DEVELOPER_MESSAGE`・4テスト定義(`FACT_TEST_DEFINITIONS_JA`)・`USER_PROMPT_TEMPLATE`(「`[VERIFIED]`から最低2件」)・`REEVAL_APPEND_NOTE_TEMPLATE`・JSON schema・技術retry・下限2件の再評価/STOP。全てProductionの`run_storyline_b3_selection`をそのまま呼ぶ(コード不変)。
- 追加: user入力の**末尾へ補助指示を追記**するだけ(`AppendNoteClient`)。全call(初回・技術retry・再評価)に同じ追記。Baselineは追記が空=Productionとバイト同一のPrompt(§3で機械証明)。
- 追加Factの位置づけ: `selected_fact_ids`に含め、`fact_tests[].reason`先頭の「【背景補完】+必要性1文」で区別(**schema・producer・Writer契約は不変**)。背景確認の結果は`recheck_note`先頭の「【背景確認】」に記録(追加不要/追加(ID・理由)/不足(何が足りずLedgerに直接述べるFactが無い))。`recheck_note`はProductionでは「6件以上のとき必須」のsoft検査にしか使われない(`b3 module L244`、runnerはevidenceへ保存するのみ`runner L183`)ため、Trialでの転用で他に影響しない。**本番化する場合は専用フィールド追加=schema変更=Production仕様変更になる**(Opus観点4、Phase Bの範囲外)。
- 共通の過剰補完抑止(`COMMON_GUARD`): 追加はFull Ledgerに実在し前提をFact自身の記述として直接述べるFactのみ/Ledger外の推測・創作・補完の禁止/帰属(誰が)・動機(なぜ)・背景は別物で、1つしか述べないFactを他2つの裏付けにしない・別の出来事のFactから主体や動機を推定して結ばない/補足便利・面白い・数字・網羅・詳細解説は目的外/最大2件/ストーリーの焦点・筋・読み味を変えない/【背景補完】のFactには4テストの「原則除外」の目安を適用しない(回答自体は事実に即して記入)。
- 比較条件の統一: 同Ledger(sha `4f7d28b0…`)・同theme・同model(`FAMILY_X_STORYLINE_B3`=routing値、`gpt-6.1-sol`)・同effort(`high`)・同schema・同developer message。温度: Productionは推論モデルで`temperature`を指定していない(`reasoning={"effort":"high"}`のみ)ため同条件=指定なし。B3は実行ごとに揺れるため、**Baseline再走を1本取り**候補差がばらつきを超えるかを見る。
- 「最低限」「不可欠」「欠落時のみ追加」の表現の違い(候補間の比較軸): C1=自問1問(open-endedな「不可欠な前提」判定)、C2=全Factへ第5テスト(選定と同時評価=Factごとの機械的判定)、C3=自問を「素朴な疑問の列挙→回答可否」に操作化(判定手順を明示)。

### 2-1 候補C1「二段階・欠落時のみ」(追記全文)
```
【背景補完の確認(補助指示・候補C1)】
上記1〜5の選定(中心Storylineの決定、4テストの適用、採用/除外の決定)を、これまでの指示どおり先に完了してください。この補助確認のために、決定済みのStorylineと採用Factを変更してはいけません(この確認でストーリーの焦点を動かさない)。
そのうえで、次の1点だけを自問してください。
「決定したStorylineと採用Factだけを読む初見の読者は、そのStorylineを最低限理解するために不可欠な前提(例: その出来事に関与している主体が誰か、その出来事が何の流れの一部か)を欠いていないか」
- 欠いていない場合: 何も追加しません。これが既定です。
- 欠いている場合に限り、Full Ledgerから、その前提を直接述べているFactを原則1件(最大2件)だけ追加採用してよい。
- 欠いているが、Ledgerにその前提を直接述べるFactが無い場合: 何も追加しません。

【共通の注意(背景補完)】
- 追加してよいのは、Full Ledgerに実在するfact_idのうち、その前提をFact自身の記述として直接述べているFactだけです。Ledgerに書かれていない事実を、推測・創作・補完してはいけません。
- 関与している主体の帰属(誰が)、動機・理由(なぜ)、背景(それまでの経緯・状況)は別のものです。あるFactが述べているのがそのうちの一つだけなら、他の二つの裏付けとして扱ってはいけません。また、別の出来事を述べたFactから、このStorylineの出来事の関与主体や動機を推定して結び付けてはいけません。
- 補足として便利、詳しくなる、面白い、数字がある、というだけのFactの追加、ニュース全体の網羅、背景の詳細な解説は目的ではありません。追加するFactは、Storylineの焦点・筋・読み味を変えないものに限ります。
- 追加の上限は最大2件です。追加によって採用数が6件以上になる場合は、従来どおりrecheck_noteへ検討内容も記載してください。
- 追加したFactは selected_fact_ids と fact_tests(decision="selected")に含め、そのreasonの先頭に「【背景補完】」を付けて、「このFactが無いと何が理解できないか」を1文で書いてください。追加しなかったFactのreasonに【背景補完】は付けません。
- 背景確認の結果は、recheck_noteの先頭に「【背景確認】」を付けて1〜3文で必ず記録してください(追加不要 / 追加(fact_idと理由) / 不足(何が足りず、Ledger内に直接述べるFactが無い))。採用数が5件以下でも記入してかまいません。この場合、上の「5件以下の場合はnull」の指示より優先します。
- 「【背景補完】」で採用するFactには、4テストの「原則除外」の目安(YES/NOの組み合わせ)は適用しません(4テストの回答自体は事実に即して記入してください)。
```

### 2-2 候補C2「第5テスト統合」(追記全文)
```
【背景補完の確認(補助指示・候補C2)】
Test1〜4(定義・判定は変更しません)に加えて、全Factに次の第5のテストも適用してください。
Test5: そのFactが無いと、選んだStorylineを初見の読者が最低限理解できなくなるか(背景の不可欠性)。Storylineの理解に不可欠な前提(例: その出来事に関与している主体が誰か、その出来事が何の流れの一部か)を、Fact自身の記述として直接述べている場合のみYES。補足として便利・詳しくなる・面白いだけならNO。
- Storylineはこれまでどおり先に決定し、Test5はそのStorylineを変えずに適用してください。
- fact_testsのJSON schemaにTest5の欄はありません。Test5=YESのFactは、reasonの先頭に「【背景補完】」を付けてください(下の記載ルール)。Test5=NOのFactには何も付けません。
- Test5=YESのFactは、Test1〜4で「原則除外」となる場合でも採用してかまいません。ただし、Test5=YESで追加採用してよいのは、Test1〜4で採用したFactだけではStorylineを最低限理解できない場合に限ります。
- Test5=YESのFactがLedgerに無い場合: 何も追加しません。

【共通の注意(背景補完)】
- 追加してよいのは、Full Ledgerに実在するfact_idのうち、その前提をFact自身の記述として直接述べているFactだけです。Ledgerに書かれていない事実を、推測・創作・補完してはいけません。
- 関与している主体の帰属(誰が)、動機・理由(なぜ)、背景(それまでの経緯・状況)は別のものです。あるFactが述べているのがそのうちの一つだけなら、他の二つの裏付けとして扱ってはいけません。また、別の出来事を述べたFactから、このStorylineの出来事の関与主体や動機を推定して結び付けてはいけません。
- 補足として便利、詳しくなる、面白い、数字がある、というだけのFactの追加、ニュース全体の網羅、背景の詳細な解説は目的ではありません。追加するFactは、Storylineの焦点・筋・読み味を変えないものに限ります。
- 追加の上限は最大2件です。追加によって採用数が6件以上になる場合は、従来どおりrecheck_noteへ検討内容も記載してください。
- 追加したFactは selected_fact_ids と fact_tests(decision="selected")に含め、そのreasonの先頭に「【背景補完】」を付けて、「このFactが無いと何が理解できないか」を1文で書いてください。追加しなかったFactのreasonに【背景補完】は付けません。
- 背景確認の結果は、recheck_noteの先頭に「【背景確認】」を付けて1〜3文で必ず記録してください(追加不要 / 追加(fact_idと理由) / 不足(何が足りず、Ledger内に直接述べるFactが無い))。採用数が5件以下でも記入してかまいません。この場合、上の「5件以下の場合はnull」の指示より優先します。
- 「【背景補完】」で採用するFactには、4テストの「原則除外」の目安(YES/NOの組み合わせ)は適用しません(4テストの回答自体は事実に即して記入してください)。
```

### 2-3 候補C3「疑問列挙による判定」(追記全文)
```
【背景補完の確認(補助指示・候補C3)】
上記1〜5の選定を先に完了し、決定済みのStorylineと採用Factはこの確認のために変更しないでください。
そのうえで、決定したStorylineを初見で読んだ読者が最初に抱く素朴な疑問を、そのStorylineが自然に抱かせるものに限り、最大2つ挙げてください(型の例: 「誰が(何が)関わっているのか」「なぜそうなったのか」「これは何の流れの一部なのか」。Storylineが触れていない話題についての疑問を作ってはいけません)。
各疑問について、採用Factだけで答えられるかを確認します。
- 採用Factだけで答えられる: 何も追加しません。
- 答えられず、Full Ledgerのfact自身がその疑問に直接答えている: そのFactを疑問ごとに1件まで追加採用してよい。
- 答えられず、Ledgerにも直接答えるFactが無い: 何も追加せず、その疑問を「Ledger内に回答なし」として記録します(推測で答えない)。
- recheck_note(【背景確認】)には、挙げた疑問ごとに「疑問 / 採用Factで回答済 / 追加Fact(fact_id)で回答 / Ledger内に回答なし」を書いてください。

【共通の注意(背景補完)】
- 追加してよいのは、Full Ledgerに実在するfact_idのうち、その前提をFact自身の記述として直接述べているFactだけです。Ledgerに書かれていない事実を、推測・創作・補完してはいけません。
- 関与している主体の帰属(誰が)、動機・理由(なぜ)、背景(それまでの経緯・状況)は別のものです。あるFactが述べているのがそのうちの一つだけなら、他の二つの裏付けとして扱ってはいけません。また、別の出来事を述べたFactから、このStorylineの出来事の関与主体や動機を推定して結び付けてはいけません。
- 補足として便利、詳しくなる、面白い、数字がある、というだけのFactの追加、ニュース全体の網羅、背景の詳細な解説は目的ではありません。追加するFactは、Storylineの焦点・筋・読み味を変えないものに限ります。
- 追加の上限は最大2件です。追加によって採用数が6件以上になる場合は、従来どおりrecheck_noteへ検討内容も記載してください。
- 追加したFactは selected_fact_ids と fact_tests(decision="selected")に含め、そのreasonの先頭に「【背景補完】」を付けて、「このFactが無いと何が理解できないか」を1文で書いてください。追加しなかったFactのreasonに【背景補完】は付けません。
- 背景確認の結果は、recheck_noteの先頭に「【背景確認】」を付けて1〜3文で必ず記録してください(追加不要 / 追加(fact_idと理由) / 不足(何が足りず、Ledger内に直接述べるFactが無い))。採用数が5件以下でも記入してかまいません。この場合、上の「5件以下の場合はnull」の指示より優先します。
- 「【背景補完】」で採用するFactには、4テストの「原則除外」の目安(YES/NOの組み合わせ)は適用しません(4テストの回答自体は事実に即して記入してください)。
```
(C1〜C3のいずれも末尾に共通の`COMMON_GUARD`を含む。上記コードブロックはC1/C2/C3それぞれ、固有部分+共通部分の連結全文。)

### 2-4 比較表

| 観点 | C1 | C2 | C3 |
|---|---|---|---|
| 「不可欠」の判定方法 | 自問1問(「初見の読者が最低限理解するのに欠く前提はないか」) | 全Factへ第5テスト(「無いと理解できないか」YESのみ) | 自問を操作化: 読者が抱く素朴な疑問を最大2つ挙げ、採用Factで答えられるか確認 |
| 既定 | 追加なし | Test5=YESでも「Test1〜4で足りない場合に限る」 | 疑問ごとに回答可なら追加なし |
| ストーリー選定との順序 | 選定完了後に確認(変更禁止を明記) | 選定と同一パスでTest5(Storyline先決め・変更禁止を明記) | 選定完了後に確認(変更禁止を明記) |
| 追加上限 | 原則1・最大2 | 最大2 | 疑問ごと1・最大2 |
| 「不足」の記録 | recheck_note【背景確認】 | 同 | 疑問ごとの回答状況をrecheck_noteに列挙(最も観測しやすい) |
| 追加の位置づけ | selected_fact_idsに含め`reason`先頭【背景補完】(全候補共通) | 同 | 同 |
| Storyline一致検査(producer`_check_inputs` L732)への影響 | なし(Storyline文は選定側が決め、briefと同一parsed出力) | 同 | 同 |
| schema/Writer契約への影響 | なし | なし(Test5専用欄は無くreasonで代替) | なし |
| 主な過剰補完リスク | 低(自問1問、既定=追加なし) | **高**(全Factに判定が走り、YES判定が複数出やすい。Storyline侵食の恐れ) | 中(「なぜ」型の疑問が解説Factを引く恐れ) |
| 判定の再現性 | 中(open-ended) | 中(Factごと機械的だがTest5の基準が主観) | 高(疑問と回答状況が記録され検証可能) |

汎用性の思考実験(各候補で固有事例なしに動くか。実走は中東記事のみ):
- 経済ニュース例(Storyline「ある企業が決算発表後に株価急落」、採用Fact=下落幅と発表内容): 不可欠な前提=「その企業が何の事業をする会社か」。Ledgerにそれを直接述べるFactがあれば、C1/C3は1件追加、C2も追加。Ledgerに無ければ全候補とも追加せず不足を記録。リスク: 過去業績や競合動向のFactをC2がTest5=YESにしやすい(網羅化)。上限2件と「焦点を変えない」で抑止されるか。
- 科学ニュース例(Storyline「観測で系外惑星の大気から水蒸気を検出」、採用Fact=検出結果と観測機器): 「検出の何が重要か」の説明Factは「理解の前提」ではなく「解説」。C1は追加しない想定。C3は「なぜ重要か」型の疑問を挙げ解説Factを追加する恐れ(最も過剰補完しやすい分岐)。C3の「Storylineが自然に抱かせる疑問に限る」「回答するFactを疑問ごと1件まで」で抑止できるかはPhase Bで観測。
- 共通: どちらも固有名・固有Factを前提にせず、判断軸は「Storylineを初見で読む読者」「前提(誰が/何の流れの一部か)」「Ledger内に直接述べるFactがあるか」のみ。

推奨順序と理由:
1. **C3とC1を先に走らせる(並列)**。理由: 「不可欠」の操作的定義が弱いのが本Trialの核心リスクで、C3は判定手順と「Ledger内に回答なし」の記録が観測可能(Ledger欠落を明示する挙動の確認に最適)。C1は最小介入のベースライン的候補(既定=追加なし)で、C3との差=判定手順の操作化の有無が1変数で比較できる。
2. **C2は対照として同時に走らせる**(B3 1回約7.6円で並列実行のため追加時間0)。理由: 選定と同時評価する方式が最も統合的だが、Storyline侵食・網羅化のリスクが高く、リスクの大きさ自体がトレードオフ情報になる。Phase Bで軸1・3が崩れれば早期に棄却できる。
3. 下流Writerは、B3段で軸3・4が問題なしの候補だけ(最大2)。

## §3 harness設計とProduction非変更の証拠

構成(全てTrial専用`er083_*`、Production module/runnerには一切手を入れない):
- `er083_b3_background_fact_trial_01_lib.py`: 候補定義`CANDIDATE_NOTES`・`AppendNoteClient`(clientのproxy)・`run_candidate`(Productionの`b3.run_storyline_b3_selection`を呼び、runnerと同一キーのevidence/brief/full_ledgerを書き、`annot.produce_annotated_b3`を呼ぶ)・`analyze_selection`・`BudgetGuard`・`cost_summary`・`StubB3Client`(API 0)・出力先guard(`run_mey_01`配下・out-root外は`RuntimeError`)。
- `..._run.py`: CLI(`--article --ledger --theme --candidate --out-root --budget-jpy [--dry-run]`)。実run時のみ`cl.install(cost_log.jsonl)`。1候補=B3 1 call(+技術retry/再評価はProduction関数に委任)。呼出前に(これまでの実費+1call見込み7.6)がbudget超過ならBudgetStop。`STOP`/`STOP_ALL`センチネルがout-rootにあれば開始しない。
- `..._eval.py`: 候補横断比較表(採用ID/不採用ID理由/追加Factと必要性/【背景確認】note/下限2件/Storyline/Baseline差分)+仕様文の固有事例混入の機械チェック(`BANNED_SPEC_TERMS`+Fact ID正規表現)+盲検パック(候補名を伏せたA/B/..とキー別ファイル)。
- `..._writer_probe.py`: Production W-1 Writer(`run_w1_writer`)を候補の一時out-dir(er083_output配下)に対して呼ぶ。契約検証V1-V10はProduction側で課金前に実行。
- 環境変数/フラグ/隠しswitchなし(test`test_trial_modules_have_no_env_switch_and_do_not_import_runner`)。runnerは`import`しない。

Production非変更の証拠(実測):
- `git diff --stat HEAD -- er019_family_x_storyline_b3_fact_selection_01.py er019_family_x_entertainment_production_runner_01.py er053_b3_deterministic_producer_01.py er053_family_x_factlock_ja_writer_01.py` = 出力0行(testでも`er053_b3_annotation_contract_01.py`を加えて検査)。
- `git status --porcelain er019_output/middle_east_yemen_saudi` = 0行(run_mey_01は無変更)。
- Baseline dry-run(モックLLM、API 0)が保存済みProduction選定(F04+F11)を再現し、`selected_brief.md`・`selected_brief_annotated.md`・`annotation.json`・`writer_constraints.txt`・`full_ledger.json`が`run_mey_01/storyline_b3/`の実ファイルと**byte同一**(`cmp`、test `test_baseline_dry_run_reproduces_production_selection_and_artifacts`)。Baselineの送信userPromptは`b3.build_user_prompt(theme, ledger)`と完全一致、developer/user template/fact_test_definitions/reeval noteのshaは`run_mey_01/storyline_b3/runtime_evidence.json`・`fact_selection_evidence.json`の記録と一致(`developer_message_sha256=b4391b03…`、`user_prompt_template_sha256=6cc72184…`、`fact_test_definitions_sha256=91513c89…`、`reeval_note_sha256=dcf4f2b4…`)。
- 下限2件の再評価がProduction経路に委ねられ、候補追記が初回・再評価の両callに付くこと、REEVAL_STILL_LT2のSTOPが握りつぶされないことをtestで確認。
- テスト結果: `er083_b3_background_fact_trial_01_test_01.py` + `er019_family_x_b3_min2_test_01.py` + `er019_family_x_b3_production_wiring_01_test_01.py` = **79 passed**(新規18件+既存61件)。
- dry-run(モック)実測: cost_log_dryrun.jsonl 7行全てが`dry_run_stub`(B3 4 + W-1 stub 3)、実API呼出0、実費0円。3件採用(F04,F11,合成F01)の産物もproducer・契約検証V1-V10を通ることをC1のwriter probe(stub)で確認。**stub応答は合成であり、実LLMの挙動の根拠ではない**。

Phase Aの制約・既知のTrial限定事項:
- 補完Factは4テストの回答が除外側になりうるため、Productionの`SELECTED_DESPITE_ALL_TESTS_EXCLUDE` soft warningが出る可能性がある(evidence記録のみで採用数/retry/STOPに不使用=Production仕様どおり)。評価では【背景補完】付きFactの警告は想定内として扱う。
- `selected_fact_ids`順=Writerの【事実N】順(`_ordered`の"selected"順)。補完Factが末尾に来るとWriterが補足扱いにする可能性があるが、順序は指示しない(観測対象)。
- `cap_of(n)=max(3,min(6,n//2))`(数値印の中核上限)はFact数nに依存するが、n=2→3、n=3→3、n=4→3 で本件では不変。

## §4 評価rubric(Phase B。盲検比較)

評価単位: ①B3選定レベル(`comparison.md`: 採用/不採用・reason・【背景確認】note)、②有望候補のみ下流JA記事(W-1の`revision2.md`)。評価者=Sonnet(別セッション/別Agent)。入力=`blind_pack.md`(候補名を伏せA/B/..、記事テキスト+採用Fact)+Ledger+本rubric+`comparison.md`の候補名を伏せた版。`blind_key.json`は評価者に渡さない。**Baselineも盲検に混ぜる**(現行`run_mey_01`記事+再走sample)。判定は各軸3回独立(Fableが多数を採用、割れた場合は低い方)。

| 軸 | 維持/良 | 軽微低下/要注意 | 低下/問題 |
|---|---|---|---|
| 1 ストーリー性・エンターテイメント性 | **維持**: 中心事象(Storyline焦点)がBaselineと同一、かつ盲検比較で面白さ・一貫性・読みやすさが同等以上 | **軽微低下**: 焦点は同一だが余計な説明が増え読み味がやや落ちる | **低下**: 焦点が変わる/解説・冗長化/一貫性が崩れる |
| 2 最低限の背景理解 | **改善**: 記事のみを読む読者が、Q1「出来事に関与している主体は(記事上)誰か」Q2「この出来事は何の流れの一部か」に、Baselineより多く、**記事内の根拠付きで**答えられる。追加Factは【背景補完】+必要性1文付き | **同等(適切な不補完)**: 追加なしで、不足が`【背景確認】`で明示され、推測で補っていない(Ledger欠落時の正解) | **低下**: Ledger内に直接述べるFactがあるのに見逃す/不足を黙殺/推測で補う |
| 3 Fact選定の節度 | **問題なし**: 追加0〜2件、全て【背景補完】マーカーと必要性1文付き、Storyline不変、総採用5件以下、補足便利・網羅目的の追加なし | **要注意**: 追加1件の必要性が弱い | **問題**: 3件以上の追加/マーカー無し追加/Storyline変更/総採用6件以上/網羅化 |
| 4 事実性・中立性 | **問題なし**: 記事・Briefの主体帰属・動機・背景の各記述が、同一Factの記述(帰属元を含む)でLedgerに裏付く。文ごとのチェックリストで0件違反 | **要注意**: 帰属元(当局発表・特使評価)の明示が弱い | **問題**: Ledger外の推測/別の出来事のFactから主体・動機を結ぶ/帰属元の消失/動機の創作。**1件でも問題**(許容0) |
| 5 汎用性の見込み | **問題なし**: 仕様文の固有語混入0(機械)、特定Fact ID誘導なし、思考実験2例で他テーマでも副作用が許容範囲 | **要注意**: 手順が当テーマの構造に依存する恐れ | **問題**: 固有語・Fact ID混入、または当テーマを前提とした分岐 |

「有望候補」の定義(委任文どおり): **軸1=維持 かつ 軸2=改善 かつ 軸3・4・5=問題なし**。
補足(Closeout報告用の併記): §1のとおりこのLedgerでは「なぜ」の動機が補完不能なので、軸2の「改善」は紛争の背景(F01相当)の補完でしか達成できない。**軸2=同等(適切な不補完)かつ他軸が問題なし**の候補は「不足明示型」として別枠で併記し、成功/失敗の扱いはFableが判定する(ユーザー§3は「不足を明示し推測しない」を許容しているため)。さらにBaseline再走sampleとの差がばらつきの範囲内か(同じ選定がBaseline再走でも出る=補助指示の効果ではない)を必ず確認する。

機械チェック(評価者の判断に依らない): 採用ID/追加ID/マーカー有無/上限超過/下限2件/Baseline差分/仕様文の固有語混入(`eval`のcomparison.json・spec_generalization_check.json)。

## §5 費用・時間見積(JPY枠150、Fable自律配分)

単価の出典: B3 1回≈7.6円(`MEY_REGEN_02_REPORT_01`の再生成実費)、W-1(R0+R1+R2)≈14.6円(委任文F-1。`run_mey_01/cost.json`のw1_r0/astra_r1/r2合計は3回分の累計のため1回分に換算した値)。総額は`cost.json`のstoryline_b3=20.287(B3 3回分の履歴)と整合。評価・レビューはSonnet/Fableセッションでありこの枠の外(API費用0)。

| 工程 | 内容 | 期待 | 上限(再評価・技術retryを見込む) |
|---|---|---|---|
| R1 | 候補C1,C2,C3のB3×各1call + Baseline再走×1call(並列) | 4×7.6=30.4 | 各最大3call(技術retry1+再評価1)でも実発生確率は低い。budget guardで1callごとに停止 |
| R2 | 有望候補(最大2)の下流W-1×各1 | 2×14.6=29.2 | 29.2 |
| R3 | 改善ループ1周: 候補1〜2本のB3再走+1本W-1 | 7.6〜15.2 + 14.6 = 22.2〜29.8 | 29.8 |
| 追加 | Baselineの下流W-1再走sample(記事ばらつきの対照) | 0(任意) | 14.6 |
| 技術retry/再評価の余裕 | 上記各B3に+1call相当を3回分 | 0 | 22.8 |
| 合計 | | **約82円**(30.4+29.2+22.2) | **約127円**(30.4+29.2+29.8+14.6+22.8)≤ 150 |

- 7-7判定: 各案件見積は300円以下(上限127円)、Fable枠150円内、日次1,000円内。中東記事E2EのCap180とは別勘定で記録(`cost_log.jsonl`は`er083_output/b3_background_fact_trial_01/`、themeタグ`FAMILY_X_B3_BACKGROUND_FACT_TRIAL_01`と`FAMILY_X_FACTLOCK_W1_PRODUCTION_01`)。
- 量産時の追加コスト見込み(参考、採否前): 追記はuser入力に約1,200〜1,500文字(約700〜1,000 input token)増えるのみで、callは増えない(再評価が起きた場合のみ従来どおり)。B3 1回あたり数十銭程度の増加見込み。補完Factが増えるとW-1の入力が増えるがFact 1〜2件分。実測はPhase Bで取得。
- 処理時間: B3は1callあたり約75秒(`runtime_evidence.json` latency 74.4秒)、4候補並列で約1.5分(再評価が起きても約3分)。W-1は1記事あたり約3分(started→finished 3分8秒)。Phase B全体はレビュー待ちを除き約15〜25分。Production追加処理時間の見込みは、callが増えないため実質+数秒(prompt長増)。

## §6 Opus独立レビュー観点案(条件A: 新しい構造・処理フローの設計。5件)

1. **補完指示がストーリー選定を侵食しないか**: 単一call内で「先に選定を完了し、その後確認、選定は変更しない」と文面で逐次性を求めている(C1/C3)。実際には逐次実行は保証されず、C2は選定と同時にTest5を評価する。Storylineの焦点・Factの顔ぶれが補助指示で動くリスクと、その検出方法(Baseline再走との差、Storyline同一性、軸1)が十分か。
2. **「不可欠」の操作的定義**: 「初見の読者が最低限理解するために不可欠」は主観的で、判定者が同一LLM。C3の疑問列挙は定義を操作化できているか。評価者が読者テスト(Q1/Q2)で外部から検証する設計は妥当か。
3. **過剰補完の抑止と4テストとの整合**: 【背景補完】のFactに4テストの「原則除外」を適用しない例外が、ユーザー確定の4テスト(逐語・変更禁止)の趣旨と両立するか。上限2件の根拠、`SELECTED_DESPITE_ALL_TESTS_EXCLUDE` soft warning多発の扱い、`recheck_note`転用(本番化時は専用フィールド=schema変更)の妥当性。
4. **Writer契約・producer検査・下限2件との整合**: 補完Factを`selected_fact_ids`に混在させる方式(Storyline一致検査L732・契約V5/V10・`_ordered`の選定順・`cap_of`)の安全性。下限2件はVERIFIEDのみ算入のため、補完FactがAMBIGUOUSの場合や再評価callでの候補追記の影響。REJECTED済みのSelect-then-Verify/再選定を再導入していないこと(追加callは既存の下限2件再評価のみ)の確認。
5. **汎用性と帰属/動機/背景の区別の信頼性**: 固有語なしの文言で、帰属のみを述べるFactを動機の裏付けにしない・別の出来事のFactから主体を結ばない、がLLMに守られるか。Ledger欠落時の「不足明示」が運用で誤警報/ノイズにならないか。思考実験(経済/科学)の妥当性と、過去テーマ展開(ユーザー確認後)でのリスク。

## §7 E-1(整合確認の記録)

Grep: `CURRENT_SPEC.md`=`B3|Fact選定|下限2件`、`OPEN_ITEMS.md`=`OPEN-420|OPEN-42[0-9]`(末尾OPEN-422、本Trialは新規OPEN-423)、リポジトリ全体=`背景Fact|background fact|文脈Fact|理解に不可欠`。

| 分類 | 対象(ファイル:行) | 内容と本Trialでの扱い |
|---|---|---|
| A(整合・制約) | `CURRENT_SPEC.md:1171` | B3採用Fact下限2件(`APPROVED_FOR_PRODUCTION`、`VERIFIED`のみ算入、再評価1回、REEVAL_STILL_LT2等でSTOP)。**不変**。候補追記は下限2件の指示・再評価noteの後ろに足すのみで、再評価は`run_storyline_b3_selection`に委任 |
| A | `er019_family_x_storyline_b3_fact_selection_01.py:40-44`(4テスト)、`:46-51`(DEVELOPER_MESSAGE)、`:92-106`(再評価note)、`:118-155`(schema) | 全て不変・import再利用。sha一致をtestで固定 |
| A | `er053_b3_deterministic_producer_01.py:717-734`(`_check_inputs`、L732=Storyline一致) | 補完Factを含む産物がproducerを通ることをdry-runで確認。producerは無変更 |
| A | `er053_b3_annotation_contract_01.py`(V1-V10)、`er053_family_x_factlock_ja_writer_01.py:318`(`run_w1_writer`) | writer probeで同一関数を呼ぶ。無変更 |
| A | `OPEN_ITEMS.md` OPEN-420(行932)、`docs/research/FAMILY-X-B3-FACT-MIN2-PRODUCTION-01/{B3_MIN2_DESIGN_01.md,OPUS_REVIEW_F_01_VERBATIM.md,MEY_REGEN_02_REPORT_01.md}` | 下限2件の設計根拠・Opusレビュー・中東記事再生成。ユーザー2026-10-19指示§2に従い、再評価経路の正式runtime evidence未取得をOPEN-420へ追記(別途) |
| B(関連、方式は再利用しない) | `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_FINAL_REPORT_01.md` | 3案とも`REJECTED`(選定後検証+再選定は費用相殺)。**再導入しない**: 本Trialは追加の検証call・再選定callを作らない。callが増える唯一の経路は既存の下限2件再評価 |
| B | `er052_open233_b3_variant_dev_01.py:35-50`(B3 variant V系: 台帳が「未提示/不明」と明記した事項をbrief末尾に「示されていない」と明記/V6「理解に不可欠でない限り省く」) | Fact記述の削減・未提示の明記が目的で、背景Factの追加ではない。Production採否は未確認(本Trialは触れない)。「Ledgerに無い事は書かず不足を示す」という方向は本Trialの【背景確認】不足明示と整合 |
| B | `er037_family_xy_concreteness_control_trial_01.py:96`(A5: 数字は主旨の理解に不可欠なものだけ) | Writer側の数値抑制Trial。別目的 |
| C(無関係) | `CURRENT_SPEC.md:555`(専門語の表: 理解に必要なら保持可)、`DECISION_LOG.md:14964,15045`(`bgroup_B3`=別の意味の「背景」)、`ER-003-A2-00_SPEC_AUDIT.md` 他 | 本Trialと無関係 |

結論: 既存仕様・Gate・REJECTED方式との**矛盾なし**。旧ルール/旧検査の撤去は発生しない(追記のみ・Production無変更)。「背景Fact補完」を直接扱った過去Trialは**ゼロ**(Grep該当は上記B/Cのみ)。
