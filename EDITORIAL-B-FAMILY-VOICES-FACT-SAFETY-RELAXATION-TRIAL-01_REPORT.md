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

管理ID: EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3(実行者sonnet-worker)。
ユーザー正式判断(2026-09-13、Fable推奨(b)採用): 2-B保守版ゲート(5/6改善、ablation型
`changed_negation`併発は安全側で現行維持)+2-D(数字任意化)+必要Regressionを実装し、AI採用テーマ
1本でStage 3実生成・統合確認を行う(2-C[受理チェック文脈整合]は今回対象外、判定context拡張案も
対象外)。

### 実装(Production変更)

- `er012_b_family_editorial_type_registry_01.py`: `VOICE_FACT_SAFETY_GATE_MODE_DEFAULT = False`
  (既定OFF、Trial継続でありProduction正式採用ではない)を追加し、`b_family_voices`の
  `EDITORIAL_TYPES`エントリへ`voice_fact_safety_gate_mode`キーを追加。`is_voice_fact_safety_gate_mode_
  enabled()`を新設(`family=="B"`かつフラグTrueのときのみTrue、`is_fact_attribution_mode_enabled()`と
  同型のcode-level gating)。
- `er012_b_family_voices_writer_generic_01.py`:
  - `_apply_b_family_voice_safety_gate(parsed, article_text)`を新設。`vfl01.run_deviation_check()`が
    返す`parsed`(`_apply_deviation_post_hoc_validation`適用済み)に対し、MAJOR deviationのみを対象に
    段階1/段階2条件を判定し、該当すればMINORへ再分類してoverall_statusを再計算する(判定基準・
    prompt本体・`MAX_REWRITE_CYCLES`等の上限回数は無変更)。
    - 段階1(Voice本文hedge免除): `section∈{voice_1,2,3_body}`(`b1prod.split_six_voice_sections()`で
      `claim_in_article`の字面一致によりsectionを特定)、主語に一人称マーカー(`I`/`I'm`/`my`/`me`等、
      `_voice_gate_has_first_person_marker`)、flag集合が`{changed_scope, changed_certainty}`の部分集合
      (他8種flagが1つでもtrueなら対象外)。
    - 段階2(Tension役割合成の保守版緩和): `section=="tension_body"`、`{changed_actor,
      unsupported_new_claim}`のいずれかがtrue、かつ**b節「常に厳格」5フラグ
      (`changed_number`/`changed_causality`/`changed_negation`/`changed_comparison`/`changed_time`)が
      flag単位で1つもtrueでない**、かつ数字・固有名詞(大文字語)・制度名(NYC/EU/NBCUniversal等)・
      第三者具体的行動(`filed`/`sued`/`lawsuit`等)の字面が対象文に含まれない
      (`_voice_gate_has_surface_signal`)場合のみMINOR降格(Stage1b-2で11/11合成true-positive・
      取りこぼし0件を確認した保守版と同一ロジック)。
  - `run_ledger_deviation_and_local_rewrite()`内の2箇所(初回判定・cycle再判定)で、
    `if registry.is_voice_fact_safety_gate_mode_enabled(): deviation_result["parsed"] =
    _apply_b_family_voice_safety_gate(...)`のガード付きで呼ぶ(opt-in、既定OFF時は完全に無変化)。
  - 2-D: `_voice_card_block_text()`(:402-404相当)の「1つのVoiceにつき最大1つの具体的な数字だけを…
    織り込んでください」(必須要求)を「自然に人を主語にした話し言葉へ織り込める場合に限り…1つだけ
    使ってください。無理に数字を使う必要はなく、数字を使わずにその人の実感だけで書いても構いません」
    (任意)へ置換。あわせて末尾の参照文言の誤記(「上記【Evidenceは脇役であること】参照」→実際には
    テンプレート内でVoice Cardブロックより後ろに出現するため「下記」が正しい)を修正。上限規定
    (:251-256相当、「具体的な数字は最大1つだけにし」)・Ledger根拠要件は無変更。

