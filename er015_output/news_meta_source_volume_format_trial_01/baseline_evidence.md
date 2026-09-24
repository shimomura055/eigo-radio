# Baseline確認(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01, Step 0)

## 前回Baseline(条件2)の入力件数・形式(根拠付き)

- 根拠ファイル: `er015_news_iterative_entertainment_trial_02.py` MATERIAL_A定数(行94-99)、`docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md` 2-B節(行41-62)
- Source数: 1件(URL: https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025)
- 文数: 2文(句点「。」区切り)
- 文字数: 209字
- 粒度: 元記事本文の要約(直接引用ではなく2〜3文への要約パラフレーズ)
- 形式: 段落形式のプレーンテキスト(箇条書きではない)、`[ニュース]`欄へ挿入

### 逐語(MATERIAL_A、条件2でそのまま再利用する)

```
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

## Prompt(P7)・Revision指示・model/effort・連鎖方式の特定

- Original Prompt(P7)本体: `er015_news_original_baseline_repro_01.py` R0_PROMPT定数(逐語、テーマ行のみ差し替え)
- テーマ行: `テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている`(trial02 THEME_LINE["A"]と同一)
- developer message: `あなたは日本語のニュースを分かりやすく面白く伝える書き手です。`
- R1指示(逐語): この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。
- R2指示(逐語): この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。
- model: gpt-5.6-luna / effort: high
- 連鎖方式: previous_response_id(trial02 chain.json Article A: {"chain_method": "previous_response_id", "stages": [{"stage": "original", "response_id": "resp_04020df138cfa5d1006ab47ee74a4087d084bd71c730cfe519", "model": "gpt-5.6-luna"}, {"stage": "r1", "response_id": "resp_04020df138cfa5d1006ab47efb01e487d0970d151832e733bd", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}, {"stage": "r2", "response_id": "resp_04020df138cfa5d1006ab47f080abc87d0b978604a1444e679", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}, {"stage": "r3", "response_id": "resp_04020df138cfa5d1006ab47f14817487d097bb6c1f31dcd299", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}]})

## 判定

STOP該当なし。条件2はMATERIAL_Aを逐語再現することでBaselineを再現する。