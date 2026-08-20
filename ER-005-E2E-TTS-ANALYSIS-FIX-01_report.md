# ER-005-E2E-TTS-ANALYSIS-FIX-01 実行報告書

**タスク**: Cost再分析・末尾音切れ調査・Point Notification再発防止
**実行日**: 2026-08-21
**前提**: [ER-005-E2E-TTS-COST-QUALITY-01](ER-005-E2E-TTS-COST-QUALITY-01_report.md)(B1/A2のE2E TTS Cost計測)の事後修正・追加調査タスク。既存ログ(`raw_usage_log.jsonl`/`tts_generation_results.json`/`run_summary_tts.json`/segment音声ファイル)のみを用いて再分析し、新規の有料API呼び出しは**Part C・Part Eの音声再生成を除き行っていない**(詳細は各章・末尾「未完了・要確認事項」を参照)。

---

## 完了報告の最上段(14項目の必須回答)

1. **B1 Clean TTS Costはいくらか**: **25.58円**(実測ベース再計算。方法論はPart A参照)
2. **B1 Clean ASR Costはいくらか**: **12.39円**
3. **B1 Retry/Fallback Waste(TTS/ASR分離)はいくらか**: TTS **63.28円**、ASR **30.31円**(合計93.58円)
4. **B1 Operator-error Waste(TTS/ASR分離)はいくらか**: TTS **62.86円**、ASR **31.31円**(合計94.18円。ディレクトリ未作成によるクラッシュ、こちらの作業ミス)
5. **B1 Evaluation Actual Spend(本タスク一連の実測総支出)はいくらか**: **225.72円**(Operator-error Waste 94.18円 + Production-path Actual 131.55円)
6. **A2 Clean TTS Costはいくらか**: **23.68円**
7. **A2 Clean ASR Costはいくらか**: **11.87円**
8. **A2 Retry/Fallback Waste(TTS/ASR分離)はいくらか**: TTS **35.35円**、ASR **15.24円**(合計50.59円)
9. **A2 Operator-error Waste(TTS/ASR分離)はいくらか**: **0円**(A2はクラッシュなし、1回のクリーン実行のみ)
10. **A2 Evaluation Actual Spend はいくらか**: **86.15円**(Operator-error Wasteなし)
11. **B1がA2よりCostが高い定量的理由**: 呼び出し回数(B1 77回 < A2 122回)ではなく、**課金対象の音声総尺**(B1約976.1秒 > A2約653.4秒、49%多い)が主因。B1のWasteは少数の高額segment(`full_story_part2`の6回連続ASR不合格=約309秒、`kp5_ja`の2回のhallucination暴走=約260秒超)に集中している。詳細はPart A参照
12. **segment分割数のCost影響の実測結果と、既存の「分割影響は限定的」という知見との整合性**: 整合する。Clean Cost実測値はB1(37.97円)・A2(35.56円)でほぼ同水準であり、B1の方がsegment数が1つ少ないにもかかわらずClean Costはむしろ高い。分割数そのものではなく、特定segmentの突発的なリトライ・hallucinationがCost差の主因(Part A参照)
13. **"effect"語尾切れの原因段階**: **TTS生成後のtrim(無音除去)処理**。標準生成・ASR検証はいずれも正常(ASRは"...cause and effect."を全文正しく書き起こしている)。trim処理の末尾安全マージンが0.08秒と薄く、無声破裂音("effect"語尾の/kt/)の低振幅な区間を無音とみなして削った可能性が高い。詳細と波形分析はPart C参照
14. **一般化した修正内容とregression結果 / Point One・Two再発防止の証拠 / Key Phrase訳語修正箇所 / CURRENT_SPEC変更有無**: 修正内容はPart C・D・Eに詳述。**trim安全マージンの拡大・Point番号ラベル検証・Key Phrase訳語修正はいずれもコード上は実装・単体テスト済みだが、実音声での正式なregeneration・regression確認は本報告執筆時点で未実施**(有料API呼び出しを伴うため、実行前にユーザー確認を得る方針。末尾「未完了・要確認事項」参照)。CURRENT_SPEC.mdは変更していない(ER-003-POINT-NOTIFICATION-01の既存決定はそのまま維持し、それを守るための実装側の修正のみ行った)。

