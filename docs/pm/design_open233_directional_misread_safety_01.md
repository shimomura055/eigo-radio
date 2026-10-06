# 方向反転(directional misread)専用Safety設計 (OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01)

## §0 前提

- 管理ID: OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02b。§0〜§5のみ。§6〜§12は委任_02c)。
- Status: 設計段階(¥0)。**本docは提案であり決定ではない**。採否はOpus条件Aレビュー後にFable→ユーザー。`APPROVED_FOR_PRODUCTION`ではない。
- 性質: Safety flow構造変更の設計。実装・Production変更・有料API・コード/prompt/runner変更は一切含まない。
- provenance: 事実は委任文の確定事実(frozen)と、読み取ったコード(checker `negation_mismatch` L496付近・`verify_supported` L538、runner `SAFETY_CRITICAL_CLAIM_DEFS` L9817)。反実仮想の数値は委任_02a産出で、§6で委任_02cが転記する(本docでは数値を書かない)。
- 禁止(ユーザー指定): 残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold変更/KPI変更/Human Reviewへの安易な振替/新Safety原則の「決定」記述。
- 本docの「推奨」「提案」はすべてユーザー判断事項。「【推測】」は未検証の推論。
- 設計課題(ユーザー原文の要旨): 「同じAIにもう一度重大かどうか聞く」のではなく、読み違いの種類(方向反転)を直接検査する。仮説=決定論検査は重大判定器ではなく「専門検査を起動するセンサー」。そのまま採用せず代替案も比較する。
- 上位原則との関係: 重大誤解原則(design_open233_self_recovery_flow_01 §0-1/§0-2、2026-10-01)=「英語学習者に記事の本質について重大な誤解を与えるものだけを止める」「記事の主要な意味・主体・方向・規模・時間軸を誤認させるか」を基準とし、BLOCK候補に「上昇→下落(方向反転)」「継続していた出来事→一度消えて戻った出来事」を明記する線引きは変更しない(委任_02cで原文と逐語照合・本行訂正済み。方向反転はBLOCK候補として既に原則内)。本設計はその検出漏れを減らす構造の提案のみ。

## §1 見逃しの正確な原因(HC-012 / meta_run03_advanced cycle1)

対象claim: 「The company also restored the human concierge feature to the way it had been before, at least for now.」

| 段階 | 結果 | 備考 |
|---|---|---|
| Stage 1 AI | SUPPORTED(routes=r3) | AIが「支持される」と読んだ |
| 決定論検査 | `negation_polarity_mismatch`で候補化 | `dev.issue`「決定論検査で戻した」。信号は出ていた |
| `changed_*` 6フラグ | 全false | 旧floorの発火条件が成立せず |
| Stage 2 | ACCEPTABLE(basis none) | 決定論信号を受け取って消した形 |
| S1(再サンプル) | ACCEPTABLE(basis ledger_claim、confirmed_downgrade=True) | 同model・同rubric(runner L4055。Opus Part 2訂正: S1本体はL4160-4203、L4055はrun_stage2結果組み立て) |
| floor | floor_reason=None、floor_cited=ACCEPTABLE | 旧floor全ONでも不発火(フラグ無し) |
| 最終本文 | 残存 | 重大誤読が通過 |

- 同型: gold A5-0(HC-012「temporarily put back the feature」、`SAFETY_CRITICAL_CLAIM_DEFS` safety_A5)。
- 決定論検査の実体(checker L496): 単位の英語否定語の有無と、引用factの1行目(claim行)の日本語否定マーカーの有無を比べる極性の粗い近似。方向語(restore/rollback等)の意味は見ていない【読んだコードからの事実】。よって「撤回→復活」型は否定語の有無のずれとして偶発的にしか拾えない【推測】。

### 揺れ vs 系統

- (a) Stage 1/Stage 2/S1の3段階が同一の読み(restoredを「ledger通り」と読む)=系統的。
- (b) S1は同model・同rubricの再サンプルであり独立でない=誤りが相関する(OF-045「同rubric再サンプルに過ぎない」と整合)。
- (c) 決定論信号は`changed_*`フラグを経由しない限り後段へ渡らず、Stage 2のACCEPTABLEで構造的に消える(OF-043「根本原因はStage 1 `changed_*`生成側」と整合)。
- (d) n=1のため、確率的な揺れの寄与は未分離。
- 結論【推測】: 系統的な読み癖+相関構造が主因、揺れは副。再現確認は委任_02aの反実仮想が別途扱う。

### 過去の同型との関係

- A5-0/A5-1/A4-0/B3/A2A3-0はいずれも「後段AIが誤って降格・通過させる」型。V2較正のA4-0/A5-1 false downgrade→V3修正、B3/A2A3-0誤降格はgold手動照合で初めて発見され自動検知を追加(委任_33)。
- 共通点: AI判定の出力だけを監視する構造のため、AIが一貫して誤ると検知できない。
- 追加の注意: A4-1(HC-012「actually speaking with human staff」)は委任_57で問題なし(ACCEPTABLE)へ再ラベル済。同factの別文であり、方向反転専用確認が当該文を誤爆しないことの確認が必要(§3の誤爆軸、§6で委任_02c)。

### §1-訂正(委任_02d、2026-10-06)

- 出典: `er052_output/open233_directional_misread_offline_01/sensor_quality_01.md`【確認】。
- 上表の「決定論`negation_polarity_mismatch`で候補化=信号は出ていた」は事実だが、**その信号は方向を見ていなかった**。
- 反応機構: Ledger行「適切な開示なしに…」の「なし」(是正案a `STAGE1_NEGATION_MODE="a"`)に偶発反応。記事側に英語否定語なし(unit_neg=[])で `(not u_neg) and all(f_negs)` が成立し発火(checker L529-535)。
- 向きの区別なし: 忠実文(rolled back)も反転文(restored/expanded)も同じ理由で発火。HC-012根拠32文のうち英語否定語を持たない肯定文は全て発火。
- 含意: 「信号を保持すれば方向反転を拾える」は成立しない。上記(c)「決定論信号の喪失」は事実だが、保持しても拾える根拠にならない(捕捉は偶然)。
- 精度: 新9 run negation反応39件=問題なし38/重大1(1/39)。旧9 run 47件。number/causal反応は新9 runで0件。
- 比較・方向専用センサーはcheckerに存在しない【確認】。

