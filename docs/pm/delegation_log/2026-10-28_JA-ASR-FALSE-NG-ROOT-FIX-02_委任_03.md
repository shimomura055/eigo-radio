# 委任文(逐語): JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03(2026-10-28、Fable→Sonnet worker)

管理ID JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03「Phase 3: Opus条件Aレビュー(M-1〜M-7/R-1〜R-7)の反映・集約規則の変更・負例母集団拡大・再評価・SSOT同期」。前提=Phase 1/2成果(`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`の PREREGISTERED_01/02、EVAL_UNIFIED_01/02、RESIDUAL_NG_ANALYSIS_01、DESIGN_PROPOSAL_01、proto_unified_02.py(+test)、n3_redraw_02.json、PM_AUDIT_01/02)、ユーザー原文`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md`。並行workerなし。
**ファイル範囲**: `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`配下、`docs/pm/RESULT_PACKET_JAFIX2D.md`、`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_委任_03.md`(本文逐語)、SSOT同期(§6の範囲のみ)。**Production code(er0XX_*.py)は編集禁止**(読む・importして呼ぶのみ)。CURRENT_SPECは変更しない。Family A/B/C不可。
開始時と有料run前に `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-FIX-02 --run-dir docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02 --out docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/stop_check_03.json`(rc=3で停止)。費用上限¥15(見積→BUDGET_PLAN_03.md→実行→BUDGET_LOG_01.md追記、cost_log記録。OpenAI gpt-4o-mini-transcribeのみ。Azure/TTS 0)。

## Fable判断(Opusレビューの採否)
Opus条件Aレビュー=条件付きGO。Fableは**M-1〜M-7を全て採用、R-1〜R-7を採用**(R-5の『どおり/通り』修正は別IDへ、検証のみ本Phaseに含める)。(ii)best-of-N集約はNO-GO(M-3「矛盾なし合意」へ変更)、(v-c)辞書追加はNO-GO(M-5の別表方式へ変更)、(iv)新「条件付きPASS」状態は作らない(R-4: 既存HR Lock/個別採用で足りる。早期HR条件は費用最適化としてのみ設計)。Phase 2結果との差分(best-of-N 6/6→合意規則では4/6+HR 2の見込み)は正直に両方併記する(R-6)。D-1〜D-4はFableがユーザーへ提示する(あなたは登録と事実整理のみ)。

## 0. Opusレビュー全文を `OPUS_REVIEW_01.md` へ逐語保存(最初に行う)
(Opusレビュー全文は `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/OPUS_REVIEW_01.md` に逐語保存済み。委任文中の同ブロックと同一。ここへは重複掲載しない。)

