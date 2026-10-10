# RESULT_01: B3 Selected Factsへの指示混在の根本対策Trial(Phase 2、MEASURED)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 委任_03 / 2026-10-10。Production code・Production Prompt・CURRENT_SPEC は変更していない。後段AI(新Checker・二重チェック・補正AI等)は追加していない。
実費 **JPY21.67**(Cap JPY60、B3 36 call + Writer R0 12 call = 48 call、技術retry 0、出力無効 0)。
使用モデル(25節): B3 = `gpt-6-luna`(Production B3と同一条件。gpt-6世代の最新だが最上位系かは未確認。理由=本番と同じモデルでの差を見るため)、Writer R0 = `gpt-6-luna`(effort high、Production同一Prompt)。返却modelも全call `gpt-6-luna`。

## Status提案: **VALIDATED(Trial限定、案D)。ただしProduction採用は USER_DECISION_REQUIRED**
- VALIDATEDでも `APPROVED_FOR_PRODUCTION` ではない。**Production実装には進まない**(コード・Prompt・CURRENT_SPEC は未変更)。
- 案D: D-minは事前登録基準を全て満たす。D-fullは採用候補規則(E5)で選ばれE9(有料)も実施したが、**E4(b)の厳格基準だけ未達**(下記)。D-minのE9は未実施(事前登録どおり1変種のみ)。この穴と変種選択はユーザー判断に残す。
- 案A'(Prompt変更): **事前登録のE3基準(95%)に不達**(81%)のため不採用。ただし混入は18本中0件で、Prompt変更だけでも混入は止まる(数字の脱落は現行B3と同程度)。

## 1. 非エンジニア向け9点
1. **なぜ混ざっていたか**: AIが「事実の要約文」を作る工程(B3)に、台帳の「Writerへの注意書き」(`notes_for_writer`)をどう扱うかの指示が一切なく、AIが気分で取り込んだり落としたりしていた。しかも以前はWriterが台帳を直接読んでいたのに、B3導入(2026-09-26)で台帳が渡らなくなり、注意書きの届け方が決められないまま切れた。
2. **どこで混ざったか**: 台帳の段階では事実と注意書きは別の欄に分かれている。混ざるのは**B3の自由記述の要約文を書く1点だけ**(ResearchやLedger工程では混ざらない。ただしLedger工程が曖昧なfactに指示調のタグ`[AMBIGUOUS - …]`を付ける点は混入源の一つ、INVESTIGATION_01の是正済み)。
3. **バグか意図された旧設計か**: 意図した設計ではなく**仕様の穴(副作用)**。混在を狙った記述はどこにも見つからなかった。ただしその後の規則(Fact Lock R0の規則4など)は混在を前提に作られている。
4. **最小の根本対策**: B3は従来どおり「どの事実を使うか」だけを選び、事実の文は**台帳の`claim`をそのまま1行1事実で決定論的に並べ**、注意書きは別ブロック(「Writerへの注意(事実ではありません)」)へ**そのまま転記**する(案D)。追加のAI呼び出しは0。
5. **Trialで本当に分離できたか**: できた。Facts側の指示文は **現行B3(再生成18本)で8本(44%)、既存9本で5本** に含まれていたのに対し、**案Dは54本(D-min/D-full各27)で0本**。案A'(Prompt変更)も18本で0本。目視で確認(現行B3の混入のうち3本は自動検出が見逃した)。Writerの記事(R0)でも、現行は**指示文を「事実」として出典タグ付きで引用**(6テーマ中5テーマ)し、台帳内部語「Ledger上」が記事に漏れた(1本)のに対し、案Dは**どちらも0**。
6. **B3注記AIは不要にできそうか**: **部分的に可能**。【事実N】と台帳IDの対応は、1事実=1行になったので**機械的に決定論で付けられる**(案D 54本で既存の注記形式検査 `check_a`/`check_d` が全PASS)。**残る課題は数値印**(【中核数値】/【周辺数値】の付与。どの数字が中核かの判断)で、これは本Trialでは未解決。別管理ID候補: 「B3呼出への中核数値構造化出力」(既存のB3呼び出しの出力に、採用factごとの中核数値の一覧を構造化して出させる。新規呼び出しなし)。
7. **記事あたり追加コスト**: **追加のAI呼び出し 0**。B3 1 callの単価はA'で+2.1%(JPY0.464 vs 現行0.455)、案D自体はB3の呼び出しを変えない。Writer R0の入力が増える分は1 callあたり+JPY0.047(+11.6%、JPY0.450 vs 0.403)程度で、1記事あたり**約+JPY0.05**。
8. **既存仕様への副作用**: 下の4節。要点=Q1(briefを決定論生成にすること=ユーザー確定事項(7)の読み方)、Q4(Storyline行内の注意は未対処)、Q5(BYD型で今まで届かなかった注意書きが新たに届く)。Production側は**R0入力の連結1関数+evidenceの2欄追加+4〜5箇所の読み替え**が必要で、Lane A(W-1配線)のrunner R0入力組立と編集箇所が競合する。
9. **Production採用に必要なユーザー判断**: 5節。