## §2 専門検査対象の意味関係タクソノミー

方針: 単語リストではなく「Ledger側事象とArticle側表現の意味関係」で型を定義する。語彙は検出(trigger)の近似にすぎず、判定は意味関係で行う。

| 型 | 意味関係の定義 | 既存gold/過去事故 | 段階 |
|---|---|---|---|
| (i) 極性 polarity | 事象が行われた/行われなかった、撤回された/維持された、肯定/否定の反転 | A5-0・HC-012(撤回→復活の読み違い)、決定論`negation_polarity_mismatch`の守備範囲 | 第1段 |
| (ii) 方向 direction | 同一軸上の対極(増/減、開始/停止、拡大/縮小、許可/禁止、承認/却下、追加/削除、復元/撤回)の取り違え | HC-012の restore vs rollback型。ユーザー列挙の語対はここの例 | 第1段 |
| (iii) 主体・相手先 agent/patient | 誰が誰に何をしたかの入れ替わり・取り違え | A4-0(completed the exchanges with users) | 第2段候補 |
| (iv) 時間順序・一時性 | 一時的な縮小→回復、前後関係、at least for now等の期間限定の消失 | HF-009型、A5-0の「temporarily」側面 | 第2段候補 |
| (v) 範囲 scope | 全体/一部、条件付き/無条件の拡張・縮小 | B4-a(take over when AI alone has trouble) | 対象外(既存経路) |
| (vi) 因果 causal | 因果でない並置の因果化 | B3(flashy 20% plan)、A2A3-0 | 対象外(既存`causal_not_in_fact`経路) |

- 第1段の対象=(i)(ii)(ユーザー指定の方向反転)。第2段候補=(iii)(iv)は、第1段の実績を見てから範囲拡張を検討する(ユーザー判断)。(v)(vi)は既存検査を維持。
- ユーザー列挙の語対(rollback/restore、withdraw/reinstate、increase/decrease、start/stop、expand/shrink、allow/prohibit、approve/reject、add/remove)は(i)(ii)の例示。「その他」は、同一対象に対して反対の状態変化を表す関係として一般化する。
- 一般化の定義案: 「同じ対象Xに対し、Ledger側の状態変化ベクトルとArticle側のそれが、符号(向き)で反転している」。語の対応表は持たず、専用確認promptがXと状態変化の向きを自然文で答えさせる。
- 語彙リストを使う場合の位置付け: triggerの補助(T-C、§4)に限り、判定には使わない。リストは網羅不能のため、単独では過適合(OF-044「正規表現当て込みで過適合」と同趣旨の懸念)。
- 注意: (iv)「一時性」は(i)(ii)と重なる(A5-0)。第1段のprompt出力に「期間・一時性の食い違い」を観察欄として記録だけさせる案を§3で扱う(判定には使わない)。

### §2-改訂(Opus Part 1の型T1〜T6との対応、委任_02e)

| Opus型 | 内容 | 既存型 | 例 | 段階案 |
|---|---|---|---|---|
| T1 | 状態変化の向き反転 | (i)(ii) | A5-0/HC-012 | 第1段 |
| T2 | 推移・比較の向き反転 | (ii)(iv) | 委任_61/HF-009 | 第1段 |
| T3 | 当事者取り違え | (iii) | A4-0 | 第2段候補 |
| T4 | 未指定役割の充填 | (iii)寄り | A2A3-0/HF-003 | 第2段候補 |
| T5 | 因果・条件の捏造 | (v)(vi) | B3/B4-a | 対象外 |
| T6 | 可能性の既成事実化 | (新) | 軽微 | 対象外 |

- 共通核(定義案): 「語彙はLedgerと大きく重なるが、事象の枠(主体/行為/相手/向き・結果状態/条件)が1つだけ入れ替わる」。
- 第1段=T1+T2(枠「向き・結果状態」)。第2段候補=T3+T4(枠「主体・相手」)。第1段の枠抽出schemaを枠名で拡張できる設計なら第2段は追加のみ【推測】。
- T5は既存`causal_not_in_fact`経路と重複、T6は重大度が軽微なため対象外。
- 注: 「向き」の枠は語彙リストではなく、Ledger/記事の各側から抽出した値の比較で扱う(§3案E)。

## §3 設計案の比較

### 案の定義

- 案A(ユーザー仮説): 決定論検査=センサー→方向反転専用の独立確認。別prompt、3問(Ledger側事象の極性・方向/Article側の極性・方向/一致・逆転・曖昧)。入力=該当fact+notes+該当文+前後1文のみ。出力schema固定(各問に逐語引用付き)。model=Stage 2と別系統を第一候補、同modelでも別prompt+限定入力を第二候補。
- 案B: Stage 2 rubricへ「決定論信号がある候補は極性を明示比較せよ」を追加。同model同rubric拡張。
- 案C: Stage 1再分類(4観点)に第5観点「極性・方向」を追加。不一致なら`polarity_mismatch`をStage 2へ明示的に渡す。前段で信号保持、専用確認なし。
- 案D: A+C。前段で信号を保持し、後段で専用確認。

### 比較表

| 軸 | A | B | C | D |
|---|---|---|---|---|
| Safety(HC-012捕捉見込み) | 中〜高。問いが直接で、信号がある限り起動【推測】 | 低〜中。同じ読み癖が残る【推測】 | 中。Stage 1が同じ読み癖なら不発 | 中〜高。信号保持+専用確認の二重 |
| gold維持(A4-0等) | 他経路は不変 | rubric変更で他goldへ波及(V2→V3前例) | Stage 1変更が波及 | Cの波及リスクを含む |
| 独立性(model/prompt/入力) | 高(別prompt+限定入力+別model可) | 低(全部同じ) | 低(同model同Stage) | A側が高 |
| 誤爆・不要Rewrite | 専用問で「一致」を返せば通過。起動件数次第 | 低〜中 | 中(第5観点の過検出) | A+C併せ |
| 追加確認件数 | 起動件数に比例(委任_02aの数値を§6で転記予定) | なし | なし(Stage 2へ渡る件数のみ増) | Aと同等以下 |
| 費用 | 起動件数×小さな1call | 増なし | 微増 | A+微増 |
| 実装複雑性 | 中(新call+schema+接続) | 低 | 中(Stage 1 prompt/schema変更) | 高 |
| retry/fallback/regen整合 | 新callはretry上限・fallback規則を明記して既存に従う(要設計、§7以降) | 影響小 | 影響小 | A同様 |
| 既存信号の保持 | 保持(§4) | 保持されない | 前段のみ保持 | 保持 |
| 旧time verify失敗との違い | 下記 | 同じ失敗を再現しうる | 同左 | 下記 |

