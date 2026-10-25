# OPUS_REVIEW_01: Opus条件A独立レビュー結果(Fableが委任_02A文§2〜§3に逐語転記したもの)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 / 保存日 2026-10-25。レビュー対象=`OPUS_REVIEW_REQUEST_01.md`(DESIGN_01・SPEC_LEDGER_01等)。
**出所の注記**: 以下は、Opus独立レビューの結果をFable(sandwich-pm)が委任_02A文の§2(Opusレビュー要点)・§3(Fable確定判断)に転記した本文を、**一字も変えずに保存**したもの。Opusの生の応答全文は本Sonnet(02A)の手元に無く、本書の範囲が逐語である。Opus原文の全文が必要な場合はFable側の記録を参照。

---

## (逐語) §2 Opusレビュー(要点)

- 結論: 新規er121(Z stage形式)は妥当。M-1〜M-6反映後に実装着手可。
- **M-1(実装不具合、Phase 0の「不具合0」は誤り)**: `er110_family_y_persona_text_trial_01.py:376-381,405-414` kind="tension"の判定promptは`_TENSION_ITEMS`のみで組み立てられ、その1行目「leak_evidence_subject/leak_discovery_syntax/leak_evidence_memorable: 上記と同じ意味」の「上記」=`_VOICE_ITEMS`が同promptに入っていない(developerにも定義なし)。判定器は3項目を定義なしで推測判定している。旧B英語版(`er012…:342-374`)は全セクション1promptで成立していた→Y版の移植ミス。過去FAIL#3(「見えてくる」discovery_syntax)・#4はこれが原因の可能性(G-2不要になる見込み)。具体案: Production側のtension判定promptで3項目の定義を`_VOICE_ITEMS`から逐語展開(判定基準文言は一字も変えず欠落定義を補うだけ)。DEVは変更しない。Production版とDEV版の差分が「定義の展開だけ」であることをtestで固定。着手前に過去Closing 11件+案B+Lead/紹介Gate(tension項目使用時)を修正後promptで再判定して較正(数円)。案BがFAILになった場合はユーザー判断。
- **M-2**: 既存`run_gate`/`run_gate_pl`のtension書換え規則`TENSION_RULES(_PL)`は旧B骨格(共通→違い→食い違い→締め、1文45字)でPrompt 02出力に当てるとPrompt 02の意味が変わる。`apply_rewrites`のtension経路は一人称検査のみで`check_closing`(175〜245字・1文55字・「？」終わり)を通さない。委任_28先例はCLOSING_RULESへ差替え+CLOSING_POST_GATE_STOPで再検査。具体案: 書換え規則はsha固定Prompt 02の【最終パートの書き方】節をマーカーで切り出して逐語使用+選定済み切り口(`new_view`+`evidence_quotes`)+run_gate共通「指摘箇所だけ直す」。書換え後は`check_closing`+記号・タグ検査必須、2回失敗で`REWRITE_STOP`。`closing_record`に書換え有無・生成時sha・最終sha。判定≤3・LEAKAGE_RESIDUAL_STOPは承認範囲内。書換え経路はTrialで未通過→過去FAIL稿(R1宅配gen_1、R2宅配H2)を入力に書換え経路のruntime evidenceを取る(新規生成不要、数円)。
- **M-3**: 共通工程(Zの`stage_kp` er026:1839-1954=約120行、`run_tts_stage` er063:1367〜)の「相当版」をYに書くと将来の配線漏れが再発。(a)DESIGN_02にstageごとの「直接importする共通関数」と「Y固有新規範囲(テキスト生成・segment計画・timeline順・role文のみ)」の境界表。(b)構造一致test: er026/er019の対応stageが呼ぶ共通module呼出しを静的抽出しer121と比較、意図的差分は台帳ID付き許可リスト。(c)STOP/RUN_LOCKは`er062_family_z_structure_01.py`の関数(`check_stop_sentinel`/`acquire_run_lock`/`record_launch_and_check_storm`等)をimport。
- **M-4**: KP HRは「stage 8の直後」ではなくKP呼出そのものを`er119_kp_wiring_01.run_kp_with_review`(`sc.run_key_phrases`互換、family引数)に置き換え、XのPENDING(rc=4)/NotConfirmed(rc=4)/Inconsistent(rc=3)入口確認・`verify_selection_matches_outputs`・`part1_items`も同形で最初から入れる。文法HR/Part 2(er120)のみ接続点として残す。
- **M-5**: 台帳漏れ: Source Reference Contract(X=候補ID方式、Z=D1)、YのKP引用文参照方式、gloss再整合(OF-229/`EIGO_KP_GLOSS_ALIGNMENT`)、gloss人称Gate(ITEM1)、gloss HR、Run Entity Table(OPEN-472)、TTS予算wrapper、mock時attempt_history隔離。スコープ判定基準の明文化: (i)Family非依存でYの明示除外なし→適用(PNAP/er109/基本形化例外、開示事項) (ii)Family別パラメータ方式→Y用方式承認まで「除外+OPEN記録」(Chunk。「判断待ち」より正確) (iii)明示除外→除外(中核数値v4/J2)。
- **M-6**: `voices`段(Voice生成+Voice Gate)のProduction runtime evidenceが計画にない→E-3でSNSのTheme Packageから`voices`段を実行(既存テーマ、約20〜26円、Cap 150円内)。
- R-1 案B固定registryはslugだけでなくTheme Package sha(f0d0af…)とVoice R0 `article_ja.md` sha(566ebd97…)にも紐付け、Voice変更時は注入せずSTOP。Gateは同shaの既存PASS記録(`closing_B/gate/gate_result.json`)を来歴検査付きで再利用(M-1で判定promptが変わった場合のみ再判定)。`check_closing`も適用。R-2 E-3はSNSで`english`・`plan`まで。R-3 model_id照合はer006既存の実model照合関数を流用。英訳は`FAMILY_Y_TRANSLATE_*`(値はX定数参照+drift test)。R-4 Voice Gate書換えpromptは題材非依存の`build_voice_rewrite_prompt_pl`系。R-5 配線漏れ防止: item33は28-2運用2と重複→正本はCURRENT_SPEC「共通仕様のFamily別配線Status表」に一本化しM-5の漏れ行を追加、`spec_ledger_01.json`は立上げ作業表としY PRODUCTION_WIRED時に廃止、コード強制はM-3(b)。R-6 原価: cached_tokens実測、flex/Batchの可否確認(未確認)。R-7 routing key名を先に確定しL1/L2を並行、Closing段+routing完成時点でE-3(M-2書換えevidence含む)を先行。
- C-1〜C-7 問題なし(X拡張/DEV昇格不採用、Prompt 02 byte一致+sha照合・schema・決定論検査・再生成1回・CONTRACT_STOP、I-2/I-3/I-4、Lead/紹介にTension専用2項目非適用、除外の妥当性、Y segment ID新設+網羅test[page・assembly・Master store keyまで]、G-1〜G-3/P-1のユーザー判断整理)。
- ユーザー確認: (1)原文復元(本委任§1で解決) (2)M-1再判定で案BがFAILの場合のみ (3)G-1提示時はY版`leak_tension_reverts_to_research`が旧B原文のFAIL条件(「survey/研究結果の紹介・数字比較が主たる内容ならFAIL」)と括弧内観点を欠く=「移植時の欠落の復元」に近い旨を添える。70円超過・Chunk非適用は実測後の報告事項。

