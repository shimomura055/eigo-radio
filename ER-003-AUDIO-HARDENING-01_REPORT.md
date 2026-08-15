# ER-003-AUDIO-HARDENING-01 実行報告(TTS/ASR共通安定化＋仕様継承チェックリスト)

**管理ID: ER-003-AUDIO-HARDENING-01**
**実施日: 2026-08-15**
**目的: 実装の安定化のみ。サービス仕様(CEFR仕様・B1/B2共通化決定・
記事構造・Audio UX仕様等)は一切変更しない**

## A. Root Causes(4件の技術的問題、個別記事の一回限りの修正だった状態)

ER-003-B1-SCAFFOLD-AUDIO-01でA02固有の応急処置として発見・修正した
問題を、再発防止可能な形で一般化する対象として棚卸しした。

| # | 問題 | 発生条件 | 元の対処(A02固有・一回限り) |
|---|---|---|---|
| 1 | TTS入力中のMarkdown強調記号(`**`)・カーブ引用符 | 記事本文に`**"default"**`型の強調表現が含まれる場合、Gemini TTSが`400 INVALID_ARGUMENT: Model tried to generate text, but it should only be used for TTS`を返す | `strip_markdown_emphasis`をA02専用scriptに直書き |
| 2 | 自己言及的な一文("The word default matters."型) | 上記1を解消した後も特定の文でTTSが同じ400エラーを返し続ける | MINIMAL_INSTRUCTION_PREFIX経路への個別fallbackをA02専用scriptに直書き |
| 3 | ASR検証の文字列比較方式(`text[:40] in asr_text`) | 改行混入・単語途中切断・ハイフン複合語のASR正規化・コンマ有無で偽陰性 | `expected_words_present`(単語列連続部分列一致)をA02専用scriptに直書き |
| 4 | 英国綴り/米国綴り差(personalised/personalized) | Azure STTがAmerican綴りへ正規化して書き起こすため、British綴り原文との文字列比較が恒常的に不一致 | Key Phrase 1件だけ`tts_text`フィールドでAmerican綴りに個別置換 |

いずれも、発生時点ではA02という1記事専用のscript内に直書きされており、
他のA2/B1/B2音声制作へ機械的に再利用できる形になっていなかった。

## B. TTS Input Normalization(何を・どこで)

新規共通モジュール[er003_audio_tts_asr_safety.py](er003_audio_tts_asr_safety.py)
の`strip_markdown_for_tts(text)`として一般化した。

- **適用場所**: TTSアダプター呼び出しの直前のみ。関数は入力を書き換えず
  コピーを返すため、呼び出し側が明示的に「TTS用の使い捨てコピー」として
  扱う設計になっている
- **絶対に変更しないもの**: カノニカル記事本文、表示用テキスト、
  Fact-QA用テキスト(4つの独立した概念として維持)
- 自己言及的な一文の検出は、`looks_self_referential`という簡易
  ヒューリスティックとして提供したが、これは確定的な判定ではなく
  ログ・優先度判断の補助情報にとどめている(過信していない)

## C. ASR Validation Normalization(何を許容し、何を許容しないか)

`validate_asr_match(expected_text, asr_text, n=6, asr_error=None)`として
実装した。

**許容する(NORMALIZED_MATCHとしてPASSにする)**:
- 大文字小文字の違い
- 句読点・改行・ハイフン複合語の表記揺れ
- 英国綴り/米国綴りの体系的な差異のみ(`-ise`/`-ize`、`-ised`/`-ized`、
  `-ising`/`-izing`、`-isation`/`-ization`、`-our`/`-or`)

**絶対に許容しない(必ずFAILにする)**:
- 語句の欠落・追加
- 数字の違い
- 否定の有無(意味が反転するケース)
- 無関係な内容(ASRが別の文章を書き起こした場合含む)
- 英国/米国綴り以外の綴り差(例: "colour"のような無関係な単語への
  すり替えは、たとえ`-our`/`-or`ルールの対象文字列に偶然近くても、
  単語全体が一致しない限り通さない)

英国綴り/米国綴りの吸収は、体系的な接尾辞パターンのみに限定し、
語彙単位の大規模同義語辞書は作らなかった(過剰正規化の防止を優先)。

## D. Validation Algorithm(誤PASS・誤FAILの防止)

判定は3段階の`verdict`(`EXACT_MATCH`/`NORMALIZED_MATCH`/`FAIL`)で
返す。各回の判定結果には以下を必ず含め、監査可能にした。

