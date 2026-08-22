# ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01 完了報告

数値正規化の一般化＋Production原価ロジック再精査。新規有料API呼び出しは0件(既存コードとログのみで完結)。

---

## 0. §21 質問への回答(先にまとめて回答)

| # | 質問 | 回答 |
|---|---|---|
| 1 | 数値正規化はどこまで一般化したか | cardinal(2桁以上・hundred/thousand/million)、桁区切りカンマ、小数点、パーセント、通貨($)、序数(third以降)を一般化。ordinalの"first"/"second"は副詞用法との曖昧性が高いため意図的に対象外とした(§4参照) |
| 2 | BoavidaはPASSになるか | **PASSになる**(実測確認済み。"28"↔"twenty-eight"が原因でTRUE_CONTENT_MISMATCHだったものがNORMALIZED_MATCHへ) |
| 3 | three→3:00はFAIL維持か | **維持**(regression testで明示的に確認、絶対にPASSしない) |
| 4 | false numeric PASS有無 | **0件**(新規追加した安全fixture9件・既存fixture含む全32件全PASS) |
| 5 | 数値改善で回避できるattempt数 | 実測11attempt(Subscriptions full_story_part2、12回→1回相当) |
| 6 | 数値改善による削減額 | **¥44.6**(同segment、実測ベース試算) |
| 7 | Clean Search/Research Cost | ¥2.43/pair |
| 8 | Clean Writer/Support Cost | ¥1.64/pair |
| 9 | Clean Pronunciation Cost | ¥0.22/pair(抽出のみ、常時実行分) |
| 10 | Clean TTS Cost | ¥51.95/pair(Gemini Batch + Master Audio適用後) |
| 11 | Clean Primary ASR Cost | ¥8.90/pair(OpenAI英語+Azure日本語、単発) |
| 12 | Expected Secondary ASR Cost | ¥4.01/pair(conditional、ESTIMATEラベル、根拠は§11) |
| 13 | Expected TTS Retry Waste | ¥41.43/pair(実測waste比1.68倍ベース) |
| 14 | Total Clean Cost | **¥65.14/pair** |
| 15 | Total Expected Waste | **¥46.03/pair** |
| 16 | Total Expected Production Cost | **¥111.17/pair** |
| 17 | ¥106.4と¥113.0の差の原因 | §8参照。¥106.4はPronunciation/Cascade費用を一切含んでいない値(その時点で未実装だったため)。¥113.0はPronunciation/Cascade費用を含めたが、発動率の仮定(1.3回/topic)が実測(3 topic中2回=0.67回/topic)より高く、根拠薄弱だった。今回、実測に基づき再構築した¥111.17を正とする |
| 18 | 20 Topic/day月額 | **¥66,702** |
| 19 | 30 Topic/day月額 | **¥100,053** |
| 20 | 100/300/500/1000 users原価率 | 20t/day: 136.1%/45.4%/27.2%/13.6%。30t/day: 204.2%/68.1%/40.8%/20.4%(§18) |
| 21 | Audio QA追加開発を終了できるか | **主要な数値正規化開発は終了してよい**。今回の一般化で、既知の数値表記由来falseNGパターン(cardinal・comma・decimal・percent・currency・ordinal)は一通りカバーした。Cascade自体のProduction default化は引き続き追加検証待ち(OPEN-48から継続) |
| 22 | 残存Open Item | OPEN-49として記録(§10) |
| 23 | 新規API Cost | **¥0**(既存コード・既存ログの再分析のみ、新規TTS/ASR/LLM呼び出しなし) |

---

## 1. ER-006-NUMERIC-NORMALIZATION-01: 数値正規化の一般化

### 1.1 実装内容

`er006_preprod_hardening_01_validation.py`の`normalize_text()`内で使っていた、2〜12限定の単語⇔算用数字変換(`_EN_NUMBER_WORDS`)と、無条件の序数接尾辞除去(`_ORDINAL_RE`)を、新しい`normalize_numeric()`関数へ置き換えた。

| 対象 | 例 | 実装方式 |
|---|---|---|
| cardinal number(桁数無制限) | 28↔twenty-eight、125↔one hundred twenty-five、2023↔two thousand twenty-three | 汎用のword-to-number parser(ones/tens/hundred/thousand/millionの組み合わせを解釈) |
| 桁区切りカンマ | 1,000↔1000 | digit間のカンマのみ除去(3桁区切り位置限定) |
| 小数点 | 2.5↔two point five | "digit point digit"パターンをマーカーへ変換(後段の記号除去で消えないよう保護) |
| パーセント | 28%↔twenty-eight percent | digitの直後の%/percentをマーカーへ変換 |
| 通貨($のみ) | \$5↔five dollars | 前置$と後置dollarsをどちらもマーカーへ統一 |
| 序数(third以降) | third↔3rd | 序数語→算用数字+序数接尾辞(基数へは変換しない) |
| 日付文脈の序数接尾辞 | March 4th↔March 4 | **月名の直後のみ**に限定(従来は無条件で全ての"28th"型を"28"へ変換していたため、"28 ≠ 28th"という意味の違いを見逃す実バグがあった。今回修正) |

