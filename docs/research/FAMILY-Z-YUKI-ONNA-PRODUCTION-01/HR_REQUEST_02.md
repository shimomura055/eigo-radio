# HR_REQUEST_02 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01。NUANCE-CORNER-ABOLITION-01 委任_02で2026-10-30再出力: ニュアンス解説欄を除去。HR_REQUEST_01と旧フォームdata[Std=ニュアンス欄つき]は無効)

**区分: 既存ルートを正常に通過した結果のHR**(KP + 文法の人間選定待ち。不具合・未実行工程ではない)。

1. 対象: 雪女(Yuki-Onna、Family Z)、Std(a2)/Adv(b1b)、工程=kpのHuman Review(rc=4 KP_REVIEW_PENDING)。run=`er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01`。TTS(音声生成)は未実行。
2. 承認済みProductionルート: Family Z runner `er026_family_z_fiction_production_runner_01.py` `stage_kp`(KP候補生成→KP Human Review待機。ユーザーのKP選定+文法選定が必須で、自動確定は明示の不在宣言のみ)。KP仕様=ユーザー正式決定の「KPは人間が選定」(CURRENT_SPEC KP節・PM_GOVERNANCE 30節のHR運用)。選定フォーム=V3(`user_test/selection_form_v3`)。
3. 通過工程(JST): 07:58:43起動1 seed_check通過→writer r0/r1/r2→std_adjust→plan(話者3のみ・clip6件ずつ)→08:02:13起動2 support→part2文法候補→kp(候補生成+gloss整列)→Gate(CMU未登録 "woodcutters" を除外し補完候補で補填)→KP_REVIEW_PENDING(rc=4)。全LLM呼出success、失敗0。詳細=`RUNTIME_EVIDENCE_01.md`。
4. retry/fallback/LR/再生成: 発動なし(対象外=TTS前の段でありLR/TTS fallbackは音声工程のみ。Writer再生成なし=本文再点検で×△なし)。
5. 直接原因: 仕様どおりKPと文法はユーザー選定が必須のため待機(失敗ではない)。
6. 残る自動救済: なし(HR待機は設計上の停止点。選定後に同じコマンドで再開し、以降のtts_b1b/tts_a2にTTS retry/Fallback/LRが適用される)。
7. ユーザーに判断してほしいこと: 学習項目(KP最大3件+単語最大5件)の選定、文法(Part 2)の選定。**文法候補は0件**(Std・Adv とも grammar_status=no_candidates_found、選択不要=0件で可)。

## 選定フォーム(Std / Adv)
- Std: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html?a=yuki_onna__a2
- Adv: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html?a=yuki_onna__b1b
- (push後にHTTP 200を実測し、RESULT_PACKET_ZY02.mdに記録)

## KP候補(依頼書 = `er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/review_request.md`、AI推奨付き)
- Adv(b1b)の候補10件: KP推奨=slip away / have reason to complain / keep silent、単語推奨=take shelter / as you deserve、ほか go no farther / persuade / widowed / bar / struggle(補完)。
- Std(a2)の候補7件: KP推奨=talk someone into staying / get what you deserve / slip away、単語推奨=riverside / mist、ほか light-skinned / complain(補完)。

## 参考(Fable向け)
