# FICTION-STORY-DNA-E-AXIS-REDESIGN-01_REPORT.md

管理ID: FICTION-STORY-DNA-E-AXIS-REDESIGN-01
Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
到達上限: VALIDATED(Production採用は本タスクの対象外)。

## §1 目的

前回Trial(FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01)は、Prompt Bias
(共通developer message/promptの世界設定列挙)を除去した結果、E軸を持たない
Run(Run2)は技術的記憶ギミックから離脱したが、E軸にFuture/技術系の値を
持つRun(Run1/4/5)は依然として「記憶技術が暴力(殺人)を予告する」という
同一の物語エンジンへ収束したままだった(旧REPORT §9)。

本Trialは、**Story DNA設計(5軸・2-3軸・seed・Run5 Coverageの仕組み・4共通
原則・語数280-420・Bias除去済みPrompt文言)は一切変更せず**、ユーザー決定済み
の新E軸(6値: contemporary everyday reality / realistic but socially unusual
situation / realistic but emotionally unusual situation / future / reality
with one changed rule / supernatural or fantastical world)へ**E軸の値
リストだけ**差し替え、同一seed(seed_base=20260925、Run毎に+1で
20260926〜20260930)で5 Run再生成し、(A)E軸の偏り、(B)殺人・死の描写
との対応を観察した。

## §2 新E軸反映内容(差分逐語、Coverage暫定判断)

`er018_fiction_core_provocation_prompt_bias_retrial_01.py`をコピーし
`er018_fiction_story_dna_e_axis_redesign_01.py`を作成、`diff`で確認した
変更箇所は以下のみ(コメント・管理ID表記・出力パスの表記変更を除く、
実行時の挙動に影響する変更点)。

1. **`AXIS_DEFS["E"]["values"]`**(6値、旧→新、全置換)
   - 旧: `contemporary everyday life` / `a near future` / `a greatly
     changed future` / `a world with technology or institutions that do
     not exist in reality` / `a supernatural or fantastical world` /
     `a world almost identical to reality except one rule is different`
   - 新: `contemporary everyday reality` / `realistic but socially
     unusual situation` / `realistic but emotionally unusual situation`
     / `future` / `reality with one changed rule` / `supernatural /
     fantastical world`(日本語ラベル併記、逐語は
     `er018_fiction_story_dna_e_axis_redesign_01.py`参照)。
2. **`E_FUTURE_VALUE_INDICES`**(Run5 Coverage Run用の母集団index)
   - 旧: `[1, 2, 3]`(旧E軸のFuture系3値)
   - 新: `[3]`(新E軸の`future`1値のみ)

それ以外(A/B/C/D軸の値、`select_dna()`の2-3軸抽選ロジック、seed生成式、
`COMMON_PRINCIPLES`、`DNA_BLOCK_TEMPLATE`、Core Provocation/Writer各
developer message・prompt template・語数280-420・schema)は逐語のまま
変更していない(diff全文は本タスクの作業ログで確認済み、git diffでも
再確認可能)。

**Coverage Runの母集団対応は設計判断が必要だった(委任文の指示どおり判断
せず2案を記録)**。詳細は
`er018_output/fiction_story_dna_e_axis_redesign_01/e_axis_redesign_notes.md`
に記録。要約:
- (a) `future`の1値のみに対応(**実行**): 旧仕様の呼称「Future Coverage
  Run」の字義に最も近く、追加解釈が最小。ただしRun5のE値が常に`future`
  固定になり、旧仕様が持っていた「Future系3値からランダム選択する多様性」
  は失われる(暫定判断、REPORT本節に明記)。
- (b) 非現実系3値(future/one changed rule/supernatural、index[3,4,5])に
  対応: 旧Future系3値の「非現実的」という共通点を継承し多様性を維持できる
  が、「非現実系」という新しい分類基準を追加することになる。
- **USER_DECISION_REQUIRED該当性の判断**: 上記は値リストの対応関係のみの
  選択であり、新しい安全制約や仕様追加を伴わないため、本Trialでは
  USER_DECISION_REQUIREDへ格上げせず暫定(a)で実行した。ただしRun5の
  多様性喪失は将来のCoverage Run設計見直しの検討材料として§9で報告する。

