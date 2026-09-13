# EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-STRENGTH-DESIGN-01

実行者: sonnet-worker(read-only調査+設計。Git/API呼び出し/SSOT編集/コード変更なし。追加API費用¥0、既存artifact・既存コードの読解のみ)。
Status: **USER_DECISION_REQUIRED**

一時ファイル: `docs/pm/ACTIVE_TASK_3V_FS.md`(本タスク用、上書き対象)。

---

## 0. 要点(5行)

1. Voices/Perspectiveの厳しさの主因は「権限の非対称性を明示せよ」という単一の文言問題ではなく、**Tension構造原則(design.md B-7、3段構造の第3段)が要求する「3人の役割・権限差を1文にまとめた断定」と、Ledger Deviation Checker(`changed_actor`/`unsupported_new_claim`)が禁じる「単一Ledger事実にない複数証拠の合成」が構造的に正面衝突している**こと。実データ(下記d節)で確認済み。
2. Local Rewriteの「hedgeを増やす」是正(`can/may/in some cases`)は、`changed_certainty`/`changed_scope`には効くが、`changed_actor`/`unsupported_new_claim`には効かない。実測で、hedgeを9箇所使った書き換えでもLEDGER_DEVIATIONのまま3回上限に達し`human_review_required`になった事例が存在する(d節の事例5)。「hedgeを増やしても通らない」というユーザー所見は実データで裏付けられる。
3. Fact Checker A'(Web検索版、News/Discoveryと共有の同一Production Prompt)は、Voice本文の「心理・意図として読める表現」も検証対象に含む設計(`当事者の心理や意図として読める表現`を明示)。Voice帰属免除(`registry.build_voice_attribution_block`)は**Fact Checker A'にのみ**適用され、Ledger Deviation Checkerには一切適用されていない(非対称な保護)。
4. 数字1個「必須」の指示(`er012_b_family_voices_writer_generic_01.py:402-404`、旧`er012_editorial_b_voices_3v_person_voice_trial_02.py:379-380/466-471`)は、ユーザー指摘どおり撤廃してもFact Safety自体(Ledger根拠の要件)は無傷で維持できる。既存コードの「数字は最大1個までの上限」規定(`:251-256`)とは別物であり、上限規定を変えずに済む。
5. 全ての緩和候補は、`family=="B"`ゲート(`er012_b_family_editorial_type_registry_01.py:475-480`、既存のFact Checker A' opt-in機構と同一パターン)で追加でき、A-Family News/Discoveryの`hook_aware`既定False・共有prompt本体は無改変のまま実装可能(構造的にA-Family非混入)。

---

## a. 現在の判定機構の一覧と過剰候補の特定

`run_voices_pattern_3v`(`er012_b_family_voices_writer_generic_01.py:942`)から呼ばれる順に整理する。

| # | 機構 | 実装/呼び出し箇所 | 判定基準 | retry trigger |
|---|---|---|---|---|
| 1 | Fact Checker A'(Web検索、News/Discoveryと同一Production関数) | `run_fact_check_a_prime_3v`(`:528`)→`b1prod.run_fact_checker`(`er012_b_family_voices_production_01.py:101`)→`r3.build_fact_check_prompt`(`er002_ja_web_research_r3.py:241`、prompt本体は`er002_v1_2m_restore_briefs/fact_checker_prompt_template_r3.txt`) | `verdict`∈{PASS,REVIEW_REQUIRED,FAIL}。テンプレ21行目「数字、日付、人名・組織名…**当事者の心理や意図として読める表現**…を検証対象」 | `verdict==FAIL`のみ即NG_REVIEW_REQUIRED(`:977`)。REVIEW_REQUIREDは素通り(retryなし) |
| 2 | Ledger Deviation Checker(Hook-aware版、News Production `er003_v1_n3_01_articles_generate.py`と同一関数) | `run_ledger_deviation_and_local_rewrite`(`:781`)→`vfl01.run_deviation_check(..., hook_aware=True)`(`er003_v1_en_direct_vfl_01_generate.py:603`) | 10種類の意味変化flag、`severity`∈{MINOR,MAJOR}。hook_awareは`changed_scope`/`changed_comparison`のみ緩和、他8種は常時厳格(`:548-564`) | MAJOR→Local Rewrite(3attempt×3cycle上限)。残存MAJORまたは`human_review_required`→即NG_REVIEW_REQUIRED(`:992`) |
| 3 | Local Rewrite(Ledger MAJOR是正) | `er010_ledger_local_rewrite_09.py:168` | `REWRITE_SYSTEM_PROMPT`で`can/may/might/some/sometimes/in some cases`によるhedge化を明示指示(`:103`) | 文単位3attempt上限(`MAX_REWRITE_ATTEMPTS=3`)、記事全体cycle3上限(`MAX_REWRITE_CYCLES=3`) |
| 4 | Directional Fact Precheck(rule-based、¥0) | `dfp.audit_article_directional_facts`(`:1010`) | 数値の増減方向のLedger照合のみ | **記録のみ、retry/gateに関与しない**(`directional_precheck_status`はdictへ格納されるだけ) |
| 5 | Analytical Leakage Check(3V固有) | `run_analytical_leakage_check_3v`(`:708`) | `leak_evidence_subject`等6項目(Voice)/6+1項目(Tension)/1項目(Closing)、PASS/FAIL | `any_flagged`→corrective_noteを付けて再生成、`MAX_WRITER_ATTEMPTS=3`上限 |

**過剰候補の特定(実データ根拠)**:

- **#2(Ledger Deviation)の`changed_actor`/`unsupported_new_claim`が、Tensionの構造要求(3人の役割・権限差の統合)と恒常的に衝突する。** 4個体(d節)すべてで同一スロット(Tension非対称性文)がMAJOR化。
- **#1(Fact Checker A')のテンプレートは「当事者の心理・意図」を明示的な検証対象にしており(`fact_checker_prompt_template_r3.txt:21`)、これは実在する事件の記者記事を想定した基準であり、意図的に合成されたVoiceの内心描写には設計思想上そぐわない。** 現状はVoice帰属ブロック(`voice_attribution_block`)で一部緩和済みだが、Ledger evidenceに直接対応しない「純粋な感情・判断」(Ledgerに影も形もない心情吐露)は対象外のまま。
- **#3(Local Rewrite)の`REWRITE_SYSTEM_PROMPT`はhedge化を明示指示する既存Production機構であり、これ自体は過剰ではない。過剰なのは#2がhedge化後も`changed_actor`等でMAJORを出し続け、#3のhedge化では原理的に解消できない意味変化カテゴリに対して繰り返し発火する点。**
- #4は記録専用のためgate上の過剰さは無い(現状維持でよい)。
- #5(Leakage Check)はhedge語彙そのものを罰する項目を持たない(`leak_evidence_subject`等は主語位置・語り口の問題であり、hedge語の有無を直接見ていない)。d節の4個体でLeakage Checkがhedge文自体をFAILにした実例は無い(flagged項目はいずれも統計主語文、hedgeとは別種の問題)。**Leakage Check自体は本ユーザー指摘の主因ではない。**

---

## b. 厳格判定を維持する境界(現状どおり動く/動かすべき部分)

以下は緩和対象から明示的に除外する(全緩和案に共通の前提):

1. **具体的数字・割合・件数**(`changed_number`)— Ledgerと異なる値への変更は常に厳格。
2. **固有名詞・組織名・制度名**(NBCUniversal、ニューヨーク市法、IBM等)— Ledgerが確認した主体を超える帰属は常に厳格。
3. **第三者(実在の個人・組織)の具体的行動の断定**(`changed_fact`、Voice以外が主語の事実文)— 常に厳格。
4. **Hook/Tension/Closingという「地の文」での客観的主張**(`VOICE_ATTRIBUTION_RULE_TEXT`が既に明示: 「Voice本文以外の地の文…は検証対象外にしない」`er012_b_family_editorial_type_registry_01.py:386-387`)— 既存ルールを踏襲し、地の文の客観風主張は緩和対象にしない。
5. **因果・否定・比較・時系列の反転**(`changed_causality`/`changed_negation`/`changed_comparison`/`changed_time`)— 常に厳格(hook_awareでも緩和対象外の8種と同じ扱い)。
6. **Ledgerに一切根拠のない新規具体的主張の捏造**(`unsupported_new_claim`のうち、複数Voiceの証拠を跨がない単純な捏造)— 常に厳格。

緩和候補として残るのは、**(i) Voice本文内で一人称として語られる意見・感情・判断の一般化に付随する`changed_scope`/`changed_certainty`**、および**(ii) Tensionで複数Voiceの断片的Ledger証拠を「役割の違い」として統合する際に生じる`changed_actor`/`unsupported_new_claim`(数字・固有名詞を伴わないもの限定)**の2種のみ。

---

## c. Voice限定で許容する境界案(判定ロジック上の区別方法)

判定ロジックが利用できる既存の区別軸は3つある。

1. **section区分(地の文 vs Voice本文)**: 6区切りparser(`b1prod.split_six_voice_sections`)が既に`voice_1_body`/`voice_2_body`/`voice_3_body`と`hook_body`/`tension_body`/`closing_body`を分離している。Ledger Deviation Checkerへ渡す際、**現状はこの区分を一切使っていない**(`article_text`全文を1回で渡す、`:784`)。区分を渡せば「Voice本文か地の文か」で緩和対象を機械的に切り分けられる。
2. **一人称/hedge語彙の検出**(rule-based、¥0): `changed_scope`/`changed_certainty`のみがtrueで、`changed_fact`/`changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`が全てfalseの場合に限り「hedge起因の逸脱」と分類できる。これは`_apply_deviation_post_hoc_validation`(`er003_v1_en_direct_vfl_01_generate.py:513`)と全く同じ形の後処理(既存関数のロジックを踏襲、新規発明ではない)。
3. **Voice attribution機構の転用**: `registry.build_voice_attribution_block`が持つ「Voice本文の主張がLedger evidenceと実質的に対応していれば出典明記の欠如を理由に計上しない」というルール文言パターンを、Ledger Deviation Checker用のprompt追加ブロックとして複製・適用する(HOOK_AWARE_DEVIATION_*と同じ「追加ブロックによるopt-in」パターン)。

**具体的な緩和ロジック案(2段階)**:

- **段階1(Voice本文限定、狭い)**: Voice 1/2/3本文内の文で、(a) 主語が一人称(I/my/me)または当該Voiceの立場を指す代名詞であり、(b) `changed_scope`または`changed_certainty`のみがtrueで他8種がfalseの場合、MAJORへ格上げしない(MINORへ自動降格、`_apply_deviation_post_hoc_validation`と同型の追加ルール)。数字・固有名詞・第三者行動を含む文は対象外(b節の境界がそのまま働く=`changed_number`/`changed_fact`/`changed_actor`のいずれかがtrueなら対象外)。
- **段階2(Tension構造の役割合成、広い)**: Tension本文の「非対称性」段(design.md B-7第3段)に限り、Ledgerが個別に確認した各Voiceの役割記述(例: Voice 1 evidenceが応募者の発言権欠如、Voice 2 evidenceが採用担当者の運用実務、Voice 3 evidenceが経営判断)を1文へ統合した際に生じる`changed_actor`/`unsupported_new_claim`を、数字・固有名詞・制度名を伴わない場合に限り緩和する。これはHook-aware版がすでに採用している「特定section・特定条件下でのみ・特定flagのみ緩和」という設計パターン(`HOOK_CLAUSE`)をTensionの非対称性段へ複製するもの。

段階1はd節のhedge文の大半(事例1〜4)を解決するが、事例5(ablation、`changed_actor`が主因)は解決しない。段階2まで実施して初めて事例5型が解消される見込み(推定、未検証)。

---

## d. 実例(Phase 1b-04の4サンプル+旧Trial-02)とレベル別PASS/FAIL比較

対象: `er012_output/editorial_b_voices_3v_generalization_regression_01_attempt{1,2,3}`(新Regression run、Phase 1b-04)+ `editorial_b_voices_3v_ablation_no_grounding_block_01_attempt1`(同Phase 1b-04の原則除去ablation)+ 旧`editorial_b_voices_3v_person_voice_trial_02`採用版(比較対象)。すべて実データ(`local_rewrite_results.json`/`ledger_deviation.json`)からの引用。

| # | 出典 | 元文(Tension非対称性文) | 検出flag | 何回のhedge試行で収束したか | 現状の結果 |
|---|---|---|---|---|---|
| 1 | 旧Trial-02採用版 | "The applicant cannot choose the system; the recruiter runs it but cannot adopt it; the owner decides." | `changed_actor`他5フラグ、MAJOR | 1回で"...recruiter runs it **and may also help decide** whether to adopt it; the owner **may** make the final call."→PASS | 通過(hedge2箇所) |
| 2 | 新Regression attempt1 | "Power is unequal: the applicant is judged, the recruiter runs a tool without choosing it, and the owner chooses it and carries the result." | `changed_fact`,`changed_scope`,`changed_actor`,`unsupported_new_claim` | 1回(hedge化ではなく表現全体を"The positions are not identical: ..."へ再構成)→PASS | 通過 |
| 3 | 新Regression attempt2 | "Their power is unequal: the applicant cannot choose the system, the recruiter runs it without final authority, and the owner approves its use." | `changed_fact`,`changed_scope`,`changed_certainty`,`changed_actor`,`unsupported_new_claim` | 1回で"Their power **can** be unequal: **in some cases**, applicants **may** have little control…employers and recruiters determine…"→PASS | 通過(hedge3箇所) |
| 4 | 新Regression attempt3(採用版) | "Power is uneven: the applicant cannot choose, the recruiter operates, and the owner decides." | 同上5フラグ | 1回で"Power **can** be uneven: **in some cases**, the applicant **may** have little control…the recruiter **may** operate…the employer **may** remain responsible…"→PASS | 通過(hedge4箇所) |
| 5 | ablation(原則除去) attempt1 | "Their power is uneven: the applicant cannot choose the process; the recruiter runs it but does not choose adoption; the owner chooses and bears the consequences." | 同型5フラグ | **3回(上限)ともLEDGER_DEVIATION**。最終形"**In these cases**, their power **may** be uneven: the applicant **may** have limited influence…and **may** face difficulty…the recruiter or hiring manager **may** use the tool and, **in some cases**, help decide…the company or business leader **may** weigh…"(hedge7箇所超)でも不合格 | **収束せず、`human_review_required=True`→NG_REVIEW_REQUIRED** |

**緩和レベル別のPASS/FAIL予測(現状=hedgeで運任せ、が実態)**:

| レベル | 事例1 | 事例2 | 事例3 | 事例4 | 事例5 |
|---|---|---|---|---|---|
| 現状(緩和なし) | PASS(紙一重) | PASS | PASS(紙一重) | PASS(紙一重) | **FAIL(3回上限)** |
| 段階1(Voice本文hedge免除のみ) | 変化なし(Tension文は対象外) | 変化なし | 変化なし | 変化なし | 変化なし(`changed_actor`が主因のため不変) |
| 段階2(Tension役割合成の`changed_actor`/`unsupported_new_claim`緩和) | 初回からPASS(rewrite自体不要) | 初回からPASS | 初回からPASS | 初回からPASS | **PASSへ転換(想定、未検証)** |

**技術的な副次観察(政策論とは別、bug寄りの発見)**: ablation cycle1で対象文は文単位の受理チェック(`before_ctx+text+after_ctx`のみを見る`_run_check_window`)では3回ともLEDGER_DEVIATIONだったが、同じ改変後テキストを含む**記事全体のcycle終了時再判定**では、この文はもはやMAJOR一覧に含まれていなかった(`local_rewrite_cycles.json`: cycle1 recheck_major=2件、うち対象文なし=cycle2はこの文を再対象にしていない)。つまり**Local Rewriteの受理チェックが、生成プロンプトに渡している`point_context`(section全体)より狭いwindow(前後1文のみ)で判定しており、記事全体で見れば許容される文を、狭い文脈だけで見て誤って拒否している可能性がある**。これは判定基準を緩めるものではなく、**受理チェックに渡す文脈量を生成プロンプトと揃えるだけの整合性修正**であり、h節で「その他案」として扱う。

---

## e. 安全境界・Regression条件・retry/fallbackへの影響

### 安全境界(緩和対象の明示的限定)

- 緩和対象は**「Ledger逸脱のうち`changed_scope`/`changed_certainty`のみ、かつ`changed_number`/`changed_fact`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`が全てfalse」の場合のみ**(段階1)。段階2を採用する場合のみ、Tension非対称性段に限り`changed_actor`/`unsupported_new_claim`も対象に含めるが、**数字・固有名詞・制度名を伴う場合は対象外**(b節の境界を機械的に強制)。
- 具体的数値・固有名詞・制度・第三者の具体的行動は、段階1・段階2のいずれでも一切対象外(b節の6項目は不変)。

### Regression条件(実行可能な検証手順)

1. **真陽性温存テスト(¥0、offline)**: 既存9個体(旧Trial-02 attempt1/2、新Regression attempt1/2/3、ablation attempt1、その他既存Ledger逸脱ログ)の`ledger_deviation.json`に記録済みの全deviationsを、新ルールで再分類する。**具体的数字・固有名詞・第三者行動を含むdeviation(例: 9-2節のNBCUniversal関連`changed_actor`)が緩和後も引き続きMAJORのままであること**を確認する(緩和ルールがb節の境界を守っているかの直接検証、追加API呼び出し不要)。[2026-09-13訂正: 実データでは該当箇所(`regression_attempt3`の"I prepare an audit summary and notice, as required under New York City rules.")は現行severity=MINORであり、MAJOR化した記録はない(Stage 1で確認、`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`A3節)。したがって本引用は「緩和してもMAJORのまま残るべき真陽性」の実例としては成立していない。真に数字・固有名詞入りのMAJOR実例は、Stage 1のサンプル(10個体・21件)には存在しなかった]
2. **A-Family無変化テスト**: `hook_aware`の既定値・`DEVIATION_PROMPT_TEMPLATE`本体を無改変のまま、新ルールを`family=="B"`ゲート付きの追加関数(例: `run_deviation_check_voice_aware`)として実装し、A-Family呼び出し元(`er003_v1_n3_01_articles_generate.py`)からは一切参照されないことをimport/grep差分で確認する。既存A-Family offlineテスト(`er010_n9_production_integration_09_test_01.py`等)を無変更のまま実行し全PASSを確認する。
3. **既存offlineテストの回帰**: `er012_b_family_voices_writer_generic_01_test_01.py`(現状56件PASS、Phase1b-04実測)を無変更のまま実行し、新規追加分のみ増分テストとして追加する。

### retry/fallback/Local Rewriteへの影響

- 段階1のみ: Voice本文のMAJORが一部MINORへ降格するため、**Local Rewrite発動回数が減り、費用が下がる方向**(既存3attempt×3cycle上限は無変更)。
- 段階2: Tension非対称性文が初回からLEDGER_COMPLIANTになりやすくなるため、**事例5型(3回上限到達→human_review_required)の再発を抑制**できる可能性が高いが、Tensionの`changed_actor`緩和が「本当は起きていない権限構造」を通してしまうリスクとのトレードオフ(h節で評価)。
- MAX_REWRITE_CYCLES(3)/MAX_REWRITE_ATTEMPTS(3)/MAX_WRITER_ATTEMPTS(3)といった既存の安全装置の上限値は、いずれの案でも変更しない(緩和は「MAJORと判定するかどうか」の基準側であり、上限回数側ではない)。
- 費用: Phase1b-04実測(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_REPORT.md`)で、Local Rewrite発動が多いattemptほど高コスト(attempt1=¥24.3、attempt2=¥28.3、attempt3=¥25.5)。段階1・2とも「MAJORと判定される回数を減らす」方向のため、**1本あたりのコストは現状以下になる見込み**(悪化方向のリスクは無い)。

