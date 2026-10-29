# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=a2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/a2/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `1b65418d4120c7d0` / 本文sha: `49e80412534f`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | equivalent width | 光の線の特徴を表す幅 | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 天文学で線の強さを示す専門用語。 |  |
| 2 | KP | a lower limit | 下限 | That absence helped set a lower limit for its equivalent width, but more observations are needed to find its source | 定量的な下限を示す学術的な表現。 |  |
| 3 | KP | narrow down the source | 発生源を絞り込む | The empty space had become a clue that could help narrow down the source | 候補や範囲を絞り込む句動詞表現。 |  |
| 4 | 単語 | turn the usual steps around | いつもの手順を逆にする | But this time, researchers turned the usual steps around | 手順を逆転させる意味の慣用的な言い方。 |  |
| 5 | 単語 | line's absence from images | 画像に光の線が写っていないこと | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 画像に線が見られないことを表す科学的表現。 | 重複(アラームのみ・選んでも止まりません): 11 |
| 6 |  | wavelength | 波長 | They looked for lines of light at a certain wavelength | 光の波長を表す科学分野で汎用性の高い語。 |  |
| 7 |  | estimate | およその値を出す | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 数量や価値を推定する際に幅広く使われる語。 |  |
| 8 |  | investigation | 調査 | Then the investigation took an unexpected turn | 調査や捜査を指し、幅広い文脈で使える語。 |  |
| 9 |  | frustrate | いら立たせる | This kind of mystery could frustrate any detective | 期待や計画を妨げ、いら立たせる意味の動詞。 |  |
| 10 |  | overlap | 一部が重なる | In the area they studied, they closed small windows that overlapped with some known space objects | 重なり合うことを示す動詞の過去形。 |  |
| 11 |  | show up | 現れる | The fact that it "doesn't show up" became evidence | 「現れる・目に見える」の意味で使う句動詞です。 | 重複(アラームのみ・選んでも止まりません): 5 / 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- limited the search to : canonicalization_qa : 救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)。検査未了の候補は提示しない=fail-closed

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --accept-ai --candidates-sha 1b65418d4120c7d0ed457183bea5ccaaae6bafb32c02e30869584918aaedffe6 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=b1b)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/b1b/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `7f0bc16d183feb7d` / 本文sha: `33ec46beb6f1`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | equivalent width | スペクトル線の強さを示す等価幅 | The authors used the line's absence from the images to estimate that its "equivalent width," a measure of the line's features, was at least 7,620 Å | 輝線の強さを表す天文学の専門用語。 |  |
| 2 | KP | narrow down the source | 発生源を絞り込む | The blank space had become a clue that could help narrow down the source | 候補を絞り込む句動詞の使い方が学べる。 |  |
| 3 | KP | set a lower limit | 下限を決める | That absence helped researchers set a lower limit on the line's equivalent width, but more observations are needed to identify its source | 研究で下限値を設定する際の定型表現。 |  |
| 4 | 単語 | take an unexpected turn | 思わぬ展開になる | Then the investigation took an unexpected turn | 予想外の展開になるという慣用表現。 |  |
| 5 | 単語 | point-like object | 点のように見える物体 | But when they checked its position in a deep image, they could not find a matching point-like object | 点状天体を表す天文学の専門表現。 |  |
| 6 |  | wavelength | 波長 | They searched for lines of light that appear at a particular wavelength | 光の波長を表す専門語で、科学文脈で広く使われます。 |  |
| 7 |  | celestial | 天体の | In the area they observed, they closed small windows that overlapped with some celestial objects already known, while leaving almost all the others open | 天体や天空に関する対象を表す、汎用性のある語です。 |  |
| 8 |  | absence | 見当たらないこと | The authors used the line's absence from the images to estimate that its "equivalent width," a measure of the line's features, was at least 7,620 Å | 「不在・欠如」を表し、抽象的な文脈でも使えます。 |  |
| 9 |  | investigation | 調査 | But this time, the researchers have turned the usual steps of the investigation upside down | 調査や捜査を意味し、幅広い話題で使える語です。 |  |
| 10 |  | frustrate | いら立たせる | A mystery like this, enough to frustrate any detective, has appeared in space | 期待や目的を妨げ、いら立たせる意味を持つ動詞です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --accept-ai --candidates-sha 7f0bc16d183feb7dafcfe820c3d6f2f8fcba476ce8d1ced95f59caa112d3cecd --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/a2/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `0509a3359f0dac6d` / 本文sha: `91e34de1c56c` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 比較基準が省略された比較級 [T1 / CMP] 段落P8  (評価順位1 / id: `gd5b0fc2d0f`)

