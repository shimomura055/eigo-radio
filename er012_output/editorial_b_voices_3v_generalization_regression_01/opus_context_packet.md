# Opus Context Packet — EDITORIAL-B-FAMILY-VOICES-3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01

作成: sonnet-worker(packet作成専用委任、read-only)。テンプレート:
`docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。元REPORT:
`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_REPORT.md`
(931行、修正1〜3回目まで含む)。本packetはこのREPORT全文の代わりに
Opusへ渡すことを想定する(Opusは本packetのみを読み、Progressive
Disclosure以外でREPORT本体・元artifact全量を読まない前提)。

---

## (a) 論点(限定)

1. Analytical Leakage(Voice本文の主語が統計・調査寄りになる)が新経路
   (attempt3=1件、N+1=2件)で2/2回発生し、旧Trial-02(0件)と比較して
   系統的劣化と言えるか、それとも既存retry設計(全文書き直し×3回上限)
   下でのrun分散(旧Trial-02自身もattempt1で同型失敗→attempt2で自己修正
   していた実績あり)の範囲内か。
2. Fable仮説「`COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`(体験claimの
   根拠付け原則)の文言が統計調・分析調を誘発している」は、ablation
   (同原則をmonkeypatchで無効化)で検証できたか。検証できなかった場合
   (今回はLedger側の別の安全装置が先に発動しLeakage Checkに到達しな
   かった)、Leakage Checkまで到達させる代替のablation設計はあるか。
3. ablationで観測されたLedger逸脱4件(4個体中最多、うち1件は
   `human_review_required=true`のままNG_REVIEW_REQUIRED)は、原則除去の
   系統的効果(原則がVoice本文以外の地の文の確信度も間接的に抑制して
   いた副次効果)か、n=1のrun分散の外れ値か。
4. Sonnetが提示した3つの文言修正案(9-6節、意味を変えない範囲)は
   妥当か。他に見落としている原因候補(例: 汎用テンプレートの
   Voice Cardデータそのもの[49%/90%統計の提示位置]、Fact Attribution
   Modeとの相互作用等)はあるか。
5. 本Regressionを「PASS(旧と同等)」と判定できる条件は何か。スマホ
   使用制限テーマ等、次のテーマへ進む前に必要な最小限の追加検証
   (費用付き、既存上限¥230に対し残り約¥40.1)は何か。
6. 3V方式の意味(Voices=3人のPerspectives、賛否の二元論ではない)が、
   汎用テンプレート化によって損なわれていないか(Tension/Closingの
   修辞的骨格が旧・新1回目・新N+1・ablationの4個体で共通して現れている
   ことをどう解釈すべきか)。

### 論点と材料の対応チェック(必須)

| 論点番号 | 必要な材料 | (b)/(c)のどこにあるか | 不足時の扱い |
|---|---|---|---|
| 1 | 4記事全文、Leakage Check実文4件(旧attempt1含む)、attempt推移表 | (b)「記事本文」「Leakage Check実文」節 | 不足なし |
| 2 | ablation実行方法・結果(NG_REVIEW_REQUIREDで停止した経緯)、Leakage Check未実施の理由 | (b)「Ledger逸脱実文」節、(c)`run_voices_pattern_3v`早期停止分岐 | 不足なし |
| 3 | ablation Ledger逸脱4件の実文・severity・resolved状況 | (b)「Ledger逸脱実文」節 | 不足なし。ただしn=1のため追加ablation(N+2)は未実施(費用理由) |
| 4 | prompt diff該当ブロック全文、修正案3つの転記 | (b)「prompt構成」節、(d)Sonnet要約 | 不足なし |
| 5 | 必須5項目表4run分、費用実測、残予算 | (b)「必須5項目表」「費用」節 | 不足なし |
| 6 | Closing/Hookの修辞骨格実文比較(4個体) | (b)「定型句」節 | 不足なし |

---

## (b) 主要数値表・要点

### 要点(5行以内)

1. AI採用選考テーマ(旧Trial-02、承認済み)を汎用Writerテンプレート
   経路で3回再生成(新1回目・新N+1・ablation)した結果、Fact Checker
   PASS・Ledger LEDGER_COMPLIANTは概ね維持されたが、Analytical
   Leakage Checkのflagged項目は新2本(attempt3=1件、N+1=2件)で
   旧(0件)より悪化した。
2. ablationは「体験claim根拠付け原則を無効化してLeakageが再現するか」
   を検証する設計だったが、Ledger Local Rewrite側の既存安全装置
   (human_review_required判定)がより早く発動しNG_REVIEW_REQUIREDで
   停止したため、Leakage Checkに到達せず当初の設問には未回答。
3. ablation実行時にLedger逸脱4件(4個体中最多)が観測されたが、n=1で
   あり原則除去の系統的効果かrun分散の外れ値かは切り分け不能。
4. prompt全文diffでは、体験claim原則の文言はほぼ同一(意味を変える
   差分なし)で、1件の転記漏れ(Tension外部制約列挙禁止の再掲文)を
   発見・復元済み(offlineテスト48項目PASS、¥0)。誤記1件(「上記」
   should be「下記」、参照先の見出し自体は削除されていない)も発見
   したが影響は低いと判断し未修正。
5. 費用は本管理ID累計約¥189.9(Fable承認済み上限¥230、残り約¥40.1)。
   N+2規模の追加ablationやLeakage到達までの再設計には追加予算承認が
   必要。Sonnet委任ループは既に上限(初回+3回、計4回)に到達している。

### 結果表(4run比較)

| 項目 | 旧Trial-02(採用attempt2) | 新1回目(attempt3、採用) | 新N+1(n2_attempt3、採用) | ablation(attempt1、NG停止) |
|---|---|---|---|---|
| 最終status | OK | OK(flagged残存) | OK(flagged残存) | NG_REVIEW_REQUIRED |
| Fact Checker verdict | PASS | PASS | REVIEW_REQUIRED(3件、地の文の一般化断定) | PASS |
| Ledger overall_status | LEDGER_COMPLIANT(deviations 0) | LEDGER_COMPLIANT(deviations 1、MINOR changed_actor) | LEDGER_COMPLIANT(deviations 0) | LEDGER_COMPLIANT(最終再判定、ただし履歴上human_review_required=true 1件が残りNG判定) |
| Local Rewrite発動 | 1回(cycle1、MAJOR、resolved=true) | 1回(cycle1、MAJOR、resolved=true) | 0回 | 2サイクル、NG項目5件(3+2)、うち1件`resolved=false`/`human_review_required=true` |
| Analytical Leakage any_flagged | False(0件) | True(1件、voice_1) | True(2件、voice_1+voice_2) | 未実施(N/A、Ledger早期停止のため到達せず) |
| Directional Fact Precheck | PASS(results=[]) | DIRECTION_REVIEW_REQUIRED(1件、30%表現) | PASS(results=[]、全attempt) | N/A(未到達) |
| Point Overlap QA最大比率(閾値0.4) | 0.163(voice系ペア、下記(b)near-duplicate節参照) | 0.158(voice_1_vs_hook) | 0.154 | 0.143(voice_1_vs_hook) |
| Writer attempt数(上限3) | 2/3(attempt2で確定) | 3/3(上限到達) | 3/3(上限到達) | 1/3(早期break、既存仕様どおり) |
| metrics.json word_count | 488 | 462 | 470 | 517(局所Rewrite前の値。局所Rewrite後の最終語数はsummary.json記載569、11-5節注記のとおり別計測方式で簡易合計565) |

---

### 記事本文(全文転記、4本)

#### 旧Trial-02(採用版、`er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/article.md`)

```
# When AI Sits Between a Job and a Person

