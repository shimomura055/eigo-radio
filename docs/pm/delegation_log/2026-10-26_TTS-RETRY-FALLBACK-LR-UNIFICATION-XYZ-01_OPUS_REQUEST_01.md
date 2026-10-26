## 依頼種別

Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A: 新しい処理フロー構造の実装前レビュー)。対象=TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01の設計(commit 6669925cf)。read-only。結論はあなたの返信本文で返す(ファイル書込不要。Fableが転記する)。

## 背景(ユーザー承認済み仕様、再承認不要)

2026-10-26 ユーザーがAPPROVED_FOR_PRODUCTIONとした統一仕様: 基本フロー ①通常Style→②同Style→**180秒待機**→③Fallback Style→(LRあり部位は)LR1回+同じ3回構成(最大6回・待機2回)。LRなし部位3回。KP英語のみ4回維持(通常2回→180秒→ENGLISH_LOCK 2回)。Zセリフ=ctx2回→180秒→従来Dialogue1回(LRなし)。Adv英語の③=短文Style新適用。Z冒頭英語=共通仕様へ是正(LRあり)。Adv KP英語解説=音声実在経路のみ、短文Style適合性を確認(不可なら同一Style)。日本語=日本語短文Style・LRなし。LR再入禁止(OPEN-376)・Style脱落(OPEN-312)解消。非ASR起因NGはLR不可なら無益処理回避(ただし待機・③は省略しない)。旧600秒・旧回数・LR後1回・「Adv技術エラー時のみ切替」は撤去。Voice/モデル変更はScope外。ユーザー原文=`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`。

## 読む物(この順)

1. `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/OPUS_REVIEW_REQUEST_01.md`(論点O-1〜O-8、Sonnetが作成)
2. 同dir `DESIGN_01.md`(共通核 er127: BLOCK_PROFILES 9 policy / cooldown_core / lr_recover depth guard / kp_two_stage / BlockProgress、loop型・stage型2アダプタ、D6 Std 6%減速の案A/B/C、Z ctx統合範囲)
3. 同dir `ROW_MAPPING_01.md`(49行→policy)、`REMOVAL_01.md`(R-01〜15/K-01〜09)、`SPEC_LEDGER_01.md` §6、`TEST_PLAN_01.md`・`EVIDENCE_PLAN_01.md`は必要箇所のみ
4. 必要に応じ現行コード: `er020_tts_retry_local_rewrite_01.py:57-93,739-815`、`er122_fz_ctx_policy_01.py:270-345`、`er019_family_x_audio_production_runner_01.py` M3 gate付近(685-743)、`er121_family_y_audio_01.py:650-790`、`er063_family_z_audio_01.py:985-1100`、`er109`(scope)。全文読込は不要、Grep→該当範囲。

## レビューしてほしい論点(O-1〜O-8に加えFableの追加観点)

- O-1〜O-8(依頼文のとおり)。特に:
  - **O-6/D6**(最大リスク): Std本文の6%減速+ASR再検証の外側ループ(OPEN-270 M3配管)を、案A「減速+再検証を各attemptの検証に取り込み外側ループ撤去」にしてよいか。承認済み仕様「減速後最終NGはLRなしHR(U-09)」との整合、chunk経路(er117、chunk単位3回構成)との整合、既存Regression(減速比・無音・Gate)への影響。案B/Cとの比較でどれを採るべきか結論を出す。
  - **O-2** depth guardによるLR再入禁止がresume(途中再開)・regeneration(`--regenerate-stage`)で破れないか。BlockProgressの保存粒度。
  - **O-3** Z ctx(`DialogueAttemptPolicy`、Opusレビュー済みE-1〜E-6)をcooldown_coreだけ共通化しstate machineは統合しない判断の妥当性。
  - **O-7** KP英語 2+2のENGLISH_LOCK直前180秒の位置、KP二段3複製→1統合の安全性(X/Y/Zで微差がないか)。
- **Fable追加F-1(OPEN-537との交差)**: 並行して「Family Y runner の`STYLE_PROFILE="default"`固定を、承認済み`fx_20261017`継承(`resolve_run_profile`)へ是正する」設計が進んでいる(FAMILY-Y-STYLE-PROFILE-FIX-01)。本設計は「Y STYLE_PROFILE不変」を前提に書かれている。統一核がStyle名/prefixを**自前で保持せず、呼出元が解決したprofileを①②(と③のFallback Style)へ透過的に渡す**構造になっているか。固定文字列や`default`前提が核に紛れ込む箇所があれば指摘。
- **Fable追加F-2(A/B/C凍結)**: `er109.current_scope()`でX/Y/Zのみ有効、A/B/Cはbyte同一という主張の検証方法(T-SCOPE golden)が十分か。scope判定が未設定の経路(ツール・test・旧runner)で誤ってX/Y/Z扱いにならないか。
- **Fable追加F-3(evidence)**: Lean 46case(保守約200円)の代表性。転写1語置換によるLR経路強制NGがProduction判定ロジックを迂回・改変しないか。U-03(QA単独NG)の再現方法。

## 出力形式

1. 結論(GO / GO with changes / NO-GO)と理由3行以内
2. 論点別判定表(O-1〜O-8、F-1〜F-3): 判定(妥当/要修正/要再設計)、根拠(ファイル:行)、修正指示(M-番号、実装前必須)または推奨(R-番号、任意)
3. D6の採択案と理由
4. 見落としリスク(設計に書かれていない重大点があれば)
5. 10行以内の要約

推測で断定しない。確認できない点は「未確認」と書く。