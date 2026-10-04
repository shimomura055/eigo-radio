# OPEN-233-KPI-RECOVERY-REDESIGN-02 設計書(委任_01、設計案の比較のみ・Production未変更・実装なし)

管理ID: `OPEN-233-KPI-RECOVERY-REDESIGN-02`(親`OPEN-233-SELF-RECOVERY-TRIAL-01`)。性質: ユーザー指示(2026-10-04、`DECISION_LOG.md`末尾に逐語記録済み)に基づく設計案の比較。費用¥0(既存instance JSONの走査・オフラインreplay・リポジトリ内の価格表確認のみ。API課金なし)。Trial Status: `IN_PROGRESS`のまま(`VALIDATED`/`USER_DECISION_REQUIRED`には到達していない)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。
KPI(変更・緩和なし): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。
凡例: 「確認」=実データ・コードで直接確認、「推定」=確認値からの試算、「未確認」=今回確認していない。
関連: RCA=`docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`、replay=`er052_output/open233_kpi_recovery_02_offline_01/`、Opus packet=`docs/pm/opus_packet_open233_kpi_recovery_02_01.md`。

## 0. 先に結論

1. **後段(Stage 2)の「1回のAI判定で重大→問題なし/軽微」を禁止する**(RCA §9・§10)。解除の条件を「Checkerの構造化出力+claim文から決定論で決まるクラス」と「それ以外」で分ける。
2. 推奨案**D\***(組み合わせ): (A)決定論クラスGuard `G_H`(Checkerの`changed_causality=true`∧claim文に因果接続語∧ヘッジ語なし)と、`issue_actor`(Checkerのissue文が支払者・責任主体の付与を名指し)に当たるclaimは、Stage 2が非BLOCKINGを返しても**解除不可(BLOCKING固定)**にする。(B)それ以外の降格(Stage 2単独の非BLOCKING)は**2回確認(S1)**で、2回とも非BLOCKINGのときだけ確定する(委任_67/68の案S1。追加call+¥0.08〜0.15/記事程度、q=0/30)。
3. ¥0 replay(既存ログMAJOR 1143件、降格534件): D\*のGuardは、Safety-critical流出10行のうち**9行(B3型7+A2A3-0型2)を決定論で閉じ**、残り1行はrep24 cycle 2のRewrite後本文(S1で対象)。**正当な降格のうち解除不可になるのは7/524件(1.3%)**で、内訳はneg5のB3同一文6件(プロジェクトのv2訂正で正BLOCKING扱い)とneg3の1件。rep24のllm_direct降格68件では2件(neg5のB3同一文)。
4. 説明文混入型(d)5件は**5件とも決定論で解ける**(試作replayで5/5確定、既に確定済み164件への影響0、他の型への影響0)。ただし「長い説明文の残り」の棄却ガードを外すため、under-scope(範囲が狭すぎる)の可能性を、Recheckの後ろ盾で受ける設計(§5)。
5. 強モデル(Sol)は**全面採用しない**。Sol単価は`gpt-6-luna`の正確に20倍で、Stage 2 1callは実測平均¥0.14→Sol換算約¥2.8(p95 約¥5、最大 約¥8)。1callで+¥3のCapを超えうるため、Sol使用は「2回のLuna判定が割れたときの裁定」に限定する案の比較に留める(§7)。
6. 全ての「見通し」は決定論部分のreplayに基づく。**LLM部分(S1の見逃し率、2回目の追加Rewrite率)は既存の測定[q=0/30]の再利用で、新しいTrialは未実施**。KPI達成の確認は委任_03(Step 6)で、同じ構成の実flowで行う。

## 1. 前提(RCAの要約)

RCA(`docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`)の構造的欠陥: (a)判定役がCheckerの指摘を知らない、(b)解除にEvidence要件がない、(c)ACCEPTABLEに追加要件がなく、promptに緩い定義が併存、(d)降格方向は1回判定、(e)因果は決定論floorの外、(f)rubricの個別パッチで再発を止められていない、(g)QUALITYも「Rewriteなし通過」で流出する(流出10行中8行)、(h)reasoning量が少ない回に降格が出る相関、(i)(別問題)Stage 1 recall。

## 2. 後段Safety設計案の比較(A-1)

KPIを維持したまま「AI1回で重大→問題なし」を禁止する案を並べた。表中の数値は§3のreplay(決定論部分)。LLMを含む部分は「推定」と明記。

