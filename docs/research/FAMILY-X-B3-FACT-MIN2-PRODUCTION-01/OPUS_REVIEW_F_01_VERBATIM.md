## Opus独立技術レビュー_F(条件A)FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 — 読み取り専用

### 総合判定: GO_WITH_CHANGES

方向性は案I(Prompt 1か所変更+module内で再評価1回+STOP)で妥当です。ただし案IIIの二重ガード(producer`_check_inputs`の変更+契約V5の変更)は、置き場所と数え方に問題があります。**修正版「案I+runner合流点ガード」**を推奨します。

**必須修正(M1〜M6)**
- **M1** 再評価では、`topic`の範囲内でStorylineを見直してよいことにする。4テストは全Factへ再適用する(論点1)。
- **M2** 下流ガードはproducer/契約に入れず、runnerのL420直前に置く。契約V5の`K<2`化はやめる(論点3)。
- **M3** 下限の数え方を1つの定義に統一する。数えるのは`[VERIFIED]`のIDのみ。再評価を起動する条件も「採用IDのうちVERIFIEDが2件未満」とする(論点2)。
- **M4** 再評価で2件以上になった場合は、Storyline・fact_tests・ID・Briefをすべて再評価callの出力1回分で置き換える。初回出力と混ぜない。STOP記録の古いものが残って誤読されないよう、取り扱いを決める(論点4)。
- **M5** Regressionに3点を追加する。(a) 4テストの結果と採用判定の矛盾を機械的に検出して記録する (b) producerの`rules_sha256`が変わらないことのassert (c) Trial側の非影響確認(論点5)。
- **M6** 再生成計画に2点を追加する。(a) STOP時に古い成果物(F11のみの版)を使わない手順 (b) 採用Factが記事で使われたかを、既存の`r0_with_tags.md`で機械的に突合する(論点6)。

---

### 論点1 再評価の定義
- **結論**: Storylineを固定したまま再評価すると、meyではほぼ確実に再びF11のみになりSTOPします。`topic`の範囲内でStorylineを見直してよい形にするべきです。4テストの文言は変えずに済みます。
- **根拠**:
  - mey台帳(`run_mey_01/research_ledger/verified_fact_ledger.txt`)は11件中10件が`OBSERVED_REPORTED`です。因果を含むFactはF11(`CAUSAL_STATED_BY_SOURCE`、L83)だけです。
  - Test2・Test3(`er019_family_x_storyline_b3_fact_selection_01.py:40-41`)は「因果」と「なぜ」を問います。そのため、F11を中心にしたStorylineでは、他のFactは「F11が引用済み」「背景のみ」として除外されます。設計書§2では10件すべてがTest2=NO・Test3=NOでした。
  - 原因はテストの文言ではなく、Storylineが1件のFactに集約されたことです。StorylineをF02〜F05・F07・F08(空港・施設への攻撃)とF11(特使の評価)の因果としてまとめ直せば、F04などはTest2=YESになりうる構造です。
  - ユーザー原文§2の「中心テーマに関連するFactを再評価」は、Storylineの固定を求めていません。
- **必須修正(M1)**: 再評価noteに次の4点を明記してください。
  1. 初回は検証済みFactが1件以下だったこと。`【テーマ】`の範囲内で、Storylineを見直してよいこと。テーマから外れるStorylineは不可であること。
  2. 4テストは見直したStorylineに対して全Factへ改めて適用し、採用判定はテストの回答と整合させること。テストの回答を変えずに採用判定だけ変えることを禁止すること。
  3. 数合わせのために、関連性の低いFactや`[AMBIGUOUS]`を検証済みとして扱わないこと。2件に届かない場合は、各Factのreasonにその理由を書くこと。
  4. 初回のStorylineと採用IDは参考として示してよい。ただし理由の引き継ぎはしないこと。

  JSON schemaは変更しないでください。不足理由のために新しいフィールドを作る必要はなく、各Factのreasonで足ります。
