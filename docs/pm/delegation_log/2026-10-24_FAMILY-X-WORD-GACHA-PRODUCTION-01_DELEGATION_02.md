FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_02(Fableから): Advanced `full_story_part3` のHuman Review Lock(3回ともASRが「gacha」を「gotcha」と聞き取りNG_BOTH、Standardは2回目でOK)について、Fableは次のとおり判断した。

## Fable判断
- 「gacha」/ˈɡɑːtʃə/と「gotcha」はほぼ同音で、ASRが高頻度語に寄せた可能性が高い。音声欠陥の証拠はない(他の全語は一致)。Secondary(Azure)は文の混線で裏付けにならなかった。
- **approve_regenerate をFable権限で許可**: 既存HR手順に従い `full_story_part3`(Adv)の再生成を**最大2回**まで(cooldownは待つ、迂回しない)。案件上限を100→110円に引上げ(Fable 7-3自律、日次1,000円内。10-24把握分約458円+Z残≤40円+本作≤20円)。
- 2回で解消しなければ再生成を止め、状態を記録してFableへ(その場合はユーザー耳確認のための該当segment音声の提示方法を含めて報告)。
- 原稿改変(gachaの言い換え)で検査を回避しない。新しい同音規則・受理クラスの実装はしない。

## 作業
1. 既存HR手順で approve_regenerate を記録付きで実行(reason: "FABLE_APPROVE_REGENERATE 2026-10-24 FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_02: ASR homophone gacha->gotcha x3, no audio defect evidence, Std passed on retry; max 2 regenerations")。audio runner の既存手順(stage=再生成対象のみ)で再生成→判定。起動前に `tools/stop_scope_check_01.py --managed-id FAMILY-X-WORD-GACHA-PRODUCTION-01` rc=0、`git status`でX経路import graphに未commit変更なし。
2. OKになったら Adv `--stage assemble` → 試聴ページ(`er019_nws2_final_page_01.py`、`user_test/family_x_word_gacha_01/`、Std/Adv切替・通し・パート別・全スクリプト・KP、開発者向け情報なし)→ 公開page_verify(`er019_nws2_play_verify_01.py`、Playwright実再生)PASS証跡。
3. 「gacha↔gotcha」型(記事の中心語が固有名詞でない借用語でASR同音誤認→HR)の扱いを11-8で分類: 既存の承認済み機構(er109同音規則のデータ表、PNAP受理境界、RET実体表、approved equivalence)で**データ追加だけで**扱えるなら「修正へ進む」として対応案(影響分析gate付き)を `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/GACHA_HOMOPHONE_01.md` に書く(本委任では実装しない。Fable判断後)。新しい受理クラスが必要なら「ユーザー判断要」として選択肢・QCD影響を書く。OPEN新規登録(分類明記)。
4. 費用目標超過(90円 vs 目標70円)の内訳分析を `RUNTIME_EVIDENCE_01.md` に: Azure Secondary 27.5円が最大(呼出回数と理由)、3回試行分、GIGAZINE/wordgacha Research分。量産単価への示唆(Secondary呼出を減らす余地があるか=事実のみ、仕様変更提案はしない)。
5. `RUNTIME_EVIDENCE_01.md` 完成(『賢者の贈り物』書式)、OPEN_ITEMSにUDR待ち項目、`docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(最終試聴PASS可否、A/B、推奨A、試聴URL、耳確認候補=PASS_WITH_WARNING 3件+part3)、DECISION_LOG 1エントリ(制作・HR・Fable approve_regenerate・費用)。
6. Git: `git status`でindex確認→`git commit --only`→`git push origin HEAD:main`(wav/mp3/raw_usage_log/STOP/ACTIVE_TASK/RESULT_PACKET不追跡、`review_queue/post_en/index.jsonl`等の他agent差分は巻き込まない、OPEN-490不復元)。禁止操作(add -A/-u/-f/-N、amend、rebase、force push、stash、clean、reset --hard、checkout -f)。secret grep 0件。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_02.md`(Nは先頭「FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_02」を含むAgent呼出の0始まり通番、直近464以降)。

## handback(ユーザー原文§6の8項目で、完成なら全項目。未完成なら状態・再生成結果・費用・次の選択肢)
RESULT_PACKET 4行、commit hash、raw URL。