```
expected_text, normalized_expected_words,
asr_text, normalized_actual_words,
verdict, passed, reason
```

ASR未取得(空文字列・None)・API/認証エラー(`asr_error`引数で明示)は、
どちらも無条件で`FAIL`となり、`reason`に"PASS forbidden"という文言が
必ず入る設計にした(Azure STT 401のような認証障害を誤ってPASS扱い
してしまう事態を、実装レベルで構造的に禁止している)。

**開発中に自己発見したバグ**: 回帰テスト作成中に、`_subsequence_match`
内の単語比較が`actual_words[j]`(常にリスト先頭付近だけを見る誤り)に
なっており、`actual_words[i + j]`であるべきだったバグを検出した
(`test_hyphenated_compound_word_normalized_still_passes`が失敗した
ことで発覚)。この回帰テストマトリクス自体が、実装直後に実際にバグを
1件検出・修正させており、要求された「テストで安全性を確認する」という
目的を実際に達成している。

## E. Regression Tests(全ケース・期待値・実際)

[er003_test_audio_tts_asr_safety.py](er003_test_audio_tts_asr_safety.py)
に25件、既存の[er003_test_b1_scaffold_audio_01.py](er003_test_b1_scaffold_audio_01.py)
12件、計37件。全件成功。

| ケース | 期待 | 実際 |
|---|---|---|
| Markdown `**default**` | TTS-safe input produced | PASS |
| straight quotes | 無変更のまま正常処理 | PASS |
| curly quotes | 除去されて正常処理 | PASS |
| `The word "default" matters.`型 | 自己言及ヒントとして検出 | PASS |
| primary失敗→fallback成功 | fallback経路で成功を返す | PASS |
| primary/fallback両方失敗 | STOPPED(human_review_required) | PASS |
| personalised vs ASR "personalized" | validation PASS(NORMALIZED_MATCH) | PASS |
| capitalization difference | PASS | PASS |
| punctuation difference | PASS | PASS |
| exact match | EXACT_MATCH | PASS |
| word omission | FAIL | PASS |
| number changed | FAIL | PASS |
| negation added | FAIL | PASS |
| negation removed | FAIL | PASS |
| unrelated sentence | FAIL | PASS |
| empty ASR | FAIL | PASS |
| None ASR | FAIL | PASS |
| Azure auth error(asr_error指定) | FAIL、PASS禁止の理由付き | PASS |
| 長時間無関係読み上げ(hallucination型) | FAIL | PASS |
| ハイフン複合語 | 正規化後PASS | PASS(バグ修正後) |
| 監査trailの全フィールド存在 | 7フィールド全て含む | PASS |
| 綴り正規化の過剰適用防止(colour⇔curfew) | FAIL(内容が異なる) | PASS |

実際のTTS層での修正効果(400エラー解消)自体は、本ステージでは新規の
TTS呼び出しを行っていないため再検証していない。ER-003-B1-SCAFFOLD-
AUDIO-01/02実行時の実TTS+実ASRでの検証結果
(各`audit/segment_generation_results.json`)を根拠として引き続き有効
とみなしている。

## F. Shared Usage(A2/B1/B2からの再利用方法)

`er003_audio_tts_asr_safety.py`はProduction本体のTTS/ASR実装
(`er003_b1_p9a_audio.py`、`er003_v1_repro01_main_generate.py`等)を
importしない。呼び出し側が実際のTTS関数をcallableとして
`generate_tts_with_fallback(text, out_path, primary_fn, fallback_fn)`
へ渡すオーケストレーション方式にしたため、

- 既存script(A2/B1どちらも)は、このモジュールをimportして
  `strip_markdown_for_tts`と`validate_asr_match`をそのまま使える
- Production本体側への変更は不要
- 大規模なパイプライン統合・置き換えは今回行っていない(非スコープ)

## G. Audio Inheritance Checklist(場所・構成)

[ER-003_AUDIO_INHERITANCE_CHECKLIST.md](ER-003_AUDIO_INHERITANCE_CHECKLIST.md)
として新規作成した。A. Content/Structure、B. Audio Shell、C. Key
Phrase、D. Spoken-first(Number Treatment/Point Balance)、E. Text
Integrity/Fact Safety、F. TTS/ASR、G. Post-processingの7節構成。
`APPLICABLE`/`NOT_APPLICABLE`/`VERIFIED`/`NEEDS_DECISION`のステータス
語彙と、Preflight/Implementation/Completionの3段階運用モデルを持つ。

