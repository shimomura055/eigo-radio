# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_05(①Melos/Mellows: ユーザー2026-10-20新指示の原文保存[T-0]+「なぜ既存の承認済み音韻同等性判定で救済されなかったか」のA/B/C具体解明+11-8不具合判定テスト+範囲内不具合があれば修正・Regression・正式経路検証)。2026-10-20。
並行タスク衝突確認: 同時に委任_06(②③配線保証の証拠整理+再生成計画、JPY0、書込先=`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md`・`REGEN_PLAN_01.md`・`docs/pm/RESULT_PACKET_FZAQ6.md`)が走る。本委任はそれらのファイルと`er020_tts_retry_local_rewrite_01.py`/`er003_v1_n3_01_tts_generate.py`/`er003_v1_crosslevel_audio_02_common.py`/`er026_output/`を**編集しない**(読取は可)。SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)の編集権は**無し**(追記文案はRESULT_PACKETへ)。`docs/pm/ACTIVE_TASK.md`は先頭へ自委任ヘッダを追記するのみ(他ヘッダを消さない)。commit前に`git status --porcelain`で`.git/index.lock`不在を確認し、自分が変更したファイルのみ明示`git add`する。

## 性質/到達上限Status/禁止事項
- 性質: 調査(原因解明・仕様照合)+範囲内不具合があれば修正・Regression・正式経路offline検証。Production変更は「承認済み仕様・設計原則との矛盾の是正」に限る。
- 到達上限Status: `ITEM1_ROOT_CAUSE_EXPLAINED_PENDING_FABLE`(不具合0件の場合)/`ITEM1_DEFECT_FIXED_TESTED_PENDING_FABLE`(範囲内修正を実施した場合)/判断候補あり(仕様変更が必要と判明した場合、ラベルはFableが付ける)。PRODUCTION_WIREDの判定はFable。
- 禁止: (1)**A案・A'案(P1=M1 `_post_check`の受理拡張、Ledger限定版を含む)およびP2(G-1/G-2)はユーザーがREJECTED**(2026-10-20)。名称・形を変えて実装・既定動作化しない。(2)Melos/Mellows専用の個別例外(辞書追加・hardcode・閾値緩和)禁止。(3)承認済み仕様で許容されている判定(例: `Melo drank`のbenign単複PASS)を独断で厳格化しない。(4)新規TTS生成禁止。(5)HR Lock・`er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/review_lock_state.json`(sha256 `6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19`)の変更禁止(Lock解除は委任_06/_07で別途)。(6)`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。(7)有料runの再起動禁止(PM_GOVERNANCE 26節)。
- 修正範囲の線引き(PM_GOVERNANCE 11-8): 範囲外=受理面・閾値・方式の新設/拡大(P1/P2/個別例外はここ)。範囲内=承認済み仕様文・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。**範囲内の不具合を見つけた場合は、自律的に修正→Regression→正式経路offline検証まで進める。ただし修正が共通ASR判定cascade(`er006_secondary_asr_01.py`/`er006_m1_multi_candidate_01.py`/`er006_preprod_hardening_01_validation.py`/`er011_*validator*`/`er021_*`/`er078_*`)の判定意味を変える場合は、実装前に設計(変更箇所:行・前後の挙動・Regression案・影響Family)を文書化してRESULT_PACKETで報告する(Opus独立レビュー条件A/C該当のためFableがOpusへ回す)。判定意味を変えない配線・データ・記録の不具合は即修正してよい。**
- Opus独立技術レビューGate(11-3): 本委任自体は非該当(調査+範囲内修正)。上記の判定意味変更を伴う修正案が出た場合は条件A/C該当としてFableが起動する。
- 費用/日次: 当日(JST 2026-10-20)既使用JPY=未集計(本委任で`daily_dev_cost_01.py`により集計しRESULT_PACKETへ記載)/本委任見積JPY0〜10(根拠: 新規TTS 0・LLM 0。ASR再転写は既存wavの同条件再転写が**追加で必要な場合のみ**、Azure STT USD1.0/audio hour+OpenAI gpt-4o-mini-transcribe、最大10呼出程度)/改善見込み中/承認区分C(承認済みscope内・300円以下・日次1,000円以内)。
- T-3: 上限¥10(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 時間見込み: 全体2.5〜4h(T-0 10分/仕様文収集・照合60〜90分/過去Trial比較30分/11-8テスト表30分/[修正がある場合]修正+Regression 60分/文書・報告30分)。並列化: 委任_06(②③配線保証・再生成計画)と並列。直列化理由: 本委任内の修正実施は仕様照合結果に依存。
- 前委任(委任_01/_03)のQDC・受入記録(11-6): 目的=①の原因究明と修正設計/試行=全棄却箇所R1〜R12を関数:行で追跡、音素比較・ASR再転写・音響簡易指標/原因仮説と証拠=「仕様どおり棄却」+Melo/Mello非対称(OPEN-330)+OOV語の音素取得不能(R8)+S↔Z有声性差の未定義(R9)/結果=不具合0件・P1/P2は仕様変更候補としてUDR #120へ/改善見込み=ユーザーがA/A'をREJECTEDし「既存仕様の不具合原因との関係や採用する必要性が説明できていない」「なぜ現行の承認済みルールで救済できなかったかを具体的に説明すること」と差戻し/費用=約JPY7(委任_01)+JPY0(委任_03)/次の一手=本委任(仕様文の逐語照合を軸に、A/B/Cを「どの承認済み文が何を許容し、何を許容していないか」の水準で説明し、11-8不具合テストを各棄却点に適用)。受入判定=前回成果物は証拠付きだが、ユーザー要求(具体的説明・仕様内不具合の有無の判定根拠)に未達=ACCEPTED不可→再委任。判定整合行: 重大NG=説明の粒度不足と不具合/空白/仕様どおりの区別根拠の弱さ/主因=仕様文の逐語照合を提示せず結論先行/是正対象=本委任で仕様文逐語+判定表/STOP理由=なし/提示=Fable→ユーザー。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。(定型文は上記「性質」欄に記載済み)

## ユーザー指示(原文)
**T-0の最優先作業**: 次の原文を**一字一句そのまま**(要約・省略はFAIL)`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`へ保存し、文字数とsha256(`Get-FileHash -Algorithm SHA256`)をRESULT_PACKETへ記録する。原文は`# Family Z Melos音声品質問題 — 根本原因解決・Production配線保証・Closeout`で始まり`未充足のGate・未確認のruntime evidence・未処理のUSER_DECISION_REQUIREDを隠さず、必要十分な品質でCloseoutすること。`で終わる。先頭に次のメタ3行だけを付け、本文は改変しない: `<!-- 受領日: 2026-10-20 / 受領者: Fable(sandwich-pm) / 保存: 委任_05 -->`。

---(原文ここから)---
# Family Z Melos音声品質問題 — 根本原因解決・Production配線保証・Closeout

## 1. ユーザー決定・目的

今回の目的は、**本来OKになるべき音声がHuman Reviewに回された原因を特定し、承認済み仕様が正しく機能する状態を実現すること**である。

ユーザーの正式判断：

1. 発音判定の改善候補 **A案・A'案はいずれもREJECTED**。現時点で、既存仕様の不具合原因との関係や採用する必要性が説明できていないため、採用しない。
2. 両案が根本原因の解決に必要と判明した場合に限り、原因・既存仕様との関係・他の解決策との比較・QCD影響を明確にしたうえで、新たなユーザー判断事項として提案できる。却下案を名称変更して無断採用しない。
3. Rewrite発動条件の修正、およびRewrite後の原稿照合修正は、**正式Productionで確実に有効になっていることを確認する。**
4. 録音2のHuman Review Lock解除は承認済み。
5. ①の問題解決後、Family Zの該当記事についてAdvancedを含む全TTSを再生成する。Advancedの「He drank」は元の「Melos」を含む原稿に戻す。
6. 大原則不遵守への既存対策は維持し、追加制度を設けず実運用で有効性を確認する。

優先順位：品質（Q）＞納期・速度（D）＞量産単価（C）≫開発費用。

## 2. ① Melos / Mellows — 根本原因の解明と是正

### 問題

録音2：

- 原稿：`Melos drank`
- Primary：`Mello drank` → NG
- Secondary：`Mellows drank` → NG
- ユーザー試聴：自然に「Melos drank」と聞こえる

既存の承認済み仕様では、単なる綴りの違いによって音韻的に同等な発音を不合格にしない。

しかし今回、Secondaryの`Mellows drank`がNGとなった。

**最も重要な未解決事項は、なぜ既存の音韻同等性判定でこの認識結果が救済されなかったかである。**

### 必須調査

以下を、既存仕様・過去Trial・今回のruntime evidence・実際の判定条件に基づき解明すること。

**A. `Melos → Melo`**

- 既存の単数・複数形等の表記揺れ補正によってPASSしていることの正確な根拠。
- 音連結による許容とは明確に区別する。
- 今回のPASSが既存の承認済み仕様の適用範囲内なのか確認する。
- 承認済み仕様で許容される判定を、独断で厳格化しない。

**B. `Melos → Mello`**

- MeloとMelloの発音・音韻上の関係を確認する。
- 語末s/zの差と綴りの違いが重なった場合、どの既存判定条件が発動し、どこで棄却されるのかを特定する。
- 単数・複数形の補正、音韻同等性判定、M1/F1等の関係を整理する。

**C. `Melos → Mellows`【最重要】**

- MelosとMellowsの実際の発音が音韻的に同等か確認する。
- 同等なら、承認済みの一般化された音韻同等性判定で、なぜPASSしなかったのかを特定する。
- 異なるなら、音声・ASRの語彙推定・PhraseList・辞書等を切り分ける。
- 過去のMelos関連M1/F1 TrialのPASS結果と今回のNG結果を比較し、条件の違い、配線・判定順序、既存仕様の空白を明確にする。
- **既に検証・承認した仕組みが、Productionで意図どおり動いていたかを確認する。**

### 是正方針

既存の承認済み仕様内の不具合なら、原因究明→修正→Regression→正式経路の検証まで自律的に完了すること。

Melos/Mellows専用の個別例外追加を解決策としない。

新しい許容条件・品質基準変更が必要と判明した場合のみ、原因と必要性を示してユーザー判断を求める。

A案・A'案は現時点でREJECTEDであり、暗黙に採用・実装しない。

**単に「既存仕様の空白」「ユーザー判断待ち」と整理して終了せず、なぜ現行の承認済みルールで救済できなかったかを具体的に説明すること。**

## 3. ② Rewrite発動条件 — Production配線保証

ユーザー正式承認済み：

**「両ASRが同じ箇所の誤読に合意すること」という条件を削除する。**

基本フロー：

TTS初回生成 → 承認済みPrimary/Secondary検証 → NGなら最大2回のTTS再生成 → なおNGなら既存のRewrite条件・Gateに従ってRewrite。

今回の原因分析で、旧条件は実装されておらず、閾値未定義のまま仕様書上だけで配線済みと扱われたことが判明した。

今回の修正について、同じ問題を絶対に繰り返さないこと。

具体的には以下を確認する。

- 正式初回Production経路で新仕様が有効である。
- DEV／Trial専用経路や、起動時の手動フラグONに依存しない。
- retry／fallback／regeneration／resumeでも整合する。
- 旧条件がコード・Prompt・Validator・後続経路から参照されていない。
- 実行時の有効設定・判定経路・モデルrouting等の証拠を確認する。
- 必須Regression／integration testがPASSする。
- CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Gitが実装内容と一致する。

**コード変更済み・テストPASSというだけでPRODUCTION_WIREDにしない。**

既存の証拠で十分に確認できる部分については、不要な有料再検証を繰り返さないこと。

## 4. ③ Rewrite後の原稿照合 — Production配線保証

正式に許可されたRewrite後は、**書換え後の実送信文を、後続の音声検査の正解原稿とする。**

例：

- 元原稿：`Melos drank`
- Rewrite後：`He drank`
- TTS実送信：`He drank`
- 減速後の照合先：`He drank`

今回、旧原稿を照合先としていた不具合は修正済みとの報告だが、正式Productionで確実に有効になっていることを再確認する。

対象：

- 正式初回経路からのRewrite後TTS
- 減速後再検証
- retry／fallback
- regeneration／resume
- 再利用・継承
- Family X／Zの対象共通経路

既存のSTOP・HR Lock・監査記録・品質Gateを変更しない。

今回の報告では、offline正式経路による実音声検証はPASSしているが、live Rewrite自然発火は未観測。

**必要なruntime evidenceの充足状況を整理し、追加の確認が必要なら最小限の検証で取得すること。**

自然発生の誤発音やRewriteを待つために、不必要な有料TTSを繰り返さない。

正式経路の発火証拠が不足する場合は、未確認事項を明示し、証拠なしにPRODUCTION_WIREDと判定しない。

## 5. 音声再生成・Human Review

録音2のHuman Review Lock解除はユーザー承認済み。

まず①の問題を解決し、承認済み発音判定が正しく機能していることを確認する。

その後、Family Zの該当Melos記事について、**Standard／Advancedの全TTSを正式Production経路で再生成する。**

- Advancedの「He drank」は、元の「Melos」を含む原稿へ戻す。
- 原稿の意味・構成・その他の承認済み品質仕様は維持する。
- 必須の音声QA・再試行・Rewrite・減速後再検証・Assembly Gateを通す。
- 完成音声と試聴ページを更新する。
- 実際に発動した判定経路・警告・Human Review対象を記録する。

ユーザー承認済みの録音2を、新たな判断待ちとして再提示しないこと。

ただし、再生成した新音声は既存の品質Gateに従って独立に検証する。

①の解決に新たな仕様承認が必要となった場合は、その境界でSTOPし、未承認仕様のまま再生成を強行しない。

## 6. 大原則・PM Gate・再発防止

今回導入した大原則不遵守への対策は維持する。

新たな重複Gate・毎回の全文確認・過剰な制度追加は行わない。

既存の8原則に基づき、

- 正当なSTOP理由がない限り、自律的に原因究明から修正・検証まで完了する。
- 不具合修正と新仕様採用を区別する。
- STOP時は承認済みSTOP条件との対応を明示する。
- 一部工程の成功ではなく、Project全体のProduction完成状態を基準に判断する。
- 独立作業は並列化し、Deliveryを最小化する。
- 不要なTrial・重複API・再実行を避ける。

FableはClaudeの「完了」報告をそのまま採用せず、実装・正式経路・runtime evidence・SSOT・Gitを独立照合すること。

Cross-Family共通仕様は、Family X／Z双方で配線・整合を確認する。Family A／B／Cの開発停止方針は維持し、無断で対象を広げない。

## 7. 最終報告・完了条件

報告順序は次のとおり。

1. **①の根本原因**：特にMellowsがNGになった具体的な条件と、過去TrialでPASSした条件との違い。
2. **①の是正結果**：既存仕様内で何を修正し、どう検証したか。仕様変更が必要な場合は、その必要性・選択肢・推奨。
3. **②③のProduction配線証拠**：正式初回経路・後続経路・runtime evidence・有効設定・テスト結果。
4. **Standard／Advancedの音声再生成結果**：全SectionのQA、Assembly、試聴ページ。
5. **大原則に基づく自律対応の結果**：不必要なSTOP・未報告の判断待ちがなかったか。
6. **QCD・SSOT・Git**：実費、量産単価への影響、commit/push、残課題。
7. **ユーザー判断事項**：承認済み仕様内では解決できない場合のみ提示。

**最終的な目標は、今回のMelos音声を完成させることだけではない。**

承認済みの発音判定・Rewrite条件・原稿照合が、今後の正式Productionでも確実に機能し、同種の不必要なHuman ReviewやProduction配線漏れを再発させない状態を実現することである。

Trial成功・コード修正・テストPASS・正式Production配線・完成音声のユーザー試聴評価を混同しない。

未充足のGate・未確認のruntime evidence・未処理のUSER_DECISION_REQUIREDを隠さず、必要十分な品質でCloseoutすること。
---(原文ここまで)---

## 本委任の作業(①のみ。②③④は委任_06/_07)
Fableからの前提共有(鵜呑みにせず照合せよ): 委任_01の分析(`ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md` §0〜§5)では「録音2の棄却点R1〜R12は全て仕様どおり、不具合0件、R8/R9は仕様の空白」と結論し、P1/P2を仕様変更候補とした。ユーザーはA/A'(P1系)をREJECTEDし、「なぜ現行の承認済みルールで救済できなかったか」の具体説明と、仕様内不具合の有無の再判定を求めている。重要: 録音2でP1が効くのはPrimary(`Mello`)側であり、Secondary(`Mellows`)はP1では救済されない(P2のみ)。この点をユーザー向けに明確にする必要がある。

成果物: `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`(新規)。構成:
- §1 **承認済み「音韻同等性」仕様文の逐語一覧**(各行番号付き・原文引用): CURRENT_SPEC L2136付近(classify/benign単複/`HIGH_SIMILARITY_SAFE`)、L2144(Tier3)、L2150(F1 Pattern A/B/C・残差0)、L2151(Equivalence Layer・voicing除外)、L1829-1831(Case A/homophone・OOVはHR)、L2794-2801(M1・OF-178)、L2814(Primary#2廃止)、設計原則文書`docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md` §1・§2-1〜2-7(**Status=DESIGN_PRINCIPLE_AGREED、Production仕様ではない**ことを明記)。さらにユーザーの前提文「既存の承認済み仕様では、単なる綴りの違いによって音韻的に同等な発音を不合格にしない」に**最も近い承認済み文**を特定し、その文が(i)Production仕様か設計原則か、(ii)「音韻的に同等」の定義(音素列同一か/連結発音で説明可か/綴り水準か)、(iii)固有名詞・OOV語への適用条件、を逐語で示す。
- §2 **A/B/Cの具体解明**(ユーザー原文の問いにそれぞれ1対1で答える):
  - A `Melos→Melo`: PASSの正確な根拠を関数:行+仕様文で示す(`_is_benign_plural_pair` L690-696/`_singularize_simple`、`HIGH_SIMILARITY_SAFE` 0.98、一致率計算)。「音連結(Pattern A)による許容」とは別経路であることを、`drank`が歯擦音でない事実とPattern A条件文で示す。benign単複の承認文(DECISION_LOG/CURRENT_SPECでの導入決定、対象=一般語の単複か固有名詞も含むか)を逐語で引き、今回のPASSが承認範囲内か/範囲の明文化が無いか、を判定する。厳格化はしない。
  - B `Melos→Mello`: CMU音素列(`M EH L OW`=Melo/Mello/Mellow同一)を示し、Primary `Mello drank`が通る判定順序(classify→Tier3→Case A→M1)で各段の棄却条件式を実測値で示す(委任_01 R1〜R5を再掲・再検証)。「単複補正はなぜ`Mello`に効かないか」(`_singularize_simple('melos')=='melo'≠'mello'`=綴り一致のみ)を明示。M1 `_post_check`がOF-178で「F1で説明できる置換のみ」を要求し`drank`文脈で不成立になることを、OF-178の採用文(`docs/pm/OPUS_FINDINGS_LEDGER.md:205`付近)の逐語とともに示す。
  - C `Melos→Mellows`【最重要】: (c-1)音韻同等性: Ledger候補4件(`ec716e185835dba3`)と`Mellows`の導出音素`M EH L OW Z`を比較し、差=語末S/Zの有声性のみ、かつ**承認済み定義のどれにも該当しない**(exact不一致/脱落ではない/付加ではない/Eq Layerはvoicing変化を明示除外)ことを仕様文逐語で示す。(c-2)判定順序: Secondaryに対する各段(classify→Case A→M1→Eq Layer不呼出)の棄却条件式(R6〜R10)を再掲し、特に**M1で`Mellows`がCMU未収録のため音素比較に入れない(R8)**点について、M1承認時の設計文(C3=G2P非採用、UDR #52、OF-184)の逐語を引き、「承認時に意図的に対象外とした領域」か「見落とし」かを判定する。(c-3)切り分け: 委任_01 §4の再転写・音響簡易指標の結果を再掲し、音声に/s/があること・Azureがtake決定的に`Mellows`を返しPhraseListが無効だったことを根拠に「ASR語彙推定側」と結論(追加APIは、既存結果で不足する場合のみ)。(c-4)**過去Melos Trial PASSとの比較表**: 過去のM1/F1 Trial(er068 `er068_output/asr_phonetic_equivalence_generalization_01/OFFLINE_EVAL_01.md`、M1導入時のfixture/Trial、run_e2e_01〜03のpart3_c1結果、run_03 PASS版=Primary`Mellow drank`+Azure`Melos drank`→Tier3 PASS)について、各PASSの「次語の音(歯擦音か)」「Azureが正綴りを返したか」「発動した受理経路」を列挙し、今回NGとの違い(次語`drank`=/d/、Azureが`Mellows`、OpenAIが`Mello`)を1表にする。(c-5)「検証・承認した仕組みがProductionで意図どおり動いていたか」: 各機構の有効設定(`m1_enabled`既定、Tier3 role、Eq Layer入口、PhraseList注入)を実行時証拠(E21 telemetry行9613-9614、`attempt_history`行15172-15176、`m1_offline_replay_part3c1_10_result.json`)で確認し、「設計どおり動いた/動かなかった」を機構ごとに判定する。
- §3 **11-8不具合判定テスト表**: 棄却点R1〜R12それぞれに「承認済み仕様文(行)」「実装挙動(関数:行)」「矛盾の有無」「判定=不具合(範囲内修正)/仕様どおり/承認時に意図的に対象外/仕様の空白」「是正に受理面・閾値・方式の新設/拡大を伴うか」の5列。Melo PASS/Mello NGの非対称(OPEN-330)は「設計原則(DESIGN_PRINCIPLE_AGREED、Production未採用)とは矛盾するがProduction仕様文(OF-178・benign単複)とは矛盾しない」等、**どの文書水準で矛盾するか**を明記する。
- §4 **是正**: §3で「不具合(範囲内)」が1件でもあれば、修正(上記「修正範囲の線引き」の手順に従う)+Regression test(記事非依存fixture)+正式経路offline検証(新規TTS 0、`m1_offline_replay_part3c1_10`と同方式で録音1/2/3のProduction記録転写を再判定)を実施し、結果を記録する。0件なら「0件」とその根拠(§3の表)を記す。
- §5 **ユーザー判断候補(該当時のみ)**: 「新しい許容条件・品質基準変更が必要」と判明した場合に限り、原因・既存仕様との関係・他の解決策との比較(却下済みA/A'/P2・B・C・OPEN-318 C-a[Ledger人間確定]・R1原稿ルール等を含む)・QCD影響を表にする。A/A'を別名で推奨しない。該当しなければ「該当なし」。
- §6 **①の結論(ユーザー向け1段落)**: 「なぜ救済されなかったか」を、仕様文の引用付きで3〜6文に凝縮(Fableがそのまま報告に使う)。録音2の救済経路がPrimary側(Mello)かSecondary側(Mellows)かも明示。

## 事前指定Read一覧
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md`:1-125(前回分析。再掲元)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/OPUS_REVIEW_G_01_VERBATIM.md`: Grep `Melo drank|benign|HIGH_SIMILARITY|Hayes|M1-a|M6-a`→該当範囲Read(Opus_Gの前提訂正とM1-a〜c条件)
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/HR_LOCK_PART3C1_ROOT_CAUSE_01.md`: Grep `^## `→§3(再転写)と§6(NG率)の範囲Read
- `docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`:1-70、および`^## 4`以降の「将来同じ問題が起きたときの判断手順」節
- `CURRENT_SPEC.md`: 2136, 2144, 2150-2151, 1829-1831, 2794-2801, 2814, 2818 の各行(全文Read禁止)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-178|OF-181|OF-184`→該当行Read
- `er006_preprod_hardening_01_validation.py`:640-700, 1140-1160, 1195-1215(benign単複・一致率・classify)
- `er006_m1_multi_candidate_01.py`:200-260, 290-310, 350-430(C2候補・forms_from・_enumerate_subs・_post_check)
- `er011_b1_connected_speech_validator_01.py`:30-100, 150-170, 235-260(Pattern A条件)
- `er011_connected_speech_equivalence_layer_production_01.py`:40-70, 160-190(voicing除外)
- `er021_en_asr_semantic_equivalence_production_01.py`:710-750(Tier3 token一致)
- `er006_secondary_asr_01.py`:500-530, 680-700, 880-950(判定順序)
- `er068_output/asr_phonetic_equivalence_generalization_01/OFFLINE_EVAL_01.md`: Grep `Melos|PASS|said|drank`→該当範囲Read(過去Trial条件)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/m1_post_check_whatif_01_result.json`と`phoneme_compare_melos_01_result.json`: 先頭200行(既存結果の再利用。再実行不要)
- `docs/pm/RESULT_PACKET_FZAQ1.md`:1-60(前委任の費用・手順)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `benign_plural|_is_benign_plural_pair|単複|複数形` in `CURRENT_SPEC.md`・`DECISION_LOG.md`・`DECISION_LOG_HISTORY.md`(`-n`、全文Read禁止)→benign単複の導入決定文(対象語種・承認日)を特定し§1・§2-Aへ逐語引用。
- Grep `m1_enabled|M1_ENABLED` in `er006_secondary_asr_01.py`・`er078_asr_unified_judge_01.py`・`.env.example`→既定値と起動flag非依存を§2-C(c-5)へ。
- Grep `Melos|melos` in `er068_output/asr_phonetic_equivalence_generalization_01/*.md`と`er006_m1_multi_candidate_*test*.py`→過去Trial/fixtureの文脈(次語)一覧を§2-C(c-4)へ。
- Grep `part3_c1` in `er026_output/family_z_production_e2e_01/melos/run_e2e_01/a2/audit/*.json`〜`run_e2e_03/...`(存在する範囲)→過去runのpart3_c1判定結果(転写・受理経路)を(c-4)表へ。
- Grep `UDR #52|G2P|C3` in `docs/pm/USER_DECISION_REGISTER_01.md`・`CURRENT_SPEC.md`(`-n`)→M1承認時のG2P非採用文を§2-C(c-2)へ。
- `docs/pm/ACTIVE_TASK.md`: 先頭に本委任ヘッダ(管理ID/Status/UDR-blocking/禁止維持/報告=RESULT_PACKET_FZAQ5.md)を4行で追記。他ヘッダは残す。

## 実行コマンド全文
- T-0検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_05.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_05.md_check.json`(委任文本文=本メッセージ全文を同パスへ先に保存)
- 原文sha: `powershell -Command "Get-FileHash -Algorithm SHA256 docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md | Select-Object -ExpandProperty Hash; (Get-Content -Raw docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md).Length"`
- 当日費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --help` で引数を確認後、2026-10-20(JST)分を集計(引数例 `--date 2026-10-20`、存在しない場合はhelpの指定に従う)。
- Lock sha不変確認(作業前後): `powershell -Command "Get-FileHash -Algorithm SHA256 er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\review_lock_state.json | Select-Object -ExpandProperty Hash"`
- 正式経路offline再判定(§4で修正があった場合のみ): `.venv\Scripts\python.exe docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\m1_offline_replay_part3c1_10.py`(存在パス・引数はファイル冒頭docstringで確認し、実引数をRESULT_PACKETへ記録)
- Regression(§4で修正があった場合のみ): `.venv\Scripts\python.exe er058_output\unified_all_roles_production_wiring_01\patch_03b\run_tests_per_file.py --pattern "er006_m1_*_test_*.py" --pattern "er006_preprod_hardening_*_test_*.py" --pattern "er011_b1_connected_speech_*_test_*.py" --pattern "er021_en_asr_*_test_*.py" --pattern "er078_asr_unified_*_test_*.py"`(runnerの実引数名は冒頭docstringで確認。既知fail 3件[er007 ja_secondary_asr ×2、er020 fullseg ×1]は既知として区別)
- secret scan(commit前): `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain` → `git add <明示パス>` → `git commit -m "<下記>"` → push(直近commit e3995f51a と同じ手順。`git log --oneline -3 origin/main`で到達を確認。force/rebase禁止)

## SSOT追記文
本委任にSSOT編集権は無い。次の文案をRESULT_PACKETへ記載する(Fableが委任_07で統合): (1)`OPEN_ITEMS.md` OPEN-422へ「2026-10-20 ユーザー決定: A/A' REJECTED、Lock解除承認、全TTS再生成指示。①再照合(委任_05)結果=<§3表の集計: 不具合N件/仕様どおりN件/意図的対象外N件/空白N件>、是正=<有無>」の1行案。(2)`docs/pm/USER_DECISION_REGISTER_01.md` #120へ「2026-10-20 ユーザー: A/A' REJECTED(理由=既存仕様の不具合原因との関係・必要性の説明不足)。再提案は原因・既存仕様との関係・他案比較・QCDを揃えた場合のみ」、#116へ「2026-10-20 ユーザー: 録音2のLock解除承認」の追記案。(3)`DECISION_LOG.md`末尾への決定記録案(原文ファイルパス・sha256・文字数付き)。

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`、`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_05.md`(+`_check.json`)、`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`、(修正があれば)変更したコード・test・offline検証結果json。`ACTIVE_TASK.md`/`RESULT_PACKET_FZAQ5.md`はgitignore対象でaddしない。
- commit 1(先行、原文保存直後): `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_05: ユーザー2026-10-20指示原文保存(A/A' REJECTED・Lock解除承認・全TTS再生成指示)`
- commit 2: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_05: ①Melos/Mellows 承認済み仕様文との逐語照合・11-8不具合判定表(<不具合N件>)<+修正内容>`
- trailer: `Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_05`
- SSOT編集権: 無し(上記)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZAQ5.md`(新規)に: (1)T-0結果(原文ファイル・文字数・sha256、check PASS/FAIL+reasons) (2)§6の結論段落(逐語) (3)§3の判定表集計と各R#の1行判定 (4)A/B/Cの要点(各3行以内、仕様文引用の行番号付き) (5)(c-4)過去Trial比較表 (6)修正の有無・内容・Regression結果・offline検証結果(新規TTS 0を明記) (7)判断候補(該当時のみ。A/A'再提案は禁止) (8)費用(当日既使用JPY・本委任実費・出典) (9)Lock sha前後 (10)Git(commit hash・push到達・secret scan hits) (11)SSOT追記文案 (12)一覧外Read理由(あれば)。ラベル`USER_DECISION_REQUIRED`は付けない(判断候補と表記)。