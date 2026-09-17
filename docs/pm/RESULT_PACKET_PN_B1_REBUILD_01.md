# RESULT_PACKET: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01(累積Full Report)

管理ID: `USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`

★★★★報告ここから★★★★

## 0. T-0(委任文検証)

`docs/pm/delegation_log/USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01.md`を保存し
`check_delegation_prompt.py`を実行。結果=`FAIL`(「実行コマンド全文」セクション
欠落、固定ブロックE-1/D-1/G-1/F-1欠落)。ルールどおりFAILでも継続。JSON:
`docs/pm/delegation_log/USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01_check.json`。

## 1. Research結果サマリ

2026-09-17時点でweb_search経由vfl01標準経路(Researcher→Verification)を2本実行。
Part1(政治的態度変化研究の現状再確認、`er012_personalized_news_b1_rebuild_01_research.py`):
facts19件下書き、VERIFIED17/AMBIGUOUS2/REJECTED0、web_search 13クエリ、¥54.58。
Part2(パーソナライズ機構・Reuters Institute調査・EU DSA・CRS説明の現状再確認、
`_research_part2.py`): facts23件下書き、VERIFIED22/AMBIGUOUS1/REJECTED0、¥61.22。
Research合計¥115.80。raw結果は`er012_output/personalized_news_b1_rebuild_01/research/`
(fact_ledger_draft*.json・fact_ledger_verification*.json・verified_fact_ledger_flat*.json)。

## 2. 旧Ledgerの何が古かったか

(a) STALE: 旧TENSION_ASYMMETRY_VALUEの「研究自体も、短期的には測定可能な政治的態度の
変化を検出できていない」は、旧Ledger自身の2-08(Nature、Xユーザー4,965人・平均7週間、
政策態度が保守方向へ0.12SD変化=有意な変化あり)と矛盾する過度な一般化だった。再Research
で、独・米filter bubble実験(2025年、中道層の分極化増加)・Xホスティリティ再ランキング
実験(2025年、1週間で感情的分極化変化)・Nature Registered Report(2026年、8週間で
党派的敵意知覚増加)等、複数の最近の研究が短期での測定可能な変化を報告していることを
確認し、単純な一般化がもはや成立しないことを確定させた。(b) AMBIGUOUS: 旧Ledgerは
当該Nature論文を「2023年」とだけ記していたが、実施は2023年・オンライン公開は
2026-02-18(印刷号2026年4月号)であり、実施年と発表年の混同がfreshness評価を誤らせて
いた(Fact Checkerが検出した「2026-02-18公開の新しいNature論文」は実は同一論文だった)。
(c) INVALID化: 個別Factが事実として誤っていたケースは無し(問題は個別Factでなく複数
Factを跨いだ一般化)。(d) 旧2-05相当の研究に2026-03-19付Science訂正(主要な実験効果
推定には影響なし)があったが旧Ledgerは未反映。(e) Voice1側(便利さ)Factも再確認し、
Reuters Instituteは2025年DNR・2023年調査という旧Ledger2016年調査より新しい2波を採用。
詳細監査記録: `er012_output/personalized_news_b1_rebuild_01/research/ledger_full_documentation_with_staleness_analysis.txt`。

## 3. 新Ledger主要claim一覧(要約、全文は3節参照)

| claim | source | date | population | evidence type | 判定 | freshness | B1使用可否 |
|---|---|---|---|---|---|---|---|
| Google News「For you」機構+利用者調整機能 | Google Newsヘルプ | 現行 | 全利用者 | 仕様説明 | VERIFIED | 2026-09-17確認 | 可(V1-01) |
| Reuters Institute 2025 DNR、49%comfortable | Reuters Institute | 2025 | 複数市場平均 | 調査 | VERIFIED | 2025年(新) | 可(V1-02) |
| 同、肯定理由(関連性・時間節約・偏り少ない・多様性) | 同上 | 2025 | 同上 | 調査自由記述 | VERIFIED | 2025年 | 可(V1-03) |
| 自動選択30% vs 編集者27% vs 友人19% | Reuters Institute | 2023 | 調査対象国 | 調査 | VERIFIED | 2023年(新) | 可(V1-04) |
| FB中央値50.4%同類/14.7%対立側露出 | Nature/Science系 | 2020データ・2023発表 | 米国FB利用者 | 観察 | VERIFIED | - | 可(V2-01) |
| Reuters Institute懸念(見落とし・偏り・プライバシー) | Reuters Institute | 2025 | 同上 | 調査自由記述 | VERIFIED | 2025年 | 可(V2-02) |
| 48%重要情報見落とし懸念/46%視点見落とし懸念 | Reuters Institute | 2023 | 同上 | 調査 | VERIFIED | 2023年(新) | 可(V2-03) |
| CRS: SNS運営者のエンゲージメント/広告収益インセンティブ | CRS | 2025更新 | - | 公式報告 | VERIFIED | 2025年(新) | 可(V2-04) |
| EU DSA Art.27/38(透明性・非profiling選択肢) | EUR-Lex | 現行 | EU大規模PF | 現行法令 | VERIFIED(施行形式のみAMBIGUOUS) | 2026-09-17確認 | 可(V2-05) |
| Meta feed機構(候補1000超→約500に絞込) | Meta公式 | 現行 | 全利用者 | 仕様説明 | VERIFIED | 2026-09-17確認 | 可(X-01、CROSS_REF) |
| X 4,965人・7週間、政策態度0.12SD保守化 | Nature | 2023実施/2026-02-18公開 | 米国Xの活動的利用者 | CAUSAL | VERIFIED | 2026年(最新) | **不使用**(記事スコープ外、4節参照) |
| 独・米filter bubble実験、中道層分極化増加 | 2025年発表論文 | 2025 | 独1,786人・米1,306人 | CAUSAL | VERIFIED | 2025年(新) | 不使用(同上) |

