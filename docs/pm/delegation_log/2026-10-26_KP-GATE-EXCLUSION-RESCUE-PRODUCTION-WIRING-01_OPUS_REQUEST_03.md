## 管理ID

KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 OPUS_REVIEW_03(PM_GOVERNANCE 11-3 条件A: Key Phrase候補生成のX/Y/Z共通核へ「Gate除外候補の救済フロー(検出→修正→再検査→候補登録)」を既定ONで加える設計の、Production配線前の独立技術レビュー。read-only)。

## 性質/到達上限Status/禁止事項

- 性質: 独立技術レビュー(設計の穴・誤受理リスク・一貫性・fail-closed性の指摘)。到達上限=所見(問題なし/要修正[修正案]/ユーザー判断要)の提示。編集・実行・API不可(Read/Grep/Globのみ)。
- スコープ: **変更部のみ**(`OPUS_REVIEW_REQUEST_03.md`に抽出済み)。既存レビュー(`KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md` M1〜M6/R1〜R4、`…DESIGN-02/OPUS_REVIEW_02.md`)で結論が出た論点は再レビュー不要(設計がそれらに従っているかの確認は可)。
- 費用/日次: JPY0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 本レビュー依頼文はFableが`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_OPUS_REQUEST_03.md`として後続委任で保存させる(あなたは保存不要)。
T-2: TTSなし。

## ユーザー承認(原文抜粋、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_USER.md` §2)

「時制・活用形 | 本文との対応を確認でき、正しく原形化できる場合は救済」「慣用句 | 助動詞等の機械的判定で不当に除外される自然な慣用表現を救済」「5語以下 | 制限維持。6語以上を意味のない短縮で救済しない」「本文にない語の追加 | 不採用」「発音辞書未登録語の分解救済 | 不採用」「既存仕様に反する実装条件4件 | 承認済み仕様に合わせて是正」「個別の5表現だけを例外登録するのではなく、同じ原因を持つ候補を救済できる一般的な仕組みとすること。」「品質Gateを緩和して不適切な候補を通すのではなく、本文との照合、適切な正規化、自然な慣用表現の判定によって救済する。」「Humanが明示的にNGとした候補は、救済処理によって復活させない。」「過去に提案された「27件の固定例外リスト」は、実装方式として正式承認されたものではない。」§3「Human Reviewあり／なしの両経路との整合」「retry／fallback／regeneration／resumeでの救済結果の一貫性」。

## レビューしてほしい重要論点(これ以外は不要。ただしあなた自身の追加探索は妨げない)

1. **慣用句の一般機構の誤受理リスク**: Wiktionary English idioms見出し(10,674件、sha固定・fail-closed)+構造条件(助動詞始まり・be系除外・倒置疑問文/名詞主語の完全文/中身語のない断片を除外・主語`it`のみ除去)+除外表10件。辞書全体で構造条件に合う116件、現行guardの判断が変わる25件(`idiom_exception_listing_01.json`)。この25件に学習素材として不適切なもの(卑語・古語・ことわざ断片・文脈依存で意味が立たないもの)が含まれていないか。構造条件の抜け(例: `can't`のASCII/curly差、`cannot`、`won't`、否定縮約の正規化、所有格スロット`one's`の扱い、2語以上の主語除去を許さない点の妥当性)。辞書更新時のsha再ピン手順が運用上fail-closedを壊さないか。
2. **HRなし経路でのauto_eligible条件(β)**: canonicalization段の救済(M1/revert)は「gloss強制再整合成功 かつ QA 12項目再判定PASS」のときだけ`auto_eligible`維持。QA再判定は**新Promptを作らず承認済みfulltext canonicalization prompt/schemaに`display_phrase=救済後key`を渡して再利用**し、返却keyが不一致なら`NOT_REJUDGED`=HRのみ採用可。この再利用方式が(a)承認済みPromptの意味的流用として妥当か(sha固定Promptの入力を変えるだけで「Prompt変更」に当たらないか)、(b)LLMが救済後keyをさらに書き換えて返す場合の扱い、(c)選定段の救済(D1再アンカー・慣用句核)は通常canonicalizationを通るので追加条件なしとした点の妥当性。
3. **既定ON+kill switch(`EIGO_KP_RESCUE=0`)と配線4箇所(H1 `er105:941 contains_finite_aux_role_based`/H2 `er105 validate_and_resolve:225`/H3 `scaffold:475 run_key_phrase_canonicalization(rescue=)`+`er119:162`/H4 `er119:305`+`rv:829`)**: (a)A/B/C旧経路(`_is_ft=False`)への波及がないか、(b)H1はvalidatorと選定段の両方が使う関数=救済例外が「最終Gateの引数同一性」を崩さないか(M6の趣旨)、(c)環境変数kill switchがProduction既定動作の外部依存を増やす点の是非(flagの既定値・読取り箇所・testでの固定)、(d)Z限定のSRC D1・人称整合、Yの`er121_family_y_runner_01.py:540-569`経路が救済後itemに通常どおり適用されるか。
4. **retry/resume一貫性**: 救済メタを候補ファイルへ永続化し`candidates_sha256`に含める、resume時は再計算せず読み戻す、救済成功itemは`gate_dropped`に数えない(M5変更)、救済失敗のみOPEN-456 F1累積。(a)外側retry(`n_auto<3 and gate_dropped`)の発動頻度が意図せず下がり、結果として「救済形だが品質の低い候補で埋まる」方向に働かないか、(b)resume時に辞書sha/validator版が変わっていた場合の扱い(読み戻し優先で古い救済結果が残るのは許容か)、(c)既存run(AI島`run_ai_01`等)のHR候補不変の保証がtestで足りているか。
5. **Fable解釈の妥当性(事実確認のみ)**: 「6語以上を意味のない短縮で救済しない」を「短縮救済は一切しない(意味が狭まる短縮も不採用)」と解釈し、`too soon to wave a flag`は除外のままとした。この解釈が承認文の範囲内か、拡大解釈(ユーザー判断要)か。
6. **見落とし**: 量化詞限定詞guard是正(`_QUANT_DET`/`_quant_follow_ok`、実データ133候補で新規受理0)の副作用、縮約形R5(ASCII `can't`すり抜け/curly拒否)を配線と同時に是正しない判断の是非(OPEN起票で後続とした)。

## 事前指定Read一覧

- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/OPUS_REVIEW_REQUEST_03.md` 全文
- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/DESIGN_03.md` 全文
- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/IDIOM_LEXICON_01.md` 全文、`idiom_exception_listing_01.json`(25件)、`data/kp_idiom_lexicon_01/denylist.txt`・`meta.json`
- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/SPEC_LEDGER_01.md` 全文(採用表→実装対応、Fable解釈)
- `er125_kp_rescue_production_01.py` 全文(新規module)
- `er125_kp_rescue_production_test_01.py`: Grep `def test_` → 一覧、関心箇所のみRead
- `er105_kp_fulltext_selector_01.py`: Grep `_QUANT_DET|_quant_follow_ok|contains_finite_aux_role_based|def validate_and_resolve` → ±30
- `er119_kp_candidates_01.py:150-175,295-345`
- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`・`…DESIGN-02/OPUS_REVIEW_02.md`: 自分の既存所見の再確認用(必要箇所のみ)

## 期待する出力

論点1〜6ごとに「問題なし/要修正(修正案・最小変更)/ユーザー判断要」と根拠(ファイル:行)。最後に「Production配線へ進んでよいか(条件付き可の場合は条件)」を1行で。指摘にはID(OF-KPRW-M1…/R1…: M=配線前必須、R=推奨)を付ける。