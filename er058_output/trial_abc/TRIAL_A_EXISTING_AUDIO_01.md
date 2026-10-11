# TRIAL_A_EXISTING_AUDIO_01(既存音声のNG判定妥当性、2026-10-12、費用JPY 0・API呼出なし)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B Trial A。Trial限定・Production変更なし。
使ったもの: 既存の保存済みPrimary/Azure転写(attempt json、Phase 0 `results_01.jsonl`、`ja_offline_replay_01.json`)、既存の無料local whisper転写(`whisper_aux_01.json`、`local_wav_check_01.json`、`local_proxy_results_01.json`/`_medium_followup_01.json`)、既存validatorの純関数呼出(`classify_ja_asr_match`、Reading Resolver LLM OFF)。**新規のOpenAI/Azure/Gemini呼出は0回、新規local whisper実行も無し(既存転写のみ)**。script: `er058_trial_a_existing_audio_01.py`(表は `trial_a_tables_01.md`、日本語行データ `trial_a_ja_rows_01.json`)。
**限界**: 真のground truth(人間が聴いてどうか)は無い。ラベルは代理(whisper 2モデル/Azureの一致、META出演のユーザー試聴3件)。「未確定(要試聴)」は代理でも決められないもの。Azure転写は、日本語はPhrase Listなし(統一フロー想定どおり)、**英語の既存Azure転写はPhrase List付きで取得済み**(Phrase Listなしの転写は無い=注記。統一フローで「Phrase Listなし」にした場合の結果は未測定)。

## 0. 結論(先に)
1. **NG判定の多くは「真の誤読」ではなく Primary側のASR誤認 or Validatorの厳格さ**。日本語Phase 0(25音声)の統一フロー適用結果: 真の誤読の代理(C群5本)は**全て再生成(誤採用0)**、ユーザー試聴で正解確認済みのMETA 3本と正解の代理(whisper 2モデル+Azure一致)の音声は **Secondaryで採用(偽NGを救済)**。現行SCGと比べた差はg8(C1除外で再生成→統一フローでは採用)とg7(類似度<0.4除外→採用)の2件。
2. **g8(熟すと出るガス)**: 分類=**Primary側のASR誤認(ほぼ確定)+ルール設計(C1除外)による未救済**。Primaryは`熟す→じくす`+`ガス→カス`と転写したが、Azure(Phrase Listなし)・whisper small/medium が`熟すと出るガス`(濁音)で一致。Trial Bでも、Azureは`ガス/カス`・`バス/パス`・`ビル/ヒル`のいずれも逐語転写し原稿へ寄せなかった(3/3、`TRIAL_B_INTENTIONAL_MISREAD_01.md`)ので、g8のAzure PASSは「丸め」ではなく実際に`ガス`と聞こえた可能性が高い(試聴は任意)。
3. **needs_listen 5音声(g11a1/g18a2,a3/g1a1/g27)は未確定(要試聴)のまま**。Azure PASS、Primary/whisperの一部が原稿と不一致。Trial Bの結果(Azureが誤読形を概ね逐語転写する)は「Azure PASSなら原稿どおりである可能性」を支持するが証明ではない。統一フローではこの5本はSecondaryで**採用される**(現行SCGでも採用される)ので、誤りならそのまま通る。試聴(0円、ユーザー作業)で確定すべき。
4. **Coffee Standard part2 の5 attempt**: 統一フローなら #1 採用、#2 Primary NG→Secondary(Azure)未実施(localは両PASS=救済見込み)、#3 NG(Primary UNCERTAIN×2+Azure TCM×2、再生成)、#4 採用(forced Azure廃止)、#5 採用。**#5(LR後)はPrimary PASSで採用されるが、Azure・local smallが`raw bean`を`robbing`と転写しており、真の誤読の可能性が残る(未確定、要試聴)**。統一フローは「Primary PASS時にSecondaryを呼ばない」ため、この型のPrimary単独PASSの見逃しは防げない。
5. **「SecondaryのPASSを無条件に信頼して真の誤読を見逃す危険」**: Phase 0の真の誤読(C群5本)でSecondaryが誤PASSしたものは0(Azureは逐語転写)。Trial Bとあわせ、Secondary固有の原稿寄せ誤PASSは1件(`ja_voi5`、GT未確定)にとどまる。

