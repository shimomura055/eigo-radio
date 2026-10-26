# OPEN_TRACKING_01 — 残Open Item・判断候補・PRODUCTION_WIRED判定ゲート

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0)。**新規OPEN行は作らない**(OPEN-528を本案件の追跡に使う。委任文指定)。本書は本案件内の残件・判断候補の一覧。
Status: **APPROVED_FOR_PRODUCTION(ユーザー2026-10-26)/ DESIGN_READY_FOR_OPUS / PRODUCTION_WIRED未達**。

## 1. 判断候補(ユーザー判断が必要なもののみ。`USER_DECISION_REQUIRED`のラベルはFableのみ)

分類(27-3): A=既判断(承認原文file:line)/B=承認範囲内で自己解決/C=現タスクと独立/D=真に新しい判断。**いずれも本案件のPhase 1着手を止めない(非ブロッキング)**。

| ID | 判断候補 | 内容・理由 | 影響(QCD) | 代替案 | 推奨 | 分類 |
|---|---|---|---|---|---|---|
| J-1 | Z dialogueにLocal Rewriteを新規配線するか | ユーザー文言『3回目NG→既存のLocal Rewrite処理へ』『Local Rewriteも既存の回数上限・安全条件を維持』は、LRがdialogueに存在する前提に読める。しかし**現行のZ dialogue生成にLRは未配線**(`er012_b_family_voices_production_01.py`にLR呼出0、`er003_v1_n3_01_tts_generate.py:319`のdocstringも『A2外側ループ内にはLR配線が無い』と明記、全Z run dialogue 667 entryで`audit_text_deviation`=0)。LR対象のFULL_STORYには`full_story_part{n}_c{k}`が含まれる(`er020…resolve_narrative_role`)が、dialogue clipの生成関数側に呼出が無い | Q: LRで救えるclipが増える可能性(ただしセリフ=登場人物の台詞本文を書換える新機能。Natural English QA・原作保持との整合が新規論点)。C: LR配線は別案件規模(実装+LLM費用。dialogue向けの費用は未確認)。D: 影響の大きさは未確認(Trialでctx 3 call全NGは1/53 clip、従来方式に戻した後もNGになる頻度は未測定) | (a)本案件は『LR新設なし、3回NG→STOPPED→HR Lock→Gate BLOCK』(現行動作・ユーザー文言後段の『Local Rewriteで解決できなければ既存のHuman Review／STOP』を満たす) (b)別案件でdialogue LRを新仕様として設計(Trial→ユーザー判断) | (a)。(b)は本案件の外 | **D(LRのdialogue新規配線は真に新しい仕様判断)。ただし本案件の進行判断としては B(現行動作の維持でユーザー文言を満たす)** |
| J-4 | Trial観測の話速/長ポーズ/境界音量差/F0について新しい品質基準(gate)を設けるか | 6項目のいずれも既存の承認済みValidator・組立・品質条件に反しない(DESIGN_01 §E)。ユーザー原文§4は『独自の新しい品質基準を設けない』『実質的な仕様変更が必要なら USER_DECISION_REQUIRED』 | 現状は観測値の開示のみ。gate化すると再生成率とcooldown発生が増え、費用・時間が増える | (a)開示のみ(推奨)。(b)ユーザー試聴の結果、不満が確認された項目のみ後日別Trialで基準案を検討 | (a) | D(新基準は新仕様)。現段階は不要=開示のみ |

(欠番J-2/J-3: Fable委任文の仮番号。J-2=cooldownのclip内ブロック vs deferral は**B(承認範囲内で自己解決、Fable/Opus判断)**、J-3=既存run・in-flightのpolicy扱いは**B(policy pin、キー無し=legacy)で解決済み**のため、ユーザー判断候補から除外。)

## 2. 残Open Item(本案件内。新規OPEN行ではなくOPEN-528追跡の下位項目)

11-8分類: 修正へ進む / ユーザー判断要 / 実害なし。

