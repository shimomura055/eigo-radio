管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_03(設計書・事前登録のOpus条件A反映改訂+ユーザー決定記録、API支出¥0、Production変更なし)。日付 2026-10-09。並行して委任_02(B3注記仕様 v1 作成、新規ファイルのみ・git操作なし)が走っている。**委任_02の成果物(`B3_ANNOTATION_SPEC_v1*.md`、`b3_annotation_check_01*.py`)には触らない・stageしない。**

## ユーザー決定(2026-10-09、記録対象)
1. 案B(JA再確認)の新腕の扱い: **B1採用**=新腕は「新Writerの再実行」で回復(Fact Lock R0に既存must-fixブロック`original_must_fix`を付けて再生成→Astra R1→R2[系列X逐語]→後処理→EN再実行、1記事1回まで、Trial全体の上限3回[見積約¥105]、超過はSTOP記録)。
2. B3注記仕様をTrial前に正式なTrial仕様として先に固定する(ユーザー逐語は委任_02の委任文`docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02.md`に保存される。本委任ではその要旨を記録: 都度判断の注記では記事ごとに条件が揺れFact Lockの性能が測れない。何を【事実N】とするか/複数要素の分け方/重要数値の定義/数字が主役の場合/名称内番号/台帳由来制約/迷った場合/注記後の照合、を固定し、旧4+新6の全10記事を同一仕様で**再注記**する)。手順: B3注記仕様作成(¥0)→Opusレビュー→ユーザー提示・確認→E2E実装・実行。
3. 新6テーマの選定は未回答(候補10件提示済み)。

## Opus条件Aレビュー結果(2026-10-09、Fableが採用判断済み。全文はFableの手元にあり、要点を以下に転記。設計書・事前登録へ反映すること)
- 論点1 交絡: Arm C不要。影の対照を**両腕**で取る: M1(a)=旧腕本文に「M1入力の要約+EN検査1回」、新腕本文に「旧入力の要約+EN検査1回」(20対)。M1(b)=要約のみMAJOR発火時にもう一方の規則をログ専用で1回実行(新腕なら旧規則=Advanced再生成1回+EN検査1回[約¥0.6/発火、`er012_...runner_01.py` L556-579]、旧腕なら`open243_m1_summary_only_retry`)。M3=旧腕runで「changed_actorがあれば保護されていた除外claim」を¥0で列挙し任意でStage 2を1回。DESIGN §3 L106-107「M1(b)の反実仮想は安く再現できない」は**誤り**なので訂正。追加費用見積 計¥10〜15。
- 論点2 案B: B1採用(上記)。必須(¥0): 主指標に「初回(回復前)のJA_RECHECK発生率」を両腕で記録(旧腕は`JARecheckRequiredError`捕捉時点)。前提作業(c)タグ残存修正(30〜50行)が必要になる。PREREGISTRATION §5-8を確定。
- 論点3 Production等価性: 新腕のFC MAJORは「記録して続行」を維持しつつ、R2後のFC MAJORに`shadow_stop=true`を付ける。複合主指標「**人手介入必要率** =(JA STOP+影STOP+EN STOP+Human Review)÷予定run数」を両腕同定義で追加。B1採用時はR2のFC MAJORも同じ回復経路(1回)に統一してProduction等価にする。記号Gateは記録のみで可、残存はTTS対象2本で確認。
- 論点4 M1 Standard: 実装しない。Standardのattempt1 MAJORを`open243_majors_only_in_summary`で要約/本文に分類して記録(¥0)。「Standard側のM1効果は未測定」と明記(Standardは修正済みAdvanced要約を含む全文をA2化するため部分的に伝わる、`er003_v1_n3_01_standard_a2_generate.py` L522/L541)。
- 論点5 注記brief: 条件付き可。注記ルール固定・sha256凍結、注記者に生成結果・腕を見せない、独立二重注記で一致率記録、不一致はルールで機械的決定、**strip_tags(注記版)=旧腕B3原文をG0で照合(er019再利用分岐はJSON `fact_selection_evidence.json`の`selected_fact_brief_text`を読む[L336-339]のでJSONもsha256照合対象)**、旧4/新6の層別報告。→ ユーザー決定2により、全10記事を新仕様で再注記する(旧4の過去注記は使わない)に更新。結果は「人手注記の上限性能」と明記、Production化にはB3自動注記が必要(OPEN項目候補)。
- 論点6 判定線: EN STOP率は「3記事差以上**かつ**translation MAJOR×0.75」に厳格化(または記述指標へ格下げ)。分母は予定run数(各腕20)に固定しSTOPを独立カテゴリに。STOP記事の採用されなかった本文(`rejected_*.md`)もラベル対象(「出荷されなかった」別枠)。2-2(EN)/2-3(JA)の軽微二重計上を解消。2-1「1テーマでも悪化」は判定ではなく要確認フラグ。JAはAstra/Lunaの文体差で腕が推測できるため盲検不完全と明記。新規具体主張(ii)検出器(約¥0.2/本)を両腕のJA最終本文に指標追加。
- 論点7 停止・費用: 旧4テーマでresearch/B3のAPI呼び出し(web_search含む)を検出したら即停止(er019 L92分岐で台帳コピー漏れ時に黙って再実行される)。予算は各API段の前に横断集計(worker別台帳合計+実行中見込みの予約)で判定。astra単価はG1後にダッシュボード請求増分と照合、照合までガードは×1.5安全係数。G1カナリアにChecker 1 run(動的fixture `baseline_parsed=None`のruntime確認)と旧腕の再利用分岐でAdvancedまで通す確認を追加(約+¥8)。旧4完了後に中間チェック(フロー健全性のみ、新腕STOPが系統的[例4/4]ならFable停止判断)。TTSはG2から切り離し後回し。
- 論点8 R0復唱: 検出のみ(案A)。R0と最終JA(R2)の両方で検出し、改稿後も残るかを記録。残れば表現上の軽微として別枠。
- 費用影響(推定): 追加分約¥25〜30(B1除く)、B1上限3回で最大+¥105、総額推定約¥690〜900。上限¥1,000内。

