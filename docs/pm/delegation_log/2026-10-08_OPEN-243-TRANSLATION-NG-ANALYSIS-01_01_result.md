# OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_01 result (2026-10-08)

Status: ANALYZED(既存artifactのみ・API支出 ¥0・SSOT/Production/git無変更。`RESULT_PACKET.md`/`ACTIVE_TASK.md`は未編集)
成果物(`er052_output/open243_translation_ng_analysis_01/`): `ANALYSIS_01.md`(全件表・集計表・傾向)、`COUNTERMEASURES_01.md`(対策案)、`items.jsonl`(74行=EN所在の盲検判定66+保留8、`event_id`付き)。再現用script・中間json(`_*.py`/`_*.json`)も同ディレクトリ。
check_delegation_prompt: 委任文を `..._01.md` に保存し実行 → **FAIL**(必須セクション不足: 事前指定Read一覧/Grep一覧+追記位置/実行コマンド全文/文末の短い報告(RESULT_PACKET)指示、固定ブロックE-1/D-1/G-1/F-1。委任文が標準フォーマットでないため)。FAILのまま続行。結果: `..._01_check.json`。
所要時間: 約30分(16:48 保存〜17:15)。

## 件数(出典はANALYSIS_01.md)
- EN所在の盲検NG判定 66件(Trial A 28 / Trial B 38。重大4・軽微62)→ 同一文を束ねた事象 53(翻訳段由来22・翻訳で増幅4・JA由来27)。判定は手動(JA R2対応文を突合)。保留のEN関連8件は算入せず別掲。
- EN deviation checkの origin=translation 指摘 48レコード(同一世代・同一文で35件。MAJOR 21要約+11本文、MINOR 3)。全79 deviation中、`changed_actor`=true は12件で全て ja_source。
- Checkerゴールドセット(T-B)・OPEN-233 REPORT でJAに無くENで生じた重大: PAST-ai-p2r1-02、PAST-hormuz-T0M0r2-01 の2件(Checker検出: 前者 6-luna 2/2・5.6 0/2、後者 0/4)。
- O3(本日E2E): run_01 STOP = 「## In one line」1文の `changed_scope`(MUSE-HC-07、AI phone feature全体へ範囲拡大)が2回連続MAJOR。run_02は deviation 0件で完走。

## 主要傾向(翻訳段由来/増幅 26事象、重大2・n小)
- 末尾「In one line」要約に集中: 9/59行(15%) vs 本文 17/1,505文(1.1%) = 約13倍。JA本文に対応文が無く、英語記事のみから別callで生成(台帳もJAも渡らない)。
- EN STOP 8世代は全て要約。要約MAJOR 14世代中6のみ再生成で回復(本文MAJORは10/10回復)。コード上、要約の再生成には must-fix が渡らない。
- 本文は「日本語の数無標」8事象(幹部→executives 5、米政府機関→agencies 2、従業員→employees 1)。JA「副社長」9記事は誤り0、「幹部」9記事は6記事が複数形。主体は主語省略の誤補完(Meta was asked)等。
- 検出: EN deviation check 5/26事象(全MINOR、MAJOR 0、うち3つはorigin=ja_source)、Checker候補化 14/24、書き換え4。どちらも候補化しない10/24。重大2件のうちEV-25(Meta was asked)は両層素通り(EN check=MINOR/changed_number、Checker=QUALITY。Stage 1が別事実HC-010で候補化)。第2意見はEV-26・EV-28では救済側に働いた(格下げが原因ではない)。
- モデル世代・Standard(A2)・タイトル・テーマ差: n不足(Fact Lock cellが交絡)。盲検判定者間の一致は27%(件数は下限)。

## 対策案一覧(優先順位なし。詳細・費用換算・検証方法は COUNTERMEASURES_01.md)
A 翻訳入力に台帳+保持指示(M) / B 要約の生成方式見直し(B1停止・B2入力にJA+台帳・B3 JA側生成・B4要約専用検査) / C JA↔EN決定論チェック(数・時制、¥0、M) / D EN deviation checkの`changed_actor`定義拡張・origin判定・専用質問(M) / E Checker Stage 1入力の補強(ENのMINORを引継ぎ、M〜L)。第2意見の格下げ不可化は根拠が成立せず、床の復活は2026-10-06承認決定の覆し / F タイトル・用語固定(n不足) / G1 JA側で集合名詞を台帳表記へ(上流) / G2 要約再生成へmust-fix受け渡し(S) / G3 translation起源MINORのtelemetry追加(S)。

## 未確認事項
- 費用はトークン実測×確認済み単価(gpt-6-luna $0.1/$0.5 per 1M、USD_JPY 160)の換算で、追加call実測ではない。台帳単体のtoken数は未測定。
- 要約再生成にmust-fixが渡らないことが回復率の低さの原因かは未検証(仮説)。
- Trial A/Bのchecker実行が `FLOOR_MODE=number_only` だったかはdumpに出力が無く直接未確認。
- 各案の効果量・Standard(A2)の翻訳段NGは未測定。Opus独立レビュー(条件A該当の可能性)はFable判断。
