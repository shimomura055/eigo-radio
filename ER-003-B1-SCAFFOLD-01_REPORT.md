# ER-003-B1-SCAFFOLD-01 実行報告(A02 B1 Supported Natural English Prototype)

**管理ID: ER-003-B1-SCAFFOLD-01**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**B1をB2専用英文の別生成ではなく「B2と完全共通のNatural English本文
+ 易しいListening Support」で成立させる、という設計は概ね機能した。
ただし、Support側(Comment 4)で1件のMAJOR Ledger Deviationを発見した。**

- ニュース本文(Full Story Part1/Part2/Point One/Point Two/In One Line)
  はB2 V2版(ER-003-CEFR-DIRECT-02)と一字一句完全一致で使用した
- Preview・Comment1〜4はすべて易しいSupport英語で生成成功
  (技術的再試行0回)
- Key Phrases(Strategy L選定+Canonicalization、English→Japanese→
  Englishの5件)はすべてQA `PASS`
- **Support Fact Checker: `PASS`(矛盾0件)**
- **Support Ledger Deviation Check: `LEDGER_DEVIATION`(MAJOR 1件、
  Comment 4)**。パイロットのnight-curfew群(全体の一部)に限定される
  報告を、"this pilot"/"People"として調査全体・一般的な人々の結果
  であるかのように述べていた
- Number Treatment監査で、B2本文中14個の数字表現を分類し、うち3件が
  Listening-first原則上は丸め・省略が望ましいと判定された(H節、
  本文は書き換えていない)
- **開発中に自己発見した実装バグ**: Point One/Twoの見出しテキストを
  誤って本文と同一視してしまうバグがあり、初回生成時はComment 3へ
  誤ってPointの全文が渡っていた(結果的に出力への漏洩は無かったが、
  設計意図に反する入力だった)。バグを修正し、Comment 3のみ正しい
  入力で再生成した(F節で詳述)

最終的な採否判断はユーザーに委ねる。

## B. Fixed B2 News English

ニュース本文はER-003-CEFR-DIRECT-02の`er003_output/cefr_direct_02/A02/B2_v2/article.md`
(SHA256: `e0d1c7f6d839ff83ed42bfe58fd1a4a79e3bb0284a6e082be79e71d0763611d7`)
をそのまま使用した。1語も変更していない。

Full Story Part1/Part2の分割は、意味上の転換点("And the plan does
not stop at bedtime."、夜間制限の説明→終日適用の別制度の説明という
切り替わり)で機械的に行った(Part1=88語、Part2=128語)。分割自体は
文言を一切変更しない、パラグラフ単位の切り出しのみである。

## C. B1 Supported Full Script

全11パートの全文は比較Artifact(I節)参照。構成:

1. Preview(49語)
2. Key Phrases(5件、English→Japanese→English)
3. Comment 1 — Listening Focus(17語)
4. Full Story Part 1(B2共通、88語)
5. Comment 2 — Mid-story Recovery + Next Question(24語)
6. Full Story Part 2(B2共通、128語)
7. Comment 3 — Story Meaning + Bridge to Points(39語)
8. Point One(B2共通、55語)
9. Point Two(B2共通、49語)
10. Comment 4 — Point Recovery + Bridge to In One Line(38語)
11. In One Line(B2共通、31語)

## D. Support Design

| パート | 役割 | 入力コンテキスト | 語数 |
|---|---|---|---|
| Preview | theme/problem/value/questionの提示。答え・結論・turning pointを先出ししない。Comment1・2と重複させない | エピソード全文(参考、Fact追加禁止)+ Comment1・2の確定テキスト(重複回避のため) | 49語 |
| Comment 1 | Listening Focus。次に何を聞くか示す。答えは言わない | Full Story Part 1 | 17語 |
| Comment 2 | Mid-story Recovery + Next Question。Part1要点を1点回収、Part2への問いを提示 | Full Story Part 1・Part 2 | 24語 |
| Comment 3 | Story Meaning + Bridge to Points。ニュース全体の意味を整理、Pointへの橋渡し。Point内容は伏せる | Full Story Part 1・Part 2 + Point見出しのみ(内容は非公開) | 39語 |
| Comment 4 | Point Recovery + Bridge to In One Line。Pointの意味を軽く回収 | Point One・Point Two全文 + In One Line | 38語 |