**[PM-DELEGATION-NOTE 2026-09-13]** 委任文の入力節はb節「常に厳格」5フラグを
`[changed_number/changed_fact/changed_negation/changed_comparison/changed_time]`と表記していたが、
Stage1b-2で11/11合成true-positive・実データ5/6改善を実証したのは`changed_causality`版
(`changed_number/changed_causality/changed_negation/changed_comparison/changed_time`、b節本文・
`stage1b2_synthetic_gate_test.py`のALWAYS_STRICT_TENSION_FLAGSと一致)であり、`changed_fact`ではない。
実データのtension MAJOR 6件は全件`changed_fact=true`を伴うため、`changed_fact`を常に厳格側に含めると
段階2の適用対象が0/6になり、本委任文が明示的に確認を求める「5/6改善」の前提と矛盾する。本実装は
検証済みの`changed_causality`版を採用した(コード内コメントにも明記)。この不一致自体をFableへ
報告する(Production正式仕様の変更ではなく、委任文中の表記揺れの指摘)。

### テスト(2-E相当、¥0)

`er012_b_family_voices_writer_generic_01_test_01.py`へ14件追加(既存20件は無変更のままPASS、合計34件
PASS)。追加テスト内容: (1) opt-in既定OFF・`family=="B"`gating、(2) 段階1合成true-positive6件全件が
非該当のまま(取りこぼし0件)、(3) 段階2(保守版)合成true-positive11件全件が非該当のまま(取りこぼし
0件)、(4) 段階1/2の正例(実際に緩和対象になること)、(5) `_apply_b_family_voice_safety_gate()`の
end-to-end(section特定+ゲート適用+overall_status再計算)、(6)
`run_ledger_deviation_and_local_rewrite()`を`vfl01.run_deviation_check`mock化で呼び、opt-in OFF時は
現行どおりLocal Rewriteが複数回発火し(mock呼び出し4回)、ON時はMINOR降格によりLocal Rewriteが
一度も発火しない(mock呼び出し1回)ことを確認、(7) 2-D(数字任意化文言・参照修正・上限規定不変)。

既存offlineテストの回帰確認(すべてPASS、無変更):
`er012_b_family_voices_writer_generic_01_test_01.py`(34件)+
`er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`(56件)+
`er012_open131_fact_attribution_production_wiring_01_test_01.py`(4件)=合計94件PASS(実測、
`.venv/Scripts/python.exe -m unittest`)。A-Family offline: `er010_n9_production_integration_09_test_01.py`
33件PASS(無変更)。A-Family呼び出し元(`er003_v1_n3_01_articles_generate.py`)は
`voice_fact_safety_gate_mode`/`is_voice_fact_safety_gate_mode_enabled`/
`er012_b_family_voices_writer_generic_01`のいずれも参照しないことをgrepで確認(0件)。

### 2-F. offline Regression(¥0、Production関数を実際にimportして適用)

scratchpad`stage2_2f_offline_regression.py`が、Stage1が既に機械分類済みの実データ(最終ledger 4件+
cycle内MAJOR 17件、計21件、6個体×複数attempt/cycle、うち1個体[run1ng]は参考個体)へ、
**scratchpadの複製ロジックではなくProduction関数`wg._voice_gate_stage1_eligible`/
`wg._voice_gate_stage2_eligible`をそのままimportして**適用し、Before(実際の記録severity)/
After(ゲート適用後)を比較した。

| 指標 | 値 |
|---|---|
| Before MAJOR件数 | 17件(cycle内MAJOR全件、最終ledger4件は元々MINOR) |
| After MAJOR件数 | 12件 |
| 降格件数(MAJOR→MINOR) | **5件、すべてtension_body**(`trial02_attempt2`/`regression_attempt1`/
`regression_attempt2`/`regression_attempt3`/`regression_run1ng_attempt1`のcycle1 Tension非対称性文) |
| 降格されなかった理由 | Voice本文10件(全件`changed_fact`併発のため段階1対象外、0/10=Stage1と同じ)、
hook本文1件(対象外section)、tension残り1件(`ablation_attempt1`、`changed_negation`併発のため
段階2対象外)、`regression_run1ng_attempt1`cycle2のtension文(NYC言及、`changed_causality`併発のため
対象外、字面除外[institution]でも独立に除外される) |

