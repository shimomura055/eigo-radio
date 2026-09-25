# FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01_REPORT.md

管理ID: FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01
Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
到達上限: VALIDATED(Production採用は本タスクの対象外)。

## §1 目的

前回Trial(FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01、
`FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01_REPORT.md`)は、5本中4本
(Run1/2/4/5)が「記憶を記録・保存・交換・再生する技術が、まだ起きていない
出来事(殺人/暴力)を予告する」という同一パターンへ収束した(§9)。原因の
一部として、共通developer message/Writer promptに旧Future設計由来の
「real / future / unreal / imagined-speculative」等の世界設定列挙が残って
おり、E軸を持たないRun(Run2: C=secret, D=schoolのみ)まで技術的記憶ギミック
へ誘導した可能性があった。

本Trialは、**Story DNA設計(5軸・2-3軸・seed・Run5 Future Coverage・4共通
原則・語数280-420)は一切変更せず**、上記の世界設定列挙(Prompt Bias)だけを
除去し、同一seed(`seed_base=20260925`)・同一DNAで5 Run再生成して、収束傾向が
変化するかを確認する。

## §2 Bias箇所と除去差分(逐語)

全文grep(対象語: future/unreal/speculative/imagined/fantastical/real
world/realistic)の結果、Promptに影響する箇所は3箇所のみだった(詳細な
分類表・全文Before/Afterは`er018_output/fiction_core_provocation_prompt_
bias_retrial_01/prompt_bias_diff.md`)。

1. **`CORE_PROVOCATION_DEVELOPER_MESSAGE`**(全Run共通のdeveloper message)
   - Before: `"...single central idea or question -- regardless of whether
     the story takes place in the real world, the future, an unreal/
     fantastical setting, or an imagined/speculative world -- that would
     make a reader feel..."`
   - After: `"...single central idea or question that would make a reader
     feel..."`(列挙句を単純削除)
2. **`WRITER_DEVELOPER_MESSAGE`**(全Run共通のdeveloper message)
   - Before: `"...not a summary of studies or an abstract essay. The setting
     can be realistic, near-future, far-future, or entirely unreal/
     speculative -- whatever fits the Core Provocation best. Do not force
     the story..."`
   - After: `"...not a summary of studies or an abstract essay. Do not
     force the story..."`(1文を単純削除)
3. **`WRITER_PROMPT_TEMPLATE`の`[Your single job]`**(全Run共通のprompt)
   - Before: `"Write a short story built around the Core Provocation above,
     in whatever kind of setting fits it best (real, future, unreal, or an
     imagined/speculative world). Make a reader genuinely feel..."`
   - After: `"Write a short story built around the Core Provocation above.
     Make a reader genuinely feel..."`(括弧句を単純削除)

いずれも列挙の単純削除であり、新しい誘導語は追加していない。

**維持した箇所**: `AXIS_DEFS["E"]["values"]`内の"a near future"/"a greatly
changed future"/"a supernatural or fantastical world"等(Story DNA E軸の値
そのもの。DNAブロック経由でLLMへ渡る部分であり、委任文により変更禁止)。
`COMMON_PRINCIPLES`・`DNA_BLOCK_TEMPLATE`には世界設定列挙は含まれておらず、
「要判断」に該当する箇所はなかった。

## §3 DNA一致確認

新スクリプト`er018_fiction_core_provocation_prompt_bias_retrial_01.py`の
`--step dna --seed-base 20260925`を実行し(APIコールなし、乾式)、前回
`dna_log.json`・各`runs/runN/dna.json`と`diff`したところ、**5 Run全てbyte単位
で完全一致**した(`er018_output/fiction_core_provocation_prompt_bias_
retrial_01/dna_match_confirmation.txt`)。Run1=A/E(strangers/a near
future)、Run2=C/D(a secret/school)、Run3=A/B/E(colleagues/bittersweet/a
supernatural or fantastical world)、Run4=C/D/E(an exchange/a workplace/
technology-institution world)、Run5(Coverage)=C/D/E(a reversal/a
hospital/technology-institution world)。

## §4 各Run(DNA/候補3案/選択Core Provocation/Story全文)

全文は`er018_output/fiction_core_provocation_prompt_bias_retrial_01/
stories_all.md`(DNA・候補3案チョイス理由・Story本文)、blind版は同dirの
`blind.md`+`blind_key.json`(Fableのブラインド評価用)。要約は§5・§6を参照。

## §5 旧vs新一覧