### 1.2 意図的に対象外としたもの

- **"first"・"second"**: 序数としてだけでなく"may first run"(副詞、「まず最初に」の意)のような数とは無関係な高頻度用法があるため対象外。実際に既存fixture("may first run" vs "May 1st")で、含めると誤ってPASSしてしまう回帰を検出したため除外した。
- **複合序数**(twenty-eighth等): 実装したが検証中に不完全な変換になる既知の限界を発見(§10 Open Item参照)。今回のfixture要件には含まれないため、安全側(未変換のまま残る=絶対にPASSしない)として許容した。
- **大きな通貨(¢・€・£等)**: $のみ対応。他通貨記号は将来必要になった時点で追加する。

### 1.3 発見・修正した実バグ

検証中に、既存の`_ORDINAL_RE`(序数接尾辞の無条件除去)が"28"と"28th"を同一視してしまう実際のバグを発見した(`classify_asr_match("The study included 28 articles.", "The study included 28th articles.")`が誤ってNORMALIZED_MATCHを返していた)。月名直後限定の`_DATE_ORDINAL_RE`へ置き換えて修正し、regression fixtureへ追加した。

---

## 2. 安全性の実証(§4)

以下を全てregression fixture化し、**絶対に一致してはいけない**ことを確認した(全てTRUE_CONTENT_MISMATCH、should_pass=False)。

| ケース | 結果 |
|---|---|
| three ≠ 3:00 | ✓ 維持(桁が変わる) |
| 28 ≠ 28th | ✓ 維持(今回発見・修正した実バグ) |
| 5 ≠ \$5 | ✓ 維持(通貨マーカーで区別) |
| 5 ≠ 5% | ✓ 維持(パーセントマーカーで区別) |
| 1.5 ≠ 15 | ✓ 維持(小数点マーカーで区別、後段の記号除去で"1 5"に分断されない) |
| 2023 ≠ 2024 | ✓ 維持(値そのものが違う) |
| 2016 ≠ "2,016 people"(挿入語含む別文脈) | ✓ 維持(挿入語の検出でcatch) |
| 28% ≠ 30%(値違い) | ✓ 維持 |
| "5 dollars" ≠ "5"(単位脱落) | ✓ 維持 |

**数字だけ抽出して一致すればPASS、という実装はしていない**。既存のprotected_check(digit/date/negation保護、content-word検証、normalized match)の枠組みはそのまま維持し、その入力となる正規化ロジックだけを安全に拡張した。

---

## 3. 実fixtureでの再評価(§6)

### 3.1 PASS期待ケース(実測)

| ケース | 結果 |
|---|---|
| 28 ↔ twenty-eight | ✓ NORMALIZED_MATCH |
| two ↔ 2 | ✓ NORMALIZED_MATCH(既存維持) |
| street ↔ St. | ✓ NORMALIZED_MATCH(既存回帰確認、劣化なし) |
| 125 ↔ one hundred twenty-five | ✓ NORMALIZED_MATCH |
| 2023 ↔ two thousand twenty-three | ✓ NORMALIZED_MATCH |
| 1,000 ↔ 1000 | ✓ NORMALIZED_MATCH |
| 28% ↔ twenty-eight percent | ✓ NORMALIZED_MATCH |
| \$5 ↔ five dollars | ✓ NORMALIZED_MATCH |
| 2.5 ↔ two point five | ✓ NORMALIZED_MATCH |
| third ↔ 3rd | ✓ NORMALIZED_MATCH |

### 3.2 Public Benches Boavida segmentの再判定

```
canonical: "...examined 28 articles published from 2020 to 2023."
Azure Secondary ASR(実測): "...examined twenty-eight articles published from 2020 to 2023."
判定(旧): TRUE_CONTENT_MISMATCH
判定(新): NORMALIZED_MATCH ✓
```

前回タスク(ER-006-AUDIO-RETRY-CASCADE-PROD-01)で「Secondary ASRは固有名詞を正しく認識したのにsegment全体はFAILする」と報告した問題が、今回の数値正規化で解消したことを実測確認した。

