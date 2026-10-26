## 管理ID

KP-PHRASE7-WORD5-PRODUCTION-01 委任_02(Opus条件Aレビュー反映`DESIGN_02.md`+Production実装+test+6経路runtime evidence。実装・testはAPI 0、evidenceは有料=上限¥60(Fable自律枠300円以下、見積約¥31))。前提=委任_01設計(commit 875f4455a)+Opusレビュー(下記M-1〜M-9、Fable照合済み・全件採用。M-7は**直列**を採用=並列化しない)。Fable確定D1〜D6: R0(新flagなし・既定ON正規実装・旧Prompt 2/2-V本文とpin test残置)/Adv AUTO vocab5現行維持/`not_single_word` Gate/W5'補足行=ユーザー原文逐語「すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除külする。」の正しい表記「すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。」/補完Prompt種類別/旧HR待ち候補は作り直さない。
並行Agent: (a)KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A(`er119_kp_human_review_01.py`へフック追加中、新module er128、Y/Z runner stage_kp 1行)、(b)LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_03(`user_test/selection_form_v3/**`、`export_form_data_01.py`)。**`er119_kp_human_review_01.py`は(a)のcommitがorigin/mainに載ってから(`git log origin/main -1 -- er119_kp_human_review_01.py`で確認)`KP_CANDIDATE_MAX`の1行だけ変更**し、それまでは他作業を進める。`export_form_data_01.py`の`cap`既定8→12は本委任で触らず委任_03/フォーム側へ引継ぎ(RESULT_PACKETに記載)。あなたの所有=新module `er119_kp_p7w5_prompts_01.py`、`er119_kp_candidates_01.py`、`er119_kp_backfill_01.py`、`er105_kp_fulltext_selector_01.py`(keyword-only既定値付き引数)、`er119_kp_prompt_2v_01.py`(`max_items`引数化)、`er119_test_support_01.py`、`er106_joint_runtime_evidence_01.py`(KPFT-1/3/4 prompt_id別期待値)、`er003_v1_n3_01_scaffold_generate.py`(telemetry 1行のみ必要なら)、関連test、`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{DESIGN_02,OPUS_REVIEW_01,IMPLEMENTATION_01,REMOVAL_RESULT_01,EVIDENCE_01,COST_01}.md`+`evidence_runs/`+`tools/`、`docs/pm/OPUS_FINDINGS_LEDGER.md`(本件条件A依頼・M-1〜M-9・採否記録。KCP2Aが同ファイルを編集中の可能性=commit前に`git pull --ff-only`不可のため、編集直前に`git log origin/main -1 -- docs/pm/OPUS_FINDINGS_LEDGER.md`を確認し最新HEAD blobを基に追記)、`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_{OPUS_RESULT_01,DELEGATION_02}.md`(+check.json)、`docs/pm/RESULT_PACKET_KP75B.md`。`CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS`編集権なし。pathspec付きcommit(実装commitとevidence commitを分ける)。

## 性質/禁止

