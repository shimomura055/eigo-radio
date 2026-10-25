# DESIGN_07(Trial-07: Part 2 文法解説は最大1件・該当なければ0件)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12 / 日付: 2026-10-25 / Status: DEV/Trial専用。合格しても到達上限VALIDATED。Production配線は禁止、正式採用は別途ユーザー判断。
根拠: ユーザー統合指示(`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md` §3・§4)、`EVAL_06.md`。実装: `run_trial_07.py`/`analyze_07.py`/`test_trial_07.py`。基準: `PREREGISTERED_CRITERIA_07.md`(Step A'' 生成前commit)。

## 1. Trial-06からの差分
| 項目 | Trial-06 | Trial-07 |
|---|---|---|
| 件数 | 最大2件(同一クラス・同一段落は1件まで) | **最大1件・適格0なら0件**(2件目の選定ロジック廃止。件数を満たすための選定なし) |
| 学習価値 | なし(分類+misread欄のみ) | `teaching_value`(HIGH/LOW)+`teaching_value_ja`(身につく読み方1句)。HIGHかつ非空でなければ適格にならない(強クラスにも適用) |
| FRONT | 定義に副詞節を例示しつつ基礎項目にも基本接続=**矛盾**(Trial-06の許容集合外14件中10件がbefore/after+節のFRONT) | `front_kind`欄を追加。CLAUSE_SIMPLE(単純な副詞節)・PHRASE_SHORT(短い副詞・前置詞句)は基礎=不適格。PARTICIPLE/ADJECTIVE/AS_THOUGH/NESTED_OR_LONG/OBJECT_OR_COMPLEMENTは適格(複雑な文頭要素は一律除外しない)。Promptの定義と基礎項目を整合 |
| ELL | `Still the same.`等3件が許容集合外 | 「別の主語の動詞・比較の基準を補う省略」に限定、`omitted_words`非空を適格条件に。同じ主語の並列・省略された関係代名詞は基礎 |
| 欄 | correct_structure_ja/subject_span/main_verb/other_desc(記録のみ) | 削除(出力トークン削減=費用)。`front_kind`/`omitted_words`/`teaching_value`/`teaching_value_ja`を追加 |
| 引用文連結 | resolve6が失敗→feature脱落(開いた窓r2でP21=中核が脱落) | Prompt禁止文+`resolve7`(段落境界連結の検出・主張段落spanへ再解決・誤修復しない)+`verify_single_span`(最終検査)+回帰テスト |
| 作品 | 6 | 8(既存6=Trial-06と同一本文・同一許容集合 + 新ホールドアウト2: 退屈と攻撃性=難所あり[Family X Advanced既存本文]、走れメロス=平易・許容集合∅[Family Z既存本文]) |
| 標本 | 6×3=18 | 18 call(開いた窓3・賢者3・他6作品N=2)。上限12円内に収めた配分(PREREGISTERED_CRITERIA_07 §3) |
| 費用ガード | 予約方式 | 同じ`Budget`を再利用(上限Step A'' 10.8円・全体12.0円) |

## 2. 引用文連結不具合の原因と対策
- 原因(実出力で確認): Trial-06 `OUTPUT_06_open_window_r2_STEPA_DEV.json` featuresのP21で、LLMが`Across the quiet garden came a young voice: “Bertie, why do you bound?”`を返した。本文ではP21=`Across the quiet garden came a young voice:`(コロンで終わる)、P22=`“Bertie, why do you bound?”`(別段落)。`resolve_verbatim`は主張段落内を検索するため失敗し(`sentence not found in para`)、連結文は出力に出ず安全側に落ちたが、中核のP21がfeatureごと脱落した。
- 対策(層ごと): (1) Prompt: 段落をまたぐ連結の禁止とコロンの扱いを明記。(2) `resolve7`: resolve6が失敗した場合に限り、語列が「主張段落の末尾+直後(最大3段落)の先頭」または「直前段落の末尾+主張段落の先頭」に**厳密一致**するときだけ、主張段落内のspanへ限定して再解決しflagを記録(一致しなければ失敗のまま=誤修復しない。引用符の有無は語の前後の記号を無視して比較)。(3) `verify_single_span`: 解決後の文が主張段落1つの逐語spanで改行を含まないことを検査し、不合格なら適格にしない。既存の`resolve_verbatim`/`resolve6`/段落境界/引用符処理を土台に再利用し、新しい抽出機構は作っていない。
- 回帰テスト: `test_trial_07.py`/`run_trial_07.py selftest`(Trial-06実出力の固定データ再現・逆向き・誤修復しない3種・既存動作不変・実出力features全体のparse・mock LLMのend-to-end・0件経路)。

## 3. 既存機構との整合・Production境界
- Production側に英語学習テキスト解説は存在しない(DESIGN_04 §1)。全てDEV専用で、Production code/Prompt/閾値/flagの変更0。`er019_*`/`er026_*`は読み取り(本文入力)のみ。
- 新Checker/Validator新設ではない(選定段の分類と決定論規則、抽出段の検証のみ)。Part 1の配線は別agentが担当し本委任では触らない。
- 責務分離: 点検・分類・学習価値の事実記述(LLM) / 選定(コード・固定優先順位・1件) / 執筆(Step B LLM、Trial-04と同一Prompt)。「どの構文を教えるか」の価値判断(優先順位・FRONT採否・学習価値HIGH要件)は事前登録で固定し、VALIDATED報告時にユーザーへ開示する。
- 過剰適合防止: Promptの例は全て自作文(8作品全文との逐語照合をdry-run/selftestでassert)。ホールドアウト2作品は設計時に本文を見ていない。
