# Opus独立レビュー#16: OPEN-233 Stage 1再設計(条件A+ユーザー指示による必須、条件B相当、2026-10-05)

管理ID: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(委任_05で保存)
レビュー対象: `docs/pm/design_open233_stage1_redesign_01.md`、`docs/pm/opus_packet_open233_stage1_redesign_01.md`(委任_03)
抽出元: Fableセッション記録(transcript)からOpus出力本文を機械抽出(モデルによる再出力なし)。性質: 読み取り専用の独立レビュー。Production採用可否は判断していない。

# Opus独立技術レビュー#16(条件A+ユーザー指示による必須、条件B相当): OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 Stage 1再設計

表記: 【確認】=ファイル・コードで確かめた事実、【推測】=推論。採用可否は判断しない。実装・修正は開始していない。

## 1. 結論

- **再設計は必要か**: 必要。条件Bの判定は「個別バグの連続」ではなく**根本設計の問題**。RCAの分離結果に同意する。そのうえで、Fable/Sonnet案が見落としている構造上の原因を3つ追加で確認した(1-a〜1-c)。
- **推奨構造**: 案3'単独ではなく、**修正版の3'(以下3'-R)+fact単位の逆方向照合(案5-lite)の2経路∪+F3配線+fail-closedの是正**とする。ループ1では2経路を**同じinstanceで別々に実行**し、経路ごとの検出率・∪の検出率・見逃しの相関を1回の測定で取る。これでFableが案6を後回しにした理由(どちらが効いたか分からなくなる)は解消する。案6はループ1に入れない。必要になってもループ2で案5の次の候補とする。
- **リスク**: (i) 案3'は、neg5型の見逃しを**むしろ悪化させうる**(文単位に分けると、文をまたぐ因果が見えなくなる)。(ii) Stage 1の判定方針(迷ったら許容する、MINORはStage 2へ渡さない)を残したまま判定を強制しても、「OK」が並ぶだけになりやすい。(iii) HF-011のgold扱いが評価ごとに食い違っている(1-c)。(iv) Stage 1のAPI失敗が**PASSに抜ける**経路がある(Safety hole H1)。
- **代替案**: 「文ごとにYes/Noを返す小さなcall」を束ねる案は不採用(費用が増え、前後の文脈を失い、neg5型が悪化する)。既存資産だけでできる最も単純な代替は「V0+V4Aの異なるprompt同士の∪」。¥0 replayで基準線として測る価値はあるが、主軸にはしない(両方とも列挙が途中で止まる性質と、許容寄りの判定方針を持つため)。

### 新たに確認した重要な事実

- **1-a neg5の見逃しは文をまたぐ因果の問題である疑いが強い**【確認+推測】。B3の文は`continued on July 14, so the flashy 20% plan left the stage`で、1文の中で「, so」とつながる(`a_frozen_fresh_01/bgroup_B3/run_1.json` L9)。fresh検出は2/2。neg5は`…continued on July 14. So the flashy 20% plan left the stage.`で、2文に分かれ、2文目が「So」で始まる(`agg_a_frozen.json` L304/L329/L334)。fresh検出は0/2。文を1つずつ切り出すと、各文は単独では真になる(懸念は続いていた/案は消えた)。そのため、**案3'の文単位の判定は、このパターンを構造的に見落としやすい**。
- **1-b Stage 1自体が再現率を下げる設計になっている**【確認】。
  - Promptに「明確にtrueの場合のみMAJOR」「判断に迷う場合は、ほぼ同じ意味を保っているかを最優先」とある(`er003_v1_en_direct_vfl_01_generate.py` L532-537)。developer messageにも「意味が変わらない限り報告しない」とある(L495-499)。
  - 後段へ渡すのはMAJORだけで、MINORは捨てられる(`er052_open233_self_recovery_flow_runner_01.py` L8269)。
  - flagがすべてfalseのMAJORはMINORへ自動降格される(er003 L544-554)。
  - 判定方針を変えずに判定だけ強制しても、迷う文はOKかMINORに落ち、Stage 2へ届かない。
- **1-c HF-011のgold扱いに不整合がある**【確認】。
  - 正式なSafety-critical定義`SAFETY_CRITICAL_CLAIM_DEFS`(runner L9313-9363)にHF-011は**含まれない**。BLOCKING扱いはB3・A2A3-0・A4-0・A5-0・B4-a・B3-same@neg5の6件。
  - REPORTの記載もHF-011を「V0差替えclaim」として、SC定義claimとは区別している(REPORT L4535)。
  - 一方、因果floorのreplayでは、HF-011文のStage 2降格を「**正当な降格**」と数え、止めることを誤停止としている(`replay_guards_04_causal_floor.json` L59-84。bgroup_B2_hormuzが4件)。
  - それなのに、事前評価と設計書の「gold 7文」やSTOP条件案(「7 goldのいずれか<67%」)はHF-011をSafety-criticalとして扱っている。これは「gold・母数の変更禁止」に抵触するおそれがある。HF-011を狙ってStage 1を設計すると、**正式goldではない文への過適合**(V4Aで起きたことの再演)になりうる。
  - 参考: HF-011を検出できているのはV0@6luna 1/2と候補prompt@5.6luna 1/1。V4A@6lunaは0/5前後(`matrix_2x2.json`)【確認、n小】。

## 2. 案別判定

| 案 | 判定 | 一行理由 |
|---|---|---|
| 1 Prompt改善のみ | 不採用 | 網羅を機械で検査できない。ユーザー§2にも反する |
| 2 同一promptの複数回∪ | 不採用 | neg5・HF-011は∪でも0【確認】。負例は66.7%へ悪化 |
| 3 alignmentで文×factの対を列挙 | 不採用 | alignment精度(厳格5/7)に頼り、対にならない文が漏れる |
| 3' 文ID強制分類 | **修正採用(3'-R)** | 列挙途中で止まる型(A4-0、B4非SC)には有効。ただし文またぎ・判定方針・MINOR切り捨てを直さないと、残っている見逃しは閉じない |
| 4 カテゴリ別の機械照合 | 修正採用(**検出ではなく検査**に使う) | 候補を作る用途はL1 0/7・L2 1/7で不適【確認】。LLMの「OK」判定の裏付けを検査する用途に限る |
| 5 fact単位の網羅問い合わせ | **修正採用(5-lite、ループ1から第2経路)** | Ledgerから記事を見る逆方向の照合。3'(記事からLedgerを見る方向)と分析の軸が違うので独立性が高い。neg5のような「原因は何か」を問う形が文またぎに強い【推測】 |
| 6 PASS前の独立安全確認 | 保留(ループ2で案5の次) | 記事全体・SCカテゴリという軸がStage 1と同じで、同じモデル。最も見逃しが相関しやすい。PASSを止める側の確認なので原則上は許容できる |
| 7' 組合せ(F3+3'+6) | 修正採用 | 「F3+3'-R+5-lite」へ差し替える。fail-closedの是正(H1)を前提にする |