## 1. A-2. Coffee Standard part2(英語、保存済み転写+既存local転写。Azureは既存=Phrase List付き)
(分類凡例: 真の誤読/ASR誤認/Validator不具合/retry制御不具合/未確定。出典: `en_asr_confirm_retry_redesign_01/FREE_VERIFICATION_01.md` 4-1/4-2、`ATTEMPT4_CONDITIONS_01.md` §1、attempt json、`local_wav_check_01.json`)
| TTS通算 | 音声 | Primary(記録) | Azure(既存、PL付き) | local small / medium | 原因分類 | 統一フローなら |
|---|---|---|---|---|---|---|
| #1 15:13 | 減速前初回 | NORMALIZED_MATCH=PASS。**NGの発生は6%減速後のPrimary-only再検証UNCERTAIN(本文未保存)** | 未実施 | NORMALIZED / UNCERTAIN(`People`脱落+`U.S.`) | **retry制御/設計不具合 + ASR誤認**: 減速前はPASS、減速後の再検証が単独ASRのUNCERTAINで破棄された(減速音声をlocal small再現ではNUMERIC_EQUIVALENCE_MATCH=PASS) | **採用(Primary PASS)**。減速後再検証をどう扱うかは別問題(未決) |
| #2 15:16 | 標準1回目 | TRUE_CONTENT_MISMATCH(`showed→show`+`us→u s`)=NG | **未実施**(cascadeが走らず) | NORMALIZED / NORMALIZED(両方`showed coffee cost`) | **ASR誤認(Primary)の可能性が高い(偽NG)**。ただし`showed`か`show`かは**未確定(要試聴、8-3-B)** | Primary NG → Secondary(Azure)の結果が無いため**判定不能**(local 2モデルがPASSなので救済された見込み) |
| #3 15:18 | 標準2回目 | UNCERTAIN ×2(`us→u s`×3のみ、entity-like=capitalized) | TCM ×2(`raw bean→robbing`、`appear`脱落、`us→u s`) | NORMALIZED / NORMALIZED | Primary: **Validator不具合(仕様どおりの偽NG、F-5/OPEN-272: US→U.S.+cost→costs同時でdespace等価が崩れる)**。Azure(PL付き): **ASR誤認**(local 2モデルとも原稿一致、かつ他のAzure NGと異なり転写が不安定) | **NG→再生成**(Primary UNCERTAIN、Azure TCMの両NG。ただしこの Azure は Phrase List付き。Phrase Listなしでは結果が変わるかは未測定) |
| #4 15:31 | fallback | NUMERIC_EQUIVALENCE_MATCH=PASS | forced TCM(転写欠落) | NORMALIZED / NORMALIZED | **retry制御不具合 + Azure側ASR誤認**: PrimaryがPASSなのにforced-SecondaryのNGで不採用(forced Secondary廃止が統一フローの方針) | **採用(Primary PASS)** |
| #5 15:35 | Local Rewrite後の再TTS(最終) | NORMALIZED_MATCH=PASS | forced TCM(`raw bean→Robbing`) | **TCM(`robbing`)** / NORMALIZED | **未確定(要試聴)**: 4系統中2系統(Azure、local small)が`robbing`と聴く。Trial Bでは`raw bean→robin/robbing`の誤読を全ASR(Primary/Azure/local)が逐語で検出できたため、Azure/smallの`robbing`は**真の誤読の可能性を排除できない** | **採用(Primary PASS)**。Primary単独PASSのため、真の誤読なら**見逃し** |
読み取り: (1) Coffee part2のNG 5件のうち、真の誤読と確定できたものは**0件**。(2) #2/#3/#4は別系統ASRが原稿一致=偽NG(Primary側ASR誤認/Validator仕様/Azure誤認)の可能性が高く、#5だけが真の誤読の可能性が残る。(3) **統一フローは偽NGを減らす(#4の不採用が解消)が、#5型のPrimary PASS見逃しを防げない**。(4) 「Primary PASSなら Secondaryを呼ばない」設計は、Primary誤PASSをSecondaryが拾える機会を捨てる(Primary PASSの標本監査=local mediumは良品の32.5%をNGにするため単独では使えない、FREE_VERIFICATION 4-8)。

