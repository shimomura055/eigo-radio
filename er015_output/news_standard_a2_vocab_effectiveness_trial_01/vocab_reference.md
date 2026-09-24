# vocab_reference.md — 採用した頻度基準(NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01)

## 探索手順と結果

1. Repo内探索: `Glob **/*{ngsl,NGSL,oxford,gsl,wordlist,word_list,frequency,cefr}*`
   および `Grep pattern="ngsl|oxford 3000|wordfreq|cefr" -i` を実行。
   ヒットしたファイルはいずれも既存Report/Prompt内の「CEFR」という語句への
   言及のみで、実体を持つ頻度リストファイル・CEFR語彙リストファイルは
   Repo内に存在しなかった。
2. .venv既存依存確認: `pip show wordfreq` / `pip show nltk` / `pip show spacy`
   はいずれも `Package(s) not found`(未導入)。
3. 無料公開の頻度リストを1回だけ新規取得: `pip install wordfreq`
   (PyPI, Apache-2.0ライセンス, ローカル計算・無料、有料APIではない)を実行し
   `wordfreq==3.1.1` を導入。`wordfreq.top_n_list("en", 2000)` で英語の
   頻度上位2,000語形(wordform)を取得した。

## 採用基準

- 「約2,000語圏」= `wordfreq.top_n_list("en", 2000)` が返す上位2,000語形。
- 圏内/圏外の判定は **lemma化した集合同士の比較** で行う: 上位2,000語形を
  `simple_lemma()`(標準ライブラリのみ、複数形/三単現/過去形/-ing/比較級・
  最上級の規則活用のみ簡易正規化)でlemma化し重複除去した集合
  (`frequency_lemma_set.json`、1686語)を「頻度圏内」の基準集合
  とする。記事側のcontent wordも同じ`simple_lemma()`でlemma化してから
  この集合に含まれるかを判定する。

## 限界(既知)

- `simple_lemma()`は不規則活用(bring→brought、child→children等)に
  対応していない。該当語は圏外判定になりうる(誤判定リスクとして記録)。
- `wordfreq`の頻度データは複数コーパスの統合値であり、CEFR A2公式語彙
  リスト(例: Cambridge English Profile)そのものではない。「高頻度語」
  であることと「A2レベルとして学習指導要領上適切」であることは同義では
  ない。本Trialでは代替指標として使用する。
- lemma化により2,000語形が1686lemmaに縮約されている
  (同一lemmaの活用形が複数含まれるため)。「頻度圏内」の実質カバー範囲は
  語形2,000個より若干狭い可能性がある。
