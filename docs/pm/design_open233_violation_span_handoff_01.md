# OPEN-233 設計案: 「違反範囲をそのまま渡す」Rewrite受け渡しの再設計(委任_39)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01 / 委任_39
Status: **USER_DECISION_REQUIRED のまま(変更なし)**。本書は設計案であり、**ユーザー未承認・未実装**。
実装・Trial・API課金(費用¥0)・Production正式path変更・git commitはいずれも行っていない。
**実装前にOpus独立レビューへ回す対象**(ユーザー明示指示、PM_GOVERNANCE 11-3 条件A・B該当)。
読み手: プロジェクト責任者、およびレビュー役のOpus。Opusが「ファイル:行」を辿って検証できるよう、根拠の行番号を付けた。

## 結論の要約(10行以内)

1. 現行は「Checkerの違反箇所」を一度記事から探し直している。探し直す必要がある部分は「実在確認・置換位置・文脈取得」だけで、
   「どの文を直すか」の再推測(Stage 2のhint引用優先、類似度による1文選び、複数断片の包含スパン、JA側の位置比近似)は、設計上の必然ではなく経緯である(§1)。
2. 推奨は**案1「原文逐語+複数範囲(配列)をそのまま渡す」**。文ID・文字オフセットは現時点では不要(§6)。
3. 既存記録の再集計(¥0、既存JSONの読み取りのみ)では、Checkerの`claim_in_article`の82.8%は、**Prompt変更なしに**
   「引用符を外す/引用断片に分ける」だけで記事の逐語部分文字列として機械的に復元できた。大文字小文字・空白の差まで許すと91.5%(付録A)。
4. 今回の2例(rep21 sample1=連続2文、rep20 sample2=離れた2文)の`claim_in_article`は、いずれも上記の機械的復元で逐語範囲になる。
   つまり主因は「Checkerが返したものを再推測で縮小・拡張したこと」であり、Prompt変更は逐語率を上げる補強(段階2)に位置づける(§5)。
5. **逐語は100%保証できない**。逐語でなかった範囲は「機械的正規化(大文字小文字・空白・引用符のみ)→それでも不一致なら人間確認へ(fail-closed)」を推奨し、
   Checkerへの1回の返し直し(追加LLM call、概算¥0.5前後)は、Trialで不一致率が問題になった場合の次段とする(§2-4)。
6. 受け渡しを直しても**解決しない要因**がある: Recheckが毎周新しい別事実(rep21 sample1のMUSE-HC-010)を指摘する非決定性、Rewrite役が実際に適切に直すか、
   JA/ENの文対応が1対1でないこと(§5-3、§8)。「1周で2文とも処理」は、設計が保証するのは「2文とも対象としてRewriteへ渡り書き戻し対象になる」ところまで。
7. 最大の未確認事項: **逐語指示を入れたCheckerの実際の逐語率・検出精度への影響は未測定**(§8、付録A末尾)。

---

## 0. 用語(初出の簡単な説明)

- **検査役(Checker、Stage 1)**: 記事が事実台帳(Ledger)から逸脱していないかを調べるLLM。Recheck(再検査)も同じ検査役の再実行。
- **判定役(Stage 2)**: 検査役の指摘が本当に重大(BLOCKING)かを別LLMが再判定し、重大なら「直し方メモ(rewrite hint)」も作る。
- **書き換え役(Rewrite、Stage 3)**: 指摘された箇所を直すLLM。「最小変更ラダー」=単語→1文→段落の順に、小さい直しから試す仕組み(設計書§0-3、§5-7)。
- **Stage 4**: 自動で直しきれず人間確認(Human Review)へ回す状態。**fail-closed**: 迷ったら安全側(人間確認)へ倒す方針。
- **逐語(verbatim)**: 記事本文から一字一句そのまま写したこと。**span(範囲)**: 記事中の連続した文字列1つ(1文でも複数文でもよい)。
- DEV/Trial path: `er052_open233_self_recovery_flow_runner_01.py`等、検証用の隔離経路。Production正式path: `er003_v1_n3_01_articles_generate.py`等の量産経路。

---

## 1. 現行フローと基本線4点の差分

### 1-1. 処理順の表

凡例: **(R)** 違反対象を再推測している処理 / **(P)** 特定済みの範囲を記事へ戻す・記録する・文脈を取るための処理 / **(?)** どちらとも言えない。
行番号は`er052_open233_self_recovery_flow_runner_01.py`(以下「runner」)、`er003_v1_en_direct_vfl_01_generate.py`(以下「vfl01」)、
`er052_open233_self_recovery_stage2_production_01.py`(以下「stage2」)。いずれもコードで確認した。

| # | 工程 | 現行の動き(根拠) | 基本線4点との差 | 分類 |
|---|---|---|---|---|
| 1 | Checkerが返すもの | `claim_in_article`は型が文字列というだけ(vfl01:464)。Promptに逐語指示なし(vfl01:502-541)。位置・範囲・配列のfieldなし。runnerが`same_fact_id_locations`だけは逐語指示付きで追加(runner:1119-1126、schemaは`build_recheck_schema` runner:1468-1480) | 基本線1(逐語)・2(複数文は複数文のまま)・3(そのまま渡す)が満たされない出発点。実測では多くが逐語抜粋だが保証はない(付録A) | - |
| 2 | 同一fact別箇所の展開 | `expand_same_fact_id_locations`(runner:1138〜)が各locationを「記事中の逐語substringとして実在する場合のみ」独立deviationへ展開 | 実在確認のみ。再推測なし | (P) |
| 3 | Stage 2入力 | `claim_text = claim_in_article`(runner:4081)。stage2は`claim_text`の先頭40字(と引用符を外した版)で段落を探して±1段落の文脈を作る(stage2:184-213、見つからなければ記事全文) | 文脈取得だが、探し方が先頭40字の文字列照合 | (P)(軽微) |
| 4 | 区分判定(title/hook/in_one_line/body) | `detect_claim_section_type`(runner:1844-1872)が`locate_best_sentence`(類似度)で文を選んでから区分を決める | 区分を決めるためにも1文へ再推測している | (R) |
| 5 | Stage 2出力 | 判定役がBLOCKINGなら「記事本文からの逐語引用+修正指示+fact_id」をrewrite_hintに入れる(stage2:48-56)。QUALITY/ACCEPTABLEなら空文字(同56)。rep21 sample1 cycle1は空だった | 別のLLMによる引用。Checkerの指摘範囲と別の箇所を指しうる | (?)(後述) |
| 6 | 対象文の決定 `locate_target`(runner:2449-2473) | 第1キー=hintの引用断片(2458-2460)→第2キー=`locate_multi_quote_span`(2461-2463)→第3キー=`locate_best_sentence`(2464)→第4キー=er010の単語重なり(2467-2472) | 基本線3・「勝手に縮小・再解釈しない」に反する中心部分 | **(R)** |
| 6a | 第1キー: hint引用 | hintの最長(`extract_quoted_fragment`、2290-2311)の引用が記事にあれば採用 | Checkerの範囲ではなくStage 2の引用を第一手にしている。hintが空だと不発(rep21 s1 cycle1)。Stage 2は文脈を見て1文へ絞ることもJA引用を返すこともある(rep20 s2 cycle2はJA引用) | **(R)** |
| 6b | 第2キー: `locate_multi_quote_span` | 引用断片が2つ以上ある時、「最初の断片の開始〜最後の断片の終了」の最小包含スパン(2381-2405) | 離れた2文なら間の文も含めて1スパンにする(**拡大**)。rep20 s2の2文claimなら、間の「They enjoyed AI’s convenience, but a human was on the other end.」(cycle1でQUALITY判定済み=触らない扱いの文)まで対象に入る(実データで確認、付録B) | **(R)** |
| 6c | 第3キー: `locate_best_sentence` | 引用符を外さずに完全一致を見る(2249-2250)。外れたらSequenceMatcherの最高得点1文、次点との差0.08未満なら不採用(2251-2268) | 複数文claimを1文へ**縮小**する。rep21 s1で2文claimの類似度は0.689/0.623(差0.066)で僅差不採用(委任_38再計算値)→次のfallbackへ | **(R)** |
| 6d | 第4キー | er010の英語単語重なり(2467-2472) | 純粋な再推測 | **(R)** |
| 7 | 最小変更ラダーの対象範囲 | E1(単語・接続詞)/E2(1文)の対象=`target_sentence`(2781-2795)。段落水準は`locate_paragraph_block(target_sentence)`(2798、2476-2494) | 範囲は「6で選んだ1文」に固定される。**段落取得自体は文脈取得(P)**だが、1文への絞り込みは(R)の結果 | (P)+(R)の帰結 |
| 8 | Rewriteへ渡すもの | `[Sentence flagged]`=6の結果、`[Checker's issue]`、`[Rewrite hint]`(空なら`materiality=…, basis=…`の合成文、2747)、Ledger(2557-2599)。**`claim_in_article`自体は渡さない** | 「違反範囲をそのまま渡す」になっていない(Checker文字列→探し直し→別の文) | (R)の帰結 |
| 9 | 記事への戻し | `full_text.replace(target, revised, 1)`(2832)、delete型は`.replace(target,"",1)`(2762)、JA/EN対は3061-3062 | 完全一致の最初の1箇所を置換 | **(P)** |
| 10 | 書き換え後guard | `claim_text.strip() not in candidate`(2833、2860、paired 3066)。delete後は`locate_best_sentence(claim_text, updated_text)`で再出現を類似度確認(2769) | 「問題の文言が消えたか」の判定。ただし`claim_text`が“”付き・複数文の場合、**元から常に成立しうる**(rep21 s1 cycle1: 第1文だけ変えたのに`guard_ok: true`)。2769は類似度による再推測 | (?)(§1-3) |
| 11 | JA側の対応付け(origin=`ja_source`のみ。`run_stage3_for_claim` 3199-3203) | `paired_rewrite`(2920〜): ①multi_quote時は位置比(2958-2959)②hintの引用がJA本文にあれば採用(2960-2962)③`locate_best_sentence(claim_text, ja_full)`(2964)④Ledger claim文でlexical探索(2966-2971)⑤EN文の位置比をJA文数へ写す近似`locate_ja_counterpart_by_position`(2497-2536) | Checkerが返さない情報(JA側の対応箇所)を、5段の推測で埋めている | **(R)**(§4-3で正直に扱う) |
| 12 | Rewrite前後の記録 | `before_fragment`/`after_fragment`(2854、2916、3192) | 置換した文字列の記録 | **(P)** |
| 13 | 再検査 | `prior_issues`に`claim_in_article=c["claim_text"]`を入れて全文Recheck(runner:4499-4509)。paired時はJA本文も別Recheck(4513-4516)。次cycleのdeviationsはRecheck結果から再構築(4606、JA側MAJORも合流 4619-4631)。局所QA fastpathは`after_fragment`を使い`find_sentence_context`で文脈を取る(3488、3677〜) | 再検査は「新しい検査役呼び出し」であり対象の再推測ではない | **(P)** |
| 14 | cycle上限 | `MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`(runner:275-279)。上限超過時は「blocking件数が減った」または「同一fact_idの新しい箇所」の場合のみ追加1周(4194-4226)。それ以外は`cycle_limit_exhausted` | 受け渡しの取りこぼしが1周を消費する | - |

