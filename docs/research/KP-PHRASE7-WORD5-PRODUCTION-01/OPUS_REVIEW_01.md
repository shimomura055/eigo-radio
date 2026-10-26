# OPUS_REVIEW_01: KP-PHRASE7-WORD5-PRODUCTION-01 Opus独立レビュー(条件A、実装前)
逐語保存の正本=`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_OPUS_RESULT_01.md`。本ファイルは同内容(参照用の写し)。Fable採否と反映先は`DESIGN_02.md` §0の対応表。

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
