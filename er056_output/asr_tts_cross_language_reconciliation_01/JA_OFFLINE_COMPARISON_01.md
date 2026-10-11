# JA_OFFLINE_COMPARISON_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01、2026-10-11)

日本語に目標共通フロー(初回 -> Primary NG -> Secondary -> 両NG -> 再生成(1) -> (2) -> Human Review、同一Prompt固定、minimal fallback/Local Rewrite除外)を当てはめた場合のオフライン再計算。
使用モデル/API: **API未使用**(有料API 0円)。再利用データ: Phase 0 Trial保存Azure転写25行・既存Primary転写・whisper補助転写(`er053_output/open258_phase0_trial_01/`)、`attempt_history.jsonl`、JA attempt json 630件、OPEN258_OFFLINE_EVIDENCE_01.json。判定は現行コード(`er007_ja_*`、Reading Resolver LLM OFF)。
再現: `.venv\Scripts\python.exe er056_ja_scg_offline_replay_01.py`(出力 `ja_offline_replay_01.json`)。

## 重要な前提・限界(先に)

1. **標本は小さく偏っている**: Phase 0は「Primary NGの保存音声」から救済候補(whisper一致)+誤PASS検証用C群を選んだ25音声。母集団の率(誤PASS率・救済率・HR率)を直接示すものではない。
2. ground truth(音声が実際に原稿通りか)は試聴のみ。ラベルは代理: `error_proxy`=C群5(whisper 2モデル+Primaryが原稿と不一致)、`correct_user`=META出演3(ユーザー試聴で出演)、`correct_strong/probable`=whisper 2モデル/Azureが原稿と一致等、`needs_listen`=RESULT_01(4)の要試聴5音声(Azure PASSだがwhisper/Primaryと不一致)。
3. 誤PASSは「error_proxyでSCG PASS」の件数。needs_listenでSCG PASSした5音声は、試聴で誤りと判明すれば誤PASSに加算される(未確定)。
4. 「再生成回数」は標本groupの実履歴attempt数(`n_attempts_hist`)と、SCG PASSできる最初のattempt `k`から`n - k`を機械的に削減としている(RESULT_01(5)と同方式)。3回上限(現行Production)を適用した版も併記。
5. 英語側の知見・Tierの流用はしていない。目標フローの「両NG->再生成」は日本語の現行を変える前提の仮定(UNCERTAIN経路の扱いは下記「フロー差」参照)。

## 1) 比較したポリシー

| 略称 | 内容 | 意味 |
|---|---|---|
| PRE_SCG | SCG導入前(Primary TCM -> 再生成のみ) | 2026-10-11以前 |
| CURRENT | 現行Production SCG(除外: 数字/否定/類似度<0.4/C1[entity_like・辞書読み・ラテン]/C2/否定マーカー/length_ok) | PRODUCTION_WIRED |
| NO_C1 | CURRENTからC1(entity_like等)だけ外す(仮定) | g8が救済 |
| HARD_ONLY | 数字・否定(保護チェック+否定マーカー)だけ除外(類似度<0.4・C1・C2も外す)(仮定) | 「Secondary確認を全PrimaryNGに」へ最も近い |
| ALL | 除外なし(Primary NGなら必ずSecondary)(仮定) | 参照上限 |

全ポリシーでSCG PASSは現行どおり「Azure転写が原稿とEXACT/NORMALIZED一致」のみ。PHONETIC_MATCHを許す仮定は別行で併記。

## 2) 音声単位の結果(25音声、Phase 0保存データ)

