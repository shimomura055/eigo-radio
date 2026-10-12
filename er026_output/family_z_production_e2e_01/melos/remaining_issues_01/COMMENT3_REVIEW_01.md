# COMMENT3_REVIEW_01 (FAMILY-Z-MELOS-E2E-REMAINING-ISSUES-01 項目2、2026-10-12、費用JPY0・API不使用)

## a. 25%規則(`limit_comment3_part`、er062_family_z_writer_01.py L816-835)の適用範囲と既存仕様との整合
- 適用範囲: `run_support_std`(n==3のときのみ)と`run_support_adv`(ctxs[3]のみ)の2箇所。Adv/Std共通、**Comment3のみ**。
  Comment1(parts[1]全文)・Comment2(parts[2]全文)・Preview(物語全文を参照)は無改変=影響なし。
  Std Comment3は「すでに聞いた部分」としてparts[2]のみ参照、Advは1+2全文参照(従来から)。
- 既存仕様との整合: CURRENT_SPEC.md L579「Comment 3の役割=Story Meaning+Bridge to Points」は旧11パート構成(A2)の定義。
  Family Zは2026-10-12決定(L1524)で3分割+Comment3つ・Comment4/Pointsなし(Comment3=Part2-3間)に**置換済み**であり、
  Zの Comment3 は「Part3の導入」。25%規則はDECISION_LOG L20609(委任_12D、Fable判断)が正本で、CURRENT_SPECに
  25%規則自体の明文はない(Family Z節にも記載なし)。既存の安全装置(lint/retry)とは独立で、無効化していない。
- 判定: 現行Melos E2Eの範囲内の運用としては矛盾なし。ただし規則が**Z-Writer内の定数・正規表現のコード実装のみ**で、
  SPEC本文に未記載(OPEN候補: 規則のSPEC明文化)。

## 汎用性評価(`comment3_limit_offline_eval_01.py/.json/.txt` のAPIなし評価)
| 入力 | 結果 | 評価 |
|---|---|---|
| Melos Adv r2 Part3(14段落) | 3段落(remember/water/One step)、マーカー段落なし | 良好 |
| Melos Std Part3(14段落) | 3段落、同上 | 良好 |
| 合成: 推理もの。Part3冒頭2段落が「庭師が死んでいた/犯人は実の兄」 | 2/8段落残り**犯人の結末をそのまま含む** | **ネタバレ通過**(マーカー語なし) |
| 合成: 旅もの。Part3第1段落に`arrived` | 1/8段落残るがその段落が**マーカー該当段落そのもの** | 最低1段落保持の仕様でマーカー段落を残す |
| 合成: ファンタジー。第1段落が`sword`(練習の剣) | 1/9段落のみ | 偽陽性。内容が過少になる |
- 設計上の問題点:
  1. マーカー語がMelos固有(city gate/sword/square/I'm back/fell against/free both/embrace/forg*)。他作品では結末語彙が異なり検出不能。
     `forg*`(forget/forgot)、`square`、`gate`、`sword`は偽陽性になりうる。
  2. Part3冒頭にネタバレがあっても「先頭25%・最低2段落」は無条件で通す(推理ものの例)。25%は位置の保証でしかなく、内容の保証ではない。
  3. 先頭段落がマーカーに該当しても`head[:max(i,1)]`で1段落は残るため、マーカー段落を渡す。
  4. 段落数ベースのため、長大な1段落やダイアログ主体の短段落でも同一比率(文字数・文数の保証なし)。
  5. Part分割(場面転換点)の位置次第でPart3冒頭が山場になりうる(Melosでは偶然「思い出し」から始まり安全)。
- 最終防御はLLM promptの`content_facts`制約(「【これから聞く部分】に書かれていない事実・結末は使わない」)とlintのみで、
  入力が既にネタバレなら防げない。

## b. 今回のMelos Comment3の再確認(run_e2e_02/support/a2_support.json, b1b_support.json)
- Std(a2、再生成版): 「メロスは、鎖を受け入れるために差し出された友人の手を思い出します。友人は、もう一度約束を求めずに彼を信じていました。
  岩の割れ目から水が少しずつ流れ、メロスはそれを飲んで立ち上がり、一歩ずつ進みます。」
  - ネタバレ: なし(city gate・鐘・剣・再会・王に触れない。旧版は「門で鐘が鳴り剣が掲げられた友のもとへ走って戻ったと叫ぶ」と結末直前まで到達していた=解消)。
  - 意味: Part3冒頭(思い出し→水→立つ→一歩)と一致。新事実なし。
  - 日本語の自然さ: おおむね自然。軽微な点は「鎖を受け入れるために差し出された友人の手」がやや説明的、
    「一歩ずつ進みます」はPart3の「One step. Another.」に基づく。ユーザー試聴で最終確認する範囲。
  - 役割: Z仕様の「Part3への導入」は満たす。Pointsへの橋渡し(旧定義)はFamily Zでは不要。要点: 紹介だけでPart2までの流れ(逡巡)から
    Part3冒頭への橋渡し語が少ないが、Comment2が「戻る選択」で終わっているため繋がりは成立。
- Adv(b1b、現行=規則施行前生成): 「Melos is badly hurt, and for a moment he thinks about giving up. What will make him keep going, and will he reach the city in time?」
  - ネタバレ: なし(疑問形で結末に触れない。「reach the city in time?」は到着の成否を問う=結末を明かさない)。
  - 意味: Part2末の状況の再確認+Part3への問い。Part3冒頭の内容(友の信頼を思い出す)は触れない=情報量は少ないが導入として自然。
  - 懸念: 規則施行前生成(Part3全文入力)のため、今回はたまたまネタバレなし。Part3全文入力のままでは再発しうる点は規則施行の趣旨通り
    (再生成不要という既存Fable判断を維持)。

## c. 小規模Trial(LLM生成)
- 実施せず(費用JPY0)。理由: (1)Family Zの他Story素材がリポジトリに存在しない(er060_output/er061_fixturesはMelos派生のみ)。
  (2)問題の本質はLLMではなく入力選別ロジック(上表)で、APIなしの決定論評価で再現・説明できる。合成素材によるLLM Trialは
  結論を変えない(入力に結末が含まれる素材は規則上そのままLLMへ渡される)。
- Trial Status: `NOT_RUN`(オフライン評価のみ: Melos=`VALIDATED`、汎用性=`USER_DECISION_REQUIRED`)。

## d. 分類
- Melos E2Eの範囲内: 既承認範囲内の運用で足りる(Melos Comment3のネタバレは解消、Std/Advとも問題なし)。
- 共通仕様化(Family Z全般・他Story)には**判断が必要(USER_DECISION_REQUIRED候補)**: 
  (案A)マーカーをStory別設定(Writer段で結末段落を指定)にする、(案B)LLM判定で「Part3冒頭で結末・犯人等が明かされる段落」を除外、
  (案C)先頭段落がマーカー該当ならその段落を渡さず文単位で切る、(案D)現行維持(Melos専用運用)。いずれもFamily Z全体仕様の新規決定になるため
  Production配線は行わない。
