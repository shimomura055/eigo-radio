# ER-003 Audio Inheritance Checklist(音声制作 仕様継承チェックリスト)

**管理ID: ER-003-AUDIO-HARDENING-01の成果物**
**このドキュメントの位置づけ(必読)**

このチェックリストは**Source of Truth(SoT)ではない**。実際の仕様は
常に以下が正であり、このチェックリストはそれらを「実装時に見落とさな
いための確認ツール」に過ぎない。内容が食い違った場合はSoT側が正しい。

- [CURRENT_SPEC.md](CURRENT_SPEC.md) — 現行の正式仕様
- [DECISION_LOG.md](DECISION_LOG.md) — 個別の設計判断とその根拠
- 各段階の最終承認済みscript(例: A2は`er003_v1_a2_audio_ab_01_generate.py`)
- [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) — 成果物の承認状態

このチェックリストの各項目文言がSoTの記述と食い違っていると気づいた
場合、その場でこのチェックリストを書き換えて「新しい仕様」にしない
こと。SoT側を確認し、必要ならSoT側を更新するか、DECISION_LOGに矛盾
として記録すること(ER-003-B1-SCAFFOLD-AUDIO-02で実例あり: F節参照)。

**ステータス語彙**
| 状態 | 意味 |
|---|---|
| `APPLICABLE` | この作業(記事/レベル)に適用される項目 |
| `NOT_APPLICABLE` | この作業には適用されない項目(理由を記録) |
| `VERIFIED` | 適用した上で、実際に確認・検証済み |
| `NEEDS_DECISION` | SoT間の食い違い・未決事項があり、独断で進めず報告が必要 |

**使い方(3段階ワークフロー)**
1. **Preflight(着手前)**: 新しい記事・レベルの音声制作に入る前に、
   このチェックリストを上から確認し、どの項目が`APPLICABLE`かを
   洗い出す。SoTを都度参照し、このチェックリストの文言だけで判断しない。
2. **Implementation(実装中)**: 適用した項目を`VERIFIED`へ更新しながら
   進める。SoTとの食い違いに気づいたら`NEEDS_DECISION`とし、独断で
   解決せず報告する。
3. **Completion(完了時)**: 全`APPLICABLE`項目が`VERIFIED`か
   `NEEDS_DECISION`(未解決として報告済み)になっているか確認する。
   `APPLICABLE`のまま未確認の項目を残さない。

---

## A. Content / Structure(記事本文の構成要素)

Preview, Key Phrases, Comment1, Full Story Part1, Comment2, Full Story
Part2, Comment3, Point One, Point Two, Comment4, In One Line

- SoT: [CURRENT_SPEC.md](CURRENT_SPEC.md)「Full Story構造」節
- 確認事項: 全11要素が過不足なく含まれているか。Comment等の
  Support要素とNews本文要素を混同していないか

## B. Audio Shell(番組の入れ物)

Intro, Outro, Notification/SFX, SFX配置, Comment前後のSFX有無(なし),
transition, silence/pause, セクション順序, 再利用可能な共通音源

- SoT: A2最終承認済みscript(現時点: `er003_v1_a2_audio_ab_01_generate.py`
  のbuild_pieces_with_timeline)、[DECISION_LOG.md](DECISION_LOG.md)の
  ER-003-A2-AUDIO-AB-01エントリ
- 確認事項:
  - 最新の承認済みscriptを参照しているか(超過去の類似script
    `er003_v1_a2_audio_01/02_generate.py`にはpause値等の古い値が
    残っている場合があるため注意。ER-003-B1-SCAFFOLD-AUDIO-02で
    この区別が必要だった)
  - `CURRENT_SPEC.md`の文言と実装scriptの動作を両方確認し、
    食い違いがあれば`NEEDS_DECISION`として報告する(例:
    ER-003-B1-SCAFFOLD-AUDIO-02で発見した`CURRENT_SPEC.md:148`の
    notification2配置記述とA2最終scriptの実装の不一致)

## C. Key Phrase(語彙提示)

選定ルール、English→Japanese→English提示順、文脈内での自然な
prosody、発音の正確性、フレーズのグルーピング、承認済み発音対応
(英国綴り/米国綴り等)

- SoT: [CURRENT_SPEC.md](CURRENT_SPEC.md)「Key Phrase」節、
  Canonicalization原則([DECISION_LOG.md](DECISION_LOG.md)の
  ER-003-KP-02エントリ)
- 確認事項: レベル・記事ごとにKey Phrase内容自体は異なってよいが、
  提示方式(E→J→E、番号読み上げ)はSoT通りか

## D. Spoken-first(音声視点での情報設計)