- **任意改善**: L70-71の差し替え文に「`[VERIFIED]`から最低2件(`[AMBIGUOUS]`は採用可だが2件に数えない)」と書き、LLMに数え方を伝えると、再評価の頻度が下がります。`DEVELOPER_MESSAGE`の「最小限」は変更不要です。下限との矛盾は、L70-71の変更で十分に解消できます。

### 論点2 「検証済み」の算入
- **結論**: VERIFIEDだけを数え、AMBIGUOUSは採用できるが数えない、という扱いは妥当です。台帳のVERIFIEDが2件未満ならAPIを呼ぶ前にSTOPする点も妥当です。AMBIGUOUSの扱い(採用可、producerが限定文を付ける)は変わらないので、ユーザー原文「AMBIGUOUS取扱いを維持」と整合します。
- **根拠**:
  - producerはAMBIGUOUSに固定の限定文を付けます(`er053_b3_deterministic_producer_01.py:11,64,83`)。
  - b3 module側のID抽出(`er019_family_x_storyline_b3_fact_selection_01.py:129`)はVERIFIEDとAMBIGUOUSを区別しません。
- **必須修正(M3)**: 数え方の定義を1つにしてください。b3 moduleとrunnerガードの両方で、producerの`parse_ledger`(`ambiguous`フラグ付き、L77-83)を使うか、同じ正規表現を使うことをテストで固定します。再評価の起動条件は「採用総数が2件未満」ではなく「採用IDのうちVERIFIEDが2件未満」とします。例えばVERIFIED 1件+AMBIGUOUS 1件の場合も再評価を起動します。
- **任意改善**: この保守的な解釈をDECISION_LOGに記録しておいてください。ユーザー判断は不要です(原文「検証済みFactから」の文言どおり)。

### 論点3 全経路評価の完全性と案III
- **結論**: 二重ガードは必要です。ただし案IIIの置き場所(producer`_check_inputs`と契約V5)は、影響範囲が広すぎるうえ数え方もずれています。runnerのL420直前に1か所置けば、すべての経路を漏れなく評価でき、影響もX Productionに限られます。
- **根拠**:
  - runnerのL409-420では、`stage`が`storyline_b3`/`writer`/`advanced`/`standard`/`all`のどれでも`need_storyline`がTrueになります。初回・regenerate・resume・再利用のすべてがL420の`run_annotation_producer`を通ってからWriterへ進みます。Writer再利用(U-1、L431-435)もこの後段です。したがってL420直前の1か所で全経路を評価できます。
  - `produce_annotated_b3`は、RLCT Trial(`er082_rlct_trial_01_lib.py`)、MAQ Trial(`er052_output/.../maq_driver_01.py`・`maq_driver_02.py`)、`er053_dev_b3_fixture_adapter_01.py`からも呼ばれています。`_check_inputs`に下限を入れると、混入禁止としているRLCTなどにも波及します。
  - 契約V5(`er053_b3_annotation_contract_01.py:233`)が数えるのはFact行の数です。1行が1 ID(producer L659)なので件数は一致しますが、V5はVERIFIEDとAMBIGUOUSを区別できません。新しい定義と数え方が食い違います。
  - `validate_annotated_b3`もRLCT・MAQ・テストから呼ばれています。
  - なお`_check_inputs`は`_PORTED_NAMES`(L681-692)に含まれないため、変更しても`rules_sha256`は変わりません。設計書§3-0-6の「要確認」はこれで解決です。
- **必須修正(M2)**:
  - (g)と(h)をやめ、代わりにrunnerへ`assert_b3_min_verified(out_dir)`を新設して、L420の直前で呼んでください。中身は、`fact_selection_evidence.json`の`selected_fact_ids`と台帳のVERIFIED判定を照合し、2件未満なら`B3MinFactsStop`にします。API呼出は0、「`--regenerate-stage storyline_b3`で再選定してください」と案内します。
  - これで設計書(f)は不要になります。
  - 下限を判定する根拠は、evidenceにある`selected_fact_ids`だけにしてください。`min2_policy`キーの有無は判定に使いません。既存の3件以上のrunを不要に止めないためです(ユーザー§3「2件採用の既存正常例は不要に変更しない」)。
  - producer・契約・`rules_sha256`・K=1のfixture・RLCT・MAQは変更しません。
