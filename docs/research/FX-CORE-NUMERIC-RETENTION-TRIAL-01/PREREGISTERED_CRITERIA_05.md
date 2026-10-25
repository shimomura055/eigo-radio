# PREREGISTERED_CRITERIA_05(FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_06 C-2、生成前commit)

出典: Opus条件C(`OPUS_REVIEW_03.md` C-2)。目的=v4(判定基準を「①〜③のどれか」へ緩めた版)が、**数値が中心でない記事**で不要な数値を欄へ入れる逆方向の失敗をしないかの対照確認。評価方針(切り口基準)はユーザー承認済み(`2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_03.md`)で、新しい品質基準は作らない。

## 1. 標本(B3のみ・v4不変・R0以降は実行しない)
| 標本ID | 記事 | 入力 | 位置づけ |
|---|---|---|---|
| c2uk1 | uk_train_speaker_playback | er019_output/uk_train_speaker_playback/run_nws_02(既存ledger) | 対照。Phase 1のv1(Storyline方式)ではE=∅。ledgerの数値=制定年・罰金上限£1,000・TfL調査70%等(主題は『規則/キャンペーン』) |
| c2mg1 | manga_ai_chat_byus | er019_output/manga_ai_chat_byus/run_byus_01(既存ledger) | 数値が中心でない記事(AIチャットサービス発表。ledgerには1,400万件・+67%・+105%等の数値あり=入れてしまう誘惑がある型) |
| c2uk2 | uk_train_speaker_playback | 同上 | c2uk1の再現(同一入力のB3ゆらぎ確認) |
起動順=c2uk1 → c2mg1 → c2uk2(予算が尽きた場合に、種類の異なる記事[manga]を優先して残す)。
コマンド(各1回・並列なし=残額確認を挟むため直列): `.venv\Scripts\python.exe er115_fx_numeric_retention_trial_01.py b3 --article <A> --sample <ID> --b3-addendum v4 --max-attempts 1 --per-run-cap-jpy 15 --phase-cap-jpy <起動時の累計+15>`。モデル=Production B3と同じ`gpt-6.1-sol`(最新世代)。

## 2. 費用管理(上限厳守)
- 案件累計544.02円/上限580円(残35.98円)。**1本あたり最大見込み13円を予約**し、起動前に `phase_spent_jpy()` で残額(580−累計)≥13円を確認。足りなければ起動しない(=3本目が入らなければ2本で止めて報告)。
- B3再実行(M1違反時の自動再実行)は費用が倍になるため、C-2では`--max-attempts 1`で**再実行しない**(M1違反が出た場合は結果として記録し、無料のC-1再適用で判定の参考にする)。per-run cap=15円。
- 再起動0。外部停止・原因不明のrc≠0が2回続いたら即STOP。

## 3. 合否(標本ごと。判定はFableがStoryline・欄・選定理由を読んで行う。機械的な固定表は使わない)
合格:
- (a) `reader_must_hear_numbers`が`[]`(数値を入れなかった)。
- (b) 欄に数値が入った場合でも、その数値が**その標本のStoryline(B3が選んだ切り口)の問いを直接支え**、v4の①〜③のどれかに強く当てはまり、かつ④⑤の問題がない(=ユーザー承認の切り口基準。数値が無いと切り口が伝わりにくい/驚き・面白さを支える/論旨・比較の説得力を支える)。
不合格:
- (c) 欄に数値が入り、それが切り口に不要(背景・補足の数値、他の数値の言い換え・内訳、比較の相手側の値、記事の中心でない数値、ledgerに出るだけの数値)。
記録する材料(Fable読み用): Storyline / 欄 / 欄の各数値のledger行(numeric_value・numeric_scope・claim) / 採用Fact一覧 / B3の選定理由(`fact_selection_evidence.json`の理由欄) / M1の構造検査結果(first-pass) / 費用。
合否の集計: 3標本の合否を個別に示す。**全標本が合格ならC-2合格**(数値が中心でない記事での逆方向の失敗なし)。1本でも不合格なら、v4指示文は事前登録04のとおり不変のまま(追加のv5調整はユーザー判断)、事実・原因仮説・影響(量産での不要数値混入の見込み)を報告する。

## 4. 固定事項
- v4の指示文(`B3_ADDENDUM_V4`)・schema欄・M1/E/Gateの実装は、委任_05と同一(C-1の欄優先導出は本C-2のB3 callの動作に影響しない=B3出力後の決定論処理のみ。C-2の判定にはC-1再適用の結果を併記するが、合否は欄の中身で決める)。
- Production file変更0。出力はer115_output/のみ。