---

## 4. TTS retry削減効果の再計算(§7)

既存10件の音声生成監査ログ(audit/tts_generation_results.json)全件を、旧Validator(今回の変更前)と新Validatorの両方で再評価し、差分を確認した(新規TTS/ASR呼び出しは行っていない)。

| Segment | 旧判定 | 新判定 | 原因 |
|---|---|---|---|
| Public Benches Boavida(A2 full_story_part2) | (stored audit上はOK、ただし前回タスクの再ASR実測ではFAIL) | PASS | 28↔twenty-eight |
| **Subscriptions full_story_part2(A2)** | STOPPED(12回attempt全滅) | **PASS**(既存attemptの中に、今回の正規化で合格する回答が実在した) | "Eighth Circuit"(canonical)↔"8th"(Azure ASR)、序数語の一般化 |

他8件の既存STOPPED/UNCERTAIN segmentは、旧Validator時点で既にPASSしていた(prior task群の成果、今回の数値正規化とは無関係)か、日本語segment(このValidatorの対象外)だった。

**回避attempt数**: Subscriptions full_story_part2は実際に12回のTTS+ASR attemptを消費してSTOPPEDになっていたが、今回の修正により既存attemptの中の1回が合格と判定される。もし今回の修正が最初から入っていれば、残り11回のattemptは不要だった。

**回避cost**: 11 attempt × 平均attempt単価(TTS+ASR、¥4.05/回、既存セッション確立値) ≈ **¥44.6**。

---

## 5. 原価SSOT(§9〜11)

### 5.1 4分類の原則(§10)

- **Historical Actual**: 過去に実際に払った額(旧Azure全言語ASR + Standard TTS基準、ER-006-AUDIO-COST-PILOT-02の実測¥306/pair)。
- **Clean Production Cost**: 全工程が初回成功した場合(Batch TTS・Master Audio・新ASR構成前提)。
- **Expected Waste**: 現実のretry/secondary/research発動率を反映した追加費用。
- **Expected Production Cost**: Clean + Expected Waste。

### 5.2 Stage別内訳(§17の表)

| Stage | Clean Cost/pair | Expected Conditional/Waste | Expected Total | 根拠 |
|---|---|---|---|---|
| Search/Research | ¥2.43 | ¥0(常時1回のみ、条件分岐なし) | ¥2.43 | 実測(既存確立値) |
| Writer/Support | ¥1.64 | ¥0(Luna固定、条件分岐なし) | ¥1.64 | 実測(既存確立値) |
| Pronunciation(抽出) | ¥0.22 | — | ¥0.22 | 実測平均(3topic: ¥0.16/0.25/0.27相当) |
| Pronunciation(Research) | — | ¥0.59(**ESTIMATE**) | ¥0.59 | 実測cache miss単価(¥0.88、Startups Katz/Shapiro)×実測cache miss率(2/3 topic) |
| TTS(Gemini Batch+Master Audio) | ¥51.95 | (下記waste行に統合) | ¥51.95 | 実測(Pilot Actual実測値から按分・Batch/Master Audio割引を適用、二重計上なし) |
| Primary ASR(OpenAI EN+Azure JA) | ¥8.90 | (下記waste行に統合) | ¥8.90 | 実測(同上) |
| TTS/ASR Retry Waste | — | ¥41.43(実測waste比1.68倍) | ¥41.43 | 実測(PILOT-02、79 attempts/47 segments) |
| Secondary ASR(Cascade) | — | ¥4.01(**ESTIMATE**) | ¥4.01 | 実測per-trigger単価(¥4.01=(¥6.59+¥1.43)/2)×**保守的estimate**(1回/topic、根拠は§6) |
| **Total** | **¥65.14** | **¥46.03** | **¥111.17** | |

Master Audio・Gemini Batchは実測値へ直接反映済みであり、Clean Costに二重計上していない(§14確認)。Primary #2・Azure Secondary・追加Pronunciation Research・TTS retryは全てExpected Waste側へ分離している(§11・§15確認)。

### 5.3 ESTIMATEラベルの根拠(§12優先順位に従う)

