# PATTERN_DESIGN_01: パターン別の救済方式(設計+DEV実証)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 2026-10-26。Production非変更・DEV実装=`er123_kp_rescue_dev_01.py`(52 test PASS、API 0)・LLM評価は救済候補の**評価のみ**(生成は決定論)。
前提: 前回Opus M1〜M6/R1〜R4(`KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`)は設計へ組込み済み(DESIGN_01 §0の反映表)。区分の定義は委任文のとおり: **区分1**=承認済み規則の意図に沿う是正(規則文に無い内部条件・閉表の網羅漏れ・助動詞誤判定)、**区分2**=受理面の拡大/新しい処理工程でユーザー判断、**区分3**=救済すべきでない(意味変化・不自然・出典対応喪失・Human NG)。

## 0. 設計の骨格(全パターン共通)

```
[除外の検出] → [原因の分類(理由文+段)] → [パターン別の修正方式] → [既存Gateを同一引数で再適用(M6)] → [通過したものだけ候補化]
                                              ↓失敗                                              ↓
                                       救済しない(元の除外のまま。現行どおり)       rescue記録+HR表の旗+auto_eligible=False(M4)+gloss再整合(M3)
```

- **規則是正(区分1)で通る形は、救済フローを使わず通常フローに乗る**(Gate自体が通すようにする)。LLMの提案keyが通常のcanonicalization→gloss→QAを通るので、`rescue`記録もQA未再判定旗も要らない。
- **救済フロー(区分2)** は、LLM/選定の出力を、既存validatorを通る形へ決定論で寄せる後処理。新語形を作らない(M1)。HR経路(`er119 generate_candidates`)限定・既定OFF(M2)。救済候補は`auto_eligible=False`・`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`(QAをPASS表示しない)(M4)・gloss再整合を強制(M3)。外側retryのトリガー判定では救済句を`gate_dropped`相当として数える(M5、現行挙動維持)。
- LLMの役割は「評価」だけ: 候補の**生成**は決定論(連続部分列・窓内トークン選択・逆引き)。LLM評価はDEVでの品質確認(自然さ・意味保持・学習単位)に使い、Production設計では「A1のように候補が複数ある場合の選択」にのみ任意で使う(§A)。

---

## A. 語数超過(`too soon to wave a flag`、6語)

### 原因とリスク
Prompt 2-Vが5語上限を守らなかった(正当な除外)。ただし、本文に無い語を足さずに5語以内へ寄せられる。リスクは**意味反転と比喩の喪失**: `too`を落とした`soon to wave a flag`は「時期尚早」が「もうすぐ振る」に反転する。`wave a flag`だけにすると「時期尚早に勝利を宣言する」という比喩の核(`too soon`)が消え、字義の旗振りに読める。

### A1 連続部分列への短縮(現行規則内・受理面不変)=区分2(救済フロー本体の採否)
1. 元句のトークン列から、真部分の連続列(1〜5語)を全て列挙(決定論)。
2. **決定論の禁止表**: (a)演算子語(`too/not/never/no/only/hardly/barely/scarcely/rarely/seldom/nor/neither/less/least/nothing/none/nobody/without/cannot/nowhere/almost/nearly`、`n't`)を落として**被演算子(直後語)だけを残す**案は禁止(意味反転)。演算子が句末に残り被演算子が無い案も禁止(未完)。(b)先頭/末尾が機能語(冠詞・前置詞・接続詞・be等)の案は禁止。(c)機能語/代名詞だけの案は禁止。(d)動詞が句末に残り目的語・補語を欠く案は禁止(例: `too soon to wave`。比喩が目的語側にある場合に字義へ誤解されうる)。
3. 既存selection gate(本文連続一致・1〜5語・有限助動詞・数値)+CMU+既存候補との包含/重複を再適用。
4. 順位(HRに最初に見せる1案だけを決めるための決定論ヒューリスティック): 元句の演算子語を保持 > 動詞アンカー(先頭の動詞形、無ければ最初の`to`直後)を含む > 語数が多い > 右端が句末/前置詞句の直前 > 左に近い。同一系統からHRに出すのは1案(call2の重複規則)。
5. 候補が複数あるとき、**LLMを評価者として使う任意段**(約0.1円/呼出)。全部`reject`なら救済しない。