---

## Part A. Cost再分析(既存ログのみによる実測ベース再構築)

### A-1. 旧方法論の問題(却下理由)

旧報告([ER-005-E2E-TTS-COST-QUALITY-01](ER-005-E2E-TTS-COST-QUALITY-01_report.md))は、「全segment数 ÷ 実際のGemini TTS呼び出し総数」という比率を実測Actual Costへ乗じてClean Costを概算していた。この方法は、リトライされたsegmentの実際の長さ・TTS/ASRそれぞれ異なる課金体系・segmentごとの試行回数のばらつきを一切反映しない。ユーザーからの指摘の通り、A2の場合「約335秒の音声をGemini TTSで1回生成しただけでも出力だけで約26.8円かかる」計算になり、これは旧報告の「Clean Cost約20.1円(TTS+ASR合計)」と矛盾する。この方法論は撤回する。

### A-2. 再構築の方法

以下のログのみを使用し、新規の有料API呼び出しは行っていない。

- `raw_usage_log.jsonl`: 全Gemini TTS・Azure STT呼び出しの成否・token数・音声秒数・timestamp
- `{b1b,a2}/audit/tts_generation_results.json`: segment別・Key Phrase別の試行記録(3種類のschema variantが混在することを確認し、それぞれに対応する解析を実装)
- `{b1b,a2}/run_summary_tts.json`: segment別の最終status(OK/STOPPED)
- 該当segmentのnarration wavファイル(JSON上に音声長データが一切残っていなかった2segmentのみ、直接wavファイルを読み測定)

**カテゴリ定義**:
- **Clean Cost**: 全23(B1)/24(A2)segmentが「1回で成功した場合」の実測ベースコスト。各segmentの「最終的に採用された(=組み立てに使われた)試行」の実測音声長 × 実測トークン単価から算出
- **Retry-Fallback Waste**: 実測Actual Cost(工程全体の合計) − Clean Cost。ASR不一致による再試行・fallback経路への切替・hallucinationによる暴走などをまとめて含む
- **Production-path Actual**: Clean + Retry-Fallback Wasteの合計。旧報告の「Actual Cost」と同一値
- **Operator-error Waste**: 本タスク実行時のディレクトリ未作成バグによりクラッシュした、B1の初回実行分(`raw_usage_log.jsonl`行0〜147)。測定対象の生成過程とは無関係な、こちらの作業ミスによる損失
- **Evaluation Actual Spend**: Operator-error Waste + Production-path Actual(この評価タスク全体で実際に支払われた金額)

### A-3. Clean Costの算出根拠

各segmentの「採用された試行」の実測音声長(trim後raw_duration_seconds)を合計し、実測平均token単価(Geminiの実測output_tokens/秒、実測平均input_tokens/回)を用いて算出した。

| | B1 | A2 |
|---|---:|---:|
| 採用試行の合計音声長(秒) | 278.80 | 267.10 |
| 実測平均 output token/秒 | 27.44 | 26.63 |
| 実測平均 input token/回 | 298.6 | 241.2 |
| segment数 | 23 | 24 |
| Clean TTS Cost(出力) | 24.48円 | 22.76円 |
| Clean TTS Cost(入力) | 1.10円 | 0.93円 |
| **Clean TTS Cost計** | **25.58円** | **23.68円** |
| **Clean ASR Cost**(Azure $1/時間×音声長) | **12.39円** | **11.87円** |

**うちB1の2segment(`point_one_heading`/`point_two_heading`)は、既存ログのschema上どの試行にも音声長データが一切保存されておらず**(8回とも`{asr_text, verdict, verified, instruction_type}`のみでtrim_info自体が存在しない)、実測復元は不可能だった。この2segmentのみ、最終的に組み立てに使われたwavファイル(`narration/point_one_heading.wav`=4.411秒、`narration/point_two_heading.wav`=3.971秒)を直接測定して代用した。この2件は「ログからの機械的再構築」ではなく「音声ファイルの直接測定」であることを明記する。

