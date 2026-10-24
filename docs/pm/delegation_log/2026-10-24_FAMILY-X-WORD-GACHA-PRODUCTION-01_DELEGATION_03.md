FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_03(Fableから、API 0): Adv `full_story_part3` のStyle Profile Gate(人間承認待ち)について、ユーザー判断事項をUDR登録し、OPEN-498/499の分類をFable判断で確定してcommit/push。

## Fable判断
- OPEN-499(本作のAdv part3の扱い)= **ユーザー判断要**。選択肢: (a)ユーザーが耳確認のうえ人間承認→Adv assemble→試聴ページ→page_verify(費用0) / (b)2回目の再生成(約+14.7円、案件上限110→125円、Local Rewrite再発の可能性あり) / (c)OPEN-498案Aを先に実装し再判定(費用ほぼ0だがSecondary確認とStyle Gateは残る)。Fable推奨=(a)。
- OPEN-498(gacha↔gotcha: CMU未登録の借用語でer109がfail-closed)= **修正へ進む候補だが、共有Validator(A/B/C含む)のASR受理境界に触れるためユーザー承認を得てから実施**(案A: `_HOMOPHONE_OVERRIDE_GROUPS`に`{gacha,gotcha}`を1件追加、NG→UNCERTAINへの降格のみで自動PASSにはならない、影響分析gate=保存ASR記録4,877件の再判定でPASS→NG 0、golden/wiring signature確認)。案B(借用語発音補完辞書の新設)は新受理クラス=ユーザー判断要。Fable推奨=案Aを承認のうえ実施(個別語追加は非スケーラブルなため、記事の中心語が辞書外の借用語である場合の運用は別途検討と注記)。

## 作業
1. `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR 1件(件名=『英単語ガチャ』Advanced最終パートの完成方法とgacha同音対応。選択肢(a)(b)(c)+OPEN-498案A承認の可否、推奨(a)+案A承認。耳確認用音声のローカルパス `er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/ear_check/adv_full_story_part3_regen1_final.mp3`(47.2秒)、聴取ポイント3点、Standard完成済み(320.08秒)、費用104.73円の内訳とAzure Secondary 36.07円の説明、を記載)。
2. `OPEN_ITEMS.md` OPEN-498/499 に上記分類とUDR番号を反映。`DECISION_LOG.md` 1エントリ(Fable判断)。
3. 日次累計(10-24把握分)を `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/BUDGET_PLAN_01.md` 末尾に記録: 約458.5(Y含む)+Z 46.82+X 104.73+学習テキスト0.23≒約610円/1,000円。
4. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_03.md`(Nは先頭「FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_03」を含むAgent呼出の0始まり通番、直近469以降)。
5. Git: `git status`でindex確認→`git commit --only`→`git push origin HEAD:main`(一時index方式、禁止操作なし、secret grep 0件)。
6. handback: UDR番号、commit hash、raw URL。