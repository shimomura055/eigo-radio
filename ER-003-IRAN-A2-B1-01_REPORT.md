# ER-003-IRAN-A2-B1-01 完了レポート

対象範囲: ER-003-IRAN-A2-B1-01の指示以降、本セッションで実施した全作業(A2/B1音声制作+ユーザー報告不具合の修正2件)。

ステータス: PROTOTYPE / 検証用。Production(本番)仕様は無変更。

---

## 1. 目的

現行のER-003暫定仕様(B2 Natural English + B1 Support、A2 V2改1/Cognitive Load Reduction)を、これまで扱ったことのないテーマ「最新のイラン情勢」へ横展開できるかを検証した。A2とB1を同一のFact Ledgerから生成し、両方ともFull Audioまで完成させることを目標とした。

---

## 2. Research / Fact Ledger

- Research実施日: 2026-08-16。個別Factの情報cutoffは2026-08-15付報道まで。
- 選定angle: 「トランプ大統領はホルムズ海峡を『米国の領土にする』可能性に言及したが、実際に水域で進んでいるのはイランとオマーンによる技術的な航路再開合意である」という、政治的発言と実際の進行事実の対比。
- スコープ外: 死傷者数、核問題詳細、イラン国内政治(中心angleを1つに絞るため)。
- タグ体系: `[CONFIRMED_FACT]` `[GOV_CLAIM]` `[DIPLOMATIC_PROPOSAL]` `[AGREEMENT_UNDER_NEGOTIATION]` `[PREDICTION]` `[ANALYSIS]` `[DISPUTED]`
- 共通Fact Ledgerは1つのみ作成し、A2/B1双方がここから生成された(別々のFact世界は作らない、というユーザー指示に準拠)。

### Ledgerの改訂(v2)

B2/A2の初回記事に対する独立Fact Checkerの結果が`FAIL`だったため、追加のWeb調査を行いLedgerを修正した(詳細は下記4節)。矛盾は解消したが、記事の中心Fact自体は`REVIEW_REQUIRED`のまま残った。この状態のままB1/A2の音声制作へ進んでよいかをユーザーに確認し、承認を得て継続した。

---

## 3. B2 Natural English / A2 V2改1 記事生成

| 項目 | B2(News本文、B1が共有) | A2(V2改1、別Narrative) |
|---|---|---|
| タイトル | Hormuz: Trump Talks Territory as Iran and Oman Draw a Route Back | Trump Talks Territory. Iran and Oman Draw a Route. |
| 総語数 | 367語 | 403語 |
| Point One | 44語 | 43語 |
| Point Two | 45語 | 42語 |
| In One Line | 25語 | 39語 |
| 文数/平均文長 | 22文 / 16.9語 | 30文 / 13.6語 |

A2は今回のB1 Voice Allocationを移植せず、A2独自の既存アーキテクチャ(単一Aoede voice、日本語Preview/Comment)をそのまま踏襲した。

---

## 4. Fact Safety QA(反復記録)

| 段階 | B2 | A2 |
|---|---|---|
| 初回Fact Checker | **FAIL**(Trump発言の日付/場面混同、Brent原油価格の誤り、船舶通航数レンジの根拠不足等) | **FAIL**(同種の指摘) |
| Ledger修正後(2回目) | REVIEW_REQUIRED(矛盾0件、中心Fact一次資料未確認) | REVIEW_REQUIRED(同上) |
| 軽微な文言修正後(3回目、Ledger逸脱1件発生→復元) | REVIEW_REQUIRED(変わらず) | REVIEW_REQUIRED(変わらず) |
| Ledger Deviation Check | LEDGER_COMPLIANT(0件) | LEDGER_COMPLIANT(0件) |

Ledger修正内容(v2): (1) Trump発言を8/12 Truth Social投稿と8/14ニューヨーク集会発言の2件に分離、(2) Brent原油価格を「約72ドル→80ドル台後半、約20%上昇」へ修正、(3) 船舶通航数を「数隻程度(情報源により幅あり)」へ緩和、(4) 機雷除去をFACT-01/02の確定条項から削除、(5) FACT-01(8/15合意発表)自体は追加のWebSearchで5つの独立報道機関(anews/Pakistan Today/Fortune/Bloomberg/CGTN)により再確認した。

