FABLE-DELEGATION-MARKER: PNPS-OPUS-REFLECT-E1b-委任_04-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_04 [E-1b]: Opusレビュー(OF-PNPS-S1-01〜10、S2-01〜09)のFable採否反映。Stage 1=module/test/設計書の修正(Production配線はまだしない=D-2完了後のE-2)、Stage 2=計画v4。API 0・JPY0)

## 0. 運用ルール・並列注意
他agent稼働中: (D-2)`er078_*`/`er006_secondary_asr_01.py`/`er003_*`/`er019_family_x_kp_en_k2_store_01.py`/`er019_family_x_audio_production_runner_01.py`/`er063_*`/CURRENT_SPEC ASR節、(記事A調査)`docs/research/FAMILY-X-B3-*`/`run_pp_02/audit`。あなたは`er097_*`・`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`・OPUS台帳・OPEN-441行・REPORT_LEDGERのみ。Production .py編集禁止。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。有料API/Web取得禁止(R0収録率等の0円オフライン測定はローカルデータ・既存dumpのみ可。HTTP取得は禁止)。

## 1. Opus所見とFable採否(`docs/pm/OPUS_FINDINGS_LEDGER.md`へ登録、採否を付す)
### Part 1 Stage 1(配線着手=条件付き可。条件=S1-01/02/03/Fを配線前または同時)
- S1-01 [Major] **採用**: 設計書§0-3/§3-4を「判定ロジック・閾値・自動PASS条件は不変。将来のLedger蓄積(Phrase Listの語句・M1のC2候補)は**減る方向にのみ**変わり得る(一般語entryを作らない/否定記録期間中は再調査しない/別typeのentryがあれば調査用entryを作らない)。保存データでの実発生0件」に修正し3経路を開示。
- S1-02 [Major] **採用**: 副作用(調査API・Ledger登録・sidecar書込・HTTP取得)はすべて`_resolve_unresolved_entity_for_review`の内側からのみ到達。呼出側はmockが`None`を返しても従来どおりstubで動く。既存test(列挙: `er006_secondary_asr_01_test.py:125,354,501`、`er006_secondary_asr_01_m1_wiring_test_01.py:119-184`、`er020_*`、`er026_*`、`er078_*`、`er096_*`、`er057_*`、`er006_pronunciation_ledger_invalid_entry_remediation_01_test.py:108-122`)のmock隔離が壊れない配線設計へ書き直す(E-2で実装)。
- S1-03 [Major] **採用(今回er097で修正)**: 否定記録get/put・V1'照合・HR表示キー生成の例外はすべて捕捉し従来動作へ(調査APIの例外は従来どおり素通し)。一時ファイル名にpid/uuid。`is_safe_url`は`Exception`全般でFalse。
- S1-04 [Minor] **採用(er097修正+test 2件)**: 調査用type entryが存在する場合は従来どおり先に処理(返す/隔離ならNone)。手順3の対象を調査用type entryに限定。
- S1-05 [Minor] **採用**: 採用entryのtypeが調査用typeでない場合、HR表示に「同綴りの別entry(type=○○)の情報。同一対象かは未確認」を1行追加。
- S1-06 [Minor] **採用(E-2)**: stubの`ambiguity_note`を省略理由別(一般語/否定記録/隔離entry)に変える。
- S1-07 [Minor] **採用(er097修正)**: 照合表記5文字以上、`æ`等を許可、空白を残した正規化テキスト上で語境界つき照合。
- S1-08 [Minor] **採用**: module定数1個`PRON_SUPPLY_STAGE1_ENABLED`で全体ON/OFF(項目別定数は併用可だがtestは全ON/全OFFのみ、サポート組合せを明記)。
- S1-09 [Minor] **採用(E-2)**: Ledger `upsert`の素通し3キーは「今回渡されたentryにある場合だけ」書き、既存entryから引き継がない。キー無し呼出のバイト一致test。
- S1-10 [Info] 否定記録の即時無効化ロジックは残置可(害なし)。sidecar fileは`er006_output/`配下でgit管理**する**(Fable判断: 再現性のため。サイズが大きくなれば見直し)。
- 論点B **Fable判断**: Phrase List間接影響は許容。加えて既存の一般語entry `mini` はOPEN-436の枠で**隔離する**(E-2で実施、前後のPhrase List差分と判定差分0を記録)。
- 論点E **採用**: 実調査1回・実URL取得は、Ledger/sidecar pathを一時コピーへ差し替えて行う(架空語をProduction Ledgerへ登録しない)。4,032ペア判定差分0は回帰確認に留まる旨を明記。「自然発生は未観測」を残事項として明記。
- 論点F **採用(命名・報告)**: V1'は「出典ページ照合(名称・発音表記の出現確認、弱い確認)」と呼び、保存キーは`source_page_check_v1`。ユーザー報告では「ご承認の引用実在確認のうちStage 1で実施できたのは弱い照合のみ。本来の引用確認はStage 2の調査形式変更(Prompt変更で承認が必要)と同時に行う」と明示。
### Part 2 Stage 2(計画v3=修正後提出→v4)
- S2-01 [Major] **採用**: 「共通部分が空または1候補のみなら不発」を「estimatorが1つだけの場合は不発。共通部分が1音素列に収束するのは受理条件」に書き直す。
- S2-02 [Major] **採用**: 接続点を(a)既存1:1同音判定と(b)L1(多語)の2箇所として記載。`expected_phoneme_provider`は未実装の設計名と明記。両方とも「承認済み安全条件の変更」として判断3に含める。
- S2-03 [Major] **採用**: ⑤を「CMU収録かつ衝突フラグなしの語には適用しない」へ。Trial P2の語は現行で実際にHRへ行っている辞書外語(Toteme/Khaite/Altuzarra/Zabelina等)から選ぶ。byUs例は「現行で既にPASS(BI3)、Stage 2の差分は出ない」と明記し、判定例として別語(例: Toteme)を主例にする(byUsはユーザー指定の具体例として併記)。
- S2-04 [Major] **採用**: O0に「保存データでHRに到達したsegmentのうち警告付きPASSに変わる件数」を必須測定項目とし、Trial継続の判断条件に加える(0件なら効果なしとして報告)。
- S2-05 [Major] **採用**: ESTIMATEDはTTSヒント注入・M1のC2・Phrase Listへ供給しない(別field or 隔離フラグ)。循環を遮断。
- S2-06 [Major] **採用**: E1単独成立は明示的境界(CamelCase/ハイフン/空白/数字)がある場合のみ。推定とTTSの非独立性、E2・E3の非独立性を残留リスクとして開示。
- S2-07 [Minor] **採用**: 事後試聴NG→推定失効の取り込み経路を設計に含める(Trial範囲外なら明記)。
- S2-08 [Minor] **採用**: R0の最初の段に「記事自身の出典資料(Writer取得済みsource本文)から pronounced/IPA/`/…/`を機械抽出(0円、対象同定が自然)」を追加。Forvo/YouGlish非推奨は維持。
- S2-09 [Minor] **採用(Fable判断)**: 既定方式=代替A(R0+E1、必要時E2/E3)、R1は後から追加。P1(R1実測)は後回しにし、その費用をP2の誤発音種類追加(1語あたり誤発音2種=9本、約46円)へ。Cap案JPY100内。**R0収録率とG2P可否の0円測定は、HTTP取得を伴わない範囲(ローカル既存データ・ライブラリimport可否)のみ本委任で実施可**。HTTP取得が必要なR0収録率はTrial O1(ユーザーGO後)。
- ユーザー判断事項(報告用に整理): (1)Stage 2 Trial実行とCap(JPY100案)/(2)既存1:1同音判定とL1の承認済み安全条件の変更(推定・公式発音をcanonical側基準に使う=1837(B)例外)/(3)G2Pの本番依存導入(Trial内利用はFable可)/(4)V1'弱い照合の報告(判断ではなく承認範囲の正確な伝達)。

