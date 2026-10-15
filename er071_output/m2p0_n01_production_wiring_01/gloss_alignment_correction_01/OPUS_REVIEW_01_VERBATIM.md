保存者: sonnet-worker 委任_02、出典: Fable経由のopus-consultant報告、改変なし

# Opus独立技術レビュー: KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 / DESIGN_DRAFT_01(条件A、2026-10-15、read-only)

このレビューでは実装・修正を行っていない。Production採用可否も判断していない。「安全側」は依頼文の定義に従い、「学習者に届く最終成果物(KP英語+日本語gloss+音声/表示)が目的要件を満たす側、または満たさないものが完成扱いされない側」とした。

## 1. 総評

- **必要/不要**: 必要。欠陥①(「～」記号を合否条件にしていた)と欠陥②(FAILEDでも下流を素通り)はどちらも実在する。コード読解で確認済み(`er003_key_words_gloss_alignment.py:223-226,257-258`、`er003_v1_n3_01_scaffold_generate.py:802-808`、INVESTIGATION_01 5節)。工程目的・プロンプト修正方針・fallback(i)の廃止・item単位の検証という骨格は妥当。
- **推奨構造**: 「停止」は既存の`_only_segments_skip`前例(`er019…:589-598`、非OK statusを返してAudio Validation Gateにassemblyを止めさせる)と、`stage_kp`の`FamilyZE2EStop`で実装する。Human Review Lockと音声用`human_review_queue.jsonl`は流用しない。HR登録は外側retryループが確定した後の最終artifactに対して1回だけ行う。
- **最大リスク(BLOCKER)**: 草案4.2のLock流用は**fail-open(異常時に止まらず通過する)**になる。
  - 実際のA2 KP日本語のwavは`narration/meaning_{i}.wav`(iはrank順のindex)で、Lockのcanonical_textは`ja_gloss_tts`(`er019…:1259-1268`)。草案の`kp{rank}_japanese_meaning.wav`/`text=現在gloss`で記録すると、Lockのkey・text hashと一致しない。そのためLockは「新version」としてTTSを通し、OK→VALIDATED→assemble完了となる。
  - B1ではglossがKP解説LLMの入力(`er019…:898`)になっている。まだ存在しない解説テキストに対してLockをかけることは原理的にできない。
- **次点リスク**: 停止後の「HR解消→再開」の手段が無い(Family Zは再開時に選定から再実行される可能性が高く、人間が確定したglossは上書きされる)。また、新しい機械検査(追加語→日本語span対応)が慣用句的な自然なglossを誤NGにする、または直訳調への書換えを誘発するリスクを、Trial計画が測っていない。

## 2. 12観点の判定(1行ずつ)

1. 必要性: 必要。根拠はINVESTIGATION_01:29-41(FAILEDの素通り)、gloss_alignment.py:223-226(「～」ルール)。
2. より単純な構造: 単純化できる。Lock+queue+Gate+report+summaryの5点セットは過剰。単一の関所(`_generate_or_reuse_kp`の前例+`stage_kp`)+HR報告書+run summaryで足りる(er019…:589-598、er026…:1175-1178)。
3. 既存処理の利用: 方針は良い。ただし選んだ既存機構が誤っている。Lockは「wav生成後のASR結果記録」が前提で(er011:355-358 docstring「generate関数の実行完了後に必ず呼ぶ」)、queueは音声segment単位(er006:321-336)。
4. 前段情報の喪失・再探索: 一部懸念あり。追加語は`kp_adds_words_beyond_display`の算出を再利用しており良い(gloss_alignment.py:90-103)。一方、Family Zの解説はdisplay_phrase+旧/新glossを入力にし、sigにglossを含めない(er026…:1188-1196)。このためgloss確定後も解説が古いまま再利用されうる。
5. 不要なLLM処理: 追加なし(call数は不変、出力フィールド1つ増)。妥当。代替案E(独立verifier)を保留したのも妥当。
6. 非決定性: 微増。item単位retryの仕様が未定義(2回目に全件を再送するのか未解決分だけか、2回目で結果が変わった既成立itemをどう扱うか)。DESIGN_DRAFT_01:28,50。
7. Human Review: 増える方向。ただし例外対応としては正当。増加量は機械検査の誤NG率に依存し、未測定(TRIAL_PLAN_01にその型のパターンが無い。後述j)。
8. 不要なRewrite: 懸念あり。対照10件中1件で誤書換えが実測されている(DESIGN_DRAFT_01:83、`drop the fee`)。さらに語ごとのspan要求は、慣用的なglossを直訳調へ書き換える圧力になる(承認規則19行「直訳調…は避けて」に反する方向)。
9. コスト: 問題なし。追加出力は対象item(全体の0.6〜1.4%)に限られ、1記事セットあたり恒久増は概ね0.01円未満のオーダー(推定、T1で実測)。
10. retry/fallback/regenerationとの整合: 不整合あり。再整合は外側Redundancy retryループの内側(scaffold:715-733)にある。草案7節はHR登録を`run_key_phrase_canonicalization`内に置いており、外側retryで選定し直した場合に、存在しなくなったKPのHR/Lockが孤児として残る。
11. Failure時に安全側へ倒れるか: 設計意図は安全側。ただし実装方式(Lock)がfail-openで、B1の解説経路は未停止。現状のままでは安全側にならない(BLOCKER)。
12. 再発防止: 部分的。「消費側が状態を参照する」という構造化は再発防止になる。ただし同型の抜け道(INVESTIGATION_01 7節a: Family XのNG_REVIEW_REQUIRED素通り)を同じ関所で塞げるのに、対象外にしている。

