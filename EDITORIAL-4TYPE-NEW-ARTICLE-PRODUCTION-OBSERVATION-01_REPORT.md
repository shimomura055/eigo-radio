# EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01 REPORT

管理ID: EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(統合: PM-CLOSEOUT-CONSOLIDATION-128)
日付: 2026-09-14

4記事タイプ(News/Trend/Discovery/Voices)について、既存の正式Production
path(または正式初回経路)を使って新規トピックを生成できるかを観測した記録。
**本タスクは新仕様Trialではない**。4記事の生成成功を理由に、いかなる仕様の
Statusも変更していない(VALIDATED/APPROVED等への変更なし)。

---

## A. 記事

比較ページ(Reader-facing本文全文、直接開けるHTML):
`er014_output/four_type_observation_01/index.html`

- **News**(AI regulation vs AI race、A2、OK): AI安全規制とAI開発競争の
  緊張関係を扱うNews記事。既存の正式Research経路+`run_one_pattern()`で生成。
- **Trend**(The end of the smartphone as the main interface、B1=OK/
  A2=NG_REVIEW_REQUIRED): スマホがデジタル体験の唯一の入口ではなくなりつつ
  あるというTrend Synthesis記事。`run_writer_for_theme()`はB1+A2を常に両方
  生成する設計のため両方生成、B1は合格、A2はFact CheckerがFAILし人間レビュー
  対象(Production採用不可)。
- **Discovery**(Why can silence feel uncomfortable?、A2、OK): 沈黙が
  不快に感じられる理由についてのDiscovery Focus S2記事。正式Stage関数
  `run_one_pattern_staged_discovery_focus()`で生成。
- **Voices**(Is personalized news good for us?、2 Voices、未生成): 2 Voices
  で新規トピックを書き起こす正式Production pathが存在しないため、実装変更
  なしでSTOP(詳細はH節)。

---

## B. 品質(status/主要QA/retry/word count)

| Type | Status | 主要QA verdict | retry | word count |
|---|---|---|---|---|
| News | OK | Fact Checker PASS / Ledger Deviation COMPLIANT / Point Overlap retry 0 | 0 | 406 |
| Trend B1(main) | OK | Fact Checker REVIEW_REQUIRED / Ledger Deviation COMPLIANT / Point Overlap retry 0 | 0 | 394 |
| Trend A2(副産物) | NG_REVIEW_REQUIRED | **Fact Checker FAIL**(GoogleのXRメガネ発売時期の矛盾。他2件のunsupported claim) | 記事全体retry 1/2(Point Overlap起因) | 413 |
| Discovery | OK | Fact Checker PASS / Ledger Deviation COMPLIANT / Point Overlap retry 0 / Stage1 regen 0 | 0 | 569(`run_summary.json`実測。`wc -w`では603、差異未調査) |
| Voices | 未生成 | 該当なし | 該当なし | 該当なし |

補足所見(Fable所見、人間確認要):
- **Trend A2 Fact Checker FAILの内容**: 記事がGoogleのXRメガネを「まだ製品
  デモで発売未確認」と記述しているが、Googleは2026年5月19日に2026年秋発売を
  公式発表済みであり矛盾。これは既存QAが正しく機能した結果(QA自体の欠陥では
  ない)。
- **Trend B1にも同じ記述が残っている**: B1本文にも「Google’s XR glasses
  remain a development-stage demonstration」という同種の表現が含まれるが、
  B1のFact Checkerは`REVIEW_REQUIRED`(FAILではない)止まりで通過している。
  A2とB1でFact Checker判定が割れており、Research時点の情報が発表後に古くなる
  「Ledger鮮度」問題の可能性がある(人間確認要、Open Item候補G-6)。
- **Discovery「Point One」の専門語密度の疑い**: "Quiet Does Not Always Mean
  Calmest"のセクションに"parasympathetic activity" "fMRI acoustic noise"
  "sympathetic activity"等の専門用語が集中しており、A2レベルとして語彙難度が
  超過している疑いがある(Fable所見、人間確認要、Open Item候補G-7)。

---

## C. 量産コスト表(量産時1記事単価・Standard同期・今回実測)