## 2. 表(自動生成、`trial_a_tables_01.md`の転記)
### A-1. 日本語 Phase 0 25音声(統一フロー適用。Azureは保存済み転写=Phrase Listなし)
統一フロー判定 = Primary PASSなら採用 / Primary NGでAzure PASSなら採用 / 両NGなら再生成。現行(CURRENT)は SCG除外(C1等)でAzureを呼ばない場合があるため、現行結果も併記(replay JSONの値)。

| key | GT代理 | 原稿 | Primary転写→判定 | Azure転写→判定 | whisper small/medium | 統一フロー | 現行(CURRENT) | NG原因分類 |
|---|---|---|---|---|---|---|---|---|
| g35_japanese_title_a1 | correct_user | AIの電話に人間が出演。問題は「キャスト変更」のお知らせでし | AIの電話に人間が出現。問題は、キャスト変更のお知らせでした [NG:TRUE_CONTENT] | AIの電話に人間が出演。問題はキャスト変更のお知らせでした。 [PASS:NORMALIZED_M] | 不一致/不一致 | 採用(Secondary) | PASS | Primary側のASR誤認(ユーザー試聴で出演を確認済み=偽NG) |
| g35_japanese_title_a2 | correct_user | AIの電話に人間が出演。問題は「キャスト変更」のお知らせでし | AIの電話に人間が出現。問題は、キャスト変更のお知らせでした [NG:TRUE_CONTENT] | AIの電話に人間が出演。問題はキャスト変更のお知らせでした。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(ユーザー試聴で出演を確認済み=偽NG) |
| g35_japanese_title_a3 | correct_user | AIの電話に人間が出演。問題は「キャスト変更」のお知らせでし | AIの電話に人間が出現、問題はキャスト変更のお知らせでした。 [NG:TRUE_CONTENT] | AIの電話に人間が出演。問題はキャスト変更のお知らせでした。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(ユーザー試聴で出演を確認済み=偽NG) |
| g12_kp1_ja_aoede_a2 | error_proxy | しばられず自由になれる感じの | 縛られる、自由になれる感じの。 [NG:TRUE_CONTENT] | 縛られる。自由になれる感じの。 [NG:TRUE_CONTENT] | 不一致/不一致 | NG(再生成) | Azure不呼出(除外:negation | 真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致) |
| g3_kp4_ja_charon_a1 | error_proxy | 体内時計 | 体内毒行 [NG:TRUE_CONTENT] | 体内どこ。 [NG:TRUE_CONTENT] | 不一致/不一致 | NG(再生成) | NG | 真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致) |
| g4_kp2_ja_charon_a1 | error_proxy | 証拠だと受け取られる | 証拠がと受け取られる。 [NG:TRUE_CONTENT] | 証拠が？と受け取られる。 [NG:TRUE_CONTENT] | 不一致/不一致 | NG(再生成) | NG | 真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致) |
| g5_kp4_ja_charon_a1 | error_proxy | 名所を中心にした旅程 | 名勝を中心にした旅亭。 [NG:TRUE_CONTENT] | 名称を中心にした料亭。 [NG:TRUE_CONTENT] | 不一致/不一致 | NG(再生成) | Azure不呼出(除外:heteroph | 真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致) |
| g6_kp5_ja_charon_a1 | error_proxy | 形になり始める | 形に始める [NG:TRUE_CONTENT] | 形に始める。 [NG:TRUE_CONTENT] | 不一致/不一致 | NG(再生成) | NG | 真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致) |
| g2_kp2_ja_charon_a1 | correct_strong | においを出す | においを断つ。 [NG:TRUE_CONTENT] | 匂いを出す。 [NG:PHONETIC_MAT] | 一致/一致 | NG(再生成) | NG | Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致) |
| g8_kp4_ja_charon_a1 | correct_strong | 熟すと出るガス | じくすと出るカス。 [NG:TRUE_CONTENT] | 熟すと出るガス。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | Azure不呼出(除外:entity_l | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g11_kp5_ja_aoede_a1 | needs_listen | 理屈の上では | 肉の上では [NG:TRUE_CONTENT] | 理屈の上では。 [PASS:NORMALIZED_M] | 不一致/一致 | 採用(Secondary) | PASS | 未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致 |
| g11_kp5_ja_aoede_a2 | correct_strong | 理屈の上では | リクスの上では [NG:TRUE_CONTENT] | 理屈の上で。 [NG:TRUE_CONTENT] | 一致/一致 | NG(再生成) | NG | Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致) |
| g17_kp5_ja_charon_a1 | correct_strong | 最新のニュースについていく | 最新のニュースに追いついていく。 [NG:TRUE_CONTENT] | 最新のニュースについていく。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g20_kp2_ja_charon_a1 | correct_strong | クリックを集めるように調整される | クリックを集めるように調整する。 [NG:TRUE_CONTENT] | クリックを集めるように調整される。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g21_comment_3_a1 | correct_strong | 世界市場の価格は下がりましたが、米国のコーヒー価格は前年同月 | 世界市場の価格は下がりましたが、米国のコーヒー価格は前年同月 [NG:TRUE_CONTENT] | 世界市場の価格は下がりましたが、米国のコーヒー価格は前年同月 [NG:PHONETIC_MAT] | 一致/一致 | NG(再生成) | NG | Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致) |
| g23_meaning_2_a1 | correct_probable | 焙煎前のコーヒー豆 | 買いせまいのコーヒー豆。 [NG:TRUE_CONTENT] | 焙煎米のコーヒー豆。 [NG:TRUE_CONTENT] | 一致/一致 | NG(再生成) | NG | Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致) |
| g27_kp1_ja_charon_a1 | needs_listen | 上がった分をいったん吐き出す | 上がった分を一旦履きます。 [NG:TRUE_CONTENT] | 上がった分をいったん吐き出す。 [PASS:NORMALIZED_M] | 一致/不一致 | 採用(Secondary) | PASS | 未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致 |
| g31_meaning_2_a1 | correct_strong | 海を封鎖すること | 海をふささすること。 [NG:TRUE_CONTENT] | 海を封鎖すること。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g33_meaning_5_a1 | correct_strong | 目を引く | 目をしく。 [NG:TRUE_CONTENT] | 目を引く。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g33_meaning_5_a2 | correct_strong | 目を引く | 目をしつ [NG:TRUE_CONTENT] | 目を引く。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | PASS | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |
| g36_comment_1_a1 | correct_strong | まず、20％という計画が発表されたあと、支払い方法など何がま | まず、20パーセントという計画が発表された後、支払い方法など [NG:TRUE_CONTENT] | まず、 20%という計画が発表された後、支払い方法など何がま [NG:PHONETIC_MAT] | 一致/一致 | NG(再生成) | NG | Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致) |
| g18_meaning_2_a2 | needs_listen | 拒絶されたように感じる | 強制されたように感じる。 [NG:TRUE_CONTENT] | 拒絶されたように感じる。 [PASS:NORMALIZED_M] | 不一致/一致 | 採用(Secondary) | PASS | 未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致 |
| g18_meaning_2_a3 | needs_listen | 拒絶されたように感じる | 強制されたように感じる。 [NG:TRUE_CONTENT] | 拒絶されたように感じる。 [PASS:NORMALIZED_M] | 不一致/一致 | 採用(Secondary) | PASS | 未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致 |
| g1_meaning_4_a1 | needs_listen | 活動し続ける | 活動をし続ける。 [NG:TRUE_CONTENT] | 活動し続ける。 [PASS:NORMALIZED_M] | 不一致/一致 | 採用(Secondary) | PASS | 未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致 |
| g7_meaning_4_a1 | correct_strong | 湿度 | 死図塔 [NG:TRUE_CONTENT] | 湿度。 [PASS:NORMALIZED_M] | 一致/一致 | 採用(Secondary) | Azure不呼出(除外:similari | Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG) |

