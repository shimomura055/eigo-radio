# TRIAL_DESIGN_03: 最小化条件(新Prompt第3条)を現行Production経路のKP選定Promptへ組み込む比較Trial

管理ID: FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_01 / 2026-10-22 / Trial専用・Production無変更
ユーザー決定: KP選定=gpt-6-luna維持、2工程方式見送り、提案C=GO(原文 `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_USER.md`、190字、sha256 f32a06fb4793412d409ffc7f0d55b1394c8eb8aa4a39c612d48fe22842d0569f)。
注記: 設計値(arm・比較軸・合格基準・見積)は有料run前に確定したもの。本文書への清書は実行中〜実行後に行った。

## 1. 経路図(Trialは本番と同じ関数列をそのまま呼ぶ)
```
[本番] er019_family_x_audio_production_runner_01.py:411  sc.run_key_phrases(article_text, kp_dir, article_id, level, process=A2/B1_SUPPORT, kp_backend="db_hybrid")
[Trial] er102_kp_min_prodpath_trial_03_run.py  同じ sc.run_key_phrases(...) を同一引数で呼ぶ(level=Standard->a2 / Advanced->b1b)
  sc.run_key_phrases           er003_v1_n3_01_scaffold_generate.py:802
   -> _run_key_phrases_impl    :835  (Redundancy/Symbol QA NG時の選定やり直しretryループ :868)
    -> run_key_phrase_selection :294 -> _run_key_phrase_selection_db_hybrid_with_fallback :577
      -> db_hybrid.run_db_hybrid_selection  er030_key_phrase_db_hybrid_selector_01.py:416
         shortlist(M2P0供給 build_m2_stage1_and_shortlist) -> Prompt組立(:543 bk.load_prompt_template() -> extract_static_instructions + 候補一覧 + 選定方針)
         -> Luna選定(候補ID契約) -> source span復元/検証   (DbHybridFailure時のみStrategy L fallback)
    -> run_key_phrase_canonicalization :683 (原形化[Luna]+gloss整合[Luna])
    -> run_key_phrase_redundancy_qa (相互重複QA[Luna]) -> NGなら選定からretry
```
Trial内だけで行う差し替え(Productionファイルは無編集): (1)`sc.KP_BACKEND_TELEMETRY_PATH`をTrial out_dirへ (2)Arm Bのみ`bk.load_prompt_template`の戻り値へ第3条を挿入 (3)`m2_supply.build_m2_stage1_and_shortlist`のpickleキャッシュ化(Arm S=同関数を実行して保存、Arm A/B=同じ保存物を読む=shortlist同一) (4)`er005_cost_logger`をTrial logへinstall(OpenAI Responses usage記録)。

## 2. Prompt差分(Before/After全文は `KP_MIN_PRODPATH_COMPARISON_03.xlsx` Sheet4、実体 `er102_output/kp_min_prodpath_trial_03/inputs/template_{A_current,B_plus_clause3}.txt`)
- Before = `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(無改変)。
- After(Arm B) = Beforeの段落「display_phraseは1〜5語にしてください。完全文、主語と有限動詞を持つ節、記事固有の長い説明は禁止です。」の直後に空行+次の1段落を挿入(他の文言・順序・出力形式は不変):
  `学習ポイントの明確化と最小化（必須）：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。`
  (本文はユーザー提示§3-2の3を逐語。現行templateは番号・太字を使わないため「3.」と`**`は付さない。現行templateに「5語以内」「学習価値」の文言はなく、5語規定の段落直後に置いた。)
- 実際に送信される選定Promptでの差分は「空行+上記1行」のみ(`prompt_parity.json`: Arm A vs B、retry時のdiagnostic_note差を除く全単位で2行差)。Arm Aの選定Promptは既存Production run(同記事)のkeywords_selector_prompt.txtとバイト一致(A_Std/A_Adv/B_Std/B_Adv/C_Std/C_Adv/F_Std/F_Adv=8/12。D=retry注記差、E=別run世代、G=既存dirなし)。

## 3. arm・条件
- 14単位=`er098_output/kp_six_model_trial_01/inputs/manifest.json`と同一(copy_sha256一致をrunnerでassert)。記事G(旧記事)もM2P0 shortlistを構築できた(欠落0)。
- Arm A: 現行template無改変・fresh実行。Arm B: 現行+第3条。shortlist同一、モデル=gpt-6-luna(routing: A2_SUPPORT/B1_SUPPORT)。選定・canonicalization・gloss整合・Redundancy QAは両armでProduction通り全実行(「選定直後」=display_phrase/source_span、「canonical後」=key_phrase を両方保存)。
- Productionのretry/fallback/Gateは無効化せずそのまま適用(Redundancy retry最大2、DbHybridFailure時Strategy L fallback等)。品質理由の手動再生成なし。

## 4. 比較軸
(1)機械: 語数分布・5語超・本文一致・5件充足・重複 (2)Arm Aと既存Production KP(実記録)の一致率=現行再現性 (3)独立評価=claude-sonnet-5-5単独、TRIAL-02と同rubric(V/E/N+C/U/S/X)をA/Bへ匿名同一バッチ適用(本文span版=TRIAL-02 Trial①と同形、canonical後key_phrase版=最終成果物) (4)Trial②Luna全文渡しとの参考比較(尺度差あり) (5)例示3件追跡。

## 5. 合格基準(事前指定)
Arm BがArm Aと同等以上の遵守率(成功率・5語上限)で平均語数が短縮し、評価のC/U/S/Xが上回り、V/E/Nが下がらないこと。

## 6. 見積(有料run前)
- 選定チェーン: 28単位×約1.2〜2.0円(既存Production実測: 選定のみ約0.43円/単位+canonicalization・gloss・Redundancy QA)=約34〜56円
- 評価: Sonnet 5.5 約24〜28呼出×約1.0〜1.6円=約25〜45円。 合計約60〜100円、Cap JPY150。
- 日次: 当日既使用約800円+見積上限100円=約900円<1,000円(7-9判定OK)。承認区分C(ユーザーGO済み・300円以下)。
- 実績は`TRIAL_RESULT_03.md` 5節。
