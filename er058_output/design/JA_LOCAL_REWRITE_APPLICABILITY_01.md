# JA_LOCAL_REWRITE_APPLICABILITY_01: 日本語Local Rewrite適用性Trial(委任_04D 作業5、2026-10-12)

状態: Trial/設計(TTS生成なし、Production変更なし)。採否・日本語適用範囲はユーザー判断。
使用モデル: **`gpt-6-luna`**(reasoning_effort=`high`)= Production LRと同一(`routing.WRITER_MODEL`、`er003_v1_en_direct_vfl_01`経由、`er020`が`b1s.MODEL`として使用)。**最新モデルか: いいえ(同世代の「効率系」。最上位は`gpt-6-astra`、推奨系は`gpt-6.1-sol`、`docs/pm/dev_eval_model_inventory_01.md` 2026-10-09取得)。理由: 例外種別2「ライン組み込み候補としてそのモデル自体の性能確認」(Production LRの実モデルで日本語適用可否を見る必要がある)。評価者LLMは使わず、機械チェック+Fable/ユーザー確認用に提示**。`gpt-6.1-sol`は`pricing_snapshot.json`未登録、`gpt-6-astra`は単価が高く費用上限JPY3に収まらないため未使用。
費用: 5 call、入力2,346 tok・出力8,460 tok、推定**JPY0.71**(`gpt-6-luna` $0.10/$0.50 per 1M、USD_JPY=160、請求画面は未確認。上限JPY3)。
証跡: `er058_output/ja_local_rewrite_applicability_01/ja_lr_trial_results.json`。スクリプト: `er058_ja_local_rewrite_applicability_01.py`。

---