## 3. 追加観点(a)〜(k)

**(a) 正常系・異常系の最終成果物**
- 正常系: 最終KP+再整合gloss(または不変)→TTS→Gate→完成。要件を満たす。残るリスクは、span自体は存在するが意味が誤る誤PASS(LLM依存)と、整合済みglossの誤書換え(実測1/10)。
- 異常系(草案どおり実装した場合の実際の挙動):
  - A2: Lockのkey/textが一致しないためLockは発動しない。TTS段で`STOPPED_…` statusを記録する実装も別途必要で、それが無ければ、旧glossを読み上げた`meaning_i.wav`がVALIDATEDになりassembleされる。成果物=不整合のまま完成。要件違反。
  - B1: glossが解説LLMへ流れ、解説音声が生成される。表示(page)にも旧glossが出る(`er019…:1890`、display_gloss:994)。
  - Z: `stage_kp`で停止するので成果物は無い(要件を満たす)。
- 推奨構造での異常系: 当該levelのKP segmentは`STOPPED_GLOSS_ALIGNMENT_FAILED`を返して0 API callとなり、B1の解説生成もしない。Gateが`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`を出し、完成物は無い。HR報告書・run summary・stdoutで報告される。
- MUST: 異常系の成果物を実データで1例観測する(T3を拡張)。

**(b) 承認済み仕様との整合**
- 3.3の課題指示文: 「スロット語に限り許可」は削除済みで、承認規則との矛盾は解消している。
- 残る緊張は「すべての語」「過不足なく」と承認規則17/19行「短く自然」「直訳調を避ける」の間。指示3(各追加語に対応するspanを切り出す)は、慣用的な訳(例: 句全体を1語で訳す)を禁止する意図ではないことを1文で明記するべき(SHOULD)。例:「複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません」。
- 判定例2行: どちらも`based on`系。モデルが「～をもとにした」型へ寄る偏りは小さいと見る。ただし例1(`based on`)は追加語なしで再整合対象にならないため、例としての情報価値は「～可」のシグナルだけ。偏りの懸念はT1で、例と無関係な語彙での出力を見れば足りる(MAY)。
- 承認規則15行(数値の穴埋めを要する句・gloss「ソロ旅行を～％とする」は選ばない)に対し、TRIAL_PLAN_01 P3は`put solo travel at`を「正当な辞書的『～』」として扱っており、承認規則と矛盾している(MAJOR、OF-KGDC-07)。census 28/29「正当」の推定にも同型が含まれていないか、再確認が必要。
- 選定/canonicalization Prompt・Rule7・Gateには触れていない。整合している。

**(c) 既存機構との整合**
- Lock: 流用不可(MUST)。理由は4点。
  1. 前提(生成後の記録、attempts_logの集計)と合わない(er011:355-386)。
  2. key/textの不一致でfail-open(meaning_{i}.wav / `ja_gloss_tts`)。
  3. `attempt_history.jsonl`へ`action=PROCEED, human_review_reached=True`が追記され、HR統計とtelemetryを汚染する(er011:450-468)。
  4. 人間が「現glossで良い」と判断した場合の解除(`approve_regenerate`)と、artifact側の`FAILED`という二重の状態源ができる。
