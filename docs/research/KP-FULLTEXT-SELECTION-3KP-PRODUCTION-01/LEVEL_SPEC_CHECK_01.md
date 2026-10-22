# LEVEL_SPEC_CHECK_01: Prompt 2「英語上級者」とStandard/Advancedの承認済みレベル仕様の整合確認

管理ID: KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01 / 2026-10-22(ユーザー原文§5「Standardにそのまま適用すると既存レベル別学習品質と衝突する可能性。承認済みレベル品質を変更する必要があるなら独断で変えずUSER_DECISION_REQUIRED」への回答)

## 1. 結論
- **衝突は確認されなかった**(区分B: 承認範囲内で自己解決。`USER_DECISION_REQUIRED`不要)。根拠: **現行の承認済みKP選定基準にStandard専用の選定基準は存在しない**。選定Prompt(`b1_p2_keywords_l_prompt_template.txt`)は**A2/B1・両経路共有の唯一のファイル**で、Standard(A2本文)にも同一文面(Listening Blocker優先)が使われている(CURRENT_SPEC:1975「A2/B1・両経路共有の唯一のファイル」、:596「A2専用の新方式は作らない」)。Prompt 2を両レベルへ同一適用しても、**承認済みの「レベル別選定基準」を変更したことにならない**(レベル差は本文そのもの[Advanced=Natural English Adaptation B1相当、Standard=6,000語ライン+自然さ優先のA2相当]から生じる)。
- ただし**選定基準そのもの(Listening Blocker優先→上級者向け学習価値+易しい表現除外)の変更は、ユーザー自身の今回の正式決定**であり、AIが独断で変えたものではない。AIが決めたのは「Standardだけ別文言にしない」ことのみ。
- 副次: **承認済み4+1構成(Topic Phrase 1枠)は、Prompt 2がrole出力を持たないため全文選定では適用されない**(§4)。これはユーザー決定(Prompt 2逐語採用)に内在する置換であり、Fableが受入記録で確認する事項(区分B/C)。

## 2. 照合した承認済み仕様(CURRENT_SPEC行)
| 項目 | 内容 | 行 | 本件との関係 |
|---|---|---|---|
| KP選定(A2) | A2最終本文から改めて選定。既存Strategy L(Listening Blocker Ranking)+Canonicalizationをそのまま使用(A2専用の新方式は作らない) | :596 | **Standard専用の選定基準は存在しない**=Prompt 2を共通適用しても変更にならない |
| KP選定(B1)・提示順序 | B1本文から選定。English→Japanese→English | :645-651 | 選定元=各レベル自身の本文(Prompt 2も同じ入力) |
| KP音声構造(Std/Adv共通骨格) | Std=英Phrase→日本語意味(J3)→英Phrase / Adv=英Phrase→英語解説(Variant B)→英Phrase | :1986-2000 | **不変**(選定のみ変更。音声構造・順序は触れない) |
| Standard本文 | v5「6,000語ライン+自然さ優先」Prompt。**頻出約6,000語以内は原則そのまま使用・必要に応じてKey Words/Phrases側で学習補助**。6,000語超でも不可欠語は残る | :839 | Standardは本文側で平易化済み。KPは「補助」の位置づけ(KPの選定方針は未規定)。Prompt 2は本文中の学習価値ある語句を選ぶため補助目的と矛盾しない(§3) |
| 件数 | 5件/記事 `DECIDED`(ER-003-P2I) | :1953 | ユーザー決定でX/Z=最大3件に置換(A/B/Cは旧仕様のまま) |
| 4+1(Topic枠) | 重要語4+Topic 1(key_phrase_role) | :1975 | Prompt 2はrole非出力=X/Zでは**roleなし3件**(§4) |
| Z SRC D1 | Zは候補ID方式を導入せずStrategy L全文選定+Python事後付与 | :1977 | 全文選定のため整合(Zは元々全文選定) |
| M2P0・優先順位A | X固有。Zは対象外 | :1691,:1984 | Xは本決定でM2P0供給から全文選定へ(ユーザー決定による置換) |
| KP選定モデル | GPT-6 Luna(`gpt-6-luna`) | :2509 | 一致(Luna固定) |