統一フロー結果 x GT代理(件数):

| GT代理 | 採用(Primary) | 採用(Secondary) | NG(再生成) |
|---|---|---|---|
| correct_user | 0 | 3 | 0 |
| correct_strong | 0 | 7 | 4 |
| correct_probable | 0 | 0 | 1 |
| needs_listen | 0 | 5 | 0 |
| error_proxy | 0 | 0 | 5 |

### A-3. 英語 他NG segment 20本(Standard/Advanced の Primary NG 保存音声、Azure転写は保存されていないためlocal small/mediumのみ=Secondary代理)

| segment | Primary種別 | local small | local medium | 統一フローでSecondary(代理)がPASSなら | 原因分類 |
|---|---|---|---|---|---|
| full_story_part1 | CONTENT_WORD_NONENTITY | NG | PASS | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part3 | CONTENT_WORD_NONENTITY | PASS | NG | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part2 | PASS | PASS | 未実施 | (ASRは対象外) | ASR以外のgate由来(Primary再判定ではPASS: 長さ/Repetition QA/Disfluency QA等) |
| full_story_part1 | CONTENT_WORD_NONENTITY | NG | PASS | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part3 | CONTENT_WORD_NONENTITY | PASS | NG | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part2 | CONTENT_WORD_NONENTITY | NG | NG | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| full_story_part1 | NUM_OR_NEGATION | NG | 未実施 | NG(再生成) | 真の誤読の可能性高(数値/否定、local NG なら) |
| full_story_part1 | NUM_OR_NEGATION | NG | 未実施 | NG(再生成) | 真の誤読の可能性高(数値/否定、local NG なら) |
| full_story_part1 | NUM_OR_NEGATION | NG | 未実施 | NG(再生成) | 真の誤読の可能性高(数値/否定、local NG なら) |
| full_story_part1 | NUM_OR_NEGATION | NG | 未実施 | NG(再生成) | 真の誤読の可能性高(数値/否定、local NG なら) |
| full_story_part2 | ENTITY_ONLY | NG | 未実施 | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| full_story_part3 | ENTITY_ONLY | NG | 未実施 | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| full_story_part3 | ENTITY_ONLY | NG | 未実施 | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| preview | OTHER_LOW_SIMILARITY | PASS | PASS | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part3 | PASS | PASS | 未実施 | (ASRは対象外) | ASR以外のgate由来(Primary再判定ではPASS: 長さ/Repetition QA/Disfluency QA等) |
| full_story_part3 | CONTENT_WORD_NONENTITY | PASS | NG | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| in_one_line | ENTITY_ONLY | NG | 未実施 | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| comment_2 | ENTITY_ONLY | NG | 未実施 | NG(再生成) | 未確定(要試聴): 別系統ASRも原稿不一致 |
| comment_3 | CONTENT_WORD_NONENTITY | NG | PASS | 採用(救済) | Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致) |
| full_story_part1 | PASS | NG | 未実施 | (ASRは対象外) | ASR以外のgate由来(Primary再判定ではPASS: 長さ/Repetition QA/Disfluency QA等) |

