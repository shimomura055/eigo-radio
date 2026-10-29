# TRIAL_DESIGN_01: 新学習コーナー「One Step Further」品質検証Trial(ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_01、2026-10-30)

Status上限=VALIDATED(Trial専用)。Production code/Prompt/記事本文/音声/KP/文法は変更しない。ユーザー原文=`docs/pm/delegation_log/2026-10-30_ONE-STEP-FURTHER-CORNER-TRIAL-01_USER.md`。

## 1. 現行仕様との役割分担(確認結果)
- Key Phrase/Word=本文に出た重要表現。文法・構文=本文の英文の仕組み。ニュアンス解説(er134、Production、Prompt v3案はNUANCE-QUALITY-IMPROVEMENT-TRIAL-01=別Trial・UDR #224)=本文中の表現の含み。
- 新コーナー=本文に無い別表現を、記事の話題から紹介する(本文既出は対象外)。ニュアンス①表示順序・②HR事前チェックの作業、および③Trialとは別物。本Trialは既存run成果物を読むだけで、それらの配線に触れない。

## 2. 対象記事の選定理由
| Family | 記事 | 選定理由 |
|---|---|---|
| Y | 姓記事 `er121_output/family_y_production_01/surname_choice/run_02` | 指定。Std a2/Adv b1b本文・KP確定・文法確定・ニュアンス採用文あり |
| X | AIの島 `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`(公開済み) | KP(confirmed_selection)確定済み・文法候補あり。話題が「リセットされても残るメモ」「探索」「結果の見方」と、意見・状況を表す別表現を導きやすい。ニュアンスTrialで同記事の現行形/v3があり比較が取れる |
| Z | 告げ口心臓 `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01`(公開済み) | KP確定済み。語り手の緊張・疑い・解釈という「気持ち」から日常にも使える表現を導きやすい。ニュアンスTrialで同記事の比較が取れる(文法候補は「該当なし」=文法重複判定は無し) |
(月・coffee_prices・走れメロス・藪の中は、KP/文法の確定状況・比較参照の有無で上記を優先。除外ではなく今回見送り。)

## 3. 方式
- 入力=当該レベルの英文本文、確定Key Phrase/Word、確定文法/文法候補上位2(重複回避用)。ニュアンス採用文は生成に与えず評価時の比較に使う。日本語本文は与えない(英文のみ。生成側が記事の事実を取り違えないかは評価で確認)。
- 出力schema(JSONのみ): `scenes_considered[]`、`items[1〜2]{topic_hook_ja, basic_en, basic_ja, further_en, further_ja, core_expression, point_ja, why_ja, meaning_shift_note, self_check}`。
- Prompt v1=委任文§3・§4の方針(平易な基本文→実用的な発展表現、難語自体は加点しない、記事にない事実・心理の捏造禁止、KP/文法/本文既出との重複回避、レベル差、参考例6件の再利用禁止を明記)。
- Prompt v2=v1の欠陥(同義語への単純置換=言い換え型、学校英語で既習の頻出熟語で新味が薄い)に対し「言い換え型でないか」「新鮮味」の2条件と、ポイントへ「基本表現では言えない点」「日本語話者が間違えやすい点」を追加。欠陥の種類ごとの変更で、同じ修正の反復ではない。最大v3の枠内で、v3は有料枠(¥60)到達のため未実施(RESULT_01.md参照)。
- 実行(tools/osf01_gen.py、Production非import。費用単価表の数値のみ転記): 6セル(3記事×2レベル)を並列。条件=(v1/v2)×(gpt-6.1-sol 1回、gpt-6-luna 2回)。
- モデル(PM_GOVERNANCE 25節): 主候補=gpt-6.1-sol(最新上位系)。量産費用比較用に現行Production routeのgpt-6-luna(er006_model_routing_contract_01.py:50 SUPPORT_MODEL)。監査=gpt-6.1-sol(匿名・順序シャッフル、1記事1call=Std/Adv同梱)。

## 4. 評価
- 機械検査(tools/osf01_show.py): 項目数1〜2、必須field、point_ja≤130字、核表現がKP/Wordと一致・包含しない、核表現が本文に既出でない、発展文にKPを含まない、参考6例を使っていない。
- 独立監査(tools/osf01_audit.py): 学習価値/正確性/日本語/関連性/レベル適合(1〜5)+捏造/KP重複/既知の3フラグ。現行ニュアンス解説(Y採用文、X/Zは改善Trial v3)を混ぜて匿名比較。
- 人手(筆者)評価: 全出力を目視し、RESULT_01.mdの評価表に○△×と理由を記録。
- 再現性=同条件の複数生成での選定表現と品質のぶれ。費用・時間=usage_log.jsonlの実測。

## 5. 費用上限
通常¥40、理由記録で¥60まで。実績¥59.93(RESULT_01.md)。上限到達のため以後の有料runは不可(超える見込みは報告)。
