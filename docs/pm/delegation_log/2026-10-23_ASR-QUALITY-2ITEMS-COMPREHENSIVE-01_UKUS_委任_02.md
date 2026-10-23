FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-UKUS-委任_02-TRIAL-IMPL-VERIFY-20261023

# 委任_02(②英米綴り): Opus条件Aレビュー反映→DEV/Trial実装→検証V1〜V8(+追加)→自律改善ループ→Fable評価資料。Production/Prompt/flag/閾値変更0。API費用は原則0(必要時≤20円、理由記録)。

## 前提読込
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/RESULT_PACKET_ASRQ_UKUS1.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md`(§3自律改善ループ・§4②受入条件・§5境界)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_UKUS_委任_02.md`(index 346以降、先頭MARKER一致)。
2. **Opusレビュー本文を保存**: 下記「Opus所見(逐語要約)」を `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/OPUS_REVIEW_01.md` として保存(Fable転記である旨を冒頭に明記)。
3. ACTIVE_TASK自分の行のみ(並行: ①PN agent[Opusレビュー中→Trial]、他)。OPEN_ITEMS: 仮ID `OPEN-ASRQ-UKUS` を正式採番(既存最大+1。①PN側 `OPEN-ASRQ-PN` と衝突しないよう、git status→再Grep→自分の行のみ即commit。先に採番された側があればその次番号)。

## Fable判定(記録用)
Opus総合判定=「必須修正5点を反映すればTrial実装可」。Claude案と方向は実質一致(新層・X/Z限定・音素層不変・fail-closed・VarCon主辞書・AMB一方向・規則3系統)。対立点は差し込み方式・Tier-2扱い・breame・VarConタグ解析・V5で、いずれも技術品質の修正でありProduct原則の変更ではない→**Fable判断でTrial実装へ進む**(11-3のSTOP条件非該当)。案H(LR入口で綴り差のみならHRへ)はProductionの意味的変更=別案件・ユーザー承認事項として記録のみ。

## Opus所見(逐語要約。必須=OF-01〜05、推奨=06〜12、情報=13〜14)
- OF-01[必須] key正規化方式をやめ、元keyのまま整列後、同じ長さ・語unitのみのreplace spanで位置ごとに(canonical語, ASR語)対を判定。既存判定(音素)が不合格の位置だけ許可対集合(推移しない直接対、AMBは方向付き)を参照、一致位置は `SpanRecord(rule="ukus_spelling_variant", equivalent=True)`、残り位置は既存の `bad` チェック/`_judge_span`。単調性(既存不合格位置だけ追加PASS)を構造保証しPASS→NG 0。長さ違いspanは従来どおりNG。`jewellery`(CMU未登録)は対一致位置をbadチェック対象外に。(根拠 ukus_sim_01.py:28-36、er109:729-761)
- OF-02[必須] 試作の手抜き排除: 側(canonical/ASR)を明示的に渡す(ukus_sim_01.py:30の偶奇判定禁止)、偽の発音 `{("UKUS",)}` 注入禁止(:35、er109:743のfail-closed迂回禁止)、`entity_tokens` 除外(§3-2-2)を実装、canonicalがUS形固有名詞でASRがUK形(Rockefeller Center→Centre)はcanonical側の固有名詞判定で除外。
- OF-03[必須] VarConタグ解析修正: `us if "A" in plain else uk`(ukus_lexicon_01.py:40-41)ではAv(米変異綴り nite等)がUK側に混入。UK側はB/Z(必要ならC/D)タグを変異印v/V/-/xなしで持つ語に限定。
- OF-04[必須] AMB判定拡張: UK形が別語義で有効な米綴り(mum[silent]/mom)はVarCon別エントリのAタグ(x/-なし)で自動検出しAMBまたは除外。breame対は用法情報なしでAMB判定不能→不採用(OF-11)。
- OF-05[必須] Tier-2(level71〜99)は初回Trialでは非同値(fail-closed)。UKUS情報は `warnings` に入れない(er109:534でPASS_WITH_WARNING化、er109_xz_scope_01.py:133でORTHO_*写像→事後試聴負担増)。別フィールド(`ukus_pairs`/`pron_differs`)に記録。規則はOF-08強化のうえ警告なしPASS+監査のみ。
- OF-06[推奨] 発音も違う対(speciality/aluminium)はTTSが米式に読んでもPASSする残存リスク→`pron_differs` を監査記録・件数監視し最終報告で明示。
- OF-07[推奨] hook整合OK(P-06非関与、Store guard `ortho_contributed`、KP投票同入口)。注意: `_evaluate_cached` LRU(er109_xz_scope_01.py:97-101)はON/OFF比較前後で `cache_clear()` 必須。`eq.version != LAYER_VERSION`(:131)でdecisionが黙ってNone→V6偽NGの原因。採用時はLAYER_VERSION更新+X/Z golden再作成。隔離: Trialはer109のmoduleグローバルをmonkeypatchせず、内部関数を読むだけの「Trial用evaluate」を別moduleに置く。V6のみtest専用processのcontext managerでpatch+cache_clear、LR/TTS/ネットワークはmock。AST testでProduction module(er006/er020/er078/er104/runner)がTrial moduleをimportしないこと、`_units`/`evaluate`への代入がtest/trial以外にないことを固定。
- OF-08[推奨] 規則の実在語判定をwordfreq zipf≥1.5からSCOWL米国語リスト(level≤70)固定版へ、かつ「変換前の語がSCOWL英国語リストにあること」を条件追加(otherwize/expertize型防止、runtime依存排除)。
- OF-09[推奨] V5は自己参照的→V5b: パブリックドメイン英国作家テキスト(Saki等)+英国記事から英国式語を抽出しカバー率・誤写像候補を測る。V5c: 最終対表全体から両形が高頻度独立語で語義が重ならない対を自動抽出し人手レビュー。
- OF-10[推奨] V2追加: mum→mom、文頭大文字一般語、所有格・ハイフン複合語(jewellery-making)。V3追加: US形固有名詞→UK形、同語反復文の整列。V4: 全件照合+er109経由現行PASS行のreason変化一覧。V6: Secondary(Azure)とKP投票経路も。V8: 隔離AST test+golden不変。
- OF-11[推奨] license: VarConはSCOWL許諾表記を全複製物に残し、runtime解析ではなくビルド時生成の固定対表(denylist適用済み・元hash付き・冒頭に著作権/許諾文)を同梱。breame不採用。事実誤り訂正: DESIGN_01.md:25/ROOT_CAUSE_01.md:59「breameはpractise・licenceを欠く」は誤り(spelling_constants.py:883,1217に収録)。
- OF-12[推奨] 案HはTrial前提にしない。別案件「綴り差のみ疑いのNGはLRで書き換えずHRへ」=Production意味的変更、ユーザー承認事項として記録。
- OF-13[情報] Z英国作品限定でAzure Secondaryをen-GBにする補助案(Primary綴りは制御不可、X逆方向問題)→将来案として記録。
- OF-14[情報] API 0円、辞書ロード0.24秒(固定表でさらに短縮)、効果=c12型1件あたり約1.1円・10.6分・脚本改変1か所を防止。

