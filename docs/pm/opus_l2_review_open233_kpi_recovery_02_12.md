# Opus独立レビュー#12(条件B/A)保存とFable評価: OPEN-233-KPI-RECOVERY-REDESIGN-02

保存日: 2026-10-04(委任_06)。親: OPEN-233-SELF-RECOVERY-TRIAL-01。Production未変更。

## (1) Opusへの依頼(逐語。委任_06の委任文末尾に記載されていた形式のまま)

注: 委任文には依頼の要旨(論点1〜7)のみが記載されており、依頼packet全文は`docs/pm/opus_packet_open233_kpi_recovery_02_02.md`にある。

[Fableがopus-consultantへ送った依頼。論点1〜7: 1.是正(a)の安全性 2.案N1-aの評価(空DEVIATIONの扱い) 3.neg3/neg2の自己矛盾の根本原因(prior_issues入力の不整合、N3具体化、技術是正か設計変更か) 4.L6の位置づけ 5.残STAGE4経路の棚卸し 6.より単純な方法 7.Production配線。packet: `docs/pm/opus_packet_open233_kpi_recovery_02_02.md`、設計書§12。]

## (2) Opus独立レビュー#12 全文(逐語)

# Opus独立レビュー#12: OPEN-233-KPI-RECOVERY-REDESIGN-02(rep27のHuman Review残3件の是正)

## 結論
- **是正(a)(carry-forwardをL6より先に適用)**: 妥当です。維持してよいです。
- **案N1-a**: 方向は正しいものの、このままでは不十分です。修正版のN1′を推奨します。
  - 欠陥1: N1-aは再確認(Recheck結果が自己矛盾したときに追加で1回呼ぶ確認call)のdeviations(Checkerが返す逸脱指摘)のうちMAJORだけを次cycleへ渡します。このため、再確認が「元指摘は未解消」と答えたのに、その指摘がdeviationsに無い場合、元指摘が消えてしまいます。現行の再確認が防いでいる「静かな降格」を作り直すことになります。
  - 欠陥2: 空のDEVIATIONだけをSTAGE4に残すのは、通常経路より厳しい特別扱いです。根拠が無く、Human Reviewの経路を1本残してしまいます。
- **neg3/neg2の自己矛盾の根本原因**: 設計書§12-2は「入力の不整合は主因でない」としていますが、この推論には誤りがあります。既存データは逆に、「Recheckに書き換え前後の対が無いこと」が主因だという説を強く支持しています(論点3)。
- **条件Bの判定**: neg3の再発(iter5〜rep27で5回)は個別バグの連続ではありません。原因は2つの設計上の問題です。(1)再確認の結果を捨てて、Stage 2(materiality判定)を通さずSTAGE4へ直行させている。(2)Recheckの入力に、`issue`が指している元の文が含まれていない。

## 12観点(要点のみ)
1. 必要か: 是正(a)は必要です(実害2件を確認済み)。N1系も必要です。STAGE4へ直行する現行の扱いは、通常経路と矛盾しています。
2. 単純化: N1′は、`stage1_deviations`を作る規則を1か所変えるだけで済みます。
3. 既存の再利用:
   - 再確認が使っている書き換え前後の対(`before_after_pairs`)を、通常のRecheckにも渡す案があります(N3′、論点3)。
   - 次cycleへ渡す経路・Stage 2・cycle上限は既存のものをそのまま使えます。
4. 情報の喪失: 現行は再確認のdeviationsとprior_issues_resolved(項目別の解消判定)を捨てています。これが今回の穴の正体です。
5. LLM callの追加: N1′・N3′とも追加callは0です。N3′は再確認の発生そのものを減らす見込みです。
6. 非決定性: N1′は増やしません。N2(再確認2回)は増やします。
7. Human Review: N1′で`unconfirmed_after_reverify`の経路自体がなくなります。ただし後述のとおり、別の経路へ移る可能性があります。
8. 不要Rewrite: N1′で、再確認の指摘がBLOCKINGになった場合だけcycle 2のRewriteが増えます。中身は未測定です。
9. コスト: 増えません。
10. retry / fallback / regenerationとの整合: 既存のcycle上限(MAX_CYCLES=2、HARD_MAX_CYCLES=3)の内側に収まります。新しいloopは作りません。
11. 失敗時に安全側へ倒れるか: N1′の条件を守れば倒れます(論点2)。
12. 再発防止: N1′とN3′を組み合わせれば、個別パッチではなく構造的な是正になります。