> How much closer will the next observation bring us to the source of this voice?

- 教える価値: 比較級の基準が明示されない場合、文脈から現在の状態など比較対象を補って読む。
- 読み違えやすい点: closerの比較の基準が明示されていないため、何と比べてどれほど近づくのかを補わずに読む可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
次の観測で、この声の源にどれほど近づくのだろうか。

【文法・構文の仕組み】
**closer** は **close**（近い）の比較級で、「より近く」という意味です。比較級は通常、何と比べているかを **than ...** などで示しますが、この文では比較の基準が明示されていません。現在の状態などを基準にして「より近くなる」と読むことができます。

**How much closer** は「どれほど近く」という程度を尋ねる表現です。**will the next observation bring us** は「次の観測が私たちを連れていくのか」という意味で、**to the source of this voice** が「この声の源へ」という到達点を示しています。

【意味・ニュアンス・表現効果】
この問いは、次の観測によって、この声の源にどれくらい近づけるのかを尋ねています。比較の基準をあえて明示せず、次の観測で得られる進展の程度に焦点を当てています。

## Top2: 長い動名詞句主語 [T1 / HEAVY] 段落P5  (評価順位2 / id: `g3595e0b388`)

> Not seeing something in an image does not mean it does not exist.

- 教える価値: 動名詞句に目的語や修飾語が続くときは、その句全体を主語として捉えてから定動詞を探す。
- 読み違えやすい点: somethingを主語と取り違え、動名詞句全体がdoes not meanの主語であることを見落とす可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
画像の中に何かが見えないからといって、それが存在しないということにはならない。

【文法・構文の仕組み】
文頭の **Not seeing something in an image** が、ひとまとまりの主語です。動名詞 **seeing** に **Not** がつき、「画像の中に何かが見えないこと」を表しています。

主節の動詞は **does not mean** です。その後ろの **it does not exist** は、「それが存在しないということ」を表し、**mean** の内容を説明しています。つまり、「画像で見えないこと」が「存在しないこと」を意味するわけではない、という構造です。

【意味・ニュアンス・表現効果】
「見えない」と「存在しない」を同じこととして扱わないようにする表現です。直前では、目に見える形のない宇宙の物体を発見したと言うにはまだ早いと述べられています。この文は、画像に何かが写っていないように見えても、それだけで対象が存在しないとは判断できない、という考えを示しています。

