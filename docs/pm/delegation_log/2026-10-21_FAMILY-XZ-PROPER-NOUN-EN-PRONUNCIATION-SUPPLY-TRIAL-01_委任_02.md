# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_02(Opus条件Aレビュー[OF-PNEP-R-01〜12]のFable照合結果=**修正後Go**。設計書を修正→Trial harness実装(Trial専用、Production非配線)→無課金検証→有料検証(圧縮)→結果整理。到達上限=Trial結果(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の材料。最終ラベルはFable)。Production採用はユーザーのみ)。
並行agent: `FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01`(①是正。`er006_preprod_hardening_01_validation.py`等を修正中、完了時にcommit/push)。**本委任はProduction codeを触らない**。SSOT共有プロトコル(OPEN_ITEMS OPEN-434行/REPORT_LEDGER/ACTIVE_TASK/Opus台帳: 編集直前`git status --porcelain`+再Grep→自分の行だけ→即add/commit)。

## 性質/到達上限Status/禁止事項
- 性質: Offline Trial(Trial専用経路`er089_*`、Trial用Ledgerコピー、Production非配線、既存TTS音声・正式記事成果物・本物のLedger/HR queue/telemetry/cost log/Master Storeへの書込禁止)。
- 費用: 本Trial上限(T-3 Cap)=**JPY200**(Opus R-10採用: Azure A/Bは各条件1回+差異があったwavと決定性確認2本のみ2回目→約22〜26呼出≒JPY55〜60/研究 腕A+B≒JPY35〜45/検出LLM≒JPY5〜20/**腕N[TTS極小]は実施しない**[TTS生成禁止、LINE→LionはCMU代表発音不一致でNG維持が既に示せる])。見積中央≒JPY100〜125。承認区分C(ユーザー承認済みTrial、300円以下)。日次はS0で実測、超過見込み時は事前にSTOP。設計外の有料呼出(研究APIの裏発火等)は**0件**であること(R-01)。
- 禁止: 判定基準・同音等価ルールの拡張(J3は測定のみ)、カタカナ読みからの英語発音推定・登録(J7はTrialでは適用せず証拠収集のみ)、既存Ledgerへの書込、Production code/Prompt/設定変更、TTS生成、`git add -A`等。
- 依存: 必須ケースK3(byUs→Bias+story-making→storymaking=PASS)は①是正の反映が前提。**有料検証とK3の判定は、①のcommitがorigin/mainに到達してから**(`git log origin/main --oneline -20 | findstr MULTI-DIFF`で確認、未到達なら無課金工程を先に進め、最大60分待っても未到達ならSTOP報告)。実行時は①のcommit shaをresults/設計書に固定記録。
- 最新モデル原則(25節): 検出LLM=gpt-6.1-sol本命(記事単位1回呼び、R-12)+luna比較1回。研究=腕A OpenAI web_search(gpt-6.1-sol)/腕B Perplexity(現行資産、最新世代をS0で確認)。`pricing_snapshot.json`にsolが無ければS0で単価を登録(出典URL付き)。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PRONUNCIATION-SUPPLY-TRIAL-01 委任_02」を含む最新index)。check結果1行。T-2: TTSなし。

## Opus台帳更新(11-5、必須)
`docs/pm/`配下の既存Opus台帳(Grep `OF-PLW-J-01`で所在特定、同書式)へ OF-PNEP-R-01〜R-12 を追加: 各行=ID/重要度/要旨/Fable判定(下記)/反映先(設計書§・harness file:行)/Status(ADOPTED→実装後RESOLVED、NOT_ADOPTED理由、DEFERRED=J6/J7)。

## Fable照合結果(Opus所見の採否。Sonnetは変更しない)
- **ADOPTED(Go条件、実装必須)**: R-01(研究API stub化+HR queue/telemetry/cost logのTrial隔離+test固定)、R-02(同一性検証は`evaluate_attempt_with_cascade`[M1有効]経由・既存転写注入・条件切替ごとに`_reset_m1_freeze_cache()`+`LEDGER_PATH`切替・`candidate_set_hash`記録、Z1は変化集計へ分離)、R-04(V1'=source URLをHTTP取得しquoteの本文一致を確認、不可なら`UNCONFIRMED_SAFE[source_unverifiable]`、擬似造語Zorblefluxで落ちることをtest)、R-06(V5の拒否権はEN発音情報ありかつ品質基準を満たすentryのみ。low/汚染/ja_reading_katakanaは拒否権なし。共存時のM1候補集合を記録)。
- **ADOPTED(推奨)**: R-05(漏れ測定: 過去run全EN segment本文にTrial Ledgerで`get_hint_for_text`を再計算し、新規entryごとの「本来の記事以外での発火件数」を集計[費用0]。CMU収録一般語で公式発音=CMU代表発音の語[LINE]は「登録不要(CMU層で足りる)」案を本命とし、登録した場合の漏れ件数も測る)、R-08(効果仮説を「Azureの多語化(Buy Us/by us)をbyUsへ寄せられるか」に絞って§5-2に明記。腕M[綴りのみ直接供給]は「Production関数経由ではない」ラベルで区別)、R-09(K5投票者=Primary既存転写/Azure PL無/whisper mediumの3つ、Azure PL有は投票から除外、同系統ASRの一致を独立証拠と呼ばない、AMBIGUOUSはPASS扱いにせず試聴要否報告)、R-10(Azure呼出削減、er084負例は新PL語を含むものだけ再実行し見積に計上)、R-11(a:複数語surfaceはPL=句全体/M1=語ごとの扱いを明記 b:Z人名のCMU収録をS0で`pronouncing`確認 c:Family横断漏れはR-05で測定 d:所有格Melos'sをZ1に1件)、R-12(D1に「Ledgerにja_reading_katakana entryのあるLatin語」「JA側Gate検出の未知Latin語」規則を追加、D2は記事単位1回を本命)。
- **DEFERRED(判断候補、Trialでは適用しない)**: J6(PL/M1用の取り消し手段+自動/人手entry区別[OPEN-339]=採用前提条件)、J7(権利者の公式な日本語読みが英単語と一意対応する場合の登録可否)。K1がbyUsで`UNCONFIRMED_SAFE`になった場合は「安全終了・要件未達」として記録し、J7の証拠(PR TIMES等の原文該当箇所・英語情報源の有無)を集める。
- R-07の別件(記事B本文"It is pronounced 'bias.'"がWriterのカタカナ由来推定である可能性)は、Research Ledger(`er019_output/manga_ai_chat_byus/run_byus_01/research_ledger/verified_fact_ledger.txt`)の該当Fact(読み「バイアス」の帰属)を引用して事実関係のみ記録(本Trialの範囲外、Fableへ報告)。

## 手順
S0. `git status`件数、daily cost、T-0、①到達確認、`pricing_snapshot.json`のsol/Perplexity単価確認・登録、Z人名のCMU収録確認(pronouncing)、Research Ledgerの格納場所特定。設計書を`TRIAL_DESIGN_01.md`末尾「v02(Opus反映)」節として追記(本文は書き換えず、変更点をID付きで)→commit(有料前)。
S1. harness `er089_proper_noun_en_pronunciation_trial_01_{lib,run,eval,test}.py`: Trial Ledger(コピー)・研究API stub(腕A/B以外で呼ばれたら記録して失敗を返す)・HR queue/telemetry/cost logのTrial dirへの隔離・M1 cache reset・candidate_set_hash・Azure SDK診断ログから`speech.context`(dgi.Items/bias)を呼出ごと1行記録・validator V1〜V6+V1'・D1/D2検出器。test(API 0): stub発火検出、隔離先、V1'がZorblefluxで落ちる、V5拒否権の限定、M1 reset。
S2. 無課金工程: D1検出(記事B本文/メロス/開いた窓)、漏れ測定(R-05)、Ledger有/無の同一性検証(既存転写注入、M1有効、K2/K5/K6/Z2)、Z1変化集計(①到達後に実施してもよいが判定関数の変更はZ1に影響しない想定=結果で確認)。
S3. 有料工程(①到達後): D2検出(sol記事単位1回+luna 1回)、研究(byUs/LINE/Z人名のうちEN未登録のもの: 腕A・腕B各1回ずつ、上限8語)、登録(validator通過分のみ、Trial Ledger)、Azure A/B(既存wav 11本×PL有無×1回+差異wav・決定性2本の2回目)、K3(①反映後の判定関数で既存転写を再判定[API 0]+part1 att1 wavの実ASR1回)。費用を呼出ごとに記録、Cap監視。
S4. 評価(事前固定ラベル): 必須ケース表K1〜K6/Z1/Z2の結果、効果(Azure多語化の件数変化)、誤NG/誤PASS(既存PASS音声・er084負例)、漏れ件数、QCD(1語あたり費用・時間、70円への影響)。Sonnet所見は判断材料、ラベルはFable。
S5. `TRIAL_RESULT_01.md`、OPEN-434行頭Status更新(`TRIAL_DONE_PENDING_FABLE`)、Opus台帳、REPORT_LEDGER、ACTIVE_TASK。secret scan→明示add(設計書・harness・test・er089_output[Trial Ledgerコピーはサイズ次第、sha記録]・delegation_log・台帳・SSOT)→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PNEP2.md 上書き。ユーザー原文§7の順)
1.記事B実例の再現結果(K3ほか、PASSすべきケースがPASSしたか、NGケースがNG維持か) 2.(①は別報告)②との接続点 3.検出・公式発音確認・Ledger登録・PL投入・重み2.0の証拠(speech.contextログ引用) 4.ASR改善結果(Azure多語化の変化)と誤PASSリスク・漏れ件数 5.費用(実測・呼出数・出典)・時間・量産影響 6.Fable評価用材料(Opus Go条件4点の反映証拠、設計外API呼出0の証拠) 7.判断候補(J6/J7/K1未達時/J3測定結果)+commit・raw URL+4行判定。