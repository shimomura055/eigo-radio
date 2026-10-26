# PORT_01 移植方針と成果物(2026-10-26)
- 基準: `docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`(sha256 `13ef9085f625ea1618e63500793ffcbe959552c8ac0325484c623b1edb4fce79`、無改変でGit追加)。
- 実装: `user_test/selection_form_v3/index.html`(CSS・画面構成・DOM構造は参照から逐語流用: `<style>`は参照のstyleをそのまま+追加ルール3つのみ)、`form_logic.js`(参照の`counts/allowed/payload`を純関数化)、`data/articles.json`(index)、`data/monkeys_paw__b1b.json`、`data/ui_check_dummy__dummy.json`。
- 保持: 統計4枠(①/①+②/①+②+③/文法)、①②③チェック列、同一候補1区分、上限到達時の`.full`/`.locked`/disabled、解除常時可、文法チェック最大2・全文表示、自由コメント、ChatGPT送信(`chatgpt.com/?q=`、6000字超はコピー誘導)、コピー。
- 生成: `build_data_01.py`が`trial_result.json`から猿の手b1b候補をJSON化(read-only、API 0)。
- 全差異=`DIFF_01.md`。
