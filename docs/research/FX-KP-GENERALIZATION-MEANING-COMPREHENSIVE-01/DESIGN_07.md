# DESIGN_07: 課題① 字義訳 — 根本対策候補(正しい意味を最初から生成する方法の優先、追加call 0を優先)(委任_21、2026-10-24、API 0・設計のみ)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21 / 原因=`ROOT_CAUSE_04.md` / Trial設計=`TRIAL_DESIGN_05.md` / Opus依頼=`OPUS_REVIEW_REQUEST_07.md`
状態: 設計案。Production採用は未承認。DEV/Trial専用経路(er112系)でのみ検証する。本書はコード・Prompt・SSOTを変更しない。
行番号はHEAD(c7a43c8f3)基準(並行の課題②配線で作業ツリーが編集中のため)。

## 0-R. 【改訂(委任_22、2026-10-24)】OPUS_REVIEW_07 OF-KP1-01〜08の反映
- 主因の順位を改訂(`ROOT_CAUSE_04.md` §0-R): 主因=本文での意味を確定する段の欠如、H5=増悪因子(未検証)。案Aの推奨理由は『H5の置換』でなく『Cpの実績(意味の計算を促した効果)+判定結果をglossの規則に接続する点+費用削減』。以下の§0で『(i)文脈限定句=案A/Bで置換』を最優先と読める箇所は、この節が優先する。
- Cpは参照でなく**armとして並べる**(OF-KP1-03)。X2がCp同等以上かつ安価なら案A、劣るなら案C最適化版(英語文を1文、未使用の`gloss_conveys`削除)。
- §4の草案から『他の記事でも同じ意味で使える表現にします』を削除、yes経路に『naive_jaをそのまま写さず定訳・自然な訳を選ぶ』を追加(下記§4に反映済み)。
- few-shot例『fall into→～に落ちる(「～に陥る」へ書き換えません)』は字義寄りを手本とする原因候補(`ROOT_CAUSE_04.md` §0-R)。X2/X1のM-baseでは除かれる。
- Trial出力schemaはProduction必須欄(`current_gloss_consistent`/`qa_reflects_all_key_phrase_words`/`added_word_mappings`/`reasoning`)を残し、新欄(`meaning_in_text_en`/`naive_ja`/`naive_ja_conveys`)を`japanese_gloss`の前に挿入する(OF-KP1-07)。混在batch・Z repair/再整合経路の扱いは`TRIAL_DESIGN_06.md`。(下記§4の『DEVはM_SCHEMA同様…持たない』は本改訂で『持つ』に変更)

## 0. 結論(先頭)

- **推奨: 案A(gloss生成call内で『本文での意味(英)→字義の日本語は意味を運ぶか→gloss』を先に書かせ、文脈限定句を『本文での用法に合わせる』へ置換)**。追加LLM call 0。字義の日本語が意味を運ぶ(yes)場合は現行と同じ自然な訳に戻るため、通常表現への影響を構造的に抑える。
- **同時にTrialで検証する対照**: 案B(文脈限定句の置換だけ。欄追加なし。**最安・原価は現行より下がる**)、案C(Trial_04のCp=自己監査欄つき生成。**既存実測で全arm最良、再現確認が必要**)。
- 案D(canonicalization所見のhint渡し)・案E(選定schemaへの意味メモ欄)は、案A/Bが不十分だった場合の次手。案F(事後検査C)はユーザーが現段階で不採用のため最終手段。
- 3点の原因(ROOT_CAUSE_04)に対応: (i)文脈限定句=**案A/Bで置換**、(ii)解釈が出力に現れない=**案Aで先に書かせる**、(iii)日本語化段に字義像の判定が無い=**案Aの`naive_ja_conveys`**。

## 1. 設計要件(原因から導出)

