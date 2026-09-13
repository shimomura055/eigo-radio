# EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT

管理ID: EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE1-OFFLINE

## Stage 1

Stage 1 = ¥0 offline検証(実API呼び出し0件、保存済みデータ+scratchpadスクリプトのみ)。
判定語(REJECTED/VALIDATED/UDR)はFableが確定する。本節は判定材料の提示のみ。

参照した設計文書: `EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-STRENGTH-DESIGN-01_REPORT.md`(b/c/d/e/i節)、
`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_REPORT.md`(9-2節、費用実測)。

検証スクリプト・中間出力(すべて新規、Git未追跡):
- `er012_output/fact_safety_relaxation_trial_01/a_deviation_classification.json`(最終ledger_deviation.json、4件)
- `er012_output/fact_safety_relaxation_trial_01/a2_major_reclassification.json`(cycle内MAJOR、17件)
- `er012_output/fact_safety_relaxation_trial_01/b_cycle_extraction.json`(local_rewrite_cycles.json機械抽出、17件)
- `er012_output/fact_safety_relaxation_trial_01/c_cost_breakdown.json`(raw_usage_log集計)

対象10個体: `person_voice_trial_02`(b1b_run01 attempt1/2)、`generalization_regression_01`
(attempt1/2/3)、同`_n2`(attempt1/2/3)、`ablation_no_grounding_block_01`(attempt1)、
`generalization_regression_01_run1_ng_review_required`(旧run1、NG_REVIEW_REQUIRED、
参考として追加)。設計報告書が挙げた6個体に加え、n2の3個体・旧run1を追加し計10個体・
21件のdeviation(最終ledger 4件+cycle内MAJOR 17件)を機械分類した(設計時点より広いサンプル)。

---

### A. 段階1/段階2の再分類検証

#### A1〜A2. 全deviation列挙・再分類結果

6区切りparser(`er012_b_family_voices_production_01.py:222-241 split_six_voice_sections`、
`_HEADING_RE`はL122)のロジックをそのまま複製し(numpy依存の重い本体import不要のpure関数のみ)、
各deviationの`claim_in_article`/`original_ng_sentence`を`pre_editor_article.md`(cycle実行前の
原文)へ照合してsectionを機械判定した。全21件でsection判定は成功(NOT_FOUND/PARSE_FAILED 0件)。

**最終ledger_deviation.json(4件、すべて現行severity=MINOR、MAJORは0件)**:

| 個体 | section | 一人称主語 | flags(true) | 数字/固有名詞/制度/第三者 | 現行severity |
|---|---|---|---|---|---|
| regression_attempt2 | voice_2_body | Yes | changed_certainty | なし | MINOR |
| regression_attempt2 | voice_3_body | Yes | changed_scope, changed_certainty, **changed_actor** | なし(※後述A4) | MINOR |
| regression_attempt3 | voice_2_body | Yes | **changed_actor** | institution: New York City | MINOR |
| regression_run1ng_attempt1 | voice_1_body | **No**(第三者主語) | **changed_actor** | thirdparty_action: "Another applicant said" | MINOR |

**cycle内で検出された旧MAJOR(Local Rewriteが発動した17件、`local_rewrite_cycles.json`の
`original_ng_sentence`+`flags`、現行では最終記事に残らない=hedge成功後は「deviations」配列から消える)**:

全17件の内訳(individual×cycle、詳細は`a2_major_reclassification.json`):

| section | 件数 | flags共通パターン | Stage1適用可否 | Stage2適用可否 |
|---|---|---|---|---|
| voice_1/2/3_body | 10件 | 全件`changed_fact`を含む(+time/actor/unsupported_new_claim等) | **0/10 該当**(Stage1条件=「changed_scope/changed_certainty以外すべてfalse」だが、実データはchanged_factが常に共存) | N/A |
| hook_body | 1件(ablation cycle2) | changed_fact, changed_certainty | 対象外(hookはStage1の対象sectionに含まれない) | N/A |
| tension_body | 6件 | changed_fact + (changed_actor or unsupported_new_claim)、数字/固有名詞/制度なし | N/A | **6/6 該当** |

**重要な発見(Stage1の実効性)**: cycle内MAJOR 10件のVoice本文deviationは**全件**
`changed_fact=true`を伴っていた。Stage1の定義(c節67行目)は「`changed_scope`または
`changed_certainty`のみがtrueで他8種(`changed_fact`含む)がfalse」であり、この条件に
一致する実例は**サンプル21件中0件**だった(最終ledgerの1件[regression_attempt2の
voice_2、changed_certaintyのみ]は元々MINORであり、MAJORからの降格ではない)。
つまり、実データでは「MAJORと判定されるほどの逸脱」には常に`changed_fact`が併記されて
おり、**Stage1は少なくともこのサンプルではLocal Rewrite発動回数を1件も減らさない
(e節の「発動回数が減り費用が下がる」という想定はこのサンプルでは裏付けられない)**。

**Stage2の実効性**: Tension本文の「役割の非対称性」定型文(3人の権限差を1文に統合する文)は
6個体すべてで検出され、**全6件がStage2の緩和条件(数字・固有名詞・制度・第三者具体的行動を
含まず、changed_actor/unsupported_new_claimのみが問題)に一致**した。設計報告書d節の
表(事例1〜5)に加え、旧run1個体でも同型の6件目を確認(再現性の追加証拠)。

