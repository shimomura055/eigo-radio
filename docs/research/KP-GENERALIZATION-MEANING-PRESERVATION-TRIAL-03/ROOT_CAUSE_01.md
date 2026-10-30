# ROOT_CAUSE_01: Key Phrase一般化で「本文と異なる意味・用法」が入った原因(KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03 委任_01、2026-10-30、API 0)

原文=`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03_USER.md` §2・§3(逐語保存済み)。
調査方法: TRIAL-02の保存結果(`../KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02/kpg03_work/results/*.json`のtokens・verify・display_form_pre_fix)と、**実際のLLM入出力キャッシュ**(`../KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/kpg01_work/llm_cache/<key>.json`。metaのtagで工程特定)、Prompt生成コード(`kpg03_methods.py`・`kpg01_gen2.py`・`kpg01_methods.py`)を突き合わせた。新規API呼出0。
凡例: **[確認]**=保存された入出力・コードで直接確認 / **[推測]**=確認データからの推論(検証方法を併記)。
注意: キャッシュはgit管理外(ローカルのみ)。再現性のため、下記に該当出力を引用した。

## 0. 結論(先に)
| 項目 | 結論 |
|---|---|
| `hear it out`→`hear something out` | **[確認]** 本文の指示対象は誤っていない(itは擬人化された「サプリ」=物。E2のsense_noteも「補助食品の言い分を聞く比喩」と認識)。誤りの本体は、**someone/somethingを「本文の指示対象」で決める規則**(GEN Prompt規則A)にあり、「`hear ... out`という見出しの標準用法(人を取る)」を見る工程がどこにも無い。tokens分類は11/11 runで `it=SLOT_THING`。最後の安全網(別系列VER)がsomeoneへ直したのは3/11 runだけで、確率的。 |
| `take points away from`→`take away from` | **[確認]** 目的語の除去は**一般化(GEN)ではなく検証(VER, gemini)で起きた**。GENは正しく`take something away from`を作っていた(`display_form_pre_fix`)。VERが「日本語訳が『価値や効果を損なう』なので、イディオムは目的語を取らない形が正しい」と判断し`take away from`へ直した(`meaning_preserved=true`のまま)。**その日本語訳は、本文の意味(減点する)ではなく選定工程(SEL)の理由文由来**。 |
| E2/E3/E4が`take something away from`を保てた理由 | **[確認]** 上位モデルのためではない。E4のsolは塊判定(SEL)にだけ使われ、一般化(GEN_ALL, luna)はE2/E3/E4で**同一キャッシュ(同一call)**。差の実体は**工程順序と情報の流れ**: GENが選定理由を受け取らないため、日本語訳が本文由来(「〜から評価を差し引く」)のまま残り、VERは形ではなく訳を直した。 |
| 二つの誤りは同じ原因か | **別原因**。前者=見出しの標準用法を見る工程の欠落(+規則の定義誤り+安全網の確率性)。後者=上流の誤った語義(選定理由)が後続工程へ「アンカー」として伝播し、検証が本文ではなく上流の訳に整合させた(+検証Promptが目的語の除去を促す)。対策も分離する(DESIGN_01)。 |
| 既存の独立評価は検知できていたか | **[確認]** 検知できていない。deepseek-flash(TRIAL-02独立評価)は両誤りを16/16件「OK」と判定。gemini判定は正解側(D: `hear someone out`)をNOT_GENERALIZED(不可)とし、誤り側を可とした(逆向き)。評価Rubricが「someone/somethingは本文の指す対象に合う」(`kpg03_judge.py` RUBRIC)と指示しているため。 |
| Productionの現状 | **[確認]** Production(P7・canonicalization)は規則1〜5以外の一般化を禁止しており、`hear it out`/`take points away from`は**そのまま通る**(保存docのgloss「最後まで話を聞く」「～から点を差し引く」=正しい)。この誤りは**TRIAL-01/02で導入した一般化層が作ったリスク**で、現行Productionの不具合ではない(`../KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/CURRENT_STATE_01.md` 3節)。 |

## 1. 事例A: `hear it out` → `hear something out`
### 1-1. 本文(untidi_a2)
`...That supplement may be taking its job quite seriously.` の直前文 `Before you bring out the storage box, hear it out`。記事は「サプリを被告に見立てた模擬裁判」の比喩で、`it`=サプリ(物)。Productionの保存gloss=「最後まで話を聞く」。

