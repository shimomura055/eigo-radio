FABLE-DELEGATION-MARKER: KPQ-USER-DECISION-RECORD-委任_01-20261022

管理ID: KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01(OPEN-458)付随の記録のみ。費用0、Production/コード編集禁止。並行agent(KPQ 委任_02=配線中、AHO 委任_01=調査中)が共有SSOTを編集し得るため、`git status`→該当行再Grep→自分の行だけ編集→即commit。

## ユーザー原文(逐語。`docs/pm/delegation_log/2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_USER-DECISION-02.md` へ見出しから末尾まで一字一句保存)
# Key Phrase品質改善2項目・追加案へのユーザー決定

## 1. ユーザー決定

**① Key Phrase英語音声の数値・否定保護解除**
- 承認済み。予定どおりFamily X／ZのProduction Wiringを進める。
- 正式runtime検証、Regression、retry／fallback／Store再利用、SSOT／Git反映、Fable受入まで完了させる。

**② CMU辞書登録語のみをKey Phraseに選定**
- 承認済み。①と並行してFamily X／ZのProduction Wiringを進める。
- 同様にPRODUCTION_WIREDまで検証する。

**③ Azureの整形前テキストを併用する追加案**
- **REJECTED（正式不採用）。**
- 理由：Azureの個別現象に対する対症療法であり、根本解決にならないため。
- 将来の採用候補として保留するのではなく、不採用としてDECISION_LOGに記録する。
- 本追加案をProductionに配線しない。

## 2. 同一発音・異表記の包括対策

`one ⇔ 1`、`one's ⇔ 1's` を含め、**発音が同じなのに表記差だけでASRがNGになる問題は、別途指示済みの包括対策で解決する。**

- Key Phrase限定ではなく、すべての英語ASR判定を対象とする。
- Azure固有の個別処理ではなく、共通Validator／同音救済機構で解決する。
- 既存の数値正規化・同音救済仕様・過去Trialを確認し、重複や矛盾を防ぐ。
- Opusによる独立レビューを活用し、同種の取りこぼしを体系的に洗い出す。
- 発音が同一のものは表記・意味の違いだけでNGにしない。一方、異なる発音の誤PASSは認めない。
- 新たな判定範囲のProduction採用には、既存のPM Gateに従う。

## 3. 進行方針

①②のProduction Wiringと、包括対策の調査・設計・検証は、依存関係のない範囲で並行して進める。

包括対策の完成を理由に①②を不必要に停止させない。

Opusレビューで①②に重大な品質リスクが発見された場合は、必要な是正を行い、承認済み品質水準を守る。

**今回の（ア）／（イ）について、追加のユーザー判断は不要。決定済みとして進める。**

完了時は①②それぞれのProduction Wiring証拠と、包括対策の進捗・未決事項を分けて報告すること。

## 作業
1. 上記逐語保存(文字数・sha256)。
2. `DECISION_LOG.md`末尾にエントリ: 「2026-10-22 ユーザー決定: ③Azure整形前テキスト(lexical形)併用案=REJECTED(正式不採用。理由: Azure個別現象への対症療法で根本解決にならない。保留ではなく不採用。Productionへ配線しない)。①②は承認済みのまま配線継続。同一発音・異表記はASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01(包括対策)で解決、Production採用は既存PM Gate。」
3. `docs/pm/USER_DECISION_REGISTER_01.md`: Fableが提示した「a2型対処(ア)C1承認/(イ)①②のみ」の問いがKPQ 委任_02により採番済みかGrep(「a2型」「lexical」「C1」で検索)。あれば「ユーザー回答: ③REJECTED(2026-10-22)、包括対策へ」を追記。無ければ新番号で問い+回答(決定済み)を追加。
4. `OPEN_ITEMS.md`: OPEN-456 F3へ「C1はユーザー不採用(REJECTED)。one's↔1's等は包括対策OPEN(ASR-HOMOPHONE…)で扱う」を1行、OPEN-458へ「③REJECTED」を1行。`docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/AZURE_ITN_IMPACT_01.md`のC1行に「ユーザー不採用(2026-10-22)」注記。
5. `docs/pm/REPORT_LEDGER.md`1行、T-0保存 `docs/pm/delegation_log/2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_決定記録_委任_01.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: KPQ-USER-DECISION-RECORD-委任_01-20261022` 一致で確定)。
6. commit(自分のファイルのみ `git add <file>`)、secret_scan hits=0、`git push origin HEAD:main`。報告: 更新行、commit hash、raw URL(短く)。