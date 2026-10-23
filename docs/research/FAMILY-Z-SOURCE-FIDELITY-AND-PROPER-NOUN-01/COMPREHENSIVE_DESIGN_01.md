# COMPREHENSIVE_DESIGN_01: 原作の本質を守る包括対策の設計案(Opus/Fableレビュー用)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01A / 区分A / 2026-10-23 / 設計のみ・API 0
Status: **設計案(採用未承認)**。Trial・Production実装・Prompt変更・撤去Validatorの復活は行っていない。到達可能Status=調査完了/USER_DECISION_REQUIRED(Fable付与)。
前提: 原因は`ROOT_CAUSE_01.md`(主因=Seed `conversion_plan`が結末を「犬の嘘」で定義+最後の行の後の説明を禁止、編集方針から結末維持条項が消失)。

## 1. 設計の制約(ユーザー原文§4・2026-10-12決定)
- 必須の品質: 重要な結末・種明かし・伏線回収、主要人物の役割/関係/動機、重要因果、解釈を根本的に変える省略・改変をしない。許容: 脇筋・重複描写・背景説明の省略、自然な英語のための表現変更。逐語再現は要求しない。
- 方向: **Writer・構成Promptの改善を最優先**。必要なら重要要素を構造化して最終本文へ引き継ぐ。検査追加は比較してから。過剰な判定・retry・Human Reviewを発生させない。
- 2026-10-12決定(③④)との整合: ③=意味保持LLM Validator・別名の意味チェック/独立QAを新設しない、④=品質問題はWriter側Promptで対応、Checker/Validatorを安易に増設しない。**撤去済みer061は復活させない**。

## 2. 候補(4案)
| 案 | 内容 | 原因(§2 of ROOT_CAUSE)への対応 |
|---|---|---|
| A | Writer Prompt原則の追記のみ(編集方針ブロックに「原作の結末・種明かし・伏線回収・主要人物の役割は落とさない」等を追加) | 主因のうち「結末維持条項の消失」だけに効く。Seedの`conversion_plan`矛盾は残る |
| B | **維持必須要素の構造化(Seed側)+全Writer段への引継ぎ**: `seed.json`に`source_essentials`(任意キー)を持たせ、R0〜R2・Std調整のPromptへ「Must-keep」ブロックとして渡す。追加API呼出なし。確認はSeed承認時の人手確認と既存のFable CP(チェックリストをessentialsから機械的に作る)で行う | 主因(結末定義の矛盾)と副因(結末維持条項の消失)の両方に効く。出来事でない結末(語り手の総括等)も明示できる |
| C | B + 最終本文に対する軽量事後確認(1回LLM判定、非Blocking=記録のみ、またはBlocking) | 同上+LLMの自主的省略を検出。非Blockingでも新規LLM呼出が増える |
| D | 独立Validator復活(er061型) | 検出のみ(原因は直さない)。2026-10-12ユーザー決定③と衝突 |

## 3. 比較表(必要性・QCD・リスク・既存承認との相違)
費用の単価は`writer/provenance.json`の実測から逆算(gpt-6.1-sol: 入力約0.32円/1k tok、出力約1.6円/1k tok。R0=1,373in/1,084out=2.17円、R1=651in/1,003out=1.81円から連立で算出)。現行のText工程実費=17.76円/記事(writer 8.22+std 9.54)。