---

## f. Voice attribution等B-Family固有機構との整合

- 既存の`VOICE_ATTRIBUTION_RULE_TEXT`(`er012_b_family_editorial_type_registry_01.py:372-388`)は**Fact Checker A'にのみ**適用され、Ledger Deviation Checkerには渡されていない(`vfl01.run_deviation_check`呼び出し2箇所[`:784`,`:795`]はいずれも`verified_ledger_text`と`article_text`のみを渡し、attribution blockの引数を持たない)。
- 段階1・2の実装では、Ledger Deviation Checker用に**同型の追加ブロック**(HOOK_AWARE_DEVIATION_*と同じ「テンプレートへの追記+スキーマへのフラグ追加」パターン)を新設することで、既存のVoice attribution機構の設計思想(「Voice本文はLedger evidenceの一人称翻案であり、出典明記の欠如だけを理由に計上しない」)をLedger Deviation Checker側にも一貫させることができる。これは新しい原則の創造ではなく、**既に片方のCheckerで承認済みの考え方をもう片方へ揃えるだけ**という説明が可能。
- `VOICE_ATTRIBUTION_RULE_TEXT`の除外規定(「Voice本文以外の地の文…は検証対象外にしない」)は、段階2(Tension緩和)を採用する場合に**明示的な例外**として扱う必要がある(現状の除外規定と矛盾しないよう、Tension非対称性段だけの限定条項として書き分ける)。

