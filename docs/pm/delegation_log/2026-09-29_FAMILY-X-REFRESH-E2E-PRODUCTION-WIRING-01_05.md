## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(SSOT 反映 / ユーザー決定 2 件の記録、委任 _05)。一時ファイル `docs/pm/ACTIVE_TASK_RF5.md` / `docs/pm/RESULT_PACKET_RF5.md`(commitしない)。並行: 別 Sonnet 1 件(W1: `er003_v1_n3_01_*`/`er012_*`/`er019_family_x_*runner*.py`/REPORT/設計書を編集中)→ **これらに触れない**。本タスクの所有: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`(SSOT 編集権は本タスクのみ=SSOT 直列化)、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。費用 ¥0(SSOT 編集のみ)。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_05.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_05.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_05.md_check.json` を実行し結果1行記録。T-2/T-3: API 支出なし。

## 記録するユーザー決定(2026-09-29、逐語で記録。解釈・拡張禁止)

### 決定 1: Key Phrase 音声構造(Standard/Advanced 共通骨格)

「Advanced Key Phrase の音声構造は、以下で正式決定です。
Advanced: 英語 Phrase → 英語解説 → 英語 Phrase
Standard: 英語 Phrase → 日本語意味 → 英語 Phrase
つまり、両レベルで『Phraseを最初と最後にもう一度聞く』という同じ骨格にし、中間だけをレベル別に変えます。Standard: 中間=日本語意味/Advanced: 中間=平易な英語解説。この仕様でProduction正式経路へ配線してください。今回の決定により、先ほどのAdvanced KP Assembly順序に関する USER_DECISION_REQUIRED は解消です。」
付帯条件(逐語): 「Advancedの英語解説音声は、採用済み Variant B」「最後の英語Phraseは、最初と同じcanonical Phraseを使用」「追加の別文言・別候補を作らない」「Standard側の既存構造を壊さず、対応関係を明確に保つ」「retry / fallback / cache / Master Storeでも、最初と最後のPhraseが同一canonical text・同一正式音源/生成条件になること」「量産コスト報告ではこの構造によりAdvancedでPhraseがもう1回再生される分について、追加生成callが発生するのか、既存Phrase音源のreuseで済むのかを明示してください。reuse可能なら量産APIコスト増として数えないこと。」
Status: `APPROVED_FOR_PRODUCTION`(未配線。配線は本管理ID W4 で実施、`PRODUCTION_WIRED` は E2E Gate 後の Fable 判定)。既存の「KP 英語解説 text 仕様 APPROVED_FOR_PRODUCTION(未配線)」「Variant B 採用(`clear, precise, at a measured pace, without dragging`)」と統合し、矛盾なく 1 小節にまとめる(重複記述は残さず参照で結ぶ)。

### 決定 2: 固定フレーズ Champion の残り 2 件

num_three=**B take1**、num_five=**B take1**(`TTS-FIXED-SHELL-THREE-FIVE-RETRIAL-01`、er047、model gemini-3.8-flash-lite-tts / voice Charon)をユーザーが決定済み。CURRENT_SPEC の「未確定」表記を解消し、10 phrase の Champion 一覧(welcome=A 現行継続/preview_intro=C/key_phrases_intro=C/full_story_intro=C/num_one=C/num_two=B/num_three=B take1/num_four=C/num_five=B take1/point_explanation=B)を確定表記にする。付記: W2(commit `2ecb0c64`)で welcome 除く 9 件を Production Master Store へ登録済み(`v3_champion_2026_09_29`、TTS 0 回 reuse 確認済み)。Status は「登録済み・E2E Gate 待ち」であり `PRODUCTION_WIRED` とは書かない。

## 手順

1. Grep で該当箇所のみ特定(全文読込禁止): `CURRENT_SPEC.md` の `Key Phrase|KP 英語解説|Variant B|固定フレーズ|Champion|num_three|num_five|未確定`、`OPEN_ITEMS.md` の `OPEN-222|OPEN-229|OPEN-230|KP|Key Phrase|Champion`、`DECISION_LOG.md` の先頭ヘッダーチェーン形式(直近エントリ 1 件の書式を踏襲)。
2. CURRENT_SPEC: KP 音声構造小節(Standard/Advanced 対比表)と Champion 一覧を更新。DECISION_LOG: 決定 1・2 を新エントリとして追加(ヘッダーチェーン更新)。OPEN_ITEMS: 関連 OPEN(OPEN-222 等)に決定反映を追記、Advanced KP 組立順序に関する USER_DECISION_REQUIRED 記述があれば「解消(2026-09-29 決定)」へ。既決事項の再提示・他の未決事項の変更はしない。
3. 各ファイルの本体行 3,000 文字制限・HISTORY 切り出し規約(CLAUDE.md)に従う。
4. `git diff --stat` で SSOT 3 ファイル+delegation_log のみであることを確認し、path 指定 add、メッセージ `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: SSOT反映(Key Phrase音声構造=両レベル Phrase→中間→Phrase 骨格の正式決定、固定フレーズChampion num_three/num_five=B take1 確定、Advanced KP組立順序のUSER_DECISION_REQUIRED解消)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、push。

## 報告(RESULT_PACKET_RF5 + handback、目安15行)

更新箇所(ファイル・小節名)/決定文の逐語性確認/矛盾チェック結果(旧「未確定」「USER_DECISION_REQUIRED」残存 0 件)/commit hash・raw URL 3 件/STOP 有無。
