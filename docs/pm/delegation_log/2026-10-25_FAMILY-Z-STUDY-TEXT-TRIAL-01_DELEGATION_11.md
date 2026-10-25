FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11(Trial-06: Part 2選定の工程設計見直し=決定論規則化、Opus条件Bレビュー反映)。あなたはsonnet-worker。Fable(PM)からの委任。

## 0. 前提・位置づけ
- 管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01(OPEN-497)。Trial-05(委任_10、EVAL_05/COMPARISON_05/DESIGN_05/PREREGISTERED_CRITERIA_05/analysis_05.json/analysis_05b.json)で「拾い漏れは解消したが層A/B閾値が呼出ごとに揺れる」が未達。同じ問題へ2回修正済みのため3回目前にOpus条件B必須レビューを実施済み(下記§1に逐語)。Fable判断: Opus推奨どおり3回目(Trial-06)を実施。**本Trialで不合格なら4回目は行わず撤退案提示へ進む(終了条件)**。
- 性質: DEV/Trial専用。Production file変更0(`er003_*`/`er026_*`/`er062_*`等のProduction module・Prompt・閾値を編集しない)。
- 費用: **本委任の上限14円**(Step A'' 18 call×最大見込み0.8円=予約14.4円のうち実費見込み約10円、Step B約1.2円)。案件累計上限はFable権限で**20円→35円へ引き上げ**(300円以下のFable自律範囲、BUDGET_LOG_01.mdへ「Fable引き上げ、2026-10-25、理由=Opus条件B推奨の3回目実施」と記録)。日次1,000円(JST)の範囲内。有料生成の起動は上限内でのみ。前回(Trial-05)の上限超過(8円に対し9.11円)の原因=費用ガードが呼出開始時点累計で判定していたこと。**今回は必ず「1 callあたり最大見込み額を先に予約してから各波を起動する」方式へ改修し、selftestで確認してから有料実行**。
- モデル: Trial-04/05と同じ Luna(`gpt-6-luna`)。最新世代原則(PM_GOVERNANCE 25節)に沿い、報告に使用モデル名/最新か/理由を記載。
- 有料runは`.venv\Scripts\python.exe`、無料処理は`py`(`python`はstub)。Windows/PowerShell。

## 1. Opus条件Bレビュー結果(逐語。`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/OPUS_REVIEW_04.md`としてこの内容を逐語保存すること。先頭に「# OPUS_REVIEW_04(条件B: Part 2選定 3回目設計の是非、2026-10-25、opus-consultant、read-only・API 0)」の見出しを付ける)

---
## 判定
**3回目の実施を推奨する。** ただし層A/B判定を捨てて「工程設計の見直し」として行い、これで駄目なら4回目はやらない(撤退してユーザー判断へ回す)という終了条件を事前登録に書くこと。根拠は次のとおり。
- 揺れの原因は「LLMに相対的な難しさを判定させること」そのものにあり、Promptを直しても収束しない見込みが高い。
- 一方で、分類コード(何の構文か)と本文中の場所は、標本が変わってもほぼ安定していた。この安定な情報だけを使えば、構造上、揺れを避けられる。
- 費用は約10〜12円、量産単価は約0.8円/セットで、撤退した場合と比べて費用面の不利はほぼない。

## (a) 真因
生データを照合した。0件になった標本(開いた窓r5・イグr6・猿の手r2)では、その1回の呼出の中で**全ての文が層Bと判定されていた**。たとえば開いた窓r5ではP21がINV(倒置)なのに層Bになっている。つまり揺れは「文ごとの判定ミス」ではなく、**呼出ごとに層Aの基準そのものがずれる**現象である。

層Bの定義は「取り違えても大意は文脈からつかめる」だった。これは「読者がどう誤読するか」という観察できない仮定に基づく基準で、短い物語ではほぼどの文にも当てはまってしまう。そのため推論量やschemaを直しても収束は見込めない。2値化(難所/非難所)しても、同じ呼出単位のずれが「0件」として再発するだけである。

逆に、分類コードは標本間で安定していた(P21=INV、P29=HEAVY、イグP4/P8=CLEFT、P5=CMP、猿の手P24=INV)。

補足:
- `basic_only=true`は18標本で一度も付かなかった。基礎文を除外していたのは実際には「列挙するかどうか」の段階であり、basic_only欄は機能していない。
- what-if規則の選定順は分類優先順で決まる。イグでP5(CMP)がP8より後になるのも、同じCLEFT同士が段落順で前に並ぶためである。

## (b) what-if規則の妥当性
方向は妥当であり、ユーザー要件とも整合する。「どの構文を教えるべきか」という価値判断を、LLMの確率的な判定から、設計で固定した決定論的な規則へ移すからである。