| Type | 量産時実測単価 | retry追加分 | 備考 |
|---|---|---|---|
| News | ¥70.16 | ¥0 | Research/Ledger¥42.52・Writer¥2.84・QA¥24.80・rewrite¥0 |
| Trend(B1+A2合算) | ¥87.98 | ≈¥1.89(参考値、厳密な機械分離は未実施) | Research/Ledger¥48.73・Writer¥4.28・QA¥33.74・uncategorized¥1.22。A2はNG_REVIEW_REQUIRED |
| Discovery | ¥104.25 | ¥0 | Research/Ledger¥58.37・Stage1(Writer+Fact QA+Ledger Deviation)¥18.80・Stage2¥0.53・Stage3(Writer+EC)¥0.56・Point Value QA¥0.18・最終Fact Checker¥25.01・最終Ledger Deviation¥0.80 |
| Voices 2V | 未生成(¥0) | 該当なし | 生成未着手のためAPI呼び出しなし |
| **合計** | **¥262.39** | — | News+Trend+Discovery(Voices¥0) |

---

## D. API token表

| Type | Model | Input | Output | Cached | Total | Calls |
|---|---|---|---|---|---|---|
| News | gpt-5.6-luna | 307,109 | 39,908 | 4,471 | 347,017 | 8 |
| Trend(B1+A2合算) | gpt-5.6-luna | 429,193 | 57,225 | 25,884 | 486,418 | 17 |
| Discovery | gpt-5.6-luna | 445,091 | 38,180 | 18,070 | 483,271 | 11 |
| Voices | 該当なし | 0 | 0 | 0 | 0 | 0 |

- retry分離: News/Discoveryは記事全体retry=0のため全額が通常生成分。
  Trendは記事全体retry=1/2(A2側Point Overlap起因)発生しているが、
  `run_result.json`がB1B/A2ネスト形式のため`aggregate_usage.py`の自動判定が
  誤検出(`retry_occurred=false`)しており、retry専用tokenの厳密な機械分離は
  未実施(手動概算¥1.89相当のみ、C節参照)。全てprovider=openai。

---

## E. Claude Code利用量表

| Type | Claude usage/tokens | Tool uses | Delegations | 備考 |
|---|---|---|---|---|
| News | cumulative_usage計 7,458,389(初回1,500,661+再委任5,957,728、transcript実測4項目合算) | 35+67=102(実測) | 2(初回STOP+再委任、Fable実測) | input/output/cache内訳は取得不能。Fable自己申告tool call数(概算)12 |
| Trend | cumulative_usage 3,505,070(transcript実測) | 41(実測) | 1(Fable実測) | input/output/cache内訳は取得不能。Fable自己申告tool call数(概算)2 |
| Discovery | cumulative_usage 5,855,428(transcript実測) | 57(実測) | 1(Fable実測) | input/output/cache内訳は取得不能。Fable自己申告tool call数(概算)1 |
| Voices | cumulative_usage 1,376,256(transcript実測、`measure_delegation_task.py --task-id aed06c1b062a335c3`) | 23(実測) | 1(Fable実測) | input/output/cache内訳は取得不能。Fable自己申告tool call数(概算)3 |

cumulative_usageは「input+output+cache_read+cache_creationの4項目合算値」
(`measure_delegation_task.py`の標準出力フィールド、transcript実測)であり、
記事生成API tokenとは別枠(合算していない)。

**4記事全体のsession usage delta**: **取得不能**(Fable/SonnetからClaude
Codeのセッション利用枠・`/cost`・`/usage`値を取得する手段がないため)。
代替指標:
- 全委任のcumulative_usage合計: **18,195,143**(News 7,458,389+Trend
  3,505,070+Discovery 5,855,428+Voices 1,376,256)
- Fable通知の最終ターン値(委任文記載のまま、**最終ターン値であり累積では
  ない**点に注意): News初回93,138・News再委任144,148・Trend 124,254・
  Discovery 141,324・Voices 81,961(合計584,825)。上記cumulative_usage
  合計とは集計方法が異なるため単純比較不可(cumulative_usageは全ターンの
  token使用量合算、最終ターン値はセッション末尾1ターン分のみ)。

---

## F. 費用区分