Stage1b-2のoffline合成テスト(11/11・6/6取りこぼし0件)およびStage1が予測した「5/6改善(ablation型
`changed_negation`併発1件のみ未解決)」と**Production関数の実測が完全一致**した。真陽性(数字・固有
名詞・第三者具体行動を伴うMAJOR)は今回のサンプルにも存在せず(Stage1のA3節既知の限界を継承)、
`ablation_attempt1`のtension文・`run1ng`cycle2のtension文(NYC言及)は狙いどおり厳格判定のまま維持
された(実文は下記Stage 3節で人手照合)。詳細JSON:
`stage2_2f_results.json`(scratchpad、Git未追跡)。

## Stage 3

管理ID: EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3。想定費用¥25.5〜78
(事前記載どおり、RESULT_PACKET_3V_FS_S3.mdへも記載)。実測合計¥56.49(後述)。

### 実行方法

`voice_fact_safety_gate_mode`はProduction既定Falseのまま(コード変更なし)、scratchpadドライバ
スクリプトが`registry.EDITORIAL_TYPES["b_family_voices"]["voice_fact_safety_gate_mode"] = True`を
一時的に上書きし(`is_fact_attribution_mode_enabled`の既存テスト手法[monkeypatch]と同型)、
`er012_b_family_voices_writer_generic_01.run_writer_stage_generic(theme_ai_screening.THEME_CONFIG,
"er012_output/fact_safety_relaxation_trial_01/stage3_gate_on_run01")`を呼び出した(新経路
generic+theme、AI採用選考テーマ、既存Ledger)。

**技術的中断と再開(Fact Safety判定ロジックとは無関係)**: attempt1はFact Checker A' PASS→Ledger
Deviation 1件MAJOR検出→Local Rewrite 1attemptで解決→cycle再判定LEDGER_COMPLIANTまで正常完走した
直後、Directional Fact Precheckのログ行に含まれる半角記号(円記号)をWindowsコンソール(cp932)へ
printしようとして`UnicodeEncodeError`でクラッシュした(Production側の既存print文の話であり、
Ledger Deviation Checker・本ゲートの判定ロジックとは無関係。実測¥23.09が既に消費済みだったため、
Writerを再生成せずattempt1の保存済み成果物[article.md/fact_qa.json/ledger_deviation.json/
local_rewrite_*.json等]をそのまま再利用し、Production関数[`dfp.audit_article_directional_facts`/
`run_analytical_leakage_check_3v`等]をそのまま呼んで残り手順を完走させた[`stage3_resume_driver.py`、
Git未追跡]。無駄なAPI再課金を避けるための処置であり、Writer生成をやり直していないため「追加の
実生成」には該当しない)。

### 結果(実測)

| 段階 | attempt1 | attempt2 |
|---|---|---|
| Fact Checker A' verdict | PASS | REVIEW_REQUIRED(FAILではないため即NG化はしない、既存仕様どおり) |
| Ledger Deviation(初回) | MAJOR 1件(`Power is uneven: the applicant cannot set the process, the recruiter operates but does not choose the tool, and the owner chooses and carries responsibility.`、flags=changed_fact/changed_actor/**changed_negation**/unsupported_new_claim) | MAJOR 2件(cycle1: causality系2件、cycle2: fact系2件) |
| ゲート適用結果 | **非該当(MAJOR維持)**: `changed_negation`が常に厳格5フラグに該当するため段階2対象外(狙いどおり保守的) | 4件とも非該当(cycle1は`changed_causality`併発、cycle2は`changed_fact`併発でVoice本文のため段階1対象外)。**本Stage3実生成では段階1/2ゲートは0件適用(発火せず)** |
| Local Rewrite | 1 cycle・1 attempt で解決(hedge化) | cycle1: item1は3attempt後もresolved=False(human_review_required=True)、item2は2attemptで解決。cycle2: item1は3attempt後もresolved=False(human_review_required=True)、item2は1attemptで解決。cycle2再判定はMAJOR=0(overall LEDGER_COMPLIANT)だが、**cycle内でhuman_review_requiredが立った記録が残るため**最終`any_human_review_required=True` |
| Analytical Leakage Check | voice_3が`leak_evidence_subject`/`leak_numbers_foreground`/`leak_discovery_syntax`でFAIL(該当文: "AI is tempting because some reports show hiring moving from weeks to days, while others report lower costs."、**数字を含まないにもかかわらず**"reports show..."という報告主語構文でFAILした) | (到達せず、Ledger起因のNG_REVIEW_REQUIREDで打ち切り) |
| 最終status | (attempt2へ) | **NG_REVIEW_REQUIRED**(`any_human_review_required=True`のため) |