### 旧time verify(委任_61)との違い

- 旧verify: Stage 2と同modelで「2回確認+逐語引用」。比較の方向反転がverifyで誤解放され決定論へ戻した(runner L2760)。同model・同系の問い(「この文は問題か」)の再確認だったため、相関した誤りを共有した。
- 案Aの差: (1)問いを「重大か」でなく「各側の極性・方向」へ分解(2)入力限定(判定に不要な文脈を除く)(3)別modelを第一候補(4)検証対象を決定論の警告に限定。
- ただし限界: 同model・別promptの案A第二候補は旧verifyとの差が(1)(2)(4)のみ。別model無しでは相関リスクが残る【推測】。委任_02aの反実仮想で捕捉可否を確認する。

### Claude側の評価と代替案

- 評価: 「センサー」構造は妥当。理由=決定論は意味を理解しない代わりにAIと誤りが独立。ただし本検査はマーカー有無の粗い近似で(§1)、false negative(フラグ未発火)は救えない。センサー単独では網羅性に限界。
- 代替V(Opus Part 2で旧名から改名。案Eと混同回避)(提案): 決定論に頼らず、第1段の対象型(i)(ii)に当たりうる動詞を含む文だけを別promptで全件確認(語彙トリガ主導)。網羅性は上がるが起動件数と過適合が増える。T-C(§4)の位置付けに近い。
- 暫定推奨(ユーザー判断事項、Opus条件Aレビュー前): 案D(信号保持+専用確認)を第一候補。ただしCの前段変更は波及リスクがあり、段階導入(まずAのみ→Cは後)も選択肢。

### 案の追加・再評価(委任_02e、2026-10-06。上の暫定推奨は§1-訂正により前提が崩れた)

- 案E(枠抽出方式、Opus Part 1(4)): 対象claimについてLLMが「Ledger側の枠値」「記事側の枠値」を**別々に**抽出(schema固定、各値に逐語引用付き)。一致/逆転/未指定充填/不明の判定はPython側で比較して決める。LLMは判定役でなく抽出役。同一モデルの相関誤り(同じ読みで両側を判定)を遮断する狙い【推測】。
- 案F(最単純): Stage 2 promptへChecker `issue`・決定論理由を渡す。priming前例(委任_16)あり、独立性なし。
- 注: 案Eのschema枠案は「主体/行為/相手/向き・結果状態/条件」(§2-改訂の共通核)。第1段は「向き・結果状態」のみ必須。

| 軸 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Safety | trigger次第(T-A/Bは偶然) | 低〜中 | 低〜中 | trigger次第 | 中〜高(抽出+Python比較)【推測】 | 低〜中(priming) |
| 独立性 | 高(別model可) | 低 | 低 | A側が高 | 高(判定を分離、別model可) | 低 |
| 誤爆 | 一致なら通過 | 低〜中 | 中 | 併せ | 抽出ミスによる偽「逆転」。逐語引用で抑制【推測】 | 中(primingで過検出) |
| 件数 | trigger依存 | なし | 微増 | A同等以下 | triggerによる(§4 T-D/T-E) | なし |
| 費用 | 小 | 増なし | 微増 | A+微増 | 小〜中(§7) | 増なし |
| 複雑性 | 中 | 低 | 中 | 高 | 中〜高(schema+Python比較) | 低 |
| HC-012捕捉の根拠 | **偶然(「なし」)** | 不確実 | 不確実 | **偶然** | 設計上は根拠あり(restoredのvs rolled back抽出)【推測、未検証】 | 不確実 |

- 案A・D: trigger(T-A/T-B)が方向非識別のため、**triggerを差し替えない限り推奨不可**。
- 案E/Fは¥0では未検証。検証は§9の限定Trial。

## §4 Checker機械信号の保持

- 提案: 決定論検査の警告(`negation_polarity_mismatch`等)を`cycle_record`に「未解消機械信号」として保持する。後段AI(Stage 2/S1)がACCEPTABLEにしても信号は消さない。
- 強制重大化はしない。信号=専用確認の起動trigger。AIの判断を覆さず、追加の直接確認を差し込むだけ。
- 保持の最小スキーマ案(実装は後工程): `{claim_id, signal_type, source(deterministic/stage1), raised_at, resolved: false|true, resolution: agree|reversed|ambiguous|none}`。
- 解消ルール: 専用確認が「一致」→resolved=true(解消記録を残す)/「逆転」→BLOCKING(§5)/「曖昧」→§5の曖昧処理。確認を実行できなかった場合は未解消のまま記録(黙って消さない)。

### triggerの定義候補

| ID | 条件 | 長所 | 短所 |
|---|---|---|---|
| T-A | 決定論由来の信号がある候補×後段の判定が非BLOCKING | 単純。HC-012を拾う | 決定論の誤検出(benign否定、BENIGN_JA_RE等)も全件起動し件数が多い可能性 |
| T-B | T-Aのうち、決定論とStage 1 AIの判断が食い違う(決定論=異常、AI=SUPPORTED) | 件数を絞れる。HC-012は該当 | 決定論が発火しStage 1が同意するケースは既存経路が処理するため抜けは小さい【推測】 |
| T-C | 文に極性・方向を表す語彙(型(i)(ii)の近似)を含む | 決定論未発火も拾える(代替V) | 語彙依存、過適合懸念(OF-044同趣旨)。補助用途に限る |

- 推奨(ユーザー判断事項): T-Bを基本、T-Aを上限、T-Cは補助(まず使わない)。起動件数は委任_02aの反実仮想で確認後に絞る(§6で委任_02cが転記)。
- 起動しても専用確認は1候補につき1回(retry上限は既存規則に従う、設計は§7以降)。
- 新規信号を作らない: 既存の決定論信号を後段で保持するだけで、新しい機械floorは追加しない(全機械floor復活は禁止事項)。

### trigger再定義(委任_02d後、委任_02e)