Preview以外はComment1→2→3→4の順に先に生成し、Previewは最後に
Comment1・2のテキストを踏まえて生成した(重複回避を構造的に担保する
ため)。

Key Phrasesは、B2本文全体(Main Story+Point One+Point Two)に対し、
Production機構(Strategy L選定 `er003_key_words_production.py`/
`er003_key_words_min_unit.py`/`er003_b1_p2_keywords.py` + Canonicalization
`er003_key_words_canonicalization.py`)を、`er003_v1_a2_kp_select_generate.py`
と同一の呼び出しパターンで読み取り専用にimportして適用した。新しい
選定ロジックは設計していない。

## E. B2 vs B1 Comparison

| 項目 | B2 | B1 Supported |
|---|---|---|
| ニュース本文 | B2 V2(自然な成人英語) | B2と完全同一(無変更) |
| Preview/Comment | (B2独自仕様、比較対象外) | 易しいSupport英語、5パート追加 |
| Key Phrases | (今回対象外) | English→Japanese→English、5件 |
| 難易度の作り方 | 英文そのものの複雑さ | 支援量(Preview/Comment/Key Phrase)と自力理解の割合 |

## F. 開発中に発見した実装バグとその修正

**バグ**: `sf1r1.split_sections`(既存のword-count専用ヘルパー)は、
Point One/Twoの`###`見出し行そのものを内部で破棄し、本文行だけを
集計する設計になっている(word count目的では正しい挙動)。今回、この
関数をPoint見出しテキストの取得に流用した結果、見出しが取得できず、
本文冒頭の1文が誤って「見出し」として扱われ、実際の見出し
("The pilot is a clue, not a crystal ball"等)が失われた。

**影響**: Comment 3の生成コンテキストに、本来「見出しのみ(内容は
伏せる)」を渡すべきところ、Point One/Twoの全文が誤って渡っていた。
**実際の初回生成結果を確認したところ、具体的な数字や結論の明示的な
漏洩は発生していなかった**(モデルが自律的に抽象的な橋渡し文を書いた
ため)が、設計意図(Comment 3にPointの内容を見せない)には反していた。

**修正**: 生の Markdown を正規表現で直接解析する専用パーサーへ
書き換え、見出しテキストを正しく抽出できるようにした。**Comment 3
のみ**、修正後の正しいコンテキスト(見出しのみ)で再生成した(他の
パート・Key Phrases・Number Treatment監査はこのバグの影響を受けて
いないため、再生成していない)。これは内容評価によるbest-of的な
再試行ではなく、実装バグの修正による再生成であり、修正前後の内容を
本節で透明に記録する。

**修正前のComment 3(バグの影響下、参考記録)**: Point One/Twoの全文を
コンテキストとして受け取った状態で生成されたが、具体的な内容は
明示的には漏洩していなかった。

**修正後のComment 3(採用)**: "This plan is not a complete social
media ban for 16- and 17-year-olds. It would turn on extra protection
settings automatically, but young users could still change them.
Next, we will look at what these changes may mean in practice."
Point見出しのみを渡した結果、Pointの具体的内容(パイロットの詳細)へ
一切触れず、本編の要約と次への橋渡しに徹する、より意図に忠実な
Comment 3になった。

なお、Comment 3の差し替えに伴い、Support Ledger Deviation Check・
Support Fact Checkは修正後のテキストで再実行した(G節)。

## G. Fact Safety

| Check | 対象 | 結果 |
|---|---|---|
| Support Fact Checker | Preview+Comment1〜4(結合) | `PASS`(矛盾0件、Web検索あり) |
| Support Ledger Deviation Check | Preview+Comment1〜4(結合) | `LEDGER_DEVIATION`(MAJOR 1件) |

### G-1. Comment 4のLedger Deviation(MAJOR 1件)

該当箇所: "So, this pilot gives us context, not a prediction. People
reported better sleep, but many changed when they used screens rather
than how much they used them."

指摘: Verified Fact Ledgerで睡眠改善・利用時間帯の移動が報告されて
いるのは、午後9時〜午前7時のnight-curfew群(パイロット全体309世帯の
うち81世帯)に限定される。この一文は「this pilot」「People」として、
あたかもパイロット全体・一般的な人々の結果であるかのように述べており、
対象群のscopeを維持していない。

