FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_03-FABLE-EVAL-SSOT-20261023

# 委任_03: ①固有名詞(RET)・②英米綴り(UKUS)のFable独立評価=VALIDATEDをSSOTへ反映し、採用判断UDRを起票(API 0、コード変更0、約15分)

前提: `docs/pm/RESULT_PACKET_ASRQ_PN2.md`、`docs/pm/RESULT_PACKET_ASRQ_UKUS2.md`、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/{PN,UKUS}/TRIAL_RESULT_01.md` を読む。

## T-0
委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_03.md`(index 354以降、先頭MARKER一致)。ACTIVE_TASK自分の行のみ(並行: FX-KP-GM Trial、FAMILY-Y 委任_07。他ファイル不可触)。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## Fable独立評価(そのまま記録)
- **②英米綴り(OPEN-471)= VALIDATED(Fable 2026-10-23)**。根拠: V1〜V8全PASS(90対両方向同値、意味差の新規誤PASS 0[意図したAMB一方向tyre→tireのみ]、保存6,137行PASS→NG 0、c12は Primary/Secondary/KP投票/Store guard/rejudge×X/Z 30セル全てOFF=NG→ON=PASS、Production 9 module・golden不変、API 0、p95 0.1ms)。V5の指標置換(ホールドアウト再現76.8%→V5b外部英国語テキスト被覆94.8%/意図除外除き99.4%+breame照合94.6%)はTier-2非活性・SCOWL level≤70採用に伴う定義上の帰結で、安全側(救済を狭める)の変更としてFableが受理。残存リスク=発音も違う対52件がスペルだけでPASS(pron_differs監査で監視)、AMB一方向168対、語尾差・CMU未登録対は従来どおりNG。
- **①固有名詞(OPEN-472)= VALIDATED(条件開示付き、Fable 2026-10-23)**。根拠: SC-1/2/3/4/5/5b/6/8/10 PASS、HR queue 88(初見語再現)でアラーム付き受理36→56・証拠欠落9→0・span跨ぎ16→3(残3は意図どおり不受理)、退行0、Bertie型21/21・Bertie 3/3受理、新規受理20イベント29 diffをFableが目視し意味変更0・一般語誤読受理0を確認(全て固有名詞のみの差、実誤読型6事象は2026-10-22承認方針内のアラーム付き受理)、受理境界不変(表が空のときer103とバイト一致)、API 5.30円。条件開示: SC-7最大0.168円/記事セット(Z長編1群のみ。平均0.059〜0.067円、70円比0.24%で実害なし)、SC-9 text別安定性0.90未満4/27(失敗方向は安全側=証拠が減るだけ、和集合でも非固有名詞への付与0)。RET-3のカンマ連結許容(語を挟まない句読点のみ)はOpus趣旨の範囲内としてFable受理。改善候補(a)(b)は採用時の配線設計で検討(今は追加Trialしない=Charter 1)。
- 区分: ②=既存er109同値層の拡張(X/Z限定・既存hook)。①=LLM NER新証拠源+RET-3(既存G3の変更)は**新仕様候補**で、RET-3は11-7限定例外の対象外の可能性が高い→採用時は「ユーザー正式採用→Production実装(Opus条件C)→runtime evidence」の経路。

## 反映
1. OPEN-471 Status=`VALIDATED(Fable 2026-10-23)_PENDING_USER_ADOPTION`、OPEN-472 同(条件開示付き)。OPEN-465(『開いた窓』)に「①②VALIDATED。採用後に Bertie 4clip再生成(約2〜5円)+c12は既に音声forte(採用後も再生成は別判断)→gate→assemble→公開差替え」を追記。
2. UDR 1件起票(既存最大+1): 件名=ASR包括対策①②のProduction採用判断。選択肢: ①RET(LLM NER証拠源+RET-3)をX/Z正式経路へ採用するか(採用時はOpus条件Cレビュー→Production実装→runtime evidence、費用+0.06〜0.17円/記事セット)、②UKUS綴り同値層をer109へ採用するか(API 0)、③『開いた窓』の再開方法(採用・配線後に正式経路で再開[推奨]/採用判断前に個別対応はしない[ユーザー既決])、④c12「forte」音声の扱い(②採用後に原稿「speciality」で再生成するか/forteのまま)。推奨は書かない(Fable報告側で付す)。
3. DECISION_LOG(Fable評価エントリ①②)、REPORT_LEDGER、CURRENT_SPEC: 既存の「ASR包括対策 er109 v1」「PNAP」節に「Trial候補(VALIDATED・未採用)」として1行ずつ参照を追加(仕様本文は変更しない)。
4. 明示add、secret_scan hits=0、`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_ASRQ3.md)
UDR番号・commit・raw URL。RESULT_PACKET 4行+「判定整合: 重大NG=なし」。