| ID | 要件 | 根拠(ROOT_CAUSE_04) |
|---|---|---|
| R1 | gloss段に『本文のこの箇所での意味を読む』ことを求め、『文脈を使うな』を撤去する | §2-1(H5) |
| R2 | 本文での意味を、gloss確定**前**に可視化する(英語1文) | §2-4(G2 draw a line r2以外、unseen clock 4/4) |
| R3 | 日本語化の前に『字義の日本語がその意味を運ぶか』を判定する | §2-4(G2 draw a line r2の字義訳、G3が案を並べると0/7) |
| R4 | 字義の日本語が意味を運ぶ場合(term・日本語でも通じる慣用・字義用法)は、**現行どおりの自然な訳**に戻す(G2/G3の説明文化△を避ける) | §2-5-2(b) |
| R5 | 追加LLM call 0、既存のretry/fallback/Gate(qa、括弧禁止、人称整合、attempt上限2、HR経路)を回避しない | ユーザー§2-3、charter |
| R6 | X/Y/Z共通(`er003_key_words_gloss_alignment`の1箇所)、Adv説明のB仕様(PROMPT_SHA256)は変えない | §1表 |
| R7 | 検証は結果に依らない事前層別+新規repの対照で、検出力を確保(事後層別バイアスを避ける) | ROOT_CAUSE_04 §6 |

## 2. 候補案(6案)

### 案A: gloss生成call内の『解釈先行+字義像判定』(推奨)
- **変更する工程**: gloss生成call(新規生成=current gloss null、全KP)。入力はM-base(再整合用の文を除く)に、使い方の指示を置換。出力schemaに3欄を**japanese_glossの前**に追加。
- **入力構造の変更**: (a)見出し文を『この表現が本文のこの箇所で実際に表している意味を日本語で表す』へ置換(HEAD `:603`の『他の文脈でも再利用できる…文脈の追加はしない』を『記事固有の固有名詞・数値・出来事はglossに入れない』へ限定)。(b)新規生成規則 `:320`と人称規則 `:309`の『source_sentenceは語義を選ぶためだけに使う』を『source_sentenceと前後の文脈は語義と用法(字義/比喩・慣用)を決めるために使う』へ。(c)再整合用の1〜3・判定参考例を除く(M-base、費用減)。
- **出力構造(順序固定)**: `meaning_in_text_en`(平易な英語1文、本文での意味)→`naive_ja`(英単語を日本語対応語へ置換しただけの訳、解釈なし)→`naive_ja_conveys`(yes/partly/no)→`japanese_gloss`。
- **gloss規則**: yes=現行どおり自然で平易な訳(定訳・日本語の慣用があればそれ)。partly/no=naive_jaの像を使わず、meaning_in_textを日本語の慣用表現か平易な短い言い換えで。**key_phraseと同じ品詞・同程度の長さの句**(説明文・定義文にしない)。
- **追加call**: **0**。
- **比喩・慣用・通常の扱い**: 字義用法・term・コロケーション=yes(現行どおり、定訳を維持)。日本語でも通じる比喩慣用(光を当てる、ハンドルを握る、舞台裏)=yes。日本語に運ばれない新造比喩・断片慣用=no→意味に寄せる。部分的に落ちる(拳を突き上げる→喜びが落ちる)=partly。
- **通常表現の非劣化の担保**: (1)yes経路のgloss規則は現行と同一の目標(自然な訳・定訳)。(2)G2/G3の△の原因(一律の言い換え強制・一般化した中心義・『聞いてすぐ分かる』基準)をいずれも持たない。(3)Trialで非対象KP57個をFable盲検で対B0比較(§TRIAL_DESIGN_05)。**構造保証ではなく実測**(Cp同様、文字列は変わりうる)。
- **X/Y/Z共通**: 共通(`er003_v1_n3_01_scaffold_generate.py:538`のgloss alignmentをX・Yが、`er026_family_z_fiction_production_runner_01.py:1552`のZ repairが同じmoduleから呼ぶ。Yは`er110_family_y_text_trial_01_run.py:235,264`が`sc.run_key_phrases`経由)。1箇所の変更で3 Familyに及ぶ。
- **量産単価・速度**: 出力欄が増え(実測proxy: G2 0.107〜0.130、G3 0.094〜0.104、Cp 0.179 円/call vs B0 0.061)、M-baseの入力縮小(−0.024/call)で一部相殺。見込み **+0.05〜+0.12円/call、1記事2call(a2+b1b)で+0.1〜+0.24円/記事(70円目標の0.1〜0.3%)**。Trial前に6〜10 callの小規模実測で確定(Trial_04の見積り超過の再発防止)。速度: 出力token増(Cpで+1,200 token/call)で数秒〜十数秒/call(未測定。KP段は他段と並行性なし、記事全体の所要の数%)。
- **既存Trialとの差(なぜ今回は効くと言えるか)**:
  - 対G0/M: 文脈限定句を**置換**し、解釈を**出力に出させる**(G1・Mは言い回しだけの変更)。
  - 対G2: 欄は『一般化した中心義』でなく**本文での意味**。さらに**条件付き**(yesなら現行どおり)で、一律の言い換え強制をしない。G2で日本語化が字義に戻った例(draw a line r2)には`naive_ja_conveys`で対処。
  - 対G3: 候補比較は使わず、現行の自然な訳を既定にする(説明文化の原因を避ける)。
  - 対Cp: Cpの欄は**gloss後**(出力が使われない自己点検)。案Aは**gloss前**で、判定結果を**glossの生成規則に接続**(partly/noなら字義の像を禁止)。Cpの有効性(0/4、F層FAIL 0)を『欄の存在が意味同定を促した』と解釈し、その効果を保ちつつ英語文を2文→1文+短欄に絞る。
  - 対C: 検査callなし、誤検知による再生成なし。