---

## g. 項目5(Voice内の数字1個「必須」要求の撤廃)

### 現行文言(実文、両ファイルで意味的に同一)

- 汎用prompt(`er012_b_family_voices_writer_generic_01.py:402-404`、`_voice_card_block_text`関数内):
  > "この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください(詳細ルールは上記【Evidenceは脇役であること】参照)。"
- 旧prompt(`er012_editorial_b_voices_3v_person_voice_trial_02.py:376-380`、Voice Card 1内、ルール本体は`:466-471`):
  > "この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください(詳細ルールは下記【Voice内の数字】参照)。"
- ルール本体(`:251-256`、両ファイル共通の趣旨):
  > "1つのVoiceのセクション全体を通して、具体的な数字は最大1つだけにし、必ずその人/その立場の人々の実感に折り込み、話し言葉で書いてください。"

**この2つは別物である**: `:251-256`は「上限(最大1個まで)」の規定であり、`:402-404`は「使うことを指示する(織り込んでください)」という**要求**。ユーザー指摘の撤廃対象は後者のみで、前者(上限規定・Fact Safety=Ledger根拠の要求)はそのまま維持できる。

### 実測との対応(Opus L3診断で既に文書化済み、EDITORIAL-B-FAMILY-VOICES-3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01_REPORT.md論点2/論点4(A))