| 案 | 追加API呼出/記事 | 追加費用/記事(概算) | retry・HR発生リスク | 既存承認との相違 | 再発防止力 | 主な欠点 |
|---|---|---|---|---|---|---|
| A | 0 | 約0.04円(R0入力+約120tok) | なし | ④の範囲内(Writer Prompt改善)。ただし編集方針ブロックの文言変更=Writer Prompt原則の変更→**ユーザー承認要** | 中。LLMが「何が本質か」を自分で判断する必要があり、今回の失敗点(判断の誘導)は`conversion_plan`側に残る | Seed側の矛盾を直さないと効果が不確実 |
| **B(推奨)** | **0**(Seed作成時のSeed担当の作業内) | **約0.3〜1.0円**(Must-keepブロック約250tok×4段=入力約1,000tok=0.32円。各段の出力は変えない=自己チェック出力なし。自己チェック文を出力させる場合のみ+約1円) | なし(検査Gate・retryを追加しない) | ④の範囲内(Writer側改善・Checker非増設)。③に抵触しない(Validator無し)。**Writer Prompt原則の変更+`seed.json`スキーマ追加+Seed作成手順の追加=ユーザー承認要**。旧「Keep every Story Seed element」の復活ではなく、必須要素だけに絞る点を明示 | 高。結末定義の矛盾を構造的に解消。出来事でない結末も1項目として指定可。essentialsはFable CPのチェックリストにそのまま流用でき、CP観点4のような曖昧さを無くす | 検出は人手(Fable CP)依存。essentialsの質=Seed作成担当の質に依存 |
| C(非Blocking) | 2(Adv/Std各1) | 約1.4円(各 約1,350in/150out=約0.67円) | 非Blockingなら無し。Blockingにすると欠落時に再生成(約17円)+retry/HR増 | **新しい検査の追加**。③「別名の意味チェック・独立QAを新設しない」「Checker/Validatorを安易に増設しない」と相違が大きい | 高(検出)。原因は直さない | ユーザー判断が要る新Gate。誤検知時のコスト |
| D | 2〜4(判定+再判定)+calibration | 判定約0.4円/回(Melos実績の委任_10 Validator呼出 0.39円)+作品別anchors作成+calibration(上限8円/作品、`er061 CALIBRATION_CAP_JPY=8.0`)+FAIL時の再生成約17円 | 高(FAIL→再生成/STOP/NEEDS_REVIEW) | **2026-10-12ユーザー決定③の直接撤回**。復活には明示のユーザー判断が必要 | 高(検出) | Melos用anchorsを作品ごとに作る必要(『開いた窓』には元から無かった)。過剰判定・HRリスク |

## 4. 推奨案(1つ): **案B(維持必須要素のSeed構造化+全Writer段への引継ぎ。新規LLM呼出なし・新規Gateなし)**
理由(QDC):
- **Q**: 原因の中心(Seed側の結末定義の矛盾と、Promptから結末維持条項が消えたこと)を直接直す。「逐語でなく意味を残す」ことを明示でき、脇筋・表現変更の自由(④)を保てる。
- **D**: 追加API呼出0、Writer段のPrompt追記のみ。再生成・retry・HRを増やさない。作業はSeed作成時に完結。
- **C**: +0.3〜1.0円/記事(Text工程17.76円に対し+2〜6%)。Validator案Dの継続費(判定+calibration+FAIL時再生成)を回避。
- 既存承認との相違: ③の「新Validator/別名の意味チェックを作らない」に抵触しない(検査追加なし)。④の「品質問題はWriter側Prompt改善で対応」を実行する案。**相違点は「Writer Prompt原則の変更」「seed.jsonスキーマ追加」「Seed作成手順の追加」の3点で、いずれもユーザー承認が必要**。

### 4-1 設計の中身(案B)
1. `seed.json`に任意キー`source_essentials`(未設定の作品=現行動作と出力が完全に同一。後方互換)。項目は最大5〜6件:
   - `ending_reveal`: 結末・種明かしの意味(1文)、`source_quote`(原作の該当文)、`placement`(例 final)、`wording`(自由。ただし聞き手に意味が明示的に伝わること)。**出来事でない結末(語り手の総括)もここに書く**。
   - `setups_and_payoffs`: 伏線→回収の対(例 窓/白いコート/歌/スパニエル→人影の場面)。
   - `key_roles`: 物語上必須の人物の役割・動機(各`keep_name: true|false`を持てる。区分B「重要人物は名前を維持」の判定を、共通Promptだけに任せず作品のSeedで確定させる補助線にもなる。01Bの共通Prompt Trial結果次第で使用)。
   - `key_causality`: 壊してはいけない因果(例 少女の作り話→客の逃走→犬の作り話)。
   - `free_to_cut`: 省略・圧縮してよいもの(脇筋・背景、④の自由を明示)。
2. R0 Prompt: `[Must-keep -- story essentials]`ブロックを編集方針ブロックの直後に挿入。文言案: 「Whatever else you change, the following must remain recognizable to the listener. Wording is yours to choose, but the idea must be clearly conveyed, and the reveal must not be replaced by a different ending. If the original's final reveal comes from the narrator, keep it as the final line.」+ 項目列。`free_to_cut`は「Everything else may be shortened or reshaped.」とする。
3. `conversion_plan`の書き方指針(Seed作成手順): 「結末」を出来事で定義するときは"最終文(語り手の総括)を含む"か明示する。「最後の行の後に説明を足すな」は、原作自身の最終文を除外する旨を明記する(今回の矛盾の直接修正)。
4. R1/R2: `REVISE_USER_TMPL`(`er062_family_z_writer_01.py:139`)に`Keep these essentials: …`を1行追加(Seed全文は渡さない=アンカリングによる自由度低下を避ける)。Std調整Prompt(`STD_PROMPT_TAIL`、L153〜)にも同1行(A2化で必須語が平易語へ置換されること自体は許容、意味維持が要件)。
5. 確認: Seed承認時にFableがessentialsを原作と照合(1回)。本文承認(Fable CP)ではessentialsを項目別に「本文のどこで満たされているか」を引用で確認(チェックリスト化。観点4型の曖昧な文言をやめる)。コード上のGate・retry・Human Reviewは追加しない。
6. 実装の隔離(11-7): essentialsを持たないSeed(Melos現行Production)は出力不変。`build_r0_prompt`/`build_revise_prompt`/`build_std_prompt`にessentials有無の分岐を追加する変更は、**ユーザーがWriter Prompt原則の変更を承認するまで実装しない**(未承認Promptを既定ONにしない)。