### A-4. 実測Cost内訳表(円建て)

| 項目 | B1 TTS | B1 ASR | B1計 | A2 TTS | A2 ASR | A2計 |
|---|---:|---:|---:|---:|---:|---:|
| Clean Cost | 25.58 | 12.39 | **37.97** | 23.68 | 11.87 | **35.56** |
| Retry-Fallback Waste | 63.28 | 30.31 | **93.58** | 35.35 | 15.24 | **50.59** |
| = Production-path Actual | 88.85 | 42.70 | **131.55** | 59.04 | 27.11 | **86.15** |
| Operator-error Waste | 62.86 | 31.31 | **94.18** | 0 | 0 | **0** |
| = Evaluation Actual Spend | 151.71 | 74.01 | **225.72** | 59.04 | 27.11 | **86.15** |
| 1episode総Cost(前段含む、Production-path Actual採用) | | | **141.41** | | | **96.46** |

前段(Topic Selection + Research + Writer + Support): B1 9.859円、A2 10.307円(変更なし)。

Production-path Actualの値(131.55円/86.15円)は、既存ログの全件サム(呼び出し回数・失敗ステータス問わず)から独立に算出しても131.547円/86.148円と一致しており、この合計値自体の信頼性は高い。

### A-5. B1がA2よりCostが高い理由(定量的説明)

**呼び出し回数ではなく課金対象の音声総尺が主因。** `output_audio_seconds_computed_from_pcm`の合計は、B1約976.1秒、A2約653.4秒で、B1がA2より49%多い(B1の方がGemini呼び出し回数は77回とA2の122回より少ないにもかかわらず)。

segment別のtracked試行記録を突き合わせた結果、B1のWaste(93.58円)は特に以下2segmentに集中している:

| segment | 試行回数 | 内容 |
|---|---|---|
| `full_story_part2` | 6回、全てASR不一致で不合格 | 毎回約49〜56秒(合計約309秒)を生成し直した。ASR書き起こしは"study's"→"studies"等ごく軽微な差異のみで、内容はほぼ正確(false negativeの可能性が高い、旧報告E章参照) |
| `kp5_ja`("association"の日本語meaning「関連・相関」) | 3回 | 1・2回目がそれぞれ約137秒・128秒の無関係な内容を生成する暴走(hallucination)を起こし、3回目でようやく2.76秒の正常な音声に収束した |

この2segmentだけでB1のtracked音声尺合計(約872秒)の過半(約577秒、66%)を占める。

一方A2のWaste(50.59円)は、`400 INVALID_ARGUMENT`(`"Model tried to generate text, but it should only be used for TTS..."`)という即時拒否エラーが122回中38回(31%、B1は77回中12回=16%)と高頻度に発生していることが特徴。このエラーはAPI応答自体にtoken使用量が一切含まれず(`usage_source: "N/A_FAILED_CALL"`)、課金の有無・金額は既存ログからは確認できない(下記A-6参照)。ただし`elapsed_seconds`が短い(約1秒程度、正常生成は7秒以上)ことから、生成の早い段階での拒否と推測され、**音声を最後まで生成した上でのWaste(B1のケース)よりコストへの影響は小さい**とみられる。

**この2つの現象は同一の根本原因を共有している可能性が高い**: TTSモデルが与えられたテキストをそのまま読み上げず、無関係な内容を生成しようとする挙動(300 INVALID_ARGUMENTとして拒否される場合と、拒否されず暴走生成として通ってしまう場合がある)。これは既にB1 Key Phrase 5英語("association")でも17.331秒の無関係な歌詞的内容が生成された事例として確認済みであり、今回のkp5_ja(日本語meaning側)の2度の暴走も同一パターンの再発とみられる。

**既存知見との整合性**: Clean Cost実測値はB1 37.97円・A2 35.56円とほぼ同水準(B1の方がsegment数が1つ少ない23個にもかかわらず、Clean Costはむしろ高い)であり、「segment分割数自体によるCost影響は限定的」という既存知見と整合する。B1・A2間のCost差(131.55円 vs 86.15円)を生んでいるのは分割数ではなく、上記の特定segmentにおける突発的なリトライ・hallucinationである。