- **リスク**: (1)`naive_ja_conveys`が常にyes(確証バイアス)になり効果が出ない→Trialで`naive_ja_conveys`の再現率を測る。(2)no/partlyが多すぎて説明文化→N層・F層の非対象KPで検出。(3)出力token増による費用超過→pilot実測。(4)Adv入力のglossが変わる→gloss変更でAdvが再生成(既存signature機構、追加callなし。『一線を引く』→Adv『acceptable』狭小化の逆方向=改善見込み、`ROOT_CAUSE_02.md` §3-1)。

### 案B: 文脈限定句の置換のみ(欄追加なし、原価最小)
- **変更する工程**: gloss生成callのmessage(M-base)。見出し文と新規生成規則の『語義選択専用・文脈追加禁止』を『本文での用法に合わせる』へ置換するのみ。schema変更なし。
- **追加call**: 0。**原価は現行より下がる**(M実測0.0376 vs B0 0.0612円/call)。
- **比喩・慣用・通常の扱い**: モデルが本文の用法に応じて自力で決める。
- **非劣化の担保**: 追加の欄・規則が無いため、変化は『文脈の使い方』のみ。Trialで実測。
- **X/Y/Z共通**: 共通。
- **既存Trialとの差**: Mは再整合文を除いたが**制約句は残した**。Bは制約句そのものを置換する(H5の直接検証)。
- **リスク**: 解釈が出力に現れないため、効果が不十分な可能性(解釈先行の効果が必要なら案A)。文脈追加が『固有名詞・出来事の混入』を招く可能性(規則で禁止を維持するが要確認)。
- **位置づけ**: 案Aの因果対照(欄の寄与を分離)。**効けば最安の採用候補**。

