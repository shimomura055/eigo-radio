# 委任文 ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_02a(再実行、2026-10-15)

## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01`(AUW)委任_02a(再実行)。前回はOpusレビュー原文の貼付・書込がモデル安全フィルタで中断したため、原文はプロンプトに含めず、Opus採点者セッションの出力ログからスクリプトで抽出して保存する方式に変更。到達上限 `DESIGN_02_READY`。コード・SSOT本体無変更、費用JPY0。並行: CRB採点(Repo外)。git index.lock衝突時は30秒待ち最大3回再試行。

## 作業規律

- Opus原文を自分のコンテキストに読み込まない。python -Iスクリプトで抽出・書込し、stdoutは文字数・行数・sha256・先頭/末尾30字のみ。
- 設計追補の本文は、Fable判断とDESIGN_01.mdの該当節を基に自分の言葉で書く(Opus原文の転記・引用はしない。所見IDと要旨のみ参照)。

## 手順(要約)

1. T-0: 本委任文を保存しcheck_delegation_prompt.pyを実行(FAILでも継続)。
2. Opus原文抽出: 入力=採点者セッションログ(agent-ac1ecc8f4a4ac554e.jsonl)。既存extract_opus_text.pyを引数化して再利用。出力=er058_output/unified_all_roles_production_wiring_01/OPUS_REVIEW_A_01_VERBATIM.md。読み戻しでsha256・文字数・行数・先頭末尾30字を記録。
3. DESIGN_02_ADDENDUM_01.md作成。構成: §0 Fable判断表(OF-AUW-01〜18)/§1 値ガードの意味論(5値NO_VALUES,EQUAL,DIFF,AMBIGUOUS,UNKNOWN、判定表、擬似コード、test追加パターン、DESIGN_01の:282/:361/:381/:395矛盾箇所の改定文)/§2 ロールアウト(作業branch feat/auw-unified-asr-01、単一merge、OF-AUW-02/13)/§3 判定点J11引継ぎ・再利用+import graph静的監査(OF-AUW-03/04)/§4 Secondary障害処理(OF-AUW-10)/§5 LR(OF-AUW-07、OF-AUW-06=U2)/§6 JA受理集合(OF-AUW-08 R+、14、17)/§7 費用(OF-AUW-09)/§8 試聴リスト(OF-AUW-15)/§9 OF-AUW-12確認結果(R、3回へ揃える)/§10 test・evidence計画改定(OF-AUW-05/11)/§11 ユーザー判断U1・U2質問文案/§12 記録のみ(OF-AUW-16/18)/§13 委任分割改定(02b〜07)。
4. DESIGN_01.md:414 C-B行とAPPLICABILITY_MATRIX_01.csv X-B1-06行を「R(3回へ揃える)」へ修正(最小差分)。
5. docs/pm/OPUS_FINDINGS_LEDGER.mdへOF-AUW-01〜18追記、docs/pm/REPORT_LEDGER.mdへ1行。
6. secret scan --staged hits=0→明示add→commit→push origin/main。禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
7. 報告docs/pm/RESULT_PACKET_AUW2a.md。

## Fable判断(採否)

採用: OF-AUW-01, 02, 03, 04, 05, 07, 08(R+), 09, 10, 11, 13, 14(記録), 15, 17。ユーザー判断: U1=C-A5/A6、U2=OF-AUW-06。確認済み→R: OF-AUW-12(3回へ揃える)。記録のみ(OPEN候補): OF-AUW-16, 18。理由: いずれもユーザー承認仕様(§2〜§7)の範囲内で安全側かつ誤NG側の歯止めを加えるもの。U1/U2は既存ユーザー承認/未決事項の変更に当たるため。