### A-6. 復元できなかった情報(明示)

以下は既存ログのみでは正確に復元できなかった。推測値を正式値として扱っていない。

- **B1 `point_one_heading`/`point_two_heading`の8回の試行それぞれの音声長・課金額**: schema上一切保存されていない(A-3参照)。最終採用分のみwavファイルから直接測定して代用した
- **`400 INVALID_ARGUMENT`失敗コールの実際の課金額**: API応答にtoken使用量が含まれないため不明。$0(生成前拒否)である可能性が高いと推測するが、確証はない。A2で38回、B1で2回発生しており、もし実際に課金されている場合、A2のRetry-Fallback Wasteは本報告の推計より高い可能性がある
- **B1・A2それぞれのtracked音声尺合計(872秒/399秒)と実測raw_usage_log合計(976秒/653秒)の差分**(それぞれ約104秒・約254秒): 一部は上記の無課金データ試行(STOPPED、音声長未記録)によるものと考えられるが、完全な内訳は再構築できていない。この差分はClean/Waste計算そのもの(A-4表)には影響しない(Cleanは採用試行の実測値、Wasteは実測Actual全体からの差分算出のため)が、「どの試行が具体的に何秒だったか」という粒度でのフルレジャーは作成できていない

---

## Part C. A2 "effect" 語尾切れ調査

### C-1. 対象

A2 `point_two`segment(本文: "...so the pattern cannot be read as proof of cause and effect."、`er005_output/e2e_tts_cost_quality_01/a2/narration/point_two.wav`)の末尾で、ユーザーが"effect"の語尾(/kt/の破裂音)が欠けて聞こえると指摘。

### C-2. 追跡結果

| 段階 | 確認結果 |
|---|---|
| canonical text | `"...so the pattern cannot be read as proof of cause and effect."`(正しい) |
| TTS入力text | canonical textと同一(正しい) |
| 生成試行 | 1回で成功(`status: OK`、リトライなし) |
| ASR書き起こし | `"...so the pattern cannot be read as proof of cause and effect."`(**"effect"を完全な単語として正しく書き起こしている**) |
| trim情報 | `raw_duration_seconds: 17.051`→`trimmed_duration_seconds: 16.431`、`trailing_margin_retained_seconds: 0.08` |
| Assembly後の位置 | `281.303s〜297.734s`(timeline.json)。次segmentとの間はpauseのみで、crossfadeやAssembly側の追加trimは一切行われていない(標準wavファイルの末尾波形とAssembly後の該当区間の波形を10ms単位で比較し、完全に一致することを確認) |

**Assembly/crossfade-concatは原因から除外**: `narration/point_two.wav`(標準生成、16.431秒)の末尾波形と、完成音声`assembled/English_Your_Way_A2_SCREENTIME_CONFLICT_E2E01.wav`の該当区間(296.9〜297.9秒)の波形を10ms単位のRMSで比較したところ、完全に一致した。Assemblyは単純な連結(セグメント終了直後に無音pauseが続く)であり、追加のtrimや重なりは発生していない。

**波形分析による所見**: `narration/point_two.wav`の末尾を10ms単位で解析すると、16.35秒付近から低振幅(RMS 30〜200程度、通常発話時のRMS 1000〜4000台と比べ大幅に低い)の区間が断続的に続き、クリップ終端(16.431秒)の直前サンプルもRMS約17(完全な無音=0ではない)で、不自然に唐突な切断で終わっている。この波形パターンは、無声破裂音("effect"語尾の/k/closure→burst→/t/closure→burst)の低エネルギー区間が、trim処理の無音判定に引っかかり、末尾安全マージン(`trailing_margin_retained_seconds: 0.08秒`)が薄いために、破裂音の減衰が完了する前に切断された可能性と整合する。

### C-3. なぜ既存のASR検証がすり抜けたか

