# FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01 報告書

管理ID: `FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`
(read-only設計作業。SSOT編集・Git操作・コード変更・API支出は一切行っていない。
本報告書ファイルの新規作成のみ)

## 要点(5行)

1. 現行News Family Production経路(Verified Fact Ledger→Writer→Fact
   Checker、`er003_v1_n3_01_articles_generate.py`)には、今回も
   「日本人名の英語表記を事前にWeb検索確認しWriterへ反映する」専用機構は
   **見つからなかった**(前回結論を維持)。
2. ただし今回の再探索で、**歴史的な未配線コード**を1件新規発見した。
   `generate_test.py`(2026-07-14 Initial commitから存在、CURRENT_SPEC.md
   517行で「無関係な別番組専用」と明記された旧スクリプト)には、まさに
   ユーザーが記憶する仕組み(`extract_names`→`verify_romanization`
   [OpenAI Web検索ツール]→`NAME_GLOSSARY`キャッシュ)が実装されていたが、
   **構築した`verified_glossary`はどのプロンプトにも一度も注入されず**
   (`FACTS`変数は生の日本語のまま4箇所のプロンプトへ直接使われる)、
   自身のファイル内で最初から死蔵コードだった。現行News Productionへは
   引き継がれていない。
3. Failure modeは人名に限らず固有名詞一般に及ぶが、実データ確認では
   **日本語発の固有名詞(選手名・地名等)を含むテーマでのみ発生**する
   (Health/Household等の英語一次情報源テーマのLedgerには、そもそも
   ローマ字化が必要な日本語固有名詞が登場しないため無縁)。
4. 候補4案+組み合わせを、品質/コスト/実装影響/再発防止力/既存機構との
   重複の5軸で比較した(下表)。既存Gate順序(Point Overlap Gate→Fact
   Checker)を変更する案はSTOP必須級のため、まず**Gate順序を変えない
   予防的候補(a)**を推奨Trialとする。
5. Production判断が必要な点(Ledgerスキーマ変更の要否、CURRENT_SPEC
   改訂の要否等)を5節に列挙。本タスクでは実施・実装は一切行っていない。

---

## 1. 再確認結果(2回目、前回と異なる探索経路)

### 1-1. 探索方法

前回(`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-RECONCILE-01_REPORT.md`)
とは異なる語で再Grepした: `katakana_name`/`player_name`/`roster`/
`official_site`/`npb`/`english_name`/`name_map`/`spelling`/
`transliterat`/`Hepburn`/`ヘボン`。加えて、Research/Search系プロンプト
本文(`er002_ja_web_research_r3.py`、`er003_v1_translator_briefs/*.txt`)、
Ledger生成箇所、Writer system prompt、`CURRENT_SPEC.md`の
「固有名詞」「人名」節、`ARTIFACT_REGISTRY.md`を個別に確認した。

### 1-2. 現行Production経路への結論(維持)

- `er002_ja_web_research_r3.py`(Fact Checkerプロンプト構築)に
  `person`/`人名`/`proper noun`/`固有名詞`の語は一切出現しない。
- Writerプロンプトテンプレート(`er003_v1_translator_briefs/
  a2_p1_r3_prompt_template.txt`・`a2_vocab_qa_prompt_template.txt`)に
  出現する「proper noun」関連記述は、**語彙密度カウントの除外規則**
  (5語制限に数えない、人名を繰り返し使うか短縮するか)のみであり、
  綴りの正しさを検証する指示は無い。
- `CURRENT_SPEC.md`の「固有名詞」「人名」を含む行(501/862/957/959/
  974-975/991/1012-1019/1024/1074行)は、すべて既存3機構(語彙密度
  ルール・ASR/TTS発音判定・Pronunciation Ledger運用・Human Review
  表示ルール)に関する記述であり、英語記事本文の綴り事前確認とは無関係
  (前回報告の分類と一致)。
- `ARTIFACT_REGISTRY.md`に`Ledger`の語は2箇所あるが、いずれも記事一覧
  表の列名・過去案の言及であり、canonical spelling関連の記載は無い。

### 1-3. 新規発見(前回未検出): `generate_test.py`のNAME_GLOSSARY

