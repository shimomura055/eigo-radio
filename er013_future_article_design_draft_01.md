# er013_future_article_design_draft_01.md

管理ID: EDITORIAL-FUTURE-ARTICLE-DESIGN-01
性質: Trial設計draft。**Production未配線**(このファイルはどのPython
モジュールからもimportされていない。Markdownとして保存し、Trial実施時に
初めてPythonファイルへ実装・importするかどうかをFable/ユーザーが判断する)。
本文中の文言は全て「未承認draft」であり、`APPROVED_FOR_PRODUCTION`では
ない。

対応する設計根拠: `EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md`。

---

## 1. Future Editorial Type Module Block(draft、Writer prompt追加ブロック)

Trend Synthesis(`er003_v1_n3_01_articles_generate.py::
TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`)と同型の位置付け
(`editorial_type_module_block` placeholder、COMMON_BLOCK_TEMPLATE内
【Spoken-first原則】直前への挿入を想定)。`editorial_mode="future"`
指定時のみ挿入する案。

```
FUTURE_FOCUS_MODULE_BLOCK_DRAFT = """【Future Focus(記事タイプ固有の焦点。draft、未承認)】
この記事は、現在の根拠を解説する記事ではありません。聞き手が、描かれる
未来に強くわくわくする、または強い不安を感じる、印象に残る記事を目指し
ます。

Main Storyでは、意味のある1〜3通りの未来を描いてください。数合わせの
分岐は作らないでください(1通りでも、意味があれば十分です)。それぞれの
未来について、その未来の具体的な姿と、そこに至る変化・条件の両方に触れ
てください。どちらに重点を置くかはテーマに合わせて判断してください。

【現在の事実と、想像した未来の区別(最重要)】
以下の3種類を、書きながら常に区別してください:
1. 確認済みの現在の事実(Verified Fact Ledgerが裏付けるもの)
2. 明示的な仮定・条件(「もしこの流れが続けば」「この技術が実用化されれ
   ば」のように、読み手にも仮定だとわかる形で書かれるもの)
3. 想像した未来の場面・情景(具体的な未来の1シーンなど。想像であることが
   読み手に伝わる書き方をしてください)

未来を、既に起きた確定事実であるかのように断定して語らないでください
(will/断定形を使う場合も、記事全体の文脈から「これは想像・予測であ
る」と聞き手が理解できるようにしてください)。逆に、現在の事実を、想像
した未来の要素と混ぜて曖昧にしないでください。現在の事実は、Ledgerの
範囲内で正確に保ってください。

仮想の未来の場面を使うかどうか、冒頭や展開の型をどうするかは、この記事
のテーマに最も合う形を選んでください。型を固定しません。

Point One・Point Twoは、この記事の未来の数(1〜3)に対応させる必要は
ありません。以下の候補から、テーマに最も合う異なる役割を1つずつ選んで
ください:
- その未来に至る変化・条件
- 別の未来(反転・分岐・もう一つの可能性)
- 見えなかった実生活上の意味
- 希望と不安のどちらに転ぶかの分かれ目

In One Lineでは、事実の要約ではなく、聞き手が持ち帰る印象(わくわく/
不安の余韻)を残してください。

研究・出典・データの説明を、記事の主役にしないでください。それらは
制作時の裏付けとして使うものであり、聞き手に解説として前面に出す
ものではありません(この点でDiscovery/Trend Synthesisとは異なる編集
方針です)。"""
```

## 2. Ledger 3層タグ規約(draft)

既存タグ規約(`[VOICE_n_EVIDENCE]`、
`er012_b_family_editorial_type_registry_01.py::build_voice_attribution_block()`
の抽出ロジックと同型のline-based抽出を想定)を踏襲する案。

```
[PRESENT_FACT]
(既存Verified Fact Ledgerのfactエントリと同一フォーマット。無変更)

[FUTURE_ASSUMPTION]
assumption: <明示的な仮定・条件の文>
based_on: <この仮定の根拠となるPRESENT_FACTのID、または「なし(一般的推論)」>

[IMAGINED_FUTURE]
scene: <想像した未来の場面・情景の下書き>
grounded_in: <この場面が参照するPRESENT_FACT/FUTURE_ASSUMPTIONのID一覧>
```

## 3. Future Framing QA 要件定義(draft、未実装)

対象: `[FUTURE_ASSUMPTION]`/`[IMAGINED_FUTURE]`に紐づく文のみ
(`[PRESENT_FACT]`に紐づく文は既存Fact Checker A'/Ledger Deviation
Checkerが従来どおり厳格に検証、本QAの対象外)。

判定項目(draft):

| 項目 | 判定内容 | 悪い例 | 良い例 |
|---|---|---|---|
| Framing | 未来が確定事実として断定されていないか | "By 2035, every city will have banned private cars." | "Picture a city, twenty years from now, where private cars have become rare." |
| 現在事実の捏造なし | 想像パッセージ内の現在時制の主張がLedgerと矛盾していないか | "Cities are already banning cars today"(Ledgerに未確認の現在主張) | 現在時制の主張をLedger範囲内に限定 |
| 仮定の明示性 | 仮定が読み手に分かる形で示されているか | 仮定を示さず断定に飛躍 | "If this pace continues, ..." のような明示 |
| 根拠解説の不在 | 研究・出典・データ説明が本文の主役化していないか | "A 2023 study of 500 firms found that ..." を本文で詳述 | 裏付けは足場に留め、場面・意味を前面に出す |

出力スキーマ(draft、実装しない):

```
{
  "framing_violations": [{"claim": str, "issue": str}],
  "fabricated_present_facts": [{"claim": str, "issue": str}],
  "unlabeled_assumptions": [{"claim": str, "issue": str}],
  "discovery_style_leakage": [{"claim": str, "issue": str}],
  "overall_status": "PASS" | "REVIEW_REQUIRED" | "FAIL"
}
```

Ledger Deviation Checker(10 flags、`er009_ledger_deviation_recalibration_02.py`)
との関係: Layer 2/3のclaimは、既存の`unsupported_new_claim`/
`changed_certainty`フラグの判定対象から明示的に除外し、代わりに本QAの
判定対象とする案(ルーティング方式、閾値の一律緩和ではない)。ルーティ
ングの実装方法は`EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md`§3-3の
STOP事項どおり未確定。

## 4. 未確定事項(Trial実施前に確認が必要)

- Writerが本文中で想像パッセージをどう視覚的/構造的に区切るか(段落
  マーカー等)の具体的な書式規約
- Layer判定(claim→Layer 1/2/3のどれか)を自動化する方法
- COMMON_BLOCK_TEMPLATE本体(【Fact Ledger使用上の制約】文言)を一部
  書き換える必要があるか、Module Block追加だけで足りるか
