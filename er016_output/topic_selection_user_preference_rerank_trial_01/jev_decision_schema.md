# Jev Native Decisions schema・batch設計メモ

## state(全stepで同一、byte固定)
`evaluation_objective`(委任文の逐語文)+ `preference_examples`(Teacher 57件、
`dataset_id`/`topic_ja`/`hook_ja`/`user_score`のみ)。UTF-8で11,866 bytes
(2026-09-24実測、`jev_probe.json`/本ファイル作成時点のTeacherデータに基づく)。
32 KiB上限(32,768 bytes)のうち、questions側に残る予算は約20,900 bytes。

「同一stateを維持した決定論的batch」の解釈: state自体(preference_examples +
evaluation_objective)はどのbatchでも一切変更しない。batchで変わるのは
`questions`のみ(どのcandidateを尋ねるか)。Candidateの内容(topic_ja/
summary_ja/source_name)は各questionの`instructions.candidate`に埋め込む
(stateには入れない)。この設計により「同一state」はbyte単位で厳密に維持
される。

## questions(score type)
1 candidate = 1 question。`criteria`はdocsの制約(2〜10レベル)に従い
`Level 1`〜`Level 10`の10段階。`instructions`は object形式(docsで許可)
: `{"task": <逐語文>, "candidate": {...}}`。

## batch size N の決定(60件を固定Nで分割)
候補60件・Teacher 57件で実測したpayload総bytes(state+questions)は以下
(2026-09-24, 実データで実測、`json.dumps(..., ensure_ascii=False)`):

| N  | batch数 | 最大batch実測bytes | 32 KiB(32768)以内か |
|----|---------|---------------------|------------------------|
| 15 | 4       | 24,569               | Yes(余裕8,199 bytes)  |
| 20 | 3       | 28,094               | Yes(余裕4,674 bytes)  |
| 25 | 3       | 32,372               | Yes(余裕396 bytes)    |

理論上の最大固定NはN=25(3 batchのまま)だが、余裕が396 bytesしかなく、
実際のHTTP送信時のencoding差・将来Teacherデータ追加等で容易に超過し得る
ため採用しない。**N=20(3 batch、余裕4,674 bytes=14%)を採用**する
(安定性優先、`CLAUDE.md`開発方針)。60÷20=3 batchで均等に分割できる点も
理由。

## 情報量の同一性(byte比較)について
Teacherフィールド(dataset_id/topic_ja/hook_ja/user_score)・Candidateフィー
ルド(id/topic_ja/summary_ja/source_name=媒体)は、Jev用stateとquestionsへ
一切要約・省略せず、`candidate_pool.json`/`topic_selection_user_eval_dataset
.json`の値をそのまま埋め込んでいる(Luna/Terra/Sol側で同一内容を使うかどうか
は、L/T/S実装が本リポジトリに存在しないため比較できない。詳細はRESULT_PACKET
の該当項目参照)。