- T-A/T-Bは方向非識別(精度1/39、HC-012捕捉は「なし」への偶然)→**センサーとして不適**。上の「新規信号を作らない/信号保持」案は、保持しても方向を拾えないため単独では成立しない。
- 新候補:
  - T-D: Ledger事実側の分類。fact作成時またはrun開始時に1回、facts数ぶんのcall。各factが「状態変化・推移・比較を含むか」+向き語を抽出。該当factに紐づく全claimを案Eの対象とする。記事側の語彙に依存しない。
  - T-E: fact紐付き全claimに案Eを適用(trigger無し、全件抽出)。
  - T-C(語彙)は補助。記事側の語(restored等)を見る点でT-A/Bと異なる。
- 件数見込み(既存集計から転記):

| 候補 | 件数 | 備考 |
|---|---|---|
| T-A/T-B(旧) | 43/新9 run(4.78/run) | 方向非識別、参考 |
| T-C | 55/新9 run(6.11/run)、旧105 | 語彙補助。Ledger本文なし(過小評価の可能性) |
| T-E | 123/新9 run(約13.7/run) | `trigger_replay_01.json` n_labeled_joined=123。fact紐付き全件と同数と仮定【推測】 |
| T-D(fact分類call) | facts数(要集計) | 既存jsonに集計なし。新規script禁止のため要集計 |
| T-D(該当claim) | 要集計 | 該当fact比率が不明。T-E以下になる |

### §4 Opus Part 2反映(2026-10-06)
- 訂正: 「T-E 123件=fact紐付き全claim」は誤り。
- 123件=Stage 1候補(Stage 2へ渡った記録)のみ。SUPPORTED判定文を含まない。
- HC-012が123件に入ったのは「なし」の偶然。
- 正しい母集団=Stage 1の全単位(`support_fact_ids`付き、SUPPORTED含む、checker L636-645)。
- 件数は要集計(¥0、先行実施)。

## §5 最終判定ルール案(提案、ユーザー判断事項)

| 専用確認の結果 | 判定 | 処理 |
|---|---|---|
| 明確な逆転(Ledger側とArticle側で向きが反対、双方に逐語引用あり) | 重大 | BLOCKING→Rewrite。方向語をLedger側の語へ置換する限定Rewrite。信号は「逆転」で解消記録 |
| 一致(同方向、逐語引用で裏付け) | 通過 | 信号をresolved(agree)として記録。以降の経路は変更なし |
| 本当に曖昧 | 下記の選択肢 | - |

### 「本当に曖昧」の定義

- Ledger側の極性・方向自体が不明確で、factのnotes・前後文を見ても決まらない場合に限る。
- Article側の表現が両義的なだけ(Ledgerは明確)は曖昧に含めない。Ledgerが明確なら一致/逆転のどちらかを必ず判定させる(逃げ道を狭める)。
- 逐語引用が取れない判定は「曖昧」へ倒さず、判定不能として未解消のまま記録する。

### 曖昧の扱い選択肢

- (i) QUALITY記録のみ: 本文は変えない。過剰Safetyを避ける。見逃しリスクは残る。
- (ii) 限定Rewrite: 方向語のみ置換。確実だが、実は一致だった場合の不要Rewriteになる。
- (iii) 別modelで再確認→なお曖昧ならQUALITY(i)。追加費用は小さく、独立性も上がる。
- 推奨(ユーザー判断事項): (iii)。理由=曖昧は少数と見込まれ(【推測】)、別modelの追加callは低コストで独立性を足せる。なお曖昧なら(i)。Human Reviewへの振替はしない(禁止事項、過剰Safety・費用増の回避)。
- 逆転判定の誤爆対策: 「逆転」はBLOCKINGにするが、逆転の根拠は必ず両側の逐語引用付き。引用がなければ「逆転」を採用しない。
- 注: 数値・件数の見積り(起動件数、逆転/一致/曖昧の比率、gold誤爆)は委任_02aの反実仮想を§6で転記する。本§の推奨は数値で裏付けられていない暫定案。

## §6 反実仮想結果(委任_02a転記、frozen/reuse・決定論集計【確認】、¥0)

出典: `er052_output/open233_directional_misread_offline_01/trigger_replay_01.md`。非BLOCKING=llm_materiality基準(final基準でも新9 runは同数)。

| 集合 | T-A | T-B | T-C |
|---|---|---|---|
| 新9 run(16 cycle・123件)trigger | 43(4.78/run) | 43 | 55(6.11/run) |
| 旧9 run(25 cycle・326件)trigger | 52(5.78/run) | 52 | 105(11.67/run) |
| 新9 runラベル 重大/軽微/問題なし/UNDECIDABLE | 1/0/42/0 | 1/0/42/0 | 1/3/51/0 |
| HC-012(meta_run03_advanced cycle1) | trigger | trigger | trigger |
| 新9 run重大4件のtrigger | HC-012のみ | 同左 | 同左 |
| 旧35件 正当6件のtrigger | 0 | 0 | 0 |
| 旧floor誤爆24件のtrigger | 0 | 0 | 8 |
| 旧判断不能5件のtrigger | 0 | 0 | 3 |
| 段階A(42 run・候補658) | 決定論由来155 | 同左 | 語彙該当183 |

- HC-012は`sub_reasons=negation_polarity_mismatch`、llm/final=ACCEPTABLE。3案ともtrigger=捕捉前提を満たす。
- 他の重大3件(B3/HC-011/HF-009)はAIがBLOCKING済みで`sub_reasons=model`のため非trigger=影響なし。
- 段階A SC gold(各3 run): 一致候補は全て3件。T-C語彙該当はB3とA5-0が各3、A2A3-0/A4-0/B4-a/B3-same@neg5は0。決定論由来候補はA4-0のみ2 run。
- 所見(Sonnet、【推測】): trigger精度(真に重大/trigger)=1/43で約2%。ただし専用確認は軽量callで強制重大化しないため、専用確認が正しく「一致」と返す限り不要Rewriteは増えない。この前提は未検証(§9段階1で測定)。
- T-CはT-Aより対象が広く、旧誤爆24件のうち8件もtriggerする(処理増)。T-Aは旧誤爆24件に0(floor誤爆集合と独立)。
- 近似の限界: T-Bは「`sub_reasons`に`model`が無い」で近似しT-Aと同数(区別不能)。T-CはLedger fact本文がjsonに無くclaim_textのみ適用(過小評価の可能性)。専用確認自体の捕捉可否はLLM未実行の分析評価で【推測】。
- 注: 決定論が未発火の方向反転は、T-A/T-Bでは構造的に救えない(§10論点)。

