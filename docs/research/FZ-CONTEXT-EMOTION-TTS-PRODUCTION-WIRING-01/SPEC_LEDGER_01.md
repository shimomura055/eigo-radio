# SPEC_LEDGER_01 — ユーザー正式決定原文(2026-10-26)の要求項目台帳

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0)。原文=`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`(逐語保存)。機械可読版=`spec_ledger_01.json`(同内容)。

Status列の意味: DESIGN_READY_FOR_OPUS=設計済み・Opus条件Aレビュー待ち / Phase 2待ち=runtime evidence取得後に確定 / Fable待ち=独立照合。**PRODUCTION_WIREDの行は1件も無い。**

実装先候補の略称: DESIGN_01=本ディレクトリのDESIGN_01.md。TEST-nn=TEST_PLAN_01.md。E-n=Phase 2 runtime evidence(TEST_PLAN_01 §3)。

| ID | 原文§ | 原文(逐語) | 実装先候補 | 検証方法 | Status |
|---|---|---|---|---|---|
| R1-1 | §1 | Family Zの「文脈・感情付きTTS」を正式採用する。 | 新規Production module(DESIGN_01 §A)+er063 dialogue()配線 | TEST-01〜06+Phase2 E-1 | DESIGN_READY_FOR_OPUS |
| R1-2 | §1 | **Status：APPROVED_FOR_PRODUCTION**<br>**目標：PRODUCTION_WIRED** | SSOT(OPEN-528追記)。PRODUCTION_WIRED判定はPhase2完了+Fable独立照合後 | OPEN_TRACKING_01 §ゲート | APPROVED_FOR_PRODUCTION(PRODUCTION_WIRED未達) |
| R1-3 | §1 | 対象はFamily Zのセリフ音声、Standard／Advanced両方。 | er063.real_generators().dialogue の a2(Std)/b1b(Adv)両分岐 | TEST-01/02(Std・Adv各)+E-1(Std・Adv各) | DESIGN_READY_FOR_OPUS |
| R1-4 | §1 | Family X/Yには適用しない。既存のナレーション、Key Phrase、その他のTTS仕様も変更しない。 | 入口=Z dialogue()closureのみ。共有generate関数は既定None不変 | TEST-12(X/Y/B/C/narrator/KPバイト同一) | DESIGN_READY_FOR_OPUS |
| R2-1 | §2 | **1回目：文脈・感情付きTTS**<br>- PASS → 採用<br>- NG → 即時Retry | attempt policy n=1: ctx style、待機なし | TEST-01,TEST-02 | DESIGN_READY_FOR_OPUS |
| R2-2 | §2 | **2回目：文脈・感情付きTTS**<br>- PASS → 採用<br>- NG → 10分クールダウン | attempt policy n=2: ctx style。NG時 cooldown 600秒(er020.COOLDOWN_SECONDS再利用) | TEST-02,TEST-03,TEST-08 | DESIGN_READY_FOR_OPUS |
| R2-3 | §2 | **3回目：従来方式TTSへFallback**<br>- 文脈・感情情報を付加しない、従来の承認済みTTS指示・Styleを使用<br>- PASS → 採用<br>- NG → 既存のLocal Rewrite処理へ | attempt policy n=3: style_prefix_override=None(=p9a.ENGLISH_STYLE_PREFIX、現行Z dialogueとバイト同一)。NG後=判断候補J-1(Z dialogueにLR未配線) | TEST-03,TEST-04,TEST-05 | DESIGN_READY_FOR_OPUS(NG後の扱いはJ-1) |
| R2-4 | §2 | Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う。 | 既存finalize/record_outcome→HR Lock→Gate BLOCK(無変更) | TEST-04 | DESIGN_READY_FOR_OPUS |
| R2-5 | §2 | **TTS総試行回数は初回を含め最大3回。** Fallbackを追加の4回目として扱わない。 | state machineの反復上限=3(永続化、resume・外側ループ・LRをまたぐ) | TEST-09,TEST-04 | DESIGN_READY_FOR_OPUS |
| R2-6 | §2 | Local Rewriteも既存の回数上限・安全条件を維持し、無制限な再生成を発生させない。 | Z dialogueのLR経路は新設しない(J-1の既定)。将来LRが配線される場合も既存`lr_used==0`・累積15回guardを維持 | TEST-10 | DESIGN_READY_FOR_OPUS(J-1) |
| R3-1 | §3① | 今回の『猿の手』『走れメロス』全編Trialで使用した文脈・感情情報生成方式とTTS指示を、承認済み仕様として正式Productionへ移植する。 | er118_fz_dialogue_context_tts_trial_01.py の extract_context/EMOTION_DEVELOPER/EMOTION_SCHEMA/validate_emotion_items/CONTEXT_HEAD・TAIL/build_context_block/style_for_arm を新Production moduleへ逐語移植 | TEST-01(Trial 53 clipのstyle_sha256 golden一致) | DESIGN_READY_FOR_OPUS |
| R3-2 | §3① | 未承認のPrompt改変、感情分類方式の変更、品質基準の追加・緩和は行わない。 | Prompt/rule 1-10/検査規則は逐語・sha固定。leakageはblockingにしない(観測のみ) | TEST-01(prompt sha固定)、DESIGN_01 §F | DESIGN_READY_FOR_OPUS |
| R3-3 | §3① | Trialの一時コードを単に呼び出すのではなく、正式初回Production経路として機能させる。 | Production moduleはer118を一切importしない。run_tts_stage前段に配線 | TEST-11(import禁止)、E-1 | DESIGN_READY_FOR_OPUS |
| R3-4 | §3② | 以下の経路すべてで同一仕様を保証する。<br><br>- 初回Production生成<br>- retry<br>- fallback<br>- regeneration<br>- resume<br>- 中断後の再開<br>- Local Rewrite<br>- Human Review Lock | 単一のattempt policy object(clip単位・永続state)が全経路の唯一の決定者。経路別の経路表=DESIGN_01 §C-8 | TEST-01〜10、E-1〜E-4 | DESIGN_READY_FOR_OPUS |
| R3-5 | §3② | 失敗が発生した場合も、残りの試行回数・状態・生成方式を正しく引き継ぐこと。 | state file(<level>/audit/dialogue_ctx_attempt_state.json)をattempt開始前/後に原子的に書く | TEST-07,TEST-09 | DESIGN_READY_FOR_OPUS |
| R3-6 | §3② | 特に、再開によって1〜2回目の文脈・感情付きTTSを不必要に再実行したり、3回の上限を超えたりしないこと。 | resumeはstateのn_startedから続行。started-but-unfinishedは消費済み扱い(安全側) | TEST-07,TEST-09,E-3 | DESIGN_READY_FOR_OPUS |
| R3-7 | §3③ | 3回目のFallbackでは、今回の文脈・感情情報をTTS指示から完全に除外する。 | attempt3のstyle引数=None。CONTEXT関連のどの文字列も合成関数に渡さない | TEST-05(Style完全除外・バイト一致) | DESIGN_READY_FOR_OPUS |
| R3-8 | §3③ | 従来方式のVoice、Style、速度、発音制御、品質検査を維持する。 | Voice=spec.voice、速度=Adv atempo 1.06外側ループ、発音=_norm_for_tts/PNAP、品質検査=既存unified judge+repetition QA(全て無変更) | TEST-05,TEST-12 | DESIGN_READY_FOR_OPUS |
| R3-9 | §3③ | 文脈・感情付き方式の一部設定が残り、従来方式と異なる音声になることを防ぐ。 | attempt3のprompt全体(STYLE+TEXT)がlegacy Zのprompt(HEAD時点)とsha一致をtestで固定 | TEST-05 | DESIGN_READY_FOR_OPUS |
| R3-10 | §3④ | ASR Primary／Secondaryの承認済み判定規則<br>- 発音・内容一致検査<br>- ASR表記揺れへの救済<br>- Local Rewrite／Natural English QA<br>- Human Review Lock<br>- STOP条件<br>- 音声の組立・音量・速度に関する承認済み仕様 | 全て無変更(generic loop内のASR/QA呼出は触らない)。hookはstyle選択と記録のみ | TEST-12、static diff確認 | DESIGN_READY_FOR_OPUS |
| R3-11 | §3④ | 特に、ASRの表記違いだけを理由に不要なTTS再生成を行わないこと。 | leakageを再生成理由にしない(観測のみ)。ctx固有の追加NG条件を作らない | TEST-13(表記揺れ入力で再生成0) | DESIGN_READY_FOR_OPUS |
| R4-1 | §4 | これらを隠さず、Production品質への影響を確認する。 | DESIGN_01 §E(6項目×既存Validator照合)、EXISTING_SPEC_CHECK §5 | 文書+Phase2観測 | DESIGN_READY_FOR_OPUS |
| R4-2 | §4 | 既存の承認済みValidator・組立・品質条件に反する問題は、承認範囲内で是正する。 | 現時点で『既存条件に反する』と確認できた問題=0件(DESIGN_01 §E)。新規発見時は同一委任内で是正 | Phase2観測 | DESIGN_READY_FOR_OPUS |
| R4-3 | §4 | ただし、Trial結果を理由に独自の新しい品質基準を設けたり、承認した文脈・感情方式を変更したりしない。 | 話速/ポーズ/音量差/F0の新gateは作らない(判断候補J-4として分離) | DESIGN_01 §E | DESIGN_READY_FOR_OPUS |
| R4-4 | §4 | 実質的な仕様変更が必要なら、理由とQCD影響を示してUSER_DECISION_REQUIREDで報告する。 | OPEN_TRACKING_01 判断候補J-1〜J-4 | Fable報告 | DESIGN_READY_FOR_OPUS |
| R5-1 | §5 | **Family Z専用のコスト増として管理する。Family X/Yは変更しない。** | BUDGET_PLAN_01(Z専用) | BUDGET_PLAN_01 | DESIGN_READY_FOR_OPUS |
| R5-2 | §5 | 1. 文脈・感情情報生成の追加費用<br>2. 文脈・感情付きTTSの費用差<br>3. Retry／Fallbackの発生率と期待費用<br>4. Local Rewrite・ASR追加費用<br>5. Family Zの記事セットあたり総量産単価<br>6. 制作時間への影響 | BUDGET_PLAN_01 §1の6区分表(出典付き。未確認は『未確認』) | BUDGET_PLAN_01、Phase2で実測置換 | DESIGN_READY_FOR_OPUS |
| R5-3 | §5 | 70円／記事セットの目標を継続する。品質を維持できる範囲で、情報生成の再利用・キャッシュ・不要な再生成防止によって原価を最適化する。 | 感情情報のrun内immutable cache(resumeでLLM再call 0)、state永続でresume時の再生成防止、fallback deferral案(BUDGET_PLAN §4) | TEST-14(LLM再call 0) | DESIGN_READY_FOR_OPUS |
| R5-4 | §5 | **品質 ＞ Delivery ＞ 量産単価。**<br><br>費用削減のために承認済み品質を下げないこと。 | 費用最適化は上記cache/再生成防止のみ。品質基準は触らない | DESIGN_01 §F | DESIGN_READY_FOR_OPUS |
| R6-1 | §6 | \| 1回目PASS \| 文脈・感情付き音声を採用 \| | TEST-01、E-1 | unit+runtime | DESIGN_READY_FOR_OPUS |
| R6-2 | §6 | \| 1回目NG、2回目PASS \| 即時Retry後に採用 \| | TEST-02 | unit(+runtime自然発生時) | DESIGN_READY_FOR_OPUS |
| R6-3 | §6 | \| 1・2回目NG、3回目PASS \| 10分クールダウン後、従来方式で採用 \| | TEST-03、E-2(強制NG注入、Std/Adv) | unit+runtime | DESIGN_READY_FOR_OPUS |
| R6-4 | §6 | \| 3回ともNG \| Local Rewrite／Human Review／STOPへ正しく移行 \| | TEST-04、E-4(Std/Adv) | unit+runtime(強制NG)。LR部分=J-1 | DESIGN_READY_FOR_OPUS(J-1) |
| R6-5 | §6 | \| retry途中で中断・再開 \| 回数・方式を維持 \| | TEST-07、E-3(Std/Adv) | unit+runtime(kill→resume) | DESIGN_READY_FOR_OPUS |
| R6-6 | §6 | \| X/Yの通常TTS \| 一切変更なし \| | TEST-12 | unit(バイト同一) | DESIGN_READY_FOR_OPUS |
| R6-7 | §6 | Mockテストに加え、正式Production runtimeで文脈・感情付き方式が実際に発火した証拠を取得すること。 | Phase 2 E-1(正式runner経由、実TTS request promptにCONTEXT有をsha/文字列で記録) | Phase 2 | Phase 2待ち |
| R6-8 | §6 | Fallbackは3回目まで偶発的に失敗するのを待たず、強制NGによるテストで遷移を検証してよい。ただし、Mockだけで通常経路全体をPRODUCTION_WIREDと判定しないこと。 | E-2はGate出力をNG方向にのみ上書きするdriver注入(Production code内に注入口を作らない)。E-1(正常経路)は注入なし | DESIGN_01 §H、TEST_PLAN §3 | DESIGN_READY_FOR_OPUS |
| R6-9 | §6 | 実際の正常経路・Fallback経路を区別して証拠を記録する。 | 証拠JSONに path=normal|forced_ng_fallback|forced_ng_resume|forced_ng_exhaust を必須記録 | Phase 2 | Phase 2待ち |
| R6-10 | §6 | Fableは独立して設計、コード、正式実行経路、回帰テスト、runtime evidenceを照合する。 | Fable照合チェックリスト=OPEN_TRACKING_01 §ゲート | Fable | Fable待ち |
| R7-1 | §7 | CURRENT_SPEC<br>- DECISION_LOG<br>- OPEN_ITEMS<br>- 必要な設計・runtime evidence<br>- Git commit／push | 本委任: DECISION_LOG/OPEN_ITEMS/UDR+設計文書。CURRENT_SPECはPhase1/2完了時(文案=DESIGN_01末尾) | git log | 本委任分DONE/CURRENT_SPECは後続 |
| R7-2 | §7 | 今回の正式採用をFamily Z専用仕様として記録する。 | DECISION_LOGエントリ+OPEN-528追記 | SSOT diff | DONE(本委任) |
| R7-3 | §7 | 旧方式は3回目のFallbackとして利用できるよう維持し、新方式が後続経路で参照されない等のDangling Referenceを防ぐ。 | legacy style(p9a.ENGLISH_STYLE_PREFIX)・build_reuse_key・style_text_for・_effective_style_sha・extract_attempt_evidence・verify_z_speed_profile を維持。新方式の参照点(reuse_key/entry/evidence/page/gate)を表で全列挙(DESIGN_01 §G) | TEST-15(Grep+参照表) | DESIGN_READY_FOR_OPUS |
| R7-4 | §7 | 完了報告では、Family Z Standard／Advancedそれぞれについて、正式初回生成・retry・fallback・resume・QA・実音声・コストを明示すること。 | Phase 2完了報告の必須表(Std/Adv×7項目)=OPEN_TRACKING_01 §完了報告雛形 | Phase 2 | Phase 2待ち |
| R7-5 | §7 | **すべてのGate条件を満たして初めてPRODUCTION_WIREDと判定する。**<br><br>未確認事項がある場合は、完了とせず残るOpen Itemと解消条件を報告すること。 | OPEN_TRACKING_01 §PRODUCTION_WIRED判定ゲート | Fable | Fable待ち |
| R8-1 | §8 | 既存の承認済み作業・日次予算内で、独立作業を並列化して速やかに進める。 | Phase 2 E-1〜E-4を並列(別run dir・別process)、Phase1は実装/テスト/証拠driverを並列 | BUDGET_PLAN §3 | DESIGN_READY_FOR_OPUS |
| R8-2 | §8 | 不要な追加Trialや磨き込みは行わない。 | 追加Trialなし。Phase 2は受入条件の最小証拠のみ | BUDGET_PLAN | DESIGN_READY_FOR_OPUS |
| R8-3 | §8 | 重大な品質・安全問題、予算超過見込み、承認範囲外の仕様変更が必要な場合はSTOPし、判断事項を整理する。 | 判断候補J-1〜J-4(OPEN_TRACKING_01) | Fable | DESIGN_READY_FOR_OPUS |
| R8-4 | §8 | **今回の最重要目的は、Family Zで文脈・感情付きTTSを標準方式とし、2回失敗した場合だけ、10分クールダウン後の3回目に従来方式へ戻すこと。そして、その動作を正式Productionの全経路で保証することです。** | 本設計全体(単一attempt policy+永続state+hook) | 全TEST+全E | DESIGN_READY_FOR_OPUS |

## §6 受入表(必須test登録)

6ケース(R6-1〜R6-6)は TEST_PLAN_01 の TEST-01(1回目PASS)/TEST-02(2回目PASS)/TEST-03(3回目PASS)/TEST-04(3回NG)/TEST-07(中断再開)/TEST-12(X/Y不変)に必須testとして登録した。runtimeはE-1(正常)・E-2(強制NG fallback)・E-3(強制NG+kill+resume)・E-4(強制NG 3回NG)。