## §3 DNA差分(旧→新)

乾式(APIコールなし)`--step dna --seed-base 20260925`を実行し、前回
`dna_log.json`と比較した(詳細は
`er018_output/fiction_story_dna_e_axis_redesign_01/dna_diff.md`)。

- **Run2(E軸を持たない)**: axes/values ともに旧新で完全一致(byte単位)。
  E軸の値リスト変更の影響を受けないことを確認。
- **Run1/3/4(E軸を持つ、非Coverage)**: 選択されるE軸の**index**は旧新で
  完全一致(Run1=index1、Run3=index4、Run4=index3)。値リストが旧新とも
  6要素のため`rng.randrange(6)`の返り値が同一になり、**値のラベルだけが
  新E軸に置き換わった**(A/B/C/D軸の値・k(軸数)・他軸の選択も全Run完全
  一致)。
- **Run5(Coverage Run)**: E軸自体は今回のseedでは新旧ともindex3相当の値
  (旧=technology-institution world、新=future)になったが、Coverage母集団
  リストの長さを3→1に変更した副作用で、Python標準乱数の内部状態消費量が
  変わり、**後続のC/D軸の値が変化した**(旧: C=a reversal, D=a hospital
  → 新: C=a loss, D=a public space)。E軸強制の仕組み自体(コードパス)は
  変更していないが、リスト長の変更に伴う想定内の副作用であり、
  e_axis_redesign_notes.mdに機序を記録した。

## §4 各Run(DNA/候補/選択/Story全文)

全文は`er018_output/fiction_story_dna_e_axis_redesign_01/stories_all.md`
(DNA・候補・選択理由・Story本文)。ブラインド版は同dirの`blind.md`+
`blind_key.json`(Fableのブラインド評価用、`Story-P`〜`Story-T`のマッピング
はRun5/4/3/2/1)。要約は以下。

| Run | DNA(選択軸) | タイトル | 概要 |
|---|---|---|---|
| 1 | A=strangers, E=realistic-socially-unusual | The Brass Key | 認知症の依頼人が娘役の女性に鍵を託し、語る「重大な過ち」の内容が思い出す度に変わる |
| 2 | C=a secret, D=school(E軸なし) | The Memory Test | クラス全員が同じ嘘の証言を暗記させられていた教室の謎、記憶テストが真実を呼び起こす |
| 3 | A=colleagues, B=bittersweet, E=reality-one-changed-rule | The Memory She Left Behind | 記憶を譲渡すると渡した側は永遠に忘れるルールの世界、退職前の同僚が友情の記憶と引き換えに安全報告書改ざんの証拠を託す |
| 4 | C=an exchange, D=a workplace, E=future | The Memory Trade | 記憶で給料を払う未来の会社、ロボット事故の記憶を交換した新人が「まだ起きていない事故」を巡り同僚と対峙 |
| 5(Coverage) | C=a loss, D=a public space, E=future | The Borrowed Memory | 未来の駅で他人の記憶を借りられる世界、亡き娘の記憶を見知らぬ男に借りられた母親が返却前に取り戻そうと追う |

## §5 目的A結果(E値分布、現実系/非現実系の分散)

**分類基準**(`retrial_design.md`で事前固定): 現実系=index0-2(contemporary
/ socially unusual / emotionally unusual)またはE軸なし、非現実系=index3-5
(future / one changed rule / supernatural)。

- **DNA上のE値分布**(E軸を持つRun1/3/4/5、4件中): 現実系1件(Run1=socially
  unusual)、非現実系3件(Run3=one changed rule、Run4=future、Run5(Coverage)
  =future)。E軸なし1件(Run2)。
- **実際に書かれたStoryの世界観**: DNA指定とほぼ一致した。Run1(現実系
  DNA)→完全に現代の日常設定。Run3(one changed rule DNA)→「記憶を渡すと
  渡した側が忘れる」という1ルールのみ変えた現実的職場ドラマ、DNAと厳密に
  一致。Run4/5(future DNA)→未来の企業経済・未来の駅、DNAと一致。
  **Run2(E軸なし)は、旧Trialでは技術的記憶ロッカーという設定を自発的に
  補っていたが、新Trialでは「記憶テスト」「机の下の少女」という、技術も
  未来も明示しない、やや不可解な(ただし現実世界に近い)設定にとどまった**
  (完全に現実的とは言い切れないが、明示的な超自然/技術要素はない)。
