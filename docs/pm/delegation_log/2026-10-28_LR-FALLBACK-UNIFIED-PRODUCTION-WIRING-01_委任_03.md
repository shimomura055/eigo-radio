# 委任_03(Phase A / W3): UD-3「M3/Style Gateの正常LR・Fallback停止解除」の設計(X M3・Y Style Gate・Z相当経路・HR Lock)(API 0)

共通事項=`…_委任_00_COMMON.md`(必読)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W3_UD3_GATE_DESIGN_01.md`。**設計のみ(コード変更禁止)**。Opus条件Aレビュー対象。

## ユーザー決定(原文§5、再質問しない)
1. 承認済みStyleとの照合は維持。
2. Fallback検出・記録は維持。**正常なFallback発動のみを理由とする**組立停止・Human Review要求は解除。
3. LR検出・記録は維持。**正常なLR発動のみを理由とする**組立停止・Human Review要求は解除。
- 従来どおり停止: 未承認・不明Styleへの切替/許可されていないFallback方式/Style記録・証拠の欠落・不一致/ASR NG等の音声品質NG/LRによる意味・Fact・確定内容・原作保持違反/本文と音声の不一致/技術的・安全STOP。
- ASR・Style品質検査そのものは弱めない。TTS試行回数・待機・Fallback Style・LR範囲・ASR判定基準・Voice/速度・確定内容保護は不変。

## 設計すべき事項
1. **現行Gateの判定項目の分類表**(X `m3_assembly_gate` 全項目、Y `er121_family_y_audio_01.py:~929` gate、Z `run_audio_gate`/`verify_*`群、HR Lock投入条件、`pass_with_warning`系): 各項目を「維持(承認済みStyle照合・証拠欠落・不一致・品質NG)」「解除(正常なLR/Fallbackのみを理由とする停止・HR要求: 例 `LOCAL_REWRITE_RECOVERY`、`STD_FALLBACK_USED_OR_UNKNOWN`のうちfallback_used=trueかつ記録完全な場合)」「分割が必要(1項目が正常/異常を混在判定している場合→異常側だけ残す具体案)」に分ける。file:line付き。
2. **「正常なFallback」「正常なLR」の判定定義**: 承認済みpolicy(`er127 PROFILES`)の③/③'で、Style名が承認済みFallback Styleの集合に含まれ、記録(Style名・attempt・採用)が完全で、ASR PASS(警告含む)であること等。「許可されていないFallback方式」「未承認・不明Style」をどう検知し続けるか(Style名のallowlist照合の所在)。
3. **HR Lock/Human Review要求の変更点**: 正常LR/Fallbackのみでは投入しない。品質NG・終端NG・三者不一致は従来どおり投入。`LR_REWRITTEN`警告(PASS時)は記録として維持しつつHRを要求しない扱いの整理。既存の`pass_with_warning_listening_list`(事後試聴)への影響。
4. **Family Z・他Familyの整合**: ZにはLR Gateがない(OPEN-567(1))。UD-3適用後のX/Y/Zの判定が「同じ基準」になるかの整合表(Zで新たに停止を増やさない。品質NG検知の欠落があれば、それは原文§5の「従来どおり停止」範囲として指摘)。A/B/Cは方式置換禁止=対象外を明記。
5. **撤去・残置**: 解除で不要になるコード・test・SSOT記述(例: OPEN-312 M3 LR項の根拠、CURRENT_SPEC M3記述)の一覧と撤去方針(Charter 8原則「旧ルール・旧検査の撤去要否」)。
6. **test計画**: 既存test(`er019_family_x_style_profile_01_test_01.py`、`er121_family_y_style_profile_test_01.py`等)のうち変更が必要なケース、新規ケース(正常LR→通過・異常Style→停止・証拠欠落→停止・ASR NG→停止・本文音声不一致→停止)。
7. **runtime evidence計画**: 保存済みrun(AI島 hr_02 等、M3 BLOCK実績あり)で新Gateを読み取り専用で再評価し「正常LRのみ→通過」「異常→停止」を示す方法(有料0)。

## 出力形式
表+file:line。判断候補A/B/C/D区分。品質基準の引下げに当たる懸念があれば「D」として具体的に指摘(ただしユーザー決定済み範囲は再質問しない)。
