FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14(Part 1「Vocabulary & Expressions」案α Production Wiring 実装: Opus条件A反映→実装→test→runtime evidence→SSOT。訳欄はユーザー判断待ちのため描画を止める)。あなたはsonnet-worker。Fable(PM)からの委任。

## 0. 前提
- ユーザー決定: 案α=APPROVED_FOR_PRODUCTION(原文`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`)。目標PRODUCTION_WIRED(受入条件1〜9)。「Part 1正式採用は新しい未承認仕様の包括承認ではない」。
- Phase 0成果(委任_13、commit 0d8fe4cd6): `PART1_WIRING_{SPEC_CHECK,DESIGN,OPUS_REVIEW_REQUEST}_01.md`、`part1_wiring_tests_draft_01.py`。OPEN-512、UDR #197(T1/T2=引用英文の日本語訳の生成元、**ユーザー判断待ち**)。
- Opus条件Aレビュー結果=「条件付きで実装へ進んでよい(実装前に必須M1〜M4を設計書へ追記・修正、実装時必須1〜10)」(§1に逐語。`PART1_WIRING_OPUS_REVIEW_01.md`として逐語保存、見出し「# PART1_WIRING_OPUS_REVIEW_01(条件A、2026-10-25、opus-consultant、read-only・API 0)」)。同内容の再レビューは不要(Fable照合済み)。
- Fable判断: (1)M1〜M4を設計書に反映してから実装。(2)**M3は(ii)を採用**: 訳欄(`source_sentence_ja`)はnull+`PENDING_USER_DECISION`で生成・保存まで行い、**ページ描画はT1/T2のユーザー判断が出るまで止める**(描画コードは実装し、`study_text_render_enabled`等のrun-time条件=「訳欄の判断記録が存在する」で有効化。環境変数やflagで既定ONにしない。判断前に公開ページへstudy blockを出さない)。(3)E2E発火証拠はZ=複製runで`--stage kp`、X=複製sourceでscaffold 1回(Opus推奨、主経路の実runtime確認、数円・自律範囲内)+`--stage study_text`。(4)Xのユーザー向け公開ページ(per-article script)への組込みは、同一module経路で最小の追加で実現できるなら本委任で実施。できなければX=`WIRED_EXCEPT_USER_PAGE`として理由と見積を報告(PRODUCTION_WIREDと呼ばない)。
- 費用: E2E発火証拠≈0.3〜0.4円+X scaffold 1回(数円)。本委任上限10円。日次1,000円内(起動前に当日JST累計を確認)。有料は`.venv\Scripts\python.exe`、無料は`py`。
- 並行agent: FX-CORE-NUMERIC(er115 DEV+docs、間もなくProduction配線委任が始まる可能性: `er019_family_x_storyline_b3_*`/`er053_*`/Writer系を編集。**あなたはX側では`er019_family_x_audio_production_runner_01.py`のKP/scaffold/stage部分と`er019_family_x_kp_explanation_01.py`のみ、B3/Writer系は触らない**)/ Family Y音声化(er110 Trial)/ Z Chunk(DEV)/ 告げ口心臓確認(docs)。SSOT編集は直前再Read・最小Edit・衝突時再適用。Production fileの編集前に`git status`で他agentの未commit差分を確認し、同一ファイルに他者差分があれば一時index方式でcommit。

## 1. Opus条件Aレビュー(逐語保存用)
---
## 判定: 条件付きで実装へ進んでよい(条件は下の必須4件)

設計の大枠は妥当です。新しい共通module、KP確定後・TTS前に置く単独段、入力は英語表現のみ、再生成キーは表現と順序、失敗時は技術retry 1回のあとfail-closed、Validatorは新設しない、という構成です。差し戻しは不要です。ただし下の「実装前に必須」4件は、設計書(PART1_WIRING_DESIGN_01)への追記・修正として実装委任より前に固めてください。同じ内容での再レビューは不要です。Fableの照合で足ります。

---

### 実装前に必須(設計修正)

**M1. Xの失敗状態とmarkerを、KP失敗から分ける(論点c/d)**
- 現設計は、Part 1の失敗を既存の`kp_stage_status`に`KP_PART1_FAILED`として載せ、rc=3にします。
- 既存の停止メッセージは「同stageを再実行」と案内します(`er019_family_x_audio_production_runner_01.py:2715`)。scaffoldを再実行すると、support生成とKP選定がやり直しになります(:436-444)。その結果、費用が発生し、別のKPに変わります。
- `--scaffold-only kp`は「1レベル1回」の制約で止まります(:429-433)。
- KP失敗markerは「旧attemptのKP」という意味で使われ、KPが成功したときに削除されます(:452-453, 2731-2734)。Part 1の失敗にこのmarkerを流用すると意味が混ざります。
- 修正案:
  - 専用のstatus/marker(例: `kp_part1_failed.json`)を設ける。
  - rc=3のメッセージで`--stage study_text`を案内する。
  - `--stage study_text`が成功したらmarkerを削除する。
  - `study_text`の実行前に、KP PASS・KP失敗markerなし・HR以外の前提を確認する。

**M2. Part 1を使う側で、存在と最新性をfail-closedで確認する(論点b/d)**
- 現設計の生成点はZ=`stage_kp`、X=scaffoldの各1箇所だけです。TTSやpagesだけを単独で起動する経路に穴があります。
  - Zの`--stage tts_b1b`は`load_level_inputs`を通りますが(`er026_family_z_fiction_production_runner_01.py:1781-1817`)、Part 1は確認されません。
  - `--stage pages`は`build_pages`を直接呼びます(:1897-1900)。
  - Xの`--stage tts`/`player`も同様です(:2730-2779)。
- そのため、次のことが起こり得ます。
  - Part 1導入前に始まった進行中runを再開すると、Part 1なしで音声が作られる。
  - `--regenerate-stage kp_b1b`のあとに`kp_part1_b1b`を再生成し忘れると、古い解説が表示される。
- 修正案:
  - Z: `load_level_inputs`(b1b)と`stage_pages`の組立時に、`kp_general_explanations.json`があること、`phrases_signature(現在のKP)`と保存済みsignatureが一致すること、を確認する。不一致はSTOPし、`--regenerate-stage kp_part1_b1b`を案内する。
  - X: tts/assemble/playerの入口で同じ確認をする(既存marker確認:2731の隣)。
- これで「TTS前で止める」が全経路で成り立ちます。

**M3. 訳(T1/T2)が未決のまま、「訳なし表示」をProductionの既定にしない(論点h)**
- 設計は項目1・2・3・5を先行して配線し、訳はNone許容にします(DESIGN §11)。
- このままページ表示まで有効にすると、以後のProduction記事は事実上T2(訳欄なし)の構成で公開されます。これは「未承認の新仕様を暗黙に採用しない」(`USER_05.md:52-54`)に抵触します。
- 修正案(どちらか):
  - (i) T1/T2の判断を今すぐ並列でユーザーに求める(判断は軽い)。
  - (ii) 判断が出るまでは生成・保存(study_text JSON/MDに`source_sentence_ja: null`と`PENDING_USER_DECISION`を明記)だけを行い、ページへの描画を止める。
- 推奨は(i)と(ii)の併用です。

**M4. 入力の抜け道を塞ぐ: display_phraseへのfallbackを禁止する(論点a)**
- `explanation_phrase()`は、`fulltext_source_ref`が無いか`used_form`が空のとき、本文の表層形である`display_phrase`を返します(`er019_family_x_kp_explanation_01.py:149-151`)。
- 旧strategy_lのKPを再利用した場合(Zでもその可能性が記録されています、runner:1737)、本文由来の語形がそのまま解説LLMへ渡ります。
- 修正案: `generate_for_kp_items`と`phrases_signature`では、全itemに`fulltext_source_ref`と空でない`used_form`を必須とし、欠ければ課金前にSTOPする。`explanation_phrase`をそのまま使わず、Part 1専用の厳格版を用意する。

---

### 実装時に必須

1. **見出しの照合を正規化する(論点a/c)。** Trial-04の実際の出力6件のうち2件は見出しが括弧付きでした(`_raw_04a_r1_p1_open_window.txt:1`の`### 1. (give way)`、`_raw_04a_r2_p1_gift.txt:1`)。曲がったアポストロフィ(`moment’s`)も出ています。原因はPromptの書式例`### 1. (英語表現)`(`run_trial_04.py:70`)です。
   - 括弧・`**`・引用符・曲がったアポストロフィを除去・統一し、大文字小文字と空白を正規化してから照合する。
   - 表示する見出しはLLMの見出しではなく、入力の`used_form`を使う。
   - これをしないと約1/3のcallでretryが起き、retry後の失敗でSTOPが多発します。
   - 「日本語を含み一定長以上」の閾値は、6件の実出力で較正する。
2. **リーク検査の範囲を、Promptの可変部(列挙部)だけにする。**
   - 固定のHEAD/BODYには日本語(「意味」「場面」「用法」等、`run_trial_04.py:46-73`)が含まれます。短いglossがこれと偶然一致すると、誤STOPになります。
   - 「長さ≥表現長+4」の条件をglossに当てると、glossはほぼ常に短いため検査が実質無効になります。基準として一貫していません。
   - 推奨: Prompt == HEAD+列挙+BODYの決定論再構成であることをassertし、可変部にCJKが無いことを確認する。そのうえで、itemの文字列値(`gloss_alignment`配下のような入れ子も含めて汎用に収集)が可変部に含まれないことを確認する。
3. **`validate_phrases`の許可文字を実データで較正する。** 既存の全`keywords_canonicalized.json`の`used_form`を集計し、`/`・`()`・`,`・数字を含む正当なKPが誤STOPしないことを確認する。拒否条件は「CJK・改行・制御文字・長さ超過」を中心にする方が安全です。
4. **ページ部品の構造を決める(論点f)。**
   - `check_page`は、kp表以外で`td`が3個以上ある`tr`を、スクリプト行として数えます(`er_user_listening_page_common_01.py:178-191`)。
   - h2は節の境界になります(:151-157)。
   - したがってstudy blockには`<table>`と`<h2>`を使わず、`<h3>`と`<div>`/`<dl>`で作る。
   - LLM出力はHTMLエスケープしてから描画する。Trial出力は全件で`**`太字を使っているため、その扱い(除去か`<b>`化)も決める。
   - Zのlintはページ全文に`英語:|日本語:|EN:|JA:|English:|(B1)|B1B`の禁止パターンをかけます(`er063_family_z_audio_01.py:1800,2056-2059`、`page_verify:56-58`)。ラベル文言をこれに当たらない形にする。
   - 加えて、生成時に同じ正規表現を解説文へ適用し、構造失敗としてretry対象にする。これで、TTS後のpages段で初めて落ちる事態を防げます。新しい品質判定ではなく、既存ページ規則を前倒しで適用するものです。
5. **routing関連のtestを更新する(論点e)。**
   - `er054_family_z_story_pool_trial_02_test_01.py:31-50`の`LATER_APPROVED_PRODUCTION_KEYS`へ追加しないと「想定外のkey追加」でFAILします。
   - `er053_cost_aggregate_01_test_01.py:92-99`はgit HEADとの差分で判定するため、commit前の作業ツリーではFAILします。実行順序に注意してください。
   - 費用計算で`cost_jpy_for_call`を使う場合は、`er009_..._open251_test.py:11`の`TABLE_PATH_PROCESSES`へ追加する。
6. **mock modeの扱いとcost記録。**
   - Zのmock/dry-runでhookが無いときは、実APIを呼ばずにSTOPする(`_person_repair_factory`と同じ型、runner:1569-1574)。
   - 有料callは既存のcost logger経由で記録し、runのbudget guardと日次集計に必ず載せる。
7. **signatureの細部。**
   - X/Zともrank昇順に並べてから計算する。
   - Zの`input_sha`には`PROMPT_TEMPLATE_SHA256`とmodelも含める(本文・glossは含めない設計意図はそのまま。Prompt変更時に古い解説を再利用しないため)。
   - ensure_stageのentry fieldsへauditの要約(model・prompt_sha・cost)を載せる。
8. **逐語照合は既存の正規化を再利用する。** 新しい照合ロジックを作らず、Zは`canonical_article_text`とSRC D1(`er026_family_z_src_posthoc_01`)の基準に合わせる。照合元の正規化が食い違うと、誤STOPになります。
9. **STOPメッセージに次の一手を書く。** Zで表現が変わったとき、まず`kp_expl_b1b`が止まり、再生成後に`kp_part1_b1b`が止まる、という2段の再起動が生じます。各メッセージに次のコマンドを明記する。
10. **E2E前の事前確認(論点g)。**
    - コピーしたZ runで`--stage kp`を実行すると、`kp_part1_b1b`より前の`kp_expl_b1b`(sigにgloss/SRCを含む、runner:1751-1761)がProvenanceMismatchで止まり、Part 1まで届かない可能性があります。
    - 人称関所(:1664-1672)が修復のための有料callとartifact書換を起こす可能性もあります。
    - 対象runは、この2点がreuse・CLEANになることを事前に確認して選ぶ。

---

### 推奨(任意)

- DEPENDENTSに`kp_b1b→kp_part1_b1b`を**追加しない**判断は正しいです。追加するとKP再生成のたびにstale化し、表現が同じでも明示的な再生成が必要になります。表現のみをキーにする設計意図と矛盾します(`er062_family_z_writer_01.py:64-67,666-675,699-701`)。Z=明示的再生成/X=自動という差も、既存の`kp_expl`と同型なので許容してよいです(Z `ensure_stage`:690-720、X `_resolve_kp_explanations_text`:1069-1098)。
- glossの更新・HR解決では再生成しない、という設計は妥当です。解説の入力は表現だけで、glossは描画時に現在値を読むためです。
- Xの発火証拠について。`--stage study_text`だけでは、正規の主経路(`run_theme_scaffold`内)が実runtimeで一度も通りません。複製sourceでscaffoldを1回実行すると、数円・自律範囲内で主経路を確認できます。受入条件4の「正式runtime」を強めるなら、これを推奨します。実施するかはFableの判断です。最初の新規Production記事を、追補の発火証拠として記録することも推奨します。
- 標準適合checkへ「study blockは任意・存在時は整形式」の項目を足すことは任意です。実装時必須4の構造を守れば、既存のC2/C3/C4は壊れません。
- `kp_expl`との並列化は不要です。+11〜13.5秒はTTS全体に比べて小さいためです。費用0.0775円/set(70円比約0.11%)は見合います。Luna(=`SUPPORT_MODEL`)の使用も、Trialとの同一性・最新モデル原則と整合します。
- X/Zの主要な実行経路は網羅されています(Regen、Local Rewrite、HR、外側retry、`--regenerate-stage`、resume)。これ以外の見落としは、上記M2(単独stage起動)と旧KPの再利用(M4)です。

---

### 論点別の結論

- **(a) 入力隔離:** 多層化の方針は妥当です。M4と実装時必須1〜3で修正が必要です。残るリスクは、`used_form`自体が文脈語を含む場合(例 `bound to the protein`、`_raw_04a_r1_p1_ig_nobel.txt:4`)です。これはKP仕様の側の問題なので、本配線の範囲外として明示しておけばよいです。
- **(b) 再生成制御:** キーは表現と順序で十分です(Prompt sha+modelを追加)。M2が必須です。DEPENDENTSは追加しません。
- **(c) retry/fallback:** 「技術retry 1回→fail-closed→TTS前STOP」は、`generate_kp_explanations`(:258-289)・KPMP-03・「安全≠成功」と整合します。KPの外側retryの後に置く判断も、非blockingにしない判断も妥当です。新しい既定動作には当たりません。Xの状態の扱いはM1で修正が必要です。
- **(d) 一貫性・配線点:** 配線点は許容です。tts段の前提確認はM2として必須です。Advanced限定は妥当です(Trial-04はAdvancedのみ)。ただしユーザー報告で「Advancedのみ表示」と明記してください。
- **(e) Dangling Reference:** 置換・撤去対象0とした調査を否定する材料は見つかりませんでした(本レビューでの再Grepはrouting関連testのみ)。`kp_expl`(英語の短い定義、音声用)との並存は、見出し「Vocabulary & Expressions」と「解説」の表記で区別できます。routingのtest影響は実装時必須5のとおりです。
- **(f)(h) 表示と訳:** 実装時必須4とM3のとおりです。訳の技術整理は下の「ユーザー判断事項」に記載します。
- **(g) E2E計画:** 費用約0.3〜0.4円は妥当です。実公開ページの更新を切り離す判断も妥当です。実装時必須10と、推奨のX主経路の発火確認を加えてください。

### CURRENT_SPEC記載案(要旨)

「Family X/Z 学習テキスト Vocabulary & Expressions(Advancedのみ)」節として、次を記載する。

- 案αを採用し、入力は確定KPの`used_form`だけとする。本文・gloss・引用文は送らない。
- 生成はKP確定後・TTS前に1 call(`KEY_PHRASE_GENERAL_EXPLANATION`=gpt-6-luna、Trial-04 Promptとバイト一致)で行う。
- 再生成キーは表現・順序・Prompt sha・model。Zは不一致でSTOPし明示的に再生成、Xは自動再生成。
- 使う側(TTS・pages・player)で存在と最新性を確認し、不一致はSTOPする。
- 技術retry 1回→fail-closed。fallbackも空欄での続行もしない。
- 表示は、確定KP/本文中の意味(描画時の現在値、HR未解決ならSTOP)/本文引用英文(逐語照合)/訳(T1/T2の判断に従う)/解説。
- 費用は約0.08円/set、時間は+約11〜14秒。

---

### ユーザー判断が必要な事項(T1/T2以外)

新しい独立事項は「なし」です。ただし、T1/T2の判断パッケージに次の2点を含めることを推奨します。

1. **T1の訳callにglossを参照として渡すか。** 渡さない場合、訳の中のKP部分の日本語が項目2(本文中の意味)とずれて並ぶリスクがあります。渡しても、案αの隔離対象は解説LLMなので抵触しません。
2. **T1の品質根拠。** 単独の訳call方式は未Trialです。Trial-03/04の訳は03d由来で、本文全体を見る別のcallで作られています。新しい訳callの訳の意味整合を担保する既存検査はありません(構造検査のみ)。「直接採用して初回記事を目視」か「小Trial(数円)を挟む」かを選んでもらう。
   - T1の技術面: 入力は引用英文と前後1文(Zは`source_sentence_id`/SRC D1の文分割を再利用し、Xは文分割を新設)。キャッシュキーはsha(文と前後文、Prompt sha、model)。失敗はfail-closed。+約0.03円で、並列なら+0秒。
   - T2の技術面: 訳欄を出さない。実装は簡単ですが、ユーザーが指定した出力構成(`USER_05.md:49`)を満たさないため、構成変更の承認が必要です。
- 補足(Fableの判断事項): Xのユーザー向け公開ページはper-article scriptで、本配線の範囲外です。「全条件を満たしたFamilyのみPRODUCTION_WIRED」(`USER_05.md:70`)に照らすと、Xはユーザー向けページへの組込みが済むまでPRODUCTION_WIREDと呼ばないのが安全です。
---

## 2. 作業
### Step 1 設計修正(API 0、commit)
- `PART1_WIRING_DESIGN_01.md`へM1〜M4と実装時必須1〜10、M3(ii)の描画停止条件、X公開ページ組込みの扱い、CURRENT_SPEC記載案を追記(§番号を振る)。

### Step 2 実装(Production)
- 新module `er003_kp_general_explanation_01.py`: 厳格入力(`fulltext_source_ref`必須・空でない`used_form`、`display_phrase` fallback禁止=M4)、`validate_phrases`(実データ較正=必須3)、Prompt=Trial-04案αとバイト一致(HEAD+列挙+BODYの決定論再構成assert、可変部CJKなし+item文字列の非含有=必須2)、routing `KEY_PHRASE_GENERAL_EXPLANATION`(routing表1行+test更新=必須5)、見出し正規化照合と表示見出し=used_form(必須1)、Zページlint正規表現の前倒し適用(必須4)、技術retry 1回→fail-closed、audit(model/prompt_sha/input_sha/response_ids/cost/retry/reuse)、cost logger経由(必須6)、signature=rank昇順の表現+順序+PROMPT_TEMPLATE_SHA256+model(必須7)、出力JSON/MDに`source_sentence_ja: null`+`translation_status: PENDING_USER_DECISION`。
- Z: `stage_kp`の`kp_expl_b1b`直後に`kp_part1_b1b`(ensure_stage、entry fieldsにaudit要約)、`load_level_inputs`(b1b)と`stage_pages`で存在・signature一致をfail-closed確認(M2)、STOPメッセージに次コマンド(必須9)、mock/dry-runでhook無しはSTOP(必須6)、`build_pages`へstudy block(`<h3>`+`<div>/<dl>`、HTMLエスケープ、`**`は`<b>`化、禁止ラベル回避=必須4)。**描画は「訳欄の判断記録ファイル(例: `docs/pm/decisions/part1_translation_decision.json`等、実装で場所を定義)が存在し`T1`または`T2`を示す」ときのみ有効**。それまでは描画しない(生成・保存のみ)。
- X: `run_theme_scaffold`のb1b KP PASS後に呼出、`--stage study_text`、専用marker `kp_part1_failed.json`とrc=3メッセージ(M1)、tts/assemble/player入口での存在・signature確認(M2)、X自動再生成(表現変化時)。X公開ページ(per-article)組込み: 同一経路で最小追加が可能なら実装(描画条件はZと同じ)、不可なら`WIRED_EXCEPT_USER_PAGE`として見積を報告。
- 逐語照合は既存正規化(Z: `canonical_article_text`/SRC D1、X: 既存のKP alignmentの基準)を再利用(必須8)。
- test: `part1_wiring_tests_draft_01.py`を正式test file(例: `er003_kp_general_explanation_01_test_01.py`+runner統合test)へ移し、B/C/D全件PASS。DefaultOff相当の確認=「判断記録なし→描画なし」のtest。回帰: `run_project_regression.py`+pytest群(他agent起因は分類し、clean worktreeで再現確認)。

### Step 3 runtime evidence(有料、上限10円)
- 事前確認(必須10): Z複製runで`kp_expl_b1b`がreuse・人称関所CLEANになるrunを選ぶ。
- Z: 複製runへ`--stage kp`→`kp_part1_b1b`が1 call発火。X: 複製sourceでscaffold 1回(主経路発火)+`--stage study_text`。
- `PART1_WIRING_EVIDENCE_01.md`: actual model_id、prompt sha、input sha、routing、費用、retry/reuse、出力(解説全文)、M2の確認が効くこと(signature不一致時STOPのtest証跡)、描画停止の確認(判断記録なしでページにstudy blockが出ない)。
- 実公開ページは更新しない。

### Step 4 SSOT・Git
- CURRENT_SPECへ新節(Opus記載案に基づく。訳欄は「T1/T2判断待ち、描画停止中」と明記)、OPEN-512更新(X/Z別Status: Z=`WIRED_PENDING_FABLE`(描画停止中)、X=同または`WIRED_EXCEPT_USER_PAGE`)、DECISION_LOG 1件、UDR #197に「M3(ii)採用・描画停止中」追記。ADOPTION_NOTE_04 §1/§4追記。
- `docs/pm/RESULT_PACKET_FZST14.md`、ACTIVE_TASK自行。委任文逐語保存: `--index 534`で`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_14.md`(冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14」で照合、不一致なら±5)。
- Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`→`git push origin HEAD:main`。Production実装+testは1 commit(revert単位)、設計修正・evidence・SSOTは別commit。secret grep 0件。

## 3. STOP条件
上限10円超過見込み / 既存test・Gateを迂回しないと実装できない / 新しい既定動作が必要 / 他agentと同一Production fileで解決できない衝突。

## 4. 報告(Fableへ)
(1)M1〜M4・実装時必須1〜10の反映対応表 (2)X/Z別のStatus候補と受入条件1〜9の充足表(描画停止中の扱いを明記) (3)runtime evidence要約(モデル・Prompt sha・routing・費用・解説全文の所在) (4)test/回帰結果(他agent起因の分類とclean再現) (5)量産単価・処理時間の実測 (6)X公開ページ組込みの結果または見積 (7)変更ファイル・commit・raw URL (8)RESULT_PACKET 4行+「判定整合」1行。