## 1. 設計更新
`DESIGN_02.md`(OF反映差分表付き、事実誤り訂正、案H/en-GBは別案件候補として§末尾に記録)。

## 2. Trial実装(DEV専用)
- module名は **`er111_ukus_spelling_trial_01.py`**(er110はFamily Y使用中のため不可)+固定対表 `er111_ukus_pairs_v1.json`(ビルドscript `er111_ukus_pairs_build_01.py`、VarCon固定版hash、denylist、AMB方向、Tier、license文)+test `er111_ukus_spelling_trial_01_test_01.py`。
- OF-01〜05・07・08・11を実装。Production module無変更、import方向はTrial→er109のみ。11-7のflag/既定OFFは「Production配線」ではないため作らない(Trial moduleは正式経路から未参照であることをAST testで固定)。
- 事前denylist人手レビュー(約145対+OF-04自動検出分)は、結果表を `PAIRS_REVIEW_01.md` に残す(除外理由付き)。

## 3. 検証(V1〜V8+OF-09/10追加分)。各Vの結果jsonと集計mdを `TRIAL_01/` に保存
- 成功基準はDESIGN_01 §5の数値(V1≥50対両方向全同値/V2≥30対+追加ケース新規PASS 0/V3境界/V4 PASS→NG 0・NG→PASS全件目視分類/V5+V5b+V5c/V6 c12再現でretry・LR・HR 0[Primary/Secondary/KP投票経路、mock]/V7性能/V8回帰0+隔離AST+golden不変)。
- **自律改善ループ**: 未達なら原因分析→(同方向微修正でなく)前提・方式の見直し→再検証。各反復を `ITERATION_LOG_01.md` に(何を変え、何が改善し、何が未達か)。見込みがなくなった場合のみ停止して報告。
- 『開いた窓』c12の保存転写(Primary/Azure)で対策後PASSになることを示す(API 0)。停止中音声・run_sf_prod_01は触らない。

## 4. Fable評価資料
`TRIAL_RESULT_01.md`: ユーザー最終報告9項目のうち②に関わる1〜7(根本原因/仕組み/改善前後比較/再設計履歴/残存リスク[OF-06含む]/X・Z適用範囲/速度・単価影響)を数値で。VALIDATED自己宣言はしない(判定はFable)。

## 5. SSOT・Git
OPEN行Status更新、DECISION_LOG(Fable判断: Opus反映→Trial実装)、REPORT_LEDGER。明示add、secret_scan hits=0、`git push origin HEAD:main`。全回帰は最後に単独実行し分類(既知: Y DEV `er110_family_y_audio_trial_01.py` によるfx_20261016 guard failは他委任由来)。

## 6. 禁止
Production/Prompt/flag/閾値/golden変更、er109/er006/er020/er078/er104/runner編集、A/B/C参照、LR/TTS実行、脚本変更、run_sf_prod_01操作、breame採用、Tier-2同値化、warnings経由のPASS_WITH_WARNING化。

## 7. 報告(docs/pm/RESULT_PACKET_ASRQ_UKUS2.md)
(1)OF反映状況表 (2)実装構成 (3)V1〜V8+追加の結果表(基準/実測/判定) (4)反復履歴 (5)残存リスク (6)費用・時間 (7)commit・raw URL・SSOT (8)RESULT_PACKET 4行+「判定整合: 重大NG=あり/なし」。