## 論点1: 是正(a)の安全性
- **他のL6復元への影響**: 新しい判定は「同じcycleに先行Rewriteがある」場合だけ動きます。L6の本来の救済例であるrep24のA2A3 s2 c2とB3 s2 c2は、どちらもcycle 2の事例です(span restore設計書§5-2)。これらは今回の是正の対象外で、引き続きL6が働きます。
- **同じ文を指す2つのclaimが別の問題を指す場合**: 実害は出にくい構造です。runner 8148〜8158行で確認しました。
  - covered扱いになったclaimも`blocking_claims`に含まれたまま、自分の`issue`付きでRecheckの`prior_issues`に入ります。つまり、もう一方の問題は「解消したか」を項目として明示的に検査されます。
  - ただし未解消と判定された後、それがどう流れるかは論点2の欠陥1と同じ穴を通ります。再確認経由だとN1-aでは消えます。通常経路でも、DEVIATIONかつ`all_prior=False`で、その問題がdeviationsに入っていなければ消えます(既存の潜在ギャップ)。
  - したがって、是正(a)の安全性はN1′の「未解消のprior issueを次cycleへ合流させる」とセットで成り立ちます。
- **規則(2)(`restored_equals_after_unit`)**: 同じcycle内のclaimはcycle開始時点の本文に基づいて作られます。先行Rewriteが新しく持ち込んだ問題を指すことはありえないので、誤って適用される余地は小さいです。単独で効いた実例は0件で、合成テストのみです。害は小さいので維持でよいです。

## 論点2: N1-aの評価と代替案
- **N1′(推奨)**: 再確認がCOMPLIANTかつ`all_prior=True`以外の結果を返したら、次の2つを合わせて次cycleのstage1とし、既存のStage 2へ流します(重複はfact_idで除く)。
  - (i) 再確認deviationsのMAJOR
  - (ii) 再確認の`prior_issues_resolved`でresolved=falseになった元のblocking claimのdev
- **(ii)が既存のladder機構に乗ること**: (ii)は元claimそのものなので、既存の`find_matching_prior_record`で一致します。結果は次のどちらかになり、既存のladderに自然に乗ります。
  - まだ段落水準まで試していなければ段落水準へ昇段してRewrite
  - 試行済みなら`same_claim_fact_id_reblocked`
- **空のDEVIATIONの扱い**: (i)(ii)とも空になった場合は、既存の`not blocking_claims`経路でRESOLVED_REWRITE_THEN_DOWNGRADEになります。これは通常経路で「DEVIATIONだがMAJORは0件」のときと同じ扱いです。
  - 安全性の根拠: 全文検査2回(Recheck=COMPLIANT、再確認=MAJORなし)と、cite-or-release(根拠の引用ができない未解消を解除する仕組み)を経た「元指摘は解消」が揃っています。元指摘が静かに消えることはありません。
  - 監査用に`reverify_deviation_without_major=True`を記録するよう追加を推奨します。
- **3条件の判定**:
  - Human Reviewへ逃げない: 満たします。
  - Safety側へ倒れる: 満たします。未解消は必ずStage 2を通り、降格を防ぐ既存のガード(Tier 0・S1)も維持されます。
  - 新しいretry loopを作らない: 満たします。既存の`cycle`を使います。
- **他案との比較**:
  - N1-a: 空のDEVIATIONでHuman Reviewが残り、KPI(Human Review 0)と整合しません。
  - 「もう1回再確認」: N2と同じで、費用と非決定性が増えるだけです。
  - N1-b(ladder次段のRewrite): 問題が指定されていない文を書き換えることになり、不要Rewriteが増えます。
  - 以上により、いずれもN1′より劣ります。
- **残るリスク**:
  - 再確認の指摘がBLOCKINGと判定されれば、cycle 2のRewriteが走ります。ACCEPTABLE記事での不要Rewriteになりえます。
  - Human Reviewが`cycle_limit_exhausted`や`same_claim_fact_id_reblocked`へ移るだけの可能性があります。
  - どちらも次runで、記録専用で追加した逐語ログから測る必要があります。

## 論点3: 自己矛盾が恒常的になる根本原因
- **§12-2の推論の誤り**: §12-2は「現行本文化の後も4/4で自己矛盾した。だから主因ではない」としています。しかし、委任_01の現行本文化こそが「`claim_in_article`=書き換え後、`issue`=書き換え前の欠陥」という不整合を生んでいます(是正前は`claim_in_article`が本文に存在しない、という別の不整合でした)。両方とも不整合なので、この推論で否定できるのは「本文の取り違え」説だけです。
- **より強い証拠(§12-2の対比表6行)**:
  - 6件すべてで、Recheck(前後の対なし)は`all_prior=False`でした。
  - 6件すべてで、再確認(前後の対あり)は`all_prior=True`でした。
  - 自己矛盾は「出来事の継続を残す」正しい書き換え(rep26 s1、rep27 s2)でも出ています。
  - `released_count=0`なので、cite-or-releaseが機械的に解除した結果でもありません。Checker自身が判断を変えています。
  - つまり、解消判定を変えている要因は文面の良し悪しではなく、「`issue`が指す元の文が入力にあるかどうか」だと推定されます(強い推定)。