### 4-2 却下理由
- A単独: Seedの`conversion_plan`矛盾が残り、主因を直さない。BのPromptブロックの一部として吸収する。
- C: 現時点では不要。**Bを適用した後の複数作品で欠落が再発した場合のみ、実測を添えて再提案する**(判断基準: 2作品連続でessentials未充足、など。過剰なretry/HRを避けるため、導入するなら非Blocking・記録のみ)。
- D: 2026-10-12決定③の撤回が必要で、作品ごとのanchors作成・calibration・FAIL時の再生成コストが大きく、原因(指示体系)を直さない。無断復活はしない。

## 5. 検証設計(承認後・未実施。API費用0の現段階では行わない)
- 因果反証(最小): 同一Seedで`conversion_plan`の矛盾箇所だけを直した条件、旧ブロック(f955847db)条件、案B条件のR0のみを各n=3回生成し、最終文の有無を比較。R0単価2.17円×3条件×3回=約19.6円(7-7の300円以下。ただし**新仕様/未承認Trial範囲**に当たるため、委任文でScope承認が必要=判断候補)。
- Trial成功≠Production採用。成功してもAPPROVED_FOR_PRODUCTIONは人間ユーザーのみ。

## 6. Opus/Fableレビュー用の論点
1. 主因判定の妥当性: `conversion_plan`の矛盾(結末の定義+最後の行の後の説明禁止)を主因(約80%)とする根拠は十分か。反事実未検証の扱い。
2. 案Bの「Writer Prompt原則の変更」は、2026-10-12④(Writer Prompt改善で対応)の範囲内と解釈してよいか、それとも「承認済み仕様の変更」としてユーザー承認を要するか(本設計は後者として扱う)。
3. R1/R2/Stdにessentialsを渡すことで、R1/R2の面白さ最適化(「more engaging」)を損なわないか。渡さない場合はR0の取りこぼしを下流で救えない(今回の構造)。
4. 人手確認(Fable CP)だけに依存する構造の脆弱性。非Blocking記録(案C)をいつ導入するか。
5. essentialsの質をどう担保するか(Seed作成担当と承認者、項目数の上限、書式)。
6. 『出来事でない結末』『語り手の総括』以外に、古典で落ちやすい要素(冒頭の枠物語、最終段の反転、題名の意味)をスキーマで拾えているか。
7. 区分B(固有名詞)との結合: `key_roles.keep_name`を使うか、共通Prompt(01B Trial)のみで運用するか。作品個別の指定が必要になった場合の置き場所として妥当か。
8. 『開いた窓』support lintの`forbidden_names`(`er062_family_z_structure_01.py:810`にヴェラ)と、区分Bの新ルール(Vera維持)の衝突(Preview/Commentに名前を出さない規則との整合)をどこで解消するか。

## 7. ユーザー判断事項(判断候補、`USER_DECISION_REQUIRED`ラベルはFableが付与)
| 項目 | 区分 | 内容 |
|---|---|---|
| 案Bの採用(Writer Prompt原則の変更+seed.jsonスキーマ追加+Seed作成手順の追加) | D 真に新しい判断 | 2026-10-12④「原作と異なる展開も許容」に、「重要な結末・種明かし・伏線回収・主要人物の役割・重要因果は維持、脇筋・表現は自由」という境界を明文化するもの。Validator/Gateの追加は含まない。QCD: +0.3〜1.0円/記事、遅延0、品質リスク低減 |
| 因果反証Trial(約20円)の実施 | D | 案B採用判断の前に、原因(b)を検証するか、検証なしで案Bに進むか。推奨=案B採用判断と並行して実施(約20円、7-7内だが未承認Trial範囲) |
| 案C/Dの扱い | A既判断 | Dは2026-10-12③で中止済み(`CURRENT_SPEC.md:1620`)。Cは本提案で採用せず、再発時のみ再提案 |
