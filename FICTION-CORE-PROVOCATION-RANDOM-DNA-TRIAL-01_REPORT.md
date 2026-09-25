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

### 13.1 blind照合(blind_key.json: P=Run5, Q=Run4, R=Run3, S=Run2, T=Run1)
Fableはblind.mdを先に読み、keyを後で開いた。blind段階のグルーピングは
「{P,S,T}=同一群 / Q=準同一 / R=別物」で、key開封後もこの判断は変わらなかった。

### 13.2 各Runの評価
| Run | seed | DNA(軸=値) | Core Provocation要旨 | Story題名 | DNAの効き方 |
|---|---|---|---|---|---|
| 1 | 20260926 | A=見知らぬ人 / E=少し先の未来 | 見知らぬ男が「法的に消される記憶」を24時間預かってほしいと頼む。開くと「明日自分がその男を殺す記憶」だった | The Memory for Tomorrow | A・Eとも表層は反映(駅の見知らぬ男/2041年)。ただし核は「記憶技術が明日の殺人を予告」で、DNAはこの核を動かしていない |
| 2 | 20260927 | C=秘密 / D=学校 | 学校の記憶ロッカーに「明日付け」の自分の告白録音。教師を隠したのは自分 | The Memory for Tomorrow | Dは反映(学校・ロッカー)。Cは「隠した教師」として弱く反映。E軸未指定なのに未来技術設定を自発選択し、Run1と題名まで完全一致 |
| 3 | 20260928 | A=同僚 / B=切ない / E=超自然・幻想 | 幻想図書館で同僚があらゆる記録から消え、証明しようとするたびに自分の記憶も消える | The Empty Chair | 3軸すべてが核まで届いている。暴力なし・喪失と余韻の物語で、B(切ない)が結末のトーンを実際に決めた。5本中唯一の質的異物 |
| 4 | 20260929 | C=交換 / D=職場 / E=現実にない技術 | シフト交代のため記憶を交換した2人が、同じ殺人を「相手が凶器を持っていた」形で記憶 | The Memory Shift | C(交換)は核に直結し機能した。ただし素材(Mara/銀のナイフ/血のシャツ/機械の太字メッセージ)はRun1/5と共通で、テイストは同群 |
| 5(Coverage) | 20260930 | C=逆転 / D=病院 / E=現実にない技術(強制) | 昏睡患者の記憶カードが「自分が目覚める時刻」と「その前に殺すべき家族」を告げる。目覚めた本人は「未来からのメッセージ」と言う | The Memory Before | D・Eは反映。Cは「弟が『明日を覚えている』」という終盤の反転として弱く反映。結果としてRun1/2と最も近い(未来からの録音が暴力を予告し、予言か罠かで終わる)|

### 13.3 5本の違いの超サマリ
- 群1(Run1・Run2・Run5): 「未来の時点の録音/記憶が暴力を予告し、予言か罠か分からないまま終わる」。同一の仕掛け。
- 準群(Run4): 「交換した記憶の中の殺人で加害者が入れ替わる」。仕掛けは違うが、殺人・ナイフ・機械メッセージ・主人公Maraという素材が群1と同じで、読者体験としては同じテイスト。
- 別物(Run3): 喪失・消滅・余韻。暴力も技術もなし。
- 質的に異なる本数: 最大3(群1/Run4/Run3)、厳格には2(群1+Run4 / Run3)。

### 13.4 同じテイストへ収束した箇所(具体)
- 主人公名「Mara」がRun1/4/5の3本で一致(Run2は「Maya」で音まで近い)。
- 題名「The Memory for Tomorrow」がRun1/2で完全一致。
- 「X時17分」という時刻指定がRun1(8:17)/Run2(4:17)/Run5(3:17)の3本に出現。
- 「blood covered his shirt」がRun1/4で同文。銀色のカード/ナイフがRun1/2/4/5。
- 機械が太字で短文メッセージを出す演出(**EXCHANGE COMPLETE** / **PLAY NEXT MEMORY?** / **MEMORY: TOMORROW**)がRun2/4/5。
- 主人公が「自分の声」で未来の自分の行為を聞く構造がRun1/2/5。
- TF-IDF類似度(§8)は0.39–0.61で機械的には「中程度」だが、上記の反復は語彙類似度に表れない仕掛け・小道具レベルの収束であり、機械指標は本Trialの判定に使えない。

### 13.5 Future Coverage Run(Run5)の評価
- 機械的には成功(E軸がFuture系値に強制され、dna_log.jsonに`is_coverage_run: true`で記録、seed再現可能)。
- 品質的には失敗。E軸を未来技術に固定した結果、群1と最も近い作品になった。Coverage Runが「Future味を確保する」目的は達したが、「5本の中で1本ぶんの多様性を担う」目的は果たしていない。
- 副次知見: E軸を指定しなかったRun2でも未来技術設定を自発選択している。テーマ「記憶」がある限り、E軸のFuture強制は不要で、むしろ非未来値(現代の日常/超自然など)の強制の方が多様性に効く可能性がある(Run3が唯一の異物である事実と整合)。