- **再確認のDEVIATIONが約24%で出る理由**: 解消判定とは別に、全文検査そのものが揺れていることによると考えられます(N1′で扱います)。
- **N3′(具体化)**: Checker本体のPrompt・Schema・判定規則は変えずに、通常のRecheckにも、再確認で既に使っている書き換え前後の対の部分(cite-or-release指示は除く)を同じ形式で渡します(Trial側のみ)。
  - 効けば、neg3/neg2の再確認callの大半(neg3は82%)が不要になります。費用・非決定性とも下がり、再確認の揺れに当たる機会も減ります。
  - リスク: 全instanceのRecheck入力が変わります。前後の対を見て、形だけの書き換えでも「解消」と甘く判定する方向へ動く可能性があります。¥0では検証できないため、次runで382件の自己矛盾率と見逃しを測る必要があります。
- **技術的見解(是正か、設計変更か)**:
  - 「`issue`が参照する元の文を入力に揃える」こと自体は、ユーザーが技術是正とした「Rewrite前の古い文章をCheckerへ渡していた問題」の自然な完結にあたり、不具合是正の延長と言えます。
  - 一方で、Recheckのプロンプトに新しい情報ブロックを足す点は、「Checker Prompt不変」という制約の解釈次第です。
  - 判定の基準や`issue`の文言そのものを書き換える(LLMで書き直す等)のは、Checkerの入力設計の変更にあたり、ユーザー判断事項です。
  - Fableは、N3′がどちらに当たるかを境界事例としてユーザーに確認するのが安全です。
- **先に取れる材料**: 次runで`recheck_prior_issues_resolved`の逐語が取れれば、resolved=falseの理由文から原因を直接確認できます。その確認をN3′より先に行うことを推奨します。

## 論点4: L6をONのまま維持するか
ONのまま維持し、観測を続けることを推奨します。外すべきではありません。
- L6が対象とする失敗の実例(rep24でHuman Review 2件、どちらもcycle 2)をreplayで救済しています。
- 合成ストレス712件で誤復元0件、決定論で追加callも0です。
- rep26・27で救済例が0件だったのは、`violation_span_unverified`が出なかったため(発生率は0.02〜0.05件/run程度)と考えられ、無価値の証拠にはなりません。
- 外すと、`violation_span_unverified`の経路(rep24で2/38)が再び開きます。
- 有害だった相互作用は、是正(a)で除去済みです。

## 論点5: 残STAGE4経路の棚卸し
`stage4_reason`の代入箇所はGrepで全列挙して照合しました(7738・7791・7834・7951・7970・8055・8276・8309行)。棚卸し表と一致しており、漏れはありません。その上で、次の補足があります。
- **(a) 表にない停止経路**: 例外終了(API失敗、連続エラー、予算上限=budget_state)は`stage4_reason`を持ちません。KPI上の「Human Review相当」に数えるのかどうかを定義しておく必要があります。rep27は0件です。
- **(b) N1′導入後の移動先**: N1′を入れると、`unconfirmed_after_reverify`の分が`same_claim_fact_id_reblocked`、`cycle_limit_exhausted(_after_recheck)`へ移る可能性があります。「KPI構成で0件」という評価は、N1′導入後に測り直してください。
- **(c) `ladder_exhausted`の他の原因**: 旧構成の10件(rep16・rep18・rep20・iter8)について、「同じcycleで同じ文を指すclaimが重複していた」型かどうかを、既存ログから¥0で分類できます。L6以外の原因が残っているかを、run前に安く確認できます。
- **`cycle_limit_exhausted`**: 上限は触れないでよいです。ただし(b)のとおり、発生件数は監視対象にしてください。
- **仕分けの妥当性**: 次の仕分けは妥当です。
  - 技術是正で潰せるもの: `unconfirmed_after_reverify`(N1′)、`ladder_exhausted`(是正(a)+分類)
  - 継続観察: `violation_span_unverified`(L6)
  - 旧構成でのみ発生: その他

