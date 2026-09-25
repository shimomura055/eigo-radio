# prompt_diff_provocation.md
FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01

流用元: `er013_family_c_future_provocation_08.py`
(`CORE_IDEA_DEVELOPER_MESSAGE` / `CORE_IDEA_PROMPT_TEMPLATE` / `CORE_IDEA_JSON_SCHEMA`)
新規: `er018_fiction_core_provocation_random_dna_trial_01.py`
(`CORE_PROVOCATION_DEVELOPER_MESSAGE` / `CORE_PROVOCATION_PROMPT_TEMPLATE` /
`CORE_PROVOCATION_JSON_SCHEMA`)

## 1. Developer message

### Before(旧、Future限定)
```
You are brainstorming Core Provocations for a short imagined-future story in an
English-learning magazine's 'Future' article family. A Core Provocation is a
single central idea or question about the future that would make a reader feel
'I want to know what happens next' and 'I have never thought about it this way
before'. Come up with 1 to 3 promising central ideas for the given theme (fewer,
stronger ideas are better than three weak ones -- do not pad to 3 just to fill
the list). Do NOT classify ideas by scale (intimate/personal vs societal vs
radical) or by any other fixed category -- just judge which idea is most
genuinely interesting and story-worthy. Then pick the single most interesting one
to write as the article.
```

### After(新、Fiction、Future限定を除去)
```
You are brainstorming Core Provocations for a short fiction story in an
English-learning magazine's Fiction article family. A Core Provocation is a
single central idea or question -- regardless of whether the story takes place
in the real world, the future, an unreal/fantastical setting, or an
imagined/speculative world -- that would make a reader feel 'I want to know what
happens next' and 'I have never thought about it this way before'. Come up with 1
to 3 promising central ideas for the given theme (fewer, stronger ideas are
better than three weak ones -- do not pad to 3 just to fill the list). Do NOT
classify ideas by scale (intimate/personal vs societal vs radical) or by any
other fixed category -- just judge which idea is most genuinely interesting and
story-worthy. Then pick the single most interesting one to write as the article.
```

### 差分の要点
- "a short imagined-future story in an English-learning magazine's 'Future'
  article family" → "a short fiction story in an English-learning magazine's
  Fiction article family"
- "A Core Provocation is a single central idea or question about the future
  that would make a reader feel" → "A Core Provocation is a single central idea
  or question -- regardless of whether the story takes place in the real world,
  the future, an unreal/fantastical setting, or an imagined/speculative world --
  that would make a reader feel"(委任文の「現実・未来・非現実・仮想設定を問わず」を
  ここへ反映)
- それ以外の文(1-3案の方針/scale分類禁止/選定方針)は無変更(逐語)。

## 2. Prompt template(ユーザーメッセージ)

### Before(旧、v8run側の呼び出し形、inspiration_note付き)
```
[Theme]
{theme_label}

[Inspiration note -- a starting angle, not a rule to follow literally]
{inspiration_note}

[Task]
1. Propose 1 to 3 candidate Core Provocations for this theme. For each, give a short
   core_provocation (1-2 sentences) and why_interesting (1 sentence).
2. Pick the single one that would make the best short story for a reader who wants to
   feel the future, keep reading, and feel some excitement and a little tension.
   Set selected_id to that candidate's id and give a short selection_reason.
```

### After(新、DNA nudge + 共通原則を追加、inspiration_noteは今回未使用のため削除、
Future限定語句を除去)
```
[Theme]
{theme_label}

[Story DNA -- a creative nudge, not a contract]
Use the following elements as a nudge to move your thinking away from your default story. You may interpret them freely. Do not force them; if an element does not fit naturally, let it stay in the background.
{dna_lines}
Everything not listed here is yours to decide.

[Common principles for this story family]
A good premise here makes the listener want to know what happens next. Prefer concrete events over abstract or literary implication. Keep to a small cast, one time frame, and few places. Meaning may come at the end, but the story itself must be clear first.

[Task]
1. Propose 1 to 3 candidate Core Provocations for this theme. For each, give a short
   core_provocation (1-2 sentences) and why_interesting (1 sentence).
2. Pick the single one that would make the best short story for a reader who wants to
   keep reading and feel some excitement and a little tension. Set chosen_index to
   that candidate's 0-based index in the candidates array and give a short
   reason_for_choice.
```

### 差分の要点
- "feel the future, keep reading" → "keep reading"(Future限定語句を除去)
- `[Inspiration note]`ブロックを削除(このTrialではper-runのinspiration_noteを
  使わず、代わりにStory DNA nudgeブロックを新規挿入。委任文の指示どおり
  DNA nudge文を逐語で追加)
- `[Common principles for this story family]`ブロックを新規追加(委任文の
  共通原則を逐語で追加)
- 選定方式を`selected_id`(文字列ID)から`chosen_index`(0-based配列index)へ
  変更(委任文が明示的に指定したschema形に合わせた。schema自体の差分は下記3節)

## 3. JSON Schema

### Before(旧)
`candidates[].id`(string, required)を含み、`selected_id`(string)+
`selection_reason`(string)で選択。

### After(新)
`candidates[]`から`id`フィールドを削除(委任文のschema定義どおり
`core_provocation`/`why_interesting`のみ)。選択は`chosen_index`(0-based
integer)+`reason_for_choice`(string)で行う(委任文の逐語schemaに合わせた
呼称変更、`id`ベースから配列index方式への変更)。