原因分類件数: Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致)=7, ASR以外のgate由来(Primary再判定ではPASS: 長さ/Repetition QA/Disfluency QA等)=3, 未確定(要試聴): 別系統ASRも原稿不一致=6, 真の誤読の可能性高(数値/否定、local NG なら)=4

## 3. 読み取りと分類サマリ
**日本語Phase 0(25音声)の分類(件数)**: Primary側のASR誤認(偽NG) 10(ユーザー試聴で出演確認のg35 3本+Azure・whisper 2モデルが原稿一致の7本[g8、g17、g20、g31、g33a1、g33a2、g7])、Validator厳格/表記差/Azure側誤認でNGのまま 5(g2・g21・g36はAzureがPHONETIC_MATCH[匂い/におい、20%/20パーセント等]で現行SCGの厳格方針によりNG、g11a2はAzureが助詞を落とした「理屈の上で」=Secondary側のASR誤認、g23はPrimary/Azureが同一の誤聴でwhisper 2モデルのみ原稿一致)、真の誤読(代理) 5(g12、g3、g4、g5、g6。統一フローでも全て再生成=誤採用0)、未確定(要試聴) 5(needs_listen)。
- **統一フローと現行SCGの差は2件のみ**: g8(C1除外→採用)、g7(類似度<0.4除外→採用。Primary `死図塔`/Azure `湿度`、whisper 2モデル原稿一致)。誤読の代理(C群5)の誤採用は0のまま。
- **g8(ガス/カス)はTrial Bの結果と整合**: Azureは濁点の誤読を丸めない(ガス→カス、バス→パス、ビル→ヒルの3/3でAzure/Primary/localとも誤読形をそのまま転写)。
- **needs_listen 5件の試聴ポイント**(0円、ユーザー作業、URLは`RECONCILIATION_REPORT_02.md` 8-3-B): g11a1(理屈の上では/肉の上では)、g27(吐き出す/履きます)、g18a2・a3(拒絶された/強制された)、g1a1(活動し続ける/活動をし続ける)。いずれもAzure「原稿」・Primary「別語」。聴いて原稿どおりなら全て偽NG(Primaryの誤認)、別語なら**Azure PASS誤採用**=統一フローの重大な穴。

