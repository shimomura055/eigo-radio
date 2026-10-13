# ADV_STYLE_FACTCHECK_02 (OF-X10、API 0円、2026-10-13)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02。TTSなし。`er071_style_factcheck_02.py`で生成(style解決関数の直接呼出+results読取)。

判定ルール(Fable既定): (i)元run(e_tone_01)のstyleが承認Styleと一致→seed+引継ぎ / (ii)不一致かつmain runner `coffee_n01_r2_p3`の解決styleが承認Styleと一致→正式経路で再生成 / (iii)両方不一致→STOP(approved-but-unwired)。

## b1b(Adv)

| segment | 承認Style(出典) | 承認sha | e_tone_01実style sha | e_tone一致 | main解決style sha | main一致 | 判定 |
|---|---|---|---|---|---|---|---|
| topic_intro | `brief, clear, engaging news topic introduction wit...` (可変segment Role Style節: EN TOPIC_INTRO=E2(現行定数FAMILY_X_ROLE_STYLE_EN)。Coffee限定のIntro A5/B5は固定Master phrase(welcome/preview_intro)用) | `d16e099cb4f6` | `d16e099cb4f6` | 一致 | `d16e099cb4f6` | 一致 | (i) seed+引継ぎ |
| preview | `calm, composed news anchor; steady and unhurried, ...` (L2620: Advanced Preview=E1(er057_tone_trial_tts_gen_01.py SPECS['E']['E1'])) | `8862317ff766` | `37c52d6ec237` | 不一致 | `57c3fda67c1d` | 不一致 | (iii) STOP: approved-but-unwired |
| comment_1 | `calm, conversational...` (可変segment Role Style節: PREVIEW/COMMENTはE2未検証のためE0のまま(=現行定数)。Coffee限定のComment Style決定記述はCURRENT_SPECに無い) | `57c3fda67c1d` | `37c52d6ec237` | 不一致 | `57c3fda67c1d` | 一致 | (ii) 正式経路で再生成 |
| comment_2 | `calm, conversational...` (可変segment Role Style節: PREVIEW/COMMENTはE2未検証のためE0のまま(=現行定数)。Coffee限定のComment Style決定記述はCURRENT_SPECに無い) | `57c3fda67c1d` | `37c52d6ec237` | 不一致 | `57c3fda67c1d` | 一致 | (ii) 正式経路で再生成 |
| comment_3 | `calm, conversational...` (可変segment Role Style節: PREVIEW/COMMENTはE2未検証のためE0のまま(=現行定数)。Coffee限定のComment Style決定記述はCURRENT_SPECに無い) | `57c3fda67c1d` | `37c52d6ec237` | 不一致 | `57c3fda67c1d` | 一致 | (ii) 正式経路で再生成 |
| comment_4 | `calm, conversational...` (可変segment Role Style節: PREVIEW/COMMENTはE2未検証のためE0のまま(=現行定数)。Coffee限定のComment Style決定記述はCURRENT_SPECに無い) | `57c3fda67c1d` | `37c52d6ec237` | 不一致 | `57c3fda67c1d` | 一致 | (ii) 正式経路で再生成 |
| in_one_line | `concise, clear, landing naturally as a settled con...` (L2620: In One Line=既存承認Style(=FAMILY_X_ROLE_STYLE_EN['IN_ONE_LINE']=E2)) | `63495557ec82` | `63495557ec82` | 一致 | `63495557ec82` | 一致 | (i) seed+引継ぎ |

## a2(Std)

| segment | 承認Style(出典) | 承認sha | e_tone_01実style sha | e_tone一致 | main解決style sha | main一致 | 判定 |
|---|---|---|---|---|---|---|---|
| topic_intro | `brief, clear, engaging news topic introduction wit...` (同上(E2)) | `d16e099cb4f6` | `d16e099cb4f6` | 一致 | `d16e099cb4f6` | 一致 | (i) seed+引継ぎ |
| japanese_title | `落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技が...` (可変segment Role Style節: JA=J3(japanese_titleも対象、W3)) | `ae68e3e6ac8e` | `fb2087f4d62c` | 不一致 | `ae68e3e6ac8e` | 一致 | (ii) 正式経路で再生成 |
| preview | `明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリ...` (L2624(C): Standard Preview/Comment1-4=R2) | `625826c1187b` | `fb2087f4d62c` | 不一致 | `625826c1187b` | 一致 | (ii) 正式経路で再生成 |
| comment_1 | `明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリ...` (L2624(C): Standard Preview/Comment1-4=R2) | `625826c1187b` | `fb2087f4d62c` | 不一致 | `625826c1187b` | 一致 | (ii) 正式経路で再生成 |
| comment_2 | `明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリ...` (L2624(C): Standard Preview/Comment1-4=R2) | `625826c1187b` | `fb2087f4d62c` | 不一致 | `625826c1187b` | 一致 | (ii) 正式経路で再生成 |
| comment_3 | `明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリ...` (L2624(C): Standard Preview/Comment1-4=R2) | `625826c1187b` | `fb2087f4d62c` | 不一致 | `625826c1187b` | 一致 | (ii) 正式経路で再生成 |
| comment_4 | `明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリ...` (L2624(C): Standard Preview/Comment1-4=R2) | `625826c1187b` | `fb2087f4d62c` | 不一致 | `625826c1187b` | 一致 | (ii) 正式経路で再生成 |
| in_one_line | `concise, clear, landing naturally as a settled con...` (既存承認Style(E2)+Standardの既承認減速instruction) | `10e21170b1b1` | `10e21170b1b1` | 一致 | `10e21170b1b1` | 一致 | (i) seed+引継ぎ |

## e_tone_01実styleの文言(参考)

- b1b/topic_intro: sha `d16e099cb4f6` / `'brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.'`
- b1b/preview: sha `37c52d6ec237` / `'warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.'`
- b1b/comment_1: sha `37c52d6ec237` / `'warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.'`
- b1b/in_one_line: sha `63495557ec82` / `'concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.'`
- a2/topic_intro: sha `d16e099cb4f6` / `'brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.'`
- a2/preview: sha `fb2087f4d62c` / `'明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。'`
- a2/comment_1: sha `fb2087f4d62c` / `'明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。'`
- a2/in_one_line: sha `10e21170b1b1` / `'concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.\nSpeak at a slightly slower,'`
- a2/japanese_title: sha `fb2087f4d62c` / `'明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。'`

## main runner (coffee_n01_r2_p3) 解決style(参考)

- b1b PREVIEW/COMMENT: `'calm, conversational'`  (E1は未配線: PREVIEW定数は'calm, conversational')
- b1b TOPIC_INTRO: `'brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.'`
- b1b IN_ONE_LINE: `'concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.'`
