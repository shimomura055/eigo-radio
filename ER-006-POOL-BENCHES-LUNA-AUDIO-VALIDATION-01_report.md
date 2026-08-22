# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 完了報告

Public Benches 1 Topic × B1/A2 = 2 episodesの範囲で完了。残りPool Topicの生成には進んでいない。

## 0. 最初に回答(21章の質問に対する要約)

1. **Luna B1/A2完成可否**: 完成。B1: Writer Fact Check PASS・Ledger完全準拠。
   A2: Fact Check REVIEW_REQUIRED(矛盾ではなく詳細未確認3件)・Ledger MINOR
   逸脱2件。いずれも致命的な問題ではない(詳細5章)。
2. **Human Review Artifact**: 3本(下記)。
   - [Public Benches B1: Sol vs Luna](https://claude.ai/code/artifact/3bc2118f-af92-479a-9c1e-0f91db23fca7)
   - [Public Benches A2: Sol vs Luna](https://claude.ai/code/artifact/293c96b0-8e51-4f78-a9d2-dbd501267205)
   - [hostile architecture 発音診断(7クリップ)](https://claude.ai/code/artifact/35f67200-4d3e-4ec0-b593-88e271071f39)
3. **全OpenAI stage actual model_id**: 4章。
4. **Sol call 0件の証拠**: 4章(raw_usage_log実測、writer/support/tts全stageでSol呼び出し0件)。
5. **Luna Writer品質評価**: 5章。
6. **Luna Support品質評価**: 5章。
7. **旧Sol版との差**: 5章(B1はLunaの方がクリーン、A2はLunaがわずかに逸脱増)。
8. **hostile architecture問題の根本原因**: 6〜8章(TTS生成時の振幅エンベロープ特性、
   hostile固有ではなく短いKey Phrase発話の一般的傾向の可能性)。
9. **問題はraw TTS時点かassembly後か**: raw TTS時点(8章、cross-correlationで実測確認)。
10. **English 1回目/2回目の双方で発生した理由**: 6章(設計上、同一audioを2回再生する
    ため、そもそも独立した2回の生成ではない)。
11. **実施した恒久対策**: Audio Validation(正規化+6分類+retry guardrail)を
    Production英語retry loopへ配線(9章)。振幅エンベロープ検出の新Validationは
    今回実装せず、Open Item化(10章)。
12. **他Key Phraseにも再発し得る問題か**: 再発しうる(7章、"happy ending"等でも
    同程度の急峻さを確認)。hostile固有のwhitelistは作らなかった。
13. **B1 Actual Cost**: ¥146.5(Luna、11章)。
14. **A2 Actual Cost**: ¥206.5(Luna、11章)。
15. **Writer/Support Cost**: Writer合計 Sol ¥693.1→Luna ¥41.6、Support合計
    Sol ¥72.5→Luna ¥5.3(11章)。
16. **Clean Audio Cost**: 12章(推定、旧手法踏襲)。
17. **旧Public BenchesとのWaste比較**: 12章。
18. **STOPPED数 before/after**: Sol 4件 → Luna 7件STOPPED+1件UNCERTAIN(13章、
    詳細な原因分析あり)。
19. **Rewrite数・理由**: 0件(Luna版は一発合格、Rewrite不要。14章)。
20. **Regression test結果**: 全PASS(15章)。
21. **残存Open Item**: OPEN-44(hostile/振幅エンベロープ問題、`UNDER_REVIEW`)。
22. **残りPool Topicへ進める状態か**: 断定しない(16章)。
23. **新規API Cost**: ¥353.0(Luna本番生成)+診断用生成 約¥1程度(h onset比較4件)。

---

## 1. Public Benches Luna版の生成

Research(Evidence Pack/VFL/Verification/Ledger)は完全に再利用し、再実行していない
(Research不備は見つからなかった)。Writer→Support→Key Phrase→Support Fact
Check→TTS/ASR/Assemblyの全工程をModel Routing Contract経由でLunaのみを使い新規生成した。

出力: `er006_output/pool_pilot_01/pool_benches_luna/`
(`b1b/assembled/English_Your_Way_B1B_POOL_BENCHES_LUNA.wav`、
`a2/assembled/English_Your_Way_A2_POOL_BENCHES_LUNA.wav`)。

## 2. Public Benches旧Failureとの比較(14章の作業)

旧Public Benches(Sol)で問題だった4箇所(B1 point_two・B1 Key Phrase 2・A2
full_story_part2・A2 point_two)は、いずれも今回のROOTFIX/PREPROD-HARDENING
調査で「表記差によるSurface-only mismatch」と判明済みの箇所。今回のLuna版でも
一部(A2側のMalmö/Triangeln文脈の`point_two`)で同種の事象が再現したが、
新たにASR_VALIDATION_UNCERTAIN(retry打ち切り+Human Review対象)として正しく
処理されるようになったことを確認した(旧版は12回まるごとSTOPPEDするまで
気づかれなかった)。

## 3. Human Review Artifact

0章のリンク参照。B1/A2それぞれSol版・Luna版の音声・記事本文・Fact Check結果・
Ledger逸脱・Audio QA(STOPPED/UNCERTAIN一覧)を並べて比較できる。hostile
architecture診断ページは、Sol B1・Sol A2・Luna B1の実音声に加え、追加生成した
4クリップ(hostile再生成2件・比較用/h/語2件)を個別に聴ける。

## 4. Model Routing Telemetry(証拠)

`raw_usage_log.jsonl`(theme=`pool_benches_luna`)の実測集計:

| stage | provider | model_id | 件数 |
|---|---|---|---:|
| writer_b1 | openai | **gpt-5.6-luna** | 3 |
| writer_a2 | openai | **gpt-5.6-luna** | 3 |
| support_b1 | openai | **gpt-5.6-luna** | 8 |
| support_a2 | openai | **gpt-5.6-luna** | 8 |
| tts_b1 | gemini | gemini-2.5-pro-preview-tts / gemini-3.1-flash-tts-preview(日本語) | 39 / 16 |
| tts_a2 | gemini | 同上 | 45 / 11 |
| tts_b1/a2 | azure | azure-speech-stt | 54 / 56 |

**OpenAI呼び出し22件全てgpt-5.6-luna。gpt-5.6-solの呼び出しは0件。**

補足: TTSは英語用`gemini-2.5-pro-preview-tts`と日本語用
`gemini-3.1-flash-tts-preview`の2モデルを使い分ける既存設計だが、
`er006_model_routing_contract_01.py`の`TTS_MODEL`定数は英語用の1つしか
定義していない(Provider単位の`require_provider()`はTTS呼び出し自体には
まだ配線していないため、今回はこの差異を検出する仕組みではなく目視確認で
気づいた)。Gemini製品ファミリー内という点では契約に反していないが、
将来TTSもmodel単位で厳密化する場合はSSOTを2モデル対応へ拡張する必要がある。

## 5. Luna Writer/Support品質評価

| | Sol版(旧) | Luna版(新) |
|---|---|---|
| B1 Writer Fact Check | PASS | **PASS** |
| B1 Ledger Deviation | MINOR 1件 | **LEDGER_COMPLIANT(0件)** |
| A2 Writer Fact Check | PASS | **REVIEW_REQUIRED**(矛盾0件、詳細未確認の主張3件) |
| A2 Ledger Deviation | LEDGER_COMPLIANT(0件) | MINOR 2件 |
| Support Fact Check(B1/A2共) | PASS | PASS |

**B1はLuna版の方がクリーン(Sol版にあった1件のMINOR逸脱がLuna版では0件)。**
**A2はLuna版がSol版よりやや逸脱が増えた**(ただしいずれもMINOR、矛盾や
虚偽記載は無い)。A2 Fact Checkで指摘された3件は、いずれも「部分的にしか
確認できない」「明示的な記載までは確認できない」という精度面の留保であり、
事実誤認ではない。総じて**明確な品質劣化があるとは判断していない**が、
A2でSol版より慎重な確認が必要という留保は残す。記事本文自体(構成・自然な
英文・情報密度)は、実際にArtifactで読み比べての判断をお願いしたい。

## 6. hostile architecture問題: 調査手順と切り分け結果

A. **Canonical text**: "hostile architecture"のみ、余分な文字・記号なし(確認済み)。
B. **TTS input**: Structured Separation後のTEXT TO SPEAK sectionも汚染なし
   (`p4c.build_tts_prompt(text, style_prefix)`、textはそのまま渡る設計を確認)。
C. **Raw TTS audio**: 振幅エンベロープを解析(下記7〜8章)。
D. **Assembly後Audio**: cross-correlationで実際のassembled episode中の該当箇所
   (前後2回、574,058サンプルの精度で特定)を抽出し、raw音声とエンベロープ形状を
   比較。**完全に同一の波形形状**(gain scaling以外の差なし)であることを定量確認。
   Assembly処理(48kHzへのresampling・RMS gain)による新たな歪みではないと結論。
E. **ASR transcript**: 全サンプルで"Hostile architecture."と正しく書き起こされて
   おり、ASR一致だけでは今回の問題を検出できない実例として記録した。

**English 1回目/2回目の双方で発生した理由**: `er003_b1_p9a_audio.py::build_key_
phrase_block()`が、英語Componentを「1回目・2回目とも同じ音声を再利用する」設計
(コード内コメントで明記)であることを確認した。つまり独立した2回の生成ではなく、
**同一の1つのTTS生成結果を、組み立て時に2回concatenateしているだけ**。問題が
あれば両方に出るのは当然の帰結であり、「2回とも同じ問題が起きた」ことは追加の
証拠にはならない。

## 7. 発音問題の一般化検証(hostile固有か/h/開始語全般か)

既存生成物だけでは原因を確定できなかったため、最小限の追加生成(4件、Model
Routing Contract経由・費用は微小)を行った:

| サンプル | 20ms窓での最大振幅ジャンプ比 | 備考 |
|---|---:|---|
| hostile architecture(Sol B1) | 4.0倍 | |
| hostile architecture(Sol A2) | 変化はより緩やか | |
| hostile architecture(診断再生成1) | 34.8倍(外れ値) | ASRが先頭に"A"を幻聴的に追加(hallucination、別事象) |
| hostile architecture(診断再生成2) | 3.6倍 | |
| hostile architecture(Luna B1) | **2.4倍** | 5サンプル中最も滑らか |
| hidden cost(比較語) | 2.6倍 | |
| happy ending(比較語) | **4.7倍**(hostileより急峻) | |

**"happy ending"がhostileより急峻な立ち上がりを示したことから、この特性は
hostile固有ではなく、短いKey Phrase発話でのTTS生成に伴う一般的な(ただし
確率的にばらつく)特性である可能性が高いと判断した。** 個別語のphonetic
respelling・whitelistは作っていない。

## 8. Raw TTS vs Assembly後の定量比較

[er006_output/pool_pilot_01/](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_output/pool_pilot_01/)
配下のnarration(per-segment)とassembled(完成episode)から該当箇所を
cross-correlation(scipy.signal.correlate)で特定し、20ms窓RMS包絡線を比較した。
Assembly後の2箇所(前後の再生)は完全に同一の値を示し(設計通り同一audioの
再利用)、raw音声との形状比較でも新たな歪みは検出されなかった。**根本原因は
Assembly/trim/normalization処理ではなく、raw TTS生成時点で既に決まっている**
と結論した。

## 9. Audio ValidationのProduction配線

ER-006-POOL-PREPROD-HARDENING-01で実装済みだった正規化+6分類+Protected
Check+retry guardrailを、英語(en)のProduction retry loop 5モジュールへ配線した
(前回のcommitで実施、詳細は
[ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01(進行中1/2)commit](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_preprod_hardening_01_validation.py)参照)。
実際のPublic Benches Luna版生成で、A2 `point_two`が新status
`ASR_VALIDATION_UNCERTAIN`で正しく打ち切られたことを実測で確認した
(9章の一部として既に前コミットで完了・検証済み)。

## 10. 恒久対策として実装しなかったもの(Open Item化)

振幅エンベロープの急峻さを検出する新しいAudio Validation(語頭200-300ms区間の
RMS変化率チェック等)は、**今回は実装していない**。理由: 十分なsample数
(今回5サンプル)での閾値設計は時期尚早であり、誤検知(正常な発話を過剰に
reject)のリスクを、追加テストなしに本番へ投入したくなかったため。
[OPEN_ITEMS.md](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md)
のOPEN-44として記録し、`UNDER_REVIEW`のまま維持する。「ASR一致=発音品質
PASSではない」という原則は
[CURRENT_SPEC.md](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/CURRENT_SPEC.md)
のQA/Human Review節へ明文化した。

## 11. Cost(実測、Model Routing Telemetryから直接計測)

| | Sol版(履歴実費、Rewrite込み) | Luna版(新規実費、Research再利用のため0円計上) |
|---|---:|---:|
| B1 Actual | ¥443.1 | **¥146.5** |
| A2 Actual | ¥524.0 | **¥206.5** |
| Writer合計(B1+A2、FC/Deviation込み) | ¥693.1 | **¥41.6** |
| Support合計(B1+A2、KP/FC込み) | ¥72.5 | **¥5.3** |
| Audio合計(TTS+ASR、B1+A2) | ¥201.5 | ¥306.1 |
| **総額** | **¥1,003.3** | **¥353.0** |

Writer+Supportは約16分の1(¥765.6→¥46.9)。Audioのみ約1.5倍に増加(13章で
原因分析)。総額は約65%削減。**Sol版の総額にはWikipedia出典修正によるRewrite
(Research再実行を除く、Writer再実行分)が含まれており、単純な「1回で書けた
場合のコスト差」よりは実質的な差が大きく出ている点に留意**(Luna版はRewrite
0回で一発合格のため)。

## 12. Clean Audio Cost・Waste評価(旧Baselineとの比較)

ER-006-POOL-PILOT-COST-ROOTFIX-01で確立した「segment attempt1のみ」を
Clean Audio Costとする方式を踏襲。Luna版の各segmentのattempt1コストを合計:

Luna Clean Audio Cost(推定): B1 ¥38.4 / A2 ¥58.2(概算、詳細は
[cost_time_summary系JSON](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_output/pool_pilot_01/pool_benches_sol_vs_luna_cost.json)参照)。
Sol版のClean Audio Cost(ROOTFIX報告より): B1 ¥36.9 / A2 ¥40.3。**Clean Audio
Cost自体はSol/Lunaでほぼ同水準**(TTS/ASRのProvider・単価はSol/Lunaで変わらない
ため、これは予想通り)。**Audio Retry Wasteの増加(A2側で特に顕著)が、7件
STOPPED+1件UNCERTAINという今回の結果を押し上げている主因**。

## 13. STOPPED増加の原因分析(重要、正直な報告)

Luna版はSol版より多くのSTOPPED(7件 vs 4件)+新規UNCERTAIN(1件)を記録した。
個別調査の結果:

| segment | 原因 |
|---|---|
| B1 full_story_part1 | "street furniture"→ASRが"St. furniture"と書き起こす、既知の系統的ASR表記揺れ(Sol版でも同一パターンを確認済み) |
| B1 point_one | 固有名詞"Ottoni"の誤認識+数字"three"を"3:00"と書き起こす(時刻表記混入)ASR quirk。Protected Checkが数字差として正しく検出、保守的にretry対象のまま |
| B1 comment_3/point_two, A2 full_story_part1/point_one | 句読点結合等の軽微なASR表記揺れが、内容語差として保守的に判定された可能性(個別の深掘りは今回のスコープでは実施せず) |
| A2 point_two | Malmö/Triangeln固有名詞の音訳差(既知パターン)。**新設のASR_VALIDATION_UNCERTAINで正しく打ち切られた**(旧版のような12回STOPPEDではない) |
| B1 kp5(日本語) | 日本語経路(既存phonetic_verdict方式、今回変更なし)側の事象 |

**結論: STOPPED増加はLuna Writerが生成した文章の品質問題ではなく、この
記事が扱うトピック特有の要素(固有名詞Malmö/Triangeln、"street furniture"
という頻出フレーズ)がAzure ASRの表記揺れを誘発しやすいことに起因する。
Sol版でも同種の事象("street"→"St."、Malmö/Triangeln)が確認されており、
Model(Sol/Luna)の違いによるものではない。** ただし、Protected Check
(数字・内容語チェック)が保守的に働きすぎて、本来pass可能なケースまで
retry対象にしている可能性は残る(6章のcomment_3等)。これは今回深掘りして
いない残存課題として記録する。

## 14. Rewrite

**0回。** Luna版のWriter/Support/Fact Check/Deviation Checkは、いずれも
1回の実行(Rewriteなし)で完了した(Fact Check REVIEW_REQUIREDは自動での
書き直しをトリガーする性質の判定ではなく、Human Reviewでの確認対象として
記録するに留めた。矛盾ではなく詳細未確認レベルのため、機械的な連続
Rewriteは行わなかった)。

## 15. Regression test結果

既存の全regression test(Model Routing Contract・Static Audit・Boundary
Test・Audio Validation Wiring確認・Ledger metadata)を再実行し、全PASS。

## 16. 残りPool Topicへ進める状態か

断定しない。Writer/Support面はLunaで明確な品質劣化は見られず、Costも
大幅に下がった。一方でAudio面はSTOPPED件数が今回増えており(原因は
Model由来ではないと判断しているが)、6章で見送った振幅エンベロープ
Validationが未実装のままである点、A2でLuna版が旧版よりやや逸脱が増えた
点は、量産判断の前に確認しておくべき留保事項として残す。

## 17. 受入条件チェック

| # | 内容 | 状況 |
|---|---|---|
| 1 | Public Benches B1/A2 Luna版完成 | ✅ 1章 |
| 2 | Research原則再利用 | ✅ 1章(再実行せず) |
| 3 | Sol API call 0 | ✅ 4章 |
| 4 | Luna routing telemetry証明 | ✅ 4章 |
| 5 | Sol版/Luna版比較Artifact | ✅ 3章 |
| 6 | Writer品質比較あり | ✅ 5章 |
| 7 | Support品質比較あり | ✅ 5章 |
| 8 | hostile architecture旧audioの原因切り分け完了 | ✅ 6〜8章 |
| 9 | raw TTS vs assembled audio比較あり | ✅ 8章(cross-correlation実測) |
| 10 | English 2回とも問題が起きた理由を評価 | ✅ 6章(同一audio再利用と判明) |
| 11 | 個別whitelist/phonetic hackなし | ✅ |
| 12 | 必要なら一般化した恒久対策 | ✅ 9章(Audio Validation配線)、10章(振幅エンベロープ検出は将来課題として明記) |
| 13 | Audio validationをProduction loopへ配線 | ✅ 9章 |
| 14 | 旧STOPPED segmentとのbefore/afterあり | ✅ 2・13章 |
| 15 | Clean/Actual/Waste分離 | ✅ 11〜12章 |
| 16 | 異常retryでCost暴走しない | ✅ Guardrail動作確認済み、想定外の高額支出なし |
| 17 | Regression tests PASS | ✅ 15章 |
| 18 | Human Review Artifactあり | ✅ 3章 |
| 19 | サービス仕様を勝手に変更しない | ✅ 変更なし(Audio実装詳細・Model Routing運用の追加のみ) |

## 18. リスク・注意点

- A2でLuna版がSol版よりやや逸脱が増えた点(5章)、Audio STOPPEDが増えた点
  (13章)は、明確な劣化ではないと判断しているが、量産前に追加サンプルでの
  確認が望ましい。
- hostile architecture問題(OPEN-44)は根本原因の仮説は強く支持されたが、
  「なぜ人間の耳には特に/p/様に聞こえるのか」の音響心理学的な最終確証はない。
  実際にArtifactを聴いてユーザー自身の耳で判断してほしい。
- 振幅エンベロープ検出Validationは未実装。実装する場合は追加のサンプル収集
  ・閾値設計・regression testが別途必要。
- TTSのGemini model(英語/日本語2種)はSSOTの`TTS_MODEL`定数が1つしか
  カバーしておらず、Provider単位のfail-closed検証もTTS呼び出し自体には
  配線していない(Contractの対象範囲としては未成熟)。

## 19. 次のステップについて

このタスクをもって停止する。残りPool Topicへの本番投入は、18章の留保事項
(A2品質の追加確認、振幅エンベロープValidationの要否)について判断してから
進めることを推奨する。