## 3. Standard(A2本文)への適用の実データ確認(保存Trial-02/03、API 0)
- Standard 7単位(A〜G)のLuna出力(5件版Prompt、Prompt 2より1件多い)は**全単位で5件選定できた**: A `pumps its fist/keep raw beans in stock/pushed prices up/appear in US shop prices/its own hidden clock`、C `think up/Before you know it/moving the story forward/make a story public/leave the reader's seat`、E `behind the scenes/pulled back/take over`等。**「候補不足で3件に満たない」はStandardでも観測されなかった**(0/7単位)。
- 「易しい表現の除外」で選ばれる語句の水準: Standardの選定にも`keep ... in stock`/`think up`のような学習価値のある表現が含まれ、基本語だけの字面どおりの表現は少ない(目視。Standard/Advancedの品質差の定量評価はしていない)。
- 懸念として残るのは「Standard学習者にとって『上級者でも学ぶ価値』の語句が難しすぎる」可能性だが、(ア)ユーザー決定の文面どおり、(イ)Standardの学習支援(日本語意味J3)は音声構造として別に担保、(ウ)Standardの本文自体が平易化済みで、選ばれる語句は本文内に実在する表現に限られる、ため構造的な衝突とは判定しない。

## 4. 4+1(Topic Phrase)構成の取扱い(判断候補ではなく受入記録事項)
CURRENT_SPEC:1975は2026-09-28のユーザー`APPROVED_FOR_PRODUCTION`(Key Phrase 5枠=重要語4+Topic 1)。Prompt 2(ユーザー逐語・一字一句固定)はTopic/role出力を要求せず、ユーザーは「各レベル5件→3件」「既存の原形化・一般化は維持」とのみ指示。したがって:
- X/Zの全文選定itemは`key_phrase_role`を持たない(設計: `er105`はroleを出力せず、canonicalization passthroughも`key_phrase_role`欠落を既存の後方互換どおり許容)。
- 4+1のvalidator/schema/template(#1-#3)は**A/B/C共有の旧経路として無変更で残置**(27-7)。
- 区分: **B(ユーザー決定の逐語採用に内在する置換。AIが新規判断を加えていない)**。ただし「Topic枠の廃止」を明文でユーザーに確認する価値があるかはFableの判断(推奨: 受入記録に「4+1はX/Zで全文選定へ置換された」旨を1行記載。再質問はしない=27-3 A/B既判断扱い)。

## 5. 選択肢(ユーザー原文§5の要請に従い、衝突時の選択肢と影響を併記。ただし衝突は無いため推奨=(ア))
| 案 | 内容 | 承認要否 | 影響 |
|---|---|---|---|
| **(ア)推奨** | Prompt 2を両レベルへ逐語適用 | 不要(ユーザー決定の文面どおり) | 実装最小。レベル差は本文由来。runtime evidenceでStandardの3件を報告に併記 |
| (イ) | Standardのみ文言調整(例: 「英語上級者」→「学習者」) | **要**(Prompt逐語固定の変更=ユーザー明示承認) | Prompt二重化。比較Trial不要というユーザー方針に反する |
| (ウ) | Standardは既存基準(Strategy L・Listening Blocker・5件)維持 | **要**(ユーザー決定「X/Z共通・各レベル3件」と不整合) | 新旧2系統が残り「5件前提を残さない」に反する |

## 6. 監視(必要十分な品質で止める範囲)
- runtime evidence(X/Z各1記事)の報告に、StandardとAdvancedの**3件の英語・日本語意味・本文位置を並記**し、Fableが受入時に「学習者向けの水準として明白に不適」でないかを確認する(追加Trial・比較は行わない)。
- 明白に不適(例: 固有名詞のみ・本文断片)と判定された場合のみ`判断候補`として報告(現時点でその兆候なし)。
