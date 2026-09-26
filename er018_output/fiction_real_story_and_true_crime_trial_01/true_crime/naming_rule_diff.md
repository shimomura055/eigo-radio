# Naming Rule Diff — The Second Skeleton (true_crime)

管理ID: FICTION-FAMILY-Z-PRODUCTION-E2E-01(追従修正、2026-09-26)

適用ルール: Family Z共通「外国人の人名は本文中でFirst name / Last nameのどちらか
一方だけを使用する」。本作は歴史上の通称がLast name（Aram, Houseman, Clarke）で
あるためLast name側へ統一。

- Before: `story_fullname_superseded.md`(修正前、334語)
- After: `story.md`(修正後、326語)
- 差分: フルネーム表記8箇所からFirst name（Daniel/Eugene/Richard）を削除し、
  Last name（Clarke/Aram/Houseman）のみに統一。内容・Fact・Storyline・
  文構造・段落構成は一切変更していない。

## 変更文一覧(Before/After + 意味差なしの確認)

| # | 段落 | Before | After | 意味差 |
|---|------|--------|-------|--------|
| 1 | 1 | In the eighteenth century, in England, **Daniel Clarke** had silver and jewels. | In the eighteenth century, in England, **Clarke** had silver and jewels. | なし(同一人物を指す表記の簡略化のみ) |
| 2 | 1 | **Eugene Aram** and **Richard Houseman** persuaded him to walk out at night to discuss how to dispose of them. | **Aram** and **Houseman** persuaded him to walk out at night to discuss how to dispose of them. | なし |
| 3 | 2 | People believed Clarke had disappeared. **Eugene Aram**, however, remained apparently respectable. | People believed Clarke had disappeared. **Aram**, however, remained apparently respectable. | なし |
| 4 | 5 | During the inquiry, **Richard Houseman** was asked to handle a bone. | During the inquiry, **Houseman** was asked to handle a bone. | なし |
| 5 | 5 | He exclaimed, "This is no more **Daniel Clarke's** bone than it is mine!" | He exclaimed, "This is no more **Clarke's** bone than it is mine!" | なし(引用の趣旨・所有格の意味は同一) |
| 6 | 8 | **Eugene Aram** was arrested and brought to trial. | **Aram** was arrested and brought to trial. | なし |
| 7 | 9 | On 16 August 1759, **Eugene Aram** was executed at York. | On 16 August 1759, **Aram** was executed at York. | なし |

上記以外の文(段落3, 4, 6, 7の全文および段落1・2・5・8・9の残り部分)は元々
Last name表記（Aram / Houseman / Clarke）のみを使用しており、変更なし。

## 確認結果
- Fact・Storyline・年代(1759年8月16日)・地名(St. Robert's Cave, York)・
  事件の経過(第一の骨格発見→審問→Housemanの発言→自白→第二の骨格発見→Aramの裁判・処刑)
  はすべて変更前と同一。
- 文法・冠詞・所有格("Clarke's")の整合を確認済み(全箇所で問題なし)。
- 語数変化(334語→326語)は、First name 8箇所の削除のみに起因する自然な結果であり、
  内容・Fact・Storylineの変更を伴わない。