**実証**(`rescue_eval_07.json`): 有効な連続部分列は`too soon`/`wave a flag`/`flag`の3案(`soon to wave a flag`等は(a)で、`too soon to wave`は(d)で、`to wave a flag`/`a flag`は(b)で禁止)。LLM評価8回: `too soon`=7回すべてadopt系・意味narrowed、`wave a flag`=8回中7回「意味changed」、`flag`=全reject。**決定論の第1案=`too soon`**。→ 救済率への寄与は小さい(2語の狭い単位。学習価値の最終判断はHR=ユーザー)が、本文対応・意味保持・自然さの基準は満たす。
**設計の改善履歴**: 初版の順位は「接尾部分列優先」で`wave a flag`を第1案にした → LLM評価で「意味changed」と判明 → 演算子保持優先+動詞句末禁止へ変更(LOOP_LOG ループ2)。

### A2 スロット一般化(`too soon to do`)=区分3推奨(ユーザー例のため区分2の判断材料も併記)
- 生成(決定論): `(…) to <動詞句2語以上>`の動詞句を`to do`へ。検査: 演算子を保持/語数≤5/CMU/助動詞なし/置換tailが2語以上/元句の冒頭連続部分列を保持。DEV実装済み(`slot_generalization_candidates`)、全検査PASS。
- **現行規則との衝突**: 本文に無い語`do`を生成する=Rule7(「source_spanに存在しない別の辞書形を勝手に生成しない」`kc:620`)と衝突。承認済みの一般化は「人称・参照語の閉じた1対1置換」だけ(`one's/someone/a`)で、N対1の動詞句一般化は範囲外(新規則)。
- **意味保持・品質**: LLM評価8回中7回reject(「`to do`で終わる形は不自然」「原文にない語」)、1回だけadopt_with_hr_flag(weak)。元の語`wave a flag`が担う比喩を失い、枠(`too soon to + 動詞`)だけが残る。
- **結論**: 本文対応が失われ、不自然な単位になる→**区分3推奨**。「現行規則違反だから不可」ではなく、(1)検査は通る形を実装し、(2)意味保持と自然さを独立評価で測り、(3)基準を満たさなかった、という根拠。ユーザーが枠学習の価値を重視して採用する場合は新規則(スロット一般化)となり、`auto_eligible=False`・HR表に元句と本文の文を併記・否定/程度語の保持(DEV実装済み)を必須条件とする。
- 代替: A1(`too soon`)、または救済しない(外側retryに任せる)。

### A3(参考・非推奨) 語数上限の6語への緩和
承認済み1〜5語(`CURRENT_SPEC.md:1962`)の変更になるため品質基準の変更=ユーザー承認事項。発生率はHR導入後12 level-runで1件(8%)。非推奨。

---

## B. 動詞の活用形→基本形(原形化)のguard

### B-0 guardの必要性・承認根拠・副作用(結論)
- **承認根拠**: `_guard_ok`(`er105:662`)の次トークン条件は**承認文に無い実装判断**。承認文=P-04「動詞の活用形変換は先頭トークンかtoの直後に限る」(`OPUS_REVIEW_COND_A_01.md:118-123`)と`CURRENT_SPEC.md:1997`。guardは配線commit `84d9a6412`(2026-10-22)がコメント`er105:570-575`と共に導入(OPEN-530で記録漏れ登録済み)。
- **必要性(guardの目的)**: P-04が防ぎたいのは`heated debate→heat debate`・`mixed feelings→mix feelings`型=**形容詞化した分詞+名詞**の誤変換。直後が名詞のとき分詞が形容詞である可能性があるので、直後が限定詞/代名詞/不変化詞/前置詞のときだけ原形化を許す設計。この目的に対し`_PARTICIPIAL_ADJ_EXCLUDE`(閉表)が既にある。
- **副作用(過剰除外)**: 直後が副詞・量化詞(`no/each/every/all…`)のとき、分詞は動詞用法で、guardの目的と無関係なのに拒否される。HR導入前29種中6種(`accepts no responsibility`・`leaving no mark`・`pulling free`・`eased open`・`growing louder and louder`・`lost touch`)、HR導入後1種(`studied separately`)が該当。**guard全体を撤廃すると誤受理が増える**ので、目的に適う範囲だけ広げる。

