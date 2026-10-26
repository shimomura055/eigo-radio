## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02(OPEN-537是正の実装: Y runnerのStyle profile配線是正+fail-closed Gate+再発防止test → 再配達記事の影響音声を正式経路で再生成 → Std/Adv再組立・公開`_03`(旧`_02`との比較ページ付き) → OPEN-535の実経路evidence同時取得。Opus任意レビューM-1〜M-4必須、R-1〜R-8原則採用)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(新規`er127_*`+leaf module編集。Family runner call siteはX→Z→Yの順で、Yは他Agentの未commit変更があれば保留する取り決め)。**あなたは`er121_family_y_runner_01.py`/`er121_family_y_audio_01.py`/`er121_*test*.py`を所有**。`er019_family_x_style_profile_01.py`は**編集禁止**(Opus R-8: `m3_assembly_gate` default分岐は変更しない。必要な照合はY側で実装)。`er011_*`編集禁止。所有=上記er121群、新規`er121_family_y_style_profile_test_01.py`等、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{DESIGN_02,OPUS_REVIEW_01,IMPLEMENTATION_01,REGEN_RESULT_01,COMPARISON_01,VERIFY_01,COST_01}.md`、`user_test/family_y_production_redelivery_fee_03/**`、`er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/**`(wav/raw_usage_log/STOP/lockは不追跡、公開mp3は`user_test/`のみ)、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_{DELEGATION_02,OPUS_REQUEST_01,OPUS_RESULT_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP2.md`。SSOT編集権なし。pathspec付きcommit(実装/再生成・公開で分割可)。git index.lock競合は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(fx_20261017継承)とProduction runnerの乖離是正(B・T1)+再発防止+影響音声の再生成・再提出。到達上限Status=**修正版・ユーザー再試聴待ち**(PRODUCTION_WIRED判定はFable。Opus M-3: Voice 1〜3のS9評価未実施のため、Fable受入でも「完成」「PRODUCTION_WIRED」とは呼ばない)。
- 禁止: 新Style・新Prompt・新flag、Voice変更(Voice 1=Puck/2=Zephyr/3=Schedar、Persona維持)、Adv Comment 2の復活、本文改変、旧`_01`/`_02`公開ページ・旧run dir(`run_01`/`run_voice_puck_ev_01`)の改変、legacy waiverの新規作成(Opus M-2: 作らないのが最善。旧runの再pagesは不要)、`er019_family_x_style_profile_01.py`編集、同一dirでの`migrate_record`使用(Opus見落としリスク1)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用: 上限¥60(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日既使用約JPY563/残約JPY437/本委任見積JPY25〜45(33 take+5 clip≈38 take×約0.65〜1.2円+ASR、Puck×PD06 177字のretry率は未知)/改善見込み高/承認区分: C(300円以下、承認済みScope内)。
- Opus独立技術レビューGate: 任意レビュー実施済み(GO with changes)。M-1〜M-4は実装前必須、R-1〜R-8は原則採用(不採用は理由記載)。
- 修正範囲の線引き(11-8): 範囲内=profile配線是正・固定記録・Y Gate fail-closed・照合表・test・再生成・公開。範囲外=Gate緩和、PD06文面変更、V2(Voice本文default維持=新例外。ユーザー判断後に別委任)、X/Z Gate変更、TTS retry規則(OPEN-540)。
- 時間見込み: 約3.5h(実装+test 2h / 再生成0.5h / 公開・検査0.5h / 文書0.5h)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_02.md` をN=678から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02」のものを採用。Opus依頼文(先頭「## 依頼種別」「Opus独立技術レビュー(PM_GOVERNANCE 11-3 任意レビュー」「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01の設計」、N=677付近)を`..._OPUS_REQUEST_01.md`へ。下記Opus結果(逐語)を`..._OPUS_RESULT_01.md`と`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/OPUS_REVIEW_01.md`へ逐語保存。

## Fable判定(Opus照合)

- **V1(Voice 1〜3本文にも承認既定のPD06を適用)で再生成する**。理由: 承認記録(A19/T10/28-1運用7/USER_09)は全て適用で一致、Y固有承認Styleは0件、V2は新例外。ただしA19は「S9評価で確認」条件付きで未実施(Opus M-3)=**Voice 1〜3(Std/Adv 6 segment)は「S9未評価のユーザー判断項目」として旧`_02`(default)と新版をsegment単位で並べて再試聴に出す**。差戻し(V2)時の費用約8円・時間約30分を報告に添える。ユーザー原文「PD06を一律適用して個性を失わせない」はこの比較試聴で判断いただく(Fableが事前に新例外を採用しない)。
- 5 clip(Adv topic_intro/comment_1/comment_3、Std topic_intro/japanese_title)は**案R(再生成、約2.5円)**。理由: 音声再利用機構は同一out_dir cacheのみで、新dirへの引継ぎ機構を新設しない(R-5として報告に1行明記)。
- legacy waiverは作らない(M-2は「作らない」で充足。waiver機能自体に制限を入れるのは本委任範囲外、設計に記載のみ)。
- X/Z Gateの`checked=[]`穴は共通化しない(R-8)。Y runner入口で「新規runは承認profile必須」をassert。Z実測照合は別read-only確認(RESULT_PACKETに次委任案として記載)。
- OPEN-535実経路evidence: `run_style_fix_01`へ**`y_voice_1`の旧Algieba承認record(run_01由来)だけを意図的に複製**し、正式経路(実TTS)でreconcileが`Y_HR_APPROVAL_VOICE_MISMATCH`で退避→Puckで再生成されることを記録(追加費用0。y_voice_1はどのみち再生成対象)。他の承認は複製しない。quarantine fileと`audit/`記録を証跡とし、REGEN_RESULT_01に「意図的複製」であることを明記。
- 並行OPEN-535修正(commit 5568631ba)が`er121_family_y_audio_01.py`に入っている。HEADを取り込んだ上で作業(`git log --oneline -3 -- er121_family_y_audio_01.py`で確認)。
- 前委任(OPEN-527)の`er121_family_y_multiparagraph_regression_test_01.py` `TestPlannerBoundary`がCRLFで赤との報告あり(OPEN-535 Agent)、一方OPEN-527 Agentは7/7 PASSと報告。HEADで実行し事実を確認、赤ならtest側の期待(CRLFは段落区切りでない=現行仕様)に合わせて修正し記録(planner本体は変更しない)。
- 不要artifact: `er121_output/family_y_production_01/redelivery_fee/run_hrguard_ev_01_mock/`(OPEN-535 Agentのmock失敗run、自己発動RESTART_STORM sentinel入り、API 0、未追跡)は**Fable権限で削除を許可**(理由: mock専用・証跡はdocsに保存済み。削除前に`ls`でwav以外に固有ファイルがないことを確認し、削除した事実をRESULT_PACKETに記録)。`run_hrguard_ev_02_mock/`は残す。

## Opusレビュー結果(逐語。保存用+実装必須)

## 1. 結論: GO with changes（修正付きで進めてよい）

- 方式（X方式の`resolve_run_profile`をYに配線し、新run dirを使う）、33 take（Adv 15 / Std 18）、5 clip再生成の案R、V1（Voice本文にもPD06）は、どれも承認記録・コードと整合しています。
- ただし fail-closed Gate の「role網羅」検査は、設計どおりに実装すると Y 本文で空振りします（M-1）。legacy waiver が default 音声の新規生成経路になり得ます（M-2）。
- PD06 の文面は人物の語りを平板化させる懸念が文言上も具体的にあります。さらに A19 の承認は「S9評価で確認する」条件付きで、その評価は未実施です。V1 は「配線是正」で完了扱いにせず、S9 をユーザーの判断事項として明示して提出する必要があります（M-3）。

## 2. 判定表

| 論点 | 判定 | 根拠（ファイル:行） | 必須(M) / 推奨(R) |
|---|---|---|---|
| P-1 Voice本文にPD06 | 妥当（条件付き） | PD06の実文 `er019_family_x_style_profile_01.py:108-111` は「a smile in your voice」「reassuring」「like a favorite morning radio host」「keeping the news clear and credible」。どれも司会者役への指示で、全話者に一様な明るい感情の色を付けます。批判的・不満を述べる人物と食い違う可能性が文言から読めます（default 側の「calm, steady news narration…not dramatic」も語り手型ですが、感情の方向を指定していません）。A19/T10（`DESIGN_PROPOSAL_02.md:109,242`）は「適用」ですが、同:347 は「S9をTrialで評価し、PD06除外等が要れば再判断」とする条件付きの承認で、その評価結果は記録がありません（STYLE_MATRIX §6-2）。前例も無く、Z の人物 Dialogue は PD06 非適用です（`DESIGN_PROPOSAL_02.md:317`）。一方 V2 は Y 固有承認の Style ではなく、新しい例外です。V1 を既定とする判断自体は正しいです。 | **M-3**: 再提出では、Voice 1〜3（Std/Adv 6 segment）を「S9未評価のユーザー判断項目」と明記します。旧`_02`（default）と新版を segment 単位で並べ、追加費用は0円です。差戻し時の V2 の費用・時間（約8円）も添え、S9 確認前に「完成」「PRODUCTION_WIRED」と呼びません。**R-1**: Std 本文は PD06 逐語のため、旧 default にあった減速指示の連結が消え、話速が変わり得ます（後処理の6%減速は継続）。前後比較表に話速（WPM）を入れます。**R-2**: V2 実装例の `_base` は、Std では `_base_slower` にします（DESIGN 2-2-4）。 |
| P-2 fail-closed Gate | 要修正 | (1) `m3_assembly_gate` は FULL_STORY の対象を `full_story_part1..3` に固定しています（`er019…:201-202,675-681`）。Y ではこれらが entry=None のまま `checked` に入り、その後 `_X_ONLY_SEGMENTS` で除外されます（`er121_family_y_audio_01.py:765,799`）。このため設計(iv)「`x_gate.checked` が当該roleで≥1件」は、Y 本文が1件も検査されなくても満たされます。(2) SUPPORT_JA と KP_JA_MEANING は base sha だけで判定しています（`er019…:564-569`）。しかも `_generate_or_reuse` で再利用した entry は「untouched」扱いにならず、`attach_segment_profile_record` で現行 profile の sha が上書きされます（`er121…audio:699-700`、`er019_family_x_audio_production_runner_01.py:1114-1117`、`validation_inheritance:186-189`）。そのため日本語 role の照合は構造上「一致」になり、実際の送信値の測定にはなっていません。今回は新 run dir（M2）なので実害はありませんが、`style_actual_vs_approved.json` を「実測照合表」と呼ぶ根拠になりません。(3) 英語 role の偽陽性は確認範囲では見当たりません。発音 hint ありは head200 の前方一致で判定（`er019…:584-588`）、Std は逐語で sha 一致、LR は `<default:` → RECORD_MISSING とあわせて BLOCK → HR で、設計どおりです。resume は同一 profile なので問題なく、chunk は全 chunk を検査しています。(4) 並行中の TTS 統一（er127）は未コミットのため未確認です（ファイル0件）。 | **M-1**: 網羅検査は `x_gate.checked` ではなく、Y 側の期待集合（`Y_ROLE_COVERAGE` の role×level×segment）との**完全一致**で判定します。entry が存在し、`evaluate_segment_evidence` を実行した件数で数え、≥1件ではなく全件を要求します。**M-4**: 照合表の日本語行は送信 instruction の実測値（attempt または raw_usage_log の instruction）から取ります。取れない場合は「意図sha（実測なし）」と明示ラベルを付け、一致扱いにしません。**R-3**: er127 が Adv ③（短文Style）を承認済みの通常成功経路にする場合、現 Gate は `ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED` で BLOCK します。そこで「採用 attempt 番号＋承認済み Style 変種の一覧」を Gate が参照する形を er127 側の設計で定義します。順序は er127 確定 → Y Gate 実装です。**R-4**: profile 有効化で Adv の `ADV_MINIMAL_FALLBACK`、Std の `STD_FALLBACK_USED` が Y にも効き始めます。人間確認（HR）待ちの発生率が上がり得ることを QDC 見込みに入れます。 |
| P-2 補足 legacy waiver | 要修正 | `resolve_run_profile` は CLI で `default` が指定されると、run state の有無を見ずに default を返します（`er019…:481-482`）。waiver はファイルの path を渡すだけなので、AI 側で作成できます。 | **M-2**: waiver は (a) 既存 run state あり・固定記録なしの dir に限定し、(b) `tts_*` stage との併用を禁止して課金前に STOP し、(c) ref は `docs/pm/delegation_log/*_USER.md` 配下で対象 run の path を含むことを検査します。旧 run の再 pages が不要なら、waiver 自体を作らないのが最善です。 |
| P-3 再生成範囲 | 妥当 | 5 clip が Style 不変という判定はコードで確認しました。Adv topic_intro=`TOPIC_INTRO`、comment=`COMMENT` はいずれも override なし（`er121…audio:571,581`）。Std topic_intro=`TOPIC_INTRO`、japanese_title=`_role_style_ja()` で profile を通りません（同:678,688）。音声の再利用機構は同一 out_dir の cache だけで（`er019…runner:1076-1118`）、新 dir では M2 により結果ファイルを持ち込めません（`er019…:290-295,483-493`）。案R が正しいです。Voice 2/3 の再生成が必須という理解も正しいです。ただし本質的な理由は sha ではなく、音声自体が誤った Style で生成されていることです。 | **R-5**: ユーザー原文は「無関係な音声は再利用」なので、5 clip（約2.5円）を再生成する理由（新しい引継ぎ機構を作らない）を報告に1行明記します。**R-6**: KP 英語（K2）が Std と Adv で同じ Master Store key を共有する場合、2つ目の level は Store hit になり、3 take 少なくなる可能性があります（未確認。見積の過大側）。 |
| P-4 再発防止 | 一部不足 | (a)(c)(d) と M-1 で、Y の配線漏れは機械的に検出できます。ただし (c) の test は Y 専用（`er121_*`）です。新 Family では、その test を作らない限り何も検出できず、チェックリスト（人手の手順）頼みになります。X の `checked=[]` で PASS する経路は profile=default の分岐だけです（`er019…:695-696`）。default 以外の profile では `_gate_targets` が必ず名前を生成するため、`checked` は空になりません。共通 helper で塞ぐと、X の legacy default resume（公開済み旧 run）を壊します。 | **R-7**: 横断の登録表（Family→runner→`ROLE_COVERAGE`）と、Production runner を glob で列挙し、未登録なら FAIL する test を1本作ります。これで新 Family の未配線を機械検出できます。**R-8**: `m3_assembly_gate` の default 分岐は変更しません（X に影響するため）。各 Family の runner 入口で「新規 run は承認 profile 必須」を assert する方式が影響最小です（X は既に `DEFAULT_NEW_RUN_PROFILE` で同等）。Z の実測照合は未確認のままで、別途 read-only 確認でよいです。 |

## 3. 見落としリスク

- **再利用 entry の上書きで照合が自己一致になる**: 再利用した entry には現行 profile の sha が上書きされます（P-2(2)）。英語 role は最終 style の記録で実測検査されますが、日本語 role は自己一致になります。将来「同一 dir で profile を移行する」経路（`migrate_record`、`er019…:767-`）を Y で使うと、古い Style の日本語音声が PASS します。Y では使用禁止とするか、M-4 の適用が前提です。
- **長い PD06 と Puck の安定性**: Puck は default Style では1 attempt で通っていましたが、177字の PD06 との組合せは未経験です。retry 率は未知です（Cap 60円の範囲内）。
- **ゲート判定を固定記録からも取る**: `y_style_gate` は profile を引数で受け取ります。DESIGN 2-1-7 の再検証に加え、Gate 内でも `read_record` を正として、引数と食い違えば STOP するのが安全です。
- **並行作業の順序**: OPEN-527 の test が `r.STYLE_PROFILE` を参照しているため、名称撤去の前に並行委任を完了させる必要があります（設計どおり）。er127 が未コミットなので、照合キー（top-level `style_prefix` の正規化）の最終形は未確認です。
- **未読範囲**: ROOT_CAUSE_01 §Q2 と `assemble_level` の内部（Gate の再呼出しの有無）は読んでいません。

## 4. 5行要約

1. 方式・再生成範囲（33 take、案R）・V1 は承認記録とコードに整合しており、GO with changes です。
2. M-1: Y 本文の網羅検査は `x_gate.checked` だと X 専用の名前で空振りするため、Y 期待集合との完全一致で判定します。
3. M-2: legacy waiver は tts stage との併用を禁止し、ユーザー記録の ref 検査を必須にします。M-4: 日本語 role の照合表は実測値を使うか、「実測なし」と明示します。
4. M-3: PD06 の文面（smile / reassuring / radio host）は人物の語りを平板化し得ます。A19 は S9 評価が条件でしたが未実施なので、Voice 1〜3 は旧版と並べた試聴でユーザー判断項目として提出します。
5. X の `checked=[]` の穴は default 分岐だけで、共通化は X に影響するため見送ります。新 Family の配線漏れの機械検出には、横断の登録表 test（R-7）を推奨します。

(Opus逐語ここまで)

## 実施事項

1. **DESIGN_02.md**: DESIGN_01との差分(M-1〜M-4/R-1〜R-8の反映、Fable判定)。
2. **実装(API 0)**: DESIGN_01+M反映。runner `STYLE_PROFILE`撤去→`Y_APPROVED_STYLE_PROFILE="fx_20261017"`+`resolve_run_profile`(課金前)+固定記録`audit/style_profile.json`+ctxを生成/gate/assemble/stage shaへ透過、`generate_y_*`の`"default"`既定引数撤去、runner入口「新規runは承認profile必須」assert(R-8)。Y Gate fail-closed: 記録欠落/不一致/非承認profile/role未カバー=BLOCK、網羅は`Y_ROLE_COVERAGE`(role×level×segment)との完全一致(M-1)、Gate内でも`read_record`を正とし引数と食い違えばSTOP(Opus見落とし3)、`audit/style_actual_vs_approved.json`は英語role=実送信prefix照合、日本語role=実測instruction(attempt/raw_usage_log)から取得、取れなければ「意図sha(実測なし)」ラベルで一致扱いしない(M-4)。`migrate_record`はY経路で禁止(assert)。test: AST test(resolve呼出必須・`"default"`リテラル禁止)、drift test(承認profileと6 role sha)、Y_ROLE_COVERAGE完全一致test、fail-closed各ケース、resume/regenerate/chunk/LR再TTS/KP経路で誤BLOCKなし、R-7横断登録表test(Family→runner→ROLE_COVERAGE、Production runnerをglob列挙し未登録FAIL。X/Zは現状のまま登録)。OPEN-527 testの`r.STYLE_PROFILE`参照を更新。CRLF test事実確認。回帰: `er121*`全件・`er019*`(既知R4赤は区別)・`er063*`・`er011*`、接続0。**commit(実装)**。
3. **再生成(有料)**: `run_style_fix_01`を`run_voice_puck_ev_01`から**入力のみ**複製(HR承認/review_lock/stage JSON/resultsは複製しない。例外=y_voice_1の旧Algieba承認recordのみ意図的複製[OPEN-535 evidence])。事前: T-2追記4点確認、`py tools/stop_scope_check_01.py --managed-id FAMILY-Y-STYLE-PROFILE-FIX-01 --run-dir <run_style_fix_01> --out <docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/stop_check_02.json>`。正式CLI 1起動(`.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_style_fix_01 --theme-package <run_01と同じ> --approved-budget-jpy 60 --tts-execution-mode STANDARD` +必要stage。引数は`--help`で実値確認)、環境変数`TTS_EXECUTION_MODE=STANDARD`明示。起動間隔150秒以上・同一run 5分3回禁止。Adv Comment 2削除維持(`removed_by_spec`)。KP/Vocab/文法/shellはStore再利用(R-6のStore hitを記録)。費用はraw_usage_log実績で集計(`COST_01.md`)。OPEN-535 evidence: quarantine file・`audit/`・y_voice_1がPuckで再生成された記録を`REGEN_RESULT_01.md`に。
4. **公開`user_test/family_y_production_redelivery_fee_03/`**: Std/Adv完成版+**比較節**: Voice 1〜3(Std/Adv 6 segment)を旧`_02`(default Style)と新版(PD06)で並べて個別再生、「S9未評価・ユーザー判断項目」と明記、話速WPM前後表(R-1)、部位別Style前後表(全segment: 旧prefix→新prefix・再生成/再利用)。旧`_01`/`_02`は不変。page_verify・HTML/mp3存在・リンク検査(`VERIFY_01.md`)。**commit(公開)**。
5. **文書**: `IMPLEMENTATION_01.md`(変更一覧・Gate契約・test件数)、`COMPARISON_01.md`(前後Style・対象音声・品質[ASR一致・Gate結果・HR待ち件数R-4]・費用)、`REGEN_RESULT_01.md`、`COST_01.md`、`VERIFY_01.md`。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{DESIGN_01,STYLE_MATRIX_01,PREVENTION_01,REGEN_PLAN_01}.md`(自成果物)
- `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{BUILD_01,EVIDENCE_01,VERIFY_01}.md`(前回`_02`の起動コマンド・公開手順・検査項目を踏襲)
- `er121_family_y_runner_01.py:30-40,540-640,960-1040`、`er121_family_y_audio_01.py`(HEAD、OPEN-535変更取り込み後): Grep `reconcile_hr_approvals_for_request|stamp_requested_voice|y_style_gate|attach_segment_profile_record|_X_ONLY_SEGMENTS|style_prefix` → ±15
- `er019_family_x_style_profile_01.py:100-120,180-220,270-300,440-520,560-600,620-640,685-760`(読み取りのみ)
- `er019_family_x_audio_production_runner_01.py:1070-1120,3340-3360`(X方式の参照)
- `er121_family_y_hr_approval_guard_test_01.py`(構造)、`er121_family_y_multiparagraph_regression_test_01.py`(CRLF test)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_02.md --json-out ...\_check.json`
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er121*_test_*.py"`、`--pattern "er019*_test_*.py"`、`--pattern "er063*_test_*.py"`、`--pattern "er011*_test_*.py"`
- stop_scope_check(上記)、正式CLI(上記、実値はRESULT_PACKETに全文記録)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_YSP2.md`(9)にOPEN-537更新文案(是正実装・再生成・`_03`公開・再試聴待ち、S9判断項目)、OPEN-535文案(実経路evidence追記)、OPEN-539文案(新版`_03`再承認待ち)、CURRENT_SPEC Y節文案(Style profile継承=fx_20261017、Gate fail-closed、Voice本文S9未評価)、PM_GOVERNANCE改訂提案(Gate 7実測照合表、項目33)、新規OPEN候補(Z実測照合read-only確認/横断登録表のX・Z側充実/`run_hrguard_ev_02_mock`処置)。

## Git

- add対象: 所有ファイルのみ(wav/raw_usage_log/STOP/lock除外、公開mp3は`user_test/..._03/`のみ)。実装commit→公開commitの2段。
- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02a: Y runner Style profile配線是正(fx_20261017継承・固定記録・fail-closed Gate・Y_ROLE_COVERAGE完全一致・AST/drift/横断登録test、Opus M-1〜M-4反映、API 0)` / `... 委任_02b: 再配達記事 run_style_fix_01 再生成(33+5 take、実費¥X)+公開_03(旧_02比較節・S9判断項目)+OPEN-535実経路evidence`
- trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/02`
- push: `git push origin HEAD:main`(non-ffなら fetch→merge --no-edit→push。競合はSTOP報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YSP2.md`: (0)T-0、(1)M/R反映箇所、(2)変更ファイル・test件数・回帰結果(既知赤の区別、CRLF事実)、(3)再生成結果(take数・retry・HR待ち件数・Gate結果・Store hit・OPEN-535 evidence)、(4)前後Style表(全segment)・WPM表、(5)費用実績(raw_usage_log出典)・時間、(6)公開URL(`index.html`絶対URL)と検査結果、(7)判断候補(S9=Voice 1〜3のPD06可否[V1維持/V2差戻し約8円]のみ想定)、(8)必須4行+「判定整合: 重大NG=<なし|あり>」、(9)SSOT文案、(10)一覧外Read、commit hash、raw URL。末尾10行要約。