## The Question

A job application may pass through software before a person sees it. A résumé can be screened, a personality test scored, or a video judged by facial expressions, voice, and gestures. The applicant sees a career opportunity. The recruiter sees a crowded queue. The owner sees a decision that can affect the company. One screen creates three different moments.

### The Applicant's Voice: Under the Camera

I speak to a camera while software scores my tone, face, and gestures. I have read about a woman who did well on a skills test but was rejected after AI rated her gestures and facial expressions low. She later faced long-term unemployment. I also know of an applicant who said AI scored his reliability and honesty without an opt-out or a way to challenge the result. I want my ability and character seen, not reduced to a score.

### Another Voice: The Recruiter

I start with résumés and an AI tool that sorts them, schedules interviews, and matches people to jobs. It helps when applications arrive faster than my team can read them. But the work does not end with a score. I may prepare a plain summary of a fairness check and answer candidates' questions; one company's public notice makes that duty concrete. I also judge AI-written résumés: useful skill, or too little effort? I run the tool, but I do not decide whether the company adopts it.

### A Third Voice: The Business Owner

Each week, I look at the hiring dashboard: time, cost, and the people we still need. If hiring slows, the work does not wait. I have seen reports of faster hiring and lower costs after AI. That is why I may keep using it. But news of a tool that rated women lower makes me look twice at my own choice. If it is questioned, my name is attached. I am protecting the company's future while carrying the risk of being wrong.

## Why They See It Differently

All three want the right person in the right job. But the applicant may lose a fair chance, the recruiter must keep work moving and explain it, and the owner must keep the company running and answer for the choice. The applicant cannot choose the system; the recruiter runs it and may also help decide whether to adopt it; the owner may make the final call. Outside limits narrow all three roles. In New York City, an employer needs a recent fairness check, a public summary, and notice before using an automated hiring tool. The recruiter cannot use it silently, the owner cannot rely on speed alone, and the applicant still cannot control the score. One company stopped a tool after it rated women lower. Their views cannot simply make one answer.

## What This Question Really Means

This is not merely a question about whether a machine can read a résumé or a face. It is about who defines a fair chance, who must explain it, and who carries the consequences when it fails. Hiring is not just a tool choice. It is a question of power, proof, and responsibility.
```

セクション別語数(REPORT 4-4節、簡易regexカウント): Hook 59 / Voice1 79 /
Voice2 86 / Voice3 82 / Tension 132 / Closing 53 / 合計491。

#### 新1回目(採用版attempt3、`er012_output/editorial_b_voices_3v_generalization_regression_01_attempt3/article.md`)

```
# When AI Enters the Hiring Room

## The Question

An application is sent. A video answer is recorded. Software may sort the resume, score a personality test, or read a face and a voice. By September 2026, this is a real part of hiring. It brings three people into the same scene: the applicant, the recruiter, and the business owner.

### The applicant's voice: under the camera

I watch the camera light while software studies my tone, face, and gestures. I may do well on a skills test and still be marked down in the video. In one real case, a woman said this happened and later faced a long period without work. I may not know what counted against me, or be allowed to refuse the analysis or challenge the result. I am not alone: 49% of working U.S. job seekers say these tools seem more biased than human recruiters.