**全体結果**: 既存のretry機構(人為介入なし)が正常に動作し、attempt1のLeakage FAILを受けてattempt2へ
自動移行、attempt2でLedger起因のhuman_review_requiredにより最終`NG_REVIEW_REQUIRED`で確定した。
これは**新しいfailure modeではない**(Stage1データの`ablation_no_grounding_block_01`/
`generalization_regression_01_run1_ng_review_required`個体で既に確認済みの、3回上限到達→
human_review_required→discardという既存の安全側の挙動と同型。原因flagも`changed_causality`/
`changed_fact`であり、いずれも本ゲートの緩和対象[`changed_scope`/`changed_certainty`/保守版
`changed_actor`・`unsupported_new_claim`]の**外側**)。追加runは実施せずSTOPする(本タスクの
制約どおり)。

### 確認項目(委任文の必須項目)

1. **Fact Checker/Ledger Deviation(適用件数・実文)**: 上記のとおり実測。本Stage3実生成では
   ゲート適用0件(発火せず)。理由は生成テキストの非決定性(LLMの出力が毎回変わる)により、今回の
   Tension非対称性文が偶然`changed_negation`(attempt1)・`changed_causality`(attempt2)を伴う表現に
   なったため(Stage1データの5/6は`changed_actor`/`unsupported_new_claim`のみで`changed_negation`等を
   伴わない表現だった)。**ゲート自体の効果は2-Fのoffline Regression(Production関数で5/6実証)で
   裏付けられているが、本Stage3の1サンプルではその効果が可視化されなかった**(サンプル数1の
   ばらつきとして正直に報告する。過大に成功と主張しない)。
2. **Local Rewrite回数・収束性**: attempt1は1cycle・1attemptで収束(既存機構どおり)。attempt2は
   2cycle実施も1項目(causality系→fact系、実際には別文)が両cycleとも3attempt以内に収束せず
   human_review_required(既存の収束限界、ゲート無関係)。
3. **Analytical Leakage Check**: attempt1 voice_3 FAIL(上記)。**2-D(数字任意化)の限界**:
   voice_1〜3本文はいずれも数字ゼロ(2-Dの意図どおり、後述4参照)だったにもかかわらず、voice_3は
   「一部の報告は〜と示す("some reports show...")」という報告主語構文でLeakage FAILとなった。
   **数字を外すだけでは`leak_evidence_subject`型の漏洩を防げない**(Evidenceを主語にする構文自体が
   問題であり、数字の有無とは独立)。既存のLeakage Check+corrective note機構が正しく検出し、
   既存のretry機構どおりattempt2へ自動移行した(安全側の動作、regressionではない)。
