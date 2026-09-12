# FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-RECONCILE-01 報告書

管理ID: `FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-RECONCILE-01`
(read-only調査。SSOT編集・Git操作・コード変更・API支出は一切行っていない)

## 要点(5行)

1. リポジトリ全体を再調査したが、「人名が出たらネット検索して**正しい
   英語表記(spelling)**を事前確認し、記事本文(Writer出力)へ反映する」
   という、ユーザーが記憶している仕組みは**見つからなかった**
   (`NEW`と判定)。
2. 類似する既存機構は3つあるが、いずれも別の問題(発音・日本語TTS読み・
   Fact Checkerの一般的事後検知)を対象としており、今回のFailure mode
   (英語記事本文中の人名ローマ字綴りの誤り)を防ぐ設計にはなっていない。
3. Fact Checker(News含む全Family共通、Web検索ツール搭載)は人名を検証
   対象に含んでおり実際に伏見寅威等の誤りを検出できているが、verdict=
   FAILは記事の自動修正ではなく人間レビュー行き(NG_REVIEW_REQUIRED)で
   止める設計であり、かつTrial-12/12b/14では**Point Overlap Gateが先に
   実行され、そのGateがNGのまま予算上限に達すると明示的にFact Checker
   呼び出し自体をスキップする**ため、多くのサンプル記事でFact Checkerが
   一度も呼ばれていなかった(これはTrial-14自身の報告書が既に特定済み)。
4. Pronunciation Ledger(ER-006)はPerplexity検索で`canonical_spelling`
   まで取得するが、(a)呼び出しはASR Cascade(Primary/Secondary計4段)を
   尽くしてもTTS音声とcanonical textが一致しない場合のみの反応的トリガー
   であり、(b)得られた情報は明示的な設計制約により**記事本文の綴りを
   一切書き換えない**(TTSの発音ヒントのみに使う)。
5. Production判断が必要な項目=既存対策の配線漏れ是正ではなく、**新規
   Trial案の検討要否**(下記「結論」節、QCD概算付き)。実装は行っていない。

---

## 1. 調査方法

`CURRENT_SPEC.md`・`OPEN_ITEMS.md`・`OPEN_ITEMS_HISTORY.md`・
`DECISION_LOG.md`・`DECISION_LOG_HISTORY.md`・全`*_REPORT.md`(198件)・
全`er0*.py`に対し、`romaniz`/`romaji`/`ローマ字`/`英語表記`/
`person_name`/`proper_noun`/`固有名詞`/`name_reading`/
`pronunciation_ledger`/`safe_reading`/`NAME_VERIFICATION`/`entity`
(OPEN-125含む)でGrepし、該当箇所を実コード・実データで追跡した。

## 2. 発見した関連機構と、今回の問題との関係

| 機構 | 管理ID/実装箇所 | 何を対象にしているか | 今回の問題(英語記事本文の人名ローマ字誤り)に効くか |
|---|---|---|---|
| ER-009 JA Foreign Token Gate | `er003_audio_tts_asr_safety.classify_foreign_tokens_in_japanese_text()`、`CURRENT_SPEC.md`974行 | **日本語**canonical text中の英字混じりトークン(TTS読み上げ前の日本語ナレーション)の分類 | 効かない(対象言語・対象工程が異なる。英語記事本文は対象外) |
| Pronunciation Ledger + Perplexity研究 | `er006_pronunciation_ledger_01.py`/`er006_pronunciation_research_01.py`/`er006_pronunciation_tts_injection_01.py`、`CURRENT_SPEC.md`862行 | TTS**音声**が固有名詞をどう発音すべきか(ASR不一致のHuman Reviewパッケージ充実、`_resolve_unresolved_entity_for_review()`経由で`er006_secondary_asr_01.py`のASR Cascade全4段消尽後にのみ発火) | 直接は効かない。`canonical_spelling`は取得するが、`er006_pronunciation_tts_injection_01.py`のコメントで明示される設計制約「article textを書き換えない」「本文の綴りをphonetic spellingへ置換しない」により、記事本文の綴り誤りを修正する経路には一切使われない |
| Fact Checker(全Family共通) | `er002_ja_web_research_r3.py`(`build_fact_check_prompt`/`make_fact_checker_fn`/`run_fact_checker_with_gates`)、prompt: `er002_v1_2m_restore_briefs/fact_checker_prompt_template_r3.txt` 21行「人名・組織名」を明記 | 生成済み記事本文に対する独立Web検索での事後検証(News/Trend Synthesis含む共通経路、`er003_v1_n3_01_articles_generate.py`から呼び出し) | **唯一、実際に人名ローマ字誤りを検知できている**(Trial-14実データで実証、下記3節)。ただし(i) verdict=FAILは記事自動修正でなくNG_REVIEW_REQUIRED(人間判断待ち)で停止するのみ(`er003_v1_n3_01_articles_generate.py` 1006-1031行、ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12によるユーザー正式決定)、(ii) 同ファイル内でPoint Overlap/Value QA Gateが**Fact Checkerより先に実行され**、そのGateがリトライ上限まで解消しない場合は明示的に「Fact Checker以降は実行しません」としてFact Checker呼び出し自体をスキップする(883-951行) |
| OPEN-125(entity_only_diffs誤区分) | `er006_preprod_hardening_01_validation.py` 451-473行 | TTS Retry分類における編集見出しラベル(Title Case)の固有名詞誤判定 | 無関係(TTS音声側のretry分類ロジックの話であり、記事本文の人名綴りとは別問題) |