### 1-2. 工程別の事実(E1L, `untidi_a2__E1L.json` / キャッシュ`40307068…`(SEL), `ee27df7d…`(GEN), `5412dc05…`(VER))
| 工程 | 入力で与えた情報 | 出力 | 判定 |
|---|---|---|---|
| SEL(luna, span判定) | 本文語句`hear it out`と文 | 理由「**hear someone out**で相手の言い分を最後まで聞く」・C | **[確認]** 選定段は見出し形を正しく知っていた(someone) |
| GEN(luna) | 語句・トークン・本文の文・**SELの理由(塊の種類/理由)**・記事全文。規則A「目的語の位置の語が本文で人を指すならSLOT_PERSON、物・事ならSLOT_THING」 | tokens: hear=CORE, **it=SLOT_THING**, out=CORE → `hear something out` | **[確認]** 規則Aを字義どおり適用(itは物=サプリ)。SELの`hear someone out`は規則上の根拠にならず無視された |
| VER(gemini) | 形`hear something out`・訳・理由・本文 | `OK`(meaning_preserved=true, natural_headword=true) | **[確認]** 検査項目(a)〜(e)に「someone/somethingが見出しの標準用法に合うか」が無い |
| 決定論検査(display_check) | 形とspan | 通過(somethingはプレースホルダ許容) | 検知対象外 |

### 1-3. 確認事項への回答
- **itの指示対象**: [確認] サプリ(物、擬人化)。モデルは正しく把握(E2 sense_note「補助食品の言い分を聞く比喩」)。**「itを機械的にsomethingとした」というより、「物を指すからsomething」という規則どおりに動いた**。
- **`hear ... out`の語義・用法**: 辞書上は「人の話を最後まで聞く」で目的語は人。物を取る用法は標準ではない。[確認] SEL・E1L/E2/E3のVER(`natural_headword=false`「hear outは人に対して使う」)は知っていた。
- **どの工程でsomethingが選ばれたか**: [確認] GEN(トークン分類)。D/E1L/E1S/E2/E3/E4の**全11 run**で`it=SLOT_THING`(`hear someone out`が出たのはVER FIXの3 run: untidi_b1b D, untidi_a2 E2, untidi_a2 E3)。
- **人・物・事柄の判別は行われたか**: [確認] 行われた(SLOT_PERSON/THINGの二択)が、**判別基準が「本文での指示対象」**であり、見出し形の標準用法ではない。擬人化・比喩の扱い規則が無い。
- **文脈は十分だったか**: [確認] 十分。GEN/VERには記事全文と文が渡されている(`BODY + text`)。**不足したのは文脈ではなく判断基準(見出しの標準的な項タイプ)**。
- **VERの確率性**: [確認] 同一prompt種でも D untidi_b1b=FIX(someone)、E1L untidi_b1b=OK(something)。安全網としては不安定。

## 2. 事例B: `take points away from` → `take away from`
### 2-1. 本文の意味
`A scorecard might say, "The fewer things you can see, the better." But that could take points away from the ways each home has found to make life work.` → スコアカードの比喩で「(各家庭の工夫から)減点する」。Production保存gloss=「～から点を差し引く」(正しい)。

### 2-2. E1Lの工程別の事実(キャッシュ`40307068…`(SEL), `ee27df7d…`(GEN), `5412dc05…`(VER))
| 工程 | 出力(引用) | 判定 |
|---|---|---|
| SEL(luna, span) | 理由「take something away fromで**価値や効果を損なう**」 | **[確認]** 語義の取り違えの発生点。見出し形は正しい(take something away from)が、語義を別見出し`take away from`(=detract from)の語義へすり替え。同じ表現はTRIAL-01のC1_luna:B2にも既出(「価値や効果を損なう意味で使う句動詞」)=再現する癖 |
| GEN(luna, **SEL理由を入力に含む**) | tokens: take=CORE, **points=SLOT_THING**, away, from → `take something away from`。gloss「**〜の価値や効果を損なう**」 | **[確認]** 形は正しいが、**glossはSELの理由文をそのまま写した**(形=減点系、訳=損なう系で不一致) |
| VER(gemini) | FIX: `take away from`。issue「『〜の価値や効果を損なう』というイディオムの場合、通常目的語をとらず`take away from`の形で用いられます。本文の`take points away from`は比喩的にpointsを入れた表現です」。`meaning_preserved=true` | **[確認]** **目的語(points→something)を除去した工程**。形と訳の不一致を、**訳に合わせて形を直す**方向で解決した |
| 決定論検査 | 通過(`take away from`は`take points away from`の部分列) | 検知対象外 |