#### A3. 真陽性温存確認

`changed_number=true`の実例、または数字・固有名詞・制度・第三者具体的行動を明確に含む
**MAJOR**deviationは、対象21件の中に**存在しなかった**(Stage1/Stage2いずれの適用対象からも
除外される事例は1件あったが、それはMINORで元々MAJORではない[後述])。したがって
「緩和後にMAJORから外れてしまう真陽性」は**0件**であり、A3のSTOP条件
(「1件でも真陽性が緩和で落ちる」)には**該当しない**。

ただし重要な限界がある: 設計報告書e節107行目が真陽性の具体例として挙げた
「9-2節のNBCUniversal関連changed_actor」(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-
WIRING-PHASE1B-04_REPORT.md`336-355行目、`regression_attempt3`の
"I prepare an audit summary and notice, as required under New York City rules.")を
実データで確認したところ、**現行severityはMINORであり、Local Rewriteが発動した記録もない
(最初からMAJORになったことがない)**。つまりこの引用例は「緩和してもMAJORのまま残る
べき真陽性」の実例としては**成立していない**(そもそも緩和対象になるほどMAJORだった
ことがない)。これはStage1/2の安全性が破られたという意味ではない(真陽性が実際に
落ちた事例はない)が、**設計報告書の引用の正確性の誤り**であり、Fableへの報告事項として
明記する。あわせて、「具体的数字・固有名詞・制度・第三者行動を伴う真のMAJOR事例」自体が
今回の10個体・21件のサンプルには存在しなかったため、**Stage1/2の安全境界は「危険な
緩和が実際に起きなかった」ことの確認に留まり、「危険な事例を正しくMAJORのまま
維持できる」ことの積極的な実証にはなっていない**(サンプルにその種の事例が無いため)。
より多様なテーマでの追加確認が望ましい(未実施、費用が発生する)。

#### A4. 境界事例(rule-basedで判別が曖昧な文、保守側に倒した場合の結果)

1. **Hilton一般化事例**(regression_attempt2、voice_3_body、MINOR、flags=
   changed_scope/changed_certainty/**changed_actor**): 元Ledger事実は「Hiltonが採用期間を
   平均6週間→5日に短縮したと報告」という具体的企業名+数字を含む事実だが、記事本文
   ("I have seen hiring move from weeks to days")には数字も企業名も**残っていない**
   (一般化により消えている)。本タスクのrule(iv)は最終テキストの字面(数字・固有名詞の
   有無)を機械チェックするため、この事例では**字面だけでは「数字・固有名詞を含む」と
   検出できない**。この事例が誤ってStage1に緩和されなかったのは、`changed_actor`が
   trueで他8種いずれかがtrueならStage1対象外という**フラグ条件による除外**が効いた
   ためであり、字面チェック単独では防げなかった。**保守側の結論**: 実装時は
   「最終テキストの字面」ではなく「flags(changed_fact/changed_number/changed_actor等)」を
   一次的な安全境界とし、字面チェックは補助(二次防御)に留めるべき(設計報告書b/c節の
   記述自体は既にflags優先になっており、本確認はその設計判断の妥当性を裏付けるもの)。
2. **NYC言及Tension文**(旧run1個体cycle2、tension_body、flags=changed_fact/
   changed_causality/changed_certainty/**unsupported_new_claim**、"New York City's yearly
   bias check and notice rule adds work for the recruiter..."): flagsだけを見ると
   `unsupported_new_claim=true`のためStage2の対象条件(changed_actor **or**
   unsupported_new_claim)に一致するが、本文中に"New York City"という制度名が明記されて
   おり、rule(iv)の制度名チェックで**正しく除外**された。もしこの制度名チェックが
   無ければ、この文はStage2により誤って緩和候補に含まれていた。**この1件は、
   flagsだけでは不十分で、字面(制度名)チェックが実際に安全側の役割を果たした
   唯一の確認事例**であり、Stage2実装では「flags条件」と「数字・固有名詞・制度名の
   字面除外」の**両方**が必須であることを裏付ける。
3. **第三者行動の言い換え耐性**: Baker事例("Another applicant said he was scored...")は
   regex(`the applicant...said`等の定型パターン)で検出できたが、より婉曲な言い換え
   (例: 「一部の応募者はそう感じている」等、主語+動詞が定型から外れる表現)は
   regexで見逃す可能性がある。今回のサンプルには該当する見逃し事例はなかったが、
   実装時はrule-basedのみに依存せず、既存のLedger Deviation Checker(LLM判定)の
   flags出力を主とし、字面ルールは補助とする設計が保守的(1の結論と整合)。

**STOP条件(A3/A4)への該当有無**: 真陽性が緩和で落ちた事例は0件のため**A3のSTOP条件には
非該当**。ただし上記の境界事例2件(Hilton、NYC言及)は「flagsのみ」「字面のみ」の
いずれか片方だけに依存した場合に安全性が損なわれ得ることを示しており、**実装する場合は
flags条件+字面除外条件の両方を必須とする**必要がある(これは既存設計案(b/c節)の
記述と一致しており、新たな仕様変更を要求するものではない)。

---

### B. その他案3(Local Rewrite受理チェックの文脈不整合)の¥0検証

#### B1. コード差分(行番号付き)

- 受理チェック(狭いwindow): `er012_b_family_voices_writer_generic_01.py:794`
  `_run_check_window(window_text)`が呼ばれる際、`824-825`行目で
  `before_ctx = sentences[sidx-1]`、`after_ctx = sentences[sidx+1]`
  (1文前・1文後のみ、`_SENTENCE_SPLIT_RE`による文分割)。実際の受理判定は
  `er010_ledger_local_rewrite_09.py:189/199/208`の
  `run_check_window_fn(f"{before_ctx} {text} {after_ctx}".strip())`で行われる
  (対象文+前後各1文のみ)。
- 生成prompt(広いcontext): 同ファイル`826`行目`point_context =
  local_rewrite.extract_point_context(article_text, target)`(抽出失敗時のみ
  `829`行目で`before_ctx+target+after_ctx`にフォールバック)。`extract_point_context`は
  対象文が属するsection全体(見出しから次の見出し直前まで)を返す(実データで確認、
  B2参照)。
- **差分の実体**: 生成には「section全体」を渡す一方、その生成結果を受理するか
  どうかの判定には「前後各1文」しか渡していない(生成コンテキスト>受理判定コンテキスト、
  常に受理判定の方が狭い)。

#### B2. 実データからの機械抽出

`local_rewrite_cycles.json`の`results[].attempts[].ledger_status`(window受理判定)と
`cycle.full_recheck_remaining_major_claims`(記事全体再判定でのMAJOR一覧)を10個体分
全件突合(`b_cycle_extraction.json`)。

**window受理チェック=3/3回ともLEDGER_DEVIATION(上限到達、human_review_required=True)、
かつ同cycleの記事全体再判定のMAJOR一覧には不在、という事例が2件確認された**:

| 個体 | 元文(Tension非対称性文) | flags | window受理判定(3回) | 同cycleの記事全体再判定major_count | 対象文がmajor一覧に含まれるか |
|---|---|---|---|---|---|
| ablation_no_grounding_block_01_attempt1(cycle1) | "Their power is uneven: the applicant cannot choose the process; the recruiter runs it but does not choose adoption; the owner chooses and bears the consequences." | changed_fact,changed_scope,changed_certainty,changed_actor,changed_negation,unsupported_new_claim | LEDGER_DEVIATION×3 | 2(別文2件) | **含まれない** |
| generalization_regression_01_run1_ng_review_required(cycle1) | "Their power is uneven: the applicant is judged, the recruiter runs a tool without choosing it, and the owner decides whether to use it." | changed_fact,changed_certainty,changed_actor,unsupported_new_claim | LEDGER_DEVIATION×3 | 2(別文2件) | **含まれない** |

上記2件はどちらも設計報告書d節「事例5」型(Tension非対称性文、`changed_actor`が主因)。
逆方向(window受理→記事全体再判定で不合格に転じる)の事例は、resolved=True(window受理
成功)とされた15件全件を確認したが**確認されなかった**(該当する組み合わせなし)。

`point_context`(section全体、平均約146トークン相当)と実際に構築されるwindow文字列
(前後各1文+対象文、平均約68トークン相当)を16件で実測比較したところ、平均拡大率
約2.6倍(1.27倍〜4.15倍、`window_vs_point.py`実測)。

#### B3. 判定

上記2件は「Local Rewriteの生成が使うcontext(section全体)」と「受理チェックが使う
context(前後1文のみ)」が異なるために、**同一の改変後テキストが生成直後には
狭い文脈で不合格判定を受け続け、記事全体という広い文脈で見れば実際には問題視されない
(MAJOR一覧に入らない)**という技術的な不整合であると判断できる(¥0で確認可能な範囲では)。
判定基準(Ledger Deviation Checkerのseverity算出ロジック・flag定義)自体は両チェックで
同一のはずであり、**文脈量の違いだけで結果が割れている**ことが2件で確認できた
(判定基準・severityを変える提案ではなく、受理チェックへ渡す文脈量を生成promptと
揃えるだけの整合性修正、という設計報告書d節94行目の主張と一致)。

**未確認事項(¥0では確定できない)**: 受理チェックのwindowを`point_context`(section全体)に
置き換えた場合に、この2件が実際にPASSするかどうかは、同一プロンプトへ広いcontextを
与えて再実行しないと確定できない(LLM応答の非決定性・prompt文言の微妙な違いにより、
文脈量だけが原因と断定はできない)。**確認に必要な最小の有料再判定(実行しない)**:
この2件+コントロールとして既存の「resolved=True」を維持すべき数件(回帰確認用、
目安3〜5件)、合計**約5〜10回のLedger Deviation Checker呼び出し**。1回あたりの
実測トークン規模(既存ログの`ledger_deviation_or_local_rewrite`相当呼び出し、
入力約8,000〜9,600トークン)から概算コスト**約$0.02〜0.05(約¥3〜8)**。

---

### C. コストBefore実測

#### C1. コンポーネント別(呼び出し回数・token・コスト)

`raw_usage_log_writer.jsonl`(3系列)・`raw_usage_log_3v_writer.jsonl`(trial02)を実測。
役割分類はresponse_id突合(Fact Checker A'=`fact_qa.json`、Writer draft=
`writer_attempts.json`、Evidence Compression=`evidence_compression_editor_raw.json`、
Leakage Check=`attempt_history.json`記載のresponse_id)+呼び出し順序・入力規模による
機械分類(詳細`c_cost_breakdown.json`)。単価は`er005_output/cost_baseline_01/
pricing_snapshot.json`(gpt-5.6-luna: input $0.20/1M, cached $0.02/1M, output $1.20/1M,
web_search $10/1000件)、JPY換算レートは既存REPORT(PHASE1B-04)が使う逆算値
約¥160/$を継続使用(公式レートではないSonnet側近似、既存REPORTと同一手法)。

| 個体(全attempt合算) | 呼出数 | Writer draft | Evidence圧縮 | Fact Checker A' | Ledger Deviation+Local Rewrite(合算) | Leakage Check | 合計(実測) |
|---|---|---|---|---|---|---|---|
| trial02(b1b_run01、attempt1+2) | 13 | ¥5.0 | ¥0.6 | ¥23.1 | ¥7.5 | ¥1.5 | **¥37.6** |
| regression_01(attempt1〜3、採用run) | 35 | ¥6.8 | ¥0.8 | ¥46.9 | ¥21.1 | ¥2.4 | **¥78.0** |
| regression_01_n2(attempt1〜3) | 15 | ¥7.7 | ¥0.8 | ¥26.6 | ¥16.2 | ¥2.3 | **¥53.6** |
| ablation_no_grounding_block_01(attempt1、NG discard) | 20 | ¥1.9 | ¥0.3 | ¥12.2 | ¥11.9 | (未到達) | **¥26.2** |

上記合計は既存REPORT(PHASE1B-04、9-5節)記載の実測値(regression_01=¥78.0、
n2=¥53.6、ablation=$0.1637≈¥26.2)と完全一致し、集計方法の妥当性をクロス確認済み。
「Ledger Deviation Checker」単独と「Local Rewrite」単独への厳密分離は、usage log側に
呼び出し種別のtagが無いため(`stage`フィールドは`writer_b1b_attemptN`のみでチェッカー種別を
区別しない)、**¥0の範囲では合算値までしか確定できない**(限界として明記)。

1記事完成までの総Fact Safety関連コスト(Fact Checker A'+Ledger Deviation+Local Rewrite+
Leakage Check、Writer draft部分を除く): trial02≈¥32.6、regression_01(3attempt要)≈¥70.4、
n2(3attempt要)≈¥45.1、ablation(discard)≈¥24.1。**平均・レンジ**: 単純平均≈¥43.1、
レンジ¥24.1(discard)〜¥70.4(3attempt+leakage retry)。retryなしの最良ケース
(Phase1b-04実測、attempt3のみ+Phase A確認)は¥25.5。

#### C2. その他案3のコスト影響

window(平均約68token相当)→point_context(section全体、平均約146token相当)への
置き換えによる1回あたり追加token≈78token(input)。単価input $0.20/1M换算で
追加コスト≈$0.0000156/回(≈¥0.0025/回)。この追加分は、実測された1回あたりの
実際のinput規模(約8,000〜9,600token、ledger_text+instructions等の定型部分が大部分)の
**約1%未満**であり、コスト影響は無視できる水準。

Local Rewrite回数減少による相殺(段階2適用後の推定): 6個体すべてでTension非対称性文が
初回からLEDGER_COMPLIANTになると仮定した場合、各個体で少なくとも1回分の
window再試行(1〜3回)+場合によっては後続cycle全体(ablation/旧run1のように
3回上限到達→human_review_required→個体丸ごとdiscardに至った2件)を回避できる可能性が
ある。1個体丸ごとdiscardの回避価値は¥24〜32(Writer 1 attempt分)に相当し、
その他案3の追加コスト(¥0.0025/回程度)より**桁違いに大きい**。

#### C3. コスト抑制案の比較(実装しない、試算のみ)

| 案 | 内容 | 1記事あたり追加コスト(試算) |
|---|---|---|
| (a)必要sectionのみ追加 | 対象文が属するsectionのみ`point_context`として渡す(=現在の生成側の実装をそのまま受理チェックにも使う) | ≈+¥0.003〜0.01(受理チェック回数×¥0.0025目安) |
| (b)問題発生時のみ広いcontextへ昇格(2段階) | まず狭いwindowで判定、不合格の場合のみsection全体で再判定 | (a)よりさらに小さい(狭いwindowで通る大多数のケースでは追加コストゼロ、不合格時のみ(a)相当が発生) |
| (c)常時section全体 | 生成・受理チェック双方で常にsection全体を使う | (a)と実質同一(このPipelineでは`point_context`は既にsection全体のため(a)=(c)) |

(a)/(c)は本Pipelineの構造上ほぼ同一案であり、(b)は追加の分岐実装コストに見合う節約が
乏しい(そもそも(a)の追加コストが¥0.01未満のオーダーのため)。

#### C4. 100記事換算

- その他案3の追加コスト: (a)/(c)採用時で約¥0.3〜1.0/100記事(受理チェック回数を
  1記事あたり平均1〜3回と仮定)。**現行比で無視できる増分**。
- 段階2による節約(推定): 1個体丸ごとdiscard(¥24〜32相当)の再発を100記事中
  何本抑止できるかに依存する未確定の推定値。今回のサンプル(10個体中2個体=20%が
  この型のdiscardに至った)をそのまま外挿すると、100記事換算で理論上¥480〜640相当の
  節約余地があるが、**サンプル数10は少なく外挿の信頼度は低い**(参考値、未検証)。
- 段階1による節約: 実データでは0件該当のため、**100記事換算でも節約効果は
  実証されない**(0円と見積もるのが最も保守的)。

---

### D. 総括

**A3/B3のSTOP条件該当有無**: A3(真陽性温存)は該当なし(緩和で落ちた真陽性は0件、ただし
検証対象のサンプルに真の危険事例が含まれていなかったという限界あり)。B3(その他案3の
技術的不整合)は「仕様変更ではなく文脈量整合の修正」という設計報告書の主張と一致する
証拠を2件で確認したが、実際にPASSへ転じるかは¥0では未確定(有料再判定が必要、
約5〜10回・¥3〜8円、未実行)。

**Stage 2へ進める条件の充足状況**:
- Stage1: 真陽性リスクは無いが、実データでの適用事例が0件であり効果不明(適用しても
  実質的な変化が起きない可能性が高い)。
- Stage2: 6個体中6個体で一貫して適用対象となり、真陽性の誤緩和も確認されなかったが、
  サンプルに真の危険事例(数字・固有名詞入りのMAJOR)が無いため安全性の実証としては
  限定的。
- その他案3: 技術的不整合の存在は確認できたが、修正後に実際にPASSへ転じるかは
  有料再判定が必要(¥3〜8円、未実行)。

**Stage 3実生成の想定費用レンジ**: Phase 1b-04実測ベースで¥25.5(retryなし最良ケース)
〜¥78.0(leakage retryで2attempt discardした実測最悪ケース)。中間実測値としてn2の
¥53.6も参考。現残額¥40.1(上限¥230)との比較: 最良ケース(¥25.5)は残額内に収まるが、
実測レンジの上振れ(¥53.6〜¥78.0)は残額¥40.1を¥13.5〜¥37.9超過する。Stage 3実行前に
**予算延長(上限¥230の範囲内での追加確保、または上限自体の見直し)の要否をユーザーへ
確認する必要がある**(本タスクでは判断しない)。

**Fableへの報告事項(判断が必要)**:
1. 設計報告書e節107行目のNBCUniversal引用は実データと不一致(現行MINOR、MAJOR化した
   記録なし)。引用の訂正、または真に該当するMAJOR実例への差し替えが必要。
2. Stage1は実データでの適用事例が0件(コスト削減効果が実証されない)。Stage2を優先し、
   Stage1は「安全だが効果不明」として扱うか、適用条件の見直し(その場合は仕様変更を
   伴うため別途ユーザー判断)を検討するか、Fableの判断を仰ぐ。
3. その他案3の技術的不整合は2件確認できたが、修正後PASSの確証には有料再判定
   (¥3〜8円、約5〜10回)が必要。
4. A3/A4のとおり、真に危険な実例(数字・固有名詞入りMAJOR)を含む多様なテーマでの
   追加確認が望ましい(未実施)。

## Stage 1b

管理ID: EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE1B-AND-STAGE2(実行者sonnet-worker、
Git操作禁止・SSOT編集禁止、Writer実生成[Stage 3]は本タスクで未実行)。

一時ファイル: `docs/pm/ACTIVE_TASK_3V_FS_S2.md`。scratchpad(すべて`C:\Users\tensh\AppData\Local\Temp\claude\
...\scratchpad\`配下、Git未追跡): `stage1b1_context_recheck.py`(その他案3の有料確証、8 API呼び出し)、
`stage1b1_results.json`/`stage1b1_usage.json`(結果・token実測)、`stage1b2_synthetic_gate_test.py`/
`stage1b2_results.json`(合成true-positiveゲートテスト、¥0 offline)。

### 1b-1. その他案3(受理チェック文脈整合)の確証(¥9.75、8 API呼び出し)

**方法**: Production関数(`vfl01.run_deviation_check`・`local_rewrite.split_sentences`・
`locate_target_sentence`)をそのままimportし、判定基準・severity・promptテンプレートは一切変更せず、
引数(`window_text`)だけをメモリ内で差し替えて再実行した(コード変更なし)。対象は、Stage 1で確認した
「3回とも狭いwindowでLEDGER_DEVIATION、かつ同cycleの記事全体再判定のMAJOR一覧には不在」の2個体
(ablation_no_grounding_block_01_attempt1 cycle1、generalization_regression_01_run1_ng_review_required
cycle1)の最終rewrite文(attempt3のfinal_text)。各文について(a)現行と同じ狭いwindow(前後各1文、
`pre_editor_article.md`から再計算)、(b)生成promptと同じ`point_context`(section全体、対象文だけを
final_textへ置換)の両方で再判定し、加えて回帰確認用control 4件(元々narrow windowで1回合格していた
別のTension/Voice文)を`point_context`条件のみで再確認した(計8呼び出し、5〜10回の予算内)。

**結果(実測、非決定的なLLM応答であることに留意)**:

| 対象 | 条件 | overall_status | 対象文自体がdeviationとして検出されたか |
|---|---|---|---|
| A(ablation) | 狭いwindow(再現) | LEDGER_DEVIATION | Yes("owner must keep...")※狭いwindowのafter_ctx文 |
| A(ablation) | point_context(拡張) | LEDGER_DEVIATION | **No**(検出されたのは対象文と別の"NYC/EU"文) |
| B(run1ng) | 狭いwindow(再現) | LEDGER_DEVIATION | No(狭いwindowのafter_ctx="NYC yearly..."文が検出された) |
| B(run1ng) | point_context(拡張) | LEDGER_DEVIATION | **No**(検出されたのは"NYC yearly"文+別2文) |
| control 4件(point_context) | — | 3/4がLEDGER_DEVIATION(regression)、1/4がLEDGER_COMPLIANT | 4件とも対象文自体は非検出(検出されたのは常に別の隣接文) |

**確定した点(1b-1の当初の問い)**: A・Bいずれも、**対象文自体は`point_context`(拡張文脈)では
一度もdeviationとして検出されなかった**。これはStage 1報告書B3節の仮説(「文脈量を揃えるだけで
対象文の受理判定が変わる可能性がある」)を**支持する**結果であり、技術的不整合(生成に使う文脈と
受理チェックに使う文脈が異なるために、同じ文の評価が割れる)は**実データで確認できた**。

**新たな重要な発見(当初のB3節の想定にはなかった副作用)**: `_run_check_window`は「渡されたwindow
全体」に対する`overall_status`(1個でもMAJORがあればLEDGER_DEVIATION)を受理基準として使っている
(`er010_ledger_local_rewrite_09.py:189/199/208`)。windowを広げる(section全体`point_context`を渡す)と、
**対象文とは無関係な、そのsection内の既存の他の文(rewriteの対象ではない文)が、そのAPI呼び出し限りの
LLMサンプリングで新たにMAJORとして検出されることがある**。実測では、狭いwindowで既に合格していた
4件のcontrolのうち**3件が、point_contextへ拡張しただけで新たにLEDGER_DEVIATIONへ転じた**(regression)。
検出された問題はいずれも対象文ではなく、同じsection内の別文(例: "One company stopped an internal
tool after it rated women's résumés lower."という、Ledgerに無い企業事例文。これは複数個体のTensionで
繰り返し使われている定型的な一文で、Stage 1のサンプルには元々含まれていたが、Ledger Deviation
Checkerの応答は非決定的なため、狭いwindowでは偶然拾われず、広いwindowでは拾われた可能性が高い)。
さらに、この「隣接文による巻き添え」は拡張文脈に限った問題ではなく、**現行の狭いwindow設計にも
部分的に既に存在する**ことも判明した(B個体の狭いwindow再現で検出されたのは対象文ではなく
after_ctxの隣接文であり、対象文の前後1文がたまたま問題を含む場合、現行設計でも巻き添えが起きる)。

**1b-1の結論(STOP条件に直結する新知見)**: 「その他案3」が主張する技術的不整合そのもの
(対象文単独では広い文脈で問題視されなくなる)は実データで支持されたが、**設計文書c/e/h節・本タスク
2-Cが想定する実装方法(`window_text=point_context`に単純差し替え、`overall_status`で受理判定、
判定基準・prompt本体は不変)は、そのままでは安全に機能しない**。受理基準が「window全体に問題が
ないか」である限り、windowを広げるほど無関係な既存文の巻き添えで新規に不合格化するリスクが増え、
最悪の場合Local Rewriteの収束性を悪化させうる(狭いwindowより広いwindowの方が「合格しにくくなる」
という、意図と逆方向の副作用)。この副作用を避けるには、受理判定を「window全体のoverall_status」
ではなく「拡張windowが返す`deviations`のうち、`claim_in_article`が対象文(または対象文を含む
置換後テキスト)と一致するものだけを見る」という**target-sentence-matching方式への変更**が必要と
考えられるが、これは`run_check_window_fn`のインターフェース自体を変える設計変更であり、
「判定基準・severity・promptテンプレート本体は変えない」という2-Cの前提の範囲を超える。

### 1b-2. 合成真陽性テスト(¥0、offline)

段階1/段階2の後処理ゲート(DRAFT、未配線)をscratchpadで実装し、rule-basedゲートが確実に弾くべき
合成deviationで検証した。

**段階2(Tension緩和)、11件**: 設計文書c/e節の**文字どおりの記述**(`changed_actor`/
`unsupported_new_claim`のみを見る、他flagは不問、数字・固有名詞・制度・第三者行動の字面チェックのみ)
でゲートを実装したところ、**11件中6件で誤って緩和対象と判定された(取りこぼし)**:
`changed_number`/`changed_negation`/`changed_causality`/`changed_comparison`/`changed_time`のいずれかが
flagとして立っているが、文の字面には数字・固有名詞が現れない合成ケース(例: "The recruiter no longer
has any say in the process."[`changed_negation`のみ、字面は安全])で、字面チェックだけでは検出できず
誤って緩和されてしまった。b節が「常に厳格」と明記する5フラグ(`changed_number`/`changed_causality`/
`changed_negation`/`changed_comparison`/`changed_time`)を、字面チェックとは別にflag単位でも明示的に
除外条件へ追加した保守版ゲートを実装したところ、**11件中11件すべて正しく非該当(MAJOR維持)**となった
(取りこぼし0件)。段階1についても合成6件(Voice本文だが`changed_fact`/`changed_number`/`changed_actor`/
`unsupported_new_claim`併発、または第三者主語、またはsection誤り)を作成し、**6件すべて正しく
非該当**を確認した(取りこぼし0件、こちらは元の設計文書の記述どおりの厳格な条件[他8種すべてfalse]で
既に安全)。

**実データへの影響(重要な副次発見)**: Stage 1で「Stage2適用可否6/6該当」としていた実データの
Tension MAJOR 6件に、保守版ゲート(flag単位除外を追加したもの)を再適用したところ、**5/6のみが
引き続き該当**となった。除外された1件はablation個体の事例(design.md報告書d節の「事例5」、
3回上限まで収束せずhuman_review_requiredに至った、まさにStage 2が解決を想定していた最も深刻な
実例)であり、この文には`changed_negation`がflagとして立っていた。**つまり、b節の安全境界を
文字どおり厳格に(flag単位でも)適用すると、Stage 2は設計文書d節が「段階2まで実施して初めて
事例5型が解消される見込み」と述べていた、まさにその事例5自体は解消できない**(5/6の実例は
解消される見込みが残るが、最も深刻だった1件は残る)。

**1b-2の結論**: 「真陽性の取りこぼし0件」は**保守版ゲート(flag単位でのb節5項目除外を追加した
もの)を採用する場合に限り達成できる**。設計文書の文字どおりの記述(flagは`changed_actor`/
`unsupported_new_claim`のみを見る)のままでは取りこぼしが発生する(11件中6件)。

### 1b-3. 設計報告書のNBCUniversal引用訂正

`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-STRENGTH-DESIGN-01_REPORT.md`のe節107行目該当箇所に
「[2026-09-13訂正: 実データではMINOR、Stage 1で確認]」を注記済み(該当行のみ編集、他は無変更)。

### Stage 1b全体のSTOP条件該当有無

- 1b-1(技術的不整合の確定): **限定的に確定**(対象文単独の不整合は確認できたが、2-Cが前提とする
  「単純な引数差し替えで安全に修正できる」という想定は成立しないという新たな制約が判明)。
- 1b-2(真陽性の取りこぼし0件): **保守版ゲートを採用する場合のみ達成**(設計文書の文字どおりの
  記述では未達成)。
- Stage 2の発動条件文(「1b-1で技術的不整合が確定 かつ 1b-2で真陽性の取りこぼし0件の場合のみ実施」)
  を字面どおり判定すると両条件とも一応「満たす経路はある」が、**いずれも設計文書の記述をそのまま
  実装した場合には満たされず、本タスクの権限範囲(判定基準・prompt本体を変えない、既存の安全装置を
  独自判断で回避・無効化しない)を超えるゲート設計の修正(保守版flag除外の追加、target-sentence-
  matchingへの変更)を要する**。これはProduction Fact Safety機構の安全境界に関わる仕様修正であり、
  本タスクの範囲(既存設計の実装)を超える判断が必要なため、**Stage 2のコード実装(2-A〜2-F)は
  実行せずSTOPし、Fableへ報告する**(詳細は下記「## Stage 2」節)。

## Stage 2

**Status: 未実行(STOP、Fableへの判断待ち)**。上記1b-1/1b-2の新発見(2-Cの単純実装は隣接文巻き添えで
安全に機能しない、2-Bの設計文書文言どおりのゲートは取りこぼしが発生する)は、いずれも承認済み設計
文書(`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-STRENGTH-DESIGN-01_REPORT.md`)の記述と異なる追加の
安全設計判断(ゲート条件の強化、受理ロジックのtarget-sentence-matching化)を必要とするため、
Production Fact Safety機構(`er012_b_family_voices_writer_generic_01.py`のB-Family専用Ledger Deviation
Checker/Local Rewrite統合)への実際のコード変更は行わなかった。2-A(段階1)/2-D(数字任意化)/2-E
(整合確認)/2-F(offline Regression)についても、2-Bの安全なゲート定義が未確定な状態で着手すると
手戻りが大きいため、まとめて保留した。

**Fableへの報告事項(判断が必要)**:
1. 2-Bを実装する場合、設計文書の文字どおりの条件(`changed_actor`/`unsupported_new_claim`のみ判定)
   ではなく、b節の「常に厳格」5フラグ(`changed_number`/`changed_causality`/`changed_negation`/
   `changed_comparison`/`changed_time`)をflag単位でも明示的に除外する**保守版ゲーム**を採用する
   必要がある(1b-2で実証済み)。この場合、Stage 1が「Stage 2で解決見込み」としていたTension
   MAJOR 6件のうち、**5件は解決見込みが残るが、最も深刻だった事例(ablation、3回上限到達→
   human_review_required)は解決されない**(`changed_negation`のため)。この点は設計文書d節の
   想定と異なる結果であり、Stage 2実装の価値(コスト削減効果)を保守版ゲームでは過大評価しない
   よう申し添える。
2. 2-C(その他案3)は、単純な`window_text=point_context`差し替え+既存`overall_status`判定のままでは
   **安全に機能しない**(1b-1で確認、隣接文巻き添えによる新規regressionリスク)。実装するには
   受理ロジックを「拡張windowが返すdeviationsのうち対象文に一致するものだけを見る」方式へ変更する
   必要があり、これは`run_check_window_fn`インターフェースの設計変更を伴う(2-Cの前提「判定基準・
   severity不変」は維持できるが、受理判定の実装方式は「不変」ではなくなる)。この設計変更の是非は
   本タスクの権限範囲を超えるため、実装せず報告する。
3. 上記1・2を踏まえたうえで、(a)2-Bを保守版ゲームで、2-D(数字任意化、Checker変更不要で独立性が
   高い)を先行して実装する、(b)2-Cは追加設計(target-sentence-matching)を別タスクとして起票する、
   (c)Stage 2全体を見送り2-D単独のみ進める、等の進め方をFableに判断いただきたい。

## Stage 3準備

Stage 2が実行されていないため、Stage 3(実生成)の前提となる本番コード変更は存在しない。以下は
Stage 2が将来承認・実装された場合に備えた準備であり、現時点で実行するものではない。

- **想定費用レンジ**: Phase 1b-04実測ベースで¥25.5(retryなし最良ケース)〜¥78.0(leakage retryで
  2attempt discardした実測最悪ケース)。Stage 2(保守版ゲート採用時)の効果は「5/6のTension MAJORで
  Local Rewrite 1回分の再試行を削減できる可能性」程度であり、レンジの上限側を大きく引き下げる根拠には
  ならない(1b-2の結論を踏まえた保守的な見立て)。
- **確認項目チェックリスト(Stage 2実装後、実生成前に確認)**: (1) Fact Checker A' verdict、
  (2) Ledger Deviation Checkerの検出件数・severity内訳(Stage 2適用有無別)、(3) Local Rewriteの
  発動回数・収束cycle数、(4) Analytical Leakage Check全項目、(5) Voice本文が実際に一人称・
  Perspectiveらしく書けているか(数字任意化で内容が薄くならないか)、(6) Tensionの品質(役割合成が
  緩和されて説得力が落ちていないか)、(7) 新規false accept(緩和で本来MAJORにすべき文を見逃していないか、
  目視レビュー必須)、(8) 数字撤廃後の内容の厚み、(9) 3V方式の意味(Voices=Perspectives・賛否陣営化
  なし・単純合計では答えにならない)が保たれているか、(10) retry/fallbackが従来と同じ挙動を保つか、
  (11) A-Family(News/Discovery)への影響が皆無か(import/grep差分+既存offlineテストPASS)。
- **既存Regression(旧Trial-02採用版)との比較方法**: 同一Ledger・同一テーマで旧採用版記事と
  Stage 2適用後の新規生成記事を並べ、Tension文の言い回し・Local Rewrite発動有無・Fact Safety
  違反件数を比較する(既存の`qa/pairwise_voice_distinctness_check.json`等の既存QA成果物を再利用可能)。

## コスト評価

Stage 2が未実装のため、Before/After比較は**仮の試算(未検証)**である。

| 指標 | Before(Stage 1実測) | After(仮試算、保守版ゲート採用時) |
|---|---|---|
| 品質 | 現状どおり(hedge運任せ、事例5型は3回上限到達のリスクあり) | 5/6のTension MAJORでhedge不要化見込み、事例5型は未解決のまま残る |
| 安全性 | Fact Safety基準は現行のまま | 1b-2の保守版ゲート採用が前提(設計文書文言どおりの実装は不可、取りこぼしリスクあり) |
| 1記事あたりコスト | 平均¥43.1(レンジ¥24.1〜¥70.4) | 未実装のため実測不可。5/6のTension MAJORでLocal Rewrite 1回分(¥1〜3程度)を削減できる可能性があるが、隣接文巻き添えリスク(1b-1)を考慮すると2-Cは見送りが安全 |
| 100記事換算コスト | 平均約¥4,310(単純外挿) | 未実装のため試算不可(2-B単独なら微減、2-C見送りなら影響なし) |
| 処理時間 | 現状どおり | 2-Dは¥0・即日実装可能。2-A/2-Bは保守版ゲート実装+テスト追加が必要(規模未見積もり) |

## 費用

Stage 1: 本タスク(Stage 1)でのAPI呼び出しは0件(¥0)。既存の保存済みデータ・scratchpadスクリプトの
みで実施。

Stage 1b: 実測¥9.75(1b-1、8 API呼び出し、input=61,897 tokens・output=40,480 tokens、
`gpt-5.6-luna`、pricing_snapshot単価・¥160/$換算)。1b-2/1b-3は¥0(offline)。上限¥10以内。
Stage 2はコード実装を実行しなかったため追加API呼び出しなし。