`generate_test.py`(News Familyの現行`er003_v1_n3_01_articles_generate.py`
とは別の、より古いスクリプト。git初回コミット2026-07-14 14:51から存在。
`CURRENT_SPEC.md` 517行で「`levels.py`のA2/B1/B2数値は、
`generate_test.py`/`tts_test.py`という**無関係な別番組専用**の値であり、
このCEFR表には一切採用していない」と明記されている)に、以下の実装が
`git log --all`の初回コミットから存在することを確認した。

```
generate_test.py 180-233行:
NAME_GLOSSARY = {}  # 確認済みの正しい英語表記をキャッシュ

def extract_names(text):
    """FACTSに含まれる固有名詞を機械的に抜き出す(NER的な処理)。"""
    ...

def verify_romanization(name):
    """OpenAIのWeb検索ツール(Responses API)を使い、実在人物の
    正しい英語表記を確認する。"""
    res = client.responses.create(..., tools=[{"type": "web_search"}], ...)
    return res.output_text.strip()

def build_verified_glossary(text):
    """FACTS内の固有名詞を抽出し、1つずつ検索して正しい表記を確認、
    辞書として返す。"""
    ...
```

呼び出し箇所(430-433行):
```
if NEEDS_NAME_CHECK:
    verified_glossary = build_verified_glossary(FACTS)
    NAME_GLOSSARY.update(verified_glossary)
```

**しかし`verified_glossary`/`NAME_GLOSSARY`は、このファイル全体でこの
2箇所以外に一度も参照されない**(`grep -n "NAME_GLOSSARY\|glossary"`で
確認、380/493/563/747行の実際のWriterプロンプトはすべて生の`FACTS`
[日本語のまま]を直接埋め込んでおり、glossaryの結果は反映されない)。
つまりこの機構は、Web検索まで実行してキャッシュを構築しておきながら、
**その結果をプロンプトへ注入する配線が最初から無い**、`generate_test.py`
自身の中でも未完成・死蔵状態のコードだった。

**訂正・結論**: ユーザーが記憶する「Web検索で事前確認しWriterへ反映する」
という**着想自体は過去に実装が試みられたことがある**(2026-07-14時点)が、
(a)対象は現行News Family Productionとは別の旧スクリプトであり、
`CURRENT_SPEC.md`上も明示的に無関係と区別されている、(b)そのスクリプト
内でも実際にはWriterへ反映されておらず未配線のまま放置されていた、
という2重の理由で、**現行Production経路には一度も実効した対策として
存在したことがない**。前回報告の「専用対策はNEW(存在しない)」という
結論の実質(現行Production経路に有効な対策は無い)は変わらないが、
「一度も着想・試作されたことがない」という部分は誤りであり、ここで
訂正する。

## 2. Failure mode定義(固有名詞一般)

**定義**: Ledgerに日本語表記しかない固有名詞(人名・球団名・地名・製品名
等)をWriter(LLM)が英語記事本文へ変換する際、公式のローマ字表記を
確認せず推測で生成するため、(1)同一人物・同一団体でも実行のたびに
綴りが揺れる、(2)Fact Checkerに到達しない限り検出されない、という
再現性・検出可能性の欠如が起きる。

**対象が人名に限らないことの実データ確認**: 実際のNews Family Ledger
(`er003_output/n3_01/hanshin/a2/audit/deviation_full_record.json`)は
選手名(FACT-03「伊原陵人」、FACT-05「伏見寅威」)を日本語表記のみで
保持しており、これは人名固有の問題ではなく、**Ledgerが日本語で記録した
固有名詞全般に共通する構造的な弱点**である(球団名・スタジアム名・
戦術用語等も理論上同型のリスクを持つ)。

**Hanshin以外のNewsテーマでの発生有無**: 同じFamily A Newsの他テーマ
(`er003_output/n3_01/health`・`n3_01/household`)のLedgerを実際に
確認したが、これらは大学Extension機関・学術誌等の**英語一次情報源**を
直接調査して作成されており、Ledger自体に日本語表記の固有名詞がほぼ
登場しない(著者名も英語論文の表記がそのまま使える)。したがって、
今回のfailure modeは「Ledgerが英語一次情報源のテーマでは顕在化せず、
日本語一次情報源(NPB公式・日本語報道等)を扱うテーマでのみ顕在化する」
という条件付き汎化性を持つ。Hanshin以外にも、将来的に日本語発の
News/Trendテーマ(選挙・企業・地方自治体等)が扱われれば、同型の
再発可能性がある。