### 2-3. 確認事項への回答
- **どの工程でpointsが除去されたか**: [確認] 2段階。①GEN: `points`→SLOT_THING(something)=形としては目的語を残した(正しい)。②**VER: `something`自体を削除**して`take away from`にした(最終的に`points`相当が無くなった工程)。
- **目的語・前置詞の関係の判定**: [確認] 誰も本文でのframe(`take X away from Y`=XをYから取り除く)を検査していない。VERの検査(c)「不要な目的語…が残っていないか」は目的語を除く方向へ促し、重要注記「元の本文の語を戻す方向のfixは書かない」と合わせて、**除去のみ許される**設計になっている(`kpg01_methods.py` `prompt_B4`)。
- **語義変化を検知できなかった理由**: [確認] 各工程は上流の出力(理由→gloss→形)と整合を取るだけで、**本文の文から語義を独立に導き直す工程が無い**。VERのmeaning_preservedは「形と訳の整合」を見ており、訳が既に誤り(上流由来)のため、整合を取るほど誤りが固定される。
- **本文の文脈と日本語訳がどこで切り離されたか**: [確認] SEL→GEN。glossの根拠が「本文」から「SELの理由文」に切り替わった時点。以降(VER)はこの訳を基準に形を直した。
- **E2/E3/E4が`take something away from`を生成できた理由**: 次節。

## 3. E2/E3/E4が回避できた理由(上位モデルのためではない)
| 要素 | E1L | E2/E3/E4 | 根拠 |
|---|---|---|---|
| 工程順序 | SEL → GEN → VER | **GEN_ALL → SEL → VER(/GATE)** | `kpg03_methods.py` run_E1(l.274-282) / run_E2(l.285-) |
| GENが受け取る選定理由 | あり(`with_chunk=True`、l.280、プロンプトl.100「塊の種類/理由」) | **なし**(`with_chunk=False`、l.289) | 同上 |
| GENが出したgloss | 「〜の価値や効果を損なう」(SEL理由の写し) | **「〜から評価を差し引く」**(本文由来。sense_noteは「各家庭の工夫の価値を損なう」) | キャッシュ`ee27df7d…`(E1L GEN) vs `4b614964…`(E2 GEN_ALL) |
| VERの状況 | 形(somethingあり)と訳(損なう)が不一致 → **形を直した** | 形と訳が整合。残る不一致は「訳にpoints(評価)が残る」(gloss_consistent=false) → **訳を直した**(`〜から…を奪う、損なう`等)、形は保持 | `untidi_a2__E2/E3/E4.json` verify.issue |
| 使われたモデル | luna | **GEN_ALLはE2/E3/E4で同一call(luna)**。E4のsolはSELのみ | `kpg03_methods.py` run_E2(m_sel=SOLはSELだけ)。E4のGEN_ALLはE2とcache共有(設計書§3) |
**E4の判断方法の低コスト再利用**: E4固有の「判断」は存在しない(solはkeep判定のみ)。再利用できる要素は(1)**生成を選定理由から切り離す**こと(N1: 選定済み候補のGENでSEL理由を渡さない。追加call 0)、(2)**形と訳が食い違うとき本文の語義を基準に直す方向を指定**すること(VER Prompt。追加call 0)、(3)本文から語義を先に確定させる(N2)こと。E2型(全候補を一般化)は良質候補の脱落が大きい(脱落20/60 vs E1L 13/60、`kpg03_work/stats_14.txt`)ため、E1Lの選定段は維持する(DESIGN_01)。
**[推測]** E2系が回避できたのは構造的要因だが、1例(n=1)かつVERが確率的なため偶然の寄与は排除できない。検証=probeのablation(P0 vs N1a, DESIGN_01 §5)。

## 4. §3の7仮説と証拠
| # | 仮説 | 判定 | 証拠 |
|---|---|---|---|
| 1 | 本文中の語義を誤って理解した | **部分的に該当(B)/該当せず(A)** | B: SELが`take points away from`を「価値や効果を損なう」と誤読(キャッシュ`40307068…`、TRIAL-01 C1_luna:B2にも同表現)。A: `hear it out`の語義(最後まで聞く)は全工程で正しい |
| 2 | 代名詞の指示対象を誤った | **該当せず(A)** | itの指示対象(サプリ=擬人化された物)は正しく把握(E2 sense_note)。**誤りは指示対象ではなく、規則Aが指示対象でsomeone/somethingを決める点**(`kpg03_methods.py` GEN4_EXTRA A、`kpg01_gen2.py` l.22) |
| 3 | 意味上必須の要素を削除した | **該当(B)** | VER(gemini)が`something`(=points)を削除。検査(c)が除去方向のみを許す(`prompt_B4`)。**ただし許容される修飾語除去(set a lower limit→set a limit等)とは区別**: 原文§2-C。TRIAL-02の判定はこれらを`MEAN`NGにしており(`kpg03_manual.py`)、原文の新基準と食い違う→再判定要(P0) |
| 4 | 自然な一般形だが別の語義に変わった | **該当(B)** | `take away from`(=detract from)は自然な別見出し。英語としての自然さは検知手段にならない |
| 5 | 一般形と日本語訳の対応が崩れた | **該当(B、原因側)** | E1L GEN出力: 形`take something away from`+訳「損なう」の不一致(SEL理由の写し)→VERがこれを形側で解消 |
| 6 | 塊判定が一般化後の語義変化を見逃した | **構造上該当(A・B)** | E1/D系の塊判定は**本文語句(span)**を判定(`mode='span'`)し、一般化後の形を見ない。判定の対象外。VERも一般化前後の語義比較をしていない。E2系は形を判定するが、語義の同一性は判定項目に無い |
| 7 | 工程順序や入力文脈の不足 | **順序は該当(B)/文脈不足は該当せず** | 順序: SEL理由がGENとVERへ伝播(アンカー)。文脈: 記事全文・文・理由が全工程に渡されている |
| (追加8) | 安全網の確率性 | **該当(A)** | hear it outのVER: someoneへの修正3/11、残りOK。同一入力種でも結果が割れる |
| (追加9) | 独立評価の盲点 | **該当** | deepseek-flash 0/16検知(両誤り)、geminiは逆向き。Rubricが指示対象基準(`kpg03_judge.py`) |