政治的態度変化系facts(V2-06〜V2-11相当、F009〜F017)は監査用ledger全文
(`ledger_full_documentation_with_staleness_analysis.txt`)には残すが、Writer供給用
`verified_fact_ledger.txt`には含めていない(4節参照)。

## 4. Fact/Ledger Checker結果

r8(採用記事)attempt1: Fact Checker A' verdict=**PASS**(web_search 6件、Google News/
Reuters Institute/CRS記述を再確認、`verified_claims_summary`4件、矛盾0件)。Ledger
Deviation Checker=**LEDGER_COMPLIANT**(deviation 0件、Local Rewrite発火なし)。
Comment Contract検証=LEDGER_COMPLIANT。r1(旧Ledger構成)はFact Checker/Ledger
Deviationとも問題なかったが、Analytical Leakage Check(Tension)が3attempt上限まで
残存しSTOP(6節参照)。

## 5. 新B1構成・word count

タイトル: "One Feed, Two Very Different Experiences"/「一つのフィード、二つの全く
違う経験」。Hook(part1+part2)=68語。Voice A(便利さに頼る読者)=91語。Voice B(狭まりを
懸念する読者)=97語。Tension=82語。Closing(in_one_line)=60語。総語数399語(見出し含む)。
Preview=60語。Comment 1〜4=14/20/41/27語(固定ロール、Comment Contract経路)。

## 6. Voices leakage/position結果(attempt別7項目)

| Run | 内容変更点 | Voice A | Voice B | Tension | Closing | 結果 |
|---|---|---|---|---|---|---|
| r1(3attempt) | 旧Ledger構成そのまま踏襲 | 全PASS | 全PASS | 5項目中5FAIL(evidence_subject/numbers_foreground/discovery_syntax/evidence_memorable/reverts_to_research) | 全PASS | **LEAKAGE_RESIDUAL_STOP**(3attempt後も残存) |
| r2 | Tension文を「二人の内側の認識論的立場」へ抽象化(研究名なし) | 全PASS | 全PASS | 3項目FAIL(evidence_subject/discovery_syntax/reverts_to_research) | 全PASS | 破棄(途中kill、budget節約) |
| r3 | さらに研究言及ゼロ化を試行も"platform experiments"が残存 | 全PASS | 全PASS | 5項目中5FAIL | 全PASS | 破棄 |
| r4 | Ledger側C-01に抽象度指示を追記 | 全PASS | 全PASS | 2項目FAIL(evidence_subject/reverts_to_research) | 全PASS | 破棄(僅差) |
| r5 | 「研究/報告」を主語にしない指示へ変更 | 全PASS | 全PASS | 2項目FAIL(discovery_syntax/reverts_to_research) | 全PASS | 破棄 |
| r6 | 政治的態度変化言及を本文から完全削除(Ledger側は残存) | 全PASS | 全PASS | 2項目FAIL(evidence_subject/reverts_to_research、Ledger内C-01をWriterが自発的に引用) | 全PASS | 破棄 |
| r7 | Ledger内C-01を「不使用」注記(実質は残したまま) | 全PASS | 全PASS | 5項目中5FAIL(V1-05 PNAS factを自発的に引用) | 全PASS | 破棄 |
| **r8** | V1-05含め政治的態度変化系factを**Ledgerから完全除外**+明示的注記 | **全PASS** | **全PASS** | **全PASS(0 FAIL)** | **全PASS** | **採用(attempt1で確定)** |