### 13.6 Sonnetのスコープ逸脱(Fableとしてユーザーへ明示)
Sonnetは`er013_family_c_future_writer_08.py`流用時、委任文の「Future限定語句のみ置換」の範囲を超えて、Writer promptの`[CURRENT FACT -- forbidden]`ブロックと`[Required marker]`(`[[IMAGINED]]`マーカー必須化)ブロックの2つを丸ごと削除した(prompt_diff_writer.md §2に自己申告あり)。
- Fable判定: 理由(Fictionでは「現在事実 vs 想像未来」の区別が字義通り成立しない/本TrialにFact Safety層とマーカー再試行機構がない)は妥当で、5本の結果を汚す性質の変更ではない。ただし手続き上は逸脱であり、事前にFableへ確認して進めるべきだった。
- 本Trialの結論(収束)はこの削除と無関係(削除されたのは安全機構であり、物語の多様性に関わる指示ではない)。
- 将来Fiction familyを本実装する場合、Fact Safety層をどう扱うかは別途仕様判断が必要(§15へ)。

### 13.7 Sonnet参考評価との差
なし。Sonnet §9–10の「4/5が同一パターン、Run3のみ異質、FAIL寄りボーダーライン」とFable評価は一致。FableはRun4を「仕掛けは別だがテイスト同群」として群1と分けて数えたが、分類結果は変わらない。

## §14 分類
**REJECTED**(本Trialの方式=「Core ProvocationのFuture限定解除 + コード側乱数Story DNA 2–3軸 + テーマ固定5本」は、このままではFiction familyの多様性確保策として不採用)。

判定根拠(ユーザーの受入条件との照合):
- STRONG PASS(≥4本が質的に異なる): 不成立。
- PASS(≥3本): 最も甘く数えても3(群1/Run4/Run3)だが、Run4は素材・テイストが群1と同じで「質的に異なる」とは言えない。厳格には2。
- FAIL条件「違いが2本以下、またはStory DNAを入れても同じテイストに収束」: 後者に明確に該当(§13.4)。
- よってFAIL → 分類REJECTED。ただし「Story DNAが全く効かなかった」わけではない(Run3では3軸が核まで届いた/Run4のC=交換は核を動かした)。効かなかったのは「テーマ×暴力サスペンス」への引力に対して、A/D/E(表層軸)が弱すぎた点。

Production変更なし。SSOT記録は行わない(ユーザーが次の方針を決めた時点で、必要ならDECISION_LOG/OPEN_ITEMSへ「不採用の記録」として1件追記)。

(Sonnet参考評価としては§9の収束傾向が強く、暫定的には
「PASS未満(FAILに近いボーダーライン)」寄りと見るが、最終分類は
Fable/ユーザー判断)。

## §15 USER_DECISION_REQUIRED
本Trialは5本でSTOP済み。追加Trial・追加軸はFable/Sonnetからは提案のみで実施しない。ユーザー判断事項:

1. Fiction family多様性の次の一手を決める(いずれも新Trialとして別管理IDが必要)。改善案は§11(Sonnet)と以下のFable案の「提案のみ」:
   - (a) Core Provocation段階に「前Run群の仕掛け要約」を渡し、同じ仕掛け(未来予告・殺人・入れ替わり)を明示的に禁止する負の記憶(Negative memory)を追加する。本Trialのtheme memoryは題材の重複回避に効いていない。
   - (b) B軸(感情トーン)を毎回必ず含める(Run3の唯一の成功要因は「切ない」が結末を決めたこと)。暴力サスペンス以外のトーン値(温かい/おかしい/静か 等)が選ばれる確率を上げる。
   - (c) E軸のFuture強制Coverageを廃止し、代わりに「非未来値」のCoverageに反転する(Run2の自発未来化・Run5の収束を踏まえ)。
   - (d) 主人公名・時刻・小道具の反復を防ぐ軽い禁止リスト(生成後の機械チェック+1回再生成)を入れる。
   推奨: (a)+(b)を1つのTrialで検証(¥10以内)。理由: 収束の原因が「仕掛けの反復」と「トーンの単調さ」の2点に集約されるため、この2点だけ変えて効果を見るのが最小差分。
2. Sonnetが削除したWriter promptの2ブロック(CURRENT FACT禁止/`[[IMAGINED]]`マーカー)の扱い: Fiction familyを本実装する際にFact Safety層を(i)Future family同様に維持する、(ii)Fictionでは不要として外す、のどちらかを仕様として決める。本Trialの結論には影響しない。推奨: 今は決めない(方式自体がREJECTEDのため)。
3. 5本のうちRun3「The Empty Chair」を単体で記事候補として残すか(残す場合も本方式の採用を意味しない)。推奨: 保留(Fiction familyの方式が決まってから)。

## §16 Production変更なしの確認

本Trialは以下を一切変更していない: `CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`等SSOT、既存`er013_family_c_future_*.py`(全て新規import
のみ、無編集)、既存`er013_output/family_c_future_trial_*`(読み取りのみ)。
新規追加は`er018_fiction_core_provocation_random_dna_trial_01.py`と
`er018_output/fiction_core_provocation_random_dna_trial_01/`配下のみ。
Production採用(`APPROVED_FOR_PRODUCTION`)は行っていない。