| ポリシー | Azure呼出 | Azure秒 | Azure見積(円) | SCG PASS | うち確定正解音声の救済(母数15) | PASS中の要試聴 | 誤PASS(C群5) | 不要NGのまま残る確定正解音声 |
|---|---|---|---|---|---|---|---|---|
| CURRENT | 21 | 80.6 | 4.04 | 13 | 8 | 5 | **0** | 7(g2,g8,g11a2,g21,g23,g36,g7) |
| NO_C1 | 22 | 82.9 | 4.18 | 14 | 9 | 5 | **0** | 6(g8が救済) |
| HARD_ONLY | 24 | 86.7 | 4.40 | 15 | 10 | 5 | **0** | 5(g7も救済) |
| ALL | 25 | 90.2 | 4.58 | 15 | 10 | 5 | **0** | 5 |
| (参考)PHONETIC_MATCHもPASS | CURRENT 21 / NO_C1 22 / HARD 24 / ALL 25 | - | - | 16 / 17 / 18 / 18 | - | - | 0(C群のAzure転写はすべてTCM) | - |

読み取り:
- どのポリシーでも**C群5音声の誤PASSは0**(Azureは原稿へ丸めず逐語転写)。除外を外しても(HARD_ONLY/ALL)この標本では増えない。ただし標本5件・濁点誤読を含まない。
- CURRENTで残る不要NG7件の内訳: Azure側も表記差(PHONETIC_MATCH)でNG=g2,g21,g36(PHONETIC許容なら救済可、ただし現行はユーザー決定済みの安全条件で非許容)、Azureの助詞欠落=g11a2、Primary/Azureとも同一誤聴=g23(Muse型、SCGでは救えない)、除外起因=g8(C1)・g7(類似度<0.4)。
- 費用: CURRENTのAzure 21回見積約4.04円に対し、回避できる再生成(下表)は約0.1円/回(RESULT_01(5)の概算、Gemini TTS+Primary ASR)。標本では**金額は純増約2〜3円**(RESULT_01と整合)。便益は金額でなく時間とStyle/Voice揺れ・HR回避。

### 音声別一覧(`ja_offline_replay_01.json`より)

| key | GT | 原稿 | Primary | Azure | Sec判定 | CURRENT除外 | CUR | NO_C1 | HARD | ALL |
|---|---|---|---|---|---|---|---|---|---|---|
| g35_japanese_title_a1 | correct_user | AIの電話に人間が出演… | …出現… | …出演… | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g35_japanese_title_a2 | correct_user | 同上 | 同上 | 同上 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g35_japanese_title_a3(fallback) | correct_user | 同上 | …出現、… | 同上 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g12_kp1_ja_aoede_a2 | error_proxy | しばられず自由になれる感じの | 縛られる、自由に… | 縛られる。自由に… | TCM | negation_marker_diff | - | - | - | - |
| g3_kp4_ja_charon_a1 | error_proxy | 体内時計 | 体内毒行 | 体内どこ。 | TCM | (呼出) | - | - | - | - |
| g4_kp2_ja_charon_a1 | error_proxy | 証拠だと受け取られる | 証拠がと… | 証拠が？と… | TCM | (呼出) | - | - | - | - |
| g5_kp4_ja_charon_a1 | error_proxy | 名所を中心にした旅程 | 名勝を…旅亭 | 名称を…料亭 | TCM | heterophone_reading_candidate | - | - | - | - |
| g6_kp5_ja_charon_a1 | error_proxy | 形になり始める | 形に始める | 形に始める。 | TCM | (呼出) | - | - | - | - |
| g2_kp2_ja_charon_a1 | correct_strong | においを出す | においを断つ。 | 匂いを出す。 | PHONETIC | (呼出) | - | - | - | - |
| g8_kp4_ja_charon_a1 | correct_strong | 熟すと出るガス | じくすと出るカス。 | 熟すと出るガス。 | NORMALIZED | entity_like_diff | - | PASS | PASS | PASS |
| g11_kp5_ja_aoede_a1 | needs_listen | 理屈の上では | 肉の上では | 理屈の上では。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g11_kp5_ja_aoede_a2 | correct_strong | 理屈の上では | リクスの上では | 理屈の上で。 | TCM | (呼出) | - | - | - | - |
| g17_kp5_ja_charon_a1 | correct_strong | 最新のニュースについていく | …追いついていく。 | …ついていく。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g20_kp2_ja_charon_a1 | correct_strong | …調整される | …調整する。 | …調整される。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g21_comment_3_a1 | correct_strong | 世界市場の価格は…(19秒) | …(表記差) | …(表記差) | PHONETIC | (呼出) | - | - | - | - |
| g23_meaning_2_a1 | correct_probable | 焙煎前のコーヒー豆 | 買いせまいの… | 焙煎米の… | TCM | (呼出) | - | - | - | - |
| g27_kp1_ja_charon_a1 | needs_listen | 上がった分をいったん吐き出す | …一旦履きます。 | …いったん吐き出す。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g31_meaning_2_a1 | correct_strong | 海を封鎖すること | 海をふささすること。 | 海を封鎖すること。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g33_meaning_5_a1 | correct_strong | 目を引く | 目をしく。 | 目を引く。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g33_meaning_5_a2 | correct_strong | 目を引く | 目をしつ | 目を引く。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g36_comment_1_a1 | correct_strong | まず、20％という計画が… | 20パーセント… | 20%… | PHONETIC | (呼出) | - | - | - | - |
| g18_meaning_2_a2 | needs_listen | 拒絶されたように感じる | 強制された… | 拒絶された… | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g18_meaning_2_a3 | needs_listen | 同上 | 同上 | 同上 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g1_meaning_4_a1 | needs_listen | 活動し続ける | 活動をし続ける。 | 活動し続ける。 | NORMALIZED | (呼出) | PASS | PASS | PASS | PASS |
| g7_meaning_4_a1 | correct_strong | 湿度 | 死図塔 | 湿度。 | NORMALIZED | similarity_lt_0.4 | - | - | PASS | PASS |

