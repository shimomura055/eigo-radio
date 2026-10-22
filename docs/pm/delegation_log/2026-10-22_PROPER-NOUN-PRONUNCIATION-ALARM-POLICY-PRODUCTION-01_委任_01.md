FABLE-DELEGATION-MARKER: PNAP-DESIGN-委任_01-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01: ユーザー正式承認(`APPROVED_FOR_PRODUCTION`)の固有名詞発音新方針[①TTS発音供給(A階層自動/B階層は人承認時のみ)・②固有名詞のASR不一致はアラーム記録のみで停止/HRしない・③アラームを完成報告へ掲載し一般リスナーへ非表示]のFamily X/Z Production反映に向けた**現状調査+衝突調査+実装設計+未配線test**。Production .py未編集・API 0・JPY0。設計後にOpus条件Aレビュー→配線は次委任)

## 管理ID
PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01(新規。関連=OPEN-441[Stage 2 Trial Closeout、UDR #147は本承認で回答済み扱い]、OPEN-440[KP両方PASS=維持]、OPEN-371[技術STOP→HR Lock]、Stage 1配線[er097]、M1[er006_m1]、Reicher辞書[er003_v1_n3_01_tts_generate.py:990-999]。並行: `FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03`(er102、OPEN-445/446/新規行、UDR #145/#146、DECISION_LOG末尾)と`HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02`(er021系test、OPEN-447)が作業中。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。新規OPEN番号は編集直前にGrep最新+1)。

## 性質/到達上限Status/禁止事項
- 性質: Production実装の前段(調査・設計・未配線module+test)。到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(Production既存ファイル未編集=`PRODUCTION_WIRED`ではない)。
- Opus Gate: **条件A該当(新しい処理フロー: 固有名詞不一致の受理分岐+アラーム経路+Ledger→TTS供給)**。本委任の設計書を対象にFableがOpusレビューを手配する。あなたはレビュー観点が照合できる粒度で設計書を書く。
- 修正範囲(11-8): 本委任で編集可=新規`er103_*`(未配線module/test)、`docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/`、OPEN_ITEMS新規行、REPORT_LEDGER、delegation_log。**Production既存.py・Prompt・CURRENT_SPEC・DECISION_LOG・Ledger・HR queue・Storeは編集不可**(SSOT本文案はRESULT_PACKETへ)。
- 時間見込み(8-X): 約4〜5時間(調査2h/設計1.5h/module+test 1.5h)。並列: X経路とZ経路の調査は並列に読める。
- 費用/日次: JPY0(API呼出なし)。当日既使用 約JPY800+KPMP進行中(≤150)。実装後のruntime evidence(有料・見積は本委任で算出)は日次1,000円の制約から**翌JST日になる可能性**を前提に計画し、見積を明記。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止(管理ID・仕様名でGrep)。他agentの未commit差分を混ぜない。承認範囲を広げない(Writer側のCMU辞書外固有名詞禁止ルールは対象外。KP条件・一般語誤発音・文意変更・音声欠落の条件は維持)。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
# Claude Code指示：固有名詞発音の新方針 — Family X/Z Production正式反映

## 1. 目的・正式承認

ユーザーは以下の固有名詞発音方針を**正式Production仕様として承認した**。

目的は、英語学習サービスとして必要な品質を維持しながら、1日15作品の安定量産を実現すること。

**基本方針：固有名詞の発音は可能な範囲で改善するが、発音不一致だけを理由にProductionを停止せず、Human Reviewにも回さない。代わりに必ずアラームを記録・報告する。**

- 対象：Family X/Z共通
- Status：`APPROVED_FOR_PRODUCTION`
- 到達目標：両Familyで`PRODUCTION_WIRED`
- 今回の承認は、固有名詞発音に関する以下の仕様に限定する。
- WriterにCMU辞書外の固有名詞を禁止するルールは、今回の採用範囲に含めない。

## 2. 承認済み新仕様

### ① TTS発音改善方式の採用

Stage 2 Trialで検証した新方式を採用する。

- 正しい発音情報を調査・取得し、TTS入力側へ供給する。
- 公式・信頼できる根拠を確認済みの発音情報を優先する。
- Stage 2で提案された根拠階層を踏襲し、公式等のA階層は自動供給、媒体由来のB階層は人間が承認済みの場合のみ辞書登録・供給する。
- 発音が取得できない場合、推定発音を無条件に正解として登録・供給しない。
- 読み方の登録・再利用・根拠の保存を整合させる。
- 既存の綴り置換方式（Reicher→Riker）等を活用し、不要な別機構を増やさない。

### ② 固有名詞のASR発音不一致

固有名詞の発音不一致を検出した場合、**アラームを記録するが、それだけではNGによる制作停止やHuman Reviewを発動しない。**

- 対象の固有名詞、記事、該当箇所、ASR認識結果、発音根拠、アラーム理由を記録する。
- 同じ固有名詞による無意味なretry・regenerationを繰り返さない。
- 固有名詞の不一致が解消しなくても、その他の品質条件を満たせば制作を完了できるようにする。

### ③ アラーム通知

**アラームは必ず記事完成報告に掲載する。**

報告には少なくとも以下を含める。

- 対象固有名詞
- 該当する音声箇所
- 検出した発音不一致
- 発音の根拠・確からしさ
- TTS発音改善を試みた結果
- 最終状態：アラーム付き完成

実際の本番サービスでは、アラームはeigo-radio運営責任者だけが確認できる形とし、一般リスナーには表示しない。

通知は制作を止めず、確認・承認操作も完成の必須条件にしない。

## 3. 品質判断の根拠

今回の方針は以下の理由に基づく。

1. 固有名詞には公式発音が公表されていないもの、確定した読みが存在しないもの、人や地域によって読み方が異なるものがある。
2. 正しい発音をTTSに供給しても、綴りなどに引きずられて正しく発音できないケースがTrialで確認された。
3. 現時点では対象語の発生頻度が比較的低い。ただし、1日15作品量産時の実際の頻度は未検証。
4. eigo-radioは英語学習サービスであり、固有名詞の発音の絶対的正確性を追求することが主目的ではない。

したがって、固有名詞の発音不一致について、過剰な調査・再生成・Human Reviewで制作を止めない。

## 4. 適用範囲と安全条件

**緩和対象は、固有名詞の発音不一致による停止・Human Review条件のみ。**

以下は従来の品質条件を維持する。

- 一般英単語の誤発音
- Key Phraseの発音検査（既存のPrimary/Secondary両PASS条件を含む）
- 文意を変える重大な読み間違い
- 音声欠落・構造不良・その他の重大な音声品質問題

固有名詞に分類されているという理由だけで、別の一般語を読み上げたり、文意を著しく変えたりする問題まで無条件に許容しない。

特に、**Key Phraseに固有名詞が含まれる場合などの既存承認済み品質条件との衝突**を調査し、独断で緩和しない。衝突があれば具体的なケースと選択肢を報告する。

## 5. Production実装・検証

Family X/Zそれぞれについて、正式初回Production経路へ反映する。

以下を確認すること。

1. 固有名詞発音情報の取得・TTS供給が正式経路で動作する。
2. 固有名詞の発音不一致時にはアラームを記録し、制作が継続する。
3. 固有名詞の不一致のみでHuman Reviewに回らない。
4. 通常のASR品質検査、retry、fallback、regeneration、resumeとの整合が取れている。
5. 固有名詞以外の不一致は従来どおり品質検査される。
6. アラームが最終記事完成報告まで確実に引き継がれる。
7. 本番サービスで一般リスナーにアラームが露出しない。
8. 必須Regression・Validator・integration testがPASSする。
9. 正式runtimeでFamily X/Z双方の動作証拠を取得する。

既存のHuman Review・ASR・Pronunciation Ledgerとの重複やDangling Referenceを確認し、不要になった旧ルール・旧検査は適切に整理する。

## 6. QCD・実行方針

品質（Q）＞速度（D）＞量産単価（C）≫開発費用。

- 既存機構を最大限活用する。
- 不要なAPI呼び出し・TTS再生成を増やさない。
- 固有名詞の発音不一致を理由とした不要な制作停止をなくす。
- Family X/Zで共通実装を優先する。
- 独立作業は並列化し、不要な日付分割・待機を行わない。
- 技術的な問題は承認範囲内で自律的に調査・修正・検証する。
- 開発費の日次原則1,000円（JST）と既存の個別承認枠を遵守する。追加承認が必要な費用・仕様・Trial範囲を無断で実施しない。

## 7. SSOT・受入条件・Closeout

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、必要なPM記録を更新し、Gitへ反映する。

Fableによる独立受入評価を実施する。

**PRODUCTION_WIREDと判定する条件**

- Family X/Z双方の正式Production初回経路へ配線済み
- retry/fallback/regeneration/resumeと整合
- 実runtimeで発火証拠あり
- 必須テストPASS
- 発音情報の出典・使用方法、actual model ID、routing、判定結果を確認可能
- 完成報告へのアラーム表示確認
- 一般リスナーへの非表示確認
- SSOT/Git反映済み
- 未処理の判断待ち・未配線仕様・Dangling Referenceなし

1項目でも不足すれば、未確認事項を明示し、`PRODUCTION_WIRED`とは判定しない。

## 8. 最終報告

次の順序で簡潔に報告する。

1. Family X/Zの実装Status
2. 新方式で発音改善できた具体例
3. 固有名詞不一致でもHuman Reviewなしで完成したruntime evidence
4. 完成報告のアラーム表示例
5. 既存品質条件が維持されている証拠
6. 量産単価・制作速度への影響
7. Fable受入判定・SSOT/Git反映
8. 未解決事項と必要なユーザー判断

**最終目標：固有名詞の発音について、改善できるものは改善し、改善できないものも運営側にアラームを残しながら、品質条件を守って制作を継続できるProductionを完成させること。**
---

## Fableの事前整理(設計の前提。再照合しズレは報告)
- 承認の線引き: 緩和されるのは「固有名詞の発音不一致**だけ**が原因の停止/HR」。KP英語フレーズ(両方PASS必須、OPEN-440)・KP解説文・一般語・数値/否定・文意変更・音声欠落・構造不良は従来どおり。Writer側ルールは対象外。
- 「固有名詞不一致だけ」の機械的定義が設計の核心: 既存の判定器が持つ区分(entity-like span限定の差分=`ASR_VALIDATION_UNCERTAIN`系/`cascade_unresolved_entity`/Stage 1の`_resolve_unresolved_entity_for_review`の入口条件、`TRUE_CONTENT_MISMATCH`との境界、数値・否定ガード、M1・多語同音救済との順序)を調査し、**「差分がcanonical側の固有名詞トークン(entity_like判定)に閉じており、それ以外のトークンは一致(既存正規化後)、語の追加・脱落なし、数値・否定・KPに非該当」**を受理条件の案として具体化する(Melos「Mellow Strength」型=語の追加を伴うものは対象外、等の境界例を列挙)。固有名詞の判定方法(既存entity_type検出/大文字始まり/CMU未収録/Ledger登録済み)の精度と誤分類リスク(一般語を固有名詞扱いして許容してしまう)を評価。
- retry/regeneration: 「同じ固有名詞による無意味なretry・regenerationを繰り返さない」→不一致が固有名詞のみなら**初回attemptでアラーム受理し再試行しない**(既存のattempt上限・cascade・Tier3・M1は先に適用し、解決すればそちらを優先)。resume時の再判定・Store再利用・HR Lock(`er011_human_review_lock_01`)との整合: アラーム受理は`approve_regenerate`等の人間承認を必要としない完了状態として扱う。既存のPASS_WITH_WARNING(事後試聴区分)との関係を定義(新区分`PASS_WITH_PRONUNCIATION_ALARM`等)。
- ①TTS供給: 既存`tts_safe_name_pronunciation_en`(辞書{"Reicher":"Riker"}、n3経路。X/Zの現行経路に配線されているかを確認)を、Pronunciation Ledgerの階層(Stage 1の`basis`/A・B階層、引用実在確認)から供給する形へ(A階層=自動、B階層=`human_approved`が真の語のみ)。ESTIMATEDは供給しない。供給した場合のASR比較対象(置換後テキスト)と、供給根拠の監査記録。Stage 2 Trialの知見(Khaite→Kate 8/8、Meink/Altuzarraは制御不能)を設計の期待値に反映。調査(Stage 1の最終slot調査)は維持しつつ、HR向けパッケージ→**アラーム内容**へ用途を変える(重複排除)。
- ③アラーム: 記録先(run配下`audit/pronunciation_alarms.json`+共有`er006_output/.../pronunciation_alarms.jsonl`)、完成報告への掲載(X/Zのassembly audit→RESULT_PACKET/試聴ページの**運営者向け**セクション)。一般リスナー非表示: 現行のユーザーテスト配布(GitHub Pages `user_test/*/index.html`)は実質公開のため、アラームはindex.htmlに出さず、別ファイル(例`audit/operator_alarms.json`、Pages非公開dir or 非リンク)に置く案と、将来の本番配信での扱いを分けて設計。
- 旧ルール整理: 固有名詞のみ不一致でHR Lockへ送る経路、Stage 1のHRパッケージ表示、OPEN-318/327/330/331/335等の「固有名詞ASR救済」系Open ItemsのStatus整理候補(閉じるのはFable/ユーザー)。Dangling Referenceの洗い出し。
- 衝突調査(報告必須): (a)KPフレーズに固有名詞が含まれる場合(例: byUs)=KP条件維持なので従来どおりHR/再生成(アラームは併記するか)、(b)JA segmentの固有名詞(メロス→メオス)は日本語ASRの別経路=対象か否か、(c)Family Zの対話文での人物名(Melos/Selinuntius)=固有名詞のみ差分が頻発し得る→アラーム多発の見込み件数、(d)数値・否定を含むsegment内の固有名詞、(e)音声欠落(語の脱落)と「固有名詞の脱落」の区別、(f)Secondary(Azure)Phrase Listとの関係、(g)OPEN-371(技術STOP→HR Lock)との関係。各ケースに選択肢を付けて報告(独断で緩和しない)。
- runtime evidence計画: X/Zそれぞれで固有名詞不一致を自然発火させられる既存記事/segment(例: Khaite/Toteme/Altuzarraを含むFamily X記事、Melos Z記事)を特定し、正式runnerで最小の有料run(segment限定)を設計、見積(円)を出す。翌JST日実行の前提可。

## 実行内容
1. 調査(0円): 上記前提の各項目をコードで確認し`INVESTIGATION_01.md`(経路図X/Z: TTS→ASR判定→cascade/M1/多語同音/Stage 1→HR Lock→assembly→完成報告→Pages、file:行付き)。
2. 衝突調査`CONFLICTS_01.md`(a〜g+発見分、各ケース: 現行挙動/新方針適用時の挙動案/選択肢/Fable・ユーザー判断要否)。
3. 設計`IMPLEMENTATION_DESIGN_01.md`: 新module案(例`er103_proper_noun_alarm_policy_01.py`=受理条件判定+アラーム記録の純関数、単一flag `PROPER_NOUN_ALARM_POLICY_ENABLED`[既定は配線時にTrue=承認済み]、`er103_pronunciation_tts_supply_01.py`=Ledger階層→置換辞書供給[A自動/B人承認]+監査)、配線点一覧(X: `er019_*`runner/`er006_secondary_asr_01.py`/`er011_human_review_lock_01.py`/assembly audit、Z: `er063_*`/`er026_*`)、順序(既存救済→アラーム受理の位置)、resume/Store/retryとの整合、完成報告・Pagesの表示設計(運営者のみ)、旧ルール整理一覧、test計画(unit/wiring/DefaultOff isolation/Regression対象pattern)、runtime evidence計画+見積、ロールバック手順、量産単価影響(API追加0の根拠、調査費は現行と同じ)。Opus条件Aの観点(新構造の妥当性・既存Gateとの整合・安全条件・副作用・テスト十分性)に答えられる記述。
4. 未配線module+unit test(`er103_*_test_01.py`、Production import可だがProduction .py無編集)。
5. SSOT: `OPEN_ITEMS.md`新規行「PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01」`APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(ユーザー承認2026-10-22、原文所在、Production未編集)。`REPORT_LEDGER.md`1行。CURRENT_SPEC/DECISION_LOGの追記文案はRESULT_PACKETへ(配線委任で反映)。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: PNAP-DESIGN-委任_01-20261022`を含むAgent tool_useの通番、277前後。先頭行で一致確認)。
6. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_PNAP1.md`。

## 事前指定Read/Grep
- Read: `er006_secondary_asr_01.py`(Grep `def evaluate_attempt_with_cascade_detail|_log_human_review|_resolve_unresolved_entity_for_review|ASR_VALIDATION_UNCERTAIN|TRUE_CONTENT_MISMATCH|entity_like|cascade_unresolved_entity` → 該当範囲)、`er011_human_review_lock_01.py:100-200,300-340`、`er003_v1_n3_01_tts_generate.py:980-1005`、`er097_pronunciation_supply_stage1_01.py:1-120`(階層定義)、`er006_pronunciation_ledger_01.py`(Grep `basis|human_approved|tier`)、`er019_family_x_audio_production_runner_01.py`(Grep `human_review|HR|assemble|audit`)、`er063_family_z_audio_01.py`/`er026_family_z_fiction_production_runner_01.py`(同)、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_CLOSEOUT_01.md`(階層・知見)。
- Grep: CURRENT_SPEC `1837|2111|2818|多語同音救済|M1_MULTI_CANDIDATE|固有名詞` (節位置のみ)、OPEN_ITEMS `OPEN-318|OPEN-327|OPEN-330|OPEN-331|OPEN-335|OPEN-371`(Status行のみ)、`user_test` index生成script(Grep `PASS_WITH_WARNING` in `er019_*page*.py`/`er026_*page*.py`)で現在の警告表示の有無。

## Git
- 明示add: `er103_*.py`、`docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/**`、delegation_log 2件、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit: `PNAP 委任_01: 固有名詞発音新方針(ユーザー承認APPROVED_FOR_PRODUCTION)のX/Z配線に向けた調査・衝突調査・実装設計・未配線module+test、Production未編集、¥0`。

## 報告(RESULT_PACKET_PNAP1.md)
経路図要点/受理条件案と境界例/衝突ケースと選択肢(ユーザー判断が本当に必要なものだけを`判断候補`に)/設計要点と配線点/旧ルール整理一覧/test結果/runtime evidence計画と見積/量産単価影響/CURRENT_SPEC・DECISION_LOG追記文案/RESULT_PACKET 4行/raw URL(設計書3点)。