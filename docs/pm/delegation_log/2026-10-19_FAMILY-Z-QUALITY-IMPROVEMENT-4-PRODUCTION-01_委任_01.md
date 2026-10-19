# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_01(ユーザー2026-10-19指示原文保存+改善項目①「Key Phrase日本語訳の恒久改善」の原因調査・既存経路マップ・共通仕様の設計案・Regression案・費用見積。**Phase 1=read-only調査+文書、JPY0、Production変更なし**。実装はOpus条件Aレビュー後の委任_03以降)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 調査・設計文書(Phase 1)。コード変更0、有料API呼出0。
- 到達上限Status: `ITEM1_ROOT_CAUSE_AND_DESIGN_READY_PENDING_OPUS_A`。
- 禁止: Production・Prompt・Styleの変更/有料実行/特定表現(`in someone's place`)だけを置換するhardcode案の採用/未承認の新品質基準・新生成方式の「採用」(候補として列挙しUSER_DECISION_REQUIRED候補に区分するのは可)/`er082_*`への接触。
- 固定ブロック: **E-1**(既存仕様・過去Trial照合: CURRENT_SPEC「共通仕様のFamily別配線Status表」、KP関連(K2/P8-KP/M2P0+A/SRC/Strategy L/canonicalization/gloss HR/Source Consistency Gate)、OPEN_ITEMSのKP日本語意味・gloss関連項目、過去TrialのKP JA訳品質に関する記録を必ずGrepし、A(既存仕様あり)/B(過去Trialあり未採用)/C(真に新規)に分類)/**D-1**(本Phaseは不適用。実装時の方式はOpus後に決定)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agent(委任_02=②③④調査)あり: SSOTは自分の変更行のみstaged blob、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASK.mdは編集直前に再読し自分のブロックのみ先頭追記)/**F-1**(JPY0。見積は既存実測単価(run_e2e_03 `cost_log.jsonl`、`audit/cost_by_stage_17.json`)を出典に)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_01.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI1.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md`へ原文のまま保存し、文字数とsha256を報告)
---
# Claude Code／Fableへの指示
## Family Z 品質改善4項目・Production反映

### 1. 目的と基本方針

「走れメロス」のユーザー試聴で明らかになった課題を改善し、Family Zの正式Production仕様へ反映する。

**今回の4項目はユーザー正式決定済み。Status＝APPROVED_FOR_PRODUCTION。**

品質（Q）＞Delivery（D）＞量産単価（C）≫開発費用の優先順位と、改訂済み行動大原則8項目を遵守する。

既存仕様・過去Trial・Production実経路を確認し、必要な変更だけを実施する。独立作業は並列化し、問題は承認範囲内で自律解決する。不要な再生成・追加Trial・日付分割・少額費用の都度承認は行わない。

### 2. 改善項目

#### ① Key Phrase日本語訳の恒久改善

**目的は「in someone's place」の個別修正ではなく、同種の誤訳を量産時に発生させないことである。**

今回、`in someone's place` に対し「あなたの代わりに」という日本語訳が生成された。英語表現に存在しない二人称を補った不適切な訳である。

対応内容：

- 既存のKey Phrase選定、canonicalization、日本語意味生成、検査・retryの経路を調査し、誤訳を生んだ原因と既存対策の不足を特定する。
- 英語Key Phraseと日本語意味の間で、人称・所有格・指示対象・意味関係が不当に変わらないよう、**記事や特定表現に依存しない共通仕様**として改善する。
- `someone's` → `your` のような指示対象の変更だけでなく、文脈による「立場／代わり」などの意味選択も適切に扱う。
- 機械的な逐語訳を強制せず、自然な日本語と原文の意味の両方を守る。
- Family X／Z／将来のYで共通化すべき仕様かを判断し、既存の承認済み共通仕様と整合させる。
- 改善したProduction経路を使用して、今回のメロスの該当Key Phraseを再処理し、正しい日本語意味に修正されることを確認する。
- 同種の誤訳を使ったRegressionを実施する。特定表現だけを置換するhardcodeは不可。

**受入条件：仕様自体が改善され、その正式経路からメロスの正しい日本語訳が生成されること。手動修正のみでは未達。**

なお、新たな品質基準・生成方式を承認済み範囲を超えて導入する必要が生じる場合は、候補を検証した上でUSER_DECISION_REQUIREDとして報告し、未承認のままProductionに採用しない。

#### ② Standard Preview／Comment生成方式の変更

**Advancedで採用しているPreview／Comment生成方式を、日本語版としてStandardに適用する。**

目的は、事前に物語の展開を説明することではなく、リスナーが何に注目して聴けばよいかを示し、続きへの興味を引き出すこと。

対応内容：

- Advancedの正式Production Prompt・生成経路を確認する。
- その構成・役割・情報開示方針をStandardの日本語生成へ適用する。
- 本文中の出来事・障害・結末を不必要に先取りしない。
- Standardとして理解に必要な平易さは維持するが、旧方式の詳細なあらすじ説明を無条件に残さない。
- PreviewとComment1〜3の重複や情報の先取りを確認する。
- 新仕様をFamily Zの正式生成経路、retry／regenerationへ反映する。

既存Advanced方式の日本語適用がユーザー承認範囲であり、別の独自方式への変更は含まれない。

#### ③ Standard Dialogue音声速度の改善

**Standardの登場人物のセリフは、Advancedと同じDialogue Styleで生成し、生成後に6％減速する。**

現行Standardの「生成時の減速指示＋生成後6％減速」は廃止する。

対応内容：

- `A2_ENGLISH_STYLE_PREFIX_SLOWER` 等、Dialogueに追加されている生成時減速指示を取り除く。
- Advancedと同一のDialogue Styleを使用する。既存の登場人物別Voice割当は維持する。
- Standardの生成後6％減速、既存ASR／音声QA／retry／fallbackは維持する。
- narratorのPD06や、Standard本文ナレーションの6％減速仕様は変更しない。
- 問題が顕著だった王のセリフを含め、変更後の速度・自然さと6％減速の実施を検証する。

対象例：

`Your friend must stay here. Return late, and he will die in your place.`

セリフの速度改善のために、ユーザー未承認の数値WPM基準や追加品質Gateを新設しない。

#### ④ Family Z本文語数の変更

**Family Zの本文語数目標を350語から400語へ変更する。**

- Standard／Advanced共通
- **目標400語、目安範囲330〜470語（400±70）**
- 従来の「センター値±70語」をそのまま踏襲
- ハードキャップではない
- 範囲外はWARNのみ
- 語数だけを理由とした自動再生成・STOPは行わない
- 不自然な加筆・削除による語数合わせは禁止

Writer Prompt、定数、Guardrail、文書、必要なテストを整合させる。

今回のメロスは既存本文がStandard約408語／Advanced約387語で新しい目安範囲内にあるため、**語数変更のみを理由とした本文再生成は不要**。

### 3. 実施順序と効率化

①②④の仕様調査・修正・テストは、依存関係と競合を考慮して可能な限り並列化する。

③の音声修正は、必要な本文・話者割当が確定していれば先行可能。

既存の承認済み成果物・音声は再利用し、変更が必要なPreview／Comment、該当Key Phrase日本語意味、Standard Dialogueのみを必要に応じて再生成する。

ただし、最終Assemblyは変更後の正式仕様と原稿の整合が取れた状態で行う。

開発費は原則1,000円／日（JST）と既存個別Capの双方を管理する。承認済み範囲内の少額Trial・修正のたびにユーザー承認を求めない。個別Cap超過、新規Trial範囲、重大な仕様変更は承認境界を遵守する。

### 4. Production反映とGate

各変更について以下を確認する。

- 正式初回Production経路に反映済み
- retry／fallback／regeneration／resumeへの反映
- DEV／Trial専用の変更ではない
- 正式runtimeで変更が発火した証拠
- 必須Validator／Regression／integration test PASS
- 実際のPrompt、Style、Voice、model_id、routingの記録
- Family X／Z共通仕様との整合、および各Familyの配線確認
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- Git commit／push完了
- 承認された仕様と実動作が一致

各項目は個別にStatus管理し、条件を満たしたものだけをPRODUCTION_WIREDとする。

特に①について、改善仕様の実装範囲がFamily Zのみにとどまる場合は、Family Xの未配線を見落とさずOPEN_ITEMSに記録する。

### 5. 完成物・ユーザー試聴

「走れメロス」のStandard／Advancedについて、変更箇所を反映した完成音声と既存標準フォーマットの試聴ページを更新する。

- 全編再生
- 再生順の全スクリプト
- Preview／Comment／Dialogue
- Key Phrasesと日本語意味
- 既存のユーザー向け表示仕様

変更対象外のAdvanced音声・既存本文などは可能な限り再利用する。

**最終的な音声の自然さ・Previewの良し悪しはユーザー試聴で判断する。** Production技術検証PASSとユーザー試聴PASSを混同しない。

### 6. Fable独立受入・最終報告

FableはClaudeの完了宣言をそのまま受け入れず、4項目について独立して承認内容・実装・runtime evidence・テスト・QCD・SSOTを照合する。

最終報告は次の順序で簡潔にまとめる。

1. 4項目それぞれのStatusと完了／未完了
2. ①誤訳の根本原因、変更した共通仕様、再発防止テスト、メロスへの適用結果
3. ②Preview／Commentの修正前後
4. ③DialogueのStyle・速度・実測結果
5. ④400±70語への仕様変更・実装確認
6. 実費・量産単価への影響・所要時間
7. Git／SSOT／runtime evidence
8. Standard／Advanced試聴ページURLと残るユーザー判断

既存の明示STOP、安全STOP、予算上限、未承認Production仕様の採用禁止を遵守する。

**目標は4件を個別に直すことではなく、承認された品質が以後のFamily Z量産でも再現される正式Production仕様にすることである。**
---

## Fable指示(①の調査・設計の要件)
1. **経路マップ**: Family Zの正式KP経路(er026 runner `stage_kp`→Strategy L選定→canonicalization→日本語意味生成→検査/HR/retry→`install_kp_assets`→TTS P8-KP)と、Family Xの正式KP経路(M2P0+A/K2/P8-KP、gloss生成・gloss HR・Source Consistency Gate)で、「日本語意味」を生成するPrompt・関数・モデル・検査を関数名:行で列挙。X/Zで共通moduleか別実装かを明示。
2. **根本原因**: run_e2e_03の`in someone's place`(a2 rank2、SRC: S8 unique_containment、quote_boundary_truncated=true)について、実際のPrompt入力(与えた文脈=引用符跨ぎで切れた1文か、原文"he will die in your place"か)、出力「あなたの代わりに」、通過した検査(何を検査し何を検査していないか)をaudit/KP成果物から再現し、原因を特定(仮説例: 文脈文が"your place"を含み、Promptが「文脈に合う意味」を優先させ辞書形`someone's`との指示対象整合を要求していない/検査が人称・所有格の不整合を見ていない)。推測と実証を分ける。
3. **既存対策の不足**: 既存のKP日本語意味の検査・HR・retry条件を列挙し、人称・所有格・指示対象・意味関係の整合を検査する仕組みの有無を明記。
4. **共通仕様の設計案(2案以上、hardcode不可)**: 例=(案I)日本語意味生成Promptに「辞書形の不定代名詞(someone/something/one's)は日本語でも不定のまま保持し、文脈文の具体的人称へ置換しない。文脈は意味選択(立場/代わり等)にのみ使う」という汎用制約を追加+出力に`meaning_general`(辞書形)と`usage_in_text`(文中での意味)を分離させる構造化/(案II)生成後の決定論的整合check(英語KPの不定代名詞・所有格パターンと日本語訳の人称語(あなた/彼/私 等)の出現を突合し、不整合ならretry・HR)/(案III)I+II。各案について: 変更箇所(X/Z共通module化の可否)、既存承認仕様との整合(gloss HR・Source Consistency Gate・P8-KP Styleに影響しないか)、retry/regeneration/resumeへの反映点、副作用(自然さの低下、過剰HR)、費用影響(token増)、Regression設計(同種誤訳fixture: someone's→your、one's→私の、something→それ 等、記事非依存。特定表現置換でないこと)。「承認済み範囲内の改善」か「新品質基準/新生成方式(USER_DECISION_REQUIRED候補)」かを案ごとに区分。
5. **メロス適用計画**: 改善後の正式経路で該当KP(a2 rank2)を再処理する手順(`--regenerate-stage kp_a2`相当で既存KP選定を維持しつつ日本語意味のみ再生成できるか、全KP再生成が必要か、SRC Gate・kp_expl署名・P8-KP TTS再生成への波及)と費用見積(出典: run_e2e_03実測)。
6. **Opusレビュー観点案(条件A)**: ①の設計で確認すべき論点を5件以内。
7. 文書: `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/ITEM1_KP_JA_MEANING_DESIGN_01.md`(§1経路マップ/§2根本原因/§3既存対策の不足/§4設計案/§5メロス適用計画/§6 Opus観点/§7 E-1分類)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\a2\key_phrases\`配下(KP成果物・audit、日本語意味とPrompt入出力の記録があるファイル)と`audit\src_z_posthoc_01.json`
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` `stage_kp`〜`install_kp_assets`(L1100-1300付近)と日本語意味生成の呼出先
- Family X側: Grep `KP_JA_MEANING|kp_ja|japanese_meaning|gloss` を `er019_family_x_*.py`・`er030_*.py`で実施し該当関数
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\FZ_COMPLETION_PLAN_01.md` §1(f)・§5(c)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\SRC_Z_POSTHOC_DRYRUN_01.md`

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `P8-KP|KP日本語|日本語意味|gloss HR|Source Consistency|canonicaliz`→該当行番号を§7 E-1分類に記録(編集しない)。
- `OPEN_ITEMS.md`: Grep `gloss|日本語意味|KP.*訳`→関連Open Itemを§7に列挙。本委任では新規起票: `OPEN-419 FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01(4項目の親、Status=PHASE1_INVESTIGATION)`(番号は末尾最大+1、並行agentと衝突しないようcommit直前に再Grep。既に委任_02が起票していればそれを使う)。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ユーザー指示受領(4項目APPROVED_FOR_PRODUCTION)、Phase 1調査開始」。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 本指示を判断済み(次番号)で登録(委任_02と重複登録しないよう直前Grep)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_01.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\stop_scope_check_fzqi1.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-419(新規): 「ユーザー2026-10-19指示(4項目=APPROVED_FOR_PRODUCTION、原文sha)。①KP JA訳共通仕様/②Std Preview・Comment=Adv方式の日本語適用/③Std Dialogue=Adv Style+後処理6%減速/④本文400±70語。Phase 1調査中。各項目は個別Status管理、PRODUCTION_WIREDは条件充足分のみ」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 2件(+_check.json)、ITEM1_KP_JA_MEANING_DESIGN_01.md、OPEN_ITEMS.md、DECISION_LOG.md、USER_DECISION_REGISTER_01.md、REPORT_LEDGER.md。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_01: ユーザー2026-10-19指示(4項目APPROVED_FOR_PRODUCTION)原文保存+①KP日本語訳の経路マップ・根本原因・既存対策不足・共通仕様設計案(hardcode不可)・Regression案・メロス適用計画(Phase 1、JPY0、Opus条件A前)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI1.md`)
4行: (1)整合(E-1分類A/B/C、既存仕様行)(2)Production到達経路=変更なし(3)成果物とcommit sha、根本原因の結論(実証/推測の別)、設計案の比較要約(案ごとに承認範囲内/USER_DECISION候補の区分)、X/Z共通化の判断、メロス適用の手順と見積(4)撤去/残置候補。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/コード不変/hardcode案なし)。