### B-1 修正方式(区分別の階層)
| tier | 追加する条件 | 目的との整合 | 区分 |
|---|---|---|---|
| T1-quant | 直後が量化詞限定詞(`no/each/every/all/both/another/either/neither/several/few/many/much/enough`) | guardの文言は「限定詞」。`no/each…`は限定詞なのに表の網羅漏れ | **区分1** |
| T1-adverb | 直後が**manner副詞**(`-ly`、ただし`-ly形容詞表`[friendly/lovely/early/daily/only/likely…]を除く、および`again/alone/hard/well/fast/often/always/never/still`)で、副詞が句末、または直後が前置詞/不変化詞/限定詞/等位接続詞 | 副詞が続く分詞は動詞用法。副詞の後が名詞なら(形容詞+名詞の可能性)不許可 | **区分1(Fable確認事項: 『規則文に無い内部条件』を承認文の水準へ戻す是正。受理面の拡大と見る余地があるため境界判定を依頼)** |
| T1-past | 過去形専用/曖昧不規則表の補完(`rang/sang/ate/drank…`51語+曖昧20語+分詞35語。`bound`除外=OPEN-476) | 承認文は不規則形一般 | **区分1** |
| T2-lexicon | 辞書裏付け: 原形句がWiktionary見出し(idioms/phrasal verbs/proverbs、延べ17,389件・重複含む)に一致すれば、V+名詞でも動詞用法と見なす(`lost touch→lose touch`) | 規則文より広い(外部データを受理根拠に使う) | **区分2** |
| 不採用 | 補語形容詞(`free/open/louder`)・V+名詞一般の受理 | 形容詞/名詞用法との区別にPOS情報が要る | 表層形のまま(revert)で候補に残す |

### B-2 誤った原形を作るリスクの検査(必要十分)
T1-adverb/T1-quantの追加経路にだけ課す(既存経路は無変更): ①**LLM提案語**であること(再導出ではdisplay語/LLM語のみ、前回M1) ②**CMU実在** ③**前方活用生成一致**: 原形から規則/不規則活用を前方生成し、displayの語が生成集合に含まれること(`hoped→hop`は不一致、`hoped→hope`は一致。単音節/語末強勢のCVCは重子音、無強勢はそのまま=`hop→hopped`・`visit→visited`をCMU強勢で判定)。④**文脈**: 副詞は句末/前置詞等の直前。⑤既存の形容詞化分詞除外表・複数除外表は維持。
**実証**: 実選定句315種(X/Y/Z全KP出力)に対し、既受理84ペアの取りこぼし0(単調性)、新規受理は3変換のみ(`rang through→ring through`・`studied separately→study separately`・`thrown into it→throw into it`)で全て妥当。初回実装で`bound to the protein→bind to the protein`の誤受理が出て`bound`を表補完から除外(OPEN-476=DEFERRED)。敵対的な組(`heat debate/mix feelings/limit time/use cars/break record/close doors/new(news)/bind to`)はT1後も全て拒否(test `test_participial_adjective_nouns_still_rejected_under_tier1`)。`hop quietly`(`hoped quietly`)はCMU実在語でも前方生成不一致で拒否(test)。