### §6-訂正(委任_02d、委任_02e)

- 上表HC-012「3案ともtrigger」は、T-A/T-Bについては**偶然**(Ledger行の「なし」)による。向きの識別ではない。gold A5-0も同様(是正案aの「なし」のみ発火)。
- T-Cのみ記事側の語(restored)を見ている。ただしT-Cは旧誤爆24件のうち8件もtrigger(処理増)。
- HF-009(K16/K19)はlegacyのみ「ほどなく」の「なく」で発火、是正案aでは不発(偶発)。
- 「他の重大3件は非trigger=影響なし」は変わらず(AIがBLOCKING済み)。

## §7 追加費用見込み(推計【推測】、実測は§9段階1)

- Stage 2単価の根拠: `er052_output/open233_prod_e2e_02/report_final/report_abcde.md`の「後段判定関連(Stage2+S1+floor_verify)」=¥7.2932(新9 run、123判定)→約¥0.059/判定(S1・verify込みのため1判定あたりは過大寄り)。参考: 同E2E総額¥31.52/9 run(約¥3.5/run)。
- 専用確認1 call: 入力=該当fact+notes+該当文+前後1文≒400〜800 tok、出力=schema固定≒100 tok。Stage 2 1判定の1/3〜1/2と仮定→¥0.020〜0.030/call。

| 項目 | low | mid | high |
|---|---|---|---|
| 単価(¥/call) | 0.020 | 0.030 | 0.059(Stage 2同等) |
| T-A 4.78 call/run → ¥/run | 0.10 | 0.14 | 0.28 |
| 9 run(43 call) → ¥ | 0.9 | 1.3 | 2.5 |
| T-C 6.11 call/run → ¥/run | 0.12 | 0.18 | 0.36 |
| 曖昧の別model再確認(曖昧率10〜30%仮定)を上乗せ | +0.1 | +0.3 | +0.8 |

- 結論【推測】: 追加費用は1 run約¥0.1〜0.4で、現行約¥3.5/runの約3〜10%。費用はボトルネックでない。
- 別model(Stage 2と別系統)を使う場合の単価差は「未測定、段階1で実測」。上のhighは単価2倍近傍の安全側。
- 処理件数: T-A約4.8 call/run(約2.7/cycle)。旧9 runは5.78/run(¥0.1〜0.3/run相当)。件数ではなく時間・レイテンシへの影響は§10論点。

### §7-改訂(T-D/T-E/案E、委任_02e、推計【推測】)

- 前提: 単価は上と同じ(low¥0.020/mid¥0.030/high¥0.059)。案Eの1 claimあたり=抽出call 1回(Ledger側+記事側を1 schemaで)をbase、Ledger側/記事側を別callにする場合は2倍(別model時の独立性重視)。
- ※単価は案Eの抽出callが専用確認より入出力が大きい可能性があり未測定。

| 項目 | low | mid | high |
|---|---|---|---|
| T-E 約13.7 call/run(1call/claim) ¥/run | 0.27 | 0.41 | 0.81 |
| T-E 9 run(123 call) ¥ | 2.5 | 3.7 | 7.3 |
| T-E 2call/claim 9 run ¥ | 4.9 | 7.4 | 14.5 |
| T-C 55件 案E 9 run ¥ | 1.1 | 1.7 | 3.2 |
| T-D fact分類(facts数要集計) | 要集計 | 要集計 | 要集計 |

- T-Eは現行約¥3.5/runの約8〜23%(1call/claim)。T-C限定なら約3〜9%。
- T-D: 分類callはfact単位でrun間再利用可(factが固定資産なら1回のみ)の見込み【推測、未確認】。該当claimがT-Eの部分集合になるため、T-Eが費用上限。
- 曖昧の別model再確認は上の+0.1〜0.8/run相当を追加。
- 不要Rewrite由来の費用は専用確認が「一致」を返す限り発生しない。誤って「逆転」を返す率が費用・品質の支配因子(§9で測定)。

### §7 Opus Part 2反映(2026-10-06)
- §7-改訂のT-E 123件は母集団として誤り(§4 Opus Part 2反映参照)。
- 正母集団=Stage 1全単位(SUPPORTED含む)。T-D'(Ledger側抽出が分類を兼ねる)の件数で再推計要。
- T-E 9 run(123 call)の費用行は過小の可能性【推測】。再集計後に更新。

## §8 推奨案(Sonnet所見。決定ではなくユーザー判断事項)

- 推奨: 案D = 案C(前段で信号保持)+決定論センサー(T-B基本/T-A上限)→案A(方向反転専用の独立確認)。曖昧は別model再確認→なお曖昧ならQUALITY記録。
- 段階導入案: 先にAのみ(信号保持=§4の記録のみ+専用確認)を試し、Stage 1第5観点(案C前段変更)は後続判断。Stage 1変更は波及リスク(V2→V3前例)のため。
- 理由:
  - Safety: HC-012はT-A/T-B/T-Cすべてtrigger(§6)。他のgold(A4-0等)は既存経路を変更しないため非影響。
  - 独立性: 別prompt+限定入力(+別model)。旧time verifyとの差は§3の通り。別modelなしでは相関リスクが残る【推測】。
  - 誤爆: 強制重大化なし。専用確認が「一致」なら通過、逆転は両側逐語引用必須(§5)。
  - 費用: 約5 call/run、約¥0.1〜0.4/run(§7)。
- 採用しない案:
  - B(Stage 2 rubric拡張): 同model同rubricで同じ読み癖が残り、gold波及の前例あり。
  - C単独: Stage 1が同じ読み癖なら不発。独立確認がない。
  - V/T-C主導: 語彙過適合(OF-044同趣旨)、旧誤爆24件のうち8件もtriggerし処理増。補助に限る。
  - 全機械floor復活・Human Review振替: ユーザー禁止事項。
- 限界(正直な記述): 決定論が未発火の方向反転は救えない。決定論由来の信号がAI3段階とも通過する型のみを狙う限定案。網羅的Safetyではない。
- T-AとT-Bは新9 runで同数のため区別が付かない。当面はT-A(単純)とし、T-B分離は段階1で判断する案。

