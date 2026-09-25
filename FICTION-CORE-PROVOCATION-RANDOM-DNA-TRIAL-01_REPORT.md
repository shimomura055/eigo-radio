# FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01 REPORT

Trial専用。Production採用ではない。最大到達Status: `VALIDATED`。
SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)は無変更。

実装: `er018_fiction_core_provocation_random_dna_trial_01.py`
出力: `er018_output/fiction_core_provocation_random_dna_trial_01/`

---

## §1 条件・Prompt全文・旧Futureからの差分

- 流用元(旧Future、Trial-08相当): `er013_family_c_future_provocation_08.py`
  (Core Provocation Prompt/schema)、`er013_family_c_future_writer_08.py`
  (Story Writer Prompt)、`er013_family_c_future_trial_08_run.py`(呼び出し
  流儀: `client.responses.create`、`routing.require_model_or_override`、
  `er005_cost_logger.logging_context`)。特定方法: `Grep "Core Provocation|
  core_provocation|imagined-future|about the future" -i` で56ファイルを
  検出、直近のFuture Trialである`family_c_future_trial_08`系を最終流用元に
  選定(Trial-08は「1-3案+選定をLLM1回」「低制約Writer」という設計が
  委任文の「旧Futureの良点」と最も一致するため)。
- Future限定語句の置換(語句レベル): "'Future' article family" →
  "Fiction article family"、"imagined-future story" →
  "fiction story ... regardless of whether the story takes place in the real
  world, the future, an unreal/fantastical setting, or an imagined/speculative
  world"、"feel the future" → "feel something"、"a vivid imagined future
  scene" → "a vivid scene ... The setting can be realistic, near-future,
  far-future, or entirely unreal/speculative"。全文は
  `er018_output/.../prompt_diff_provocation.md`と
  `er018_output/.../prompt_diff_writer.md`に逐語記録。
- **構造的な削除(語句置換を超える判断、Fable/ユーザー確認事項)**: Story
  Writer PromptからCURRENT FACT禁止ブロック([[FACT]]系マーカーの概念は
  そもそも渡していない)と`[[IMAGINED: timeframe]]...[[/IMAGINED]]`マーカー
  必須化ブロックを削除した。理由: この2つはFuture family固有の技術的
  安全機構(現在事実と想像上の未来の混同防止)であり、Fictionへ拡張すると
  (E軸に「現代の日常」「超自然・幻想的な世界」等、必ずしも「未来」でない
  設定を含むため)単純な語句置換では意味が成立しない。委任文の実装範囲
  (10 call予算、Fact Safety層なし、マーカー再試行機構なし)からもこの
  削除は前提とされていたと判断したが、これは「Future限定語句のみ置換する」
  という委任文の原則を厳密に超える判断であるため、そのまま報告する
  (詳細根拠: `prompt_diff_writer.md`)。
