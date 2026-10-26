## 管理ID

PM-SSOT-SYNC-17(TTS統一のFable受入反映=OPEN-540 PRODUCTION_WIRED(限定)、CURRENT_SPEC統一仕様新節+旧記述履歴化、OPEN-376/312/538/274/389/528/536の解消反映、OPEN-548/551の調査結果反映、日次費用締め。API 0・JPY0)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_04(コード、SSOT編集権なし)。**SSOT編集権は本委任のみ**。所有=`OPEN_ITEMS.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/OPUS_FINDINGS_LEDGER.md`(TTS統一のOpus所見M-1〜M-11/R-1〜R-7のCLOSEOUT記録)・`docs/pm/delegation_log/2026-10-27_PM-SSOT-SYNC-17_DELEGATION_01.md`(+check.json)・`docs/pm/RESULT_PACKET_SSOT17.md`。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。worktree SSOTがHEADより古ければHEAD blob書き戻し後に自hunk追加。

## 性質/禁止

- 性質: SSOT同期(Fable判定の転記)。到達上限=SYNCED。
- 禁止: SSOT全文読込、コード編集、Fable判定を超える格上げ、禁止Git操作。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1/T-0/T-2なし/T-3なし)。T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-17_DELEGATION_01.md` をN=694から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-17」のものを採用(同時刻に委任_04あり、先頭一致必須)。

## 事前指定Read一覧(文案の正本。Fable判定優先)

- `docs/pm/RESULT_PACKET_TRU3.md`(9)SSOT文案、`TRU2.md`(9)、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{EVIDENCE_01(必須12項目表),ROW_MAPPING_01(§2統一後星取表),REMOVAL_RESULT_01,COST_01,HR_IMPACT_01,OPUS_REVIEW_01}.md`
- `docs/pm/RESULT_PACKET_INV1.md`(OPEN-548/551文案)
- `CURRENT_SPEC.md`: Grep `COOLDOWN|600秒|10分|LR後1回|Adv技術エラー|Fallback Style` → 旧記述(:1531/:1647-1651/:1857/:2185付近)、Y節のStyle記述
- `OPEN_ITEMS.md`: Grep `^\| OPEN-(540|376|312|538|274|389|528|536|548|551|535) `
- `docs/pm/OPUS_FINDINGS_LEDGER.md` 末尾(記載形式)

## Fable判定(転記)

### A. OPEN-540 → **PRODUCTION_WIRED(限定)**(Fable受入 2026-10-27)
- 根拠(9項目): ①承認仕様一致=ROW_MAPPING 49/49行policy付与・SPEC_LEDGER F/S/C/L/Q/V、②正式初回経路=X/Y/Z全leaf L1〜L8+call site(commit 18d997941/e8773980a/65e5b036e)、③retry/fallback/regeneration/resume整合=BlockProgress・E-S6 3本(X-Adv-12/X-Std-10/X-Adv-16)・STOP(Y-Std-6/Z-Std-8)、④runtime発火=X 29case/Y 14/Z 15、FAIL 0、実180秒待機51回(179.97〜180.00秒)、実LR・実Gate、E-S2b 7case(TTS6・待機2・LR1・HRQ1行)、U-03即HR、KP 2+180+2、Z冒頭英語LR有効化(U-06)、Opus追加2本(Std chunk減速後NG→②PASS→Gate PASS、Adv L1 Voice=Charon)、⑤test=er127 97件・A/B/C golden 80ケースbyte同一・回帰に本件起因失敗なし、⑥actual model_id/routing=evidence各case(Zセリフはgemini-2.5-pro-preview-tts不変)、⑦SSOT=本委任、⑧Git=上記+evidence 31423fdce、⑨未承認仕様・Dangling Reference=なし(REMOVAL_RESULT: X/Y/Z専用moduleに`COOLDOWN_SECONDS`参照0、正式180秒定義はer127のみ、旧経路はscope外分岐のみ)。
- **限定事項**(委任_04で是正・確認中、解除後に「限定」を外す): (a)JA部位の終端NGでHRQ行登録が判定器のslot書込に依存(X-Std-7/Z-Adv-3で駆動側の判定注入時にHRQ 0行。実経路で欠落するかは確認中)、(b)BlockProgress `mark_done`がLR block(depth 1)の監査記録を上書き(resume正当性に影響なし)。未観測: X FamilyのSTOP(offline testのみ)、Yのchunk経路(構造的不発火)、Zセリフ終端Std版、X-Adv-5/Z-Std-3/Z-Adv-7(同leafは別caseで実走)。
- Production軽微修正1件(evidence中): `er121_family_y_audio_01.py`の`generate_y_b1_segments`のdecorator位置ずれ(scope外になっていた)を是正、test 2件追加(31423fdce)。
- 費用: evidence実費¥86.60(X 36.97/Y 34.25/Z 15.39)、設計・実装API 0。限界費用attempt約¥0.353・LR約¥0.282。量産原価影響+1円/セット未満(推定)。制作時間: 1ブロック−420秒、新規待機部位+180秒/イベント。HR影響: ③/LR採用25caseのうちGate BLOCK 4(X Adv preview③/KP解説③、Y Std本文③/Adv LR採用)=既存fail-closed Gateどおり、追加HR待ち推定+0.1〜0.5件/記事(Gate緩和は別提案・現状変更なし)。
- 2026-10-26の日次費用締め: 約¥708(563+KP Trial-02 16.3+Y Style 32.09+KP補完 26.25+TTS統一 86.60等)/1,000。