## 5. 原因の分離(一つの対策で全部を処理しない)
| 原因 | 事例 | 対策の方向(DESIGN_01) |
|---|---|---|
| R1 見出しの標準用法(項タイプ)を決める工程と規則が無い | A | 一般化で「headword_frame」を本文の指示対象と独立に書かせ、tokensと不一致なら決定論で調停(N2) |
| R2 上流の語義(選定理由)が後続へ伝播するアンカー | B | GENへ選定理由を渡さない(N1)。語義は本文から再導出(N2) |
| R3 検証が上流の訳に整合させる/目的語除去を促す | B | VER Promptに「本文の語義が基準」「訳に合わせるだけで目的語・前置詞を削らない」を追加(追加call 0。N1以降) |
| R4 安全網の確率性・独立評価の盲点 | A・B | 決定論flag(疑わしい候補のみ)に別系列の局所検査(N4)。評価はRubric刷新+既知NGで判定器の感度を事前確認 |
| R5 判定基準の食い違い(修飾語除去) | C | 原文§2-Cを評価Rubricに反映(2軸分離、`kpg04_manual.py`)。過去判定の再読み替え(P0) |

## 6. 追加で分かった事実(設計に使用)
- 決定論flag(`kpg04_methods.flag_item`、LLM不使用)を既存結果に適用(API 0): **S軸の誤り全7件(D: hear something out 1、E1L: hear something out 2+take away from 1、E2/E3: hear something out 1、E4: hear something out 2。E3はE2と同一のためE2/E3は合わせて1種)は全てflag済み**(hear it out=PRONOUN_SLOT、take away from=VER_FIXED_FORM)。正しかった同表現(E2/E4の`take something away from`、D/E2/E3の`hear someone out`の一部)は一部flagされない/される。flag率(項目比): D 42%、E1L 40%、E2 34%、E4 30%。1回以上flagのあるレベル 11-12/14。→ 疑わしい候補限定の検査は「項目の約3-4割・ほぼ全レベル1call」(費用見積はDESIGN_01 §6)。**ただし既知の誤りに対して作ったflagの検出率であり、未知の誤りクラスへの感度は未検証(probe 42件とheld-outで測る)**。
- TRIAL-02のSonnet判定は`set a limit`/`take a turn`を`MEAN`NG(E1L: 3件)としたが、原文§2-Cは許容→新定義でのS軸NG(意味・用法)件数はD 1/71、E1L 3/81(hear×2+take away from)、E2 1/77、E3 1/77、E4 2/70。**母数が小さく率の差は数件**であり、probe(42件)とheld-outで補う。
- 本調査は1記事2事例(n=1)の機構解明。**他の誤りクラス(FRAME_SHIFT: take up space→take up、MOD_SHIFT等)がTRIAL-02結果に潜在するかは未確認**(P0の再監査で確認する。設計書)。

## 7. 参照(再現用)
- 実データ: `kpg03_work/results/untidi_a2__{D,E1L,E1S,E2,E3,E4}.json`、`untidi_b1b__*`
- キャッシュ(ローカル): `kpg01_work/llm_cache/` の `40307068e1b1cf3acd13bdd3`(E1L SEL)・`ee27df7d0b380322a4f3bd6a`(E1L GEN)・`5412dc0548cc5c538ab3c464`(E1L VER)・`4b6149643e89f11979e37120`(E2 GEN_ALL)・`3033a74517384725efc30301`(TRIAL-01 C1 B2)
- Prompt/コード: `kpg03_methods.py`(run_E1/run_E2/GEN4_EXTRA/prompt_G4)、`kpg01_gen2.py`(GEN2_RULES)、`kpg01_methods.py`(prompt_B4)、`kpg03_judge.py`(RUBRIC)
- 未実施: キャッシュkeyからのPrompt全文の再構成(出力一致とコード読解で代替)。