### §8 推奨案(改訂、委任_02e。上の旧推奨案Dは前提崩壊により撤回候補。決定ではない)

- 候補推奨(Sonnet所見): **案E(枠抽出+Python比較)をT-D(Ledger事実側分類)またはT-E(fact紐付き全claim)で起動**。曖昧は別model再確認→なお曖昧ならQUALITY記録。抽出失敗・引用なしはBLOCKING→限定Rewrite(Human Reviewへ振らない、hintに両側の枠を入れる)。
- 旧案Dとの差:
  - 旧: 決定論信号(T-A/B)をセンサーにする。→ 信号は方向を見ておらず(§1-訂正)、HC-012捕捉は偶然。保持しても拾えない。
  - 新: センサー(trigger)を事実側分類(T-D)または全件(T-E)に差し替え、記事側語彙・決定論偶発に依存しない。判定をLLMから外し抽出+Python比較へ。
- 理由:
  - Safety: 捕捉の根拠が偶然でなく構造的【推測、未検証】。
  - 独立性: 判定でなく抽出のため、同一model相関誤りの影響が小さい見込み【推測】。
  - 費用: T-Eでも現行の約8〜23%(§7-改訂)。
- 最単純案F(Stage 2へissue渡し)は低コストだが、独立性なしでpriming前例(委任_16)があり、決定論理由名が役に立たない(§13)ため単独推奨しない。
- ユーザー仮説(決定論=センサー→専用確認)との関係【推測】:
  - 既存の決定論検査(`negation_polarity_mismatch`)はセンサーに不適(方向非識別)。
  - 「センサー→専用確認」の構造自体は、センサーをT-D(事実側分類)に置き換えれば成立する。
  - ユーザー仮説のうち「センサー」の実体の差し替えは新しい設計判断=ユーザー判断事項。
- 限界: T-D分類が見落とした事実(状態変化を含むのに非該当)は救えない。T-Eは全件で網羅的だが費用が上限。案Eの抽出精度は未測定(§9で測定)。

### §8 Opus Part 2反映(2026-10-06)
- 撤回: 「抽出失敗・引用なし=BLOCKING」。訂正=1回retry→未解消記録+QUALITY(BLOCKINGにしない)。§5 L193/L201と整合。
- 推奨を案E'(Opus修正版)へ整理。旧案Dは撤回候補。
- Ledger側: factごと1回、記事文脈なしで事前抽出。
  - 枠の値=動詞でなく「事象後の状態」のenum固定値: 利用可能/停止/一時停止/増加/減少/不変/未言及/不明。
  - 事象リスト化。2モデル一致、割れたfactはQUALITY。
- 記事側: 対象Xだけ渡しLedger値を見せないblind抽出。どの事象かを引用付きで選ばせる。
- Python比較: 未言及=通過、一時性の差=逆転にしない。
- 明確な逆転(両側逐語引用あり)=Stage 2・S1を迂回してBLOCKING(precheck_floor型、runner L8784-8789)。
- 解消判定=書き換え後の文を再抽出してPython再比較(LLM Recheckに任せない)。
- Rewrite上限到達時=Human Reviewに振らず、STOPかQUALITYかユーザー選択。
- T3・T4は同callで観察欄に記録のみ。
- 起動=T-D'(Ledger側抽出が分類を兼ね、状態変化・比較を含むfactに紐づくStage 1全単位)。T-Eは監査用(Trial時のみ全件)。T-Cは不採用。
- 旧記述の「E/T-C主導」は「V/T-C主導」へ改名済み。

## §9 次の限定Trial案(提案。有料のためユーザー承認事項)

- 段階0(¥0): 完了(§6のreplay)。
- 段階1(有料・保存候補への実測のみ、再生成なし、Production非変更):
  - HC-012(1件、T-A 43件に含む)=捕捉可否。
  - 段階AのA5-0候補(3件)=同型gold 3/3。
  - 新9 runのT-A trigger 43件(真に重大1・問題なし42)=誤反転(逆転誤判定)率の測定。
  - 旧floor誤爆24件のうちT-C該当8件=T-C補助の誤爆確認。
  - 委任_61の方向反転再現ケース(件数は未確認、仮に約5件)。
  - 合計約59 call(重複除く)。同一入力へ別model/同modelを比較する場合は2倍。
- 費用概算(件数×§7単価): low約¥1.2 / mid約¥1.8 / high約¥3.5。別model比較込みでhigh約¥7。
- 測定項目案(新KPIではない): HC-012捕捉(逆転)、A5-0 3/3、問題なし42件の「一致」率、曖昧率、「逆転」誤判定件数と逐語引用の有無。
- STOP条件案: HC-012非捕捉/問題なしの逆転誤判定が複数(目安: 42件中3件以上)/曖昧が多数(目安: 20%超)。目安値はOpus/ユーザーで調整する暫定値【推測】。
- 段階2: Production配線設計。条件A・C該当のため再度Opus必須+ユーザー承認(`APPROVED_FOR_PRODUCTION`は人間のみ)。
- 段階1実行にも、Trial専用経路(DEV/Trial)で実施しProduction runnerへ混入させないことが前提。

### §9-改訂(案E向け限定Trial案、委任_02e。上の段階1は案A前提で旧)

- 対象(有料、保存候補への実測のみ、再生成なし、Production非変更):
  - HC-012の4文(忠実=rolled back/反転=restored・expanded等): 反転検出と忠実文が「一致」になるか。
  - A5-0候補3件、K16/K19/委任_61合成(「plan withdrawn, oil prices fell」)計約3件。
  - 新9 runのT-C該当55件、またはfact紐付き123件(T-E)。どちらにするかはユーザー判断。
  - 旧floor誤爆24件(正常文の誤逆転確認)。
- 件数: 小構成=4+3+3+55+24=約89call、大構成(T-E)=約157call(重複除かず、実測時に重複除去)。
- 測定(新KPIではない): 反転検出率/忠実文を「一致」と返す率/枠抽出の逐語引用成功率/曖昧率/Ledger側抽出の失敗率。
- 費用(1call/claim。2call/claimは2倍):

| 構成 | low | mid | high |
|---|---|---|---|
| 小(約89call) | 1.8 | 2.7 | 5.3 |
| 大(約157call) | 3.1 | 4.7 | 9.3 |

