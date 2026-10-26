# Claude Codeへの指示｜Family XYZ TTS Retry・Fallback・Local Rewrite統一・Production Wiring

## 1. 目的・Status・到達目標

Family X／Y／Z、Standard／AdvancedのTTS再試行・Fallback・Local Rewrite（以下LR）を、ユーザーが正式承認した共通仕様へ統一する。

**Status：APPROVED_FOR_PRODUCTION**
**到達目標：対象Family・音声部位すべてでPRODUCTION_WIRED**

最優先順位は、品質（Q）＞完成速度（D）＞量産単価（C）。

既存の49行の音声部位別星取表と関連する承認済み仕様を起点とし、共通処理の活用によって不要なFamily別分岐・重複実装を減らすこと。

## 2. 正式採用する基本フロー

原則として、品質NG時は次の順序とする。

1. 通常StyleでTTS① → NG
2. 同じStyleでTTS② → NG
3. **180秒（3分）待機**
4. Fallback Styleに切り替えてTTS③ → NG
5. LRありの場合：問題箇所を1回だけ書き換え、①〜④と同じ3回構成で再生成する
6. LR後もNGならHuman Review／STOP
7. LRなしの場合：最初のTTS③がNGならHuman Review／STOP

**重要条件**

- 1回目または2回目がPASSすれば、待機も後続の生成も実施しない。
- 180秒待機は、各3回構成において2回目NG後、3回目を実行する直前にのみ発生する。
- LRあり：最大6回の品質再生成、待機最大2回＝計360秒。
- LRなし：最大3回の品質再生成、待機最大1回＝180秒。
- LRは最大1回。LR後に再度LRへ入る再帰処理は禁止。
- LR後の原稿に対しても、元の品質Gate・ASR・音声QAを適用する。
- 技術的エラーに対する既存の即時再試行は、品質NGによる上記回数とは別枠で維持する。安全上限・STOP条件も維持する。
- 3分待機の目的は、連続したTTS生成を避けて間隔を空けること。品質基準の緩和は行わない。

今後、実績を観測して単純なRetryの効果が乏しいと確認できた場合は回数削減を検討するが、今回は変更しない。

## 3. 音声部位別の正式仕様

| 対象 | 3回目のFallback | LR | 最大TTS |
|---|---|---|---|
| XYZ Standard 英語本文・Comment等 | 既存の短文Style | あり | 6回 |
| XYZ Advanced 英語本文・Comment等 | **短文Styleを新たに適用** | あり | 6回 |
| Z Standard／Advanced セリフ（文脈・感情方式） | 承認済みの従来Dialogue Style | 現状なし | 3回 |
| XYZ Standard 日本語音声 | 既存の日本語短文Style | なし | 3回 |
| XYZ Standard／Advanced Key Phrase英語 | ENGLISH_LOCK | なし | **4回維持** |
| XYZ Advanced KP英語解説（音声が存在する経路） | 既存短文Styleの適合性を確認。不可なら同一Style | 現状なし | 3回 |
| Z Standard／Advanced 冒頭英語 | 短文Style | あり | 6回 |

**Key Phrase英語は正式承認済みの「通常2回＋ENGLISH_LOCK 2回」を維持する唯一の回数例外。**

この4回構成でもFallback移行前、すなわち通常2回NG後に180秒待機を適用する。後段のENGLISH_LOCKは既存どおり最大2回実行する。

### 部位・Familyの整合確認

既存49行を必ず再照合し、Preview、Comment、Full Story、chunk、In One Line、Topic Intro、Family Yの各Voice、Key Phrase、日本語等の適用漏れがないようにする。

特に以下を確認すること。

- **Family YのVoice音声**：英語本文と同一の共通処理が適用できるか確認し、承認済みの再試行仕様に整合させる。ただし、Voiceの既定Styleそのものを無断変更しない。
- **Family Zのセリフ**：文脈・感情Styleを2回、3分待機後に従来Dialogue Styleを1回。LRは今回追加しない。
- **Family Zの冒頭英語**：未分類によるFallback・LR未適用を解消し、共通仕様を適用する。
- **Advanced英語**：従来の「品質NGではStyleを変えず、技術エラー時のみ切替」を改め、3回目には短文Styleへ切り替える。
- **Advanced KP英語解説**：適用対象に実際のTTS音声が存在するか正式経路を確認する。存在する場合のみ本仕様を適用し、存在しない学習テキストを新たに音声化しない。

KP英語解説の短文Styleが適さない場合は、この部位のみ「同一Style2回→180秒待機→同一Style3回目→HR」とする。適合性確認はClaude/Fableが自律的に行い、不要な新Style・新Promptの開発は行わないこと。

## 4. LRの扱い・安全条件

LRの**有無は現行を基本とし、今回はLR対象の新規拡張を目的としない**。

ただし、Z冒頭英語のように、承認済み対象でありながら部位判定の不備で適用されていなかったものは、今回の統一対象として是正する。

