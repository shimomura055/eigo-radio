Fable転記、2026-10-25、条件A

## Opus独立レビュー(条件A) FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 Phase 1前

### 判定: 条件付きで進行可(Phase 1前に必須修正5件)
方向性(Validatorは足さず、Seed→essentials→全段のMust-keepで語り口を運ぶ)は妥当で、ユーザー原則§4にも合っています。ただし、原因の一部(key_rolesの描画文言)と、新しい行の文言・評価基準に穴があります。この穴を残したまま1aと1bを回すと、結果を正しく解釈できません。

### 観点別の所見(要点のみ)
**(a) 根本原因**: 証拠に基づいており十分です。固定文言の由来は`er059_melos_sol_b3z_trial_01.py:83-87`で、Family X W-1の文言をメロスA2用に最小限変えたものです(同じ文に"only Melos may have a personal name"がある)。三人称作品では、R0がconversion_planの三人称指定で既に三人称を書くため、この文言は念押しにすぎず、外しても挙動はほぼ変わらない見込みです(Phase 2で確認)。
- 見落とし1(寄与要因): `_render_essentials_block`(`er062_family_z_writer_01.py:424`)は、keep_name=falseの人物すべてに「refer to this person by role or relationship, without a name」と描画します。語り手が一人称の作品では、これが「外から呼称で描け」という指示として働き、"in third person"と組み合わさって"the old man's housemate"を生んだと読むのが自然です。案Aはこの点に触れていません(必須修正1)。
- 見落とし2(過去Trial): `er055_family_z_d_predictive_validation_trial_01.py:135-143`の`NEUTRAL_CONVERSION_PLAN`に、汎用文「Keep the original point of view (first person if the original is first person, third person if it is third person)」があります。ROOT_CAUSE_01 §5の「過去Trial 0件」は不正確なので訂正し、照合記録を残してください。これは「Seed欄なしの汎用文言置換」という対照案にもなります(必須修正4)。

**(b) 上流で生成されない設計か**: 構造としては上流です。非空検査とCPチェックリスト1行は、Seed記入規則と確認入口の補修であり、本文Validatorには当たらないという整理で問題ありません。ただし、1文で守れるのは人称と語り手の立場(呼びかけ)までと見るべきです。自己陶酔などの「語りの質」が残るかは未検証で、さらに下記の矛盾で弱められています。DESIGN §3-3のように「1〜2例は残す」をnarration_voiceへ寄せると、この欄が作品別の内容ノルマ置き場になり、記述が増えていく入口になります(必須修正3)。

**(c) Std調整段**: Stdは「Adv最終が正しい人称であること」と「std modeへ同じ行を描画すること」の二重で担保され、設計上は十分です。今回Stdが一人称に戻った原因は、key_rolesの"first-person speaker"という語句が引力になったことと見られます。この推定は(a)の見落とし1と整合します。

**(d) 「欄がある作品でのみ置換」の分岐**: Trial中は、Production SeedとのDefaultOffIsolation(既定OFFの隔離確認)のために必要で、問題ありません。採用時はnarration_voiceを全essentials作品で必須にしてください。そうすれば置換の条件は既存の「essentialsの有無」(名前置換と同じ切替。Melosだけが従来どおり)と一致し、3状態目は生まれません。これは作品別例外ではありません。既存4作品のSeedに1行追記すれば足り、公開版は変わりません。

**(e) 整合**: 修正版B(`COMPREHENSIVE_DESIGN_02.md` §3-5のSeed全文を渡さない方針)と矛盾しません。未実装の`tone`もこれで回収できます。Voice構造(`er062_family_z_structure_01.py:316-318`は一人称前提)や話者表の変更が不要という判断も妥当です。ただし、free_to_cut「narrator's repeated arguments that he is wise and cunning」(seed.json:63)とnarration_voice「relishing his own cunning」は、同じSeedの中で正面から矛盾しています。

**(f)(g)**: 下記の必須修正5と「Phase構成・費用」を参照してください。

**(h) 影響範囲**: X/Yへの波及はありません(import元はZ専用、X側はKP関係のtestだけ)。撤退は容易です。採用時の作業は、REVISE文言を逐語で固定しているtest(`er026_family_z_story_registry_open_window_test_01.py:180-181`など)のfixture更新と、全essentials Seedへの1行追記です。