ASR検証は**テキスト内容の一致のみ**を確認しており、音声波形が最後まで完全に残っているかは一切検証していない。今回のケースでは、Azure STTが文脈・音響モデルから"effect"という単語を(末尾数十msが多少削れていても)正しく推定して書き起こしたため、内容一致検証は問題なくPASSした。**ASR検証は「その単語がおおよそ発話されたこと」の証拠にはなるが、「その単語の全サンプルが音声ファイルに残っていること」の証拠にはならない**という、既存の検証手法の限界がこの欠陥をすり抜けさせた根本原因である。

### C-4. 既存の類似事例との関係(一つの語だけの対症療法にしない根拠)

`er003_v1_repro01_main_generate.py`/`er003_b1_p9a_audio.py`のコードとコメントを確認したところ、**この種の問題は今回が初めてではなく、既に一度発見・対応済みの既知のクラスの不具合**であることが分かった:

- `ER-003-N3-ROOT-FIX-01`(2026-08-17): Key Phrase英語音声の**語頭**で、無声摩擦音("follow-up time"の/f/等)がデフォルトの安全マージン(`EN_TRIM_SAFETY_MARGIN_SECONDS = 0.08秒`)では削られる事例が見つかり、Key Phrase専用に`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = 0.20秒`へ拡大する修正が既に行われていた
- B1側の長文segment(`full_story_part1/2`・`point_one`・`point_two`・`in_one_line`)は、`er003_v1_sing01_news_tail_fix.py`の`generate_news_narration_wide_margin`経由で`LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS = 0.35秒`という、さらに広いマージンを既に使っていた(コメントに「長文の語尾フリケイティブ/decay」対策と明記)
- しかしA2側の同種segment(`topic_intro`/`point_one_heading`/`point_two_heading`/`full_story_part1/2`/`point_one`/`point_two`/`in_one_line`)は、`c.generate_english_segment_with_fallback` → `repro01.generate_narration_snippet_verified_strict`という経路を通っており、**この経路のデフォルト値は薄いままの0.08秒だった**(B1の広いマージンも、Key Phraseの拡大マージンも適用されていなかった)

つまり「語頭の無声摩擦音」「長文語尾のフリケイティブ/decay」については既に対策済みだったが、**A2の中〜長文segmentの語尾に限って対策が及んでいなかった、既知の穴**であり、"effect"という単語固有の問題ではない。

### C-5. 実施した修正(一般化した修正)

単語固有の対症療法(例: "effect"だけにパディングを足す)は行っていない。代わりに、A2の該当経路が使うtrim安全マージンのデフォルト値を、既に実績のある値(B1の長文経路と同じ0.35秒)へ引き上げた。

| ファイル | 変更内容 |
|---|---|
| `er003_b1_p3u_audio.py` | 新定数`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS = 0.35`を追加(既存の`EN_TRIM_SAFETY_MARGIN_SECONDS = 0.08`はそのまま残す。他のレガシースクリプトへの影響を避けるため) |
| `er003_v1_repro01_main_generate.py` | `generate_narration_snippet_verified_strict`のデフォルト値を`EN_TRIM_SAFETY_MARGIN_SECONDS`→`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS`へ変更。`generate_english_component_minimal_instruction`(fallback経路)も同様に変更 |
| `er003_v1_n3_01_tts_generate.py` | `_generate_a2_japanese_minimal_instruction`(A2日本語fallback経路)のtrim呼び出しに、同じ`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS`を明示的に渡すよう変更 |

この変更は、A2の`topic_intro`/`japanese_title`/`preview`/`comment_1〜4`/`point_one_heading`/`point_two_heading`/`full_story_part1〜2`/`point_one`/`point_two`/`in_one_line`(英語・日本語の両方、標準経路・fallback経路の両方)に**一律に**適用される。Key Phrase生成(`generate_key_phrase_component_verified`)は既存通り`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = 0.20`を明示的に渡しており、この変更の影響を受けない(確認済み)。

**tempo/pauseへの影響について**: Assembly側は各segmentの後に既に0.4〜1.0秒のpauseを明示的に挿入しており、マージンの拡大分(0.08秒→0.35秒、差分0.27秒)はこの既存pauseに吸収される形になるため、聞感上の不自然な間や間延びを生む可能性は低いと判断した(ただし実音声での確認は未実施、下記「未完了事項」参照)。

