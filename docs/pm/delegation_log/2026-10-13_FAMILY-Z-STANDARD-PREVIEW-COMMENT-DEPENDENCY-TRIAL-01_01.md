## 管理ID

FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01 委任_01(初回。ユーザーTrial承認済み、総予算¥100)。前身: FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01(`er070_*`、統一Prompt)、FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01(`er072_*`、A条件の既存3 take=`er072_output/melos_preview_std_adv_3take_01/std_take1〜3.txt`)。並行タスク: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03(`er030_*`/`er019_*`/Coffee run dir/SSOT編集中)、FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01(`er073_*`)。本委任はSSOT編集権あり、ただし`OPEN_ITEMS.md`のOPEN-338行・`DECISION_LOG.md`末尾・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/REPORT_LEDGER.md`に限定(`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`は編集しない)。SSOT編集は最終工程、直前に`git status --porcelain`で他agentの未commit変更を確認(あれば60秒×5回待ち、残っていても自分の変更行のみ追記・自分の変更ファイルのみ明示add)。一時ファイル: `docs/pm/ACTIVE_TASK_FZPC.md`/`docs/pm/RESULT_PACKET_FZPC.md`。出力: `er074_output/family_z_std_preview_comment_dependency_01/`、script `er074_family_z_std_preview_comment_dependency_01.py`(+`_test_01.py`)。`.git/index.lock`待ち30秒×3、fetch→ff-only(不可なら`git pull --no-rebase`、conflict時は両追記保持)。全commitに`Managed-ID: FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01` trailer。

## 性質/到達上限Status/禁止事項

- 性質: Trial(原因切り分け: Comment参照量・重複回避条件がStd Previewの抽象化を招いているか)。
- 到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。Production採用・実装禁止、結果報告時点でSTOP。
- 費用: 上限¥100(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。(見込み: B〜E 12 call×約¥0.12≒¥1.5、他作品展開を含めても¥5未満)。**予算が余っていても無益な追加探索をしない**。各takeは独立生成、lint NGでも再生成しない。
- 禁止: Production Prompt・code・Validator・Gateの変更、Writerへの新制約追加、E条件のための新Preview構成指針の追加、入力条件以外の仕様変更、Family Zの記事再生成・音声化・Comment/KP再生成、TTS、A条件の新規生成(既存3 take再利用)、retry/fallbackへの未承認Preview仕様追加、CURRENT_SPECへの未承認仕様記載、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`、秘密値出力、wav/telemetry/logのadd、ACTIVE_TASK/RESULT_PACKETのcommit、Melos run_e2e_02配下・Master Store・HR・attempt_history・telemetryへの書込、外部プロセス再起動、監督ループ/timeoutラッパ。
- STOP条件(ユーザー指示): 入力条件以外に未承認の仕様変更が必要/既存の比較可能性を保てない/¥100超のおそれ/品質改善が見られず追加探索が無益/承認範囲超のUSER_DECISION_REQUIRED/`STOP_NOTICE`/`STOP`/`STOP_ALL`。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 非該当(入力条件の比較Trial。Family X共通仕様の変更提案が出た場合はユーザー判断事項として報告、Production採用提案時に条件C)。
- 時間見込み: 60〜90分。並列化: 他agentと並列。生成は直列(rate limit)。
- 最新モデル原則: Production同一`gpt-6-luna`・effort high(例外理由=Production Preview生成との比較可能性)。応答model_id実測を記録。

(以下、ユーザー指示原文・事前指定Read一覧・作業内容・実行コマンド・Git・報告項目は委任文本文のとおり。本ファイルには管理ID〜最新モデル原則までと、下記ユーザー指示原文を保存。)

## ユーザー指示(原文)