**この発見の位置づけ**: F節のバグとは独立した、Comment 4自体の
内容の問題である(Comment 4はバグの影響を受けていない)。ER-003-
CEFR-DIRECT-02/03で確認した「B1向けの明示的な回収・要約指示が、
Ledgerの対象群scopeを超えた一般化を誘発しやすい」という傾向と同種の
パターンが、今回のSupport(Comment 4の"Point Recovery"役割)でも
再現したと考えられる。Comment 4の生成指示自体に「本文が述べていない
新しい具体的Factを追加しない」「過度な一般化をしない」という禁止
事項を含めていたにもかかわらず発生しており、この種の一般化ドリフトは
禁止事項の明記だけでは十分に防げない可能性を示す、実務上重要な知見
である。

**今回の対応**: 品質を理由とした再生成(best-of)は行わず、この
逸脱をそのまま記録した。Comment 4の修正・再設計は次段階の課題として
K節へ送る。

## H. Number Treatment Audit

B2本文(ニュース本文は書き換えていない)に対し、`er003_v1_spoken_
first_01_generate.run_classification`をそのまま再利用して分類を
実行した(14個の数字表現を検出)。

| 数字 | 分類 | 精度要件 | 推奨surface form(未適用) |
|---|---|---|---|
| At midnight(冒頭) | DISPENSABLE | EXACT_REQUIRED | 冒頭では省略、後段の完全な時間帯表現に一本化 |
| aged 16 and 17 | ANCHOR | EXACT_REQUIRED | 維持 |
| From midnight until 6 a.m. | ANCHOR | EXACT_REQUIRED | 維持 |
| 16- and 17-year-olds(2回目) | DISPENSABLE | EXACT_REQUIRED | 既出のため"for those users"等へ置換候補 |
| throughout the day | ANCHOR | EXACT_REQUIRED | 維持、"all day, not only overnight"と対比を明示 |
| two clocks(比喩) | SUPPORTING | EXACT_REQUIRED | 比喩を具体化する代替案あり(必須ではない) |
| under 16 | SUPPORTING | EXACT_REQUIRED | 維持(基準としての年齢) |
| As of 12 August 2026 | ANCHOR | EXACT_REQUIRED | 維持 |
| spring 2027 | ANCHOR | APPROXIMATE_OK | 維持(既に概略的) |
| 2026 pilot | SUPPORTING | EXACT_REQUIRED | 維持 |
| **309 households** | SUPPORTING | **APPROXIMATE_OK** | **"just over 300 households in all"への丸めが望ましい** |
| aged 13 to 17 | SUPPORTING | EXACT_REQUIRED | 維持 |
| **81 households** | SUPPORTING | **APPROXIMATE_OK** | **"about 80 of those households"への丸めが望ましい** |
| a midnight padlock(比喩、結び) | DISPENSABLE | DIRECTION_ONLY | 省略または"not a hard curfew"への置換候補 |

**監査結果の要点**: 14件中11件はすでに適切な扱い(ANCHORは正確な
まま、比喩は必要に応じて維持)だが、**309households・81households
の2件は、Listening-first原則(過去のSPOKEN-FIRST検証で確立)に
照らすと丸め表現("about 300"/"about 80")が望ましいと判定された**。
これは、B2 V2版がER-003-CEFR-DIRECT-02の時点でNumber Treatmentを
明示的な生成条件としていなかったために生じた差分である。今回は
方針通り、本文を勝手に書き換えず、この監査結果のみを報告する。
Production候補化する際に、B2/B1/A2共通の修正対象として扱うことを
提案する(K節)。

## I. Comparison Artifact

11パート全体の流れ(Support/Newsをラベルで区別)、Support QA、Fact
Safetyをまとめた。

**URL**: https://claude.ai/code/artifact/11164a79-2b0e-41ca-9339-73377a54b355

リポジトリ内の原本: `er003_output/b1_scaffold_01/comparison.html`

比較Artifactの補足として、Support QA(10観点)・Overall B1 QA(8観点)
は以下の通り(Artifactにも一部掲載)。

### Support QA(10観点)

