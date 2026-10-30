# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02 Closeout案(Trial専用・Production変更0・flag未実装)

作成: 2026-10-30。基点=origin/main `ff84fdb7d`。ユーザー原文=`docs/pm/delegation_log/2026-10-30_FX4-LATTER-APPROVAL-AND-FLAP-T-TRIAL_USER.md`(§3.3 Voice[:100]、§4.3 受入条件[:153-167]、§5 境界[:169])。設計=`DESIGN_01.md`、現状=`CURRENT_STATE_01.md`、Voice実測=`VOICE_PROBE_02.md`/`voice_probe_02.json`、offline再判定=`phase3_rejudge_02.json`(本書3節)。

## 1. 結論(Status案)
**VALIDATED(Trial合格。ただし条件4の回帰testはProduction未配線のため配線時に必須)。PRODUCTION_WIREDではない。Production採用はユーザー判断(D2、USER_DECISION_REQUIRED)。**
理由: 受入7条件のうち1・2・3・5・6・7を証拠で満たし、4は設計上の整合(各票PASSを1つ増やすだけ・最終ANDゲート不変)までを確認した。実装の回帰test(er006/er078/er104/er109)は未配線ゆえ未実施で、これを理由にVALIDATED止まりとし、採用判断時の前提条件として明記する。再Trialは見込みのある変更が無い限り行わない(同一方式の反復はしない、原文§4.2)。

## 2. 受入7条件(原文§4.3)への適合表
| # | 条件 | 判定 | 証拠(file:line / 実測) |
|---|---|---|---|
| 1 | 典型的Flap-T同音を適切に救済 | PASS | `tools/flapt_equivalence_proto_01_test_01.py` 36 PASS(今回再実行 `36 passed in 1.52s`)。正例P01-P12 12/12 RESCUE(`DESIGN_01.md:5節`、`case_results_01.json`)。**実音声で再現**: 全13 (Voice,path)組合せでlatter/atom/coating/betting等がd綴りで転写(`voice_probe_02.json`、例 Aoede|fl latter→OpenAI「Ladder」/Azure「Ladder.」/Whisper「ladder.」=FX4⑨と同現象)。実データRESCUE=latter→ladder・Bertie→Birdie(`stored_census_02.json`) |
| 2 | 単純なt/d置換による誤救済なし | PASS | 不変条件I-1/I-3(`DESIGN_01.md:2節`)。反例N01-N18全NG維持(0/18)、保存ASR転写の現行NG 1,336件(`stored_census_02.json` stats.ng_and_now_ng。母集団はtts_generation_results 422 file+HR queue 289行、重複backup含む)に適用してRESCUE=latter→ladder・bertie→birdieの**2語のみ**、他は0(誤救済0。`td_diff_declined` 80件はcanonical複数読み42・音素同一22・CMU未登録10等で非救済)。ten/den・time/dime・語頭語末・クラスターは非救済(N01/N02/N11/N17) |
| 3 | 音韻環境・母音差の不一致を無条件にPASSさせない | PASS | 母音完全一致I-2・AY/AW核は自動救済せずNG維持I-5(`flapt_equivalence_proto_01.py:21,106`)。N06(water/wader)・N07(letter/leader)・X01(writer/rider)・X02(title/tidal)。**実音声でI-5を補強**: writer 13組合せ39転写で「Rider」は1件のみ=ASRは通常 writer/rider を区別(`VOICE_PROBE_02.md`2節)→AY/AWを辞書で救済しない方針は妥当 |
| 4 | 既存ASR Gate・同音救済・retry・fallbackと整合 | **設計適合・回帰test未実施** | I-9(`DESIGN_01.md:2節`)。窓口=er109同型の第3層、`approved_equivalence`に編入しない(`er078_asr_unified_judge_01.py:73-77`)、呼出点は既存3箇所(`er006_secondary_asr_01.py:1135/1207`、`er104_kp_three_asr_vote_01.py:246`)で新規call siteなし。retry/fallback上限・最終ANDゲートは不変。**回帰test(er006/er078/er104/er109)はProduction未変更のため未実施=配線時必須(4節)** |
| 5 | 承認済み品質基準を引き下げない | PASS | 閾値・Gate・Prompt・辞書の変更0(今回のcommit対象はdocs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/配下のTrial専用file・`user_test/asr_flap_t_trial_01/`のみ)。根拠は音韻規則限定でASR収束を根拠にしない(I-7、`CURRENT_SPEC.md:1864`)。救済は必ず`FLAP_T_EQUIVALENT`warning付き(I-10) |
| 6 | Family・Voice・レベルごとの適用境界が明確 | PASS | Family=X/Y/Z run scope限定(A/B/C対象外。er109 `APPROVED_SCOPES`同型、`er109_xz_scope_01.py:92/100/149`)。Voice=(Voice, TTS path)単位の許可リスト(実証ベース、`VOICE_PROBE_02.md`3節。**未probe組合せ・Voice不明は不適用**)。レベル=Std/Adv同一規則で、Std 6%減速でもflapは維持(Aoede/Schedar/Zephyr実測、同2節) |
| 7 | 再生成削減効果と量産単価への影響を評価 | PASS(上限見積) | 3節。追加API **0円**(CMU辞書のみ)。削減見込み=下記3節。単価増0 |

