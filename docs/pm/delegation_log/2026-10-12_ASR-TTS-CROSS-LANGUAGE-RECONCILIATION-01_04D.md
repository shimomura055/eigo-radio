# 委任_04D 報告: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 作業B(2026-10-12)

範囲: 日英共通フロー設計v03、minimal fallback撤去依存整理、Key Phrase K2と既存対策の逐語比較、Trial D(KP英語Prompt、小規模)、日本語Local Rewrite適用性Trial。**Trial/設計限定、Production変更なし**(Production code/Prompt/Validator/Routing/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS無変更。SSOT記録は統合委任で)。Production telemetry/queue/Master Store書込なし。並行agent領域(`er058_output/{trial_abc,trial_c,asr_tts_prodfix_01}/`、worktree、`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`、`user_test/coffee_*`)に触れていない。

## 使用モデル(最新原則報告)
| 用途 | モデル | 最新か | 理由 |
|---|---|---|---|
| Trial D TTS | gemini-3.8-flash-lite-tts(Aoede) | Production同一(Production比較のため) | 例外種別2: ライン組み込み候補の性能確認+既存結果との同一条件 |
| Trial D Primary ASR | Production同一`routing.transcribe`(OpenAI gpt-4o-mini-transcribe系) | Production同一 | 同上 |
| ローカルwhisper | faster-whisper small(Production disfluency QAと同一) | 参考 | 同上 |
| JA LR候補生成 | gpt-6-luna(reasoning high、Production LRと同一) | 最新ではない(最上位gpt-6-astra、推奨gpt-6.1-sol) | 例外種別2: Production LRの実モデルの適用可否確認。astra/solは単価登録・費用上限の制約 |
| 評価者LLM | なし(機械チェック+人間確認) | - | - |