| 観点 | 評価 |
|---|---|
| 1. Support English ease | 高い。全パート短い宣言文中心 |
| 2. First-listen comprehensibility | 高い |
| 3. Listening guidance quality | 良好 |
| 4. Recovery effectiveness | C2は良好、C4は要点回収を狙って逸脱を招いた(G節) |
| 5. Transition clarity | 良好 |
| 6. Support brevity | 良好(全17〜49語、隣接ニュース部分88〜128語より明確に短い) |
| 7. Support naturalness | 良好 |
| 8. Adult tone | 維持 |
| 9. No new Fact | Comment 4のみ例外 |
| 10. No over-explanation | 良好 |

### Overall B1 QA(8観点)

| 質問 | 評価 |
|---|---|
| 1. B1リスナーがB2英語を追える可能性があるか | 概ねYES。Comment/Key Phraseの支援が機能している |
| 2. Key PhrasesがMajor blockerを除去しているか | 概ねYES(by default/curfew/cross the finish line/pilot/personalised feedsはいずれも妥当な選定) |
| 3. Commentsが認知負荷を下げているか | YES |
| 4. 記事が自然なニュースらしさを保っているか | YES(本文完全同一のため当然) |
| 5. ペーシングが保たれているか | YES(Supportが本文より短い) |
| 6. 日本語使用が十分に限定されているか | YES(Key Phrase 5件のみ) |
| 7. B1体験がB2より有意に易しいか | YES(支援点が5箇所追加され、体験として明確に異なる) |
| 8. B1専用ニュース英文生成は依然として必要か | **LIKELY NO**。ただしComment 4の一般化ドリフト(G節)の修正が前提条件 |

## J. Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・A2/VFL/spoken_first/
  cefr_direct系スクリプト**: 無変更。新規の独立ファイル
  (`er003_v1_b1_scaffold_01_generate.py`)から、Key Phrase Production
  機構(Strategy L選定・Canonicalization)とNumber Classificationを
  読み取り専用でimportした
- **B1専用ニュース英文生成**: 実施していない
- **A01/ADD03のB1 Support生成**: 実施していない
- **B1/B2共通化の最終決定**: 行っていない(今回はプロトタイプ検証)
- **A2再生成**: 実施していない
- **TTS/audio assembly/WPM変更**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **B2本文のNumber Treatment反映**: 監査のみで、本文は書き換えていない

## K. 次のDecision

以下から提案する。

### Option 1

B1 = Supported Natural Englishを継続する。今回の結果を踏まえ、
Comment 4のような一般化ドリフトを防ぐための指示強化(下記)を行った
上で、他記事でのN増しへ進む。

### Option 2

Supportを再調整する。具体的には、Comment 4(Point Recovery)の生成
指示へ、「Point Oneがnight-curfew群という特定の対象群の結果である
ことを、要約時にも維持する」「'this pilot'や'people'のような主語で
対象群を一般化しない」という明示的な禁止を追加し、再検証する。

### Option 3

B1専用英文へ戻る。ただし、ER-003-CEFR-DIRECT-02/03で確認した
「B1専用ニュース英文は3ジャンルすべてでFact Safety上の問題を起こす」
という結果と比較すると、今回発見した問題(Comment 4、1件のMAJOR
逸脱、修正可能な指示の問題)の方が、B1専用英文の問題(3ジャンル
すべてで発生する構造的な傾向)より限定的であり、Option 3を選ぶ根拠は
現時点では弱いと考える。

**今回の結果を踏まえた所見**: B2共通本文+Support scaffoldingという
設計思想自体は、今回のA02プロトタイプでは概ね成立した(Fact
Checker PASS、Key Phrase PASS、構造・分量とも設計通り)。唯一の
問題(Comment 4のLedger Deviation)は、B1専用英文で見られたような
「難易度指示そのものに起因する構造的傾向」というより、「要約・回収
という機能を持つ短い一文が、対象群のscopeを保持し損ねた」という、
より限定的で修正しやすい問題に見える。Option 1(指示強化の上で
継続)が現時点でもっとも妥当と考えるが、最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_b1_scaffold_01_generate.py`(新規) | B1 Supported Natural English生成パイプライン。Key Phrase Production機構・Number Classificationを読み取り専用でimport |
| `er003_output/b1_scaffold_01/A02/`(新規) | fixed_news_parts.json・support_texts.json・key_phrases/・number_treatment_audit.json・support_ledger_deviation.json・support_fact_qa.json・b1_supported_script.md・audit記録 |
| `er003_output/b1_scaffold_01/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
