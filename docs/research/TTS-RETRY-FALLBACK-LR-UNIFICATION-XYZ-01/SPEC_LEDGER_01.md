# SPEC_LEDGER_01 — ユーザー原文(§2・§3・§4・§5・§6)の要件ID分解と現行→新仕様の差分

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(設計)。原文=`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`。
現行=棚卸し`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`(REPORT_01のU-ID・P1〜P8・COMMON_CORE_01の場所)。設計項目=`DESIGN_01.md`のD番号。
差分の種類: 回数 / 待機 / Style / LR構成 / 分類是正 / 撤去 / 追加(新設) / 維持。ユーザー最終報告§8-2「変更前後の差分」の素案を兼ねる。

## 1. 基本フロー(原文§2)

| ID | 要件(原文の趣旨) | 現行実装(U-ID・ファイル:行) | 新仕様 | 差分の種類 | 設計 |
|---|---|---|---|---|---|
| F-01 | ①通常Style→NG→②**同じStyle** | 全英語leaf: ①②は同一Style(P1〜P7)。Z ctxは①②ctx(er122) | 変更なし(①②は呼出側が渡したStyleのまま) | 維持 | D1 |
| F-02 | ②NG後・③直前に**180秒**待機。①②PASSなら待機なし | `COOLDOWN_SECONDS=600`(er020:57)。cs=True部位のみ(voice01:156/news_tail_fix:149/crosslevel:200/repro01:339)。JA・KP・KP解説・shell・Z topic(U-06)は待機なし。Z ctxは分割sleep(er122:298-338) | 全部位(表のとおり)で②NG後・③実TTS直前に180秒。1箇所定義・STOP確認つき | 待機(600→180)+待機新設(JA/KP/KP解説/Z topic/Z legacy) | D2 |
| F-03 | ③=Fallback Styleに切替 | Std英語/JA: ③=minimal(L3/L7)。**Adv英語: Style不変、技術エラー時のみ切替(F-Tech)**(voice01:179-216/news_tail_fix:171-181)。Z ctx: ③従来Dialogue。KP: ③④ENGLISH_LOCK。KP解説: Fallbackなし(U-08) | Std英語/JA=既存短文Style(維持)。**Adv英語=短文Style新規適用**。Z ctx=従来Dialogue(維持)。KP=ENGLISH_LOCK(維持)。KP解説=短文Style(適合確認済み §8) | Style(Adv英語・KP解説) | D1/D3/D9 |
| F-04 | LRありなら③NG→**問題箇所を1回だけ書換え→元と同じ3回構成で再生成** | LR再TTSは**1回のみ**(`max_attempts=1`: voice01:365/news_tail_fix:372、L3は`_run_a2_minimal_fallback_attempt`直呼び:crosslevel:425)。再入可(U-01/OPEN-376) | LR後は①'②'(同じStyle)→180秒→③'(Fallback Style)。再入なし | LR構成(1→3回) | D4 |
| F-05 | LR後もNGならHR/STOP。LRなしなら③NGでHR/STOP | 現行もHR/STOP(Lock)。HRQ行がLR前に書かれる(U-04) | 終端NGでLock+HRQ(1行) | 維持+HRQ契機一本化 | D5 |
| F-06 | 最大回数: LRあり6/待機2(360秒)、LRなし3/待機1(180秒)、**KP英語のみ4(通常2+ENGLISH_LOCK2)** | LRあり総4(2+1+LR後1 or 3+LR後1)、LRなし総3、KP4(前段2+ENGLISH_LOCK2、待機なし) | LRあり6、LRなし3、KP4。待機はブロックごと1回 | 回数 | D1 |
| F-07 | LRは最大1回。**LR後に再度LRへ入る再帰処理は禁止** | voice01/news_tail_fixは再入可(U-01、実例3件)。L3は再入なし | 深さカウンタ`BlockCtx.depth`で構造的に禁止(+`run_local_rewrite_recovery`のdepthガード) | 撤去(再入経路)/追加(depth guard) | D4 |
| F-08 | LR後の原稿にも元の品質Gate・ASR・音声QAを適用 | 統一judge(書換え後文を正解: er020:815)、`script_version=v1`、`m1_anchor_text`。QAは部位ごとに元引数を転送(L2のみStyle脱落: U-02) | LR block内の全attemptで元と同じ引数一式(Style含む)・同じjudge・同じQA | LR構成/分類是正(OPEN-312) | D4 |
| F-09 | 技術的エラーの既存即時再試行は別枠で維持。安全上限・STOP維持 | `_call_tts_with_retry(max_retry=1)`(各TTS呼出内)・F-Tech・ER-011累積15/ASR60・RESTART_STORM等 | 変更なし | 維持 | D14 |
| F-10 | 3分待機の目的=連続生成を避ける。品質基準は緩和しない | — | `cooldown_core`は待機のみ。判定閾値・ASR・QAに触れない | 維持 | D2 |
| F-11 | 実績観測後の回数削減検討は今回しない | — | 回数は原文のまま | 維持 | — |