- STOP条件案(暫定【推測】、Opus/ユーザーで調整): HC-012反転文を一致と返す/忠実文の逆転誤判定が複数(目安3件以上)/逐語引用成功率が低い(目安80%未満)/曖昧率20%超/抽出schema違反が多い。
- 並列化: Trial対象群は独立のため並列実行可(同一条件を保てる範囲)。有料はユーザー承認事項。

### §9 Opus Part 2反映(2026-10-06)
- 限定Trial追加対象:
  - (1) HC-012紐づき実文32文全件(忠実文rolled back系含む)
  - (2) 状態変化factごとのStage 1 SUPPORTED実文
  - (3) 決定論で作る合成反転文10〜20件(gold非変更・Trial専用)
  - (4) 比較条件: 1call両側 vs 2call blind、同model vs 別model(Ledger側)
  - (5) HC-012・A5-0各3回以上反復
  - (6) Ledger側正解枠の事前登録
- STOP条件(事前登録): 誤逆転率×全単位数=1 runあたり不要Rewrite見込み。比較基準=現行Rewrite約0.67件/run。
- 費用約¥15以内【推測】。有料のためユーザー承認事項。

## §10 Opus条件Aレビュー論点

- ユーザー指定4点:
  1. 同一モデルの相関誤りを本当に減らせるか(別prompt+限定入力+別modelの実効、旧verifyとの差)。
  2. 方向反転以外の同型systematic misread(§2の(iii)(iv)等)はないか。
  3. 過剰Safetyへ逆戻りしないか(trigger精度約2%、T-C誤爆8/24)。
  4. 既存Checker信号を捨てている他の箇所がないか(Stage 2でACCEPTABLEにより消える信号一般、`changed_*`以外の信号)。
- Fable追加:
  - S1(second_opinion)との関係: 置換か併用か。S1は同model同rubricの再サンプルで独立でない(§1)。
  - 決定論検査の粗さ(英語否定語×日本語否定マーカー近似)をセンサーに使う妥当性と偽陰性。
  - trigger精度約2%の処理負荷。
  - Recheck/出口/retry/regenでの専用確認の再実行要否。既存retry上限・fallbackとの整合。
  - 専用確認の失敗時はfail-closed(未解消記録、黙って通さない)か、安全装置の独自無効化にならないか。
  - 「曖昧→別model再確認」の費用・無限ループ回避(1候補1回の上限)。
- Part 1(信号喪失箇所・同型誤読)は並行実施中、Part 2(本docの設計案評価)はFableが依頼。結果はFableが追記。

### §10-追加(Opus Part 1(3)の論点、委任_02e転記)

1. 系統的誤読のT1〜T6(§2-改訂)のうち、第1段対象をT1+T2に絞る妥当性。T3+T4を第2段にする順序。
2. 案E(枠抽出+Python比較)で、抽出役の誤りが同一model相関で両側に出ないか(別model要否)。
3. 枠schemaの粒度(主体/行為/相手/向き・結果状態/条件)。細かすぎると抽出失敗・誤爆、粗いと見逃し。
4. T-D(事実側分類)の見落とし(偽陰性)をどう検知するか。T-E全件にすれば解消するが費用上限。
5. 案F(issue渡し)を併用してよいか、primingの害(委任_16)との兼ね合い。
6. 抽出失敗・引用なし時の扱い(BLOCKING→Rewrite、Human Review非増)の妥当性とRewrite hintの設計(両側の枠を入れる)。
7. 既存信号の喪失箇所(§13)をどこまで本件の範囲で是正するか、別IDへ切り出すか。

## §11 Existing Spec/Prior Trial Check(A/B/C)

| 既存要素 | 区分 | 本設計との関係 |
|---|---|---|
| 旧time verify(別prompt・2回確認方式、委任_61) | B(試行済み・失敗前例) | 比較の方向反転を誤解放し決定論へ戻した。本設計は問い分解・入力限定・別modelで差別化(§3)。同model別promptのみでは再現リスク【推測】 |
| cite-to-fire(反実仮想記録あり) | B | 逐語引用必須は§5で踏襲。過去の反実仮想記録の再確認は未実施(Opus/Fableで照合) |
| S1(`apply_stage2_second_opinion`、Stage 2承認構成の一部) | A | 併用前提。置換しない(置換可否はOpus論点) |
| Stage 2 V3 rubric修正 | A | 変更しない(案Bを採らない理由) |
| 決定論検査(checker `negation_polarity_mismatch`) | A | 既存信号の保持のみ。新floorを足さない |
| 重大誤解原則(self_recovery_flow_01 §0-1/§0-2) | A | 原則変更なし。方向反転は既にBLOCK候補(§0-2)。本設計は検出構造のみ |
| 本設計(センサー→専用独立確認) | C(新規) | 条件A(新構造)でOpus必須 |

- Dangling Reference確認(Grep、実在):
  - `negation_polarity_mismatch`: `er052_open233_stage1_coverage_checker_01.py` L24(理由一覧)・L560(付与)・L683。
  - `sub_reasons`: 同checker L586/L598/L642(候補フィールド)。
  - `second_opinion`: `er052_open233_self_recovery_flow_runner_01.py` L4141(`stage2_second_opinion_eligible`)・L4160(`apply_stage2_second_opinion`)・L4198。
  - `cycle_record`: 同runner L8854(辞書生成)。
  - `changed_*`・`SAFETY_CRITICAL_CLAIM_DEFS`(runner L9817)は委任_02bで確認済み、今回再Grepしない。
- 注: §4の「未解消機械信号」フィールドと専用確認callは未実装の新規提案であり、既存名ではない(Dangling対象外)。

## §12 STOP条件該当判定

| 項目 | 判定 |
|---|---|
| 新Safety原則の追加 | 非該当と見る【推測】。「決定論検査をセンサーとして専用確認を起動」は新構造だが、既存の重大誤解原則の検出手段であり原則追加ではない。ただし解釈はユーザー確認事項 |
| gold変更 | 不要(§6でgold非影響) |
| 有料Trial | 段階1で必要(約¥1.2〜3.5、別model比較込みで約¥7)。ユーザー承認事項 |
| Production変更 | 段階2で必要。条件A/C+`APPROVED_FOR_PRODUCTION`(人間のみ) |
| 禁止事項(残11 run/全機械floor復活/一律Checker厳格化/KPI変更/Human Review振替) | 本設計は該当操作を含まない |

