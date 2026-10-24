# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_05(Trial-03: 英語学習解説 Part 1・Part 2 改善Trial、3作品Advanced、DEV/Trial専用、Production変更0、上限10円)
Status: TRIAL_APPROVED(ユーザー2026-10-25、UDR #185への回答=案Aを拡張した形) / Production採用・配線: 未承認 / 到達可能Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED

## 0. ユーザー原文(2026-10-25、逐語。まず `docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_03.md` に以下を一字一句そのまま保存すること)

```
# Claude Code指示｜英語学習解説 Part 1・2 改善Trial

## 1. 承認事項・目的

ユーザーは、英語学習解説のPart 1・Part 2改善Trialを承認しました。

対象は計3作品です。

1. **Family Z『賢者の贈り物』**（必須）
2. **Family Xの既存完成記事から1作品**（必須）
3. **Family Zの既存作品から1作品**

2・3の作品選定はClaude/Fableに委任します。異なる英文構造やKey Phraseを検証できる組み合わせを選び、理由を報告してください。

Standardは対象外。**Advancedの学習解説テキストのみ**を検証します。

Status：TRIAL_APPROVED。Production採用・配線は未承認です。

## 2. Part 1｜Vocabulary & Expressions

Trial-02の実用性重視版をベースに改善してください。

目標は、単語・表現の意味を説明するだけでなく、**実際にどのような場面で使え、どんなニュアンスが伝わるのかを理解できる解説**にすることです。

改善方針：

- 日常生活に加え、仕事・社会での使用場面にも目を向ける。
- 比喩的・拡張的な用法が自然に存在する場合は説明する。
- 具体的な使用場面を示し、表現の使い分けやニュアンスが理解できるようにする。
- すべてのPhraseに仕事での用途や比喩表現を無理に当てはめない。
- 文法解説に脱線せず、実用性を中心にする。
- 必要十分な説明量とし、単なる文章の水増しはしない。

『賢者の贈り物』では、特に以下を確認してください。

- `hand down`：家族内の継承だけでなく、技術・知識・経験を後輩や次世代へ伝える場面
- `catch sight of`：現在の良好な実用性を維持
- `catch one's breath`：身体的に息を整える意味に加え、忙しさから一息つく用法

## 3. Part 2｜Grammar & Sentence Structure

**Trial-02の『whose』解説はユーザー評価NGです。**

理由は、Advancedの学習者にとって極めて基本的な用法であり、この文章でわざわざ説明する価値が低いためです。

### 新しい選定方針

**作中から、Advancedの学習者でも難しい・煩雑・構造や意味を理解しにくいと考えられる一文を選び、その読解を助ける文法・構文解説を作成してください。**

重視すること：

1. 学習者がなぜその文章を理解しにくいのか。
2. どの文法・構文が理解を難しくしているのか。
3. その構文がどのような仕組みで成立しているのか。
4. 通常の語順や別の表現との違いは何か。
5. その違いによって意味・ニュアンス・表現効果がどう変わるのか。

基礎的な文法は、特殊な用法や重要な表現効果がない限り選ばないでください。

文法の高度さを競うのではなく、**解説によって文章の理解がどれだけ深まるか**を判断基準とします。

### 『賢者の贈り物』での重要な評価対象

次の英文を対象にしてください。

"Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers."

この文章では、`whose` よりも**倒置構文**の解説が明らかに有益です。

単に「倒置が使われている」と説明するのではなく、

- なぜ通常とは異なる語順を使っているのか
- 通常の語順ではどうなるのか
- 情報の提示順序や焦点がどう変わるのか
- 原文の文学的な効果は何か

まで説明してください。

ただし、この一例を全作品に機械的に適用せず、ほかの2作品では、それぞれの本文で最も解説価値の高い構文を自律的に選定してください。

## 4. Part 3・Part 4

今回の改善対象ではありません。

- Part 3：現行Prompt維持
- Part 4：現行Prompt維持

ただし、4 Part一括生成による全体の品質低下や副作用がないかは確認してください。

## 5. Trial設計・実行

既存のTrial-02成果・Prompt・本文を再利用し、**Part 1・2のPrompt変更による効果を同時に検証**してください。

- 3作品ともAdvancedで生成
- 各作品の正式な本文・Key Phraseを使用
- Part 1・2以外の条件は原則固定
- 既存Trial-02をBeforeとして比較
- 新規作品については、必要な範囲で同条件のBeforeを取得
- 本文引用の逐語一致、意味の正確性を確認
- 追加の音声生成は不要
- 正式Production経路は変更しない

初回で問題が見つかった場合も、承認Scope・予算・STOP条件内で原因究明、Prompt改善、再検証まで自律的に進めてください。

改善見込みの低い反復は行わず、必要十分な品質に達した時点でTrialを終了してください。

## 6. 評価・受入条件

### Part 1

- Key Phraseの実用場面が具体的に分かる。
- 実生活での使い方やニュアンスが理解できる。
- 自然な拡張用法を取りこぼしていない。
- 不自然な用途や用法を創作していない。
- 文法解説との役割重複がない。

### Part 2

- その文章を選んだ理由に十分な学習価値がある。
- Advancedの読者が理解に苦しむ可能性のある構文を選べている。
- 文法・構文の仕組みを分かりやすく説明している。
- 必要に応じて通常の語順や表現との差を説明している。
- 意味・ニュアンス・表現効果の理解につながる。
- 基本的すぎる文法を安易に選んでいない。

**特に、Part 2は「文法説明として正しい」だけではPASSとしないこと。選定自体の学習価値を評価してください。**

## 7. QCDと進行管理

優先順位は品質 ＞ 速度 ＞ 量産単価 ≫ 開発費です。

- 既存のPrompt・本文・検証結果を最大限再利用する。
- 独立作業は並列化する。
- 不要な追加LLM呼出やWeb検索を避ける。
- 開発予算と既存STOP条件を遵守する。
- 本Trialの追加実費と、Production採用時の量産費用を分けて報告する。
- 新しいValidatorや複雑な検査機構を安易に増やさない。

## 8. 最終報告

Fable独立評価を含め、以下を報告してください。

1. 選定した3作品と、その理由
2. Part 1・2の改善Prompt
3. **3作品×4 Partの出力全文（無編集）**
4. Part 1の実用性評価
5. Part 2の構文選定・解説品質評価
6. Trial-02との比較と残存問題
7. Part 3・4への副作用の有無
8. 実費・生成時間・量産単価への影響
9. Trial Closeout Status（VALIDATED／REJECTED／USER_DECISION_REQUIRED）
10. SSOT・Git反映状況

特に『賢者の贈り物』については、前回のwhose解説から倒置解説へ改善され、実際の学習価値が高まったかを明確にしてください。

**Trialの結果が良好でも、ユーザーの正式承認前にProductionへ配線しないこと。**

最終目標は、Part 1では実際に使える英語表現を学べること、Part 2では難しい英文の読み方・構造・意味を理解できることです。
```

## 1. 前提(Fable把握、要確認)
- Trial-02の資産: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{run_trial_02.py,PROMPT_02.md,PROMPT_DIFF_02.md,OUTPUT_02_RAW.md,INPUT_CHECK_02.md,usage_02.json,EVAL_02.md,FABLE_EVAL_02.md,BUDGET_LOG_01.md}`、ユーザー原文 `docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_02.md`(Part 1実用性重視ルール・参考例)。モデル=Luna(gpt-6-luna、Trial-01/02と同一model_id・API設定)。費用実績=Trial-02 0.171円/1call。
- 『賢者の贈り物』Advanced本文・KP 3個(hand down / catch sight of / catch one's breath)はTrial-02と同一。
- 作品選定(Fable委任→Sonnetが選定し理由を報告。Fableが受入時に確認):
  - Family X: ユーザー最終承認済み(CLOSED_USER_PASS)の記事から選ぶ: 候補=『英単語ガチャ』(word_gacha)、『イグ・ノーベル賞2026』(ig_nobel_2026)、『英国の電車マナー』(uk_train_speaker_playback、本日承認)、コーヒー系等。選定基準=Advanced本文の英文構造が物語文と異なる(説明文・引用・数値表現・複文)、正式KP 3個が句動詞/イディオム/コロケーションの別種を含む、正式KP成果物(gloss含む)が残っている。
  - Family Z: 『賢者の贈り物』以外の完成作品(猿の手/開いた窓/二十年後/メロス。『告げ口心臓』はAdvユーザーNG中のため対象外)。選定基準=会話中心・語順/構文が『賢者』と異なる・正式KPが残っている。
  - 各作品の「正式な本文・Key Phrase」はProduction runの最終Adv本文(X: `er019_output/.../run_*/`系の英訳Adv最終、Z: `er026_output/family_z_production_e2e_01/<story>/run_*/writer/r2.md`等)と正式KP(kp stage成果)から取り、出典pathとsha256を `INPUT_CHECK_03.md` に記録。
- Opus条件Aレビュー: 本TrialはPrompt文言の改善Trial(既存Trial-02の枠組み・処理フロー不変)のため不要(Fable判断)。
- 予算: 上限10円(推定: After 3作品×1call+新規2作品のBefore 2call=5call≈1円。再検証で数call増えても十分)。日次1,000円内。

## 2. 作業
A. Prompt改訂 `PROMPT_03.md` + `PROMPT_DIFF_03.md`(Trial-02比、変更はPart 1・Part 2の指示のみ。Part 3/4・出力形式・本文/KP注入方式は不変):
   - Part 1: ユーザー原文§2の改善方針を指示化(日常+仕事・社会の場面、比喩的・拡張的用法は自然に存在する場合のみ、使い分け・ニュアンス、無理な当てはめ禁止、文法脱線禁止、水増し禁止)。参考例(USER_02 §3)は品質の方向性として示す。
   - Part 2: ユーザー原文§3の新選定方針を指示化(Advancedでも理解しにくい一文を選ぶ、理解を妨げている構文、仕組み、通常語順/別表現との違い、意味・ニュアンス・表現効果、基礎文法は特殊用法/重要効果がない限り選ばない、判断基準=理解がどれだけ深まるか)。**『賢者の贈り物』の特定文や「倒置」をPromptに固定しない**(作品横断の汎用Promptで、『賢者』で倒置が選ばれるかを検証する)。
B. 生成(Luna、各1回、無編集保存、自動修正なし):
   - After(PROMPT_03): 『賢者』『X選定作品』『Z選定作品』各1call → `OUTPUT_03_{gift,<x>,<z>}_RAW.md`、`usage_03_*.json`。
   - Before(PROMPT_02、Trial-02同条件): X選定作品・Z選定作品 各1call → `OUTPUT_02B_{<x>,<z>}_RAW.md`(『賢者』のBeforeはOUTPUT_02_RAW.mdを再利用)。
   - 引用逐語一致の決定論照合(本文中の英文がAdv本文に逐語で存在するか)を全出力で実施し `INPUT_CHECK_03.md` に記録。
C. 評価 `EVAL_03.md`: ユーザー原文§6の受入条件ごとに、作品×Part 1(KPごと)/Part 2で判定と根拠。『賢者』Part 2が倒置構文を選び、§3の4点(なぜ通常と異なる語順か/通常語順/情報提示順序・焦点/文学的効果)を満たすか。Part 1は参考例との比較(hand downの後輩・次世代への技術/知識/経験、catch one's breathの忙しさから一息)。Part 3/4の副作用(Trial-02比)。Before/After比較表。残存問題。
   - Part 2が基礎文法を選んだ・§3の深さに届かない・Part 1が創作用法を含む等の場合は、原因(Prompt文言)を特定してPROMPT_03bへ改訂し再生成(上限内、改善見込みがある場合のみ、各改訂の差分とその理由を記録)。見込みが低ければ停止して報告。
D. 費用 `BUDGET_LOG_01.md` 追記(Trial実費と、Production採用時の量産費用[1記事セットあたり1call≈0.2円]を分けて)。
E. SSOT: OPEN-497 Status更新(Trial-03実施・Status候補)、`docs/pm/USER_DECISION_REGISTER_01.md` #185を判断済み(2026-10-25、原文path、「Part 1・2改善Trial承認、3作品Adv、Production未承認」)に更新、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行のみ(並行agent3本が同時編集中: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/FX-CORE-NUMERIC-RETENTION-TRIAL-01/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認(OPEN_ITEMS.mdはCRLF/LF混在に注意、USER_DECISION_REGISTERはCRLF化事故の前例あり)。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 505 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_05.md`。冒頭が「管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_05」と一致するか確認、不一致なら index 503〜508 を順に試す(`--index -1`不可)。
G. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。
H. 報告 `docs/pm/RESULT_PACKET_FZST5.md`: ①選定3作品と理由(X/Zの候補比較)、②PROMPT_03の変更点(Part 1/2)、③3作品×4 Partの出力全文(無編集、Before/After)の所在、④Part 1評価、⑤Part 2評価(選定の学習価値を主、『賢者』の倒置化と§3の4点)、⑥Trial-02比較・残存問題、⑦Part 3/4副作用、⑧実費・生成時間・量産費用、⑨Status候補(Sonnet所見、最終はFable評価)、⑩変更ファイル・commit、⑪`check_delegation_prompt.py`結果、⑫問題点。raw.githubusercontent.com URL(OUTPUT_03_*、PROMPT_03、EVAL_03)。

## 3. 禁止
Production code/Prompt/flag変更、Production KP選定仕様の変更、KP追加選定(既存3個のみ)、音声生成、Web検索、出力の編集・自動修正、Part 3/4 Promptの変更、Cap超過、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction配線へ進まない。