## 論点6: より単純な方法・既存Evidenceの再利用
- **再確認callの廃止**: 推奨しません。廃止して自己矛盾を直接Stage 2へ流すと、neg3の82%で毎回cycle 2に入り、不要Rewriteが増えます。再確認は、安い判定役として機能しています。
- **最小の組み合わせ**: N1′(追加call 0)を必須とし、N3′は測定付きの任意とします。N3′が効けば、再確認はほとんど呼ばれなくなります。
- **N2**: 不採用でよいです。
- **既存Evidenceの再利用**: 次runは、記録専用で追加した逐語ログを取ることを主目的にすれば、追加費用はほぼ0です。

## 論点7: Production配線時の整合
- Production(`er012`、410〜430行)には、Stage 2・cycle・ladderがそもそもありません(再生成→再検査→不成立ならSTOP)。N1′だけを移植しても成立しません。
- 推奨する方向: 再検査の結果を正規化する純関数を1つ設け、TrialとProductionで共有します。
  - 入力: `(recheck, confirm)`
  - 出力: `PASS` / `NEXT_CYCLE(MAJOR ∪ 未解消prior)` / `STOP`
- Productionが自己回復flowを持たない間は、`NEXT_CYCLE`を`STOP`へ写像します(現行のSTOP相当で、安全側)。
- 自己回復flow全体をProductionへ配線するときに、この関数をそのまま使えば、TrialとProductionで仕様が分岐しません。
- N3′を入れる場合は、Production共通の`build_prior_issues_instruction`(`er003` 678行)をどう扱うかを、この配線と同時に決めてください。
- 採用可否は宣言しません(人間ユーザーのみが決めます)。

## 十分に答えられなかった論点
- 再確認deviationsの中身と、Recheckでresolved=falseになった理由文は未保存です。このため、N1′で不要Rewriteがどれだけ増えるか、N3′がどれだけ効くかは推定にとどまります。
- 通常経路の潜在ギャップ(DEVIATIONかつ`all_prior=False`で、未解消の元指摘がdeviationsに無い場合に脱落する)の実際の発生件数は、未集計です。次runの`recheck_prior_issues_resolved`から¥0で集計できます。

## 追加で読んだファイルと概算文字数
- `docs\pm\design_open233_kpi_recovery_02.md` §12(302〜407行): 約1.6万字
- `er052_open233_self_recovery_flow_runner_01.py`: 8180〜8319行、7690〜7839行、8140〜8164行、7466〜7495行(約1.6万字)。加えて`stage4_reason`と`prior_issues`のGrep
- `docs\pm\design_open233_span_sentence_restore_01.md`: Grepで約30行(約3千字)
- 合計: packetを含め約4.8万字

## (3) Fableの評価(逐語。委任_06の委任文より。変更しない)

