# DESIGN_03: Key Phrase 日本語意味(Std)・英語説明(Adv)の品質 — 原因に基づく再設計(Opus条件Aレビュー前)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_06(2026-10-23) / 根拠=`ROOT_CAUSE_02.md`(以下RC2) / 前版=`DESIGN_02.md`
状態: **設計のみ**(Trial実装はOpus条件Aレビュー後)。Production/Prompt/template/flag変更0。A-1(canonicalization規則5)は`APPROVED_FOR_PRODUCTION`維持(UDR #169、配線は別系統)。本設計は**未承認の追加改善案**であり、VALIDATED後にユーザー正式採否を求める。
制約: 新規LLM call原則0、承認済み品質基準を緩めない、X/Z共通、個別対策不可、Promptの文言反復をしない。

## 0. 設計の骨格(先頭)

RC2の結論から、**文言の再調整でなく「情報の流れ」と「判断力の律速」を直す**。

1. **Advの失敗の大半は、Std向け日本語gloss(訳語の含意・字義寄り・記事固有条件)がAdv説明に伝染すること**(`draw a line`: gloss「一線を引く」で`acceptable`型 3/4、他のglossでは0/4)。→ 解は「中心義を共有する」ではなく、**Adv説明をglossから独立させ、説明call内で用法→中心義を自分で先に決めさせる**(新規call 0、Prompt文言の追記ではなく入出力の構造変更)。
2. **一方で、同じ段で決めた中心義を下流へ固定すると悪化**(E3 46%)。独立した2つの目(Std gloss/Adv説明)の相互訂正を残すこと自体が設計要件。
3. **Std glossの字義/慣用の判定は、Prompt/構造の変更では差し引き0**(G1・G2・過去のA-2)で、モデルの判断力が律速している疑い。ここは**Prompt反復を止め**、上位model・構造の組合せを数値で比較する段階的Trial(gate付き)に切替える(Charter 5の方針転換進言)。

## 1. 推奨案(1案): 「Adv説明の独立化(伝染遮断)+用法先決め」+「Std glossの律速検証(gate付き)」

### 1-1 Adv(推奨の核)— 案A
- **何を変えるか**(いずれも既存の説明call=`er019_family_x_kp_explanation_01.py`内、call数は不変):
  1. 説明callの入力から`japanese_reference_meaning`行(`:174`)を外す。入力=phrase+source_sentence(1文)のみ。
  2. 出力schemaを`usage_type`(literal/figurative/phrasal/term)→`core_sense`(一般形の中心義、記事固有の要素を含めない)→`english_explanation`の順にする(同一call内の順序構造。採用するのは`english_explanation`のみで、下流・TTS・表示・検査の入力は不変)。
  3. 再生成signature(`er019_family_x_audio_production_runner_01.py:1081`)から`japanese_gloss`を外す(gloss変更でAdvが再生成されなくなる=副次的に再生成費用・揺れが減る)。
- **何が変わらないか**: Adv説明Promptの承認済み部分(`explanation_en`仕様文・15語・新規Fact不可・「別文脈でも通じる」)は逐語維持。語数/新規Fact検査、技術retry、Store reuseは不変。
- **失敗を構造的に防ぐ理由**:
  - `draw a line`の「acceptable」型: 原因(gloss「一線を引く」の含意)が入力に存在しないので再発しない(probe-03b: gloss除去で0/4)。
  - A-3 v3の「一般義への逃げ」: 「一般的に」を指示するのでなく、**本文の用法(usage_type)を決めた上で**その用法の中心義を書く。`take the wheel`(E3: 字義に固定→悪化)は、独立判断(E4)で比喩義を2/2取れる。
  - `bring in`: E4は2/2とも字義側(`to take something inside…`)に落ちた。独立判断でも外れる例であり**残存リスク**(Judge sense_okは通過、Fable目視で再確認)。
  - `hold on`: E4 2/2適合(問題なし)。
  - 併記(`A or B`): single 28/28(E0は23/28)。
- **新規LLM call 0**。出力トークン増≈+40/KP(≈+0.001円/KP)。Promptの追加文1行(用法→中心義→説明の順序指示)はschemaの順序を補助するもので、**承認済みB仕様のPrompt文の変更=PROMPT_SHA256変更**に当たる(後述 §4)。

### 1-2 Std glossの律速検証(gate付き)— 案B
RC2 §3-3より、Promptの語句(G1)・用法先決め構造(G2)・過去のA-2は、**差し引きで効かない**。Std側は次の順で測り、効くものだけ採る:
- **B1(構造)**: G2相当(gloss callの出力に`usage_type`と`core_sense_en`を前置。新規call 0、schema追加のみ)。単独採用は見送り(net 0)。**ただしB2と組合せたときの効果は未測定**。
- **B2(model)**: Std glossのみ`gpt-6.1-sol`(既存の承認済みmodel、Family XのB3/R0/R1/R2で使用)。費用試算: 現行gloss 1 call=0.0985円(入力2,719/出力688token、`gloss_alignment_runtime_metadata.json`実測)→ Sol単価(入2.0/出10.0 USD/M)で同token数なら**約1.97円/call**。Std glossは1 call/記事セット → **+約1.9円/セット(70円目標の2.7%)**。Advレベルのgloss(表示用)はlunaのまま。
- **gate**: Stdの字義/逐語NG率が現行(G0)の半分以下かつ`draw a line`=慣用義3/3なら、B2を採否判断へ提示(**Production挙動のmodel変更+費用増=ユーザー判断**)。効かなければ「現行維持」でなく**別の切り口(辞書資産の整備、事前登録型の慣用句glossなど)をユーザーへ進言**し、Closeしない。

### 1-3 最小構成(Charter 1)
**案A(Adv独立化)+A-1(既に採用)**を最小構成の第一候補。A単独でAdvの主因(伝染)は除かれる。Std側は案Bのgateの結果で追加。案Aが検証基準(§6)を満たさなければ、案Aも見送る(手段不採用=目的達成ではない。次はE1/E4の変種、またはAdv説明modelの検討)。

## 2. 代替案と比較表

| 案 | 仕組み | 新規call | 費用差/セット | 実測の効果 | 副作用・リスク | 既存仕様との差分 | 判定 |
|---|---|---|---|---|---|---|---|
| **A(推奨核)** Adv独立化+用法先決め | 説明callからglossを外し、同call内で用法→中心義→説明 | 0 | ≈ -0.00〜+0.003円 | E4: 併記解消(single 28/28)、`draw a line`の`acceptable`0/4、`take the wheel` 2/2比喩 | 独立判断が外れる(`bring in`が字義側、`pull someone under`が曖昧)。Judge pass 19/28 vs E0 22/28(Judge偽陽性が主、要再測定) | B仕様(Prompt逐語、PROMPT_SHA256)変更。Trial-02逐語性testの更新。signatureからgloss除去 | **採用候補**(Trial) |
| B1 Std用法先決め(G2相当) | gloss出力にusage_type/core_sense_enを前置 | 0 | +0.001円 | `draw a line`・`shine a light on`は慣用義側へ。`take the wheel`・`refueling support`は悪化。NG 6/28→7/28 | schema変更(gloss出力、validatorは不変)、downstreamはjapanese_glossのみ使用 | gloss規則(承認)は不変、Prompt追記あり(承認要) | 単独は見送り。B2と組合せのみ再評価 |
| B2 Std glossをSolに | model変更 | 0 | **+約1.9円(+2.7%)** | 未測定(費用上)。字義/慣用判断が律速ならここが効く | コスト増。Production挙動の意味的変更 | routing(`SUPPORT_MODEL`)のStd gloss用途だけ別model化 | **Trial armで実測→ユーザー判断** |
| S 中心義の正本化(gloss callまたはcanon callの出力に`sense`を追加し両下流に渡す) | 1回決めた中心義をStd/Advで共有 | 0 | +0.01円 | **E3: 46% vs E0 79%**。用法判定が外れたKP(`take the wheel`/`Carry the Load`/wallet)で誤りが固定される | canon schema/validator/goldenにも影響。Std/Advの第2の目が消える | canonical item schema拡張(fulltext専用)、Trial-02(別工程)とは違い既存call拡張 | **現modelでは不採用**。Sol等で決定精度が示された場合のみ再検討(Trial armとして1回測定) |
| G gloss Prompt構造化/「全語反映」撤回 | G1=句除去、G2=用法先決め | 0 | 0 | G1: NG率不変(21%→21%)。G2: net 0 | mapping検査(record-only)との整合は問題なし | Prompt変更(承認要) | **不採用**(効果なし。『全語反映』は原因でない) |
| E 説明入力の拡張(全文/前後文) | 1文→全文 | 0 | +0.003円 | **E2: 61%(悪化)** | 記事固有の対象が混入しやすい | B仕様のinput変更 | **不採用** |
| D 決定論補助(慣用句辞書、逐語検知) | 辞書/語対応で警告 | 0 | 0 | 未測定 | **リポジトリに慣用句辞書なし**(整備費大)。語対応辞書も無く「光を当てる」等の正当な直訳を誤検知 | 新検査(原則避ける) | **不採用**(根拠不足) |
| H A-3 v3(説明Prompt追記) | 「中心義1つ」指示 | 0 | 0 | 症状を抑えるが軸上のトレードオフ(sense -4pt)、総合72→73% | 一般義への逃げ(bring in等) | PROMPT_SHA256変更 | ユーザー決定で不採用 |
| N A-1のみ(現状) | 変更なし | 0 | 0 | `draw a line`: Adv 3/4で`acceptable`(glossが一線の場合)、Std 線を引く 2/2 | 目的未達 | — | 目的未達のため終了しない |

## 3. 失敗例が構造的に防がれる理由(各案)

| 失敗例 | 原因(RC2) | 案Aでの扱い | 案Sでの扱い(参考) |
|---|---|---|---|
| A-3 v3の「一般義への逃げ」(`bring in`:本文は『使えるものとして持ち込む』) | 一般義を指示するPromptが本文の用法判定を上書き | 用法判定(usage_type)が先、その用法の中心義を書く。ただし独立判断でも`bring in`はE4で字義側(要検証・残存リスク) | 外れた判定が固定される |
| `letter of introduction`の曖昧化 | 簡潔化の副作用 | E4: 2/2『a letter that introduces someone』等。定義的で曖昧化しない | — |
| `hold on`の薄まり(`to wait for a short time`) | 条件(制止)を落とす | E4 2/2『wait a moment before doing or deciding』 | — |
| `draw a line`のacceptable型 | gloss「一線を引く」の含意の伝染 | **除去**(0/4) | 影響なし |
| `Carry the Load`の字義 | gloss「荷物を運ぶ」の字義が伝染+見出しが比喩 | gloss除去で0/4字義。ただしE4自体は`literal`と判定(2/2)=用法判断は外れ続ける→Stdの律速と同根 | 固定される |

## 4. 既存仕様・過去Trial・承認事項との整合(Charter 8)

- 照合: `CURRENT_SPEC.md:2032`(Adv text仕様=Trial-02 B候補、逐語・15語・新規Fact不可・PROMPT_SHA256)、`TRIAL_RESULT_02.md:72`(一般化LLM工程=REJECTED→既存callで担う)、`er019_family_x_kp_explanation_01.py:54-85,164-178`、`er019_family_x_audio_production_runner_01.py:1077-1091`(signature)、`er003_key_words_gloss_alignment.py:575-612`、`TRIAL_RESULT_01.md` §2・§7、`A3_VERIFICATION_01.md`、`DESIGN_02.md` §3(A-2/A-3)、OPEN-454/458/474/476。
- **案Aは承認済みB仕様の入力・Prompt・schemaの変更**(逐語性・PROMPT_SHA256が変わる)。ただし承認時の目的は「アドバンスの学習者に平易な英語解説を付ける」で、**『日本語参考意味を入力に流す』設計は目的ではなく実装選択**(承認文は`explanation_en`の仕様文を逐語再利用すること)。採用はユーザー判断(VALIDATED後)。
- Trial-02逐語性test(`er041_..._test_01.py`のPROMPT_SHA256固定)は案A採用時に更新が必要(**旧testの反転・撤去対象**)。DefaultOff隔離: Trialは`er112`系のDEV注入のみで、Production moduleのhash開始=終了を記録(委任_02と同じ方式)。
- Std gloss承認規則(平易・直訳調回避・括弧禁止、`b1_p2_keywords_l_prompt_template.txt`抽出)は不変。慣用句の語義選択規則は**新規の品質規則**でありユーザー承認事項(案B1採用時)。
- OPEN-476(bound→bind)・OPEN-475(大文字残り)は対象外。
- 撤去/残置の識別子(採用時の変更案): 撤去=`japanese_reference_meaning`入力行・signatureのgloss項・Trial-02逐語性testの固定SHA。残置=語数/新規Fact検査・技術retry・A-1の全項目。

## 5. 副作用とX/Z

- X/Z共通: 説明callは`er019_family_x_kp_explanation_01`を両Familyが共有(`er026_family_z_fiction_production_runner_01.py:1515,1532`)。Zは物語で固有人名・状況が多く、独立判断の方が記事固有条件の混入を受けにくいと予想(要検証。Zの難例は`pull someone under`・`execution bell`・`letter of introduction`)。
- **Std/Adv整合の構造的保証が弱まる**: gloss→Advの一方向依存を断つので、同じKPでStdとAdvの語義が食い違う可能性は理論上増える。現行でも不整合は7件中2件(RC2/RC1 §3(d))で、A-1後のP判定は100%(n小)。Trialで共有KPのP判定を必須測定とし、不整合があれば**不一致時のみAdv表示glossを同じ用法で再生成する条件付き再整合**(call増は不一致時のみ)を次案とする。
- 費用: 案Aは≈0円/セット。案B2は+約1.9円/セット。

## 6. 検証計画(Trial≤60円、Opus条件Aレビュー後に実装)

### 6-1 検証セット(≥75 KP、重複排除、X/Z)
- 難例20: er112難例(`draw a line, pull someone under, sentence someone to death, shine a light on, reach for someone's wallet, fire the starting gun, Carry the Load, brace yourself for, apply one's findings, refueling support, execution bell, leap into action, take the wheel, bring in, hold on, letter of introduction`)+census逐語gloss境界例(`on the throne`等)から20。X/Zを含める。
- 正常30: census 78 KPから難例を除き層化抽出(X20/Z10、慣用句・句動詞・名詞句・コロケーションを含む)。
- A3_verify新規25(既存run入力あり)。
- 入力はすべて既存run由来のreplay入力(`units_a3verify.json`、`er112 inputs/units.json`、各run `gloss_alignment_prompt.txt`/`canonicalization_prompt.txt`)。**過去Trialの入力・失敗例を再利用**。

### 6-2 arm(各2〜3回、段別再利用でcanonicalizationは共通)
- Adv: **E0**現行 / **E4**案A / **E1**(独立のみ、用法先決めなし)。
- Std gloss: **G0**現行(luna) / **G2**用法先決め(luna) / **G0-sol** / **G2-sol**(Solは難例20 KPのバッチのみ1回、費用制約)。
- 参考: **E3-sol**(Solで決めた中心義を固定する案S)を難例のみ1回(Sol anchorの精度で案Sが復活するかを1回だけ確認)。
- 上記すべてA-1適用後の入力(used_form)で実行。

### 6-3 Judge(基準の修正を先に実施)
- 2系統(`claude-sonnet-5-5`+`gpt-6.1-sol`、いずれも評価用の最新世代)+Fable目視20%抽出。armラベル非開示。生成はProduction同一`gpt-6-luna`(Std Solアームは評価対象)。
- **`core`基準の修正**: 『表現そのものが持つ意味(定義)に含まれる語(例: refueling supportのfuel、execution bellのexecution)』は混入に数えず、『表現に含まれない、記事の対象・目的・場面・評価条件(例: research、vehicles、what is acceptable)』のみ混入と数える。例示付きで、RC2 §3-2で偽陽性だった行(E0/E4不合格の約半数)を再判定してキャリブレーション。
- 追加項目: `over_general`(本文の用法から外れた一般義)、`literal`(逐語・字義、OF-07定義)。
- Std/Adv整合(P): 共有KPで2者判定。

### 6-4 成功基準(数値、方向判断+信頼区間を併記)
| # | 項目 | 基準 |
|---|---|---|
| 1 | 本文での意味一致(sense_ok 2者) | ≥ 現行(E0/G0、同条件再測定)かつ ≥ 90% |
| 2 | 記事固有条件の混入(core、修正基準) | ≤ 5% |
| 3 | 過度限定(narrow)・過度一般化(over_general) | 各 ≤ 5% |
| 4 | Std/Adv整合(共有KP) | 100%(不一致は条件付き再整合の要否を判定) |
| 5 | 正常KPの非劣化(現行で合格だったKPが新armでも合格) | ≥ 95% |
| 6 | `draw a line` | Std慣用義3/3(字義の「線を引く」でない)、Adv中心義3/3(`acceptable`系0) |
| 7 | 逐語・字義gloss(OF-07定義、難例) | ≤ 10%、かつG0比で半減以下(B2採否のgate) |
| 8 | 併記(single) | ≥ 95% |
| 9 | X/Z双方で1〜8成立 | 必須 |

### 6-5 ユーザー検証項目1〜6への対応
1)`draw a line` Std = 基準6+Fable目視 / 2)同KPのAdv = 基準1・2・6 / 3)他の慣用句・句動詞・一般表現 = 検証セット全体 / 4)既に正しい説明を壊さない = 基準5 / 5)X/Z = 基準9 / 6)retry/fallbackを含む量産条件 = 下記。

