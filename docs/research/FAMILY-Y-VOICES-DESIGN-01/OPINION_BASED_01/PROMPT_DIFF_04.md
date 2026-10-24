# PROMPT_DIFF_04 (委任_22: PROMPT_DIFF_03からの差分。残存問題『世界設定の定義がV1の語りへ混入』の是正。DEV/Trial専用)

Production(X/Z)のPrompt・正規表現・閾値・辞書は無編集。`er110_family_y_opinion_based_01.py`ほか既存er110 text moduleはgit diffで無変更(testで固定)。変更は`er110_family_y_opinion_based_02.py`のみ(+音声段のOPEN-493修正)。

## 原因
世界設定の`distinctions`(年齢による制限・利用禁止・年齢確認・段階的な制限)が全Voiceの生成Promptへそのまま渡され、V1が定義の内容を自分の意見として語った(02a V1第7文、02b V1第6文)。

## 差分(2点を併用。人物名のハードコードなし)
| # | 変更 | 場所 | 理由 |
|---|---|---|---|
| 1 | 定義をVoiceごとに絞る: Sheetのデータ`relevant_terms`(V1=年齢による制限のみ / V2=年齢による制限・利用禁止 / V3=年齢による制限・段階的な制限)にある用語だけを`build_voice_prompt_02`が01のbuilderへ渡す(`patched_ob`のwith内だけ差し替え)。`relevant_terms`が無いSheetは全件のまま | `SHEETS_02[...]["relevant_terms"]`、`build_voice_prompt_02` | V1に『段階的な制限』の定義が見えなければ、V1がそれを意見として語る誘因が無くなる。各Voiceの経験欄・主張に対応する用語だけに限る |
| 2 | THINK_BLOCKに考え方Dを追加: 「【区別の定義】は用語の意味を取り違えないための前提であり、語る中身ではない。定義にある内容を、経験・意見の欄に根拠のない、この人自身の考えとして述べない」 | `THINK_BLOCK` | 絞った後も残る定義(V2/V3)が、他人物の意見として混入するのを防ぐ文面側の歯止め |
| 3 | THINK_BLOCK考え方Cの末尾に「同じたとえや言い回しは、一度使ったら語りの中で繰り返さない」を追加(一般指示のみ。回数の機械化なし) | `THINK_BLOCK` | 02b V3のたとえ2回の軽い反復への対処 |
| 4 | runnerの起動ガード: `main(run_name, paid=False)`。`--paid`が無ければ承認ファイルの有無にかかわらず終了コード8(API 0)。許可run名に`run_03`を追加 | `main` | 委任_21の誤起動事故の再発防止(委任_22 §3) |

不変: 規則4(出典ルール)・7・9・10・11、約260〜300字、常体、考え方A〜C、V2の監視0を保つSheet、V3の泳ぐたとえ、Gate・UNMAPPED再生成の上限(各Voice1回)・予算の歯止め。

## 結果(run_03)
V1に定義由来の文なし(正規表現・agent目視とも0)。V2監視文0、V3のたとえ1回。ただしV3は『準備なしに急に使い始める』心配を第4・6・7文で言い換えており目視で軽い反復(機械指標0)。詳細は`PROVENANCE_03.md`・`EVAL_SET_03.md`。

## 残存・撤去のGrep
- 撤去: なし(追加のみ)。`SHEETS_02`内の`relevant_terms`以外のSheetデータは無変更。02a/02b再現: 01のBUILDERが復元される(with外)ため影響なし。