## 1. 事前登録 `PREREGISTERED_03.md`(有料draw前にcommit)
- 集約規則: 主=M-3「矛盾なし合意」(全draw+Secondary保存、値以外の内容spanで原稿と食い違うdrawが1本でもあればHR[例外=explain_garble可能な数値garble・M-1/C2通過のPRON同音のみ]、force_secondary必須、PASS_W必須、N≤3、発火理由ホワイトリスト=p1_value_diff/secondary_not_accepted のうち否定差・A7・C2・length以外、Azure再試行なし)。参考=best-of-N(Phase 2既出)。N=2/3は4drawの全部分集合平均で算出(出た順に依存させない)。
- 負例母集団拡大: 保存済みの人間NG判定wav(`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、N3の実音声負例、他に見つかるJA実誤読wav。**Family A/B/Cのwavは除外**)を列挙(wav sha・NG根拠・出典)、各4 draw。見積(件数×4×¥0.0056)→上限¥15。
- 正例拡大: 6本+Y/Preview(`er121_output/family_y_production_01/redelivery_fee/run_01`・`run_hrguard_ev_02_mock`のPreview attempt wav)+既存のHR承認済み誤NG wav(個別採用記録から辿れるもの)。各4 draw。
- 指標・合否: 6本の最終判定(PASS/既存PASS_W/新方式PASS_W/HR/NGの5区分)、負例増分(型別、OTHER>0で不合格)、回帰0、合意規則下のN別誤PASS率、Y/Preview型の救済可否。

## 2. proto_unified_03.py(+test、proto_02を基に)
M-1(a)(b)(c)(d)、M-2(新warning code専用・APPROVED_EQUIVALENCE_BASES非登録・3区分集計)、M-3(合意集約)、M-4(再試行発火segmentではβ読み食い違い=veto→HR)、M-5(L3を「送り仮名省略訓読み別表」として新層内のみ参照。両engine読み水準一致・置換後残差0・C2候補span除外・PASS_W。汎用辞書不変)、M-6(E3 rejections非空→新層不適用、E4 cascade_diffsを救済根拠にしない監査)、M-7(phrase_list_hash非空→fail-closed)、R-1(差分span内の漢字1文字ごとにC2候補検査。変更前後の差を測る)、R-2(ENGINE_reading_difference経路を除外)、R-7(全draw・規則版・層版の保存、保存drawのみからの再現test、flag OFF/scope外先行block)。Flags全OFF=L0同一をtestで固定。Production関数は呼ぶだけ。

## 3. 有料draw(§1の見積内)→ `redraw_03.json`(wav sha・draw番号・モデルID・応答メタ・時刻)、cost_log記録。

## 4. 評価 `eval_unified_03.py`(API 0、socket guard、2回実行sha一致)→`EVAL_UNIFIED_03.md`
- 6音声×層(L0/L1/L1+L2/L1+L2+L3/+合意再試行N=2,3)の5区分最終判定・理由・条件・転写。R-6のとおり「4/6+HR 2」等の表記で、best-of-N(Phase 2)との差を併記。
- 増分表の作り直し(M-1/M-6/R-1入り)。R-3: 事前登録どおりの数字と再分類後の数字を併記。
- 負例拡大集合での合意規則N別誤PASS率、wav別draw分布(独立性)、時刻依存の有無。
- Y/Preview型の救済可否(案R(i)が効くか)。
- run単位の実益(参考: run_ms_03/run_reselect_01が何attemptで完走するか、再生成・HR件数の見込み)。
- 6合格条件への到達度表とStatus候補(最終はFable)。費用・単価(式と区間)。
- 残NG 2本の扱い: 既存HR Lock→個別採用(sha単位)で人間承認する手順(API 0)を1段落で(新状態は作らない)。

## 5. SSOT同期(追記のみ、既存文削除なし)
- `OPEN_ITEMS.md` OPEN-515: Phase 2/3結果(機械判定上限4/6 PASS_W+HR 2、Opus条件A反映、D-1〜D-4はUDR)。新規OPEN 3件: (a)Y/Preview『思いどおり↔思い通り』同読み表記ゆれ(分類=修正へ進む、別ID・別Opusレビュー、Family Y)、(b)基線の限界=L0がPS_same(読み一致)で本帳/本蝶等の同音誤表記をPASSさせる(記録・ASRテキスト限界、是正は本件外)、(c)PM: A8横展開で未登録36件+trigger不明10件(`PM_AUDIT_02_CROSSCHECK.md`)の一括Deferred登録を別PM委任で行う(トリガー=本件Closeout後の最初のPM委任)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #204〜#207=D-1〜D-4(事実・選択肢・費用・ブロック対象を1行ずつ、推奨欄は「Fable報告参照」)。#201/#202/#203の備考に「Phase 3結果で更新、#204〜207と一体で判断」。
- `DECISION_LOG.md`末尾1件: Phase 1〜3の経緯、Opus条件A採否、機械判定上限の結論、Status(Fable最終=USER_DECISION_REQUIRED見込み)。
- `docs/pm/ACTIVE_TASK.md`: (F)受入条件表を更新(B1=未達[機械4/6 PASS_W+HR2]、B2=部分[T1/T2構造的]、B3=達成、B4=達成、B5=達成(設計)/部分(配線未)、B6=達成)、(G)FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01=完了・VALIDATED・ユーザー判断待ち(Comment3採否、急がない)を1行追加。固定ヘッダの「全commit push済み」shaを更新。
- `docs/pm/RESULT_PACKET_JAFIX2D.md`(≤20行、4行+判定整合行)。

## 6. Git
`git diff --cached --name-only`空確認→自分のファイル(+SSOT)を明示`git add … && git commit -m "JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03: Opus条件A反映(M-1〜M-7/R-1〜R-7)・合意集約・負例拡大再評価(実費X円)+SSOT同期(Production変更0)"`を1コマンド(事前登録commitは別に先行可)。`git add -A`禁止。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 6音声×層の5区分表(1行ずつ)、負例増分(事前登録/再分類併記)、合意規則N別誤PASS率、Y/Preview救済可否、残NG扱い、Status候補、実費、commit sha、判断候補。