## 3. Trial-12/12b/14で「なぜ発火しなかったか」(コードで実証)

`er003_v1_n3_01_articles_generate.py`のPoint Overlap/Value QA Gate(883-
951行)は、記事全体retryを`POINT_OVERLAP_ARTICLE_RETRY_MAX`回行っても
解消しない場合、`NG_REVIEW_REQUIRED`を返し**Fact Checker呼び出し自体を
実行しない**(949行コメント「Fact Checker以降は実行しません」)。これは
バグでも配線漏れでもなく、既存の意図的なGate順序設計である。

News Trial-12(条件A、fact5件)の元パイプラインでは、この理由により
N=6中1本しかFact Checkerへ到達しておらず(Trial-14報告書2-2節)、残り
5本の記事本文に含まれていたかもしれない人名誤りはFact Checkerに一度も
検証されないままNG_REVIEW_REQUIREDで停止していた。Trial-14はこの
「打ち切り記事」8本へFact Checkerを単独適用し直すことで、初めてFAILの
77.8%(9件中7件)が人名ローマ字誤りであることを発見した
(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_
REPORT.md` 146-171行、既にTrial-14自身が特定済みの結論であり、本調査は
これを裏付け・再確認したのみ)。

**Ledger側の根本要因(本調査で新たに確認)**: 実際のProduction Verified
Fact Ledger(`er003_output/n3_01/hanshin/a2/audit/deviation_full_record.
json`)を直読すると、選手名はFACT-03「伊原陵人」・FACT-05「伏見寅威」の
ように**日本語表記のみ**で登録されており、英語canonical spellingは
一切含まれていない(例外: FACT-04のE・モンテロのみ、独立Fact Checkerの
指摘を受けて事後的にフルネーム`Elehuris Montero`を人手で追加検証・
記載した形跡がある)。したがってWriter(LLM)は記事生成のたびに
日本語人名からゼロから英語ローマ字表記を独自に推測しており、これが
実行のたびに揺れる(同一人物でも run により`Takato Ihara`/`Rihito
Ihara`/`Ryoto Ihara`等、`Torai Fushimi`/`Tora Fushimi`/`Tai Fushimi`等)
原因である。参考として、実際に公開されたProduction記事本文
(`er003_output/n3_01/hanshin/a2/article.md`)では偶然`Takato Ihara`・
`Torai Fushimi`とも正しく生成されていたが、これはRun依存の結果であり、
Ledgerに英語表記が固定されていることの証明ではない。

## 4. Pronunciation Ledger実データ確認

`er006_output/pronunciation_ledger_01/ledger.json`に`Ihara`/`Fushimi`/
`Montero`の登録は0件だった(grep実施、ヒットなし)。これは、これらの
人名がASR Cascade全4段を消尽するほどの音声不一致を一度も起こしておらず
(＝TTS音声の**発音**自体は問題なく、問題は音声化以前の**本文綴り**に
あるため)、Pronunciation Ledgerの発火条件にそもそも該当しないことと
整合する。

## 5. 結論(Family / 現象 / 既存対策 / 今回なぜ効かなかったか / 追加Trial有無 / 結果 / Production判断)

- **Family**: News(Major/Daily)、共通Writer/Fact Checker基盤経由で他
  Editorial Typeにも波及しうる一般的弱点
- **現象**: 英語記事本文中の日本人選手名ローマ字表記の誤り(例: 伊原陵人
  →公式`Takato Ihara`に対し`Rihito Ihara`/`Ryoto Ihara`、伏見寅威→
  公式`Torai Fushimi`に対し`Tora Fushimi`/`Tai Fushimi`)
- **既存対策**: 本調査の範囲では**「事前にネット検索して正しい英語表記を
  確認し記事へ反映する」専用の仕組みは存在しない**(`NEW`)。関連する
  既存機構(ER-009 JA Foreign Token Gate、Pronunciation Ledger、Fact
  Checker)はいずれも別問題(日本語TTS読み分類/音声発音/事後的な一般
  ファクトチェック)向けであり、本問題への専用対策として設計・承認された
  記録はSSOT上に見当たらなかった
- **今回なぜ効かなかったか**: (a) Fact Checkerは人名検証能力自体は持つが
  verdict=FAILは自動修正でなく人間レビュー待ち停止のみ、(b) Point
  Overlap Gateが先行し、そのGateのNGでFact Checker呼び出し自体が
  スキップされるケースが多かった(Trial-12実測でFact Checker到達率
  1/6)、(c) そもそもVerified Fact Ledgerが人名を日本語表記のみで保持し
  英語canonical spellingを持たないため、Writerが生成の都度ゼロから
  ローマ字を推測し結果が揺れる
- **追加Trial有無**: 本タスクは調査のみ(実施なし)
- **結果**: `NEW`(既存対策の配線漏れではなく、未設計の対策候補)
- **Production判断が必要か**: 既存対策の是正ではなく、**新規Trial案の
  採否**をユーザーが判断する必要がある。候補(いずれも未承認・未実装、
  Trial-14報告書4-4節で既に提示済みのUDR候補2と同一系譜):
  - 候補(a) Verified Fact Ledgerの人名に英語canonical spelling併記を
    Research段階で追加する(Web検索1回追加、Q:既存Research呼び出しへの
    追記のためコスト増分は小、C:見込み¥50〜100程度[小規模Trial]、
    D:News Ledger生成コード+Researchプロンプト変更を伴うため
    `docs/pm/PM_GOVERNANCE.md`承認手続き必須)
  - 候補(b) Point Overlap Gate NGでもFact Checkerを必ず1回実行する
    よう順序を変更する検証(Q:Gate順序自体の変更でありSTOP必須級の
    仕様変更、C:見込み¥100〜150程度、D:既存retry/fallback設計との
    整合確認が必要、安全装置の独自変更は不可のため慎重な検討が必要)
  - 候補(c) 現状維持(何もしない)。Fact Checker自体は人名以外の一般
    事実確認機構であり、人名専用対策を追加コストとして正当化できるか
    ユーザー判断

## 6. 参照artifact(絶対パス)

- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md`(862行・974行・501行)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py`
  (883-1031行)
- `C:\Users\tensh\eigo-radio\er002_ja_web_research_r3.py`(241-423行)
- `C:\Users\tensh\eigo-radio\er002_v1_2m_restore_briefs\
  fact_checker_prompt_template_r3.txt`
- `C:\Users\tensh\eigo-radio\er006_pronunciation_ledger_01.py`
- `C:\Users\tensh\eigo-radio\er006_pronunciation_research_01.py`
- `C:\Users\tensh\eigo-radio\er006_pronunciation_tts_injection_01.py`
- `C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py`(190-260行)
- `C:\Users\tensh\eigo-radio\er006_output\pronunciation_ledger_01\
  ledger.json`
- `C:\Users\tensh\eigo-radio\er011_news_ledger_enrichment_ab_trial_12_
  run.py`
- `C:\Users\tensh\eigo-radio\er003_output\n3_01\hanshin\a2\article.md`
- `C:\Users\tensh\eigo-radio\er003_output\n3_01\hanshin\a2\audit\
  deviation_full_record.json`
- `C:\Users\tensh\eigo-radio\FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-
  DISAMBIGUATION-TRIAL-14_REPORT.md`(2-2節・4節)
- `C:\Users\tensh\eigo-radio\er011_output\news_ledger_enrichment_ab_
  trial_12\factcheck_censored\current_a2_run1\fact_qa.json`
  (Fushimi誤り実データ)