### The recruiter's voice: between speed and questions

I start with a queue of resumes. AI helps me screen them, arrange interviews, and write job posts. When an applicant asks how the tool treats people fairly, I cannot answer with a shrug. I prepare an audit summary and notice, as required under New York City rules. I also face a hard question: is AI in an applicant's resume a useful skill or less effort? I operate the tool, but I do not decide whether the company adopts it.

### The business owner's voice: watching the dashboard

Each week I check the dashboard: hiring days, open roles, and cost. I must decide whether to keep paying for the tool. I have seen one reported case where hiring costs fell by about 30 percent. That is hard to ignore. Then a legal challenge involving an AI hiring tool makes me ask whether our speed is worth the worry. If our choice is questioned, my name is on it. I need the company to keep hiring, and I must answer for that choice.

## Why They See It Differently

All three want the right person in the right job. But their losses differ: the applicant may miss a fair chance; the recruiter must join speed with explanation; the owner must keep the company moving and answer for the choice. Power can be uneven: in some cases, the applicant may have little control over the process, while the recruiter may operate the tool or help decide whether to use it, and the employer may remain responsible for how it is used. New York City requires a bias check and applicant notice, so the recruiter must document and the owner must follow the rule; the applicant still cannot control the score. One company stopped a tool that rated resumes with women's terms lower. These outside limits mean their reasons cannot simply be added.

## What This Is Really About

Seen this way, the question is not only whether a machine can sort applications faster. It is who gets to be seen, who can question the judgment, and who carries the decision when the system is challenged. AI hiring is also a question about power: whose opportunity is measured, who must explain the process, and whose name carries the risk.
```

セクション別語数(REPORT 10-7節表): Hook 50 / Voice1 84 / Voice2 81 /
Voice3 83 / Tension 133 / Closing 60 / 簡易合計491(metrics.json総語数462)。

#### 新N+1(採用版attempt3、`er012_output/editorial_b_voices_3v_generalization_regression_01_n2_attempt3/article.md`)

```
# When AI Becomes Part of the Hiring Decision

## The Question

An application may pass through several checks before a person sees the result. Software can scan a résumé, score a test, or judge a recorded interview. The applicant may learn this before speaking or after rejection. Three people can face the same process very differently.

### The applicant: speaking under the score

I speak to a camera knowing that software may score my tone, face, and gestures. I can do well on a skills test and still be marked down in the video, without knowing why I stopped moving forward. I may receive a score about my honesty or reliability without a chance to opt out or challenge it. I do not choose the system; it chooses what part of me counts. About half of working U.S. job seekers see these tools as more biased than human recruiters.

### The recruiter: working inside the tool

I open a screening tool beside a stack of résumés. It helps me sort applications, arrange interviews, and match people with jobs. But I still need to explain the tool, its bias audit, and the notice sent to candidates. I also face a hard question about AI-written applications: useful skill, or less effort? I did not choose the final system, but I face its questions. About 90% of HR leaders say they use AI somewhere in hiring.

### The business owner: carrying the decision

Each week, I watch a dashboard showing hiring time, cost, and open roles. I decide whether an AI tool stays. When my team fills the roles we need, I feel relief. Then I see news about a hiring system accused of unfair treatment, and the decision feels personal. If the choice is questioned, my name is on it. I need the company to keep moving, but speed is not the only thing at stake.

## Why They See It Differently

All three want the same result: the right person in the right job. But the stakes split. An applicant may lose a chance without being fairly seen. A recruiter must keep work moving and answer for the process. An owner must keep the company running and carry the decision. Their power is uneven: the applicant is judged, the recruiter operates but does not choose the tool, and the owner chooses it and owns the result. In New York City, notice and a recent bias audit restrict that choice. One company stopped a tool after it rated women lower. These outside limits mean the applicant cannot create transparency, the recruiter must document it, and the owner must weigh more than speed. Their views cannot simply be added into one answer.

## What This Changes

The real question is not only whether a machine can sort applications. It is who gets a fair chance, who can ask why, and who carries responsibility when the process fails. AI has made hiring a shared decision with unequal power and risk, shaped by rules outside any one person's control. One voice cannot settle it.
```

セクション別語数(REPORT 10-7節表): Hook 46 / Voice1 87 / Voice2 79 /
Voice3 74 / Tension 129 / Closing 57 / 簡易合計472(metrics.json総語数470)。

#### ablation(NG停止時点の最終稿attempt1、`er012_output/editorial_b_voices_3v_ablation_no_grounding_block_01_attempt1/article.md`、Local Rewrite cycle1・2適用後)

```
# When AI Helps Decide Who Gets Hired

## The Question

An application is sent. A video interview begins. Behind the screen, software may scan a résumé, score a test, or read a person's voice and face. The applicant waits to be judged. The recruiter may use the system—or decide whether to use it. The owner must decide whether its cost is worth it. One question connects them: should companies use AI to screen job applicants?

### The Applicant's Voice: Under the Camera

I send in an application, then sit before a camera while software scores my voice, face, and movements. I want my skills to be seen, and I want to know why I did not move forward. One woman told a news outlet that her skills test went well, but AI rated her gestures and facial expressions poorly. She was rejected and later faced long-term unemployment. Another applicant sued after being scored for "reliability and honesty" without a way to opt out or challenge the result. I may have limited say in the system.