- queue: 流用は非推奨(SHOULD NOT)。`human_review_queue.jsonl`はリポジトリ共通の単一ファイル(er006:321)で、参照元は33ファイル(state guard、census、HRページ生成`tools/build_family_z_hr_review_page.py`等)。消費側でsteps無しentryを許容するかの確認は「build_review 1本」では済まない。音声を持たない種別のentryを混ぜると、既存のHR集計やstate guardの比較を壊すおそれがある。
- Gate: 新status文字列で確実にblockされる(assemble.py:111-134で非許可statusはUNVALIDATED、482/495でblocked)。ただし`tts_generation_results.json`が無い場合はGateが即return(assemble.py:472-473、既存のfail-open)。TTS段を飛ばしてassembleする経路が存在しないことをT3で確認する(MUST)。
- FamilyZE2EStop: 整合する。外側retryとM2 fallbackは、HR登録を外側ループ確定後に置けば整合する(MUST、OF-KGDC-04)。

**(d) E2E整合**
- HR解消の手段が無いと詰む(MUST)。
  - Family X: artifactの`FAILED`が残る限り、関所が永久にTTSを拒否する。
  - Family Z: `stage_kp`の例外はrunner内で送出されるため、`ensure_stage`に結果が保存されず、再開時に選定から再実行される可能性が高い(`w62.ensure_stage`は未精読のため推定)。そうなると人間の確定glossはsrc→dstの上書き(er026…:1150-1158)でも失われる。また再選定は事実上「案B」になる。
  - 最小手段: `resolve_gloss(kp_json_path, rank, gloss, resolved_by)`の小関数1つ。glossと`japanese_gloss_tts`を書き、`gloss_alignment_status="HUMAN_RESOLVED"`と記録者・時刻を残す。ZではsrcとZの段結果の両方を対象にする。あわせて「HR解消後の再開は選定を再実行しない」ことをT3で検証する。
- Zの解説(kp_expl_b1b)はsigにglossを含まないため、gloss確定後も旧glossを入力にした解説が再利用される(er026…:1188)。sigにglossを含めるか、HR解消時に`regenerate_stage=kp_expl_b1b`を必須手順にする(SHOULD)。

**(e) 新しい機械検査(追加内容語→日本語span)**
- 必要性: 同じLLMの自己申告を構造化したもの(span実在の検査は幻覚検出にのみ独立性がある)。効果は主に「LLMに追加語を必ず意識させる」ことで、捕捉力は「LLM自身が対応を見つけられない」場合に限られる。意味が誤ったspan(prices→コーヒー豆)は通る。
- 誤NGの経路:
  1. 1:1対応を要求している(草案3.1「1:1か」)ため、慣用句・複合語(raw-bean→「生豆」を1span、bring in a human helper→「人の手を借りる」)が不一致になる。
  2. 機能語(around、in等の前置詞・不変化詞)が追加語に入る(`_TOKEN_RE`は冠詞のみ除外、gloss_alignment.py:97-102)。
  3. 表記ゆれ(全角/半角、～/〜、活用形でspanを書いた場合)、英語語の綴り(' / ')。
  4. 日本語での主語・目的語の省略(close around me→自然な訳で「私」を省く)。
- 最小形(MUSTとして提案。Production追加はユーザー承認事項):
  - mappingは多対一・重複を許可し、`english_word`に句も可とする。
  - 機能語(前置詞・不変化詞・助動詞・代名詞の一般化)は必須対象から外す。
  - 比較はNFKC正規化と空白除去の後の部分文字列一致とする。
  - 判定は「必須の内容語すべてが、記号以外のspanにどれかの対応で覆われている」こと。
- 新しい品質条件として、Trial中は「gateとして判定する場合」と「記録のみの場合」の両方を集計し、gateが追加で何件捕捉し何件誤NGを出したかを、ユーザーの採否判断材料にする。

**(f) Q/D/量産C**
- 出力増分: 1対象itemあたり数十トークン程度(推定)。reasoning tokenの方が支配的なので、1 batchあたり+数%〜十数%(推定、未測定)。対象は全item中0.6〜1.4%なので、1記事セットあたりの恒久増は0.01円未満のオーダーで、70円・1〜2円基準のいずれにも影響しないと見る(T1で実測確定)。
- HR到達率: 対象記事率(約7%)×2回失敗率。現行の観測は0/16。新しい機械検査の誤NG率次第で、これが支配的になる。Q/Dへの影響(ユーザーの時間)の方がCより大きい。T1で「1回目のINVALID率」と「2回とも失敗した率」をitem単位で報告させる(MUST)。