### C-6. 未検証事項(実音声での確認が必要)

コード修正・単体テスト(正規表現・定数の動作確認)は完了しているが、**実際にTTSを再実行して"effect"の欠けが解消されたことを確認する作業、および他segmentへのregression確認は未実施**。これには新規の有料TTS+ASR API呼び出しが必要なため、Part Aの方針(「追加のAPI呼び出しが必要な場合は自動で課金しない」)に従い、実行前にユーザーに確認する。詳細は本報告末尾を参照。

---

## Part D. Point One/Two番号ラベルのTTS到達防止

### D-1. 根本原因(再掲・確定)

`er003_v1_n3_01_scaffold_generate.py`の`split_article_text()`は、Writerが生成したMarkdownの`###`見出しを`clean_heading()`で処理するが、この関数は先頭の**記号・装飾文字のみ**(`^[\W_]+\s*`)を除去する設計であり、"Point One:"のような**単語**は除去対象外だった。WriterのプロンプトはPoint見出しの生成を指示する際「Point One相当、Point Two相当」という表現を使っており、これがLLMに「'Point One'という文字列そのものを見出しに含める」と解釈される余地を残していた。結果として、B1・A2とも見出しに"Point One: "/"Point Two: "が literal に残り、そのままTTSへ渡り、ASR検証と衝突して合格しなかった(旧報告D章)。CURRENT_SPEC.mdの`ER-003-POINT-NOTIFICATION-01`(DECIDED)は、この番号を読み上げず専用Notification音で表現する仕様を既に確定していたため、これは**仕様違反**である。

### D-2. 実施した修正(1: Writer生成契約)

`er003_v1_n3_01_articles_generate.py`のWriterプロンプト(`COMMON_BLOCK_TEMPLATE`)に、###見出しの文字列自体に番号ラベルを含めてはいけない旨、良い例・悪い例付きで明記した。

```
3. ポイント部分: Markdownの「###」見出しをちょうど2つ置いてください(Point One相当、Point Two相当)
   【重要・見出しテキストの制約】この「###」見出しの文字列自体には、
   "Point One"・"Point Two"・"Point 1"・"Point 2"・「第一に」・「第二に」
   といった番号ラベルを含めないでください。番号は本文の音声化時に
   専用のNotification音で表現する仕様(ER-003-POINT-NOTIFICATION-01)
   のため、見出しはその内容だけを短く言い表すフレーズにしてください
   (良い例: "A pattern, not a final cause" / 悪い例: "Point Two: A
   pattern, not a final cause")。
```

### D-3. 実施した修正(2: 機械的な事前検証)

LLMの出力やプロンプトの実装に依存しない、決定的(deterministic)な検証を2層追加した。

**層1(自動補正)**: `clean_heading()`に、番号ラベルのprefix("Point One/Two/1/2"、「第一に」「第二に」、各種区切り記号)を機械的に除去する処理を追加(表示用のH3見出し自体は変更せず、TTSへ渡す値のみを加工)。

**層2(最後の砦)**: `assert_no_point_number_label(text, segment_name)`関数を新設し、`generate_b1_segments`/`generate_a2_segments`内の4箇所(`point_one_heading`/`point_two_heading`/`point_one`/`point_two`)で、TTS API呼び出しの直前に必ず呼び出すよう組み込んだ。万一これらの文字列が残っていた場合、**TTS API呼び出しを一切行わずに例外で処理を停止する**。

```python
def assert_no_point_number_label(text: str, segment_name: str) -> None:
    m = _POINT_NUMBER_LABEL_ANYWHERE_RE.search(text)
    if m:
        raise RuntimeError(
            f"[ER-003-POINT-NOTIFICATION-01違反] segment={segment_name!r} のTTS入力テキストに"
            f"Point番号ラベル({m.group(0)!r})が含まれています。...")
```

