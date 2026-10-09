# PREREGISTRATION_02: 追加Trial(委任_04、Sol・DeepSeek)の事前登録(実行前に固定、2026-10-09)

本書は追加Trialの評価LLMを1回も呼ぶ前に固定する。実行後の変更は禁止(変更時は理由と影響を記録)。前Trialの PREREGISTRATION_01.md の式・閾値を継承し、本書で追加・限定した点だけを記す。

## 1. 入力の不変宣言
- 入力は前Trialと同一で不変: `eval_items_01.json`(sha256 `d9f1201b0f398ac59559d90562fd6450e11c23015a6b58ee10a7727631c1adbd`)、`eval_prompt_01.txt`(sha256 `5644ff435f0aa0e70fd6ff0e0e8e55fc9da2bf33432878e86514afeb423f6a09`)。
- ケース、Fact、前後文、3分類(A/B/C)、盲検条件(評価LLMへ渡すのは case_id/fact/target_sentence/context_before/context_after の5項目のみ)、人間既知ラベルは変更しない。Checker判定は評価LLMに見せない。新ケース追加・Prompt改善はしない。
- 唯一のAPI仕様上の差分: DeepSeekはreasoning tokenが可視出力と同一予算のため `max_tokens` を6000→32000とする(er005 `_deepseek_call` の既存注記と同じ理由。プロンプト・ケース不変)。

## 2. モデル・rep
- `gpt-5.6-sol`(登録済み単価 input $5.00 / cached $0.50 / output $30.00 per 1M)、reasoning effort=medium(Lunaと同じ)、各2rep。temperatureはLunaと同じ扱い(拒否されたら指定なしで再実行し実効値をログ)。
- `deepseek-v4-flash`(`er005_research_model_ab_01.py` の `DEEPSEEK_MODEL` と同一ID)、各2rep。公式価格ページ(https://api-docs.deepseek.com/quick_start/pricing、2026-10-09取得)により `pricing_snapshot.json` へ登録: 標準(Peak、費用算出に使う) input miss $0.30 / cache hit $0.006 / output $1.20 per 1M、Off-peak(割引、記録のみ・費用算出に使わない) $0.15 / $0.003 / $0.60。公式脚注: 旧名 `deepseek-v4-flash` は引退済みで、リクエストは DeepSeek-V4.1-Flash で提供されFlash価格で課金される(= 前提として、評価者の実体は V4.1-Flash である。応答の `model` フィールドを全呼び出しで記録する)。
- 比較対象(再実行しない、既存結果): gpt-6-luna rep1/2、gpt-5.6-luna rep1/2。

## 3. 指標(前Trialと同一式)
- M1: K01・K02・K03 × 2rep = 6判定。Aが1つでも → M1=FAIL(REJECTED) / Aなし・B混在 → USER_DECISION_REQUIRED / 6判定すべてC → PASS。
- M2: K08・K09・K12 × 2rep = 6判定。B/Cが付いた判定が1以下かつC=0 でPASS、それ以外FAIL。
- M4: 同一モデルのrep1/rep2ラベル一致率(10ケース)。80%未満なら USER_DECISION_REQUIRED へ格下げ(前Trial 0-R.4と同じ保守側)。
- K11(sw-p2r2-01)は参考(期待=CまたはB、Aは見逃しとして報告、合否に使わない)。
- 判定不能(形式違反後も不正)は M1/M2 で外れ扱い。各(モデル,case,rep)で最初に有効なJSON応答を採用、再実行・差し替え禁止。形式違反は1回だけ再呼び出し。
- 併記: 10ケース×{gpt-6-luna, gpt-5.6-luna, sol, deepseek}×rep1/rep2 の横並び表、人間既知、Checker参考(正解扱いしない)、C検出数(K01/K02/K03/K11別)、両B件数、人間確認対象率(定義1=不一致のみ、定義2=不一致+両B)。ペアは sol × deepseek(rep別)。

## 4. 「改善」の定義(事前固定)
モデルXで「改善」とは、**M1で C判定数が gpt-6-luna(K01/K02/K03×2rep=6判定中 C=0)を上回る、または M1=PASS**、**かつ M2=PASS** のこと。(C判定数が1以上であってもM2がFAILなら改善とは言わない。)

## 5. 解釈規則(ユーザー指示に基づく固定)
- Solで改善 → 「モデル性能依存」(同系統でもモデル性能を上げれば重大を拾える)。
- DeepSeekで改善 → 「モデル/vendor依存」。
- 両方でも重大を安定検出できない(= 両方とも改善なし、またはM1がPASSしない) → 「LLMを主要Checker／客観評価器にする方式自体の現実性に強い疑義」。
- 成功しても「LLM Checkerが客観的に正しい」とは結論しない。n=10・重大3件(+参考1)での機能確認に限る。VALIDATEDでもProduction採用ではない。大規模Trialへ自動進行しない。
- 「安定検出」= M1の6判定すべてC(PASS)。一部のみCの場合は「部分的」とし、断定せず論点として分けて報告する。

## 6. Status割当(機械式)
- モデル別Status(併記): M2=FAIL または M1にAあり → REJECTED / M1がB混在(Aなし) → USER_DECISION_REQUIRED / M1,M2 PASS かつ M4≥80% → VALIDATED / M1,M2 PASS かつ M4<80% → USER_DECISION_REQUIRED(M4格下げ)。M1,M2 PASSかつM4を無視した場合の値も併記する。
- Trial全体: いずれかのモデルが VALIDATED → VALIDATED(評価器候補であり、Production採用ではない) / 全モデルが REJECTED → REJECTED / それ以外 → USER_DECISION_REQUIRED。
- 注: ユーザー指示の「いずれかのモデルでM1 PASSかつM2 PASS→VALIDATED」とM4格下げが衝突する場合は、M4格下げ後の値を主、M4無視の値を併記とし、どちらを採るかはFable判断とする。

## 7. 費用・STOP条件
- 上限: sol 2rep 合計 JPY 40、DeepSeek 2rep 合計 JPY 20。dry-run見積が上限を超える場合はSTOPして報告。実費 = usage × 登録単価(USD/JPY=160)。
- STOP条件: 上限到達 / 認証失敗 / 形式違反が全件の30%超。
- 限界: 前Trial PREREGISTRATION_01.md の§5・§6-5(n=10、HC-012偏重、K12はSonnet暫定等)を継承して結果報告に引用する。加えて、DeepSeekはthinking modeがデフォルトでtemperature等が無視される可能性がある(実効値をログ)。
