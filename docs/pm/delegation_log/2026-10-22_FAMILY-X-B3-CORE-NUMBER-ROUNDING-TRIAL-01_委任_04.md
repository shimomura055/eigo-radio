FABLE-DELEGATION-MARKER: B3RD-FABLE-VERDICT-委任_04-20261022

# 委任(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_04: Trial2のFable独立評価・分類の記録のみ。API 0・JPY0・コード無変更)

## 0. 運用ルール
他agentは現在動いていない。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。対象ファイルのみ明示add、secret_scan `--staged` hits=0、push=`git push origin HEAD:main`。一時ファイル(`ACTIVE_TASK.md`/`RESULT_PACKET_*.md`)はforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er0XX_output/*`)を混ぜない。

## 1. 記録するFable判定(逐語で`docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/TRIAL_RESULT_02.md`の項目10「Fable独立評価」欄へ記入。改変・補強しない。事実関係に明らかな誤りがあれば記入せず報告)

---
**Trial2の分類: `VALIDATED`(条件付き)。管理IDのStatusは引き続き`USER_DECISION_REQUIRED`(UDR #135を更新)。** `APPROVED_FOR_PRODUCTION`ではなく、Production採用・配線はユーザー正式承認が必須。

**何が確認できたか(Fable)**
- Luna化: 判断品質はSolと同等(誤りの型も同じ)、1件あたり費用約97%減(JPY3.65→0.12)、時間約74%減。Prompt・判定基準・V1〜V7は無変更。探索停止は妥当。→ 目的1は確認できた。
- N増しFact整合: 独立18記事・Fact 75・中核数値71(人工fixture 0)で7カテゴリ充足。Writerまで到達した「丸めで意味が変わったNG」0、停止0/12、retry 0/12、Risk Flaggerの丸め由来flag 0/27、旧LDC changed_number 0、注入テスト7種はRFが7/7検出。B3・Ledger・storylineのshaは全arm一致、Promptの差分は追記のみ、概数0件の記事ではPromptがbyte一致。→ 「丸めで量産が頻繁に止まる」兆候はない。

**留保(Fable)**
1. 判断段の実害候補1件: `14(原告数)→約10`がV1〜V7を通過した。相対誤差約29%で、Writerが使えばFactの規模が変わる。提案V8(相対誤差10%上限)は保存判断90件で6件を阻止し正しい丸めの阻止0。**採用する場合はV8を必須条件とする**(基準の引下げではなく追加の安全網)。
2. 正解率の読み方: 事前登録のstrictラベルでは54〜56/63(過剰丸め6〜9)。承認済み既定(小数%は概数が既定、`er003_v1_n3_01_evidence_compression_editor.py:121-131`)へ整合させた事後ラベルv2では51〜54/54。v2は事後の再ラベルであり、粒度の正解はユーザー定義(D3)に依存するため、v2の数値を単独で品質証明に使わない。
3. 価値の大きさ: 指定概数をWriterが実際に使ったのは7件中2件。聞き取り評価は未実施。効果は限定的で、採用の是非は原価ではなく「聞き手向けの数値表現を品質として求めるか」の判断。
4. 標本: Writer段は4記事・各arm 1〜2サンプル。Control同士でもRF flag 14↔25、LDC 2↔15と揺れており、Human Review増分の検出力は低い。0/12は「頻繁な停止がない」ことの弱い証拠であり、統計的証明ではない。
5. 無音の品質リスク: `【概数表記】`タグは`TAG_LEAK_RE`/`assert_no_tag_leak`の対象外(実関数で確認)。漏れればTTSがそのまま読む。実測漏れ0だが、**採用時はS5(MARK_RE/TAG_LEAK_REへの追加)を必須条件とする**。
6. 判断LLM(Luna)とRisk Flagger(Luna系を含む)の同系列バイアスは残る。注入テストで検出7/7だが、`11件→約10件`は信頼度0.30と低い。

**費用(出典付き)**: 本案件実費JPY217.39(judge Sol 3.80/Luna 11.67、Phase2 12arm 192.0、注入テスト9.93。案件見積300円以内、設計時見積210〜230)。`daily_dev_cost_01.py --date 2026-10-22`のadopted値はJPY213.61で、本日の実費合計(本案件217.39+PNMH Trial 6.32=223.71)と約10円の差がある(集計範囲の違いと推定、未確認)。日次1,000円以内。

**Fable推奨(Production採用判断=ユーザー)**: 前回(#135)の推奨「保留」の主因だった原価(+4〜6%)はLuna化で+0.17%まで下がり、量産停止の兆候も観測されなかった。したがって推奨を**「(ア)採用方向で最小仕様を確定」へ更新**する。条件=V8必須・S5必須・粒度方針を承認済み既定(小数%は概数)+相対誤差10%以内+既に概数の値は再丸めしない、で固定・judge=Luna low。採用方向が選ばれた場合、Production実装前にOpus独立レビュー(11-3条件C、S1〜S7+V8+S5の設計)を入れ、その後に実装・Regression・runtime evidenceへ進む(設計レビューまでは追加費用0)。価値が限定的(使用2/7)であることを踏まえ「(イ)保留」も合理的であり、ユーザーの品質定義に従う。
---

## 2. SSOT
- `OPEN_ITEMS.md` OPEN-437: Status=`USER_DECISION_REQUIRED`(Trial2=`VALIDATED`条件付き)。履歴追記(Fable判定2026-10-22、実費217.39、D1〜D5、推奨更新)。3,000字超なら`OPEN_ITEMS_HISTORY.md`へ切出し。
- `docs/pm/USER_DECISION_REGISTER_01.md` #135を更新: 選択肢=(ア)採用方向で最小仕様確定(条件: V8・S5・粒度方針固定・Luna low、Opus条件Cレビュー後に実装)/(イ)保留。Fable推奨=(ア)(前回(ア)保留からの更新、理由=原価+0.17%・停止0/12)。付随判断=D1規則(5)例外化、D3粒度方針、D5タグガード、V8採否、D4価値判断。
- `docs/pm/REPORT_LEDGER.md`に行追加。DECISION_LOG・CURRENT_SPECは書かない。
- T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_04.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: B3RD-FABLE-VERDICT-委任_04-20261022` を含むAgent tool_useの0始まり通番、240前後)。
- commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_B3RD4.md`へ短い報告(変更ファイル・commit・raw URL・RESULT_PACKET 4行・JPY0)。