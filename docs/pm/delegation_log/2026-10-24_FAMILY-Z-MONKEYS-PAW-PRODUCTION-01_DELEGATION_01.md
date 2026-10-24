FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01(Fableから): ユーザー承認済みのFamily Z新作 W. W. Jacobs『The Monkey's Paw(猿の手)』を、『二十年後』『賢者の贈り物』と同じ承認済みProduction経路でStandard/Advanced完成版→ユーザー試聴ページ公開まで制作する。ホラー・サスペンスとして恐怖・不安・緊張感を楽しめる作品にする(会話と語りで。未承認の効果音・演出仕様・作品固有ハードコードは追加しない)。最終試聴PASSはユーザー判断(UDR登録)。並行してFamily X『英単語ガチャ』を別agentが制作中(TTS直列化flagを尊重、相手のrunを終了・待機解除しない)、Family Y 委任_25(text-only)も並行中。

## 0. 最初に(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語・改変禁止)を `docs/pm/delegation_log/2026-10-24_FAMILY-Z-MONKEYS-PAW-PRODUCTION-01_USER.md` に保存(Family X分と同一原文。X側も別名で保存するが重複可)。
- 直前作の手順を踏襲: `docs/research/FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01/{CP_CHECK_01,SOURCE_CHECK_01,BUDGET_PLAN_01,RUNTIME_EVIDENCE_01,CLOSEOUT_01}.md` と登録commit 5bf3d590b の差分(STORY_REGISTRY/STORY_VOICE_ROSTER/STORY_SPEAKER_CONFIG/STORY_LINT_CONFIG/STORY_MAIN_CHARACTER のdata表追加のみ、ロジック変更0)を参照。
- 着手時確認(`docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/CP_CHECK_01.md` §A): (1)正式Production経路(er026 runner `--story the_monkeys_paw --run run_sf_prod_01`、E2E stage順、完成段1起動) (2)Std/Adv構成・語数範囲・Voice=正式Voice表+決定的割当規則(pinなし) (3)原作忠実性基準(Seed `source_essentials`、維持必須=猿の手と3つの願い/危険の警告/White一家の人物関係/願いと悲劇の因果/終盤の緊迫/最後の願いと余韻の結末) (4)KP: A-1・課題②=PRODUCTION_WIRED適用、課題①X2p'(UDR #179未回答)等の未承認案は不適用(`EIGO_KP_GLOSS_ALIGNMENT`既定のまま) (5)ASR/TTS/retry/fallback/HR現行仕様、本日反映のASR数値・時刻修正(OPEN-487/489/491/494、commit d6d17562b/7d4ec5bc4/1d104d711)がHEADに含まれること (6)**作業ツリー確認**: `git status`で、Z Production経路のimport graphに含まれるファイルに未commit変更がないことを確認し記録(該当があればFableへ報告して待つ。無関係ファイルの他agent差分は記録のみ) (7)日次予算: 10-24把握分約433円+Y≤30円+X≤100円+本作上限100円で1,000円内であることを `BUDGET_PLAN_01.md` に記録。

## 1. 原作・権利(`SOURCE_CHECK_01.md`)
- Project Gutenberg(『The Lady of the Barge』1902収録、または単独eBook)から原文を取得、sha256・取得日・行範囲を記録。W. W. Jacobs 没1943-09-01: 日本での保護期間(死後50年+英国分の戦時加算)を計算して満了を確認、米国も1902年出版でPD。第三者翻訳・翻案・あらすじ不使用。
- 原文の要素確認表(設定、Mr./Mrs. White、Herbert、Sergeant-Major Morris、Maw and Meggins の使者、3つの願い、200ポンド、墓地からの帰還の暗示、ドアのノック、最後の願い、静かな街灯の結末)。Seedの withhold/spoiler 語を設定。

## 2. 登録・制作
- 作品登録はdata表のみ(ロジック変更0)。登録test・全回帰(他agent起因の失敗は`docs/research/REGRESSION_BASELINE_2026-10-24.md`と比較)。
- Voice: 決定的割当規則に従う(narrator/Mr. White/Mrs. White/Herbert/Morris/使者)。登場人物の発話者数が多いので、ROSTERは原作の発話者のみ、規則上の割当を記録(人選の個別例外は入れない)。
- 制作は各stage 1起動、`TTS_EXECUTION_MODE=STANDARD`、`.venv\Scripts\python.exe`、各起動前 `tools/stop_scope_check_01.py --managed-id FAMILY-Z-MONKEYS-PAW-PRODUCTION-01` rc=0。HR Lock時はapprove_regenerateしない(記録しFableへ)。原稿改変で検査を回避しない。
- 上限100円(目標70円)。80円で見込み再計算。
- 試聴ページ `user_test/family_z_monkeys_paw_01/`、公開page_verify(Playwright)PASS証跡。

## 3. 記録・SSOT・Git
- `docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/{CP_CHECK_01(§B 原作忠実性チェックポイント引用照合),SOURCE_CHECK_01,BUDGET_PLAN_01,RUNTIME_EVIDENCE_01}.md`(『賢者の贈り物』と同書式)。ホラーとしての緊張感の所見(会話・語りの運び)も§Bに1項。
- OPEN_ITEMSにUDR待ち項目(非blocking)、`docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(最終試聴PASS可否、A PASS/B指摘、推奨A)、DECISION_LOG 1エントリ。不具合は11-8に従い委任範囲内なら修正まで(登録だけで止めない)。
- commit前に`git status`でindex確認→`git commit --only -- <本委任ファイル>`→`git push origin HEAD:main`(wav・raw_usage_log・STOP・ACTIVE_TASK・RESULT_PACKET不追跡、OPEN-490不復元・不stage)。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。secret grep 0件。他agent(X/Y)のSSOT差分を巻き込まない(一時index方式可)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-MONKEYS-PAW-PRODUCTION-01_DELEGATION_01.md`(Nは先頭「FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01」を含むAgent呼出の0始まり通番、直近459以降)。

## 4. handback(ユーザー原文§6の8項目)
1 試聴URL / 2 構成・再生時間・Voice / 3 原作忠実性検査結果(チェックポイント引用) / 4 KP・固有名詞・発音 / 5 retry・再生成・HR / 6 実費・所要時間 / 7 Production経路・runtime evidence(HEAD、作業ツリー確認) / 8 SSOT・Git・残存Open Item・UDR番号。RESULT_PACKET 4行、commit hash、raw URL。

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