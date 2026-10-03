## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_57)。並行タスクなし(委任_55・56・Opus#7は終了)。

## 性質/到達上限Status/禁止事項

- 性質: (1)再較正で外れたA4-1の正解ラベルを、ユーザー正式採用の線引き(2026-10-03)に合わせて再判定・反映し、委任_55の未commit分をcommit、(2)Opusレビュー#7とFableのPM評価の保存、(3)説明文混入対策「P-strict-closed」(Opus#7の4ガード付き後段分離)の¥0事前確認と、確認が通った場合のみTrial専用スイッチ(既定OFF)での実装、(4)SSOT更新と`USER_DECISION_REQUIRED`でのSTOP。
- 到達上限Status: 線引き=`APPROVED_FOR_PRODUCTION`(未配線)。説明文混入対策=Trial実装(既定OFF)まで。**有効化・採用はユーザー承認待ち。** 次Trial・29件横断は開始しない。
- 禁止事項: Production正式path(`er003*`〜`er019*`)の変更禁止。機械的な安全装置(`FLOOR_FLAGS`のfloor、precheck、主体置換ガード、`DISCLOSURE_GAP_NEGATION_RE`)を変更しない。LLM/API呼び出し禁止(¥0。再較正の再実行もしない)。新しい仕様候補を勝手に追加しない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分に触れない。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 説明文混入対策はOpus独立レビュー#7(条件A)実施済み。本委任はそのレビューで示されたガードを含む形で実装する(レビュー済みの形と異なる変更が必要になったら実装せず報告)。A4-1の再ラベルはユーザー正式採用基準の適用で、構造変更ではない(非該当)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

