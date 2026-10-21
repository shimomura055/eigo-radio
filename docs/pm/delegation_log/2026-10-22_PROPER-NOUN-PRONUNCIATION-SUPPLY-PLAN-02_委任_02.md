FABLE-DELEGATION-MARKER: PNPS-PLAN-B2-委任_02-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_02 [B-2]: Fable独立レビュー所見の反映=計画v2。計画のみ・API 0・JPY0・Trial/Production/Ledger無変更)

## 0. 運用ルール・並列注意
他agent稼働中: (A-2)多語同音救済配線 `er006_*`/`er094_*`/PNMH docs/CURRENT_SPEC、(C-1)B3丸め設計 `er090_*`/`er095_*`/B3 docs。あなたは `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`・OPEN-441・UDR #133行・REPORT_LEDGERのみ。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。有料API・Web取得禁止(費用0の既存データ再集計のみ可)。

## 1. Fable独立レビュー所見(ユーザー11観点に基づく。`REVIEW_POINTS_01.md` §3の反映欄へ各IDを記入し、各文書へ反映。所見文は改変しない)
- **FR-01 [Major] 段階分割を計画の骨格にする**: Stage 1(PASS/NG判定を変えない改善)=否定記録/entity_type非依存のlookup統一/一般語の誤トリガー除外/Human Reviewパッケージの階層表示/Ledger登録validatorへの「出典引用の実在確認(V1')」追加。Stage 2(判定基準の変更=新仕様、ユーザー承認+Trial必須)=A階層音素列のL1 canonical側への供給/決定不要判定のPASS_WITH_WARNING受理/人間確認の語単位再利用(A1)/M1の階層連動。Stage 1は「不要な有料再調査・誤トリガーを止める改善」でPASS基準不変だが、Production Ledger/HR表示を変えるためユーザーへ軽い承認事項として提示する(承認済み原則内と明記)。各Stageの費用・効果・リスクを分けて書く。
- **FR-02 [Major] 出典の質をA階層条件に含める**: 「引用がページに実在する」だけでは不十分(個人ブログの誤記でも実在する)。A階層=公式ドメイン(本人・所属組織・権利者・公式イベント)または信頼できる辞書(allowlistで定義、拡張は人間)+引用実在確認。それ以外は引用が実在してもB階層(HR表示用)。CURRENT_SPEC:1837の判定優先順位(1)〜(4)と対応付ける。
- **FR-03 [Major] M1との整合をStage 2に含める**: M1はconfidenceで絞らずlow候補も使う(`er006_m1_multi_candidate_01.py:235`、OPEN-426 Mullos→Melosの既知リスクと同根)。階層導入時に「M1候補をB階層以上に限定」した場合の影響を、保存済みM1記録のオフラインreplay(0円)で測る項目をTrial O0に追加し、結果に応じてStage 2の判断材料にする(実装は提案のみ)。
- **FR-04 [Minor] トリガー時期の根拠を分離して試算**: 「最終slotまで不一致が残ったとき」に限定する根拠(OF-179凍結)はM1 anchor textの凍結の話であり、Ledger lookup/調査の早期化を妨げるものではないことを確認する(違えば根拠を示す)。辞書外/衝突語の初回NG時に調査を走らせた場合の「TTS再試行削減(1回あたりの実測TTS+ASR単価×削減回数)vs 調査費(PNEP実測5.4円/語)」を既存データで0円試算し、Trialに比較arm(最終slot vs 初回NG)を置くかの判断材料を出す。
- **FR-05 [Minor] 決定不要判定の受理条件を明文化**: 候補集合の定義(CMU同綴り全variant+綴り規則からの合理的読み[生成方法を明記]+Ledger B階層候補)、共通部分が空または1候補のみなら不発、受理は`PASS_WITH_WARNING`+事後試聴リスト登録+Ledgerに「公式発音未確認・共通読み受理」を記録、人間承認またはA階層登録で上書き。残留リスク(公式読みが共通読みと異なりTTSも共通読み)を1行で明記。これは新仕様(Stage 2)。
- **FR-06 [Minor] 否定記録の仕様**: key=正規化token(entity_type非依存)、TTL 60日は暫定、人間承認・A階層登録で即無効化、一時失敗(枠切れ・HTTP失敗・タイムアウト)は保存しない、否定記録中でもHRパッケージには「調査済み・未取得」と表示。
- **FR-07 [Minor] 外部URL取得の安全条件**: 読み取り専用・サイズ上限・タイムアウト・HTMLテキスト抽出のみ・スクリプト/ファイル実行なし・取得物は専用dirに保存し解析scriptと分離(環境ルール)・公式ドメイン優先。Trial O1で確認。
- **FR-08 [Info] #133への反映**: 本計画をユーザー判断#133の第4案(エ)「反応的・階層付きLedger(Stage 1先行、Stage 2はTrial後)」として併記し、Fable推奨を従来の(イ)見送りから(エ)へ更新する旨を`docs/pm/USER_DECISION_REGISTER_01.md`の#133行に追記(#133のStatusは未回答のまま、選択肢の追加のみ)。
- **FR-09 [Info] 未確認単価**: Perplexity sonar・`gpt-6-luna`+web_search・現行最終slot調査の単価はTrial GO前にRepo正式定義で確定し、確定できないものは「未確認」のまま見積に含めない(現状のPNEP実測ベース見積は可)。
- **FR-10 [Info] 用語・仕様位置づけ**: 「PASS根拠階層」はCURRENT_SPEC:1837(B)「Ledger情報は自動PASSの根拠にしない」の例外=新仕様であることを計画冒頭で明示。IPA→ARPAbet変換は「M1既存の決定論変換器で全記号が1:1対応する場合のみ、対応しない記号を含むIPAは階層外」と定義し、1837の「近似自動PASS禁止」との関係を1文で書く。
- **FR-11 [Info] 代替案の結論**: 縮小案(Stage 1のみ)はbyUs型とHR再発を解決しないが誤PASS・費用とも最小。Fable見解=Stage 1を先行し、Stage 2はTrialで取得率・誤登録0を確認してから。計画の推奨もこの順に揃える。

## 2. 作業
1. 上記FR-01〜11を`PLAN_01.md`/`DESIGN_OPTIONS_01.md`/`REVIEW_POINTS_01.md`§3/`PLAN_SUMMARY_01.md`へ反映(v2節として追記、v1本文は履歴として残す)。`PLAN_SUMMARY_01.md`冒頭をStage 1/Stage 2構成で書き直し、Status=`PLAN_V2_PENDING_USER`。
2. Trial計画をStage別に再構成: Stage 1検証(0円オフライン: 否定記録・lookup統一・誤トリガー除外の効果を保存HR queue/telemetryで再集計、FR-03のM1 replay、FR-04の試算)/Stage 2 Trial(有料、P1約10語、Cap案JPY150、FR-07の安全条件)。合格基準は既存のハード条件を維持。
3. ユーザー判断事項をStage別に整理: Stage 1の実施承認(軽)/Stage 2のTrial GO+Cap/J7/判断3(1837(B)例外)/判断4(決定不要判定)/判断5(A1)/#134(バックエンド)/#133(エ)。
4. SSOT: OPEN-441→`PLAN_V2_PENDING_USER`(履歴追記)。#133行に(エ)追記(FR-08)。REPORT_LEDGER行追加。DECISION_LOG/CURRENT_SPECは書かない。
5. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_02.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-PLAN-B2-委任_02-20261022` を含むAgent tool_useの0始まり通番、246前後)。`check_delegation_prompt.py`(見出し不一致FAILは既知の偽陽性)。
6. commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS2.md`へ報告: FR-01〜11の反映結果(各1行)/FR-04試算結果/Stage別の費用・効果・判断事項/ユーザー§5 B部分8項目の最終要約/RESULT_PACKET 4行/JPY0/raw URL(PLAN_SUMMARY_01.md, PLAN_01.md)。

## 3. 禁止
Trial実行・Production/Ledger/Validator/Prompt変更・有料API/Web取得、#133/#134/J7のStatus変更(選択肢追記のみ可)、AI推測で発音を確定する設計、Fable所見の改変。