# EVIDENCE_PLAN_01 実API runtime evidence計画(全6経路、見積<=JPY40。GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01)

目的: ユーザー§8の受入条件1〜11を、正式runner(Production経路)の実行で6経路すべて示す。DEV/Trialだけの成功を根拠にしない。一部のFamily/levelだけでの全体完了判定をしない。実施は実装・test完了後の次委任(本委任は計画のみ)。

## 1. 方式(費用と正式性の両立)
- **方式A(推奨・既定)**: 既存の完了run(KP 7+5 evidenceで使った本文・音声あり)を`copy-run`し、**正式runnerのstageだけ**を実行する。文法は音声に影響しないため本文・TTS・assembleは再利用(再生成しない=ユーザー§9「不要な本文・音声の再生成を避ける」)。先行事例: KCP委任_02B(Z: `--stages kp --mode real` → `--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**[OPEN-480]、追加費用0)。
  - 元run: X=`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kp75_ev_01`(またはai_island_temple)、Y=`er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01`、Z=`er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01`。copyは`--out`を新規run名にし、元runを書換えない。
  - 各runが両level(a2/b1b)を持つため、1 runで **X/Y/Z x Std/Adv の6経路**を同時に踏む。
- **方式B(任意・別Scope)**: 完全な新規記事でのE2E(本文生成からTTS・公開まで)。費用は量産単価目標JPY70/記事セットを目安に約JPY70 x 3 Family(実費は未確認の概算)で、本計画の<=JPY40を超える。ユーザー受入§8-1の「正式初回Production」の解釈(方式Aのcopy-runで足りるか)をFableが判断。推奨=Aで6経路を証明し、Bは次の通常記事制作に相乗り(追加費用なし)で追跡(OPEN)。

## 2. 実行手順(Family共通。launch間隔を空けRESTART_STORM[3起動/300秒]を回避。STOPセンチネルは削除しない)
各Familyで、作業開始時と有料run前に`py tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <run> --out <json>`(rc=3なら停止)。
1. **候補+事前生成(実API)**: X=`--stage study_text --level both`(+scaffold相当)、Y=`--stages kp`、Z=`--stages kp --mode real`。期待: Std Step A'' 1 call、Adv Step A''は**再利用(API 0)**(本文sha・Prompt・model一致)、各level候補のStep B事前生成(候補数 call)。rc=4(Human Review待ち、KP+文法Std+文法Adv統合依頼書)。
2. **フォーム経路(受入2〜5)**: `export_form_data_01`相当(F-5接続後)でrunのフォームdata生成→`user_test/selection_form_v3`相当のローカル静的ページにPlaywrightで読込→(i)文法候補の文法名・解説全文表示 (ii)最大2件選択・3件目不可 (iii)①②③上限/排他 (iv)AI理由表示 (v)コピー/送信payload取得(`buildStructured`)。スクリーンショットとpayload原文を保存。
3. **確定(受入5)**: `confirm --from-form <payload> --run --level a2/b1b --actor evidence --user-ref <委任文>`(evidence actorはユーザー確定ではないと明記。KCP付録2)。Std/Adv各levelで文法0/1/2件のパターンを網羅(例: Adv 2件、Std 1件、可能なら0件)。`confirmed_grammar*.json`(sidecar/凍結 v2)・review `pick`反映・`explanations_sha256`一致を確認。
4. **再開(受入7,8)**: 同コマンドで再実行→finalize/Part 1/TTS入口/gate/assemble/pages/page_verify(Zは`--stages provision_shell,gate,assemble,pages,page_verify`を1起動)。**追加API呼出0**(cost_log不変)、KP救済/Gate除外補完/HR整合(統合依頼書の1回rc=4)を確認。
5. **確定内容保護(受入7)**: (a) `--regenerate-stage part2_cand_<lv>`・`part2_expl_<lv>` → 拒否(API 0・レコード不変、`CONFIRMED_CONTENT_LOCKED`) (b) 解説・訳の改ざんをassets/結果へ注入→G4で`CONFIRMED_CONTENT_INTEGRITY_VIOLATION` (c) 本文1文変更(offline fixture): 確定文が残る→再バインドAPI 0 / 残らない→ISSUE。起動回数が300秒内3回を超えないよう間隔管理、超えそうな検証は関数レベルtest(T10/T12)で代替し明記。
6. **公開ページ(受入6)**: Playwright `--local`(`page_verify`)でindex.html: 各levelの節に文法ブロックが**1個ずつ**、Advは`Vocabulary & Expressions`直後、Stdは文法のみ、文法名・解説全文・対象英文が確定内容と一致(md/HTML/part2_result/凍結の4者一致)。標準適合check PASS。
7. **モデル/routing/Prompt(受入10)**: `part2_result.json`/`grammar_explanations.json`のauditから、`STUDY_TEXT_GRAMMAR_EXTRACT/EXPLAIN`のactual model_id(期待`gpt-6-luna`=SUPPORT_MODEL)、`requested_model==response_model`、`prompt_sha256`が定数`STEPA/STEPB_PROMPT_SHA256`由来であることを表にする。最新モデル原則(PM_GOVERNANCE 25節)の報告項目(使用モデル名/最新か/理由)を併記。

## 3. 6経路の合否表(各セルに証跡path)
| 受入項目(§8) | X Std | X Adv | Y Std | Y Adv | Z Std | Z Adv |
|---|---|---|---|---|---|---|
| 1 候補データがフォームへ渡る | | | | | | |
| 2 英語・和訳・AI理由表示(KP側。文法は名称+解説全文) | | | | | | |
| 3 ①②③上限・排他/文法最大2 | | | | | | |
| 4 文法候補+事前生成解説全文がフォームに表示 | | | | | | |
| 5 確定内容の保存(sidecar/凍結/review) | | | | | | |
| 6 公開ページ反映(自levelの節に1個、4者一致) | | | | | | |
| 7 retry/fallback/regeneration/resume維持 | | | | | | |
| 8 KP救済・Gate除外補完・HR整合 | | | | | | |
| 9 Regression/Validator/Integration test | | | | | | |
| 10 model_id/routing/Prompt/runtime証拠 | | | | | | |
未観測セルは「未観測」と明記し追跡(全6経路が揃うまで一括PRODUCTION_WIREDと判定しない)。ユーザー実操作確認(フォーム)が未完了なら受入Statusと混同せず明示。

## 4. Std候補率の計測(新規情報・費用小)
Stdの文法候補数・ZERO率は未観測。方式Aの3 run(各1 Std本文)に加え、**既存の完了Std本文**(`er019_output/*/a2/article.md`等)から最大8本を選び、Std Step A''のみ(1 call/本、ページ生成なし)を実行して候補数/ZERO率/tier分布を記録(事実の報告用。Prompt変更の根拠にはしない)。<=JPY7。

## 5. 費用(詳細COST_ESTIMATE_01) / 失敗時の成果物
- 想定JPY12-27、上限JPY40。個別Cap内(案件見積<=JPY300)ゆえ都度承認不要。予算guardは各runnerの`--approved-budget-jpy`に設定(超過で停止、分割回避なし)。
- 失敗時: 事前生成STOP→`part2_failed.json`+部分`grammar_explanations.json`(再開でAPI 0)。ISSUE→`confirmed_content_issue.json/.md`。プロセスが外部停止/原因不明rc!=0が2回→再起動せず即STOP報告。
- 保存先: 既存の`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_01.md`(新委任で作成)+`evidence_runs/`(KCP先例の構造に倣う)。新しい証跡置き場は作らない。
