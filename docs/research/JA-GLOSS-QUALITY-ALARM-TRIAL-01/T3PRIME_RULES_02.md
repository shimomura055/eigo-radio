# 巧妙型の合成T3' 作成規則 (T3PRIME_RULES_02) -- 作成前に固定した変換規則と選定手順

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / 委任_02A / 2026-10-31(Opus M-2対応)。API 0・人手作成。**特定の語を狙って作らない**: 規則→適用基準→機械的な選定アルゴリズムの順で固定し、語は選定結果として決まる。

## 1. なぜT3'か
既存のT3(`tools/build_eval_set_01.py` T3_SPECS)は反意・別義・別概念・状態反転(類型1)だけで、検査器が見つけやすい。held-out側の重大誤訳が実質T3のみになる問題(Opus M-2)を避けるため、類型2〜5の「巧妙型」を加える。T3(易しい型)と分けて判定する。

## 2. 類型ごとの変換規則(固定)
| 類型 | 規則ID | 変換規則 | severity |
|---|---|---|---|
| 2 辞書第一義への一般化 | C2 | 文脈上の語義でなく、主要語の辞書第一義(最頻義)の訳へ差し替える。品詞・文型は元訳に合わせ自然に見せる | major |
| 3 比喩・物語像の喪失 | C3 | 比喩・婉曲・含みのある語句を、含意を落とした字義/平板な訳へ置換し、含意(意味)が変わるようにする | major |
| 4 定訳・専門用語の不適切な言い換え | C4 | 定訳のある語を、近縁だが指す対象が異なる別語(または別範疇の語)へ置換する | major |
| 5 不自然・冗長・分かりにくさ | C5 | 意味は変えず、冗長な言い回し・不要な迂言・説明過剰で、訳語として不自然にする | minor |
類型1(反意・別義)は既存T3が担当。類型6(記事内不整合)は02Bの参考入力で別途評価する(単独項目では作れない)。

## 3. 選定アルゴリズム(固定)
1. 母集団=承認済みT2 71件(正常・凍結ラベルで normal)。
2. 除外: T1の表現(verdict/culprit/charge/radius/equivalent width/things left out)、既存T3の置換元、凍結ラベルで problem/borderline とした項目。
3. 各類型の適用基準(C2=多義語で文脈義が第二義以降/C3=比喩・婉曲・含みのある語句/C4=定訳・専門用語・名詞的な確立語/C5=任意)を満たす候補をT2のid昇順に並べ、dev/held-out(記事単位)を交互に、同一表現は1件まで、各類型4件(dev2+held-out2)を採る。
4. 置換後の訳は上表の規則を適用して人手で記述し、`tools/build_t3prime_02a.py` の SPEC に固定。以後変更しない。

## 4. 結果(16件、dev8/held-out8、major12/minor4)
| id | split | 類型 | sev | 表現 | 元訳(T2) | T3'訳 | 元T2 id |
|---|---|---|---|---|---|---|---|
| JAQ-T3P-116 | dev | 2 | major | biased | 偏った | 偏見をもった | T2-006 |
| JAQ-T3P-117 | dev | 2 | major | subscription | 定額制の契約 | 新聞や雑誌の購読 | T2-022 |
| JAQ-T3P-118 | dev | 3 | major | turn into an interrogation | 尋問になる | 質問の場になる | T2-042 |
| JAQ-T3P-119 | dev | 3 | major | or so it seemed | そう見えたのだが | そのように見えた | T2-008 |
| JAQ-T3P-120 | dev | 4 | major | clutter | 散らかった物 | ゴミ | T2-040 |
| JAQ-T3P-121 | dev | 4 | major | Sales pitch | 売り込み文句 | 広告 | T2-005 |
| JAQ-T3P-122 | dev | 5 | minor | end up receiving | 結局受け取ることになる | 結果的に最終的には受け取るという形に落ち着いてしまう | T2-051 |
| JAQ-T3P-123 | dev | 5 | minor | when it suits someone | 人の都合のよいときに | その人にとって都合がよいと言えるような状況であるときに | T2-050 |
| JAQ-T3P-124 | held_out | 2 | major | adopted | 養子になった | 採用された | T2-055 |
| JAQ-T3P-125 | held_out | 2 | major | bar | 通れないようにふさぐ | 出入りを禁じる | T2-083 |
| JAQ-T3P-126 | held_out | 3 | major | get what you deserve | 自分にふさわしい報いを受ける | 自分にふさわしいものを手に入れる | T2-075 |
| JAQ-T3P-127 | held_out | 3 | major | shoving match | 激しい押し合い | 押し合いの試合 | T2-028 |
| JAQ-T3P-128 | held_out | 4 | major | wavelength | 波長 | 周波数 | T2-012 |
| JAQ-T3P-129 | held_out | 4 | major | light-skinned | 色白の | 白人の | T2-078 |
| JAQ-T3P-130 | held_out | 5 | minor | talk someone into staying | 誰かを説得して残ってもらう | 誰かを説得することによって、その人がその場に残るという状態にしてもらう | T2-074 |
| JAQ-T3P-131 | held_out | 5 | minor | go no farther | それ以上先へ進まない | それよりも先の方向へと進むという行為をしない | T2-081 |
- 分割は元T2の記事のsplitに従う(記事単位。devとheld-outで同じ記事が跨らない)。
- 各T3'は `must_not_share_batch_with=[元T2のid]`(元訳と同じバッチに同居させない。バッチ構成とR-3の12件埋めは委任_02B)。T3'の `existing_explanation_ja`/`existing_sentence_ja` は元の正常訳の解説が漏れないよう null。
- 一部のT3'(例: Sales pitch→広告、subscription→購読)は『辞書的には近いが文脈で誤り』という設計上の巧妙さの目安であり、検出の難易度は未検証(Trial前)。
- 限界: 16件は小さい。ガードの分母(下記)はheld-outで6件(major)しかなく、1件の見逃しで85%を割る。区間付きで報告する(TRIAL_PLAN_02 §3)。
