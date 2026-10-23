# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り DESIGN_02
(UKUS 委任_02 / 2026-10-23。DESIGN_01 に Opus 条件Aレビュー(OPUS_REVIEW_01.md、Fable転記)を反映した確定設計。Production・Prompt・flag・閾値・脚本・golden の変更 0、API 0円)
前提: ROOT_CAUSE_01.md / DESIGN_01.md。承認済み仕様の根拠: er109 v1 は Family X/Z 限定で PRODUCTION_WIRED(OPEN-459)、A/B/C 凍結(PM_GOVERNANCE 27-3)。本設計の実装(`er111_*`)は DEV/Trial 専用で Production 経路から参照されない。

## 1. OF 反映状況表(差分)
| OF | 区分 | DESIGN_01 → DESIGN_02 の変更 | 実装箇所 | 検証 |
|---|---|---|---|---|
| OF-01 | 必須 | key 正規化方式を廃止。**元 key のまま整列**し、同数・語 unit・1:1 の replace span を**位置ごと**に判定。既存判定(音素)が不合格の位置だけ固定対表を参照。残り位置は既存の bad チェック/`_judge_span`。**さらに既存 er109 が PASS なら結果をそのまま返す**(単調性を構造で保証)。長さ違い・欠落・付加は従来どおり NG。CMU 未登録(jewellery)は対一致位置を bad 検査の対象外に | `er111_ukus_spelling_trial_01.py: evaluate_trial` | V4(PASS→NG 0・PASS 行の reason 変化 0)、test `test_existing_pass_is_byte_identical`/`test_monotonic_over_stored_pairs` |
| OF-02 | 必須 | 側(canonical→ASR)を明示、偽の発音注入なし、canonical 側の固有名詞らしさで除外(全大文字・語中大文字・非ASCII・文中大文字始まり・文頭大文字+次が大文字語)。sim の偶奇判定・`{("UKUS",)}` 注入は廃止 | `_canon_entity_flags` / `PairTable.direct` | V3(Aluminium City 等 NG 維持)、V2 追加(文頭大文字一般語は PASS) |
| OF-03 | 必須 | VarCon タグ解析修正。UK 側=B/Z タグ(x/- なし)かつ A 第一推奨でない語(Av=米変異は B を持たないので入らない)。US 側=A 第一推奨(B/Z/C/D 併記可) | `er111_ukus_pairs_build_01.py: varcon_pairs` | test `test_of03_av_variant_not_uk_side` |
| OF-04 | 必須 | AMB 判定拡張。UK 形が別項で有効な米綴り(mum[silent]/mom 型)を VarCon の他行の A タグで自動検出し、**CMU 両側登録で発音が同じなら AMB(UK→US 一方向)、未登録/発音が違うなら除外**(mum/mom, analyses/analyzes, busses/buses 型は除外)。breame は用法情報が無いため不採用 | `build()` 前半 | test `test_of04_excluded_mum_mom_and_analyses` |
| OF-05 | 必須 | Tier-2(level71〜99)は初回 Trial では非同値(active=False、8,718 対を inactive として記録のみ)。UKUS 情報は **warnings に入れない**(`res.ukus_pairs`/`pron_differs` の別 field)。PASS_WITH_WARNING にならず、ORTHO_* 写像(事後試聴負担)も起きない | `PairTable`(active のみ)/`audit_ukus` | test `test_c12_both_directions`(warnings==[]/verdict==PASS)、`test_tier2_inactive_fail_closed` |
| OF-06 | 推奨 | 発音も違う対(speciality/aluminium/catalogue…)は TTS が米式に読んでも PASS する残存リスク → 対ごとに `pron_differs` を表に記録(52 対)、評価時に `pron_differs_n` を集計。最終報告で明示 | pairs.json `pron_differs`/`cmu_dist` | V1 `pron_differs_via_ukus`、TRIAL_RESULT_01 §5 |
| OF-07 | 推奨 | hook 整合・隔離。Trial は er109 の module global を **monkeypatch しない**(import 時に `evaluate` を束縛して再帰も防ぐ)。V6 のみ専用 worker process で `er109_xz_scope_01._evaluate_cached` を差し替え+`cache_clear`(終了で消える)。AST test で Production→Trial の import 0・代入 0 を固定。`eq.version`(=LAYER_VERSION)は既定値のまま通る | `evaluate_trial_cached`(V6 専用)、`er111_ukus_trial_eval_01.py:_v6_worker` | V6、test `Isolation` 6 件 |
| OF-08 | 推奨 | 規則(ise→ize, yse→yze, our→or)の実在語判定を wordfreq から **SCOWL 固定版**へ(変換前=SCOWL 英国語専用リストの語、変換後=SCOWL 米国語/共通語 level≤70、stem≥4)。規則は**ビルド時に固定表へ展開**し runtime に規則・wordfreq 依存なし | `rule_target`/`build()` 後半 | V5(規則精度: 誤同値候補 0) |
| OF-09 | 推奨 | V5 は自己参照 → **V5b**(パブリックドメイン英国作家+repo の英国記事で被覆率・誤写像候補)、**V5c**(両形が高頻度独立語の対の人手レビュー)、独立辞書 breame による被覆確認を追加 | `v5/v5b/v5c` | V5/V5b/V5c |
| OF-10 | 推奨 | V2 追加(mum→mom・文頭大文字一般語・所有格・ハイフン複合)、V3 追加(US 形固有名詞→UK 形・同語反復文)、V4 全件+reason 変化一覧、V6 に Secondary/KP 投票経路、V8 に隔離 AST+golden 不変 | `er111_ukus_trial_cases_01.py` ほか | V2〜V8 |
| OF-11 | 推奨 | license: 固定対表(denylist 適用済み・入力 hash・冒頭に著作権/許諾文)を同梱、runtime は固定表のみ、breame 不採用 | `er111_ukus_pairs_v1.json: meta` | test `test_license_and_input_hashes` |
| OF-12 | 推奨 | 案 H(LR 入口で綴り差のみなら HR)は Trial 前提にしない。**別案件候補として末尾に記録のみ** | 本書 §6 | — |
| OF-13/14 | 情報 | Azure Secondary を en-GB にする補助案は将来案として §6 に記録。API 0 円・辞書ロードは固定表で 0.017 秒(測定) | §6、V7 | V7 |

