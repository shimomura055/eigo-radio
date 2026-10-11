# QCD_COMPARISON_01 — 現行 vs 新方式(固定Prompt最大3回 + Primary NG時Secondary確認)

管理ID: FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 / 2026-10-11 / 今回は**無料検証のみ**(有料API 0)。新方式の実測値はなく、**過去データの再計算と確率モデル**による見込み。優先順位は ①音声品質(トーン連続性・誤PASS防止) ②完成率 ③コスト ④所要時間。
データ根拠: `replay_results_01.json`、`qcd_model_01.json`、`qcd_scenarios_01.json`、`local_wav_check_01.json`、`mutation_safety_01.json`(いずれも本ディレクトリ)。再現: `er056_en_asr_retry_replay_01.py collect|qcd|scenarios|mutations|local|medium`(課金API呼出なし)。

## (1) 現行仕様フロー図
CURRENT_SPEC_SURVEY_01.md §1(Standard A2 / Advanced B1B / 共通ASR判定)参照。要点: A2 は「標準2(同一Prompt)→10分cool-down→fallback1(別Prompt・Azure必須)→Local Rewrite」を、6%減速後の Primary-only 再検証NGの度に最大3周繰り返す。

## (2) Coffee NG の根本原因
COFFEE_NG_ROOTCAUSE_01.md 参照。1行要約: **偽NG(Primary-only減速後再検証+notation偽NG+Azure誤認識)と、Prompt不連続・LR誤span・証跡欠落という retry 制御の欠陥の複合**。確定した「真の音声不良」は0件(標準1回目・LR音声は未確定、要・人間聴取)。

## (3) 目標フローとの差分
TARGET_FLOW_DESIGN_01.md §2 の10項目。構造変更は「A2 fallback廃止」「減速外側ループ廃止/折込み」「英語 Primary-NG→Secondary 確認ゲート新設」「LR接続外し」の4点。

## (4) 条件別例外の要否
TARGET_FLOW_DESIGN_01.md §3-9。例外が必要なのは **ASR技術再試行(attempt非消費)** と **Key Phrase(現行4回構成維持)** の2点。日本語・共有殻は対象外。

## (5) 誤PASS・品質劣化リスクと防止策
| リスク | 無料検証での確認 | 防止策(案) |
|---|---|---|
| Secondary転写が真の誤りを通す(Validator側) | 合成16種(数値3・否定2・時制2・重要語4・文脱落/追加/反復4・entity1)で**誤PASS 0/16**、benign 7種中5種を救済(`mutation_safety_01.json`) | 数値/否定は Secondary を呼ばず再生成、厳格PASS集合、同一Validator |
| Secondary ASR 自身が原稿へ自動補正(LM寄り/Phrase List) | **未検証(測定不能)**: 真の誤読音声の正解ラベルがない。local small で NUM/NEG の真誤り4件は 4/4 NG のまま(救済されない)=自動補正は観測されず(n=4) | Phrase Listなし、2系統目(local medium)併用、Primary/Secondary 転写の全文証跡、ユーザー最終試聴を維持 |
| Primary PASS を信じすぎる(Primary誤PASS) | 過去の forced-Secondary で「Primary PASS・Azure NG」は queue 上 5件[同一原稿の重複を除き4件](2026-08〜09)。Azure diff は `sweets→suites`、`dates→states`、`M→am`、語脱落で **Azure側の誤認識/表記差が大半**に見える(FREE_VERIFICATION §4-5) | 目標どおり Primary PASS 時は Secondary 不要。ただし No.7 point_one_heading の事故(CS:1911)を根拠に、**Primary単独PASSの事後監査**(サンプル、local medium で無料)を提案 |
| 固定Prompt3回で全NG→HR率上昇 | 完了率 下限91.9%〜上限95.6% vs 現行93.1%(§(7)) | 実測は有料Trial(§(9)) |
| トーン不連続 | 新方式では**構造上ゼロ**(別Prompt経路を削除。fingerprint assert) | 現行(main)ではfallback Styleが別物([branch]は是正済み) |