(E-1/D-1/G-1/F-1/T-0/T-2は通常の固定ブロックどおり。本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_57.md`。委任文は全文そのまま保存(要旨化不可)。一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文、2026-10-03。全文は`DECISION_LOG.md`の委任_55エントリに逐語あり)

- 「この線引きを正式仕様として扱い、現在の判定ルール・正解ラベル・Safety-critical登録・降格ルール等と食い違う箇所を修正してください。」
- 「ただし、数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に勝手に緩めないでください。」
- 例2: 「`They enjoyed AI's convenience, but a human was on the other end. They did not realize it.` → **問題なしとして許容。**」
- 「問題なし: 確認済みFactから自然に導ける描写・推論で、新しい具体的事実を追加しないもの」
- 「ユーザー承認なしに、説明文混入対策をProduction採用しないでください。また、次Trialへも進まないでください。」
- 「今回の作業が終わったら、何が解決したか、何が未解決か、次Trialへ進める状態かを報告してSTOPしてください。」

## 作業1: A4-1の再ラベル(Fable判断: ユーザー正式採用基準の適用)

委任_55の再較正で、Safety-critical登録のA4-1(対象文「people who thought they were speaking with AI were actually speaking with human staff」「That was what people thought as they spoke.」、safety_A4)がV7で2/2 ACCEPTABLEとなり不合格だった。Fable判断: この文は、ユーザー判断済みの例2(利用者がAIだと思っていた、気づかなかった、という推論)と同型で、「were actually speaking with human staff」の事実部分はLedger(人間の契約スタッフが一部の電話を担当)に支持されるため、正式採用基準では**問題なし(ACCEPTABLE)**。旧Safety-criticalラベルが新基準と食い違っているので、ラベル側を直す(選択肢(イ))。rubric V7は変更しない。
1-1. `er052_open233_self_recovery_r3dprime_calibration_01.py`の`SAFETY_CRITICAL_SUB_IDS`からA4-1を外し(6件→5件)、runnerの`SAFETY_CRITICAL_CLAIM_DEFS`では`expected:"ACCEPTABLE"`の監視用として残す(Meta-1/Meta-2と同じ扱い)。設計書の正解ラベル表(委任_55が更新した§7-1付近、Grep `A4-1`)を「ACCEPTABLE(2026-10-03、正式採用基準の適用。旧: BLOCKING Safety-critical)」に更新。再分類doc・criteria docにも1行追記。
1-2. 残りのSafety-critical登録(B3、B4-a、A2A3-0、A4-0、A5-0)について、各対象文を正式採用基準の3定義に当てて「重大のまま」で正しいかを1行ずつ確認して表にする(変更は、例2と同型のものがもう1件あった場合のみ。あれば実装せず報告)。
1-3. 再較正の結果ファイル(`er052_output/open233_safety_control_03/results_01.json`)に、再実行せずに「A4-1は期待ラベルの修正により合格扱い(2026-10-03、Fable判断、理由)」の注記を**別ファイル**`relabel_note_a41.md`として追加する(元の結果は改変しない)。再較正の最終判定: (a)Safety-critical 5claim 誤降格0、(b)Safety12 0/18、(c)Hormuz V6と同じ、(d)例3件期待どおり、(e)K16・K20 BLOCKING、(f)false BLOCK 0 → **合格(ラベル修正後)**。
1-4. テスト更新(A4-1が監視用へ移ったこと、`detect_safety_critical_misdowngrades`対象外)。

## 作業2: Opusレビュー#7とPM評価の保存

`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\agent-ad9d076b79a05de9e.jsonl`から依頼文(最初のuserメッセージ)とSubagentHandbackの報告文を抽出し、`docs/pm/opus_l2_review_open233_self_recovery_07.md`に、`_06.md`と同じ構成((1)位置づけ[条件A、ユーザー明示指示]、(2)依頼文逐語、(3)Opus全文逐語、(4)FableのPM評価)で保存。あわせて委任_55・56の最終報告(`agent-af2959cc462bbfd90.jsonl`、`agent-af637d9ce6c035cf5.jsonl`)を`_55_result.md`・`_56_result.md`として保存。

(4)に貼るPM評価(そのまま):

**Fable PM評価(2026-10-03、Opus独立レビュー#7)**
1. 照合(11-3節8項目): 委任_56の設計doc・Opus#7・ユーザー指示(2026-10-03 §4〜§8: 見送らない、原因深掘り、複数案、Opus必須、再評価)・OPEN-233の目的(Checkerの指摘箇所を本文へ照合し最小Rewrite)・正式採用の線引き・最小Rewrite原則・「Human Reviewは非常口」・QCD・予算(上限¥900)を照合した。
2. 採用: (a)原因分析はOpusの順位づけ(主因=複数箇所の置き場の欠如[既に欄を常設し`prior_issues`に確定範囲を渡す形で解消済み、現行構成で混入0/35]、従=エコー、補助=指示文)を採る。(b)前回方式の検出低下の説明にH6(証拠負担の増加で境界的な指摘を出さなくなった。空出力3回は推論量が極端に少ない)を加える。これは案R(Prompt最小追記)にも当てはまるため案Rは採らない。(c)対策はP-strict-closed(委任_56のP-strictに、Opusの4ガード: 残りの長さ制限[英語6語以上/日本語11文字以上は確定不能]、対比・参照語の検出、残りが記事内で断片に連続している場合の拒否、英語本文限定)をTrial専用スイッチ(既定OFF)で実装する。U06・U11・U12は人間確認のまま(「勝手に縮小しない」との衝突を避ける)。(d)案Q(別欄の逐語で補う)は経路の不整合(Rewrite対象決定に反映されない)のため採らない。案Q'・案R・配列方式の再試行・案S2(委任_35の判断を覆す)も採らない。
3. そのまま採用しなかった点: (a)Opusは「T+監視」も正解としたが、ユーザー指示(見送らない、対策検討)とQCD(¥0・決定論・fail-closed・約80行)を踏まえ、安全網としてのTrial実装までは進める。有効化と採用はユーザー承認待ち。(b)「現行構成で実害ほぼ0」は、346行の大半が旧構成の記録であることと、実記事(発言の引用符が多い)での再発が未測定であることから、「安全網の価値は低いが0ではない」と評価する。
4. 実装前の¥0確認(Opus指摘): 複数範囲を改行でつないだ`claim_span_text`のエコーの有無を既存ログで確認、4ガード入りの規則で346行と合成テスト(対比の引用・発言の引用・日本語「」・paragraph N等の位置語)を再生。1件でも確定→確定不能または範囲変化が出たら実装せず報告。
5. Production配線時の必須確認(`OPEN-233-A1-PROD`の条件に追加): 発言の引用符を多く含む実記事でのオフライン再生と確定範囲の目視確認、Trial runnerとProductionの同値テスト、runtime evidence(P確定レベル・捨てた残りの文字列)、局所QA fastpathの条件(e)のProduction信号への置き換え。
6. 自己点検(ユーザー指示§8): 見送り以外の手段(P系4案・Q・Q'・R・S1・S2)を比較し、Opusの独立評価も得た。結論は「主因は解消済み+¥0の安全網を追加」であり、1案失敗を理由にした見送りではない。
7. 進行判断: 11-3節の進行条件を満たす(Claude案とOpusは実質一致[ガード追加で収束]、承認済み範囲内、新Product原則なし、Safety/QCDの新しいトレードオフなし、Production採用判断ではない、予算内、新しい`USER_DECISION_REQUIRED`なし)。ただしユーザー指示§11により、採用・有効化はユーザー承認待ちとし、Trial実装(既定OFF)までで止める。

## 作業3: P-strict-closedの¥0事前確認

3-1. **エコー確認**: 委任_42以降の実行記録(rep22、委任_49以降のinstance JSON)で、`prior_issues`に渡した複数範囲の改行連結文字列を、次周回のRecheckが`claim_in_article`にそのまま(改行または連結の形で)返した例があるかを数える(スクリプト、標準ライブラリのみ、`er052_output/open233_explanatory_mixed_offline_check_01/echo_check_01.py`)。
3-2. **再生**: `er052_output/open233_explanatory_mixed_offline_check_01/check_01.py`をコピーして`check_02.py`を作り、Opusの4ガードを実装した規則(P-strict-closed)で、(a)13行、(b)346行、(c)委任_53対照腕62件、(d)非BLOCKING6行・`same_fact_id_locations`14件、を再生。委任_56の表と同じ形式で、確定→確定不能・範囲変化・確定不能→確定・理由変化を出す。合成テストに次を追加: 対比の引用(`The article says “X” but the Ledger says “Y”`でYが記事に1箇所ある)、記事内の発言引用(`He said “…” in the opening`で記事に`He said “…”`がある)、日本語「」引用、`paragraph 5`・`closing`・`elsewhere`の位置語、残りが断片の直前・直後に連続する例、英語6語以上の説明文、日本語11文字以上の説明文。期待は全て確定不能。
3-3. 判定(Fable基準): (b)で確定→確定不能0・範囲変化0、合成テスト全件期待どおり、(a)で採用が10行(U06・U11・U12は確定不能)なら作業4へ。外れたら作業4を行わず報告。

## 作業4: P-strict-closedのTrial実装(3-3が通った場合のみ)

- スイッチ `VS_EXPLAIN_SPLIT`(既定False。CLI `--vs-explain-split`)。ONのとき、`_resolve_claim_string`でL0〜L5(と`label_only`)が確定不能だった場合にのみ、P-strict-closedを試す(照合経路は1箇所のまま。Stage 1初回・Recheck・Rewrite周回・retry・fallbackが同じ経路)。
- 規則: 引用符(“ ” " 「」)で囲まれた断片を全て取り出し、各断片を既存照合(L0〜L3、`VS_MATCH_EXT`ONならL5・単語境界)で「ちょうど1箇所」に確定。引用符の外の残りについて、(i)記事本文の3語以上の逐語でないこと、(ii)英語6語以上・日本語11文字以上でないこと、(iii)対比・参照語(ledger/source/but/instead/not/should/however/rather/台帳/原文/ではなく/しかし/べき 等。語彙はコード定数にし報告に逐語で載せる)を含まないこと、(iv)記事内で断片の直前・直後に逐語で連続していないこと、を全て満たす場合だけ採用。断片が1つも無い・不一致・複数一致・閉じ忘れ・上記(i)〜(iv)のいずれかに該当は確定不能(理由コード`explain_split_rejected:<理由>`)。英語本文のみ(日本語本文では新たに確定しない)。
- runtime evidence: `handoff`に`level="P:<断片数>"`、採用した断片、捨てた残りの文字列、拒否理由を記録。
- 複数範囲の`claim_span_text`(prior_issuesへ渡す連結)は**変更しない**(エコー確認の結果を報告し、変更が必要ならFable判断)。
- テスト: U01〜U13の実文字列(採用10・確定不能3)、合成テスト全件、スイッチOFFで委任_55時点と同一、`HANDOFF_MODE=legacy`で無影響。runner単体・er052回帰・全体回帰(基準11件以外に新規なし。`budget_state_c233an_42_rep22.json`の書き換えは`git checkout`で戻す)。

## 作業5: SSOT更新とSTOP

5-1. `DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-03、委任_55〜57、Fable判断。`USER_DECISION_REQUIRED`で停止)」: (1)線引き正式採用の反映(V7、ラベル更新一覧、Safety-critical登録8→5[A5-1は委任_29、Meta-1/2・A4-1は正式採用基準の適用]、再較正の結果と費用¥6.48、A4-1の再ラベル理由)、(2)残る食い違い(K19は`changed_comparison`のfloorで実行によりBLOCKINGになりうる=機械的安全装置は不変のため受容、「動機の帰属=QUALITY」、`DISCLOSURE_GAP_NEGATION_RE`否定形限定[rubric側で肯定形を扱う])、(3)説明文混入: 原因深掘りの結論・Opus#7の要点・PM評価の要点・P-strict-closedの事前確認結果・Trial実装(既定OFF)の有無、(4)`OPEN-233-A1-PROD`の条件追加(Production配線時の必須確認)、(5)ユーザー判断事項: 判断A=P-strict-closedを次Trialで有効化し、自己修復機構のProduction配線時の構成要素に含めるか(Fable推奨: 有効化する。¥0・決定論・fail-closed・Opusレビュー済み)、判断B=K19がfloorでBLOCKINGになる残りを受容するか(Fable推奨: 受容。機械的安全装置は緩めない方針どおり)、判断C=次Trial(5記事×2レベル)の前に行う限定flow確認と29件横断(1回)の実施可否、(6)予算: Phase累計¥536.4930、残¥363.5070。
5-2. `OPEN_ITEMS.md` OPEN-233行Status: 「`USER_DECISION_REQUIRED`(2026-10-03、委任_57): 線引き`APPROVED_FOR_PRODUCTION`反映・再較正合格(ラベル修正後)。真の重大見逃し0/23。説明文混入は主因解消済み+P-strict-closed【Trial実装済み(既定OFF)/未実装】。ユーザー判断A〜C待ち。次Trial・29件横断は開始禁止。`PRODUCTION_WIRED`ではない。」(旧Statusは「旧Status参考(委任_55)」として残す)。`OPEN-233-A1-PROD`行に、配線時の必須確認(PM評価5)とP-strict-closedの扱いを追記。
5-3. `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考、Opus発火列に「L2(条件A、#7、2026-10-03)」併記。
5-4. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §40(作業1〜4の結果と表)。
5-5. `docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`末尾に「5. Opusレビュー#7後の採否と事前確認・実装結果(委任_57)」を追記。
5-6. `docs/pm/ACTIVE_TASK.md` Status=`USER_DECISION_REQUIRED`、判断A〜Cを記載(addしない)。

## 事前指定Read一覧 / Grep一覧 / 実行コマンド / Git / 報告

(本委任文の「事前指定Read一覧」「事前指定Grep一覧」「実行コマンド全文」「SSOT追記文」「Git(明示add対象・コミットメッセージ・trailer)」「報告(RESULT_PACKET項目)」は、受領した委任文の記載どおり。要点: 順序=作業1→作業2→1回目commit/push→作業3→作業4→作業5→2回目commit/push。1回目メッセージ「OPEN-233-SELF-RECOVERY-TRIAL-01: 線引き正式採用の再較正結果とSSOTを反映、A4-1を正式採用基準の適用で問題なしへ再ラベル(Safety-critical登録8→5)、Opus独立レビュー#7と説明文混入の原因深掘り・複数案を保存(委任_55〜57)」。2回目メッセージ「OPEN-233-SELF-RECOVERY-TRIAL-01: 説明文混入対策P-strict-closed(Opus#7の4ガード付き後段分離)の¥0事前確認【結果】とTrial専用スイッチ実装(既定OFF、未採用)、USER_DECISION_REQUIREDでSTOP(委任_57)」。報告項目(1)結論10行以内(2)作業1(3)作業2(4)作業3(5)作業4(6)SSOT更新箇所(7)ユーザーへ戻す条件(8)T-0・commit・push・raw URL・一覧外Read・確認/推測の区別。)
