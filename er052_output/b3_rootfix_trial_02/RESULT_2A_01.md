# RESULT_2A_01(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 委任_02 Phase 2a 中間報告、2026-10-10)
Status提案: **D-det=`VALIDATED_PENDING_M10`(Trial限定・E9未実施)、D-plus=機械分類`REJECTED`(M7 STOP・M9超過、論点あり)、Separate-call(Luna)=機械分類`REJECTED`(Sol未実施)、役割宣言のみ=`VALIDATED`(Trial限定・no-harm)**。いずれも`APPROVED_FOR_PRODUCTION`ではない。Production code/Prompt/CURRENT_SPEC/SSOT・ACTIVE_TASK・RESULT_PACKET(正式)は未変更、git操作(add/commit/checkout/stash)は未実行。
**E9(R0を通した記事への影響確認)は本委任では実行していない**(Lane A C2が編集中の jaw/er012_e/er019 entertainment runner/audio runner を読まないため)。Phase 2bで実施する。
使用モデル: B3系・Separate-call=`gpt-6-luna`(gpt-6世代の最新だが最上位系かは未確認。例外理由=Production B3/R0と同一条件での比較が目的)。Solは発動条件(Luna不達)に該当せず未使用。応答modelは全callで`gpt-6-luna`を確認。
実費: **JPY31.68**(cap JPY60内): D-plus 16.47(18出力、retry/STOP込み)、役割宣言のみ 9.61(18)、Separate-call(Luna) 5.59(18出力、STOP 2含む)。台帳: `cost_ledger_b3r2_01.jsonl`。

## 非エンジニア向け要約(10項目)
1. **同一callで数値ランク付けは成立したか**: 動きはするが割に合わない。18回中17回は出力が得られ、LLMが付けた中核/周辺は規則と92%一致。ただし18回中1回(central_bank)が2回試行しても技術的に有効な出力にならずSTOP(事前登録は0を要求)、1出力あたりJPY0.915(合格線0.68)、応答66秒(合格線65.4秒)。B3の出力量(思考量)が約2倍(約4,950→約9,370トークン)に膨らむのが原因。
2. **別call方式は必要か**: **不要と見る**。最終の中核/周辺は規則だけで決められるので、LLMに期待できるのは「数字の表記を拾う」ことだけだが、それは正規表現(D-det)で足り、LLMの方が表記の切り方が雑(「221%増」「月額11.99ドル」のように助詞・語を含める)で、実在の落ちを補った例は0件だった。Separate-call(Luna)自体も、検証エラーでSTOP 2/18、同一入力の2回で結果が一致する率0.67(合格線0.90)。
3. **別callなら1記事いくら(実測)**: 成功した16 callの平均で**JPY0.18/記事**(+約17秒)。retry/STOP込みでは0.31。Sonnet注記(約JPY15.7/記事)の約1/90〜1/50。費用面の障害ではない(障害は再現性と検証エラー)。
4. **Fact/注意を分離してB3へ見せる方式は成立したか**: **成立**。役割宣言+欄ラベル(制約)を足しても、注意書きの継承は100%(65/65・68/68が制約ブロックに逐語存在)、Fact行側の指示調0件、Fact選択は悪化せず(採用件数は3.28→3.7〜3.8に増える方向、選択の再現性もノイズ床以上)、Storyline品質に事実誤り・主題ずれなし。
5. **Storyline混入は消えたか**: 事前登録の検出器では元々0/27で**天井(効果は判定不能)**。ただし後から探索的に調べると、C0に3/9・C1に3/18あった「メタ注記・指示調っぽい文」(例:「ただしLedger上確定できない」「誇張せず整理する」)が、役割宣言のみ 1/18、D-plus 0/17に減っている。小標本・探索的regexなので「減った傾向」止まり。
6. **Storyline品質は落ちなかったか**: 事実誤り・主題ずれは見つからず(M2合格)。ただし**長くなる**(平均 C1=102字 → 131〜133字、155字超が各腕4件、最長217字)。読みやすさへの副作用として残る。
7. **D-det(決定論)は十分か**: **十分な見込み(E9待ち)**。9テーマのBlind目視で「危険な誤り」は1件のみ(central_bankでStoryline主役の「25ベーシスポイント」が周辺に落ち「12対0」「30年」が中核になった。事前登録の合格線0〜1の上限)。既存の注記検査は9/9テーマで`annotator`欄の値(`DETERMINISTIC`)以外すべて通過。再実行で完全一致。LLMが追加で補えた実在の表記は0件。central_bank型は未適用の修正案あり(HUMAN_CHECK)。
8. **追加コスト**: D-det=JPY0(call 0)。役割宣言のみ=+約17%(0.534 vs 0.455)。D-plus=+54〜100%(単発0.70〜retry込み0.92)。Separate-call=+JPY0.18〜0.31/記事。
9. **Sonnet注記不要化の見通し**: **見込みあり**。D-detが作る注記(【事実N】と【中核数値】/【周辺数値】)は既存検査にほぼそのまま通る。注記の費用約JPY15.7/記事→JPY0にできる可能性。ただし(a)E9で記事が崩れないかの確認、(b)`annotator`値など既存検査の期待欄との整合、(c)central_bank型の修正、(d)Storyline側の表記も印付け対象にする仕様の確認、が残る。
10. **残るユーザー判断**: ①D-det一本化でPhase 2b(E9)へ進むか ②D-detのcentral_bank型修正(未適用)を入れて再freezeするか ③検証器の`DUPLICATE`扱い(同じ表記が同じFactに2回出るのは無害として畳む)を仕様候補として扱うか(今回の実害源) ④Separate-callをSolで追加試行するか(私見は不要) ⑤U2/U3(Production採用時のユーザー判断、委任文に内容記載なし=Fableから受領後に事前登録へ追記) ⑥Storylineが長くなる副作用を許容するか。