## 3) segment(group)単位: TTS再生成・Human Review・完成率(3回上限を適用、標本20group)

20group = Phase 0で実行した全group(META g35、14群の実行分、C群、g18、g1。g24=g21・g26=g23の重複音声は除く)。完成=3 attempt以内に合格。HR/STOPPED=3 attempt以内に合格せず。

| ポリシー | TTS attempt総数 | 3回以内に完成 | HR/STOPPED | PRE_SCG比のattempt削減 |
|---|---|---|---|---|
| PRE_SCG | 48 | 15 | 5(g35,g1,g6,g11,g18) | - |
| CURRENT | 35 | 19 | 1(g6=C群の真のTTS誤り) | -13 |
| NO_C1 | 34 | 19 | 1 | -14 |
| HARD_ONLY | 33 | 19 | 1 | -15 |
| ALL | 33 | 19 | 1 | -15 |

- 標本内HR/STOPPED率: 25%(5/20) -> 5%(1/20)。完成率: 75% -> 95%。**ただし標本が救済候補に偏るため、母集団の率ではない**。
- 時間: 1回のBATCH再生成=120〜170秒(RESULT_01実測)。CURRENT 13回削減=約26〜37分。Azure 21回の合計待ち時間は約29秒(平均1.4秒)。
- 全体母集団の参考(確定): `attempt_history.jsonl`の実運用JA segment呼出(test theme除外、2026-09-05以降550件)は初回成功91.3%(502/550)、平均TTS attempt 1.10、HR到達26件(4.7%)。JA attempt json 630件中、不合格77件のうち76件がTCM(Primary NG)。SCGが救える割合はこのTCMのうち一部で、Phase 0の25音声以外は未測定(下限として、25標本でCURRENT PASS 13件=TCM 76件の約17%)。

## 4) 目標共通フローを日本語に当てはめたときのフロー差(現行からの変更点)