- **Number Treatment**: ANCHOR/SUPPORTING/DISPENSABLE ×
  EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY の分類、不要な精度の
  四捨五入、リスニング前提の情報密度
  - SoT: [CURRENT_SPEC.md](CURRENT_SPEC.md)「Number Treatment」節
  - **教訓(E-1参照)**: この項目は難易度生成系タスク(CEFR-DIRECT系等)
    で暗黙のうちに継承漏れが起きたことがある。新しい記事・派生
    テキストを作る際は必ずPreflightで明示確認すること
- **Point Balance**: Point One/TwoがMain Storyと同等の長さ・情報量に
  ならないよう、役割・比重で判断する(固定語数ルールではない)
  - SoT: [DECISION_LOG.md](DECISION_LOG.md)のER-003-SPOKEN-FIRST-03
    エントリ。**注意**: 「40〜50語」はA02単独での実測収束値であり、
    他記事・他ジャンルへの固定ルールとしての適用は`NOT_YET_
    GENERALIZED`(未一般化)

## E. Text Integrity / Fact Safety(事実の正確性)

Ledgerの範囲、因果関係の表現、policy(決定事項)とpilot(試験段階)の
区別、B1/B2共有テキストが必要な箇所での完全一致、Supportに新しい
事実を追加しないこと、Fact Checker、Ledger Deviation Check

- SoT: Verified Fact Ledger運用(`er003_v1_en_direct_vfl_01_generate.py`
  の`run_deviation_check`)、[CURRENT_SPEC.md](CURRENT_SPEC.md)の
  Fact Safety関連節
- 確認事項: 音声化前のテキスト全て(Support含む)についてFact
  Checker `PASS`・Ledger Deviation `LEDGER_COMPLIANT`を確認したか。
  B1がB2ニュース本文を再利用する場合、SHA256等で完全一致を機械的に
  確認したか(テキストの目視確認だけに頼らない)

## F. TTS / ASR(音声生成・検証の技術層)

TTS入力正規化、ASR検証正規化、ASRは必須(スキップ禁止)、空ASRを
PASS扱いにしない、API/認証エラーをPASS扱いにしない、英国綴り/米国
綴りの許容、不一致のログ記録

- SoT/実装: [er003_audio_tts_asr_safety.py](er003_audio_tts_asr_safety.py)
  (本チェックリストと同じER-003-AUDIO-HARDENING-01で作成した共通
  モジュール)。回帰テスト: [er003_test_audio_tts_asr_safety.py](er003_test_audio_tts_asr_safety.py)
- 確認事項:
  - `strip_markdown_for_tts`はTTS呼び出し直前のみに適用し、カノニカル
    テキスト・表示用テキスト・Fact-QA用テキストには適用していないか
  - ASR検証は`validate_asr_match`を使い、判定根拠(expected/normalized
    expected/actual/normalized actual/verdict/reason)を監査ログとして
    残しているか
  - ASR取得失敗(空文字列・None・API/認証エラー)を`FAIL`以外の
    verdictにしていないか

## G. Post-processing(音量・仕上げ)— 現行採用分のみ

Dynamics、減衰処理、音量処理、Outro処理、その他現行の後処理

- SoT: A2最終承認済みscriptの`apply_gain_and_convert`
  (target_rms方式、Outro二段減衰)
- **注意**: 過去の実験的な値(旧scriptの0.5秒一律pause等)を現行仕様と
  混同しないこと。必ず最新の承認済みscriptの値を確認する

---

## H. このステージ(ER-003-AUDIO-HARDENING-01)で判明した継承ギャップ(Lessons Learned)

批判・原因追及としてではなく、「暗黙の継承は漏れる。明示的な
Preflightが必要」という教訓として記録する。

1. **Number Treatmentの非継承**: CEFR-DIRECT系の難易度検証作業
   (ER-003-CEFR-DIRECT-01/02/03)では、Number Treatment(ANCHOR/
   SUPPORTING/DISPENSABLE等の分類)が作業スコープの前提として明示
   継承されていなかった。個別のNumber表現判断は都度なされたが、
   「Number Treatmentという既決の枠組みを最初に参照する」手順が
   なかった
2. **Audio Shellの非継承**: ER-003-B1-SCAFFOLD-AUDIO-01(B1最初の
   完成音声試作)では、Intro/Outro/Notification/Key-Phrase-Audio等の
   Audio Shellがスコープに含まれておらず、11コンテンツパートの
   単純連結にとどまった。Shellの統合はAUDIO-02という別段階まで
   持ち越された

このチェックリストは、上記2件のような「決定済みの仕様が新しい作業へ
明示的に引き継がれない」問題を防ぐために作成した。
