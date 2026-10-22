FABLE-DELEGATION-MARKER: PNAP-IMPL-委任_02-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02: Opus条件Aレビュー(OF-PNAP-P-01〜15)の必須7項目+推奨項目を設計・moduleへ反映→校正再実行→**Family X/Z正式経路へ配線**→Regression→runtime evidence(日次残内なら本日、超えるなら翌JST日)→SSOT。ユーザー承認済み`APPROVED_FOR_PRODUCTION`の配線。`PRODUCTION_WIRED`判定はFable)

## 管理ID
PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02(OPEN-450。並行: (1)`FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_03`が`er019_family_x_audio_production_runner_01.py`のKP stage(約:400-440)を編集中→**本委任はer019の編集を、その委任のcommit(`git log --oneline -20`で`FX-KP-FAILCLOSED`を確認、またはRESULT_PACKET_KPMP3.md存在)を確認してから行う**(それまでは設計反映・module・er006/er063側を先行)。(2)`KP-THREE-ASR-MAJORITY-PRODUCTION-01`(er104)はOpusレビュー中で配線は本委任の後。(3)`KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01`(er105)は設計中・Production未編集。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/到達上限Status/禁止事項
- 性質: Production配線(ユーザー承認済み)。到達Status: `WIRED_PENDING_FABLE`(runtime evidence取得まで。取得できない場合は`WIRED_RUNTIME_EVIDENCE_PENDING`)。`PRODUCTION_WIRED`宣言はFable。
- Opus Gate: 条件A実施済み(本委任で反映)。配線後の再レビューは内容が変わった場合のみFableが判断。
- 修正範囲(11-8): 範囲内=設計書§2/§5/§7更新、`er103_*`改修+test、配線点(`er006_secondary_asr_01.py`挿入点1146付近[adapter]、`er019_*`runner/validation_inheritance、`er063_*`、`er006_pronunciation_ledger_01.py` additiveキー、`er006_master_audio_store_01.py`のscope外ALARM非再利用、完成報告生成)、旧ルール整理(撤去0・Open Items範囲縮小の文案)、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新。範囲外=KP(`dual_required=True`)経路・日本語・Family A/B/C・判定基準の緩和拡大・共有`er003_v1_n3_01_tts_generate.py`の編集(設計どおり)・Writer側ルール。
- 時間見込み(8-X): 約6〜8時間(Opus反映+校正2h/配線X/Z 2.5h/Regression 1h/evidence 1h/SSOT 0.5h)。並列: 設計反映・module・testとer006/er063配線は先行、er019は上記確認後。
- 費用/日次: 当日既使用 約JPY878(出典 RESULT_PACKET_KPMP2)。runtime evidence見積(設計§7)約80円(X Khaite/Toteme/Altuzarra segment約8+Z Melos clip約10+Stage 1調査約20+予備)。**実行前に`paid_calls`で再見積し、878+見積が1,000円以内なら本日実行、超えるなら翌JST日(2026-10-23 00:00以降)に実行**(日次境界回避ではなく上限遵守)。Guardrail(T-3) Cap JPY100(到達だけで自動STOPしないが超過見込みで有料呼出停止・報告)。承認区分: C。`TTS_EXECUTION_MODE=STANDARD`。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない(特に`er019`はhunk単位で自分の差分だけadd: `git add -p`不可なら、相手commit後に編集)。有料runの再起動禁止・STOPセンチネル確認後に開始(rc≠0なら起動しない)。過去記事・保存音声の再生成禁止。推定発音のTTS供給禁止。

## 前委任(委任_01)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_USER.md`): 「固有名詞の発音は可能な範囲で改善するが、発音不一致だけを理由にProductionを停止せず、Human Reviewにも回さない。代わりに必ずアラームを記録・報告する。」到達目標=X/Z双方で`PRODUCTION_WIRED`。
- 最終成果物: `docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/{INVESTIGATION_01,CONFLICTS_01,IMPLEMENTATION_DESIGN_01}.md`、`calibrate_replay_01*.`、`er103_proper_noun_alarm_policy_01.py`/`er103_pronunciation_tts_supply_01.py`/`er103_proper_noun_alarm_policy_test_01.py`(52 PASS)。commit dde6bed6e。Production未編集。
- 証拠: 挿入点1箇所(`er006:1146`)、校正88イベントで受理45/不受理43、衝突a〜m整理、既定OFF。
- 一致・不一致: 設計範囲=一致。Opusレビューで安全条件の抜け道3・再利用2・供給/報告3の計8件(必須7)が検出=設計の修正が必要(本委任)。
- 判定: ACCEPTED(設計段階として)。判定整合: 重大NG=なし/主因=なし/是正対象=Opus必須7項目/STOP理由=なし/提示=B階層承認候補(ユーザー、別途Fableが提示)。

## Opusレビュー(OF-PNAP-P-01〜15)のFable採否(全文=本委任文末尾に転記、`docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md`へ保存し、`docs/pm/OPUS_FINDINGS_LEDGER.md`にOF-PNAP-P-01〜15を登録[FABLE_DECIDED→IMPLEMENTED])
- **必須(全て採用)**: P-01(G1に`p3_entry=="p3_primary_ng"`∧dualなし)/P-02(Title Case・題名・コロン/引用符直後の大文字は根拠にしない。CMU収録語はLedger/CMU未収録/単独ALLCAPSのみ)/P-03(Primary・Secondary双方のASR側句が全token一般語[CMU∧zipf≥4.0]なら不受理=HR。類似度は綴り4文字以下なら≥0.5、ASR語数≤原稿語数)/P-05(i)継承再判定にALARM分岐=保存転写へ現行定数で`evaluate_alarm_eligibility`を再評価、`_j11_adopted_judgement`はALARM時Primary転写採用 (ii)scope外(A/B/C)ではStoreのALARM entryを再利用せず再生成 (iii)entryに`tts_input_text`と供給判断を保存し再判定に使用/P-06(供給置換は大文字小文字区別。小文字形が一般語なら大文字始まりの出現のみ)/P-07(A階層自動供給は「人のtts_respelling」または「hintが検証済み引用のIPA/respellingと整合」に限定、ホストはラベル単位一致、Wikipediaは整合条件付きでA可)/P-08(完成報告へ機械的に埋め込み[run summary/assembly audit→RESULT_PACKETは生成物から転記]、ALARM state数とreport件数の一致検査、report不在時は「アラーム集計失敗」を明示[制作は止めない]、hookはfinallyでSTOP/途中失敗経路でも実行、Xは記事単位集約、継承recordは現runのlocation/segmentで表示)。
- **推奨(採用)**: P-04(Secondaryだけの非固有名詞差に上限: ≤2件・内容語2語以上の連続脱落は不受理)/P-10(scopeはcontext manager+finallyで解除、test)/P-11(完成報告に「発音供給の適用一覧」節、`compute_ledger_hits`の供給前text注記、Reicher→Rikerを`supply_map`へ登録)/P-12(er019の未commit差分を確認してから配線)/P-13(境界外で固有名詞のみ不一致なのにHRに残る件数を校正内訳と完成報告で区別、JA対象外を未解決事項に明記)。
- **P-09(初回attempt受理の妥当性)**: 採用=0円で保存`attempts_log`/HR queueから「固有名詞のみ不一致がslot2/3で解消した率」を語別に集計し、**Fable規則**: 全体でslot2解消率≥25%なら`ALARM_ACCEPT_MIN_SLOT=2`(1回だけ再試行してから受理、+約1円/件)、未満なら1(初回受理)。集計値と適用値を報告(数値根拠付き)。
- P-14(旧ルール: 撤去0、OPEN-318/327/330/331/335は「固有名詞のみHR」部分を範囲縮小して継続)=採用(文案をSSOTへ)。P-15(test不足観点)=採用(全て追加)。

## 実行内容
1. 設計書更新(§2/§3/§5/§7/§13→反映済み欄)+`er103_*`改修+test追加(P-15の観点全て)→`calibrate_replay_01.py`再実行し受理/不受理の新数値・Muse系の除外を確認(`calibrate_replay_02_result.json`)。P-09集計script(0円)。
2. 配線(Production): 設計§5の5-1〜5-10をOpus反映版で実装。順序: er006 adapter→Ledger additive→Store scope外非再利用→er063(Z)→validation inheritance→er019(X、相手commit確認後)→完成報告生成(X/Zのassembly audit→`audit/pronunciation_alarms.json`・`audit/operator_alarm_report.md`・run summaryへの埋め込み、公開`index.html`非露出)→flag既定ON(`PROPER_NOUN_ALARM_POLICY_ENABLED=True`、`TTS_SUPPLY_ENABLED=True`[供給対象0件でも配線は有効])。
3. Regression: `run_project_regression.py --pattern "er006*_test*.py"`,`"er078*_test*.py"`,`"er011*_test*.py"`,`"er019*_test*.py"`,`"er063*_test*.py"`,`"er026*_test*.py"`,`"er103*_test*.py"`,`"er097*_test*.py"`,`"er096*_test*.py"`。既存失敗(er011 DefaultByteParity 3件・er007 azure import)は委任_03の切り分け結果を参照し本件由来でないことを明記。4,032ペア/HR79行のON/OFF差分(Stage 1配線時の手法)を再利用し、KP・JA・A/B/Cで差分0を確認。
4. runtime evidence(費用条件は上記): X=Khaite/Toteme/Altuzarraを含む記事のsegment限定run(`--only-segments`、正式runner、新run dir、旧run無変更)で (a)固有名詞不一致→ALARM受理→HR Lock 0→完成、(b)アラームが`audit/`と完成報告に出る、(c)公開index.htmlに出ない、(d)KP(dual)には不適用、を記録。Z=Melos clip限定(`--only-clips`)で同様。供給①の実発火はA階層/人承認B階層が0件なら「供給対象0件(Khaite B階層は人承認待ち=UDR)」として記録し、供給機構のunit/wiring evidence(mock)で代替することを明記。actual model ID・routing・判定記録を保存。
5. SSOT: CURRENT_SPEC(委任_01のRESULT_PACKET文案をOpus反映で更新し追記)、DECISION_LOG、OPEN-450=`WIRED_PENDING_FABLE`(+Opus反映・校正新数値・evidence)、OPEN-318/327/330/331/335の範囲縮小注記(各行末尾1句、Statusは変えない)、OPUS_FINDINGS_LEDGER、REPORT_LEDGER。UDRは編集しない(B階層承認候補はFableが提示済み)。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: PNAP-IMPL-委任_02-20261022`を含むAgent tool_useの通番、285前後。先頭行で一致確認)。
6. 段階commit(設計反映+module→配線→Regression→evidence→SSOT)→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_PNAP2.md`(ユーザー§8の1〜8順、7はFable欄)。

## 事前指定Read/Grep
- Read: Opus指摘の該当箇所(`er078_asr_unified_judge_01.py:446-471,586-587`、`er006_secondary_asr_01.py:1053-1066,1140-1200`、`er103_proper_noun_alarm_policy_01.py:100-160`、`er103_pronunciation_tts_supply_01.py:100-215`、`er019_family_x_validation_inheritance_01.py:296-335`、`er006_master_audio_store_01.py:122-193`、`er078_reuse_value_guard_01.py`、`er019_family_x_audio_production_runner_01.py` Grep `tts_safe_news_en|compute_ledger_hits|PASS_WITH_WARNING`、`er063_family_z_audio_01.py:750-770,1160-1180,1710-1770`)。
- Grep: `attempts_log|slot` in `er011_*.py`(P-09集計の元データ)、`human_review_queue.jsonl`の固有名詞行(委任_01の校正入力を再利用)。

## Git
- 明示add: 変更した各ファイル(他agentの差分を含めない。er019は相手commit後)。commit例: (1)`PNAP 委任_02a: Opus条件A反映(P-01〜P-15)+校正再実行、module/test更新、Production未編集` (2)`PNAP 委任_02b: 固有名詞アラーム受理+TTS供給をX/Z正式経路へ配線(adapter/Ledger/Store/継承/完成報告/非露出)、Regression PASS` (3)`PNAP 委任_02c: runtime evidence X/Z+SSOT、WIRED_PENDING_FABLE`。

## 報告(RESULT_PACKET_PNAP2.md)
ユーザー§8順(1 X/Z Status/2 発音改善の具体例[供給0件なら明記]/3 HRなし完成のruntime evidence/4 完成報告のアラーム表示例/5 既存品質条件維持の証拠[KP・JA・A/B/C差分0、負例]/6 量産単価・速度/7 Fable欄/8 未解決[JA対象外・B階層承認待ち・1日15作品頻度未検証])+Opus反映一覧・校正新数値・P-09集計値と適用slot・費用実測(出典)・実行コマンド・RESULT_PACKET 4行・raw URL。

## 付録: Opusレビュー全文(逐語転記して保存すること)
[Fable注: 以下はOpus(opus-consultant)の所見全文]
結論: 条件付きで実装へ進んでよい。骨子は妥当で、既存Gateとも大筋で整合している。骨子とは、全ての救済層を通った後の`NG_BOTH/secondary_not_accepted`だけを入口にし、leafへはstatus OKとして返すため、HR Lock・queue・`approve_regenerate`を構造的に経由しないこと。flag×run scopeでFamily A/B/Cから切り離す点、語の脱落・数値・否定・KP・日本語をfail-closedにする点も妥当。ただし、受理の入口と固有名詞の判定根拠に「固有名詞の不一致だけ」を超えて緩和してしまう抜け道が3点、再利用経路にscope漏れと整合の不備が2点、TTS供給と完成報告の保証に穴が3点ある。
OF-PNAP-P-01 Major 入口条件が「Primaryが本当にNG」に限定されていない(er078:446-471,586-587; er006:1053-1066)。G1に`audit["p3_entry"]=="p3_primary_ng"`(かつdualなし)を追加。test: force_secondary×CMU-alt PASS×Secondary一般語差→不受理、primary_length_ng→不受理。
OF-PNAP-P-02 Major 文中大文字の根拠がTitle Caseで一般語を固有名詞扱い(er103:146-159、TOPIC_INTRO題名)。題名部分・連続大文字2語以上・コロン/引用符直後ではCMU収録語に大文字だけの根拠を認めない。test: 題名内一般語→不受理。
OF-PNAP-P-03 Major 両ASRが高頻度一般語に揃う場合(Muse→use系4件)は不受理。低頻度語への崩れ(kite/mellow/totem/mink)は承認の中心例として維持。類似度は綴り4文字以下で≥0.5、ASR語数≤原稿語数。校正再計測。
OF-PNAP-P-04 Info G3は許容。Secondaryだけの非固有名詞差に上限(≤2件、内容語2語以上の連続脱落は不受理)を推奨。脱落不受理は妥当。
OF-PNAP-P-05 Major (i)`rejudge_with_current_judge`は保存転写で必ずNG_BOTH→ALARM分岐で`evaluate_alarm_eligibility`再評価、`_j11_adopted_judgement`はALARM時Primary転写採用 (ii)Store共有でscope外からALARM音声が再利用され得る→scope外では再利用せず再生成 (iii)供給後PASS音声の再判定で元綴りと不一致→entryに`tts_input_text`と供給判断を保存し再判定に使用。
OF-PNAP-P-06 Major 供給置換のIGNORECASEで一般語(Nice/Muse/Gap)を書き換える→大文字小文字区別、小文字形が一般語なら大文字始まりのみ置換、test。
OF-PNAP-P-07 Major A階層自動供給のrespellingが検証済み引用と結び付いていない→人のtts_respelling、またはhintが引用のIPA/respellingと整合する場合のみ自動。ホストはラベル単位一致。Wikipediaは整合条件付きでA可。
OF-PNAP-P-08 Major 完成報告への掲載保証が手作業と例外握りつぶしに依存→機械生成報告へ埋め込み、ALARM数とreport件数一致検査、report不在時「集計失敗」明示(制作は止めない)、hookはfinally、Xは記事単位集約、継承recordは現runのlocation/segment。
OF-PNAP-P-09 Major(データ確認で解消) 初回受理の妥当性→slot2/3解消率を0円集計し`ALARM_ACCEPT_MIN_SLOT`をFableが決定。
OF-PNAP-P-10 Minor run scopeはcontext manager+finallyで解除。
OF-PNAP-P-11 Minor 供給の監査: 完成報告に「発音供給の適用一覧」、`compute_ledger_hits`の供給前text注記、Reicher→Rikerを`supply_map`へ。
OF-PNAP-P-12 Minor 設計書の行番号が古い(er019未commit差分、実際は1008/1407)。配線前確認。
OF-PNAP-P-13 Minor 境界外でHRに残る固有名詞のみ不一致の件数を区別表示。JA対象外を未解決事項に明記。
OF-PNAP-P-14 Info 旧ルール: HR投入経路は受け皿として必要、撤去0で妥当。OPEN-318/327/330/331/335は範囲縮小して継続。OPEN-371独立に同意。
OF-PNAP-P-15 Info test不足観点(P-01/02/03/05(i)〜(iii)/06、類似度0.40前後、scope解除、Z clip IDのFULL_STORY解決、Storeをまたぐ再利用、配布ファイル一覧に`audit/`非含有)。runtime見積約80円・翌JST日・7-7自律は妥当。供給の実発火証拠はA階層0件・Khaite B階層のままでは取れない(ユーザー承認操作)。量産単価は下がる方向、P-09で再試行を残す場合+約1円/件で再計算。
ユーザー判断・操作が本当に必要な事項: B階層(媒体由来)の承認操作は仕様上「人間」が行う。Khaite→Kate(出典Nylon、Stage 2で8/8有効)の承認登録がなければ運用開始時の供給効果は0件。Fableが承認候補一覧を作りユーザーに1回確認するのが適切。その他は承認範囲内の技術判断。