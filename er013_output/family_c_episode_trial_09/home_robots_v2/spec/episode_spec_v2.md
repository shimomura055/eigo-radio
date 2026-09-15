# Family C / Home Robots v2 — episode spec(Comment構成、恒久決定)

管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2(2026-09-15)。

## Comment構成の恒久決定(Family C全体に適用)

- **Comment 4は使用しない**(ユーザー正式決定、2026-09-15)。Family Cの
  Comment構成は常にComment 1〜3の3件とする。
- 構成原則:
  - Comment 1 = 導入理解補助(Story本編が始まる直前、Full story intro直後)。
  - Comment 2 = Story途中の自然な節目(semantic break/scene transition)。
  - Comment 3 = 後半の自然な節目(turning point付近)。
  - Comment 4 = なし(Story終了直後の総括的コメントは置かない)。
- Comment位置は**segment番号やplan_indexの固定値で決めない**。記事ごとに
  以下を根拠に決定する:
  - semantic break(意味の区切り)
  - scene transition(場面転換)
  - turning point(物語の転換点)
  - 前後のtext volume(語数バランス)
  - 前後のaudio duration(尺のバランス)
- Story終了後は既存Family A(A2)構成どおり、pause(0.5秒、A2既存値
  `build_a2_timeline` pause_0.5 In One Line→Outro)→Outroとする
  (Comment 4削除に伴う変更、`er013_family_c_episode_trial_09b_run.py`の
  Assembly Stage Hに実装済み)。
- この構成原則は`er013_family_c_episode_trial_09b_run.py`の既定
  (`COMMENT_NUMBERS = (1, 2, 3)`)として実装済み。B1側scriptも同じ構成
  原則を採用すること(B1 scriptは並行タスクが作成するため本タスクでは
  変更していない)。

## 本記事(home_robots_v2)でのComment位置(実測)

| Comment | 位置根拠 | 前segment | 後segment |
|---|---|---|---|
| 1 | 導入部(Preview後・Story前) | なし(Full story intro直後) | story_001 |
| 2 | v1 story_009/010境界相当(段落9/10境界、"何でも便利にこなす"日常描写から母親来訪の場面転換点) | story_009 | story_010 |
| 3 | v1 story_017/018境界相当(段落22/23境界、ロボットが最適解を示せない場面の直後、turning point) | story_017 | story_022 |

詳細な語数・尺は`../comment_placement.json`参照。

## Comment 3修正の記録(2026-09-15)

- 旧文(誰が質問したか曖昧という指摘を受けた): 「お金や睡眠、仕事、安全に
  ついて聞いても、今回はロボットのいつもの方法では答えが見つからない
  ようです。」
- 新文(ユーザー原文をそのまま採用、微調整なし): 「お金や睡眠、仕事、
  安全についてロボットが問いかけ、マヤは答えましたが、今回はいつものように
  ロボットが最適解を示してくれることはありませんでした。」
- 根拠(記事本文、`../article_normalized.txt`): "The robot asked about
  money, sleep, work, and safety. Maya answered. Still, no answer came."
  (ロボットが問いかけ、マヤが答えたが、答えは出なかった)と一致。
- 旧文は`../comments_ja_prev.md`に保存。

## Family C全体の採用状況

Family C(Home Robots含む)は現時点でProduction正式path未承認
(`APPROVED_FOR_PRODUCTION`は人間ユーザーのみが決定できる)。本v2は
Trial・VALIDATED候補にとどまる。