Notification音自体、およびNotification→semantic heading→本文という既存の再生順序は一切変更していない(`er003_v1_n3_01_tts_generate.py`のsegment生成順序・`timeline.json`の構成ロジックは無変更)。

### D-4. テスト証拠(単体テスト、有料API呼び出し不要)

`clean_heading()`が要求された正確な見出しテキストを生成することを確認した:

| 入力(Writerが生成しうる形) | `clean_heading()`出力 | 要求されたacceptance test文言と一致 |
|---|---|---|
| `Point One: "Behavior problems" is not one single picture` | `"Behavior problems" is not one single picture` | B1 Point One: 一致 |
| `Point Two: A pattern, not a final cause` | `A pattern, not a final cause` | B1 Point Two: 一致 |
| `Point One, Warmth and conflict were not mirror images` | `Warmth and conflict were not mirror images` | A2 Point One: 一致 |
| `Point 2 - The study shows a path, not a final answer` | `The study shows a path, not a final answer` | A2 Point Two: 一致 |

`assert_no_point_number_label()`が禁止パターンを確実に検出することを確認した:

| 入力 | 結果 |
|---|---|
| `Point One: hello` | ブロック(例外送出) |
| `Point Two hello` | ブロック |
| `point 1 test`(小文字) | ブロック |
| `第二に、これは` | ブロック |
| `no label here` | 通過(正常) |
| `firstly, this is fine` | 通過(正常、"第一に"以外の通常の英語表現は誤検知しない) |

**実際のB1/A2記事本文を使ったend-to-endの再生成確認(実際に`generate_b1_segments`/`generate_a2_segments`を実行し、TTSに渡る直前のテキストを観測する)は、新規の有料TTS呼び出しを伴うため未実施。** ただし`clean_heading()`と`assert_no_point_number_label()`は純粋な文字列処理関数であり、上記の単体テストは本番コードと同一の関数・同一の正規表現を直接呼び出して確認したものである。

---

## Part E. B1 Key Phrase 日本語訳語の修正(internalizing/externalizing problems)

### E-1. 問題

B1 Key Phrase 3「internalizing problems」の日本語訳が「内向化問題・内側に表れる問題」、Key Phrase 4「externalizing problems」が「外向化問題・外側に表れる問題」となっていたが、心理学分野の標準訳語は「内在化問題」「外在化問題」であり、「内向化/外向化」は標準的でない訳語(字面から自然っぽく思いつく誤訳)だった。

### E-2. 供給元の追跡

`japanese_gloss`(`ja_gloss`)フィールドは、Key Phrase選定段階(`er003_key_words_production.py`、プロンプト`er003_v1_translator_briefs/b2_key_words_production_l_prompt_template.txt`)で生成され、後続の正規化段階(`er003_key_words_canonicalization.py`)はこの値を素通しするのみで、英語表現(`display_phrase`→`key_phrase`)の正規化のみを行っている(`japanese_gloss`には一切触れない)。生成プロンプトの該当行は「選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けてください」のみで、**専門用語に対して標準訳語を使うべきという指示が存在しなかった**ことが根本原因である。

### E-3. 実施した修正

**(1) 供給元プロンプトの修正**(一回限りの手動修正ではなく、今後同種の専門用語が出た場合にも機能する一般的な修正):

`er003_v1_translator_briefs/b2_key_words_production_l_prompt_template.txt`に以下を追加した。

```
その表現が心理学・医学・法律・経済学などの分野で確立した専門用語である場合(例:
internalizing problems, externalizing problems)は、字面から自然っぽく思いつく直訳
(例:「内向化問題」「外向化問題」)を作らず、その分野で実際に使われている標準的な
訳語(例:「内在化問題」「外在化問題」)を優先してください。判断に迷う場合は、直訳
ではなく学術的に定着した訳語を選ぶ側に倒してください。
```

**(2) 既存データの直接修正**: 以下のファイルの`internalizing problems`/`externalizing problems`の訳語を、「内在化問題・感情や心の内側に表れやすい問題」「外在化問題・行動として外に表れやすい問題」へ修正した。

