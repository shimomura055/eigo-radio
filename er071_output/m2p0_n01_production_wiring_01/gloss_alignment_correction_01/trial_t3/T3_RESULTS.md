# T3 mock統合結果 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02)

27/27 PASS / 実API・実TTS呼出 0 / 費用 JPY0 / TTS_EXECUTION_MODE=STANDARD

| ID | 内容 | 結果 |
|---|---|---|
| T3(a) | alignment API例外2回 -> FAILED_HUMAN_REVIEW_REQUIRED(KP維持・旧gloss維持)+HR報告書+event+stdout | PASS |
| T3(b) | JSON不正2回 -> HR待ち | PASS |
| T3(c) | 不正gloss(括弧/算用数字/…)2回 -> HR待ち | PASS |
| T3(d) | mapping欠落: gate判定=HR待ち / record-only=LLM判定で採用+machine_check不合格を並記(誤NG/誤PASS採否材料) | PASS |
| T3(e) | 1回目失敗->2回目成功: 採用・HR報告書なし・event空・非OK statusなし | PASS |
| T3(f) | 2回連続失敗: 報告書必須項目(article/level/rank/英語KP/現gloss/失敗理由/全attempt/再生成候補)+event+stdout、queue/Lock/attempt_history不使用 | PASS |
| T3(g) | batch内一部成立・一部失敗: 成立分(rank5)は採用、未解決(rank2)のみHR待ち、2回目は未解決のみ送信 | PASS |
| T3(h) | HR報告の書込失敗/再読検証失敗 -> GlossAlignmentNotificationErrorで当該stage停止(fail-closed) | PASS |
| T3(i-A2) | FAILED itemのlevelはKP segment全体(5rank x en/ja)がSTOPPED_GLOSS_ALIGNMENT_FAILED・TTS 0 call・Gateがassembly拒否 | PASS |
| T3(p) | B1: 解説LLM・解説TTS・KP TTSいずれも0 call(glossが解説LLM入力になる経路を停止)、explanation segmentはSTOPPED、Gate拒否 | PASS |
| T3(o) | tts_generation_results.json欠落: 既存Gateは素通り(既存fail-open)だが、assemble前チェックEPISODE_BLOCKED_BY_GLOSS_ALIGNMENTが拒否 | PASS |
| T3(q) | page/player: HR待ちglossは(assemble summaryがOKを装っても/BLOCKEDでも)tableに出ない | PASS |
| T3(k-X) | legacy FAILED artifact(=現行Production挙動)は関所で止まらずTTSへ進む=無変更(corrected専用の関所は発動しない) | PASS |
| T3(k-ga) | mode未指定(legacy既定)のalign_glosses出力がHEAD(現行)版と同一(4シナリオ)+flag OFFはDISABLED | PASS |
| T3(l-X) | resolve_gloss後の再実行: KP TTSが進む(10 call)、Gateは拒否しない。人間確定glossが入力に使われる | PASS |
| T3(t-X) | 独立level(HRなし)のB1 KPは影響を受けず通常どおり進む(解説LLM 1 call・KP TTS/解説TTS実行) | PASS |
| T3(n) | 外側redundancy retryで選び直した最終artifactが整合 -> HR報告書/eventなし(途中attemptのHR孤児なし) | PASS |
| T3(n2) | 最終attemptにHR待ちが残る場合、報告書は最終artifactの該当rankのみ(1回・過去attemptの分を含まない) | PASS |
| T3(v) | X scaffold: legacy既定はrun_key_phrasesへmode引数を渡さずsummary形不変 / corrected時のみ明示渡し+event入りsummary+最終専用stdout行 | PASS |
| T3(j) | Z stage_kp: FAILED(HR待ち)で既存FamilyZE2EStop送出、HR報告書(再読検証)+run-level event、assets未配備・stage結果未保存・TTS/解説 0 call | PASS |
| T3(m) | tts段を別実行しても保留: assets不在=例外、HR待ちartifactコピーがあってもload_level_inputsがFamilyZE2EStop。TTS API 0 call | PASS |
| T3(l-Z) | Z: resolve_gloss後に同stageを再実行 -> b1b選定は再実行されない(kp_fn計1回+a2初回のみ)、人間確定glossでassets配備、解説sigにgloss含む、snapshot消費済み | PASS |
| T3(h-Z) | Z: HR報告の再読検証失敗 -> GlossAlignmentNotificationErrorでkp stage停止(通知失敗のまま継続しない)、assets未配備 | PASS |
| T3(k-Z) | Z legacy既定(ctx.gloss_alignment_mode未設定=legacy): 既存mock kp stageが従来どおり通る(挙動不変) | PASS |
| T3(exit) | 別プロセス実行: Z=FamilyZE2EStopで非0終了、X=Gate拒否で非0終了。最終stdoutに専用行(「届いた」条件③) | PASS |
| T3(r) | attempt_history.jsonl/human_review_queue.jsonl/Master Store/telemetry/cost_summaryを汚染しない(全パターン実行前後でsha同一) | PASS |
| T3(api0) | 全パターンで実API呼出0(OpenAI/alignment/get_client禁止patchへの到達0) | PASS |