## 1. 英語LR実装の構造(`er020_tts_retry_local_rewrite_01.py`)
| 段 | 関数 | 内容 | 言語依存 |
|---|---|---|---|
| role判定 | `resolve_narrative_role`/`connected_speech_enabled_for` | 5 role(Full Story/Comment/Preview/Topic intro/In One Line)のみ適用。**Key Phrase・Heading readoutは非適用**(`NON_APPLICABLE_SEGMENT_IDS`/`KEY_PHRASE`) | なし |
| span選択 | `identify_ng_span`(L171) | `asr_validation.tokenize`(ASCII英数字のみ)で単語化し、`difflib`の**最初のdiff op**+前後3語を問題spanとする | **英語(ASCII)専用** |
| 候補生成 | `call_luna_candidate_gen`(L447)、`CANDIDATE_GEN_SYSTEM_PROMPT` | Luna(`json_schema` strict)、5候補(single_word_swap/short_phrase_rewrite)、全文verbatim+span before/after | プロンプトが「natural idiomatic spoken **English**」 |
| 機械Gate | `diagnose_candidate_full_segment`(L293)、`check_span_consistency`、`check_numeric_preservation`、`check_locality`(Gate 6)、`compute_unchanged_ratio`(Gate 7、しきい値0.7) | 全文性・断片/過剰拡張拒否(長さ比0.7〜1.5)・申告span整合・数値保持・局所性(±3 token)・未変更率 | 単語単位(`[A-Za-z']+`、`\w+`)。**日本語は明記**: 「英語TTS role専用。日本語経路は未対応(Gate7がASCII語のみ計数するため純日本語候補は常にGate7不合格)」(L296-298) |
| 局所QA | `call_luna_local_qa`(L597)、`LOCAL_QA_SYSTEM_PROMPT` | 5 Gate(意味保持/role保持/Fact矛盾なし/文脈接続/**Natural English**)をLuna 1 callで | Natural **English**判定 |
| 選択 | `select_final_candidate` | 全7 Gate PASSのうち`unchanged_ratio`最大 | |
| 統合 | `run_local_rewrite_recovery`(L677) | span特定->候補->QA->選択->`retts_fn`(再TTS)。`identify_ng_span`が`found=False`なら`HUMAN_REVIEW_LOCKED_NO_NG_SPAN` | |

## 2. 日本語に機械流用した場合の失敗(確定、実測)
5実例で既存関数を日本語入力へそのまま呼んだ結果(`ja_lr_trial_results.json`の`existing_en_funcs_on_ja`と各候補の`en_*`):
| 既存関数 | 日本語入力での結果 | 影響 |
|---|---|---|
| `identify_ng_span` | **g8/g5/g6(純日本語)は`found=False`**(ASCIIトークンが空)=`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`で即HR。**g21/g36は`found=True`だが、数字(`2`/`20`)のASCII部分だけを拾った偶然の発火**で、実際の問題語(g21は「続き->鈴木」)を指さない | span選択が日本語で**未動作または誤動作** |
| `compute_unchanged_ratio`(Gate 7) | 自分自身を比べても**0.0**(全15候補で0.0)=Gate 7は日本語で**常に不合格**(確定) | 全候補が機械的に落ちる |
| `diagnose_candidate_full_segment` | 長さ比・先頭/末尾判定は動くが、`_simple_tokens`(`\w+`)が日本語を**1つの長い語**として扱うため`check_span_consistency`が**正しい候補でも`SPAN_INCONSISTENT_UNDECLARED_CHANGE`**(g8候補1、g5候補1〜3、g36候補1〜3)、短い名詞句では`LOW_ORIGINAL_COVERAGE`(g6)、`TOO_LONG_OVER_EXPANDED`(g8候補2〜3)。g21は全て`FULL_SEGMENT_OK` | 判定が**不安定**(一部偽合格、一部偽不合格) |
| 局所QA(`natural_english`) | 日本語候補を「English」として評価 | プロンプトの日本語版が必要(Trialでは未実施) |

**結論(確定)**: 現行LR実装は日本語では**Gate 7が常に落ち、span特定が動かない**ため、機械流用では運用不可。日本語対応には、(a)文字/形態素単位のspan特定、(b)Gate 6/7/span整合/全文性の文字単位版、(c)日本語QAプロンプトが必要。

## 3. 日本語に適用する際の課題
| 課題 | 内容 | 実例 |
|---|---|---|
| **読み・漢字** | 日本語は表記と読みが別。書換えが**読み(TTSの発音)を変える**ため、読み一致Gate(`pykakasi`等の読み比較・辞書)が要る。ASRの誤転写が**表記違い**(熟/じく、所/勝)なのか**読み違い**なのかをspan選択時に区別できない | g8: 「熟す」を「じくす」。Azure/whisperは正解=TTSは正しかった可能性が高い(Primary誤認) |
| **助詞・活用・送り仮名** | span境界が語の途中(送り仮名・助詞)になりやすい。語単位の境界は形態素解析が必要(未導入) | g6: 「形に**なり**始める」の脱落、g21の「ふまえて/踏まえて」 |
| **同形異音語・表記ゆれ** | 同形異音語(例: 名所のような漢字の別読み)や、数詞(二/2)・記号(％/パーセント)・送り仮名(表れる/現れる)は**TTSが正しくてもASRの表記が揺れる** | g21(二->2、表れる/現れる)、g36(％->パーセント) |
| **意味保持Gate** | 日本語の言い換えは含意・敬体/常体・語感がずれやすい。LLM QAの日本語版+Fact語(数詞・固有名詞・漢字連続語)の機械保持チェックが要る | 下4章 |
| **対象roleの不一致** | NG実例の多くは**Key Phrase/短い意味語(g8/g5/g6/g7)でLR非適用role**。LR対象の5 roleに当たるのはComment等の長文のみ | 5実例中、LR対象roleはg21・g36のみ |
| **表記差のみのNG** | Secondaryを厳格PASS集合(EXACT/NORMALIZED)にすると、g21・g36はAzure=`PHONETIC_MATCH`(`secondary_pass=False`、報告02ja_offline_replay)でNG扱い->**TTSが正しいまま3回再生成->LR発火**し、**正しい原稿を書き換える**リスク | 共通フロー設計(PHONETIC許容、U-3(c))との関係 |
| **span特定の基準** | 「最初のdiff op」方式は、表記差(二->2)を先に拾い**本当の誤り(続き->鈴木)を外す** | g21 |

## 4. 日本語LR候補の生成結果(5実例、候補3件ずつ、TTSなし)
機械チェック: 文字単位の変更量、全文verbatim+申告span整合、span外のFact語(数詞・漢字/カタカナ連続語)保持、末尾句点、長さ比。**意味・自然さの判断は下表の「私の暫定所見」であり未検証、Fable/ユーザーの確認用**(LLM QAは今回未実行、費用上限のため)。

| 実例 | role | 原稿(NG型) | ASR(Primary)のNG | 生成候補(span before->after) | 機械チェック | 暫定所見(要確認) |
|---|---|---|---|---|---|---|
| g8 | KP意味(**LR非適用role**) | 熟すと出るガス(読み+濁点) | じくすと出るカス | 1) 熟すと出る->**成熟すると出る** 2) ->成熟が進むと発生する 3) ->成熟に伴って生じる | 全て全文verbatim+span整合OK、Fact語保持OK、変更2/9/7文字、長さ比1.29/1.71/1.57 | **候補はいずれも本当のNG(濁点ガ/カ、熟/じく)を直しておらず、TTSは正しかった可能性が高い(Azure/whisper正解)原稿を書き換えるだけ**。候補1は最小だが「熟す」->「成熟する」で語感が変わる。2・3は拡張しすぎ。**LR不要例** |
| g5 | KP意味(**非適用role**) | 名所を中心にした旅程(同形異音/漢字誤認) | 名勝を中心にした旅亭 | 1) 中心に->軸に 2) 中心にした->メインにした 3) ->主軸にした | 全てspan整合OK、変更2〜3文字、長さ比0.9〜1.1 | **実際の誤り箇所(名所の「所」、旅程の「程」)ではなく「中心」を書換え**(最初のdiffが「所->勝」なのにLLMが周辺を選択)。「メイン」は外来語化で語感が変わる。意味はほぼ保持。**NG span外の書換え=目的を果たさない** |
| g6 | KP意味(**非適用role**) | 形になり始める(脱落) | 形に始める | 1) 形になり始める->**形を成し始める** 2) ->形を取り始める 3) ->形を帯び始める | 全て整合OK、変更2〜3文字、長さ比1.0 | 「なり」脱落を避ける最小書換えだが、候補2「形を取る」・3「形を帯びる」は**含意が変わる**(「形になる」=具体化)。候補1(形を成す)が最も近い。**慣用句の言い換えは意味保持が難しい** |
| g21 | **Comment(LR対象)** | 世界市場…。この二つは比べる期間が違い、…続きに耳を傾けてみましょう。(数詞表記+固有語誤認) | 二->2、続き->鈴木(**実際の誤りは「続き」**、Azure正解) | 1) この二つは比べる期間が違い->**両者では比べる期間が違い** 2) ->比較する期間は両者で異なり 3) ->それぞれの比較期間が異なり | 全て全文verbatim+span整合OK、span外Fact語(数詞・固有語)保持OK、変更4/14/12文字、長さ比0.99〜1.0、句点同じ | 最初のdiff(二->2、**表記差でTTSは正しい**)を選んだため**真の問題「続き」には触れない**。候補1は**4文字変更で自然・意味保持**(「この二つ」->「両者」)だが原稿の「二つ」という数への言及が消える。候補2・3は前文との接続や「二つ」の参照が弱くなる。**NG原因が「ASRの誤認」であり書換えは不要** |
| g36 | **Comment(LR対象)** | まず、20％という計画が…注目してください。(記号の読み) | 20パーセントという(Azure=20%、**TTSは正しい**) | 1) 20％->**20パーセント** 2) 20％という->20パーセントの 3) ->20パーセントとした | 全て整合OK、数値保持OK、変更5〜7文字、長さ比1.04〜1.08 | 候補1は**読み(パーセント)へ表記を寄せるだけ=TTS-safe正規化と同じ**(音声はほぼ不変)。候補2・3は助詞変更で含意が変わる(「とした」=定めた)。**表記差のみのNG=LR不要、むしろTTS-safe正規化の問題** |

### 4-1. 集計
| 観点 | 結果(5実例・15候補) |
|---|---|
| 全文verbatim+span整合 | 15/15(Luna日本語の指示追従は良好) |
| span外のFact語保持 | 15/15(機械チェックは全て通過=**機械チェックだけでは意味のずれを検出できない**) |
| 最小変更(変更文字数<=3) | g5・g6・g8候補1で該当(約7/15)。拡張しすぎ(>=7文字)が5/15 |
| **本当のNG原因に触れた** | **0/5実例**(g8・g5は周辺語、g6は近いがASR誤認の可能性、g21・g36は表記差で書換え不要) |
| TTSが正しい可能性が高い(Azure/whisperが正解) | g8、g21、g36(3/5) |
| 意味・含意の保持(暫定所見) | 候補1は概ね保持、他は含意変化が多い(慣用句・助詞変更) |

## 5. 結論(ユーザー判断材料)
- **日本語LRは「機械流用では運用不可」**(確定、Gate 7常時不合格+span特定未動作)。
- 日本語LRを使うには**新規設計が必要**: 文字/形態素単位のspan特定(誤りのある語を指すこと)、日本語版Gate、読みGate、日本語QAプロンプト。
- 5実例では**Lunaは日本語の最小書換え候補を作れる**が、**NGの原因がASR誤認/表記差(3/5)の場合、書換えは本来不要で、原稿を変えるデメリットだけが残る**。LRの前提「TTSが実際に誤っている」を保証するのは共通フローのSecondary確認+表記差の扱い(PASS_WITH_WARNING/PHONETIC許容、U-3(c))であり、**LR設計よりSecondary側の方が先**。
- 対象roleに限ると(Comment等)、日本語LRの需要は表記差のNG(g21・g36型)に偏る可能性がある(標本2件、推測)。この型は**Secondary側で解消すべき**。
- **推奨(提案のみ)**: 日本語は当面**LRなし(3回不合格->Human Review)**で共通フローを開始。LR日本語対応は(1)Secondary厳格集合の偽NG率を測る最小対Trial(8-3-A)後に、(2)実際に「TTSが誤読したComment等の長文」が複数観測されたら設計。KP・見出しはLR非適用のまま。

## 6. 限界
- 標本は5実例(各1回生成、n=3候補)。LLM QA(意味/自然さ/文脈)は未実行。context(前後文)は未提供。
- 実際のTTS生成・再ASRは未実施(上限・範囲外)。候補が実際にASRを通るかは未検証。
- `identify_ng_span`相当の日本語span特定は本Trialの文字単位簡易版(Production化は未検討)。