- 到達Status案: DESIGN_READY_FOR_REVIEW(Opus Part 2後にFableが判定)。未決の採否はUSER_DECISION_REQUIRED。
- ユーザー判断事項: (1)案D/段階導入の採否 (2)T-A/T-B/T-C範囲 (3)別model使用 (4)曖昧処理(iii) (5)段階1有料Trialの承認 (6)新Safety原則解釈。
- 注意: 本docの推奨はすべて提案。実装・Production配線・有料実行は未承認。

### §12-更新(委任_02e)

- ユーザー仮説「決定論検査=センサー」の**前提が崩れた**(§1-訂正、sensor_quality_01)。センサー実体の差し替え(T-D/T-E、案E)は新しい設計判断。
- 判定: **USER_DECISION_REQUIRED候補**(Opus Part 2後にFableが判定。本docは判定しない)。
- ユーザー判断事項(追加): (7)センサー差し替え(T-D/T-E/T-C補助)の採否 (8)案E/案Fの採否 (9)数字floor穴の是正が承認範囲内か(§13)。
- 新Safety原則の追加: 引き続き非該当と見る【推測】が、「抽出+Python比較」は新構造のため解釈はユーザー確認。
- 禁止事項(残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold・KPI変更/Human Review振替/有料API)には非該当。

### §12 Opus Part 2反映(2026-10-06)
- ユーザー判断事項をOpus提示7点へ差し替え(旧(1)案Dは撤回候補):
  - (1) センサー差し替え(決定論→T-D')推奨採用。ユーザー仮説の「センサー→専用確認」構造は維持・実体を差し替え。
  - (2) 別model: Ledger側2モデル一致、記事側はTrialで比較。
  - (3) 失敗=retry→QUALITY。
  - (4) 逆転経路=Stage 2/S1迂回。上限到達時はSTOP/QUALITYの選択。
  - (5) T3/T4は観察のみ。
  - (6) 数字floor穴(checker L554-555/L640-643、実害0)と`apply_stage2_two_of_two`(runner L4106-4122、OFF、`claim_identity`=`fact:<id>` L1424-1429)は別管理ID推奨。
  - (7) 限定Trial約¥15以内の承認。¥0のT-D'母集団再集計を先行。
- 到達Status=DESIGN_READY_FOR_REVIEW。Fable最終判定=USER_DECISION_REQUIRED(理由: ユーザー仮説の前提崩れ・センサー実体差し替え・有料Trial)。

## §13 Part 1: 信号喪失箇所の整理と潜在不具合(Opus Part 1転記、委任_02e)

出典: Opus前段スキャン(Part 1)。行番号はOpus記載。【確認/推測】はOpus原文の区別を踏襲。

| # | 箇所 | 内容 | 影響 |
|---|---|---|---|
| 1 | calib L652-662 | Checkerの`issue`/`flags`/`sub_reasons`がStage 2 promptへ渡っていない。S1も同入力【確認】 | Stage 2/S1は決定論信号を見ていない |
| 2 | DV/Tier0 | issueを見るが承認構成でOFF【確認】 | 信号を使う経路が無効 |
| 3 | Recheck `prior_issues` | BLOCKINGのみ【確認】 | 非BLOCKINGの信号は再検査へ渡らない |
| 4 | runner L8765-8775(S-4非BLOCKING再利用) | キーに`sub_reasons`が無く、以降cycleで素通り【確認】 | 信号が後続cycleで消える |
| 5 | 出口検査 | Rewriteがあった記事のみ【確認】 | Rewriteなし記事は出口で検査されない |
| 6 | 再分類filter | model由来候補のみ【確認】 | 決定論由来候補は再分類対象外 |
| 7 | Rewrite hint | 決定論理由名(例`negation_polarity_mismatch`)がそのまま入る【確認】 | hintとして役に立たない |
| 8 | `apply_stage2_two_of_two` L4106-4122 | `fact:<id>`キーで兄弟文を上書き(現在OFF、L430)【確認】 | **潜在不具合**。今は影響なし |
| 9 | 数字floor穴 checker L554-555/L640-643 | `number_not_in_fact`が`changed_number`へ未変換(sensor_quality_01 D) | 新9 runで実害0件(`number_not_in_fact`出現0) |

- 取扱い(ユーザー判断事項):
  - #9数字floor穴: ユーザー確認事項(承認範囲内の是正か)。本doc/本委任では修正しない。
  - #8: 再有効化前に修正要(今は影響なし)。
  - #1〜#7: 案E採用時、抽出対象にはclaim_text/local_context/related_fact_id等を使うため、#1の信号渡しは必須ではない【推測】。案F採用時のみ#1が直接関係。
- 入力限定に使えるデータ(Opus(6)): claim_text/local_context/related_fact_id/unit_ids、`floor_verify_fact_block`、`ledger_block_fields`、DV骨組み(L3584-3628)流用可。取れない: r3の`ledger_quotes`、`support_fact_ids`2件目以降。

### §13 Opus Part 2反映(2026-10-06)
- (新1) SUPPORTED判定文はStage 2へ行かない(checker L636-645)。案Eの適用点はStage 1全単位。
- (新2) 逆転判定をStage 2候補として流すとStage 2/S1が再降格【推測】。迂回要。S1/2-of-2対象条件(runner L4141-4148/L4086-4093)から外す。
- (新3) Stage 4許可理由(L8307-8311)はStage 2 BLOCKING確定が条件。迂回BLOCKINGは`not_funnelled`で宙に浮く。Python再比較で解消判定。
  - Rewrite hintは理由名でなく固定値の状態(例「機能は当面停止。restoredと書かない」)。
- 最終本文への案E実行はRewrite有無によらず全記事。
- 参考: HC-012の`dev.severity_final=BLOCKING`(`existing_major_v2`)は全候補共通のMAJOR写像で方向信号ではない。

## §14 Opus Part 2レビュー要約とFable照合
- 総合判定=条件付きで進める。必須修正3点: blind分離抽出/母集団訂正/§5-§8矛盾解消。本委任で反映済み。
- Fable照合: 方向性(案E)一致。Opus発見の誤り反映。STOP条件該当→USER_DECISION_REQUIRED。
- 逐語は`docs/pm/opus_l2_review_open233_directional_misread_safety_01.md`(別委任で作成)。