### 案C: Cp(自己監査欄つき生成)を生成方式として採る
- **変更する工程**: gloss生成callに、`usage_in_sentence`・`usage_meaning_en`・`gloss_alone_reading_en`・`gloss_conveys`(japanese_glossの後)を追加(既存DEV実装 `er112_kp_gm_trial_04_gen.py` `CP_BLOCK`/`cp_schema`)。
- **追加call**: 0。**実測**: F層41KP FAIL 0/41(B0 7/82)、hard-core 0/4、THIN 2/61(`supply chain`・`draw a line`)、費用0.179円/call(+0.118)、1 rep。
- **問題**: (1)gloss後の欄はglossに影響しない構造のため、効果の機序が不明(prompt内の欄の存在が推論に影響した可能性。仮説)。(2)英語文2文+日本語読み取りで出力tokenが約3.3倍(517→1,716)。(3)判定値を使わない(`gloss_conveys`はflag 0/61)ので欄の大半が無駄。(4)1 repで再現未確認。
- **位置づけ**: 案Aの『下限』(既に近い効果が出ている参照)。案Aが同等以上で安価なら案A、案Aが劣るなら案C(費用を許容するか判断)。
- **X/Y/Z共通**: 共通。**リスク**: 費用+0.24円/記事、薄い2件。

### 案D: canonicalizationの所見をhintとしてgloss段へ渡す
- **変更する工程**: canonicalization(全文を見る既存call、0.28円)のschemaに`usage_in_text`・`meaning_in_text_en`欄を追加し、glossの入力に『参考(誤りの可能性あり)』として添付。
- **追加call**: 0(ただしcanon callの出力増)。2 module変更。
- **効く対象**: `Carry the Load`型(canonicalizationが『負担を担う』と認識しているのにglossが字義)。選定時の意味把握の引継ぎというユーザー例示そのもの。
- **既存Trialとの差/リスク**: E3(中心義を固定して共有)は判断が外れたとき**悪化**(`ROOT_CAUSE_02.md` §3-2: PASS 13/28=最悪)。hintとして『誤りの可能性あり』を明示しても、同一の判断が引き継がれる**独立性の喪失**が残る。canon callの責務(形の正規化、INVALID/REVIEW閾値)が増え、規則3/5との干渉(課題②のA-1配線と同じ箇所)を招く。
- **位置づけ**: 次手。案A/Bで`Carry the Load`型が残る場合のみ。

### 案E: 選定schemaへ意味メモ欄を追加
- **変更する工程**: 選定(Prompt 2は逐語固定=ユーザー承認事項、sha固定)。schemaに`meaning_note`を追加する案、または規則3『最小化』を修正して手がかり(`neighbor's`)を残す案。
- **効く対象**: `greener grass`の断片化(選定が`greener`1語に縮約)。選定時の意味把握を最も上流で引き継ぐ。
- **リスク**: Prompt 2/schemaの変更は**承認済み仕様の変更**(OPEN-454)。選定品質(語の選び方)へ波及する可能性があり、検証コストが大きい。E3同様の判断固定リスク。
- **位置づけ**: 案Aで断片化KPが残る場合の将来案(ユーザー判断が前提)。今回は実施しない。

### 案F: 事後検査C(独立検査+flag項目の再生成)
- 既存実測: F層字義NG 6→1、recall 5/6、precision 5/19、費用+0.2〜0.25円/記事、再生成負荷。**ユーザーが現段階不採用**。生成側の対策が不十分だった場合の最終手段。

### (却下)案G: Adv英語説明を先に作ってStd glossへ渡す
Adv説明はb1bのみで、Std(a2)に存在しない(`ROOT_CAUSE_03.md` B-5)。B仕様(PROMPT_SHA256)の入力にglossが含まれる循環があり、順序入替は承認済み仕様の変更+直列化で遅くなる。却下。

## 3. 比較表