## 2. 評価結果(詳細は `eval/eval_results_02.json`、差分一覧 `eval/side_by_side_02.md`)
| 指標 | 結果 |
|---|---|
| E1 命令文漏れ | 現行B3(C1) 18本中 regex検出5本・**人手(腕名を伏せた全件目視)8本**(自動検出は3本を見逃し)。C0 9本中5本。**A' 0/18。D-min 0/27、D-full 0/27**(A'・Dは全文目視、regexも0)。台帳内部語・ID・Storyline重複行の混入(補足指標): C1で`Ledger`2本/ID付き2本/`Storyline：`重複1本、C0で1/1/2本。A'・Dは全て0 |
| E2 notes継承 | D-min/D-full **97/97(100%)**、A' **73/73**(完全一致)。現行は注意書き12字以上がWriterに届いた割合: C0 6/39(15%)、C1 6/58(10%) |
| E3 数値・日付 | D: claimの数字214件を欠落0・台帳に無い数字0(100%)。**A': 欠落30/161=coverage 81%(事前登録95%に不達)**、新数字0。参考: C0 76%、C1 65% |
| E4 主体・因果・時系列 | D-min: 差0(固有名詞欠落0、因果接続語増0、日付順差0)。**D-full: 因果接続語が14/27本で増加**(事前登録の厳格基準では未達)。全件が台帳の`scope`/`conditions`の文言由来で、claim+scope+conditionsに対する説明不能な増加は0。A': 日付順差6・因果増3・固有名詞欠落17本(B3の圧縮。意味を変える差は未確認だが、目視では致命的な差なし) |
| E5 情報欠落(C0/C1比) | 台帳根拠ありの欠落語: D-min 49、**D-full 20**(採用候補規則「max(10語,15%)以上少ない」を満たす)。残り20語は表記差(「唐系142」[数字の桁区切りで語が切れた]、「新価格」「政策金利」等のB3の言い換え語)で、事実情報の欠落は人手確認で0。台帳に無い語(B3の言い換え・新規)83語は対照側の特徴 |
| E6 乾式組立(全消費経路) | **PASS 54/54**。R0/注記系/er019 runner系/er012_e再生成系の全経路で同じニュース欄を組める。R0 promptの末尾(Fact Lock規則等)のsha256は6テーマ・両腕で一致(`edb558b1dd84`) |
| E7 注記LLM不要化 | 【事実N】付与+台帳ID対応は決定論で可能(54/54 `check_a`/`check_d` PASS)。数値印は未解決(6節、別管理ID候補) |
| E8 コスト・時間 | B3 C1 JPY8.185(平均0.455)、A' JPY8.358(平均0.464、+2.1%)、E9 D JPY2.702(平均0.450)、E9 C0 JPY2.421(平均0.403)。B3 latency 平均43.6秒。追加call 0(D・A'とも)。Trial module LOC: build 125 / eval 389 / driver 179 |
| E10 AMBIGUOUS保持 | D(D-min/D-full): 選択された6件全てで固定限定文あり+ambiguity_noteが制約側に存在(**6/6=100%**)。C0/C1/A'は曖昧語がbriefのどこかにある程度(目視確認が必要、合否なし) |

## 3. E9(Writer R0のみ、D-full vs 現行C0、6テーマ x 1 rep = 12 call)
| 観点 | C0(現行) | D(D-full) |
|---|---|---|
| (1) 制約/注意行への【事実N】付与 | 指示文が事実行として番号付き(5/6テーマ)。**Writerがその番号で引用** | 0(制約行への付与0、番号範囲外0) |
| (2) 注意文の逐語転記(12字以上) | 0 | 0(ただし言い換え形で反映された箇所は両腕にある=意図どおり) |
| (3) 台帳ID・台帳内部語の記事漏出 | **1本**(「Ledger上で…」+存在しない`【事実7】`引用、semiconductor) | **0**(HF-007「Ledger上では必ず…」を含むhormuzも0) |
| (4) AMBIGUOUS限定の反映 | - | semiconductorのF1(AMBIGUOUS)は記事で使われず、反映は確認できなかった(入力には存在) |
| (5) BYD型(注意が新たに届く) | notes0件 | 4件届き、記事は「ブレーキ灯が点き続ける誤信号」という公告の範囲に沿った(「効かなくなる」とは書かず) |
| (6) 記号Gate該当 | 0 | 0 |
| (7) R0タグ整合PASS | 6/6 | 6/6 |
| (8) R0冒頭復唱 | 1 | 0 |
| (9) 「Ledger上では」逐語転記 | 1(semiconductor) | 0 |
全12本の記事を通読し、Dの記事の品質(読み物としての面白さ)が目に見えて悪化した所見はなかった(品質の主評価はしていない)。数値印を付けていないため、両腕とも記事に数字がほとんど出ない(Trial共通の制約)。