## (6) TTS生成回数・ASR実行回数
**現行の理論最大**(1 segment、A2 EN本文): TTS = 外側3周×(標準2+fallback1+LR再TTS1) = **12**。Primary ASR ≒ TTS数、Azure = cascade(最大2/attempt)+forced(fallback/LR各1)+... 実例(Coffee part2): TTS 5、OpenAI ASR 7、Azure 4、LLM 2。B1B: attempt 3(+技術fallbackで最大6)+LR1。
**新方式**: TTS ≤ **3**(固定)。Primary ASR ≤ 3、Secondary ≤ 3(Primary NG かつ除外条件に非該当のattemptのみ。通常は0〜1)。LR・force_secondary・Primary#2/Secondary#2・減速外側ループは消滅。
**過去データ(narrative5、160 calls、Flash-Lite期)の実測**:
| 指標 | 値 |
|---|---|
| 1回目でPrimary合格 | 134/160 = 83.8%(95%CI 77.3〜88.7%) |
| 平均TTS/call | 1.188 |
| 2回目到達 / 2回目合格 | 22 / 13(59.1%、CI 38.7〜76.7%) |
| 3回目到達 / 3回目合格 | 8 / 2(25.0%、CI 7.1〜59.1%) |
| call内で未合格 | 11/160 = 6.9%(CI 3.9〜11.9%) |
| fallback経路を使ったcall | 7/160 = 4.4%(うち合格2・不合格5) |
| 同一segmentで複数call(減速取り直し/再実行) | 42/288 segment |
新方式の期待値(確率モデル、Primary通過率は上表、Secondary救済率rを感度):
| r(eligible NGのうちSecondaryが救済する割合) | E[TTS] | E[Secondary呼出] | P(HR) |
|---|---|---|---|
| 0.0 | 1.229 | 0.247 | 5.0% |
| 0.2 | 1.179 | 0.222 | 2.8% |
| 0.4 | 1.133 | 0.200 | 1.3% |
| 0.6 | 1.091 | 0.181 | 0.5% |
(モデルは p2=0.59・p3=0.25 を同一Prompt再試行の条件付き通過率とする近似。信頼区間が広く、p2/p3 は旧Promptの再試行を含む。現行観測値 TTS 1.188・未合格6.9%と比べ、r=0で新方式のHR率が下がるのは「fallback/外側ループ/stop_retrying 打切りで3回目まで到達しなかったcall」が3回目まで継続する効果が含まれる=要・実測。)

