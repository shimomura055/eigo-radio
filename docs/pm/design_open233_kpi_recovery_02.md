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
