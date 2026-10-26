## 管理ID

PM-SSOT-SYNC-19(SSOT同期: KP-PHRASE7-WORD5-PRODUCTION-01 Fable受入=PRODUCTION_WIRED、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02/_03、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01/_02A(新規OPEN起票)、FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05(HR新形式)、HR提出形式の共通運用規則、ユーザー指示3件の記録。API 0・JPY0)。**本委任のみがSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/PM_GOVERNANCE.md`の編集権を持つ**。並行Agent: KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B(コード・`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/`)、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04(フォーム側)。これらのファイルは編集しない。所有=上記SSOT 5ファイル、`docs/research/PM-SSOT-SYNC-19/REPORT_01.md`、`docs/pm/delegation_log/2026-10-27_PM-SSOT-SYNC-19_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_SSOT19.md`。pathspec付きcommit。

## 性質/禁止

- 性質: SSOT同期(判定はFable済み。文案の転記・整形・整合)。到達上限=SSOT同期完了。
- 禁止: SSOT全文読込(Grep/部分Readのみ)、判定内容の変更、Status格上げ(下記Fable判定どおり)、禁止Git操作、worktree stale SSOTの上書き(編集直前に`git log origin/main -1 -- <path>`、更新ありならHEAD blobへ自hunk再適用)。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-19_DELEGATION_01.md` をN=709から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-19」のものを採用(同時刻にFORM 委任_04あり)。

## Fable判定(転記する内容。文案の出典=各RESULT_PACKET(gitignore、ローカル存在): `docs/pm/RESULT_PACKET_{KP75,KP75B,FORM2,FORM3,KCP1,KCP2A,YSP5}.md`)