## 3. Phase 3 offline再判定(API 0。`tools/flapt_phase3_rejudge_02.py`、出力 `phase3_rejudge_02.json`)
Production未変更・読取専用。Flap層ON/OFF=保存転写をTrial prototype(`flapt_equivalence_proto_01.evaluate`)で再判定し、『全NG転写がRESCUE・他のNG無し・(Voice,path)が許可リスト内』のattemptを`PASS_WITH_WARNING(FLAP_T_EQUIVALENT)`扱い。attempt費用は各runのtelemetryの実額(`er019_..._runner_01.compute_cost_jpy_so_far`で単価計算)÷TTS attempt数。他のGate(長さ・Repetition QA・Azureの本文転写等)は保存attemptに全部は残らないため再評価しておらず、**上限見積**。
| 対象 | OFF(実際) | ON(Flap層) | 回避可能attempt/費用(上限) |
|---|---|---|---|
| X ⑨ `latter`(meta_waddle_world b1b、Aoede flash-lite) | 4 attempt(+fallback/minimal/lock、telemetry上TTS 5回)全て OpenAI/Azure が「Ladder」→STOPPED→HR | attempt 1で OpenAI・Azure とも RESCUE → **初回PASS_WITH_WARNING**。HR 1件が不要 | 3 attempt、**約¥0.26**(1 attempt=¥0.085) |
| Z The Open Window a2 `full_story_part1_c14`(Zephyr 2.5-pro) | 7 attempt | attempt 1でPASS(Bertie→Birdieのみが差) | 6 attempt、約¥8.78(1 attempt=¥1.46) |
| 同 b1b `full_story_part1_c14` | 8 attempt | attempt 1でPASS | 7 attempt、約¥10.25 |
| 同 a2 `full_story_part3_c2`(Schedar 2.5-pro) | 4 attempt | attempt 1は別の語差(「what is you」)でNG維持、attempt 2でPASS | 2 attempt、約¥0.80 |
| 同 b1b `full_story_part3_c2` | 4 attempt | attempt 1でPASS | 3 attempt、約¥1.19 |
| **合計(上限)** | | | **X ¥0.26 / Z ¥21.0**(Zは1回のE2Eでの値。Family X/Yのvocab英語は1 attempt約¥0.085なので1件あたりは小さい) |
- Family別HR削減: 保存STOPPED/HR 132 segment中の救済可能は**1**(X ⑨ latter)=0.8%。ただし⑨は現に完成をBLOCKしていた構造的な穴で、同型語(latter型のflap語)が今後のvocab英語に出れば再発する。Z Bertie→Birdieは最終OKだが9 attemptを消費していた。
- 再確認: 保存ASR転写 6,979件・現行NG 1,336件(`stored_census_02.json`。`stored_census_01.json`比で+28転写は新規commit分[pre_fx4h backup copy等]を含む)にFlap層を当てた結果、RESCUEは**latter→ladder・bertie→birdieの2語(distinct 7組)のみ、誤救済0**(重複backup除く13 transcript)。REQUIRES_EXTRA_EVIDENCE=title→tidal 1件(AKB48 b1b、AY核)も自動救済せず。
- **試聴ページ**: `user_test/asr_flap_t_trial_01/index.html`(救済候補音声のみ18本[X ⑨ 4本+Z 14本]、mp3+想定テキスト+ASR転写+Voice+Flap層ON時の扱い)。判断依頼=『各音声が想定語を正しく発話しているか』のみ。ユーザー試聴は未実施=**誤救済0の最終確認は耳で未完**(全13 transcriptは機械判定が意図どおりの語であることをFZ記録[`PHASE4_RESULT_01.md:17`]と⑨の既存承認で裏付け)。

