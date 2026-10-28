# CP_RESULT_02(委任_04、2026-10-28)

## 結論
std_adjust再実行(1回、承認済み経路 `--regenerate-stage std_adjust`)を実行。**CP基準(b)が不合格**: 性暴力の表現が再び明示的(`I forced her to have sex.`、出口の `with me` が落ちただけで直接表現は残存)。委任文どおり**再実行せず停止**。plan/support/kp再実行・Std選定フォーム公開は未実施(本文が未是正のため候補を作っても無駄)。

## 費用
- 本委任の有料API: std_adjust 1呼出 **¥9.8452**(旧 ¥10.5974。output 6,130 tok/reasoning 5,601 tok、attempts=1)。Cap¥20内。
- runner報告 spent_jpy=36.7941(runの累計表示。委任文の「22.00」+9.85=31.85と約¥4.9差。cost_log.jsonlにcost_jpy列が無く本agentでは差の内訳を未確認=**未確認**。Cap70内)。
- 起動1回のみ(RESTART_STORM無関係)。

## sha
- Std本文 旧 `7f9e52bb4e0500b3…`(6aa5c86dd0d6系、是正前)→ 新 `9bac8d94c67a117243e87ec9100770b4c5dd8cf9bd669c5126327f2d615ed7bd`
- 旧成果物退避: `docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/_superseded_01/`(writer/key_phrases/a2/support/study_text/segment_plan_a2.json等)。
- 来歴: downstream_stale=[plan_a2, part2_cand_a2, support_a2](kp_a2は旧entryのまま=再実行時に要regenerate)。
- Std review状態: kp/文法とも PENDING_REVIEW・selection空(Human未選定)。旧候補sha(KP 761026a5…/文法 c9124ec5…)は本文が変わったため失効扱い。フォーム未公開のため選定されない。
- Adv(b1b)は不変(候補sha 941647eb…/本文sha ee543393…)。

## CP検査(Fable再CP用)
- (a) 7証言順・3当事者の矛盾・結末(見えない手→闇へ沈む)・評決なし: OK(構成不変)。
- (b) **NG**: 11行 `She fought with her dagger, but I forced her to have sex.`(目標 `I took her by force.`)。
- (c) 創作なし: 新規の真犯人/証拠創作なし(OK)。
- (d) 語数422(旧422)/段落(非空行)14相当、行数15: OK。
- 付随の軽微な異常(Fable注記): 11行目のTajomaru台詞の閉じ引用符「”」が欠落(`...have sex.` で終わり、次段落13行は開き引用符のみ。旧版は同様に閉じ引用あり)。また旧版にあった導入句(`I killed him, but listen before calling me a coward`)が `I killed him fairly` に変わり、冒頭の証人説明も一部変化(他文も書換わっている=Std他文は不変でない)。

## 新Std本文(全文、writer/std.md)
# The Thicket

“I found him in the bushes this morning,” the woodcutter said. “He lay near the mountain road, stabbed once in the chest. The blood was already dry when I saw him. Broken bamboo and marks on the ground showed a fight. I found no sword or bow, only rope and a comb.”

“I saw the couple yesterday at noon,” the traveling monk said. “He carried a sword and bow, and his wife rode beside him.”

“I caught the famous bandit Tajomaru near the bridge,” the constable said. “He had fallen off a horse, but still had Takehiro’s bow. Find the wife and ask her what he did.”

“Takehiro, a kind samurai, married my daughter Masago,” the old woman said. “She is proud and only nineteen. Please find her before you send me home without news.”

“I killed him fairly,” Tajomaru said. “The wind lifted her face covering, and I wanted her. I promised him buried treasure and led him into the bushes. There I tied him to a cedar tree. She fought with her dagger, but I forced her to have sex.

“She held my arm and begged for one of us to die. She would leave with the man who lived. I freed him for a fair sword fight. Twenty-three blows—no other man had lasted twenty! She was gone when he fell. I took his weapons and left.”

“I crawled towards my husband,” Masago said at the temple. “The bandit had left him tied up. I begged him to die with me. His cold eyes said I was nothing, even though I was his wife.

“He moved his lips while I held my dagger. ‘Kill me,’ he said, so I stabbed him. I could not stand those eyes.

“I later tried drowning myself, but I failed. Where can I go after that?”

“I heard him speaking kindly to her,” Takehiro’s spirit said through a medium. “She asked him to take her anywhere. Then she pointed at me: ‘Kill that man.’

“He pushed her away and asked if she should live or die. I nearly forgave him then, but she ran away. He cut one rope and left me.

“I got up beside the cedar and picked up her small dagger. She had dropped it there. I pushed it into my own chest.

“The bushes around me grew quiet. Someone came slowly towards me on silent feet. A hand I could not see quietly pulled the dagger from my chest.

“I sank into the darkness and never came back.”

## 原因仮説と次の一手(Fable向け)
- 事実(観測): Adv `r2.md:11` は `...but I took her by force.`(CP許容の非グラフィック表現)。std_adjust入力(`std_adjust_prompt.txt:52`にも同文が含まれる)なのに、モデル(gpt-6.1-sol, effort high)が **2回とも(旧・新)** 当該文を `I forced her to have sex...` に書換えた。Advの文を保持せず、Stdで「平易化(説明化)」する際に明示化する傾向。Prompt(`std_adjust_prompt.txt`)に「性的表現を明示化しない/Advの当該表現を保持」の指示は無い(grep sex/forceで該当はAdv本文引用と一般記述のみ)。
- 再々実行(約¥10)は同結果の確率が高く推奨しない(2/2再現)。
- 候補: (1) CP処置規則(CURRENT_SPEC:1630(5))の置換patch拡張(exact 1文置換、API 0。仕様変更=ユーザー承認事項)。(2) std_adjust Promptへ保持指示を追加(Prompt変更=承認済み仕様変更、ユーザー承認事項)。(3) Std側で当該文を許容する(CP基準(b)緩和=ユーザー/Fable判断。ただし目標年齢層・Seed conversion_planに反する)。推奨=(1)(費用0、1文のみ置換、Adv同一文言の転用、再CP不要)。いずれも判断候補(区分D:新仕様/規則変更)。委任文どおり2回目以降はFable/ユーザー判断。
