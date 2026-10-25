FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0: Family X B0.2・Family Z B_r1のTTS Chunk分割をProduction正式経路へ配線するための既存仕様照合・配線設計・Opus条件Aレビュー依頼書・test準備。API 0、Production file編集0)。あなたはsonnet-worker。Fable(PM)からの委任。ユーザー指示原文は§9に逐語(`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md`へ全文保存)。

> 保存注記(sonnet-worker、2026-10-25): 本文は受領した委任文§0〜§3・§9見出しの転記。`--index 542`による自動逐語保存ツールは実行環境に見当たらず(`tools/`・`.claude/`・`scripts/`にも無し)、sonnet-workerが受領テキストから手で転記した。Fableの逐語保存で上書きしてよい。§9原文は`..._USER.md`に全文保存済み。

## 0. ユーザー正式決定(2026-10-25)
- **APPROVED_FOR_PRODUCTION**: X=段落分割+0.2秒追加ポーズ(Trial B0.2)/ Z=B_r1(約70語目安=ceil(語数/100)で100語超のnarrator clipを段落境界>文境界で分割、最小25語、引用途中禁止、chunk間0.2秒)。Zのクライマックス直前の分割位置はユーザー試聴で「全く問題なし」判断済み。**境界音量差を理由に追加Trial・採用保留をしない。B_alt/B_fineへの変更不要。**
- 目標: PRODUCTION_WIRED(X/Zそれぞれ、全Gateを満たしたFamilyのみ)。要件1〜9(正式初回経路配線/retry・fallback・regeneration・resumeで維持/欠落・重複・順序変更防止/Voice・Style・モデル・発音検査・ASR Gate維持/回帰test/正式経路runtime evidence/actual model_id・分割位置・Chunk数・追加ポーズ・Prompt/Style・検査結果・費用・処理時間の記録/SSOT・Git/旧処理整理)。
- 適用範囲: X=Trial条件(Advanced=b1b、Production同一関数`news_tail_fix.generate_news_narration_wide_margin`、本文1〜3の段落単位、chunk単位RMS正規化、固定無音0.2秒、ヘッドルーム弁)と既存仕様を照合し**未承認の対象拡大なし**(Standard(A2、6%減速あり)への適用はTrial未検証=対象外として明記)。Z=Advのnarrator clipのうち100語超のみ、Dialogue/話者切替clip・Std・KPは不変(Std除外理由=6%減速との相互作用、Trial未検証)。
- STOP条件: 採用済み方式・ポーズ・対象の変更が必要/既存承認仕様と両立不可/承認範囲・予算超過/重大品質問題。

## 1. 読むもの(必要箇所のみ)
X Trial正本(`docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/`)、`er113_fx_paragraph_chunk_trial_01.py`/`_02.py`。Z Trial正本(`docs/research/FZ-NARRATION-CHUNK-TTS-TRIAL-01/`)、`er114_fz_narration_chunk_trial_01.py`/`_02.py`。Production: X=`er019_family_x_audio_production_runner_01.py`のTTS段・`news_tail_fix.generate_news_narration_wide_margin`・X組立。Z=`er063_family_z_audio_01.py`(:730-738 style、:826-835 narrator生成、:738-750 reuse_key、:1722-1796 組立/RMS/gain_report)、`er013_family_c_production_01.py:202-326`、`er013_family_c_production_runner_01.py:665-680`、`er026_family_z_fiction_production_runner_01.py`、Z speed v2・`verify_z_speed_profile`、segment_plan。SSOT: CURRENT_SPEC(TTS/組立/音量正規化/gap/Dialogue別Voice/速度仕様v2/Master Audio Store/ER-003-B1-P6B不採用)、OPEN-506/510、UDR #191、DECISION_LOG。並行agent(重要): FAMILY-Z-STUDY Part 1配線/FX-CORE-NUMERIC配線/Family Y音声化(er110)。**本委任はProduction fileを編集しない(設計のみ)**。実装委任では同一ファイル衝突に備え、編集箇所を関数単位で限定し一時index方式でcommitする設計にする。

## 2. 成果物(`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/`)
`EXISTING_SPEC_CHECK_01.md`(X/Z正式TTS経路図[初回・retry・regeneration・resume・Local Rewrite後・Master Audio Store再利用]、配線点、既存組立規則、ASR Gate/発音Ledger/HRの適用単位、Trial差分表)/`WIRING_DESIGN_01.md`(X/Z別に(a)分割planner (b)生成 (c)組立 (d)Store/reuse_key (e)retry/regeneration/resume (f)runtime evidence項目 (g)Z speed v2 Gate整合・X Std非適用 (h)旧処理整理[Zの既存150語超2分割との関係] (i)test計画 (j)evidence取得計画と費用 (k)原価・処理時間増分 (l)CURRENT_SPEC記載案 (m)SSOT更新案)/`OPUS_REVIEW_REQUEST_01.md`(条件A論点)/`tests_draft_01.py`(Production未編集)。SSOT: OPEN-506/510に「APPROVED_FOR_PRODUCTION・配線設計中・未配線(PRODUCTION_WIREDではない)」を最小追記、UDR #191に採用決定を追記、DECISION_LOG 1件。`docs/pm/RESULT_PACKET_FXZC1.md`、ACTIVE_TASK自行。Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`(Production file無し)→`git commit --only`→`git push origin HEAD:main`。secret grep 0件。

## 3. 報告(Fableへ)
(1)X/Zの配線点と差分表の要点 (2)設計要点(a)〜(m) (3)旧150語ルールの整理方針 (4)実装委任の分割案(X/Z並列可否、衝突回避: 編集関数・ファイル一覧)と見積(作業量・evidence費用) (5)ユーザー判断が必要な事項(無ければ「なし」) (6)変更ファイル・commit・raw URL (7)RESULT_PACKET 4行+「判定整合」1行。

## 9. ユーザー指示原文(逐語)
`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md` を参照(全文保存済み)。