### 1-2. 「なぜCheckerの出力を一度記事から探し直しているのか」の再評価

**本当に必要なもの(残す)**:
1. **実在確認**。Checkerの文字列が本当に記事の一部かの照合。LLM出力である以上、逐語を保証できないため(§2-3)。これは「探索」ではなく「検査」であり、完全一致(必要なら機械的正規化)で済む。
2. **置換位置の確定**。書き戻しが文字列置換なので、置換する瞬間に「この文字列が記事のどこに1回だけある」ことが必要(`.replace(target, revised, 1)`、2832)。**特定済みの範囲を置換するための位置確認**であり、違反対象の再推測ではない。
3. **文脈取得**(段落ブロック、前後文、区分[title/hook/in_one_line/body]、Stage 2へ渡す±1段落)。範囲が分かれば機械的に取れる。

**現行実装の都合・経緯に過ぎないもの(なくす候補)**:
- 6a(Stage 2のhint引用を第一手に使う): 委任_10で「Checkerが引用を返さない」ため、判定役の引用で代用した経緯(設計書§5-4 1908付近)。Checker自身が範囲を返せるなら不要。
- 6b・6c・6d(包含スパン/類似度の1文選び/単語重なり): いずれも「Checkerの文字列が記事と一致しない場合」の保険として積み上がったもの(設計書§5-4、§6-17)。委任_36の包含スパンは症状への個別パッチ。
- 11(JA側の5段の推測): §4-3で別途扱う(完全にはなくせない可能性がある)。
- 4(区分判定の類似度1文選び): 範囲が分かれば「範囲が各区分ブロックに含まれるか」で機械的に判定できる。

**Stage 2のhint引用を対象決定の第一手に使っている点**: Checkerは「この2文が問題」と言い、判定役LLMは文脈を見て「核心の1文」を引用しうる。両者が別の箇所を指しうること、およびhintが空になる非決定性
(rep21 s1 cycle1は空、rep20 s2 cycle1は2文全体を引用して1周で解消、同cycle2はJA引用)が、結果を揺らしている。**実データ**: rep20 s2 cycle1ではhintが2文claim全体を引用しており、
`rewrite_hint_quote`で2文が1つの対象となり、E1水準で「during calls.→during a call.」「These calls→This call」の2箇所が1回のRewriteで直った(rep20 s2 cycles[0]、付録B)。
つまり**「範囲をそのまま渡せば、Rewrite役は2文を扱える」**ことは、少なくとも1件は実データで確認済み(n=1、LLM非決定性あり)。

**最小変更ラダー(単語→1文→段落)が対象範囲を1文へ絞る点**: ラダーが本来縮めるべきなのは「**編集の自由度**(単語1つの置換か、文の書き直しか)」であり、
「**Checkerが指摘した範囲**」ではない。現行は水準①③の対象が6で選んだ1文なので、範囲を縮める副作用がある。新設計では、水準①③④とも「範囲=Checkerのspan全体(④は含む段落)」を渡し、
水準の違いは「どこまで書き換えてよいか」の指示のみにする(§4-4)。設計書§0-3(不要な書き換えを増やさない)とは、範囲全体を見せつつ「変更は最小」「変更不要な文は一字一句そのまま返す」と指示することで両立させる。

### 1-3. 書き換え後guard(`claim_text not in candidate`)の問題

- `claim_text`は検査役が書いた文字列で、“ ”付きのことが多い(23件中19件が引用符で囲まれた1個の断片、付録A rep19-21)。“ ”付き文字列は記事本文には元から存在しない。
  したがって`claim_text.strip() not in candidate`は、書き換え前から成立している(委任_38実測: 引用符付き文字列が記事に含まれるか=False)。
- 引用符を外しても、2文claimは第1文だけ変えれば連結文字列が崩れるため成立する。実際rep21 s1 cycle1は第1文のみ変更で`guard_ok: true`(rep21 s1 cycles[0].rewrite_records)。
- 結論: 現行のguardは、複数文・引用符付きでは**取りこぼしを検出できない安全装置**になっている。ただし、これは「安全装置を無効化せよ」という提案ではない。
  新設計では、guardを「**各spanが書き換えで実際に変化したか**」(spanごとの前後比較、機械判定)に置き換え、解消そのものの判定は従来どおり**全文Recheckが担う**(§4-5)。この置換は新しい挙動なので、Opusに特に見てほしい(§11)。

---

## 2. Checker出力の逐語性

### 2-1. 前提: Checker Promptの差し替えはTrial専用で可能か(確認済み)

- vfl01の`DEVIATION_PROMPT_TEMPLATE`(vfl01:502)・`DEVIATION_JSON_SCHEMA`(vfl01:454)は**Production正式path**でも使われる:
  `er003_v1_n3_01_articles_generate.py`が`vfl01.run_deviation_check`を呼ぶ(同ファイル:1142、1161、1264)。
- 一方Self-Recovery Flow(DEV/Trial)は、vfl01の定数自体は変更せず、**runner側で文字列を連結して拡張する既存パターン**を使っている:
  `run_recheck`(runner:1499-1508)は`trial.build_trial_prompt_template("V4A")`(er051:232-243、vfl01のtemplate+Trial差分ブロック)に
  `RELATED_FACT_ID_INSTRUCTION`・`ORIGIN_INSTRUCTION_TEMPLATE`・`build_prior_issues_instruction`・`SAME_FACT_ID_ENUMERATION_INSTRUCTION`を追記し、
  schemaもrunner側の`build_recheck_schema`(1468)でローカル拡張している。
- `er003_v1_n3_01_articles_generate.py`等のProduction側にer051/er052のimportはない(Grep確認)。
- よって、**新しい逐語・範囲指示とschema fieldの追加は、既存の`SAME_FACT_ID_ENUMERATION_INSTRUCTION`/`build_deviation_schema_with_enumeration`(1119-1135)と同じ手口でTrial専用に実現でき、
  vfl01・Production正式pathに触れない**。Production採用は別途`APPROVED_FOR_PRODUCTION`の人間承認が必要(本書の範囲外)。

### 2-2. Promptへ加える指示の文案(実装はしない。文案のみ)

Checker Promptは日本語のため、日本語で書く。runnerの追記パターンに合わせ、既存Promptの末尾へ追記する想定。