**(g) 撤去対象の列挙漏れ**
草案7節に載っているもの: `SLOT_TOKENS`/`kp_has_slot_word`/`gloss_has_unjustified_slot`/fallback(i)/`revert_to_candidate_allowed`。漏れていると見るもの:
- `GLOSS_ALIGNMENT_FALLBACK_MODE`と定数群(gloss_alignment.py:42-45)、`apply_alignment`の`fallback_mode`引数
- モジュール冒頭コメント20-22行(OF-227(i)の説明)と46行
- `build_gloss_alignment_fallback_record`のnote「人間確認Queueへは送らない」(:397)
- `apply_alignment` docstring(:323-329)
- `write_failed_notice`の出力先(key_phrases/配下)とファイル名の扱い
- テスト(`er003_test_key_words_gloss_alignment.py`の該当12箇所。特に不整合出力をassertする`test_failed_alignment_keeps_kp_flags_failed_not_human_review`と「～」禁止を固定するtest)
- 参照スクリプト(`er071_gloss_alignment_01_replay.py`/`_census.py`/`_correction_01_offline_audit.py`。これらは証跡なので、改修ではなく旧版固定のまま保存し、import破綻を避ける注記が必要)
- SSOT・台帳側のOF-227/228/230の文言、OPEN-356の運用文言

(SHOULD: 撤去対象をGrepで再列挙した一覧を実装委任文に含める)

**(h) 停止粒度**
- Family Xでitem単位の保留は技術的に可能。ただしHR解決策の一つが「KP再生成」(5件全体と相互重複判定が変わる)なので、当該levelのKP segment全体(5 rank)を保留し、本文・support・他levelは継続するのが、無駄TTSと複雑度のバランスとして良い(SHOULD)。
- B1では解説LLMの生成も同じ粒度で止める(MUST)。
- Zのstage停止は既存前例に合致し妥当。ただしb1bで停止するとa2も止まる(ループ順、er026…:1166)。独立工程を止めることにはなるが、KP段は安価なので許容範囲。

**(i) 案Bの技術的得失(判断はユーザー)**
- 得: HR到達率が下がる。既存ループ(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)の再利用なので新機構が無い。
- 失:
  - 問題のない他4件のKPまで入れ替わる(観点8、不要なRewrite)。
  - 同じ記事・同じPromptなので同一句が再選定されやすく、同じ失敗を繰り返しうる(実効性は未測定)。
  - 再選定とcanonicalizationの費用が増える。
- 方針Cとの関係: 「再整合2回失敗→HR」を文字どおり読めば、HRの前に再選定を挟むのは文言と異なる。「再整合段の2回」とは別の上位retryと解釈することは技術的には可能だが、その解釈を採るかはユーザーの判断。
- 注記: Zの現行再開挙動は事実上、案Bを暗黙に実行する可能性がある((d)参照)。

**(j) TRIAL_PLAN_01の十分性**
- 有効な点: O1(対象外itemの差分0・呼出0)は決定論的で、非劣化の強い証拠になる。T3の(a)〜(m)は網羅的。
- 不足しているパターン:
  1. 追加語を持つ拡張KPで、自然な慣用的glossが正解のもの(機械検査の誤NGと直訳化の測定。P3は追加語が空になり機械検査を素通りするので、この検証にならない)。
  2. ハイフン複合語、多語→1span、機能語の追加(bring in、close around)。
  3. 表記ゆれ・活用形のspan。
  4. 承認規則15行違反の`put solo travel at`をP3から外し、規則違反の検出側(期待NG)へ移す。
  5. T3への追加: 外側redundancy retry後にHR孤児が残らないこと/`tts_generation_results.json`欠落時のGate/HR解消→再開で選定を再実行しないこと/B1解説が生成されないこと/page・playerにFAILED glossが出ないこと/HR統計(attempt_history・queue)を汚染しないこと。
