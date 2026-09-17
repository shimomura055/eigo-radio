# 委任文: USER-TEST-SCRIPT-READABILITY-TRIAL-01

## 管理ID

`USER-TEST-SCRIPT-READABILITY-TRIAL-01`(**Trial**。Production正式採用ではない)。報告は`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_TRIAL_01.md`(新規、★★★★報告ここから/ここまで)。一時ファイル`docs/pm/ACTIVE_TASK_SCRIPT_READABILITY_TRIAL_01.md`。現在main=origin/main=`b441ecda`(要fetch確認)。**並行Agentなし。外部API/TTS/LLM呼び出し0**(日本語訳はSonnet自身が作成する。外部LLM APIは呼ばない)。到達Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`のみ(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進めない)。

## 目的

ユーザーテスト視聴ページのスクリプト理解しやすさ改善を、Personalized News 1記事ペア(Standard A2/Advanced B1)でTrial: (A)本文中のKey Phrase該当箇所ハイライト、(B)スクリプト下部に構造対応付きの日本語訳セクション追加。

## 対象(canonical、読み取り専用・変更禁止)

- Standard(A2): `er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`
- Advanced(B1): `er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/`
- `user_test/unified.html`、`user_test/articles_2026_0918.html`、Google Sheet、canonical URLは変更禁止。

## Trial用コピー

新規dir `user_test/trial/script_readability_01/`に: (1)`unified_trial.html`、(2)`personalized_news_a2/translation_ja.json`・`personalized_news_b1/translation_ja.json`、(3)必要ならKey Phrase一致結果JSON。音声(mp3)は複製しない。

## Trial仕様A: Key Phraseハイライト

exact match優先→normalized match(大小文字・句読点・引用符・ハイフン/スペース差・全角半角のみ)。曖昧一致は実装しない。DOMテキストノード内で該当範囲を`<mark class="kp-hl">`で包む。

## Trial仕様B: 日本語訳セクション

Standard: 本文和訳+既存日本語Comment再掲(グレー表示)。Advanced: 本文和訳+Comment1-4和訳(Sonnet自身が翻訳)。`translation_qa.json`にセルフチェック表を保存。

## Browser確認

Playwright、rawcdn.githack Trial URL、PC 1280x800/スマホ390x844、screenshot+e2e_result.jsonを`docs/pm/closeout_136_e2e/script_readability_trial_01/`へ。

## STOP条件・対象外

canonical不一致/曖昧ハイライト等はSTOP判断。音声再生成・TTS変更・Script/Comment/Key Phrase本文変更・記事構成変更・10記事一覧反映・他9記事展開・canonical更新は対象外(禁止)。

## SSOT/Git

DECISION_LOG.md/OPEN_ITEMS.md/ARTIFACT_REGISTRY.mdへTrial行追加。明示add、git add -A禁止、mp3/wav追加なし、fetch→merge、trailer `Task-ID: USER-TEST-SCRIPT-READABILITY-TRIAL-01`。

## 報告(21項目)

Trial最終Status/対象/canonical path/Trial copy path/Trial URL(2件)/Key Phrase総数/ハイライト成功数/unmatched/Standard日本語訳結果/Standard Comment再掲結果/Advanced日本語訳結果/Advanced Comment翻訳結果/PC・スマホBrowser確認/音声再生への影響/元canonical無変更証拠(sha256)/Git commit/共通化課題/USER_DECISION_REQUIRED事項/Production反映は未実施。