## 2. 音声部位別の正式仕様(原文§3の表)

| ID | 対象(表の行) | 3回目Fallback | LR | 最大TTS | 現行→新(要点) | 該当行(ROW_MAPPING) | 設計 |
|---|---|---|---|---|---|---|---|
| S-01 | XYZ Std 英語本文・Comment等 | 既存の短文Style | あり | 6 | 総4→6、待機600→180、LR後1→3構成、再入禁止、Style保持 | EN_LR_STD 10行 | D1/D4/D6 |
| S-02 | XYZ Adv 英語本文・Comment等 | **短文Styleを新規適用** | あり | 6 | 総4→6、Style不変→③短文、待機600→180、LR後1→3構成、再入禁止、LR再TTSのStyle保持 | EN_LR_ADV 14行 | D1/D3/D4 |
| S-03 | Z Std/Adv セリフ(文脈・感情) | 承認済みの従来Dialogue Style | 現状なし | 3 | 待機600→180(共通化)、LRは追加しない | Z_DLG_CTX 2行(+legacy 2行=A-2) | D10 |
| S-04 | XYZ Std 日本語音声 | 既存の日本語短文Style | なし | 3 | 待機なし→180新設 | JA_STD 8行 | D7 |
| S-05 | XYZ Std/Adv Key Phrase英語 | ENGLISH_LOCK | なし | **4維持** | 待機なし→②NG後(ENGLISH_LOCK段直前)に180秒新設。2+2維持 | KP_EN 6行 | D8 |
| S-06 | XYZ Adv KP英語解説(音声が存在する経路) | 既存短文Styleの適合確認。不可なら同一Style | 現状なし | 3 | Fallbackなし・待機なし→短文③+180秒(適合確認済み §8) | KP_EXPL 3行 | D9 |
| S-07 | Z Std/Adv 冒頭英語(topic_intro_en) | 短文Style | あり | 6 | **部位判定不備(U-06)を是正**。総3・LRなし・待機なし→総6・LRあり・待機あり | EN_LR_STD(Z-A2-TOPIC)+EN_LR_ADV(Z-B1B-TOPIC) | D11 |

### 2-1. 整合確認(原文§3「部位・Familyの整合確認」)

| ID | 確認項目 | 結果 |
|---|---|---|
| C-01 | 既存49行を再照合し、Preview/Comment/Full Story/chunk/In One Line/Topic Intro/Y各Voice/Key Phrase/日本語に適用漏れがない | ROW_MAPPING_01で49/49行にpolicyを付与(漏れ0を機械確認) |
| C-02 | Family YのVoice音声は英語本文と同一の共通処理が適用可能か。Voice既定Style不変 | 可(Y-S-06/Y-B-05は`y_voice_*`→FULL_STORY[er020:132]で本文と同じleaf・同じpolicy)。①②は呼出引数のまま、③のみFallback。**Voice既定Style・Y runnerのStyle profile(OPEN-537)は変更しない** |
| C-03 | Zセリフ=文脈・感情2回→180秒→従来1回、LR追加しない | S-03 |
| C-04 | Z冒頭英語の未分類是正 | S-07/D11 |
| C-05 | Adv英語「品質NGではStyle不変」を3回目短文Styleへ | S-02/D3 |
| C-06 | Adv KP解説: 正式経路にTTS音声が実在する場合のみ適用。存在しない学習テキストは音声化しない | 実在(X/Y/Z 3行)。新規音声化なし(§8) |
| C-07 | KP解説で短文Styleが不適なら「同一2回→180秒→同一③→HR」 | 適合と判断。実測で不適なら`style_seq`1行変更で縮退 |

## 3. LR安全条件(原文§4)

