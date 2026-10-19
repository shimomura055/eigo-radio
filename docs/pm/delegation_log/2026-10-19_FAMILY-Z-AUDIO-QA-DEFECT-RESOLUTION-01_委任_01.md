# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_01(ユーザー2026-10-19指示原文保存+不具合①「Melos/Mellowsの音韻同等性判定」の原因究明: 既存の一般化された音韻同等性判定(M1/F1/Tier3 er021/統一判定er078/Pronunciation Ledger)のどこで・なぜ棄却されたかをruntime evidenceとコードで特定し、承認済み仕様内の不具合なら修正設計(実装はOpusレビュー後の委任_03)、仕様変更が必要なら根拠・QCD付きで区分。**Phase 1=調査+修正設計、コード変更0、原則JPY0(既存wavへの既存ASR経路再実行のみ上限JPY10)、新規TTS禁止、HR Lock不変**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 原因究明+修正設計(Phase 1)。
- 到達上限Status: `ITEM1_ROOT_CAUSE_IDENTIFIED_FIX_DESIGNED_PENDING_OPUS`。
- 禁止: 「Melos↔Mellows」の個別例外・辞書追加で終わらせること/品質基準・閾値の緩和をもって「修正」とすること(閾値・許容基準の変更が必要なら「仕様変更候補」として区分し採用しない)/HR Lock・`review_lock_state.json`の変更/新規TTS/er019・run_mey_01への接触/並行agent(委任_02: `er020_tts_retry_local_rewrite_01.py`・`er003_v1_n3_01_tts_generate.py`・`er003_v1_crosslevel_audio_02_common.py`・CURRENT_SPEC LR節を担当)の担当ファイル編集。
- 固定ブロック: **E-1**(CURRENT_SPEC L2792-2816[M1/統一ASR]、L2137[Ledger/Resolver]、L2142[Tier3]、L1827[固有名詞HR]、OPEN-318、過去Trial: er021 EN ASR semantic equivalence・er078統一判定・er011 F1連結音声・M1 C2の設計/REPORT、OF-AUW-*のOpus指摘をGrepし、「音韻同等性」を判定する全機構とその仕様上の受理条件を関数:行で列挙)/**D-1**(本Phaseはコード変更なし。修正案は「既存仕様内の不具合修正」か「仕様変更」かを明確に区分)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(委任_02)**: 共有SSOT(OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER/CURRENT_SPEC)は「編集直前に`git status --porcelain <file>`でclean確認(dirtyなら60秒間隔最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASKは先頭に自ブロック追記(gitignore))/**F-1**(原則JPY0。ASR再実行は上限JPY10、実費を出典付き[pricing_snapshot+token実測]で報告し推定なら推定と明記)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_01.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ1.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`へ以下「# Family Z 音声品質不具合の解決」から「`USER_DECISION_REQUIRED`で報告すること。」までを原文のまま(1文字も変えず)保存し、文字数とsha256を報告。並行agent(委任_02)も同じファイルへ保存を試みるため、既に存在しsha256が一致すれば保存をスキップ)

# Family Z 音声品質不具合の解決・大原則不遵守の原因分析と再発防止

## 1. 背景・ユーザーFeedback

今回のMelos音声問題では、以下の3件が判明した。

1. 既存の音韻同等性判定が期待どおり機能していない可能性があるにもかかわらず、原因分析が完了していない。
2. Rewriteの既存発動条件と実装に不一致があったにもかかわらず、不具合の報告のみで止まっている。
3. Rewrite後の音声を旧原稿と照合する明確な不具合が判明したにもかかわらず、修正・検証まで進んでいない。

**ユーザーFeedback：これらは本来、承認済みの大原則に従い、AI側が原因究明から修正・検証まで自律的に完遂すべき問題である。**

なぜ不具合の発見・報告だけで作業を止め、ユーザーに再度指摘させることになったのか。

以下の実務対応と併せて、大原則不遵守の原因分析・再発防止を行うこと。

## 2. 不具合① Melos / Mellowsの音韻同等性判定

**目的：既存の一般化された音韻同等性判定を、承認済み仕様どおりに機能させる。**

今回の録音2では、

- 正解原稿：`Melos drank`
- Primary：`Mello drank`
- Secondary：`Mellows drank`
- ユーザー試聴：自然に「Melos drank」と聞こえる

という結果だった。

次を確認すること。

- 「Melos」と「Mellows」は実際に音韻的に同等なのか、それとも異なるのか。
- 同等なら、なぜ既存の一般化された音韻同等性判定でPASSにならなかったのか。どの処理・判定条件で棄却されたのかを特定する。
- 異なるなら、なぜSecondaryが「Mellows」と認識したのか。音声そのもの、ASRの固有名詞推定、辞書、PhraseList等の影響を切り分ける。
- 既存のM1・F1・Tier3等の関連機構、承認済み仕様、過去の同種不具合・Trialとの整合を確認する。

**「Melos ↔ Mellows」という個別例外を追加して終わらせない。** 一般化された既存機構のどこに問題があるかを明確にし、既存仕様内の不具合なら修正・検証まで自律的に完了すること。

新たな発音許容基準・品質基準の変更が必要な場合は、独断で採用せず、根拠とQCD影響を示してユーザー判断に上げること。

## 3. 不具合② TTS再試行・Rewrite発動条件

### 正式なユーザー決定

**「両ASRが同じ箇所の誤読に合意すること」というRewrite発動条件を削除する。**

Status：`APPROVED_FOR_PRODUCTION`

基本フロー：

TTS初回生成 → Primary／Secondaryによる承認済み検証 → NGなら最大2回のTTS再生成 → なおNGならRewriteへ進む。

既存の音韻同等性判定やその他の承認済み品質・安全条件を省略することは認めない。

### 必須対応

1. 以前の「両ASR合意」条件が、なぜ今回の実装で守られていなかったのかを調査する。結果的に条件を削除するからといって、不一致原因の分析を省略しない。
2. 当該条件の導入経緯・関連コード・Validator・retry・fallback・Human Reviewとの関係を確認する。
3. 今回承認された条件削除を正式Production経路に反映し、旧条件の不要な参照・検査を整理する。
4. 書換え前に誤判定でNGとなる問題が残らないよう、①の調査結果との整合を確認する。
5. Rewrite後の再検証・失敗時の処理・Human Reviewへの最終移行も含めて確認する。

この仕様変更によって、別の未承認のRewrite許容条件や品質基準を追加しないこと。

## 4. 不具合③ Rewrite後の原稿照合

今回、`Melos drank` → `He drank` と書き換えた後、減速処理後の音声を旧原稿 `Melos drank` と比較していた。

これは明確な実装不整合である。

**正式に許可されたRewrite後は、書換え後の原稿を正解として、すべての後続音声検査を行うこと。**

以下を実施する。

- 古い原稿が残存した原因を特定する。
- Rewrite後の正しい原稿が、減速・再生成・retry・fallback・resume・最終検証まで一貫して参照されることを確認する。
- 同種の不整合が他のProduction経路やFamilyにないか、必要十分な範囲で確認する。
- 修正・Regression test・正式経路での検証を完了する。

## 5. 大原則に従って行動できなかった原因分析

**今回の重要な追加課題である。単に「大原則の遵守を徹底します」という回答は禁止する。**

Repoの`CLAUDE.md`および`docs/pm/PM_GOVERNANCE.md`にある、2026年10月18日改訂の正式な大原則8項目を確認すること。

特に次の原則への適合を評価する。

- **原則2：品質を守りながら最速で完成させる**
- **原則4：不具合は委任範囲内で自律的に解決する**
- **原則5：手段に固執せず、全体を俯瞰して自律的に問題を解決する**
- **原則6：人間には重要な判断だけを求める**
- **原則7：工程の一部ではなくProject全体を見て判断する**
- **原則8：変更時は既存仕様・過去のTrial・全体工程との整合を確認する**

以下を分析すること。

**A. なぜ報告だけで止まったのか**

不具合の発見時点で、実際にどのGate・STOP条件・予算・委任範囲・ユーザー承認境界を根拠として作業を停止したのかを、ログや判断記録から特定する。

正当な停止理由がなかったなら、なぜ自律的に修正・検証へ進まなかったのかを明確にする。

**B. なぜ不十分な原因分析で報告したのか**

①について、既存機構が機能しなかった原因を調べず、単なる調査課題としてユーザーに提示した理由を明確にする。

**C. なぜ既存の大原則が実際の行動に反映されなかったのか**

Fableの委任判断、Claude Codeの実行範囲、STOP判定、PM Gate、報告・受入条件を確認し、どこで大原則が実行上の判断から抜け落ちたかを特定する。

今回固有の問題と、今後も再発し得る構造的な問題を区別する。

**D. 再発防止策**

原因に対応した具体的な再発防止策を示し、既存の承認済みルール内で実施できるものは反映・検証する。

再発防止策は、新たな過剰Gate・重複チェック・不要な待機を増やさず、既存の委任・Closeout・報告の仕組みを優先して改善すること。

正式なPM運用ルールや承認境界の変更が必要なら、ユーザー判断事項として切り分ける。

なお、ChatGPT側の報告評価・指示設計にも問題があった。Claude/Fable側だけに原因を限定せず、判断や引き継ぎの境界も含めて分析すること。

## 6. 実行・受入条件

- 既存の承認済み仕様・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・過去Trial・関連Productionコードを必要範囲で確認する。
- 独立して進められる調査・修正・テストは並列化し、品質を守りながら最短で完成させる。
- 承認済みの開発費・委任範囲内で自律的に原因究明→修正→検証を進める。小額費用や委任回数だけを理由に逐次承認を求めない。
- 正当なSTOP条件・予算上限・承認境界は維持する。未承認の仕様変更、品質基準変更、新しいTrial範囲は独断で採用しない。
- Cross-Family共通仕様かFamily固有仕様かを確認し、該当するFamilyのProduction配線・検証状況を個別に報告する。
- 正式初回Production経路、retry／fallback／regeneration／resume、Validator、runtime evidence、actual model_id・routing、SSOT・Git反映を確認する。
- `PRODUCTION_WIRED`の要件をすべて満たすまでは、配線完了と報告しない。
- Fableによる報告照合・独立受入評価を行う。既存のOpusレビュー必須条件に該当する場合は、そのGateも適用する。

## 7. 最終報告

報告は以下の順番とする。

1. **①〜③それぞれの結論**：原因、修正内容、検証結果、残課題、Status
2. **大原則不遵守の原因**：何が、どの判断段階で、なぜ起こったか。確認できた証拠
3. **再発防止策**：実施済み対策と、その有効性の検証結果
4. **QCDへの影響**：音声品質・完成速度・量産単価・開発費用
5. **Production反映・SSOT/Git状況**：実経路の証拠と未完了項目
6. **ユーザー判断が必要な事項**：ある場合のみ、推奨案と理由を提示

**完了条件は「調査・報告したこと」ではなく、承認範囲内の不具合を修正・検証し、必要な再発防止まで完了したこと。**

正当なSTOP条件や未承認の仕様変更が必要となる場合のみ、理由・証拠・解決案を整理して`USER_DECISION_REQUIRED`で報告すること。

## Fable指示(①の調査・設計要件。本委任の対象は①のみ。②③は委任_02、⑤は委任_04)
1. **音韻同等性判定の全機構マップ**: 「期待語 vs ASR転写語」の同等性を判定する全ての処理を列挙(関数:行、入力[文字列/ARPAbet/G2P]、受理条件、呼出順序、どのFamily/経路で使われるか): M1(`er006_m1_multi_candidate_01.py` 置換案生成・`_post_check`・F1説明要件)、F1連結音声(`er011_b1_connected_speech_validator_01.py`:153-168 Pattern A等)、Tier3(er021 semantic equivalence: Secondary転写と期待語の比較方法=文字列正規化か音素か)、統一判定(`er078_asr_unified_judge_01.py`:352付近)、Secondary(`er006_secondary_asr_01.py`:805-860,896,946)、Pronunciation Ledger照合(ledger key `ec716e185835dba3` の4候補とPhraseList)、er025 Resolver(confidence low→hints未適用)。
2. **音韻比較の事実**: 期待「Melos」(Ledger候補 `M EH L OW S`等4件)とSecondary転写「Mellows」(CMU/G2P: `M EH L OW Z`)、Primary「Mello」(`M EH L OW`)、「Melo」のARPAbet列を実際に取得(既存のG2P/CMU経路を使用)し、差分を音素単位で表にする(語末/S/↔/Z/の有声性のみの差か、母音差か、音節数差か)。既存機構の「同等」定義(どの音素差を許容するか)と照合し、「Mellows」が既存定義で同等とされるべきか否かを**仕様文(CURRENT_SPEC行番号)と判定コードの条件式**で判定する。
3. **棄却箇所の特定**: 録音2(attempt2)の判定ログ(E21 telemetry行9613-9614、attempt_history行15172-15176、`asr_reeval_part3c1_10_result.json`、`m1_offline_replay_part3c1_10_result.json`)で、各機構が「Mellows」「Mello」をどの条件式で棄却したかを1件ずつ特定(例: Tier3が音素比較ではなく正規化文字列一致で比較している/F1がPattern A[歯擦音後続]のみで語末有声性差を扱わない/M1の`_post_check`がF1説明を必須にしている等)。各棄却について「仕様どおりの棄却」「仕様では受理すべきなのにコードが棄却(不具合)」「仕様が未定義(空白)」の3区分。
4. **Secondaryが「Mellows」を返した理由の切り分け**: PhraseList(Ledger由来)の内容と効果、Azureの固有名詞推定、音声そのもの(録音2・録音3・run_e2e_03 PASS版で同条件再転写し一貫性を見る。既存ASR経路のみ、上限JPY10)。可能なら語末区間の簡易音響指標(sibilantエネルギーの有無。既存ライブラリで可能な範囲、新規依存追加不可)。
5. **修正設計(不具合に該当する箇所のみ)**: 一般化された修正案(例: Tier3/統一判定で期待語とSecondary転写をARPAbetで比較し、既存の「同等」定義に従って判定する/F1に既存定義内の未実装パターンがあるなら補完)を、変更箇所・影響Family(X/Y/Z・B1/A2)・retry/fallback/resume経路・Regression案(fixture: 語末有声性差・歯擦音後続・母音差の非受理例を含む記事非依存ケース)・費用影響と共に提示。**個別例外(Melos↔Mellows)は不可**。閾値・許容基準の新設/緩和が必要な場合は「仕様変更候補」として分離しQCD影響を付す(採用しない)。併せて、修正後に録音2がPASSになるかをoffline what-if(既存転写に対する判定のみ、API 0)で見積もる。
6. **Opusレビュー観点案**: 5件以内。
7. 文書: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md`(§1機構マップ/§2音素比較/§3棄却箇所と3区分/§4 Secondary要因/§5修正設計とwhat-if/§6 Opus観点/§7 E-1)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\HR_LOCK_PART3C1_ROOT_CAUSE_01.md`(§1〜§4)と同ディレクトリの`m1_offline_replay_part3c1_10_result.json`・`asr_reeval_part3c1_10_result.json`・`asr_reeval_slowed_part3c1_10_result.json`
- `C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01.py`、`C:\Users\tensh\eigo-radio\er011_b1_connected_speech_validator_01.py`、`C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py`、`C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py`(該当関数)、er021のTier3実装(Grepで特定)
- `C:\Users\tensh\eigo-radio\er006_output\pronunciation_ledger_01\ledger.json`(key `ec716e185835dba3`)
- `C:\Users\tensh\eigo-radio\er021_output\en_asr_semantic_equivalence_production_wiring_01\telemetry.jsonl` 行9611-9621、`C:\Users\tensh\eigo-radio\er011_output\attempt_history.jsonl` 行15172-15176
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\narration\attempts\full_story_part3_c1_attempt2*`(wav+json)、同attempt3、`run_e2e_03`の同clip PASS版wav

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: `音韻|phonetic|ARPAbet|semantic equivalence|Tier3|M1|F1|PhraseList`→仕様上の同等定義と受理条件を§7に行番号付きで記録(編集しない)。
- `OPEN_ITEMS.md`: `OPEN-318|OPEN-419|OF-AUW`→関連を§7へ。新規起票`OPEN-422 FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01`(親項目: ①②③+⑤。番号は直前Grepで末尾+1。並行agent(委任_02)が先に起票していればそれを使い、①の行を追記)。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ユーザー指示受領(①原因究明、②両ASR合意条件の削除=APPROVED_FOR_PRODUCTION、③Rewrite後原稿照合の修正、⑤大原則不遵守の原因分析)。原文sha」(委任_02が先に書いていれば重複させない)。`docs/pm/USER_DECISION_REGISTER_01.md`: 本指示を判断済み(次番号)で登録(重複確認)。`docs/pm/REPORT_LEDGER.md`: 1行。`docs/pm/ACTIVE_TASK.md`: 先頭固定ヘッダ。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_01.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FZAQ1_stop_check.json`
- `certutil -hashfile C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md SHA256`
- `rg -n "Tier3|tier3|semantic_equiv" C:\Users\tensh\eigo-radio --glob "er021*.py" --glob "er078*.py" --glob "er006*.py"`
- 音素比較script(新規、API 0): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\phoneme_compare_melos_01.py --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\phoneme_compare_melos_01_result.json`(既存G2P/CMU経路をimportして「Melos/Mellows/Mello/Melo」のARPAbetを取得・差分表を出力。`-I`でimport不可なら`-I`なしで実行し理由を記録)
- ASR再転写(必要時のみ、上限JPY10): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\asr_consistency_part3c1_01.py --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\asr_consistency_part3c1_01_result.json`(入力=attempt2/attempt3/run_e2e_03 PASS版wav、Primary・Secondaryを既存経路で各1回、費用記録)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`

## SSOT追記文(要点)
- OPEN-422(新規または追記): 「①音韻同等性判定: 棄却箇所=<関数:行・条件式>、3区分=<仕様どおり/不具合/空白>、修正設計=<要点>、Opusレビュー待ち。個別例外は不採用」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log(USER[未保存なら]+委任_01+check+stop_check)、ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md、script+result json、SSOT(OPEN_ITEMS/DECISION_LOG/REGISTER/REPORT_LEDGER)。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_01: ユーザー2026-10-19指示原文保存+①Melos/Mellows音韻同等性判定の原因究明(全機構マップ・音素差分・棄却箇所の3区分・一般化修正設計、コード変更0)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ1.md`)
4行: (1)整合(E-1: 仕様上の同等定義[行]と各機構の受理条件、Cross-Family/Family固有の別)(2)Production到達経路=変更なし(3)成果物とcommit sha、音素差分表の要約、棄却箇所一覧(機構/条件式/3区分)、「Mellows」の要因切り分け結論、修正設計の要点(不具合修正/仕様変更候補の区分、影響Family、what-if結果)、実費(出典)(4)撤去/残置。`判定整合:`・`判断候補:`(仕様変更候補はQCD付き)・T-0 check・自己チェック(コード不変/Lock sha不変/新規TTS 0/原文sha256)。