## 3. 論点別判定(Fableの10論点)

### 論点1 案3'の保証範囲【修正採用】

- 保証できるのは「全文が判定された」ことまで。判定の正しさは保証できない。この点はSonnetの整理どおり。
- neg5は「判定を強制すれば拾える」型ではなく、文をまたぐ関係の問題(1-a)。兄弟箇所の重複が主因とは考えにくい(B3では同じ内容を拾えている)【推測】。
- HF-011は、gold自体が未確定(1-c)。案3'で改善するという根拠はない。

3'-Rの修正点(すべて決定論で検査できる):
1. **関係単位**: 文頭に因果・照応の語がある文(既存の`CAUSAL_SENTENCE_INITIAL_RE`、runner L3147を再利用。This/That is why等を追加)は、直前の文と組にした単位IDも作り、判定を必須にする。
2. **裏付けのあるOK**: OK(SUPPORTED)には`support_fact_ids`とLedgerからの逐語引用を必須にする。機械が引用の実在を検査し、引用がない・実在しないOKは候補として扱う。
3. **判定方針の分離**: Stage 1から「迷えば許容」を外し、「迷えば候補」に変える。MAJOR/MINORで後段へ渡すかどうかを決めない。重大度の判定はStage 2の責務にする。これはPromptの文言だけの変更ではなく、責務の移動である。
4. **同じ文の判定一致**: 正規化後に同じ文が複数のIDにあれば同じ判定を要求し、食い違えば候補にする(兄弟箇所対策)。