- 件数の根拠(パターン×2rep)は情報価値の観点で妥当。ただし0/20の95%上限が約14%であることは、量産判断に十分ではない。量産判断は決定論部分(O1/O3/T3)と、誤NG・HR率の点推定+上限の併記で行う、と明記する(SHOULD)。
- 合否基準: VALIDATED条件に「機械検査の誤NG 0(慣用句パターン)」と「直訳化の目視評価」を追加する(SHOULD)。

**(k) 既定ONのリスクと既定OFF化**
- INVESTIGATION_01 8節は「S3 既定OFF化が必要」とするが、技術的には条件付きで異論がある。
  - OFFにすると再整合前の挙動に戻る。過去実測では対象itemの6/8が不整合のまま無検出で通過しており、これは定義上「安全側」ではない。
  - 現行ONでは、欠陥①②があっても成功経路は16/16整合で、失敗時は旧glossに戻る(=OFFと同等)。つまりitem単位ではON≧OFFの品質になる。
- 量産を再開する前の技術的推奨:
  - (1) 量産runの運用凍結をFable側で明示的に管理する。
  - (2) 実装中・Trial中は、環境変数ではなく`align_glosses(enabled=True)`をTrial runnerから明示的に渡す(import時評価のenvに依存しない)。
  - (3) 既定値は、新設計のfail-closed(停止)部分が入るまでは現行ONのまま、または量産そのものを止める。OFF化は「承認境界」上は安全だが「品質」上は後退する、とユーザーに得失を並べて提示する。
- 採否はユーザー。

## 4. 所見一覧

- **OF-KGDC-01 / BLOCKER**: Human Review Lockの流用がfail-openになる。
  - 内容: 草案4.2のLock流用はfail-openで、TTS停止として機能しない。
  - 根拠: KP日本語wavは`narration/meaning_{i}.wav`、canonical_textは`ja_gloss_tts`(er019…:1259-1268)。Lockはパス由来のkeyとtext hashが一致しないと「新version」としてproceedする(er011:327-331)。`record_outcome`は生成後の記録が前提(er011:355-386)。
  - 推奨: Lockを使わない。`_generate_or_reuse_kp`の`_only_segments_skip`前例と同型で、itemの`gloss_alignment_status in {FAILED}`なら`{"status":"STOPPED_GLOSS_ALIGNMENT_FAILED"}`を返す(0 API call)。Gateは無変更でblockする。
  - 採用時に生じ得るFailure: 関所を経由しない別のTTS呼出元(他Familyや旧runner)で素通りが起きる。呼出元をGrepで全数確認すること。
- **OF-KGDC-02 / BLOCKER**: B1の解説経路が止まらない。
  - 内容: B1ではglossが英語解説LLMの入力とページ表示に流れ、草案の停止範囲(TTS)では止まらない。
  - 根拠: er019…:898,994,1890。Zはer026…:1194-1196。
  - 推奨: 解説生成の入力を組み立てる箇所でもFAILED itemを除外し、解説segmentを非OK statusにする。page/player生成がGateの後にしか実行されないことを確認する。
  - 採用時に生じ得るFailure: 解説が欠けたlevelの構造完全性チェック(`_check_structural_completeness`)が別の理由でblockし、停止理由が分かりにくくなる。statusにreasonを必ず載せること。
- **OF-KGDC-03 / MAJOR**: HR解消後に再開する手段が無い。
  - 内容: Family Xはartifactの`FAILED`が永久にblockし、Zは再開時に選定から再実行して人間確定値を失う可能性がある。
  - 根拠: 草案8節3は未決。er026…:1150-1182(install_kp_assetsの上書き、runner内の例外)。
  - 推奨: `HUMAN_RESOLVED`を書く小関数1つ+手順書。Zでは段結果の保存先と再開経路をT3(l)で実証する。Zの解説sigにglossを含める。
  - 採用時に生じ得るFailure: 人手で書いたglossが承認規則(括弧・算用数字・…)に違反する。resolve関数内で既存の記号チェックを再利用すること。
- **OF-KGDC-04 / MAJOR**: HR登録の位置が外側retryと矛盾する。
  - 内容: HR登録(report/summary)を`run_key_phrase_canonicalization`内で行うと、外側redundancy/記号QAのretryで捨てられたattemptのHRが孤児として残る。
  - 根拠: scaffold:715-733(canonicalization内)、:812以降のループ。草案7節。
  - 推奨: HR報告とeventの生成は`run_key_phrases`の戻り(最終artifact)に対して1回だけ行う。
  - 採用時に生じ得るFailure: 途中attemptのFAILED履歴が失われる。attempts_detailは監査用に残すこと。