- 維持したブロック(Future限定語句を含まないため逐語のまま): Characters
  制約(基本1-2人・最大3人、主人公のみ固有名可)、Listening-friendliness
  段落、「固定構造を強制しない」という指示("Do not follow any fixed
  structure...")。v8には「テンプレート構造を強制する」指示は元々存在せず、
  委任文が想定した「残す/外すの判断」対象は実質無かった。
- 新規追加(委任文の逐語): `[Story DNA -- a creative nudge, not a contract]`
  ブロック、`[Common principles for this story family]`ブロック(両Prompt
  共通)。
- モデル/effort: `gpt-5.6-luna`(Model Routing Contract `A2_WRITER`を
  override_reason付きで転用)。Core Provocation effort=`medium`、
  Story effort=`high`。
- Memory記事(旧Future比較用)の特定: `Glob **/*memory*`は無関係ファイル
  (mfa_tool/venv内)が大量にヒットしたため、`er013_output/**/memory*/**`へ
  絞り込み。採用した2件(パス+sha256):
  - `er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`
    (sha256=`a9a646a798bfe44b632038c790d58680a3b278979ac39473339cace2733b2ea2`、
    旧Trial-08そのままのFuture記事、384語)
  - `er013_output/family_c_episode_trial_10/memory_a2/article_normalized.txt`
    (sha256=`c973802df02a0daae760d65169e9576272b240a6ea9ff17a0b9646bfc8e5cefc`、
    上記を量産パイプラインでさらに調整した版、384語。参考として追加で
    類似度計算に含めた、事前指定外Read)

## §2 Story DNA定義と乱数方式

5軸定義(A関係性/B感情トーン/C中心ドラマ/D舞台/E世界設定)は委任文の逐語を
コード内`AXIS_DEFS`へ日英併記で実装。乱数方式: `random.Random(seed)`
(seed=`--seed-base`(既定20260925)+run番号、Run1=20260926〜Run5=20260930)。
通常run: `k=rng.choice([2,3])`→`axes=sorted(rng.sample(全5軸, k))`→各軸
`rng.randrange(len(values))`で1値選択。Run5(Future Coverage Run):
E軸を必須で含め、Eの値は`rng.choice([1,2,3])`でFuture系3値(少し先の未来/
大きく変わった未来/現実にはない技術・制度がある世界)のみから選択、残り
(k-1)軸はA/B/C/Dから通常どおり選択。全て決定的(同一seedで再実行すれば
同一結果、`dna_log.json`に記録)。

## §3-§7 Run1〜5

(Story全文は`er018_output/.../stories_all.md`、Prompt全文は各run配下の
`provocation_prompt.txt`/`story_prompt.txt`、候補全文は`provocation.json`
参照。以下は要約。)

### Run1(seed=20260926、通常run、軸=A,E)
DNA: Relationship=strangers/見知らぬ人、World=a near future/少し先の未来。
候補3案(すべて「記憶売買/記憶ストレージ+犯罪の予兆」系)。選択: 「見知らぬ男が
記憶を24時間預け、開けると自分が明日彼を殺す記憶が入っていた」。word_count=399。
Story: 「The Memory for Tomorrow」。近未来の記憶ストレージ技術、見知らぬ人との
緊迫した1対1構図、自己成就予言を回避できるかのサスペンス。ラストは殺人を回避し
解決(ただし「見せたのか、作ったのか」で余韻を残す)。
**DNAの効き方**: 「見知らぬ人」関係性が「動機の分からない他人からの依頼」という
緊張を生み、「少し先の未来」が技術設定に自然な説得力を与えている。ただし
「記憶技術が犯罪/死を予兆する」という核の仕掛けはDNAから直接導かれたものではない。

### Run2(seed=20260927、通常run、軸=C,D)
DNA: Central drama=a secret/秘密、Setting=school/学校。候補3案(消えた生徒の
記憶/秘密の記憶消去/明日の日付の告白録音)。選択: 「学校のロッカーに、明日の
日付で『行方不明の教師を隠した』という自分の告白録音が入っていた」。
word_count=373。Story題名は**Run1と一文字違わず同一の「The Memory for
Tomorrow」**(後述§9で指摘)。学校という舞台、教師を守るミステリー、
「予言に従うことで予言が成立する」因果ループ。暴力描写はなくRun1より
「守る」方向の緊張。
**DNAの効き方**: 「秘密」が告白録音というギミックと自然に結び付き、「学校」が
舞台・関係性(生徒/教師)を規定している点は明確。ただし核となる
「未来日付の記憶メディア」という仕掛けはRun1と酷似(§9)。

### Run3(seed=20260928、通常run、軸=A,B,E)
DNA: Relationship=colleagues/同僚、Emotional tone=bittersweet/切ない、
World=a supernatural or fantastical world/超自然・幻想的な世界。候補3案
(盗まれた友情の記憶/死の予知+記憶破壊/記録から消える同僚)。選択: 「超自然の
図書館で、同僚が全ての記録から消え、証明しようとするたびに自分の記憶も
消えていく」。word_count=399。Story題名「The Empty Chair」。**5本中唯一、
殺人・犯罪の要素が一切ない**。喪失と記憶の関係を静かに描く、切ないトーンの
話。
**DNAの効き方**: 「同僚」「切ない」「超自然」の3軸が最も明確にStoryへ
反映されている(同僚という距離感の近すぎない関係、悲しくも温かい結末、
超自然的なルール)。5本の中で最も「DNAが効いた」run。

### Run4(seed=20260929、通常run、軸=C,D,E)
DNA: Central drama=an exchange/交換、Setting=a workplace/職場、
World=技術/制度がある世界。候補3案(全て記憶の売買/交換+死亡事故/失踪した
創業者)。選択: 「シフト交換のために記憶を交換した同僚2人が、翌朝同じ殺人現場を
記憶しているが、互いが相手が凶器を持っていたと記憶している」。word_count=384。
Story題名「The Memory Shift」。職場、two-hander(相互告発)構図、未解決の
まま終わるクリフハンガー。
**DNAの効き方**: 「交換」が記憶交換システムに直結し、「職場」が舞台・関係性
(同僚)を規定している。ただし核の仕掛け(記憶技術+殺人現場の食い違い)は
Run1のバリエーションに近い(§9)。

### Run5(seed=20260930、Future Coverage Run、軸=C,D,E[Future固定])
DNA: Central drama=a reversal/逆転、Setting=a hospital/病院、
World=a world with technology or institutions that do not exist in
reality/現実にはない技術・制度がある世界(Future系3値から選択)。候補3案
(記憶移植+殺人容疑の反転/記憶消去+医療事故の隠蔽/昏睡患者の未来からの
警告)。選択: 「昏睡患者の記録が、目覚める瞬間と『目覚める前に殺されるべき
家族』を予告し、目覚めた本人は『これは記憶ではなく未来からのメッセージ』と
主張する」。word_count=349。Story題名「The Memory Before」。病院という舞台、
家族関係、最後は弟が不穏に微笑み「I remember tomorrow」で締める、ホラー寄りの
反転。
**DNAの効き方**: 「逆転」が「記憶に見えたものが実は未来からの指令だった」
という核の反転に直結している。「病院」が舞台・家族関係を規定。Future系
制約(E軸)は「現実にはない技術・制度がある世界」を素直に「特殊な病院の
記憶記録制度」として自然に受け止めており、Future Coverage Runとして
Future設定はFiction化後も違和感なく成立している(詳細§10)。

## §8 機械参考指標

各Runの語数/文数/固有名詞数(参考ヒューリスティック、文頭語を除外した大文字
始まり語の異なり数。厳密なNLPではなく誤検出を含む[the/at/then等の記号的
大文字化も一部拾う])、時制参考カウントは
`er018_output/.../machine_metrics_summary.json`。語数: Run1=399/Run2=373/
Run3=399/Run4=384/Run5=349(全run 280-420語の目安内)。

**固有名詞(プロタゴニスト名)の収束**: Run1=Mara、Run2=**Maya**、Run3=Lina、
Run4=**Mara**、Run5=**Mara**。5本中3本が独立したAPI呼び出しにもかかわらず
一字一句同じ名前「Mara」を選び、Run2も一文字違いの「Maya」(Run3の
「Lina」のみ明確に異なる)。

**TF-IDFコサイン類似度**(標準ライブラリ簡易実装、`similarity_matrix.json`):

| | run1 | run2 | run3 | run4 | run5 | ref_t08 | ref_ep10 |
|---|---|---|---|---|---|---|---|
| run1 | 1.00 | 0.51 | 0.48 | 0.61 | 0.56 | 0.57 | 0.57 |
| run2 | 0.51 | 1.00 | 0.43 | 0.50 | 0.43 | 0.50 | 0.50 |
| run3 | 0.48 | 0.43 | 1.00 | 0.53 | 0.39 | 0.59 | 0.59 |
| run4 | 0.61 | 0.50 | 0.53 | 1.00 | 0.49 | 0.56 | 0.56 |
| run5 | 0.56 | 0.43 | 0.39 | 0.49 | 1.00 | 0.52 | 0.49 |

run1-run4間(0.61)が5本間で最も高く、run3-run5間(0.39)が最も低い。旧Future
Memory記事(ref_t08/ref_ep10、両者は同一記事の異版でcos=0.99)との類似度は
0.39〜0.59のレンジで、Run3が最も近い(0.59)。**TF-IDF(語彙表層の一致)は
「同じ語彙を使ったか」の指標であり、後述の「同じプロット仕掛けを使ったか」
という構造的収束(§9)を直接には捉えていない点に注意**(0.4〜0.6程度は
語彙レベルでは「ある程度似ているが別物」の範囲に見えるが、実際にはRun1/2/4/5
は核となる仕掛けがほぼ同一)。

## §9 5本の違いの超サマリ・収束箇所

**超サマリ**: DNAで指定した表層(関係性・舞台・トーン・世界設定)は5本とも
明確に異なる形でStoryへ反映されている。しかし**核となる物語の仕掛け
(dramatic engine)は5本中4本(Run1/2/4/5)が実質的に同一パターンに収束した**:
「記憶を記録・保存・交換・再生する技術が、まだ起きていない出来事(殺人/
失踪/危害)を『予告』または『証拠』として示し、登場人物がそれが予言か・罠か・
自ら成立させてしまったものかを疑いながら対処する」というサスペンス構造。
Run3のみ、この「予告される暴力/犯罪」という核から離れ、記憶の消失と喪失を
めぐる静かな話になった。

**収束の具体的な証拠**:
1. **タイトルの完全一致**: Run1とRun2のStory題名が一文字違わず同一
   (「The Memory for Tomorrow」)。
2. **主人公名の反復**: 5本中3本(Run1/4/5)が独立呼び出しにもかかわらず
   同名「Mara」、Run2も酷似する「Maya」(§8)。
3. **候補案レベルでの収束**: 実際にStoryへ選ばれなかった候補(各Run 2-3件、
   計15件中12件)を確認したところ、**ほぼ全ての候補が「記憶=証拠/凶器/
   財産」「記憶の消去・売買が人間関係の危機を招く」「人が記録から消える」の
   いずれかのバリエーション**であった(例: Run1候補[1]は「購入した記憶が
   殺人の目撃証言だった」、Run4候補[1]は「売った記憶が致命的な事故の証拠に
   なる」、Run5候補[0][1]は「記憶移植による殺人容疑の反転」「医療事故の
   隠蔽」)。これはDNAで軸を変えても、Core Provocation生成という
   ブレインストーミング段階自体が、Theme=memoryに対して
   「記憶技術×死/犯罪/喪失」という同じ引力に収束しやすいことを示唆する
   (DNAナッジがブレインストーミングの出発点を大きく動かせていない)。
4. Run3のみ、候補3案とも「消える/失われる」系だが犯罪・死の要素を伴わない
   点で他4本と質的に異なる(唯一の明確な逸脱)。

**それでも残る違い**: 舞台・関係性・語彙(TF-IDF 0.39-0.61)・結末のトーン
(Run1=緊張から解決、Run2=保護と因果ループ、Run3=喪失の受容、Run4=未解決の
相互告発、Run5=不穏な反転)には実質的な違いがある。読者が「表面的には別の
状況」と感じる可能性はあるが、「核の仕掛けそのものが別物」とまでは言えない、
というのが今回のSonnet参考評価の実態把握である。

## §10 Future Coverage Run(Run5)評価

Run5はFuture系E軸(「現実にはない技術・制度がある世界」)を強制した上で
生成されたが、結果は「病院の特殊な記憶記録制度」という設定として自然に
機能しており、Future限定を外した後もFuture的な設定がFictionの一種として
違和感なく選べることを確認できた(Future機能のFiction内での後方互換性は
成立している、という点ではCoverage Runの目的を達成)。ただし上記§9の
収束傾向どおり、Run5もRun1/2/4と同じ「記憶技術が予告する暴力」という
核の仕掛けを共有しており、Future設定であること自体が「別のテイスト」を
保証してはいない。

## §11 改善案(提案のみ、実装しない)

- Theme以外の軸(例: 別テーマでの追試)で収束傾向が本当にTheme=memory固有か
  DNA方式一般の問題かを切り分ける。
- Core Provocation生成のdeveloper messageに「暴力・死・犯罪を核に据えた
  premiseを候補の中心にしすぎない」という多様性方向の緩い指示を足す余地が
  あるかもしれない(ただし本Trialでは実装しない)。
- Central Drama軸(C)を「nudge」ではなく、より強く縛る指示に変える余地の
  検討(未実装、上記と同様)。
- 5本より多いサンプル数で収束の統計的評価を行う余地(未実装)。
(いずれも提案のみであり、STOP条件により本Trial内では実装しない。)

## §12 cost・model実値

- 総額: **¥4.45**($0.027815、USD_JPY=160換算、上限¥30の約15%)。
  `er018_output/.../cost.json`。
- record_count=10(5 run × 2 call)。**再試行(retry)は0件**(全10 call、
  1回目で成功。`runs/run{1-5}/api_meta.json`の`attempts`はすべて
  `[{"attempt":1,"success":true}]`)。
- `response.model`実値: 全10件とも`"gpt-5.6-luna"`(pricing_snapshot.json
  記載どおりのモデル、routing.WRITER_MODELと一致)。
- Web Search: 未使用(tools引数を渡していない、コード上使用不可能な構成)。

## §13 Fable参考評価
`[Fable記入]`

## §14 分類
`[Fable記入]`(Sonnet参考評価としては§9の収束傾向が強く、暫定的には
「PASS未満(FAILに近いボーダーライン)」寄りと見るが、最終分類は
Fable/ユーザー判断)。

## §15 USER_DECISION_REQUIRED
`[Fable記入]`

## §16 Production変更なしの確認

本Trialは以下を一切変更していない: `CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`等SSOT、既存`er013_family_c_future_*.py`(全て新規import
のみ、無編集)、既存`er013_output/family_c_future_trial_*`(読み取りのみ)。
新規追加は`er018_fiction_core_provocation_random_dna_trial_01.py`と
`er018_output/fiction_core_provocation_random_dna_trial_01/`配下のみ。
Production採用(`APPROVED_FOR_PRODUCTION`)は行っていない。
