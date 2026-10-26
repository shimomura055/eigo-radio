# OPUS_REVIEW_REQUEST_01 — Family Y Style profile是正 設計の独立技術レビュー依頼(任意。Fableが要否判断)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / 2026-10-26 / 性質: 設計のみ(API 0・コード変更なし)。11-3条件との関係: 既存X機構の適用であり新フローではない(条件A非該当と見込む)が、Production挙動が変わる(条件C「重要変更のProduction採用前」に当たりうる)ため、Fableが任意/必須を判断。本レビューはユーザー承認Gateではない。
レビュー対象: `DESIGN_01.md`、`PREVENTION_01.md`、`STYLE_MATRIX_01.md`(+json)、`REGEN_PLAN_01.md`、`ROOT_CAUSE_01.md`(同ディレクトリ)。
Opusに観測・検証・レビューを依頼する(代替案の比較・目的適合の判定はFable)。論点のみ記す。

1. **Voice本文へのStyle合成方針**: 承認済み設計(A19「Voice別Styleは設けない」、`DESIGN_PROPOSAL_02.md:109,242,347`)と共通仕様(PD06を本文に適用、28-1運用7)の両方を満たすか。ユーザー指示「Voice 1〜3の個性・主観性を損なわない/PD06を一律適用して個性を失わせない」(原文§1B)との整合: PD06をnarrator・Voice 1〜3にも適用するV1案(推奨)が、承認記録のみで正当化されるか、S9(平板化)の記録が無い現状で十分か。Voice本文のみdefault維持(V2)は新規Y固有例外とみなす判断で良いか。PD06文面(`er019_family_x_style_profile_01.py:108-111`)と基底(`news narration…not dramatic`)の差が人物の演技・ニュース調に与える影響の見立て。
2. **Gateのfail-closed設計**: `checked=[]`/記録欠落/default/role未カバーをBLOCKとする検査(PREVENTION (a))に抜け道が無いか。legacy waiver(`default`+`--legacy-style-waiver-ref`)が回避経路にならないか(waiverの発行者・記録・Gateでの扱い)。`profile_id`が承認でも、実測prefixが承認値と一致しない経路(LR再TTSの`<default:ENGLISH_STYLE_PREFIX>`脱落=CC-F2、chunk、`only-segments`の検証済みentry引継ぎ=`try_inherit_from_cached`)がGateを通過しないか。
3. **再生成範囲の妥当性(過不足)**: 33 take再生成/5 clipを再利用しない案R(推奨)とseed再利用案Pのトレードオフ。Style上再利用可とした5 clip(topic_intro、Adv comment_1/3、Std japanese_title)の判定根拠(`ROLE_SEGMENTS`/`ROLE_LEVELS`、`er019_family_x_style_profile_01.py:201-215`)に誤りが無いか。KP英語(K2、Master Store 2段key)が旧MINIMAL keyと衝突せず新規生成されること、shell固定音声を共有ストアから再利用してよいこと。新run dirの入力複製で複製してはならないもの(HR承認・review_lock・stage JSON)の漏れ。
4. **再発防止の十分性**: (a)Gate・(b)Gate 7/項目33の証拠定義・(c)Y_ROLE_COVERAGE+AST test・(d)drift testの組合せで、ROOT_CAUSE_01のQ2(実測値非照合)を機械的に塞げるか。X/Z側の同種欠落(Zの実測prefix照合の網羅性は未確認)に対する提案の優先度。PM_GOVERNANCE改訂案が「実質変更」(29-3)に当たるかの所見。
5. **既存機構との衝突**: OPEN-535(HR承認guard、`er121_family_y_audio_01.py`)・OPEN-527(chunk、test fixture)・OPEN-540(TTS Retry/Fallback/LR統一)との変更競合と順序。`STYLE_PROFILE`名の撤去が並行委任のtestを壊さないか。

返却形式: 論点ごとに「必須修正/推奨/所見なし」+根拠(ファイル:行)。