(2026-10-13、管理ID FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01。全文)
「## 1. 目的 Family Z Standard Previewが抽象的・評論調になる原因を特定し、物語への興味を引くPreviewの改善案を検証する。直前の3 Take比較では、Family X準拠のStandard Promptから具体的な導入が得られず、一方でAdvancedは具体的な発端から自然に導入できていた。原因候補として、Preview生成時に参照するComment 1・2との重複回避条件が、具体的な描写を妨げている可能性がある。今回の主眼は、Commentを参照する必要性そのものも検証すること。
## 2. ユーザー決定・重要原則 Comment 1: Previewの直後に流れるため、内容・説明が繰り返される冗長性を重く評価する。Comment 2: 多少の内容重複は許容する。Comment 2との重複を避けるためにPreviewを抽象化させない。本文全体: すべての条件で参照し、具体的な発端・葛藤を選べる状態を維持する。ネタバレ・あらすじ化禁止: 維持する。Writerへの新しい制約: 追加しない。Family X準拠の既存Promptは、比較基準として維持する。変更案が必要な場合もTrial専用とし、Productionへ無断反映しない。
## 3. 比較Trial 対象はまず既存のメロスStandard原稿とComment 1・2。以下を比較する。A: 基準=現行Prompt+Comment 1・2全文(既存3 Takeを再利用)/B=現行Prompt+Comment 1のみ(Comment 2を除いた効果)/C=現行Prompt+短縮したComment 1・2(Comment情報量の効果)/D=Comment 1との重複を厳格に避け、Comment 2は軽微な重複を許容(重複回避ルールの優先順位変更の効果)/E: Comment非参照=Comment 1・2を生成AIに一切渡さない(Previewの自由度と実際の重複率を確認)。
### E条件の必須事項 Comment 1・2の文章だけでなく、その要約・言い換え・内容を伝えるメタ情報もPreview生成AIへ渡さないこと。物語本文全体など、Previewに本来必要な入力は維持。Commentの内容は、生成後の評価段階でのみ参照する。E条件のために新たなPreview構成指針を付け加えない。Comment用プレースホルダーや参照指示が残り、実質的にCommentの存在を意識させることがないよう、Trial専用の最小限の入力調整を行う。この調整内容と、現行Promptとの差分を必ず報告する。E条件では、Commentとの重複を避けるよう生成AIに指示するのではなく、結果としてどれほど重複するかを観察する。
## 4. 実施順・試行回数 A: 既存3 Takeを使用し、新規生成しない。B・C・D・E: 各3 Take、合計12回を基本とする。各Takeは独立生成し、NGが出ても勝手に再生成しない。まずメロスで比較する。原因と改善の方向が確認できた場合のみ、有望な条件を既存の別の物語でも検証する。総予算上限: 100円。予算が余っていても、無益な追加探索を行わないこと。追加Trialが必要になっても、今回承認した「Comment参照量・重複回避条件の切り分け」の範囲を超えないこと。
## 5. 評価方法 生成したすべてのPreview全文を提示し、以下を比較する。1.具体的な出来事から入っているか 2.興味を引くか 3.抽象的・評論調になっていないか 4.ネタバレ・あらすじ化がないか 5.Comment 1との重複度・冗長性 6.Comment 2との重複度・冗長性 7.日本語の自然さ 8.Take間の安定性 9.他の物語にも再利用できるか。
### 重複の評価基準 単純な同一単語・同一テーマの出現を、機械的にNGとしない。特に、以下を区別する。許容: 人物・舞台・テーマなどの自然な共通情報/注意: 同じ事実や説明が繰り返される/問題: Previewで説明した内容が直後のComment 1でほぼ繰り返され、聴取体験が冗長になる。Comment 1とComment 2は別々に評価すること。Comment 2の軽微な重複だけを理由に、Previewを低評価にしない。重複の有無だけでなく、PreviewからComment 1、さらにComment 2へ続けて読んだときの情報の進み方も評価する。評価者は生成後に既存Comment全文を見て判定する。特にE条件では、評価用Comment情報が生成入力に混入していないことを確認する。
## 6. 原因分析と対策案 Trial結果から、次を切り分ける。Comment 2の重複回避が過剰だったのか/Comment 1の情報量が過剰だったのか/Comment 1・2を見せない方が自然なPreviewになるのか/Comment参照とは無関係に、Family X準拠Prompt自体が抽象的な出力を誘導しているのか。各仮説について、支持する結果・反証する結果・残る不確実性を整理すること。有効な案があれば、最小の変更で実現できる対策を提案する。Family Xの共通Preview仕様変更が必要な場合は、別途ユーザー判断事項とする。
## 7. Production・PM Gate 今回のStatusはTrial承認済み。到達できるのは`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`まで。Production Prompt・code・Validator・Gateは変更しない。Family Zの記事再生成・音声化STOPを維持。Previewの正式採用はユーザーが別途判断する。Trial成功をProduction承認とみなさない。retry/fallback等に未承認のPreview仕様を追加しない。新しい原則をProductionから参照させない(Dangling Reference Check)。CURRENT_SPECには未承認仕様を正式仕様として記載しない。必要なDECISION_LOG・OPEN_ITEMS・USER_DECISION_REGISTER・Trial成果物を更新し、Git反映結果を報告する。
## 8. STOP条件 入力条件以外に未承認の仕様変更が必要/既存の比較可能性を保てない/予算100円を超えるおそれがある/品質改善が見られず、追加探索が無益と判断できる/USER_DECISION_REQUIREDが発生し、今回承認範囲を超える判断が必要。STOP条件に達した場合、独自に追加TrialやProduction実装へ進まず報告する。
## 9. 最終報告 1.A〜E各条件のPreview全文(全Take) 2.Comment 1・2との重複比較(特にE条件) 3.具体性・面白さ・自然さ・ネタバレの比較 4.抽象化の原因分析と根拠 5.推奨する改善案と必要な変更範囲 6.他作品での再現性(実施した場合) 7.使用モデル、実行回数、費用、テスト結果 8.Production未変更の確認 9.Trial終了Status 10.ユーザー判断事項および未解決Open Item。結果報告時点でSTOPすること。Production採用・実装は行わない。」