## 成果物
1. `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md` を v2 に改訂(同ファイルを更新、冒頭に改訂履歴 v1→v2 と反映元[Opus論点番号・ユーザー決定番号]を記載)。前提作業一覧には (c)タグ残存修正(B1に必要)、B1回復経路、影の対照ログ(両腕)、G0照合拡張(JSON含む)、横断予算予約、×1.5係数、G1拡張、即停止条件追加、新規具体主張検出器、B3注記仕様 v1(委任_02成果物、ユーザー確認待ち)への依存、を反映。ゲート順を「B3注記仕様ユーザー確認→全10記事を新仕様で注記→G0→G1→G2」に更新。
2. `er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md` を v2 に改訂(§5-8確定=B1、判定線修正、分母固定、二重計上解消、要確認フラグ化、盲検限界、追加指標[人手介入必要率・初回JA_RECHECK率・(ii)検出器・shadow_stop])。
3. `docs/pm/opus_a_review_factlock_astra_e2e_01.md` を新規作成し、上記Opusレビュー要点を(Fableの転記として)保存。`docs/pm/OPUS_FINDINGS_LEDGER.md` に所見を追記(既存の採番規則に従いOF-095以降、形式は既存行に合わせる)。
4. SSOT追記(末尾追記のみ、全文読込禁止): `DECISION_LOG.md` 末尾にユーザー決定1〜3(本委任冒頭)とOpus条件Aレビュー実施・Fable採用判断を記録。`docs/pm/ACTIVE_TASK.md` 固定ヘッダを「委任_02(B3注記仕様 v1 作成中/完了)・委任_03=DESIGN v2(実行Go未、B3注記仕様のユーザー確認待ち)」に更新(既存のUDR-blocking・未回答報告の行は維持)。`docs/pm/REPORT_LEDGER.md` 1行追加。
5. 委任記録: 本委任文全文を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03.md` に保存、check_delegation_prompt.py結果を記録(FAILでも続行)。最終報告は `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03_result.md` と `docs/pm/RESULT_PACKET.md` に書く。
6. Git: 本委任で作成・変更したファイルだけを明示的に`git add`(`git add -A`禁止、委任_02のファイルは含めない)、commit、push。commit hashとraw URLを報告。

## 禁止事項
- API生成呼び出し一切禁止(¥0)。既存コード(`er0XX_*.py`)・Prompt・`CURRENT_SPEC.md`・`OPEN_ITEMS.md`の編集禁止(OPEN項目候補「B3自動注記」は報告に書くだけ、起票はFable判断後)。
- 未確認数値を確定値として書かない。

## 報告形式(result.md)
1. 成果物パス・commit hash・raw URL
2. v1→v2の変更点一覧(Opus論点番号対応)
3. 前提作業一覧 v2(各1行: 対象・見積行数・リスク)
4. 費用・時間見積 v2
5. 未確認事項・Fable判断が必要な点
6. 所要時間・API支出(¥0)

(保存注記: 本ファイルは委任文の保存コピー。上記「ユーザー決定」の番号は委任文内で1〜3だが、設計書・DECISION_LOG上は1回目の決定1〜5の続きとして決定6〜8と採番した。)
