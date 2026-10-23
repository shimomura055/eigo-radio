# OPUS_REVIEW_01 (②英米綴り UKUS) 条件Aレビュー結果
注記: 本ファイルはFable(sandwich-pm)が委任_02の委任文へ転記したOpus独立レビュー所見の逐語要約である(Opus原文ではなくFable転記)。保存: 委任_02 T-0。

## Fable判定
Opus総合判定=「必須修正5点を反映すればTrial実装可」。Claude案と方向は実質一致(新層・X/Z限定・音素層不変・fail-closed・VarCon主辞書・AMB一方向・規則3系統)。対立点は差し込み方式・Tier-2扱い・breame・VarConタグ解析・V5で、いずれも技術品質の修正でありProduct原則の変更ではない→Fable判断でTrial実装へ進む(11-3のSTOP条件非該当)。案H(LR入口で綴り差のみならHRへ)はProductionの意味的変更=別案件・ユーザー承認事項として記録のみ。

## 所見(必須=OF-01〜05、推奨=06〜12、情報=13〜14)
- OF-01[必須] key正規化方式をやめ、元keyのまま整列後、同じ長さ・語unitのみのreplace spanで位置ごとに(canonical語, ASR語)対を判定。既存判定(音素)が不合格の位置だけ許可対集合(推移しない直接対、AMBは方向付き)を参照、一致位置は SpanRecord(rule="ukus_spelling_variant", equivalent=True)、残り位置は既存の bad チェック/_judge_span。単調性(既存不合格位置だけ追加PASS)を構造保証しPASS→NG 0。長さ違いspanは従来どおりNG。jewellery(CMU未登録)は対一致位置をbadチェック対象外に。(根拠 ukus_sim_01.py:28-36、er109:729-761)
- OF-02[必須] 試作の手抜き排除: 側(canonical/ASR)を明示的に渡す(ukus_sim_01.py:30の偶奇判定禁止)、偽の発音 {("UKUS",)} 注入禁止(:35、er109:743のfail-closed迂回禁止)、entity_tokens除外(§3-2-2)を実装、canonicalがUS形固有名詞でASRがUK形(Rockefeller Center→Centre)はcanonical側の固有名詞判定で除外。
- OF-03[必須] VarConタグ解析修正: `us if "A" in plain else uk`(ukus_lexicon_01.py:40-41)ではAv(米変異綴り nite等)がUK側に混入。UK側はB/Z(必要ならC/D)タグを変異印v/V/-/xなしで持つ語に限定。
- OF-04[必須] AMB判定拡張: UK形が別語義で有効な米綴り(mum[silent]/mom)はVarCon別エントリのAタグ(x/-なし)で自動検出しAMBまたは除外。breame対は用法情報なしでAMB判定不能→不採用(OF-11)。
- OF-05[必須] Tier-2(level71〜99)は初回Trialでは非同値(fail-closed)。UKUS情報はwarningsに入れない(er109:534でPASS_WITH_WARNING化、er109_xz_scope_01.py:133でORTHO_*写像→事後試聴負担増)。別フィールド(ukus_pairs/pron_differs)に記録。規則はOF-08強化のうえ警告なしPASS+監査のみ。
- OF-06[推奨] 発音も違う対(speciality/aluminium)はTTSが米式に読んでもPASSする残存リスク→pron_differsを監査記録・件数監視し最終報告で明示。
- OF-07[推奨] hook整合OK(P-06非関与、Store guard ortho_contributed、KP投票同入口)。注意: _evaluate_cached LRU(er109_xz_scope_01.py:97-101)はON/OFF比較前後でcache_clear()必須。eq.version != LAYER_VERSION(:131)でdecisionが黙ってNone→V6偽NGの原因。採用時はLAYER_VERSION更新+X/Z golden再作成。隔離: Trialはer109のmoduleグローバルをmonkeypatchせず、内部関数を読むだけの「Trial用evaluate」を別moduleに置く。V6のみtest専用processのcontext managerでpatch+cache_clear、LR/TTS/ネットワークはmock。AST testでProduction module(er006/er020/er078/er104/runner)がTrial moduleをimportしないこと、_units/evaluateへの代入がtest/trial以外にないことを固定。
- OF-08[推奨] 規則の実在語判定をwordfreq zipf≥1.5からSCOWL米国語リスト(level≤70)固定版へ、かつ「変換前の語がSCOWL英国語リストにあること」を条件追加(otherwize/expertize型防止、runtime依存排除)。
- OF-09[推奨] V5は自己参照的→V5b: パブリックドメイン英国作家テキスト(Saki等)+英国記事から英国式語を抽出しカバー率・誤写像候補を測る。V5c: 最終対表全体から両形が高頻度独立語で語義が重ならない対を自動抽出し人手レビュー。
- OF-10[推奨] V2追加: mum→mom、文頭大文字一般語、所有格・ハイフン複合語(jewellery-making)。V3追加: US形固有名詞→UK形、同語反復文の整列。V4: 全件照合+er109経由現行PASS行のreason変化一覧。V6: Secondary(Azure)とKP投票経路も。V8: 隔離AST test+golden不変。
- OF-11[推奨] license: VarConはSCOWL許諾表記を全複製物に残し、runtime解析ではなくビルド時生成の固定対表(denylist適用済み・元hash付き・冒頭に著作権/許諾文)を同梱。breame不採用。事実誤り訂正: DESIGN_01.md:25/ROOT_CAUSE_01.md:59「breameはpractise・licenceを欠く」は誤り(spelling_constants.py:883,1217に収録)。
- OF-12[推奨] 案HはTrial前提にしない。別案件「綴り差のみ疑いのNGはLRで書き換えずHRへ」=Production意味的変更、ユーザー承認事項として記録。
- OF-13[情報] Z英国作品限定でAzure Secondaryをen-GBにする補助案(Primary綴りは制御不可、X逆方向問題)→将来案として記録。
- OF-14[情報] API 0円、辞書ロード0.24秒(固定表でさらに短縮)、効果=c12型1件あたり約1.1円・10.6分・脚本改変1か所を防止。