(他1件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --candidates-sha 0509a3359f0dac6dbb94fa7d8911e33b55826511ed71c01e3637271b66eb7be8 --by <名前> --choice pick --ids gd5b0fc2d0f --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --candidates-sha 0509a3359f0dac6dbb94fa7d8911e33b55826511ed71c01e3637271b66eb7be8 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --candidates-sha 0509a3359f0dac6dbb94fa7d8911e33b55826511ed71c01e3637271b66eb7be8 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --candidates-sha 0509a3359f0dac6dbb94fa7d8911e33b55826511ed71c01e3637271b66eb7be8 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/b1b/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `430f7657dff3fc8a` / 本文sha: `67c441f2da96` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文 [T1 / CLEFT] 段落P5  (評価順位1 / id: `gfb62c90903`)

> What they could not confirm was an image showing an object at the line’s position.

- 教える価値: Whatで始まる節をひとまとまりの主語として読み、wasの後ろに主語の内容が示される形を捉える。
- 読み違えやすい点: Whatで始まる節が主語であることを捉えられず、疑問文のように読み違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】  
彼らが確認できなかったのは、線の位置に物体が写っている画像だった。

【文法・構文の仕組み】  
この文は疑似分裂文です。文頭の **What they could not confirm** が主語で、「彼らが確認できなかったもの」という意味です。ここでの **what** は「何を」ではなく、「〜するもの・こと」を表しています。

**was** は主語とその内容を結びつける動詞で、その後ろの **an image showing an object at the line’s position** が「確認できなかったもの」の内容を示します。**showing an object at the line’s position** は **an image** を説明し、「線の位置に物体が写っている画像」という意味になります。

【意味・ニュアンス・表現効果】  
この形では、「彼らが確認できなかったものは何か」という点に焦点が当たっています。前の文では、画像に写っていないことと、物体が存在しないことは同じではないと述べられています。その流れを受けて、この文は、彼らが確認できなかったのは「線の位置に物体が写った画像」だったと説明しています。

## Top2: 比較基準が明示されていない比較級 [T1 / CMP] 段落P8  (評価順位2 / id: `gff55c88292`)

> How much closer will the next observation get us to the source of this voice?

- 教える価値: 比較級では、比較の基準が明示されているか文脈から補う必要があるかを確認する。
- 読み違えやすい点: closerが何を基準にした比較なのかを補えず、どの程度近づくことを尋ねているのか取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
次の観測によって、この声の源にどれほど近づけるのだろうか。

【文法・構文の仕組み】
「closer」は「近い」を表す「close」の比較級で、「より近く」という意味です。「How much」はその比較級にかかり、「どれほど近く」を表します。

「will the next observation get us ...?」は「次の観測は私たちを…の状態にするだろうか」という形です。「get us」の後に「closer to the source of this voice（この声の源により近い状態）」が続いています。比較の基準、たとえば「今より」や「前回の観測より」は文中に明示されていません。

【意味・ニュアンス・表現効果】
「How much closer」と尋ねることで、次の観測で近づけるかどうかだけでなく、どの程度近づけるのかに焦点が置かれています。前の文「But it may not include everything in the universe.」に続き、次の観測によって声の源にどれほど近づけるのかを問うています。

(他5件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --candidates-sha 430f7657dff3fc8a13602413d39413e3ca49a9f0fb52eccba73d012ec75cf2da --by <名前> --choice pick --ids gfb62c90903 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --candidates-sha 430f7657dff3fc8a13602413d39413e3ca49a9f0fb52eccba73d012ec75cf2da --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --candidates-sha 430f7657dff3fc8a13602413d39413e3ca49a9f0fb52eccba73d012ec75cf2da --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --candidates-sha 430f7657dff3fc8a13602413d39413e3ca49a9f0fb52eccba73d012ec75cf2da --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。

---
## ニュアンス解説(level=a2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/a2/study_text/nuance_human_review_request.md)

# ニュアンス解説 Human Review 依頼

- level: a2(Standard) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_a908f53870b003fe / candidate_sha256: a908f53870b003fee04fed613dbebcacd6fde0a931b3e2d4f430395fb2545f04

## could not confirm
- 本文の英文: They could not confirm that an image showed an object where the line was.
- 日本語訳: 画像が、光の線があった場所に天体を示しているとは確認できませんでした。
- ポイント: 「確認できない」と「存在しないと確認した」の区別

解説(全文):
could not confirm that ... は「…ではないと確認した」ではなく、「…だと確かめられなかった」という意味です。否定されているのは確認できたということ自体で、対象が存在しないとは断定していません。たとえば They confirmed that no object was there. なら「そこに天体がないと確認した」です。本文では、画像で確認できないことと、存在しないことを慎重に区別しています。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --choice adopt|reject --candidates-sha a908f53870b003fee04fed613dbebcacd6fde0a931b3e2d4f430395fb2545f04 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`

---
## ニュアンス解説(level=b1b)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/b1b/study_text/nuance_human_review_request.md)

# ニュアンス解説 Human Review 依頼

- level: b1b(Advanced) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_ec3ed9c3569671f3 / candidate_sha256: ec3ed9c3569671f32eb4d1cbdf6ab599c6ef9d8f46f5cdcf1a5ade5daf4ec966

## too soon to announce
- 本文の英文: Even so, it was too soon to announce, “A celestial object with no visible form has been found!”
- 日本語訳: それでも、「目に見える形のない天体が見つかった」と発表するには時期尚早だった。
- ポイント: 「時期尚早」が、現時点での証拠への慎重さを示す

解説(全文):
ここでの too soon は、発表する能力がないという意味ではなく、今ある証拠だけで結論を公表するのは早すぎる、という慎重な判断を示します。たとえば could not announce なら「発表できなかった」と、能力や事情による不可能さにも聞こえます。too soon は「今はまだ早いが、今後なら発表できるかもしれない」という余地を残します。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --choice adopt|reject --candidates-sha ec3ed9c3569671f32eb4d1cbdf6ab599c6ef9d8f46f5cdcf1a5ade5daf4ec966 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`

