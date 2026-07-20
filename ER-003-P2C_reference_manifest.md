# ER-003-P2C: B2「Before You Listen」概要の正式参照manifest

ER-003-P2Cにより、B2概要の語り口(第一文を`We'll look at ...`で始めるPodcast調)がユーザー承認済みのサービス仕様として確定した。今後、B2の`Before You Listen`本文として参照するファイルの優先順位は次の通り。

## 正式配信用・次工程入力

```text
er003_output/p2b/A01/summary_en_approved.md
er003_output/p2b/A02/summary_en_approved.md
er003_output/p2b/ADD03/summary_en_approved.md
```

Key Words生成・TTS等、今後の下流処理は**この`summary_en_approved.md`を参照する**。`summary_en_reading_copy.md`(未編集のモデル生成原稿)を直接使用しない。

各記事のsha256は `summary_approved_sha256.txt` に保存されている。承認内容の詳細(編集範囲・承認種別)は `summary_approval.json` を参照。

## 生成時監査用(変更しない)

```text
er003_output/p2b/A01/summary_en_reading_copy.md
er003_output/p2b/A01/attempt_1_raw_response.json
er003_output/p2b/A01/attempt_1_summary.md
er003_output/p2b/A01/attempt_1_structure_check.json
er003_output/p2b/A01/summary_qa.json
er003_output/p2b/A01/execution_log.json
(A02, ADD03も同様の構成)
```

これらはER-003-P2Bでモデルが生成した未編集の原稿・QA結果であり、ER-003-P2Cでは一切変更していない。承認前の生成物の監査証跡として保持する。

## 承認の性質

ER-003-P2Cの編集は、内容(話題・注目点・固有名詞・ネタバレの範囲)を変更しない**語り口のみの軽微編集**であり、API再実行・別モデルによるリライト・Claude Codeによる独自の代替表現作成のいずれでもない。承認済み文面はユーザー(プロジェクト責任者)が指示した確定文面をそのまま保存したものである。

- `approval_type: "USER_APPROVED_LIGHT_EDIT"`
- `api_regeneration: false`
- `post_approval_llm_rewrite: false`

## 将来の生成仕様

ER-003-P2C以降、新規に生成されるB2概要は `er003_v1_translator_briefs/b2_summary_prompt_template.txt` の更新済みprompt(`We'll look at ...`起点の語り口指示を含む)を使用し、`er003_b2_summary.validate_summary_structure()` の第一文開始検証(`REQUIRED_OPENING_RE`)に合格する必要がある。
