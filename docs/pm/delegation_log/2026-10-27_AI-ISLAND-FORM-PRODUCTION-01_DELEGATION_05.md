## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_05(ユーザー指示2026-10-27「①②③学習仕様の整合・フォーム送信確認・AI島Human Review原因調査」§4【優先】: AI島Std/AdvのHuman Review発生理由を実runtime・ログ・保存データに基づき証拠付きで明確化し、**承認済みの自動処理で解消可能なら自律的に解消**する。解消不能で正式仕様上HRが必要な場合のみ、指定8項目セットでHRを再提示。原文=`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md`(FORM委任_09が逐語保存中。未着なら本委任文の要約で進め、着き次第照合)。有料上限¥30(Fable自律枠。TTS再生成は該当1 segmentのみ、本文・他segmentの再生成禁止)。並行Agent: SLOT-23 M班(`er119`/`er128`/`er121`/`er026`編集中=**編集禁止**。`er019`は編集可だがProduction既定動作の変更・Gate緩和は禁止)、FORM委任_09(read-only)。あなたの所有=run dir `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`(明示stage再実行のみ)、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{HR_ROOT_CAUSE_01,RESOLUTION_01,HR_PACKET_02(必要時)}.md`、`user_test/family_x_ai_island_form_01/hr_02.html`(必要時)、`tools/build_hr_packet_aif3_01.py`(改修可)、`..._DELEGATION_05.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF5.md`(gitignore)。pathspec付きcommit、`git push origin HEAD:main`、wav/raw_usage_log/STOP/lock不追跡。時間見込み約2h。

## 既知の事実(委任_03/_04の記録。再確認して正確に記述すること)

- 停止=`--stage assemble`でM3 Style Gate(`er019_family_x_style_profile_01.m3_assembly_gate`)が`full_story_part1_k2`(第1部2段落目)をBLOCK。Std=`STD_FALLBACK_USED_OR_UNKNOWN`+`LOCAL_REWRITE_RECOVERY`、Adv=`LOCAL_REWRITE_RECOVERY`。
- 元原稿(Std): "The AIs sent to the island had no set tasks or rewards. But their starting settings led them to be curious, explore, and learn. They had no homework, but they were ready to explore."(段落全文を逐語で確認)。Adv: "The AIs sent to the island had no specific tasks or rewards. …"。**本文(article.md・ページ表示)は無変更**。音声のみ、承認済みLocal Rewrite規則で`AIs`→Std「AI agents」/Adv「AI systems」に言い換えて再生成(=「AI systems」が本文に無いのは当然で、音声用の言い換え語)。
- ASR: 複数形`AIs`をOpenAI/Azureとも`AI`と転写(Azure 1回のみ`AIS`)。減速後再検証でも二次ASR・Tier3は実行済み=仕様どおり(`DIAG_SLOWDOWN_ASR_01.md`)。

## 調査事項(§4の1〜5を証拠付きで)

1. 元原稿(全文/該当文、segment・Role・Level、ユーザー確認済み本文との一致=本文SHA)。2. 置換・書換えの有無(Before/After逐語、音声のみか本文も含むか、発動工程・理由・承認根拠=CURRENT_SPECのLocal Rewrite節の行番号)。3. TTS retry/Local Rewriteの発動状況(回数・結果、`standard_attempts_log`/`slowdown_attempts_log`/`local_rewrite_recovery`)。4. ASR判定(Primary/Secondary全文、差分、同音救済・**既存Phrase List/発音台帳(`er006_output/pronunciation_ledger_01/ledger.json`、発音供給枠、`EXACT_MATCH`/`NORMALIZED_MATCH`/`ORTHOGRAPHIC_VARIANT`等)の適用有無と適用できなかった理由**)。5. なぜHRか(正式Gateのどの条件=CURRENT_SPECの行番号、自動処理で解消できなかった理由、HR対象音声が確認する内容、品質/原稿整合/ASR差の区別)。

## 解消の試行(承認済み自動処理の範囲内のみ)

A. **正式仕様の照合**: CURRENT_SPEC(Grep `LOCAL_REWRITE_RECOVERY|M3|Style Gate|Local Rewrite|human_approval|record_human_approval|STD_FALLBACK_USED`)で、「Local Rewriteで品質Gateを通過した音声は人間承認が必要」が**ユーザー承認済み仕様**か、Fable/Sonnet設計判断か、を行番号付きで判定。DECISION_LOGの該当決定も引用。
B. **承認済み発音供給/Phrase Listの適用可否**: 既存の発音台帳・Phrase List・同音救済の仕様(CURRENT_SPEC該当節)に、複数形略語(AIs)を「原稿不変のまま」TTS入力/ASR照合で扱う承認済み手段があるか。あれば、それを用いて`full_story_part1_k2`のみ標準経路で再生成(≤¥10)→通常検証PASSならLR/fallbackを使わない音声として差し替え(M3 Gate通過=HR不要)。無ければ適用しない(新仕様の提案はユーザー判断事項として整理)。
C. **M3 Gateの記録非対称(OPEN-564)**: Stdの`STD_FALLBACK_USED_OR_UNKNOWN`がLR成功時の`_merge`で無条件に立つ件が、Gateの判定結果(BLOCK)を変えるか。BLOCKの根拠が`LOCAL_REWRITE_RECOVERY`だけでも成立するなら実害なし。
D. 結果: (i)HR不要と判定できる場合(=Aで人間承認が正式要件でない、またはBで標準経路PASS)は、`record_human_approval`を使わずに正規手順でassemble→player→標準builder(`er019_family_x_listening_page_01.py`。display_spec無しの現状では従来表示=新表示仕様の適用はSLOT-23 M班完了後のreconsume+再ビルドで別途)まで進め、最終試聴ページ(`user_test/family_x_ai_island_form_01/index.html`)を公開。(ii)HRが正式に必要な場合は`HR_PACKET_02.md`+`hr_02.html`(元原稿/Before・After/推奨音声1件/OpenAI・Azure結果/不一致箇所/自動解消不能の理由/AI評価と確認内容、質問1つ)を作成し、assembleは進めない。
- Gate緩和・Lock直接編集・HRなし宣言・`approve_regenerate`は禁止。起動間隔150秒以上、同一run 5分3回禁止、有料前に`stop_scope_check`+必要性1行。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: 有料=対象。

## 事前指定Read一覧

`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{HR_FULL_STORY_PART1_K2_01,DIAG_SLOWDOWN_ASR_01,BUILD_01}.md`、`docs/pm/RESULT_PACKET_AIF3.md`/`AIF4.md`、run `<run>/{a2,b1b}/audit/tts_generation_results.json`(`segments.full_story_part1_k2`のみ)、`er019_family_x_style_profile_01.py:690-750`、`er003_v1_crosslevel_audio_02_common.py:460-490`、`CURRENT_SPEC.md`(上記Grep)、`er006_output/pronunciation_ledger_01/ledger.json`(構造のみ)。

## 報告

`RESULT_PACKET_AIF5.md`: (0)T-0、(1)真因(§7-1の5点: 書換え有無/Before・After/retry・LR履歴/Primary・Secondary ASR/HRが本当に必要か)、(2)解消試行A〜Dの結果、(3)費用、(4)判断候補、(5)必須4行+「判定整合」、(6)SSOT文案(OPEN-561/564)、commit hash・公開URL・raw URL。末尾5行要約。