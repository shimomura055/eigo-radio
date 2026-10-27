# EVIDENCE_PLAN_02 実API runtime evidence計画 v2(6セル、上限JPY150。GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S)

EVIDENCE_PLAN_01(全6経路・見積<=JPY40)を、(A)Std候補率実測(STD_CANDIDATE_RATE_01.md)と(B)元run実現性(EVIDENCE_SOURCE_CHECK_01.md)で具体化した版。実施は実装・test完了後(並行委任_02の後)。ユーザー§8の受入1〜11と「一部Family/levelのみでの全体完了判定をしない」は維持。本委任の実費=Std率計測JPY3.885(上限JPY7内)のみ。

## 1. 6セルと元run(copy-run方式A)
| セル | 元run(copy) | 非0の実証 | 採用件数の実証 | 期待候補 | 備考 |
|---|---|---|---|---|---|
| X Std | `family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1` | Std a2を実走。実測1(T2 INV)。**揺れ大**(同一本文で1→3) | 1件 | 1(1-3) | Std 0件に落ちたら「Xも0が起きる」と記録(Xは4/4記事で>=1) |
| X Adv | 同 | 既存Adv候補2を事前生成 | **2件(2件採用#1)** | 2 | r2(Adv 4件)は予備 |
| Y Std | `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01` | Std実測2(CMP+HEAVY) | **2件(2件採用#2)** | 2 | `style_profile.json`あり=現行世代 |
| Y Adv | 同 | 既存Adv候補2 | 1件選択(+別操作で0件=omit) | 2 | 0/1/2件のパターンを同runで網羅 |
| Z Adv | `melos/run_p2_evidence_r3` | 既存Adv候補1(REVIEWED) | 1件 | 1 | Zは候補最大1 |
| Z Std | 同(melos Std) | **非0は不可: melos Stdは4 call全て0=ZEROのruntime観測** | 0件 | 0 | 下記O-Zで非0を別途狙う |
| (0件) Z Adv/Std | `melos/run_p2_evidence_r4` | ZERO(NO_CANDIDATE_UNREVIEWED)をAdv・Std両方で観測 | 0件 | 0/0 | 0件経路の主証跡 |
| O-Z(任意) Z Std非0 | `the_gift_of_the_magi/run_sf_prod_01`(Std実測1) or `after_twenty_years/run_sf_prod_01`(1) | KP据置でStd 1件を実走 | 1件 | 1 | **旧世代run(Part 2/KP HR記録なし)**。go/no-goがNoなら下記「mockのみ」扱い |
- **非0がruntimeで観測できるセル**: X Std・X Adv・Y Std・Y Adv・Z Adv。**Z Stdの非0はO-Z成功時のみ。失敗/見送り時は「非0はmockのみ・runtime未観測」と明記し、全6セル完了と書かない**(PRODUCTION_WIRED判定はFable)。
- **0件セル**: Z Std(melos)・Z Adv(r4)は元runのまま観測(ZERO)。
- **2件採用の実証**: 最低1経路が必須 -> X Adv(r1)・Y Std(style_fix)の2経路。Zは候補最大1のためruntime不可(unit/mockのみと明記)。
- 3件目不可・上限(最大2件)は、フォームのPlaywright(受入3)で2件選択状態の3件目クリック不可を実画面で取る。

## 2. stage列(Family別。各runは新規copy名。公開・既存runは無編集)
| Family | 1) 候補+事前生成(実API) | 2) フォーム・確定(API 0) | 3) 再開・組立(追加API 0想定) |
|---|---|---|---|
| X | `er019_family_x_audio_production_runner_01.py --stage study_text --level both`(Std Step A''、Adv Step A''は再利用、各level事前生成。rc=4でHR待ち) | `export_form_data`相当 -> フォームdata -> Playwright -> `er128 confirm --from-form <payload> --run <run> --level a2/b1b --actor evidence --user-ref <委任文>` | 同stageを再実行(確定凍結、API 0) -> `--stage player --level both`(TTS/assembleはresume) |
| Y | `er121_family_y_runner_01.py --stages kp`(Std/Adv候補+事前生成、rc=4) | 同上 | `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify`(1起動。tts_*はresumeでAPI 0想定) |
| Z | `er026_family_z_fiction_production_runner_01.py --stage kp --mode real` | 同上 | `--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**(provision_shell欠落でRESTART_STORMを自行発動するためOPEN-480。委任文に明記) |
共通: 作業開始時と有料run前に`py tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <copy run> --out <json>`(rc=3なら新規API呼出0で停止)。`TTS_EXECUTION_MODE=STANDARD`。KPは据置(`--regenerate-stage kp`は使わない)。evidence actorの確定は**ユーザー確定ではない**と明記(KCP付録2)。

## 3. 確定内容保護・再実行(受入7,8。PLAN_01 §2 step 5を継承)
(a) 確定後の`--regenerate-stage part2_cand_*`/`part2_expl_*`拒否(API 0・`CONFIRMED_CONTENT_LOCKED`) (b) 解説・訳改ざんをG4で`CONFIRMED_CONTENT_INTEGRITY_VIOLATION` (c) 本文1文変更(offline fixture)で再バインド/ISSUE。関数test(T10/T12)で代替できるものは代替と明記。

## 4. 費用・所要
| 項目 | 内訳(単価は実測: Step A'' X 0.20-0.88/Y 0.32-0.48/Z 0.09-0.34、Step B X 0.055/Y 0.09/Z 0.11) | JPY |
|---|---|---|
| X r1 | Std A'' 0.2-0.4 + Std B(<=3) 0.17 + Adv A''再利用0(署名不一致なら+0.4-0.9)+ Adv B 2 x 0.055 | 0.5-1.7 |
| Y style_fix | Std A'' 0.35 + Std B 2 x 0.09 + Adv B 2 x 0.09 | 0.7 |
| Z r3 + r4 | Std A'' 0.1-0.16 x 2 + Adv B 0.11(r3のみ) | 0.3-0.5 |
| **小計(O-Z除く)** | | **約1.5-3(上限側5)** |
| O-Z(任意) | 下限: Std A'' 0.34 + B 0.11 + Part 1 約0.5 + Adv A'' 0.3 + B 0.11 = 約1.5-2。上限: KP再選定1.1-3.3 + KP音声再生成(1level約10 segment x ¥0.29/行[Y実測]=約3/level、2level約6)=約12 | 1.5-12 |
| 再実行の余裕(失敗/再生成の確認、x2) | | 5 |
| **合計見込み** | **約JPY7-20**(上限側でも約25) | |
- 上限JPY150に対し最大でも約17%。案件見積300円以下かつ承認済みScope内=AI自律(7-7)。guardは各runnerの`--approved-budget-jpy`をX=10/Y=10/Z=25程度に設定し超過で停止(分割で境界回避しない)。
- **copyが成立しなかった場合の完全再実行見積**(本文TTS含む、参考。通常は不要): X 18.1(r1累計)-53.1(byus累計)、Y 32.1(style_fix TTS)-82.7(sns全体)、Z 33.2(Magi完走)-47.9(The Promise完走)=合計約83-184(Z/Y/X全て再実行時。**最悪側は上限150を超えるため、その場合は実行せずFableへ報告**)。
- 所要: 3 Familyを独立copy-runとして**並列**(競合なし: 別run dir・別runner)。各Family: 候補+事前生成 約5-10分(rc=4待機は人的操作でなくevidence actorのCLI確定で即)、確定・再開 数分、page_verify 約3分(Z実測170秒)。Playwrightフォーム検査を含め**全体約1.5-2時間**。直列にしない理由なし。
- 起動規律: 同一run dirの起動は**150秒以上の間隔、5分3回以内**(RESTART_STORM回避)。Zの`provision_shell,gate,assemble,pages,page_verify`は1起動。自分が起動したPIDのみ終了、監督loop/wrapper禁止、原因不明のrc!=0が2回続いたら再起動せずSTOP報告。

## 5. 実施前go/no-go(API 0。実装完了後、最初に実施)
0. `stop_scope_check_01`(rc=0)。
1. copy: `C:\Users\tensh\eigo-radio-evidence\GPAL01\<fam>\<run>`へrobocopy(**repo外**、174-295MB/run)。runnerが`er*_output`配下のpathを要求する場合のみNTFS junctionで接続し、終了時にjunctionだけ撤去(KCP EVIDENCE_Y_01の先例)。コピーは`git add`しない。
2. 新runnerの`_stage_precheck`/`input_sha`を **dry/precheck(API 0)** で実行し、`tts_b1b`/`tts_a2`/KP関連unitが**stale(再生成対象)にならない**ことを確認。**staleになる場合は有料TTSを起動せずSTOPしてFableへ報告**(新Std Part 2 unitが音声の親に入る設計不備のサイン)。
3. Yは`style_profile.json`の存在、Zは`confirmed_content_issue.json`未解決が無いことを確認(不採用run回避、EVIDENCE_SOURCE_CHECK_01 §1)。

## 6. 成果物と保存先
`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_01.md`(新委任で作成)+`evidence_runs/<family>_<level>/`(各: 候補doc、フォームpayload原文、スクリーンショット、確定record、`part2_result.json`のaudit[model_id=`gpt-6-luna`、`requested_model==response_model`、prompt sha]、`cost_log`差分、`page_verify`出力)。受入10項目 x 6セルの合否表(PLAN_01 §3)に、セルごとに証跡path。未観測セルは「未観測」と明記。
失敗時の最終成果物: 事前生成STOP -> `part2_failed.json`+部分`grammar_explanations.json`(再開でAPI 0)。ISSUE -> `confirmed_content_issue.json/.md`。copy runは元runを書換えないため、失敗しても公開物・元runは不変。

## 7. 方式B(新規記事)
次の通常制作(X/Y/Z)に相乗り(追加費用なし、受入の追跡としてOPEN)。本計画の方式Aと混同しない。Z Stdの非0がO-Zで取れなかった場合は、方式BのZ新規記事で自然発生した候補0以外の結果をもってruntime観測とする(その間は「非0はmockのみ・runtime未観測」)。

## 8. 前提・限界(隠さず記録)
- X/Yのcopy元はKP 3+5世代(KP 7+5導入前)。KP再選定をしないため、7+5と文法の統合HR依頼書(PLAN_01 §2 step 1)の**7+5側の統合表示**は本evidenceでは観測しない(KP-PHRASE7側のEVIDENCE_01で別観測済み)。
- Std候補はLLMの揺れで変動する(X AI島1→3)。表の「期待候補」は区間であり保証ではない。
- 実装が未完のため、TTS再生成なしは元runのartifact状態と既存stage構造からの判定。実測は§5 step 2。
