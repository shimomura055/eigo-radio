FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_11-STD-V1-REPAIR-B2-AND-STD-FULL-AUDIO-20261023

# FAMILY-Y-VOICES-DESIGN-01 委任_11: Standard V1(人物1)の修復案B2(Std英文V1をD'のflag位置に合わせて意味不変で言い換え→Std V1のみ再生成、最大2テイク)→正式Gate→Std通し音声組立→試聴ページ更新→page_verify。DEV/Trial経路のみ、X/Z Production変更0。費用上限6円(Y累計上限600円・残約272円の内、当日1,400円)。

## 0. 先に読むもの
`docs/pm/ACTIVE_TASK.md`(line 2、Family Y行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_FYT7.md`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/{TRIAL_03_RESULT_02,AUDIO_QA_04,V1_REWRITE_DIFF_01,PLAY_VERIFY_04,BUDGET_PLAN_02}.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_10.md`(制約継承)、Std V1の最終テイクのQA結果(D' flag位置 6.58秒付近/31.5秒付近、3テイク目のAzure TRUE_CONTENT_MISMATCH箇所)。

## 1. Fable判断
- Adv V1は言い換えで1テイク確定(D' 0.47秒)。Std V1は同じ言い換えでも別位置でD'境界flag(0.67/0.64秒)→短文連続の構成に起因する可能性。**B2(Std専用の言い換え)を1回だけ承認**(最大2テイク)。これはAdvで有効だった手段のStd向け適用であり、惰性反復ではない。2テイクで確定しなければ停止し、案A(人間試聴承認)をユーザー判断候補としてFableへ返す。
- 委任_10の委任文が要約保存になっている。`Glob **/extract_delegation*` でtoolを探し、見つかれば 委任_10 と本委任_11 を逐語で保存し直す(先頭MARKER一致確認)。見つからなければ本委任文を手で**全文**逐語保存(要約不可)し、委任_10は要約保存であった旨をOPEN-463に1行記録。

## 2. 作業
### T-0 記録・予算(API 0)
ACTIVE_TASK Family Y行(自分の行のみ): 委任_11 Status=`STD_V1_REPAIR_B2_IN_PROGRESS`、上限6円、報告=`docs/pm/RESULT_PACKET_FYT8.md`。見積(Std V1 2テイク+ASR+Gate+組立)を`BUDGET_PLAN_03.md`へ。
### T-1 Std V1英文の言い換え(API 0)
- D'がflagした2位置(6.58秒付近=冒頭2〜3文、31.5秒付近)の前後で、約1〜2秒間隔の短い語句反復(同じ文頭・同じ前置詞句の連続、"I ... I ..." 等)を崩す: 文の結合(2短文→1文、Std水準は維持 目安10〜12語/文)、文頭の変化、同義語への置換。3テイク目でAzureが不一致とした語句も確認し、ASRが拾いにくい語(固有の連語)があれば平易な同義表現へ。意味・感情・人物差・Std/Adv難易度差を変えない。差分と「意味不変」の確認文を`V1_REWRITE_DIFF_02.md`に記録。日本語稿・Adv英文は変更しない。
### T-2 再生成→Gate→組立(TTS直列化: 他行の「有料run(TTS)進行中」待機、最大30分。自行にflag記載/終了更新)
- Std V1のみ再生成(最大2テイク、minimal_fallbackに落とさない)。正式Gate(Repetition QA/ASR主副/Y style gate)を迂回しない。
- 確定→Std全編通し音声を組立(他segment再利用)→試聴ページ更新(Std全編追加、「人間確認待ち」表示解除)→page_verify(Playwright実再生、全編・パート別、console error 0)→`PLAY_VERIFY_05.md`。
- 2テイクとも未確定なら停止。最終テイクのpath・D'値・flag位置・ASR結果を`AUDIO_QA_05.md`に記録し、案Aの材料(ユーザーが聴くべきwav/ページ上の該当パートURL)を明示。
### T-3 資料・SSOT・Git
- `TRIAL_03_RESULT_03.md`: 受入条件1〜9の最終自己チェック(証跡path)、Std/Adv難易度指標、残存リスク、自己判定(VALIDATED候補/USER_DECISION_REQUIRED候補)。
- OPEN-463/469追記、DECISION_LOG(Fable承認B2)。CURRENT_SPEC変更なし。
- Git: secret scan(0件確認)→`git diff --cached --name-status`(他agentのstaged変更を巻き込まない)→`git commit --only -- <path…>`→`git push origin HEAD:main`。wav/raw_usage_log追跡禁止。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_FYT8.md`: (1)B2結果(言い換え内容・テイク数・D'値・Gate結果) (2)試聴URL(Std/Adv全編・パート別) (3)受入条件1〜9 (4)QCD(本委任費用・Y累計・当日累計、出典) (5)Status・判断候補。使用model名。

## 3. 禁止・制約
X/Z Production変更0、既存er110 module無変更。R1/R2追加なし。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。Gate/HR Lock/STOP迂回禁止。テイク上限2(3テイク目禁止)。`TTS_EXECUTION_MODE=STANDARD`。秘密情報出力禁止。上限6円無断超過禁止。
## 4. handback
完了/HR Lock残存/予算警告/blocker のいずれかで。