- 性質: ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-27)仕様のProduction実装+runtime evidence。到達上限=IMPLEMENTED+EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- 禁止: 承認外のフレーズ抽出規則新設、理由40字超・易語をGate除外にすること(品質基準の独自追加)、補完の並列化(M-7は直列)、K1(item単位化)導入、AUTOへの単語組入れ、旧HR待ち候補(OPEN-526等)の作り直し、公開済み/進行中runへの`--regenerate-stage kp`、禁止Git操作、300円超支出、Production経路からの`er124`import。
- 時間見込み: 約4h(実装2h・evidence 1.5h・文書0.5h)。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。Opusレビュー原文(下記)を`..._OPUS_RESULT_01.md`へ逐語保存。T-2(有料run前): `py tools/stop_scope_check_01.py --managed-id KP-PHRASE7-WORD5-PRODUCTION-01 --run-dir <run> --out <...>`、起動間隔150秒以上、同一run 5分3回禁止、`.venv\Scripts\python.exe`+`TTS_EXECUTION_MODE=STANDARD`(KP stageのみ=TTS不使用)。T-3: 費用はusage logから実測しCOST_01へ。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_DELEGATION_02.md` をN=704から順に試し、先頭「## 管理ID」+「KP-PHRASE7-WORD5-PRODUCTION-01 委任_02」のものを採用。

## Opusレビュー(逐語。Fable採否=M-1〜M-9全件採用、M-7は直列採用、R-1は「既知の限界として記録」、R-2〜R-6採用)

## KP-PHRASE7-WORD5-PRODUCTION-01 Opus独立レビュー(条件A、実装前、read-only)

### 結論
**条件付きで実装へ進んでよい(GO with changes)。** 大きな方針(R0、er105の再選定ループは維持、call1→call2の直列、種類別の上限7/5)は妥当です。ただし、実装前に設計へ反映すべき必須修正が9件あります。M-1・M-3・M-4の3件は、直さないと承認仕様(7+5の上限、補完は1回だけ、Key Phraseに含まれる語の除外)を破るおそれがあります。
ユーザー判断に上げる事項は**なし**です。

### 論点別判定

**O-1 Prompt差し替えの影響範囲 — 要修正(M-5, M-6, M-9)**
- 再選定ループ(MAX_ATTEMPTS=2、1件でも不適合なら全件再選定)を維持する判断は妥当です。
  - これは承認済みのcall1仕様です(`er105:482-532`)。
  - なお、Trial-02のP7は異なる方式でした(`er124:221-267`、ループなし・不適合itemだけ落とす)。Production化でここが変わることは、IMPLEMENTATION記録に明記してください。
  - K1(item単位化)は承認範囲外なので、導入しないのが正しいです。
  - P7が平均5.4件しか返さないこと自体では再選定は起きません。件数不足は不適合ではなく、`max_items=7`なら件数範囲内だからです。再選定が起きるのはitem不適合時だけで、費用は+¥0.12/回です。
- er105で引数化が必要な箇所(既定値は従来どおり):
  - 件数検査`:230`、`:423`
  - `shortfall` `:528`
  - metadataの`prompt_id`/`prompt_sha256`/`kp_count_max` `:563-566`。`bf.read_call1_dropped`がこのmetadataを読みます。
  - `build_exclusion_note`の「3件」文言 `:394`
- **M-9 telemetry**: `sc._run_key_phrase_selection_fulltext`は`prompt_sha256=ft.PROMPT_2_SHA256`を固定で書きます(`er003:359-364`)。
  - したがって`select_p7`がsc経由にしないのは正しいです(経由すると誤ったshaが記録される)。
  - ただし、その場合はtelemetry行が欠落します。`select_p7`の中で、P7のshaを付けて`sc._log_kp_backend_telemetry`を1行記録してください。
- **M-5 test harness(mock)の取り違え**:
  - `er119_test_support_01.py:198-199`は、call1を`ft.make_selector_fn`で、call2を`p2v.make_vocab_selector_fn`でmockしています。
  - `select_p7`が`p2v.make_vocab_selector_fn`をそのまま使うと、P7のmessageがcall2用mockへ流れ、件数集計やfixtureが黙って狂います。
  - 修正案: F1に薄いwrapper `make_p7_selector_fn`(schemaは2-Vと同一)を作り、harnessに追加。harnessは想定外のprompt先頭を受けたら例外にする(fail-closed)。
- **M-6 er106**: 設計F6は`:45`/`:813`しか挙げていません。実際には次の3つの検査がNGになります。
  - KPFT-1 `kp_backend` `:805`
  - KPFT-4 `n_items<=3` `:816`
  - KPFT-3 sha `:813`
  - 修正案: 両方のshaを無条件に許容するのではなく、docの`prompt_id`ごとに期待値(Prompt 2なら3件・P2 sha / P7なら7件・P7 sha)を切り替える。
- R-2: `kp_backend`は`"fulltext_p2"`(全文選定backendの名前)のまま据え置き、Promptの識別は`prompt_id`/`sha`で行う方が波及が小さいです。理由は、X runnerの既定値が`fulltext_p2`である(`er030_..._x_production_wiring_01_test.py:560`)ことと、KPFT-1が同じ値を見ることです。

**O-2 上限8→12・種類別cap・shortfall — 要修正(M-1, M-2)**
- **M-1**: `pick_backfill`の種類別の取り数が、現在は**E(除外件数)**になっています(`bf:135`。合計は`plan.total`で制限するだけ)。
  - 例: E_phrase=2・フレーズ空き1・E_word=1・単語空き1 → total=2で、フレーズを2件採るとフレーズが8件になります。
  - 修正案: `quota = {phrase: plan.quota_phrase, word: plan.quota_word}`。
- **M-2**: `candidates:369`の`gate_dropped`除外は、`NOT_COUNTED_STAGES`とは別にハードコードされたtupleです。
  - `overflow_kind`を足さないと、`EIGO_KP_BACKFILL=0`のときに上限超過で落とした句が`excluded`へ入り、外側retryが走ります。
  - 修正案: 両方を`bf.NOT_COUNTED_STAGES`を参照する形に統一する。
- `overflow_kind`をEに数えない判断と、shortfallを「上限未達の情報(エラーではない)」とする扱いは妥当です。`rejected_entries`も`NOT_COUNTED_STAGES`を参照するので整合します。
- `rec["N"]`は`room/total/phrase_wanted/word_wanted/capped`のキーを維持してください(`candidates:473`、`export_form_data_01.py:164`の`N.total`)。
- フォームexportは`[:7]`/`[:5]`/overflowで既に12件に対応しています(`export:162,169`)。

**O-3 Key Phraseに含まれる語の二重除外 — 要修正(M-4)、残りはR-1**
- 機械Gateは表層形のtoken部分列による比較です(`candidates:41-43,95`)。
  - 誤除外のリスクは小さいです。唯一の例は、後でGate除外されたcall1フレーズに含まれる語まで除外される点ですが、これはW5'に見せる一覧と同じ集合なので許容できます。
  - 取りこぼし(price/prices、所有格、ハイフン語)はありえます。W5'のPrompt本文が一次防御です。
- **M-4**: 設計§5の「既存単語を含む新規補完フレーズを保持する」は、最終集合に「Key Phraseに含まれるKey Word」を残してしまい、受入条件3と矛盾します。
  - 修正案: **新規の補完フレーズの方を落とす**(`backfill_duplicate`、Nに数えない)。
  - こうすれば既存候補の保持(§4)と含有語除外(§3補足)が両立します。
  - あわせて、最終docの不変条件(フレーズ≤7・単語≤5・単語⊄フレーズ)をunit testとevidenceの検査項目に追加してください。
- R-1(任意): 基本形化後の`used_form`同士でも含有を確認すると、語形違いをAPI 0で捕捉できます。導入しない場合は既知の限界として記録してください。

**O-4 補完 — 妥当。ただしM-1・M-3・M-7が条件**
- 発動条件(E≥1・現存候補≥1・その種類の空き≥1、初回が上限未満であること自体は条件にしない)は、原文§4と`DESIGN_02:37`に一致します。委任文の「初回上限到達」を採らない判断は正しいです。
- `quota=min(E_kind, cap_kind - 現存)`の式と`BACKFILL_MAX_CALL_ITEMS`の撤去も妥当です(5件上限は2-Vの件数由来でした)。
- **M-3**: フレーズ補完は、**`run_vocab_selection`を一般化した1回callの経路**で実行してください(`prompt_text=P7`、`max_items=7`、item単位で除外)。
  - `er105.run_selection_gate`を使うと、内容不適合で再callが起き、「補完1回・再課金なし」に反します。
  - さらに`work/keywords_runtime_metadata.json`を上書きし、call1の除外の読み取りを壊します。
  - `run_vocab_selection`の上限超過処理(`:111`)が固定値`SELECTOR_2V_MAX_ITEMS`のままなので、`max_items`への置換が必要です。
- 「P7本文が既選定に触れない」という懸念は、`ALREADY_DELIMITER`の見出し「(これらは選ばない)」(`p2v:38`)と機械除外(`existing_entries`)で緩和されます。問題ありません。

**O-5 call1の選定理由(`reason_ja`)— 妥当(軽微な条件あり)**
- canonicalizationのPromptも`merge`も、受け取る項目は固定された一覧(whitelist)だけです(`er003_key_words_canonicalization.py:363-371,859-877`)。`reason_ja`は確定物に漏れません。
- フォーム側は、call1の理由が空でなければ表示します(`export:91-94`)。docstring(`:90`)の更新はフォーム側の担当(H1)へ回します。
- 条件: er105の受け渡しは「キーが存在する時だけ付ける」形にして、Prompt 2経路をバイト同一に保つこと。
- 40字超過はGate除外にしないこと(独自の品質基準の追加になるため)。evidenceで件数を記録するだけにします。

**O-6 「1語」Gate(`not_single_word`)— 妥当(D3に同意)**
- 位置は、validate(救済後の句で評価)→ `not_single_word` → `duplicate_of_top3`の順にします。validateの1〜5語検査とは役割が異なり、競合しません。
- Eは`kind=word`固定で数えます。補完の単語callにも同じ引数を適用してください。

**O-7 resume/retry/二重生成 — 妥当**
- `ensure_kp_review`はPromptのshaを見ずに保存済みdocを読み戻します(`rv:1303-1330`)。旧3+5のdocは再生成されず、D6が成立します。
- reselectの次roundを7+5で作ることも、docのshaで出自を追えます。
- R0で`git revert`した場合も、旧コードは12件のdocを読めます(`KP_CANDIDATE_MAX`はshortfall計算にしか使われていない)。
- KCPとの境界(本件は確定前の候補生成のみを扱い、finalizeには触れない)は妥当です。`er119_kp_human_review_01.py:52`はKCP 02Aと同じファイルなので、rebase後に1行だけ変更します。

**O-8 Y/Zの呼出差 — 妥当**
- X(`er019:802`)・Y(`er121:572`)・Z(`er026:1992`)はすべて`run_kp_with_review` → `make_generate_fn`を、`select_fn`を注入せずに通ります(`er119_kp_wiring_01.py:69`)。
- 差はZの`src_fn`/`person_repair_fn`だけで、これは`_gate_chain`の内部で処理されます。7+5は6経路すべてに同一に適用されます。
- R-5: mockのE2Eは`er026:2792 n_max=8`の候補生成mockで、12件を通りません。受入条件8のmock E2Eでは、7+5のgeneratorを注入してください。`er019:800`/`er026:2018`のコメント「最大8」は表記が古いだけです(runnerは触れない方針なので記録のみ)。

**O-9 evidence計画 — 妥当(追記を推奨)**
- fresh 6経路+replay、「自然発火が見られなければ未観測と報告」、Familyごとに判定、の方針は原文§6と整合します。
- R-4 追記項目:
  - 最終docの不変条件(M-4)
  - 現行3+5に対する実測の費用・時間の増分(usage logから)
  - `call1_attempts`/`outer_attempts`
  - P7が1語を返した件数・`overflow_kind`・`not_single_word`の発生数
  - 理由文40字超の件数(記録のみ)

**O-10 費用・時間 — 妥当**
- 悪い場合の構造(外側3周×call1 2 attempt+canonicalization再実行)は現行と同じで、増分は候補数増によるtoken増と、補完が最大2 callになる分だけです。
- call1→call2の直列は、前工程の出力に依存するので正当です。call1を外側retry間で再利用する案(C-5)は、承認範囲外なので提案止まりで正しいです。
- R-3: Y/Zの予算見積(`STAGE_EST_JPY["kp"]/2`、`er121:575`/`er026:1995`)が、7+5の最悪ケースを下回らないか確認してください。

### 必須修正(M)
- **M-1** `pick_backfill`の取り数を`plan.quota_phrase`/`plan.quota_word`にする(`bf:135`)。
- **M-2** `candidates:369`の除外tupleを`NOT_COUNTED_STAGES`参照に統一し、`overflow_kind`を含める。
- **M-3** フレーズ補完は`run_vocab_selection`を一般化した1回callの経路で行う(`max_items`引数化)。er105の再選定ループは使わず、`work/`のmetadataも書かない。
- **M-4** 既存単語を含む補完フレーズは、補完フレーズの方を落とす。最終docの不変条件testを追加する。
- **M-5** `make_p7_selector_fn`を新設し、test harness(`er119_test_support_01.py:198-199`)を先頭一致で振り分ける形に改修(想定外はfail-closed)。
- **M-6** er106のKPFT-1/3/4を、docの`prompt_id`ごとの期待値に切り替える(`:805,:813,:816`)。
- **M-7** 補完を並列にするなら、submitごとに`contextvars.copy_context()`を取る。これをしないと、`er125:59`の救済文脈が別threadで失われ、選定段の救済が黙って無効になります。あわせて次を定義すること。
  - 片方の種類だけ失敗した時の扱い(推奨: 成功した種類は採用し、`prompts[kind].status`に失敗を記録)
  - futureで発生したSTOP・routing違反の伝播
  - これを担保できない場合は直列でもよい(理由: 共有state=contextvarsと`er005_cost_logger`のglobal `_CONTEXT`、発火も低頻度)。
- **M-8** D4の逐語1文でW5'のshaを再計算する(DESIGN §1-2の表は旧2文案のまま)。test専用importで次の2点をtestする。
  - `P7 == er124.P7_TEXT`
  - `W5'`が`er124.W5_TEXT`と補足行1行だけ違うこと
  - Production moduleはer124をimportしないこと。