**英語 他NG segment(A-3、Azure転写が保存されていないためlocal small/mediumをSecondary代理)**: 20本のうち、別系統ASR(local)が原稿一致=Primary側ASR誤認またはValidator厳格(偽NG)の可能性 7(Primary内容語差6+低類似度1。ただし local small は良品の32.5%をNGにするので単独では弱い)、数値・否定でlocalも不一致=真の誤読の可能性が高い 4(全て Hormuz full_story_part1)、entity-only/内容語でlocalも不一致=未確定(要試聴) 6、Primary再判定ではPASS(ASR以外のgate=長さ/Repetition QA等で不採用) 3。**ASR起因のPrimary NG 17本のうち約4割(7本)が別系統ASRで原稿一致**=Secondaryの救済余地は主に内容語差型(FREE_VERIFICATION 4-8と一致)で、数値・否定はlocalでも救済されない(真の誤読と整合)。

## 4. 統一フローの観点での評価
- **偽NG救済力**: Phase 0日本語の正解音声(代理、母数15)のうち、統一フローで採用された数は 10/15(試聴確認3+whisper/Azure一致7)、現行SCGは8/15(g8・g7が除外で未救済)。偽NGで再生成される無駄を減らせるのは、**Secondary(PHONETIC_MATCH非許容)をC1/類似度除外なしで呼ぶ**ことによる。
- **見逃しリスク**: 真の誤読(代理)でSecondaryが誤PASSした例は Phase 0 の5本で0、ただし**needs_listen 5本は未確定**で、ここに誤読があれば統一フロー(と現行SCG)の見逃し。Trial Bで見つかった「全ASRが原稿形に丸める型」(英語-ed/-s・固有名詞・同形異音、日本語の一部濁点/カタカナ)は、Primary/Secondaryどちらでも拾えない(`TRIAL_B_INTENTIONAL_MISREAD_01.md`)。
- **Validator/retry制御の不具合**(確定): (a) F-5(US→U.S.+cost→costs同時でUNCERTAIN、#3)、(b) forced-Secondary(Primary PASS後のAzure NGで不採用、#4)、(c) 減速後Primary単独再検証のUNCERTAIN破棄(#1)、(d) LRのNG span選定がPrimary転写`us/u s`に基づき、Azure NGの実箇所(`raw bean`)と別(OPEN-274、#5)。いずれも新規発見ではなく既存OPEN項目の再確認。
- 新たな仕様候補の発見は無し(上記は既存の指摘の再確認。Production変更なし)。