## (逐語) §3 Fable確定判断

M-1〜M-6・R-1〜R-7すべて採用。M-1はユーザー指示§6「判定器への入力ミス等は委任範囲内で自律的に修正・検証」に該当=Production版で定義展開(DEV不変)、較正で案BがFAILならSTOPしてユーザー判断。Chunkは「除外+OPEN記録」へ分類変更。配線漏れ防止の正本はCURRENT_SPEC配線Status表(PM_GOVERNANCE項目追加提案は取り下げ、28-2運用2の補強として記述)。

---

## 本書への02A注記(逐語ではない。Sonnet記述)

- 各指摘の反映先: M-1=`er121_family_y_text_core_01.py`(`_TENSION_ITEMS`の展開、DEV差分test)・`GATE_CALIBRATION_01.md` / M-2=同module(`closing_rules_section`/`build_closing_rewrite_prompt`/`apply_rewrites`)・`REWRITE_EVIDENCE_01.md` / M-3=`DESIGN_02.md` §3 / M-4=`DESIGN_02.md` §4 / M-5=`SPEC_LEDGER_02.md` / M-6=`BUDGET_PLAN_02.md` / R-1=registry(同module) / R-3〜R-7=`DESIGN_02.md`。
- 「M-1(DEV `er110…:376-381,405-414`)の欠落」は、02Aが実コードで再確認済み(`er110_family_y_persona_text_trial_01.py:376-381`の`_TENSION_ITEMS`が『上記と同じ意味』を参照し、`build_leak_prompt('tension')`は`_VOICE_ITEMS`を含めない)。