**REVIEW_REQUIREDの扱いについて**: 独立Fact Checkerを都合3回実行したが、いずれも「矛盾は検出されないが、中心Fact(8/15のイラン・オマーン合意発表)の一次資料(政府公式発表文そのもの)には到達できない」という同一の指摘だった。これはFact Checker自身のWeb検索到達範囲の限界による可能性が高いと判断し、B1/A2の音声制作へ進む前にユーザーへ状況を報告、「REVIEW_REQUIREDのまま進める」という回答を得て継続した。両Artifactにこの経緯を明記している。

---

## 5. B1 Support / Key Phrase

- Preview/Comment1-4を新規生成(英語、Charon voice)。Full Story/Point/In One LineはB2をそのまま使用(一字一句変更なし)。
- Key Phrase(方式L+Canonicalization、B2最終本文から選定): strait / sanctions relief / sovereignty / trade words / fanciful delusions。5件全PASS。
- Number Treatment監査: 11件の数字を検出、記録済み。
- Support Fact Safety: Ledger Deviation Check LEDGER_COMPLIANT(0件)、Fact Checker REVIEW_REQUIRED(同一の中心Fact指摘)。

## 6. A2 Preview / Comments / Key Phrase

- Preview/Comment1-4を新規生成(日本語、単一Aoede voice)。Full Story/Point/In One LineはA2独自本文(英語)。
- Key Phrase(方式L+Canonicalization、A2最終本文から独自選定、B1からの流用なし): Strait of Hormuz / declare something to be / US sanctions / one-fifth / be taken by a tweet。5件全PASS(1回目は構造検証エラー2種で失敗、3回目でPASS)。
- Support Fact Safety: Ledger Deviation Check LEDGER_COMPLIANT(0件)、Fact Checker REVIEW_REQUIRED(同一の中心Fact指摘)。

---

## 7. B1 音声制作(TTS/ASR)

VOICE-03時点のVoice Allocationを最初から適用(Charon=Navigator/Explanation、Aoede=本文)。既存の確立済み関数(`er003_v1_sing01_voice01_generate`/`er003_v1_sing01_news_tail_fix`/`er003_v1_sing01_point_headings_aoede`/`er003_v1_repro01_main_generate`)を再利用し、trim安全マージン0.35秒を全segmentへ最初から適用した(過去に発覚した語尾切れバグを未然に回避)。

発生した不具合と対応:
- num_one〜five: Azure STTが数詞("One.")を数字("1.")へ正規化して書き起こす既知パターン。VOICE-01で確立した数詞/数字等価判定(`er003_v1_sing01_voice01_labels_fix`)を再利用し解消。
- point_two: "one-fifth"→ASRは"1/5"と分数正規化。期待テキスト側を局所的に正規化する専用関数を追加し解消。
- Key Phrase 1「strait」(英語)/「海峡」(日本語)、Key Phrase 4「言葉で応酬する」(日本語): ASR同音異義語ambiguity(strait/straight、海峡/改革・改強、応酬/押収=いずれも「おうしゅう」)。ADD03「航行の自由→高校の自由」と同種のパターンと判断し、`ACCEPTED_PENDING_USER_LISTENING`として分類・記録。ユーザーの実試聴確認を推奨する形でArtifactに明記した(修正は未実施、明示的なフラグ立てのみ)。

## 8. A2 音声制作(TTS/ASR)

A2既存の単一Aoede voiceアーキテクチャ(`er003_v1_crosslevel_audio_02_common`)を再利用。Shell共通文言(welcome/preview_intro/point_explanation/key_phrases_intro/full_story_intro/num_one〜five)はA01の既存音声(サービス共通・記事非依存)をそのまま再利用し、新規TTSは行わなかった。topic_intro/japanese_titleのみ記事固有のため新規生成した。

発生した不具合と対応:
- point_one(英語)/meaning_4(日本語「5分の1」): "one-fifth"/"5分の1"→ASRは"1/5"と表記正規化。判定用のexpected_substringを調整し解消。
- Key Phrase Component「US sanctions」: ASRが"U.S. sanctions"(略語のピリオド表記)へ正規化。同上の方法で解消。
- Key Phrase選定1回目: モデルが誤ったsource_sentenceを出力する構造エラー、および省略記号を含む出力の2種類の失敗が発生。3回目の再試行でPASS。

### ユーザー報告による追加修正(公開後)

Artifact公開後、ユーザーから以下2点の指摘を受け、原因調査→承認取得→修正の順で対応した。