## 3. 候補設計と比較

| 候補 | 概要 | 品質(検出率/誤修正リスク) | コスト(¥/記事の目安) | 実装影響 | 再発防止力 | 既存機構との重複 |
|---|---|---|---|---|---|---|
| (a) Ledger schema拡張(Research段階でWeb検索取得) | `canonical_en_spelling`/`reading`列をLedgerへ追加し、既存Research呼び出し(WebSearch/WebFetch)の中で日本語固有名詞ごとに公式英語表記を1回確認、Ledgerへ記載してからWriterへ渡す | 高。Writerが生成前に正しい表記を与えられるため、揺れそのものを事前に防止(予防的)。誤修正リスクは低い(Ledgerが正としての扱いになるのみ) | 小〜中。既存Research呼び出しへの追記のため増分小(Trial規模で概算¥50〜100/記事) | 中。Ledger生成コード・Researchプロンプトの変更、Ledgerスキーマ変更を伴う(`CURRENT_SPEC.md`のLedger仕様に触れるため正式仕様変更の可能性) | 高。未出の固有名詞にも将来Research時に同じ手順が適用され汎化する。News以外のFamilyでもLedgerを使う限り横展開可能 | Pronunciation Ledger(発音)とは対象が異なり重複しない。Fact Checker(事後検証)とも独立(こちらは事前防止) |
| (b) Writer前処理でcanonical spelling表を供給(`generate_test.py`のNAME_GLOSSARY方式を現行パイプラインへ再設計・移植) | Writer呼び出し直前に固有名詞抽出+Web検索確認の独立ステップを挟み、Ledger本体は変更せず「補助資料」としてWriterへ渡す | 高。ただし`generate_test.py`で実際に起きた「構築したが注入し忘れる」配線漏れの再発リスクを明示的にテストで防ぐ必要がある | 小〜中。(a)とほぼ同等(Web検索1回/固有名詞、キャッシュ再利用可) | 中。新規ステージ(Writer呼び出しラッパー)を追加。Ledgerスキーマ自体は変えないため(a)よりCURRENT_SPEC変更の範囲は狭い可能性があるが、新規ステージ追加自体はPM承認手続きの対象 | 高。汎化可能だが、記事間キャッシュの永続化層を別途持たない場合、(a)よりLedger経由の再利用性が弱い(同じ選手名が別記事に出るたび再検索するおそれ) | Pronunciation Ledgerの`_resolve_unresolved_entity_for_review()`とロジックの一部再利用を検討できる余地がある |
| (c) Fact Checkerの固有名詞検証をPoint Overlap Gateより前に独立ステージ化 | 既存Fact Checker(実証済みで人名誤りを検出できる)を、現状の「Gate順序次第でスキップされる」状態から、必ず1回実行される独立ステージへ昇格させる | 中〜高。検出は既存機構の実証済み能力に依存(Trial-14実績: 人名FAILの77.8%を発見)。ただし「検出」であり「事前防止」ではなく、記事は一度誤ったまま生成される。自動修正まで行うなら別途retry設計が必要でスコープ拡大 | 小。Gate順序変更のみなら追加Web検索なし(既存Fact Checker呼び出しコストのみ) | 大。既存の意図的なGate順序設計(Point Overlap Gate優先)を変更するため、`docs/pm/PM_GOVERNANCE.md`のSTOP必須級の仕様変更に該当。既存retry/fallback設計との整合確認が必須で、安全装置の独自変更は不可 | 中。検出はできるが記事が一度誤って生成されること自体は防がない。人間レビュー負荷が増える可能性 | Fact Checkerという既存機構の運用順序変更のみで、新規開発コストが小さい点がメリット。ただし前回reconcile報告の候補(b)と同一系譜であり、既に「慎重な検討が必要」と整理済み |
| (d) TTS safe-reading側で対応(Writer出力は直さない) | Pronunciation Ledgerの発火条件・カバレッジを拡張し、TTS音声側だけ正しく読ませる | 低。英語記事本文自体の綴り誤りは読者に見える形で残るため、根本原因を解決しない | 低〜中。既存Pronunciation Ledger機構の延長で済む可能性 | 小。既存機構の閾値・トリガー調整のみ | 低。本文綴りの推測揺れという根本原因は放置される | Pronunciation Ledgerの既存設計制約(「本文を書き換えない」)と完全に一致するが、それゆえ今回のfailure mode(本文綴り)には非対応のまま |
| 組み合わせ (a)+(c) | Ledgerへ正式表記を記載する予防策と、Fact Checker必須実行による事後検出策を併用(多層防御) | 最も高い(予防+検出の二重化) | (a)+(c)の合算(小〜中) | 最大。(c)のGate順序変更を含むためSTOP必須級 | 最も高い | 重複は無いが、(c)単体の実装影響の大きさをそのまま引き継ぐ |

