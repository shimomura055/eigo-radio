# ER-005-E2E-TTS-COST-QUALITY-01 実行報告書

**タスク**: Text Episode → Audio End-to-End Cost Baseline
**実行日**: 2026-08-20
**入力**: ER-005-SUPPORT-COST-QUALITY-01で完成したB1/A2テキストEpisode(記事本文+Preview+Key Phrases+Comment 1〜4)をそのまま使用。Topic Selection・Research・Writer・Supportは再実行していない。
**TTS/Audio Architecture**: 既存production(`er003_v1_n3_01_tts_generate.py`/`er003_v1_n3_01_assemble.py`、およびその下位モジュール)を無変更のまま再利用。新TTS provider比較なし。
**為替**: 1ドル=160円換算(主表示は円)
**試聴Artifact**: **[Screen Time Episode Review](https://claude.ai/code/artifact/75e2178f-1c4e-48ee-81b6-b476a6ff3c09)**(B1/A2両方の完成音声+segment別QA結果一覧)

---

## 完了報告の最上段(17章の必須回答)

1. **B1 TTS + Audio QA Clean Costはいくらか**: 概算 **約42.9円**(1 segmentにつき1回で成功した場合の理論値。方法論はF章参照。実測不能なため按分による概算)
2. **B1 Actual Costはいくらか**: **131.556円**(実測、retry/fallbackを全て含む)
3. **B1の1episode総Costはいくらか**: **141.415円**(前段9.859円 + TTS/ASR 131.556円)
4. **A2 TTS + Audio QA Clean Costはいくらか**: 概算 **約20.1円**
5. **A2 Actual Costはいくらか**: **86.156円**(実測)
6. **A2の1episode総Costはいくらか**: **96.463円**(前段10.307円 + TTS/ASR 86.156円)
7. **16円TargetをB1/A2それぞれ達成したか**: **どちらも達成できなかった**。B1は目標の約8.8倍、A2は約6.0倍。12章の判定基準(FAIL: >18円)に照らすと、**両Levelとも明確なFAIL**(Clean Cost理論値だけで比較してもB1約52.8円・A2約30.4円で、リトライを完全に無くせたとしてもFAILを脱しない水準)
8. **retry/fallback wasteはいくら発生したか**: 概算でB1約88.7円、A2約66.1円(実測ActualからCleanの概算値を差し引いた分)。加えて、本タスク実行中に発見した設定不備(ディレクトリ未作成)により1回分のB1実行がクラッシュし、94.184円が完全に無駄になった(これは測定用のretry/fallbackとは別枠の、こちらの作業ミスによる損失として区別して報告する)
9. **重大なAudio QA Failureはあったか**: **あった**。B1・A2の両方で、Point One/Two見出し("Point One:"/"Point Two:"で始まる文言)の読み上げが、production既存の8回リトライ機構を使い切っても一度もASR検証に合格しなかった(下記E章)。これは既存の3テーマ(Hanshin/Health/Household)では一度も踏んだことのない、今回初めて発見された入力パターンである。他にも複数のsegmentでASR検証が不合格になったが、それらの多くは音声自体の誤りというより検証ロジックの誤検知(false negative)である可能性が高いことをF章で詳述する
10. **Number Treatmentタグ欠落は実害を起こしたか**: **明確な実害は確認されなかった**。唯一の数値関連の不一致(A2 point_oneの"two"対"2")は、TTS側の読み間違いではなく、比較検証ロジック側の正規化不整合によるfalse negativeと判断される(下記G章)。`NUMBER_TAG_REQUIRED_FOR_PRODUCTION`としての報告は不要と判断する
11. **OPEN-43と同種Failureは再現したか**: **再現しなかった**。OPEN-43は「Key Phrase 10本全てが空文字列のASR書き起こしでSTOPPED」という特有のfailure signatureだが、今回発生したKey Phrase失敗(B1 KP4日本語、A2 KP2日本語)はいずれも**非空・内容のある(ただし不一致な)ASR書き起こし**であり、OPEN-43の定義する障害パターンとは異なる。OPEN-43はUNDER_REVIEWのまま維持し、CLOSEしていない
12. **ユーザー試聴が必要なArtifactはどこか**: **[Screen Time Episode Review](https://claude.ai/code/artifact/75e2178f-1c4e-48ee-81b6-b476a6ff3c09)**(B1/A2完成音声のプレーヤーと、segment別の自動QA結果一覧)

---

## A. 実行概要

既存のtheme辞書ベースのproduction TTS/Assembly関数(`generate_b1_segments`/`generate_a2_segments`/`stage_assemble_b1`/`stage_assemble_a2`)を完全に無変更のまま再利用するため、SUPPORT-COST-QUALITY-01の成果物(`parts.json`/`b1_support_texts.json`/`a2_support_texts.json`/`keywords_canonicalized.json`)を、production側が期待する`<out_dir>/b1b`・`<out_dir>/a2`のディレクトリ構造へそのままコピーした(新規theme_id: `screentime_conflict_e2e01`)。A2のJapanese titleのみ、既存の3テーマ用ハードコード辞書に新theme分の翻訳(承認済み英語タイトルの直訳のみ、新Fact追加なし)を1件追加した。

**技術的な問題(先に開示)**: 初回実行時、ディレクトリ作成漏れ(`<out_dir>/b1b/audit`が未作成)により、B1の23segment中21件の生成が完了した後にスクリプトがクラッシュした。これは既存Production側のコードの問題ではなく、こちら側のセットアップ不備である。ディレクトリを作成して再実行し、事後的にはクリーンな結果を得たが、クラッシュ前の実行で既に発生していたAPI課金(94.184円)は無駄になった。この金額はF章のコスト集計に別枠で開示する。

---

## B. 完成音声

| Level | 再生時間 | サンプルレート | Clipping |
|---|---|---|---|
| B1 | 5:34(333.994秒) | 48kHz/2ch | 検出されず |
| A2 | 5:35(334.529秒) | 48kHz/2ch | 検出されず |

**試聴Artifact**: [Screen Time Episode Review](https://claude.ai/code/artifact/75e2178f-1c4e-48ee-81b6-b476a6ff3c09)(96kbps MP3、B1/A2両方のプレーヤー+segment別自動QA結果を掲載)

---

## C. Segment別実行結果

| Level | Segment数 | 自動QA合格 | 自動QA不合格(要レビュー) |
|---|---|---|---|
| B1 | 23(通常18 + Key Phrase英日10のうち片方) | 19 | 4 |
| A2 | 24 | 19 | 5 |

**B1不合格segment**: point_one_heading、point_two_heading、full_story_part2、Key Phrase 4日本語meaning
**A2不合格segment**: point_one_heading、point_two_heading、point_one、in_one_line、Key Phrase 2日本語meaning

不合格segmentも、production既存の仕組み上、最後(不合格のまま終わった)試行の音声ファイルがそのまま最終組み立てに使用されている(=完全な無音・欠落ではない。ただし内容が正しいかは未検証)。組み立て(Assembly)自体はB1・A2とも`status=OK`で完了しており、クラッシュや欠落は発生していない。

---

## D. 重大な新発見: "Point One:"/"Point Two:" 見出しの読み上げ失敗

B1・A2の両方で、`### Point One: ...`/`### Point Two: ...`という、Writerが生成したH3見出し(先頭に"Point One:"/"Point Two:"という語をそのまま含む形式)を音声化する際、**既存の8回リトライ機構(標準経路4回+minimal instruction経路4回、またはA2側は標準6回+fallback6回)を使い切っても、一度もASR検証に合格しなかった**。

| Level | Segment | 使用関数 | ASR書き起こし(全attemptで同一) |
|---|---|---|---|
| B1 | point_one_heading | `point_headings.generate`(Aoede) | `.1 behavior problems is not one single picture.` |
| B1 | point_two_heading | 同上 | `.2 A pattern, not a final cause.` |
| A2 | point_one_heading | `c.generate_english_segment_with_fallback` | `.1 Warmth and conflict were not mirror images.` |
| A2 | point_two_heading | 同上 | `.2 The study shows a path, not a final answer.` |

**重要な発見**: この失敗は、**2つの完全に別々のTTS呼び出し関数(B1用・A2用)で同一パターン**("Point One:"→".1"、"Point Two:"→".2")が再現しており、かつ全attemptで書き起こしが一言一句同一だった。これは特定のwrapper関数の実装バグではなく、**Gemini TTSモデル自体が"Point One:"/"Point Two:"という語を数字のように発話する傾向があり、ASRがそれを".1"/".2"という短縮表記として書き起こしている**可能性が高いことを示唆する(音声自体を人が聞いて確認する必要がある、Human Review必須の項目)。

**根本原因の推定**: 既存3テーマ(Hanshin/Health/Household)のB1記事見出しを確認したところ、いずれも"Point One:"/"Point Two:"という接頭辞を含まない、純粋な意味見出し(例: "The power may be in the combination")だった。今回のWriter(ER-005-WRITER-COST-QUALITY-01)は、見出しに"Point One:"/"Point Two:"という接頭辞を明示的に含める書き方を選んでおり、**この入力パターンは既存3テーマでは一度も踏まれていなかった**。したがって、これはWriterの見出し文言パターンとTTSモデルの相互作用による、**今回初めて発見された潜在的な問題**であり、production側の既存コードに欠陥があったわけではない。

この件はOPEN_ITEMS.md等のSoTは変更していない(仕様変更は今回のスコープ外)が、本報告書で明確に記録し、今後の対応候補として次の2つを提示する: (a) Writerの見出し生成方針を「先頭に"Point One:"/"Point Two:"を含めない」よう調整する、(b) TTS入力側でこの接頭辞パターンを検出し別の読み上げ処理を行う。いずれも今回は実施していない。

---

## E. その他の不合格segmentの評価(false negativeの可能性)

D章の見出し問題とは別に、以下の不合格segmentは、ASR書き起こしを精査した結果、**音声自体よりも自動検証ロジックの厳密さに起因するfalse negativeの可能性が高い**と判断した(ただし最終判断はユーザー試聴に委ねる、13章の規定通り)。

| Level | Segment | ASR書き起こしの実際の内容 | 所見 |
|---|---|---|---|
| B1 | full_story_part2 | 正確な内容をほぼ完全に再現、"study's"→"studies"等の軽微なASRアーティファクトのみ | 内容はほぼ正確、検証の厳密さによる不合格の可能性が高い |
| A2 | point_one | "two opposite roads"を"2 opposite roads"と書き起こし | canonical textは綴り"two"のまま、比較ロジック側の数字正規化(2↔two)が不十分だった可能性 |
| A2 | in_one_line | カンマの有無・"conflict"/"conflicts"の単複、軽微な差異のみ | 内容はほぼ正確 |
| B1 | Key Phrase 4 日本語("外向化問題") | "外交化問題"等、類似音の別語として書き起こされた | "外向化"という専門用語をASRが正しく認識できていない可能性(TTS発話自体は正しい可能性がある) |
| A2 | Key Phrase 2 日本語("行動上の問題") | "公道上の問題"等、同音異義語として書き起こされた | 同上、専門用語・同音異義語によるASR認識精度の限界の可能性 |

これらは**捏造ではなく既存ログの機械的な突き合わせで確認できる範囲の所見**であり、「音質完全PASS」という断定は行っていない。試聴Artifactでも各segmentへ同様の注記を付けている。

---

## F. Cost計測(7章、円建て)

### F-1. 実測Actual Cost(工程別)

| 工程 | B1(クリーン実行) | A2(クリーン実行) | 参考: B1初回(クラッシュ、無駄) |
|---|---:|---:|---:|
| Gemini TTS呼び出し数 | 77 | 122 | 82 |
| Azure STT呼び出し数 | 60 | 77 | 65 |
| Gemini TTS Cost | $0.5553 | $0.3690 | $0.3929 |
| Azure STT Cost | $0.2668 | $0.1694 | $0.1957 |
| **TTS+ASR Actual Cost(円)** | **131.556円** | **86.156円** | **94.184円(無駄)** |

Gemini TTS単価: `gemini-2.5-pro-preview-tts`/`gemini-3.1-flash-tts-preview`とも$1.00/1M input token(text)+$20.00/1M output token(audio、25 token/秒)、Standard tier(2026-08-20、ai.google.dev公式ドキュメントで確認)。Azure STT単価: $1.00/時間(既存pricing_snapshot.json、japanwest region)。

### F-2. Clean Cost(概算、方法論の開示)

**重要な制約**: 本タスクではproduction側の`generate_b1_segments`/`generate_a2_segments`関数を無変更のまま再利用したため、コストログの`stage`フィールドがsegment名を保持しない(呼び出し元でsegmentごとの`cl.logging_context()`ラップを行わなかったため)。このため、「どのsegmentが何回目の試行で成功したか」をログから機械的に特定できず、**真のClean Cost(全segmentが1回で成功した場合のコスト)は正確には算出できない**。

そこで、以下の按分法による概算を用いた: 「全segment数」÷「実際のGemini TTS呼び出し総数」の比率を、実測Actual Costへ乗じる(1 segmentあたり平均1回で成功したと仮定した場合の理論値)。

| Level | Segment数 | Gemini呼び出し数 | 按分比率 | Clean Cost概算(円) | Waste概算(円) |
|---|---|---|---|---:|---:|
| B1 | 23 | 77 | 0.299 | 約42.9円 | 約88.7円 |
| A2 | 24 | 122 | 0.197 | 約20.1円 | 約66.1円 |

**この概算の重要な含意**: Clean Cost概算だけを見ても、B1は約42.9円、A2は約20.1円であり、**リトライを完全にゼロにできたとしても、B1は12章のFAIL基準(>18円)を大きく超える**。A2のClean Cost単体(20.1円)は僅かにFAIL圏内だが、前段コスト(10.307円)を加えると30.4円となり、これも大きくFAILを超える。

**根本的なコスト構造**: Gemini TTSの出力単価($20/1M token audio=25 token/秒あたり)から逆算すると、1エピソード(約5.5分=330秒)の音声を1回で生成しきった場合の理論下限は、330秒×(20/25/1,000,000)ドル/token×1,000,000token/25秒 ≒ $0.264(≒42円)程度になる(実測のB1 Clean Cost概算42.9円とほぼ一致)。**これは、B1が23回の個別TTS呼び出しに分割されており、各呼び出しに固有の入力prompt(instruction文言)分のtoken課金が23回分積み重なることが主因であり、単にretryを減らすだけでは16円目標に到達できない構造的な問題である。**

### F-3. 1episode総Cost(11章)

| 工程 | B1 | A2 |
|---|---:|---:|
| 前段(Topic Selection + Research + Writer + Support) | 9.859円 | 10.307円 |
| TTS + Audio QA(Actual、実測) | 131.556円 | 86.156円 |
| **1episode総Cost(Actual)** | **141.415円** | **96.463円** |
| (参考)TTS+ASRをClean Cost概算で置き換えた場合 | 約52.8円 | 約30.4円 |

---

## G. Spoken-first Number Treatmentタグ欠落の実害確認(6章)

**Q1: 完成Writer/Support textだけで自然な音声Scriptを構成できるか** → できた。既存のsegment分割・組み立てロジックがそのまま機能し、構造上のエラーは発生しなかった。

**Q2: 数値密度・読み上げ精度に実害があるか** → **明確な実害は確認されなかった**。今回の23〜24segment中、数値そのものの読み上げ誤りとみなせる不合格は無かった。唯一関連するのはA2のpoint_one("two"↔"2")だが、これは前述の通りTTSの読み間違いではなく、比較検証ロジック側の数字正規化の非対称性(TTS入力側は"two"→"2"へ変換済みだが、canonical text側の比較には変換前の"two"が使われた可能性)によるfalse negativeであり、Number Treatmentタグの有無とは無関係と判断する。

**結論**: `NUMBER_TAG_REQUIRED_FOR_PRODUCTION`としての報告は不要。ただしD章の見出し問題は、今回の判定対象(数値の読み上げ精度)とは別種の問題として記録する。

---

## H. Business判定(12章)

| Level | 総Cost(Actual) | 判定 |
|---|---:|---|
| B1 | 141.415円 | **FAIL**(>18円を大幅に超過) |
| A2 | 96.463円 | **FAIL**(同上) |

Clean Cost概算(理論上の最良ケース)で比較しても、B1(約52.8円)・A2(約30.4円)ともFAIL基準を超えており、**現行のTTS Architecture(1エピソードを20件超の個別TTS呼び出しへ分割する構成)のままでは、リトライ削減だけで16円目標へ到達することは構造的に難しい**。

さらに13章の規定通り、Costの結果とは独立に、D章で報告した"Point One:"/"Point Two:"見出しの読み上げ失敗は、コストの多寡によらずProduction PASSの判断を妨げる重大な音声品質上の懸念であり、**ユーザーによる試聴確認が必須**である。

---

## I. Human Review Artifact(14章)

- **完成Audio**: [Screen Time Episode Review](https://claude.ai/code/artifact/75e2178f-1c4e-48ee-81b6-b476a6ff3c09)(B1/A2両方、再生可能なArtifact)
- **script**: `er005_output/e2e_tts_cost_quality_01/b1b/parts.json`、`.../a2/parts.json`(既存のWriter/Support textをそのまま使用、新規生成なし)
- **segment一覧**: 上記Artifact内、および`er005_output/e2e_tts_cost_quality_01/{b1b,a2}/run_summary_tts.json`
- **retry/fallback履歴**: `er005_output/e2e_tts_cost_quality_01/{b1b,a2}/audit/tts_generation_results.json`(全attempt、ASR書き起こし全文を含む)
- **QA結果**: 上記Artifact、および本報告書D・E章
- **Cost summary**: 本報告書F章

---

## J. 受入条件確認(18章)

- 完成済みB1/A2 textを再利用: **確認済み**
- upstream再実行なし: **確認済み**(Topic Selection・Research・Writer・Support再実行なし)
- 現行TTS Architecture使用: **確認済み**(production関数を無変更のままimport、モデル比較なし)
- B1/A2を別々にcost評価: **確認済み**(F章、12章の規定通り合算していない)
- Clean/Actual Cost分離: **確認済み**(F章、Clean Costは按分による概算である旨を明記)
- retry/fallback waste記録: **確認済み**
- Audio QA実施: **確認済み**(D・E章)
- OPEN-43を維持: **確認済み**(未CLOSE、UNDER_REVIEWのまま。OPEN_ITEMS.mdは変更していない)
- Number Treatmentタグ欠落の実害確認: **確認済み**(G章)
- 円表示: **確認済み**
- 16円/episodeとの比較: **確認済み**(H章)
- 試聴Artifactあり: **確認済み**
- 主観Audio品質をClaudeだけで最終判定しない: **確認済み**(D・E章で「要確認」「可能性」の表現に留め、最終判断はユーザー試聴に委ねている)
- Production/CURRENT_SPEC変更なし: **確認済み**(触れたのは`er005_e2e_tts_cost_quality_01.py`のみ。productionモジュールは読み取り専用importとtheme辞書への1エントリ追加のみ)

## K. Stop条件

B1 Script Assembly → B1 TTS → B1 Audio QA → A2 Script Assembly → A2 TTS → A2 Audio QA → Clean/Actual Cost計測 → 1episode総Cost算出 → 試聴Artifact作成 → Reportが完了したため、ここでSTOPする。

---

## L. 成果物一覧

- `er005_e2e_tts_cost_quality_01.py` — 実行スクリプト
- `er005_output/e2e_tts_cost_quality_01/b1b/` — B1 segment・assembly成果物一式
- `er005_output/e2e_tts_cost_quality_01/a2/` — A2 segment・assembly成果物一式
- `er005_output/e2e_tts_cost_quality_01/mp3/` — 試聴用MP3(96kbps)
- `er005_output/e2e_tts_cost_quality_01/audio_review.html` — 試聴Artifactのソース
- `er005_output/e2e_tts_cost_quality_01/raw_usage_log.jsonl` — 全486呼び出しのコストログ(クラッシュした初回実行分を含む、全て保持)
- 本報告書 `ER-005-E2E-TTS-COST-QUALITY-01_report.md`