- LRで書き換えるのはNGに関係する局所部分に限定。
- 既存の意味保持・書換え品質Gate・本文整合の安全条件を維持。
- LR後の再TTSは最大3回。再LRなし。
- 話者・Voice・速度・承認済みStyle・chunk構造を保持。
- 書換えによる音声と表示本文の関係、HR Lock、regeneration／resumeとの整合を確認。
- 既存のLR再入（OPEN-376）とStyle脱落（OPEN-312等）を、今回の共通化で解消する。
- ASR一致でも繰り返し・言い淀みQAでNGとなるケースを適切に扱い、LRが適用不可能な場合の無益な後続処理を避ける。ただし、品質NGの再試行フローや180秒待機を勝手に省略しない。

日本語・Key Phrase英語・Zセリフ等、今回LRなしとした部位へ独断でLRを追加しないこと。

## 5. QCD・実装上の方針

1. **品質**：承認済みのASR判定、自然な発話、繰り返し・言い淀み検査、Human Review Lock等を維持する。
2. **速度**：独立作業は並列化し、不要な待機・日付分割を行わない。仕様上必要な180秒待機のみ実施する。
3. **量産原価**：目標70円／記事セットを維持するため、再試行・LR・ASR増加による原価影響を計測する。失敗時のみ追加処理を実行し、PASS済み音声を無駄に再生成しない。
4. **実装の簡素化**：既存の共通関数を再利用し、Familyごとに別ロジックを増殖させない。
5. **既存仕様との整合**：旧10分待機、旧3回／4回の数え方、旧LR後1回、Advの技術エラー時のみのStyle切替など、今回置換された条件が正式経路やValidatorに残らないよう確認する。
6. **旧仕様の撤去**：新仕様と矛盾する不要なPrompt・分岐・検査・文書を整理し、Dangling Referenceを残さない。

モデルやVoiceそのものの変更は今回のScopeに含めない。

## 6. Production Wiring・受入条件

Family X／Y／Zの正式Production初回経路および以下を対象とする。

- Retry／Fallback／LR／Human Review
- regeneration／resume／既存音声の再利用
- Standard／Advanced
- chunk経路
- STOP・予算上限・技術エラー時の処理

**必須検証**

- TTS①でPASS → 追加生成・待機なし
- TTS②でPASS → 待機なし
- TTS①② NG → 180秒待機 → Fallback③
- LRなし → ③NG後にHuman Review
- LRあり → ③NG後にLRを1回 → 書換え後の3回構成 → 最終NGならHR
- LR再入なし、最大回数を超えない
- KP英語のみ4回構成と180秒待機の整合
- Std／AdvのStyle、Voice、速度保持
- LR後のQA・ASR・採用判定
- runtimeでのFallback Style切替と実際の待機時間の証拠
- Human Review Lock／キュー／Assemble BLOCK／STOP
- retry／regeneration／resumeでの重複生成・重複待機防止

既存テストを再利用し、必要十分なRegression・Validator・integration testを追加すること。

本番相当の正式runtime evidenceをFamily・レベル別に取得し、単なるDEVテスト成功で完了扱いにしない。

actual model_id、routing、Style／Prompt、試行回数、待機時間、LR実行回数、最終判定を検証可能にする。

Fable独立受入を実施し、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／必要なGit反映を完了する。

**全条件の確認後に限り、Family別にPRODUCTION_WIREDと判定する。**

## 7. 自律判断・STOP条件

承認済み仕様・品質・予算・Scope・Gate内の技術問題は、Claude/Fableが原因究明から修正・検証まで自律的に実施すること。

ユーザー判断を求めるのは、重要な品質・仕様変更、重大なQCDトレードオフ、予算・Scope超過、解決不能なblocker、新仕様の追加等に限る。

今回の共通化について、軽微な技術事項を逐一ユーザーへ転送しない。

既存案件別予算と、開発費原則1,000円／日（JST）を遵守する。必要な正式runtime検証の費用は、既存承認枠内で効率的に配分する。

安全上限・Human Review Lock・STOP条件は維持する。承認範囲外の新たなProduction仕様を発見した場合、無断で採用しないこと。

## 8. 最終報告

ユーザーが全体を把握できるよう、以下を簡潔に提示すること。

1. **統一後の星取表**：Family・Std/Adv・音声部位ごとに、①②③・Fallback・180秒待機・LR・HR・最大回数を表示
2. **変更前後の差分**：統一によって何が変わったか
3. **Family別のProduction Wiring Status**
4. **Fallback／LRの実走証拠とテスト結果**
5. **量産原価・制作時間への影響**
6. **Fable独立受入結果**
7. **残る未完了事項・判断待ち事項**

**目標は、例外の少ない共通仕様に整理し、品質を守りながら最速でProduction Wiringを完成させること。**

ユーザーが決定済みの仕様について、再承認を求めないこと。

(原文ここまで)