## 2. 作業
1. er097修正(S1-03/04/05/07/08)+test追加→全PASS。Production .py無変更を`git diff HEAD`で確認。
2. `STAGE1_IMPLEMENTATION_DESIGN_01.md`修正(S1-01/02/06/09/B/E/F)。E-2配線手順を「mock隔離を壊さない」形に書き直す。
3. `PLAN_01.md`にv4節、`PLAN_SUMMARY_01.md`をv4要約へ(S2-01〜09反映。主例=辞書外語、byUs併記。O0効果測定の必須化。代替A既定。P2拡充。Cap JPY100)。G2P import可否(ローカル)の確認結果を記載(未導入なら「未導入」)。
4. SSOT: OPUS台帳(OF-PNPS-S1-01〜10、S2-01〜09)、OPEN-441履歴追記(`STAGE1_DESIGN_REVIEWED_WIRING_PENDING_D2 / STAGE2_PLAN_V4_PENDING_FABLE`)、REPORT_LEDGER行。
5. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_04.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-OPUS-REFLECT-E1b-委任_04-20261022` を含むAgent tool_useの0始まり通番、258前後)。
6. commit(対象のみ)→push→到達確認。`docs/pm/RESULT_PACKET_PNPS4.md`へ報告(反映表・test結果・v4要約[ユーザー§7 B 8項目]・E-2への引継ぎ・RESULT_PACKET 4行・JPY0・raw URL)。

## 3. 禁止
Production .py編集、合否判定基準の変更、有料API/HTTP取得、Trial実行、D-2/記事A調査の担当ファイル編集。