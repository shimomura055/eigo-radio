FABLE-DELEGATION-MARKER: KP-QUALITY-2ITEMS-委任_02-20261022

管理ID: KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_02(OPEN-458)。Opus条件Aレビュー(条件付きGO)を反映し、①KP英語投票の数値・否定保護の解除、②CMU辞書必須のKP選定制約を、Family X/Zの正式Production経路へ配線→回帰→runtime evidence→SSOT→`WIRED_PENDING_FABLE`まで。費用上限=**60円**(evidence。超過見込みは実行前STOP報告)。本日(2026-10-22 JST)の累計≈1,157円、日次上限1,500円(ユーザー例外)。JST日付が変わった場合は翌日上限1,000円を新たに適用。

## 0. 読む・保存
- `docs/pm/PM_BRIEF.md`、`.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 26節・8節
- 委任_01成果: `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/{INVESTIGATION_01,IMPLEMENTATION_DESIGN_01}.md`、`er108_kp_cmu_lexicon_gate_01.py`、`er108_kp_vote_noguard_01.py`(+test)、`docs/pm/RESULT_PACKET_KPQ1.md`
- ユーザー原文 `docs/pm/delegation_log/2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_USER.md`
- T-0保存 `..._委任_02.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: KP-QUALITY-2ITEMS-委任_02-20261022` 一致で確定)。Opusレビュー全文(§6)を `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md` へ逐語保存し、`docs/pm/OPUS_FINDINGS_LEDGER.md` に OF-KPQ-P-01〜10 を登録。

## 1. Fable決定(Opus採否)
- 条件付きGOを採用。**must-fix P-01・P-02は配線前必須**。P-03〜P-10は配線時に実施。
- **P-01**: `guard_entry`のKP skipはlabel判定ではなく、呼出元が渡す明示引数(`kp_vote_gate_follows: bool`)で行う(Store=`reuse_gate is not None`、X前回results=`role=="english" and kp_vote.vote_enabled()`、X引継ぎ=`kp_vote_required`、Z=`spec.kind=="kp_en" and kp_vote.vote_enabled()`)。A/B/C・rollback(vote無効)・非KP labelで保護維持のtest必須。
- **P-02**: M2(canonicalization後のCMU再確認)でNGになった時点で`keywords_canonicalized.json`を即座に`*.STALE_*`へ退避し、CMU noteを次の周へ確実に渡す。scaffold再実行(resume)時のKP再走条件を配線前に確定しSSOTに記す。
- **P-09**: `er019_family_x_validation_inheritance_01.rebuild_state(rejudge_f1)`のKP英語は、`kp_vote.vote_enabled()`のときvote reuse経路で再判定する(小改修で収まる場合)。収まらない場合は対象外としてSSOTに記録。bulk rejudge scriptの運用注記を入れる。
- **F1(Azure辞書形の併用=C1)**: ①の範囲外の仕様追加。**本委任では実装しない**(ユーザー判断待ち、UDR採番は本委任で行う: 「a2型(OpenAI `'s`脱落+Azure `1's`→両NG)への対処: (ア)C1承認して追加配線=Fable/Opus推奨/(イ)①②のみ」)。最終報告では「b1b型は解消、a2型は残存」と明記。
- Q1 AMBIGUOUSは票の分類として維持(保護解除の対象外)とSSOT明記。Q3 er104へ折込み単一実装、`kp_vote_check_v1`据え置き+`guard_lifted`/`guard_lifted_version`加算、staging module `er108_kp_vote_noguard_01.py`は削除(testは移植)。Q5 R4(clitic分解)はSSOT明記+clitic側もCMUエントリで確認。Q6 M2はINVALID→外側retry。Q7/P-10 事後試聴リストに`observed_protected_diff`表示、数値系合成test拡充。P-05 KP段開始時にCMU辞書preflight+`lexicon_info()`をmetadataに記録。P-06 P1解除でP2除外が評価されるtest。P-03 `er104_kp_vote_wiring_test_01.py:309`更新、er107ページ説明の注記。P-04 不要(P-01採用)。

## 2. 実装(①②は独立ファイル群なら2系統並列で進めてよい。同一ファイルは直列)
- ①: 設計G1〜G9の解除(KP英語限定)、`NG_PROTECTED_DISSENT`/`kp3v.NG_PROTECTED`/`protected_dissent_blocks`/`Voter.protected_diff`判定用途の撤去(非KPの`er078.NG_PROTECTED`は残置)、`observed_protected_diff`監査記録、Store再利用・X引継ぎ・Z経路での再判定追随、Whisper失敗は技術STOP維持、S+W行は`PASS_WITH_WARNING`維持。
- ②: M1(er105 `run_selection_gate` validate直後)、M2(`run_kp_with_outer_retry`内 used_form再確認→INVALID)、診断note(Prompt 2本文不変・`prompt_prefix_intact` assert維持)、最終attemptでの除外→shortfall(min_keep=1、残0はINVALID)、A/B/C無影響のtest、`cmu_gate`メタデータを選定metadataへ記録。
- 既存test更新(設計§6一覧+P-03)、fixtureのKP語がCMU登録語であること、`er104_nonkp_before_after_01.py`で非KP 12,096行バイト一致の再実行。既存失敗`test_er104_core_is_imported_only_from_the_approved_production_set`はer107を研究用として除外対象へ追加して是正。
- 全回帰 `run_project_regression.py`: 新規失敗0(baselineは直近の数値と比較)。Dangling Grep(撤去識別子0、記録系er106/er107の表示文言は注記)。secret_scan hits=0。commitはファイル単位・意味単位(①配線/②配線/撤去/SSOT)、`git push origin HEAD:main`。`git add -A/-u/-f`禁止。
- 禁止: STOP/HR Lock迂回、人工entry、走行中有料runの再起動、Prompt 2本文変更、A/B/C挙動変更。

## 3. runtime evidence(配線・回帰PASS後。事前にSTOPセンチネルrc=0、`TTS_EXECUTION_MODE=STANDARD`、Production .py未commit差分0)
- ①-(a) 保存音声の本番関数再生(API 0): coffee `pump one's fist` 8本+KP3V保存84件を本番adapter経路で再判定し、N1#1・N2#4がWhisper経由PASS、84件で偽PASS増加0、N1#4は両NGのまま、を記録。
- ①-(b) 正式入口(X)で`pump one's fist`のKP英語を新out_dirで実生成(coffee a2またはb1bのKP段+該当KP音声のみ。数円)。Azureの`1's`→保護差が票に影響せずWhisperが呼ばれ、2/3でPASSになる自然発火を狙う(発火しなければ事実を記録。mock再生は証拠にしない)。
- ②: X small_bag a2(`novelty minaudière`を含む本文)とZ melosのKP段を正式入口で実行(新run dir、数円)し、除外→再選定→確定(またはshortfall)の記録と`cmu_gate`メタデータを収集。Zは`--mode dry-run`→`--stage kp`相当の正式入口(存在しなければstage allのKP段まで)。
- P-08(a): 正式runの全KP vote記録に`guard_lifted`、全選定metadataに`cmu_gate`が付くことを集計。
- 費用は出典付きで集計。STOP/HRが出たら迂回せず記録。

