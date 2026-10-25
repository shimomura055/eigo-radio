# 委任文(Fable→sonnet-worker)
管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_03(案A Production Wiring設計+既存Seed補完案+影響分析+Opus条件Aレビュー依頼書。**API 0円、Production file編集はまだ行わない**。実装・『告げ口心臓』再生成はOpusレビュー後のFable Goで委任_04)
Status: 案A=APPROVED_FOR_PRODUCTION(ユーザー正式承認2026-10-25、UDR #192判断済み)、『告げ口心臓』Std/Adv正式再生成・公開差替え=承認(UDR #193判断済み、概算約40円、ユーザー最終試聴PASSは先取りしない)。到達目標=PRODUCTION_WIRED+『告げ口心臓』正式完成候補公開。

## 0. 最初に
- ユーザー原文を `docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER_02.md` に以下を一字一句そのまま保存。

```
# Claude Code指示｜Family Z 原作本質保持 Production Wiring ＋『告げ口心臓』正式再生成

## 1. ユーザー正式承認

以下の2件について、ユーザーの明示的な正式承認を得ました。

**① 原作本質保持方式：案Aを正式採用**

- Seedの「作品の本質」に `narration_voice` を追加する。
- 語り手の自称・立場・聞き手への語りかけなど、原作固有の語り口を定義する。
- 既存の情報伝達経路を利用し、R0・R1・R2・Standard調整まで一貫して伝える。
- 推敲工程に残る三人称固定指示を撤去し、原作の語り口を維持する指示へ置き換える。
- 人称だけでなく、語り手の心理・表現・作品の本質を維持する。
- 新Validator・追加LLM呼出・新retry機構は導入しない。

Status：**APPROVED_FOR_PRODUCTION → PRODUCTION_WIREDまで実施。**

**②『告げ口心臓』Standard／Advancedの正式再生成・公開差し替え**

案Aを正式Production経路へ配線した後、両レベルを正式経路で再生成し、品質検査を経て公開してください。

概算費用は報告済みの約40円を前提とします。

今回の正式承認は再生成・公開までです。**ユーザー最終試聴PASSを先取りして記録しないこと。**

## 2. Production Wiring

Trialで検証済みの案Aを、Family Zの正式Production経路へ実装してください。

対象：

- Seedの原作本質情報
- R0初稿生成
- R1／R2推敲
- Standardレベル調整
- retry／fallback／regeneration／resume
- 関連Prompt・テスト・SSOT

特に、Trial専用経路だけで動作する状態を避け、正式初回Production経路に適用してください。

既存の `in third person` 固定指示が残る箇所を確認し、今回の正式承認と矛盾する指示を撤去してください。

既存の「人物を名前ではなく役割で呼ぶ」指示についても、一人称の語り手を不自然に三人称化しないよう、承認済みの語り口保持方針と整合させてください。

ただし、ユーザーが承認していない新たな文学的品質基準や作品別の禁止ルールを独断で追加しないこと。

## 3. Cross-Family・既存作品との整合

今回の変更はFamily Zの文学作品に関する共通仕様として適用してください。

- 『賢者の贈り物』
- 『開いた窓』
- 『猿の手』
- 『走れメロス』
- その他既存のFamily Z作品

既存Seedへの必要な情報補完と、Production経路の整合を確認してください。

今回の配線を理由に、既存の完成記事をすべて再生成する必要はありません。

既存作品への副作用は、Trialで得られた検証結果を再利用し、必要十分な回帰テストで確認してください。

Family Xなど別Familyへの無断の仕様展開は行わないでください。

## 4. 『告げ口心臓』正式再生成

案AのProduction Wiringを確認したうえで、Standard／Advancedを正式経路で再生成してください。

品質上の重点：

1. 原作の一人称独白を維持する。
2. 語り手が聞き手へ直接語りかける特徴を維持する。
3. 語り手の自己正当化・自己陶酔・狂気を表現する。
4. 老人への執着、殺害、心臓音、警官の前での心理的崩壊、自白までの因果と緊張を維持する。
5. Standard／Advancedの語り口を整合させる。
6. 語彙・文長・表現は各レベルに適応しながら、原作の本質を損なわない。

これらは今回のTrialで承認された品質方針の確認であり、新たな内容ノルマを追加するものではありません。

## 5. 音声・公開品質

正式なTTS・ASR・音声品質検査・組立工程を通してください。

- 正式Productionのモデル・Prompt・Styleを使用
- 既存のretry／fallback／resume仕様を維持
- 音声Gate・必要なRegression／integration testをPASS
- Human Reviewが発生した場合は、既存の自律解決手順に従う
- Trial音声を正式Production音声と誤認しない
- 公開ページの再生・パート切替・スクリプト表示を確認

完成後は、Standard／Advancedの全体試聴・パート別試聴が可能なページを提出してください。

正式公開ページには、古い三人称Advancedが残らないよう確認してください。

## 6. PM Gate・受入条件

**PRODUCTION_WIRED判定には、次をすべて確認してください。**

- 正式初回Production経路への案A配線
- retry／fallback／regeneration／resumeとの整合
- Trial専用経路ではないこと
- 正式runtimeで `narration_voice` が各工程へ渡った証拠
- 旧三人称固定指示が正式経路に残っていないこと
- Standard／Advancedで原作の語り口が維持されていること
- 必須テスト・音声検査PASS
- actual model_id・Prompt・routing等の実行記録
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- 必要なGit commit／push
- Fable独立受入評価

コード変更やDEVテストのみをもってPRODUCTION_WIREDとは判定しないでください。

## 7. QCD・自律進行

品質 ＞ 速度 ＞ 量産単価 ≫ 開発費の優先順位を守ってください。

- TrialでVALIDATEDとなった案Aを再利用する。
- 不要な再Trialや全記事の再生成を行わない。
- 独立作業は並列化する。
- 承認範囲内の不具合は原因調査から修正・検証まで自律的に解決する。
- 追加LLM呼出・Validator・過剰な品質検査を増やさない。
- 量産単価の増分を最小化する。
- 約40円の再生成概算と実費を比較し、既存予算・STOP条件を遵守する。

必要十分な品質に達したら追加の磨き込みを行わず、完成・報告してください。

## 8. 完了報告

以下を簡潔に報告してください。

1. 案AのProduction Wiring完了状況とruntime evidence
2. 旧三人称固定指示の撤去確認
3. 既存Family Z作品への副作用確認
4. 『告げ口心臓』Std／Advの正式再生成結果
5. 語り口・原作本質の維持評価
6. 音声Gate・Regression・integration test結果
7. 正式試聴ページURL
8. 開発実費・量産単価への影響
9. SSOT／Git反映状況
10. Fable独立受入Statusと残存Open Item

**最終的な到達目標：案AをPRODUCTION_WIREDにし、『告げ口心臓』のStandard／Advancedを正式完成候補として公開すること。**

その後、ユーザーの最終試聴・承認を受けて記事をCloseoutしてください。
```

- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 516 --out docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_DELEGATION_03.md`。冒頭が「管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_03」と一致するか確認、不一致なら index 514〜519 を順に試す(`--index -1`不可)。

## 1. 前提(委任_01/02資産)
- `docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/{ROOT_CAUSE_01,DESIGN_02,PREREGISTERED_CRITERIA_01,PHASE1_RESULT_01,PHASE2_RESULT_01,ADOPTION_NOTE_01,OPUS_REVIEW_01,FABLE_EVAL_01}.md`、DEV runner `fz_essence_dev_runner_01.py`(メモリ上差替え)、`dev_seed`(告げ口心臓・賢者・開いた窓・猿の手のnarration_voice記入例)、DefaultOffIsolation test。
- ADOPTION_NOTE_01の採用時作業: Production writer 4か所(R1/R2 REVISE固定文言"in third person"の置換、Narration行の描画[Key people行より前+汎用1句]、Std調整への伝達、Seed非空検査)、Seed 5件への`narration_voice`追記(告げ口心臓/賢者/開いた窓/猿の手/二十年後。メロスはessentials非対象=従来どおりか要確認)、REVISE文言逐語test fixture更新、`_CONVERSION_SUBSTITUTIONS`雛形を一人称作品に流用しない規則の手順書化。Opus (d): 採用時はnarration_voiceを全essentials作品で必須化し、置換条件を既存の「essentialsの有無」に一致させる(3状態目を作らない)。

## 2. 作業(API 0)
A. `WIRING_DESIGN_01.md`:
   - 変更箇所一覧(file:行、現行文言→新文言、Trial DEV実装との対応): `er062_family_z_writer_01.py`(REVISE固定文言:141、`_render_essentials_block`:424のNarration行追加と汎用1句、Std調整段への同一行描画、Seed非空検査の位置)、`er062_family_z_structure_01.py`(影響なしの確認)、`er026_family_z_fiction_production_runner_01.py`(seed_check段でのnarration_voice必須検査、retry/fallback/regeneration/resume[`--regenerate-stage`、`_bak_*`退避、STALE_attempt]でPromptが同一に組み立てられることの確認、runtime evidenceとしてprompt dump/provenanceに`narration_voice`と置換後REVISE文言が記録されること)。
   - Seed補完: Production seed置き場 `er026_output/family_z_production_e2e_01/<story>/seed/seed.json` と `er026_seeds/<story>/seed.json` の両方か片方か(正本を確認)、各作品の`narration_voice`記入文(Trial dev_seedの文を基準に、記入規則=第1項目は語り手の自称、記述のみ・禁止文なし・内容ノルマなし、free_to_cutに語りの質の源を丸ごと入れない)、メロスの扱い(essentials非対象なら従来どおり=byte同一を確認)、SEED_PROVENANCE更新。
   - 「人物を名前ではなく役割で呼ぶ」指示との整合=Opus修正1の汎用1句(「人物の役割説明は語り手を外から呼ぶ指示ではない」)をNarration行に添える。新たな文学的品質基準・作品別禁止ルールは追加しない。
   - 撤退=単一commitのrevert(Seed追記含む)。
   - test計画: 既存REVISE逐語test fixture更新(`er026_family_z_story_registry_*_test_01.py`等)、新規test(narration_voice描画順・Std調整への伝達・欄なしSeedでの挙動[必須化により欄なしはseed_checkで停止]・旧固定文言がProduction経路に残っていないことのGrep test)、全回帰(自分起因0)。
   - 既存作品の副作用確認計画: 再生成はしない。Trial Phase 2結果(賢者/開いた窓/猿の手、人称不変・副作用なし)を再利用し、配線後にPrompt組立のみ(API 0)で各既存Seedに対するR0/R1/R2/Std Promptを生成し、Trial DEV runnerが生成したPromptとbyte一致(または差分が設計どおり)であることを確認する=「Trial結果の再利用」の根拠。
   - 『告げ口心臓』正式再生成計画: 正式runner、新run id(例 `run_sf_prod_02`)、stage順 seed_check,writer,std_adjust→plan,support→kp→tts_b1b→tts_a2→provision_shell,gate,assemble,pages,page_verify、`--approved-budget-jpy`、見積(約40円、出典=run_sf_prod_01 cost)、HR Lock時は既存自律手順(approve_regenerateはFable権限)、公開ページ `user_test/family_z_tell_tale_heart_01/` 差替え(旧三人称Advが残らない確認)、runtime evidence項目(model_id・Prompt sha・routing・narration_voice伝達・REVISE文言)。
   - 量産単価増分: 追加LLM 0、+約90 token/段(Trial実測、検出不能)。
B. `OPUS_REVIEW_REQUEST_02.md`(条件A: Production配線設計): 論点=(a)配線箇所の網羅(初回経路・retry/fallback/regeneration/resumeで同一Promptか)、(b)Seed必須化と既存5作品+メロスの扱い(3状態目を作らない)、(c)旧固定文言の完全撤去とkey_roles指示との整合、(d)既存作品の副作用確認をPrompt byte一致+Trial結果再利用で済ませることの妥当性、(e)runtime evidenceの十分性、(f)撤退容易性、(g)X/Yへの波及なし。
C. SSOT: UDR #192/#193を判断済み(2026-10-25、原文path)に更新、OPEN-508 Status=`APPROVED_FOR_PRODUCTION_WIRING_DESIGN_PENDING_OPUS_A`、OPEN-503に「正式再生成承認(UDR #193)、配線後に実施」追記、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行(並行agent FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_04 が同時編集中。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py`使用。
D. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・**Production file差分0**) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
E. 報告 `docs/pm/RESULT_PACKET_FZSE3.md`: 設計要点(変更箇所表、Seed補完文、test計画、再生成計画・見積)、OPUS_REVIEW_REQUEST_02.mdの所在、変更ファイル・commit、`check_delegation_prompt.py`結果、問題点。**Production file編集・有料runは開始しない。**

## 3. 禁止
Production code/Prompt/Seed/flagの編集(本委任は設計のみ)、有料API呼出、新Validator/追加LLM/新retry機構の設計、作品別禁止ルール・新文学基準の追加、Family X/Yへの展開、`.venv\Scripts\python.exe`以外の使用(有料runなし)、自PID以外のprocess終了。