theme側のVoice 1 supporting evidenceが集計統計(49%/79%)のみのため、「1個織り込め」という要求が「その統計を使え」という誘導になり、Analytical Leakage Checkの`leak_evidence_subject`(文の主語がsurvey/dataになる)を誘発していた実例が複数確認されている(d節とは別のflag種別、`analytical_leakage_check_3v_attempt{1,3}.json`のvoice_1 flagged項目)。

### 撤廃後の文言案(実装しない、案のみ)

`:402-404`を以下に置換する案(意味変更: 「必須」→「任意」、Fact Safety要件[Ledger根拠]は無変更):

> "この裏付けの中から、自然に人を主語にした話し言葉へ織り込める場合に限り、具体的な数字を1つだけ使ってください。無理に数字を使う必要はなく、数字を使わずにその人の実感だけで書いても構いません(詳細ルールは上記【Evidenceは脇役であること】参照)。"

- **Analytical Leakage Check・retry/fallbackとの整合**: `leak_evidence_subject`/`leak_numbers_foreground`の基準文言(`:662-664`)は無変更のまま使える(「数字が0個、または1個だけ」を既にPASS条件として許容済み、`:664`)。Checker側の変更は不要。
- **Regression影響**: 数字を使わない選択が増えると、Analytical Leakage Checkの`leak_evidence_subject`系flagが減る方向(悪化リスクなし)。Fact Checker A'・Ledger Deviation Checkerの判定対象(具体的数字)自体が減るため、両Checkerの負荷・誤検知リスクも下がる方向。
- **旧prompt側**(`er012_editorial_b_voices_3v_person_voice_trial_02.py`)は既存承認済みTrial記事の生成に使われた履歴ファイルであり、本タスクでは変更しない(汎用prompt側のみが今後のProduction対象)。