- **M-9** `select_p7`でP7のshaを付けたtelemetryを1行記録する。

### 任意(R)
R-1 基本形化後の含有確認。R-2 `kp_backend` IDの据え置き。R-3 予算見積の確認。R-4 evidenceの追記。R-5 mock E2Eへの7+5注入。R-6 `count_exclusions`は`duplicate_of_top3`をEに数えるため(`bf:114`)、W5'の含有語の漏れは単語補完callになります。承認仕様どおりなので、頻度だけ監視してください。

### D1〜D6への意見
D1(R0)・D2(a)・D3(X)・D4(逐語1文)・D5(種類別。M-3の実装経路が条件)・D6(作り直さない)、すべて同意します。

### ユーザー判断に上げるべき事項
なし。

(Opusレビュー原文ここまで)

## 実施事項

1. `DESIGN_02.md`(DESIGN_01へM-1〜M-9・R-2〜R-6反映、M-7=直列、R-1=既知の限界として記録、W5' sha再計算、Trial-02のP7方式[ループなし]とProduction[er105ループ維持]の差を明記)。
2. 実装(IMPL_PLAN_01+DESIGN_02どおり): `er119_kp_p7w5_prompts_01.py`(P7/W5'本文・sha定数・`make_p7_selector_fn`、er124非import)、er105引数化(件数検査/shortfall/metadata/exclusion note文言、`reason_ja`はキー存在時のみ)、`select_p7`+telemetry(M-9)、W5' call2、`not_single_word` Gate(validate→not_single_word→duplicate_of_top3)、`KP_CANDIDATE_MAX`→12(KCP2A merge後に1行)、種類別cap(`overflow_kind`、NOT_COUNTED_STAGES統一=M-2)、補完(quota=M-1、種類別P7/W5'を`run_vocab_selection`一般化1回call=M-3、直列、`backfill_duplicate`=M-4、`BACKFILL_MAX_CALL_ITEMS`撤去)、harness(M-5)、er106(M-6)、mock E2Eへ7+5 generator注入(R-5)、Y/Z予算見積確認(R-3、不足なら`STAGE_EST_JPY`の根拠付き更新)。`REMOVAL_RESULT_01.md`(撤去: `BACKFILL_MAX_CALL_ITEMS`・単一cap room計算・「3件」固定文言。残存Grep 0)。
3. test: sha pin(P7==er124.P7_TEXT、W5'はW5と補足1行差、Production非import)、最終doc不変条件(フレーズ≤7・単語≤5・単語⊄フレーズ)、補完quota/発動条件/不発動(上限未満のみ)/FAILED続行/backfill_duplicate、not_single_word、er105既定値でPrompt 2経路バイト同一(golden)、er106 prompt_id別、isolation test、既存`er119_kp_backfill_test_01.py` 55件・`er119_*`・`er105_*`・X/Y/Z runner mock E2E。既存失敗(OPEN-543)は本件起因でないことを切り分け。
4. evidence(有料、上限¥60): 6経路fresh(X 2記事×Std/Adv相当・Y 1記事・Z melos。既存run dirをコピーした専用dir `er119_output/p7w5_evidence_01/<family>_<level>/`でKP stageのみ実行、公開済み/進行中runへは触れない)。記録: actual model_id/routing/prompt_id+sha/入出力/Gate結果/補完・救済記録/`call1_attempts`/`outer_attempts`/P7が1語を返した件数/`overflow_kind`/`not_single_word`/理由40字超件数(記録のみ)/最終doc不変条件/費用・時間の現行比増分(usage log)。自然発火(Gate除外→補完・救済)が出なければ「未観測」と記録し、replay(`tools/replay_backfill_01.py`流用)で機構確認を補う。Family別にまとめ、`EVIDENCE_01.md`に実候補例(6経路の最終候補全文=フレーズ/単語・日本語訳・理由)を載せる。
5. Opus台帳記録、`IMPLEMENTATION_01.md`、`COST_01.md`。

## 事前指定Read一覧

- `docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{DESIGN_01,IMPL_PLAN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,CURRENT_PIPELINE_01}.md`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{DESIGN_02,DATA_CONTRACT_01,EVIDENCE_01}.md`+`tools/replay_backfill_01.py`
- `er119_kp_candidates_01.py`、`er119_kp_backfill_01.py`、`er105_kp_fulltext_selector_01.py`(Grep `MAX_ATTEMPTS|max_items|shortfall|prompt_sha256|build_exclusion_note` ±10)、`er119_kp_prompt_2v_01.py`(`run_vocab_selection|SELECTOR_2V_MAX_ITEMS` ±10)、`er124_kp_phrase_word_trial_01.py:62-129`、`er119_test_support_01.py:180-220`、`er106_joint_runtime_evidence_01.py:795-820`、`er003_v1_n3_01_scaffold_generate.py:350-370`、`er125_kp_rescue_production_01.py:50-70`、`er121_family_y_runner_01.py:570-580`、`er026_family_z_fiction_production_runner_01.py:1990-2000,2785-2800`

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_DELEGATION_02.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er119_*test*.py"`、`--pattern "er105_*test*.py"`、`--pattern "er106_*test*.py"`、`--pattern "er030_*x_production_wiring*test*.py"`、`--pattern "er121_family_y_*test*.py"`、`--pattern "er026_*test*.py"`
- 有料run前: `py tools/stop_scope_check_01.py --managed-id KP-PHRASE7-WORD5-PRODUCTION-01 --run-dir <run> --out <run>/audit/stop_scope_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

`CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS`編集権なし。`RESULT_PACKET_KP75B.md`にOPEN-534更新文案(APPROVED_FOR_PRODUCTION→IMPLEMENTED+EVIDENCE_COLLECTED、PRODUCTION_WIRED判定はFable)、CURRENT_SPEC候補生成節の改訂文案(Prompt P7/W5' sha、12件、種類別補完)、DECISION_LOG文案、フォーム側引継ぎ(export `cap`既定8→12、docstring)。

## Git

- 実装commit: `KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: KP候補生成をP7(フレーズ最大7)+W5'(単語最大5・5条件・KP含有語除外)へ配線、候補上限12・種類別補完quota・not_single_word Gate・Opus M-1〜M-9反映+test(API 0)`。evidence commit: `KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: 6経路runtime evidence(X/Y/Z×Std/Adv、実費¥NN)`。trailer: `Delegation: KP-PHRASE7-WORD5-PRODUCTION-01/02`。push。wav/raw_usage_log/STOP/lockは不追跡。

## 報告

`docs/pm/RESULT_PACKET_KP75B.md`: (0)T-0、(1)DESIGN_02変更点(M/R対応表)、(2)実装差分(ファイル:行)、(3)test結果、(4)evidence要約(6経路Status表=適用確認/Gate/補完/救済/未観測、実候補例、費用・時間増分)、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案・フォーム側引継ぎ、commit hash・raw URL。末尾10行要約。