## 4. 既存仕様への副作用(8点の詳細)
- **Q1(要判断)**: briefをLLM出力から決定論生成に変える点が、ユーザー確定事項(7)「LLM出力はJSON Evidence必須(…最終Selected Fact Brief)」の読み方に依存する。B3のcallとJSON schemaは従来どおり(`selected_fact_ids`を使い、`selected_fact_brief`は無視)。
- **Q3**: `ambiguity_note`は制約側へ、Fact行には固定限定文「この点は確定していない。」。ただし固定文は文全体にかかるため、semiconductor F1のように「確定していないのは『最も最近の発表』であって決算発表そのものではない」場合に読み違える余地がある(HUMAN_CHECK参照)。
- **Q4(未対処)**: Storyline行(テーマ文)の注意は対象外のまま残る。C0で2/9、C1で2/18(例「…ただし、この発表が『最も最近』かはLedger上確定できない」)。A'は18本中0(偶然)。
- **Q5**: BYD型で従来Writerに届かなかったnotesが届く=B3導入前の状態への回帰。E9では問題なし。
- **Fact Lock/W-1**: R0 Prompt・注記契約V1〜V10・R1/R2は不変。制約ブロックはニュース欄に残す(規則4が成立)。
- **Lane A**: runner R0入力組立(`worker_new_r0`)とentertainment runner 4〜5箇所が編集競合しうる。別管理IDにするかC2へ取り込むかは調整要。
- **B3注記(Lane B)**: 【事実N】付与は不要化できるが数値印が残る。Lane B保留4点(追加4 call再実行/max_tokens調整/Production採用判断/Luna寛容化)は本結果を見て判断。

## 5. Production採用に必要なユーザー判断(いずれも未承認の新仕様候補)
1. 案D(briefの決定論生成+制約ブロックの別連結)を採用するか(Q1)。採用するなら、A'を併用する必要はない。
2. D-min / D-full のどちらか(E9はD-fullのみ実施)。D-minのE9を追加実施するか。
3. 固定限定文の文言・置き場所(Q3)。
4. Storyline行の注意を別途扱うか(Q4)。
5. Lane Aとの調整(R0入力組立の編集をC2へ取り込むか、別管理IDか)。
6. Lane B(B3注記方式)の扱い。数値印を扱う別管理ID「B3呼出への中核数値構造化出力」を起票するか。
7. Production変更(er019 `build_selected_brief_markdown`置換/evidence 2欄追加/consumer 4〜5箇所)はUSER承認後の別管理ID(Opus条件C: 重要変更のProduction採用提案前レビューが必要)。

## 6. 限界(MEASURED、一般化しない)
- 9テーマ、各1〜2 rep。台帳は凍結で、Research/Ledger工程は再実行していない。
- E9は6テーマ1 rep。数値印なしのdry-run注記(両腕共通)。D-minのE9は未実施。AMBIGUOUSの記事反映は未確認(semiconductor F1は記事で使われなかった)。
- 人手目視はClaude側(Fable/Claude)で実施。regexは過学習の可能性があり、実際に3/8を見逃した(検出器単独での運用は不可)。
- 記事の読み物としての質は主評価していない。Writer出力の差は1 repなのでサンプリング差を含む。

## 7. 成果物(`er052_output/b3_fact_instruction_separation_trial_01/`)
PREREGISTRATION_02.md、DESIGN_02.md、PROMPT_DIFF.md、INVESTIGATION_01.md(R3是正済み)、HUMAN_CHECK_B3SEP_01.md、cost_ledger_b3sep_01.jsonl、eval/(eval_results_02.json, eval_e9_02.json, e5_missing_02.json, side_by_side_02.md, blind_outputs_02.md, blind_key_02.json, e9_articles_02.md)、runs/(C1・Aprime・E9の全出力、`_raw_usage/`にcost logger生ログ)、b3sep_*.py(Trial module/driver/eval)。