## H. SoT Relationship(チェックリスト≠仕様)

チェックリスト冒頭に明記した通り、[CURRENT_SPEC.md](CURRENT_SPEC.md)・
[DECISION_LOG.md](DECISION_LOG.md)・各段階の最終承認済みscript・
[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)が正であり、このチェック
リストはそれらへのリンクを張るのみで、内容を複製・言い換えていない
(将来SoTが更新された際にチェックリストの文言だけが古くなって食い違う
リスクを避けるため)。

## I. Lessons Learned(このセッションで実際に起きた継承ギャップ)

チェックリストH節に記録した通り、責任追及ではなく再発防止の教訓として:

1. **Number Treatmentの非継承**: CEFR-DIRECT系タスクで、既決の
   Number Treatment枠組みがスコープに明示継承されなかった
2. **Audio Shellの非継承**: B1最初の完成音声試作(AUDIO-01)で、
   Intro/Outro/Notification等のAudio Shellがスコープに含まれず、
   Shell統合はAUDIO-02という別段階に持ち越された

「暗黙の継承は漏れる。明示的なPreflightが必要」という結論を、
チェックリストの存在理由として記録した。

## J. Non-scope / Production非変更確認

- TTS voice選定、Audio Dynamics、CEFR仕様、記事本文内容、Key Phrase
  選定ロジック、WPM仕様、SFX仕様、Audio Shell仕様そのもの: いずれも
  変更していない
- Production本体(`CURRENT_SPEC.md`、各audio/TTSモジュール本体)への
  組み込み・大規模refactorは行っていない。新規独立モジュール
  (`er003_audio_tts_asr_safety.py`)を追加しただけであり、既存script
  (`er003_v1_b1_scaffold_audio_01_generate.py`等)からの利用は今回は
  行っていない(次回以降の音声制作で、任意に採用可能な状態)
- ER-003-B1-SCAFFOLD-AUDIO-02は本ステージ着手前に完了・commit・push
  済みであり、本ステージの内容による変更は加えていない(ユーザー
  指示通り)

## K. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## 対象ファイル一覧

| ファイル | 内容 |
|---|---|
| `er003_audio_tts_asr_safety.py`(新規) | TTS入力正規化・ASR検証正規化・fallbackオーケストレーションの共通モジュール |
| `er003_test_audio_tts_asr_safety.py`(新規) | 回帰テスト25件(仕様4節の全ケース対応) |
| `ER-003_AUDIO_INHERITANCE_CHECKLIST.md`(新規) | 仕様継承チェックリスト(SoTではなく確認ツール) |
| `ER-003-AUDIO-HARDENING-01_REPORT.md`(新規) | 本報告書 |

## 受入条件チェック(TTS/ASR)

| 条件 | 結果 |
|---|---|
| TTS入力正規化を再利用可能な形で実装 | 済(B節) |
| ASR検証正規化を再利用可能な形で実装 | 済(C節) |
| カノニカルテキストを変更しない | 済(TTS呼び出し直前のコピーにのみ適用) |
| TTS/ASR正規化を別処理として維持 | 済(別関数、別テスト分類) |
| 正しい音声を誤ってFAILさせないケースを検証 | 済(E節、綴り差・句読点・改行等) |
| 内容が異なる音声を誤ってPASSさせないケースを検証 | 済(E節、欠落・数字・否定・無関係・過剰正規化防止) |
| 英国/米国綴り差はPASS | 済 |
| 数字違いはFAIL | 済 |
| 否定違いはFAIL | 済 |
| 無関係な内容はFAIL | 済 |
| 空ASRはFAIL | 済 |
| 認証/API失敗はPASS禁止 | 済 |
| 回帰テスト結果の提示 | 済(E節) |

## 受入条件チェック(仕様継承)

| 条件 | 結果 |
|---|---|
| Audio Inheritance Checklist作成 | 済 |
| Audio Shellを含む | 済(B節) |
| Number Treatmentを含む | 済(D節) |
| Point Balanceを含む | 済(D節) |
| Key Phrase発音を含む | 済(C節) |
| Fact Safetyを含む | 済(E節) |
| TTS/ASR検証を含む | 済(F節) |
| Post-processingを含む | 済(G節) |
| SoT参照関係を明示 | 済(冒頭・H節) |
| チェックリスト自体が新SoTにならない | 済(冒頭で明記) |
| Preflight/Completionワークフローで使える | 済(3段階運用モデル) |
| このステージ自身の継承ギャップをLessons Learnedとして記録 | 済(I節) |
