# recon_vocab_level_production_wiring_01.md

管理ID: NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01(Sonnet Phase 0事前調査、
2026-09-26、¥0、read-only)。コード・Prompt・SSOTは一切変更していない
(全項目read-only grep/read確認のみ)。

## §1 Standard正式Production path

- **Prompt定数の所在**: `er003_v1_n3_01_standard_a2_generate.py`
  L100-127 `STANDARD_A2_PROMPT_V5`(user template)+L94-98
  `STANDARD_A2_DEVELOPER`(developer message)。
  `STANDARD_A2_PROMPT_SHA256 = "ff860ab60a0d1d4ffa4e93a30e53af37fe87afa8c4e01a99bf54e06897a42353"`
  (L145)。import時に`_assert_prompt_sha256()`(L159-169)でfail-closed
  検証。
- **現行v5文言の要旨(逐語冒頭のみ抜粋)**: 「Prefer words within roughly
  the 6,000 most common English words. If a word is clearly outside that
  range, replace it when a simpler natural alternative exists. Do not
  force a replacement if it makes the sentence less natural or changes
  the meaning. Proper names are excluded from this rule. Essential
  technical terms may remain when a simpler equivalent would lose
  important meaning.」(L106-110)。**この文言は「prefer/推奨」であり、
  今回ユーザーが承認した「firm 6,000語Band+3除外条件のみ(固有名詞/
  推測容易な派生語・複合語/日本語定着語)」とは一致しない**(現行は
  "roughly"表現でBandの強度が弱く、除外条件も3分類化されていない)。
  文構造再構築指示(平均9-11語/文、1文1アイデア、長節分割、L100-105)・
  Fact/Story保持指示(L114-120)は今回のユーザー決定と矛盾しない
  (「Simplify the English, not the story」の思想を維持)。
- **呼び出し元(単一Production path、複数呼び出し元なし)**:
  `er012_e_family_entertainment_two_level_runner_01.py`
  L59 `import ... as std_gen`、L320/L328
  `std_gen.generate_standard_a2(advanced_text, client=client)`
  (`run_writer_stage()`内、初回+deviation MAJOR時1回retryの両方が
  同一関数呼び出し)。`er019_family_x_entertainment_production_runner_01.py`
  L46 `import er012_e_family_entertainment_two_level_runner_01 as efam`、
  L359 `efam.run_writer_stage(..., only="standard")`。**Family A daily
  news(`er003_v1_n3_01_articles_generate.py`ほか、Hanshin/Health等)は
  Standard A2生成を持たない別系統**(通常NewsはA2/B1直接生成、
  Entertainment英語適応版のような「Advanced→Standard」変換工程が無い)。
  `er012_b_family_production_runner_01.py`(B-Family Voices)、
  `er013_family_c_production_runner_01.py`もStandard A2 v5 importなし
  (Grep確認、`STANDARD_A2_PROMPT_V5`/`generate_standard_a2`の参照は
  `er003_v1_n3_01_standard_a2_generate.py`本体+そのtestファイル+
  `er012_e_family_entertainment_two_level_runner_01.py`+関連ADR/Trial
  ドキュメントのみ)。**結論: Prompt定数は一元管理されており、初回・
  構造retry・deviation再生成・`--regenerate-stage standard`のいずれも
  同一`STANDARD_A2_PROMPT_V5`/`build_prompt()`を参照する。**