**事実誤り訂正**(OF-11): DESIGN_01.md:25 / ROOT_CAUSE_01.md:59 の「breame は practise・licence を欠く」は誤り(breame spelling_constants.py:883,1217 に収録)。正しくは「breame は用法(名詞/動詞等)情報を持たず AMB を自動判定できない/VarCon 未収録の語は少数(約 5%)」であり、不採用の理由は後者(OF-04/OF-11)。VarCon が `speciality`・`jewellery`・`practise`・`programme`・`licence` を全て収録していることは本 Trial で確認(`er111_ukus_pairs_v1.json`)。

## 2. 確定アーキテクチャ(Trial)
```
VarCon 2020.12.07 + SCOWL 2020.12.07 ──(build: er111_ukus_pairs_build_01.py)──▶ er111_ukus_pairs_v1.json
   (UK/US タグ解析=OF-03、AMB 一方向、OF-04 自動検出、denylist 人手レビュー、規則展開=OF-08、Tier-2 非活性)   [固定・hash 付き・許諾文付き]
canonical, ASR ──▶ er111_ukus_spelling_trial_01.evaluate_trial  ──(内部で import 時束縛の e109.evaluate を呼ぶ)
   ├─ 既存 er109 が PASS → そのまま返す(単調)
   └─ NG → 同じ unit 列・同じ difflib 整列を再利用し、同数の語 replace span を位置別に判定
          位置ごと: 既存基準で PASS → 既存どおり / 既存で不合格かつ canonical 側が固有名詞らしくなく、直接対が表にある → SpanRecord(rule="ukus_spelling_variant")
          上記以外の位置が 1 つでも不合格 → 全体 NG(reason は既存と同じ形式)
Production 経路(er006/er020/er078/er104/runner/er109/scope)は上記 module を一切参照しない。
```
- 直接対のみ(推移しない)。向き: 通常対は双方向、AMB 対は canonical=UK 形→ASR=US 形のみ。語幹+同一接尾('s / s')とハイフン複合(各部が同形か対)に対応。
- 範囲外(従来どおり NG): 語数が違う span(`jewellery-making`↔`jewelry making`)、欠落・付加、数/記号/略語を含む span、canonical 側が固有名詞らしい語、表に無い語、Tier-2。