## 4. SSOT・報告
- CURRENT_SPEC KP節: P-07解釈(b)の置換(KP英語は保護なしの真理値表、AMBIGUOUS維持、`guard_lifted`)、KPFTブロックへCMU条件(正規化規則R1〜R4、M1/M2、shortfall、辞書version)追記。DECISION_LOG(ユーザー承認2026-10-22、Opus条件A、Fable決定)。OPEN-458→`WIRED_PENDING_FABLE`(evidence参照)。OPEN-456 F3へ「①で b1b型解消/a2型残存→UDR」。UDR新規採番(a2型対処)。REPORT_LEDGER 1行。ACTIVE_TASK更新。
- `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/RUNTIME_EVIDENCE_01.md`(X/Z別、①②別の判定表、path、費用出典)、`docs/pm/RESULT_PACKET_KPQ2.md`(4行+判定整合行)。
- 報告: ①②×X/Zの配線・test・evidence結果、must-fix対応箇所(file:行)、撤去一覧と残置、回帰数値、費用、commit hash、raw URL、未確認項目。

## 6. Opusレビュー全文(逐語保存用)
---
## Opus独立レビュー KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01(OPEN-458)条件A

### 1. 総合判定: 条件付きGO
設計の骨格は妥当です。判定はjudgeとer104の1箇所に集約されてX/Z両方に効き、Store再利用での判定は単調(旧PASS⊆新PASS)、②は選定段とcanonicalization後の2段で確認します。ただし次のMajor 2件を配線前に直す必要があります。
- OF-KPQ-P-01: G9をlabelで判定すると、A/B/CのKP英語の保護まで外れる。
- OF-KPQ-P-02: M2でNGになった後、不適合なKPファイルがディスクに残る。

もう1点、項目①を実装しても「a2型」の停止(coffee a2最終wav)は残ります。これは①の範囲外の仕様追加なので、ユーザー判断事項として報告に明記してください(§4)。

