MARKER: FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01(O. Henry『賢者の贈り物』Std/Adv正式制作: 既存承認済みFamily Z Production経路で作品登録→Writer→plan/support/kp→TTS→Gate→組立→試聴ページ)
# ユーザー承認: 新規作品制作を承認(2026-10-24)。最終試聴PASSはユーザー判断。原文は末尾§Zに逐語。**最初に** `docs/pm/delegation_log/2026-10-24_FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01_USER.md` として§Zを逐語保存すること。

## 0. 前例(手順の正本として再利用)
- 『二十年後』: 委任文 `docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_委任_01.md`/`_02.md`/`_03.md`/`_04.md`、登録commit 1d6642897(`STORY_REGISTRY["after_twenty_years"]`+rights_block、`er062_family_z_structure_01.py` ROSTER/SPEAKER_CONFIG/LINT、`er062_family_z_writer_01.py` STORY_MAIN_CHARACTER、`er026_seeds/after_twenty_years/{story.md,seed.json,SOURCE_PROVENANCE.json}`、登録test)、証跡 `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/{RUNTIME_EVIDENCE_01,CP_CHECK_01,BUDGET_PLAN_01,SOURCE_CHECK_01,CLOSEOUT_01}.md`、試聴ページ `user_test/family_z_after_twenty_years_01/`(同形式)。
- 登録はデータ表追加のみ(ロジック変更0)を踏襲。作品固有のハードコード・新方式は導入しない。『二十年後』で発生した「plan段の話者判定キーワード順」等の既知の注意点は委任_02/_03の報告(`RESULT_PACKET_FZ20Y1.md`〜`FZ20Y4.md`、git管理外だがローカルにあれば)を確認。

## 1. 着手時の整合確認(ユーザー§3、結果を `docs/research/FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01/CP_CHECK_01.md` に)
 1. 正式Production経路(er026 runner、stage列、1起動ルール)。
 2. Std/Advの構成(3パート)・長さ・語彙・速度・Voice割当(既存Voice Pool・固定配役ルール: ナレーター/Della/Jim。Madame Sofronie等の脇役は既存ルールの範囲で。配役を増やさない)。人物の年齢・性格・感情に合うVoiceを既存Poolから選び、理由を記す。
 3. 原作忠実性の品質基準(FAMILY-Z-SOURCE-FIDELITY修正版B、`SOURCE_CHECK` 書式): 維持必須=Della/Jimの人物像と夫婦関係、Dellaの髪とJimの時計、各自が何を手放し何を贈ったか、最後の皮肉と愛情、原題『The Gift of the Magi』とその意味(Magi=東方の三博士の説明を学習者向けに自然に)。
 4. **Key Phraseの正式承認・配線状況**: A-1はPRODUCTION_WIRED。課題②(所有格一般化 one's/someone's)は2026-10-24に APPROVED_FOR_PRODUCTION となり、別agent(FX-KP 委任_20)が**現在Production配線中**。`docs/pm/ACTIVE_TASK.md` の委任_20行で状況を確認し、(a)kp段の実行時点で②が配線済み(commit済み・Fable受入)ならそのまま適用、(b)未配線なら現行Production(A-1のみ)でkp段を進め、**finalize前に再確認して②が配線済みになっていればkp段のみ再実行**(KP再生成の追加費用は小、記録する)。未承認のG3/課題①検査方式C等は適用しない(Productionに無いので自然に満たされるが、DEV flagをONにしない)。
 5. ASR/TTS/retry/fallback/Human Reviewの現行仕様(`TTS_EXECUTION_MODE=STANDARD`、RET/PNAP/UKUS X/Z WIRED、OPEN-479修正済み)。
 6. 時刻表現検査: 第1層(er006)・第2層(er078 時刻分岐)は修正済み(commit b5138e452/e0eb13ab4)。OPEN-482残存2件(純語形`ten thirty`↔`10:30`がUNKNOWN、`ten thirty`↔`1030`桁連結EQUAL)は別管理ID ASR-TIME-NUMERAL-EQUIVALENCE-01 で対応中。本作の原稿に時刻の語形(`eight o'clock`等)が出る場合はその影響可能性を事前に記し、HR Lockになった場合は原稿改変で回避せずFableへ。