## 成果物(すべて`er058_output/design/`ほか既存構造)
- `er058_output/design/UNIFIED_FLOW_SPEC_V03.md`(共通フロー仕様案、状態遷移、共有カウンタ、Secondary条件S1〜S7、PASS集合、PASS_WITH_WARNING、技術失敗、LR位置づけ、KP 3回単一Prompt、B'、既存承認仕様との衝突C-1〜C-14)
- `er058_output/design/MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_01.md`(依存マップ、撤去手順、Dangling Reference Check)
- `er058_output/design/KP_K2_VS_EXISTING_COUNTERMEASURES_01.md`(逐語比較、統合案、Trial D結果)
- `er058_output/design/JA_LOCAL_REWRITE_APPLICABILITY_01.md`
- Trial D証跡: `er058_output/kp_english_lock_trial_01/`(`COST_ESTIMATE_D_01.md`、`prompts_D.md`、`results_gen.jsonl`、`eval_D.json`、`cost_actual_D_tts.json`、`play_evidence_D.json`、`raw/`)。試聴ページ `user_test/kp_english_lock_trial_01/index.html`
- JA LR証跡: `er058_output/ja_local_rewrite_applicability_01/ja_lr_trial_results.json`
- スクリプト: `er058_kp_english_lock_trial_01.py`、`er058_kp_english_lock_trial_page_01.py`、`er058_ja_local_rewrite_applicability_01.py`

## 費用(実費記録)
| 項目 | 事前概算 | 実績 | 上限 |
|---|---|---|---|
| Trial D TTS(35 call) | JPY2.7(+ASR0.5、合計3.2) | **JPY1.1**(usage実測) | JPY10 |
| Trial D Primary ASR(32音声) | 約JPY0.5 | 約JPY0.5(概算。usage非返却) | (上記に含む) |
| JA LR(5 call、gpt-6-luna) | (事前見込み約JPY0.5〜2.5) | **JPY0.71**(usage実測) | JPY3 |
| **合計** | | **約JPY2.3** | |
請求画面は未確認。Azure(Secondary)は呼んでいない。

## 結果(ユーザー判断材料優先)
1. **共通フローは日英・各roleで成立するか**: 状態遷移は言語非依存で成立する(設計上)。日本語はLR未成立のため「3回不合格->直接Human Review」で開始が安全。Secondary不呼出は安全条件S1〜S7に絞り、C1の粗い除外は廃止方向、C2・推奨4は維持(ユーザー採用済みのため)。UNCERTAIN->HR直行の廃止、Secondary PASS厳格集合の日英統一、script版あたり3回(LR時最大6回)は**承認済み仕様の変更**(C-1〜C-7)。
2. **KP 4回->3回単一Prompt**: 構造としては変更可能。ただし単一Promptの中身(現行Minimal/現行English Lock/K2統合)が新規仕様判断。KP 4回構成はユーザー正式決定(2026-09-01)の変更。
3. **K2の欠落**: あり。K2単独では**冠詞・機能語の弱形(対策②)が完全欠落**、「naturally and clearly」「warm announcer」「explanations等の列挙禁止」「not trailed off」「過剰強調禁止」「English Lock」が欠落/弱体化(△3・×4)。一体感はK2の方が強い。①ASR対策・③QAはPrompt非依存で維持。K2単独置換は不可、統合が必要。
4. **Trial D(8語x4版、各1回)**: 全32件Primary PASS、非ラテン0、反復0、余分な語0(自動評価の識別力は低い、聴感が必須)。傾向(n=1): K2系(V2/V3)は発話が長め(+8〜15%)で語がまとまる。完全統合版(V4、現行同等の長さ)は現行(V1)と同じ長さ・同じ連結傾向(raw bean→「Robin」転写はV1/V4)。簡潔統合(V3、現行の54%の長さ)はK2の傾向を保ちつつ対策②・English Lockを含められる可能性。**聴感評価と複数回再現は未実施**。
5. **LRは最小変更で運用可能か・日本語適用可否**: 英語は現行実装で最小変更の運用が可能(ただしLR再TTSをminimal依存から標準Prompt共通ループへ置換、位置づけ変更が必要)。**日本語は機械流用不可**(`identify_ng_span`が日本語で未動作、Gate 7が15候補全てで0.0=常に不合格、全文性判定が不安定)。5実例でLunaは最小書換え候補を作れたが、**本当のNG原因に触れたのは0/5、3/5はTTSが正しい(ASR誤認/表記差)ため書換え不要**。日本語LRよりSecondary側(表記差・PHONETICの扱い)の設計が先。KP・見出しはLR対象外roleのまま。
6. **minimal fallback撤去**: 可能。最初に壊れるのはLR再TTS(`crosslevel` L383、現状もminimal Promptで再TTS)、日英共有定数`PRODUCTION_STANDARD/MINIMAL`+assert(`er011` L102-104)、静的監査/回帰テスト。`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`はwelcome共有殻で通常使用のため**残す**。Key Phrase専用Minimal Promptは独立で**残す**(コードで確認)。
7. **QCD**: Q=偽NG由来の不要再生成・本文書換えの減少(英語)、C=ASR呼出減(日本語)・Azure追加(英語、約+0.2〜0.3円/segment見込み)・LR最大1回、D=cool-down廃止で最大約10分/segment短縮(U-6)。定量は未測定項目あり(最小対Trial要)。

## 残る判断事項(ユーザー)
1. 共通フロー全体の承認と導入順(日英同時/段階導入)。
2. KP 3回単一Prompt: 現行Minimal / 現行English Lock常用 / 簡潔統合(V3)のどれか。V3系は聴感評価と複数回Trialが先。
3. UNCERTAIN->HR直行の廃止(C-1)、例外案(両ASR一致の誤りは即HR)の要否。
4. Secondary PASS集合(PHONETIC/HIGH_SIMILARITY_SAFEの許容、U-3)と表記差のみのNG(二/2、％/パーセント)の扱い。
5. 日本語LR: 当面LRなしでよいか。
6. 決定論的技術失敗(400)の隔離経路を残すか(U-4(d))、cool-down(U-6)。
7. C1廃止(g8)の最終確認、C2維持の確認。
8. 最小対Trial(8-3-A、約15〜20円)の実施可否。

## 新しい仕様候補・懸念(実装していない、報告のみ)
- LR発火条件に「Secondaryが原稿一致と判定しない表記差のみのNG」が含まれると、正しい原稿を書き換える(g21・g36)。PASS_WITH_WARNING/表記差の扱いが先決。
- Flash-Lite TTSでは`speech_metadata.style`が`prompt_tokens`に計上されない(35 callで100 tok、Trial D実測)。Prompt長が費用に影響しない可能性(請求画面で未確認)。
- Production LR再TTSがStyle不変でない(minimal Prompt)点は、ユーザー新方針と衝突する既存の構造問題。

## Gate/Closeout
- 試聴ページ: 仕様名中立(版1〜4)、Blindにしない、各行にVoice・原稿・ASR結果。Playwright実再生evidence: `er058_output/kp_english_lock_trial_01/play_evidence_D.json`(32/32音声の実再生OK、HTTP 200、spec名リークなし、audio最小幅360px)。
- Production無変更を`git status`で確認(追加はer058_*、docs/pm、user_test/kp_english_lock_trial_01のみ)。
- Agent/Subagent起動なし。
