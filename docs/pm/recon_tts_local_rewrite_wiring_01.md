# Recon: TTS retry(cool-down/Local Rewrite/Natural English QA)+
Connected Speech 5-role Production配線(read-only調査 + 配線先確定)

Management-ID: TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01
作成: Sonnet

## 1. 目的

ユーザー承認済み仕様(A〜F)をProduction TTS retry primitiveへ配線する
にあたり、既存のTTS初回/retry経路をrole別(Full Story/Comment/Preview/
Topic intro/In One Line/Heading readout/Key Phrase)に棚卸しし、
Connected Speech Equivalence Layer(OPEN-122)の引数がどこまで到達
できるか(`docs/pm/recon_connected_speech_scope_01.md`の「事実1」で
確認済みの構造的欠落を含む)を確認した。

## 2. Role別 現行経路・配線状況(本タスク実施前 / 実施後)

| role(承認済み5+非適用2) | 現行production関数(2026-09-26時点) | 実施前: Connected Speech引数 | 実施前: cool-down/Local Rewrite | 実施後 |
|---|---|---|---|---|
| Full Story(full_story_part1/2/3、point_one/two含む) | `er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin`(B1)/ `er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback`経由`generate_a2_segment_with_slowdown`(A2) | 引数あり(既存OPEN-122配線、point_one/twoは既存動作を維持) | B1: 無し / A2: 無し | B1: 追加(cool-down+Local Rewrite回復) / A2: **引数のrole判定は一元化したがcool-down/Local Rewrite回復は未配線(Gap、4節参照)** |
| Comment(comment_1-4) | `er003_v1_sing01_voice01_generate.generate_charon_english`(B1) / A2は日本語(`generate_a2_japanese_with_reading_safety`、対象外) | **引数自体が関数シグネチャに存在しなかった**(「事実1」) | 無し | B1: 引数追加+cool-down+Local Rewrite回復配線済み |
| Preview | 同上(B1: `generate_charon_english`) | 同上(引数無し) | 無し | 同上 |
| Topic intro | B1: `generate_charon_english` / A2: `c.generate_english_segment_with_fallback`(英語、既存引数あり) | B1: 引数無し / A2: 引数あり(但し従来Falseで固定呼び出し) | B1: 無し / A2: 無し | B1: 配線済み / A2: **role判定を一元化したがcool-down/Local Rewrite回復は未配線(Gap)** |
| In One Line | B1: `generate_news_narration_wide_margin` / A2: `generate_a2_segment_with_slowdown` | 引数あり(旧: 呼び出し側が明示的にFalse固定、「本文ではないため対象外」) | 無し | **新規enable**(ユーザー承認済み5 role適用範囲により、旧除外コメントを上書き)。B1: cool-down+Local Rewrite回復も配線済み。A2: 引数True化のみ(Gap同上) |
| Heading readout(point_one/two_heading) | `er003_v1_sing01_point_headings_aoede.generate` | 該当引数なし(元々非対象) | 無し | **変更なし(非適用のまま)** |
| Key Phrase(kp*_en/kp*_ja) | `shared_narration.ensure_key_phrase_english_component` / `generate_charon_japanese_with_reading_safety` | 該当引数なし(元々非対象) | 無し | **変更なし(非適用のまま)** |

## 3. 単一集約関数(要件3、経路ごとの個別フラグ禁止)

`er020_tts_retry_local_rewrite_01.py`の`resolve_narrative_role(segment_id)`
/ `connected_speech_enabled_for(segment_id)`が唯一のSSOT判定関数。
`er003_v1_n3_01_tts_generate.py`のB1/A2両方の呼び出し箇所は、旧来の
`name in (...)`ハードコード条件式をすべてこの関数の呼び出しへ置換した
(topic_intro/preview/comment_1-4/full_story_part1-3/point_one/two/
in_one_line)。point_one/point_two(Point本文)は、承認済み5 roleの
文言には明示的に登場しないが、既存Production wiringで既にFull Story
本文と同一関数・同一OPEN-121/122スコープでTrueが適用済みだったため、
本タスクでは**回帰させず**FULL_STORY roleへ含めている(新規追加ではなく
既存動作の維持、Sonnet裁量。要確認事項として4節に明記)。

## 4. Gap・要確認事項(隠蔽せず記録)

1. **A2経路のcool-down/Local Rewrite回復は未配線**: A2のFull Story/
   Point本文/In One Lineは`generate_a2_segment_with_slowdown`経由で
   `er003_v1_crosslevel_audio_02_common.generate_english_segment_with_
   fallback`へ到達するが、本タスクでcool-down+Local Rewrite回復コードを
   実装したのは`voice01.generate_charon_english`と`news_tail_fix.
   generate_news_narration_wide_margin`の2関数のみ(B1経路)。A2の
   Connected Speech Equivalence Layer自体(既存機構)は本タスクの
   role一元化により従来通り有効(in_one_lineのみ新規True化)。A2への
   cool-down/Local Rewrite回復拡張要否はFable/ユーザー判断を仰ぐ
   (第3の関数への複製実装は、本タスクの実行時間内で同水準のテスト・
   runtime evidenceを取れる保証がなく、拙速な拡大を避けた)。
2. **point_one/point_two扱いの解釈**: 上記3節参照。ユーザー承認済み
   5 roleの文言に忠実に従うなら対象外とも解釈できるが、既存Production
   動作を壊さない安全側の判断としてFULL_STORY roleへ含めた。
3. **A2 topic_intro**は英語(`c.generate_english_segment_with_fallback`)
   のため、role一元化の対象に含めたが、cool-down/Local Rewrite回復は
   Gap 1と同じ理由で未配線。

## 5. Human Review Lock / ASR Cascade / Foreign Token Gateとの整合

- `er011_human_review_lock_01`のReview Lockデコレータ(`guarded_generate`)
  はそのまま外側に残り、Local Rewrite回復はその**内側**(デコレータで
  ラップされた関数の内部、Human Review状態遷移が起きる前)で完結する。
  回復成功時はデコレータに`status="OK"`が伝わりRESOLVEDへ、失敗時は
  従来通りSTOPPED/ASR_VALIDATION_UNCERTAINが伝わりHUMAN_REVIEW_REQUIRED
  へ遷移する(役割分担は変更なし)。
- ASR Cascade(ER-007/ER-006 Secondary ASR)・Foreign Token Gate
  (ER-009想定箇所)には一切変更を加えていない(`evaluate_attempt_with_
  cascade`への引数追加のみで、Cascade内部ロジックは無変更)。
- Local Rewrite後の再TTSは、対象関数自身の`.__wrapped__`(Review Lock
  デコレータの外側)を`max_attempts=1`で呼ぶ、Trial-01と同一の既存
  設計パターンを踏襲(二重retry予算消費・二重Human Review記録を防ぐ)。
