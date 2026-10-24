# PHASE2_RESULT_01: 既存Family Z作品への横展開(テキストのみ、案A、各1サンプル全段、実費50.34円)

作成: 2026-10-25 / 基準=`PREREGISTERED_CRITERIA_01.md` §4(生成前commit)。採用アーム=(iii)案A(1a規則による)。各DEV Seedコピー(`dev_seed/<story>/seed.json`)に`narration_voice`のみ追記(free_to_cut等は無変更、作品別の禁止文・内容ノルマなし)。順序: 『賢者の贈り物』→『開いた窓』→『猿の手』を同時起動(独立作業のため並列。3 process、JST 08:10:52起動、各1 launch、再起動0)。出力=`er026_output/family_z_dev_trials/fz_essence_01/<story>/p2_s1/writer/`。比較原稿=`COMPARISON_02.md`(完成版 vs Trial 全文)。**公開版・完成版は不変**。

| 作品 | narration_voice(第1項目=自称) | 実費 |
|---|---|---|
| 賢者の贈り物 | The story is told in the third person by an outside narrator, close on Della and Jim, in a warm, gently ironic voice. | 16.93円 |
| 開いた窓 | The story is told in the third person by an outside narrator, close on Framton, in a cool, dry, matter-of-fact voice that plays the events straight. | 15.63円 |
| 猿の手 | The story is told in the third person by an outside narrator in a quiet, restrained voice; the fear comes from sounds, silence and what the characters say and do. | 17.79円 |

## 決定論指標(完成版 `run_sf_prod_01` との比較)
| 作品/本文 | 語数 trial/完成版 | 段落 | 平均文長 | 地の文の一人称語 | 地の文のyou |
|---|---|---|---|---|---|
| 賢者 Adv | 433 / 428 | 27 / 30 (−3) | 8.49 / 7.64 (+11%) | 0 | 0 |
| 賢者 Std | 440 / 443 | 27 / 30 | 9.36 / 9.23 | 0 | 0 |
| 開いた窓 Adv | 426 / 434 | 25 / 29 (−4) | 8.35 / 7.75 (+8%) | 0 | 0 |
| 開いた窓 Std | 439 / 422 | 25 / 29 | 8.61 / 8.61 | 0 | 0 |
| 猿の手 Adv | 420 / 430 | 40 / 32 (**+8**) | 5.68 / 5.73 | 0 | 0 |
| 猿の手 Std | 438 / 439 | 40 / 32 | 7.18 / 7.08 | 0 | 0 |
- 人称不変 ○(3作品とも地の文の一人称語0、三人称語は維持。『賢者の贈り物』の語り手介入"here I have lamely related to you"(`er026_seeds/the_gift_of_the_magi/story.md:87`)は誘発されなかった=Opusの懸念した副作用なし)。Stdも同じ。
- 語数330〜470 ○、平均文長±25% ○(Adv・Std全て)。
- 段落数: 賢者−3 ○、開いた窓−4 ○(±4、境界)、**猿の手+8 ×(事前基準±4の未達)**。猿の手はTrial r0=45・r1=47・r2=40、完成版もr0=48・r1=38・r2=32とstage間で±10揺れるため、揺れの範囲内に見える。参照が完成版1点のみで確定はできない(限界)。語数・文長は不変なので「長くなる・冗長になる・テンポ悪化」の副作用は決定論上は見られない。Std/Adv段落一致は全作品保持(WARN=soft gateのみ)。
- `check_std_guardrails` failures 0(3作品)。猿の手Stdの同一文比率0.164(上限未満)。

## essentials保持(Sonnet読み、引用)
| 作品 | ending_reveal | 主要人物 | 備考 |
|---|---|---|---|
| 賢者 | “They were the magi.”(Adv)/“They are the true magi.”(Std)。伏線(髪→櫛、時計→鎖)保持 | Della・Jim維持、店主はthe ownerで無名 | 語り口は完成版より軽い皮肉("Their furniture might not impress anyone, but those two things could.")だが語り手の直接介入はなし |
| 開いた窓 | “Inventing convincing stories at a moment’s notice was Vera’s speciality.”(Adv)/Std "Vera was very good at inventing believable stories..."。窓・3人の姿・歌・犬の嘘の伏線保持 | Framton・Vera維持 | 完成版とほぼ同等 |
| 猿の手 | “The street lamp opposite shone on a quiet, deserted road.” | Mr. White・Mrs. White・Herbert維持。軍曹・firmの男は無名 | 完成版と同等。会話中心のため段落が多い |
欠落0(Sonnet読み)。

## 副作用の所見(Fable読みの観点、Sonnet暫定)
- 三人称作品で挙動は大きく変わらない(人称・語数・文長・結末が維持)。一方、narration_voiceの語り口語句("gently ironic"、"dry")が弱い文体傾向として出る程度で、冗長化・テンポ悪化は見られない。
- 限界: 各1サンプルで「大きな副作用の検出」に限られ、「挙動不変」の証明ではない。完成版との比較は1点。段落数(猿の手+8)はノイズか副作用か未確定。
- 採用時は全essentials作品でnarration_voiceを必須にする(DESIGN_02 §3)。三人称作品の記入は1行(上表)でよく、記入規則どおり作品別の禁止文は不要だった。