- Core Provocation候補14案の世界観は概ねDNAのE軸設定を踏襲しており、DNAで
  指定されていない要素(魔法・宇宙・怪物等)への逸脱はなかった。

## §6 目的B結果(殺人/死タグ表、観察のみ)

詳細な全タグ表は
`er018_output/fiction_story_dna_e_axis_redesign_01/violence_death_tags.md`
(候補14案+Story5本、新Trial・旧Trイアル両方)。要点:

- **選択されたCore Provocation候補5案(chosen_index)のうち、`violence:
  killing`タグは0/5**(旧Trialは3/5: Run1/4/5)。
- **Story本文5本のうち、`violence: killing`は0/5**(旧Trialは3/5)。
- ただし`killing`タグの候補自体が消えたわけではない。新Trial候補14案中
  1件(Run4候補1「office murderの記憶」)は`killing`/`death_role:中心`
  タグだったが、選ばれなかった(chosen_index=0の「事故の濡れ衣」候補が
  選ばれた)。**観察: 旧Trialでは`killing`候補が選ばれやすかったが、新
  Trialでは同種の候補が生成されても選ばれなかった。因果は断定しない**
  (母集団14案 vs 13案、単一Trialのサンプルであり統計的検定はできない)。
- `death_role: 背景`(死が前提設定だが中心の謎ではない)は新旧とも1/5
  Story(新Run5=亡き娘、旧Run3=亡き母)で変化なし。
- `why_interesting`/`reason_for_choice`中の"tension"/"danger"の出現は
  新Trial候補14件+reason5件中、tension3件・danger5件。"kill"/"death"/
  "threat"の文字列自体は一度も出現しなかった(要約文の語彙と、実際の
  本文内容が持つviolence/death_roleタグは独立している)。

## §7 前回Trialとの比較(発想タイプ数、収束、題名/人物名反復)

- **発想タイプ数**: 新Trial5本は、(1)認知症/矛盾する回想の人間ドラマ
  (Run1)、(2)集団的な虚偽記憶の解除ミステリー(Run2)、(3)記憶譲渡ルール+
  職場不正の隠蔽告発(Run3)、(4)記憶経済の未来職場+事故の因果逆転(Run4)、
  (5)記憶貸し借りの未来+悲嘆(Run5)の**5種、実質的な重複なし**。旧Trial
  (Bias除去後)は前回REPORT §9のFable評価で「4種(P/T同型、Q、R、S)」
  (Run1とRun5が同型)だった。**Sonnet参考評価としては、新Trialは旧Trial
  より収束が弱いと観察される**(最終判断はFable/ユーザー)。
- **TF-IDF類似度**(機械参考指標、`similarity_matrix.json`): 新Trial5本間の
  最大値はRun1×Run5=0.587(非対角の中で最高)。旧Trial5本間の最大値は
  old_run4×old_run2=0.504。数値だけを見ると新Trialの方がやや高いペアが
  ある(Run1×Run5)が、TF-IDFは表層の語彙類似度であり物語の型の違いを
  直接反映しない(旧REPORT §7と同じ限界)。Run1×Run5がやや高いのは両者
  とも主人公名"Mara"・"Memory"関連語を共有するため(語彙面、内容面では
  Run1=人間ドラマ、Run5=未来SFで型は異なる)。
- **題名重複**: 新Trial5本のタイトルは全て異なる(The Brass Key / The
  Memory Test / The Memory She Left Behind / The Memory Trade / The
  Borrowed Memory)。旧Trialは"The Last Memory"がRun1/Run3で重複していた。
  **改善**(完全な重複は解消)。ただし新Trialも5本中3本のタイトルに
  "Memory"の語を含み、語彙レベルでの均質さは残る。