| Run | Story DNA | 旧Core/Story概要 | 新Core/Story概要 | 主な変化 | Future/Tech依存(旧→新) |
|---|---|---|---|---|---|
| 1 | A=strangers, E=a near future | 「The Memory for Tomorrow」。近未来の記憶ストレージ、見知らぬ男が法的消去前の記憶を託し、開くと「明日自分が彼を殺す記憶」 | 「The Last Memory」。近未来の記憶アーカイブ、見知らぬ女性が死の直前に最後の記憶を託し、witnessは自分が彼女を殺す映像を見る | ほぼ同型(near-future記憶技術+暴力予告)。役割(誰が誰を殺すか)が逆転した程度 | 高→高(変化小) |
| 2 | C=a secret, D=school | 「The Memory for Tomorrow」(Run1と題名完全重複)。学校の記憶ロッカーに明日付けの自分の告白録音、教師は記憶消去から逃げて隠れていた | 「The Missing Face」。卒業ビデオに誰も覚えていない同級生が映っている、実は洪水事故の犠牲者を学校が隠蔽していた | **技術的記憶ギミック(デジタルロッカー・未来日付録音)が消え、非技術の人間関係的隠蔽(事故の揉み消し)に変化**。暴力の予告構造も消えた | **高→なし(明確な改善)** |
| 3 | A=colleagues, B=bittersweet, E=a supernatural or fantastical world | 「The Empty Chair」。超自然の図書館で同僚が記録から消える、思い出そうとするほど記憶も消える | 「The Last Memory」(Run1と題名重複)。幽霊が生きるための「記憶市場」、同僚が自分との友情の記憶を売ってゴーストの母を救う | 両方とも超自然・非暴力・切ない喪失系で同系統(この系統は旧Trialで唯一の異物だったが、新Trialでも同じ役割を再現) | なし→なし(変化小、両方とも非収束グループ) |
| 4 | C=an exchange, D=a workplace, E=technology-institution world | 「The Memory Shift」。シフト交代のため記憶交換した2人が同じ殺人を「相手が凶器を持っていた」形で記憶 | 「The Borrowed First Day」。ジョブ習得のため記憶交換、新人が先輩の記憶の中に隠された殺人現場を目撃、先輩自身はその記憶を失っている | ほぼ同型(職場の記憶交換制度+殺人の目撃・隠蔽)。犯人特定の構造は同じ | 高→高(変化小) |
| 5 (Coverage) | C=a reversal, D=a hospital, E=technology-institution world(Future系強制) | 「The Memory Before」。昏睡患者の記憶カードが自分の目覚める時刻と殺すべき家族を予告、目覚めた本人は「未来からのメッセージ」と主張 | 「The Sealed Memory」。記憶除去病院、看護師が自分が患者を殺す映像入りの封印記憶を発見、患者は「病院が偽の未来記憶を作って冤罪を仕込んでいる」と説明 | ほぼ同型(病院の記憶技術+暴力予告)。旧は文字通りの予知、新は「陰謀による偽記憶の作為」という説明に変化(暴力予告の構図自体は残存) | 高→高(変化小) |

**要点**: Bias除去の効果はRun2で最も明確に現れた(唯一E軸を持たないRunが、
旧Trialでは自発的に未来技術設定を選び、新Trialでは技術なしの人間ドラマへ
変化した)。Run1/4/5はDNAにE軸(近未来/現実にない技術制度)が明示的に含まれる
ため、Bias除去後も同系統のまま(これはDNA由来であり妥当)。Run3は両Trialで
一貫して非収束(超自然・非暴力)。

## §6 Run2詳細

**旧候補3案**(`er018_output/fiction_core_provocation_random_dna_trial_01/
runs/run2/provocation.json`):
1. (選択) 学校が生徒の記憶を「私的デジタルロッカー」に保管、生徒が「明日付け」の
   自分の告白録音(行方不明の教師を匿ったという内容)を発見。警告か、仕組まれた
   嘘か、すでに選んだ未来かを突き止める。
2. ある朝、クラス全員が「昨日いた女子」を覚えているのに、名前・写真・記録が
   全て消えている。1人の生徒だけが真相を覚えている(その子に「忘れて」と
   頼まれていた)。
3. 学校が卒業前に1つの辛い記憶を消去するサービスを提供、生徒がそれを使った後、
   親友が口をきいてくれない理由も一緒に消えていたことに気づく。