1. **Key Phrase 4「5分の1」の誤読**: TTSが「5分(ふん)の1」(時間の「分」)と誤読していた。正しくは「5分(ぶん)の1」(割合)。「分」は複数の読みを持つ漢字で、文脈のない短い入力(4文字のみ)に対しTTSがより頻度の高い「ふん」読みを選んでしまったことが原因。**重要な発見**: この読み間違いは、ASRによる自動検証では検出できない構造だった。正しい読み("ぶん")でも誤った読み("ふん")でも、Azure STTは分数として認識すると同じ「1/5」という数字表記へ正規化してしまうため、機械的なテキスト一致検証は常にPASSしていた。表示用の正式表記「5分の1」は変更せず、TTS入力のみ平仮名で明示的に「５ぶんの１」と書き換えて再生成することで解消した(ADD03「～」記号問題、今回のKey Phrase 2記号問題と同様の「TTS入力のみ差し替え」方式)。
2. **Comment 2内「ホルムズ海峡」の発音違和感**: テキスト内容・ASR照合はいずれも初回から正常だった(hallucinationや内容誤りではない)ため、単発の生成ゆらぎ(発音・抑揚の質のばらつき)と判断し、同一テキスト・同一voiceで単純に再生成した。発音の自然さはASRでは確認できないため、実際の聴取での最終確認をArtifact上で推奨している。

修正後、A2 Full Audioを再組み立てし、Artifactを同一URLで更新済み。

---

## 9. Full Audio

| | B1 | A2 |
|---|---|---|
| 長さ | 5分18.75秒 | 5分40.93秒(修正後) |
| ピーク | 0.947 | 0.817 |
| クリッピング | なし | なし |
| サンプルレート/チャンネル | 48000Hz / ステレオ | 48000Hz / ステレオ |

---

## 10. Artifact(Blind Listening形式)

音声を最初に提示し、聴取後に初めて台本・Key Phrase・QAサマリー・出典・A2/B1比較表が開示される2-view構成。

- B1: https://claude.ai/code/artifact/18ba8405-62a1-4596-98ff-897f191f7f63
- A2: https://claude.ai/code/artifact/3f2e878a-3ecd-4db1-b2bd-c6177310b097

比較表(中心ストーリー・語数・文構造・言語配分・Point役割等)は両Artifactの「聴取後」セクションに格納し、聴取前には開示されない構成にしている。

---

## 11. 回帰テスト・Production確認

- 関連モジュール(`er003_audio_tts_asr_safety`/`er003_b1_p3u_audio`/`er003_b1_p9a_audio`/`er003_b1_p4c_audio`/`er003_key_words_canonicalization`/`er003_b2_key_words`/`er003_v1_b1_scaffold_audio_01`)の既存テスト201件、全PASS。
- Production spec(`CURRENT_SPEC.md`等)、A2/B1の正式仕様、Voice Architecture、共通Audioモジュール本体はいずれも無変更。今回作成したスクリプトはすべて新規の独立ファイル(`er003_v1_iran01_*.py`)で、既存の確立済み関数を読み取り専用でimportして再利用する形を徹底した。

---

## 12. 未確定事項(次回以降の検討候補)

- Fact CheckerのREVIEW_REQUIRED(中心Factの一次資料未確認)を今後どう扱うか。角度自体は複数の独立報道で裏付けが取れているが、政府一次発表文への到達手段(専用の検索・別ソースの追加調査等)を検討する余地がある。
- B1の同音異義語3件(strait/海峡/応酬)は、ユーザーの実試聴によるPASS/要修正の最終判定が未実施。
- 今回のREVIEW_REQUIRED・ASR構造的限界(数字・略語の表記正規化、同音異義語)は、既存の`er003_audio_tts_asr_safety.py`(共通モジュール)への一般化を検討する余地があるが、今回は既存方針(記事専用のローカル対応、共通モジュール自体は変更しない)を踏襲した。

---

## 13. commit / push 記録

| commit | 内容 |
|---|---|
| `3d35302` | ER-003-IRAN-A2-B1-01本体(記事生成〜Full Audio〜Artifact、83ファイル) |
| `e769cd9` | ユーザー報告のA2音声2件の修正 |

いずれも`origin/main`へpush済み。`.wav`/`.mp3`/`player_final.html`はcommit対象外(既存の運用方針どおり)。

---

## 14. 完了報告時点の状態

- 本タスクの32項目受入条件のうち、Fact CheckerのPASS(REVIEW_REQUIREDに留まる)、B1同音異義語3件の人による最終確認、以外はすべて充足。
- 今回のIRAN01の作業は、ER-003-IRAN-A2-B1-01スコープに定義された「今回の非対象」(Production仕様変更・A2正式凍結・B1正式プロダクション化・Voice Architecture本番導入・過去記事の再生成)には一切踏み込んでいない。
