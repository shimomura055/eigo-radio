# TRIAL-02 Ledger側正解データ(複数事象、事前登録)

ledger_truth_02.json: 10 fact、Ledger本文の逐語quote付き事象リスト。TRIAL-01のAI抽出は参照せず本文から独立に決定(quoteは本文部分一致をbuild時にassert済)。

## Ledger側精度の採点規則(集計script用)
1. 抽出events(`subject_x`, `ledger_state`)と正解eventsを、`event_key`または`aliases`のいずれかが `subject_x` に部分一致(双方向の包含、大小無視)したものとして対応付ける。1正解eventに複数抽出が対応する場合は最初の1件。
2. 対応したeventの `ledger_state` が正解の `acceptable_states` に含まれれば state一致。state精度 = state一致数 / 対応event数(正解event総数を分母にした再現率も併記)。
3. 方向性精度: fact単位で、抽出の has_direction が正解 `has_direction` と一致する率。
4. 正解eventのうち対応する抽出が無いものは「欠落」として件数記録。
5. 対応しない余剰抽出eventは「余剰」として件数のみ記録(誤りと断定しない)。
6. 本採点は参考指標で、合格基準(HC-012/A5-0検出、誤重大2%以下等)には使わない。

## 事象一覧
| fact_id | has_direction | event_key | state(許容) | 逐語quote |
|---|---|---|---|---|
| MUSE-HC-012 | true | 電話テスト | STARTED | 契約スタッフが電話をかけるテストを開始した |
| MUSE-HC-012 | true | 機能 | PAUSED(STOPPED) | 機能を当面ロールバックした |
| HF-009 | true | 上げ幅 | DECREASED(NARROWED) | 一時的に上げ幅を縮小した |
| HF-009 | true | 水準 | INCREASED(UNCHANGED) | ほどなく発表前に近い高い水準へ戻った |
| HF-007 | true | 償還料案 | ENDED | 20％の米国償還料を、…置き換えると投稿した |
| HF-007 | true | 投資案件 | STARTED | …対米貿易・投資案件に置き換えると投稿した |
| HF-002 | true | 償還要求 | STARTED | 20％の率で償還を求めると投稿した |
| HF-011 | true | Brent先物価格 | INCREASED | 1.43ドル、1.7％上昇し |
| HF-003 | false | 制度設計 | UNCHANGED(NOT_MENTIONED) | 具体的制度設計は示されなかった |
| MUSE-HC-004 | false | 電話機能の用途 | UNCHANGED(AVAILABLE) | …などを依頼できる |
| MUSE-HC-006 | false | 人間通話テスト | UNCHANGED(STARTED) | 「human concierge」「human agent calls」のテストを実施した |
| MUSE-HC-010 | false | プライバシー懸念 | UNCHANGED | プライバシー上の懸念を示した |
| MUSE-HC-013 | false | 従業員の反応 | UNCHANGED | 「圧倒的に肯定的」だった |

## 注記
- 独立に決めた結果、HC-012/HF-009の主事象はユーザー例示と一致。追加でHF-007に「投資案件」STARTED(置換先)を登録(余剰/欠落の扱いは規則4-5)。
- HF-009「水準」はINCREASED(復帰)を正とし、実質UNCHANGEDも許容(TRIAL-01の全体判定UNCHANGEDとの整合)。