---

## h. Second option・その他案のQCD/安全性

### Second option: 「権限の非対称性」の普遍ルール化解除

design.md B-7の3段構造(共通前提→分岐点→非対称性)のうち、**第3段(非対称性の明示)を全テーマ必須の恒久ルールから外し、Ledger上その非対称性が数字・固有名詞なしで自然に成立するテーマでのみ含める**(または、成立させる場合は最初から「Voiceごとの役割は完全に分離しているとは限らない」といった留保付きの言い回しをprompt側で指示し、Local Rewriteでの事後hedge化に頼らない)。

- **Q(品質)**: Tensionの「単純合計では答えにならない」という3V方式の中核目的(design.md B-7)は、共通前提・分岐点の2段だけでも部分的に成立可能(d節の事例2は実際にhedgeではなく再構成で通過しており、断定的な権限構造文を書かなくても3人の対比は描けることを示唆)。ただし「なぜ合理的な人が意見が分かれるか」の説明力は、非対称性の明示を弱めると低下するリスクがある(design.md自身が「これが核心」と位置づけている、`design.md:493-495`)。
- **C(費用)**: 実装はprompt文言変更のみ(¥0、追加API呼び出し不要)。効果測定には最低1本の実生成が必要(¥25〜30、既存Phase1b-04実測ベース)。
- **D(納期)**: 文言案作成は即日。効果確認の実生成1本は当日中に可能。
- **安全性**: Checker側を一切変更しないため、Fact Safetyの基準自体は無傷。**最も安全な選択肢**(Checkerを緩めない、Writer側の要求を緩めるだけ)。
- **リスク**: Tensionの説得力低下、3V方式の「深い理解への着地」という目的が弱まる可能性(品質面のトレードオフ、Fact Safety面のリスクではない)。