4. **Voice本文のPerspectiveらしさ・数字撤廃後の内容の厚み**: attempt1のvoice_1/2/3本文はいずれも
   **数字0個**(旧prompt[必須]では各Voiceに最低1個含まれていたのと対照的)。語数はvoice_1=87語/
   voice_2=90語/voice_3=85語(旧Trial-02採用版: 81/91/82語、旧regression_01採用版: 84/81/83語)と、
   数字を使わずとも既存2本と同水準を維持。内容は一人称・具体的場面描写を保持("I cannot ignore a
   woman's account of that experience"、"I saw a public notice showing that an independent review…
   had been carried out"等、Ledger evidenceへ具体的に紐づく)。**内容が薄くなった徴候は無い**。
5. **Tension品質・3V方式の意味**: attempt1のTension文("Power is uneven: the applicant cannot set the
   process, the recruiter operates but does not choose the tool, and the owner chooses and carries
   responsibility.")は3人の役割非対称性を単一文で統合しており、旧2本と同型の構造(3人の合理性を
   単純に足しても答えにならない、という3V方式の中核目的)を保持。ただし本サンプルでは
   `changed_negation`のためゲート非該当となり、既存hedge機構で解決(1attempt)。
6. **retry/fallbackが従来と同じ挙動か(コード経路確認)**: 上記のとおり、Leakage FAIL→corrective
   note→attempt2という既存ループ、Ledger human_review_required→NG_REVIEW_REQUIREDという既存の
   discardロジックは、ゲートON状態でも完全に従来どおり動作した(コード上も`if registry.is_voice_
   fact_safety_gate_mode_enabled():`の外側は無変更)。
7. **A-Family無影響**: 上記テスト節のとおりgrep 0件・A-Family offlineテスト33件PASS(無変更)。
8. **必須5項目**(実測、`stage3_metrics.txt`参照、scratchpad):
   - section別語数(hook/voice_1/2/3/tension/closing、目安Hook45〜55語・Voice各70〜85語・
     Tension75〜90語・Closing45〜55語、design.md B-6 soft target): attempt1={hook:54, voice_1:87,
     voice_2:90, voice_3:85, tension:132, closing:55}合計503語。旧Trial-02採用版={60,81,91,82,132,54}
     合計500語、旧regression_01採用版={50,84,81,83,133,60}合計491語。**3本とも同様にsoft target
     (410〜450語)をやや上回る水準で、2-D適用後も傾向は変化していない**(数字任意化による顕著な
     短縮・増加は無し)。Tensionが3本とも130語超とsoft target上限(90語)を上回るのは既存の傾向で
     あり、本Trialによる新規劣化ではない。
   - near-dup最大ratio(SequenceMatcher、Tension本文同士・記事全体・対応Voice同士のペアワイズ):
     Tension本文: stage3 vs 旧Trial-02=0.075、stage3 vs 旧regression_01=0.084、旧Trial-02 vs
     旧regression_01=0.105。記事全体: 0.129/0.123/0.161。**最大ratio=0.161(旧2本同士)、いずれも
     定型句の使い回しと呼べる水準(目安0.8以上)には遠く及ばない**(3本とも独立した言い回し)。
   - caveat文(hedge語`can/may/might/some/sometimes/in some cases`等)カウント: stage3=10語、
     旧Trial-02採用版=10語、旧regression_01採用版=11語。**同水準、過剰hedge化・hedge不足化どちらも
     見られない**。
   - 記事間定型句類似(上記near-dup ratioで代替、3本間で最大0.161、定型句依存の兆候なし)。
   - 音声: 未実施(Writerのみ、TTSは呼んでいない。本Trialの範囲外)。
9. **旧Trial-02採用版との比較表**: 上記8の表に統合(word count/hedge count/near-dup ratio)。

### false accept人手照合(2-Fで降格された5件の実文、目視確認)

| 個体 | 実文 | flags | 判定 |
|---|---|---|---|
| trial02_attempt2 | "The applicant cannot choose the system; the recruiter runs it but cannot adopt it; the owner decides." | changed_actor/certainty/fact/scope/unsupported_new_claim | 数字・固有名詞・制度名・第三者具体的行動なし、役割合成のみ→**緩和妥当** |
| regression_attempt1 | "Power is unequal: the applicant is judged, the recruiter runs a tool without choosing it, and the owner chooses it and carries the result." | changed_actor/fact/scope/unsupported_new_claim | 同上→**緩和妥当** |
| regression_attempt2 | "Their power is unequal: the applicant cannot choose the system, the recruiter runs it without final authority, and the owner approves its use." | changed_actor/certainty/fact/scope/unsupported_new_claim | 同上→**緩和妥当** |
| regression_attempt3 | "Power is uneven: the applicant cannot choose, the recruiter operates, and the owner decides." | changed_actor/certainty/fact/scope/unsupported_new_claim | 同上→**緩和妥当** |
| regression_run1ng_attempt1(cycle1) | "Their power is uneven: the applicant is judged, the recruiter runs a tool without choosing it, and the owner decides whether to use it." | changed_actor/certainty/fact/unsupported_new_claim | 同上→**緩和妥当** |

比較(非該当のまま維持、意図どおり): `ablation_attempt1`の同型文(`changed_negation`併発)、
`regression_run1ng_attempt1`cycle2の"New York City's yearly bias check and notice rule adds work
for the recruiter…"(`changed_causality`併発+NYC言及)はいずれも**MAJOR維持**(false acceptなし)。

## コスト評価

| 指標 | Before(Stage1実測、緩和なし) | After(Stage2実装+Stage3実測、gate ON) |
|---|---|---|
| 品質 | hedge運任せ、ablation型は3回上限到達リスクあり | Stage3実測では本ゲート発火0件(生成テキストの非決定性)。offline Regression(2-F、Production関数)では5/6のTension MAJORでhedge不要化を確認 |
| 安全性 | Fact Safety基準は現行のまま | 保守版ゲート(5/6実証、ablation型は非該当のまま維持)。false accept 0件(2-Fの5件全件を目視照合、A-Family無影響を93+33件のoffline test PASSで確認) |
| 1記事あたりコスト(Fact Safety関連、Writer除く) | 平均¥43.1(レンジ¥24.1〜¥70.4、Stage1実測) | Stage3実測¥56.49(attempt1完走[¥23.09]+attempt2完走まで[追加¥33.4]、2attempt要のケース。Beforeレンジ¥24.1〜¥70.4の範囲内) |
| 100記事換算コスト | 平均約¥4,310(単純外挙) | 2-Bのコスト削減効果は「Tension非対称性文が偶然ゲート対象パターン[changed_actor/unsupported_new_claimのみ]になった場合のみhedge 1回分[¥1〜3程度]を削減」に限定される。今回のStage3 1サンプルでは非該当だったため削減0(このサンプルでは) |
| 処理時間 | 現状どおり | 2-D実装+テスト追加は完了(即日)。2-A/2-B実装+テスト34件PASSは完了。Stage3実生成は約10分(attempt1+attempt2、Web検索含む) |

## Gate 1判定材料

判定語(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFableが確定する。本節は判定材料の提示のみ。

- **安全性**: 2-A/2-B(保守版ゲート)はStage1b-2の合成true-positive17件(6+11)全件で取りこぼし0件、
  2-Fのoffline Regression(Production関数)で実データ5/6改善・false accept 0件(5件全件を目視照合)、
  Stage3実生成でも(発火0件ながら)非該当ケースが正しく非該当のまま維持された(`changed_negation`/
  `changed_causality`は狙いどおり常に厳格)。A-Family(News/Discovery)への影響は0件
  (import/grep差分+既存offlineテスト33件PASS)。**安全側の設計は維持されている**。
- **効果の限定性**: Stage3実生成1本では本ゲートは発火0件だった(生成テキストの非決定性により、
  たまたま今回のTension文が`changed_negation`/`changed_causality`を伴う表現になったため)。効果自体は
  offline Regression(Production関数、5/6)で裏付けられるが、**実生成1本のみでは効果を直接観測
  できなかった**(過大評価しないよう明記)。
- **新しい発見(2-D単独の限界)**: 数字撤廃(2-D)だけでは`leak_evidence_subject`型のAnalytical
  Leakage漏洩を防げない(voice_3が数字ゼロでも"reports show..."構文でFAILした)。既存のLeakage
  Check+retry機構は正しく機能した(regressionではない)が、2-Dの効果は「数字の強制」問題の解決に
  限定され、「Evidence主語構文」問題は別課題として残る(本タスクの範囲外、報告のみ)。
- **Stage3の最終結果**: NG_REVIEW_REQUIRED(既存の安全側discardロジックによる、Stage1の
  ablation/run1ng個体と同型の既知の残余リスク。本ゲートが原因ではない)。
- **委任文とSSOTの不一致**: b節「常に厳格」5フラグの表記(`changed_fact`か`changed_causality`か)に
  ついて、委任文とStage1b-2実証結果に不一致があった。本実装は実証済みの`changed_causality`版を
  採用し、Fableへ報告(上記PM-DELEGATION-NOTE参照)。
- **費用**: 本管理ID累計¥66.24(Stage1b ¥9.75+Stage3 ¥56.49)、上限¥310以内。

## 費用

Stage 1: 本タスク(Stage 1)でのAPI呼び出しは0件(¥0)。既存の保存済みデータ・scratchpadスクリプトの
みで実施。

Stage 1b: 実測¥9.75(1b-1、8 API呼び出し、input=61,897 tokens・output=40,480 tokens、
`gpt-5.6-luna`、pricing_snapshot単価・¥160/$換算)。1b-2/1b-3は¥0(offline)。上限¥10以内。

Stage 2: 実装・テスト・2-F offline Regressionはすべて¥0(API呼び出しなし)。

Stage 3: 実測¥56.49(32 API呼び出し、input=403,345 tokens・output=110,279 tokens・
cached_input=4,471 tokens・web_search=14回、`gpt-5.6-luna`、pricing_snapshot単価・¥160/$換算。
attempt1完走分¥23.09+attempt2完走までの追加分¥33.4の合計。attempt1完走後のUnicodeEncodeError
[Production側の既存print文起因、判定ロジックとは無関係]によりプロセスが中断したため、Writerを
再生成せず保存済み成果物を再利用してresumeした[詳細は上記Stage3節])。

**本管理ID累計: ¥66.24(¥9.75+¥56.49)。上限¥310以内(残額約¥243.76)。追加runは実施せずSTOP。**

## SSOT追記文案(sonnet-workerはSSOTを直接編集しない。Fable/sandwich-pm側での反映用文案)

### CURRENT_SPEC.md(3V節への追記案)

> B-Family Voices 3V: Fact Safety保守版ゲート(段階1/段階2、`voice_fact_safety_gate_mode`、既定OFF、
> `family=="B"`限定opt-in)を`er012_b_family_voices_writer_generic_01.py`/
> `er012_b_family_editorial_type_registry_01.py`へ実装済み(2026-09-13、
> EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3)。Trial継続の承認であり
> `APPROVED_FOR_PRODUCTION`ではない(既定OFFのままcommit)。2-D(Voice内数字の「必須」要求撤廃、
> 上限規定は不変)も同時実装。詳細・実測は当該REPORT参照。

### OPEN_ITEMS.md(OPEN-120への追記案)

> **追記(2026-09-13、EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3)**:
> Stage2(保守版Fact Safetyゲート実装+2-D数字任意化)完了、offline Regression(Production関数)で
> 実データ5/6改善・false accept 0件を確認。Stage3実生成1本(AI採用選考テーマ)はattempt1完走
> (Fact Checker PASS→Ledger 1件MAJOR→hedge 1回で解決)後、Leakage Check(voice_3、数字ゼロでも
> `leak_evidence_subject`型でFAIL)により既存retryでattempt2へ自動移行、attempt2はLedger起因の
> human_review_requiredで最終`NG_REVIEW_REQUIRED`(Stage1のablation/run1ng個体と同型の既知の
> 残余リスク、本ゲートは無関係、本ゲート自体はStage3では0件発火)。実測費用¥66.24(Stage1b+Stage3
> 合算、上限¥310以内)。新知見: 2-D単独では`leak_evidence_subject`型Leakageは防げない(数字撤廃と
> Evidence主語構文は別問題)。Gate1判定はFable/ユーザー判断待ち(`USER_DECISION_REQUIRED`候補)。
> 根拠: `EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`(Stage2/Stage3/
> コスト評価/Gate1判定材料節)。

### DECISION_LOG.md(新規エントリ案)

> **2026-09-13 EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3**:
> ユーザー正式判断(Fable推奨(b)採用、2026-09-13)に基づき、B-Family Voices 3V限定の保守版Fact
> Safetyゲート(段階1: Voice本文hedge免除、段階2: Tension役割合成の`changed_actor`/
> `unsupported_new_claim`緩和[b節「常に厳格」5フラグ`changed_number`/`changed_causality`/
> `changed_negation`/`changed_comparison`/`changed_time`はflag単位で除外、数字・固有名詞・制度名・
> 第三者具体的行動は字面でも除外]、既定OFF opt-in)+Voice内数字の「必須」要求撤廃(上限規定は不変)を
> 実装。offline Regression(Production関数)で実データ5/6改善・false accept 0件を確認。Stage3実生成
> 1本は既存retry機構により最終`NG_REVIEW_REQUIRED`(本ゲートとは無関係の既知の残余リスク)。
> 判定context拡張案(2-C)は本ラウンド対象外のまま。Status: `USER_DECISION_REQUIRED`
> (Gate1判定はFableが確定)。委任文の入力節記載(b節5フラグの表記)とStage1b-2実証結果に不一致が
> あり、実装は実証済みの`changed_causality`版を採用(報告済み)。根拠:
> `EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`。