### A. KP-PHRASE7-WORD5-PRODUCTION-01 → **PRODUCTION_WIRED(X/Y/Z×Std/Adv、Fable受入2026-10-27)**
- ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-27、原文=`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_USER.md`)。設計875f4455a→Opus条件A(M-1〜M-9全件採用、M-7直列、R-1既知の限界)→実装967109760→evidence 082d5ec6c。
- 受入根拠(受入条件1〜11): ①正式初回経路で6経路8doc(X UK/AI島×Std/Adv、Y再配達×Std/Adv、Zメロス×Std/Adv)にP7/W5'適用(prompt_id/sha一致、model gpt-6-luna)、②W5'=5条件・補足・出力規則をユーザー原文逐語(sha 12d33708…)、P7 sha 2e930193…、③本文一致/1語(`not_single_word` Gate)/含有除外(Prompt+Gate二重)、実測で単語⊂フレーズ0件、④上限未満docで補完不発動を確認、⑤Gate除外時のみ補完=単語補完2件自然発火(Y Std/Adv、cmu起因+1)、**フレーズ補完のreal発火は未観測(unit/golden/E2E testで担保、自然発火時に監視=OPEN-549へ統合)**、⑥救済(er125)・RQA・HR依頼書(rc=4)・フォーム(export `[:7]/[:5]`で12件対応。`cap`表示既定8→12はFORM委任_04で是正中)、⑦resume=API 0・sha不変、旧3+5のHR待ちdocは作り直さない(D6)、⑧test(er119 250/252[既存2件=OPEN-543]、er105 52/52、er106 38/38、er125 58/58、er030 92/92、er121 368/369+1skip、er019 551/552[既存R4]、er026 220/224[環境依存snapshot]、er108 36/37[既存])、⑨runtime evidence=`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{EVIDENCE_01,COST_01,IMPLEMENTATION_01,REMOVAL_RESULT_01,DESIGN_02,OPUS_REVIEW_01}.md`、⑩SSOT=本SYNC、⑪Fable受入=本判定。
- 費用: evidence実費¥15.84(Cap¥60)。量産単価影響=+¥0.24/level・約+¥0.5/記事セット(目標¥70の約0.7%)、旧比+13.5%。時間は+25秒/level程度(参考)。
- Fable設計判断D1〜D6(R0 flagなし/Adv AUTO vocab5現行維持/not_single_word Gate/W5'補足=原文逐語/補完Prompt種類別/旧HR待ち候補作り直さない)。
- 撤去: `BACKFILL_MAX_CALL_ITEMS`、単一cap room計算、外側retry独立tuple、`KP_CANDIDATE_MAX=8`。残置: Prompt 2/2-V本文・pin test(復帰はgit revert)。
- A/B/C棚卸し(`INVENTORY_ABC_01.md`): A=実装済み、B=OPEN-546計数改訂・OPEN-549/544/484追跡・フォームcap引継ぎ、C=OPEN-547 K1(区分D・現行K0維持、Trial-02でGate不合格item 0件)・Trial-01「有用閾値」「猿の手Adv偏り」(原文で判断済み・判断不要)・AUTOでの単語組入れ(新仕様・導入しない)。
- 観測(実害なし、新規OPEN候補=修正へ進む候補・軽微): X UK Adv「forced to log in|無理やり聞かされる」gloss不対応(既存gloss整合段の責務、HRで人間確認可能)。
- evidence run dir(HR待ちrc=4、記事制作用ではない): `er019_output/.../uk_train_speaker_playback__run_kp75_ev_01`、`.../ai_island_temple__run_kp75_ev_01`、`er121_output/.../redelivery_fee/run_kp75_ev_01`、`er026_output/.../melos/run_kp75_ev_01`。
- OPEN-534: Status→PRODUCTION_WIRED(上記)。Trial-01/02の判断候補(7+5採否・順序是正分離確認)はユーザー採用で解消=CLOSE相当の追記。CURRENT_SPEC候補生成節(Grep `Prompt 2-V|KP_CANDIDATE_MAX|Gate除外補完`)をP7/W5'・12件・種類別補完・not_single_wordへ改訂し旧記述は履歴化。DECISION_LOG新規エントリ(採用・D1〜D6・Opus・実費)。

### B. LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01(OPEN-545) → IMPLEMENTED+公開+自己検証(ユーザー実操作確認待ち、PRODUCTION_WIRED未判定)
- 委任_02(357a131bf/6e12c7813): 全候補に日本語訳(`japanese_gloss`逐語、official 35/provisional 19/missing)とAI理由(確認用、call1は理由なし→P7/W5'化で今後は付与)、送信schema v2(英語・日本語訳・区分・文法解説全文・コメント、AI理由は別ブロック)、長文はコピー誘導、node 36/py 11/実DOM 19。
- 委任_03(0f6c3a3e4/31c80404b/70a2d9b36): payload v2に`candidate_id`/`kind`/`candidates_sha256`追加(`schema_minor:1`、Opus KCP指摘)、node 41/py 12/実DOM 9+19、Trial/replay由来2件はsha null=照合不可扱い。
- 委任_04(進行中): export `cap`既定8→12・docstring。
- ユーザー追加指示原文=`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md`。
- UDR-FORM-1(文法解説の事前生成=新仕様)は継続(Fable推奨=採用)。実操作確認(a)〜(j)+ChatGPT `?q=`反映・clipboard・スマホは未実施。

### C. KP-CONFIRMED-CONTENT-PROTECTION-01 → **新規OPEN起票(11-8分類=修正へ進む)、Status=IMPLEMENTED(第1段、委任_02A 246093175)、第2段+evidence進行中(委任_02B)**
- ユーザー追加指示②④(USER_02)。設計17385f5f9→Opus条件A(M1〜M9全件採用、台帳OF-KCP-M-1〜M-9記録済み)→02A: `er128_kp_confirmed_content_01.py`(確定レコード`confirmed_selection.json`正本+auditミラー、payload原文保存、候補doc照合、hash chain、`user_note_sha256`、`kind`、文法sidecar)、G0/G1、例外(ISSUE rc=4/INTEGRITY STOP)、AI操作ガード7種(revise/revokeは`--user-ref`必須)、legacy drift(read-only WARN+`confirm --adopt-existing`)、Y/Z stage_kpにG1(有料派生物前)、flag `EIGO_KP_CONFIRMED_PROTECTION`既定ON(承認済み仕様。kill switchはユーザー指示+user_refのみ)、test 52件、`pinned_items`削除。
- 現行の穴(事実): Z `_gloss_person_gate`が確定後にglossを再生成上書き(R-01)、本文sha変更で確定内容を退避し全再生成(R-03)、Part 2解説がprompt sha/MODEL/`ref_ja`変更で再生成(R-09)、整合検査がcandidate_id集合のみ。
- Fable判断: Opus提示のユーザー判断(a)文法解説の確定=既出UDR-FORM-1と同一(再提示しない)、(b)Y/Z Stdページ「日本語の意味」欄がTTS用`canonical_text`を表示=CURRENT_SPEC:458-469(表示用`japanese_gloss`/TTS用分離)との不一致=バグ是正として委任_02Bで修正(Production表示変更ではなく承認済み仕様への復帰)。
- 02B範囲: M2-b/M6 Part 2凍結/M8再バインド/G2〜G4/Z人称整合ISSUE化/LR重なり警告(LR挙動不変)/単一アクセサ/Family別evidence(≤¥30)。
- 新規OPEN候補(02A報告): Z `_gloss_person_gate`のG1停止前LLM 1 call(約¥0.06、02Bで解消)/er020 `test_recorded_candidates`作業ツリー依存(OPEN-543へ統合)/er119 isolation ALLOWEDにer121/123/124なし(OPEN-543既存)。
- 区分③・Stdの②③・文法2件目は現行Productionに消費者なし(`unconsumed[]`で保持、黙って捨てない)=UDR-FORM-1と同根、新規UDRとして増やさない。

### D. FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05(bb2b6aec4) → OPEN-537/539/550追記
- ユーザー指示「Human Review提出方法の改善・Family Y再配達」(原文=`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_02.md`)。救済規則適用不可(「思いどおりに」↔「思い通りに」、送り仮名途中切れで`ORTHOGRAPHIC_VARIANT_CONFIRMED`/D-2不成立、`HR_RESCUE_CHECK_01.md`)。新形式HRパケット公開 `user_test/family_y_production_redelivery_fee_03/hr_preview_01.html`、推奨Take 1、質問1つ。承認待ち=ユーザー。
- **UDR-YRF-2/3(旧Style比較・Voice別S9評価)はユーザー指示§4により必須判断から撤回**(任意情報として`_03/index.html`に残置)。承認後=adopt→`provision_shell,gate,assemble,pages,page_verify`→通常の最終試聴ページ(API 0)。
- 新規OPEN候補(11-8=ユーザー判断要の候補・区分D、頻度を見てから提示): JA表記ゆれ救済spanの送り仮名拡張(通り/どおり型)。OPEN-550へ統合記載(新規OPENは起票しない)。
- 共通運用化(次委任案 PRODUCTION-HR-PACKET-FORMAT-01: 共通module新設、HR停止時に新形式を自動出力、additive・Gate不変、API 0、約2〜3h)=OPEN新規起票(修正へ進む)。

### E. PM_GOVERNANCE追記(ユーザー指示§5、提示方式の改善・品質基準不変)
- 「HR提出形式(X/Y/Z共通、2026-10-27ユーザー指示)」節: HRをユーザーへ依頼する場合は原則「原稿・ASR全文(一次/二次)・相違点・NG理由(規則名・実測値)・推奨音声1つ(即再生)・AI評価」をセットで提出、質問は「この音声でよいですか?」1つ、複数Take比較はAI側で済ませ、必要な場合のみ品質差と理由を説明、既存音声Gateは不変。節番号は既存構成に従う(9節付近の報告フォーマットの隣が自然。Grep `## 9|9-8`で位置確定)。

### F. ACTIVE_TASK.md更新
管理ID=PM-SSOT-SYNC-19、Status要約、進行中=KCP 委任_02B・FORM 委任_04、UDR-blocking=Y preview HR承認(hr_preview_01)・UDR-FORM-1・OPEN-526・UDR-MONKEY-1、QDC=2026-10-27当日 約¥17(TRU 1.15+KP75 15.84)、次=KCP2B受入→SYNC-20、HR共通module委任。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-534|OPEN-545|OPEN-537|OPEN-539|OPEN-550|OPEN-549|OPEN-546|OPEN-543|OPEN-526` で該当行のみRead→末尾追記(本体行3,000文字超なら`OPEN_ITEMS_HISTORY.md`へ切り出し規則どおり)。新規OPEN番号=既存最大+1(Grep `OPEN-55[0-9]`で確認、現最大OPEN-555)。
- `CURRENT_SPEC.md`: Grep `Prompt 2-V|KP_CANDIDATE_MAX|Gate除外補完|候補生成`(:2005-2035付近)で節を特定→改訂+履歴化。確定内容保護の新節は02B後(SYNC-20)に置くため今回は「準備中」注記のみ。
- `DECISION_LOG.md`: 先頭ヘッダーチェーン規則に従い新規エントリ追加(Grep `^## |ヘッダー` で形式確認)。
- `docs/pm/PM_GOVERNANCE.md`: Grep `## 9|9-8|## 11-8`で位置確定。
- 各RESULT_PACKETの(7)SSOT文案を一次資料とし、本委任文のFable判定と齟齬があれば**Fable判定を優先**し、齟齬をREPORT_01に記録。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-19_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記A〜F(本委任が編集)。

## Git

- commit message: `PM-SSOT-SYNC-19: KP 7+5 PRODUCTION_WIRED(X/Y/Z)+OPEN-534更新、OPEN-545(フォーム委任_02/03)、確定内容保護OPEN起票(IMPLEMENTED第1段)、Y HR新形式(委任_05)+UDR-YRF-2/3撤回、PM_GOVERNANCE HR提出形式(API 0)`。push。

## 報告

`docs/pm/RESULT_PACKET_SSOT19.md`: (0)T-0、(1)更新箇所一覧(ファイル:行、新規OPEN番号)、(2)齟齬・判断保留、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、commit hash・raw URL。末尾5行要約。