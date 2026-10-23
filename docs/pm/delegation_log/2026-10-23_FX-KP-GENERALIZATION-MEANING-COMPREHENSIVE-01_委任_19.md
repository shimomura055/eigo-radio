FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_19-FABLE-JUDGMENT-RECORD-AND-UDR-173-20261023

# 記録のみ(API 0・コード変更0)。Key Phrase 2課題のFable判定を保存し、UDR登録・OPEN-474更新・Git。

## 0. 読むもの
`docs/pm/ACTIVE_TASK.md`(KP行群)、`docs/pm/USER_DECISION_REGISTER_01.md`(最新番号、#172まで)、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{TRIAL_RESULT_04,WIRING_DESIGN_05,OPUS_REVIEW_06}.md`、`TRIAL_04/{REPORT_FABLE_04,POSS_RESCORE_01,POSS_REP2_01}.md`。

## 1. Fable判定(2026-10-23、逐語で `TRIAL_04/FABLE_JUDGMENT_04.md` に保存)
- 課題②(見出し語の人称placeholder、`possessor_roles`先行判定+決定論写像[revertのみ]): **VALIDATED(Fable)**。根拠: 意味関係の誤り 現行+A-1 7(rep1)/5(rep2)→本案 0/1(2rep計 14→1、公式score)、role判定76/80 gold一致、INVALID/REVIEW_REQUIRED増0、非所有格key同一率97.5%、rep間一致率96.0%(現行95.6%)、追加LLM call 0、費用+0.03円/記事、Adv/PROMPT_SHA256不変。開示: 一般化の後退4件(いずれも無変更its形、誤りではない)、rep2の誤り1件(`out of our hands`→someone's)、goldはFable基準で再採点(独立盲検ではない)、標本は所有格約40件×2rep。Opus条件C: 必須修正後に配線可(反映済み=WIRING_DESIGN_05)。Production採用はユーザー判断(UDR)。
- 課題①(Std字義訳): **部分改善・未解消**(Closeしない)。C(独立検査+flag項目のみ再生成): F層字義NG 6→1/122、FAIL計8→4(残3は継承の既知分)、flag項目内 改善5/不変14/PASS→FAIL悪化0、未flag項目はバイト同一。検出器recall 5/6・precision 5/19。残存: `question shaped like a trophy`型(rep1未修復、rep2は語義誤認へ)。Cp(同一call自己監査、1 rep・61出力)はFAIL 0だが検出器としてはrecall 0で、文字列が変わる=事実上の生成Prompt変更(非劣化の構造保証なし)。M(再整合指示除去)は改善なし。追加費用: C≈0.2〜0.25円/記事。
- 原因の確定: ②=正規化段に所有者の指示対象を判定する規則・工程が無い(規定欠落)+規則3例示の偏り。①=字義/慣用を検査する工程が全段に無い+確率的字義選択(生成Prompt側の誘因仮説Mは本Trialで不支持)。

## 2. UDR登録(次番号=#173想定)
件名: Key Phrase 2課題 — ②possessor_roles(+A-1同梱)のX/Z Production採用可否、①字義訳の次方針。
- 判断A(②採用): 採用する/しない。採用時の付帯選択: (a)物が動作主のits=選択肢A「現状維持(its)を強制」[Fable推奨]/選択肢B「non_person_agentを分ける」(OPEN-481、追加Trial要) (b)受理条件=role条件付き(my/our→someone'sはrole=other_personのみ、共有許可表不変、A/B/C不変)[Fable推奨] (c)`qa_person_reference_generalized`定義の整合変更 (d)LLM出力に対する決定論後処理(revertのみ)の新方式 (e)承認済みPrompt(規則3の例示均等化・「迷う場合は自然な側」文の「迷う場合は置換しない」への置換)の変更 (f)既存完成記事は自動再生成しない(次回KP段再実行時のみ反映)。配線前にP-T2(迷う場合文の置換)のDEV確認(36unit×1rep、約11円)をFable裁量で実施。
- 判断B(①の方針): (1)Cを採用提案へ進める(+1 call/記事≈0.2〜0.25円、F層NG 6→1、trophy型は未解消のまま) (2)**追加Trial 1回(上限40円)**: C+flag項目再検査(C-recheck)と Cp rep2、精度向上策(二重検査)を比較し、残存型(trophy)の解消可否を確認してから採否提案 [Fable推奨] (3)現状許容(字義NG約2〜5%/F層を受け入れ、①は終了しない記録のまま保留)。
- Fable推奨: A=採用(付帯a=A、b=role条件付き)、B=(2)。理由: ②は再現性・非劣化・費用の全条件を満たし、記事Bの `reach for one's wallet` 型の揺れを構造的に止める。①はCに実効はあるが精度が低く残存型があるため、採用前に1回の確認が必要十分。
## 3. 更新
- `USER_DECISION_REGISTER_01.md` #173(上記、判断待ち)。OPEN-474 Status=`USER_DECISION_REQUIRED(UDR #173)`+要約。DECISION_LOG 1エントリ(Fable判定)。ACTIVE_TASK KP行(最新行)Status更新。
- 委任文逐語保存 `..._委任_19.md`(MARKER一致)。secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。完了したらUDR番号・commit hashのみ報告。
## 4. 禁止
コード変更0。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行を編集しない。
