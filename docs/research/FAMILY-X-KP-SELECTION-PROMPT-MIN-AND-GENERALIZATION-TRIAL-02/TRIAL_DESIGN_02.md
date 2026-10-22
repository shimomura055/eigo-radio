# TRIAL_DESIGN_02: Family X Key Phrase 最小化Prompt 5モデル比較 + 一般化工程分離Trial

管理ID: FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01 / 2026-10-22 / 性質=比較Trial(Trial専用実装。Production無変更、Production採用は未承認)
ユーザー原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md`(4,525文字、sha256=`1f76fcb78c63e6ff02fae75ee877df17d97b47abf506dfcc3dea91bc8d17007c`)

## 1. 要求(ユーザー原文§1〜§7)と実装の対応表(開始前チェック)

| 要求 | 実装・確認 |
|---|---|
| §2 前回と同一の7記事x Standard/Advanced=14本文、再生成なし、版・ハッシュ一致確認 | `er098_output/kp_six_model_trial_01/inputs/manifest.json`の14本文を再利用。run前に`copy_sha256`をassert(14/14一致)、別途元`article.md`のsha256も14/14一致を確認。全70runの`article_sha256`=manifest値 |
| §3-1 5モデル(Luna/Gemini3.1 FL/Gemini3.5 FL/Haiku5.5/Sonnet5.5)、70選定、返却model ID確認、モデル別最適化・品質再生成なし | `er101_..._common.py` `MODELS`。返却model IDを全70runで記録・一致(Excel「費用・実行条件」)。再生成なし(技術的再試行のみ。1件) |
| §3-2 Prompt固定、受け渡し調整は事後報告 | `inputs/prompt_fixed.txt`(sha256=6a5d2052...)を一字一句固定。調整=KP6Mと同じ『\n\n---\n\n【記事本文】\n』+本文の後置のみ。prompt_sha256は全70run同一 |
| §3-3 評価基準・評価者を可能な限り維持+最小化観点を追加、同一尺度でない数値は優劣比較しない | 評価者=gpt-6.1-sol+claude-sonnet-5-5(前回同一、選定元と異系統=主評価)。V/E/Nは前回と同文言。G(一般化)は新Promptに一般化条項がないため除外。追加観点C(学習点の明確さ)/U(不要語除去)/S(最短形)/X(短縮の不自然さなし)を別スコアで採点(前回なし=合算しない) |
| §3-3 例示3件の追跡 | `summary.json` `example_tracking`、Excel「T1 品質評価」下部 |
| §4-1 Luna出力をBeforeとして一般化、再選定禁止、低コスト1モデル、ID・理由・料金記録 | 一般化モデル=`claude-haiku-5-5`(理由: KP6M遵守100%・安価[0.10/0.50 USD per 1M]・選定元Lunaと別系統)。単価出典=`er101_..._common.py`経由`er098 common PRICES`(公式pricingページ2026-10-22取得, sha256記載) |
| §4-2 一般化Prompt固定、対応追跡 | `inputs/gen_prompt_fixed.txt`(sha256=43635944...)。1本文=1呼出(5件)。出力は`{no,before,after,reason}`JSON。before一致・件数・番号一致を機械検証(70/70一致、再選定0) |
| §4-3 Before/After評価 | 評価者2系統が4項目PASS/NG+要変更/適用漏れ/過剰変更/意味変化/追加語。機械=5語以内・追加語検出。変更件数は加点しない |
| §5 Excel | `KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx`(6シート: T1比較/T1品質評価/T2 Before-After/T1検証詳細/T2検証詳細/費用・実行条件。ユーザー指定の5シート構成をT2検証詳細を分けて調整) |
| §6 並列・費用 | Trial①は5モデル並列(provider別)、評価はT1/T2・2評価者を同時実行。選定費/一般化費/評価費を分離記録。Cap JPY300内 |
| §7 報告順 | TRIAL_RESULT_02.md |

## 2. 機械検証規則(前回の検証ロジックをimport、無改変)
- 語数=スペース区切り。5語以内。本文一致=厳密連続部分列(大小文字・引用符・末尾句読点のみ正規化)。
- 新Promptには一般化条項がないため、前回のplaceholder wildcard照合は使わない。placeholder(~/A/B/someone等)が出た場合は`NG_PLACEHOLDER_DEVIATION`(Prompt逸脱)として別記録。活用形のみ相違は`NG_INFLECTION_ONLY`。
- 自己申告語数不一致は違反とせず別記録。厳格合格=5語以内+厳密一致+重複なし。
- 抽出(パース)は前回と同じヒューリスティック。モデルが自分で取消・修正して最終提示した4件を手動補正(`er101_..._validate.py` PARSE_OVERRIDES/PHRASE_OVERRIDES/FINAL_LISTS。TRIAL_RESULT_02.md 8節に列挙)。

## 3. Trial②の評価定義(事前固定)
- needs_change=汎用化のために変更すべき要素(固有名詞・特定対象への依存/学習上原形で示すのが自然な活用形/単複/this・its等の文脈依存語)があったか。原形化を要変更に含める点はユーザー原文(§3-3・§4-2の『原形化』『agreements→agreement、caused→cause』)に基づく。
- 主評価=2評価者平均(両者ともHaiku出力と異系統)。集計は「両者」「いずれか」を併記。