`leak_position_blur`(2026-09-17承認済み候補C)は全run・全attemptを通じてVoice A/B
両方で常にPASS(立場境界の問題は一度も発生していない。今回の反復はDiscovery-syntax系
既存項目のみが原因であり、Gate/Validator自体は一切変更していない)。

## 7. TTS/ASR結果

14segment全て`OK`/`VALIDATED`(topic_intro/preview/comment_1-4/point_one_heading/
point_two_heading/point_one/point_two/full_story_part1/full_story_part2/
tension_reflection/in_one_line)。全segmentとも初回試行で成功(`outer_retry_log`
発生なし、ASR cascade再検証は不要だった)。Human Review Lock発生なし。固有名詞は
「Google News」のみで、ASR上の問題は起きなかったためPronunciation Ledger
(`er006_output/pronunciation_ledger_01/ledger.json`)への新規追加は不要(無変更)。
Key Phrase 5件(stakes/engagement/be locked into/keep up with/sort through)は
本記事本文から新規選定(redundancy QA全件PASS)。Voice A=Algieba、Voice B=Erinome
(fallback発火なし)。

## 8. Assembly/Gate結果

status=OK、duration=321.175秒、peak=0.95049、clipping=False、headroom safety
valve適用なし(閾値0.98未満)。Audio Validation Gate=PASS(14segment全て
VALIDATED)。記事⇔音声一致確認(`article_audio_consistency.json`)は全項目PASS
(section本文がarticle.mdと逐語一致、TTS入力テキストがparts抽出結果と完全一致)。

## 9. actual model_id/routing/runtime evidence

Research/Writer/Fact Checker: `gpt-5.6-luna`(OpenAI Responses API、web_search
tool、reasoning effort=high)。Comment Contract: 同モデル。TTS: Gemini(Charon/
Aoede/Algieba/Erinome、Production標準ルーティング、`TTS_EXECUTION_MODE=STANDARD`)。
ASR: OpenAI Primary(Secondary Cascade待機、今回発火なし)。runtime evidence paths:
`er012_output/personalized_news_b1_rebuild_01/b1_2v_new_theme_r8/summary.json`
(Writer attempt history)、`.../b1_2v_new_theme_r8_attempt1/fact_qa.json`
(Fact Checker詳細)、`.../audio/b1_2v/b1b/audit/tts_generation_results.json`
(TTS詳細)、`.../audio/b1_2v/audio_validation.json`(Gate詳細)。

## 10. Browser E2E結果

`docs/pm/tools/user_test_page_e2e_check.py`実行(`docs/pm/e2e_pn_b1_rebuild_01/`)。
5項目全PASS: (i)Key Phraseラベル残存なし、(ii)2列形式(英語/日本語)確認、
(iii)ヘッダー"English Your Way · Advanced · User Test"(Standard/Advanced表示、
A2/B1裸表示なし)、(iv)Play進行確認(before currentTime=0→after 4秒後2.86秒、
paused=False、error=null)、(v)構造要素(Key Phrasesカード・Full Storyカード・
comment要素4件)確認。console errorなし。Seek確認: 60秒seek+1.5秒待機で
currentTime=60.80秒(duration=321.17秒、Assembly実測と一致)。screenshot:
`docs/pm/e2e_pn_b1_rebuild_01/screenshots/pn_b1_rebuild.png`。

## 11. A2非変更証跡

開始時: `er012_output/personalized_news_b1_rebuild_01/a2_baseline_sha256_before.txt`
(224ファイル)。終了時: 同dir`a2_baseline_sha256_after.txt`(224ファイル)。
`diff`実行結果=差分なし(exit 0)。対象: `er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`
配下全ファイル(audio/script/player/status含む)。

## 12. 最新Advanced URL

`https://rawcdn.githack.com/shimomura055/eigo-radio/e3cbed45229c7d7b386a05ef2750e067dbe4a0fd/user_test/unified.html?src=er012_output/personalized_news_b1_rebuild_01/audio/b1_2v/player.html&level=B1&en=One%20Feed%2C%20Two%20Very%20Different%20Experiences&ja=%E4%B8%80%E3%81%A4%E3%81%AE%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%E3%80%81%E4%BA%8C%E3%81%A4%E3%81%AE%E5%85%A8%E3%81%8F%E9%81%95%E3%81%86%E7%B5%8C%E9%A8%93`

## 13. Google Sheet貼付用情報