- **量産API原価合計**: ¥262.39(News¥70.16+Trend¥87.98+Discovery¥104.25、
  Voices¥0)
- **開発・Trial/検証費**: ¥0(News初回STOP・Voices STOPともAPI呼び出し
  なしのため追加費用は発生していない)
- **Claude Code subscription usage**: 上記E節参照(金額換算不能。
  cumulative_usage合計18,195,143 token相当、内訳・セッション枠deltaは
  取得不能)

---

## G. 問題・Open Item候補(登録はしない、ユーザー判断待ち)

1. **2 Voices新規トピックWriterの正式Production path不在**(本タスクの
   主発見、Voices記事未生成の直接原因)。既存2 Voices Production runnerは
   承認済み既存記事の音声再配線専用で、新規トピックを書き起こす汎用Writer
   (`writer_generic.run_writer_stage_generic()`)は3 Voices専用
   (`make_theme_config()`がvoice_cards≠3をValueErrorで拒否)。対応方針
   (3V専用writer_genericを2V対応へ一般化する/2V専用の新規Writerを設計する
   /当面は対象外とする)はUSER_DECISION_REQUIRED。
2. **CURRENT_SPEC.md L760「手動供給のみ」表記と先例の不一致**: 既存Research
   正式経路で新規Ledgerを作成した先例(DECISION_LOG L941系、Trial-09/12)が
   あるにも関わらず、CURRENT_SPEC本文は「自動Research供給経路は未配線」と
   の表記のまま。SSOT表記の更新要否を確認要。
3. `run_writer_for_theme()`(Trend Synthesis正式経路)はA2単独生成の引数を
   持たず、常にB1+A2を両方生成する設計上の制約。
4. 「Trend Gate 6条件」という独立した番号付きリストがCURRENT_SPEC.md本体に
   見当たらず、実体はL757記載のFocus Module必須要件と解釈して判定した。
   正式なGate定義文書化の要否は要確認。
5. Cost Loggerの`stage`タグが粗く、工程別(Writer/QA/rewrite)原価を
   機械分離できない。今回はresponse_idをaudit JSON側と突合せて事後分類
   したが、Production自体には工程別コストタグ付け機構が無い。
6. **Trend A2 Fact Checker FAIL=QA正常動作だが、B1にも同じ「XRメガネは
   まだ開発段階のデモ」という記述が残っており、B1側はREVIEW_REQUIRED止まり
   で通過した**。Research時点の情報が発表後に古くなる「Ledger鮮度」問題の
   可能性がある(B節参照、人間確認要)。
7. **Discovery Point Oneの専門語密度の疑い**: "parasympathetic activity"
   "fMRI acoustic noise"等がA2レベルの語彙難度を超過している疑いがある
   (B節参照、人間確認要)。
8. **OPEN-120(3V保守版Fact Safetyゲート)のruntime evidenceは今回未取得**
   (Voices生成未着手のため)。
9. **OPEN-148該当のOverlap retryはDiscoveryで未発生**(追加事例なし。
   Trendでは1回発生しているが、既存Open Item自体は変更していない)。
10. Directional Fact Precheckが3記事(News/Trend B1/Discovery)すべてで
    `DIRECTION_REVIEW_REQUIRED`(advisory・non-blocking、既知の常時REVIEW
    挙動。ブロッキングではなく参考記録)。

---

## H. Status/Gate

4記事生成は新仕様Trialではなく、いかなる仕様Statusも変更していない
(VALIDATED/APPROVED等への変更なし)。Voices 2Vは生成未着手のため
Gate 1判定は行っていない(USER_DECISION_REQUIRED、G-1参照)。

---

## 参照

- 比較ページ: `er014_output/four_type_observation_01/index.html`
- 記事別詳細: `docs/pm/RESULT_PACKET_4T_NEWS.md` / `_TREND.md` / `_DISCOVERY.md` / `_VOICES.md`
- 実測ログ: `er014_output/four_type_observation_01/claude_usage_log.md`、
  `progress_log.md`、`path_survey.md`
- 数値源: `er014_output/four_type_observation_01/{news,trend,discovery}/observation.json`
- DECISION_LOG記録: `PM-CLOSEOUT-CONSOLIDATION-128`