- **OF-KGDC-05 / MAJOR**: 音声用HR queueへの非音声entry混入。
  - 内容: `human_review_queue.jsonl`は全体共通の音声segment用ファイルで、参照元が33ファイルある。非音声entryの混入は既存のHR集計やstate guardに影響しうる。
  - 根拠: er006:321-336、Grepの結果。
  - 推奨: queueへは載せない。「届いた」の5条件を、①HR報告書のスキーマ再読検証、②run summaryのevent、③最終stdout行と非ゼロ終了またはSTOP status、④下流停止のmock実証、の4条件に置き換える。
  - 採用時に生じ得るFailure: 既存HRページで一覧化されず見落とされる。PM報告の必須項目(run summaryのevent)で担保すること。
- **OF-KGDC-06 / MAJOR**: 新しい機械検査の誤NG・直訳化を誘発する仕様。
  - 内容: 1:1対応、機能語の算入、正規化なし、という仕様が慣用的な自然なglossの誤NGと直訳化(承認規則19行と逆方向)を誘発する。
  - 根拠: 草案3.1「1:1か」、gloss_alignment.py:97-102。
  - 推奨: (e)の最小形(多対一・重複可、機能語除外、NFKC比較)。gateと記録のみの両方で集計する。Production追加はユーザー承認とする。
  - 採用時に生じ得るFailure: 判定が緩くなり、欠落の一部を見逃す(誤PASS)。T1のP1/P4で検出率を確認すること。
- **OF-KGDC-07 / MAJOR**: Trialのラベルが承認規則と矛盾。
  - 内容: TRIAL_PLAN_01 P3が`put solo travel at`(承認規則15行で禁止されている「～％」型)を正当な対照として扱っている。
  - 根拠: b1_p2…template.txt:15、TRIAL_PLAN_01:26。
  - 推奨: P3から外し、期待NGのケースへ移す。census 28/29の推定ラベルを再点検する。
  - 採用時に生じ得るFailure: 対照の数が減り、統計上の上限がさらに広がる。代わりに辞書的な「～」の正当例を追加すること。
- **OF-KGDC-08 / MAJOR**: Trialに慣用句パターンが無い。
  - 内容: 「追加語あり×自然な慣用的訳が正解」のパターンが無く、機械検査の誤NGとHR到達率を量産判断できない。
  - 根拠: TRIAL_PLAN_01:21-30(P3は追加語なし)。
  - 推奨: P7(5〜6件×2rep、約0.3円)を追加。「1回目のINVALID率」と「2回とも失敗した率」をitem単位で報告する。
  - 採用時に生じ得るFailure: Trial費用が微増する(JPY5の上限内)。
- **OF-KGDC-09 / MINOR**: item単位retryの仕様が未定義。
  - 内容: 2回目の入力が未解決itemのみか、既成立itemの結果をどちらで採用するかが決まっていない。
  - 根拠: 草案2節:28、3.2:50。
  - 推奨: 2回目は未解決itemのみで`build_user_message`を再構築し、各itemは最初の有効出力を採用する。
  - 採用時に生じ得るFailure: 1 batchが2 callに分かれ、費用がわずかに増える(上限は不変)。
- **OF-KGDC-10 / MINOR**: 「真なら不変」の厳密比較が表記差でもINVALIDになる。
  - 内容: `current_gloss_consistent=true`でgloss==currentの厳密比較を行うと、空白や～/〜の表記差でもINVALIDになり、HRへ進む。
  - 推奨: NFKCと空白除去の後に比較する。真の場合は、比較で一致を確認したうえで、採用値は常にcurrent(元の文字列)にする。
  - 採用時に生じ得るFailure: 正規化で同一とみなした実質的な書換えを見逃す。正規化の範囲を空白と～/〜に限定すること。
- **OF-KGDC-11 / MINOR**: 同型の抜け道を同じ関所で塞いでいない。
  - 内容: Family Xの`NG_REVIEW_REQUIRED`素通り(INVESTIGATION_01 7節a)を、今回の関所(runnerのKP後チェック)で同時に塞げるのに対象外にしている。
  - 推奨: 別OPENとして起票し、実装は同じ委任内で行うのが効率的。ただし別仕様なので、承認を分けて扱う。
  - 採用時に生じ得るFailure: 既存のFamily X runで、これまで黙って通っていた記事が停止するようになる。