| 項目 | 現行日本語 | 目標フロー適用後 | 影響(オフライン推定) |
|---|---|---|---|
| Primary NG時 | TCMのみSCG(除外あり)。UNCERTAINは旧Cascade 4step | 全NGでSecondary 1回 | 除外が外れた分のAzure呼出が増える(HARD_ONLY: +3/25) |
| 両NG後 | 再生成(標準2回目) | 再生成(1) | 同じ |
| 3回目 | **minimal fallback(styleがJ3->minimalへ変化)** | 同一Prompt(2回目と同じ)で再生成(2) | Voice/Style一貫性向上。ただし導入理由(短いA2日本語のinstruction leakage、ER-003-N3-ROOT-FIX-01)が再発するリスクは未測定 |
| UNCERTAIN(ガス/カス単独等) | Cascade 4step -> 全不一致でHR(再生成しない) | Secondary 1回 -> 両NG -> 再生成(1)へ | HR行きが減り再生成が増える方向。標本に純UNCERTAINは0(HR queue 8件は全てUNCERTAIN: 下記) |
| Local Rewrite | 日本語なし | 除外(既に無い) | 差なし |
| HR | 3 attempt後 or UNCERTAIN尽き | 再生成(2)後 | 同じ(上限3回) |

- 履歴のJA minimal fallback成績(確定、attempt json 630件): minimal fallback 19 attempt中7件合格(36.8%)。標準+custom経路のattempt1は468中426合格(91.0%)、attempt2は128中110合格(85.9%)。3回目に到達するsegmentは難しい(ASRが繰り返し誤るか、TTSが繰り返し誤る)ため、**同一Promptへ変えた場合の3回目成功率は直接比較できるデータがない**(選択バイアス)。標本group内のminimal fallback attempt 4件(g35 a3、g1 a3、g6 a3/a6)は全て不合格。
- JA minimal fallbackで最終採用された音声は7 segment(attempt json、全期間)。J3 style適用以降の件数は未集計。
- Voice一貫性(Charon/Aoede、モデルは同じ)は変わらない。変わるのはstyle prefixのみ(J3->minimal)。J2_BRIGHT(approved-but-unwired)導入時も同様に、現行fallbackは上書きしない設計のためJ2を喪失する(推測ではなくコード上確定: N3 L532のfallback呼出にstyle引数なし、標準経路のみ転送L516)。
- 旧Cascade(UNCERTAIN)のHuman Review 8件(`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`、2026-08-25〜09-25)は全て、Primary#2がPrimary#1と、Azure#2がAzure#1と実質同一転写(再実行の独立性が低い)。目標フロー化すれば4 ASR callが2 ASR call(Primary 1+Secondary 1)になりASR費用が減る。

## 5) 代表ケース(通常語・固有名詞・数値・否定・時制・同音異義語)

実データ(Phase 0)と、現行コードで経路を確認した合成ケース(合成は「Primary転写がこうだった場合にコードがどう動くか」の経路確認のみ。Secondary転写の想定はASR性能の証拠ではない)。