## 3. 実装中に生じた設計変更(ITERATION_LOG_01.md に詳細)
1. **UK 側定義の拡張(Bv/B. を許す)**: OF-03 を厳密に実装した初版では `encyclopaedia/encyclopedia`・`foetus/fetus`・`gaol/jail`・`yoghurt/yogurt` などが VarCon 上「B. + AV」「Bv ZV」で UK 側に入らず取りこぼした(V1 の失敗で発見)。UK 側=「B/Z タグ(x/- なし)かつ A 第一推奨でない」に修正(Av 混入は維持して防止)。増えた約 430 対は全件人手レビューし、不適切な対を denylist 化(PAIRS_REVIEW_01.md §1)。
2. **OF-04 を「除外」から「CMU 同発音なら AMB」へ**: `analogue/analog`・`draught/draft`・`dyke/dike`…は発音が同一(音声上の誤 PASS が起きない)ため一方向 AMB として復活。発音が違う/CMU 未登録(mum/mom, analyses/analyzes)は除外のまま。
3. **規則の位置づけ**: SCOWL 固定条件では規則が生成する対は全て VarCon に既存(新規 0、T2→R 昇格 5 対)。規則は「系統クラスで VarCon と矛盾しないこと(精度 100%)」を検査するビルド時の安全網であり、runtime で未知語を救済する機能ではない。未知語の救済範囲は V5b/breame 照合で実測。
4. **性能**: 初版は NG 経路で unit 化を 2 回行い p95=1.04ms(基準 1ms 超)→ 既存 NG 結果が保持する unit 列を再利用して p95=0.10ms。

## 4. 採用時の配線案(本委任では実装しない。Opus 条件C・ユーザー承認の後、別委任)
er109 に `unit_postprocess` 相当の拡張点(既定 None=従来)+X/Z scope 内の単一 flag 読取関数(既定 OFF、11-7 の 5 条件)。採用時は `LAYER_VERSION` 更新と X/Z golden 再作成(OF-07)。固定表は Production に同梱(license 文含む)。

## 5. 撤去・残置
- 撤去 0(`val.BR_AM_SPELLING_PAIRS` は共有 Validator のため触らない。DESIGN_01 §4 のとおり)。DESIGN_01 の「key 正規化方式」「breame 補助辞書」「Tier-2 を PASS_WITH_WARNING」「wordfreq 規則」は本書で**廃止**(test/Grep: `er111_*` に `wordfreq` import なし、`breame` は評価専用 V5 のみ)。

## 6. 別案件候補(本委任の範囲外・記録のみ。ユーザー承認事項)
- **案 H(OF-12)**: 「綴り差のみと疑われる NG は LR で書き換えず HR へ」= Production の意味的変更。UKUS 層(本件)が働けば不要になる補助。必要性は Trial 結果次第。
- **en-GB Secondary(OF-13)**: Z 英国作品限定で Azure Secondary を en-GB にする。Primary(OpenAI)の綴りは制御不可・X への逆方向問題あり。将来案。
- **未解決の取りこぼし(fail-closed)**: `amongst/among`・`onwards/onward`・`maths/math`(語尾 s/st の有無=発音差のある語形差)、`dialogue/dialog`・`disc/disk`・`gauge/gage`・`tonne/ton`、ハイフン複合↔分かち書き+綴り差の同居。いずれも従来どおり NG(現行と同じ)。