```
【追加指示: 違反箇所の逐語引用(Trial専用)】
各deviationについて、"violation_spans"(配列)に、その逸脱に該当する箇所を【検証対象の記事】本文から一字一句そのまま引用してください。
- 各要素の"quote"は、記事本文をそのままコピーした文字列にしてください。要約・言い換え・語順の変更・省略(…や...)・翻訳はしないでください。
- 大文字・小文字、句読点、アポストロフィ、空白、改行を変更しないでください。文頭を大文字に直す、文末のピリオドを補う・削る、といった整形もしないでください。
- 引用符(“ ” " 「 」)で囲まないでください。記事本文に実際にある文字だけを入れてください。
- 逸脱が連続する複数の文にまたがる場合は、それらの文を、記事本文のとおり(文の間の空白も含めて)連続した1つの"quote"にしてください。
- 逸脱が離れた複数の箇所にある場合は、1つの文字列につなげず、箇所ごとに別々の要素にしてください。間にある、逸脱ではない文は含めないでください。
- 逸脱が文の一部だけの場合も、その語句を含む文全体(文頭から文末の句点まで)を引用してください。どの語句が問題かはissueで説明してください。
- 各"quote"は、記事本文の中で1回だけ現れる範囲にしてください。同じ文言が複数箇所にありそうなら、前後の文を含めて一意になるようにしてください。
- 記事の原文記事(日本語)が与えられている場合に限り、"ja_counterpart_quote"に、その箇所に対応する原文記事側の文を同じ規則で逐語引用してください
  (対応が見つからない・origin が translation の場合は空文字列)。
- 該当箇所を記事本文中に特定できない場合は、"violation_spans"を空配列にしてください(推測で引用を作らないでください)。
```

出力形式案(strict JSON schemaの1要素、既存fieldは変更しない):
```json
"violation_spans": [ {"quote": "<記事の逐語>", "ja_counterpart_quote": "<原文記事の逐語、無ければ空>"} ]
```
`claim_in_article`は**変更しない**(同一性判定・prior_issues・Stage 2表示用として存続。検出精度への影響を最小化するため)。
**対象決定は`violation_spans`のみを使う**(`claim_in_article`は対象決定に使わない)。2つのfieldが食い違いうる点は§8のリスクに記載。

### 2-3. ユーザーの5点への対応と、逐語を保証できない限界

| ユーザー指定 | 文案での対応 | 保証の強さ |
|---|---|---|
| 勝手に要約しない | 「要約・言い換え・省略・翻訳はしない」 | Promptのみ。機械検出は完全一致で可能 |
| 大文字小文字を変えない | 「文頭の大文字化・末尾ピリオドの整形もしない」 | 同上。実データでは「Also, some calls…」を“Some calls…”と書いた例が多数(付録A d1: 10種類中8種類が大小文字のみの差) |
| 句読点を変えない | 同上 | 同上 |
| 複数文は複数文のまま | 連続する文は1つのquoteにする | 同上 |
| 離れた2文は別々の対象 | 別要素に分け、間の文を含めない | 同上。現行は“A” and “B”の結合文字列(rep20 s2 cycle2) |

**限界(隠さず明示)**:
1. 逐語は**Promptだけでは100%保証できない**。LLMの出力は確率的で、指示を入れても写し損ねる。**前例**: `same_fact_id_locations`には「exact verbatim substring」と明記していたが
   (runner:1119-1126)、実データでは`"Paragraph 7"`(rep21 s1 cycle2のRecheck出力)や`"Paragraph beginning “People asking Muse to call”"`(rep20 s2 cycle2)のように、位置の説明文を返した例がある
   (委任_38で確認)。このため、受け取り側(runner)で**必ず完全一致照合**し、逸脱したものを防ぐ設計とした。
2. **逐語指示を入れたCheckerの逐語率は未測定**(付録Aは、逐語指示がない現行Prompt下のデータ)。改善するかは、限定Trialまで分からない。
3. 逐語であっても**間違った箇所を逐語で引用する**(判断の誤り)ことは、形式検査では検出できない。これは案1〜3のどれでも同じ(§6)。
4. 構造化出力(strict JSON schema)は形式を守らせるが、文字列の中身の忠実さまでは保証しない(一般的な傾向であり、本プロジェクトでは未検証)。

### 2-4. 逐語でなかった場合の扱い: 「正規化」と「再推測」の境界、選択肢の比較