- **人物名反復**: 新Trial内で主人公名が2組重複した: **"Mara"**(Run1・
  Run5)、**"Mina"**(Run2・Run4)。旧Trialは5本の主人公名(Daniel/Lena/
  Eli/(無名)/Mara)に重複なし。**新Trialでは旧Trialになかった名前反復が
  新たに発生した**(観察、原因不明。DNA・Prompt・E軸の値には主人公名に
  関する指定は一切ないため、モデル側の自然なばらつきと考えられる)。
  なお"Mara"は旧Trial Run5の主人公名とも一致しており(cross-trial観察)、
  Prompt/DNAに起因しない、テーマ"memory"と相性の良い名前へのモデルの
  偏りである可能性がある(因果断定なし)。

## §8 QCD(cost・時間・失敗)

- **Cost**: 実績¥4.69(10 call、`gpt-5.6-luna`、record_count=10)。上限¥15
  に対し余裕あり。前回実績(Bias除去Trial)¥4.69と完全同水準。詳細:
  `er018_output/fiction_story_dna_e_axis_redesign_01/cost.json`・
  `raw_usage_log.jsonl`。
- **失敗・リトライ**: 全10 call(Core Provocation 5 + Story 5)とも初回
  attemptで成功、リトライ発生なし(各`runs/runN/api_meta.json`の
  `attempts`が`[{"attempt": 1, "success": true}]`のみ)。
- **語数**: 418/376/462/430/393語(目標350語、許容280-420語)。Run3のみ
  462語で上限420語を42語超過(「roughly」の範囲内という前回の扱いを踏襲
  するが、超過幅は前回Run2の+14語より大きい。次回の参考としてQCDに記録)。
- **所要時間**: dna/generate/analyze/assembleの4 stepを通しで実行、API
  呼び出し自体は数分で完了(タイムアウトなし、generate stepはバックグラウンド
  実行で完走を確認)。

## §9 Sonnet仮分類

**REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれか、最大VALIDATED**:

**暫定: VALIDATED**(Sonnet参考評価、最終判断はFable/ユーザー)。

根拠:
1. E軸の値リスト差し替えは委任どおり実施でき、A/B/C/D軸・抽選ロジック・
   seed・語数・Bias除去済みPrompt文言は完全に不変であることを確認した
   (§2・§3)。STOP条件(Story DNA変更・新軸追加・殺人禁止等の新制約導入の
   必要性)は発生しなかった。
2. 目的A(E軸偏り): DNA上のE値・実際のStory世界観ともにE軸の指定と概ね
   一致し、新E軸の6値は意味的に重複なく機能した(§5)。
3. 目的B(殺人/死): 選択されたCore Provocation候補・Story本文ともに
   `killing`タグが旧Trial3/5→新Trial0/5へ減少した(§6)。ただし
   `killing`候補自体は生成され続けており(Run4候補1)、「生成されなく
   なった」のではなく「選ばれなくなった」という違いである。母集団が
   小さい(候補14件、Story5本)単発Trialであり、統計的な断定はできない。
4. 発想タイプの重複は旧Trial(4種、Run1≈Run5同型)から新Trial(5種、重複
   なし)へ改善したと観察されるが、代わりに**旧Trialになかった人物名反復
   (Mara×2、Mina×2)が新たに発生した**(§7)。これは新しい種類の反復であり、
   完全な多様性達成とは言えない。
5. **Coverage Run(Run5)の設計判断**(§2)は暫定(a)で実行した。この結果、
   Run5のE値は今後常に`future`固定となり、旧仕様が持っていた「Future系
   複数値からのランダム選択」という多様性の仕組みは実質的に失われている。
   これは新しい安全制約の追加ではないため本Trial内ではUSER_DECISION_
   REQUIREDへ格上げしなかったが、**Coverage Runの設計そのものを見直すか
   どうかはユーザー判断が必要な事項として明示的に報告する**(下記)。

**USER_DECISION_REQUIRED候補(Production化ではなく、次のTrial設計に関する
論点)**: Run5 Coverage Runが新E軸のもとで常に`future`固定になり多様性を
失っている点について、(a)このまま`future`固定を維持する、(b)非現実系3値
(future/one changed rule/supernatural)からランダム選択する設計に変更する、
のどちらを採用するかはユーザー/Fable判断を仰ぐ。本Trial自体はこの論点の
有無に関わらずVALIDATEDの範囲で完了しており、Production変更は伴わない。

## §10 Fable評価

[Fable記入]

## §11 分類

[Fable記入]