- **OF-KGDC-12 / MINOR**: 既定OFF化の判定が品質面の後退を考慮していない。
  - 内容: INVESTIGATION 8節の「S3 既定OFF化が必要」は、品質面での後退(OFFでは対象itemの6/8が不整合のまま無検出)を考慮していない。
  - 推奨: (k)のとおり得失を並べてユーザーに提示する。Trialは`enabled=True`を明示的に渡す。
  - 採用時に生じ得るFailure: OFFを採らない場合、承認前の仕様が量産経路で動き続ける。運用凍結の明示管理が必須。

## 5. 代替案

**案A'(推奨。Aを修正したもの)**:
- Aの「Lock+queue」を外し、停止は次の3箇所で行う。
  - (1) Family Xの`_generate_or_reuse_kp`と解説入力の組み立て箇所で、`_only_segments_skip`と同型の非OK statusを返す。
  - (2) Zの`stage_kp`で既存の`FamilyZE2EStop`を送出する。
  - (3) runner側では、KP段の後に最終artifactから`collect_unresolved`を1回実行し、HR報告書・run summary event・stdoutを出す。
- 新機構はstatus文字列1つ、`collect_unresolved`関数1つ、`resolve_gloss`関数1つのみ。
- 機械検査は(e)の最小形とし、gate化はTrialデータを見てユーザーが判断する。
- Aより単純で、fail-openの経路が無く、既存HR統計を汚さない。

案B・C・D・Eの扱いは草案どおりでよい(Bの判断は(i)参照)。

## 6. 実装前に解消すべき未確認事項

1. Family X/Z/その他KP経路で、gloss(`japanese_gloss`/`japanese_gloss_tts`)を読むTTS・LLM・表示の呼出元の全数(Grep一覧)。
2. `w62.ensure_stage`の再開挙動(runnerが例外を送出した後の再実行で選定が再実行されるか)と、`w62.run_kp_stage`内部。
3. page/player生成がAudio Validation Gate(assemble)を通った後にしか実行されないか。
4. `tts_generation_results.json`が無いままassembleへ進む経路の有無(assemble.py:472-473のfail-open)。
5. HR報告の届け先(PM報告に載せる経路)の確定。queueを使わない場合に既存のHRページで見えなくなることを、ユーザーが許容するか。
6. 新しい機械検査(span対応)をProductionの品質条件として追加することへのユーザー承認(Trialの後)。
7. 量産再開までのflag運用(凍結/ON維持/OFF化)についてのユーザー判断。

## 7. 確認した範囲 / 確認していない範囲

**確認した範囲**:
- DESIGN_DRAFT_01(全文)、INVESTIGATION_01(全文)、OFFLINE_AUDIT_01(全文)、TRIAL_PLAN_01(全文)、REVIEW_AUDIT_01 §2・§4
- `er003_key_words_gloss_alignment.py` 37-48、80-439
- `er011_human_review_lock_01.py` 130-499、590-720
- `er019_family_x_audio_production_runner_01.py` 該当行(406-416、570-609、898、994、1228-1272、1890)
- `er003_v1_n3_01_tts_generate.py` 560-590
- `er003_v1_n3_01_assemble.py` 95-134、466-515
- `er006_secondary_asr_01.py` 315-336
- `er026_family_z_fiction_production_runner_01.py` 1140-1205
- `er003_v1_n3_01_scaffold_generate.py` 715-814
- 承認規則テンプレートの「日本語グロス」該当行(15、17、19、21、23)
- OPUS_FINDINGS_LEDGER 252-262
- `human_review_queue.jsonl`の参照ファイル数(33)、撤去対象シンボルの参照数(6ファイル)

**確認していない範囲**:
- `w62`(er062)内部と`ensure_stage`
- `er003_test_key_words_gloss_alignment.py`の本文
- `er003_key_words_canonicalization.py`
- B1のKP段全体(`_generate_key_phrase_segments_b1`の全体)
- page/player生成コード
- `tools/build_family_z_hr_review_page.py`と他のqueue消費側の実装
- `n3_tts.resolve_key_phrase_ja_gloss_tts`
- `gloss_alignment_01/`配下の証跡(VALIDATION_01、cost_01.json等)の実数値
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS本体
- 実行による検証は一切行っていない(すべて読解に基づく)