| ID | 内容 | 分類 | 解消条件・次の一手 |
|---|---|---|---|
| O-1 | Opus条件Aレビュー(OPUS_REVIEW_REQUEST_01) | 修正へ進む | Opus回答を`OPUS_REVIEW_01.md`へ無改変保存→Fableが照合しM/Rを設計へ反映(DESIGN_02)→Phase 1着手 |
| O-2 | Phase 1実装+offline test(TEST-01〜16) | 修正へ進む | 次委任(Opus後)。API 0 |
| O-3 | Phase 2 runtime evidence(E-1〜E-4、Std/Adv) | 修正へ進む | 別委任。見積約48円(300円以下=Fable自律枠)。`stop_scope_check`・`TTS_EXECUTION_MODE=STANDARD`・自PIDのみterminate |
| O-4 | Z『1生成セット』がPM_GOVERNANCE 15-8標準表に行が無い(15-9: 初回の原価測定委任で構成を明記してから追加) | 修正へ進む | Phase 2完了報告に構成(writer/std_adjust/plan/support/kp/tts…)と実測を記載→Fableが15-8へ反映する別委任 |
| O-5 | EVAL_01の『+約0.08円/call』と再導出『+約0.098円/call』の差 | 実害なし | 結論(70円以内)は不変。Phase 2実費で置換 |
| O-6 | Trial未検証story(`after_twenty_years`/`the_tell_tale_heart`/将来作)の話者表示名・許可語はfallback生成 | 修正へ進む | Phase 1で `speaker_display_source: fallback` を記録。必要なら該当storyのdataをユーザー判断なしで追加(値は話者key由来の機械生成、方式は不変) |
| O-7 | E-1の`pages`出力先が公開dir(`user_test/family_z_*`)を上書きしないことの確認 | 修正へ進む | Phase 1で`stage_pages`の出力先を確認。上書きの恐れがあればE-1に`pages`を含めない |
| O-8 | ASR OK確定直後〜`save_checkpoint`前のクラッシュ窓で、そのclipがn+1から再生成される(総3回は超えない) | 実害なし(数秒の窓・費用は最大0.45円/clip) | 開示。Opus判断(論点1e) |
| O-9 | `attempt_ctx`のslotは外側ループ各pass内の番号(pass2は再び1から)という既存挙動 | 実害なし(既存・本案件は変更しない) | 開示のみ |
| O-10 | ctx attemptでtechnical failure→`minimal_fallback`が発火するとその生成はctxを含まない | 実害なし(既存の安全機構・evidenceに`effective_mode`記録) | 開示。Opus判断(論点3) |
| O-11 | 感情情報の自動受理(Fable目視の除去)の残余リスク0/76 | ユーザー判断要か否かはOpus/Fable判断 | Opus論点5。新基準を作らず閉じられない場合のみ判断候補化 |
| O-12 | 公開済みrunの再開(キー無し=legacy)ではctxが適用されない | 実害なし | 仕様(混在防止)。新規runから標準方式。既存公開作品の再生成はユーザー指示があったときのみ |
| O-13 | Phase 1では`CURRENT_SPEC.md`を未更新(文案=DESIGN_01 §J) | 修正へ進む | Phase 1/2完了時の別委任でCURRENT_SPEC追記 |

## 3. PRODUCTION_WIRED判定ゲート(Fable独立照合。1つでも未達なら『完了』にせず、残Openと解消条件を報告)

1. 設計: Opus条件Aレビュー後の最終設計がSPEC_LEDGERの全R項目に紐づく(未紐づき0)。
2. コード: 正式初回Production経路(`run_tts_stage`→`dialogue()`)が新policyを使う。Trial module非依存(TEST-11)。X/Y/B/C/narrator/KP不変(TEST-12)。
3. 回帰: 既存test全PASS+新test(TEST-01〜16)全PASS(遮断harness、API 0、cost log行数不変)。
4. runtime evidence: E-1(正常経路)がStd/Advとも正式runnerで実TTS requestにCONTEXTあり。E-2/E-3/E-4(強制NG)でfallback・resume・3回NGの遷移とcooldown実時間≥600秒を確認。正常経路とfallback経路を`path`で区別して記録。強制NGはGate出力のNG方向のみ。
5. QA/Gate: Gate PASS(E-1)、HR Lock・STOPが既存規則どおり(E-4)。ASR判定規則・組立・音量・速度は不変(headroom/gain_report記録)。
6. 費用: 6区分の実測値+Z 1生成セット構成の明記+70円評価。Guardrail 200円内。
7. SSOT: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新、Opus台帳`OF-FZCW-*`、commit/push。
8. 残Open: 重大なOpen Itemなし(軽微なものは分類つきで報告)。

## 4. 完了報告雛形(Phase 2。Std/Advそれぞれ)

| 項目 | Standard | Advanced |
|---|---|---|
| 正式初回生成(ctx発火・送信prompt証拠) | | |
| retry(1→2回目) | | |
| fallback(3回目・prompt証拠・cooldown実秒) | | |
| resume(TTS総call数・state履歴) | | |
| QA(ASR判定、Gate、HR Lock) | | |
| 実音声(path・長さ・headroom・試聴mp3) | | |
| コスト(provider別実費・6区分・70円評価) | | |
