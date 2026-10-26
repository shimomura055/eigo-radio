## 管理ID

TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_05(限定解除のための実経路確認: JA部位の終端NG→HRQ 1行・Lock・STOPPEDを、正式runner+driver(判定注入ではなく**実ASR転写の1語置換注入**=委任_03と同方式)で1case実走。費用≤¥3)。並行Agent: FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01(`er063_*`編集)。あなたの所有=`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{EVIDENCE_JA_TERMINAL_01.md}`+`evidence_runs/`追記+driver、新run dir(`run_tru_ev_ja_01`、不追跡)、`docs/pm/delegation_log/2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_05.md`(+check.json)、`docs/pm/RESULT_PACKET_TRU5.md`。Productionコード編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: evidence補完(限定解除判定材料)。到達上限=EVIDENCE_COLLECTED。
- 禁止: Production hook/env追加(driver monkeypatchのみ)、HRなし宣言、禁止Git操作。
- 費用: 上限¥3(Guardrail、T-3定型どおり)。X Std日本語1 segment(①②→180秒→③、全NG→HR終端)=TTS 3+ASR≈¥1.1。
- 時間見込み: 約30分(待機180秒含む)。

## 固定ブロック

従来どおり。T-0: 委任文保存+check、結果1行。T-2: `TTS_EXECUTION_MODE=STANDARD`明示、差分再生成(`--only-segments`)確認、`--budget-jpy 3`。T-3: 上記。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_05.md` をN=695から順に試し、先頭「## 管理ID」+「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_05」のものを採用(同時刻に別委任あり、先頭一致必須)。

## 事前指定Read一覧

- `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{FOLLOWUP_01,EVIDENCE_X_01(X-Std-7)}.md`、`tools/`のdriver(委任_03のX-Std-7用。判定注入→**転写置換注入**へ変更: Primary/Secondary ASRの転写結果に1語置換を入れ、判定器自身にNGを出させる)
- `er127_tts_block_policy_01.py`: Grep `register_ja_terminal_hr` ±15

## 実施事項

1. X Std 日本語1 segment(X-Std-7と同じ部位)を`run_tru_ev_ja_01`で、転写置換注入により①②③全NG→終端。観測: HRQ 1行(重複なし)、Lock=HUMAN_REVIEW_REQUIRED、STOPPED、待機1回180秒、TTS 3回、`register_ja_terminal_hr`経由か判定器経由かの記録(両方でも1行)。stop_scope_check事前実行。
2. `EVIDENCE_JA_TERMINAL_01.md`に結果、`EVIDENCE_01.md`の必須12項目表に参照caseを追記(HRQ一本化行)。
3. 費用実績。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_05.md --json-out ...\_check.json`
- `py tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 --run-dir <run_tru_ev_ja_01> --out docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/stop_check_ja_01.json`
- 正式CLI(委任_03 X-Std-7の起動コマンドを踏襲、全文記録)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- commit message: `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_05: JA終端NG→HRQ1行の実経路evidence(転写置換注入、実費¥X)`。trailer: `Delegation: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/05`。push。

## 報告

`docs/pm/RESULT_PACKET_TRU5.md`: (0)T-0、(1)観測結果、(2)費用、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)SSOT文案(OPEN-540限定解除)、commit hash・raw URL。末尾3行要約。