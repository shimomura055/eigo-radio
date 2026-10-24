FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01(Fableから): ユーザー承認済みテーマ「英単語の勉強を『ガチャ』にしたら楽しくなる?」(元記事 GIGAZINE 2026-10-23 https://gigazine.net/news/20261023-dopatan-wordgacha/ 、対象サービス https://wordgacha.com/ )を、既存Family Xの正式Production経路でStandard/Advanced完成版→ユーザー試聴ページ公開まで制作する。最終試聴PASSはユーザー判断(UDR登録)。並行してFamily Z『猿の手』を別agentが制作中(TTS直列化flagを尊重、相手のrunを終了・待機解除しない)、Family Y 委任_25(text-only)も並行中。

## 0. 最初に(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語・改変禁止)を `docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_USER.md` に保存。
- 旧テーマ「AIも『一人で正しいより、みんなで間違えたい』?」はrepo内に着手痕跡なし(Fable Grep済み: 0件)。念のため`er0*_output`外をGrepし、あれば費用・成果を記録して停止、なければ「着手なし」と記録。
- 着手時確認(`docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/CP_CHECK_01.md` §A): (1)Family Xの正式初回Production経路(直近のX Production run、例 `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/` の起動CLI・stage順)を特定し同一経路を使う (2)承認済みResearch/Fact/Writer/Entertainment Revision/Std-Adv仕様/音声仕様(CURRENT_SPECを節単位Grep、全文読込禁止) (3)KP: A-1と課題②(所有格一般化)はPRODUCTION_WIRED(X/Z)=適用、課題①X2p'(UDR #179未回答)・G3等の未承認案は適用しない(DEV flagをONにしない、`EIGO_KP_GLOSS_ALIGNMENT`は既定のまま) (4)ASR/TTS/retry/fallback/HR現行仕様、本日反映のASR数値・時刻修正(OPEN-487/489/491/494、commit d6d17562b/7d4ec5bc4/1d104d711)がHEADに含まれること (5)**作業ツリー確認**: `git status`で、X Production経路のimport graphに含まれるファイルに未commit変更がないことを確認し記録(er110_*やdocs等の無関係ファイルの他agent差分は記録のみ。該当があればFableへ報告して待つ) (6)日次予算: 10-24把握分約433円+Y≤30円+Z≤100円+本作上限100円で1,000円内であることを `BUDGET_PLAN_01.md` に記録。

## 1. Research・事実整理(承認済みResearch/Fact経路内で)
- 一次情報(wordgacha.com)とGIGAZINE記事で確認できる事実のみ: 10連ガチャで英単語カード収集/出現頻度によるレア度/レア単語で特別演出・連続抽選/カードから意味・発音を確認/収集・ランク・実績などのゲーム要素。
- 混同禁止(Writer/Factに渡す注意): ゲームの楽しさ≠学習効果の高さ/派手な演出≠ドーパミン増加の実測/レア単語≠学習上重要な単語。学習効果の科学的実証をうたわない。機能・実験結果を創作しない。
- 記事の中心: 「英単語を覚えることより、レアな単語を引くことに夢中になってしまいそうな逆転した発想」の意外性と面白さ。既存Entertainment Revisionを活用。本作固有のPrompt・演出機構・例外処理は新設しない。
- 事実検査結果を `FACT_CHECK_01.md`(主張↔出典URLの対応表、創作0の確認)に残す。Web取得は必要最小限(2 URL+必要ならサービス内ページ数枚)。

## 2. 制作
- 正式Production経路で1起動ずつ(stage分割は既存経路どおり)。有料run起動回数は各stage 1回、再起動はHR Lock/STOPを迂回しない範囲で既存retry/fallback/resumeに任せる。HR Lockになったら自分でapprove_regenerateしない(状態を記録しFableへ)。
- `TTS_EXECUTION_MODE=STANDARD`、`.venv\Scripts\python.exe`。各起動前に `tools/stop_scope_check_01.py --managed-id FAMILY-X-WORD-GACHA-PRODUCTION-01` rc=0。
- 上限100円(目標70円)。累計80円で見込み再計算、100円超過見込みなら停止前に報告。
- 試聴ページ `user_test/family_x_word_gacha_01/`(Std/Adv切替・通し・パート別・全スクリプト・KP、開発者向け情報なし)を公開し、公開page_verify(Playwright実再生)PASSを証跡化。

## 3. 記録・SSOT・Git
- `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/{CP_CHECK_01,FACT_CHECK_01,BUDGET_PLAN_01,RUNTIME_EVIDENCE_01}.md`(RUNTIME_EVIDENCEは『賢者の贈り物』の書式: 起動履歴・HEAD commit・モデル・Voice・構成/再生時間・ASR/TTS/retry/HR・approved equivalence・PASS_WITH_WARNING・KP・page_verify・費用・所要時間)。
- OPEN_ITEMSに本作のUDR待ち項目(非blocking)を登録、`docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(最終試聴PASS可否、選択肢A PASS/B指摘あり、推奨A)。DECISION_LOG 1エントリ。不具合を見つけたら11-8に従い分類し、委任範囲内なら修正まで進める(登録だけで止めない)。
- commit前に`git status`でindex確認→`git commit --only -- <本委任ファイル>`→`git push origin HEAD:main`(wav・raw_usage_log・STOP・ACTIVE_TASK・RESULT_PACKET不追跡、OPEN-490自動書換え不復元・不stage)。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。secret grep 0件。他agent(Z/Y)のSSOT差分を巻き込まない(一時index方式可)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_01.md`(Nは先頭「FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01」を含むAgent呼出の0始まり通番、直近459以降)。

## 4. handback(ユーザー原文§6の8項目に対応)
1 試聴URL / 2 構成・再生時間・Voice / 3 事実検査結果(混同禁止3点の確認含む) / 4 KP・固有名詞・発音 / 5 retry・再生成・HR / 6 実費・所要時間 / 7 Production経路・runtime evidence(HEAD、作業ツリー確認結果) / 8 SSOT・Git・残存Open Item・UDR番号。加えてRESULT_PACKET 4行、commit hash、raw URL。

【ユーザー原文】
# Family X／Family Z｜新作2作品 Production制作指示【改訂版】

## 1. ユーザー決定・前指示の変更

以下の2作品を正式制作対象とする。

### Family X：題材変更

**「英単語の勉強を『ガチャ』にしたら楽しくなる？」**

元記事：GIGAZINE（2026年10月23日）

https://gigazine.net/news/20261023-dopatan-wordgacha/

対象サービス：

https://wordgacha.com/

先に指示した「AIも『一人で正しいより、みんなで間違えたい』？」の記事制作は**取り消す**。

旧テーマについて新規Research・生成・音声化を行わない。既に着手済みであれば、既存成果と費用を記録して作業を停止し、今回の正式テーマに切り替える。重複作業を避けること。

### Family Z：変更なし

**W・W・ジェイコブズ『猿の手（The Monkey's Paw）』**

ホラー・サスペンス作品として制作する。

両作品とも、Standard／Advancedの完成版作成からユーザー試聴ページ公開までを承認する。

最終試聴PASSはユーザー判断とする。

---

## 2. Family X｜英単語ガチャ

### 2-1. 記事の中心テーマ

「英単語の暗記という地味な勉強に、ガチャゲームの仕組みを取り入れたらどうなるか？」

という意外性と面白さを中心にする。

GIGAZINEの記事と対象サービスの一次情報を確認し、以下を中心に事実を整理する。

- 10連ガチャで英単語カードを集める。
- 英単語の出現頻度によってレア度が設定されている。
- レアな単語を引くと、特別な演出や連続抽選が発生する。
- カードから英単語の意味や発音などを確認できる。
- カード収集・ランク・実績などのゲーム要素がある。

記事の面白さは、**英単語を覚えることより、レアな単語を引くことに夢中になってしまいそうな逆転した発想**にある。

既存Family XのEntertainment Revision等を活用し、この魅力を生かすこと。

### 2-2. 事実関係の注意点

今回の記事は、ゲームの紹介・体験レビューである。

以下を混同しないこと。

- ゲームを楽しめることと、実際に英語学習効果が高いことは別。
- 派手な演出があることと、脳内ドーパミンの増加が実測されたことは別。
- レアな英単語が学習者にとって重要な英単語とは限らない。

ゲームの学習効果を科学的に実証したような説明はしない。

一次情報とGIGAZINEの記事で確認できる内容を優先し、面白さのために機能や実験結果を創作しないこと。

### 2-3. 制作仕様

既存のFamily X Production経路を使用する。

- 承認済みResearch／Fact／Writer／Entertainment Revision
- Standard／Advancedの難易度・構成・音声仕様
- 正式Productionに反映済みのKey Phrase仕様
- 既存のTTS／ASR／品質Gate
- 現行のretry／fallback／regeneration／resume

未承認のKey Phrase①字義訳改善方式などは先行適用しない。

本作固有のPrompt・特別な演出機構・例外処理を新設しない。

## 3. Family Z｜『猿の手』

前指示の制作方針を維持する。

### 3-1. 原作忠実性

信頼できる原文を使用し、権利を確認する。

重要な要素を保持する。

- 猿の手と3つの願い
- 願いに伴う危険への警告
- White一家の人物関係
- 願いと悲劇の因果関係
- 終盤の緊迫した展開
- 最後の願いと余韻を残す結末

文字数制限に応じた短縮は許容するが、重要な設定・伏線・結末を変更しない。

### 3-2. ホラーとしての魅力

これまでのFamily Zとは異なり、恐怖・不安・緊張感を楽しめる作品とする。

既存の3パート構成、Voice Pool、TTS速度仕様を維持する。

会話と語りによる自然な緊張感を重視し、未承認の効果音・演出仕様は追加しない。

## 4. 共通のProduction実行方針

両Familyで以下を厳守する。

1. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSを確認し、最新の承認済み仕様を使用する。
2. 正式初回Production経路で制作する。
3. Key Phrase、固有名詞、TTS、ASR、数値表現等の共通品質仕様を適用する。
4. 不具合は委任範囲・予算内で原因究明→修正→検証まで自律的に進める。
5. 不具合をOpen Itemに登録・報告するだけで停止しない。
6. 正常な成果物・音声・検証データを再利用する。
7. 独立工程は可能な限り並列化する。
8. 承認済み品質を満たした時点で完成させ、不要な追加Trialを行わない。

Production経路に未commitの他案件の変更が混入していないことも確認する。

## 5. QCD・予算

優先順位は**品質（Q）＞完成速度（D）＞量産単価（C）**。

- 量産単価目標：70円／記事セット
- 開発費：プロジェクト全体で1,000円／日（JST）
- 上限接近が見込まれる場合は事前報告
- 無断超過は禁止
- 不要な待機・日付分割・追加Trialは行わない

既存仕様・予算・STOP条件の範囲で自律的に完成を目指す。

## 6. 完成報告・受入条件

Family X／Zそれぞれについて報告すること。

1. Standard／Advanced完成版試聴URL
2. 記事・作品構成、再生時間、Voice配役
3. 事実関係または原作忠実性の検査結果
4. Key Phrase・固有名詞・発音品質
5. retry・再生成・Human Review
6. 実制作費・所要時間
7. 正式Production経路とruntime evidence
8. SSOT／Git反映状況、残存Open Item、ユーザー判断事項

FableはClaudeの完了報告を独立照合し、Production経路・実動作・品質・QCDに基づいて受入評価すること。

**両作品とも、完成版の公開と品質検査PASSまで進め、最終試聴PASSをユーザー判断として提出する。**

---

## 最重要事項

Family Xは、英単語をガチャにするというユニークな発想を楽しく紹介する。

Family Zは、ホラー作品としての緊張感と原作の魅力を維持する。

いずれも既存の承認仕様を守り、最速・低単価で完成させること。