# TRIAL_DESIGN_01: 比較方式・Prompt・評価設計(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_01)

Trial専用経路のみ。Production code/Prompt/Validator/閾値は一切変更しない(Productionは`prod_p7_cands`で結果を読むのと、Before再現で`select_p7`/`run_key_phrase_canonicalization`をread-only呼出するのみ。telemetry書込はprocess内でno-op化)。成果物は本ディレクトリの`kpg01_*`。

## 1. 設計方針(ユーザー指示の反映)
- 『選定(どれを出すか)』と『一般化(どう見せるか)』を別責務にする。Productionのcanonicalizationは**本文一致ルール**(規則1〜5以外の変換を禁止)を守るためのもので、学習表示用の一般化(目的語のsomething化・後続名詞句の除去)は規則にない(CURRENT_STATE_01.md 1節)。→ 本文一致は`source_span`に維持し、学習表示は別フィールド`display_form`として別validatorで守る。
- 難易度優先は維持: P7条件4・5を各方式のPromptへ**逐語**で含める(`kpg01_methods.PROD_DIFFICULTY`)。品質基準の引き下げ・易しい表現への変更なし。
- 候補不足時に品質を下げて埋めない: 全方式で「不足は不足のまま」を明記。
- 必須9例の表現はPrompt・例示に入れない(過学習防止)。Promptの例示は別の表現(walk someone through / in the event of / tighten up / pay off 等)。

## 2. 共通部品
| 部品 | 内容 | file |
|---|---|---|
| 塊価値の3区分 | W(単語のみ難しい)/F(自由な組合せ)/C(塊: idiom・phrasal_verb・collocation・fixed_phrase・compound_noun)。Cは『なぜひと塊で覚える価値があるか』の1文必須。字面と比喩の両義を持つ表現は、本文で比喩的ならC | kpg01_methods.CHUNK_DEFS |
| 一般化規則 | 核(動詞・固定の前置詞/粒子・固定名詞)と可変部(本文固有の目的語・主語・人称)の区別、something/someone/one's/oneself、**末尾の自由な目的語は付けない**、**固定表現の後ろの本文固有名詞句は除く**、核の語は本文の語形違いのみ、語義保持、5語以内 | kpg01_methods.GEN_RULES |
| 決定論検査(API 0) | `source_span`が本文の連続語句/`display_form`の核語が`source_span`の語の語形違い(WordNet morphy)で順序どおり/プレースホルダはsomething・someone・one's・oneself・somewhereのみで本文の置換語数以内/5語以内/末尾プレースホルダは前置詞・粒子の直後なら自動除去 | kpg01_validate.py |
| WordNet複合語signal | 見出しに複合語があるかをSELの参考ヒントにする(ローカルresource。再現率が低く(make room for等を検出しない)、参考のみ) | kpg01_validate.wn_multiword |
| 別系列検証 | gemini-3.8-flash(生成=OpenAI系列と別)。意味保持・日本語意味整合・見出し語の自然さ、可変部/後続名詞句の残りをOK/FIX/REJECTで判定。FIXは決定論検査を再通過した場合のみ採用 | kpg01_methods.prompt_B4 |

## 3. 比較した方式
| 記号 | 構成 | モデル | 位置付け |
|---|---|---|---|
| Before | 現行Production: P7(最大7)→canonicalization(規則1〜5)→gloss再整合→Gate | gpt-6-luna | 比較基準(保存済みfx4_01 docを使用。未使用記事は簡易再現) |
| A_luna / A_sol / A2_sol | **A 統合**: 1 callで抽出・塊判定・一般化(A2は内部screening付き) | luna / sol(low) | ユーザー指定A |
| B_luna / B_mix | **B 工程分離**: 抽出(過剰生成14)→塊判定+難易度→一般化(文章生成)→別系列検証→決定論検査 | luna / sol(low) | ユーザー指定B |
| C1 | 現行P7候補を入力に、塊判定→一般化→検証(既存機構の再利用) | luna / sol | 既存再利用の確認 |
| C2 | 現行P7候補→(塊判定+一般化を1 call)→検証 | luna / sol | 工程数を減らす案 |
| C3 | 現行P7候補+過剰生成→(塊判定+一般化1 call)→検証 | luna | 候補源の拡張 |
| **D** | **候補源=現行P7+過剰生成(luna)→塊判定(luna)→構造化一般化(トークン分類: CORE/SLOT/DROP、display_formはコードが決定論で組立)→別系列検証/修正→決定論検査** | luna+gemini | **最終設計案**。B+C3+構造化一般化の統合 |

D採用の理由(切り分けの結果): ①一般化を文章生成にすると、モデルが比喩語義に引きずられて名詞を核に残す/選択肢を`/`で併記する/語を足す等が発生(B・C系で多発)。トークン分類にすると語の追加・併記・末尾プレースホルダがコード側で構造的に防げる。②現行P7だけでは候補源が不足(C1は1〜4件)。過剰生成との和集合で、D最終候補71件中35件が過剰生成由来、合格率は同等(P7由来32/36・過剰生成由来29/35)。③sol(推奨系)は塊判定で厳しすぎ(A_sol 1件、A2_sol 2件)かつ費用が3〜10倍。lunaで塊判定・一般化を担い、別系列(gemini)の検証で補う構成が品質/費用で最良。

## 4. 評価方法
- 判定単位: 候補(表示形+日本語意味+本文の語句)。『修正せずにそのまま選べる』=一般化が適切・語義保持・日本語意味整合・塊(C)・難易度が基準内・英語として自然、の全てを満たす。
- 一次判定: Sonnet実読(`kpg01_manual.py`、全候補にNG理由)。参考: 別系列(deepseek-flash、非thinking)の独立判定(寛容で一致率は約8割)。最終の独立受入はFable。
- 必須9例: 一般化5・学習価値4(`kpg01_manual.REQUIRED`)。一般化段の単体評価(選定なしで強制通過)も実施(`kpg01_gtest3.py`)。
- 汎化: Family X(選定4記事×2レベル+AI島)、Y(姓選択)、Z(メロス)、未使用記事(イグ・ノーベル賞ゴキブリミルク、Tesla×SpaceX。本文のみ流用)。
- 副作用(既存成功例): 現行Beforeで『選べた』候補(hear it out→hear someone out 等)が After で脱落していないかを記事別に確認(比較ページ)。
