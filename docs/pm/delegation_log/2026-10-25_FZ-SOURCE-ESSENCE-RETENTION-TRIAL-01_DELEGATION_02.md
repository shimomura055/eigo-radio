# 委任文(Fable→sonnet-worker)
管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02(Opus条件A必須修正1〜5+推奨の反映→DEV実装→Phase 1[1a対照実験3アーム→1b全段2本→合格時のみAdv音声化]→基準を満たせばPhase 2[既存Z作品3本テキスト]へ継続)
前提: 委任_01(RESULT_PACKET_FZSE1.md、ROOT_CAUSE_01.md、DESIGN_01.md、commit 5c355327f)。**Fable判断: Opusレビューは案A(Seed→essentials→全段Must-keepで語り口を運ぶ)を妥当とし必須修正5件。設計と実質一致・新仕様のProduction採用は含まない・DEV/Trial専用・自律枠内(案件上限150円、Opus見積約121円+予備16円)。修正反映後にPhase 1へ進んでよい(Fable Go)。Production採用・『告げ口心臓』の再生成・公開差替えは含まない。**

## 0. 最初に
- `docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/OPUS_REVIEW_01.md` を作成し、§1のOpusレビュー全文を保存(先頭に「Fable転記、2026-10-25、条件A」)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 506 --out docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_DELEGATION_02.md`。冒頭が「管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02」と一致するか確認、不一致なら index 504〜509 を順に試す(`--index -1`不可)。

## 1. Opusレビュー全文(逐語)
```
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
```

## 2. Fable判断(反映指示)
- 必須修正1〜5: 全て反映(DESIGN_02.md に反映後の設計、Seed記入規則、Narration行文言、1a 3アーム構成、修正後の評価基準。**評価基準は生成前にcommit**)。ROOT_CAUSE_01 §5の過去Trial照合を訂正(er055 NEUTRAL_CONVERSION_PLANの先例を21節Bとして記録、「不採用」ではなくTrial内の汎用文言の先例。今回(ii)アームとして対照に使う)。
- 推奨: Phase 2は『賢者の贈り物』を最初に。ノイズ帯の限界を報告に明記。`_CONVERSION_SUBSTITUTIONS`雛形を一人称作品に流用しない規則をSeed作成手順に1行。
- 予算: 案件上限150円(Phase 1 1a≈17円+1b≈32円+1c≤12円、Phase 2≈45円、予備16円)。費用台帳 `BUDGET_LOG_01.md`(出典=provenance.json/cost.json)。有料run起動は最小回数、同一run起動間隔150秒以上、再起動回数記録、TTS直列化flag尊重。
- モデル: Production同一(Writer/R1/R2/Std/音声)。評価LLMは使わない(決定論指標+Fable盲検読み。Fableが読む比較原稿を用意する)。

## 3. 実装(DEV/Trial専用、Production file編集禁止)
- DEV runner(メモリ上差替え、`sftrial_dev_runner_01.py`同型)+DEV Seedコピー(`narration_voice`追加、必須修正1〜3反映、free_to_cut修正)。Production Seed(`er026_output/.../the_tell_tale_heart/seed/`)・`er026_seeds/`・Production runner/writerは不変。出力は `er026_output/family_z_dev_trials/fz_essence_01/<story>/<arm>/`等のDEV dirのみ。flag新設なし。DefaultOffIsolation test(欄がないProduction Seedでは従来とbyte同一のPrompt)。
- Production到達経路への新機能0を `git status`/Production file差分0で確認。

## 4. Phase 1(『告げ口心臓』)
- 1a: `r0.md`固定入力でR1のみ生成、3アーム×2本: (i)現行文言 (ii)汎用置換のみ・欄なし(B') (iii)案A。決定論集計(一人称語/三人称語/you/語数/文長)+比較原稿。
- 1b: 案A(1aで(iii)が(ii)より語りの質で優位、または同等なら最小の案を採用=Fableへ理由を報告)で全段チェーン R0→R1→R2→Std を2本。評価=修正後基準(Adv一人称維持、Std you≥1かつAdvと人称一致、過剰忠実[youがr0の2倍超]なし、語数・文長が既存3点[1b 2本+sf_prod]の幅内、心理・心臓音・自白・因果の保持)。
- 1c: 1bが基準を満たした場合のみ、Adv 1本を既存Z正式TTS/Gate経路のDEV呼び出しで音声化(≤12円、HR Lock発生時は停止・approve_regenerate禁止)。試聴ページ `user_test/fz_essence_trial_01/index.html`(現行Adv[三人称]とTrial Adv[一人称]の比較、比較原稿へのリンク)。公開版 `user_test/family_z_tell_tale_heart_01/` は不変。
- 比較原稿 `COMPARISON_01.md`: 原作抜粋/現行Adv/Trial Adv/Trial Stdを並べ、Fable盲検7観点(語り口・心理・緊張・心臓音・自白・因果・テンポ)の読み合わせ用。
- 1aで(i)が反転を再現しない場合は原因仮説を見直してFableへ報告(1bへ進まない)。

## 5. Phase 2(既存Z作品、テキストのみ)— Phase 1が基準を満たした場合のみ同一委任内で継続
- 順序: 『賢者の贈り物』→『開いた窓』→『猿の手』(各DEV Seedコピーに`narration_voice`を記入規則どおり追記、各1本全段)。評価=修正後基準(三人称維持、地の文の一人称は原作にもある語り手論評に限る[引用で確認]、語数・文長・段落数の副作用、Fable読み用比較原稿)。公開版不変。
- `PHASE2_RESULT_01.md`。

## 6. 文書・SSOT・Git・報告
- `DESIGN_02.md`、`PREREGISTERED_CRITERIA_01.md`(生成前commit)、`PHASE1_RESULT_01.md`、`PHASE2_RESULT_01.md`、`COMPARISON_01.md`、`TRIAL_RESULT_01.md`(ユーザー原文§8の1〜10に対応する事実、Status候補はSonnet所見)、`ADOPTION_NOTE_01.md`(採用時の必要作業: Production writer文言置換、全essentials Seedへの1行追記、REVISE逐語test fixture更新、『告げ口心臓』再生成要否=ユーザー判断候補、撤退=revert)、`BUDGET_LOG_01.md`。
- SSOT: OPEN-508 Status更新、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行のみ(並行agent: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02、FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_05 が同時編集中。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認(OPEN_ITEMS.mdはCRLF/LF混在に注意)。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0・wav/telemetry不混入、公開mp3は`user_test/`配下のみ) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。
- 報告 `docs/pm/RESULT_PACKET_FZSE2.md`: ①必須修正1〜5の反映、②1a結果(3アーム比較、反転再現の有無、欄の要否)、③1b結果(基準判定、決定論指標、比較原稿所在)、④1c音声化・試聴URL(実施時)、⑤Phase 2結果(実施時)、⑥費用(Phase別実費/上限150円)・有料run記録(起動回数・JST・再起動)、⑦量産単価増分、⑧Status候補と根拠、⑨ユーザー判断候補(J: 『告げ口心臓』再生成・差替え、Production採用)、⑩変更ファイル・commit、⑪`check_delegation_prompt.py`結果、⑫問題点・限界。

## 7. 禁止
Production code/Prompt/Seed/flag/閾値の変更、公開版・Production出力の変更、Validator/Check追加を主対策にすること、作品固有の禁止文・内容ノルマのSeed記入、Gate迂回・approve_regenerate、Cap超過、Web検索、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction採用・配線・『告げ口心臓』の正式再生成へ進まない。