## (7) 完成率・Human Review率(過去データからの再計算)
narrative5 の call 160件(Flash-Lite期 2026-09-27〜、+Coffee snapshot)について、保存済み attempt の分類を再現し、「新方式なら何回目で終わっていたか」を下限/上限で算出した(`replay_results_01.json` `new_flow_completion_bounds_narrative5`)。
| | 完了 | 完了率 |
|---|---|---|
| 現行(call内でPASS) | 149/160 | 93.1% |
| 新方式 **下限**(Secondary救済ゼロ、旧fallback PASSは不明として除外) | 147/160 | 91.9% |
| 新方式 **上限**(数値/否定/低類似度以外のNGをSecondaryが全て救済と仮定) | 153/160 | 95.6% |
- 下限での差は-1.2pt(旧fallbackで通った2件分: meta part3、in_one_line)。上限との差6件は Secondary 救済対象型(数値/否定/低類似度以外)の未合格call。**LR救済**(過去記録18件中 RESOLVED 8 / 失敗10[再TTS不合格7・候補なし3]、`er011_output/local_rewrite_recovery`)は新方式では自動では発生しない(HR後オプション化)。LR成功8件のうち新方式で救済される割合は不明(Secondary/3回目で救われるかは未測定)。
- 無料のローカルASR代理検証(FREE_VERIFICATION §4-8): Primary NGのうち、non-entity内容語NG 7件中3件・低類似度1件を local small が原稿一致と判定、entity-onlyは0/5、数値・否定の真誤りは0/4。→ **独立ASRによる救済余地は「内容語・notation」型に偏り、数値・否定・固有名詞では小さい**(設計の除外条件と整合)。
- Coffee 実例への当てはめ(`local_wav_check_01.json`): 標準1・標準2・fallback の3音声を local medium は全て原稿一致と転写した。新方式(Secondary=local medium併用 または Azure以外)なら標準1回目(TTS#2)で完了=**TTS 2回、約5分、HRなし**だった可能性が高い(案Cなら初回TTS#1で完了)。Secondary=Azure のみだと標準2相当の偽NGが再現し、完了は保証されない。

## (8) コスト・所要時間
単価(Coffee実run `raw_usage_log` と `pricing_snapshot.json` から計算、USD/JPY=160):
| 項目 | 単価 | 所要(平均) |
|---|---|---|
| TTS gemini-3.8-flash-lite-tts(Batch) | ¥0.135/call | 120秒/call |
| OpenAI ASR gpt-4o-mini-transcribe | ¥0.068/call | 1.1秒 |
| **Azure STT** | **$1/音声時間 = ¥0.0444/秒 → 29秒で¥1.29、50秒で¥2.2** | 12〜24秒 |
| Luna(LR候補生成+QA) | 約¥0.19/call | 14〜17秒 |
| cool-down | ¥0 | **600秒固定** |
**重要な発見(F-7)**: `RUNTIME_EVIDENCE_01.md` の「ASR ¥4.68」は OpenAI ASR 69 call の合計(¥4.685)と一致し、**Azure 8 call(231.8秒 ≒ ¥10.3)が累計 ¥20.73 に含まれていない可能性が高い**(実質 ≒ ¥31 以上)。FALLBACK_REAL_PROBE の Azure 分も別途要確認。`part2` 単体の実費は TTS ¥3.02 + OpenAI ASR ¥1.77 + **Azure ¥8.79** + LLM ¥0.37 = **約¥13.96**(Azureが63%)。
narrative5 の1 segment当たり(過去実測平均+上記単価):
| | 現行(観測) | 新方式(Secondary=Azure, r=0〜0.4) | 新方式(Secondary=local, Azure 0) |
|---|---|---|---|
| TTS | 1.19回 ≒ ¥0.16 | 1.13〜1.23回 ≒ ¥0.15〜0.17 | 同左 |
| Primary ASR | ≒ ¥0.08 | ≒ ¥0.08 | ≒ ¥0.08 |
| Azure | cascade 6+forced 7 = 13 call/160(forcedは未記録分の推定)≒ ¥0.14 | 0.20〜0.25 call ≒ ¥0.36〜0.44 | ¥0 |
| 合計/segment | ≒ ¥0.39 | ≒ ¥0.59〜0.69 | ≒ ¥0.23〜0.25 |
→ **Azure をSecondaryにすると segment 当たり +¥0.2〜0.3(+50〜75%)**、記事(EN narrative約15 segment)で +¥3〜4.5。local faster-whisper(無料)なら現行より約40%減。ただし「救済でTTS再生成を回避する」効果は1回¥0.2程度で、Azure(¥1.8/40秒)の費用を回収できない=**Azureを使う理由は費用ではなく品質(独立ベンダーによる確認)**。(Azureの「現行」側は forced 呼出の未記録分を推定で補った値、秒数40秒は概算。)
所要時間(平均/segment): 現行 TTS 143秒 + cool-down 発動時(3回目到達 8/160=5.0%)600秒×0.05 ≒ 30秒。新方式 TTS 136〜148秒 + Azure 約3秒 + (cool-down継続時のみ)同程度。**HR近傍の長尾(Coffee: 25分)が最大の差**: 新方式は理論最大 TTS3回+cool-down10分=約18分(cool-down廃止なら約8分)。

## (9) Trial結果と Production反映に必要な変更範囲
- 今回: **無料検証のみ**(FREE_VERIFICATION_01.md)。Status 候補 = `USER_DECISION_REQUIRED`(設計案、Production採用は未承認)。
- 追加Trial案(本委任では実施しない。費用見積のみ):
  - **T-1 Secondary比較Trial**: 保存済みwav(Validatorで再現できたPrimary NG 約20本+Primary PASS対照 約40本=約60本、すでにローカルに存在)を **Azure(Phrase Listなし/あり)** と **local faster-whisper medium** で転写し、救済率・自動補正(原稿寄り)の有無・偽NG率を比較。Azureのみ有料: 約60本×平均30秒×¥0.0444/秒 ≒ **¥80(上限¥120)**。OpenAI ASRの再転写は不要(既存Primary転写あり)。使用モデル: Azure Speech STT(en-US)=現行Production Secondary、faster-whisper large系は不使用(medium/small、既インストール) — **ASR評価のため最新性の論点なし(LLM/TTSは使わない)**。Trial専用経路: `er056_*_trial` として Production code を呼ぶだけ、書込は `er056_output/` 限定。
  - **T-2 E2E Trial**: 新モード実装後に Coffee part2 相当+別3 segment を実run。TTS最大3×4 segment=12 call ≒ ¥1.6+ASR+Azure ≒ **¥10〜15**(上限¥30)。実装後に別途承認。
- Production反映の変更範囲: TARGET_FLOW_DESIGN_01.md §6(6ファイル・約10関数・3 flag)。CURRENT_SPEC の更新対象行: 1692, 1911, 1916, 1971(承認後)。

## (10) 未決事項候補・ユーザー判断が必要な点
TARGET_FLOW_DESIGN_01.md §7 の D-1〜D-11。特に優先度が高い4点:
1. **D-4 6%減速後検証の扱い**(案B=attempt内に折込み / 案C=格下げ。後者はOPEN-76の承認仕様変更)。Coffee の直接原因。
2. **D-1 Secondary ASR の選択**(Azure=高コスト・偽NG多め / local medium=無料・LM補正リスク / 併用)。
3. **D-6 Local Rewrite の位置づけ**(過去8件を救済、ただし本文変更・span誤りあり)。
4. **D-5 cool-down**(+10分、効果未確定)。
新規Open Item候補(登録は未実施): (a) 英語 Primary TCM に Secondary を呼ばない構造(SCG相当の英語版、OPEN-258の対称課題)、(b) 減速後再検証の外側ループがTTS上限3を破る件(F-1)、(c) 費用集計へのAzure未計上(F-7)、(d) fallback経路のcascade_steps/Azure転写未保存と queue 重複排除(F-3)、(e) `US`↔`U.S.` notation 偽NG(F-5)、(f) LR の NG span が Primary転写基準(F-4)。
Existing Spec / Prior Trial Check(PM_GOVERNANCE 21節): (a)(b)(e)は A(既存仕様の欠陥/対称課題)、LR位置づけ・Secondary選択は B(OPEN-257 B1〜B4 / SCG未採用事項と隣接・未承認)、新規として C に分類できるのは Primary単独PASS事後監査案のみ。

## (11) 使用モデル名 / 最新か
- 本委任での有料モデル呼び出し: **なし(0円)**。LLM/TTS/ASR(OpenAI・Azure・Gemini)は呼んでいない。
- 無料ローカル: faster-whisper `small` / `medium`(Systran、HF cache既存。Productionの Connected Speech Layer と同系統)。ASR再現・代理指標のためで、Productionモデル選定ではない。最新世代LLM原則(PM_GOVERNANCE 25節)の対象外(LLM/TTS評価ではない)。ASR ProductionモデルはRouting SSOT(gpt-4o-mini-transcribe / Azure)をそのまま参照。
- 参照した実run(Coffee)のモデル: TTS=gemini-3.8-flash-lite-tts(最新)、EN=gpt-6-luna(最新)、ASR=gpt-4o-mini-transcribe+Azure(Production正式)。
