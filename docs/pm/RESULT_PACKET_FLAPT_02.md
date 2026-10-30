# RESULT_PACKET_FLAPT_02 — ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02(2026-10-30。Trial専用・Production変更0・flag未実装)

要約: Phase 2 Voice probe(実音声155clip+Std6%減速36、13 (Voice,path)組合せ)・Phase 3 offline再判定・Closeout案を完了。Status案=**VALIDATED**(条件4の回帰testは配線時必須)、Production採用=ユーザー判断(D2)。
- 費用: 約¥29.64(TTS ¥19.93[Gemini token実測]+ASR ¥9.71[Azure秒換算+OpenAI概算])/Cap ¥30固定内。Iapetus|pro末尾3clip(約¥0.8)はCap厳守で未実行(件数削減ではなく停止)。
- Voice: 全13組合せでd綴り転写(flap実証)、T_SPELLED 0件、Std6%減速でも維持。許可リスト案=(Voice,path)単位の実証ベース、未probe組合せ(Algieba|pro等)は不適用。writer(AY)はASRが通常区別(39転写中Rider 1)→AY/AW非救済維持。
- Phase 3: ⑨ latterはON時に初回PASS_WITH_WARNING(回避3 attempt約¥0.26)。Z Bertie→Birdie回避上限約¥21.0(1 E2E)。保存転写現行NG 1,336件でRESCUE=latter/bertieの2語のみ・誤救済0。試聴ページ=`user_test/asr_flap_t_trial_01/index.html`(18本、ユーザー試聴待ち)。
- 証拠: `docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/`の`VOICE_PROBE_02.md`・`CLOSEOUT_02.md`・`voice_probe_02.json`・`phase3_rejudge_02.json`・`probe_02*/results.jsonl`(原記録)・`tools/flapt_*_02.py`。worktree=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\scratchpad\wt_flapt`(残置)。

原因仮説・観測・差分・次の一手: (a)観測=全Voiceで文脈無し発話のlatter/atom/coating等がd綴りに倒れる(`voice_probe_02.json`、Aoede|fl latter 3系統すべてLadder=FX4⑨再現)。(b)前回(委任_01)との差分=設計と辞書全体の救済面(API 0)→今回は実音声で『実害が全Voiceで再現しうる』『減速でも維持』『ASRはwriter/riderを区別』を実測。(c)次の一手=ユーザー試聴ページの確認→Production採用可否(D2)。採用なら形態B+回帰test。追加価値のある再Trialは現時点で無い(同一方式の反復はしない)。OPEN_ITEMS.md: OPEN-626行への追記はmain側の他agent編集と**競合(UU)**したため解決せず、追記案を`docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/OPEN626_APPEND_02.md`に保存(Fableが行末へ反映)。改善見込みの自己評価: 追加probeは許可リスト拡張(Z本番のpro経路Voice 5組合せ≒¥15)のみ。

RESULT_PACKET 4行:
(1) 既存仕様整合: `docs/pm/delegation_log/2026-10-30_FX4-LATTER-APPROVAL-AND-FLAP-T-TRIAL_USER.md`:100(§3.3)/153-167(§4.3)/169(§5)、`CURRENT_SPEC.md:1864`(ASR収束≠発音検証)、`er078_asr_unified_judge_01.py:73-77`(approved_equivalence非編入)、`er109_xz_scope_01.py:92/100/149`(run scope+単一flag前例)、`er104_kp_three_asr_vote_01.py:246/263`、`er006_secondary_asr_01.py:1135/1207`、`er002_gemini_client.py:54,62-70`。
(2) Production到達経路の未承認機能の既定値: 追加なし(flag未実装・Production file変更0=`git diff`はOPEN_ITEMS.md/ACTIVE_TASK.mdのSSOT追記と新規file[docs/research/…/、user_test/asr_flap_t_trial_01/、本file]のみ。Grep: `flapt`を参照するProduction import 0)。11-7限定例外は未使用。
(3) 失敗終了時の最終成果物: 失敗終了なし(正常終了)。最終成果物=上記証拠一式+試聴ページ。ユーザー原文§4(Trial設計検証)・§3.3(Voice確認)・§4.3(受入7条件)に対し、実音声で適用境界を実証し、7条件適合表(条件4は設計適合・回帰test未実施と明記)を提示した。誤救済0の最終確認は試聴ページのユーザー確認が未完。
(4) 撤去・残置: 撤去した規則・検査・test 0。残置=Trial prototype(`tools/flapt_equivalence_proto_01.py`、36 test PASS再実行済)。旧ルールの残存Grep: Productionにflap層の参照0。副次: 較正run(21:00:46)と本番fl run(21:02:35)の起動間隔109秒(指示の≥150秒を41秒下回った、storm guard発動なし・再起動なし・自己申告)。
判定整合: 重大NG=なし

判断候補(停止根拠: ユーザー原文§5`:169-176`『Production採用・配線は未承認』): D2 Production採用可否=D(真に新しい判断: 新規ASR救済仕様の採用)。論点=採用要否・許可リスト運用(Voice,path実証ベース)・AY/AW非救済維持・試聴結果。推奨=形態B・既定OFFで採用検討(試聴で誤救済なしを確認後)。上記以外にユーザー判断候補なし。
