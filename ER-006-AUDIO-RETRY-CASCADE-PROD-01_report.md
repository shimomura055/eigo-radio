# ER-006-AUDIO-RETRY-CASCADE-PROD-01 完了報告

Pronunciation Ledger＋Primary/Secondary ASR CascadeのProduction配線とWaste実測。3トピック(Public Benches / Subscriptions / Startups)で検証した。

---

## 0. §26 質問への回答(先にまとめて回答)

| # | 質問 | 回答 |
|---|---|---|
| 1 | Cascade Production配線完了可否 | **完了**。本番の6箇所のASR呼び出し全てを、drop-in互換の新関数へ置き換えた(feature flag既定OFF、既存挙動と完全互換)。今回の検証実行時のみ明示的に有効化した |
| 2 | Public Benches結果 | 3対象中1件(Malmö/Triangeln)がPrimary#1のみで即PASS。残り2件(Ottoni・Boavida)はCascade4段階を尽くしてもHuman Review行き |
| 3 | Subscriptions結果 | 2対象(comment_2・full_story_part2)とも**Primary#1のみで即PASS**(Cascade発動せず)。旧Sol版では両方とも6〜12回試行してSTOPPEDだった箇所 |
| 4 | Startups結果 | Katz/Shapiro segment(旧版で12回試行しSTOPPED)が**Primary#1のみで即PASS**(Cascade発動せず) |
| 5 | Primary #1 PASS率 | 4/6(66.7%) |
| 6 | Primary #2追加解消率 | 0/2(0%、残り2件ともPrimary#2でも不一致のまま) |
| 7 | Azure #1追加解消率 | 0/2(0%、ただし対象固有名詞自体はPhrase Listで正しく認識されたケースあり、詳細は§4) |
| 8 | Azure #2追加解消率 | 0/2(0%、#1と同一結果) |
| 9 | Human Review率 | 2/6(33.3%) — ただし意図的に過去の既知failure箇所だけを選んだfixtureのため、通常segment全体に対する比率ではない |
| 10 | TTS retry before/after | Before: 対象6segment合計40回attempt。After: 新規TTS生成0回(既存音声を再利用し、ASRだけ差し替えて評価) |
| 11 | STOPPED before/after | Before: 6segment中5件がSTOPPED(Sol版4件+Luna版1件)。After: 2件がHuman Review行き(STOPPEDではなくASR_VALIDATION_UNCERTAINとして明示的に分類、残り4件はPASS) |
| 12 | UNCERTAIN before/after | Before: 0件相当(すべてSTOPPEDまで使い切っていた)。After: 2件がASR_VALIDATION_UNCERTAIN(適切にHuman Review行き) |
| 13 | true content error誤PASS有無 | **0件**(全6segment・Cascade全stepで確認) |
| 14 | Pronunciation Research cost | ¥0.88(Katz/Shapiro、Public Benches分は前回タスクで取得済みのcache再利用) |
| 15 | OpenAI追加ASR cost | ¥1.43(全Primary呼び出し合算、Primary#2含む) |
| 16 | Azure Secondary cost | ¥6.59(4回、Ottoni・Boavidaの Secondary#1/#2) |
| 17 | avoided TTS cost | **¥137.8**(6segment合計、旧attempt数から新規1attempt相当への削減を試算) |
| 18 | net savings | **¥128.4**(avoided ¥137.8 − 新規支出¥9.40) |
| 19 | 1 Topic B1+A2 Expected Production Cost | **¥113.0/pair**(PILOT-02の¥106.4 + 今回の増分¥6.6、Batch TTS・Master Audio・新ASR構成・Pronunciation Research・Cascade全込み) |
| 20 | 20 Topic/day月額 | **¥67,790** |
| 21 | 30 Topic/day月額 | **¥101,685** |
| 22 | このCascadeをProduction default化すべきか | **条件付き推奨**。§7参照。安全性(誤PASS0件)とnet savingsは確認できたが、Cascade自体が「発動して解決した」ケースは今回0件(発動2件とも未解決)であり、Cascadeの直接的な効果はまだ実証途上。まずはfeature flag ONのまま、より広いサンプルでの追加観測を推奨する |
| 23 | Audio QA追加開発を終了できるか | **一部終了、一部継続**。数字表記・略語吸収等の一般的なValidator改善は今回で一区切りとする。ただし28のような大きい数の綴り⇔算用数字ギャップ(新規発見)への対応は残る。第三のASR・phonetic MLは追加しない(§21の方針通り) |
| 24 | Human Review対象一覧 | §6参照(Ottoni・Boavida、canonical text・全4 step transcript・音声を記録済み) |
| 25 | 残存Open Item | OPEN-48として記録(§8) |
| 26 | 新規API Cost | 合計 **¥9.40**(固有名詞抽出¥0.49 + Perplexity¥0.88 + OpenAI Primary ASR¥1.43 + Azure Secondary¥6.59。新規TTS生成は0件) |

---

## 1. 実施内容

既存3 TopicのWriter/Support/Research成果物をすべて再利用(新規記事生成なし)。各Topicから、過去に実際にASR failureを起こした・または固有名詞リスクの高いsegmentを選定し、**既存音声fixtureへCascadeを適用**する形で検証した(§16の指示通り、新規TTS生成は行っていない)。

| Topic | 対象segment | 固有名詞 |
|---|---|---|
| Public Benches | B1 point_one | Ottoni |
| Public Benches | B1 point_two | Malmö、Triangeln、MTA |
| Public Benches | A2 full_story_part2 | Boavida(control) |
| Subscriptions | B1 comment_2 | (なし、綴りvariant) |
| Subscriptions | A2 full_story_part2 | (なし、綴りvariant) |
| Startups | A2 full_story_part1 | Katz、Shapiro |

---

## 2. Production配線内容

1. **Pronunciation Ledger**: `er006_proper_noun_extraction_01.py`でSubscriptions・Startups記事から固有名詞抽出(Luna)を実行、Perplexityで少数単位(1〜2語)の問い合わせを実施し、既存Ledgerへ追記した。
2. **Cascade関数の刷新**: `er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`を新設。仕様通りOpenAI Primary最大2回・Azure Secondary(Phrase List付き)最大2回のCascadeを実装し、Cost Guard(1segmentあたり累積$0.05超でFail-closed)を追加した。既存の`val.evaluate_attempt()`とのdrop-in互換ラッパー`evaluate_attempt_with_cascade()`を用意し、Human Review Queueへの自動ログ記録も実装した。
3. **本番retry loopへの配線**: `er003_v1_crosslevel_audio_02_common.py`・`er003_v1_repro01_main_generate.py`(2箇所)・`er003_v1_sing01_news_tail_fix.py`・`er003_v1_sing01_point_headings_aoede.py`・`er003_v1_sing01_voice01_generate.py`の**計6箇所全て**を、旧`audio_validation.evaluate_attempt()`直接呼び出しから、新しい`secondary_asr.evaluate_attempt_with_cascade()`へ置き換えた。`cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED`(既定False)で制御されるため、**未変更時は旧挙動と完全に同一**(regression testで確認済み)。
4. **重要な副次的修正**: 検証中に、`capitalized_flags()`(固有名詞らしさの判定関数)が「segment先頭の大文字語は一律で固有名詞候補から除外する」という設計だったため、"Ottoni and colleagues..."のように**segmentの先頭に固有名詞が来る実際のケース**(引用文の定番パターン)を正しく検出できていなかったことを発見した。既存の`_STOPWORDS`(閉じた既知集合)を使い、「先頭語が一般語(The/It/This等)の場合のみ除外し、それ以外の先頭大文字語は通常通り固有名詞候補として扱う」よう修正した。個別固有名詞のwhitelistは作っていない(§10確認)。

---

## 3. 実測結果: Before/After

| 指標 | Before(旧Sol+Azure or 旧Pilot-02) | After(OpenAI Primary + Cascade) |
|---|---|---|
| 対象6segment合計attempt数 | 40 | 実質6(既存音声再利用、新規TTS0) |
| STOPPED | 5/6 | 0/6 |
| Human Review(ASR_VALIDATION_UNCERTAIN) | 実質0(STOPPEDまで使い切っていた) | 2/6 |
| PASS(NORMALIZED_MATCH等) | 1/6 | 4/6 |
| true content error誤PASS | (未計測) | 0/6 |

**Segment別詳細**:

| Segment | Before | After | 説明 |
|---|---|---|---|
| Ottoni(benches) | STOPPED(6attempt) | Human Review(Cascade4段階完走) | Primary#1/#2とも"A Tony"のまま。Secondary#1/#2は"3:00"という既知のAzure癖(three→3:00)が再発し不一致継続 |
| Malmö/Triangeln(benches) | 前回タスクでPASS済み(3attempt) | Primary#1で即PASS | 再現性確認、hint無しでも安定 |
| Boavida(benches、control) | 前回タスクで非決定的(PASS/FAIL揺れ) | Human Review(Cascade4段階完走) | **重要な発見**: Secondary#1/#2は実際に"Boavida"を正しく認識した(Phrase List効果あり)が、"28"を"twenty-eight"と綴った新しい数字表記ギャップが原因で全体はTRUE_CONTENT_MISMATCHのまま(§8参照) |
| comment_2(subscriptions) | STOPPED(6attempt、旧Sol版) | Primary#1で即PASS | Cascade発動せず、ASR/Validator改善だけで解消 |
| full_story_part2(subscriptions) | STOPPED(12attempt、旧Sol版) | Primary#1で即PASS | 同上 |
| Katz/Shapiro(startups) | STOPPED(12attempt、旧Sol版) | Primary#1で即PASS | OpenAI-miniが"Katz and Shapiro"を一発で正確に認識(旧AzureはCats/Katzen/Katsun等、12回全て誤認識していた) |

---

## 4. 重要な発見: Cascadeの「見えない」効果(Ottoni・Boavida)

両ケースとも、**Secondary ASR(Azure+Phrase List)は実際にターゲットの固有名詞自体を正しく認識した**(Ottoniは1/2回、Boavidaは2/2回)。しかし segment 全体としては別の理由で不一致のままだった:

- Ottoni: Azure特有の「three→3:00」という既知の癖(前タスクで発見、数値2〜12の綴り/算用数字は吸収済みだが、この癖自体はAzureの時刻フォーマット誤認識であり数字表記吸収では解決しない)。
- Boavida: "28"→"twenty-eight"という、**今回新たに発見した**数字表記ギャップ。既存の吸収ロジックは2〜12のみ対応しており、28のような2桁の数はカバーしていない。

つまり、**固有名詞の認識精度自体はPhrase Listで実際に改善しているが、その改善がsegment全体のPASS/FAILという粗い指標には現れていない**。これは前回タスクの結論を精緻化する発見であり、今後の改善余地として記録する(§8)。

---

## 5. Cost計測(実測)

| 項目 | 内容 | Cost(JPY) |
|---|---|---|
| 固有名詞抽出(Luna、Subscriptions+Startups) | 2topics | ¥0.49 |
| Pronunciation Research(Perplexity、Katz+Shapiro) | 1リクエスト(少数単位、§5方針通り) | ¥0.88 |
| OpenAI Primary ASR(Primary#1+#2、全segment) | 9コール | ¥1.43 |
| Azure Secondary ASR(Phrase List込み) | 4コール、148.3秒 | ¥6.59 |
| **合計新規支出** | | **¥9.40** |
| avoided TTS+ASR cost(旧attempt数ベース試算) | 6segment合計 | ¥137.8 |
| **Net Savings** | | **¥128.4** |

新規TTS生成は0件(既存fixtureを最大限再利用、§16の方針を遵守)。

---

## 6. Human Review対象一覧(§14)

Cascade4段階(Primary#1・#2、Secondary#1・#2)を尽くしても不一致だった2件を記録した。

| Segment | Canonical Text(抜粋) | Pronunciation Research | Primary #1 | Primary #2 | Secondary #1(Phrase List: ["Ottoni"]) | Secondary #2 |
|---|---|---|---|---|---|---|
| Ottoni(B1 point_one) | "Ottoni and colleagues' 2016 qualitative study looked at three nearby Vancouver neighborhoods..." | "oh-TOH-nee"(confidence: medium) | "A Tony and colleagues'..." | "A Tony and colleagues'..." | "A Tony and colleagues... 3:00 nearby..." | 同左 |
| Boavida(A2 full_story_part2) | "A separate review by Boavida and colleagues in 2023 examined 28 articles..." | "boh-ah-VEE-dah"(confidence: low) | "Bova Vita and colleagues... examined 28 articles..." | "Boavita and colleagues... examined 28 articles..." | "**Boavida** and colleagues... examined **twenty-eight** articles..." | 同左 |

**「機械的FAIL」ではなく「pronunciation uncertainty」としての記録**: Ottoniはconfidence=medium、Boavidaはconfidence=lowと、Pronunciation Research自体がこれらの固有名詞の標準的な英語読みに一定の不確実性があることを示している。人間が読んでも判断が難しい可能性がある固有名詞として記録する。

音声そのものは前回タスクで公開したArtifact([Pronunciation Ledger Listening Review](https://claude.ai/code/artifact/61fd6da9-a5e6-4f2f-9284-6f3daaf4790d))で既に聴取可能(同一音声を再利用しているため、新たなArtifactは作成していない)。

---

## 7. 成功判定(§20)との照合

| 判定基準 | 結果 |
|---|---|
| 1. true content error誤PASS = 0 | **○達成** |
| 2. 固有名詞由来のTTS retryが明確に減る | **○達成**(40attempt相当→実質6、STOPPEDが5→0) |
| 3. 追加ASR/Research費用が回避TTS費用より小さい | **○達成**(¥9.40 vs ¥137.8) |
| 4. Human Review件数が現実的な範囲 | **○達成**(2/6、33%。ただし意図的な既知failure fixtureのため要注意) |
| 5. 3 Topicで方向性が再現 | **△部分的**。ASR/Validator改善の恩恵(Primary#1のみでPASS)は3 Topic全てで再現したが、**Cascade機構自体が実際に解決へ導いたケースは今回0件**(発動2件とも未解決のままHuman Review行き)。Cascadeの直接効果の再現性は、より大きなサンプルでの追加検証が必要 |
| 6. architectureが過度に複雑化しない | **○達成**(追加モジュール4本、既存コードへの変更は最小限、feature flag制御) |

6項目中4項目を明確に達成、1項目は部分的達成。総合判定は**「条件付き推奨」**(§0参照)。

---

## 8. 残存Open Item(OPEN-48)

1. **28のような2桁数の綴り/算用数字ギャップ**: 既存の2〜12対応の数字表記吸収ロジックでは"twenty-eight"を吸収できない。一般化した数値表記正規化(spelled numbers全般)の検討が必要。
2. **Ottoniの"three→3:00"のようなAzure時刻フォーマット誤認識**: Secondary ASRの信頼性を下げる既知の癖。Azure側の設定(音声認識のロケール・フォーマットオプション)で回避できるか未調査。
3. **Cascade機構自体の実効性はまだ小サンプル**: 今回発動2件はいずれも未解決。より多くのトピック・より多様な固有名詞パターンでの追加検証を経てから、Production default化(feature flag ON)を判断すべき。
4. **Phrase Listの「認識はできたが全体PASSに至らない」パターン**: segment全体のPASS/FAIL判定とは別に、対象固有名詞だけの認識精度を独立して測定・記録する仕組みがあれば、今回のような「見えない改善」を正しく評価できる。次回検討候補。

---

## 9. Regression Test・制約確認

- Regression test: 新規9 test(secondary_asr関連)含む既存分と合わせて全12スイートPASS。
- サービス仕様(article本文・B1/A2仕様・番組構成・voice・style・pacing・ユーザー向け表示・価格)は変更していない。
- Sol call: **0件**(実測確認済み。過去ログ上のSubscriptions/Startups関連のSol呼び出しは全て前日の別タスクによるものであり、本タスクの新規stageでは0件)。
- Feature Flag: `FEATURE_FLAG_SECONDARY_ASR_ENABLED`はコミット済みコード上は**False(既定OFF)のまま**。今回の検証実行時のみスクリプト側で明示的にTrueへ設定した。

---

完了後STOP。残りPool Topic量産には進まない。