ただし今の形のままでは、埋め草化(平易な本文でも常に2件選んでしまうこと)の対策が無い。標本では、会話の断片(開いた窓P3「Almost nothing」= ELL)や伝達部の同格(said Vera, her niece = APPOS)も層Bで列挙されている。これらは優先順位が低いので今回は選ばれなかったが、平易な本文ではそのまま選定されてしまう。次の規則を必須とする。
1. **分類を2段に分ける。** 強クラス(INV、CLEFT、CMP)と中クラス(FRONT、HEAVY、POSTMOD、SPEC、ELL、APPOS)とし、OTHERは自動選定の対象外(記録のみ)にする。
2. **中クラスは追加条件を満たす場合だけ選ぶ。** 新設する欄`misread_target`(列挙型: SUBJECT/VERB/MODIFIEE/OMITTED)が埋まっていること、かつ`misread_quote`が本文中に逐語で含まれること(コードで判定。現データでは適格文で100%成立)。
3. **同じクラスの2件目は選ばない。** イグの場合は{P4, P8}ではなく{P4, P5}になる。どちらも中核なので、学習価値はむしろ上がる。
4. **該当する文が無ければ0件にする。** 0件を既定にはしない。
5. **rankとtierの欄を廃止する。** 不安定な欄を無くし、相対比較に使われる推論トークンも減らすため。basic_only欄は残す。
6. 優先順位(INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS)は、事前登録で固定する。

## (c) 価値側分類(肯定側)の最終案
- **SPEC**: 使役動詞・知覚動詞+目的語+原形/分詞、keep/make/find+目的語+補語の基本形は、基礎(否定側)へ移す。SPECに残すのは、目的語と補語の境界が見えにくいものだけ(形式目的語it、目的語が長いもの、wish+目的語+形容詞など)。
- **ELL**: 会話の断片・間投詞・一語の返答は基礎へ移す。ELLは「前の文から動詞や比較の基準を補わないと構造が取れない省略」に限る。
- **APPOS**: 伝達部(said X)に付く同格は基礎へ移す。
- **INV**: 伝達部の倒置は既に除外済みで、このままでよい。
- 作品をまたいで安全に使えるのは強クラス3つである。中クラスは、上の追加条件で埋め草を防ぐ。

## (d) 代替案の評価
- **(B)n=3集計**(1.82円/セット): 呼出ごとの基準ずれを吸収しきれない(イグ18/20、猿の手0/1)。非推奨。
- **層の2値化**: (a)のとおり同じ現象が再発する。非推奨。
- **推論量を下げる**: 揺れの原因ではない。費用削減の効果も約0.3円/セットと小さく、今回の比較条件と交絡するので、次のTrialでは扱わない(後で別途検討する)。

## (e) QCD比較と推奨
- **3回目**: 下記の計画で約10〜12円。量産単価は約0.8円/セット(70円の1.2%)。見込みは中〜高。
- **撤退案**: Part 2を03d一括に戻す(既知の選定の揺れ・開発者語の問題が残る)か、0件許容で運用する(見落としの要件に違反する)。どちらも品質の欠陥をユーザーへ持ち込むことになる。
- 費用差はわずかで、品質は3回目の方が優れるため、**3回目を推奨する。**

## 推奨する検証計画
- **作品(計6、各N=3、Step A''は18 call)**
  - 既存の4作品。猿の手はもう学習に使ってしまったので、ホールドアウトから外して開発用作品として扱う。P18を許容集合に追加する。
  - 新しいホールドアウト1作品(難所のある本文)。
  - **平易な本文の作品1つ(必須)**。埋め草化と0件経路を検証するため。許容集合は空か少数にする。
  - 許容集合は生成前に登録する。
- **規則**: 主規則を上記(b)1〜6で固定する。比較用の規則(元のwhat-if規則、同一クラス制約なし版など)は、同じ出力にオフラインで当てて記録するだけにする(追加費用0。合否には使わない)。分析時に `subject_span`/`main_verb`(逐語)を記録欄として追加してもよい。
- **合格条件**
  - 難所のある作品: 全標本で、選定文が許容集合内・0件標本なし・基礎だけの選定0。
  - 平易な作品: 許容集合の外を選ばない(0件も可)。
  - Step BはTrial-04の基準どおり(各作品r1、約6 call)。
- **費用**: Step A''は約0.55円×18で約10円、Step Bは約1.2円、計約11〜12円。案件累計は約31円になり、Fableが設定した案件上限20円を超えるので、Fableによる明示的な上限引き上げが必要(300円以下なので自律範囲内)。
- **終了条件**: 不合格なら4回目はせず、`USER_DECISION_REQUIRED`(撤退案の提示)へ進む。