- **任意改善**: b3 moduleの`run_storyline_b3_selection`は引数`min_verified_selected=2`(既定ON)で強制してください。Production側の安全を優先する既定です。
  - `er036`(Y Trial、L141)は無変更のままで、下限を引き継ぎます。Prompt本文は共通なので、どちらにせよYにも波及します。
  - Y Trialで旧挙動が必要になった場合は、そのTrial側で`None`を渡します。
  - この波及はOPEN-420に記録してください。

### 論点4 失敗終了時の成果物
- **結論**: 新しい不完全な成果物は残りません。ただし、前回版(F11のみ)のbrief・evidence・注記済みB3・`ja_writer`は、そのまま「最新」の場所に残ります。誤って使われるのを防ぐのは、M2のガードです。案Iの(f)がなく、(g)も別の場所に置くなら、このガードは必須です。
- **根拠**:
  - `run_storyline_b3`(runner L147-190)は、選定が成功した後にだけファイルを書きます。モジュール内でSTOPすると何も書かず、L420にも到達しません。そのため、producerが古い注記を消す処理(producer L848)も動きません。
  - 設計書§4の退避はcopyなので、元の場所に旧版が残ります。
- **必須修正(M4)**:
  - (a) 再評価で2件以上になった場合は、5点すべてを再評価callの出力1回分で置き換えてください。初回のStorylineと再評価のIDが混ざると、producerのStoryline一致検査(L732)で止まりますが、STOPの理由が分かりにくくなります。
  - (b) STOP記録`b3_min2_stop_record.json`は、次の3つの場合すべてで書いてください。
    - 台帳のVERIFIEDが2件未満で、API呼出前にSTOPした場合
    - 再評価後も2件未満だった場合
    - 再評価callが技術的に不正だった場合
  - (c) 後のrunで成功した場合は、既存のSTOP記録を削除するか、`superseded`として退避してください。古いSTOP記録が残って誤読されるのを防ぎます。
  - U-1のPROVENANCE_MISMATCHとの関係では、新しく追加する経路はありません。STOP後にWriterを再利用しようとすると、先にM2のガードで止まります。
- **任意改善**: STOP時に、現在の場所にある前回の注記artifact 4ファイルを消すと、producerと同じfail-closedの考え方に揃います。安全性はM2で確保済みなので必須ではありません。

### 論点5 Regression設計(§3-6)
- **結論**: ①②③⑤⑥と経路テストは、モックで決定論的に検証できます。④「数合わせ禁止」は現案だと「コードがIDを追加しないこと」しか検証できず、不十分です。
- **根拠**: 現在のvalidator(`er019_family_x_storyline_b3_fact_selection_01.py:155-184`)は、4テストの回答と採用判定の整合を見ていません。
- **必須修正(M5)**:
  - (a) 4テストの回答がすべて除外を指している(Test1=YES・Test2=NO・Test3=NO・Test4=YES)のに採用されたFactを、soft warning `SELECTED_DESPITE_ALL_TESTS_EXCLUDE`としてevidenceに記録してください。retryやSTOPには使いません。④のテストは、このパターンのモック応答で、警告が出ることと記録されることを確認します。meyではFableの受入評価に使えます。
  - (b) 再評価Promptについて、次をassertしてください。
    - 禁止文、`topic`、Storyline見直し可の文言が入っていること
    - `fact_test_definitions_sha256`と`developer_message_sha256`が変わらないこと
    - 再評価noteのshaを新たに固定すること
  - (c) ちょうど2件(VERIFIED)の場合と3件以上の場合に、再評価が0回であることを確認してください。callは1回、`parsed`は入力と完全に一致します。
  - (d) VERIFIED 1件+AMBIGUOUS 1件の場合に、再評価が起動することを確認してください。
  - (e) `rules_sha256`が変更前の値と同じであることをassertしてください。
  - (f) runnerで次の2点を確認してください。
    - regenerate中にSTOPした場合、`selected_brief.md`とevidenceのmtimeが変わらず、producerが呼ばれないこと
    - 旧版(F11のみ)が残った状態で`--stage writer`を実行すると、M2のガードでSTOPしAPI callが0であること
  - (g) `er036`がimportでき、新しい既定値で動くこと(モック)を確認してください。