### 論点2 複数の独立経路【採用(2経路∪をループ1の構造に入れる)】

- 単一経路を推す理由は弱い。ループ1で経路ごとに別々に実行すれば、効果の分離もできる。
- 独立性の見込み【推測】:
  - 3'-Rは記事の文→Ledgerの方向。factに紐づかない新規主張に強い。
  - 5-liteはLedgerのfact→記事の方向。原因・主体・数値を問う形で、文またぎに強い。
  - 同じモデルなので、本当に判断が曖昧な文では見逃しが相関する。数値はStage Aの見逃し相関表で測る。
- 費用を抑えるため、5-liteは**3'-Rと同じ単位IDを使う1 call**にする(factごとに複数callに分けない)。

### 論点3 過剰検出とStage 2の吸収【条件付き】

- 「Stage 1は再現率、Stage 2は精度」という分担は、そのままでは成立しない【確認】。理由:
  - S1(第2意見)は「判断が割れたらBLOCKING」で、降格しにくい側に寄せた設計である(L8380-8385)。
  - 決定論floorは5フラグだけで、因果は入っていない(L757-760)。`CAUSAL_FLOOR=False`(L3126)。known6の語彙に「lead to」は無い(L3128)。
  - その結果、誤った候補はBLOCKINGで残りやすく、Rewriteにつながる。一方、本物の因果の重大(B3・neg5)はStage 2の判断頼みになる(Opus#10の懸念と整合)。
- 成立させる条件:
  - (a) E2Eで「誤った候補のうち、最後までBLOCKINGで残った割合」を測る。
  - (b) Rewriteのcycle上限に達してHuman Review/STAGE4へ流れる件数を0件で監視する。
  - (c) 同じ文の重複を除いてからStage 2へ渡す。
  - (d) 候補数に上限は設けない(SCでの見逃しを避けるため)。代わりに費用のworst runを測る。

### 論点4 F3配線【採用(¥0)】

- precheckの候補はStage 2を経由せず、直接BLOCKINGになる(L8363-8375)。24 fixtureで候補1件、それも正しい検出だった【確認】。精度は高いので、Human Reviewへの影響は小さい見込み。
- 3'-Rの「同じ文の判定一致」チェックもPASS記事に対して実行する。
- fail-closedの必須条件はH1(下記)を参照。

### 論点5 案6【保留】

- 原則上は許容できる(PASSを止める側の確認)。ただし独立性が最も低い。ループ1には入れない。

### 論点6 決定論層の到達点【修正採用】

役割は「候補を作る」ではなく「LLMのOK判定を検査する」こと。最小実装は、OK判定の単位について次の場合に候補へ戻す:
- 単位内の数値が、引用されたLedgerの範囲に無い。
- 単位に因果の語があるのに、引用されたfactに因果の記述(`causal_strength`等)が無い。
- 否定の極性が食い違う。
- 正規化後に同じ文なのに判定が違う。

日英の照合が難しいのは数値以外なので、主体名の照合は対象外にとどめる。

### 論点7 採用基準・STOP条件【修正】

設計書§4・§5の案に対して、次のとおり修正を提案する。
- **goldは正式な6件(`SAFETY_CRITICAL_CLAIM_DEFS`のBLOCKING)に限定**する。HF-011はユーザー確認が済むまで監視項目として扱う。
- Stage 1段階の基準: 2経路∪で**6件すべてn=3中3/3**。経路ごとの結果は別々に報告する。
- 過適合の監視: er009合成9種を**調整に使わないhold-out**としてn=1で入れる。
- 「負例MAJOR率58.3%の非悪化」は物差しとして不適。新方式のStage 1はMAJORを出さないため。代わりに次を見る:
  - NORMALの候補数/記事
  - E2Eで誤ってBLOCKINGになった率
  - Rewrite率
  - 費用
- 欠落IDは、再実行後も残ればfail-closedとして計上する。
- 限界も明記する: n=3×6件=18回の試行は「不合格を示す」ことはできても、「見逃し0」を証明できない。

### 論点8 E2E Trial設計【修正】

- 分母(er009合成9種、A2A3/A4/A5/B3/B4、neg1〜5、B2_hormuz、hormuz_run01/02、NORMAL)は妥当。
- ただしE2Eでは、**retry/Rewrite後のRecheckも新しいStage 1仕様で実行する**こと。

### 論点9 Productionでの成立性【条件付き】

- 文の分割は決定論的な関数で行い、hook・1行要約・引用符を区別する(既存の`split_family_x_article_text_v2`の再利用を検討)。
- 単位IDは位置で決まるため、Rewrite後は分割をやり直す。Recheckでは「変更された単位とその前後1単位」を再判定する。Rewriteが起きた記事は、出口前に3'-Rを全文で1回実行する(安全側。費用はE2Eで測る)。
- 全文再生成(regeneration)は最初から実行し直す。
- Opus#15で設計した新module+アダプタの中にStage 1を置き、6経路すべてで同じ仕様にする。アダプタが渡すのは、ledger_text・article_text・source_article_text・セクション情報(hook/本文)。

### 論点10 より単純な代替

- 上記のとおり。「文ごとにYes/Noの小さなcall」は不採用。
- 「V0+V4Aの∪」は¥0 replayの基準線として測るにとどめる。

## 4. Safety hole

- **H1(fail-open)**【確認】: Stage 1のAPIがretryを使い切って失敗すると、`{"overall_status":"LEDGER_DEVIATION","deviations":[],"_stage1_api_failure":True}`が返る(L1727/1768/1818)。このフラグはどこからも読まれていない。そのまま`stage1_deviations=[]`となり、precheckが何も出さなければ、L8447-8458で`RESOLVED_STAGE2_DOWNGRADE`(PASSの状態の1つ、L7864)になる。連続失敗時の停止(circuit breaker)が効くかは未確認。**1回だけの失敗でもPASSに抜けうる。** Trialの前に、失敗時は「PASSにしない・再実行・なお失敗ならSTOP」へ直すことが必須。新moduleでも同じ要件になる。
- **H2**【確認】: MINORが後段へ渡らない(L8269)。Stage 1が重大をMINORに付けた時点で見逃しが確定する。
- **H3**【確認】: 因果は決定論floorの対象外(L757-760、`CAUSAL_FLOOR=False`)。正式SC 6件のうち2件(B3、B3-same@neg5)は因果型で、Stage 2の判断だけに頼っている。
- **H4**【確認】: Stage 1が非検出だと、precheck・floorが走らない(F3、L8203)。

## 5. 残る穴

- 2経路とも同じモデルなので、本当に曖昧な判断では同時に誤る。
- 5-liteは記事全体の文脈やfact間の矛盾が分割の境界にかかると弱い。3'-Rはfactに紐づかない主張には強いが、判断そのものを誤る可能性は残る。
- Ledgerの質に依存する(Ledgerに無い誤りは原理的に拾えない)。
- 見逃し0は原理的に保証できない。目標は「機構ごとに独立した網を重ね、E2Eで矛盾が出ないこと」までと明記すべき。

## 6. ループ1の推奨最小構成と採用基準

**¥0の事前作業(有料実行の前に必須)**
1. fresh 32 runの`all_deviations_raw`を確認し、neg5・A4-0・HF-011の文がMINORとして出ていたかを見る。出ていれば、主因は「MINORを渡さない」ことになる。
2. HF-011のgold扱いを確定する(下記STOP)。
3. H1を是正する。
4. 分割・関係単位・同じ文の一致チェックを全fixtureで決定論的に実行し、gold文が単位IDに対応するか、特にneg5で文の組が作られるかを確認する。
5. V0+V4Aの∪を既存データでreplayし、基準線にする。

**段階A(Stage 1のみ、fresh、promptは実行前に固定)**
- 3'-Rと5-liteを別々に実行する。
- 対象: SC 6 instance+B2_hormuz+負例/NORMAL 6をn=3、er009合成9種をn=1。1経路あたり約48 call、2経路で約96 call。費用は**約¥50〜60**【推測】。
- 合格基準: 正式SC 6件が∪で3/3、hold-outで新たな見逃しなし、欠落IDは再実行で解消。
- 見逃し相関表とNORMALの候補数を記録する。

**段階B(段階Aの合格時のみ、E2E)**
- SC 7 instance+負例6をn=2(約26 run)+B2_hormuz・hormuz_run01/02をn=2。費用は**約¥40〜50**【推測】。
- 測定項目: Human Review/STAGE4、Rewrite率、誤ってBLOCKINGになった率、平均追加費用、worst run。

**ループ1の合計は約¥90〜110**で、残りの予算は約¥130。費用の余裕は小さい: 新Stage 1が約1.0〜1.3円/記事、Stage 2の増分が+0.1〜0.3円で、平均追加は+¥1.4〜1.8程度の見込み【推測】。ただし「追加費用」の基準点(既存のProduction Checker費用を差し引くかどうか)は確認できていない。

**STOP条件(修正案)**
- 正式SCのいずれかが∪で見逃される → E2Eへ進まない。原因の機構を分析する(Prompt追加で追い込まない)。
- hold-outで新たな見逃し → 過適合の疑いとしてSTOP。
- E2EでHuman Reviewまたはworst run ¥3超 → STOP。
- 欠落IDがrunの5%超で残る → STOP。

## 7. STOP条件の該当(PM_GOVERNANCE 11-3節)

**該当する。ユーザー判断が必要。**
- (1) 重要な結論が対立: Sonnet/Fableはループ1を3'単独で進める案。Opusは2経路∪、3'-Rへの修正、案6より案5を優先、を推す。
- (5)/(7) HF-011をSafety-critical goldとして扱うか: 正式定義と因果floor replayのラベル付けが食い違っており、ユーザー承認済みのmateriality基準に照らした確定が要る。
- (3) Stage 1の判定方針を許容寄りから候補寄りへ移すことは、Rewrite・費用とのトレードオフになる。
- 加えて、11-3節L2138の個別指示(OPEN-233は設計とOpus結果が出た時点でユーザーへ報告し、実装・Trialへ進まない)にも該当する。
- H1(fail-open)は、仕様の変更ではなくバグの是正として扱える【推測】。

## 8. 追加Read(合計約6万字の概算)

- `docs/pm/design_open233_stage1_redesign_01.md`全文(案と基準の確認)
- `docs/pm/rca_open233_stage1_checker_01.md`全文
- `er052_output/open233_kpi_recovery_02_offline_01/stage1_redesign_offline_eval_01.md`全文
- `er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01/agg_a_frozen.json` L232-341、L540-640(neg5・HF-011の実文)
- `er052_output/open233_stage1_phase1_recall_check_01/matrix_2x2.json`(V0とV4Aの比較)
- `bgroup_B3/run_1.json`(Grep、「, so」の形)
- `er052_open233_self_recovery_flow_runner_01.py` L757-760、L1672-1731、L3100-3199、L8150-8459、L9300-9389
- `er003_v1_en_direct_vfl_01_generate.py` L495-554
- `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_04_causal_floor.json` L40-149
- `docs/pm/investigation_ledger_deviation_check_01_part_a.md` L200-329(HF-011の経緯)
- `docs/pm/PM_GOVERNANCE.md` L2105-2142
- Grep: `DECISION_LOG.md`・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`・`rep30_stage1_provenance_01.md`のHF-011/neg5該当行

## 9. 答えられなかった点

- fresh runで、neg5・HF-011がMINORとして出ていたか(未確認。¥0事前作業1)。
- Phase1の「cand@6luna」がA構成のV4Aと同一promptか。同一なら、B4-aもfresh 2/2とcell 0/2で揺れており、「安定しているSC」も安定していないことになる。
- 連続失敗時の停止がH1を実際に止めるか。run_instanceのL8459以降と、Stage 2失敗時の経路は読んでいない。
- 案3'-R・5-liteの実際の出力tokenと検出率(未測定。すべて推測)。
- KPI「平均追加+¥2」の基準点。
- rep30実行時のS1・CAUSAL_FLOOR等のスイッチの実際の値(RCAでも未精査と記載)。
