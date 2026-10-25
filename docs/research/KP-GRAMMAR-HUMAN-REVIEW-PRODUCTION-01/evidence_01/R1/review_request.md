# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=a2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1/a2/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `aee57d7c858dceb5` / 本文sha: `07a0efc7f1d6`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | put in place | 導入する | tariffs put in place during summer raised the price of the beans themselves |  |  |
| 2 | KP | pass through | 先へと伝わる | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain |  |  |
| 3 | KP | futures price | 先物価格 | In February, before summer, New York's Arabica coffee futures price reached a record high |  |  |
| 4 |  | reach a record high | 過去最高に達する | In February, before summer, New York's Arabica coffee futures price reached a record high | 価格などが過去最高に達する際の定番表現。 |  |
| 5 |  | Turn Back the Clock | 過去にさかのぼる | The Coffee Price Rise Case: Turn Back the Clock on the Price Tag | 過去にさかのぼることを表す慣用句。 |  |
| 6 |  | supply chain | 商品が消費者に届くまでの供給の流れ | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain | 供給網を指す経済・ビジネス分野の重要語。 |  |
| 7 |  | play a part | 一役を買う | They did play a part | 何かの一因・役割を担うことを表す熟語。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level a2 --accept-ai --candidates-sha aee57d7c858dceb5c9160c113c1127cf8bdf52864044d04a4e8c8165c3d3fe74 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=b1b)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1/b1b/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `3e6a716bdd312ca8` / 本文sha: `2e58952fc33a`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | off the hook | 責任を問われずに済む | So, are tariffs off the hook |  |  |
| 2 | KP | all-time high | 史上最高 | Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high |  |  |
| 3 | KP | make its way through | 段階を追って伝わる | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid |  |  |
| 4 | 単語 | jump to conclusions | 早まって結論を出す | No, that would be jumping to conclusions too | 根拠が不十分なまま結論を急ぐことを表す慣用表現。 |  |
| 5 | 単語 | Turn Back the Clock | 時間をさかのぼる | The Coffee Price Hike Case: Turn Back the Clock on the Price Tag | 過去に戻る、または時間を巻き戻すという定番の比喩表現。 |  |
| 6 |  | futures price | 先物価格 | Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high | 先物取引で用いられる価格を指す金融用語。 |  |
| 7 |  | year over year | 前年の同じ時期と比べて | price of ground coffee rose 41% year over year, mostly because of earlier bean shortages and higher bean costs | 前年同期比を示す経済・ビジネス分野の表現。 |  |
| 8 |  | supply chain | 商品を作って届けるまでの一連の流れ | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid | 供給網を意味する、ビジネスで頻出の重要語。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level b1b --accept-ai --candidates-sha 3e6a716bdd312ca8571944efb2acf6e5f8f2c94f0598cb45670c7406a8ea4808 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1/b1b/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `fd174998eadcda8c` / 本文sha: `02c33a41d4a3` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

## AI推奨(TOP1): 候補1 [T1 / HEAVY] 段落P4

> Hopes that the next harvest would recover had also faded.

- 構文: that節を含む長い主語
- 教える価値: 名詞を説明するthat節の後ろに主節の動詞が続くと見抜く。
- 読み違えやすい点: that節内のwould recoverを主節の動詞と取り、had also fadedを見落とすことがある。

## TOP2: 候補2 [T1 / SPEC] 段落P9

> Coffee may be bitter, but we want our detective work to be clear.

- 構文: want＋目的語＋to不定詞
- 教える価値: want＋目的語＋to不定詞では、目的語がto不定詞の意味上の主語にもなると読む。
- 読み違えやすい点: our detective workをto be clearの意味上の主語として捉えず、後続の不定詞との関係を切ってしまうことがある。

## 操作(コマンド。`--by` は操作者名)

- AI推奨(TOP1)を了承: `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --candidates-sha fd174998eadcda8c3dece2c6a5262c4cc1cce8eab7ebfdbd246b64edb6a72761 --by <名前> --choice top1 --accept-ai`
- TOP1を選ぶ: `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --candidates-sha fd174998eadcda8c3dece2c6a5262c4cc1cce8eab7ebfdbd246b64edb6a72761 --by <名前> --choice top1`
- TOP2を選ぶ(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --candidates-sha fd174998eadcda8c3dece2c6a5262c4cc1cce8eab7ebfdbd246b64edb6a72761 --by <名前> --choice top2 --reason <理由>`
- 選び直し(TOP1/TOP2をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --candidates-sha fd174998eadcda8c3dece2c6a5262c4cc1cce8eab7ebfdbd246b64edb6a72761 --by <名前> --choice reselect --reason <理由>`
- 今回は解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --candidates-sha fd174998eadcda8c3dece2c6a5262c4cc1cce8eab7ebfdbd246b64edb6a72761 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。

