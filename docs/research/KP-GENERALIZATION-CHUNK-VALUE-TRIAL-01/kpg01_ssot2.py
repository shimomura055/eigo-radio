# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
open_row = (
    "| OPEN-619 | **KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 [種別=Trial(DEV/Trial専用経路のみ・Production code/Prompt/Validator変更0)、委任_01完了(2026-10-30)、Closeout案=USER_DECISION_REQUIRED(Status上限VALIDATED、Fable最終判定待ち)、採用はユーザー判断]**"
    "(ユーザー指示2026-10-30、原文=docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01_USER.md)Key Phrase候補(フレーズ枠)の一般化・塊としての学習価値の品質改善。"
    "**結果**(Sonnet実読、14ケース): ユーザーが修正せず選べる候補の割合 現行26/66(39%)→統合方式A 56/70(80%)→**工程分離方式D 61/71(86%)**(Std 27%→88%)、『3件以上選べる』ケース 現行4/12→D 12/14。"
    "D=候補源(現行P7+過剰生成)→塊判定(F/C)→トークン分類による構造化一般化(CORE/SLOT/DROP、display_formはコード組立)→別系列検証(gemini)→決定論検査。必須9例: 一般化5中3達成(at the time of/narrow down/turn something around)+G2は一般化単体で達成、G1(take points away from)は未達、学習価値4/4。"
    "**設計上の発見**: 現行canonicalizationは規則1〜5以外の変換を決定論検証で却下するため、目的語のsomething化・後続名詞句の除去は仕様上不可(不具合ではない)=改善には学習表示用display_formの新しい許容ルール(OPEN-349と同系統)が必要で、採用はユーザー判断(分類D)。"
    "残NG(D 10/71): 自由な組合せ混入4・一般化で語義変化2・不自然な一般形2・易しい1・受動形残り1。Before成功例26件中6件がDで脱落。"
    "**新規所見の分類**: (a)学習表示用一般化の新許容ルール=ユーザー判断要(UDR登録・未提示) (b)Dの意味破壊ガード・塊判定2回和集合等の追加Trial(約¥5、Cap追加要)=修正へ進む(次委任案) (c)独立判定にdeepseek-v4-proを既定thinkingで使い1回¥7.4を要した費用事故=実害なし(以降flash非thinkingへ切替・手順をkpg01_judge.pyに固定)。"
    "費用¥79.1(Cap¥60→理由記録で¥80未満)。未実施/限界=独立判定は8/14ケース・未使用記事のBefore再現1ケース・D_sol未実施・Z会話体1ケース。"
    "証跡=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/{CURRENT_STATE_01,TRIAL_DESIGN_01,RESULT_01}.md、比較ページ=https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/、報告=docs/pm/RESULT_PACKET_KPG01.md。 |")
dl = (
    "- 2026-10-30 | KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01-DECISION-01 Key Phrase選定・一般化の品質改善Trial(委任_01)完了・Closeout案=USER_DECISION_REQUIRED(Fable最終判定待ち、Trial専用・Production変更0) | "
    "工程分離方式D(候補源=現行P7+過剰生成→塊判定→トークン分類による構造化一般化→別系列検証→決定論検査)が、修正せず選べる候補の割合を現行39%→86%(統合方式Aは80%)へ改善。"
    "現行canonicalizationは規則1〜5以外の変換を却下するため、目的語のsomething化・後続名詞句の除去には学習表示用display_formの新しい許容ルール(OPEN-349同系統)が必要=採用はユーザー判断(UDR登録、未提示)。"
    "費用¥79.1。証跡=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/RESULT_01.md、OPEN-619。")
at = (
    "(KG)KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01=委任_01完了(2026-10-30): Key Phrase一般化・塊価値の品質改善Trial(Trial専用・Production変更0)。工程分離方式Dで修正せず選べる率 現行39%→86%(A統合80%)、必須9例は一般化3/5+学習価値4/4。"
    "Closeout案=USER_DECISION_REQUIRED(Fable最終判定待ち、UDR登録・未提示)。費用¥79.1/Cap¥60→¥80未満。比較ページ=https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/、"
    "RESULT_01.md=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/、報告=docs/pm/RESULT_PACKET_KPG01.md、OPEN-619。")
udr = (
    "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 **登録済み・未提示(Fableが提示)・分類D**(2026-10-30): Key Phrase候補の品質改善方式(工程分離方式D)の採否と前提判断。"
    "(1)学習表示用の一般化(display_form: 目的語のsomething化・固定表現の後続名詞句の除去、本文一致のsource_spanとは別validator)を新しい許容ルールとして認めるか(OPEN-349同系統)、"
    "(2)提示が7件に満たなくてもよいか(Dは平均5.1件、品質を下げて埋めない)、(3)G1型(比喩語義のある動詞+名詞: take points away from)を一般化優先にするか、"
    "(4)費用+約¥2/記事セット(最大、既存段置換での相殺は未確認)の容認、(5)追加Trial約¥5(意味破壊ガード・塊判定2回和集合)の承認。"
    "推奨=方式Dの方向で追加Trial後に実装設計(Opus条件A)へ。根拠=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/RESULT_01.md 9節、OPEN-619。")
json.dump({"open": open_row, "dl": dl, "at": at, "udr": udr, "open_no": "619", "restore_key": "| OPEN-618 |", "restore_from": "4442b648b"}, open(os.path.join(HERE, "ssot2.json"), "w", encoding="utf-8"), ensure_ascii=False)
open(os.path.join(HERE, "msg2.txt"), "w", encoding="utf-8").write(
    "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_01: 一般化・塊価値の品質改善Trial(方式A/B/C/D比較、修正せず選べる率39%->86%)・比較ページ・RESULT_01・SSOT。Trial専用、Production変更0\n\n"
    "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n")
print("ssot2 written")