## 必須の修正(実装)
1. **費用ガード**: 呼出の開始時点の累計で判定するのをやめ、1 callあたりの最大見込み額(例0.8円)を先に予約してから並列の各波を起動する方式にする。前回の上限超過はこれが原因。
2. `resolve_verbatim`: 文頭・文末の引用符を除去してから照合する。
3. 上記(b)と(c)のPrompt・規則変更と、そのselftest。
4. Promptに載せる例は全作品の本文以外から作り、そのことをassertで確認する(作品への過剰適合を防ぐため。前回どおり)。

## リスクと対処
- what-if規則は同じデータを見てから作った事後規則であり、新しい標本での確認が必須(計画に含めた)。
- 中クラスの追加条件が厳しすぎると、イグP2/P3のような「どちらでも可」の文は選ばれにくくなる。中核文が選ばれていれば合格なので、許容範囲である。
- 分類コード自体が揺れる文がある(猿の手P18はELL/POSTMOD/SPECに分かれた)。段落単位の重複排除と、優先順位を固定することで吸収できる。
- 分類の優先順位には「どの文法を教える価値があるか」という価値判断が含まれる。後述のとおり、VALIDATEDの報告時にユーザーへ開示する。

## (f) ユーザー判断の切り分け
- **今は無い。** 設計の選択と300円以下の費用は、Fableの裁量内である。
- **VALIDATEDの報告時**: 固定した分類の優先順位と「平易な本文では0件になる」という挙動を、ユーザーへ開示して確認を受ける。品質の定義に関わる確認であり、ブロッカーではない。
- **3回目が不合格のとき**: 撤退案(03d一括 / 0件許容 / Part 2保留)をQCD付きで`USER_DECISION_REQUIRED`として提示する。
- **Production採用**: 従来どおり、人間ユーザーだけが判断する。
---

## 2. 作業内容(順序厳守: 有料生成前に事前登録をcommit)

### Step 0 読み込み(必要箇所のみ)
- `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{DESIGN_05.md,PREREGISTERED_CRITERIA_05.md,EVAL_05.md,COMPARISON_05.md,run_trial_05.py,analyze_05.py,analyze_05b.py,PREREGISTERED_CRITERIA_04.md,run_trial_04.py,BUDGET_LOG_01.md}`
- `docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_04.md`(Trial-04ユーザー原文=Part 2要件の正本: Advancedでも難しい一文を選び、4点[なぜ語順が違うか/通常語順/焦点/文学的効果]等)と`..._USER_03.md`(Trial-03原文)。
- `OPEN_ITEMS.md`はOPEN-497行のみGrep(全文読込禁止)。

### Step 1 設計・事前登録(有料前、API 0)
- `DESIGN_06.md`: Opus(b)1〜6・(c)・必須修正1〜4を反映した工程設計(Step A''=全文タグ付け[分類コード・misread_target・misread_quote・basic_only・subject_span/main_verb記録欄、rank/tier廃止]→決定論規則で選定→Step B執筆)。比較用規則(元what-if・同一クラス制約なし版)はオフライン適用のみ。Step BはTrial-04基準(選定文につき4点解説、学習者向け表記、開発者語禁止、`resolve_verbatim`改修)。
- `PREREGISTERED_CRITERIA_06.md`: (i)優先順位 INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS を固定 (ii)強/中クラス定義と中クラス追加条件 (iii)6作品の許容集合(段落番号・英文逐語)を**Step A''実行前に登録**、猿の手はP18を追加・開発用へ変更 (iv)合格条件(難所作品: 全標本で選定が許容集合内・0件標本なし・基礎のみ選定0/平易作品: 許容集合外を選ばない、0件可) (v)終了条件(不合格なら4回目なし→撤退案提示) (vi)費用上限(本委任14円・案件累計35円) (vii)Step Bの基準(Trial-04と同じ)。
- 作品選定(Fable委任): 既存4(『賢者の贈り物』『開いた窓』イグ・ノーベル『猿の手』)+新ホールドアウト1(難所のある本文)+平易な本文1。候補は既存の公開済み/生成済みAdvanced本文(Family Z作品またはFamily X記事)から選び、選定理由を1行ずつDESIGN_06に記す。**新規記事の生成はしない**(既存本文の再利用のみ)。許容集合は本文を読んで登録し、Step A''出力を見てから変更しない(変更が必要になったら「事後変更」と明記し、合否判定には事前登録版を使う)。
- 実装: `run_trial_06.py`(費用ガード予約方式+selftest、Prompt例が全6作品本文に含まれないことのassert)、`analyze_06.py`(主規則+比較規則、引用符除去版`resolve_verbatim`)。selftest(無料、`py`)PASSを確認。
- ここまでをcommit(有料前固定)。commit message例: `FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11: Trial-06事前登録(決定論選定規則・6作品許容集合・終了条件)+DESIGN_06+費用ガード予約方式 (有料生成前、API 0・Production変更0)`。

