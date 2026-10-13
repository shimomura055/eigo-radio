# gloss_check_03 (委任_03、G運用: kp_extends_beyond_candidate=true のitemのja_gloss整合確認)

対象: Coffee Std(a2) Key Phrase canonicalization結果(CANONICALIZATION_PASS、M2 fallbackなし、費用 JPY0.76)。
証跡: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2/key_phrases/keywords_canonicalized.json`、
`.../canonicalization_runtime_metadata.json`、`.../scaffold_kp_std_d05_stdout.log`。

| rank | display_phrase | 候補span | A'窓 | 確定KP | ja_gloss(表示) | ja_gloss_tts | kp_extends_beyond_candidate |
|---|---|---|---|---|---|---|---|
| 1 | pump one's fist | pumps its fist | - | pump one's fist | 大喜びする | 大喜びする | false |
| 2 | raw bean | raw-bean | raw-bean prices take at least | raw bean | 生豆 | 生豆 | false |
| 3 | right away | right away | - | right away | すぐに | すぐに | false |
| 4 | based on | based on | based on interviews | **based on interviews** | **～をもとにした** | **なになにをもとにした** | **true** |
| 5 | take time | take time | - | take time | 時間がかかる | 時間がかかる | false |

## 伸びたitem 1件の整合判定(原文照合)
- 原文: `However, "about nine months" is an estimate based on interviews`
- 候補 `based on`(gloss `～をもとにした`、「～」は目的語スロットを示す辞書的表記。Std TTSでは先頭の「～」が「なになに」に決定論変換される)。
- LLMは Rule7(A'窓内)に適合する `based on interviews` を返した。KPの英語は目的語 `interviews` を含んで完結しているが、
  glossは目的語スロットを残した汎用形(「なになにをもとにした」)で、`interviews`(インタビュー)に対応する語を含まない。
- 判定: **不整合(軽度)**。意味の方向は矛盾しないが、英語KPの具体語 `interviews` が日本語意味に反映されず、
  日本語が「なになに」のスロット読みになる(KP英語=具体語/日本語=スロットで学習者に二重表示がずれる)。
  委任文のG運用「不整合が1件でもあればSTOP。独自にglossを書き換えない」に従い、Std側のKP音声生成以降を停止した。
- 参考(許容側の見方): `～をもとにした` を「based on 〜 の意味」と見なせば補語付きでも意味は包含される、という解釈もある(G1/G2ユーザー判断事項)。
  どちらが正かの判断・glossの書き換えは本委任では行っていない。

## 次の判断材料
- 選択肢(Fable/ユーザー判断): (G1)軽度不整合は許容して続行 / (G2)gloss再生成(G3の新工程設計が前提) / (G3)窓の上限を狭める等のA'再設計。
- Adv(b1b)側はKP日本語意味を使わない構造のため独立に実行した(別セクション参照)。
