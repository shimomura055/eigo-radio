# BUDGET_PLAN_02: 委任_02 runtime evidence見積(X/Y/Z各2レベル)

2026-10-26 / 本委任(委任_01)の実費=JPY 0(API 0)。当日既使用約552円/残約448円(委任文)。見積は7-7(承認済みScope内の案件見積300円以下はAI自律)の範囲内。

## 1. 構成
| 区分 | 内容 | 見積 |
|---|---|---|
| A. 正式初回Production経路のfresh run | X・Y・Zそれぞれ **1記事 x 2レベル(a2/b1b)** = 6 level-run。`generate_candidates`(call1 + call2 + canonicalization + gloss + Redundancy QA)をhook有効で実行。Standard/Advancedの差は後段(KP段は共通)のため、KP段は各level-runで1回、Std/Advは同一候補から派生 | 約3〜4円/level-run x 6 = 約18〜24円 |
| B. 救済発生分の追加費用(自然発生) | 該当は**約0.4件/level-run**(DESIGN-02実測)。gloss強制再整合 0.53〜0.56円/件 + QA再判定 0.5〜1円/level-run(該当時のみ) | 6 level-runで約1〜3円 |
| C. 救済の確実な発動確認(replay) | 自然発生は稀なため、既知の事例(`rose above`/`held out`型のM1・`catch their interest`型のD1・`it can't be helped`型の慣用句核)の**凍結したLLM応答/本文**を正式経路の関数群(H1〜H4)へ流し、gloss強制再整合とQA再判定だけ実LLMで1回ずつ実行(選定・canonicalization LLMはfixture=API 0) | 約2〜4円(gloss 0.55 x 3〜4件 + QA 1〜2 call) |
| 合計 | | **約21〜31円**(委任文の見積20〜30円と一致。上限の目安=50円で超過見込みならFableへ報告) |

## 2. 量産原価への影響(70円/記事セット目標)
- 救済が発生しないrun: 追加費用0(API呼出は従来と同一。`rescue`対象0件ならgloss/QA再判定を呼ばない)。
- 救済が発生するrun: 候補1件あたり約0.5〜1円(gloss再整合)+ level-runあたり約0.5〜1円(QA再判定、バッチ1 call)。期待値 約0.4件/level-run -> **約0.3〜0.6円/level-run、記事セット(a2+b1b)あたり約0.6〜1.2円=70円目標の約1〜2%**。救済により外側retry(1回あたり候補生成全体の再実行)が減る場合は差し引きで原価減の可能性(未測定。evidenceで救済あり/なしのretry回数を記録)。
- 追加のモデル利用なし: QA再判定は承認済みcanonicalization prompt/schemaを再利用(モデルは`routing.SUPPORT_MODEL`=現行と同一)。使用モデル名・最新性・routing証跡は委任_02のevidenceに記録(actual model_id)。

## 3. 実行条件(委任_02)
- 作業開始時と有料run前に`tools/stop_scope_check_01.py`を実行(rc=3なら停止)。
- 再起動は委任文が明示許可した回数のみ。Z完成段の再実行は`--stages provision_shell,gate,assemble,pages,page_verify`を1起動で指定(OPEN-480)。
- 既存音声の再利用キャッシュ・差分再生成の可否確認(T-2追記)は、KP段のみ(TTSなし)の本evidenceでは不要。後段TTSが走る場合のみ実施。