- `er005_output/e2e_tts_cost_quality_01/b1b/key_phrases/keywords_canonicalized.json`
- `er005_output/support_cost_quality_01/b1/key_phrases/keywords_canonicalized.json`
- `er005_output/support_cost_quality_01/b1/key_phrases/keywords_runtime_metadata.json`(`ja_gloss`フィールド、および`portfolio_substitution_reason`内の言及箇所)
- `er005_output/e2e_tts_cost_quality_01/audio_review.html`(試聴Artifact、テキスト表示のみ修正・再公開済み)

**`tts_generation_results.json`(既存の生成ログ)は意図的に変更していない**。これは「実際に何が生成されたか」という監査記録であり、修正後の値で書き換えると当時の事実を歪めることになるため。

### E-4. 未実施事項(実音声の修正)

上記(2)のテキスト修正は、**次回このデータで音声を生成し直した際に正しい訳語が読み上げられること**を保証するものであり、**既に生成済みのB1音声(`narration/kp3_ja_charon.wav`/`kp4_ja_charon.wav`、および組み立て済みepisode)には旧い誤った訳語("内向化問題"/"外向化問題")がそのまま音声として残っている**。この2segmentの音声を正しい訳語で再生成するには新規の有料TTS+ASR API呼び出しが必要なため、Part C同様、実行前にユーザーに確認する(末尾参照)。

---

## Part G. テスト証拠まとめ

| 項目 | 証拠 | 状態 |
|---|---|---|
| Cost: segment別試行回数・TTS/ASR別コスト・リトライ理由 | Part A-3〜A-6 | 完了(既存ログのみ、追加課金なし) |
| Point: TTSへ実際に渡る最終テキスト | Part D-4のclean_heading()出力表 | 完了(単体テスト) |
| Point: Point番号ラベル0件を証明する自動テスト | Part D-4のassert_no_point_number_label()表 | 完了(単体テスト) |
| Point: Notification→見出し→本文の順序維持確認 | `timeline.json`のsegment順序を無変更で確認 | 完了 |
| 末尾音: 標準生成 vs 組み立て後の音声比較 | Part C-2(10ms単位RMS比較、完全一致) | 完了 |
| 末尾音: 修正前後の"effect"segment比較 | ー | **未実施(要有料API確認)** |
| 末尾音: 他segmentへのregression確認 | ー | **未実施(要有料API確認)** |
| Key Phrase: 訳語修正箇所 | Part E-3 | 完了(テキストのみ) |
| Key Phrase: 修正後音声の確認 | ー | **未実施(要有料API確認)** |

---

## Part F. 非対象(Non-goals、確認)

以下は本タスクで実施していない: 新TTS provider比較、Geminiモデル変更、Azure STT代替provider比較、episode長の短縮、16円目標の変更、B1/A2のcontent構造変更、OPEN-43のCLOSE、Number Treatment仕様変更、upstream(Topic Selection/Research/Writer)の再実行。CURRENT_SPEC.mdは変更していない。

---

## 未完了・要確認事項(ユーザー確認が必要)

以下は、コード修正・データ修正・単体テストまでは完了しているが、**実音声での最終確認には新規の有料TTS(+ASR)API呼び出しが必要**なため、Part Aの方針(「追加のAPI呼び出しが必要な場合は自動で課金しない」)に従い、実行前に確認する。

1. **Part C: A2 `point_two`segmentの再生成**(trim安全マージン拡大の効果を実音声で確認。想定コスト: 数円程度、1segment分のTTS+ASR)。加えて、他segment(特にB1側は元々広いマージンのため影響なし、A2の他segmentへのregression確認)を数件追加確認する場合は追加コストが発生する
2. **Part E: B1 Key Phrase 3・4の日本語meaning音声再生成**(`kp3_ja`/`kp4_ja`を正しい訳語「内在化問題」「外在化問題」で読み上げ直す。想定コスト: 数円程度、2segment分。過去にkp4_ja(旧訳語)が6回リトライしていた経緯があるため、同程度のリトライが発生する可能性がある)

いずれも小規模(合計で数十円程度を想定)だが、実行前にご確認をお願いします。