- Fableの評価(Opus#12の採否。SSOTへ逐語記録。変更しない):
  1. **是正(a)(carry-forward優先)は維持**(Opus: 妥当)。規則(2)も維持。
  2. **N1′を採用**(N1-aは不採用): 再確認が「COMPLIANT∧all_prior=True」以外を返したら、(i)再確認deviationsのMAJOR ∪ (ii)再確認`prior_issues_resolved`でresolved=falseの元blocking claim(dev)を、fact_idで重複除去して次cycleのstage1_deviationsとし、既存Stage 2(Tier 0/S1含む)→Rewriteへ流す。(ii)は既存`find_matching_prior_record`でladderに乗る。(i)(ii)とも空なら既存`not blocking_claims`経路でRESOLVED_REWRITE_THEN_DOWNGRADE(監査用`reverify_deviation_without_major=True`を記録)。`unconfirmed_after_reverify`のSTAGE4経路は廃止。追加call 0、既存cycle上限の内側。
  3. **通常経路の潜在ギャップも同時に是正**: 通常のRecheckが`DEVIATION∧all_prior=False`で、未解消のprior issueがdeviationsに無い場合も、(ii)と同じく元claimを次cycleへ合流させる(Opus論点1・2の指摘。構造を1規則に統一: 「未解消のprior issueは必ず次cycleのStage 2を通る」)。
  4. **N3′を技術是正として採用(スイッチ付き、A/Bで効果測定)**: 通常のRecheckにも、再確認が既に使っている「書き換え前後の対」ブロック(cite-or-release指示は除く)を同じ形式で渡す。根拠: ユーザー指示(KPI-RECOVERY-02)は「Promptや入力設計の改善余地がある」をUSER_DECISION_REQUIREDではないと明記し、「Rewrite前の古い文章をCheckerへ渡していた問題」を技術是正としている。N3′はその完結(`issue`が指す元の文を入力に揃える)。Checker本体のPrompt文・Schema・判定規則・`issue`文言は変えない(Trial側で渡す情報ブロックの追加のみ)。境界事例である点はユーザーへ報告する。採用判定はA/B(下記)で、Safety側の悪化(prior issue未解消の取りこぼし)がなく自己矛盾率が下がる場合のみ29件構成に含める。
  5. **L6はONのまま維持・観測継続**(Opus論点4)。
  6. **停止経路の定義**: 例外終了(API失敗・連続エラー・予算上限)で`stage4_reason`を持たないrunも「Human Review相当」としてKPIに数える(rep27は0件)。N1′導入後の移動先(`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`)を監視対象に加える。
  7. **旧構成の`ladder_exhausted` 10件の¥0分類**(同cycle同一文の重複claim型か否か)を実施し、L6以外の原因が残るかを確認。
  8. **N2・再確認callの廃止は不採用**。Production配線は「再検査結果を正規化する純関数(PASS/NEXT_CYCLE/STOP)をTrial/Productionで共有、Productionが自己回復flowを持たない間はNEXT_CYCLE→STOP」の方向を`OPEN-233-A1-PROD`に記録(実装は配線時)。

### PM_GOVERNANCE 11-3「Fableの役割」8項目の照合

| 照合対象 | 結果 |
|---|---|
| Claude案 | 委任_05のN1-a(再確認DEVIATIONのMAJORのみ合流、空はSTAGE4)に対し、Opusは欠陥2点を指摘しN1′を推奨。FableはN1′を採用(N1-aは不採用)。Claude案とOpusの対立はない(Opusの修正採用) |
| Opusレビュー | 評価1〜8のとおり(是正(a)維持・N1′採用・潜在ギャップ是正・N3′採用[スイッチ・A/B]・L6維持・停止経路定義・¥0分類・N2不採用) |
| CURRENT_SPEC.md | 変更なし。Trial側(`er052_open233_*`)のみ。Checker本体Prompt/Schema/判定規則は不変 |
| DECISION_LOG.md | 2026-10-04のユーザー指示(KPI変更禁止・Opusの指摘はFable/Claudeで採否判断・Promptや入力設計の改善余地・古い本文をCheckerへ渡していた問題はUSER_DECISION_REQUIREDではない)の範囲内 |
| OPEN_ITEMS.md | `OPEN-233-KPI-RECOVERY-REDESIGN-02`行のStep 7再ループに対応。新しいUSER_DECISION_REQUIREDなし(N3′の境界性はユーザーへ報告事項) |
| ユーザー承認済み内容 | KPI(Human Review 0件/Safety重大見逃し0件/+¥2/+¥3 Cap)を変更しない。Human Reviewへ倒す新経路を作らない。新しいretry loopなし(`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`不変) |
| QCD | 1重大見逃し0・2 Human Review 0(`unconfirmed_after_reverify`経路の廃止)・3不要Rewriteは測定(A/B・rep28)・4 追加call 0 |
| PM強制Gate | Production採用なし(APPROVED/WIRED不変)。有料実行は費用概算を先出し、母数・採否基準を事前設定して事後変更しない |

### STOP条件(11-3「必ずSTOP」7項目)非該当の根拠

(1) 重要な結論の対立: なし。FableはOpusの推奨(是正(a)維持・N1′・N3′[測定付き]・L6維持・N2不採用)を採用し、N1-aのみ不採用(Opus自身が不十分と評価)。
(2) 新しい仕様・Product原則: なし。KPI・Human Review 0件原則の範囲内。N3′は「Checker入力設計」の境界事例だが、ユーザー指示が「Promptや入力設計の改善余地がある」「Rewrite前の古い文章をCheckerへ渡していた問題」を技術是正と明記しており、Checker本体Prompt文・Schema・判定規則・`issue`文言は不変(情報ブロックの追加のみ)。境界事例である点はユーザーへ報告する。
(3) Safety/QCD上の明確なトレードオフ: なし。N3′採否はA/Bの事前基準(形だけの解消0件・STAGE4/見逃しが増えない)で決め、満たさなければOFF。KPIは緩和しない。
(4) Production正式採用判断: なし(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない)。
(5) 既存のユーザー承認内容の変更: なし。
(6) 予算・Scope・運用方針の変更: なし。Phase残¥258.15、委任_06上限¥35のGuardrail内。
(7) 新しいUSER_DECISION_REQUIRED: なし。

結論: 進行条件7項目をすべて満たすため、Fable判断で次工程(実装・限定A/B・Step 6再確認)へ進む。
