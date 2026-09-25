# prompt_diff_writer.md
FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01

流用元: `er013_family_c_future_writer_08.py`
(`WRITER_DEVELOPER_MESSAGE` / `WRITER_PROMPT_TEMPLATE`)
新規: `er018_fiction_core_provocation_random_dna_trial_01.py`
(`WRITER_DEVELOPER_MESSAGE` / `WRITER_PROMPT_TEMPLATE`)

## 1. Developer message

### Before(旧、Future限定)
```
You are the Writer for an English-learning magazine's 'Future' article family.
Your single most important job is to make the reader genuinely feel the Core
Provocation given to you -- excitement, a little tension, and a question that
stays with them, so they want to keep reading. Write it as a story: a vivid
imagined future scene built around the Core Provocation, not a summary of
studies. Do not force the story into any fixed template, fixed number of scenes,
fixed number of emotional turns, or a fixed ending shape -- choose whatever shape
makes this particular Core Provocation land most strongly. Never insert a
present-day statistic or a sentence describing research findings into the story;
CURRENT FACT sentences are forbidden in this article, not merely discouraged.
```

### After(新、Fiction、Future限定を除去)
```
You are the Writer for an English-learning magazine's Fiction article family.
Your single most important job is to make the reader genuinely feel the Core
Provocation given to you -- excitement, a little tension, and a question that
stays with them, so they want to keep reading. Write it as a story: a vivid scene
built around the Core Provocation, not a summary of studies or an abstract essay.
The setting can be realistic, near-future, far-future, or entirely
unreal/speculative -- whatever fits the Core Provocation best. Do not force the
story into any fixed template, fixed number of scenes, fixed number of emotional
turns, or a fixed ending shape -- choose whatever shape makes this particular Core
Provocation land most strongly.
```

### 差分の要点(語句置換にとどまらない構造的な差分を含む。正直に記載)
- "'Future' article family" → "Fiction article family"
- "a vivid imagined future scene" → "a vivid scene" + 新規の1文
  "The setting can be realistic, near-future, far-future, or entirely
  unreal/speculative -- whatever fits the Core Provocation best."(委任文の
  「現実・未来・非現実・仮想設定を問わず」を反映)
- **最後の1文(CURRENT FACT禁止)を削除**: これは単なるFuture限定語句の置換
  ではなく、Future family固有のFact Safety機構(裏側でPlausibility
  Bridge/Imagined Future層と連動)に紐づく文であり、このTrialにはFact
  Safety層自体を実装しない(委任文の実装範囲・10 call予算に含まれず、
  マーカー再試行機構も無い)。単純な文言置換では意味が成立しないため削除した
  (下記2節も同様の判断)。

## 2. Prompt template(ユーザーメッセージ)

### Before(旧v8、抜粋)
```
[Core Provocation -- this must drive the whole article]
{core_provocation}

[Theme]
{theme_label}

[Your single job]
Write a short story set in an imagined future, built around the Core Provocation \
above. Make a reader genuinely feel the future, want to keep reading, and feel some \
excitement and a little tension along the way. Do not follow any fixed structure, \
fixed number of scenes, fixed number of emotional turns, or a fixed ending shape -- \
choose whatever narrative shape makes THIS Core Provocation land most strongly.

[CURRENT FACT -- forbidden, not optional]
(...省略、現在事実文の禁止を扱う1ブロック全体...)

[Characters -- keep it simple]
(...v8と同文、後述のとおり今回も維持...)

[Required marker -- technical, not creative]
(...省略、[[IMAGINED: timeframe]]...[[/IMAGINED]]マーカーの必須化を扱う
1ブロック全体...)

[Length and level]
(...v8と同文、今回はrange のみ280-420語へ変更...)

[Listening-friendliness -- an editorial goal, not a hard rule]
(...v8と同文、今回も維持...)

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short.
```

### After(新)
```
[Core Provocation -- this must drive the whole article]
{core_provocation}

[Theme]
{theme_label}

[Story DNA -- a creative nudge, not a contract]
(...本文はprompt_diff_provocation.mdと同一ブロック...)

[Common principles for this story family]
(...本文はprompt_diff_provocation.mdと同一ブロック...)

[Your single job]
Write a short story built around the Core Provocation above, in whatever kind of \
setting fits it best (real, future, unreal, or an imagined/speculative world). Make \
a reader genuinely feel something, want to keep reading, and feel some excitement and \
a little tension along the way. Do not follow any fixed structure, fixed number of \
scenes, fixed number of emotional turns, or a fixed ending shape -- choose whatever \
narrative shape makes THIS Core Provocation land most strongly.

[Characters -- keep it simple]
(...v8と同文のまま維持、詳細は下記「維持したブロック」参照...)

[Length and level]
(...v8と同構成のまま維持。ただし語数レンジのみ委任文どおり280-420語へ変更...)

[Listening-friendliness -- an editorial goal, not a hard rule]
(...v8と同文のまま維持...)

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short.
```

### 差分の要点(語句置換 vs 構造的削除・追加を明確に区別)

**単純な語句置換(Future限定語句のみ)**:
- "Write a short story set in an imagined future, built around the Core
  Provocation above." → "Write a short story built around the Core Provocation
  above, in whatever kind of setting fits it best (real, future, unreal, or an
  imagined/speculative world)."
- "Make a reader genuinely feel the future, want to keep reading" →
  "Make a reader genuinely feel something, want to keep reading"

**新規追加(委任文が明示的に要求)**:
- `[Story DNA]`ブロック・`[Common principles for this story family]`ブロック
  (prompt_diff_provocation.mdと共通の文言)

**構造的な削除(単純な語句置換の範囲を超える判断。Fable/ユーザー確認事項として
明記)**:
- `[CURRENT FACT -- forbidden, not optional]`ブロック全体を削除。
- `[Required marker -- technical, not creative]`ブロック全体
  ([[IMAGINED: timeframe]]...[[/IMAGINED]]マーカー必須化)を削除。
- 判断根拠: この2ブロックは「現在事実と想像上の未来を混同させない」という
  Future family固有の技術的安全機構であり、Fictionへ拡張した場合(E軸が
  「現代の日常」「超自然・幻想的な世界」「現実とほぼ同じだが1つだけルールが
  違う世界」等、必ずしも「未来」ではない設定を含む)には字義通りには
  成立しない。委任文の実装範囲(10 call予算、Fact Safety層の実装なし、
  マーカー不整合時の技術的retryの仕組みなし)からも、この2ブロックを
  そのまま残すことは想定されていないと判断した。これは「Future限定語句の
  みを置換する」という委任文の原則を超える判断であり、単純な語句置換では
  ないため、この事実をそのままFable/ユーザーへ報告する(REPORT§1/§11参照)。

**維持したブロック(Future限定語句を含まないため逐語のまま)**:
- `[Characters -- keep it simple]`(基本1-2人・最大3人、主人公のみ固有名可)
- `[Listening-friendliness -- an editorial goal, not a hard rule]`
- 固定Plot構造を強制しない旨の指示("Do not follow any fixed structure...")
  は元々v8にも存在し、委任文の「固定のPlot構造を指定しない」と整合するため
  そのまま維持(委任文が想定していた「テンプレート構造の指示があれば残す/
  外すの判断が必要」に該当する記述はv8には無かった -- v8は既に
  「固定構造を強制しない」という指示のみで、逆方向のテンプレート強制指示は
  含まれていなかった)。

## 3. 語数レンジ
- v8: target 350語、range 300-420語
- 今回: target 350語(維持)、range **280-420語**(委任文の明示数値へ変更)