- **Pronunciation Research conditional**: 実測cache miss単価(startups、Katz+Shapiro 1リクエスト実測¥0.88)を、実測cache miss率(3 topic中2 topicが新規research要=2/3)へ適用。優先順位1(既存3 Topic全segment実測)に基づくが、cache hit/miss率のサンプル数が3 topicのみと小さいため、estimateラベルを維持する。
- **Secondary ASR conditional**: 前回タスク(RETRY-CASCADE-PROD-01)は「1.3回/topic」という根拠不明の仮定を使っていた。今回、実測データ(3 topic・6 segment中2回発動=1topicあたり実測0.67回)を確認したが、これは**意図的に過去のfailureを集めた6 segmentのサンプル**であり、全segment(1topicあたり約47segment)に対するランダムサンプルではない(§12の警告に該当)。そのため実測0.67回をそのまま使わず、より保守的な「1回/topic」を採用しつつ、これがestimateであることを明記する。真の発動率を得るには、ランダムに選んだ全segmentでの追加検証が必要(§10 Open Item)。

---

## 6. ¥106.4と¥113.0の差の説明(§8)

| 報告 | 値 | 内訳 |
|---|---|---|
| ER-006-AUDIO-COST-PILOT-02 | ¥106.4/pair | Clean(¥64.9) + TTS/ASR retry waste(¥41.5、実測1.68倍)。**Pronunciation/Cascade費用は一切含んでいない**(その時点で未実装のワークストリームだったため) |
| ER-006-AUDIO-RETRY-CASCADE-PROD-01 | ¥113.0/pair | 上記¥106.4 + Pronunciation/Cascade増分¥6.6。ただしこの増分は「Cascade発動1.3回/topic」という**根拠不明の仮定**を使っており、実測(3 topic中2回発動=0.67回/topic)より高く見積もっていた |
| 本タスク(reconciled) | **¥111.17/pair** | Clean(¥65.14、再計算でほぼ同値・整合確認) + Waste(¥46.03: TTS/ASR¥41.43実測 + Pronunciation¥0.59実測ベース + Cascade¥4.01保守的estimate) |

**結論**: ¥106.4と¥113.0はどちらも「間違い」ではなく、**スコープが違う値**だった(¥106.4はPronunciation/Cascade抜き、¥113.0はPronunciation/Cascade込みだが根拠の薄い仮定を使用)。今回、実測データに基づいて再構築した**¥111.17/pairを正**とする。

---

## 7. 月次試算・490円プラン参考原価率(§18)

決済手数料・infra・CS・marketingは含まない(参考値)。

| | 20 Topic/day | 30 Topic/day |
|---|---|---|
| 月額AI content cost | ¥66,702 | ¥100,053 |

| Topic/day | 100 users(¥49,000) | 300 users(¥147,000) | 500 users(¥245,000) | 1,000 users(¥490,000) |
|---|---|---|---|---|
| 20 | 136.1% | 45.4% | 27.2% | 13.6% |
| 30 | 204.2% | 68.1% | 40.8% | 20.4% |

---

## 8. Regression Test・制約確認

- `er006_preprod_hardening_01_validation_test.py`へ新規fixture18件を追加(POSITIVE 9件・NEGATIVE 9件)、既存分と合わせて**全32件PASS**。
- 他11スイート(Ledger・ASR routing・Master Audio Store・Cascade等)含め、**全12スイートPASS**(regression破壊なし)。
- サービス仕様変更なし。新規Full Episode生成なし(既存の10件のaudit/audio生成ログを再分析したのみ)。
- 新規有料API支出: **¥0**(コード変更とログ再分析のみで完結)。

---

## 9. Audio QA追加開発の終了可否(§19)

主要な数値表記由来のfalse NGパターン(cardinal・カンマ・小数点・パーセント・通貨・序数)は今回で一通りカバーした。これ以上の数値Validator拡張(通貨他記号・複合序数・year-pair読み等)は、実際に必要になった時点で追加する方針とし、**今回で数値正規化の一般開発は一区切りとする**。

一方、Secondary ASR Cascadeの実効性検証は依然サンプル不足であり(OPEN-48から継続)、Production default化の判断は追加検証を待つ。

---

## 10. 残存Open Item(OPEN-49)

1. **複合序数**(twenty-eighth等)の変換が不完全(未変換のまま残るため安全側だが、吸収漏れとして残る)。
2. **Cascade発動率のランダムサンプル検証が未実施**: 今回のestimate(1回/topic)は意図的に過去failureを集めた6 segmentのサンプルに基づく保守的な値であり、全segmentのランダムサンプルでの実測が望ましい。
3. **year-pair読み**(twenty sixteen=2016のような、hundred/thousandを使わない年の特殊な読み)は未対応(§3で候補に挙がっていたが、安全な実装に追加検証が必要なため今回は見送った)。
4. **Pronunciation Research cache-hit率の追加サンプル**: 3 topicのみのサンプルであり、統計的信頼性を上げるにはさらに多くのTopicでの観測が必要。

---

完了後STOP。残りPool Topic量産には進まない。
