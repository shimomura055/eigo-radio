# ADOPTION_NOTE_01: 採用時の必要作業(Production採用は人間ユーザーのみ。本書は採用の提案ではなく、採用されたら何が必要かの整理)

作成: 2026-10-25 / `APPROVED_FOR_PRODUCTION`ではない。Trialの結果(PHASE1_RESULT_01.md・PHASE2_RESULT_01.md)に基づく所見で、採用可否はFable評価とユーザー判断。

## 方式の選択(Trial結果に対応)
- **案A(欄あり)**: 1aで語りの質が(ii)より優位だったため1b/Phase 2で使用。人称維持だけなら案B'(欄なし・REVISE固定句の汎用置換のみ)で足りる(1a (ii) 2/2 P合格)。「語りの質まで守る」には欄が効いた。採用時の選択肢: (A)案A、(B')汎用置換のみ。Fable/ユーザー判断。

## 案A採用時の必要作業(すべてProduction file変更を含むため、承認後にのみ実施)
1. `er062_family_z_writer_01.py`:
   - `_render_essentials_block`(403-433): `narration_voice`があれば導入2行の直後(Key people行より前)にNarration行を挿入(DEVの`render_dev`と同一文言、`fz_essence_dev_runner_01.py`)。mode=full/std両方。
   - `build_revise_prompt`(533-541): essentialsに`narration_voice`がある場合、`REVISE_USER_TMPL`の`in third person, `を`in the narration described in the Must-keep section below, `へ置換(既存の`_REVISE_NAME_SENT_KEEP`置換と同型、assert付き)。
   - `validate_source_essentials`(447-491): `narration_voice`が非空文字列を必須に追加(Seed記入規則の検査。本文Validatorではない)。Melos(`ESSENTIALS_EXEMPT_STORIES`)は従来どおり=置換条件は「essentialsの有無」と一致し3状態目なし。
   - `build_cp_checklist`(817): narration行を1行追加(記入はFable CP、自動判定なし)。
2. 既存essentials Seed(猿の手・開いた窓・二十年後・賢者の贈り物・告げ口心臓)の`seed.json`に`narration_voice`を1行追記し、`SEED_PROVENANCE.json`のshaを更新(seed凍結検査と整合させる)。DEV Seedコピーの記入例=`dev_seed/*/seed.json`。完成版・公開音声は再生成しない限り不変。
3. test/fixture更新: REVISE文言を逐語で固定しているtest(例 `er026_family_z_story_registry_open_window_test_01.py:180-181`、`er062_family_z_writer_01_test_01.py`、`er062_family_z_source_essentials_test_01.py`)、essentials fixture。採用前のtestは`fz_essence_dev_runner_01_test_01.py`(DefaultOffIsolation 8件)を本体testへ移植。
4. Seed作成手順(記入規則を各1行): (a)`narration_voice`の第1項目に語り手の自称(`speaks as 'I'`/`no narrator`/third-person outside narrator)を必ず書く (b)free_to_cutにnarration_voiceの担い手を丸ごと入れない(削れるのが繰り返しだけなら`repetitions of …`) (c)narration_voiceは記述のみ(作品別の禁止文・内容ノルマを書かない) (d)一人称作品のSeedに`_CONVERSION_SUBSTITUTIONS`の`third-person English`雛形(er062_family_z_writer_01.py:130-134)を流用しない。
5. 影響範囲: X/Y波及なし(`er062_family_z_writer_01.py`はZ専用)。Production Prompt追加は約+90 input token/段(実測: r1 1208→1300 token)。

## 案B'(汎用置換のみ)採用時
`REVISE_USER_TMPL`の`in third person, `を全作品で`in the same point of view and narration as the story above, `へ置換するだけ(Seed変更なし)。人称は維持されるが語りの質(呼びかけ・自己陶酔)は案Aより弱い(1a平均4.0 vs 6.0、Sonnet暫定読み)。

## 『告げ口心臓』の扱い(判断候補)
現行公開版はAdv=三人称(ユーザーNG)・Std=一人称で人称が食い違っている。採用後に再生成して差し替えるか否かはユーザー判断(再生成は全e2eで約40円/作品の実績: `run_sf_prod_01`のe2e_stage_log)。本Trialでは再生成・差替えを行っていない(Trial成果物 `er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1`・`user_test/fz_essence_trial_01/`は比較用)。

## 撤退
Productionへ未反映のため撤退=Trial成果物の放置(DEV dirのみ)。採用後に撤退する場合は採用commitのrevert(Production writer 4か所+Seed 5件+test fixtureの可逆な変更)。

## 量産単価への影響
追加LLM呼出0・Validator 0。実測でchain費用はTrial 5本とProduction同作品1本の比較で −1.4/−0.2/+4.4/+3.0/−1.6円(平均+1.0円)でreasoning token変動の範囲内、系統的な増加は確認できない(サンプル少数)。入力tokenは+約90/段(約0.05円/記事未満)。目標70円/記事セットへの影響は無視できる水準と見込む。
