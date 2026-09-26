# fact_check.md (NEWS-FAMILY-X-LONGFORM-OFFLINE-CHECK-01)

対照元: 日本語R2 `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md`、
fact scope `er012_output/e_family_two_level_wiring_01/meta/fact/meta_fact_scope.md`
(Reuters一次情報: "some of the phone calls" = 一部の**通話**をcall単位で人間が
処理、が確定scope)。

## 文単位対照表(生成本文6段落・24文)

| # | 生成本文(要約) | 対応するJA段落/一次Fact | 判定 |
|---|---|---|---|
| P1-1〜4 | AI電話代行の未来イメージ、Metaが構築中 | JA para1 | 一致・追加なし |
| P2-1〜3 | 主役Muse、電話代行機能、舞台裏で意外な光景 | JA para2-3 | 一致・追加なし |
| P3-1 | 社内試験でcontract workersが"some of the calls"を担当 | JA para4 + Reuters "some of the phone calls" | 一致(call単位のscope、Ledger確定scopeと合致) |
| P3-2 | Metaはこの役割を"human concierges"と呼んだ | JA para4 | 一致(Reutersの"human concierge"呼称とも一致) |
| P3-3 | 看板はAI電話代行、でも一部は人間が対応 | JA para5 | 一致(JA自体もここで同じ情報を反復する構成) |
| P3-4 | AIが独演しているように見えるが人間の代役が控えていた | JA para5 | 一致・追加なし |
| P4-1〜3 | 一番面白い点、ピアノに隠れた演奏者の比喩 | JA para6 | 一致・追加なし |
| P4-4〜6 | 人間の手伝いは自然という一呼吸 | JA para7 | 一致・追加なし |
| P5-1〜3 | 電話には個人情報、プライバシー懸念、契約スタッフが聞いていたと知れば驚く | JA para8 | 一致・追加なし |
| P5-4 | Reutersが確認、Meta幹部が機能を一時停止と説明 | JA para9 | 一致(下記「幹部」の単複のみ観察) |
| P6-1〜4 | 電話をかけられるかだけでなく、誰が話し誰が幕の後ろにいるか、説明の重要性 | JA para10 | 一致・追加なし |

## 「some of the calls」表現の確認

生成本文は P3-1・P3-3 の2箇所で **"some of the calls"** を使用しており、
Reuters一次情報の確定scope(call単位で一部の通話を人間が処理)と一致する。
arm3(参考・入力にはしていない)は "handled some **parts of** the calls" と
表現しており、これはfact scope文書がSource不支持と判定した誤scope
("parts of a call"相当)に近い。今回のOffline生成は誤scope表現を採用して
おらず、Ledger確定scopeと整合している。

## 観察(逸脱ではない)

- P5-4「Meta executives said」(複数形)。原文JA「Metaの幹部は」は日本語の
  性質上、単数・複数のいずれとも取れる表現であり、単複の指定はない。
  fact scope文書・Reuters引用にも単数/複数を断定する記述はないため、
  これは事実の追加・改変ではなく訳語選択の観察事項として記録する
  (arm3参考は"a Meta executive"と単数選択、今回は複数選択)。

## 結論

- 新規に追加された事実・数値・固有名詞・例示は検出されなかった(数値・
  固有名詞の機械抽出は本文中の既存Fact語彙[Meta/Muse/Reuters/human
  concierge等]の範囲内)。
- 事実の欠落も検出されなかった(JA10段落すべてに対応する内容が本文6段落
  内に存在する)。
- "some of the calls"表現によりcall単位のscopeが正しく維持されている。
