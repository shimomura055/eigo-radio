# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01 完了報告

固有名詞発音情報の事前取得＋TTS/ASR連携＋Azure Secondary ASR検証。結論を先に言うと、**インフラは正しく動作したが、Ottoniという最難関ケースを劇的に解決するには至らなかった**。正直な負の結果を含めて報告する。

---

## 0. §22 質問への回答(先にまとめて回答)

| # | 質問 | 回答 |
|---|---|---|
| 1 | Ottoniの正しい読み情報を取得できたか | できた。Perplexityから "oh-TOH-nee"(IPA: /otˈtoːni/、Italian起源、confidence=medium)を取得 |
| 2 | Malmöの読み情報 | 取得済み。"MAL-moh"(confidence=high、Swedish) |
| 3 | Triangelnの読み情報 | 取得済み。"tree-AHNG-eln"(confidence=medium、Swedish) |
| 4 | Pronunciation Ledger cost | Perplexity合計¥4.43(5リクエスト: 1件6語まとめ+4件個別)。固有名詞抽出(Luna)¥0.16 |
| 5 | TTS hintで発音が改善したか | **判定不能・要人間試聴**。ASRでは改善を確認できなかった(下記6-7)。Artifactで実際の音声を公開したので、発音そのものの改善有無はユーザー判断に委ねる |
| 6 | OpenAI Primary認識結果 | Ottoniは2回試行とも失敗("A Tony"/"Otoni")。Malmö/Triangelnはhintの有無に関わらず既にPASS。Boavida(control)はhint付きで安定してPASS |
| 7 | Azure without Phrase List結果 | Ottoni: "Otoni"(近いが不一致)/"A Tony"(2回目)。Malmö/Triangeln: "Triangle in station"と誤認識(分節誤り) |
| 8 | Azure with Phrase List結果 | Ottoni: 1回目は"Ottoni"と正しく認識(Phrase List効果あり)、2回目は"A Tony"のまま(効果なし、**不安定**)。Malmö/Triangelnは効果なし(分節誤りは変わらず) |
| 9 | Phrase List効果 | **限定的・不安定**。ASRの既定候補がターゲット語に音的に近い場合のみ後押しする(Otoni→Ottoniは成功)。既定候補が全く別の語("A Tony")の場合は効果なし |
| 10 | TTS retry before/after | 直接比較困難(Ottoniは新Cascadeでも最終的にHuman Review行きのまま)。ただし新Retry Architecture採用により、無意味な6回のTTS再生成が1回で「retry非推奨」判定に変わる可能性があり、間接的な削減効果はある(§10参照) |
| 11 | STOPPED before/after | Ottoni関連segmentは実質的にSTOPPED状態のまま(ASR側の限界のため)。ただし新設計では「STOPPED」ではなく「ASR_VALIDATION_UNCERTAIN(Human Review対象)」に正しく分類される — 無駄なretryをしない点が改善 |
| 12 | UNCERTAIN before/after | Malmö/Triangelnは既にAzure単体でUNCERTAIN相当だったが、OpenAI Primaryでは元々PASSしていたため実害はなし |
| 13 | true error誤PASS有無 | **0件**。今回の全条件・全fixtureで、内容が実際に間違っている音声を誤ってPASSさせたケースはない |
| 14 | 追加API cost | 合計 **¥27.89**(内訳: 固有名詞抽出¥0.16、Perplexity¥4.43、Gemini TTS¥10.75、OpenAI Primary ASR¥1.05、Azure Secondary ASR¥11.50) |
| 15 | avoided TTS cost | 限定的。Ottoni 1segmentについて、新Retry Architectureが「1回で退場すべき」と正しく判定すれば、既存の6回attempt分のうち5回(≈¥12.5相当)が削減候補になりうる。ただし本Pilotでは実際に6回を回避した実証はできていない(Cascade自体は検証したが、Production retry loopへは配線していないため) |
| 16 | net savings | **限定的にプラス、ただし確度は低い**。今回の新規支出¥27.89に対し、確実に回避できたコストは実証できていない(理論値≈¥12.5、支出を下回る)。1トピックのみの検証のため統計的な結論には至らない |
| 17 | Production採用推奨か | **一部のみ推奨**。Pronunciation Ledger・cache設計・抽出フローは production-ready(§18参照)。TTS pronunciation hint injectionとSecondary ASR + Phrase Listは、**feature flag OFF(既定)のまま追加検証を継続**すべきで、今回のデータだけでは全面採用を推奨しない |
| 18 | 追加対策が必要か | Ottoniのような真正なASR限界には、(a) より大規模なfixtureでのPhrase List効果の再現性検証、(b) Writer側での引用表記の見直し(例: 姓のみでなくfirst nameも添えるなど、ASRへの手がかりを増やす)、(c) 第三のASR候補の検討、のいずれかが必要。ただし今回のタスク方針(§16)通り、これ以上のarchitecture複雑化は今回は行わない |
| 19 | Human Review Artifact | [Pronunciation Ledger Listening Review](https://claude.ai/code/artifact/61fd6da9-a5e6-4f2f-9284-6f3daaf4790d) |
| 20 | 残存Open Item | OPEN-47として記録(§13) |

---

## 1. 実装したもの

1. **固有名詞抽出**(`er006_proper_noun_extraction_01.py`): Writer完成後の記事本文・Support・Key PhraseからLuna(Model Routing Contract SSOT)で抽出。全単語ではなく「通常の英語綴り規則だけでは読みが不確実、またはASR誤認識リスクが高いもの」に限定するプロンプト設計。実行結果: Vancouver・Ottoni・Boavida・Malmö・Triangeln・MTAの6件を実際に抽出(Public Benches全文から)。
2. **Pronunciation Research**(`er006_pronunciation_research_01.py`): Perplexity chat/completions(sonarモデル)を使用。構造化JSON出力(canonical_spelling/entity_type/language_origin/IPA/pronunciation_hint/alternate_pronunciations/confidence/ambiguity_note)+ 実際のcitations URL群を取得。
3. **Pronunciation Ledger**(`er006_pronunciation_ledger_01.py`): spelling×entity_typeのsha256ハッシュをキーとしたcache/store(同じ綴りでも人名/地名で衝突しないよう設計、regression testで確認済み)。
4. **TTS pronunciation context injection**(`er006_pronunciation_tts_injection_01.py`): style instructionの末尾へ発音ヒントを追記するのみ。spoken text本文・article textは一切変更しない(regression testで、text引数自体が変更されないことを直接確認)。
5. **Secondary ASR + Azure Phrase List**(`er006_secondary_asr_01.py`): `speechsdk.PhraseListGrammar`を使った新規Azure呼び出し関数、および§12-13のRetry Architecture(Primary→Secondary→両者不一致の場合のみretry候補)を実装。**Feature Flag `FEATURE_FLAG_SECONDARY_ASR_ENABLED = False`(既定OFF)**。

---

## 2. 検証結果の詳細

### 2.1 Ottoni(B1 Point One、既知の失敗ケース)

| | Condition A(既存) | Condition B(hint、試行1) | Condition B(hint、試行2) | Condition C(Azure、Phrase Listなし) | Condition D(Azure、Phrase Listあり) |
|---|---|---|---|---|---|
| ASR結果(該当箇所) | "A Tony" | "Otoni" | "A Tony" | 試行1音声: "Otoni" / 試行2音声: "A Tony" | 試行1音声: **"Ottoni"(正解)** / 試行2音声: "A Tony" |
| 判定 | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH |

**重要な追加観察**: Azureは"three"を今回も"3:00"と誤変換する既知の癖を再現した(前回タスクで発見した問題が、pronunciation hintの有無に関わらず残存)。またTTS試行1では"at two time points"の"time"が脱落していたが、試行2では正しく発話されており、これはpronunciation hint注入によるものではなく通常の生成ブレと判断した。

**結論**: Phrase Listは、ASRの既定認識候補がターゲット語に音響的に近い場合(Otoni≈Ottoni)は効く可能性があるが、既定候補が全く異なる語("A Tony")になった場合は効かない。**再現性が低く、production-readyとは言えない**。

### 2.2 Malmö / Triangeln / MTA(B1 Point Two、既にPASSしていたケース)

OpenAI Primaryは、hintの有無に関わらず既にNORMALIZED_MATCH(悪化なし、良い制御結果)。一方、Azure Secondary(Phrase Listあり/なし共通)は"Triangeln station"を"Triangle in station"と誤って**分節**しており、これはPhrase Listで単語の重み付けをしても解決しない種類のエラーだった(語の存在を知らないのではなく、音の切れ目の解釈が違う)。

### 2.3 Boavida(A2 Full Story Part 2、control/既にPASSしていたケース)

興味深い発見: 既存音声を**もう一度**Primary ASRへ通したところ、今回は"Boavita"と誤認識され、TRUE_CONTENT_MISMATCHになった(前回のPilotでは同じ音声がPASSしていた)。**ASR自体の呼び出しごとの揺れ**を示す実例。pronunciation hint付きの新規生成では、3条件(B/C/D)とも安定してPASSした。

---

## 3. Cost計測(実測)

| 項目 | 内容 | Cost(USD) | Cost(JPY) |
|---|---|---|---|
| 固有名詞抽出(Luna、1記事分) | 2,005 in / 520 out tokens | $0.00102 | ¥0.16 |
| Pronunciation Research(Perplexity) | 5リクエスト(1件×6語一括+4件個別) | $0.02769 | ¥4.43 |
| Gemini TTS(pronunciation-aware、4生成) | 実測+一部推定 | $0.06716 | ¥10.75 |
| OpenAI Primary ASR | 6+推定1コール | $0.00654 | ¥1.05 |
| Azure Secondary ASR(Phrase List込み、8コール) | 258.8秒 | $0.07188 | ¥11.50 |
| **合計新規支出** | | **$0.17429** | **¥27.89** |

**重要な発見(Perplexity batching)**: 当初、6件の固有名詞を1リクエストにまとめて問い合わせたところ、Ottoni/Malmö/Triangeln/Boavidaいずれも**confidence=low・pronunciation_hint空欄**という低品質な結果になった。個別(または2件程度の少数)クエリへ分けて再実行したところ、同じ語について明確に良い結果(confidence=medium〜high、実用的なhint)が得られた。**「1 topicにつき1 request」という当初の効率重視の方針は、Perplexityの検索深度を犠牲にして品質を下げるトレードオフがあることを実測で確認した**。今回は診断のため追加で4件の個別クエリを実行したが(合計コスト増分は¥2円未満)、Production設計では「1トピック1リクエスト」を機械的に強制せず、語数が少ない場合は分割クエリを許容する方が安全と考えられる。

---

## 4. Retry Architecture評価(§12-13)

実装した`evaluate_with_secondary_cascade()`は、以下をregression testで確認済み:

- Primaryが PASS すれば Secondary は一切呼ばれない(API呼び出し回数を実際にmockして確認)。
- Feature Flag OFFなら Secondary は絶対に呼ばれない。
- Primary が UNCERTAIN/MISMATCH で Secondary が PASS すれば、そこで確定PASS。
- **両ASRが同じ内容差(例: 数字が変わっている)を一貫して示す場合のみ** retry_recommended=True。
- 固有名詞のtransliteration差だけで両ASRの結果が食い違う場合は、retry_recommended=False(ASR_VALIDATION_UNCERTAINとして Human Review へ)。

この設計自体は健全に動作しており、**「固有名詞だけの表記差でTTSを無駄に再生成しない」という目的は達成している**。ただし今回はPilotの実retry loopへは配線していない(Production投入は§17の通り見送り)。

---

## 5. 成功判定(§15)との照合

| 判定基準 | 結果 |
|---|---|
| 1. 発音情報を与えることでGemini TTSの固有名詞発音が改善または安定 | 部分的(Boavidaでは安定化を確認。Ottoniは判定不能、Human Review待ち) |
| 2. OpenAI Primaryの認識率が改善 | **否**。Ottoniでは改善を確認できず |
| 3. Azure + Phrase Listでさらに認識改善 | 部分的・不安定(1/2回のみ成功) |
| 4. TTS retry回数が減る | 直接未実証(Cascade設計は健全、配線は未実施) |
| 5. true content errorを誤PASSしない | **○ 達成**(0件) |
| 6. 追加research/ASR costより削減TTS costが大きい | **否、確度低い**(¥27.89支出 vs 理論上の削減¥12.5、実証はできていない) |

6項目中、明確に達成できたのは基準5のみ。**§15の全体的な成功判定には届いていない**。

---

## 6. §17: 改善しなかった原因の分類(Ottoniについて)

- pronunciation research自体が不正確 → **否**。Perplexityの情報("oh-TOH-nee")自体は実在の情報源に基づく妥当な内容だった。
- TTSがhintを無視 → **判定不能**。ASRが失敗し続けるため、TTS自体の発話が改善したかどうかを機械的に確認できていない(→Human Review Artifactで確認依頼)。
- OpenAI ASR限界 → **可能性が高い**。2回とも一貫して"Ottoni"を別の語として認識した。
- Azure Phrase Listでも認識不能 → **部分的にYes**(1/2回は失敗)。既定候補が音響的に離れすぎると効かない。
- Validator問題 → **否**。Validatorは正しく動作している(false positiveなし、controlケースは正しくPASS)。
- source自体で発音が曖昧 → **部分的にYes**。Perplexityのconfidenceも"medium"にとどまり、この珍しい姓の標準的な英語読みそのものに一定の不確実性がある。

**総合診断**: OttoniはASR側(特にOpenAI Primary)の認識限界が主因であり、TTS側の発音改善やPhrase Listだけでは解決しきれない「真正に難しいケース」である可能性が高い。

---

## 7. 劇的改善しなかったため(§16は不適用)

§16の「劇的改善した場合はarchitectureを複雑化しない」という条件には該当しなかった。§17の追加対策検討に該当するが、**タスク方針通り、今回はこれ以上のarchitecture追加(第三のASRや複雑なphonetic validator)は行わない**。

---

## 8. 実装範囲・Feature Flag(§18)

Production-readyとして実装したもの(コード自体は完成、regression test PASS):

- Pronunciation Ledger構造・cache: **有効化して良い**(副作用なし、読み取り専用の参考情報)。
- 固有名詞抽出: **有効化して良い**(Writer後の追加分析のみ、既存生成物に影響しない)。
- TTS pronunciation context injection: **feature flag経由でのみ有効化を検討**(今回のデータでは効果不明瞭)。
- Secondary Azure routing + Phrase List: **`FEATURE_FLAG_SECONDARY_ASR_ENABLED = False`(既定OFF)のまま**。

いずれも本番のTTS/ASR呼び出しへ自動配線はしていない(既存のer006_asr_provider_routing_01.py::transcribeの単一Primary ASR方針は無変更)。

---

## 9. サービス仕様変更なし(§19確認)

article本文・B1/A2仕様・番組構成・voice・style・pacing・ユーザー向け表示・価格は変更していない。TTS pronunciation hintはstyle instruction(読み上げ対象外のmeta指示)にのみ追記しており、spoken textは一切変更していない(regression testで直接確認済み)。

---

## 10. 有料API制御(§20確認)

新規Full Episode生成は行っていない。固有名詞抽出・Perplexity調査・TTS生成いずれも最小限のfixture単位(5件のentity、4回のTTS生成、8回のSecondary ASR呼び出し)にとどめた。新規支出合計¥27.89は事前の想定内。

---

## 11. Regression Test

新規3スイート(`er006_pronunciation_ledger_01_test.py`・`er006_pronunciation_tts_injection_01_test.py`・`er006_secondary_asr_01_test.py`、計15 test)を含む、既存分と合わせて全12スイートPASS。

---

## 12. 残存Open Item(OPEN-47)

1. Ottoni型の真正なASR限界への対応方針が未決(発音辞書登録・Writer側citation表記見直し等)。
2. Perplexityへの「1 topic 1 request」方針は、実測で品質低下が確認されたため、production設計時に見直しが必要。
3. Secondary ASR + Phrase Listのfeature flagは既定OFFのまま。有効化するかどうかは、より大規模なfixture(複数トピック・複数の固有名詞パターン)での再検証が前提。
4. TTS pronunciation hint injection自体がGemini TTSの実際の発話を改善したかどうかは、Human Review Artifactでのユーザー試聴結果を待って判断する。

---

完了後STOP。残りPool Topic量産には進まない。