### B-3 救済フローとの関係
通常フローで通る(区分1)ので`rescue`記録は不要。通らない場合(T2やV+名詞/補語): 表層形へ戻す(revert。`er105:575`の設計意図どおり)。`pulling free`・`eased open`・`growing louder and louder`はrevertで候補に残る(LLM評価: 3回すべてadopt系、学習単位は`pulling free`=good/`eased open`=weak)。revert候補は`auto_eligible=False`・「原形化できず表層形」旗。

---

## C. 助動詞と一般動詞(`have a say`・`had our eye on`)

### 原因
語形リスト(`have/has/had`を一律に有限助動詞とみなす)が用法を見ない。OPEN-152(2026-09-14、語彙動詞haveの誤検知、`USER_DECISION_REQUIRED`/Non-blocking)として既出。原意図は「完全文・節・時制付き動詞句の排除」(ER-003-P2G)。承認済みP-04(3)の`has/had→have`と自己矛盾(CASE_ANALYSIS §0-2)。

### 方式: 役割判定(区分1)
`have/has/had`は、直後が限定詞/所有格/数量詞/名詞句の始まりなら**語彙動詞(受理)**。次は**助動詞(拒否=現行どおり)**: 直後が過去分詞(規則`-ed`[形容詞化分詞表を除く]・不規則表・追加分詞表)、`been/being/to/not/never/already/ever/just/better/rather/got`、主格代名詞(倒置: `Have you…`)、副詞(`also/often/only/finally/just/already…`)、文頭の大文字`Have/Has/Had`(倒置・疑問)、`have+名詞主語+been/過去分詞`(倒置)、句末。形容詞化分詞(`limited`等)は直後が名詞のときだけ語彙(`have limited access`)、目的語を取る形(`have limited the damage`)はaux。**迷えばaux=拒否**(現行どおり。受理面は広げるが誤受理側に倒さない)。
法助動詞(will/would/can/could/should/may/might/must)・be系(is/are/was/were)は区別しない(節の核。現行どおり拒否)。
**Production差分は`fulltext`経路限定**(`allow_inflection_normalization=True`のとき)。A/B/C(27-7)の判定は無変更。

### 実証
- test 25ケース(語彙9/aux16)全PASS。実本文の`have/has/had`始まり2〜4語窓: 現行で拒否→新たに通る71窓を人手レビュー(`have_probe_01.json`): 全て語彙用法(`had a problem`/`had no time`/`has more to`/`have in common`/`have your watch`…)。倒置/副詞挟み(`Had users been`/`have only put`/`had also faded`)は初版で漏れたが、レビューで検出して判定を強化(LOOP_LOG ループ4)。
- `had our eye on`→原形`have our eye on`も通る(P-04(3)のdead pathが解消)。`have a say`通過。X事前世代の`have a big moment`(key側)も解消。

### 慣用句の法助動詞(`it can’t be helped` / `can’t be helped`)= 区分2
承認済み規則の意図は「完全文・節の排除」。`it can’t be helped`は主語を持つ完全文=意図に当たる。`can’t be helped`は節の断片だが、日本語の「仕方がない」に対応する固定表現(Wiktionary慣用句見出し`it can't be helped`の核)で、助動詞を外すと意味が壊れる(`be helped`)。
方式(区分2): 法助動詞を含む句は、**辞書見出し(または`it/that+核`見出しの核)に一致する場合だけ**例外とする。**主語で始まる完全文は例外にしない**: 主語(it/that)を除いた本文の連続部分列(`can’t be helped`)だけを通す。例外の外(辞書に無い`could not bear`等)は現行どおり拒否。LLM評価3回すべてadopt(意味same・good)。
ユーザー判断の理由: 承認済みの「助動詞排除」に慣用句の例外を設ける(受理面の拡大)。外部データ(Wiktionary見出し)を根拠にする点が新しい。

---

## D. その他