### 必須修正(Phase 1の有料起動前に反映)
1. **key_roles描画との衝突を解消する**: Seed記入規則で、narration_voiceの第1項目に「語り手が自分をどう指すか(例: the narrator speaks as 'I' / no narrator in the story)」を必ず書くようにしてください。あわせてNarration行をKey people行より前に描画し、「人物の役割説明は語り手を外から呼ぶ指示ではない」と汎用の1句を添えてください。作品別の分岐は作りません。
2. **Narration行の文言を直す**: 「keep exactly as in the original」はやめます。理由は2つあります。R1/R2/Stdには原作が渡らないので「as in the original」を参照できないこと、そして「exactly」は過剰な忠実を招き、ユーザー原則(言い回し・長さ・構文は変更可)とずれることです。置換案は「Keep this narration throughout: the same person, point of view and narrator's stance (including how he speaks to the listener); wording, length and sentence structure may change.」です。Seed例文の末尾にある「do not retell it in the third person」も削除し、禁止はテンプレート側の汎用文に一本化してください。Seedは記述だけにすることで、作品別の禁止文が増えるのを防げます。
3. **free_to_cutとの矛盾をSeed側で解く**: 汎用の記入規則として「free_to_cutにnarration_voiceの担い手(語りの質の源)を丸ごと入れない。削れるのが繰り返しだけなら『repetitions of …』と書く」を追加してください。DEV Seedコピーではfree_to_cut側を直し、narration_voiceは3点の記述に留めます(「1〜2例は残す」のような内容ノルマは入れない)。
4. **1aを3アーム×各2サンプルにする**: (i)現行の文言 (ii)汎用置換のみで欄なし(案B'。例「in the same point of view and narration as the story above」、er055の先例と同型) (iii)案A。これで「反転の原因が文言か」に加え、「Seed欄が本当に要るか(人称は(ii)で足り、語りの質だけAが要るのか)」も切り分けられます。後者が分からないと、DESIGN §2のA>B評価に裏付けがありません。費用は約17円(現案5.6円から+11円)です。
5. **評価基準をgenerate前に修正してcommitする**:
   - 三人称作品の「一人称語≤2」は、『賢者の贈り物』で誤判定のおそれがあります。原作に語り手の直接介入「here I have lamely related to you」(`er026_seeds/the_gift_of_the_magi/story.md:87`)があり、「narrator who comments」と書けばこれが誘発されうるためです。基準は「完成版+ノイズ帯以内、かつ地の文の一人称は原作にもある語り手の論評に限る(Fableが引用で確認)」に変えてください。
   - 一人称作品のStd「you≥2」は、Stdが段落整列と簡略化で呼びかけを1つ落としやすいため、厳しすぎて偶然の不合格を生みます。「Std you≥1、かつAdvと人称が一致」を推奨します。
   - 過剰忠実の上限として、「you」が多すぎて単調になる場合(例: r0の2倍超)もFable読みの観点に入れてください。

### 推奨(任意)
- Phase 2は『賢者の贈り物』を最初に回してください。語り手介入の副作用が最も出やすく、早期撤退の判断材料になります。
- ノイズ帯の注意: 既存の複数run(pntrial/sftrial/sf_prod)はPromptがそれぞれ違うため、純粋なサンプリング揺れより幅が広く、判定は甘くなります。報告では限界として明記してください。『告げ口心臓』については、1bの2本と既存sf_prodの計3点で幅を見る方が誠実です。
- `_CONVERSION_SUBSTITUTIONS`(`er062_family_z_writer_01.py:130-134`)は"third-person English"を含む正規表現です。一人称作品のSeedにこの雛形を流用しない規則を、Seed作成手順に1行書いてください(DESIGN §3-1で既に触れており、手順書への反映だけです)。

### Phase 1/2の構成と費用
- 構成は妥当です。言えることと言えないことは次のとおりです。
  - 1a(各2本): 文言が原因であることの強い示唆と、欄が要るかの見当はつきます。
  - 1b(2本): 「系統的には反転しない」とまでは言えますが、失敗率は推定できません。
  - Phase 2(各1本): 大きな副作用の検出に限られ、「挙動不変」の証明にはなりません。
- 1a拡張(+約11円)を入れて約121円で、上限150円の内に収まります。予備16円も維持できます。音声化(1c)はAdvのみで足ります。

### リスクと対処
- 1文では語りの質までは届かない可能性があります。1aの(ii)と(iii)の差、および盲検観点2・3で判定し、届かなければ撤退条件(2)で見直します(同じ方向の文言の反復はしない)。
- R1の"more engaging"とNarration行が拮抗し、テンポが落ちる可能性があります。語数・文長に加え、Fable読みで判定します。

### ユーザー判断候補(現時点でブロックするものはなし)
- 採用後に『告げ口心臓』を再生成・差し替え公開するか(現行の公開版はAdvとStdで人称が食い違ったまま)。Trial結果が出た後に、Production採用の判断と合わせて提示してください。Production採用(APPROVED_FOR_PRODUCTION)を承認できるのはユーザーだけです。本レビューは採用可否を判断していません。