| ID | 要件 | 現行 | 新仕様 | 差分 |
|---|---|---|---|---|
| L-01 | LRの有無は現行を基本。新規拡張しない | LRあり22行 | 24行(+Z topic_intro_en 2行のみ)。JA・KP英語・KP解説・Zセリフ・shell固定英語は追加しない | 分類是正のみ |
| L-02 | LRで書換えるのはNGに関係する局所部分のみ | `identify_ng_span`→Luna局所候補→7 Gate | 不変(`run_local_rewrite_recovery`本体は変更しない) | 維持 |
| L-03 | 既存の意味保持・書換え品質Gate・本文整合の安全条件を維持 | 7 Gate+全文性+unchanged_ratio最大+In One Line文数不変 | 不変 | 維持 |
| L-04 | LR後の再TTSは最大3回、再LRなし | 1回、L1/L2は再入可 | 3回構成・再入なし | LR構成/撤去 |
| L-05 | 話者・Voice・速度・承認済みStyle・chunk構造を保持 | L2はStyle脱落、L3はminimal、L1は保持(U-02/OPEN-312) | 全leafで元の引数一式を転送。chunk境界・planは不変 | 分類是正 |
| L-06 | 書換えによる音声と表示本文の関係、HR Lock、regeneration/resumeとの整合 | `local_rewrite_recovery`・`canonical_text_before_local_rewrite`・ledger_deviation(最初の書換えのみ=OPEN-376 D-B6)。Lock keyは元原稿 | 再入が無くなり「最初=唯一」で記録が一致。Lock key・承認keyは元原稿のまま。`BlockProgress.lr_used`でresume時のLR二重実行を防止 | 維持+是正 |
| L-07 | OPEN-376(LR再入)・OPEN-312(Style脱落)を解消 | 既知OPEN | D4で解消 | 撤去/是正 |
| L-08 | ASR一致でも繰り返し・言い淀みQAでNGのケースを適切に扱う。LR適用不可なら無益な後続処理を避ける。ただし再試行フロー・180秒待機を省略しない(U-03) | ③NG後にLR不発→HR(cooldown10分+3回は既に払済)。HRQ行が出ない場合あり(U-04b) | ①②→180秒→③は実行。③NG後に`lr_applicable`(0 API)で不可なら即HR(LR LLM・LR blockなし)。HRQは終端で必ず1行 | 追加(判定)/HRQ一本化 |
| L-09 | 日本語・KP英語・Zセリフ等へ独断でLRを追加しない | — | 追加しない | 維持 |

## 4. QCD・実装方針(原文§5)

| ID | 要件 | 設計での対応 |
|---|---|---|
| Q-01 | 品質: ASR判定・自然な発話・繰り返し/言い淀み検査・HR Lock維持 | 判定閾値・ASR・QA・Lockに触れない(D14)。Gate方針も変更しない(D13) |
| Q-02 | 速度: 独立作業は並列化、不要な待機・日付分割をしない | 実装(委任_02)はFamily別test/evidence driverを並列、evidenceはprocess並列(EVIDENCE_PLAN) |
| Q-03 | 量産原価: 再試行・LR・ASR増加の原価影響を計測。失敗時のみ追加処理、PASS済みを再生成しない | BUDGET_PLAN。LR block・③はNG時のみ。PASS済みは再利用(`_generate_or_reuse`/`BlockProgress`) |
| Q-04 | 実装の簡素化: 共通関数を再利用、Family別ロジックを増殖させない | `BLOCK_PROFILES`1表+`cooldown_core`+`lr_recover`+`kp_two_stage`。DESIGN_01 §4の削減数 |
| Q-05 | 旧条件(10分待機・旧3/4の数え方・LR後1回・Advの技術エラー時のみStyle切替)が正式経路・Validatorに残らない | REMOVAL_01(scope内の正式経路から撤去。scope外=A/B/Cのみ残置、Grepで残存を確認) |
| Q-06 | 旧仕様の撤去: 矛盾するPrompt・分岐・検査・文書を整理しDangling Referenceなし | REMOVAL_01の撤去一覧+Dangling Reference Grep手順 |
| Q-07 | モデル・Voice変更はScope外 | 変更しない(③のStyleは既存のもののみ) |

## 5. Production Wiring・受入条件(原文§6)

必須検証V-01〜V-12。各項の検証手段はTEST_PLAN_01(offline)とEVIDENCE_PLAN_01(runtime)に対応づけた。