## 4. 残リスク
1. **AY/AW核(writer/rider・title/tidal)は自動救済しない=NG維持(HRへ)**。実音声ではASRが通常区別するため(39転写中Rider 1件)、救済の需要自体が小さい見込み。
2. **複数読みの語(putting=AH/UH等、I-4)は非救済**(`td_diff_declined` canonical_multiple_readings 42件の一部)。
3. **語境界をまたぐflap(what a→wad a)・R直後(party/hardy)・音節的n(eaten/Eden)は非対応**(v1の線引き。必要になれば別Trial)。
4. **Repetition QA方式A副作用**: flap語を含む3語以上のspanが台本内で意図的に繰り返される場合のみ偽NGの可能性(`CURRENT_STATE_01.md` a-3、`er011_open121_repetition_qa_production_01.py:582-634`)。配線時にtestで固定。
5. **Voice**: ASRのd綴りは『米音の証明』ではない(`VOICE_PROBE_02.md`4節)。許可リストは(Voice,path)単位で未probe組合せは不適用。Z本番で実使用の`Algieba|pro, Charon|pro, Puck|pro, Fenrir|pro, Aoede|pro`は未probe(追加probeで拡張可、約¥0.26x12 clip=約¥3/組合せ)。
6. 誤救済の型: TTSが本当に別語(ladder)を発話してもflap環境ゆえ音響的にほぼ同一なので学習者に聞こえる音は同じ。Flap層はwarning付きで事後試聴リストに入る(I-10)。

## 5. Production採用時の設計(推奨=実装形態B。採用された場合のみ。今回は実装しない)
- 新規module + `er109_...decision()`窓口に1呼出追加(er109本体は無変更。11-7(2)『既存Prompt・正規表現・閾値・辞書の直接編集には適用しない』に素直)。
- **既定OFFの単一flag読取関数**(env/引数/設定dictからONにできない)、起動script・`.env`で暗黙にONにしない、DefaultOffIsolation型test(flag未設定でAPI呼出0・出力不変・副作用file 0)。flag名と『未承認・既定OFF』を`OPEN_ITEMS.md`に記録しPRODUCTION_WIREDと呼ばない(11-7の5条件)。ただし**ユーザーがProduction正式採用した場合は11-7の限定例外ではなく通常のProduction実装**。
- `attempt_ctx`へ`voice`(effective_voice)とmodel pathを加算で渡す。voice/path不明=不適用。許可リストは単一SSOT file(sha付き、audit記録)。
- Store(master audio)再利用ガード: er109救済音声の再利用ガード(`er109_xz_scope_01.py:36-37` OUT_OF_SCOPE_BLOCK_REASON)と同型で、Flap救済で通った音声を許可外Voice/Family/flag OFFへ再利用しない。
- `make_voter`(`er104_kp_three_asr_vote_01.py:263/287`)のlabel判定にFLAP_T_EQUIVALENTを追加(票単位でwarning)。`ortho_contributed`相当の監査。
- 回帰test(必須): er006(`evaluate_attempt_with_cascade_detail`)、er078(unified judge・最終ANDゲート)、er104(3票多数決)、er109(UKUS層・ORTHO_BASIS)、Repetition QA(er011)。Trial protoの36 testをProduction側へ移植。
- 費用: API 0。独立作業(module実装・test・SSOT)は並列化可、回帰testは直列(同一file/state競合)。

## 6. 判断
- **D1(Phase 2 probe)**: 実施済み(承認範囲内。約¥29.64/Cap ¥30)。
- **D2(Production採用)**: ユーザー判断(提示のみ、自動格上げしない)。論点=①採用するか(効果は小さいが構造的な穴) ②許可リストを(Voice,path)単位の実証ベースで運用してよいか ③AY/AW等の非救済維持 ④試聴ページの結果。推奨=『採用する場合は形態B・既定OFF・上記配線で、試聴ページ(18本)で誤救済が無いことを確認後に判断』。