| 案 | 内容 | 過去の流出10行を閉じるか | 不要Rewriteへの影響(¥0試算) | Human Review | 追加call/費用 | 非決定性 | 運用の複雑さ |
|---|---|---|---|---|---|---|---|
| (i) Ledger fact本文との逐語照合(因果語・主体・数値等) | Ledgerは日本語、claimは英語で、**接続語・述語を逐語で照合できない**(確認)。関連factに日本語の因果語(基づく/ため/により等)があるかで見る派生`G_I`も評価 | `G_I`=7/10(`G_H`と同じ)。discriminationが増えない(関連factは全て因果語を持つ) | `G_I`で8件解除不可(`G_H`は6件+日本語claim3件)=ほぼ同じ | 0のまま | ¥0 | なし | 小 |
| (ii) Checker指摘を仮説として後段に渡す(F5型。反証をLedger逐語引用で) | 反証引用の逐語一致は決定論で検査可 | B3は「Ledgerに協議が理由とある」→反証できず解除不可になる見込み(推定、未実施) | 正当な降格の81%が`basis=none`(確認)=反証引用を出せない自然な推論。解除不可へ倒れ、不要Rewriteが増えるリスク(**未測定**) | 増減不明(Rewrite増経由) | ¥0(同じcall。prompt+約100 token) | 低(1回判定は残る) | 中(Stage 2 prompt/schema変更、再較正必要。Opus#8/#10のpriming懸念) |
| (iii) ACCEPTABLEの条件厳格化(反証引用+claim各要素の根拠) | 満たさなければQUALITY止まり | **QUALITYは「Rewriteなし通過」のため、流出10行中8行(QUALITY)は閉じない**(確認、RCA §6) | ACCEPTABLE降格227件中184件(81%)が`basis=none`=ほぼ全てQUALITYへ(Rewriteは増えない) | 0 | ¥0 | 変わらず | 中 |
| (iv) Major→MinorとMajor→No issueで解除条件を分ける(Minorは反証不要) | Minor=核心保持の根拠引用必須 | **閉じない**(8/10がMinor[QUALITY]経由)。Minorにも根拠(または決定論ガード)が要る | - | 0 | ¥0 | 変わらず | 中 |
| (v) LedgerとChecker根拠を使う決定論Guard | `G_H`=changed_causality∧因果接続語∧ヘッジ語なし、`issue_actor`=issueが主体付与を名指し | `G_H`単独7/10、`issue_actor`単独2/10、**`G_H`∨`issue_actor`=9/10** | 解除不可は524件中7件(1.3%、3種のclaim)。neg5のB3同一文6件(正BLOCKING扱い)+neg3 1件。**NORMAL群で不要確定は0〜1件** | 0(ただしRewriteが成功しないとStage 4へ。§4) | ¥0 | **なし(決定論)** | 小(1関数) |
| (vi) 明示Evidence不足時はMajor維持(schemaに`ledger_citation`必須) | 空・非逐語はBLOCKING | (ii)(iii)と同じ限界 | (ii)と同じ | 0 | ¥0 | 低 | 中(Stage 2 schema変更) |
| (vii) 2回一致(S1)を補助にする | 1回目が非BLOCKINGなら2回目を同条件で呼び、2回とも非BLOCKINGのときだけ確定 | 確率的(p→p²)。決定論では閉じない。単独では不十分(Opus#10) | 2回目のBLOCKING率q=**0/30**(cycle 1 0/24・cycle 2以降 0/6、委任_68測定)。95%上側限界は約10% | 0 | 約+¥0.08〜0.15/記事(rep24: 22 batch/20 instance-run、Stage 2単価実測¥0.14) | 低(2回目が揺れうる) | 小〜中 |
| (viii) reasoning量の少ない解除を要確認にする(補助) | Stage 2の解除候補で単独batchのreasoning<400 tokensなら要確認 | 相関のみ(RCA §7、Safety-critical単独batch: <400は2/3が降格、700以上は1/21)。**安全装置にしない**(因果ではなく、n小) | - | 0 | S1を全解除にするなら不要 | - | - |

### 2-1 比較から言えること(確認できたこと)

- **QUALITYも流出経路**(10行中8行)。したがって「問題なし(ACCEPTABLE)だけを厳格化」(iii)や「Minorは軽く扱う」(iv)は、流出の大半を閉じない。解除の条件は、QUALITY/ACCEPTABLEの区別でなく**「Checker MAJORを非BLOCKINGへ下げる」こと自体**に付ける必要がある。
- Ledgerとの**逐語照合(i)は、日本語Ledger×英語記事では成立しない**。決定論で使えるのはCheckerの構造化出力(flag)とclaim文・issue文の語彙で、Ledger fact本文は「関連factに因果語があるか」程度(識別力なし)。
- 決定論Guardの粗さ: `changed_causality`だけ(`G_B`)では解除不可が138件(26%)で不要Rewriteが増える。`G_C`(causality∨unsupported∨certainty)は降格の92%を止める。いずれも不採用。**接続語+ヘッジ語なしの絞り込み**(`G_H`)が、流出を閉じつつ不要Rewriteをほぼ増やさない境界(§3)。

## 3. ¥0 replay結果(決定論部分、`er052_output/open233_kpi_recovery_02_offline_01/replay_guards_01.py`・`replay_guards_02.py`)

入力: 既存instance JSON 474件(27ディレクトリ)のChecker MAJOR 1143件(Stage 2通過後)。降格(最終非BLOCKING)534件、うちStage 2単独の降格(llm_direct)471件、rep24のllm_direct 68件。Safety-critical流出10行。

| Guard | 流出閉鎖 | 解除不可になる降格(全534のうち、流出を除く) | QUALITY/ACCEPTABLE | unique claim | NORMAL群[neg5除く]の不要Rewrite確定 | neg5(B3同一文) | rep24のllm_direct 68件のうち |
|---|---|---|---|---|---|---|---|
| `G_A` changed_causality∧接続語(core)∧(日本語因果語含む) | 7/10 | 25 | 12/13 | 9 | 4 | 6 | 6 |
| **`G_H`** `G_A`∧ヘッジ語なし(英語claimのみ) | **7/10** | **6** | 3/3 | 2 | **0** | 6 | **2(neg5)** |
| `G_I` `G_H`∧関連factが日本語因果語を持つ | 7/10 | 8(日本語claim含む) | 5/3 | 4 | 0 | 6 | 2 |
| `issue_actor` issue文が主体付与(支払者等)を名指し(英語) | 2/10(A2A3-0) | 1 | 0/1 | 1 | 1(neg3) | 0 | 0 |
| **`D*` = `G_H`∨`issue_actor`** | **9/10** | **7(1.3%)** | 3/4 | 3 | 1(neg3、cycle 2) | 6 | **2** |
| `G_B` changed_causalityのみ | 8/10 | 138 | 84/54 | 62 | 27 | - | 23 |
| `G_C` causality∨unsupported∨certainty | 10/10 | 480 | 270/210 | - | 95 | - | 64 |
| `issue_cause` issue文に因果語(参考) | 8/10 | 105 | 66/39 | 49 | 40 | 11 | 27 |
| recurrence(前cycleBLOCKING→後で降格)(参考) | 1/10 | 81 | 34/47 | 55 | 18 | 0 | 0 |

- **閉じない1行**: rep24 cycle 2のB3(Rewrite後の「so」→「and」版、Checkerは因果と指摘、Stage 2 ACCEPTABLE、reasoning 259)。接続語が消えているため`G_H`に当たらない。S1の対象(決定論では閉じない)。
- `D*`でブロックされる7件の中身(確認): neg5のB3同一文6件(iter5〜7・rep24。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§13-1でプロジェクト自身が「B3と同一文、正BLOCKING維持」と確定済み)、neg3(rep17 cycle 2)「all cargo ... should provide a 20 percent reimbursement」(issue: 貨物を支払者としている=Ledgerが「支払義務者は示されていない」と記録)。いずれも**Safety原則に照らせば止めてよい文**で、「不要Rewrite」と断定できるのはneg3の1件の可能性があるのみ(仮ラベル、下記B)。
- **重要な副次発見(確認)**: neg5のB3同一文は、Stage 2が過去6回(iter5〜7・rep24×2)非BLOCKINGへ降格している。プロジェクトの正解ラベルではBLOCKING維持なので、**実質的な流出は「Safety-critical定義(`SAFETY_CRITICAL_CLAIM_DEFS`)に載っていないneg5」にも起きていた**(KPIの「重大見逃し」計数に未算入)。`SAFETY_CRITICAL_CLAIM_DEFS`へneg5の同一文を追加する測定修正を提案する(新仕様候補、**未実装・要ユーザー判断ではなく計測上の提案**)。
- 英語記事の因果接続語を含む文は、1記事あたり平均0.62文(最大2、ヘッジ語なしは平均0.45、最大2。fixture 29本、`causal_sent`集計)。決定論Guardが対象にする文の数は極めて少なく、後述§6の「causal sentence audit」候補の費用も小さい。

## 4. 不要Rewriteとの両立(B)と推奨案

既存原則「英語学習者に記事の本質について重大な誤解を与えるものだけを止める」を維持する。**「全てMajor固定」は不採用**(rep24でMAJOR 102件中68件が降格=Rewrite嵐。Primary KPIに反する)。

### 4-1 解除不可になる正当降格の仮ラベル(`D*`の7件+S1の見込み)

| 件 | 内容 | 仮ラベル | 根拠 |
|---|---|---|---|
| neg5「So the flashy 20% plan left the stage」×6 | B3と同一文、Ledger HF-007は撤回理由を「協議」と明記 | **止めるべき(不要Rewriteではない)** | プロジェクトREPORT §13-1・委任_33のrubric例1 |
| neg3「all cargo ... should provide a 20 percent reimbursement」×1(cycle 2) | 貨物を支払者として特定。Ledger: 支払義務者は未提示(HF-003) | **止めるべき**(A2A3-0と同型)。ただし記事品質を落とす不要Rewriteの可能性は残る | Rewrite後の再発(cycle 2)で既にRewrite済みの文 |
| S1で追加Rewriteになるclaim | 2回目がBLOCKING | 未測定。q=0/30 | 委任_68 |

### 4-2 推奨案D\*(Opus批判レビュー#11の対象)

**D\*** = (A)決定論クラスGuard(`G_H`∨`issue_actor`)で、該当claimのStage 2解除を禁止(BLOCKING固定、floor_reason新設) + (B)それ以外のStage 2単独の降格にS1(2回確認、降格を確定する側のみ、委任_67設計書§4-2の仕様。判定は`llm_materiality`で比較)。

理由: (1)Stage 2の1回判定が無条件で重大を解除できる構造(RCA §9)を、**決定論クラスは完全に、それ以外は2回一致**で塞ぐ。(2)Checker・Schema・Promptは変更しない(Stage 2側のprompt/schemaも変更しない。(ii)(iii)(vi)は再較正が要るため後段へ回す)。(3)不要Rewriteの追加は仮ラベル上ほぼ0(§3)。(4)非決定性は決定論クラスでゼロ、S1対象のみ。(5)Production複雑度は「Stage 2結果への後処理関数1つ+降格確認1つ」。

**D\*でも閉じない/未確認なもの(正直に)**: (a)`G_H`/`issue_actor`の語彙に当たらない新しい型の重大(S1の確率的保護p→p²のみ)、(b)Stage 1自身のrecall miss(§6、別問題)、(c)Checkerのflag不整合(A2A3-0はissueが「支払者」を名指しなのに`changed_actor`が立たなかった。`issue_actor`はこの不整合をissue文の語彙で拾う補完で、日本語issueにも語彙を持つが網羅は未確認)、(d)Guardで固定BLOCKINGになったclaimのRewriteが成功しない場合のStage 4(Human Review)。neg5・B3の同一claimは過去のRewriteで「so」を「and/while」へ変えて解消している(rep24 cycle 2、確認)が、Gate後の実flowでの解消率は**未測定**。

### 4-3 KPIの見通し(数値、推定を含む)

| KPI | 見通し | 根拠 |
|---|---|---|
| Safety(重大見逃し0) | 既知の流出クラスは決定論で閉じる(Safety-critical流出10行中9行。neg5のB3同一文6件も同じ`G_H`で閉じる)。未知クラスはp→p²(推定: 全体p≈1.6%[1/63]なら約0.03%、B3型のように難しいclaimで8%なら約0.6%[S1のみ])。**0の保証ではなく、Trial規模での再測定が必要**(委任_03) | §3、委任_67設計書§3 |
| Primary(Human Review 0) | 新しいHR経路は追加しない。Rewrite増は7/524(rep24で2/68=約3%)で、成功すればHRにならない。Rewriteが失敗する場合のみStage 4(未測定) | §3 |
| Cost(平均+¥2以内) | **約+¥0.1〜0.3/記事**(S1 22 batch/20 instance-run×Stage 2単価¥0.14≈¥0.15/instance-run、Rewrite増 約¥0.03〜0.05/run。1記事=1〜2 instance runで約¥0.2〜0.5/記事を上限の目安とする)。決定論Guardは¥0 | rep24実測単価¥0.1402、Rewrite単価¥0.5〜0.8(委任_67) |
| Cap(+¥3以内) | worstでも1記事+¥1以下の見込み(全batchがS1+Rewrite 1回追加)。Sol等を使わなければCap超過なし | 同上 |

### 4-4 Opusレビュー前に採用しないもの(再掲)

案(ii)F5型(priming懸念、再較正)、(iii)(iv)(vi)(schema変更・流出の大半[QUALITY経由]を閉じない)、`G_B`/`G_C`(不要Rewrite大量)、recurrence(流出を閉じず81件解除不可)、(viii)(相関のみ)。

## 5. 必須作業5: 説明文混入型(d)5件の解決可能性

出典: `er052_output/open233_span_restore_offline_01/results_01.md`・`u2_position_word_replay_01.md`(型分類)、`er052_output/open233_kpi_recovery_02_offline_01/d_type_dump_01.json`(各件の入力一式)、`d_type_inspect_01.py`、`replay_d_type_01.py`(試作replay、`replay_d_type_01.json`)。5件はいずれも古いChecker(iter3〜rep23)の出力で、現行(rep24〜25)では出ていない。

### 5-1 現在のP-strict-closedの4ガード(runner `vs_explain_split_resolve`、3884〜3990行付近)

(1)断片は記事に逐語・一意(`fragment_not_in_article`/`fragment_multi_match`)、(2)残りの1区間が6語以上なら拒否(`remainder_too_long`、`VS_EXPLAIN_MAX_EN_WORDS=6`)、(3)位置語が名指しする構造要素(見出し・In one line)がどの断片とも重ならなければ拒否(`dangling_position`、U-2(1)で拡張のみ可)、(4)残りが記事の3語以上の逐語・断片の直前直後に隣接なら拒否。

### 5-2 各件の分析

| 件 | Checker `claim_in_article`(逐語、要約) | issue | 記事の該当箇所 | 棄却ガード | 一意に特定できる情報 | 決定論で解けるか | 規則案 | 誤範囲リスク |
|---|---|---|---|---|---|---|---|---|
| D1 neg4_smallbag_div_a2(iter3 c1) | `“Their job is visual. They add a special feeling. They say, ‘This is today’s mood.’” Also: “Large bags are the luggage crew. ... split in their work.”` | なし(旧形式) | 見出し「### ELLE's small-bag examples」段落の末尾3文(記事は`They say, “This is today’s mood.”`)、「### Vogue's wider list of bags」最終段落の後半5文(逐語1箇所) | `fragment_not_in_article`(外側“”の内側のため引用符が‘’に置換され、記事の“”と字形が不一致) | **記事そのもの**。引用符字形を同一視すれば逐語1箇所に一意 | **解ける** | **Q**: 断片が不一致のとき、断片と記事の引用符字形(" ' ‘ ’ “ ” 等)を同一クラスへ写像(文字数不変)して再照合。一意のときだけ採用、範囲は記事側の原文 | 字形だけの差を無視する(語は変えない)。**一意でなければ採用しない**。replay: 確定済み164件への影響0 |
| D2 safety_A4(iter5 c2) | `“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.` | 記事は通話の受け手がAIと話していると信じていたと述べるが、Ledgerは開示なしのテストのみ確認し、受け手の信念は確認していない | 冒頭段落(「An AI called. **That was what people thought as they spoke.** But a human appeared ...」)に断片が逐語1箇所。「opening」は断片を含む構造要素 | `remainder_too_long`(残り14語) | 断片(逐語・一意)+位置語「opening」が名指す要素が**断片を既に含む**(追加不要) | **解ける** | **R**: 残りが(逐語/隣接/対比参照語/数字/閉じていない位置語)のいずれでもない説明文なら、長さだけでは棄却せず捨てる(上限25語) | 範囲は断片のみ(残りは範囲に入らない)。under-scopeはRecheckが拾う。replay: 1文`That was what people thought as they spoke.`のみ |
| D3 hormuz_run03_standard(iter7 c2) | `“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly as a claim about oil prices generally.` | Ledgerが確認するのはBrent先物の値動きで原油価格全般ではない。本文・見出し・要約の広い表現が検証範囲を超える | 本文の1文(逐語1箇所)、見出し`# The Fee Plan Leaves, But High Oil Prices Stay`、`## In one line`直下 | `dangling_position:headline,one_line`、U-2(1)後は`remainder_too_long`(残り17語) | 位置語が**閉じた語彙**(headline/one-line)→構造要素を決定論で取得。断片の核心語`oil prices`が2要素に大小文字無視で含まれる(補助の裏付け。試作では未使用)。issue文も本文・見出し・要約と名指し | **解ける** | **U-2(1)+R**(位置語→構造要素を範囲へ加える+長い説明文の残りを捨てる) | 範囲=断片+headline+one-lineのみ(名指しされた要素そのもの)。replay: 3範囲、いずれも記事に逐語1箇所 |
| D4 safety_A4(rep23 c3) | `“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.` | Ledger(MUSE-HC-006)は訓練済み契約スタッフが一部の通話を担当したと確認するが、バックアップ・フォールバックとしての位置づけは確認していない。日本語原文が既にこの枠組みを使う | 断片1=見出し行`### The human backup plan`、断片2=「But **that backup plan** changed the meaning of the call.」(各逐語1箇所) | `remainder_too_long`(残り8語、`and`は接続詞で通過) | 断片2つが逐語・一意。`backup`は記事内でこの2箇所のみ(単語検索で確認)で、Ledger fact本文にも`バックアップ`なし | **解ける** | **R** | 範囲=断片2つ(見出し行と文中の語句)のみ。L6(完結文復元)が必要なら、断片2の完結文へ拡張される(既存) |
| D5 hormuz_run03_standard(rep9 c2、既知) | `“Oil prices moved briefly, ...”; “oil prices stayed high” (also reflected in the headline).` | Brent先物の値動きを原油価格全般へ一般化 | 本文の1文+要約+見出し | `dangling_position:headline`(U-2(1)で解決) | 位置語`headline`→見出し要素 | **解ける**(委任_66で確認済み) | U-2(1) | 範囲=断片+見出し |

### 5-3 試作replayの結果(確認、`replay_d_type_01.json`)

- 母集団: 既存ログの一意なclaim 182件(確定164・未確定18)。5件の(d)型は**5件とも確定**(Q:1件・R:3件・U-2(1)+R:1件・U-2(1):1件。重複あり)。
- 回帰: 現行P-strict-closedで確定済みのclaimを試作へ通して結果が変わる件数=**0**。他の型(日本語claim・precheck記述・L6対象)の未確定13件は不変。
- 誤範囲検査: 全件で「断片が最終範囲に含まれる」「全範囲が記事に逐語1箇所」。

### 5-4 Opus#7の懸念(説明文が別箇所を指す)への回答と限界(確認/推定)

- **構造上の保証(確認)**: 範囲の源は「逐語・一意の断片」と「名指しされた閉じた構造要素(headline/one-line)」だけで、残りの文字列は範囲に入らない。説明文が別箇所を指していても、起きるのは範囲が狭すぎる(under-scope)ことで、無関係な文を書き換える(wrong-range)ことは構造上起きない。
- under-scopeの後ろ盾(推定、未測定): Rewrite後のRecheckは`prior_issues`(今回の是正で現行本文の置換後の文を渡す)と全文検査で未解消を検出する。見逃す場合は通常のStage 1/Recheckのrecall問題。
- `related_fact_id`のfact本文との照合では、説明文が別箇所を指すかを**排除できない**(Ledger日本語×記事英語のため、語の照合が成立しない。ASCIIの固有名詞・数値のみ部分的に可)。上記の構造上の保証を主、factの固有名詞照合(D3の`Brent`が見出しに無い等)を補助とする。
- 本規則Rが正しく範囲を決められるかの**実flow検証は未実施**(委任_02のStep 5限定確認で、(d)型5件の再現claimを使う)。

## 6. 必須作業6(第二段階): Stage 1 recall改善の低コスト案の比較

Stage 1(Checker)がB3を見逃した例(rep25 B3 s1: V4A単発が非検出→Production V0 baselineへ代替投入、`stage1_recall_miss_substituted=true`)は、後段設計を直しても残る。ユーザー指示どおり「Checker全面2回」は第一候補にしない。既存Evidence: S1-U(union screen、effort high)単価¥0.424〜0.45/screen、追加block 6件(真陽性2・偽陽性3)、安価代替(2×V4A union/S1-D medium/low)は既知recall miss 3件のうち捕捉2/3で、採否条件(全捕捉かつ負例false BLOCK 1件以下)を満たす案なし(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§11-7)。DET-A/B/C(委任_49): 現行Recheck 3/8、現行Stage 1相当 2/10、候補Prompt 4/10(重大)でrecallは検出器・本文で大きく揺れる。

| 案 | 内容 | 追加費用(/記事) | recall改善見込み | Checker Prompt変更 | 備考 |
|---|---|---|---|---|---|
| 6-A Checker入力の改善(Ledger提示順・Safety系factの強調) | Prompt本文は不変、`ledger_text`の並び・注記のみ | ¥0 | 不明(未測定) | なし(入力のみ) | Opus#8の再較正なしでは効果不明 |
| 6-B 決定論pre-checkの拡張(因果接続語・主体・時期) | 記事の因果接続語を含むヘッジなしの文を**必ず確認対象**にする候補生成。英語fixture 29本で平均0.62文/記事(最大2、ヘッジなし0.45文/最大2) | ¥0(候補生成) | B3型(因果の付加)の候補化。**偽陽性の量は後段の安価確認が決める** | なし | 因果接続語は語彙一致のため決定論。neg5型(同一文)もB3として候補になる |
| 6-C 6-Bの候補文だけの安価な補助check(Safety系fact限定) | 候補文(最大2文/記事)とその`related_fact`のみを渡す短いLuna 1 call(入力数百〜1,000 token、reasoningを抑える) | 約¥0.03〜0.08(推定: 現行Stage 2が約¥0.14/9,000入力token、本件は入力1/8〜1/10) | B3型に直接効く。Stage 1が見逃しても補助で拾う(推定) | なし(新規の補助call。Checker本体は不変) | 新しい判定基準を作る性質があり、要Opus確認(Prompt新設) |
| 6-D Stage 1がPASSした場合だけ限定再確認(合格直前検査) | 委任_49実測の再利用。DET-C(候補Prompt)¥0.72/回 | 約¥0.5〜0.7/記事(合格時のみ) | MAJOR 4/10、MINOR 8/10と高recallだが偽陽性・Rewrite増 | 候補Promptは変更に当たる | 費用・不要Rewriteが大きい |
| 6-E 特定risk flagだけ再確認 | `changed_causality`等のflagが立った場合のみ追加確認 | 発火率次第 | Stage 1が検出済みの重大の確認には効くが、**recall missには効かない** | なし | 後段(D\*)の領域 |
| 6-F 既存Ledger構造の再利用 | `causal_strength`・`notes_for_writer`の「〜と書かない」等を決定論で照合 | ¥0 | notes_for_writerに明示的な禁止がある場合に有効。B3のHF-001はnotesで「撤回の原因として記述しない」と明記(確認、RCA §1)。日本語notes×英語記事の照合が必要で語照合は限定的 | なし | 6-Bの候補の優先順位付けに使える |
| 6-G Stage 2/後段Evidenceの利用 | Stage 2が非BLOCKINGにしたclaimのうち、因果・主体の語彙が残るものを再投入 | 小 | D\*(後段)の延長で、Stage 1 miss自体は救えない | なし | - |
| 6-H Checker全面2回(union) | 第一候補にしない(費用ほぼ倍増、Evidence: 2×V4A unionは捕捉2/3、負例false BLOCK 2件) | +約¥0.4〜0.5/記事(S1-U実測) | 2/3 | なし | 比較の参考のみ |

所見: 費用と効果の見込みでは**6-B(決定論候補生成)+6-C(候補文だけの安価な補助check)**が最もQCD比が良いとみられる(**推定、未測定**)。ただし新しい補助callの設計はSafety原則に関わるため、Opus#11で批判レビューを受けてから進める(本委任では実装しない)。

## 7. 強モデル(Sol等)の限定利用の比較前提

### 7-1 価格・モデルIDの確認(リポジトリ内、実行時確認の限界を含む)

| モデル | Input/Cached input/Output($/1M tokens、Standard・Short context) | 出典(リポジトリ内) | 確認日 |
|---|---|---|---|
| `gpt-6-luna`(Stage 2の現行モデル、`s2p.MODEL`) | 0.10 / 0.01 / 0.50 | `DECISION_LOG.md`(GPT-6モデル比較Trialの単価確認、公式`platform.openai.com/docs/pricing`)、`er052_..._stage2_production_01.py` 27〜29行`PRICE_IN/PRICE_CACHED/PRICE_OUT`、`USD_JPY=156.88` | 2026-09-29(`CURRENT_SPEC.md`2333行) |
| `gpt-6-sol` | 2.00 / 0.20 / 10.00 | `docs/pm/design_gpt6_model_comparison_trial_01.md`421行(上記と同じ確認) | 2026-09-29(互換性probe 1 callのみSUCCESS、比較は保留) |
| (参考)`gpt-5.6-sol` | 5.00 / 0.50 / 30.00 | `er005_output/cost_baseline_01/pricing_snapshot.json`(`checked_date` 2026-08-17、旧) | 2026-08-17 |

- `gpt-6-sol`は`gpt-6-luna`の**正確に20倍**(input・cached・outputとも)。reasoning tokenはoutputに含まれる。
- **価格を実行時に取得する仕組みはない**(確認): 価格は各モジュールの定数(`PRICE_IN`等)と`pricing_snapshot.json`(静的な日付付きスナップショット)のみで、環境変数・設定ファイルによる取得はない。公式ページの再取得は今回`curl https://platform.openai.com/docs/pricing`がHTTP 301を返すのみで、本文は取得できなかった(**最新価格は未確認**)。したがって「リポジトリ内で最後に確認された価格(2026-09-29)」に基づく試算とし、Sol Trial前に公式ページで再確認する。
- モデルID: Stage 2=`gpt-6-luna`、Checker=`gpt-6-luna`(GPT-6モデル比較Trialで採用候補)、Sol=`gpt-6-sol`(`gpt-5.6-sol`と同系統)。Opus(Claude Code側)は`claude-opus-5-5`のみ(`PM-OPUS-MODEL-ID-INVENTORY-01`)で、パイプライン(OpenAI)とは別。

### 7-2 費用の逆算(確認+推定)

- Stage 2 1callの実測: rep24 n=45平均¥0.1402(p95 ¥0.2477、最大¥0.4038)、rep23 n=22平均¥0.1432(p95 ¥0.2729、最大¥0.3422)、rep25 n=3平均¥0.1937。同じtoken量でSolを使うと**平均約¥2.8、p95 約¥5、最大約¥8**(単価20倍、推定。Solのreasoning量は未測定)。
- **1回のSol callだけで+¥3のCap(記事あたり)を超えうる**(p95で超過)。全面Sol化は不可(¥2.8/call×解除候補batch)。
- 平均+¥2/記事以内に収めるための発火率: 他の追加費用(S1 ¥0.15、Rewrite増 ¥0.05)を除いた予算約¥1.8を、Sol 1 call(¥2.8)で割ると**1記事あたり平均約0.64 call**が上限。Capは1記事あたりSol 1 callでも超えうるため、実運用は**「1記事で最大1call、reasoningを抑えた設定(effort low)で単価を下げる」**が前提。
- 発火条件の候補: 「D\*のGuardに当たらず、かつ2回のLuna判定が割れた(1/2が非BLOCKING)とき」のみSolで裁定。rep24でGuard非該当の降格候補66件・22 batch。2回目のBLOCKING率q=0/30(委任_68)から、割れる確率は低い(推定0〜約10%)ため、**発火は22 batch×(0〜10%)=0〜2 batch/20 instance-run=0〜0.1 call/run**で、費用は約¥0〜0.3/runにとどまる(推定)。
- 比較Trial設計(実装しない): 条件=D\*+S1を実装した構成でrep24相当の全体(38 instance-run)を回し、S1で割れたclaimをSolで裁定する経路を「ログのみ(判定には使わない)」で記録し、Sol裁定が重大見逃しを閉じるか・不要Rewriteを増やすかを比較。呼び出し数が小さいため費用は推定¥5〜10(Sol 2〜4 call)。**まず後段設計(D\*)の限定確認を優先し、Solは未達の場合の次段**。

## 8. 未確認事項・Opusへの論点・次工程

- 未確認: (1)S1の見逃し率pと2回目のBLOCKING率qの新しい測定(既存q=0/30のみ)、(2)D\*のGuardで固定BLOCKINGにしたclaimのRewrite成功率(実flow)、(3)`issue_actor`語彙の網羅(今回は旧Checkerの1例による語彙。日本語issueへの対応は語彙のみ)、(4)(d)型の規則Q・Rの実flow検証、(5)Solのreasoning量と実単価、(6)公式価格の最新値。
- 次工程(Opus批判レビュー#11→Fable評価→委任_02): D\*の実装(Guard関数+S1)+規則Q/R+(d)型の実flow確認+Step 5限定確認(B3・A2A3・neg5・neg3)。費用概算: 限定確認n=5×(B3・A2A3・neg5・neg3の4 instance)で約¥15〜25(1 instance-run平均¥0.44、S1・Rewrite増を含む)。Phase残¥315.93の範囲内。
- Opusへ(packet参照): (a)`G_H`のヘッジ語除外が「could」付きの危険な因果を通さないか、(b)`issue_actor`のようなissue文の語彙に頼る決定論は妥当か(Checkerのflag不整合の補完として)、(c)S1の全MAJOR解除への適用が、claimごとの難易度による相関でp²より悪化しないか、(d)規則R(長い説明文の残りを捨てる)がunder-scopeでHuman Reviewを増やさないか、(e)neg5をSafety-critical定義へ追加する測定修正、(f)Solを裁定に限定する前提(価格・発火率)の妥当性。

## 9. Opus#11後の設計改善(三層構造)(委任_02。委任文の指示は「§8」だが既存§8[未確認事項]と番号が衝突するため§9とする)

出典: `docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`(Opus#11全文・Fable評価1〜11・PM_GOVERNANCE 11-3の8項目照合・STOP条件非該当)。性質: Trial専用(`er052_open233_*`のみ編集)、`STAGE2_DOWNGRADE_VERIFY`既定OFF、KPI確認構成(`KPI_TRIAL_SWITCHES`)ではON。Production未変更、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。

### 9-1 主構造(Fable評価1: 修正採用)

D\*(G_H∨issue_actor+S1)は主構造にしない。S1(同一prompt2回目)は採用しない(q=0/30は「再現性が高い=判別力が低い」ことでもあり、V5型・neg5型の系統誤りに効かない)。三層とする。

| 層 | 役割 | 費用 | 失敗時 |
|---|---|---|---|
| Tier 0(決定論Guard、`stage2_release_guard`) | G_L(Ledger構造化欄×Checker flag)+補助ベルト(G_H/issue_actor。既知の型向け、`reason`に`aux:`接頭辞)。該当したら確認役を呼ばずBLOCKING固定 | ¥0 | - |
| Tier 1(確認役、`run_downgrade_verify_call`/`downgrade_verify_evaluate`) | `floor_verify`の一般化。別prompt・別入力で第2の意見を出す。call 1回 | 約¥0.04〜0.05/件(推定、replayで実測) | UPHOLD/引用非逐語/API失敗/schema不一致=BLOCKING |
| Tier 2(失敗時) | 解除不可claimを既存Rewriteラダーへ(`rewrite_hint`はCheckerのissue/explanation+Ledgerのnotes_for_writer/conditionsから決定論で合成、`hint_source`記録)。Human Review・Solへの新経路なし | Rewrite 1回 約¥0.5〜0.8(Opus#11推定) | 既存のcycle上限・ラダー内 |

### 9-2 Tier 0の仕様と¥0 replay結果(Fable評価4・補助ベルト、作業3)

- G_L: (1)changed_causality ∧ Ledger関連factの`causal_strength`∈{CAUSAL_STATED_BY_SOURCE, CORRELATIONAL}、(2)changed_causality ∧ `notes_for_writer`に因果の禁止文、(3)changed_certainty ∧ `notes_for_writer`に断定の禁止文。語彙・閾値は`GL_*`定数。
- 補助ベルト: G_H(英語claim ∧ changed_causality ∧ 因果接続語 ∧ ヘッジ語なし)、issue_actor(英語claim ∧ issue文が支払者・責任主体等を名指し)。委任_01の定義のまま。
- 評価(`er052_output/open233_kpi_recovery_02_offline_01/replay_guards_03_gl.py`・`replay_guards_03_gl.json`・`_stdout.txt`。母集団=Checker MAJOR 1143件、降格534件、流出=Safety-critical旧10行+neg5のB3同一文6行=16行、正当降格=534−16=518件、NORMAL群=110件):

| Guard | 流出閉鎖(旧10/新16) | 正当降格のBLOCKING化(件/率) | NORMAL群(件/率) |
|---|---|---|---|
| G_L | 10/10・16/16 | 108件・20.8%(QUALITY 68・ACCEPTABLE 40) | 12/110・10.9% |
| G_L(causal_strength項のみ) | 8/10・14/16 | 89件・17.2% | 12/110・10.9% |
| G_L(notes禁止文項のみ) | 2/10・2/16 | 19件・3.7% | 0 |
| G_H | 7/10・13/16 | 0 | 0 |
| issue_actor | 2/10・2/16 | 1件・0.2% | 1・0.9% |
| 補助ベルト(G_H∨issue_actor) | 9/10・15/16 | 1件・0.2% | 1・0.9% |
| G_B(参考: causality flagのみ) | 8/10・14/16 | 132件・25.5% | 27/110・24.6% |
| Tier 0全体(G_L∨補助) | 10/10・16/16 | 109件・21.0% | 13/110・11.8% |

- 判定: 事前基準の文面(「正当降格BLOCKING化>5%かつ閉鎖の上積みなし」で不採用)では、G_Lは補助ベルトに対し1行(rep24 cycle 2のB3「and」版)の上積みがあるため「採用」となる。しかし(1)G_Lの正当降格BLOCKING化(20.8%)はG_B(25.5%)に近く、「G_B並みに広ければ不採用」(Fable評価4)に近い、(2)確認役replayの採否基準(ii)[NORMAL群のBLOCKING化率≤10%]はTier 0該当分も含むため、G_Lを有効にするとNORMAL群が確認役の前に10.9%となり基準を満たせない、(3)上積み1行は確認役が閉じる見込み(確認役replayで検証)。このため**Tier 0の既定は補助ベルトのみ**とし、runner定数`TIER0_G_L_ENABLED=False`とした。コード・語彙は残し、確認役replayでG_L有効時の反実仮想も併記する。**事前基準の文面と最終判断に差があることをFableへ報告する**(判断はClaude/Sonnet、補助ベルトのみで閉鎖15/16・誤停止0.2%と同じデータでの評価である点も併記)。

### 9-3 Tier 1確認役の仕様(Fable評価2)

- 対象(`downgrade_verify_target`): Checker severity=MAJOR ∧ Stage 2最終materiality∈{QUALITY, ACCEPTABLE}(floor/hook-aware/disclosure-gap適用後の最終値。QUALITYとACCEPTABLEで要件は同一) ∧ `floor_verify`で解放済みでない ∧ precheckでない ∧ Tier 0非該当。
- 入力: 関連factブロック(Ledger逐語、`floor_verify_fact_block`)・claim文(確定範囲)・局所文脈(`build_local_context`)・Checkerのissue(「検証すべき仮説」として提示)。Stage 2本体(1回目)は不変(指摘を見せない=本体の較正を崩さない)。
- 出力schema(`DV_JSON_SCHEMA`): `verdict`(UPHOLD_BLOCKING/RELEASE)+`ledger_citation`(日本語Ledger逐語)+`basis`+`explanation`。
- prompt(`DV_RUBRIC`): 単一定義の短いrubric。「英語学習者に、記事の本質について重大な誤解を与えるものだけを止めます」+正式基準3定義(BLOCKING(a)〜(e)・自然な言い換え/つなぎ=解除)+「迷う場合、引用できない場合、判断できない場合は、UPHOLD_BLOCKING」。V7・R3基底のACCEPTABLE重複定義は持ち込まない(Fable評価9: 本体rubricの統合は次回の計画的再較正に回す=記録)。
- 解除条件: verdict=RELEASE **かつ** 引用が関連factブロックの逐語(`_fv_norm`: 空白・引用符字形の正規化後の包含)のときだけ。逐語引用は「Ledgerと向き合った根拠が監査できる形で残る」ことと捏造引用の排除までの保証で、反証の証明ではない(Opus#11論点3(i)。単独の防波堤にせずTier 0・補助ベルトと併用)。
- 再評価: `run_stage2`は毎cycle呼ばれるため、Guard・確認役は毎cycleの現行本文で再評価する(Rewriteで接続語が消えてGuardを回避されても、確認役が受ける)。

### 9-4 採否基準(Fable事前設定。事後変更しない)と測定計画(作業4・5)

- offline replay(`replay_verify_01.py`、母数固定): Checker MAJOR→Stage 2非BLOCKING 534件+流出10行+neg5のB3同一文6行(Tier 0該当分は確認役を呼ばずBLOCKINGとして集計)。NORMAL群のラベル付き正当降格と流出・neg5行はn=2。指標: (i)流出10行+neg5 6行の閉鎖率=100%必須、(ii)NORMAL群正当降格のBLOCKING化率(UPHOLD+非逐語+失敗)、(iii)全降格のBLOCKING化率、(iv)QUALITY/ACCEPTABLE別・rubric版別、(v)引用非逐語率、(vi)費用、(vii)n=2一致率。
- 判定: (ii)≤10%かつ(i)=100% → 採用して限定確認(rep26)へ。(ii)10〜25% → Tier 0語彙/prompt表現(「迷えばBLOCKING」・引用要件の明確化)の調整を1回だけ試し、対象限定(NORMAL群+流出+neg5)で再replay(≤¥10)。(ii)>25%または(i)<100% → 採用せずFableへ報告(ユーザーへKPI緩和を提案しない)。
- 限定確認(`rep26`): B3・A2A3・neg5・neg3、n=2、`--kpi-trial-config`(STAGE2_DOWNGRADE_VERIFY=ON)。Human Review(STAGE4)0件・重大見逃し0件(旧新両定義)・L6実flow復元・Tier 0/確認役の発火・解除不可claimのRewrite解消率とcycle数・不要Rewrite・費用・JA変更0を確認。
- Rewrite失敗がHuman Reviewを生むと測定で示された場合のみ、Solの限定利用を再検討する(Fable評価8。条件: 1記事1 call、出力上限固定、費用見積りで+¥3超ならRewrite側へ倒す)。

### 9-5 計測の是正(Fable評価6・11)と説明文混入(Fable評価7)

- neg5のB3同一文を`SAFETY_CRITICAL_CLAIM_DEFS`へ登録(`neg5_hormuz_div_a2`、`registered_in`付き=旧定義の集計から分離)。`derive_safety_critical_from_labels()`は正BLOCKINGラベルの`text_substring`を(空白・引用符字形・大小文字の正規化後に)本文に含む他instanceへ定義を複製する(neg5を`B3@derived`として導出することを単体確認)。`safety_critical_dual_summary`が旧値(委任_01まで)と新値(登録+導出の和集合)を並記し、`aggregate_measurements`の`silent_pass_candidate`は旧定義のまま、新定義は`safety_critical_dual`へ。
- 記録: `run_stage2`の各claimへ`section_type_observed`を追加(本文断片が`## In one line`直下・hook・titleに含まれるかの単純包含、記録専用。判定・Hook専用Stage 2への振り分けは不変)。Opus#11補1「In one lineのclaimが`section_type=body`で渡る」点の計測是正。
- 規則Q(引用符字形の同一視、文字数不変、一意のみ採用)・規則U-2(1)(位置語headline/title/heading→見出し行、one-line summary/In one line/one line/summary→`## In one line`直下1行を範囲へ加える。`opening`は対象外)を`vs_explain_split_resolve`(`VS_EXPLAIN_SPLIT`配下、新スイッチなし)に実装。P-strict-closedの4ガードは不変、範囲は拡張のみ。規則R(長い説明文の残りを捨てる)は保留(現行Checkerで発生0、Opus#11の位置手がかり語彙の指摘あり)。既存346行テストの更新は意図した変化のみ: U12(D5型)が棄却→確定、U11の棄却理由がdangling_position→remainder_too_long(棄却は維持)、S8(宙に浮いた見出し名指し)が棄却→確定、新規確定10→11件。

### 9-6 Stage 1 recall(第二段階、Fable評価10。本委任では実装しない。委任_03以降の¥0評価手順)

1. 6-B(決定論候補生成): 記事の文のうち、因果接続語(`AUX_CONN_RE`+広義語彙: since/due to/thanks to/driving/prompted/that is why等)を含み、ヘッジ語を含まない文を候補にする。fixture 29本で0.45文/記事(上限)を偽陽性量の基準にする。
2. 6-F(Ledgerの因果禁止・相関のみの記録): 候補文が参照するfact(固有名詞・数値・日付トークンの一致、日英の表記差は`floor_verify_time_tokens`相当の正規化)のうち、`causal_strength`∈{CORRELATIONAL, CAUSAL_STATED_BY_SOURCE}または`notes_for_writer`に因果の禁止文があるものを残す。
3. 6-B∧6-Fを既存のprecheck経路(`detected_by=="precheck"`は無条件floor)へ候補として入れる案を¥0 replayで評価する。指標: 既知のStage 1 recall miss 3件(bgroup_B2_hormuz・bgroup_B3・hormuz_run02_advanced)の捕捉、fixture 29本の偽陽性(≤0.45文/記事を上限)、precheck floorが無条件BLOCKINGになることによる不要Rewrite見積り。新しいpromptも判定基準も作らない。精度が足りない場合のみ6-C(候補文だけの安価な補助call)へ進む(要Opus確認)。

### 9-7 確認役offline replayの結果と採否判定(委任_02 作業4。判定基準は事前設定どおり、事後変更なし)

出典: `er052_output/open233_kpi_recovery_02_offline_01/replay_verify_01.py`(`--stage probe/main/agg`)、`replay_verify_01_summary.json`・`_calls.jsonl`・`_plan.json`・`_estimate.json`・`_probe_v1_*`。

- 実行条件: 降格534件(NORMAL群110・流出旧10・neg5同一文6・その他408)。Tier 0は補助ベルトのみ(既定、G_L無効)。概算: probe 6件の単価¥0.0999×全件658呼び出し=約¥65.8>¥45のため、委任文どおり「NORMAL群正当降格全件+流出・neg5全件+その他は層化サンプル約200件」へ縮小(449呼び出し、概算約¥44.9)。実測: main ¥32.68(probe v2を含む)+probe v1 ¥0.44=**¥33.12**、呼び出し450件(1件平均¥0.0744)、API失敗0。
- probe v1→v2の修正(mainの前、結果を見て採否基準を変えたものではなく、実装の是正): v1のprobe 6件で(1)引用が離れた行をつなげて非逐語になる(2件)、(2)`DV_RUBRIC`の(b)〜(e)を私が言い換えて(c)を「未確認の主体・原因・断定」まで広げ、基底rubricより厳しくなっていたことが分かったため、(1)引用は連続1か所だけとする要件の明確化、(2)正式基準3定義(BLOCKING(a)〜(e)・QUALITY・ACCEPTABLE)を基底rubricの文言どおりに修正した。v1のprobeは`replay_verify_01_probe_v1_*`へ退避。「調整1回」の枠は消費していない(mainの(ii)は10〜25%帯に入らなかったため調整の対象外)。

| 指標 | 結果 |
|---|---|
| (i) 流出旧10行+neg5 6行の閉鎖(Tier 0 or UPHOLD、1回目) | **15/16**(旧10: 9/10、neg5: 6/6)。開いた1行=rep24 cycle 2のB3「and」版(Rewriteで接続語が消えた文)。確認役は2回ともRELEASE(「andで並べただけで因果を明示していない」)。補助ベルトで閉じた15行は確認役もUPHOLD(補助ベルト非該当でも確認役は流出を閉じる: 独立判別力は高い) |
| (ii) NORMAL群正当降格(110件)のBLOCKING化率 | **47.3%**(52/110: UPHOLD 49・fact block無し2・補助ベルト1)。2回目49.1%。基準の上限10%・調整帯25%のいずれも超過 |
| (iii) 全降格のBLOCKING化率 | 54.6%(178/326、replayの実施分)。正当降格のみ52.6%(163/310) |
| (iv) QUALITY/ACCEPTABLE別 | QUALITY 62.8%(113/180)・ACCEPTABLE 38.5%(50/130)。NORMAL群: QUALITY 55.7%・ACCEPTABLE 32.5%。rubric版別(正当降格): R3''' 49.7%・V4 60.9%・V5 61.3%・V6 53.3%・V7b 52.5% |
| (v) 引用の非逐語率 | 0/439(連続1か所の要件で非逐語は0) |
| (vi) 費用 | 1件平均¥0.0744。rep24の降格対象は1.789件/instance-run→確認役の追加約¥0.13/記事(推定)。解除不可にした分のRewrite追加は約¥0.75/記事(推定、Rewrite1回¥0.8×BLOCKING化率、実測なし)。費用だけならKPI(+¥2/記事)に収まるが、不要Rewrite率が基準を大きく超える |
| (vii) n=2の一致率 | 88.8%(111/125組) |

- **採否判定: 採用しない**(Fable評価5: (ii)>25%または(i)<100%)。(ii)=47.3%>25%、かつ(i)=15/16<100%の両方に該当。ユーザーへKPI緩和は提案しない。限定確認rep26(作業5)は「採用判定のときのみ」のため実行しない(`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`は作成済み・未実行)。
- 反実仮想(Tier 0にG_Lを追加、再集計のみ・追加費用なし): (i)=16/16(G_Lが開いた1行を閉じる)、(ii)=58.2%(G_L自体がNORMAL群12件を固定BLOCKINGにするため悪化)。→ G_Lを足しても基準は満たせない。
- 診断(¥0、既存callの再集計。再設計の手がかりであり本委任では実装しない): NORMAL群の確認役BLOCKING率は、Hook専用Stage 2経路(`stage2_route=hook`)で23/27=85%、title 7/7、承認済みの決定論降格`disclosure_gap_negative_inference_downgrade`で8/9に対し、body経路は19/52=37%、`## In one line`は0/6。確認役の単一定義rubricにHook-aware/title許容がなく、承認済みの別規則(hook-aware・disclosure-gap)の降格も覆している。bodyでも37%で10%には届かない(確認役はCheckerの仮説に同意しやすい=Opus#11が警告したprimingが実測で出た)。
- 再設計の論点(Fableへ): (1)Tier 0補助ベルト単独は流出15/16・正当降格誤停止0.2%(¥0)で、確認役は流出の独立判別力は高い(15/16)が特異度が低い(NORMAL群47%を止める)。(2)開いた1行(「and」版)は、確認役の説明どおり因果を明示していない文であり、ラベルは`text_substring`(flashy 20% plan)の部分文字列一致で付くため「ラベル上の流出」と「実際に重大な誤解を与える文」が一致しているかの確認が要る(KPI定義は変更しない。ユーザー判断事項ではなく、Safety-critical定義の運用確認)。(3)確認役の対象から「Hook/title経路」「承認済みの決定論降格(hook-aware・disclosure-gap)」を除く、確認役のpromptにsection_type別許容を入れる、等はいずれも新しい構造・prompt変更であり条件A(Opus)の対象。


## 10. 再設計ループ1: D*′(Fable判断、委任_03、2026-10-04)

委任_02の実測(確認役=NORMAL群BLOCKING化47.3%で不採用、補助ベルト=流出15/16・誤停止0.2%・¥0、G_L=NORMAL群10.9%)を受けたFableの再設計判断(委任_03の委任文より逐語。変更しない)。

1. **確認役(Tier 1 LLM、Checker指摘を提示)は不採用**: 実測でNORMAL群47.3%・body経路でも37%の正当降格を重大化し、QCD優先3に反する(Opus#11が警告したprimingが実測で確認された)。Hook/title/disclosure_gapの除外でも10%に届かない。再調整は行わない。
2. **G_Lは不採用**: 流出閉鎖の上積みは「and」版1行のみで、NORMAL群10.9%の誤停止はQCD優先3に反する。委任_02のSonnet判断(`TIER0_G_L_ENABLED=False`)を承認。
3. **Tier 0=因果floor(`G_H`の一般化)を主構造として採用**: 既存の機械的安全装置(数値・主体・否定・比較・時期のfloor)と同じ「Checker flag+決定論の文面確認」の構造で、因果(`changed_causality`∧因果接続語∧ヘッジなし)を6番目のfloorとして位置づける。Opus#11の「既知10行に合わせた語彙パッチ」の指摘に対しては、**接続語・ヘッジ語の語彙を流出事例から独立した標準的な言語学的目録から構築**し(例: 結果・理由・目的の接続詞/前置詞/動詞: so, because, since, as, due to, owing to, thanks to, therefore, thus, hence, consequently, as a result, that is why, which is why, led to, leads to, resulted in, caused, causing, drove, driving, prompted, triggered, sparked, forced, made, pushed, fueled, in response to, following[文頭+結果節]等)、**流出16行を見ずに語彙を確定してから**流出閉鎖率と正当降格518件・NORMAL群110件の誤停止率を測る(hold-out相当)。ヘッジ語は「推測・可能性・他者の見解の帰属」(may, might, could, possibly, likely, appears, seems, some say, analysts/officials say, reportedly, is said to, expected to)に限定し、`can`/`would`の扱いはA/B両方を¥0で測って誤停止≤2%かつ閉鎖最大の方を採る。
4. **`issue_actor`は補助ベルトとして残す**(主体の断定。既存floor `changed_actor`の補完)。
5. **Tier 1′=S1**(Opus#10の3修正付き: 第2意見は`run_stage2`の最終`materiality`で比較、対象claimのみのbatch、割れたらBLOCKING、API失敗はBLOCKING、floor_verify解放済みは除外、毎cycle再評価): Tier 0非該当のChecker MAJOR→Stage 2非BLOCKING全件に適用。q=0/30(委任_68)の実測により不要Rewriteを増やさず+¥0.15/記事。役割分担: Tier 0=既知クラス(因果・主体)の決定論保証、S1=偶発的な外れ(rep25型)、系統誤り(rubric起因)は既存のSafety-critical回帰(V7b再較正、0/30・10/10)で捕まえる。
6. **Tier 2=hint合成**(委任_02実装済み)は維持。解除不可claimは必ずRewrite(Human Reviewへ倒さない)。
7. **残り1行(rep24 cycle 2のB3「and」版「…continued on July 14, and the flashy 20% plan left the stage.」)のFable判断**: 正式基準(重大=事実関係の重大な誤解)で**問題なし**(「and」は因果を主張しない。確認役も2回ともRELEASE)。この行がSafety-critical流出に計上されるのは`text_substring`「flashy 20% plan」の部分一致によるラベル付けであり、A4-1(委任_57)と同じく`CORRECT_LABEL_OVERRIDES`で「and版=ACCEPTABLE」を登録して旧値/新値を並記する。この判断はユーザーへ報告し、否認されれば戻す。cycle 2でCheckerがこの文を再指摘したのはprior_issuesの古い本文(`so`)の引用が原因で、委任_01の是正で解消見込み(rep26で確認)。
8. **Opus再レビューは本委任では行わない**: D*′の構造(決定論Guard+S1)はOpus#10(S1の3修正)と#11(Guard+S1を退避案として許容)で既にレビュー済みであり、実測(確認役の特異度不足)に基づく「修正して採用」。Step 6でKPI達成なら、Production採用提案前(条件C)に改めてOpusレビューを入れる。
9. Stage 1 recall(第二段階)は本委任では着手しない(Step 6の結果で未検出があれば次ループ)。

### 10-1 語彙確定(hold-out手順)の証跡(委任_03、確認)

- 語彙(`CAUSAL_CONNECTIVES_EN`78項目・`HEDGE_MARKERS_EN`+帰属型ヘッジ・`HEDGE_CAN_WOULD_EN`)は、流出16行・Checker指摘文・降格534件の文面を見ずに、標準的な言語学的目録(CGEL・Quirk・Halliday & Hasan・PDTB・Levin・Hyland・Palmer、出典は定数のコメントに記載)のみから構築し、評価より前にgit commit `3808f61f`で固定した(評価スクリプト`replay_guards_04_causal_floor.py`の初回実行はその後)。既に委任_01/02で既知だったG_H補助ベルト6語以外は目録由来。
- 評価後に変更してよいのは`can`/`would`のA/Bのみ(実際には評価結果が採用条件を満たさず、語彙は一切変更していない)。

### 10-2 ¥0 hold-out評価の結果(`er052_output/open233_kpi_recovery_02_offline_01/replay_guards_04_causal_floor.json`・`replay_guards_04_stdout.txt`、確認)

母集団: Checker MAJOR 1143件(降格534・流出16[旧10+neg5のB3同一文6]・正当降格518・NORMAL群110[neg5除く])。

| 版 | 流出閉鎖(新16) | 閉鎖(旧10) | 閉鎖(and版除く15) | 正当降格の誤停止 | NORMAL群 |
|---|---|---|---|---|---|
| A(can/would=ヘッジ) | 13/16 | 7/10 | 13/15 | 13件(2.51%)[Q10・A3] | 3件(2.7%) |
| B(can/would≠ヘッジ) | 13/16 | 7/10 | 13/15 | 13件(2.51%) | 3件(2.7%) |
| 既知G_H 6語(参考) | 13/16 | 7/10 | 13/15 | 0件(0%) | 0件(0%) |
| Tier 0全体A(因果floor_A∨issue_actor) | 15/16 | 9/10 | 15/15 | 14件(2.70%) | 4件(3.6%) |
| Tier 0全体G_H6語(G_H∨issue_actor=委任_02補助ベルト) | 15/16 | 9/10 | 15/15 | 1件(0.19%) | 1件(0.9%) |

- 採用条件(誤停止≤2%かつ閉鎖≥15/16「and」版除き15/15)は、因果floor単独(A/B)では**満たさない**(誤停止2.51%>2%。閉鎖13/15はA2A3の主体型2行が因果floorの対象外[`issue_actor`が閉じる]のため、単独では15/15にならない)。A/Bは完全に同値(`can`/`would`を含む該当claimが無い)。Tier 0全体(因果floor_A∨issue_actor)としても誤停止2.70%で不達。
- 語彙拡張(G_H 6語→目録)の**上積みは閉鎖0件、新規誤停止13件**。13件の一致語は`lead to`(6件、同一文「The disappearance of the fee plan did not lead to a large, lasting fall in prices.」を含む[否定文])・`as`(4件)・`caused`(3件)・`makes/make`(1件)。13件は6文の重複で、全てQUALITY/ACCEPTABLEの正当降格。
- Fable事前規則(「満たさない場合は語彙を削らず事実を記録しFableへ報告、Step 5以降へ進まない」)に従い、語彙は削らず、Step 5(rep26)以降の有料実行は行わなかった。

## 11. Tier 0語彙の確定(Fable判断、委任_04、2026-10-04)

委任_03のhold-out評価(`replay_guards_04_causal_floor.json`)を受けたFable判断(逐語):

1. **Tier 0の有効語彙=既知G_H 6語+`issue_actor`**とする。根拠: 事前基準(誤停止≤2%かつ閉鎖15/15)を満たす唯一の構成(誤停止0.19%)。目録由来の拡張語彙は、同じ母集団で閉鎖の上積み0・誤停止+13件(`lead to`6[同一の否定文]、`as`4、`caused`3、`make`1)であり不採用。**語彙を結果を見て削る調整は行わない**(hold-outの趣旨)。拡張語彙の定数はコードに残し、`CAUSAL_FLOOR_VOCAB="known6"`(有効)/`"inventory"`(評価用、無効)で切替。
2. **残存リスクの明示**: 6語は観測された流出クラス(`so`型)を閉じるが、未観測の接続語型の系統誤りには効かない。これはS1(偶発的な外れ)でも閉じないため、**Step 6の結果とともにユーザーへ正直に報告する**(KPI緩和の提案ではなく、Trial規模での達成状況と残存リスクの区別)。目録拡張が誤停止を生んだ事実は、「接続語の有無だけでは因果主張を判別できない(否定scope・多義語)」という知見として記録。
3. Tier 1′ S1・Tier 2 hint・L6・prior_issues現行本文化・NORMAL群2-of-2 OFF・Q/U-2(1)は委任_03の実装のままKPI構成に含める。確認役・G_Lは無効。
4. 「and」版(rep24 cycle 2 B3)=ACCEPTABLEのFable判断は登録済み(ユーザー未確認、否認されれば戻す)。

実装(委任_04): `CAUSAL_FLOOR_VOCAB`(既定`"known6"`)。`causal_floor_guard`は`known6`のとき`AUX_CONN_RE`(so/because/therefore/as a result/led to/leading to)∧`changed_causality`∧`AUX_HEDGE_RE`なし(英語claimのみ)で判定し、`inventory`のとき目録語彙で判定する。`KPI_TRIAL_SWITCHES`に`CAUSAL_FLOOR: True`+`CAUSAL_FLOOR_VOCAB: "known6"`。補助ベルトG_H/issue_actorは従来どおり`stage2_release_guard`の後段で評価される(known6のG_Hは因果floorと同一集合のため、発火理由は`changed_causality_floor`として先に記録される)。Trial専用・Production未配線・`APPROVED_FOR_PRODUCTION`ではない。

## 12. 再設計ループ2(委任_05、2026-10-04): rep27 Human Review 3件のRCAと是正・設計

rep27(委任_04)の結果: Safety 0・Cost達成・Human Review 3件(`safety_A4` s1・`safety_A5` s1=`ladder_exhausted_without_full_rewrite`、`neg3_hormuz_prodrunner_b1b` s1=`unconfirmed_after_reverify`)。

### 12-1 A4 s1・A5 s1: L6とcarry-forwardの順序不整合(確認)と是正(実装済み、¥0)

**RCA(確認、rep27 instance JSON `rewrite_records`)**。cycle内の処理順(runner行番号は是正前の構造、`_run_stage3_cycle`は`er052_open233_self_recovery_flow_runner_01.py`):
1. `_run_stage3_cycle`(7889〜7912行)が、BLOCKING claimを順に`run_stage3_for_claim`へ渡す。各claimへ、cycle開始時点の本文(`cycle_start_en_text`)と、これまでの先行Rewriteの置換単位(`cycle_replaced_units`)を持たせる。
2. `run_stage3_for_claim_spans`は、まず現在の本文でclaim文字列を照合する(`resolve_violation_spans`→`_resolve_claim_string`、5174行)。**`_resolve_claim_string`の内部で、既存の照合(P-strict-closed含む)が`mismatch`のとき、`VS_SENTENCE_RESTORE`ONならL6(`vs_sentence_restore_resolve`、4961行)を試す(5180〜5200行)**。L6が`restored`なら`resolved`で返る。
3. `resolved`にならなかった場合に**だけ**、`carry_forward_resolution`(6316行)が呼ばれる(旧6414〜6415行)。つまり、carry-forwardはL6が復元できなかった場合の後段だった。
4. A4 s1(rep27): claim 0(`MUSE-HC-006`、引用符付き「“Through Muse, ... with users.”」)をL1でRewrite成功(`...exchanges with users.`→`...with the people they called.`)。claim 2(同じ文を**引用符なし**で指摘した別claim)は、先行Rewriteで本文から`...with users.`が消え`mismatch`→**L6が「`...with the people they called.`」(書き換え済みの文)を復元して`resolved`(level=`L6:sentence_restore`)**→2回目のRewrite(`e2_paragraph_rewrite_guard_failed`、`ladder_exhausted_without_full_rewrite=True`)→STAGE4。claim 1・3(`MUSE-HC-010`)も同じ型(claim 3はL6復元の文`...could mean...`をさらにRewriteし成功、不要な二重Rewrite)。A5 s1(`MUSE-HC-012`)も同型(claim 0=L0成功、claim 1=引用符なし版→L6が書き換え済みの文を復元→guard failed→STAGE4)。
5. 対比(rep24、L6 OFF、同じclaim): `mismatch`のまま`carry_forward_resolution`へ進み、`covered_by_earlier_rewrite_in_cycle`(A4の2件・A5の1件)で合格した(rep24 A4 s1=`RESOLVED_REWRITE_THEN_DOWNGRADE`、A5 s1=`RESOLVED_REWRITE`)。**L6を足したことで、carry-forwardが取るはずだった経路をL6が先取りした**(L6の設計書§4は「cycle内の先行Rewrite」を考慮していなかった)。

**是正(決定論、追加call 0)**: `l6_carry_forward_precedence`(新設、`run_stage3_for_claim_spans`から呼ぶ)。確定がL6を含み(`level`に`L6:sentence_restore`)、かつ同cycleに先行Rewriteの置換単位がある場合のみ、L6の結果を採用する前に次を試す。
 - (1)carry-forward判定(`carry_forward_resolution`。cycle開始時点の本文で照合、委任_04の部分一致[同じ指摘の場合]を含む)。全範囲が先行Rewrite済みなら`covered_by_earlier_rewrite_in_cycle`で解決(Rewriteしない)。
 - (2)(1)で確定しない場合でも、L6の復元範囲がすべて同cycleの先行Rewriteの置換後の文(`after_units`)と完全一致するなら、その置換単位のclaimでcovered扱い(`rule=restored_equals_after_unit`、`covered.range`は置換前の単位とし`resolve_prior_issue_text`が置換後の文を引ける)。
 - 未書き換えの範囲が残る(1の`remaining`非空)・先行Rewriteと無関係な文を復元した場合は、従来どおりL6の結果を使う(変えない)。
 - 記録: `handoff.resolution.l6_skipped={"skipped_reason":"carry_forward_precedence","rule":...,"l6_restored_ranges":[...],"sentence_restore":<L6記録>}`。解消の判定は従来どおり全文Recheckが担う(残れば次cycleで再指摘)。L6 OFFなら新コードは通らない(挙動不変)。Checker Prompt・Schema・判定方法・Productionは不変。

**¥0 replay(確認、`er052_output/open233_kpi_recovery_02_offline_01/replay_cf_l6_order_01.py`、出力`replay_cf_l6_order_01.json`・`..._stdout.txt`)**: rep26・rep27のL6が関与する全cycle(cycle開始時点=fixture本文、記録済みclaim・先行Rewriteの成功置換を再現、Rewrite=スタブ)。
 - `safety_A4` s1: claim 2・3とも是正後は`covered_by_earlier_rewrite_in_cycle`(Rewriteなし)。是正前は両方Rewriteが走る。`safety_A5` s1: claim 1が同様に`covered`。**二重Rewriteは解消**(ladder枯渇の入口が消える)。
 - **他のL6復元への影響(正直な記録)**: 委任文の「他の復元が変わらないこと」は満たされない。rep26・rep27で`L6:sentence_restore`が関与した復元(rep26 6記録・rep27 9記録)を再現すると、変わる記録はすべて「同cycleの先行Rewriteが書き換え済みの文を、後続claimのL6が復元して再Rewriteしていた」同型だった: `neg5_hormuz_div_a2`(HF-007。rep26 s1・s2、rep27 s1の3件、旧は`issue_focus_absent_recheck_only`=Rewriteなしだったので挙動差なし)、`safety_er009_changed_number`(F-002。旧は`13 million`の文を再度e2_paragraph_rewriteし成功した**不要な二重Rewrite**、是正後はRewriteしない)、A4(2件)、A5(1件)。先行Rewriteのないcycleで、L6が単独でmismatchを文へ復元した例は、rep26・rep27の証跡内に**存在しなかった**(確認)。`safety_A2A3`の復元は元々carry-forward(`covered`)経由で、変化なし。つまりrep26・27ではL6の復元はすべて「書き換え済みの文」への復元であり、是正後はL6が単独で働く例は実データ上ゼロになる(L6本来の用途=Checkerが文を言い換えた/切り詰めた引用の救済は、このデータでは別経路でカバーされていた、またはcycle 2以降で生じなかった。**推定**: L6の価値は未観測)。
 - 残るリスク(推定): 同じ文を指す2つのclaimが**別の問題**を指す場合、先行Rewriteが一方しか直さないことがある。carry-forwardの完全包含はissueの同一性を問わない(rep22 T3以来の既存仕様、全文Recheckとcycle 2が最終担保)ため、後続の指摘は次cycleで再検出される。cycle 3到達率は§12-3で扱う。

テスト(`TestL6CarryForwardPrecedence`、`er052_open233_self_recovery_flow_runner_01_test_01.py`): A4/A5のrep27実データによる再現(是正後=covered・Rewriteなし/是正前=二重Rewrite/L6 OFF=rep24と同じ/先行Rewriteなしならself L6の結果を使う/規則(2)の一致・不一致)。runner単体608・er052回帰652 pass、全体回帰は基準11件(6 failure+5 error、他の既存失敗)以外の新規なし。

### 12-2 neg3 s1 `unconfirmed_after_reverify`のRCA(¥0。確認と未確認を区別する)

**最重要の確認事項: rep27を含む全ログに、Recheck・再確認(`recheck_confirm`)の「raw応答全文」は保存されていない(確認)**。runnerは`run_recheck`(1712行)・`run_recheck_confirm`(1878行)の応答を、`call_log`へ`overall_status`・`all_prior_issues_resolved`・費用・`prompt_sha256`だけ残し、`prior_issues_resolved`(項目別の解消判定・説明)と再確認の`deviations`は**どこにも記録していなかった**(Recheck本体の`deviations`は`all_deviations_raw.rechecks`に残るが、再確認のものは無い)。API再実行は¥0制約に反するため行わない。したがって「再確認が返したdeviation claim・severity・issueの逐語」は**入手不能**(未確認)であり、claimの仮ラベルは付けられない。代わりに、(a)promptを決定論に再構築して`prompt_sha256`の一致で正しさを検証し、(b)記録済みの値から確定できる事実を全て列挙し、(c)次回runで逐語が残るよう**記録専用の追加**(挙動不変)を入れた。

**(3) 両callのprompt(確認、再構築+SHA一致、`er052_output/open233_kpi_recovery_02_offline_01/rca_neg3_prompt_reconstruct_01.py`・`.json`)**: Recheck・再確認とも、再構築したpromptの`sha256`がcall_logの`prompt_sha256`と**完全一致**(Recheck `2b397a3b...be524`、再確認 `b20a99a6...5b222`)。`prior_issues`は委任_01の是正が効いており(`prior_issue_text_sources=["current_text"]`)、現行本文の置換後の文が渡っている。逐語:

```
- index=0: fact_id=HF-009 | claim_in_article=The fee plan left the stage, but the prices themselves quickly returned. | issue=The sentence describes the events as having quickly returned and as driving oil prices, whereas HF-009 reports that relevant attacks, blockade and tanker-safety concerns continued during the price movement. It changes continued events into returning events and asserts a causal role not established by the Ledger. | explanation=The timing changes from concerns that continued to events that returned, and the sentence adds an unsupported causal link between those events and oil prices.
```

再確認callの末尾に追加された指示(逐語、cite-or-release+Rewrite前後の対):

```
【追加指示: 今回のRewriteで変更された対象文】
以下の文は、前回指摘の解消を試みるために変更されました(未解消判定の参考にしてください):
- before: The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.
  after: The fee plan left the stage, but the prices themselves quickly returned.
```

**prior_issuesの文言がCheckerに「未解消」と誤読させる余地(推定)**: `issue`/`explanation`は**書き換え前の文**(「events ... quickly returned」)の欠陥を述べたまま、`claim_in_article`だけが書き換え後の文になっている(「claim_in_article=書き換え後」+「issue=書き換え前の欠陥」の組)。書き換え後の文にも「quickly returned」が残るため、Checkerが`issue`の語に引きずられ`resolved=false`と答える余地はある(推定、逐語未確認)。ただし、委任_01の是正(現行本文化)後のrep26・rep27でも、neg3は全4 run(rep26 s1・s2、rep27 s1・s2)でRecheckが自己矛盾した(後述)ため、**自己矛盾の主因が`claim_in_article`の本文取り違えでないことは確認**できる(現行本文化では消えていない)。

**(1)Recheck(確認できる値のみ、rep27 neg3 s1 cycle 1)**: `overall_status=LEDGER_COMPLIANT`、記録された`deviations=[]`(`all_deviations_raw.rechecks[0]`)、コードが計算した`all_prior_issues_resolved=False`。`all_prior_issues_resolved`は`len(resolved)==len(prior_issues) and all(resolved)`(runner 1774行、`er003_v1_en_direct_vfl_01_generate.py` 826行と同一式)。`prior_issues`は1件なので、**`prior_issues_resolved[0].resolved=false`、または返却件数が1でない**のどちらか(どちらか不明)。raw応答全文は未保存(未確認)。
**(2)再確認(確認できる値のみ)**: `overall_status=LEDGER_DEVIATION`、`all_prior_issues_resolved=True`(cite-or-release後、`released_count=0`=未解消と答えた項目はなく、Rewrite対象文は解消と判断)。`overall_status`はCheckerのモデル出力(`classify_parsed_result_trial`は`parsed.get("overall_status")`をそのまま返す、`er051_open233_checker_trial_variant_01.py` 175行)で、`deviations`の件数・severity・claim・issueは**未保存**。**したがって「再確認が返したdeviation claimの特定・仮ラベル(重大/軽微/問題なし)」は、本委任では確定できない(未確認)**。「Rewrite後の文への新規指摘/別の文への新規指摘/空(deviationsなしでstatusだけDEVIATION)」のどれかも決められない。
**確認できる傍証**: (i)書き換え後の文`The fee plan left the stage, but the prices themselves quickly returned.`は、Ledger HF-009(「Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻った」)と照合して**問題なし**(私の目視の仮ラベル、正式基準の機械適用ではない)。neg3は`expected_group_label=ACCEPTABLE(Normal群)`の記事であり、本文の他の文(例: `Normally, removing the fee plan would seem likely to calm oil prices.`)に対する新規指摘の余地はあるが、実際の指摘は不明。(ii)同じ書き換え後の文が、rep26 s2(再確認=COMPLIANT・解消)・rep23 s2(再確認=DEVIATION)・rep27 s1(再確認=DEVIATION)で出ており、同一文で再確認の結論が割れた=**Checkerの確認callの非決定性**(確認)。

**(4)対比(確認、各instance JSON)**:

| run | 書き換え後の文(In one line) | regen | Recheck | 再確認 | 結果 |
|---|---|---|---|---|---|
| rep23 s2 | `...but the prices themselves quickly returned.` | あり | COMPLIANT∧all=False | DEVIATION∧True | STAGE4 |
| rep27 s1 | 同上 | あり | 同上 | DEVIATION∧True | STAGE4 |
| rep26 s2 | 同上 | あり | 同上 | COMPLIANT∧True | RESOLVED_REWRITE |
| rep27 s2 | `...but the concerns around oil prices continued—and the prices themselves quickly returned.` | なし | 同上 | COMPLIANT∧True | RESOLVED_REWRITE |
| rep23 s1 | `...events surrounding oil prices continued. The prices themselves quickly returned.` | あり | 同上 | COMPLIANT∧True | RESOLVED_REWRITE |
| rep26 s1 | `...events around oil prices continued, and the prices themselves quickly returned.` | あり | 同上 | COMPLIANT∧True | RESOLVED_REWRITE |

DEVIATIONになった2件はどちらも「継続していた出来事」の言及を**削る**書き換え(`...prices themselves quickly returned.`)で、passした4件のうち3件は出来事の継続を残す書き換え。ただし同じ「削る」書き換えのrep26 s2は再確認=COMPLIANTで通っており、**文面だけでは決まらない**(同一文3件中2件がDEVIATION、n小)。rep27 s1とs2の差は、書き換え後の文が「削る型/残す型」であること(s1はregenを経ても同じ`vocab_difficulty_increased_fragment`で同一文に収束)。

**既存ログ全体の集計(確認、`agg_stage4_reasons_01.py`・`.json`・`_stdout.txt`、instance JSON 521件)**:
- `unconfirmed_after_reverify` 10件(iter3 neg2・neg3、iter4 neg2・neg3、iter5 neg2・neg3、iter6 neg3、rep9 neg3、rep23 neg3、rep27 neg3)。**instanceはneg3(7件)とneg2_meta_refresh_a2(3件)のみ**。
- 再確認結果の型(記録されている範囲): iter3・iter4の4件=再確認も`LEDGER_COMPLIANT∧all_prior=False`(cite-or-release導入前)。iter5以降の6件(neg2 iter5、neg3 iter5・iter6・rep9・rep23・rep27)=`LEDGER_DEVIATION∧all_prior=True`(released 0)。**再確認の`deviations`の中身(claimあり/なし)を記録したログは0件**(記録欠落、今回是正)。
- 自己矛盾(Recheckが`COMPLIANT∧all_prior=False`)の頻度: 全418 Recheck中33回(7.9%)。**neg3は28回中23回、neg2は8回中7回、それ以外は382回中3回(safety_er009_unsupported_new_claim)**。つまり自己矛盾は、委任文の想定する「特異な事象」ではなく、neg3/neg2に**ほぼ恒常的**な応答パターン。再確認を呼んだのはneg3 21回(DEVIATION 5回=24%)・neg2 6回(DEVIATION 1回)。再確認がDEVIATIONになった6件は全て最終的にSTAGE4。
- 仮説(推定、raw未保存のため未確認): neg3/neg2(ACCEPTABLE記事)では、Checkerが`prior_issues_resolved`で「元指摘の趣旨がなお完全には解消していない」と答えつつ、全文の独立した逸脱としては挙げない(`deviations=[]`)状態が常態化しており、再確認は全文を再検査するため、本文の別箇所を新規に指摘する/しない揺れ(約24%)が出ている。
- 記録欠落の是正(今回、記録専用、挙動不変): `cycle_record`へ`recheck_prior_issues_resolved`・`recheck_prior_issues_sent_count`・`recheck_confirm_deviations`(`raw_deviation_record`、MINORを含む全件)・`recheck_confirm_prior_issues_resolved`を追加した(`er052_open233_self_recovery_flow_runner_01.py`、Recheck直後と再確認直後)。次のrunから逐語が残る。

### 12-3 再確認DEVIATIONの処理設計(比較。実装しない。Opus#12後)

**現行(委任_11以来)**: Recheckが自己矛盾(`LEDGER_COMPLIANT∧all_prior=False`、runner 8238行`en_ambiguous`)→再確認1回(`recheck_confirm`)→再確認が`COMPLIANT∧all_prior=True`ならRESOLVED_REWRITE、そうでなければSTAGE4(8276行`unconfirmed_after_reverify`、fail-closed。次cycleの空deviationsによる静かな降格を防ぐ目的)。再確認が返した`deviations`は**捨てている**(8280行の`stage1_deviations`はRecheck本体のdeviationsから作り、再確認のものは使わない)。これがHuman Review 0のKPIに対する構造的な穴: 通常のRecheck→DEVIATIONは、MAJORがStage 2を通ってcycle 2へ進む(Human Reviewへ直行しない)のに、**同じ「全文再検査でDEVIATION」が再確認経由だとStage 2を通らずSTAGE4へ直行する**不整合がある。

**案N1(再確認DEVIATIONを通常のRecheck結果として既存cycle内で処理)**: 再確認が`DEVIATION`なら、`stage1_deviations=[confirm_parsed.deviationsのMAJOR]`として通常のRecheck不成立の経路(8280行以降、`cycle += 1`→Stage 2[Tier 0/S1含む]→Rewrite→Recheck)へ流す。`MAX_CYCLES=2`・`HARD_MAX_CYCLES=3`・same_claim_fact_id_reblocked・extra_cycle等の既存上限は不変。MAJORが空(statusだけDEVIATION)の場合は、(N1-a)従来どおりSTAGE4(fail-closed維持)、または(N1-b)「prior_issuesのrangeに対するladder次段のRewrite」として扱う(新しい処理=複雑化、評価済みの文を問題なしでも書き換える=不要Rewrite増のリスク)。**推奨はN1-a**(空のDEVIATIONの事例は記録欠落のため件数不明)。
**案N2(再確認2回、一致時のみ採用、割れたらDEVIATION側をN1で処理)**: 追加call 1回(再確認の実績は約¥0.20〜0.42/回、本委任の見積り¥0.27)。neg3/neg2は自己矛盾がほぼ恒常的なので、2回目の再確認が事実上毎回走る(neg3 28 Recheck中23回=82%で+¥0.27なら約+¥0.22/neg3 run)。割れた場合の処理は結局N1。N2単独はCheckerの非決定性を平均化するだけで、Stage 2の判定に代わらず根本対策でない。
**案N3(prior_issues文言の明確化)**: `issue`/`explanation`が書き換え前の文の欠陥を述べたまま`claim_in_article`だけ現行本文、という不整合(12-2)を、「この文は修正済みの現行本文です。元の指摘(下記issue)が解消されているかを判定してください」と明示する。Checker本体Prompt・Schemaは不変(`build_prior_issues_instruction`[`er003_v1_en_direct_vfl_01_generate.py` 678行]はProduction共通。変更するならTrial側で追記文だけ足す)。ただし**rep26・rep27で現行本文を渡した後も自己矛盾が続いた**(neg3 4/4 run)ため、効果は未知(主因かどうか未確認)。追加call 0・非決定性を増やさない・不要Rewriteを増やさないが、効かない可能性が高い(推定)。

| 観点 | N1 | N2 | N3 |
|---|---|---|---|
| Human Reviewへの効果(既存の再確認DEVIATION 6件) | 6件とも通常のStage 2へ進む。Stage 2が降格すればRESOLVED_*(neg3はACCEPTABLE記事)、BLOCKING維持ならcycle 2のRewrite。**STAGE4になる経路はcycle 2以降の既存経路に限る**。実測は未(再確認のdeviationsが未保存でreplay不能、次回run後) | 割れた分はN1と同じ。自己矛盾そのもの(neg3 82%)は減らない | 効果不明(本文取り違えは主因でない)。効けば再確認の発生自体が減る |
| Safety | DEVIATION側へ倒す(安全側)。Stage 2は既存どおり判定(Tier 0・S1・Tier 1'含む、降格ガードは不変)。**Human Reviewへ倒す代わりにStage 2へ渡す**=KPIに沿う | 同左 | 変化なし(Checker判定は不変) |
| 不要Rewrite | 再確認の新規指摘が軽微以下ならStage 2で降格しRewriteされない。BLOCKING判定時のみRewrite(降格精度は既存のD\*′構成に依存) | 同左 | 増えない |
| 費用 | 追加call 0(再確認のdeviationsを捨てずに使うだけ)。cycle 2に進む場合のみ既存cycle分(実績: rep24・rep27 計76 run中cycle 2到達9件) | +約¥0.27/再確認(neg3/neg2は事実上毎回) | 0 |
| 非決定性 | 増えない(既存のStage 2を通す) | 増える方向(Checker呼び出しが増える) | 増えない |
| cycle上限との関係 | `MAX_CYCLES=2`・`HARD_MAX_CYCLES=3`の内側。cycle 3到達は実績0件(rep24・rep27)=増加見込みは小(推定) | 同左 | 影響なし |
| Production配線時の整合 | Productionの再検査(`er012_e_family_entertainment_two_level_runner_01.py` 410〜430行)は、再生成後に`COMPLIANT∧all_resolved`でなければSTOP(RuntimeError)で、**再確認callという仕組み自体がTrial専用**(`er003`の`run_deviation_check`にも無い)。N1の配線はProduction再検査経路の設計(再確認callを入れるか、自己矛盾を直接STOPにするか)と一体で決める必要がある。Trial側の変更は`er052_open233_*`の局所(`stage1_deviations`の代入)。**Production配線は本委任の範囲外** | 同左(さらにcallが増える) | `build_prior_issues_instruction`はProduction共通。Trial側のみ追記文を足す場合、Productionへは別判断 |

**推奨: N1(N1-a)を主とし、N3を併用候補とする(N2は不採用)**。根拠: (1)現行の最大の欠陥は「同じ全文再検査のDEVIATIONが、再確認経由だとStage 2を通らずSTAGE4になる」不整合で、N1はそれを既存の通常経路へ合流させる最小の変更(追加call 0・新しいretry loopなし・cycle上限は既存のまま)。(2)Human Review 0のKPIに直接効く唯一の案(再確認DEVIATION 6件をStage 2へ渡す)。(3)Safetyを緩めない(Stage 2は既存の降格ガードのまま、降格しなければRewrite)。(4)N3は追加call 0・リスクなしだが効果が未確認のため、N1実装後にRecheckの自己矛盾率(neg3 82%)が下がるか副次的に観察する位置づけ。(5)N2は費用・非決定性を増やすだけで、割れた場合の処理が結局N1。**未確認のリスク**: N1は再確認のdeviationsの中身(新規指摘がStage 2で降格されるか、BLOCKINGになるか)が未測定。BLOCKINGと判定された場合はcycle 2のRewrite(不要Rewrite増の可能性)になる。実装の前に、委任_06で記録専用の逐語(上記追加)を取るrunが必要(¥0では判定不能)。

**残るSTAGE4経路の棚卸し(確認、`agg_stage4_reasons_01.json`。全521 instance件数。KPI構成=rep24〜27の件数を併記)**:

| 経路(`stage4_reason`) | 発生箇所(runner行) | 全ログ件数 | rep24〜27 | 発生条件 | KPI 0へ向けた扱い |
|---|---|---|---|---|---|
| `violation_span_unverified` | 7951 | 6 | 2(rep24) | claim文字列が本文で確定不能(mismatch/multi/explanatory) | L6で縮小済み(rep27で0件)。ただし12-1のとおり、rep26・27で観測されたL6の復元は全て「同cycleで書き換え済みの文」への復元で、是正後はL6単独で働く実例が無い=L6の価値は未観測。技術是正(継続観察) |
| `ladder_exhausted_without_full_rewrite` | 7970 | 10 | 2(rep27 A4・A5) | 全水準でRewriteのguardが失敗 | **12-1で縮小**。他の発生(rep16 neg3・rep18 A2A3×2・rep20 meta・iter8 3件)は旧構成で原因未分析。KPI構成でL6以外の原因があるかは未測定 |
| `unconfirmed_after_reverify` | 8276 | 10 | 1(rep27 neg3) | 自己矛盾→再確認がCOMPLIANT∧解消でない | **設計(12-3 N1)**。Production配線時は再検査経路と一体で判断 |
| `cycle_limit_exhausted` / `cycle_limit_exhausted_after_recheck` | 7834 / 8309 | 9 / 6 | 0 / 0 | cycle上限超過 | KPI構成で0件。上限は既存の安全装置で変更しない。発生は旧構成(iter3〜6、rep19〜22)の、同じfact_idの別箇所検出の分散 |
| `same_claim_fact_id_reblocked` | 7791 | 23 | 0 | 同一claimがladder昇段後も再発 | KPI構成で0件(旧構成iter・rep14で発生)。未観測 |
| `ja_deviation_unresolved` | 7738 | 12 | 0 | JA側の未解消 | `JA_MODE=english_only`で無効化(KPI構成で0件) |
| `target_not_locatable` | 7951 | 2 | 0 | 対象文が一度も特定できない | iter8の2件のみ。span方式では`violation_span_unverified`へ統合 |
| `degenerate_rewrite_output` | 8055 | 2 | 0 | title/hook/In one lineの消失・極端短縮 | rep9の2件のみ。KPI構成で0件 |

**棚卸しの限界**: 件数はinstance JSONが残る範囲(521件、旧構成を含む)。KPI構成(rep24・26・27、計84 instance-run)のSTAGE4は、`violation_span_unverified` 2・`unconfirmed_after_reverify` 1・`ladder_exhausted_without_full_rewrite` 2の計5件。是正後に残る経路は`unconfirmed_after_reverify`(設計N1)と、未観測の`ladder_exhausted`(L6以外の原因)・`violation_span_unverified`(L6が働かないcase)。Stage 1/API失敗等の例外終了は`run_log`の`exceptions`で別集計(rep27は例外0)。


## 13. Opus#12後の採否と実装仕様(委任_06、2026-10-04): N1′/潜在ギャップ是正/N3′/停止経路定義

Opus#12(`docs/pm/opus_l2_review_open233_kpi_recovery_02_12.md`、全文・Fable評価1〜8逐語)の採否: 是正(a)維持・規則(2)維持、N1-a不採用/N1′採用、通常経路の潜在ギャップを同時是正、N3′を技術是正(スイッチ付き・A/B測定)として採用、L6はON維持、停止経路の統一定義、旧`ladder_exhausted` 10件の¥0分類、N2・再確認call廃止は不採用。KPI(Human Review 0/重大見逃し0/+¥2/Cap+¥3)は不変。Production未変更(`er052_open233_*`のみ)、Checker本体Prompt文・Schema・判定規則・V7b不変、`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`不変、新しいretry loopなし。

### 13-1 N1′: 再検査結果の合流(実装済み、スイッチ`RECHECK_MERGE_UNRESOLVED`、既定OFF、`KPI_TRIAL_SWITCHES`でON)

純関数`normalize_recheck_outcome(recheck, confirm, prior_blocking_claims, prior_issues=None, api_failure_is_stop=False)`(`er052_open233_self_recovery_flow_runner_01.py`、`run_recheck_confirm`の直後)。API呼び出しなし・入力を破壊しない。出力`decision`は`PASS`/`NEXT_CYCLE`/`STOP`。

- `PASS`: Recheckが`LEDGER_COMPLIANT∧all_prior=True`、またはRecheckが自己矛盾(`COMPLIANT∧all_prior=False`)で再確認を呼び、再確認が`COMPLIANT∧all_prior=True`。
- `NEXT_CYCLE`: 上記以外。判定元(自己矛盾で再確認を呼んだ場合は再確認、そうでなければRecheck)について、次cycleの`stage1_deviations`=(i)判定元deviationsのMAJOR ∪ (ii)判定元`prior_issues_resolved`でresolved=falseの元blocking claimのdev。(i)とfact_idが重複する(ii)は除く(`n_dedup_dropped`に計上)。`prior_issues_resolved`に返ってこなかったindexは未解消扱い(fail-closed。API失敗応答=resolved無しなら全priorを合流)。(ii)のdevは、現行本文の置換後の文(`resolve_prior_issue_text`の`current_text`)が単一の文で特定できるときだけ`claim_in_article`をその文へ差し替える(Stage 2/Rewriteが現行本文で位置を引けるように。複数行・特定不能は元の文のまま)。(i)(ii)とも空なら`deviations=[]`で、呼び出し側の既存`not blocking_claims`経路(`RESOLVED_REWRITE_THEN_DOWNGRADE`)へ。再確認経由で空なら監査用`reverify_deviation_without_major=True`(`cycle_record`と`recheck_merge`)。
- `STOP`: `api_failure_is_stop=True`かつ判定元がAPI失敗のときのみ(Production写像用)。Trialは既定False(API失敗は未解消としてNEXT_CYCLEへ合流=従来の「空deviationsで静かに降格」より安全側)。
- runner側: `RECHECK_MERGE_UNRESOLVED`ON時は`unconfirmed_after_reverify`のSTAGE4を行わず、`PASS`以外を`normalize_recheck_outcome`の`deviations`で次cycleへ。JA側MAJORの合流(既存)・`ja_pending_deviation`・cycle上限(`cycle > HARD_MAX_CYCLES`→`cycle_limit_exhausted_after_recheck`)は不変。OFF時は旧挙動(STAGE4`unconfirmed_after_reverify`)。
- 記録: `cycle_record["recheck_merge"]`(`decision`/`source`[recheck|reverify]/`merged_from`[`reverify_major`/`unresolved_prior`/`recheck_major`/`normal_gap`]/`n_merged`/`n_dedup_dropped`/`reverify_deviation_without_major`/`merged_claims`[fact_id・claim・label])。`switches`へ`RECHECK_MERGE_UNRESOLVED`・`RECHECK_BEFORE_AFTER_PAIRS`(ON時のみ)を記録。

### 13-2 通常経路の潜在ギャップ是正(同スイッチ)

通常のRecheckが`LEDGER_DEVIATION∧all_prior=False`で、未解消のprior issueがdeviationsに無い場合も、上記(ii)と同じく元claimを次cycleへ合流する(`merged_from=normal_gap`)。従来(OFF)は、そのprior issueが静かに消え、deviationsが空/無関係なら次cycleで`RESOLVED_REWRITE_THEN_DOWNGRADE`になり得た(Opus論点1・2)。規則は「未解消のprior issueは必ず次cycleのStage 2を通る」の1つに統一。

### 13-3 N3′: 通常Recheckへの書き換え前後の対(実装済み、スイッチ`RECHECK_BEFORE_AFTER_PAIRS`、既定OFF)

`run_recheck(..., before_after_pairs=None)`。スイッチONかつ対が非空のときだけ、prompt末尾の`build_prior_issues_instruction`の直後へ`build_before_after_instruction(pairs)`(再確認が使っているブロックと同一関数・同形式。cite-or-release指示`CITE_OR_RELEASE_INSTRUCTION`は含めない)を追加。Checker本体template(`er051`の`build_trial_prompt_template("V4A")`)・`er003`の`build_prior_issues_instruction`・Schema・判定規則はバイト不変(sha256固定テスト)。`call_log`へ`before_after_block_len`、`cycle_record`へ`recheck_before_after_pairs_n`を記録(prompt sha256は既存)。**境界事例**: 「Checker Prompt不変」の解釈次第の入力情報ブロックの追加。ユーザー指示が「Promptや入力設計の改善余地がある」「Rewrite前の古い文章をCheckerへ渡していた問題」を技術是正としているため、`issue`が指す元の文を入力に揃える完結として採用。判定基準・`issue`文言の書き換えはしない。KPI構成へ含めるかはA/B(§13-6)で決める(事前基準)。

### 13-4 旧構成`ladder_exhausted_without_full_rewrite` 10件の¥0分類(確認、`er052_output/open233_kpi_recovery_02_offline_01/classify_ladder_exhausted_01.py`・`classify_ladder_exhausted_01_stdout.txt`)

instance JSON全走査で`stage4_reason=ladder_exhausted_without_full_rewrite`は10件(rep14 A4、iter8 A4/A5/unsupported_new_claim、rep16 neg3、rep18 A2A3 s1・s2、rep20 meta s2、rep27 A4・A5)。旧ログは`handoff`・cycle開始本文を持たないため、分類は「枯渇したclaimと同cycleの他BLOCKING claimの`claim_text`(引用符除去・正規化)の包含/類似度0.8以上、およびRewrite成否・mechanism・method」による構造的分類(確認できるのは記録された範囲のみ)。

| 型 | 件数 | 該当 | 原因(1行) | KPI構成での扱い |
|---|---|---|---|---|
| (A)同cycleで先行Rewrite済みの文を後続claimが再Rewrite(carry-forward/L6の順序) | 3 | iter8 A5、rep27 A4、rep27 A5 | 先行claimがRewrite成功した文を、後続の重複claimが再度対象にして`e2_paragraph_rewrite_guard_failed` | §12-1の是正(a)で解消済み(rep27の2件は¥0 replayで確認、iter8 A5は同型の推定) |
| (B)旧`paired_ja_en(J-1)`機構のguard失敗(`JA_MODE=paired`時のみ) | 6 | iter8 A4、rep14 A4、rep16 neg3(c2)、rep18 A2A3 s1・s2、rep20 meta s2(c2) | paired(JA+EN同時)のRewriteがguardを通らず全水準枯渇。うち4件(iter8 A4・rep14 A4・rep18 s1・s2)は同cycleに同一文の重複claimを含み両方が枯渇(重複型だがL6/carry-forward順序ではなく、pairedのguard失敗そのもの) | `JA_MODE=english_only`(KPI構成)ではpaired機構を使わないため発生しない(rep24〜27で`paired`の枯渇は0件) |
| (C)その他 | 1 | iter8 `safety_er009_unsupported_new_claim` | title節の`deterministic_delete(rewrite_hint_quote)`がguardを通らない(単一claim・fact_idなし・`JA_MODE=paired`時) | KPI構成のrep24・rep27では同instanceは`RESOLVED_REWRITE`(STAGE4なし、確認)。**L6以外の原因が残る可能性**は1件(旧構成のtitle削除guard)。KPI構成での再発は未観測 |

結論(確認): 10件中、KPI構成(`english_only`)で再発し得るのは(A)の同cycle重複型3件のみで、(a)で是正済み。(B)の6件は機構が無効。(C)の1件はKPI構成で未再現。**L6以外の原因として残るのは(C)のtitle削除guard失敗1件(旧構成)**で、rep28で`ladder_exhausted`が出た場合は(C)型を疑う。

### 13-5 停止経路の統一定義(Fable評価6)

「Human Review相当」=最終`STAGE4_ESCALATION`(`stage4_reason`全種)+例外終了(API失敗・連続エラー・予算上限・`TrialAbort`でinstance JSONが残らないrun)。rep28集計で`stage4_reason`別件数+例外件数を併記する。N1′導入後の移動先(`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`/`cycle_limit_exhausted_after_recheck`)を監視対象に加える(旧`unconfirmed_after_reverify`はON構成では発生しない)。

### 13-6 A/Bの事前基準(委任_06 作業4。事後に変更しない)

neg3・neg2×n=2×{A=KPI構成+N1′、B=A+N3′}=8 run。N3′採用の条件: Bの自己矛盾率(Recheckが`COMPLIANT∧all_prior=False`となる割合)がAより低い、かつ(ア)resolved=trueと判定されたprior issueのうち本文が実際に書き換わっていないもの(形だけの解消)が0件、(イ)STAGE4・重大見逃しが増えない。満たさなければN3′ OFF(N1′のみ)で29件。

### 13-7 Production配線時の方針(記録のみ、実装は配線時)

再検査結果を正規化する純関数(`normalize_recheck_outcome`、PASS/NEXT_CYCLE/STOP)をTrial/Productionで共有する。Production(`er012`再検査、410〜430行)は現在Stage 2・cycle・ladderを持たない(再生成→再検査→不成立ならSTOP)ため、自己回復flowを持たない間は`NEXT_CYCLE`を`STOP`へ写像(現行STOP相当、安全側)。N3′を入れる場合、Production共通の`build_prior_issues_instruction`(`er003` 678行)の扱いを同時に決める。Production採用可否は人間ユーザーのみが決める(本節は`APPROVED_FOR_PRODUCTION`ではない)。

### 13-8 実測結果(委任_06、2026-10-04、確認)

- A/B(neg3・neg2×n=2×{A=N1′、B=N1′+N3′}、8 run、¥4.84): 自己矛盾率A 100%(2/2)・B 100%(2/2)→事前基準(Bが下がる)を満たさずN3′はOFF。機序=Recheckが`prior_issues`1件に対し`index=0`の項目を2件返し、`len(resolved)==len(prior_issues)`規則で`all_prior=False`(`resolved`は全てtrue、4/4。`ab_selfcontradiction_mechanism_01.*`)。再確認(cite-or-release後は件数を問わない式)は`True`。N3′(前後の対)の効果は観測されず、Opus#12の「前後の対が無いことが主因」は支持されなかった(nが小さい)。件数一致規則の扱いは判定規則に近い境界事項のため実装せずFable判断。
- rep28(Step 6、N1′ON・N3′OFF、¥20.50): Human Review 3(`safety_er009_changed_scope` s1・`meta_run03_advanced` s2=`ladder_exhausted_without_full_rewrite`[`actor_guard_rejected`]、`safety_er009_unsupported_new_claim` s1=`degenerate_rewrite_output`[title単独claimのdelete])、重大見逃し0、平均追加+¥0.10、worst追加+¥0.81 → KPI未達(Human Review)。rep27の3件(A4・A5・neg3)は解消(neg3は`unconfirmed_after_reverify` 0件)。N1′合流は5件で全て通常経路の`recheck_major`、移動先(`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`)は0件。詳細はREPORT§56。
