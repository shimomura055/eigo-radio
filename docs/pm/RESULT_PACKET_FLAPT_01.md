# RESULT_PACKET ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01(2026-10-30。調査・設計+API 0 Trial。API 0・費用0・Production変更0)

- 成果: `docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/{CURRENT_STATE_01,DESIGN_01}.md`、Trial専用`tools/`(proto+test+census 3本)、証跡json 4本(case_results/stored_census/voice_census/rescue_surface)、OPEN-626、ACTIVE_TASK(FLAPT)。STOP check rc=0(開始時)。基点=origin/main(一時worktree)。
- 結論: 既存の同音救済(CMU完全一致)・OPEN-122 CS層(語末型+独立ASR corroboration必須・A2/B1本文限定)ではlatter/ladderは原理的に救済不能。**M1=CMU音素+flap環境規則(API 0)を推奨**(er109と同型の第3層、既定OFF)。M2(LLM二重確認)非推奨、M3(ASR側を期待語へ寄せる)は循環で不採用。
- Phase 1 Trial(36 test PASS): 正例12/12、反例(ten/den・time/dime・putting・eaten/Eden・alter/alder・attack…)全NG維持、writer/rider・title/tidalはCMUが母音同一(AY1)=**辞書だけでは区別不能**→自動救済せずNG維持(REQUIRES_EXTRA_EVIDENCE)。
- 実データ(転写6,951件・NG現行1,330件): RESCUE=latter→ladder(X⑨、HR)とBertie→Birdie(Z、9 NG attempt)のみ。誤救済0(全件独立試聴は未実施)。HR 1/131(X 1/17)、リトライ9 attempt(Z)、API費用0。CMU全体の救済面=431対(+AY/AW 73)、否定語0。
- Voice: EN TTSは全てGemini prebuilt Voice+`language_code=en-us`(er002_gemini_client.py:62-70)。非米音設定は存在しない。ただし設定≠実音声。flap実証済み=Aoede/Zephyr/Schedarのみ、他8種は未確認=不適用(許可リスト・既定空)。
- 失敗終了時の最終成果物: 該当なし(正常完了。未配線のため既存Gate・成果物に変更なし)。
- Opusレビュー論点(5件): (1)AY/AW核の扱い(NG維持 vs 警告付き救済)と、辞書で区別不能な領域の判断基準 (2)canonical単一読み必須(putting/pudding型を取りこぼす)の妥当性 (3)実装形態A(er109内第3層)/B(新規module+decision()1呼出)と11-7(2)の適合 (4)Voice許可リスト方式(実証ベース)とPhase 2 probeの要否 (5)全ASR票への一括適用とI-7(ASR収束を根拠にしない)・Repetition QA副作用。
- 判断候補: **D1** Phase 2 Voice probe(有料Cap案≤¥30・概算¥12〜21)=分類B(承認範囲内自己解決。原文`docs/pm/delegation_log/2026-10-30_FX4-LATTER-APPROVAL-AND-FLAP-T-TRIAL_USER.md` §6 L186-190『少額費用ごとの承認不要』・PM_GOVERNANCE 7-7)、実行はFable指示後。**D2** Production採用=分類D(同原文 §5 L169-178『新仕様のProduction採用・配線は未承認、VALIDATED止まり』)。本委任では提示のみ。
- 次の一手(改善見込み自己評価): Phase 2 probe(Voice許可リスト確定、AY/AW方針の実測根拠。見込み高)→Phase 3 ⑨HR記録offline再判定→Fable独立評価→(VALIDATED後)ユーザー採用判断。
- 原因仮説/観測: latter=`L AE1 T ER0`・ladder=`L AE1 D ER0`(CMU、.venv確認)。ASR8判定すべてLadder(HR_ROUTE_09.md)。CS層corroborationは全ASR同語のため不成立(er011_connected_speech_equivalence_layer_production_01.py)。前回との差分=初回調査。
- (1)既存仕様整合: er006_preprod_hardening_01_validation.py:821-846/1115/1360、er008_..._homophone_en.py:73/197、er078_asr_unified_judge_01.py:73-77/542、er104_kp_three_asr_vote_01.py:160/246、er109_xz_scope_01.py:92/149、er006_secondary_asr_01.py:874/1135/1207、CURRENT_SPEC.md:1864/1866、原文§3-§5。
- (2)未承認機能の既定値: 新機能は`tools/`のTrial専用でProduction経路から未import(Grepで確認)。flag未実装=Production到達経路に入る未承認機能0。将来flag新設時は既定OFFで`OPEN_ITEMS.md` OPEN-626へ記録。
- (3)失敗終了時最終成果物: 該当なし(成功終了。成果物=上記docs/tools、目的=設計+Trial、適合: 原文§4.3の7条件に対応する表あり[DESIGN_01 9節]、Trial成功宣言はせずFable評価待ち。ユーザー原文取得済み)。
- (4)撤去・残置: 撤去した規則0。残置=既存homophone/er109/CS層は無変更。Grep `flapt|FLAP_T` はdocs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/・OPEN_ITEMS・ACTIVE_TASK・本packetのみ。
- 判定整合: 重大NG=なし