- **任意改善**: (a)を「採用数に数えない」というhardな扱いにすると、新しい品質基準に近づきます。採るならユーザー判断が必要です。既定はsoft warningのままを推奨します。

### 論点6 中東記事の再生成計画(§4)
- **結論**: 計画はおおむね妥当です。次の不足を補ってください。
- **必須修正(M6)**:
  - (a) 手順1でSTOPした場合は、現在の場所にある旧版(F11のみの記事)を、提示物や比較の「新版」として使わないでください。報告にもそのことを明記します。
  - (b) 採用Factが本文で使われたかは、既存の仕組みで機械的に突合できます。W-1のR0 Promptは、文ごとに`【事実N】`を付けるよう求めています(`er053_family_x_factlock_ja_writer_01.py:70-73`)。タグ付きの原稿が`ja_writer/factlock/r0_with_tags.md`として保存されています(L375。mey既存版にも存在)。
    - タグ番号Nを`selected_brief_annotated`のsidecarの`facts[n].ledger_ids`でFact IDに対応づけ、採用Factごとにタグの出現数を数えます。読み取り専用の集計で、Gateは新設しません。
    - R1/R2で表現が落ちていないかは、2つの方法で確認します。1つはsidecarのcore数値が`revision2.md`に残っているかの照合、もう1つは既存の手動突合です。
  - (c) 実行後に次の4点を確認してください。
    - `annotation_producer_evidence.json`の`n_facts`が2以上であること
    - `rules_sha256`が前回と同じであること
    - W-1のevidenceの`annotated_md_sha256`が新しいmanifestと一致すること
    - `entry_point.json`の`b3_module_sha256`が新しいコードの値であること(配線のruntime evidence)
  - (d) ユーザー§4「攻撃主体が未確認の場合は断定しない」の確認項目を追加してください。台帳ではF02・F03・F05〜F08が主体未特定で、主体の帰属はF09・F10のみです。本文にある「フーシ派」などの主体表記が、F09とF10の帰属だけに限られているかをGrepと手動で突合します。
- **任意改善**:
  - `--theme`は現行値(`entry_point.json`のargs)のまま変えないことを推奨します。条件を揃えるためです。ユーザー§4の中心テーマは、受入評価の基準として使います。
  - B3の再評価callの前に予算チェックはありませんが、80〜130の範囲なら実害はありません。W-1と同じ`budget_check`の受け口を付けるかどうかはFableに委ねます。

---

### ユーザー判断が必要な事項
**なし**(上記の修正はすべて、ユーザー原文§2・§3の承認範囲内です)。
- 参考: 論点5の任意改善(矛盾するFactを採用数に数えない、というhardな扱い)を採る場合だけ、ユーザー判断が必要になります。既定どおりsoft warningなら不要です。

### 最小変更原則に照らした推奨案
**修正版「案I+runner合流点ガード」**を推奨します。
- 変更するもの:
  - Prompt L70-71
  - b3 moduleの再評価1回+STOP(引数で既定ON)
  - runner(STOP記録、L420直前のVERIFIED≥2ガード)
  - テスト
- 変更しないもの: producer・契約V5・`rules_sha256`・`er036`・RLCT・MAQ
- 案IIIより変更範囲が狭く、resume・再利用・regenerate・手動差替えのすべてをL420の1か所で評価できます。案IIは仕様と矛盾が残るため不可です。

関連ファイル:
- C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py
- C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py
- C:\Users\tensh\eigo-radio\er053_b3_deterministic_producer_01.py
- C:\Users\tensh\eigo-radio\er053_b3_annotation_contract_01.py
- C:\Users\tensh\eigo-radio\er053_family_x_factlock_ja_writer_01.py
- C:\Users\tensh\eigo-radio\er036_family_y_voice_structure_trial_01.py
- C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\research_ledger\verified_fact_ledger.txt
- C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\ja_writer\factlock\r0_with_tags.md