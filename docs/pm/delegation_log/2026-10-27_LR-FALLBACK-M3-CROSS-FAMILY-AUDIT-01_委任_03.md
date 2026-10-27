# 委任_03(W3): M3 Gate・Local Rewrite・Human Reviewの整合調査(ユーザー原文 §5)

共通事項: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_委任_00_COMMON.md`(必読・遵守)。
成果物: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W3_M3_LR_HR_01.md`。読取専用・API 0。

## 対象の2仕様
(a) LR成功=`RESOLVED_BY_LOCAL_REWRITE`でHuman Review **Lock**へ進まない(2026-09-26承認 `CURRENT_SPEC.md:2214`、2026-10-19 `:2925`)。
(b) X M3 Style Gate `LOCAL_REWRITE_RECOVERY`(`er019_family_x_style_profile_01.py:742`)/Y gate(`er121_family_y_audio_01.py:929`)/Z相当の有無、が`record_human_approval`以外で解除不能。

## 明確にする7点(ユーザー原文§5)
1. それぞれの設計目的とユーザー承認履歴: (a)は承認原文。(b)はOPEN-312/OPEN-300(COFFEE-P8)・2026-10-12 Opus条件Aレビュー・DECISION_LOGで「`LOCAL_REWRITE_RECOVERY`をBLOCK対象にする」ことをユーザーが明示承認した原文があるか(HR_ROOT_CAUSE_01 §5は『ユーザー原文の明示承認文は確認できていない(先例による黙示的運用)』としている。これを確定させる)。統一仕様(`:3166`付近、2026-10-26ユーザー決定原文§4)で「③/LR採用音声をGateがBLOCK対象として検知、Gate条件無変更」がユーザー決定に含まれていたかも原文で確認。
2. 適用Family・Level・Role(X profile対象role、Y `Y_ROLE_COVERAGE`、Z gate)。
3. M3が禁止する対象: LRそのもの(原稿逸脱)か、承認済みStyleからの逸脱か。当初の導入理由(OPEN-312=LR再TTSでrole Styleが落ちる)と、統一仕様後(LR block内は元role Styleで①'②')で前提が変わったか。
4. fallback音声とLR回復音声の区別(record上のキー: `fallback_used`/`instruction_type`/`style_prefix`/`local_rewrite_recovery`/`asr_judgement.slot`)。OPEN-564の`_merge`非対称も含む。
5. LR後も承認済みStyleが維持されているか(統一後のAI島実データ `style_prefix`で確認。LR後①'で採用されたか③'で採用されたか)。
6. ASR PASS後にHRを要求する正当な理由があるか: 「音声と本文の1語差」を人が確認する価値(学習教材の一致原則)/Style逸脱の確認/先例OPEN-499。どの理由が仕様上の根拠を持つか整理。
7. 人間承認の重複・不要停止: HR Lock(er011)とM3の二重化の有無、`register_terminal_hr`との関係、Y/Zで同種停止が起きたrun数(前回監査U-02: Y本文8 segment等)。

## 分類と整合案
(a)(b)が矛盾(B)なのか、目的が異なり両立(C)なのかを判定し根拠を示す。整合案を複数(例: 現状維持/M3の`LOCAL_REWRITE_RECOVERY`をStyle維持時は警告化[=Gate緩和、ユーザー承認事項]/本文反映と組合せ/HR packetの自動生成で承認コスト低減[Gate不変])、各案の品質・速度・量産単価・HR件数・必要承認区分を比較、推奨を書く。**実装・緩和はしない**。判断候補の区分、Fableへの要約10行。
