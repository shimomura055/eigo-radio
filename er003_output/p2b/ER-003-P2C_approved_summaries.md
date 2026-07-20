# ER-003-P2C 承認済みB2「Before You Listen」概要

## 1. 決定理由

ER-003-P2Bで生成した3記事の`Before You Listen`概要は、内容・難易度・長さ・ネタバレ回避の面でユーザー承認済みだったが、全記事が`This episode ...`で始まり、教材の説明文のように聞こえる問題があった。ユーザーは、第一文をナレーターとリスナーを含む`We`を主語にし、原則`We'll look at ...`で始めるPodcast調の語り口に変更することを決定した。これはB2概要の語り口に関するサービス仕様の変更であり、内容(話題・注目点・固有名詞・ネタバレの範囲)の変更ではない。

APIは再実行していない。承認済み文面はユーザーが指示した確定文面をそのまま保存したものであり、Claude Codeが独自に作文・リライトしたものではない。

---

## 2〜4. 記事別: 旧生成概要 / 承認済み概要 / 差分

### A01: 2026年ワールドカップ準決勝のイングランド対アルゼンチン

**旧生成概要(P2B, `summary_en_reading_copy.md`)**

> This episode covers a tense World Cup match between England and Argentina, with a place in the final at stake. Listen for how late decisions and key players' actions shape the game.

**承認済み概要(P2C, `summary_en_approved.md`)**

> We'll look at a tense World Cup match between England and Argentina, with a place in the final at stake. As you listen, notice how late decisions and key players shape the game.

**差分**: 第一文の主語を"This episode covers"→"We'll look at"に変更。第二文を"Listen for how late decisions and key players' actions shape the game."→"As you listen, notice how late decisions and key players shape the game."に変更。

---

### A02: 英国の未成年向け夜間SNS設定

**旧生成概要(P2B)**

> This episode looks at a UK plan to change how social media apps work at night for teenagers. Listen for how the settings work, why users can change them, and what two studies suggest.

**承認済み概要(P2C)**

> We'll look at a UK plan to change how social media apps work at night for teenagers. As you listen, notice how the settings work, why users can change them, and what two studies suggest.

**差分**: "This episode looks at"→"We'll look at"。"Listen for"→"As you listen, notice"(以降は不変)。

---

### ADD03: ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応

**旧生成概要(P2B)**

> This episode looks at a changing U.S. plan for ships using the Strait of Hormuz and its effect on oil markets. Listen for why oil prices stayed uncertain and what worried shipping companies.

**承認済み概要(P2C)**

> We'll look at how a U.S. plan for ships using the Strait of Hormuz changed and affected oil markets. As you listen, notice what worried oil markets and shipping companies.

**差分**: 第一文を"This episode looks at a changing U.S. plan for ships using the Strait of Hormuz and its effect on oil markets."→"We'll look at how a U.S. plan for ships using the Strait of Hormuz changed and affected oil markets."に再構成。第二文を"Listen for why oil prices stayed uncertain and what worried shipping companies."→"As you listen, notice what worried oil markets and shipping companies."に変更。

---

## 5. 語数・文数・推定時間(承認済み概要、決定的再計測)

| 記事 | 語数(見出し除く/込み) | 文数 | 各文語数 | 平均文長 | 130/145/160wpm |
|---|---|---|---|---|---|
| A01 | 33 / 36 | 2 | 20, 13 | 16.5 | 0.25 / 0.23 / 0.21分 |
| A02 | 35 / 38 | 2 | 17, 18 | 17.5 | 0.27 / 0.24 / 0.22分 |
| ADD03 | 31 / 34 | 2 | 20, 11 | 15.5 | 0.24 / 0.21 / 0.19分 |

いずれも25〜35語・2〜3文の既存仕様を満たす(ER-003-P2Aで確定したsentence splitterで再計測)。

## 6. 第一文開始表現の検証

3記事とも`REQUIRED_OPENING_RE`(`^We['’]ll look at\b`)に合格(`opening_ok: true`)。`This episode`等の禁止表現は使用していない。

## 7. P2BのQA結果(監査記録として保持)

3記事とも`summary_qa_status: COMPLETED`、`summary_qa_verdict: PASS`。新事実追加・矛盾・結論ネタバレ・Point回答漏洩・In One Line漏洩はいずれも0件(旧生成文面に対する評価であり、内容自体は承認済み文面でも変更していないため、この評価は引き続き妥当)。

## 8. ユーザー承認情報

- `approval_type: "USER_APPROVED_LIGHT_EDIT"`
- 編集範囲: 第一文の主語・第二文の言い回しのみ(話題・注目点・固有名詞・ネタバレ範囲は無変更)
- 承認済みsha256は各記事の`summary_approved_sha256.txt`を参照

## 9. API再実行なし

概要生成API・概要QA APIともに今回は0回。承認は既存の承認済み内容へのテキスト置換のみ。

## 10. B2本文無変更

`er003_output/p2/{A01,A02,ADD03}/b2_version_raw.md`のsha256は変更前後で完全一致。Natural English Sourceにも一切触れていない。

## 11. 正式参照先

今後のKey Words生成・TTS等の下流処理は`summary_en_approved.md`を参照する。詳細は[ER-003-P2C_reference_manifest.md](../../ER-003-P2C_reference_manifest.md)を参照。
