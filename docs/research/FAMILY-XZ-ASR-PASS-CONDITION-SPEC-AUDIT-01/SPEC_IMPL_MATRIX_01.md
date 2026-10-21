# SPEC_IMPL_MATRIX_01 (FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_01、2026-10-22)

調査のみ。コード・Prompt・flag・Production無変更。有料API 0・費用JPY0。行番号はHEAD(31c80d76d以降)基準(`git show HEAD:<path>`)。使用モデル: Sonnet 5.5(調査実行)。ASR/TTSの実行なし(保存済みJSONの読取のみ)。
ケース判定の確定と修正着手はFable。本書は分類案と根拠。

## 0. 結論(先に)

| 対象 | ユーザー認識表 | 承認済み正式仕様(出典) | 実装(HEAD) | 分類案 |
|---|---|---|---|---|
| Key Phrase英語(X・Z共通) | Primary・Secondary両方PASS | **Primary PASSならSecondary不要**。KPは「判定のみ統一(Primary NG→Secondary 1回→WARNING採用)」。KPへの「両方PASS」の承認記録は**見当たらない** | Primary PASS→Secondary未呼出でPASS | **ケース1**(承認済み仕様がユーザー認識と異なる。実装は承認済み仕様どおり=不具合ではない) |
| Key Phrase以外の英語(X・Z共通、通常) | PrimaryがPASSすればよい | Primary PASS→PASS(AUW原文§2) | 同じ | **一致** |
| 非KP英語・同音救済(HOMOPHONE_EQUIVALENT) | Primaryのみ(「同音救済を含め」) | 古い文言CURRENT_SPEC.md:1839は「Secondary側が確認した場合のみPASS」。後続のAUWは「Primary PASSならSecondary不要」 | Primary単独でPASS(Primaryの救済層=cmu_alternate) | 実装=ユーザー認識表=AUW。**1839の文言が古く食い違う(SSOT文言の整合問題、コード不具合ではない)**。分類=一致(文書是正のみ) |
| KP英語・同音救済 | 両方PASS | 1839はSecondary要求、AUWはPrimary PASSでSecondary不要。KP専用の置換決定なし。判定が割れる | Primary単独でPASS | **判断が割れる(両論)**。実例0件(§6) |
| A2の非KP英語、minimal fallback経由 | Primaryのみ | 2026-08-26承認のfallback Secondary必須化(Primary PASSでもSecondary必須)をAUW U2(#84)で維持 | `force_secondary=True`(A2のみ) | ユーザー認識表と**一部不一致=承認済み例外**(ケース1相当の「表と異なる承認済み仕様」。ただしユーザーの目的に合致する安全側) |

最重要所見: **KPに対して「Primary・Secondary両方PASS」を承認した記録はSSOT内に存在しない**。その方式の根拠は`FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`(2026-10-21)で、ユーザー原文は「**検証する方針に同意した**」「**Production正式採用はTrial結果確認後に別途判断する**」(`docs/pm/delegation_log/2026-10-21_FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01_USER.md` L21-23)。つまり新仕様案(Trial)であり、承認済み仕様ではない。#136のKP限定Azure拒否権(C1dK/C5K)も同じ系統の未承認新仕様。

## 1. 承認履歴(a)〜(f)

(a) 「KPはPrimary・Secondary両方PASS」の承認記録: **見当たらない**。調査範囲=`CURRENT_SPEC.md`(`Primary.*Secondary.*両方`/`両方PASS`/`Key Phrase.*Secondary`のGrep、L1837-1839・L2111・L2813-2838・L452-454)、`DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`(`HOMOPHONE_EQUIVALENT`/homophone)、`docs/pm/delegation_log/*_USER.md`の`Secondary`を含む11件、`USER_DECISION_REGISTER_01.md`の#83〜#87・#136関連、`OPEN_ITEMS.md` OPEN-433/438。唯一の近縁=上記DUAL-PASS Trialの「検証方針に同意」(新仕様案)。`KP4-REMEDIATION-AND-ASR-THREE-WAY-TRIAL_USER.md` L63・L268は逆に「ASRのPrimary/Secondary変更・ValidatorのProduction仕様変更は禁止」「VALIDATEDはProduction採用を意味しない」。

(b) 「Primary PASSならSecondary不要」の承認: ユーザー原文(AUW、2026-10-15、`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md` L35-L64、§2「ユーザー承認済みの基本フロー」。各音声Section共通)の逐語:「**Primary PASSなら、その時点でASR合格。Secondaryは不要。**」(L53)/「Primary NGなら、不一致の種類によらず原則Secondaryを実行する。」(L54)。適用範囲L123以降にKey Phrase英語/日本語意味/英語解説が明示列挙され(L135-L137)、KP固有はL147「学習対象の英語表現は変更しない。既存Minimal Prompt／English Language Lockとの整合を確認。全体のTTS3回仕様との競合は整理する」のみで、**ASR合否の例外は書かれていない**。ユーザー承認: `APPROVED_FOR_PRODUCTION`(2026-10-15)、`PRODUCTION_WIRED`正式承認2026-10-16(`CURRENT_SPEC.md:2819`・同Closeout追記、原文`docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md` §1-A)。設計書の該当行: `er058_output/unified_all_roles_production_wiring_01/DESIGN_01.md` L194(X-B1-06 KP英語)・L204(X-A2-07)・L214(Z-ALL-01)=「KP既存例外(4回構成・Prompt切替・LRなし)を維持したまま**判定のみ統一**(Primary NG→Secondary 1回→WARNING採用)」。SSOT反映=`CURRENT_SPEC.md:2818`。

(c) 1839(homophoneはSecondary確認必須): `CURRENT_SPEC.md:1839`「Secondary(または2回目のASR)側の結果が(a)canonical文字一致または(b)ARPAbet完全一致を満たした場合のみPASS」。出典=ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15(2026-08-28)、`DECISION_LOG_HISTORY.md:5736`(状態DECIDED/VALIDATED)。ただし**同一commit `2b40165dc`(2026-08-28)のコード・docstringは既にPrimary単独判定**(`er006_secondary_asr_01.py:_step_alternate_pass` docstring「このステップ単独で判定してよい」、`evaluate_attempt_with_cascade_detail` L943-951「追加ASR無しで…」)。つまり文言とコードは承認当日から食い違う。**1839を置換・緩和した明示の後続決定は見つからない**。一方で次はPrimary単独PASSを前提にした記録: MDJF是正(`CURRENT_SPEC.md:452-454`、「保存済みPrimary転写がHOMOPHONE_EQUIVALENTでPASS」)、AUWの「Primary PASSならSecondary不要」(上記(b))、およびユーザー認識表(非KPはPrimaryのみ、同音救済込み)。1839の「(または2回目のASR)」はAUWで廃止された`Primary#2`のことで、既に古い。`DESIGN_01.md`/`DESIGN_02_ADDENDUM_01.md`にhomophone Primary単独PASSを明示して議論した箇所は見当たらない(L277は救済層の並び「Tier3→CMU Case A/homophone→M1」を記述するのみ)。

(d) KP英語phraseの承認済み例外: 4回構成(MINIMAL 2+ENGLISH_LOCK 2、`er003_v1_repro01_main_generate.py:679` `KEY_PHRASE_TOTAL_MAX_ATTEMPTS=4`、ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22、2026-09-01)/非ラテン文字時のSecondary再判定Cascade(ユーザー承認2026-09-06、`CURRENT_SPEC.md:2111`、`enable_non_latin_cascade=True`はKPのみ)/KP英語解説3回(OF-AUW-12)/disfluency QA(Whisper small local、`disfluency_qa=True`既定 `repro01:782`)/Master Audio Store(K2)hit時ASR 0(DESIGN_01 X-B1-09)。**いずれも「Primary・Secondary両方必須」ではない**。KP専用のforce_secondaryは存在しない(`git grep force_secondary HEAD`の本番コード呼出は(e)の1箇所のみ)。

(e) minimal fallback Secondary必須化: ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04 Part C(2026-08-26、`DECISION_LOG_HISTORY.md:4888-`、「fallback(minimal instruction)経由で生成された英語音声にSecondary ASR確認を必須化」)。実装=`er003_v1_crosslevel_audio_02_common.py:374-381`(`_run_a2_minimal_fallback_attempt`の`force_secondary=True`)のみ。AUWでU2(#84)として維持(整理済み(i)維持、`USER_DECISION_REGISTER_01.md:172,195`、ユーザー指示A-4 `2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md` L80-L96「根拠なく全レベルへ拡大してはならない」)。呼出元: `generate_english_segment_with_fallback`のA2経路(X=`er019:1290`[topic_intro]ほか、Z=`er063:804`[A2のtopic_intro])。**KPは通らない。B1(Advanced)も通らない**。

(f) Family Z固有: KP英語=`er063_family_z_audio_01.py:817-836`(`kp_en`、K2 primary 2+ENGLISH_LOCK 2、同じ`generate_narration_snippet_verified_strict`→`evaluate_attempt_with_cascade`、force_secondaryなし)。Z固有の判定例外(Dialogue=segment_id未渡しでTier1/role gate非適用など)は`DESIGN_01.md` L207-L216。「Primary・Secondary両方」を要求するZ専用承認は見当たらない。

## 2. Family × パーツ × 判定経路 対応表(英語主、JAは参考)

共通経路(X・Z共通): 呼出元→`generate_narration_snippet_verified_strict`(`er003_v1_repro01_main_generate.py`)/`voice01.generate_charon_english`/`generate_english_segment_with_fallback`→`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(adapter)→[Primary P-chain: `val.evaluate_attempt`→CS Eq層→Tier3→非ラテンKP→**CMU Case A/homophone(`_step_alternate_pass`)**→M1]→`er078_asr_unified_judge_01.unified_judge`(Primary PASS=最終ANDゲートのみ `er078:421-441`/NG=P1・P2・P3 Secondary 1回)。

| Family | レベル | パーツ | 呼出(file:line、DESIGN_01 §3.2準拠) | 通常Primary PASS | 同音救済 | Secondary呼出 | 承認済み仕様 | ユーザー認識表 | 仕様↔実装 | 表↔仕様 |
|---|---|---|---|---|---|---|---|---|---|---|
| X | A2/B1 | **KP英語phrase** | `generate_key_phrase_component_verified`(repro01:779)、X-A2-07/X-B1-06 | Primary PASS→PASS(force_secondaryなし) | Primary救済層でPASS(1839は旧文言) | Primary NG時のみ1回。非ラテン主体時はNG後に1回 | Primary PASS=合格。Secondary不要(AUW §2、DESIGN_01 L194,204) | **両方PASS** | 一致 | **不一致=ケース1** |
| X | A2/B1 | KP英語解説 | `generate_key_phrase_explanation_en_verified`(er019:690)、X-B1-07 | 同上 | 同上 | 同上 | 同上(max 3回) | 両方PASS(解説をKPに含めるか不明) | 一致 | 不一致の可能性(「KP」の範囲確認要) |
| X | A2/B1 | KP phrase_repeat | 複製のみ(er019:1081)、X-B1-08 | KP英語の判定継承 | 同左 | 新規呼出なし | 同左 | — | 一致 | — |
| X | A2/B1 | KP日本語意味 | `generate_a2_japanese_with_reading_safety`、X-A2-08 | JA Primary PASS→PASS | — | Primary NG時(U1発効後)のみ | AUW(JAはEXACT/NORMALIZEDのみ受理) | 参考 | 一致 | 参考 |
| X | A2 | 非KP英語(topic_intro等、**minimal fallback経由**) | `_run_a2_minimal_fallback_attempt`(crosslevel:374-381)、X-A2-01〜 | Primary PASS後も**Secondary必須** | Secondaryも要 | **force_secondary=True**(PrimaryがPASSでも呼ぶ) | 2026-08-26承認+U2維持 | Primaryのみ | 一致(承認済み例外) | **一部不一致(承認済み例外)** |
| X | A2 | 非KP英語(標準経路: 本文・見出し・短文・Comment等) | `generate_english_segment_with_fallback`標準/`generate_a2_segment_with_slowdown`等 | Primary PASS→PASS | Primary単独PASS(実例あり) | NG時のみ | AUW | Primaryのみ | 一致(1839の文言のみ古い) | 一致 |
| X | B1(Advanced) | 非KP英語全般 | `generate_news_narration_wide_margin`/`voice01.generate_charon_english`、X-B1-01〜05,09 | Primary PASS→PASS(**force_secondaryなし**) | 同上 | NG時のみ | AUW | Primaryのみ | 一致 | 一致 |
| X | A2/B1 | 固定shell(Master Store) | `ensure_all_shared_narration_*`、X-B1-09 | Store hit=ASR 0(再判定なし) | — | 未生成時のみ通常判定 | 既存仕様(DESIGN_01 L197) | Primaryのみ | 一致 | 一致 |
| Z | A2/B1 | **KP英語phrase** | `er063:817-836` `kp_en`、Z-ALL-01 | Primary PASS→PASS | Primary救済層でPASS | NG時のみ | Primary PASS=合格(同上) | **両方PASS** | 一致 | **不一致=ケース1** |
| Z | A2/B1 | KP英語解説 | `er063:688` `kp_expl_en`、Z-ALL-02 | 同上 | 同上 | 同上 | 同上 | 両方PASS(範囲確認要) | 一致 | 同上 |
| Z | A2/B1 | Narrator本文clip | `news_tail_fix.generate_news_narration_wide_margin`(er063:624)、Z-B1-01 | Primary PASS→PASS | Primary救済でPASS | NG時のみ | AUW | Primaryのみ | 一致 | 一致 |
| Z | A2/B1 | Dialogue | `bvoices.generate_voice_body_wide_margin`(er063:636-642)、Z-B1-02/Z-A2-02 | 同上(Tier1/role gate非適用) | 同上 | NG時のみ | AUW+DESIGN_01 L209-210 | Primaryのみ | 一致 | 一致 |
| Z | A2 | topic_intro(minimal fallback経由) | `crosslevel.generate_english_segment_with_fallback`(er063:804)、Z-A2-03 | fallback時**Secondary必須** | Secondaryも要 | force_secondary=True | 2026-08-26+U2 | Primaryのみ | 一致(承認済み例外) | 一部不一致(承認済み例外) |
| Z | B1 | topic_intro/Preview/Comment | `voice01.generate_charon_english`(er063:645)、Z-B1-03 | Primary PASS→PASS | 同上 | NG時のみ | AUW | Primaryのみ | 一致 | 一致 |
| X/Z | — | 全英語・再利用/継承 | `er019_family_x_validation_inheritance_01.rejudge_with_current_judge`(L233)、K2/Master Store | 保存転写を統一judgeでAPI 0再判定。Secondaryは新規に呼ばない(保存Secondary転写があれば使う) | 同左 | 新規0 | AUW DESIGN_02_ADDENDUM §3-1 | — | 一致(retry/fallback/regeneration/resumeとも同一のadapter→unified_judge) | — |
| X/Z | — | retry/fallback/regeneration/LR後 | `evaluate_attempt_with_cascade_detail`は唯一の入口。LR後v1=minimal fallback経路でforce_secondary(A2のみ) | 同上 | 同上 | 同上 | `CURRENT_SPEC.md:2820` | — | 一致 | — |

DEV/Trial専用経路との違い: `er088_kp_asr_dual_pass_trial_01.py:96`(`force_secondary=True`をKPに適用するTrial)、`er091_asr_three_way_trial_01_phase3.py:44-73`(C1d=両方PASS必須・C5/C5K=Whisper不一致時のみforce)は隔離Trial専用でProductionに接続されない。Production本番コードのforce_secondary呼出は`crosslevel_audio_02_common.py:381`の1箇所だけ(静的test固定、`er078_asr_unified_wiring_static_audit_01.py`)。

## 3. 重点4点

(i) KPで「Primary PASS・Secondary未呼出」でPASSする経路: **ある(通常の標準経路)**。出典=AUW原文L53・`CURRENT_SPEC.md:2818`・DESIGN_01 L194/204/214(KPは判定のみ統一)。実装=`er078_asr_unified_judge_01.py:438-440`(`not ctx.force_secondary`ならPASS)、KPはforce_secondary未指定(`repro01:350-365`、`er063:827-836`)。

(ii) 非KPでhomophone救済がPrimary単独でPASSする経路: **ある**。`er006_secondary_asr_01.py:943-951`(`cascade_eligible`→`_step_alternate_pass`→`HOMOPHONE_EQUIVALENT`、`layers="cmu_alternate"`)。1839との関係: 1839は「Secondary側でPASS」と読める古い文言で、同日のコードと食い違い、AUW(後続のユーザー承認)・MDJF(`CURRENT_SPEC.md:452-454`)・ユーザー認識表はPrimary単独を前提とする。**実装を直すのではなく1839の文言を現行(Primary単独、旧Primary#2廃止)に整合させる文書是正が最小**。

(iii) minimal fallbackのforce_secondaryが効く範囲: **A2の非KP英語セグメント(`generate_english_segment_with_fallback`経由のtopic_intro等)のみ**。KPには効かない(KPは専用4回構成で`generate_key_phrase_component_verified`)。B1・Z B1にも効かない。Z A2のtopic_intro(er063:804)には効く。

(iv) #136(OPEN-438、C1dK/C5K)の位置づけ: **新仕様**(承認済み動作の回復ではない)。根拠: (a)承認済み仕様にKPのPrimary・Secondary両方PASSが無い(§1(a))、(b)ユーザー原文は検証方針への同意のみで「正式採用は別途判断」、(c)`KP4-REMEDIATION-AND-ASR-THREE-WAY-TRIAL_USER.md` L63/L268が「Production仕様変更禁止・VALIDATEDは採用でない」と明記。したがって「不具合修正」ではなくユーザー正式採用が必要な新仕様の候補。KPで両方PASSを本番化するなら#136の判断に統合するのが整合的(重複した別系統の改修は混同を招く)。

## 4. 仕様と実装の不一致箇所(コード側)

| # | 箇所 | 内容 | 影響 |
|---|---|---|---|
| D1 | `CURRENT_SPEC.md:1839` ↔ `er006_secondary_asr_01.py:943-951` | 文言「Secondary側がPASSした場合のみ」 vs 実装「Primary単独で`HOMOPHONE_EQUIVALENT`」。2b40165dc(2026-08-28)当日から存在。置換決定なし | 非KP・KP共通。実運用の記録はPrimary単独を前提(MDJF、AUW、ユーザー認識) |
| D2 | ユーザー認識表(KP=両方PASS) ↔ 承認済み仕様(KP=Primaryで合格) | 実装は承認済み仕様どおり。**コード不具合ではない** | KP全10音声/記事。ユーザー意図(誤発音検出強化)は#136未決のため現行未実現 |
| D3 | ユーザー認識表(非KPはPrimaryのみ) ↔ A2 minimal fallback force_secondary | 承認済み例外(2026-08-26)。表と異なるがユーザー承認済み | A2のfallback発動時のみ。B1・Zのfallback無し |

実装がユーザー認識表または承認済み仕様に反している「真の不具合」は、本調査範囲では**見つかっていない**(D1はSSOT文言側の古さ、D2・D3は仕様差)。

## 5. 行ごとの分類案と決め手

| 行 | 分類案 | 決め手 |
|---|---|---|
| KP英語phrase(X・Z) | ケース1 | AUW原文L53・DESIGN_01 L194/204/214・2818。両方PASSはDUAL-PASS Trial(検証同意のみ、正式採用は別判断) |
| KP英語解説(X・Z) | ケース1の可能性(「KP」に含むかの確認が必要) | 解説もAUWで同じ判定(DESIGN L195,215)。ユーザー認識表の「Key Phrase」範囲が不明(未確認) |
| 非KP通常 | 一致 | 同上 |
| 非KP homophone | 一致(文書是正のみ) | 実装=表=AUW。1839が古い |
| KP homophone | 両論 | 1839(旧承認)+ユーザー認識表=Secondary要。AUW(新承認)=Primary救済層もPrimary PASS。決め手: ユーザー確認(実例0件のため緊急性なし) |
| A2 minimal fallback非KP | ケース1相当(承認済み例外) | 2026-08-26承認+#84維持 |

ケース2(表どおり、実装が不具合)に該当する行: **なし**。したがって「修正着手」ではなく、Fableが(1)KPの扱いをケース1として報告、(2)D1の1839文言整合を文書是正として自律実行、を判断する材料とする。

## 6. 保存転写からの実例件数(費用0、読取のみ。`er0*_output/**/tts_generation_results.json` 283件)

- KP英語の採用attempt(`status=OK`・`verified=true`): 593件のうち**Secondary未呼出(Primary単独PASS)591件**、Secondary呼出2件。母集団は旧run含む(統一judge以前のrunも含むためAUW前の挙動を含む)。
- 統一judge記録(`asr_judgement`)が`HOMOPHONE_EQUIVALENT`を含む件: 計8件(X・非KPのみ): Primary側ラベルでPASS=**6件**(`manga_ai_chat_byus__run_byus_01` 4、`middle_east_yemen_saudi__run_mey_02` 2、すべて`secondary.called=false`=Primary単独)、Secondary側ラベルのPASS_WITH_WARNING=2件(byus)。**KPのhomophone救済PASS=0件、Z=0件**。
- 既存オフライン集計(再利用): Master Store EN KP 333件中、Primary PASSかつlocal Whisper転写が不一致=28件(8.4%、`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/OFFLINE_C5K_TRIGGER_RATE_01.md` §3)。KPを両方PASSにしたとき追加でSecondaryを呼ぶ量=全KPPrimary PASSで本来未呼出の約590件分。
- 限界: 集計は走査ロジックを一時作成・1回実行(スクリプトは保存しない)。件数は旧run混在。Primary NG→Secondary救済の別件(`SECONDARY_ASR_CORROBORATED_MATCH`91件等)は本問いに含めない。

## 7. 修正する場合の最小変更案(実装はしない、判断はFable)

- **KPを両方PASSにする案(=#136系の新仕様、ユーザー採用が前提)**: 変更点は`generate_key_phrase_component_verified`(repro01:779)とZの`kp_en`(er063:817-836)から`evaluate_attempt_with_cascade`へ`force_secondary=True`を渡すだけ(Primary PASSでもSecondary必須、既存の`secondary_forced`経路 `er006:987-988`を再利用)。X・Z同時に反映される共通関数経由。副作用: Azure追加呼出がKP10音声/記事、Secondary障害時は`NG_SECONDARY_UNAVAILABLE`(circuit breaker)でKP生成が止まり得る。**承認前はDefaultOffIsolation型の単一flagに限定(PM_GOVERNANCE 11-7の5条件)**。出典の費用: DUAL-PASS Trial量産追加見込み≒JPY0.6〜0.9/記事セット(OPEN-433)、70円目標の約1%。これは**不具合修正ではなく新仕様**なので本委任の自律範囲外。
- **D1(1839の文言整合)**: `CURRENT_SPEC.md:1839`へ「2026-10-15 AUW以降、Primary救済層(CMU Case A/homophone)がPASSした場合はPrimary単独でPASS。『(または2回目のASR)』はPrimary#2廃止で失効」と**追記**(既存行は書換えず追記、コード無変更)。DECISION_LOGに「文言整合の文書是正」を1行。test・runtime evidence不要(動作無変更)。
- **test/runtime evidence計画(新仕様をユーザーが採用した場合のみ)**: unit(force_secondary=True KP、Secondary障害、cache)、DefaultOffIsolation、X・Z integration(mock engine)、正式Production経路の実API最小runtime(KP 1〜数音声、Azure+OpenAI、費用は上記出典で数円以下と見込む=未確認)。今回は実行しない。

## 8. 未確認事項

1. ユーザー認識表の「Key Phrase」に「KP英語解説(kpN_explanation_en)」を含むか。
2. KP homophoneのPrimary単独PASSに対するユーザー意図(両論、§5)。
3. Master Store(K2)再利用時の判定継承の実機確認(コード上はASR 0、`DESIGN_01.md` L197)。
4. 保存転写の走査はHEAD外の作業tree(他agent・過去runの未commit差分を含む)を読んだ。件数は目安。
5. 2b40165dc当時にユーザーが「Primary単独」を明示承認したか(文言から断定できない。`INVESTIGATION_01.md` §8-1と同じ結論)。