### B. CURRENT_SPEC
- 新節「TTS Retry/Fallback/Local Rewrite 統一仕様(X/Y/Z、APPROVED_FOR_PRODUCTION 2026-10-26、PRODUCTION_WIRED(限定) 2026-10-27)」: 基本フロー、部位別表(ROW_MAPPING §2の9 policy×49行の要約表)、LR安全条件(再入禁止・深さ1・元Style転送)、KP 2+180+2、Zセリフctx2→180→legacy③、Adv③短文Style、JA短文Style・LRなし、終端NG1件=HRQ1行、cooldown 180秒(5秒刻みSTOP確認・resume残時間)、単一読取関数`unified_flow_active()`(scope X/Y/Z内のみ、A/B/C不変)、evidence path、限定事項。
- 旧記述(:1531/:1647-1651/:1857/:2185付近の600秒・LR後1回・Adv技術エラー時のみ切替・部位別旧回数)を「履歴(2026-10-26統一前)」と明示(削除せず)。
- Y節: Style profile=fx_20261017継承(FAMILY-Y-STYLE-PROFILE-FIX-01、3af84a499)、fail-closed Gate、を反映(SYNC-16で未反映なら)。

### C. 統合先OPEN
- OPEN-376(LR再入)・OPEN-312(LR Style脱落)・OPEN-538(D11 topic_intro_en)=**解消(evidence確認済み、OPEN-540へ統合)→CLOSED**。OPEN-274/389=部分解消文案(TRU1 (9)どおり)。OPEN-528 Deferred(1)=CLOSE、OPEN-536=CLOSED(OPEN-540に包含・ユーザー決定済み)。
- OPEN-548: 「判定=設計どおり(Seed凍結fail-closed、10-25 FZ-SOURCE-ESSENCE案A承認の帰結)・実害なし。猿の手・賢者・開いた窓・二十年後の既存runは本文生成系stage(plan/support/kp/writer/std_adjust)が再開不能、tts以降は可。対応=現状維持(案3)。再生成が必要な時点で新run(公開物差替え時はユーザー判断)。記録のみでCLOSED」。
- OPEN-551: 「調査完了: Z定義照合OK(共通8 role sha一致・例外role登録・drift test)/実測照合不足(B・中): `run_audio_gate`に実送信prefix照合なし、Adv・日本語roleの実測sha未記録、猿の手Std `full_story_part1_c10`がStyle落ちfallbackを承認記録なしで採用(公開版該当かは次委任で確認)。次=Z `style_actual_vs_approved` Gate+実測記録(Y方式)、過去runは警告扱い。着手はOPEN-540限定解除後」。
- OPEN-535: Fable受入=**PRODUCTION_WIRED(Y経路)**(根拠: 5568631ba修正・test 16件・正式CLI mock退避・実経路evidence[run_style_fix_01でUNDETERMINABLE退避→Puck再生成]、X/Zは同構造だが本文Voiceを後から変えない運用で実害なし=Zセリフ割当変更時に要対応として残す)。

### D. Opus台帳
- TTS統一: OF-TRU-01〜(M-1〜M-11/R-1〜R-7)をCLOSEOUT(反映commit・test名)。KP補完: OF-KBF(M-1〜M-7/R-1〜R-10)もCLOSEOUT(未記載なら新設)。Y Style是正: OF-YSP(M-1〜M-4/R-1〜R-8)CLOSEOUT(V1・S9はUDR)。

### E. UDR/ACTIVE_TASK
- UDR: 変更なし(OPEN-526・534・UDR-FORM-1・UDR-YRF-2/3据置)。
- ACTIVE_TASK: 管理ID=TTS統一 委任_04(限定解除)/次=Z Style Gate(OPEN-551)・`_03`preview承認待ち・フォーム実操作確認待ち/QDC=2026-10-27 当日¥0(前日締め約¥708)。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-17_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、delegation_log。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-17: TTS統一 Fable受入=PRODUCTION_WIRED(限定)(OPEN-540、CURRENT_SPEC新節・旧記述履歴化、OPEN-376/312/538 CLOSED)、OPEN-535 WIRED(Y)、OPEN-548 CLOSED、OPEN-551調査反映、Opus台帳CLOSEOUT(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-17/01`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_SSOT17.md`: (0)T-0、(1)編集箇所一覧、(2)Fable判定との差異、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)commit hash・raw URL。末尾5行要約。