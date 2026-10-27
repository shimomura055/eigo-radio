# 委任_02(Phase A / W2): UD-1「LR後の英文を最終表示本文へ反映」の設計(X/Y/Z・全LR対象Role)+既公開4件の遡及是正計画(API 0)

共通事項=`…_委任_00_COMMON.md`(必読)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W2_UD1_BODY_REFLECTION_DESIGN_01.md`。**設計のみ(コード変更禁止)**。Opus条件Aレビュー対象。

## ユーザー決定(原文§3・§2・§4、再質問しない)
- LRで変更された英文を最終表示本文にも反映する。TTS入力・ASR正解原稿・最終表示本文の三者一致を検証する。
- LR前後の英文・変更箇所・変更理由・対象音声区間を記録する。
- 確定済みKP/KW/文法・日本語訳・Fact・原作保持要件を保護。干渉する場合は無断変更せずSTOP/USER_DECISION_REQUIRED。
- LRの正常発動だけではHuman Reviewへ移行しない(品質NG・重大な内容不整合は従来Gate維持)。
- 装飾用注記(赤/濃青)は最終Human報告資料のみ。表示本文・TTS・ASR・KP表示・Style Promptに混入禁止。
- AI島: Std `AIs`→`AI agents`、Adv `AIs`→`AI systems`。既存LR後音声を使用、再TTSなし、該当箇所のみ。

## 設計すべき事項
1. **本文反映の処理フロー(Family別)**: X(`er003_v1_*`系: article.md/parts.json/segment plan→pages)、Y(`er121_family_y_*`)、Z(`er063`/`er026`: writer/*.md→segment_plan→chunk→pages、既存のページ注記 ~er063:2464)について、LR採用確定後に表示本文を書換え後の文へ更新する**単一の反映点**(assemble/pages段か、採用確定時か)を提案し、(a)初回Production、(b)retry/fallback、(c)regeneration、(d)resume/再利用(`RESOLVED_BY_LOCAL_REWRITE` entry、`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`真=原文へ戻す)、の4経路で同じ結果になることを示す。原本原稿(writer出力・ユーザー承認済みスクリプト)は**書き換えない**(派生の表示本文のみ更新+記録)方針を基本とし、代替案があれば比較。
2. **三者一致の検証点**: 表示本文・TTS入力・ASR正解原稿のsha/文単位照合をどこで行い、不一致を従来Gateのどの停止に接続するか(「本文と音声の不一致」は停止対象のまま)。
3. **確定内容保護との整合**: `er128` G0-G4(text_sha256再バインド可否、確定KP/KW/文法の語がLR変更範囲に重なる場合の判定=STOP/USER_DECISION_REQUIRED)、V3照合コードの`t8`(本文sha)との関係、Fact Lock(X)・原作保持(Z)の各検証との接続。重なり判定のアルゴリズム(語・句の位置照合)を具体化。
4. **記録schema**: LR前後英文・差分語句・理由・対象区間(segment/chunk/clip id)・Family/Level/Role・最終採用attemptを、最終Human報告が読む単一の記録(案: 既存`local_rewrite_recovery`記録の拡張 or run単位の`lr_fallback_ledger.json`)として定義。既存recordとの重複・移行方針。
5. **既公開4件の遡及是正計画**(原文§8): 各件について、変更前後の本文・実音声・ASR基準・学習項目(確定KP/KW/文法との重なり)・ユーザー承認記録(UDR #183(a)等)・ページ注記の現状を照合し、「必要十分な修正」(表示本文の該当語句のみ更新+記録+最終Human報告資料)の手順・影響ファイル・公開差替えの承認要否(記事単位運用)・STOP該当有無を表にする。AI島はUD-2確定(AI agents/AI systems、hr_02の既存LR後音声使用、再TTSなし)。**実施はしない**。
6. **test計画**: 単体(反映点・三者一致・重なり判定)/integration(mock E2E X/Y/Z)/regression対象test一覧と、既存golden(A/B/C byte同一)不変の確認方法。

## 出力形式
フロー図(テキスト)+表+file:line。判断候補はA/B/C/D区分(ユーザー決定済み事項は再質問しない)。