### First option(c/d/e/f節で設計済み)との関係

Second optionのみ採用した場合、d節の事例1〜4のようなborderline hedge合戦自体が減る可能性が高いが、テーマによっては非対称性の明示が自然に必要になる場合もあり、その際は依然としてChecker側の衝突が残る。**Second option単独ではなく、First option段階1(Voice本文hedge免除)と組み合わせるのが、Checkerを最小限しか緩めずに済む組み合わせ**と考えられる。

### その他案

1. **Tension限定の緩和のみ(First option段階2のみ採用、Second optionは採用しない)**: 非対称性の明示は維持しつつ、Tensionのその1段落だけChecker側を緩和する。Second optionより品質低下リスクは低いが、Checker側の緩和範囲はFirst optionの中で最も広い(b節の境界を厳格に保つ実装が必須)。
2. **Checker severity階層化**(Opus L3診断の候補(D)相当、本タスクの新規指摘ではなく既存候補の再掲): `changed_actor`/`unsupported_new_claim`のうち、数字・固有名詞を伴わない「役割合成」型だけをMINOR固定にする(MAJORへ昇格させない)。段階2とほぼ同じ効果だが、フラグ単位ではなくseverity算出ロジック(`_apply_deviation_post_hoc_validation`相当)への追加改修になる。
3. **受理チェックの文脈整合(d節末尾のbug寄り修正、緩和ではない)**: Local Rewriteの受理チェック(`_run_check_window`)に、生成プロンプトと同じ`point_context`(section全体)を渡す。判定基準は一切変えないため、Fact Safetyへの影響は理論上ゼロだが、d節の事例5のような「受理チェックだけが記事全体recheckより厳しい」という技術的不整合を解消できる可能性がある(未検証、offlineで検証可能)。

