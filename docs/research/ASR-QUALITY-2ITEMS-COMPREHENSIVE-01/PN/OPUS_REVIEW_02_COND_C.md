# OPUS_REVIEW_02_COND_C(Opus条件C独立技術レビュー結果。Fableによる転記・逐語要約、委任_04から保存。2026-10-23)

対象: WIRING_DESIGN_01.md / OPUS_REVIEW_REQUEST_02.md。Fable判定・Opus所見は以下(原文=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_PN_委任_04.md`)。

## Fable判定(記録用)
Opus総合判定=「必須修正後に実装可、再設計不要」。骨格(新module+er103本体統合、PNAP scope、既定ON+1行rollback、hook 1か所、保存entryからの復元)は一致。対立点6(寄与判定の反実仮想化/等価性testの強化/増分表をそのまま判定に使わない/表の自動取得範囲/発火証拠の取り方/LR後text)はいずれも安全性・検証の技術修正→**Fable判断で実装へ進む**。PRODUCTION_WIREDはFable受入後(X/Z双方のevidence必須)。

## Opus所見(逐語要約)
- W-01[必須] 「表が受理に寄与したか」は反実仮想で判定: Primary句ごとにまず元の `ledger_surfaces` で `_noun_checks` を実行し、`R_NOT_PROPER_EVIDENCE` で落ちたときだけ `ls|grant` で再判定、その場合だけ `per_diff`/`entries_used`/`alarm_labels`/`entity_table` キーを付ける(Secondary同様)。grantで変わるのは `proper_noun_evidence` のみ(`is_general_word` はledger非依存 er103:267)。
- W-02[必須] 等価性test強化: (a)単調性test=D1/D2/fixtureにTrial実表を与え、表なし受理は表ありでもバイト一致 (b)差分test=Trialの `evaluate_alarm_eligibility_pn` をtestからのみimportし全コーパスで accept/reason/diffs(canonical)一致 (c)無関係表でもG3不受理分岐で `ret3_rejected` が付く矛盾→期待値を「accept/reason一致、detailは追加キーのみ許容」にするかキーを付けない設計に。署名は `evaluate_alarm_eligibility` への入力(cls diffs直列化)で凍結(上流再計算だと②UKUS導入で署名が動く)。
- W-03[必須] 表の導出属性(eligible `lowercase_seen`、見出し除外、`_det_support`)は全textに依存→保存はLLM生候補+coverageのみ、判定用の表は毎回の構築点で「今のprovider textの和集合」に対し決定論(API 0)で再計算、今のtextに逐語出現しない旧entryは外す。Zも両levelの脚本が揃えば和集合を渡す(Zは1構築あたり最大2(A+B)×2 level=4 callになり得る点を是正)。
- W-04[必須] 継承・Store再判定経路では `current_table()` を自動取得しない: 自動取得はadapter経路(er006_secondary_asr_01.py:827)に限定(センチネル引数または明示渡し)。継承は復元表かNoneを必ず明示。継承で受理したら `pronunciation_alarm.entity_table` を `dec.detail` で更新。
- W-05[必須] RET-3: span内tokenが `supply_map` に含まれる場合は不適用(`ret3_rejected="supplied_token_in_span"`)、test固定。
- W-06[必須] Store再利用: `guard_entry` は再判定NGでも保護理由でなければ `blocked=False`(REJUDGE_NG_NOT_PROTECTED er078:92-96)→呼出元(Z `generate_or_reuse_z`、X)が再生成するか確認。しなければA-11条件を `entity_contributed ∧ (not ret.is_active_for_run() or not 復元可能[builder_version不一致])` に広げ明示block。
- W-07[必須] 発火証拠はX/Zとも正式runner経由: X-2の対象を `pool_n8_airport_line` の `point_two`(Kristie Tse、系統的誤読)にし正式入口 `--only-segments` で再生成(自然発火の可能性高)。Zは Bertie 4clipを正式runnerで(B工程)。発火しなければ予備策=正式runnerの生成器差し替え(Z `run_tts_stage(generators=...)`)で保存誤読wavをreplay(隔離run_dir、Store書込は隔離/無効化)。harnessのみの証拠では PRODUCTION_WIRED にしない(証拠区分を受入記録に明記)。
- W-08[推奨] LR時NERなしは許容(fail-closed)だが「LRで新たに出た固有名詞は表外=現行挙動(受理範囲は縮小方向)」とDECISION_LOGに記録。LRで名前を残したtextも既存entryの `occurrences` で証拠付与されることをtest固定。
- W-09[推奨] NER失敗textは `covered_text_sha256` に入れず再試行、statusは構築ごと記録。
- W-10[推奨] `builder_version` 対象にwordfreq/pronouncing version・`GENERAL_WORD_MIN_ZIPF`・`CMU_OK_CATEGORIES`/`USABLE_GRADES`・`_verify_llm`/`_merge_initials`/見出し除外規則・model idを含め、明示定数+関連source hash照合のgolden test。任意で「継承無効化版(eligible規則)」と「resume再構築版(prompt/model)」を分離。
- W-11[推奨] 並行書込はlockfile(O_EXCL)。
- W-12[推奨] 逐語検証は供給前script textに加え `tts_safe_*` 変換後text(X er019:303-306)でも行い、正規化ずれをtest固定。
- W-13[推奨] Perplexity Stage1 resolveは受理diffごとに呼ばれる(er006:839-846)→run単位の名詞memoの有無確認(無ければ追加推奨)。Perplexity結果は受理を左右しない(記録のみ)ことをtest固定、operator報告で表の根拠とPerplexity根拠を別欄。
- W-14[推奨] B工程のHR Lock解除根拠=ユーザー原文USER_02 §1-B・§3を受入記録に明記(11-8維持境界)。
- W-15[推奨] commit手順: `git commit --only -- <path>`、`git diff --cached --name-status` 確認、worktree分離、baseline署名commitは単独path限定。(indexの誤staged削除11件はFable側で解消済み)
- 情報: PNAP scope選択は正しい、X dry_runはAPI 0、Z hook非経由、decorator重なり問題なし、NER費用は `cl.install` 後で予算に含まれる。11-7限定例外は使わない整理で可。②との干渉は近接hunkのみ、処理順で安全条件は緩まない。Z Seed key_rolesはBertie検証に無関係(Bertieはcall B由来confirmed)。XのSTOP確認箇所はfile:lineを明記。