### 2. 各論点の判定

**Q1(AMBIGUOUS降格の維持)— GO**
- AMBIGUOUSは「数値の不一致」ではなく、1票ごとのPASS/NG分類の一部です(S票はsame_surfaceを要求、Whisperは`ambiguous_blocks`)。多数決より優先してNGにする効き方ではないため、ユーザー文言には抵触しません。
- 保存データでもA=Bでした。SSOTには「AMBIGUOUSは票の分類として維持(保護解除の対象外)」と明記してください。

**Q2(Primary自身の保護差による短絡も解除)— GO**
- 「NG/PASS→Whisper」の行を例外なく適用するには必要です。
- 追加されるAzure呼出は、Primary NGかつ自身に保護差がある稀なケースに限られます。非保護のPrimary NGは従来からP3でAzureを呼んでいるので、増分はこのケースだけです。
- 注意: P1を外すと、該当ケースでP2除外(`_exclusion_hit`)が評価されるようになります。これは数値・否定の保護ではないので維持で正しい扱いです。testに1件加えてください。

**Q3(er104へ折り込み・version `kp_vote_check_v1`据え置き)— GO**
- reuseは毎回現行judgeで判定し直します(`kp_vote_reuse_ok`)。古い証跡を新規則で誤受理する経路はありません。
- `secondary.protected_diff`を読むProductionコードは`vote_check_from_audit`:411だけでした(Grepで確認)。
- `guard_lifted`と`guard_lifted_version`を加算形式で残せば区別できます。stagingの`CHECK_VERSION="kp_vote_check_v2_noguard"`は折り込み時に`guard_lifted_version`へ移してください。

**Q4(G9のKP skipをlabel判定1関数で行う)— NO(代替が必要)→ OF-KPQ-P-01**
- Store呼出(`er006_master_audio_store_01.py:130`)のlabelは`"master:"+style_instruction_id`です。A/B/Cの`shared.ensure_key_phrase_english_component`(`er003_v1_n3_01_tts_generate.py:1170`ほか)も同じ`style_instruction_id="key_phrase_english_component"`で、reuse_gateはありません。labelでskipすると、vote gateが後に続かないA/B/CのKP英語再利用から保護が完全に外れます。
- vote無効時(rollback)も同じで、K2のStoreは`reuse_gate=None`になります(`er019_family_x_kp_en_k2_store_01.py:86,116`)。
- 代替: `guard_entry`に明示引数(例: `kp_vote_gate_follows: bool`)を足し、4つの呼出元から渡します。
  - Store: `reuse_gate is not None`
  - X前回results: `role=="english" and kp_vote.vote_enabled()`
  - X引継ぎ: `kp_vote_required`
  - Z: `spec.kind=="kp_en" and kp_vote.vote_enabled()`
- 呼出元の変更は各1行です。「呼出元は無改修」という前提は捨ててください。
- 追加test: A/B/C keyのentryでPrimaryに値DIFF→引き続きblocked。vote無効でも引き続きblocked。`reuse_blocked`のmarkは引き続き尊重。

**Q5(CMU照合の正規化)— 条件付きGO**
- R3(ハイフン分解): TTS入力も`tts_safe_kp_en`でハイフンを空白にするため、語単位照合と整合します。GO。
- アクセントと語形変化を救済しない判断: 原文の「推測・外部辞書で代替しない」に忠実です。GO。
- R4(縮約・所有格のclitic分解): 句読点等による誤除外の防止として解釈できます。ただし規則による分解なので、SSOTに明示してください。census(調査で集計した保存KP全数)でのR4発火は0件(whole 1425/stripped 3/hyphen 2)で、実害は小さいです。辞書照合だけで説明できる形が望ましいので、clitic側(`'s`等)もCMU登録エントリであることを`lookup`で確認する形を推奨します(OF-KPQ-P-07)。

**Q6(最終attemptでの除外確定と、canonicalization後NGの非対称)— GO**
- 2回目でLunaにCMU不適合を明示したうえでの除外です。数は埋めず、件数は既存の1〜3件可変の範囲に収まり、rankも`build_original_items`で1..nに振り直されます。
- M2は後段(gloss・Redundancy前)のため、除外ではなくINVALIDとする方が単純で安全です。保存2,130件で発火は0件でした。
- ただしM2側の配線にOF-KPQ-P-02の修正が必要です。