## 詳細
### 指標と判定(事前登録 PREREGISTRATION_02 に機械適用。出典 `eval/eval_results_02.json`)
| 指標 | D-plus | 役割宣言のみ | Separate-call(Luna) | 基準 | 判定 |
|---|---|---|---|---|---|
| 出力数(成功/STOP) | 17/1 | 18/0 | 16/2 | STOP 0 | D-plus ✗、Sep ✗、RO ✓ |
| M1 Jaccard rep1 vs rep2(C1=0.698) | 0.767 | 0.673 | — | ≥0.55 | ✓ ✓ |
| M1 Jaccard vs C0(C1=0.649) | 0.632 | 0.745 | — | ≥0.50 | ✓ ✓ |
| M1 採用3〜5件の出力数(C1=11/18) | 12/17 | 15/18 | — | ≥9 | ✓ ✓ |
| M1 平均採用件数(C1=3.28) / AMBIGUOUS採用 | 3.71 / 2/63 | 3.78 / 2/68 | — | 保守化の疑い=≤2.28 or AMBIGUOUS0 | 疑い無し |
| M2 IMP / notes共通12字以上(C1=1) / 限定表現(C1=2) | 0 / 2 / 1 | 0 / 1 / 1 | — | 0 / ≤2 / ≤4 | ✓ ✓ |
| M2 Storyline新数字フラグ(C1=4、全て表記差) | 3/17 | 5/18 | — | ≤6、真の新数字なし | ✓ ✓(目視で真の新数字0) |
| M3 注意文のStoryline転記(Blind目視) | 0 | 0 | — | 0 | ✓ ✓ |
| M4 注意書き継承(逐語一致) | 65/65 | 68/68 | — | 100% | ✓ ✓ |
| M5(a) LLM role=規則 一致率 | 92.3%(96/104) | — | 90.7%(107/118) | ≥90%、NO_CORE0 | ✓ ✓(参考) |
| M6 最終 新数字・取り違え / 欠落 | 0 / 1(1.0%、実在=COSMOS 1408) | — | 0 / 0 | 0 / ≤5% | ✓ ✓ |
| M7 技術retry出力数 / STOP | 2(retry 1+STOP 1) / 1 | 0 / 0 | 2(STOP2、各エラー=DUPLICATE) / 2 | ≤2 / 0 | D-plus ✗(STOP)、Sep ✗、RO ✓ |
| M7 NUMBER_RANKS系のみ原因のretry/STOP | retry 1 / STOP 1(一次エラー=SURFACE_NOT_IN_FACT 3件、2回目=DUPLICATE) | — | STOP 2(DUPLICATE) | 別集計 | 報告 |
| M8 再現性 (fact_id,surface,role) Jaccard | 共通Factで0.74(参考) | — | 0.67(表記のみ0.79、共通表記のrole一致45/50) | Sep ≥0.90 | Sep ✗ |
| M9 JPY/出力(合格≤0.68) | 0.915(単発成功のみ0.70) | 0.534 | 0.311(単発成功のみ0.181) | ≤0.68 | D-plus ✗、RO ✓ |
| M9 latency平均(合格≤65.4秒、C1=43.6) | 66.3 | 51.8 | 16.7 | ≤65.4 | D-plus ✗(僅差)、RO ✓ |
| 平均in/out/reasoning token | 4,654/9,365/7,419 | 3,910/5,894/4,277 | 1,703/3,153/2,891 | (C1: 約3,640/4,955/3,300) | — |
- D-det(call 0): M8再実行一致=✓(決定論)。M11(既存注記検査、9テーマ): **全9テーマで`annotator`値以外の問題0**。GT比較(参考のみ。D-detの抽出規則はC0 9テーマに対する既存注記検査の判定と見比べて修正した既知値で、独立予測ではない): 対応付け済みの中核/周辺一致 42/49(0.857)、GT中核25件のうち再現22(0.88)、適合率0.81。GT中核25件はcentral_bank 6・hormuz 4で40%と偏る。central_bankを除く8テーマでは一致0.889/再現0.947/適合0.818。Sep(LLM表記+規則導出、central_bank欠)は一致0.942/再現0.947/適合0.90、LLM宣言roleそのままだと0.855/0.895/0.81。
- Blind目視(D-det/D-plus rep1/Sep rep1、9テーマ): 危険な誤り D-det 1(central_bank)、D-plus 0(central_bank欠)、Sep 0(同欠)。詳細=`HUMAN_CHECK_B3R2_01.md`。
- central_bankのD-plus rep1・Sep rep1/rep2がSTOPのため、最大テーマ(GT中核6)での比較は D-det のみ。