## 4. 推奨Trial案

### 4-1. 推奨案: 候補(a) Ledger canonical spelling追加Trial

- **目的**: Verified Fact Ledgerに日本語固有名詞の公式英語表記
  (`canonical_en_spelling`)を追加することで、Writerが生成のたびに
  ローマ字表記を推測する揺れを事前に無くせるかを検証する。
- **仮説**: Ledgerに固有名詞ごとの公式英語表記を明記し、Writerプロンプト
  に「Ledgerに記載された表記をそのまま使うこと」という指示を追加すれば、
  人名等のローマ字誤りが実行間で再現的に解消する。
- **条件**: 既存Hanshin Ledger(`hanshin_ledger_condition_b_enriched.txt`
  等、Trial-12/14で使用したもの)の日本語人名(伊原陵人・伏見寅威・
  E.モンテロ等)に対し、Web検索で公式英語表記を1回ずつ確認し
  `canonical_en_spelling`欄を追記した改訂Ledgerを作成、既存条件との
  A/B比較を行う。
- **N**: 既存Trial-12/14と同様の規模(N=6程度、条件あたり複数run)で
  十分な統計的手がかりが得られる(前例踏襲、過大なNは不要)。
- **既存harness再利用可否**: `er011_news_ledger_enrichment_
  disambiguation_trial_14_run.py`は、Ledgerテキストの機械的な
  Fact抜粋・合成(`build_ledger_e_stage()`)、Fact Checker単独実行
  (`run_one_factcheck()`)、コスト集計(`compute_cost_so_far_jpy()`)の
  各関数を既に持っており、**Ledger本文に`canonical_en_spelling`行を
  追記する処理を追加するだけで再利用可能**(新規harness構築は不要、
  既存関数の入力Ledgerテキストを差し替えるだけで済む)。
- **受入基準**:
  - 人名ローマ字FAIL率: Trial-14実測(FAIL 9件中7件が人名ローマ字誤り
    =77.8%)を上回る低減を確認する(具体的な目標値はユーザー承認が
    必要、本報告書では未確定のまま提示のみ)。
  - 真のfact誤り(数値・日付等)の見逃しが増えていないこと(Overlap
    Gate通過記事に対するFact Checker本来の検出力を退行させていないか
    を既存条件との比較で確認)。
  - Point Overlap指標(overlap率等)が悪化していないこと(Ledger変更が
    本文の重複判定に悪影響を与えていないかの確認)。
- **費用見込み**: 既存Research呼び出しへのWeb検索追加(固有名詞1件
  あたり1回、Hanshin Ledgerなら人名5〜7件程度) + Fact Checker
  再実行(A/B比較分)で、**概算¥100〜200程度**(Trial-12/14と同等規模の
  小規模Trial)。
- **Closeout語彙**: `VALIDATED`(受入基準を満たした場合)/
  `PARTIALLY_VALIDATED`(一部指標のみ改善)/`NOT_VALIDATED`
  (効果が確認できない場合)。いずれもTrial結果であり、Production採用は
  別途ユーザーの`APPROVED_FOR_PRODUCTION`判断が必要。

### 4-2. 代替案: 候補(b) Writer前処理でのcanonical spelling供給Trial