**Q7(S+W行=Primary NG・Azure PASS・Whisper PASSの増加と事後試聴リスト運用)— GO**
- 偽PASSになるには、AzureとWhisperの両方が正解側へ聞き違える必要があり、確率は低いです。
- 事後試聴リストの行に`observed_protected_diff`を表示して優先確認できるようにすることを推奨します。
- 合成の誤転写データは数値系が9件しかありません。数字同士(2↔3)、序数、`1's`などの数値ケースをtestに追加してください(費用0、OF-KPQ-P-10)。

**F1(a2型の残存とAzure lexical形の利用)— ①の範囲外で、ユーザー承認が必要な仕様追加と判断**
- ユーザーが述べた停止のしくみ(「1's→保護差→Whisper不呼出」)は①で消えます。b1b最終wavのHR原因は解消します。
- a2最終wav(N1#4)は、Primaryも`'s`を落としてNGです。両NG=NGはユーザー自身の真理値表どおりなので、①で救済すれば承認内容を超えます。
- 技術評価(C1: Azureの判定にlexical形も使う):
  - 方法: `OutputFormat.Detailed`の`NBest[0].Lexical`を取得し、期待KPに数字が無いときに限り、S票を「表示形と同じ受理判定でPASS、またはlexical形でPASS」とします。
  - 追加API: 0(同じAzure呼出の出力形式だけ変える)。
  - 偽PASSリスク: lexical形はITN前の認識結果そのものなので、表示形と同程度で低いです。ただし数字の読み下し、略語(`u s`)、`mister`などで表記が変わるので、OR結合と数字なしの条件が必要です。
  - 規模: er006のrecognizer設定とoutcome、cacheの値、judgeの受理判定、監査、testで数十行程度。Store内の旧証跡にはlexical形が無く、表示形のまま判定されます(単調なので問題なし)。
  - 共有影響: `evt.result.text`は変わらないため、非KPへの影響は「取得するだけ」に限られます。
  - 実効性の確認: coffee wavで本当に`one's`が返るかを1回のTrial(約1円)で確かめる必要があります。
- 区分: 承認済みのASR判定の入力定義を変えるので、AZURE_ITN_IMPACT_01の分類どおりユーザー承認が必要です。DEV経路でVALIDATEDまで進めてから採用を判断する流れになります。
- ①のPRODUCTION_WIREDはこれを待たずに進めて構いません。

**F2(撤去範囲の漏れ・過剰)— 条件付き**
- G1〜G9でほぼ網羅しています。`er078.NG_PROTECTED`を残すのは正しいです。
- Z(`er063`)、X前回results、X引継ぎはいずれもvote_requiredの統一judgeとG9を通るので、P-01を直せば保護解除が効きます。
- 漏れ1: `er104_kp_vote_wiring_test_01.py:309`の`kp3v.NG_PROTECTED`(judgeとdecideの一致test)が更新一覧にありません。
- 漏れ2: `er019_family_x_validation_inheritance_01.rebuild_state(rejudge_f1)`:461は、KP英語のlabelもvoteなしのjudgeで判定し直すため、S+W行を拒否し得ます。KP3Vで整理した再利用6点の外にある既存のすき間です。Production経路として扱うかを決め、扱うならvote reuseを通すか、対象外とSSOTに記録してください(Minor)。
- 漏れ3: `er078_auw_reuse_bulk_rejudge_06c.py`を再実行すると、KPのS+Wのentryに`reuse_blocked`が付き得ます。運用注記で足ります。

**F3(Store再利用とWhisper失敗時の挙動)— GO**
- `+vote1`はPASSしか保存せず、P PASS/S NGのものは`PASS_VOTE_2OF3`で、保存済みのWhisper転写があります。したがって保存音声にローカルWhisperを走らせるのは、主にS1(証跡なし)の場合に限られます。
- Whisperが失敗すると`ACTION_TECHNICAL_STOP`になり、再利用も再生成もしません。再生成ループは発生しません。
- coffeeのentryはstatusがOKでないため、そもそも再利用経路に入りません。HR Lockも自動では解除されません。①-R2は「本番関数による再生」と位置づけるのが正確です。
- 既存の軽微な問題: Storeは、Whisperが原因の技術STOPでも`TECHNICAL_STOP_SECONDARY_UNAVAILABLE`と表示します(:153)。

**F4(②の挿入点M1/M2)— 条件付き → OF-KPQ-P-02**
- noteはPrompt本文の後ろに置かれ、`prompt_prefix_intact`のassertで本文不変が保たれます。
- ループはer105で2回、外側で通算3回が上限で、無限ループはありません。空のKPは、M1では`min_keep=1`、残り0件ならINVALIDで防がれます。Z D1 gate、gloss、解説への影響はKP件数が可変になる点だけで、既存仕様の範囲内です。
- 問題: M2でNGになったとき、canon_fnがPASSとして書いた`keywords_canonicalized.json`(CMU未登録のused_formを含む)が本名のまま残ります。`_kp_retire_stale_artifact`で退避されるのは上限到達時だけです。次の周の冒頭でSTOPセンチネルを確認した時点、あるいはクラッシュで止まると、X TTS段の再開時(runner:933/:1340)がそのファイルを読みます。
- 対処: M2でNGになった時点で即座に退避し、次の周のnote用変数(cmu_note)もNGごとに作り直してください。
- scaffold再実行時の再開条件は、委任_02での確認ではなく配線前に確定させてください。

**F5(runtime evidence計画)— 条件付き**
- 線引き(mockによる再生はtestの証拠でありruntime evidenceではない)は妥当です。
- ただし自然発火しない可能性が高いので、次の2点を加えることを推奨します(OF-KPQ-P-08)。
  - (a) 正式runの全KP vote記録に`guard_lifted`、全選定metadataに`cmu_gate`が付いていることを、配線の証拠として集計する。
  - (b) ①について、正式入口(X)で`pump one's fist`のKP英語を新しいout_dirで実際に生成する。Azureは8/8で`1's`を返しており、Storeにもentryが無いため、自然発火が見込めます。費用は数円です。

### 3. must-fix / recommended
- **OF-KPQ-P-01 Major**: G9のskipを、呼出元が渡す明示引数(vote gateが後続するか)に変える。A/B/C、rollback、Z/Xの非KP labelでは保護を維持するtestを付ける。
- **OF-KPQ-P-02 Major**: M2でNGになったら`keywords_canonicalized.json`を即座に退避し、CMU noteを次の周へ確実に渡す。再開経路を配線前に確定する。
- OF-KPQ-P-03 Minor: 撤去対象とtest更新一覧に`er104_kp_vote_wiring_test_01.py:309`を追加する。er107ページの説明文が古くなることも注記する。
- OF-KPQ-P-04 Minor: label判定を残す場合は完全一致にする(`kp\d+_en`の前方一致は使わない。`kp1_explanation_en`等と区別するため)。P-01を採ればこの点は不要になる。
- OF-KPQ-P-05 Minor: KP段の開始時にCMU辞書のpreflightを1回行い、API支出の前に辞書不備で止める。`lexicon_info()`(cmudict 1.1.3、エントリ数)をmetadataに記録し、versionを固定する。
- OF-KPQ-P-06 Minor: P1を外したことでP2除外が評価されるケースのtestを足す。
- OF-KPQ-P-07 Minor: R4(clitic分解)をSSOTに明記し、clitic側もCMUエントリで確認する形を推奨。
- OF-KPQ-P-08 Minor: runtime evidenceにF5の(a)(b)を追加する。
- OF-KPQ-P-09 Minor: `rebuild_state(rejudge_f1)`のKP英語の扱いを決めて記録する。bulk rejudge scriptの運用注記も入れる。
- OF-KPQ-P-10 Minor: 事後試聴リストに`observed_protected_diff`を表示する。数値系の合成誤転写testを拡充する。

### 4. ユーザー判断が必要な事項
- **1件**: a2型(Primaryが`'s`を落とし、AzureがITNで`1's`→両NG)の残存への対処。推奨はC1(Azure lexical形をOR結合で併用、期待KPに数字が無いときだけ、API追加0、Trial約1円)です。
- 技術的には「①の実装詳細」ではなく、承認済みASR判定の入力定義の変更にあたるため、ユーザー承認が必要です。
- ①・②のPRODUCTION_WIREDはこれを待たずに進めてよいと考えます。最終報告では「b1b型は解消、a2型は残存」と明記してください。

### 5. 品質・速度・単価への影響見積の妥当性
- ①: 偽PASSの増加0は保存84件で裏付けがありますが、数値系の母数は小さいです(数値を含むKP 11句、合成9件)。追加費用は、Azureが稀なケースで1回/件、Whisperはローカル(CPU数秒)で、ほぼ0円です。HRは減る方向で、この見積は妥当です。
- ②: 未登録率2.9%/句、追加のLuna呼出0.08回/レベル(約0.2円)は妥当です。品質面では、最終attemptでの除外によってKPが3件未満になるケースが一部出ます(推定8%弱のレベルでCMUに該当し、その大半は2回目で解消)。件数は既存の可変仕様の範囲内です。M2による外側retryは、canonicalizationとglossを再実行するため1回あたりは高めですが、頻度はほぼ0です。
- runtime evidenceの40円以下は、F5(b)を加えても数円の増加で、範囲内に収まります。
---