### Closeout分類(事前登録5節を機械適用。`VALIDATED`はTrial限定で`APPROVED_FOR_PRODUCTION`ではない)
| 腕 | 分類 | 根拠 |
|---|---|---|
| D-det | **VALIDATED_PENDING_M10** | 危険な誤り1/9(≤1)・M8・M11(メタ欄以外PASS)・LLM補完なしを満たす。E9(M10)未実施のため最終VALIDATEDは保留。central_bank型の既知弱点あり |
| D-plus-single-call | **REJECTED(機械分類)** | M7 STOP 1(基準0)、M9超過(0.915/出力、66秒)。M1・M2・M3・M4・M6最終はPASS。STOPの原因の一部は検証器`DUPLICATE`仕様(下記)でFable判断に付す |
| Separate-call(Luna) | **REJECTED(Luna)/Sol未実施** | M7 STOP 2、M8 0.67<0.90。Solは「Luna不達時のみ」の条件に該当せず未実施(私見: D-detで足りるので不要) |
| 役割宣言のみ | **VALIDATED(no-harm)** | M1・M2・M3・M4・M7・M9を満たす。効果(混入削減)は天井と探索的結果のため主張は控えめに。副作用=Storyline長文化 |
- 複数腕が通過する場合は D-det > D-plus > Sep の順の単純さを第一候補とする規則に従い、**第一候補はD-det**(E9合格が前提)。採否はユーザー判断。

### 事前登録からの逸脱・開示
- D-detの抽出規則(`b3r2_rank_01.py`)は、freeze前に、C0 9テーマ(ROOTFIX-01の既存出力、有料なし)に対する既存注記検査の判定と見比べて複数回修正した(ISO日付・日付範囲・事件番号・名称内番号・倍率つき合成数・Storyline表記の取り込み・概念束ね、他)。GT比較値は独立でない既知値であることを事前登録に明記済み。freeze後は`b3r2_rank_01.py`のshaが固定され、有料runは毎回照合した。
- freeze後に評価script(`b3r2_eval_01.py`)の1箇所を修正した(`cost_latency`が`latency_seconds`を持たないSTOP記録行でKeyError)。指標の定義・基準は変えていない。
- 失敗run(STOP)の応答本文は保存していない(エラー種別のみ)。DUPLICATE等の実際の出力内容は確認できない。結果を見ての再実行・Prompt修正・検証器変更は行っていない。
- `cl.install`(`er005_cost_logger.py`)は`er003_b1_p3u_audio`系モジュールを内部import(read-only、実行・編集なし)する。Trial_01と同じ呼び出しで、委任文が禁じる 4ファイル(er012_e/jaw/er019 entertainment runner/audio production runner)は読んでいない・importしていない(`er019_family_x_audio_production_runner_01.py`と`er019_family_x_entertainment_production_runner_01.py`は作業中にgit statusで変更を確認したのみ)。