**新候補3案**(`er018_output/fiction_core_provocation_prompt_bias_retrial_01/
runs/run2/provocation.json`):
1. (選択) 卒業ビデオを準備中、教師も含め誰も覚えていない同級生の映像を発見。
   その生徒がなぜ学校の記録から消されたのかを、ビデオ上映前に突き止めなければ
   ならない。
2. 教師が「今年一番大事な出来事」について作文を書かせると、生徒全員が同じ
   平凡な1日を違う形で覚えている。その中の1つのバージョンが、学校が隠して
   きた秘密を明らかにする。
3. 忘れることを恐れる生徒が同級生の記憶をひそかに録音している、そこに
   「まだ起きていない出来事」を語る新しい録音と、数か月前に学校から消えた
   同級生の声が混ざっている。

**判定**: 旧候補1(選択)は「デジタルロッカー」「明日付けの記憶(未来技術)」
という明確な技術的記憶ギミック。新候補1(選択)には技術的記憶装置が一切なく、
「記録から消された」という表現のみ(実際のStory本文では、洪水事故で亡くなった
生徒を学校が隠蔽した結果という、完全に非技術的な人間の秘密)。ただし新候補3
には「まだ起きていない出来事を語る録音」という**未来予知的な記憶技術への収束
の残滓**が見られる(選ばれなかったが、LLMの発想の引力としては残っている)。
選択されたStoryそのものは技術/未来予知から完全に離れた。

## §7 全体比較

**未来/SF/技術系(記憶技術が暴力/死を予告するパターン)への収束数**:
旧3trial=4/5(Run1/2/4/5)→新=3/5(Run1/4/5)。Run2が唯一、収束パターンから
離脱した(§6)。Run3は両Trialで一貫して非収束(超自然・非暴力の喪失譚)。

Run1・Run4・Run5は元々DNAのE軸に「近未来」「現実にない技術・制度がある世界」
が明示的に含まれているため、Bias除去後も同系統のStoryになったこと自体は
DNA設計どおりであり問題ではない。E軸を持たないRun2だけがBias除去の影響を
最も強く受け、実際に離脱したことは、旧Trialの仮説(「Prompt Biasが
E軸なしRunまで技術系へ誘導していた」)と整合する結果である。

**同型プロット重複**: 旧Trialの「記憶技術+暴力予告」パターンは新Trialでも
3/5残存しており(Run1/4/5)、これはDNA上E軸がFuture/技術系である以上、当然の
収束であってBias除去だけでは解消しない(Theme="memory"自体の引力の可能性が
高い、旧REPORT §9-13の考察と同じ)。

**タイトル重複**: 旧Trial=Run1・Run2が完全同一(「The Memory for
Tomorrow」)。新Trial=Run1・Run3が完全同一(「The Last Memory」)。**重複自体は
解消していない**(2/5→2/5)。ただし重複したペアが変わった点(旧: 収束グループ内
の2本 → 新: 収束グループRun1と非収束グループRun3)は、収束の質的な違いを示す
偶然の一致であり、Bias除去と直接の因果関係はないと考えられる。

**主人公名の反復**: 新Trialの主人公名はDaniel(Run1)・Lena(Run2)・Eli
(Run3、一人称)・無名(Run4、一人称)・Mara(Run5)で、旧Trialのような
Mara/Maya/Linaの近似的反復([REPORT旧§8]参照)は見られなかった。ただし
Run5の"Mara"は旧Run1の主人公名と偶然一致している(乱数由来、意味のある収束
ではない)。

**DNAごとの差がStoryに出ているか**: E軸を持つRun(1/4/5)は共通してFuture/
技術系のStoryになった一方、A/B軸(relationship/tone)の違い(strangers vs
colleagues、bittersweetの有無)はStory本文の雰囲気に一定程度反映されている
(Run1は緊迫したサスペンス、Run3は切ない別れ)。C/D軸(drama/setting)は
Run2(secret+school)・Run4(exchange+workplace)で核の仕掛けに明確に反映
されている(§5表)。

**日常・人間関係ベースのStoryが出たか**: Run2が該当する(洪水事故の隠蔽という
学校の人間関係・組織的秘密であり、超自然も未来技術も使わない)。これは旧
Trialには存在しなかったタイプであり、Bias除去の最も具体的な効果と言える。