- **retry/fallback**: `vfl01.run_writer_with_technical_retry()`(構造Gate
  付き、###見出しちょうど2つ要求)。Advanced段と同一primitive
  (`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01` D4)。fallbackモデルは
  `PROCESS_MODEL_MAP`に定義なし(既存どおり)。Ledger deviation check
  (`vfl01.run_deviation_check`)MAJOR時は1回retry→なお失敗ならSTOP
  (本文を手で直さない)。
- **Local Rewrite(er020系)との関係**: 別層。er020はTTS音声生成段の
  ASR不一致回復機構(`connected_speech_enabled_for()`/
  `run_local_rewrite_recovery()`、`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-
  PRODUCTION-WIRING-01`)であり、本文生成(Standard/Advanced Writer)とは
  独立工程。Standard v5本文の語彙表現自体をer020が書き換えることはない。
- **Trial版Prompt文言との差分(統合案の材料)**:
  - `er015_standard_a2_6000_generation_first_trial_01.py`のBは、
    「generation-first」という強め表現の実験だったが、
    `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01_REPORT.md` §9 Fable評価
    により「語彙Bandの強度を上げても構文が変わらなければ体感難易度は
    下がらない」と結論され、**単独では採用candidateではない**。
  - `er015_vocab_band_6000_10000_14000_trial_01.py`の
    `PROMPT_TEMPLATE_VB`(3条件のみ: (1)固有名詞 (2)推測容易な派生語・
    複合語 (3)日本語として定着している語。例示語は
    wastewater/surprisingly/piano/curtain/Meta/Muse/Reutersのみ)。
    このTrialは**構文再構築指示を含んでいない**(語彙Bandのみの単独
    Prompt、既存v5とは別テンプレート)。Trial結論(§10 VB-2)は「次Trial
    としてv5の文再構築指示+firm 6,000 Band+3除外条件を組み合わせた版を
    検証すべき」であり、**その組み合わせ版自体はまだどのTrialでも生成・
    検証されていない**(VB-2は未実施のまま今回ユーザーが直接
    `APPROVED_FOR_PRODUCTION`とした)。
  - **最小diff統合案**(Sonnet作業前提の下書き、実装は本Phaseでは行わない):
    現行v5 L106-110(6段落)を、(a) 「Prefer」→「firm/原則として」への
    強度変更、(b) 除外条件を3分類(固有名詞/推測容易な派生語・複合語/
    日本語定着語)へ明示的に列挙し直す、(c) 個別語例示は
    wastewater/surprisingly/piano/curtain(Meta/Muse/Reutersは記事固有の
    固有名詞例のため置換案から除外、他記事にも通用する一般例のみ採用)、
    (d) v5の文構造再構築指示(L100-105)・Fact/Story保持指示(L114-122)・
    構造保持行(L122)は無変更のまま残す、という置換で構成できる。
    `STANDARD_A2_PROMPT_SHA256`は文言変更に伴い再計算・更新が必須。

## §2 Advanced正式仕様の特定

- **所在**: `er003_v1_n3_01_advanced_adaptation_generate.py`
  L144-187 `ADVANCED_VOCAB_RULE_V2_BLOCK`、
  `ADVANCED_VOCAB_RULE_V2_SHA256 =
  "d536f4b8a7780771232a95d35611606262d8041371ad8d0a1a4563b7948fb581"`
  (L189-191)。import時`_assert_vocab_rule_v2_sha256()`(L198-205、L258)で
  fail-closed検証。
- **正式名称・Status**: `ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`
  (DECISION_LOG.md L9518-9532、2026-09-26)。Status: 「v2語彙ルール自体は
  `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(語彙ルールのbuild_prompt()
  組み込みのみ。Advanced全体Status`APPROVED_FOR_PRODUCTION / WIRING
  INCOMPLETE`[Gate 3未充足、OPEN-177]は本タスクのスコープ外のため変更
  しない)」。CURRENT_SPEC.md L829にも同内容を反映済み。
- **内容要旨**: 一般英語頻度順位約12,000位超を原則平易化候補とし、
  A(易しい語からの推測可能形態・複合語、例onstage/wastewater/
  understandable)/B(日本語定着外来語、例piano/curtain/privacy、カタカナ
  表記だけでは不足)/C(固有名詞、および記事中で引用符に入った実際の呼称=
  Fact扱い)/D(平易化すると意味精度・自然さを損なう不可欠語、「専門用語
  だから」だけでは不十分)の4例外。「idiomの一部だから」は独立例外と
  しない(L181-186)。
- **生成時ルールか完成後passか**: **生成時ルール**。`build_prompt()`
  (L261-270)内でARM3_BLOCKの直後・Production contract接尾ブロックの前に
  挿入され、単一のWriter呼び出し(`vfl01.run_writer_with_technical_retry`)
  で直接生成される(候補語リスト・順位付き改稿passなし=「方式(i)」)。
  「改稿pass追加」の方式(ii)は不採用のまま`OPEN_ITEMS.md` OPEN-182で
  継続観察待ち(実装なし)。**ユーザーが今回の指示で参照した「過去報告
  ADVANCED-VOCAB-RULE-TRIAL-01 v2系、PRODUCTION_WIRED
  [commit 7c93d146、ADVANCED_VOCAB_RULE_V2_BLOCK]」は、名称・内容とも
  上記と一致することを確認した**(コミットハッシュ`7c93d146`自体は本タスク
  でgit logから再確認していないが、`ADVANCED_VOCAB_RULE_V2_BLOCK`という
  定数名・A〜D定義・12,000閾値は現行コード・DECISION_LOGと完全一致)。
- **14,000 Band相当の記述混入なし**: Grep確認
  (`14,000|14000|Topic Core|topic_core|is_metaphor|exception_used`)、
  `er003_v1_n3_01_advanced_adaptation_generate.py`本体のコード実行部分
  (build_prompt()が返す文字列)には一切出現しない。L132のコメント
  「v3(Trial-02、Topic Core Word例外+Metaphor専用ルール)は…含まない」は
  「含まれていないことの説明コメント」であり、実行時Prompt文字列への
  混入ではない。
- **v3 REJECTED経緯**: `ADVANCED-VOCAB-RULE-TRIAL-02`(Trial-02、Topic
  Core Word例外+Metaphor専用ルール)は`ADVANCED-VOCAB-V2-PRODUCTION-
  RESTORE-01`(DECISION_LOG L9522)でユーザーにより4点の理由で明示的に
  `REJECTED`確定。Production未混入をGrepで確認済み(上記)。

## §3 Dangling Reference候補

- `er015_advanced_vocab_rule_trial_01_v2.py`は`lemma_candidates_v2`/
  `rank_of_word_v2`を定義するTrialスクリプト本体(A〜D原型の出典)。
  Production側(`er003_v1_n3_01_advanced_adaptation_generate.py`)からの
  importなし(Grep確認、Production module内に`er015_`文字列の実import無し、
  コメント内のパス文字列参照のみ)。
- `er015_vocab_abcd_strict_exception_trial_01.py`/
  `STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01`/
  `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01`(いずれも2026-09-26実施の
  未報告Trial、`PM-REPORTING-LEDGER-INITIAL-VS-RESTATE-01`
  [DECISION_LOG L9546-9555]で「初回報告未」と明記): Standardに
  Advancedと同じABCD閾値方式(6,000位版)を適用する代替案を検証した
  ものだが、**ユーザーは今回の指示で明示的に「3条件のみ」
  (NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01系)を採用しており、ABCD
  整合Trialの結果を採用したわけではない**。この2件のTrialは
  Production Prompt未変更・未報告のまま並存しており、今後Standard
  実装時にABCD方式と3条件方式を混同しないよう注意が必要(SSOT上は
  いずれも`DECISION_LOG`本体エントリが無く、`REPORT_LEDGER.md`にのみ
  「初回報告未」として存在)。
- `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01`自体も**DECISION_LOG.md
  本体にエントリが存在しない**(Grep確認、0件)。存在するのはRepo直下の
  `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01_REPORT.md`のみ。今回の
  ユーザー指示はこのTrial結果(§10 VALIDATED仮判定)を直接参照して
  `APPROVED_FOR_PRODUCTION`化しており、DECISION_LOGへの正式記録は
  Standard実装時のGate 3判定と合わせて行う必要がある(未実施事実として
  記録)。
- 「A/B/C/D」「Advanced v2」「Topic Core Word」の名称は、Production Prompt
  コード自体には(Advanced側のA〜D定義以外)出現しない。「Storytelling
  保持」原則はStandard v5(L114-120)・Advanced ARM3_BLOCK(L110-117)双方に
  文言として存在し、CURRENT_SPEC.md L829/830の正式記述とも一致する
  (dangling reference無し)。

## §4 Regression対象の特定

- **既存Production出力(入力素材として使用可能)**:
  - Standard v5 Meta: `er012_output/e_family_two_level_wiring_01/meta/a2/article.md`
  - Standard v5 Sewer(v5トライアル版): `er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/a2v5_standard_sewer.md`
  - Family X B3配線runtime evidence(2026-09-26最新、Storyline+B3経由の
    Advanced/Standard実物): `er019_output/family_x_b3_production_wiring_01/run_01/`
    (Mandatory STOPによりユーザー記事確認待ち、OPEN-183)。
  - Sewer記事は`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02-SEWER-EXCLUSION-01`
    (2026-09-25)によりProduction E2E代表記事から除外済み(元Source不在)。
    語彙検証サンプルとしての利用は可(Production代表復帰ではない)。
  - 一般News(Family A、通常News Hanshin等)はStandard A2生成物を持たない
    (§1参照、別系統のためregression対象に含まれない)。
- **難語計測に流用可能な既存関数**: `er015_advanced_vocab_rule_trial_01_v2.py`
  の`lemma_candidates_v2`/`rank_of_word_v2`(rank = min(surface, best
  lemma)、-s/-es/-ies/-ed/-ing/-lyのみの単純規則、-er/-est比較級除去は
  含まない)・`fact_tokens_check`(引用符/数字/大文字語のBefore-After
  一致確認)。いずれもTrialスクリプト内定義でProduction importなし
  (方針としては複製せず「分析専用の独立呼び出し」として都度使う運用が
  これまでの実績、`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`のruntime
  evidenceでも同様の外部wordfreq分析スクリプトを使用)。
- **Advanced側「過剰簡易化(facility→place等)」検出の既存自動チェック**:
  **存在しない**。現状はFableによる編集レビュー(定性判断)のみ
  (`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`のruntime evidenceでも
  自動的な平板化検出ロジックへの言及なし)。実装時に追加するかどうかは
  Fable/ユーザー判断が必要(本Phaseでは提案のみ、実装しない)。

## §5 runtime evidence取得計画(実装時、本Phaseでは未実施)

- **正式entry point**: `er019_family_x_entertainment_production_runner_01.py
  --stage standard`(または`--regenerate-stage standard`相当を
  `er012_e_family_entertainment_two_level_runner_01.py`側で使う場合は
  `--regenerate-stage standard`)。
- **Writer inputが正式pathから渡った証拠**: `build_prompt()`が返す文字列
  全文を`entry_point.json`または専用`prompt_used.txt`へ保存し、
  `STANDARD_A2_PROMPT_SHA256`(更新後の値)と実際に送信したuser messageの
  sha256を突合する(既存`_assert_prompt_sha256()`と同型の検証)。
- **Advanced difficulty adjustment発火状況**: `ADVANCED_VOCAB_RULE_V2_BLOCK`
  はStandard実装と無関係に既に発火中(§2)。Standard実装時の主目的は
  Standard側のみであり、Advanced側は「無変更」であることをgit diffで
  確認する(既存`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`と同じ確認方法)。
- **output/validator/retry/cost保存**: 既存`run_writer_stage()`の
  `writer_run_summary.json`(2026-09-26修正1回目でマージ保存化済み、
  `NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`)、
  `raw_usage_log.jsonl`、`cost.json`(stage別)をそのまま踏襲。
- **見込みcost**: `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01`の実測
  (6 call合計¥2.73、1 call平均¥0.4543)を参考にすると、Standard文言変更
  後の少数記事(Meta+一般News1本程度)でのruntime evidence取得は
  ¥5〜20程度と見込まれる(Advanced段のLedger deviation retryが発生した
  場合は+¥数円程度上振れ)。

## §6 テスト

- **既存test(sha256 assert、変更必要)**: `er003_v1_n3_01_standard_a2_
  generate_test_01.py`の`PromptSha256Tests`
  (`test_prompt_sha256_matches_constant`/`test_prompt_sha256_mismatch_raises`、
  L74-110)。Standard v5文言を変更する場合、`STANDARD_A2_PROMPT_SHA256`
  定数と`reconstruct_prompt_file_text()`の期待値を実装と同時に更新する
  必要がある(既存パターン`ADVANCED_VOCAB_RULE_V2_SHA256`と同型)。
- **追加すべきtest(実装時、本Phaseでは未作成)**:
  1. 新Standard文言に「firm/原則として」等の強度文言が含まれることの
     文字列アサーション。
  2. 3除外条件(固有名詞/推測容易な派生語・複合語/日本語定着語)の3文言が
     漏れなく存在し、A〜D方式のラベル(KEEP-A/KEEP-B/KEEP-C/KEEP-D等)や
     「Topic Core」「is_metaphor」等のTrial固有マーカーが**存在しない**
     ことの否定アサーション(`ADVANCED_VOCAB_RULE_V2_BLOCK`の
     `VocabRuleV2Tests`と同型、L525-526既存実装のテスト設計を流用可能)。
  3. 個別語例示がwastewater/surprisingly/piano/curtainの4語のみに限定
     されていること(Meta/Muse/Reutersのような記事固有固有名詞例が
     一般Prompt本体に混入していないこと)の確認。
  4. `STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01`/
     `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01`(ABCD方式)のマーカー文字列が
     Standard新Promptに混入していないことの確認(3条件方式との混同防止)。
  5. `er012_e_family_entertainment_two_level_runner_test_01.py`/
     `er019_family_x_b3_production_wiring_01_test_01.py`の既存regression
     一式(sha256依存箇所があれば同様に更新)。

## §7 実装計画(最小)とSTOP候補

- **最小実装案**: `STANDARD_A2_PROMPT_V5`のL106-110(6,000語ライン段落)を
  §1の統合案文言へ置換し、`STANDARD_A2_PROMPT_SHA256`を再計算・更新。
  他の段落(文構造再構築・Fact/Story保持・構造保持行)は無変更。Advanced
  (`ADVANCED_VOCAB_RULE_V2_BLOCK`)は無変更。
- **STOP候補(判断はしない、事実列挙のみ)**:
  1. `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01`自体がDECISION_LOG本体
     未記載(§3)。Standard実装のGate 3判定時に、このTrialの正式記録
     (VALIDATED仮判定→ユーザーAPPROVED_FOR_PRODUCTIONへの格上げ経緯)を
     DECISION_LOGへ追記する必要があるが、これは今回の指示範囲
     (ユーザーが既に決定を下した旨を委任文で明記)であり、追記自体は
     STOP事由ではなく実装作業の一部と考えられる(最終判断はFable)。
  2. `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01`/`NEWS-FAMILY-X-WRITER-FACT-
     SELECTION-TRIAL-02`が`REPORT_LEDGER.md`上「初回報告未」のまま
     残っている(§3)。Standard実装作業がこれらの未報告Trialの存在に
     気付かずABCD方式で実装してしまうリスクがあるため、実装着手前に
     Fable/ユーザーへ「3条件方式(採用)とABCD整合Trial(不採用)の違い」を
     再確認することを推奨する。
  3. Advanced側の「過剰簡易化検出」に既存自動チェックが無い(§4)。
     ユーザーの今回の指示は「Advancedは名称だけを前提にせず現行実装で
     足りているかを照合する」ことを求めているが、自動チェック新設は
     本指示の範囲外であり、必要なら別途判断が必要。
  4. Advanced全体・Standard全体とも`APPROVED_FOR_PRODUCTION / WIRING
     INCOMPLETE`のまま(Gate 3全項目未充足、OPEN-177)。今回のStandard
     語彙文言変更は、この既存WIRING INCOMPLETE状態そのものを解消する
     ものではない(Sewer代表記事除外・Meta a2 Human Review Lock等の
     既存未解決事項は本タスクの範囲外)。

## 参照ファイル一覧(逐語根拠)

- `er003_v1_n3_01_standard_a2_generate.py`(L94-270)
- `er003_v1_n3_01_advanced_adaptation_generate.py`(L100-270)
- `er012_e_family_entertainment_two_level_runner_01.py`(L56-59, L259-364, L641)
- `er019_family_x_entertainment_production_runner_01.py`(L36-48, L350-359)
- `DECISION_LOG.md` L9410-9592(6エントリ全文確認)
- `CURRENT_SPEC.md` L828-830
- `OPEN_ITEMS.md` L331(OPEN-182)
- `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01_REPORT.md`(全文)
- `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01_REPORT.md`(冒頭)
- `STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01_REPORT.md`(冒頭)
- `er003_v1_n3_01_standard_a2_generate_test_01.py`(L74-110)
