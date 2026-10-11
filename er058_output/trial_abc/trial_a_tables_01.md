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