| 項目 | 案A(推奨) | 案B(対照・最安) | 案C(Cp参照) | 案D | 案E | 案F |
|---|---|---|---|---|---|---|
| 追加call | 0 | 0 | 0 | 0(canon出力増) | 0 | +1/記事 |
| 変更module | gloss | gloss | gloss | gloss+canon | 選定 | gloss+検査 |
| Prompt承認事項 | gloss message/schema変更 | gloss message変更 | gloss message/schema変更 | 左+canon | **Prompt 2/schema(逐語固定)** | 新工程 |
| 費用/記事(見込み) | +0.1〜+0.24円 | **−0.05円** | +0.24円 | +0.1円(未測定) | 未測定 | +0.2〜0.25円 |
| 実測済みか | 未(Trial_05) | 未(Trial_05) | 1 rep済み(0/4、F層FAIL 0) | 未 | 未 | 済み(部分改善) |
| 通常表現の保護 | 条件付き(yesで現行) | モデル任せ | 欄は使わない | 固定リスク | 不明 | 再生成はflag項目のみ |
| 主なリスク | 欄の形骸化/説明文化 | 効果不足 | 費用・THIN2 | E3悪化 | 承認事項・波及大 | 誤検知・負荷 |
| 判定 | **Trial_05で検証(本命)** | **Trial_05で検証(因果対照)** | **Trial_05で再現確認(参照)** | 次手 | 将来案 | 最終手段 |

**推奨の理由**: (1)原因のうち**制約句(H5)は全armで未変更**のため、置換が最優先(案B/Aに含まれる)。(2)解釈の可視化は新造比喩で4/4効く実績(G2/G3/Cp/C)があり、欠点(説明文化)は『一律強制』が原因で、**条件付き(yes/partly/no)にすれば避けられる見込み**。(3)追加call 0・M-baseの原価低減で量産単価の増分が小さい。(4)案A/B/Cを同一Trialで比較すれば、『制約句の寄与(B)』『欄の寄与(A−B)』『既存の最良実測(C)との差』が1回で切り分けられる(憲章2: Trial効率)。

## 4. 案Aの具体仕様(Trial用DEV実装の設計。Prompt草案)

DEVでは `er112_kp_gm_trial_04_gen.py` の `gloss_gen` と同様に、arm別にmessageとschemaを組み立てる(Production無変更)。

**developer message**: 「英語学習教材のKey Phraseに付ける日本語グロスを書いてください。」(M案と同一)

**user message(骨格)**:
1. 見出し(M_HEAD改): 「以下の各英語key_phraseは、教材として最終確定した英語表現です。各項目について、日本語グロス(japanese_gloss)を新しく書いてください。japanese_glossは、この表現が【記事本文】のこの箇所で実際に表している意味を、日本語で短く自然に表したものにしてください。記事固有の固有名詞・数値・この記事だけの出来事はglossに入れないでください。」(OF-KP1-01: 旧草案の『他の記事でも同じ意味で使える表現にします』はH5の制約句をほぼ再導入し、新造比喩のno経路と矛盾するため削除。委任_22)
2. 【意味の決め方】(各項目、japanese_glossを書く前に、この順で必ず出力):
   - `meaning_in_text_en`: 【記事本文】のこの箇所(source_sentenceとその前後の文)でkey_phraseが実際に表している意味を、平易な英語1文で書く。key_phraseの語をそのまま繰り返さず言い換える。字義どおりの用法なら字義の意味、比喩・慣用・筆者が作った比喩ならその比喩が表す意味を書く。記事固有の固有名詞・数値は入れない。
   - `naive_ja`: key_phraseの英単語を、それぞれ日本語の対応語に置き換えただけの訳を、意味の解釈を加えずに書く。
   - `naive_ja_conveys`: 日本語だけを読む学習者がnaive_jaからmeaning_in_text_enの意味を受け取れるか。`yes`(同じ意味・同じ比喩が日本語でも通じる、または字義どおりの用法)/`partly`(一部が落ちる)/`no`(字義の動作・物の像しか伝わらず、本文での意味は伝わらない)。
   - `japanese_gloss`: `yes`なら、naive_jaをそのまま写さず、自然で平易な訳(英和辞典の定訳や日本語の慣用表現があればそれ)を選ぶ(OF-KP1-05: アンカリング対策、委任_22追加)。`partly`/`no`なら、naive_jaの字義の像を使わず、meaning_in_text_enの意味を日本語の慣用表現か平易な短い言い換えで表す。key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。