| ID | 必須検証 | 検証手段 |
|---|---|---|
| V-01 | ①PASS→追加生成・待機なし | T-BLK-01 / E-N(normal) |
| V-02 | ②PASS→待機なし | T-BLK-02 / E-N |
| V-03 | ①②NG→180秒→Fallback③ | T-BLK-03 / E-S1(代表leaf) |
| V-04 | LRなし→③NG後HR | T-BLK-04 / E-S3 |
| V-05 | LRあり→③NG後LR1回→書換え後3回構成→最終NGでHR | T-LR-01〜03 / E-S2a・E-S2b |
| V-06 | LR再入なし、最大回数を超えない | T-LR-04/05 / E-S2b(TTS 6回・待機2回・LR 1回を計数) |
| V-07 | KP英語のみ4回構成と180秒待機の整合 | T-KP-01〜03 / E-S4 |
| V-08 | Std/AdvのStyle・Voice・速度保持 | T-STY-01〜04 / E-S1・E-S2(記録されたstyle_prefix/voice/速度) |
| V-09 | LR後のQA・ASR・採用判定 | T-LR-06 / E-S2a(LR後v1判定・PASS_WITH_WARNING) |
| V-10 | runtimeでFallback Style切替と実待機時間の証拠 | E-S1(`cooldown_actual_seconds>=180`、`style_prefix`が③でFallback) |
| V-11 | HR Lock・キュー・Assemble BLOCK・STOP | T-HRL-01〜06 / E-S2b・E-S3(Lock・HRQ1行・rc/Gate) |
| V-12 | retry/regeneration/resumeでの重複生成・重複待機防止 | T-RES-01〜06 / E-S6(待機中kill→resume) |
| V-13 | 実際のmodel_id・routing・Style/Prompt・試行回数・待機時間・LR実行回数・最終判定が検証可能 | evidence JSONの必須キー(EVIDENCE_PLAN §4) |
| V-14 | Fable独立受入・CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Git反映 | 委任_04(Fable) |

## 6. 差分一覧(ユーザー最終報告§8-2の素案)

| 項目 | 変更前 | 変更後 |
|---|---|---|
| 待機 | 固定600秒(cs=Trueの英語のみ。JA・KP・KP解説・Z topic_intro_enは待機なし) | 180秒(全対象部位、②NG後・③直前のみ。ブロックごと1回) |
| Adv英語の3回目 | 同一Style(技術エラー時のみ切替) | 短文Style(Stdと同じ) |
| LR後の再生成 | 1回(L1/L2は再入し得た) | 元と同じ3回構成(①'②'→180秒→③')、再入禁止 |
| 最大TTS(LRあり) | 総4(再入時は非有界) | 6(待機2回=360秒) |
| LR再TTSのStyle | 部位で違う(保持/脱落/minimal) | 元の①②Style→③Fallback Styleに統一 |
| ASR PASSでQA NGの音声 | 600秒待機・③後にLR不発→HR | 180秒・③後にLR適用可否を0 APIで判定、不可なら即HR |
| Z冒頭英語 | 待機・LRなし(未分類) | 他の英語と同じ(待機あり・LRあり) |
| KP英語 | 2+2(待機なし) | 2+2維持+ENGLISH_LOCK段直前に180秒 |
| KP英語解説(Adv) | 同一Style3回・待機なし | 同一2回→180秒→短文③ |
| 日本語(Std) | 2+JA短文1(待機なし) | 同左+③前に180秒 |
| Zセリフ(ctx) | ctx2→600秒→従来 | ctx2→180秒→従来 |
| HR queue行 | LR前に書かれLR成功でも残る/QA単独NGでは出ない | 終端NGで1行 |
| 減速後再検証の最終NG(Std本文) | LRなしHR(U-09) | 案A採用ならLRへ(案C縮退時は例外として据置) |

## 7. 要件のトレーサビリティ(要件→設計→test→evidence)

F-02→D2→T-CD-*→E-S1/E-S6 / F-03→D1・D3→T-STY-*→E-S1 / F-04・F-07・F-08→D4→T-LR-*→E-S2a/E-S2b / L-08→D5→T-LRN-*→E-S7 / S-07→D11→T-ROLE-*→E-S2(Z) / S-06→D9→T-KPX-*→E-X5 / V-12→D12→T-RES-*→E-S6。詳細表はTEST_PLAN_01 §7。