### Step 2 Step A''実行(有料、6作品×N=3=18 call)
- 予約方式ガードで上限内に収める。実費はraw usage logから確定し`BUDGET_LOG_01.md`に記録。
- `OUTPUT_06_<work>_r<n>_STEPA_DEV.json`を保存。`analyze_06.py`で主規則・比較規則を適用し`analysis_06.json`。

### Step 3 合否判定→Step B
- 事前登録どおり判定(`EVAL_06.md`)。**合格の場合のみ**Step B(各作品r1、約6 call、Trial-04基準)を実行し`OUTPUT_06_<work>_r1_USER.md`(学習者向け・Part 2全文)と`_DEV.md`(開発者向け)を保存。
- 不合格の場合はStep Bを実行せず、撤退案(03d一括/0件許容/Part 2保留)をQCD付きで整理してFableへ報告(4回目の設計はしない)。

### Step 4 記録・SSOT(最小Edit)
- `COMPARISON_06.md`: Before=03d(Trial-03)/04のPart 2、After=06のPart 2。作品別に「選定文(英文逐語)・許容集合内か・3標本の一致・Step B全文(無編集)」。学習者向けと開発者向けを分ける。
- `ADOPTION_NOTE_04.md`を更新(または`ADOPTION_NOTE_06.md`新設): 現状Status候補(Part 1=VALIDATED候補のまま、Part 2=本Trial結果)、量産単価(セットあたり円)、開示事項(分類優先順位の価値判断・平易本文で0件になる挙動)。
- `BUDGET_LOG_01.md`: 上限引き上げ記録・本委任実費・案件累計。
- `OPEN_ITEMS.md` OPEN-497行に追記(編集直前に再Read、scratchpadへバックアップ、最小Edit、CRLF/LF混在に注意、編集後`git diff --stat`で対象行のみ変わっていることを確認)。`DECISION_LOG.md`に1件(Trial-06実施とFable上限引き上げ)。並行agentが同じSSOTを編集中のことがあるため、衝突時は再Readして再適用。
- `docs/pm/RESULT_PACKET_FZST11.md`に詳細。`docs/pm/ACTIVE_TASK.md`に自行を追加(gitignore)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 523 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_11.md`(`--index -1`不可。保存内容の冒頭が「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11」で始まることを確認し、不一致なら±5の範囲でindexを試す)。`check_delegation_prompt.py --file`はFAIL想定(非blocking、結果のみ記録)。

### Step 5 Git
- `git status`→対象pathのみ`git add`(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only -- <path…>`(他agentの差分が混在する場合は一時index方式)→`git push origin HEAD:main`(作業ブランチ`work/post-merge-01`)。secret grep 0件確認。raw_usage_log/wav/STOP/lock/telemetryは追跡しない。amend/rebase/force push/stash/reset --hard/checkout -f禁止。
- commitは最低2回(有料前の事前登録固定、結果反映)。

## 3. 禁止・注意
- Production module/Prompt/閾値の編集禁止。新Checker/Validator新設不採用(ユーザー方針)。Prompt例に6作品本文の文を使わない。
- 事前登録後に許容集合・優先順位・合格条件を変えない(変えた場合は事後変更と明記、合否は事前登録版)。
- 上限14円を超える起動をしない。予約額が上限に達したら残りの波を起動せず報告。
- ユーザー承認を先取りしない(Status候補は`VALIDATED`候補まで。`APPROVED_FOR_PRODUCTION`は人間のみ)。
- 自PID以外のprocess終了不可。

## 4. 報告(Fableへ)
(1)設計要点とOpus反映の対応表(b1〜6・c・必須修正1〜4) (2)6作品と選定理由、事前登録許容集合 (3)Step A''結果: 作品別×3標本の選定(段落番号・英文逐語・分類コード)、許容集合内/外、0件標本数、基礎のみ選定数、比較規則との差 (4)合否(事前登録基準)と、合格ならStep B全文(6作品・無編集・学習者向け) (5)費用: call数・実費(raw log確定)・本委任上限14円との対比・案件累計/35円・量産単価見込み・モデル名/最新か (6)開示事項(優先順位の価値判断・平易本文0件挙動)と、不合格時の撤退案(QCD付き) (7)変更ファイル・commit hash・raw.githubusercontent.com URL(変更した追跡ファイル) (8)RESULT_PACKET 4行: 既存仕様整合/Production到達経路に入る未承認機能/失敗終了時の成果物/撤去・残置、および「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」の1行。