タイトルEN: "One Feed, Two Very Different Experiences"。タイトルJA:
「一つのフィード、二つの全く違う経験」。Standard(A2) URLは既存のまま変更なし
(11節で無変更確認済み)。Advanced欄の「—」(OPEN-166、旧B1非掲載)は、**ユーザー
試聴PASS後**に12節のURLへ差し替え可能(現時点ではまだ差し替えない、`USER_TEST_READY`
未達のため)。

## 14. OPEN-166/151等の更新

OPEN-166: 本記事固有のfreshness問題は解消(新Ledger・新記事)。一般恒久仕様
(Ledger定期再検証ルール)は未決のままOPEN維持。OPEN-151: 既存音声
`voices/audio/b1_2v_v2/`は本タスクの対象外で無変更のまま(本タスクは別記事の
新規生成であり、既存artifactの修正ではない旨を追記)。新規OPEN item登録なし。
`DECISION_LOG.md`へ`## USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`セクション新設。
`ARTIFACT_REGISTRY.md`へ「Personalized News B1(新版)」行追加(旧行は履歴として
保持)。`CURRENT_SPEC.md`は無変更(整合確認のみ、新規Voices仕様変更なし、
OPEN-167は不採用のまま)。

## 15. SSOT/Git SHA

コード+成果物本体(記事・音声・player・E2E evidence): `e3cbed45229c7d7b386a05ef2750e067dbe4a0fd`
(push済み、`origin/main`と一致)。SSOT反映(DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY/
本RESULT_PACKET/lock解除)はこの後別commitで追加予定。

## 16. コスト(内訳、上限¥400)

Research: Part1=¥54.58、Part2=¥61.22、小計¥115.80。Writer: r1(旧構成3attempt)
=¥50.55、r2=¥20.92、r3=¥17.81、r4=¥33.67、r5=¥25.57、r6=¥12.01、r7=¥29.24、
r8(採用、Comment Contract込み)=¥15.03、小計¥204.80。Audio(Key Phrase LLM+TTS+
ASR): gemini¥33.00+openai¥6.03+openai_asr¥1.59=¥40.62。**合計¥361.22**(上限
¥400以内)。委任文の目安配分(Research≈¥50/Writer≈¥120/TTS≈¥150)に対し、
Writer段階はTension leakage是正の試行錯誤(r2〜r7)により目安を大きく上回った
(実績¥204.80)が、Research(実績¥115.80、目安超過は限定的)とTTS/ASR段階
(実績¥40.62、目安を大幅に下回り)で吸収し、合計は上限内に収まった。

## 17. 未解決問題

1. Verified Fact Ledgerの定期再検証ルール(OPEN-166一般恒久仕様)は未決のまま。
2. 政治的態度変化に関する研究知見(V2-06〜V2-11相当、独・米filter bubble実験・
   Xホスティリティ再ランキング・Registered Report等)は、価値ある再Research
   成果でありながら、B-Family Voices記事の構造的制約(Discovery-syntax leakage)
   により本記事には反映できなかった。他の記事タイプ(例: Discovery/Trend形式)
   であれば活用できる可能性があり、別タスクでの再利用を検討する余地がある。
3. 既存音声`voices/audio/b1_2v_v2/`(Analytical Leakage残存)の取り扱いは
   OPEN-151で引き続き未決。

## 18. USER_DECISION_REQUIRED有無+ユーザー判断

**あり**。

**A(仕様・Product・実装判断待ち)**:
1. 新B1(本記事)をユーザーが試聴し、Google Sheet「Personalized News: Useful or
   Narrowing?」のAdvanced欄「—」へ本記事のURLを差し替えるか。
2. OPEN-166の恒久対応方針(定期再検証ルール新設 vs 現状の偶発検出時のみ対応)は
   未決のまま(推奨: 量産開始前に一度で良いので方針を決めておくと良いが、緊急性は
   低い)。
3. 既存音声`voices/audio/b1_2v_v2/`(OPEN-151、Analytical Leakage残存)を今後
   どう扱うか(現状維持/新Validatorで再評価・再生成)は、本タスクでは未着手のまま。

**B(ユーザー試聴・品質確認待ち)**:
- 新Personalized News B1(Advanced)の試聴依頼。12節のURL。旧B1(`b1_2v_v2`)とは
  別記事(新Ledger・新Writer出力)であり、Analytical Leakage残存がない点、
  政治的態度変化に関する主張を一切含まない点が異なる。試聴時の確認観点:
  (1) Voice A(便利さ)/Voice B(視野の狭まり懸念)の対比が自然で分かりやすいか、
  (2) Tension/Closingが単なる要約になっていないか、(3) Advanced(B1)として
  適切な難度・情報密度か。

★★★★報告ここまで★★★★