---

## i. 最小Trial案

### 案X: offline再判定のみ(追加API呼び出しなし、¥0)

保存済みの`ledger_deviation.json`(旧Trial-02・新Regression 3attempt・ablation、計5ファイル)に既に記録されている`raw_parsed.deviations`(モデルの生フラグ出力)を対象に、**新しい後処理ルール(段階1: `changed_scope`/`changed_certainty`のみtrueならMINORへ降格)をPythonスクリプトで再適用し、overall_statusがどう変わるかを比較する**。これはLLM呼び出しを一切伴わない(既存の生フラグを読み直すだけ)。

- 得られるもの: 段階1適用後にd節の事例1〜4がそもそもMAJOR扱いにならず、Local Rewrite自体が不要になっていたかどうかの確定判定。
- 得られないもの: 段階2(Tension役割合成の緩和)の効果。これは`changed_actor`/`unsupported_new_claim`という「対象外フラグ」自体を緩和対象に含めるかどうかの判断であり、生フラグの後処理だけでは検証できるが、**新しいprompt文言(Second option)の効果は生フラグの再利用では測れない**(promptを変えれば書き出し自体が変わるため)。
- 費用: ¥0。所要時間: 数十分(Pythonスクリプト作成+実行)。

### 案Y: 実生成が必要な場合