### 6-6 量産条件(retry/fallback)の確認計画
- Trial中: 説明callの語数>15・新規Fact・parse失敗のretry経路をmock注入で通し、schemaの順序(usage_type→core_sense→explanation)が壊れても`english_explanation`のみ採用すること、retry後も不合格時の最終成果物(NG記録・HR)が現行と同じ形であることをDefaultOffIsolation型testで確認。
- 採用後(別委任): X2記事+Z1作品の正式経路(text工程のみ=TTSなし、各≈3〜5円)でgloss/explanationのretry発動・HR・Store reuse・signature再生成の実run確認(A-1配線と同時)。

### 6-7 費用見積(≤60円)
| 段 | 内容 | 見積 |
|---|---|---|
| Std gloss luna 2 arm×2〜3 rep×約25 unit | 約0.09円/unit-call | 9〜14円 |
| Std gloss Sol 2 arm×難例8 unit×1 rep | 約2円/call | 約32円 → **8 unit以下に限定(約16円)** |
| Adv説明 3 arm×2〜3 rep×25 unit | 約0.03円/call | 4〜6円 |
| 案S-sol(参考)難例のみ | 約2円×4 unit | 約8円(gateで省略可) |
| Judge(2系統、変化行のみ、約300行) | 約0.06円/行/系統 | 約25〜30円 |
| 合計 | | **約55〜60円**(段階gateで未実施段を省略) |
段階gate: Stage1(Std lunaアーム+Sol難例+Adv E0/E4、≈25〜30円)→結果で案S-sol・追加repを実施/省略。超過見込みなら開始前に停止。

## 7. Opus論点(条件A: 工程出力の構造変更)
`OPUS_REVIEW_REQUEST_03.md`に詳細。要点: (1)因果の読み(gloss伝染)の十分性、(2)独立性とStd/Adv整合のトレードオフ(条件付き再整合の要否)、(3)E3悪化の解釈(独立性 vs 用法判断精度)とSol anchor再検討の妥当性、(4)Judge基準修正の妥当性とキャリブレーション手順、(5)B仕様(PROMPT_SHA256・Trial-02逐語性)変更の扱い、(6)Std側の「Prompt反復停止→model律速検証」への方針転換の妥当性とコスト、(7)統計(n・rep)。

## 8. 失敗終了時の最終成果物(Charter)
Trial失敗/STOP時は、DEV結果ディレクトリ(`er112_output/kp_gm_trial_02/`予定)と`ITERATION_LOG`に生成物・Judge・費用台帳が残り、Production成果物・記事B成果物は無変更(現状維持)。ただし**目的(Key Phrase意味・説明品質)は未達のまま**でありCloseしない。