| # | 内容 | 方式 | 区分 | 実証 |
|---|---|---|---|---|
| D-1 | LLMの範囲拡張(`rise above the other voices`→display窓`rose above`) | **M1再導出**: LLM keyの先頭`len(display)`語を窓として、各位置で{display語, LLM語}から選ぶ(LLM採用語数の多い順に既存validatorで試す)。窓外のtailは捨てる。新語形を作らない | 区分2(救済フロー) | `rise above`(Wiktionary句動詞)・`hold out`(同)。LLM評価3回すべてadopt系(`rise above`は1回「別義にも使われる」旗付き) |
| D-2 | 人称一般化とlemmaがロールで食い違う(`my ears began to ring`) | 同上。LLMの`one's`は採用し、通らない`begin`はdisplay語`began`に戻す | 区分2(救済フロー) | 4種全てadopt |
| D-3 | 本文不一致(LLMが原形で返した`catch their interest`) | **再アンカー**: `find_inflection_window(phrase, 本文窓)`(既存validatorを逆向き)が成立する本文窓を探す。窓が一意なときのみ表層形へ戻す。窓が無い(`in his place`)/複数は救済しない | 区分2(救済フロー) | `catches their interest`・`lost my trust in you`。創作句`grab their attention`は不一致(test) |
| D-4 | CMU未登録(`redelivery fee`) | 分解(`re`+`delivery`、両方CMU登録)は**可能**だが、合格にすると「推測による代替合格」。実TTS音声のASR一致を要件にする案もあるが、1/12 level-runで他候補が補える | 区分2・**非推奨** | `minaudière(s)`は分解不能=区分3 |
| D-5 | 構造違反/CMU post-canon(LLMのkeyが原因) | **displayへ戻す(revertのみ)**。戻した後に既存validator+CMUを再検査(前回R1) | 区分2(救済フロー) | 実イベントは未観測。DEV synthetic testのみ(`test_structural_revert…`) |
| D-6 | 助動詞を外した連続部分列(`were mocking me`→`mocking me`) | A1と同じ連続部分列+LLM評価の多数決(同一入力でも評価が揺れるため3回中2回以上) | 区分2(救済フロー) | `mocking me`のみ採用。`could not bear`→`not bear`等は意味changed/reject→区分3 |
| D-7 | 閉表の網羅漏れ(過去形) | B-1 T1-past | 区分1 | `rang`/`struck`/`froze` |
| D-8 | Human NG | 復活しない | 区分3 | match_ng(selection_phrase/used_form両方) |

## E. gloss・QA・HR引渡しの一貫設計(前回M3/M4)
- 区分1(通常フロー)は何も追加しない(LLMが通常どおりgloss/QAを付ける)。
- 救済フロー候補: `rescue = {applied, method, before{selection_phrase, llm_key_phrase, stage, reasons}, after{used_form, display}, recheck, gloss{realign_required, status_if_unresolved}}`、`flags.rescued`、`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`、`auto_eligible=False`、HR表の旗「修正済み(元: …)・QA未再判定」。**LLMのqa_*欄は上書きしない**。`final_key`がLLM提案keyと異なるとき`gloss.realign_required=true`(`hold out one's hands`の「両手を差し出す」が`hold out`に残らない)→再整合に失敗したら`gloss_hr_pending`。DEVでは`make_rescue_record`が上記を出力(`rescue_eval_07.json`の`rescue_record`)。
- HR表(`render_request_md`)には元句・本文の文・修正方式を併記。`dropped[]`には救済候補化した場合も元の除外理由を残し`rescued_as`を付ける。

## F. HR経路限定・外側retry維持(前回M2/M5)
DEVは救済を`er119 generate_candidates`経路だけの後処理として設計(`canon_fn`/`select_fn`への明示引数、既定OFF)。HRを経ない経路(`run_key_phrases`→`run_kp_with_outer_retry`、Zの`run_kp_with_outer_retry_fulltext`)では出力バイト同一をtestで固定(Production実装時の必須test、DESIGN_01 §6)。外側retryのトリガー判定では救済句を`gate_dropped`相当として数え、累積除外リストには入れない。