- **目的・仮説**: (a)と同じだが、Ledger本体を変更せず、Writer呼び出し
  直前の独立ステップとして固有名詞抽出+Web検索確認を行い、結果を
  Writerプロンプトへ補助資料として注入する方式で同等の効果が出るかを
  検証する。
- **既存harness再利用可否**: Trial-14 harnessのFact Checker関連関数は
  流用できるが、新規に「固有名詞抽出→Web検索→注入」のラッパー関数を
  追加実装する必要がある(`generate_test.py`の`extract_names`/
  `verify_romanization`のロジックは参考にできるが、そのまま移植すると
  同じ「注入し忘れ」の配線漏れを再発するリスクがあるため、注入結果が
  実際にWriterプロンプトへ含まれていることを検証するテストを必須で
  追加する)。
- **(a)との主な違い**: Ledgerスキーマを変更しないため`CURRENT_SPEC.md`
  改訂の範囲は(a)より狭い可能性がある一方、記事間でのcanonical
  spelling再利用の永続化層(キャッシュ)を別途設計しない場合、同じ
  固有名詞が複数記事に登場するたびに再検索が発生し、(a)よりランニング
  コストが高くなる可能性がある。
- **受入基準・費用見込み**: 4-1と同様の枠組み(具体的な数値は同一報告書
  内で重複記載しない)。

## 5. Production判断が必要な点

- Verified Fact Ledgerのschema変更(`canonical_en_spelling`列の追加、
  候補(a))は、`CURRENT_SPEC.md`上のLedger仕様(News Familyの
  Source of Truth形式)に対する正式仕様変更に該当するか否か。該当する
  場合、Trial実施自体は`APPROVED_FOR_PRODUCTION`前でも許容されるか
  (既存Trial運用ルールの確認)、Ledger schema変更を伴わない候補(b)の
  方が承認手続き上軽いか。
- Writerプロンプトへ「Ledgerに記載された表記をそのまま使うこと」という
  指示を追加すること自体が、既存Writerプロンプト(`CURRENT_SPEC.md`で
  `DECIDED`済みの構造・文言生成ルール)への変更に該当するかどうか。
- 候補(c)(Gate順序変更)およびそれを含む組み合わせ案は、既存の意図的な
  Gate設計(Point Overlap Gate優先)の変更であり、`docs/pm/
  PM_GOVERNANCE.md`が定めるSTOP必須級の仕様変更に該当する。本タスクの
  範囲では候補として提示のみに留め、採否はユーザー判断とする。
- 受入基準の具体的な目標値(人名FAIL率の許容水準等)は本報告書では
  未確定のまま提示した。Trial実施前にユーザーが確定させる必要がある。
- Trial実施そのもの(¥100〜200程度の見込み)を許可するか、まず4-1/4-2
  のどちらを先に検証するかは、本タスクでは判断せずユーザーへ委ねる。

## 6. 参照artifact(絶対パス)

- `C:\Users\tensh\eigo-radio\FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-RECONCILE-01_REPORT.md`(前回調査、結論の一部を本報告書3節末尾で訂正)
- `C:\Users\tensh\eigo-radio\generate_test.py`(180-233行、380/493/563/747行、git初回コミット2026-07-14)
- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md`(517行「無関係な別番組専用」、501/862/957/959/974-1074行「固有名詞」「人名」関連箇所)
- `C:\Users\tensh\eigo-radio\ARTIFACT_REGISTRY.md`
- `C:\Users\tensh\eigo-radio\er002_ja_web_research_r3.py`
- `C:\Users\tensh\eigo-radio\er003_v1_translator_briefs\a2_p1_r3_prompt_template.txt`
- `C:\Users\tensh\eigo-radio\er003_v1_translator_briefs\a2_vocab_qa_prompt_template.txt`
- `C:\Users\tensh\eigo-radio\er003_output\n3_01\hanshin\a2\audit\deviation_full_record.json`
- `C:\Users\tensh\eigo-radio\er003_output\n3_01\health\a2\audit\deviation_full_record.json`
- `C:\Users\tensh\eigo-radio\er003_output\n3_01\household\a2\audit\deviation_full_record.json`
- `C:\Users\tensh\eigo-radio\er011_news_ledger_enrichment_disambiguation_trial_14_run.py`
- `C:\Users\tensh\eigo-radio\FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_REPORT.md`