**境界の定義(本設計の核心)**:
- **機械的正規化(許可)**: 次の**文字単位の同値変換のみ**を行い、結果が記事中で**ちょうど1箇所**に一致する場合に限り、**その箇所の記事本文の文字列**を範囲として採用する(Checkerの文字列ではなく記事側を採る)。
  (N1)両端の引用符・括弧の除去(“ ” " ‘ ’ 「 」 『 』のうち、文字列全体を囲む1組)。
  (N2)空白・改行の連続を1個の空白とみなす照合。
  (N3)曲線引用符/アポストロフィと直線のそれの同一視(’と'、“”と")。
  (N4)大文字小文字の同一視。
  (N5)引用断片への分解: 文字列が“…”(または「…」『…』)の断片を2つ以上含む場合、各断片を別々のspan候補にする(“A” and “B”のandは捨てる)。
- **再推測(不許可、新設計で原則なくす)**: 類似度(SequenceMatcher等)・単語重なり・位置比・Ledger語彙・別のLLM(判定役)の引用など、**文字列の同一性ではなく「似ている」ことを根拠に範囲を選ぶ処理**。
  判定基準: 「変換後の文字列が記事中の部分文字列として**完全一致**し、一致が1箇所に定まるか」。定まらなければ再推測に進まず、下表の扱いに回す。
- 区別のポイント: N1〜N5は「Checkerが書いた文字そのものを、記法の違いだけ吸収して照合」する。Checkerが**書いていない語を足す・書いた語を落とす**変換は含まない
  (例: “Some calls needed user information to continue.”が記事の「Also, some calls needed user information to continue.」の一部に一致するのはN4により、書いた語は落としていない=許可)。

**不一致(N1〜N5でも1箇所に定まらない)の扱いの選択肢**:

| 選択肢 | 内容 | 追加LLM call | 非決定性 | Human Reviewへの影響 | 評価 |
|---|---|---|---|---|---|
| A. 当該deviationだけfail-closed | 新reason(例: `violation_span_unverified`)でStage 4へ。他の指摘は通常処理 | 0 | なし(決定論) | **増える可能性**(現行の類似度fallbackが実際に正しく直せていた分は失う。その割合は未測定) | 最も単純・安全。「迷ったら人間確認」と整合 |
| B. Checkerへ1回だけ返し直し | 「このquoteは記事に一字一句存在しません。記事からコピーし直してください」と該当deviationだけ再依頼 | +1(Recheck相当の呼び出しで過去実測平均¥0.526、n=10、meta_run03_standard rep19-21。返し直しは出力が小さいので上限の目安) | あり(再出力も揺れる) | 減らせる可能性。再度不一致ならAへ | 効果は未測定。Trialで不一致率が問題になった場合の次段 |
| C. 現行の類似度fallbackを「印付きで」残す | 不一致時のみ現行`locate_best_sentence`等を使い、ログに`guessed`と記録 | 0 | なし | 現状維持に近い | **再推測を残す**ので基本線に反する。誤って別の文を直すリスクが残る。非推奨(Opusの意見次第) |
| D. 段落/全文Rewriteへ倒す | 範囲不明のまま広く直す | +1以上 | あり | 減るが品質リスク | 設計書§0-3(Rewriteは品質リスク)に反する。非推奨 |

**推奨**: **Aを初期仕様、Bは限定Trialで不一致率を測ってから判断**。理由: 最も単純で決定論的であり、fail-closedを緩めない。
ただしAは現行より人間確認が増えうるため、限定Trialで「不一致の実数」と「現行fallbackが正しく直せていたか」を必ず測る(§10)。

---

## 3. 複数文・複数箇所の表現

出力は常に`violation_spans`という**範囲の配列**。1要素=記事中の連続した文字列1つ。文ID・文字オフセットは使わない(§6)。

| 形 | 表し方 | 例(実データ) | 後段の扱い |
|---|---|---|---|
| 連続する2文 | 1要素に2文を、記事のとおり連続した1つのquoteで入れる | rep21 s1: 「It said human staff … during calls. These calls were about … cable fees.」(135字、記事に1回出現) | 1つのspanとして1回のRewriteへ。2文とも対象 |
| 離れた2文 | 2要素。間の文は含めない | rep20 s2: 「They could not tell if it was AI or a person.」と「They did not realize it.」(間に「They enjoyed AI’s convenience, but a human was on the other end.」) | spanごとに記事順で1つずつRewrite(§4-2)。間の文は触らない |
| 1文の一部 | その語句を含む**文全体**を1要素に(Prompt文案)。どの語句かはissue | 例: 「…during calls.」の“calls”だけが問題でも文全体 | 範囲は文全体、変更は最小(ラダー水準①) |
| 複数箇所(段落をまたぐ、見出し+本文等) | 箇所ごとに1要素 | 例: 設計書§0・§13の「title/hook/in_one_line/本文に散る」ケース | spanごとにRewrite。段落をまたぐspanは結合しない |

**同一文字列が記事中に複数回出現する場合**: 照合は「ちょうど1箇所」を要求する(0箇所・2箇所以上は不一致扱い、§2-4)。
Promptで「一意になるよう前後の文を含める」よう指示する。それでも2箇所以上なら不一致扱い(Aなら人間確認)。
(より軽い解決として「何番目の出現か」を整数で返させる案があるが、現時点では追加しない。§6の「次段」条件に記載。)

**範囲同士が重なる場合**: (a)重なる、または間が空白だけで隣接するspanは、記事上の位置の和集合1つに結合する(Checker自身が指摘した文だけの和なので、再解釈ではない)。
(b)段落区切り(`\n\n`)をまたぐ結合はしない(見出し/hook/本文の区分維持のため。現行`locate_multi_quote_span`の`span_crosses_paragraph`と同方針、runner:2403-2404)。
(c)一方が他方を完全に含む場合は大きい方に吸収する。

---

## 4. 後段処理の限定

### 4-1. 残す処理/なくす処理

**なくす処理(違反対象の再推測)**:
- `locate_target`の4段(runner:2449-2473)のうち、hint引用・包含スパン・類似度・単語重なり。
- `locate_multi_quote_span`(2381-2405)と、それを前提にしたpaired_rewriteの位置比優先分岐(2958-2959)。
- 区分判定の類似度1文選び(1855)。
- JA側の推測の連鎖のうち、Checkerが返さない場合の位置比近似(§4-3で扱いを分ける)。
- 書き換え後の類似度による再出現確認(2769)→全文Recheckに一本化(§4-5)。

**残す処理(特定済みの範囲を入力として動く)**:

| 残す処理 | 入力 | 動き |
|---|---|---|
| 実在確認 | Checkerのquote | 完全一致(+N1〜N5)で、記事中の1箇所に定まるか確認。定まれば範囲=記事側の文字列 |
| 記事への戻し | 範囲+Rewrite結果 | 書き戻しの直前に、現在の記事で範囲が1箇所にあることを再確認し、`full_text.replace(範囲, revised, 1)`(現行2832と同じ。範囲の位置を再計算するだけで、新しい探索ではない) |
| Hook/Title/本文区分の維持 | 範囲 | 範囲が各区分ブロック(`_paragraph_title`/`_extract_in_one_line_text`/`_hook_paragraph_block`、runner:1852-1854で既存)に含まれるかの包含判定。複数spanが別区分なら最も保護の強い区分(title>in_one_line>hook>body)をclaim区分とする(保守的、設計判断なのでOpus確認) |
| 前後文脈の取得 | 範囲 | 範囲を含む段落(±1)を取る。`locate_paragraph_block`(2476-2494)は範囲の包含判定で使える。Stage 2のlocal_contextも範囲から機械的に作れる |
| Rewrite前後の記録 | 範囲+revised | spanごとに`before_fragment=範囲`、`after_fragment=revised`(runner:4303の`before_after_pairs`を踏襲)。連続2文のafterは`find_sentence_context`の複数文対応(委任_21)がそのまま使える |
| 再検査 | 記事全体 | 現行どおり全文Recheck(prior_issuesあり)。解消の判定は検査役に任せる |
| 区分別の降格ルール、品質劣化検出v2、`section_role_violation` | テキスト全体 | 変更なし(範囲に依存しない) |

### 4-2. Rewriteへ渡すもの・戻し方・複数範囲の扱い

- **1 span = 1 Rewrite呼び出し**を基本とする。連続2文は1 span(1回の呼び出しで2文とも渡す)。離れた2文は2 span。
- 離れたspanは**記事順に1つずつ**、その時点の記事に対して処理する(現行も複数claimを`_run_stage3_cycle`でen_outを更新しながら順に処理、runner:4281-4303)。
  先のspanの書き換えが後のspanの文字列を変えない(範囲が重ならないため)ので、後のspanは書き戻し直前に1箇所一致を再確認すれば足りる。**オフセットを持たないので、先の書き換えで位置がずれる問題がない**(§6の案3との差)。
- Rewrite Promptには(1)`[Flagged range]`=範囲そのもの(1文以上)、(2)`[Other flagged ranges for the same issue]`(同じdeviationの他span。読み取り専用、既に書き換え済みならその結果も示す。整合のため)、
  (3)issue、(4)Stage 2のhint(**指示文としてのみ使用**、対象決定には使わない)、(5)Ledger、を渡す。
- Prompt文言は、現行E1/E2(runner:2557-2599)の「Return ONLY the revised sentence」を「範囲(1文以上)を返す。**直す必要のない文は一字一句そのまま返す**」へ読み替える(Trial専用のrunner内定数。Productionに影響しない)。
  これにより「範囲全体を渡しつつ、変更は最小」が両立する。

### 4-3. JA側の対応範囲(正直に: 再推測を完全にはなくせない可能性)

JA側の対応範囲は、**Checkerが返さない情報を必要とする**。確認済みの事実:
- JA/ENペア書き換えは`origin == "ja_source"`のclaimだけ(runner:3199-3203)。`translation`起源はEN側のみ(rep21 s1はこちら=JAは無関係)。
- 検査役は、原文記事(JA)を既にPromptで渡されている(`ORIGIN_INSTRUCTION_TEMPLATE`、vfl01:667-675、runner:1502-1504)ので、JA側の対応箇所を返させる追加callは不要。
- **JA/ENは文数が1対1にならない**。実データ(rep19 meta_run03_standard cycle2、同一固定データ由来と想定=未確認)で、EN段落[5]は7文、対応するJA段落[5]は5文。EN段落[7]は5文、JA段落[7]は3文。
  文IDや位置比が、そのままでは成立しない。
- JA側Recheck(runner:4513-4516)は、ENではなくJA本文だけを検査役に渡している(`recheck_fixture["source_article_text"]=current_ja_text`、4506)。
  すなわち**JA側の指摘に対応するENの箇所**は、現行ではCheckerから得られない(逆方向も同じ問題)。

| 選択肢 | 内容 | 追加call | 残る推測 | 評価 |
|---|---|---|---|---|
| J1. Checkerが`ja_counterpart_quote`も逐語で返す(推奨) | 検査役がJA対応文を原文記事から逐語引用。同じ照合(実在・1箇所)をJA本文に適用 | 0 | 対応づけそのものは**検査役の判断**(機械では検証できない)。ただし後段が推測するのではなく、検査役が宣言した対応を使う | 対応づけの「責任者」が明確になる。誤りは機械検出不可(実在照合は通る) |
| J2. 各言語は自言語のCheckerが返したspanだけで直す | ENのspanはEN検査、JAのspanはJA検査(runner:4514)の結果で直す。クロスリンガルの推測なし | JA事前検査+1(cycle1でJAを検査する分。Recheck平均¥0.53) | なし | 最も純粋だが、cycle1でJAも検査する追加コスト、解消に周回が増える可能性 |
| J3. 現行の位置比近似を残す | 2497-2536 | 0 | 5段の推測 | 基本線に反する。文数が1対1でない実データ(上)から、近似は文脈次第で外れる |

**推奨**: J1を主、J1の`ja_counterpart_quote`が不一致/空の場合は**既存の「片側のみ特定」経路**(runner:3081-3106、`single_text_rewrite`でEN側のみ直し、
`mechanism`は`paired`のままなのでJA Recheck〔4513〕が走り、JA側の残りはJA検査役の自言語span=J2で次周に直す)に倒す。位置比近似(J3)は新設計の主経路から外す。
**これで「残る推測」はJ1の「対応づけの正しさを検査役の判断に委ねている」点のみ**。J1の誤り(別の文を対応と宣言)は、JA Recheck(全文)が検出する構造で、fail-closed(`ja_pending_deviation`、runner:4559-4560)は維持される。
J3を一定条件で残すか(Trialで片側経路のStage 4が多すぎる場合)は、ユーザー/Opusの判断事項。

### 4-4. 最小変更ラダー・設計書§0-3との両立

- ラダー水準①(単語・接続詞)/③(1文=範囲の書き直し)/④(範囲を含む段落)の**対象範囲はspan全体**で固定し、水準は「許す編集の大きさ」のみを変える。
  水準①のPrompt(runner:2569-2578の「swap a single word…」)は、範囲が複数文でもそのまま使える(変更不要な文は一字一句返す指示を追加)。
- 書き戻しは「範囲全体の置換」。範囲内で変えなかった文は、Rewrite結果の中で同じ文字列として戻る。
- 範囲を拡大する処理(包含スパン)は作らない。**触るのはCheckerが指摘した文だけ**。rep20 s2のように、間の文がcycle1で非BLOCKING判定済みなら、それを巻き込まない(§1-1の6b)。
- `escalate_to_paragraph`(runner:2814-2815)・`filter_levels_by_problem_kind`(2819-2821)は、水準の選択ロジックでありspan決定とは独立。変更しない。
- 注意: ラダーは「水準①で直らなければ③へ」進む。範囲が2文になると、①の最小編集で2文とも直るかはRewrite役次第(§5で分けて書く)。

### 4-5. 書き換え後guardの置換案

- 現行guardの限界は§1-3。新設計の案: spanごとに、`revised != span`(範囲が実際に変化)、かつ既存の`actor_rewrite_guard_ok`(2844、主体置換ガード)は維持、空文字は水準①では不可(既存どおり)。
- 「範囲内の全文が変化していること」までは要求しない(要求すると、変更不要な文まで書き換えさせ、§0-3に反する)。
- 追加の観測: spanごとに「範囲内の各文が変化したか」をログに残す(gatingにしない)。取りこぼしの疑いは次の全文Recheckで検出される。
- delete型の再出現確認(2769、類似度)は、再推測を含むため新設計ではRecheckへ一本化する案。Opusの意見を求める(§11)。

---

## 5. 実例への適用

実データは、`er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json`、同rep20 `instances_s2`、
rep19の固定Stage 1 `stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`(いずれも読み取りのみ)。
「Checkerの新しい出力例」は**設計上の想定であり、実測ではない**(新Promptは未実行)。

### 5-1. 実例(i): rep21 sample1、連続2文

**元記事(段落[7]、逐語)**:
> News reports also cited one employee’s report. It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees. However, this is only one report. It would be wrong to say all contract workers did this.

**現行のChecker出力(実データ、固定fixture deviations[1])**: `claim_in_article` =
`“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`(“ ”付き)、`related_fact_id: MUSE-HC-011`、`origin: translation`。

**段階0(Prompt変更なし)の機械的復元(既存記録で確認)**: 両端の“ ”を外した文字列(135字)は、記事に**ちょうど1回**出現する(スクリプト確認、付録B)。
引用符付きのままでは記事に含まれない(False)。→ 範囲=この2文。

**新Promptでの想定出力(設計上の想定)**:
```json
"violation_spans": [
  {"quote": "It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.",
   "ja_counterpart_quote": ""}
]
```
(origin=translationなのでJA対応は空。EN側のみ。)

**処理順(新設計)**:
1. 実在確認: 完全一致、1箇所。範囲確定(再推測なし)。区分: 範囲は本文段落→`body`。
2. Stage 2: 範囲(2文)を`[対象claim]`として渡す。hintが空でも対象決定に影響しない(現行はここで探し直しに落ちた)。
3. Rewrite(水準①): `[Flagged range]`=上の2文、issue=「複数形callsがLedgerの1件の報告と合わない」。2文とも対象。
   **想定(保証ではない)**: 「…during a call. This call was about …」。**参考実績**: rep20 s2 cycle1は同じ2文claimがhint引用経由で2文の1範囲として渡り、水準①で2箇所が直った(付録B)。
4. 書き戻し: 範囲(2文)を`.replace(範囲, revised, 1)`で置換。`before_fragment`=2文、`after_fragment`=revised。
5. guard: `revised != 範囲`を確認。
6. JA: origin=translationのためJAは書き換えない。
7. 再検査: 全文Recheck。第1文・第2文とも直っていれば「解消」。

**「1周で2文とも適切に処理できるか」**:
- **設計が保証する**: 2文とも対象としてRewriteへ渡る。2文を含む範囲全体が書き戻し対象になる。現行のように「第2文が次周に持ち越される」構造はない。
- **保証できない**: (a)Rewrite役のLLMが2文とも適切に直すか(水準①の最小編集で足りるか、足りず水準③へ進むか)。(b)Recheckが別の指摘を出すか。

**受け渡しの是正では解決しない要因(実データ)**: rep21 s1 cycle3で、別事実**MUSE-HC-010**(「Also, some calls needed user information to continue.」)が新規BLOCKINGとして指摘された。
同じclaim(先頭が大文字の“Some calls needed user information to continue.”)はiter5〜8・rep9/11/12/20/21の多くのrunで繰り返し現れている(付録A d1)。
これはRecheckが毎周別の事実を指摘する非決定性であり、受け渡しを直しても消えない。**もし新設計で第1周にHC-011を直し切れたなら、
HC-010は第2周で出る可能性が高いが(推測)、MAX_CYCLES=2に収まるかはRecheckの出方次第**で、収まらない場合は`cycle_limit_exhausted`が残る(runner:275-279、4194-4226)。

### 5-2. 実例(ii): rep20 sample2、離れた2文

**元記事(段落[5]、逐語、cycle1後)**:
> People asking Muse to call might think AI was calling. But sometimes, a human was speaking instead. If no one explained this clearly, users could not know. They could not tell if it was AI or a person. They enjoyed AI’s convenience, but a human was on the other end. They did not realize it. That was happening behind the scenes.

**現行のChecker出力(実データ、cycle2 stage2_results)**: `claim_text` = `“They could not tell if it was AI or a person” and “They did not realize it.”`、`related_fact_id: MUSE-HC-012`、`origin: ja_source`。
2つの“ ”断片は、それぞれ記事に1回ずつ出現する(確認済み)。間に「They enjoyed AI’s convenience, but a human was on the other end.」がある。

**現行の動き(再確認)**: `locate_multi_quote_span`(委任_36)導入後は、最初の断片の開始〜最後の断片の終了=135字の3文(間の文を含む)が1つの対象になる(スクリプトで再現、付録B)。
この間の文は、cycle1では別claim(MUSE-HC-012のQUALITY、Rewriteしない扱い)として判定されている(rep20 s2 cycles[0].stage2_results)。**包含スパンはQUALITYと判定済みの文まで書き換え対象に含めてしまう**(§0-3との衝突)。

**段階0(Prompt変更なし)の機械的復元**: N5(断片分解)で2つの断片を別々のspan候補にする。各断片は記事に1箇所で一致(「…or a person」は末尾の「.」を含まないが記事の部分文字列)。→ 2 span。

**新Promptでの想定出力(設計上の想定)**:
```json
"violation_spans": [
  {"quote": "They could not tell if it was AI or a person.", "ja_counterpart_quote": "<原文記事の対応文(検査役の判断)>"},
  {"quote": "They did not realize it.", "ja_counterpart_quote": "<原文記事の対応文(検査役の判断)>"}
]
```

**処理順(新設計)**:
1. 実在確認: 2 spanとも1箇所で一致。
2. Rewrite: span1→(書き戻し)→span2、の順に1つずつ。それぞれ水準①から。間の「They enjoyed AI’s convenience…」は触らない。
3. JA側(origin=ja_source→ペア書き換え): `ja_counterpart_quote`を原文記事で完全一致照合。通れば`ja_target`として使う。通らなければ片側経路(§4-3)。
   **正直な注意**: JA対応は多対多になりうる。実データ(rep19同一固定データ想定)では、EN「They could not tell…」「They did not realize it.」付近のJA段落[5]は
   「しかも、適切な説明がないままなら、利用者は相手がAIなのか人間なのかを知ることができません。」「AIの便利さを楽しんでいたら、いつの間にか電話の向こうに人間がいた。」等で、
   EN文とJA文が1対1に対応しない。**検査役が選んだJA文が本当に正しい対応かは、機械では検証できない**(実在照合は通ってしまう)。rep20 s2のJA本文は記録されていないため、実際の対応は未確認。
   現行ではStage 2のhintのJA引用(「けれど、その一部では人間が話していた。しかも、…」の2文)が、EN側の対象と食い違う箇所を指した(設計書§6-17)。
4. 再検査: 全文Recheck+JA Recheck。

**「1周で2文とも適切に処理できるか」**:
- **保証する**: 2 spanが2つとも対象として渡り、2つとも書き戻し対象になる。間の文は巻き込まない。
- **保証できない**: Rewrite役が各spanを適切に直すか。JA対応づけの正しさ(検査役の判断依存)。Recheckの新規指摘。
- **受け渡しの是正では解決しない要因**: この例では、cycle2のclaim自体が「Checkerがandで結合した合成文字列」を返す非決定性、JA/EN文構造の不一致。

---

## 6. 3案比較

評価は「◎=最もよい、○=よい、△=注意、×=不利」。根拠のない一般論は「(一般的傾向・本プロジェクト未検証)」と明記。

| 軸 | 案1: 原文逐語+複数範囲(配列) | 案2: 文ID併用 | 案3: 文字オフセットまで持つ |
|---|---|---|---|
| LLMに出させるもの | 記事から写した文字列の配列(+JA対応の文字列) | 文ID(整数)の配列。記事を文に分割して番号を振った版をCheckerへ渡す前処理が必要 | 開始・終了の文字位置(整数)。通常は照合のため逐語も併記 |
| LLMが間違えたとき | 写し損ね→**完全一致で機械検出**(0箇所/複数箇所)。判断の誤り(別の文を引用)は検出不可 | ID取り違え(隣の文など)は**静かに別の文を指す**。逐語を併記しない限り機械検出不可 | LLMは文字数を数えるのが苦手(一般的傾向・本プロジェクト未検証)。ずれは逐語を併記しない限り検出不可 |
| 単純さ | ◎ 前処理なし。既存の完全一致・`.replace`の延長 | △ 文分割器(記事・JA)・番号付き記事の提示・IDから文への逆引きが必要 | × 上に加えオフセット管理 |
| 堅牢性 | ○ 不一致は決定論的に検出。曲線引用符・空白はN1〜N5で吸収 | △ 分割境界(略語「U.S.」等)が提示側と書き戻し側でずれると事故。現行の分割器は`.!?。`で単純に切る(runner:2251、2411-2425) | × 書き換え後にオフセットが全てずれる(同cycleで複数claimを順に書き換える現行構造、runner:4281-4303) |
| 非決定性 | ○ 出力形式が逐語のみ。ただし逐語率は未測定 | △ Checkerに見せる記事の体裁(番号付き)が変わるため、検出精度に影響しうる(未測定) | △ 検出精度への影響に加え、数値出力の揺れ |
| JA/EN対応 | △ JA対応は別quoteが必要(J1)。ただし文数が1対1でないのは全案共通 | × 文IDはJA/ENで別系統。実データでEN7文↔JA5文(§4-3)。IDでの対応づけは成立しない | × 同左+言語ごとに文字位置 |
| Rewrite後の戻しやすさ | ◎ 書き戻し直前に範囲を再照合して`.replace`。位置ずれの問題なし | ○ ID→文→置換。ただし1件書き換えると以降の文番号がずれる(分割・結合・削除でID再計算) | △ 書き換えごとに全オフセットを更新する必要 |
| 既存コードへの影響 | ◎ 追加のみ(`violation_spans`+機械照合)。`locate_target`4段を置換。既存の`.replace`書き戻し、ladder、guardをほぼ流用 | △ 分割器・番号付与・逆引き・提示フォーマット変更 | × オフセット更新・位置管理の追加 |
| 再発防止 | ○ 「Checkerの範囲をそのまま使う」構造が再推測を防ぐ。誤引用(判断の誤り)は防げない | ○ 同左。ID取り違えという新しい誤りが加わる | ○ 同左。位置誤りという新しい誤りが加わる |
| コスト | ◎ 出力トークン増は引用分のみ(未算定)。追加call 0 | ○ 入力に番号付き記事、前処理は¥0 | △ 同左+再計算 |

**推奨: 案1**。理由: 最も単純で、機械的に失敗を検出でき、位置ずれが起きない。案2・3の主な利点(文字列の写し損ね・重複への強さ)は、案1の機械的正規化(N1〜N5)と「1箇所一致」で大部分が代替でき、
欠点(提示記事の体裁変更・前処理・JA/EN非対応・位置ずれ)は新しいFailure modeを増やす。**案2・3でも「Checkerが間違った文を指す」判断の誤りは防げない**(形式の問題ではない)。

**推奨案で足りない場合にのみ次へ進む条件**(閾値の数値は本書では決めない。ユーザー/Fableが事前に決める):
1. 限定Trialで、Checkerのspan不一致のうち**「同一文言が複数箇所」(2箇所以上一致)が主因**と分かった場合 → まず**案1.5「quote+何番目の出現か(整数)」**(IDも位置も使わない最小の曖昧性解消)。
2. 案1.5でも、文の分割境界を跨ぐ・文言の写し損ねが主因で不一致が多い場合のみ、案2(文IDを逐語と併記し、IDは補助的な照合用に限定)を検討。
3. 案3は、案2でも解決できない具体的な失敗例が実データで示された場合に限る。現時点でその根拠はない。

---

## 7. 影響範囲と整合(実装はしない。変更が必要になる箇所の一覧)

### 7-1. Trial専用で実現できる範囲(Production正式pathに触れない)

すべて`er052_open233_self_recovery_flow_runner_01.py`(およびrunner専用の追加モジュール)内で完結し、vfl01・er051・stage2モジュールの既存関数は変更しない想定:
- Checker追記指示+schema拡張: `SAME_FACT_ID_ENUMERATION_INSTRUCTION`(runner:1119)・`build_deviation_schema_with_enumeration`(1129)・`build_recheck_schema`(1468)・`stage1_fresh_with_enumeration`(1277)・`run_recheck`(1483)・`run_recheck_confirm`(1646)の追記/拡張。
- 範囲確定の新関数(完全一致+N1〜N5、1箇所一致、結合規則)と、`locate_target`(2449)の置換。旧`claim_in_article`からの機械的復元アダプタ(段階0)。
- `single_text_rewrite`(2731)・`paired_rewrite`(2920)の対象決定部、E1/E2/J1 Prompt雛形(2551-2636)の文言、guard(2833、2860、3066)。
- `detect_claim_section_type`(1844)、Stage 2入力の`claim_text`表示(4081)。
- Stage 2モジュールの`REWRITE_HINT_INSTRUCTION`(stage2:48-56)は、hintを対象決定に使わなくなるので変更必須ではない(hintは指示文として残る)。変更するなら引用要件の緩和のみ。

### 7-2. Production正式pathに触れる範囲

- Checker Prompt本体(vfl01:502)・schema(vfl01:454)を変えてProductionで逐語・範囲を返させる場合は、Production採用(`APPROVED_FOR_PRODUCTION`、人間承認)が必要。**本書の範囲外であり、触れない**。
- Self-Recovery Flow自体がOPEN-233の`USER_DECISION_REQUIRED`で、Productionへ配線されていない(approved-but-unwired・未承認を確認。本書でも変更しない)。

### 7-3. テスト(既存テストが固定している挙動=影響範囲。実行はしていない)

`er052_open233_self_recovery_flow_runner_01_test_01.py`(Grepで確認): `TestLocateBestSentence`(78)、`TestExtractQuotedFragment`(182)、`TestLocateTarget`(205、特に`test_uses_rewrite_hint_quote_as_first_key` 206)、
`TestExtractAllQuotedFragments`(241)、`TestLocateMultiQuoteSpan`(263)、`TestLocateTargetMultiQuoteIntegration`(317、`test_locate_target_prefers_multi_quote_span_over_single_sentence_match` 319、
`test_rewrite_hint_quote_still_takes_priority_over_multi_quote_span` 333)、`TestLocateJaCounterpartByPosition`(386)、`TestLocateParagraphBlock`(453)、`TestDetectClaimSectionType`(1241)、
`TestMinimalChangeLadderOrdering`(1349)、`TestJ1MinimalChangeLadderOrdering`(1409)、`TestEscalateToParagraphLadderSkip`(2330)、`TestLadderExhaustedWithoutFullRewriteWiring`(2501)、
paired partial-locate系(1830、1870)、`find_sentence_context`系(2915等)。
上のうち、**`locate_target`の優先順位(hint引用が第一手、包含スパン優先)を固定しているテストは、新設計で意図的に書き換わる**。ladder順序・paragraph block・partial-locate・`find_sentence_context`は新設計でも使い続ける。
`er051_open233_checker_trial_variant_01_test_01.py`は、V0/V1がvfl01のtemplateと一致することを固定している(139-140行付近)。runner側の追記方式なら影響しない。

### 7-4. retry/fallback/再検査・cycle上限・fail-closedとの整合

- **cycle上限**(`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`、追加1周条件 runner:4194-4226): 変更しない。範囲の取りこぼしで周回を消費する分が減る方向だが、Recheckの新規指摘の非決定性は残る。
- **ladder**(①→③→④、⑥はOFF `ENABLE_LADDER_LEVEL_6_FULL_REWRITE`既定OFF): 変更しない。`target_not_locatable`(2871)は「範囲が確定できない」場合の既存reasonに対応させるか、新reason`violation_span_unverified`を足す(Trial内の記録)。独自判断で⑥を有効化したり上限を超えたりしない。
- **fail-closed**: 範囲が確定できない場合は人間確認(§2-4 A)。解消判定は全文Recheck(従来どおり)。Recheckのcite-or-release(`remaining_sentence`、runner:1646〜)は、検査役の逐語引用を機械検証する既存の前例として維持。
- **JA fail-open封鎖**(`ja_pending_deviation`、`ja_fail_open_guard`、runner:4559-4560等)は維持。`ja_fail_open_guard`が使う「指摘JA文の逐語残存」は、`ja_counterpart_quote`から作れる。

### 7-5. 既存の是正のうち不要になるもの/残すもの

| 是正 | 新設計での扱い |
|---|---|
| 委任_36 `locate_multi_quote_span`+paired位置比優先(runner:2381-2405、2958-2959) | **不要になる**(段階0の断片分解N5+「範囲をそのまま使う」で置換。包含スパンは拡大するため副作用もある) |
| 委任_10 hint引用を第一手に使う(2458-2460) | **対象決定から外す**(hintは指示文としてのみ) |
| 委任_21 `find_sentence_context`の複数文needle対応(3488〜) | **残す**(連続2文のRewrite結果も扱うため) |
| 委任_20 W1(iii) `ja_fail_open_guard`、W2 `same_fact_id_locations`の展開・照合 | **残す**(範囲の再推測ではない。`same_fact_id_locations`をspan配列へ統合して廃止できる可能性はあるが、本設計の範囲外=別途検討) |
| 委任_35 原因(d)の是正(floorのfact_id単位broadcast廃止+enumerationのcycle1限定+iol_degenerate guard) | **残す**(受け渡しとは別の原因) |
| 委任_36 §6-17 JA/EN食い違いの是正 | JA側は§4-3の方式へ置換 |

---

## 8. 新しく生まれうるFailure modeと残るリスク

1. **逐語でない出力でHuman Reviewが増える**: 現行のあいまい一致fallbackで「たまたま正しく直せていた」分を、fail-closed(§2-4 A)に変えると失う。割合は未測定(付録Aは、claim文字列の逐語性の集計であって、現行fallbackの正否ではない)。
2. **Checkerの出力形式変更が検出精度(見逃し・誤検出)に影響する可能性**: `violation_spans`の追加は新しい出力負荷になり、検出自体が揺れうる。既知の非決定性(Stage 1の揺れ、委任_33/34で固定入力に切り離した経緯)と区別して測る必要がある。**未測定**。
3. **2つのfieldの食い違い**: `claim_in_article`と`violation_spans`が別の箇所を指す可能性。対象決定は`violation_spans`のみで行うが、Stage 2の判定入力やprior_issuesは`claim_in_article`を使うため、判定対象と書き換え対象がずれうる。対策案: Stage 2・prior_issuesの表示にも`violation_spans`のquoteを使う。
4. **範囲全体を渡すことで書き換え量が増える可能性**: 2文を渡すと、Rewrite役が不要な文まで書き換えるリスク。対策はPrompt(変更不要な文は一字一句返す)とspanごとの変化ログのみで、LLMの遵守は保証できない(§0-3の「Rewriteは品質リスク」が残る)。
5. **JA対応の誤り**: 検査役が宣言したJA対応が誤っていても実在照合は通る。検出はJA Recheck頼み。
6. **固定fixtureの不整合**: 既存のfrozen fixture(rep19)には`violation_spans`がなく、段階0のアダプタ(claim_in_articleから機械的に復元)で動かす必要がある。段階1(新Prompt)の実測は固定fixtureを使えず、Stage 1の揺れが再び混ざる。
7. **文分割の限界**: 範囲を記事に戻すだけなら文分割器は不要だが、`locate_paragraph_block`・JA位置系は`\n\n`や句点で分ける簡易実装で、略語(「U.S.」)等で誤分割しうる(現行と同じ限界)。
8. **逐語の「正解」が曖昧な文字**: 改行・全角/半角空白・NBSP・合字などの差。N2・N3は空白と引用符のみを同一視する。それ以外(ハイフン/ダッシュ等)は不一致扱いで、Trialで実測してから正規化に加えるか決める。
9. **短い断片の曖昧一致**: N4(大文字小文字の同一視)で、元の文より短い断片(例: “Some calls…”)が記事の文頭以外にも一致しうる。「1箇所一致」条件で安全側に倒れるが、短い断片は一致が多箇所になりやすく、不一致扱いが増えうる。

**Human Reviewを本当に減らせるかの見込み**:
- **根拠がある範囲**: (1)meta_run03_standardで固定Stage 1入力でもStage 4になった2 run(rep20 s2、rep21 s1)は、いずれも複数文claimの取りこぼしが主因(委任_38 §4-2、本書付録B)。受け渡しの是正はこの2件の主因に直接対応する。
  (2)現行のCheckerのclaim文字列の82.8%は、Prompt変更なしに逐語範囲へ機械的に復元できる(付録A)。
- **根拠がない/不明な範囲**: (1)他記事(hormuz系、B4、neg系)のStage 4原因は本書では調べていない(未確認)。(2)rep21 s1は、HC-010の新規指摘が残るため、受け渡しを直しても人間確認が残る可能性がある。
  (3)逐語指示後のCheckerの実際の逐語率・検出精度への影響。(4)Rewrite役が2文範囲を適切に直す確率(n=1の成功例のみ)。
  **削減率の数値目標は、根拠がないため書かない**。

---

## 9. Existing Spec / Prior Trial Check(PM_GOVERNANCE 21節)

確認方法: `docs/pm/design_open233_self_recovery_flow_01.md`、`docs/pm/design_open233_checker_redesign_trial_01.md`、`docs/pm/opus_l2_review_open233_self_recovery_01〜04.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`を、`verbatim|逐語|exact substring|offset|オフセット|文ID|sentence_id|文番号|位置情報|claim_in_article.*(逐語|verbatim)`等でGrepし、該当箇所を読んだ
(REPORTは設計書§6-14〜6-17が同内容のため該当語のみ確認。全文は読んでいない)。

| 項目 | 分類 | 根拠 |
|---|---|---|
| 判定役(Stage 2)に記事からの逐語引用をrewrite_hintへ入れさせる | **A(既存仕様あり)** | `REWRITE_HINT_INSTRUCTION`(stage2:48-56)、設計書§5-4(1908付近)。ただしCheckerではなくStage 2、かつ対象決定の第一手に使う設計 |
| 検査役に「同一factの他箇所を逐語substringで列挙」させ、実在確認する | **A** | `same_fact_id_locations`(runner:1119-1126)、設計書§6-14(2868-2874付近)。逐語指示にもかかわらず`"Paragraph 7"`が返った前例あり |
| Recheckの`remaining_sentence`を逐語引用させ機械検証(cite-or-release) | **A** | 設計書§6-3(2460-2480付近)、runner:1556〜 |
| 複数引用断片claimの包含スパン特定 | **A(実装済み、本設計で置換提案)** | 委任_36、設計書§6-17(3306-3340付近) |
| 検査役の`claim_in_article`自体に逐語指示・複数範囲配列(`violation_spans`)を持たせる | **C(本当に新規)** | 上記Grepで該当提案・Trial・却下の記録なし。vfl01のPrompt/schemaにも指示なし(vfl01:464、502-541) |
| 文ID・文字オフセットでの範囲指定 | **C** | 同上。設計書・Opus L2レビュー01〜04・Checker redesign設計書に、検討・試行・却下の記録なし(Grep該当なし) |
| 「同一fact_idを参照する全箇所を1回のRewriteで一括修正」(多箇所一括Rewrite) | **B寄り(Phase 2設計課題として記録、実装・Trialなし、ユーザー判断待ち)** | 設計書§5末尾「委任_13追記 Phase 2設計課題1」(4608-4618付近)。本設計の複数spanは「同一deviationのspan配列」で、cross-fact一括とは別 |

注: Grepは語彙検索であり、別の表現で検討された可能性までは網羅できない。「C」は「今回のGrepで記録を見つけられなかった」の意味。

---

## 10. 検証するなら何を確認すべきか(限定Trialの骨子。実行しない)

**段階0(¥0、決定論、LLMなし)**: 既存の固定Stage 1・既存記録の`claim_in_article`を、アダプタ(完全一致+N1〜N5)で範囲へ変換し、
(a)付録Aの再集計を再現する、(b)rep21 s1・rep20 s2の2例で範囲が§5のとおりになる、(c)新locateと旧locateの結果の差分を全件列挙する、をunit testとして確認。

**段階1(Rewrite以降のみ、固定Stage 1入力、API課金あり)**: 固定fixture(meta_run03_standard)を新しい受け渡しで走らせ、Stage 1の揺れを混ぜずに受け渡しの効果だけを見る。
確認項目: (1)複数span claimが1周で全spanへRewriteされたか、(2)Stage 4のreasonの分布、(3)Safety対照(changed_number等)で既存floorが引き続き発火し、false PASSが0件か、
(4)cycle数・費用。**成功基準の数値はユーザー/Fableが事前に決める**(本書では決めない)。
費用の概算根拠: rep21 s1の実測は1 run ¥2.1567(3 cycle、8 call)、rep20/21の本体は合計¥3.3619(委任_36、設計書§6-17)。n=2〜4 runなら**概算¥5〜10程度**
(過去実測からの単純外挿。Trial設計時に確定する。未算定扱いでも可)。

**段階2(新Checker Prompt、API課金あり)**: 同じ記事にCheckerの新指示を実行し、(1)`violation_spans`の逐語率(完全一致/N1〜N5一致/不一致)、(2)現行Checkerとの検出差(見逃し・誤検出の変化)、
(3)不一致の内訳(写し損ね/複数箇所一致/省略記号/要約)を測る。この結果で、§2-4のAで足りるかBが必要か、§6の次段へ進むかを判断する。
Checker呼び出しの過去実測平均は¥0.526(`stage1_recheck`、n=10、meta_run03_standard rep19-21)。回数は設計時に確定(未算定)。

Productionへの影響: いずれの段階もDEV/Trialのみ。Production採用判断は別途人間承認。

---

## 11. 確認済み/未確認の区別、Opusに特に見てほしい論点

### 11-1. 確認済み(コード・実データで直接確認)

- 現行の対象決定の4段、書き戻しの完全一致`.replace`、guardの式、JA側5段の推測(runner該当行、本文中に記載)。
- Checker Prompt/schemaに逐語・位置の指示がないこと(vfl01:464、502-541)。Production正式pathがvfl01を使い(er003_v1_n3_01_articles_generate.py:1142等)、Self-Recovery Flowはrunner側で追記・schema拡張している事実。
- rep21 s1・rep20 s2の実claim文字列、記事の該当段落、hint、rewrite_records。rep20 s2 cycle1でhint引用経由の2文範囲が1回のRewriteで直ったこと。
- 付録Aの再集計(既存記録の読み取り)。EN/JAの文数の不一致(rep19の実データ)。
- JA Recheckが英語本文を渡されていないこと(runner:4504-4516)。

### 11-2. 未確認(推測・未測定)

- 逐語指示を入れた新Checkerの逐語率・検出精度への影響(未実行)。
- Rewrite役が2文範囲を適切に直す確率(n=1のみ)。
- 現行のあいまい一致fallbackが「正しく」直せていた割合(付録Aは逐語性の集計であり、正否ではない)。
- rep20 s2のJA本文(記録なし)。JA対応の実際の正解。rep19のJA段落は同一固定データ由来と想定(未確認)。
- 他記事のStage 4の原因(未調査)。
- 新設計でrep21 s1が`cycle_limit_exhausted`を回避できるか(HC-010の出方次第)。

### 11-3. Opusに特に見てほしい論点(設計者として自信がない点・判断が割れうる点)

1. **fail-closed(§2-4 A)の妥当性**: 不一致を人間確認に倒すと、現行fallbackで正しく直せていた分のHuman Reviewを増やす恐れ。BやCを初期仕様にすべきか。
2. **正規化の境界(N1〜N5)**: N4(大文字小文字の同一視)は「機械的」と言えるか。短い断片の曖昧一致を、「1箇所一致」だけで十分に防げるか。
3. **guard置換(§1-3、§4-5)**: 現行guardは複数文で取りこぼしを検出できないが、置換案(spanが変化したか+Recheck)は「安全装置の弱体化」と読まれないか。delete型の再出現確認(2769)をRecheckに一本化してよいか。
4. **JA側(§4-3)**: J1(検査役がJA対応を宣言)は、位置比近似より良いのか、単に責任の所在を変えただけか。J2(自言語のspanで直す)を主にすべきか。文数が1対1でない前提で、JA/ENペア書き換え自体の設計が妥当か。
5. **1 span=1 Rewrite呼び出し(§4-2)**: 離れた複数spanを別呼び出しにすると、整合(同じ語句の訳し分け等)が崩れないか。1回の呼び出しでJSON配列を返す方が安全か。
6. **claim区分(§4-1)**: 複数spanが別区分(hook+本文等)のときに「最も保護の強い区分」とする判断。
7. **`claim_in_article`と`violation_spans`の二重化(§8-3)**: 食い違いが新しいFailure modeにならないか。`claim_in_article`を廃止し`violation_spans`へ統合すべきか。
8. **Stage 2のhint引用を対象決定から完全に外す(§1-2)**: Stage 2が文脈を見て絞り込んだ引用が、Checkerの範囲より適切な場合を切り捨てていないか。
9. **段階0(Prompt変更なしの機械的復元)だけで十分では**: 付録Aの82.8%/91.5%が本当なら、Checker Promptの変更(段階1以降)は不要か、効果は限定的か。「最も単純で十分な案」は段階0までではないか。
10. **既存テスト・Trial設計の整合**: 7-3の書き換え対象テストの範囲は妥当か。
11. **さらに単純な代替案**: 例えばCheckerの`claim_in_article`の引用符を外して`locate_best_sentence`の完全一致を通すだけ(1行修正)は、本設計のうちどこまでを解決し、何が残るか。
    (本書の見立て: 連続2文は解決する。離れた2文はN5が必要。逐語でない・複数箇所一致・JA対応は残る。**Opusの独立判断を求める**)

---

## 付録A. 既存記録の再集計(「既存記録の再集計」ラベル。Trialではない)

性質: 既存の`er052_output/`配下のJSON(`instances_*/*.json`)を**読み取り集計**しただけ。LLM呼び出し・API課金・Trial実行はなし(¥0)。スクリプトはリポジトリ外の一時ディレクトリで実行。

**対象**: `er052_output/open233_self_recovery_flow_runner_01_{iter5,6,7,8,rep7〜rep21}/instances_*/*.json`(277ファイル中、cyclesを持つもの)。
**含める**: `detected_by == "stage1_llm"`かつ`enumeration_source_claim`なし(=検査役が自分で返した`claim_in_article`)かつ、そのcycleで検査役が見た記事(EN)の本文が記録されているもの。
**除外**: 同一fact別箇所の展開claim(213件、逐語substringで作られるため)、precheck由来claim、記事本文が記録されていないcycle(75件)。検査役が見た記事は、cycle k≥2なら`cycles[k-2].en_text_after_rewrite`、cycle1なら`cycles[0].en_text_before_rewrite`とした(この対応は本集計での仮定。cycle3等で記録がない場合は除外)。
**注意**: 固定Stage 1を再利用したrepは同じclaimが繰り返し現れるため、行数は独立なサンプルではない(ユニーク文字列数も併記)。JA言語のclaimがEN記事に対して照合されたもの(3種類)は、記事の対応付けの仮定が外れている可能性がある(未確認)。

分類: (a)そのまま記事に含まれる (b)両端の引用符を外せば含まれる (c)“…”断片ごとに分ければ全て含まれる (d1)大文字小文字・空白・曲線引用符のみ正規化すれば含まれる (d)いずれでも含まれない。

| 対象 | n | (a) | (b) | (c) | (d1) | (d) |
|---|---|---|---|---|---|---|
| 全run・全記事(行数) | 389 | 157 | 146 | 19(複数断片14+単一断片5) | 34 | 33 |
| 全run・全記事(ユニーク文字列) | 134 | 51 | 44 | 16 | 10 | 13 |
| meta_run03_standard(全run) | 71 | 7 | 43 | 4 | 17 | 0 |
| meta_run03_standard rep19-21 | 23 | 0 | 19 | 2 | 2 | 0 |

- (a)+(b)+(c)=322/389=**82.8%**(行数)、111/134=82.8%(ユニーク)。(d1)まで含めると356/389=**91.5%**、121/134=90.3%。(d)=33/389=8.5%、13/134=9.7%。
- (d1)のユニーク10種類の内訳: 大文字小文字のみ8、空白のみ2。典型は“Some calls needed user information to continue.”(記事は「Also, some calls…」)。
- (d)のユニーク13種類: JA言語のclaim3、bgroup_B3の要約的な文2、その他8(省略記号「…」入り、複数引用の接続、見出しの言い換え等。個別の原因分類は本書では未実施)。
- 逐語(a/b/c)322行のうち、複数文を1つの引用に入れたもの55行、複数断片のもの19行(23%)。「複数文・複数断片」は稀ではない。
- 参考(現行locateの経路、BLOCKING claim261件のうち`rewrite_hint_quote`で対象が決まったもの65件=逐語(a/b/c)41+(d1)24)。現行は(d1)(大文字小文字の差)を、実質的にStage 2のhint引用で救済している。
  新設計でN4(大文字小文字の同一視)を入れるのは、この救済を機械的に代替するため。locate方式を判別できない記録が多く、この参考値は不完全。
- **逐語指示を入れたCheckerの逐語率は未測定**。上の数値は、逐語指示のない現行Promptが出したclaim文字列を、機械的に変換した結果である。

## 付録B. 実例の確認結果(既存記録の読み取り)

- rep21 s1: 固定Stage 1 deviations[1]の`claim_in_article`の引用符を外した文字列(135字)は、cycle1入力の記事に1回出現。引用符付きは含まれない。
  cycle1 rewrite_recordsの`guard_ok: true`・method=`e1_minimal_word_edit(er010_word_overlap(sentence_fallback(overlap=0.55)))`・差分は`during calls.`→`during a call.`のみ。
  cycle2のStage 2 hintは`“These calls were about …”`を引用し`rewrite_hint_quote`で第2文が直った。cycle3は別事実MUSE-HC-010のclaimがBLOCKINGで残り`cycle_limit_exhausted`。
- rep20 s2 cycle1: hintが2文claim全体を引用→`e1_minimal_word_edit(rewrite_hint_quote)`、`guard_ok: true`、段落[7](0始まり)の差分は「during calls. These calls were」→「during a call. This call was」(2箇所1回のRewrite)。
- rep20 s2 cycle2: `claim_text`=`“They could not tell if it was AI or a person” and “They did not realize it.”`。2断片は各1回出現。`locate_multi_quote_span`相当の包含スパンは135字の3文(間の文「They enjoyed AI’s convenience, but a human was on the other end.」を含む)。
  stage4_reason=`ladder_exhausted_without_full_rewrite`、各水準のLLM出力は記録なし。
- (注)委任_38の説明書にあったrep20 s2の「0.74/0.48」等のSequenceMatcher再計算値は、本書では再実行していない。

## 付録C. 読んだファイル(本委任)

`docs/pm/explain_open233_checker_to_rewrite_target_01.md`(全文)、runner(1105-1155、1844-1875、2241-2536、2540-2640、2731-3235、4075-4264、4278-4337、4496-4650、およびGrep)、
`er003_v1_en_direct_vfl_01_generate.py`(440-604)、`er051_open233_checker_trial_variant_01.py`(175-250)、stage2(40-79、184-213)、
`docs/pm/design_open233_self_recovery_flow_01.md`(219-290、470-532、1900-1925、2460-2480、2936-2960、3300-3345、3370-3392、4608-4624、5170-5195)。
一覧外の追加Read: runner 4075-4264・4278-4337・4496-4650(Recheckと周回の流れ確認のため)、er051 175-250(Trial variantの構造確認のため)、design 470-532(Stage 1の仕様確認のため)。