### Another Voice: The Recruiter at the Desk

I use software to sort résumés, arrange interviews, and match people with jobs. When the pile is large, that help matters. But in some cases, I may also be expected to answer candidates' doubts and help provide a plain summary of a bias audit. I have seen what this looks like at one large company: its hiring tool was independently reviewed, and applicants were notified. I also judge applications written with AI. Is that useful skill, or too little effort? I run the tool, but I do not make the final company decision.

### A Third Voice: The Owner Watching the Clock

I judge the business impact by two key measures: hiring time and cost. If key jobs stay open, the business feels it, and I am responsible. In one reported case, a hotel chain's hiring time fell from about six weeks to days after AI was introduced. That is hard to ignore when the company must keep moving. But if a tool is accused of discrimination, my name is tied to the reputation, legal bill, and trust at risk. I decide whether to keep using it, then live with the result.

## Why They See It Differently

All three want the same result: the right person in the right job. They divide over what they could lose. The applicant may lose a chance without being fairly seen. The recruiter must keep work moving and answer for the tool. The owner must keep the company running and carry the result personally. In these cases, their power may be uneven: the applicant may have limited influence over the process and may face difficulty understanding or challenging it; the recruiter or hiring manager may use the tool and, in some cases, help decide whether it is used; and the company or business leader may weigh efficiency against fairness, legal, and other risks and consequences. Their views cannot simply be added. New York City requires a recent bias audit and notice when these tools are used, while the EU treats hiring AI as high-risk, with oversight and transparency duties. Those outside rules limit the choices inside the process, so no one person's reasonable need can settle it.

## What This Changes