### 内容分析
1. **D-detで足りない表記**: 今回の9テーマ(選択Fact+Storyline)に漢数字の量・「数百」は0件(`eval/kanji_scan_02.json`)。実例として欠けたのは**Storyline側の表記と台帳側の表記が違う場合の紐付け**(25ベーシスポイント↔0.25パーセントポイント)。四半期・時刻・日のみは常に周辺(不適格)としており、GT側のkindとずれる可能性。
2. **D-plusのLLM抽出の価値**: 追加で拾えた実在表記=0件。誤り/雑な例=「221%増」「月額11.99ドル」「2026年9月18日付」「2億5,000万ドルを超える」(助詞・語を含むスパン)、時刻の分割、台帳欄にだけ有る表記(「2025年3月」「数十万件」「2026-09-23」)、数字を含まない「II」、「1バレル」単独。実在の落ち=「COSMOS 1408」(rep2)。
3. **Separateの再現性**: 同一入力2反復で(fact_id,表記,role)Jaccard平均0.67。差の主因は表記のスパンの揺れ(例: hormuzで「7月13日午前10時16分」vs「10時16分」+「7月13日」)で、共通表記のrole一致は45/50(90%)。
4. **役割宣言のStoryline影響**: 長文化(上記)、Fact選択は増加方向、メタ注記混入は減る傾向。
5. **Fact選択の保守化**: なし(むしろ採用件数が増加)。U1の削除と関係するか因果は不明。
6. **Lane A interface への含意**:
 - 漏れ1(role不一致時の採用規則): 最終roleは規則で導出し、LLM宣言roleは使わない(不一致率7.7〜9.3%はログのみ)→採用規則が不要になる。
 - 漏れ2(annotation.json): 決定論で出せる=`ledger_ids`(表記を含む全Fact)、`concept`(同表記/同Factの主数字・単位一致/包含の束ね)、`class`、`kind`。出せない/要仕様化=`unmapped_claims`(Storylineだけにある台帳外の数字は`_STORY`=未紐付けとして検出可能だがtype付与の規則が必要)、`annotation_notes`(cap超過の周辺化は`capped_off`で出せる、漢数字候補は走査で出せる)、`annotator`値(既存検査は`A/B/MERGED`のみ許容)、`spec_sha256`。
 - 漏れ3(【事実N】の作り手/Storyline行の印): 【事実N】はassemblerのFact行順で決定論付与可能。Storyline行の印は表記をFact本文表記と照合して紐付けるが、表記が違うと(25bp↔0.25pt)未紐付けで周辺落ちする→紐付けを`numeric_value`経由にする仕様候補(未実装)。D-fullのFact行はscope/conditionsの数字も含むため、number_ranksのsurface範囲は「ID行のclaim」でなく「組立済みFact行」にしないと印の漏れが出る(D-plusのM11で確認)。
 - Production採用時は、`DUPLICATE`の扱い、Storyline表記の紐付け、`annotator`値の3点が確定仕様として必要(いずれも新仕様候補=人間承認前に実装しない)。

### Phase 2b計画(E9=R0への影響、未実施)
6テーマ(問題5+byd_recall)×{D-det(C0 ID+決定論印)、対照=D-base(C0 ID、印なし/現行注記)}×R0 1回=12 call、R0のみ・`full_ledger_text=None`・Fact Lock R0 Prompt=Production同一。測定=Trial_01 E9の9項目+【中核数値】【周辺数値】タグの記事への漏出。見込み費用JPY5.4〜14.9(実測JPY0.45/call、保守1.24/call)、cap別枠。runnerの扱い(Lane A C2のrunner編集が終わるまで待つか、Trial専用の独立R0ハーネスを作るか)をFable判断。central_bank型の修正を入れる場合は先に再freeze。

### 成果物
`er052_output/b3_rootfix_trial_02/`: PREREGISTRATION_02.md、frozen_b3r2_02.json、PROMPT_DIFF_02.md、PROMPT_DIFF_ROLEONLY_02.md、b3r2_{rank,sepcall,make_dplus,b3_dplus,b3_roleonly,driver,eval}_01.py、runs/(D-plus・RoleOnly・Sep)、cost_ledger_b3r2_01.jsonl、selftest_result_01.json(34項目+既存、ALL_PASS)、dry_run/、eval/(eval_results_02.json、blind_sheet_02.md、blind_key_02.json、content_dump_02.json、m11/、kanji_scan_02.json、exploratory_meta_regex_02.json)、HUMAN_CHECK_B3R2_01.md。