| 種別 | ケース | Primary分類 | 現行の経路 | 目標フロー(除外撤廃 HARD_ONLY) | 備考 |
|---|---|---|---|---|---|
| 通常語(実) | g17 ついて/追いついて、g20 調整される/する、g31 封鎖/ふささす、g33 引く/しく | TCM | SCG実行、Azure一致でPASS | 同じ | 救済。誤PASS 0 |
| 通常語・助詞(合成) | は->が | TCM | Azure 1回 | 同じ | 助詞追加除外はPhase 0で採用せず |
| 漢字近音(実) | 出演/出現(META) | TCM | SCG実行でPASS 3/3 | 同じ | OPEN-258の動機 |
| 固有名詞・カナ(実) | **g8 ガス->カス(+熟->じく)** | TCM | **NOT_APPLIED(entity_like_diff)** | SCG実行でPASS | 本件。NO_C1で救済 |
| 固有名詞・カナ(合成) | メダ->メタ(置換・濁点) | UNCERTAIN | 旧Cascade(Primary#2->Azure#1->#2、PHONETIC含めPASS) | Secondary 1回(PHONETIC不可なら厳格化) | 単独は元からSecondary確認 |
| 固有名詞・カナ(合成) | メタ->メタン(挿入) | TCM | **Azure実行**(C1除外にならない。辞書登録語なら`reading_dictionary_mismatch`で除外) | 同じ | C1の穴(挿入/脱落は対象外) |
| 固有名詞・漢字(合成) | 鈴木->薄木 | TCM | Azure 1回 | 同じ | 漢字固有名詞は元々C1対象外 |
| 固有名詞・漢字(合成) | 李->里(同読み) | PHONETIC_MATCH | Primary PASS | 同じ | 正しい漢字かは検査されない(既存の盲点) |
| 数値(合成) | 3->4 | TCM | NOT_APPLIED(number_mismatch) | NOT_APPLIED | 除外維持。実データではg36(20%/20パーセント)がPHONETIC |
| 否定(実) | g12 縛られず->縛られる | TCM | NOT_APPLIED(negation_marker_diff)。仮にAzureを呼んでもNG | NOT_APPLIED | Azure 0.18円/回を節約 |
| 否定(合成) | 来なかった->来た | TCM | **Azure実行**(マーカー対象外) | 同じ | ギャップ。Azureが逐語転写すればNGで安全。丸めると誤PASS |
| 否定(合成) | 行かない->行く | TCM | NOT_APPLIED(negation_mismatch) | NOT_APPLIED | 既存マーカー「ない」 |
| 時制(合成) | 終わった->終わる | TCM | Azure 1回 | 同じ | 時制専用ルールなし。Phase 0に時制の実サンプルなし |
| 同音異義(合成) | 市場(いちば/しじょう)の漢字違い | PHONETIC_MATCH | Primary PASS | 同じ | 読み一致=PASSで漢字の正誤は不問 |
| 同形異音(合成) | 試合に行った->試合を行った | TCM | Azure実行(C2は差分が助詞のため非該当) | 同じ | OPEN-263: 「行った」の候補が辞書に無く、diffが「行」自体でないとC2は発火しない |
| 同形異音(実) | g5 名所/名勝・旅程/旅亭 | TCM | NOT_APPLIED(C2) | Azure実行でもNG | 偶然C2で除外。C群は真の誤り |

## 6) 追加Trialの要否(提案のみ、実行せずSTOP)

不足している実測:
1. **濁点/半濁点の最小対でのAzure/Primary感度**(g8判断の根拠、G8_GAS_KASU_INVESTIGATION_01.md参照): 40クリップ、約9〜10円(TTS約4円+Azure約3.6円+Primary ASR約1円未満)。
2. **Human Reviewに回った実segmentの保存音声へのSCG再計算**(母集団での救済率): 該当26件の保存音声(存在する分)に対しAzure 1回ずつ。約3〜8円(音声秒数による。26件x最大3 attempt x平均2〜3秒x0.0444円/秒)。目的はHR率低減の母集団推定。
3. **時制・否定活用・同形異音語の実データ**(現状は合成のみ): 実運用TCMから該当する保存音声を抽出するoffline調査(¥0)で可能か先に確認。
4. **needs_listen 5音声の試聴確認**(ユーザー作業、費用0): 誤PASSの最終確定。試聴ページ `https://shimomura055.github.io/eigo-radio/user_test/open258_phase0_listen_01/index.html`(Phase 0当日HTTP 200確認)。

モデル名と最新性: Trial 1はTTS=現行Production標準(`gemini-3.1-flash-tts-preview`。最新モデル原則の例外として「測定対象がProduction経路そのもの」)、Primary=gpt-4o-mini-transcribe(Production固定)、Azure Speech STT ja-JP(SDK 1.50.0、japanwest)。最新かどうかは本調査で確認していない(実行前にFableが確認)。Trial 2はASRのみ(新規LLM/TTSなし)。いずれも**未実行**。

## 付録: 実行ログ要約

- 生成ファイル: `er056_ja_scg_offline_replay_01.py`(課金0、API呼出なし、Productionコード無変更)、`ja_offline_replay_01.json`。
- 追加確認(オフライン、Azureはmock): `evaluate_attempt_ja_with_cascade_detail` を g8 で実呼出 -> 現行=NOT_APPLIED / C1を外す仮想=PASS(G8_GAS_KASU_INVESTIGATION_01.md)。`er007_ja_scg_phase0_regression_test_01.py` 12件PASS。
- 合成ケースの経路確認一覧(再掲): `ja_offline_replay_01.json` の `synthetic_route_check`。