## 2. 制作手順
 A. 原作テキスト(Public Domain、Project Gutenberg等)取得→`er026_seeds/the_gift_of_the_magi/{story.md,seed.json,SOURCE_PROVENANCE.json}`、`STORY_REGISTRY["the_gift_of_the_magi"]`+rights_block、ROSTER/SPEAKER_CONFIG/LINT、STORY_MAIN_CHARACTER("Della")、登録test(『二十年後』testを雛形に)。全回帰 自分起因0→commit/push(登録のみで1 commit)。
 B. Writer(Std/Adv、既存承認Writer・モデル)→原作忠実性チェック(`SOURCE_CHECK_01.md`、修正版Bの重大項目)→plan/support/kp→TTS(Std/Adv、他agentの「有料run(TTS)進行中」flagを確認し直列化、最大待機30分)→Gate→`provision_shell,gate,assemble,pages,page_verify` を**1起動**→試聴ページ `user_test/family_z_gift_of_the_magi_01/`(Std/Adv切替・通し・パート別・全スクリプト・KP・開発者情報なし)→公開page_verify(全音声再生・seek・リンク・表示)。
 C. **HR Lock/STOP発生時**: 自分で `approve_regenerate` しない。Lock理由(判定ログ原文)・ASR転記・該当テイク・原因分析(音声側か検査側か)を添えて**STOPしFableへ**(原稿改変での回避は不可)。RESTART_STORM回避: 有料run再起動は本委任文で明示した回数のみ(TTS段=Std/Adv各1起動、完成段=1起動)。cool-downはハングではないので自PIDを終了しない(26-6)。
 D. 費用: 上限 **100円**(目標70円)、内訳をstageごとに記録(`BUDGET_PLAN_01.md`)。10-24日次累計(現在約240円+並行Y≤27円+KP②≤25円)を記録、1,000円超過見込みなら事前STOP。ACTIVE_TASKに本管理IDの行を新設し有料run進行中/終了を記録。
 E. runtime evidence `RUNTIME_EVIDENCE_01.md`: 正式経路の起動コマンド・stage結果・model_id・RET/PNAP/UKUS発火有無・KP②適用有無(配線状況と実行時刻の対応)・Gate結果・HR Lock履歴・費用。
 F. SSOT(完成後): `OPEN_ITEMS.md` 新規OPEN(完成版提出・ユーザー最終試聴待ち)、OPEN-472(RET会話経路追認)に本run材料の有無を1行、`DECISION_LOG.md`(ユーザー承認・制作完了)、`docs/pm/USER_DECISION_REGISTER_01.md` 新規UDR(最終試聴PASS可否、非blocking、推奨=試聴後)。並行編集中の他agentがあるため、commit前に `git diff -- OPEN_ITEMS.md DECISION_LOG.md` で自分以外のhunkを確認(含まれる場合は数分待って再確認、残る場合は報告に明記)。
 G. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01_委任_01.md`(先頭MARKER一致、0始まり)。commit(変更ファイル明示、`git diff --cached --name-status`、`git commit --only -- <paths>`、secret grep 0件、`git add -A/-u/-f`禁止、wav/raw_usage_log/STOP関連不追跡)→`git push origin HEAD:main`。`.venv\Scripts\python.exe` を使う(`py`はPython 3.14で依存欠落)。
 H. 報告 `docs/pm/RESULT_PACKET_FZGM1.md`(ユーザー§6の8項目: 1試聴URLとページ検証 2構成・再生時間・Voice配役 3原作忠実性・品質検査 4KP・固有名詞・発音検査 5retry/再生成/HR 6実制作費・所要時間・量産性 7Production経路・evidence・SSOT/Git 8未解決OpenとUDR)+4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)+判定整合行+使用モデル(最新か・理由)。途中STOP時は到達stage・成果物・原因・選択肢を報告。

## §Z ユーザー指示原文(逐語)
# Family Z『賢者の贈り物』制作指示

## 1. 目的・対象

Family Zの新作として、O・ヘンリーの短編小説 **『賢者の贈り物（The Gift of the Magi）』** を制作する。

Standard／Advancedの2レベルを制作し、正式完成候補としてユーザー試聴ページまで公開すること。

**Status：新規作品制作を承認。完成版の最終試聴PASSはユーザー判断待ち。**

前作『二十年後』で使用した、承認済みFamily Z Production経路を利用する。作品固有のハードコードや新しい制作方式は原則導入しない。

## 2. 作品設計

### 原作忠実性

原作の中心的な魅力である、夫婦の互いを思いやる気持ちと、贈り物に関する意外な結末を確実に残すこと。

特に以下を維持する。

- DellaとJimの人物像、夫婦関係
- Dellaの髪とJimの時計という大切な持ち物
- それぞれが相手のために何を手放し、何を贈るのか
- 最後の皮肉と、その奥にある愛情
- 原題『The Gift of the Magi』とその意味

文字数・学習レベルに合わせた文章の整理・短縮は認めるが、主要設定・因果関係・結末を不必要に改変しない。

原作の表現や構成を機械的に残すことより、**原作の魅力を損なわず、英語学習者が自然に楽しめること**を重視する。

### 構成・長さ・Voice

既存のFamily Z承認仕様を踏襲する。

- 3パート構成
- Standard／Advancedそれぞれの承認済み語彙・文章・速度仕様
- 既存Voice Pool・固定配役ルール
- ナレーター／Della／Jimを中心とする自然な演じ分け
- 既存のKey Phrase・音声検査・公開品質Gate

人物の年齢・性格・感情に合ったVoiceを選択すること。特にDellaとJimの会話で、感情が伝わることを重視する。

音声表現を過度に演劇的にする必要はない。

## 3. 既存仕様との整合

着手時点でCURRENT_SPEC、DECISION_LOG、OPEN_ITEMSおよびProduction実装を確認すること。

特に以下を確認する。

1. Family Z『二十年後』で使用した正式Production経路
2. Standard／Advancedの構成・長さ・Voice割当
3. 原作忠実性の品質基準
4. Key Phraseの現時点の正式承認・配線状況
5. ASR・TTS・retry・fallback・Human Reviewの現行仕様
6. 『二十年後』制作時に修正した時刻表現検査、およびOPEN-482の最新状況

**未承認のKey Phrase改善案などを、本作品だけに先行適用しないこと。**

一方、既に正式承認・Production配線済みの共通品質改善は漏れなく適用する。

## 4. 制作・品質検証

作品登録から本文生成、音声化、品質検査、公開まで、既存の正式Production工程で一貫して実行する。

品質上の問題が発生した場合、既存仕様・承認済み予算・STOP条件の範囲内で、原因究明→修正→再検証を自律的に進めること。

- 正常な音声・成果物は可能な限り再利用する。
- 不要な再生成・重複検査・Web検索を避ける。
- 独立工程は並列化し、制作時間を最小化する。
- Human Reviewを通常の解決手段とせず、既存の自動解決機構を活用する。
- 既存の承認品質を満たしたら追加の磨き込みをせず完成させる。

作品固有の問題を解決するために、未承認の新仕様や品質基準変更をProductionへ導入しないこと。

## 5. QCD

優先順位は **品質（Q）＞完成速度（D）＞量産単価（C）**。

- 品質：既存Family Zの承認品質を厳守。
- 速度：不要な待機・逐次化を避け、最短で完成。
- 量産単価：70円／記事セットを目標とし、品質維持を前提に低減を図る。
- 開発費：既存の日次予算・承認範囲を遵守。

問題解決に伴う必要な修正は自律的に進めるが、予算超過・重大な品質問題・未承認仕様変更・解決不能なblockerではSTOPすること。

## 6. 完成時の成果物・報告

以下を揃えて報告すること。

1. **完成版試聴URL**：Standard／Advanced切替、通し再生、パート別再生、全スクリプト、Key Phraseを掲載。開発者向け情報は除外。
2. **構成・再生時間・Voice配役**
3. **原作忠実性・品質検査結果**
4. **Key Phrase・固有名詞・発音検査の結果**
5. **retry／再生成／Human Reviewの発生状況と原因**
6. **実制作費・所要時間・量産性への示唆**
7. **Production経路・runtime evidence・SSOT／Git反映状況**
8. **未解決Open Item・ユーザー判断事項**

公開ページは全音声再生、シーク、リンク、表示内容を検証すること。

FableはClaudeの完了報告を鵜呑みにせず、正式経路・実行証拠・検査結果・原作忠実性・QCDを独立して照合する。

### 完了条件

Standard／Advancedとも正式Production経路で生成し、必要な品質GateをPASS、完成版試聴ページを公開する。

その後、**ユーザーの最終試聴PASSをもって作品完成を承認**する。

未解決の判断事項があればOPEN_ITEMSに記録し、作品の承認判断と独立課題を適切に区別すること。

---

**既存のFamily Z制作基盤を最大限活用し、品質を維持しながら、最短・低単価で『賢者の贈り物』を完成させること。**