**発想タイプの類似性(人間が読める説明)**: 5本のうち3本(Run1/4/5)は
「記憶を扱う制度・技術があり、その記憶が暴力や殺人を予告・目撃する」という
同一の物語エンジンを使っている。残り2本(Run2/3)はこの型から外れており、
Run2は「学校組織の秘密の隠蔽」、Run3は「別れ・喪失の切なさ」という別の
物語エンジンを使っている。TF-IDF類似度(補助指標、後述)は0.36〜0.63の
範囲でどれも「中程度」としか出ず、この質的な収束・非収束の区別を機械指標
だけでは捉えられない(旧REPORTと同じ限界)。

**TF-IDF類似度(補助指標)**:
- 新5本同士の平均コサイン類似度: 0.4409(`er018_output/fiction_core_
  provocation_prompt_bias_retrial_01/similarity_matrix.json`から算出)
- 旧5本同士の平均コサイン類似度: 0.4936(旧`similarity_matrix.json`から算出)
- 新旧の相互類似度(cross similarity、5×5=25ペア)は0.357〜0.625の範囲。
  最も高いのはRun5×old_run1(0.6249、両方とも「病院/暴力予告」系の語彙が
  近い)、最も低いのはRun2×old_run5(0.3697)。
- 数値は下がったが(0.4936→0.4409)、差は小さく、上記の質的な変化(Run2の
  離脱)ほど劇的ではない。TF-IDFは表層の語彙類似度であり、物語エンジンの
  型の違いを直接には反映しない(旧REPORT §8と同じ限界を再確認)。

## §8 QCD(cost・時間・失敗)

- **Cost**: 実績¥4.69(10 call、`gpt-5.6-luna`、record_count=10)。上限¥15に
  対し余裕あり。前回実績¥4.45とほぼ同水準(差は¥0.24、モデル出力の自然な
  ばらつき)。詳細: `er018_output/fiction_core_provocation_prompt_bias_
  retrial_01/cost.json`・`raw_usage_log.jsonl`。
- **失敗・リトライ**: 全10 call(Core Provocation 5 + Story 5)とも初回attempt
  で成功、リトライ発生なし(各`runs/runN/api_meta.json`の`attempts`が
  `[{"attempt": 1, "success": true}]`のみ)。
- **語数**: 393/434/417/418/403語(目標350語、許容280-420語)。Run2のみ434語で
  上限420語を14語超過(「roughly」の範囲であり致命的ではないが、次回の
  参考としてQCDに記録)。
- **所要時間**: dna/generate/analyze/assembleの4 stepを通しで実行、API呼び出し
  自体は数分で完了(タイムアウトなし)。

## §9 Sonnet仮分類

**REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれか、最大VALIDATED**:

**暫定: VALIDATED**(Sonnet参考評価、最終判断はFable/ユーザー)。

根拠:
1. Prompt Bias除去は委任どおり実施でき、Story DNA設計・seed・DNA選定結果は
   完全一致を確認した(§3)、STOP条件(Story DNA変更・新軸追加の必要性)は
   発生しなかった。
2. Bias除去の効果は限定的だが実在する: 唯一E軸を持たないRun2が、旧Trialでは
   自発的に技術的記憶ギミックへ収束していたのに対し、新Trialでは技術なしの
   人間関係ドラマへ変化した(§6・§7)。これは旧Trialの仮説(「共通Prompt文言が
   E軸なしRunまで技術系へ誘導していた」)を裏付ける具体的な証拠である。
3. ただし、E軸にFuture/技術系の値を持つRun(1/4/5、DNAとして正当)は
   Bias除去後も同系統のStoryを生成しており、5本中3本が「記憶技術が暴力を
   予告する」という同一の物語エンジンに収束したままである(旧4/5→新3/5、
   改善はしたが解消はしていない)。これはDNA自体(Theme="memory"+E軸の
   Future/技術系値)由来である可能性が高く、Prompt Bias除去だけでは
   解決しない領域であり、本Trialのスコープ外(Story DNA変更が必要になる
   可能性があり、それは本Trialでは禁止されている)。
4. タイトル重複は解消していない(2/5→2/5、重複ペアの中身は変化)。

したがって「Bias除去という狭い施策単体の効果検証」としては目的を達成し
(REJECTEDには当たらない)、「5本の多様性を完全に解消する」というより大きな
目標に対しては部分的な前進にとどまる(現状ではUSER_DECISION_REQUIREDへ
格上げするほどの新しい仕様変更の必要性は生じていないため、VALIDATEDで
報告し、残る収束(3/5)への対処が必要かはFable/ユーザー判断に委ねる)。

## §10 [Fable記入]

## §11 [Fable記入]