3. 新規生成規則(置換): 「source_sentenceと記事本文の前後の文脈は、key_phraseの語義と用法(字義か、比喩・慣用か)を決めるために使ってください。」
4. 人称規則(`PERSON_CONSTRAINT_TEXT`)・承認済みgloss規則(rules)・対象項目JSON・記事本文は現行どおり(**承認済みgloss規則は一字も変更しない**)。人称規則内の『source_sentenceは人称の指示対象を決めるためには使わない』は人称の指示対象(課題②の領域)の規定として**維持**(用法判定のための文脈利用とは別項目)。

**schema(strict)**: `items[]`: `rank`, `meaning_in_text_en`, `naive_ja`, `naive_ja_conveys`(enum), `japanese_gloss`(この順)。~~DEVはM_SCHEMA同様`qa_reflects_all_key_phrase_words`・`added_word_mappings`・`reasoning`を持たない。~~(委任_22で撤回: Production必須欄`current_gloss_consistent`/`qa_reflects_all_key_phrase_words`/`added_word_mappings`/`reasoning`を残す。OF-KP1-07)**Production配線時は`validate_item_corrected`(括弧禁止・数字・人称整合・qa)との互換を維持する必要がある**(採用提案時に設計。qa/mappingは新規生成項目では`added_content_words`が空で記録のみ)。

**対照(案B)**: 上記1の見出しと3のみ(2の欄なし)、schemaは`rank`,`japanese_gloss`(M_SCHEMA)。
**参照(案C)**: Trial_04の`CP_BLOCK`+`cp_schema`(既存実装を再利用)。

## 5. 採用時の変更点と承認事項(参考、今回は実装しない)
- 変更: `er003_key_words_gloss_alignment.py`の`build_user_message_corrected`新規生成経路(見出し・新規生成規則・schema)、`GLOSS_ALIGNMENT_JSON_SCHEMA`(新規生成用に分岐。既存glossの再整合用経路は変更しない)。Adv説明(`er019_family_x_kp_explanation_01.py`)・canonicalization・選定は不変(PROMPT_SHA256 `c3d3734b…`不変)。
- 承認が要る事項(`判断候補`、D=真に新しい判断): (1)gloss Promptの文脈限定句の置換(承認済みgloss規則の外だがProduction Prompt変更)、(2)schema欄追加と出力の保存先(audit用、Adv入力・TTSへは渡さない)、(3)費用増(+0.1〜0.24円/記事、案Bなら減)。11-7限定例外(新コード経路+単一flag・既定OFF・DefaultOffIsolation)の適用可否は採用提案時に判断(今回は適用しない)。
- 並行の課題②(A-1/possessor_roles)との関係: ②はcanonicalization段、①はgloss段で責務は分離。ただし`er003_key_words_gloss_alignment.py`を共有するため、配線時は①②の変更を別flag・別test(DefaultOffIsolation)で併存させる(今回の設計は②のコード・SSOTに触れない)。

## 6. 撤去・残置
- 本書で撤去する規則・検査・testは無い(新規設計のみ)。案A採用時に整理候補となるのは、新規生成経路での再整合用指示(`:575-595`相当の1〜3・判定参考例)。ただし再整合用経路(current glossあり)では必要なため**残置**。
- 旧ルール残存Grep(識別子): `key_phrase単体で他の文脈でも再利用できる自然な訳`(HEAD `er003_key_words_gloss_alignment.py:603` 1箇所)、`辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに`(同 `:309`・`:320` 2箇所)、`M_HEAD`(`er112_kp_gm_trial_04_gen.py`、DEV)。採用時に置換対象。