The deeper question is not simply whether a machine can sort faster. It is who gets to define a fair chance when a machine helps decide, and who must answer when that chance is lost. Hiring AI turns speed, trust, personal responsibility, and outside review into one connected decision. The machine is only one part of that judgment.
```

セクション別語数(REPORT 11-5節表、caveat語数併記): Hook 65語(caveat2) /
Voice1 93語(caveat1) / Voice2 93語(caveat2) / Voice3 90語(caveat0) /
Tension 166語(caveat9、Local Rewriteのhedge追加が主因) / Closing 58語
(caveat1)。metrics.json word_count=517(局所Rewrite前の値、注記のとおり
局所Rewrite後の最終稿はこれと異なる)。

---

### Analytical Leakage Check flagged実文(全4件+旧attempt1の自己修正実績)

| run | Voice | fail_fields | quoted_evidence(flagged実文) |
|---|---|---|---|
| 旧Trial-02 **attempt1**(下書き、後にattempt2で自己修正) | voice_1 | leak_evidence_subject | "Nearly half of working U.S. job seekers see AI hiring tools as more biased than people." |
| 旧Trial-02 attempt1 | voice_2 | leak_evidence_subject | "Around nine in ten HR leaders say they already use AI in hiring." |
| 旧Trial-02 attempt1 | voice_3 | leak_evidence_subject | "I have seen reported cases where some companies cut hiring time from weeks to days, and another cut hiring costs by about 30%." |
| 旧Trial-02 **attempt2(採用)** | — | any_flagged=false(0件) | (該当なし) |
| 新1回目 attempt1 | voice_2/voice_3/tension | 計7項目(discovery_syntax等) | (attempt1個別JSON未転記、REPORT4-1節に集計のみ記載) |
| 新1回目 attempt2 | voice_2 | leak_evidence_subject, leak_discovery_syntax | (attempt2個別JSON未転記、REPORT4-1節に集計のみ記載) |
| 新1回目 **attempt3(採用)** | voice_1 | leak_evidence_subject | "I am not alone: 49% of working U.S. job seekers say these tools seem more biased than human recruiters." |
| 新N+1 attempt1 | voice_2 | 3項目 | (個別JSON未転記、REPORT10-1節に集計のみ記載) |
| 新N+1 attempt2 | voice_3 | 2項目 | (個別JSON未転記、REPORT10-1節に集計のみ記載) |
| 新N+1 **attempt3(採用)** | voice_1 | leak_evidence_subject, leak_numbers_foreground, leak_discovery_syntax | "About half of working U.S. job seekers see these tools as more biased than human recruiters." |
| 新N+1 attempt3(採用) | voice_2 | leak_evidence_subject, leak_numbers_foreground, leak_discovery_syntax | "About 90% of HR leaders say they use AI somewhere in hiring." |
| ablation attempt1 | — | 未実施(N/A) | Ledger早期停止のためLeakage Checkに到達せず |

Checkerのreasoning原文(新1回目attempt3、voice_1、`analytical_leakage_
check_3v_attempt3.json`より): 「終始、応募者本人の不安と経験を一人称で
描いているため、外部の語り手による分析やDiscovery記事調の構造は
ありません。ただし、最後の文ではパーセンテージが文の主語になっています。」

Checkerのreasoning原文(新N+1 attempt3、voice_1): 「本人のカメラ審査や
異議申立て不能という具体的経験が中心で、語り手による人物分析はない。
一方、末尾の割合文は本人の実感ではなく、percentageを主語にした調査・
Trend記事型の文として挿入されている。」

同voice_2: 「採用担当者が実際に行う選別や説明責任、AI応募書類への迷いが
一人称で描かれており、外部からの人物分析はない。ただし、末尾の90%と
いう統計は本人の経験に自然に織り込まれず、割合を主語にしたDiscovery型の
外部情報になっている。」

---

### Ledger逸脱実文

**新1回目 attempt3(採用、MINOR 1件、`ledger_deviation.json`)**:
- claim_in_article: "I prepare an audit summary and notice, as required
  under New York City rules."
- issue: 「Ledgerが確認しているのは、雇用主・人材紹介会社が監査結果の
  要約を公開し応募者に通知すること、およびNBCUniversalの企業運用例で
  あり、個々の採用担当者が自ら作成することまでは確認していない。」
- severity=MINOR、changed_actor=true、overall_status=LEDGER_COMPLIANT
  (MINORのため0件扱いにはならないがLocal Rewrite対象外)。

**ablation attempt1(4件、`audit/local_rewrite_cycles.json`/`summary.
json`より、cycle1で3件・cycle2で2件[うちcycle1の1件が再判定で新規発見
の2件を生んだため合計4件がMAJORとして処理]):**

| # | original_ng_sentence | flags | resolved | human_review_required |
|---|---|---|---|---|
| 1 | "But I must also answer candidates' doubts and prepare a plain summary of a bias audit." | changed_fact, changed_scope, changed_certainty | true(cycle1) | false |
| 2 | "Each week, I check the dashboard: hiring time and cost." | changed_fact, changed_time, unsupported_new_claim | true(cycle1) | false |
| 3 | "Their power is uneven: the applicant cannot choose the process; the recruiter runs it but does not choose adoption; the owner chooses and bears the consequences." | changed_fact, changed_scope, changed_certainty, changed_actor, changed_negation, unsupported_new_claim | **false(3回rewrite失敗)** | **true** |
| 4 | "The recruiter must use the system."(cycle1再判定で新規発見) | changed_fact, changed_certainty | true(cycle2) | false |
| 5 | "I have no say in the system."(cycle1再判定で新規発見) | changed_fact, changed_certainty | true(cycle2) | false |

項目3の最終rewrite文(3回目、それでも`ledger_status: LEDGER_DEVIATION`
のまま): "In these cases, their power may be uneven: the applicant may
have limited influence over the process and may face difficulty
understanding or challenging it; the recruiter or hiring manager may use
the tool and, in some cases, help decide whether it is used; and the
company or business leader may weigh efficiency against fairness, legal,
and other risks and consequences."

issue(項目3): 「Ledgerは、応募者側の不透明性・異議申立て困難のリスク、
採用担当者がツールを使うか使用可否を判断する役割、企業・経営層が効率と
リスクを評価する立場を示している。記事はこれを、応募者・採用担当者・
所有者の固定的な権限分担に変え、採用担当者が導入可否を判断し得る可能性を
否定している。」

**最終判定ロジック(該当コード、`er012_b_family_voices_writer_generic_
01.py:874`, `:992`)**: `any_human_review_required`は
`local_rewrite_results`全体(cycle1・cycle2両方の記録)を通した`any()`
であるため、cycle2後の全体再判定が`overall_status=LEDGER_COMPLIANT`・
`MAJOR=0`になっても、cycle1で発生した項目3の`human_review_required=
true`という履歴自体は消えず、`run_voices_pattern_3v()`の992行の分岐で
`NG_REVIEW_REQUIRED`として確定した(既存の安全装置がそのとおりに機能、
バイパスなし)。

---

### Fact Checker REVIEW_REQUIRED実文(新N+1のみ、`fact_qa.json`
`unsupported_specific_claims`、3件すべて地の文)

1. "All three want the same result: the right person in the right job."
   (3者共通の目的の断定)
2. "Their power is uneven: the applicant is judged, the recruiter
   operates but does not choose the tool, and the owner chooses it and
   owns the result."(役割・権限関係の一律断定)
3. "AI has made hiring a shared decision with unequal power and risk"
   (記事全体からの解釈的結論)

checkerの`notes`原文: 「指定されたVoice別Verified Fact Ledgerのルールに
従い、Voice本文の具体的主張は、対応するLedger evidenceと実質的に一致する
範囲では未裏付けとして計上していない。問題は主としてVoice本文以外の
地の文にある普遍的な動機・権限・責任の断定と、そこから導く解釈である。
明確な事実矛盾は確認できないためFAILではない。」`contradictions: []`
(矛盾は0件)。

---

### Directional Fact Precheck 1件(新1回目attempt3のみ、`audit/
directional_fact_precheck.json`)

```json
{
  "overall_status": "DIRECTION_REVIEW_REQUIRED",
  "results": [{
    "verdict": "DIRECTION_REVIEW_REQUIRED",
    "reference_signals": [],
    "candidate_signals": [{"axis": "magnitude", "bucket": "low", "term": "fell", "confidence": "high", "category": "trend"}],
    "conflicts": [],
    "reason": "片方にのみ方向表現があり、機械的に一致/不一致を判定できない",
    "ledger_sentence": "IBMは採用コストを約30%削減したと報告されている。",
    "script_sentence": "I have seen one reported case where hiring costs fell by about 30 percent.",
    "shared_numbers": ["30"]
  }]
}
```

**checker技術的原因の精密化(本packet作成時にGrep確認、REPORT9-3節の
「言語間ギャップ」を補強する具体的根拠)**: `er008_directional_fact_
precheck_08.py`の方向語彙辞書(`_MAGNITUDE_LOW`、96-112行)には日本語の
「減少」「減る」「減った」「下落」「下がる」「下がった」「低下」
「縮小」「半減」「を下回る」「未満」は含まれるが、**Ledger文で実際に
使われている動詞「削減」は辞書に含まれていない**(Grep確認: `Grep
"削減" er008_directional_fact_precheck_08.py` → 0件マッチ)。そのため
「IBMは採用コストを約30%削減した」という日本語文からは`reference_
signals`が一つも抽出されず(`extract_direction_signals()`、147-161行)、
英語側の"fell"(`candidate_signals`)とのペアで比較不能となり
`DIRECTION_REVIEW_REQUIRED`になった。これは「英語方向語彙リストが日本語
文と一致しない」という一般的な言語間ギャップというより、**日本語辞書
自体に「削減」という1語が抜けている個別の語彙カバレッジ不足**という、
より特定可能な原因である(辞書へ「削減」を追加すれば、本ケースは
`MATCH`または少なくとも比較可能になる可能性が高いが、この修正の実装は
本タスクの権限範囲外、Fable/ユーザー判断)。

旧Trial-02(採用attempt2)の同箇所は"I have seen reports of faster hiring
and lower costs after AI"(数字なし)であり、`find_matching_script_
sentences()`が数字ベースでマッチする対象文自体が存在しないため、この
checkerは実質的に起動していない(`directional_fact_precheck.json`:
`{"overall_status": "PASS", "results": []}`、判定対象0件のPASSであって
方向性が実際に検証された結果ではない)。

---

### 語数target/tolerance実数値表

| 項目 | 数値 | 出典 |
|---|---|---|
| 記事全体soft target | 約410〜450語(hard capではない) | `er012_b_family_voices_writer_generic_01.py:313-321`(design.md B-6由来) |
| Hook目安 | 45〜55語程度 | 同上 |
| 各Voice目安 | 70〜85語程度(3人合計約210〜255語) | 同上 |
| Tension目安 | 75〜90語程度(60語未満への圧縮は禁止指示あり) | 同上 |
| Closing目安 | 45〜55語程度 | 同上 |
| 旧metrics.json実測 | 488語 | `.../person_voice_trial_02/b1b_run01_attempt2/metrics.json` |
| 新1回目metrics.json実測 | 462語 | `.../generalization_regression_01_attempt3/metrics.json` |
| 新N+1 metrics.json実測 | 470語 | `.../generalization_regression_01_n2_attempt3/metrics.json` |
| ablation metrics.json実測(局所Rewrite前) | 517語 | `.../ablation_no_grounding_block_01_attempt1/metrics.json` |
| ablation局所Rewrite後(summary.json final_result) | 569語(本REPORT11-5表の簡易合計は565語、集計方式差) | `.../ablation_no_grounding_block_01/summary.json` |

4個体とも410〜450語のsoft targetを上回っている。これは新経路固有の
劣化ではなく、旧記事(承認済み)も同水準で超過していた(REPORT4-4節)。

---

### near-duplicate・Point Overlap実測

Point Overlap QA(監視専用、Production関数`er008_point_overlap_qa_18.
py`の`lexical_overlap_ratio()`を無変更使用、閾値0.4、9値=有向Voice
ペア6+Voice vs Hook 3)の実測最大比率:

| run | 最大overlap比率 | 該当ペア |
|---|---|---|
| 旧Trial-02 attempt2 | **0.163**(REPORT本文は0.158と記載、本packet作成時に`point_overlap_qa_monitoring_3v.json`を実測した値は0.163。差異は僅少だが実測値を優先記載) | (JSON内、値0.163のキー) |
| 新1回目attempt3 | 0.158 | voice_1_vs_hook |
| 新N+1 attempt3 | 0.154 | (JSON内voice_2_vs_voice_3系) |
| ablation attempt1 | 0.143 | voice_1_vs_hook |

いずれもthreshold 0.4未満でany_flagged=false(4個体とも)。

記事内文同士のnear-duplicate最大ratio(difflib.SequenceMatcher文字
ベース、REPORT記載のSonnet独自計測、本packet作成時の再計算は未実施):
旧=0.582(「But the work does not end with a score.」対「If hiring
slows, the work does not wait.」)、新1回目=0.471、新N+1=**0.590**
(該当文: "I do not choose the system; it chooses what part of me
counts." 対 "I did not choose the final system, but I face its
questions."、いずれもVoice1・Voice2内)、ablation=0.143
(Point Overlap QA最大値を代用、REPORT11-5節)。

---

### 比較対象Trialの定型句(Closing/Hook修辞骨格)

| 対象 | Closing実文冒頭 |
|---|---|
| 旧Trial-02 | "This is not merely a question about whether a machine can read a résumé or a face. It is about who defines a fair chance, who must explain it, and who carries the consequences when it fails." |
| 新1回目 | "Seen this way, the question is not only whether a machine can sort applications faster. It is who gets to be seen, who can question the judgment, and who carries the decision when the system is challenged." |
| 新N+1 | "The real question is not only whether a machine can sort applications. It is who gets a fair chance, who can ask why, and who carries responsibility when the process fails." |
| ablation | "The deeper question is not simply whether a machine can sort faster. It is who gets to define a fair chance when a machine helps decide, and who must answer when that chance is lost." |

4個体すべてで「Xは単に〜かという問いではない。それは誰が〜し、誰が
〜し、誰が〜を負うかという問いだ」という修辞骨格が踏襲されている
(REPORT4-5・10-7・11-5節で継続確認)。

| 対象 | Hook実文冒頭 |
|---|---|
| 旧Trial-02 | "A job application may pass through software before a person sees it." |
| 新1回目 | "An application is sent. A video answer is recorded. Software may sort the resume..." |
| 新N+1 | "An application may pass through several checks before a person sees the result." |
| ablation | "An application is sent. A video interview begins. Behind the screen, software may scan a résumé..." |

「application→software/screenがresume/test/videoをscore/scan/judge→
3人が同じ場面に立つ」という骨格も4個体で共通。

---

### comparison artifact生成有無

- 生成有無: **生成していない**(記事本文全文比較は本packetの表・全文
  転記で代替。`comparison.html`等の目視比較artifactは本タスクでは
  作成されていない)。

### 費用按分単位

- 按分単位: **管理ID単位の累計**(記事単位・attempt単位の内訳はREPORT
  5節・9-6節・10-9節・11-7節に個別記載あり、按分の基準テーブルとしては
  「1記事Writerのみ[TTS抜き]のOpenAI Responses API実測」)。
- 単価目安(Standard同期、1回で確定した場合): 約¥25.5〜¥26.2
  (attempt複数回要した場合は¥53.6〜¥78.0まで上振れ)。
- 本管理ID累計: 約¥189.9(内訳: 初回invocation run1[NG]+採用run
  attempt1-3=¥110.1、修正2回目N+1=¥53.6、修正3回目ablation=¥26.2)。
  Fable承認済み上限¥230に対し残り約¥40.1。

### failure modeの条件差

- Voice2(Recruiter)のcaveat(ヘッジ表現)文数が0件になる現象は、新1回目
  ・新N+1の2/2回で再現したが、ablationでは2件(再現しなかった)。
  「Voice2 caveat=0」がテンプレート/Ledger fragment内容由来の固定
  パターンか単なるrun分散かは、この1点の条件差だけでは確定できない
  (REPORT10-7・11-5節、Fable/ユーザー判断待ちとされている)。
- Ledger逸脱の内容は、新1回目(Voice2の主体ズレ=changed_actor)と
  ablation(Narrator文側の権限構造絶対化=changed_scope/changed_
  certainty中心)とで**質的に異なる**(前者はVoice本文内の主体誤り、
  後者はTension/地の文の確信度上昇)。これは「体験claim根拠付け原則」
  が対象とする範囲(Voice本文)を超えて、地の文の確信度にも間接的な
  抑制効果を持っていた可能性を示す弱い状況証拠(n=1、REPORT11-6節)。

---

## (c) 必要なProduction code/spec sectionの該当行範囲のみ

| ファイル | 行範囲 | この範囲が必要な理由 | Grep確認 |
|---|---|---|---|
| `er012_b_family_voices_writer_generic_01.py` | 63 | `MAX_WRITER_ATTEMPTS = 3`(既存承認済み上限、初回+是正2回) | 済(Grep一致、コメント含め確認) |
| `er012_b_family_voices_writer_generic_01.py` | 344-354 | `COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`全文(恒久原則、ablation対象) | 済(Read実施) |
| `er012_b_family_voices_writer_generic_01.py` | 356-389 | `TENSION_EXTERNAL_CONSTRAINT_BLOCK_TEMPLATE`/`TENSION_EXTERNAL_CONSTRAINT_PROHIBITION_BULLET`/`TENSION_SELF_CHECK_WITH_EXTERNAL_CONSTRAINT`(任意パターン、外部制約統合) | 済(Read実施) |
| `er012_b_family_voices_writer_generic_01.py` | 219, 251, 392-406 | Voice Card block(219)がheading「Evidenceは脇役であること」(251)より**前**に展開されることを確認(9-1(iii)の「上記/下記」誤記の実際の位置関係の裏付け、404行の「上記」参照は本来「下記」であるべき) | 済(Grep+Read、行番号相互確認) |
| `er012_b_family_voices_writer_generic_01.py` | 942-1027 | `run_voices_pattern_3v()`: Fact Checker FAIL→即NG_REVIEW_REQUIRED(977-984)、Ledger早期停止条件(992: `remaining_major_count or any_human_review_required`)、Directional Fact Precheck呼び出し(1006-1014)の実行順 | 済(Read実施) |
| `er012_b_family_voices_writer_generic_01.py` | 781-881 | `run_ledger_deviation_and_local_rewrite()`: Local Rewrite cycle上限(800: `cycle < local_rewrite.MAX_REWRITE_CYCLES`)、`any_human_review_required`が全cycle履歴のunion判定になっている点(874) | 済(Read実施) |
| `er012_b_family_voices_writer_generic_01.py` | 1029-1093 | `run_pipeline_3v()`: attempt loop、Leakage Check呼び出し(1072-1073)、is `any_flagged`でretry継続/確定を分岐(1080-1086) | 済(Read実施) |
| `er010_ledger_local_rewrite_09.py` | 28, 37 | `MAX_REWRITE_ATTEMPTS = 3`、`MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS`(Local Rewrite cycle上限の実値) | 済(Grep一致) |
| `er008_directional_fact_precheck_08.py` | 76-112 | 方向語彙辞書(`_MAGNITUDE_HIGH`/`_MAGNITUDE_LOW`)。日本語語彙は存在するが「削減」は含まれない(実測、本packetのDirectional Fact Precheck節参照) | 済(Read+Grep `"削減"`で0件確認) |
| `er008_directional_fact_precheck_08.py` | 147-161, 310-357 | `extract_direction_signals()`/`audit_article_directional_facts()`: overall_status判定順序(POTENTIAL_DIRECTION_REVERSAL > DIRECTION_REVIEW_REQUIRED > PASS) | 済(Read実施) |
| `er012_editorial_b_voices_3v_person_voice_trial_02.py` | 380 | 旧Trial-02 prompt側の同一箇所「詳細ルールは**下記**【Voice内の数字】参照」(新版との差分比較対象) | 済(Grep一致) |
| `er012_b_family_voices_theme_ai_screening_01.py` | 157-174 | `EXTERNAL_CONSTRAINT`/`THEME_CONFIG`定義(Ledgerパス・Voice Card 3枚・external_constraint、旧Trial-02からの無変更転記) | 済(Grep一致) |

---

## (d) Sonnet要約

新経路(汎用テンプレート)は旧Trial-02と比べ、Fact Checker・Ledgerの
「合格/不合格」ラベルはほぼ同水準を維持しつつ、Analytical Leakage
Check(2/2回でflagged残存)・Directional Fact Precheck(1/2回で
REVIEW_REQUIRED)・Fact Checker(1/2回でREVIEW_REQUIRED)という3種類の
「軽微な指摘」が、旧記事には出なかった形でrunごとに異なる箇所に出現する
という挙動が観測された。原因診断のためのprompt全文diff(9-1)・Ledger
文言diff(9-2)・ablation(11節)では、いずれも「汎用化そのものが原因」と
断定できる明確な証拠は得られず、(a)旧Trial-02自身のattempt1にも同型の
Leakage失敗が既にあった(自己修正済み)、(b)Directional Fact Precheckの
指摘は辞書の語彙カバレッジ不足(「削減」未収録)という既存checkerの
技術的限界が濃厚、という2点は本packet作成時に実文・行番号で裏付けが
取れた。一方、(c)ablationで観測されたLedger逸脱4件(過去最多)が原則
除去の系統的効果かrun分散かはn=1で切り分け不能なまま残っている。
Sonnet側の懸念: 4個体という少ないサンプルサイズで「run分散」と結論
づけることの統計的な弱さ、および全文書き直し方式のretry設計自体が
「一度直った箇所が別attemptで再発する」という構造的な不安定さを本質的に
抱えている可能性(これは汎用化固有ではなく既存Trial-02設計からの
持ち越し課題)。

---

## (e) Progressive Disclosure手順(Opus向け指示文)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。
> ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、
> 診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告
> すること。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、
> 必要な事実を省いてまで読込量を減らしてはならない。
>
> 参考(本packetに含めなかった主な追加ファイル候補): 元REPORT全文
> (`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_
> REPORT.md`、931行)、新1回目attempt1/attempt2の個別`analytical_
> leakage_check_3v_attempt{1,2}.json`(本packetには集計値のみ転記)、
> `er012_b_family_voices_writer_generic_01_test_01.py`(20テストの
> 詳細)、`er012_b_family_voices_production_runner_01.py`の
> `write_new_theme`分岐実装。

---

## (f) 入力文字数の自己計測欄

(Python `len()`実測、本packetファイル自体に対して計測)

- (a)論点セクション(論点と材料の対応チェック含む): 1,655字
- (b)主要数値表・要点セクション(記事本文・語数実数値表・near-duplicate
  実文・比較対象定型句・comparison artifact有無・費用按分単位・
  failure mode条件差の7小節を含む): 26,943字
  - うち記事本文小節のみ(4本のコードブロック合計): 12,260字
    (target目安4,000〜5,000字を大きく超過。理由: 本Regressionは
    「1本のテーマ×1レベル」ではなく「同一テーマの4個体[旧Trial-02+
    新1回目+新N+1+ablation]の比較」が診断対象そのものであり、4個体
    それぞれの全文が無ければ論点1・3・6[Leakage再現性・Ledger逸脱の
    質的差・Closing/Hook修辞骨格の継続]を判定できないため、複数
    レベル比較に準じて4本とも全文転記した)
- (c)Production code/spec抜粋セクション(Grep確認欄含む): 2,399字
- (d)Sonnet要約セクション: 773字
- (e)Progressive Disclosure指示文: 589字
- **packet合計文字数: 33,556字**(目安2〜3万字を約3,556字[約12%]
  超過。理由: 上記のとおり記事本文4本転記[12,260字]が主因。3個体
  比較[旧+新1本]であれば目安内に収まった可能性が高いが、Fableから
  明示された論点(新1回目・新N+1・ablationの3run比較+旧との対照)を
  材料なしで立てることを避けるため、超過を許容してでも4本全文を
  優先した)
- 前回packet(改訂前)との差分: 本packetは本template改訂後、
  PHASE1B-04向けとして新規作成した初回packetであり、直接比較できる
  「前回packet」は存在しない。ただし記事本文4本・Leakage Check実文
  ・Ledger逸脱実文・Directional Fact Precheck実文をすべて転記した
  ことで、Opusが`article.md`4本・`analytical_leakage_check_3v_
  attempt3.json`2本・`ledger_deviation.json`2本・`directional_fact_
  precheck.json`2本・`fact_qa.json`1本をProgressive Disclosureで
  個別に読む必要性は理論上ゼロになっているはずである(実際にOpusが
  これらを追加で読んだ場合、次回改訂で本packetの不足点として扱う)。