Second option(Tension文言の書き分け)またはFirst option段階2(Ledger Deviation Checkerへの追加ブロック)の効果を確認するには、**実際にWriterを再実行してTension文がどう書かれるか、Checkerがどう判定するかを見る必要がある**。

- 最小構成: 既存テーマ(AI採用選考、Ledger既存)で1本(1〜3attempt、Phase1b-04実測ベースで¥25〜78)。
- 汎用性確認には別テーマ1本が望ましい(Opus L3診断が既に指摘した「テンプレート固着」懸念とも共通、`論点6`)が、これは本タスクの範囲(Fact Safety強度)を超えるためオプション扱い。
- 合計目安: 最小1本(¥25〜78)、汎用性確認込みで2本(¥50〜156)。既存の管理ID予算枠がある場合はそれに従う(本Reportは費用執行を含まない)。

---

## 参照した実データ・ファイル(すべてRead/Grepで直接確認、要約の孫引きなし)

- `er012_b_family_production_runner_01.py:604-814`(3V Production Wiring Phase1、Ledger Deviation Checkはmonitoring専用と明記)
- `er012_b_family_voices_writer_generic_01.py:1-1145`(Voice Card bullet、共通原則ブロック、Fact Checker A'、Analytical Leakage Check、run_pipeline_3v)
- `er012_editorial_b_voices_3v_person_voice_trial_02.py:1-50,355-481,925-1034`(旧prompt、Local Rewriteループ)
- `er003_v1_en_direct_vfl_01_generate.py:423-627`(Ledger Deviation Checker本体、Hook-aware版)
- `er010_ledger_local_rewrite_09.py:1-228`(Local Rewrite、REWRITE_SYSTEM_PROMPT)
- `er012_b_family_voices_production_01.py:85-124`(Fact Checker呼び出し)
- `er002_ja_web_research_r3.py:150-434`(Fact Checkerゲート、verdict retry無し)
- `er002_v1_2m_restore_briefs/fact_checker_prompt_template_r3.txt`(News/Discovery共有prompt本体)
- `er012_b_family_editorial_type_registry_01.py:372-480`(Voice attribution、family=="B"ゲート)
- `er008_directional_fact_precheck_08.py:310-370`(記録専用チェック)
- `design.md`(`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/`、B-7節、非対称性の設計根拠)
- `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_REPORT.md`(9節・11節、実測flagged実文・caveat語数表・費用実測)
- `EDITORIAL-B-FAMILY-VOICES-3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01_REPORT.md`(論点2〜4、二律背反の既存診断、案1〜3は本タスクのユーザー方針未反映のため不採用)
- `er012_output/editorial_b_voices_3v_generalization_regression_01_attempt{1,2,3}/audit/local_rewrite_results.json`、`ledger_deviation.json`、`analytical_leakage_check_3v_attempt{1,2,3}.json`
- `er012_output/editorial_b_voices_3v_ablation_no_grounding_block_01_attempt1/audit/local_rewrite_results.json`、`local_rewrite_cycles.json`

## Status

**USER_DECISION_REQUIRED**: First option(段階1/段階2/組み合わせ)・Second option・その他案(Tension限定/severity階層化/受理チェック文脈整合)のいずれを採用するか、または案X(offline ¥0)を先に実行してから判断するかをユーザーに選定いただく必要がある。Production実装・配線は本Reportの範囲外(未実施)。
