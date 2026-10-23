# OPEN_WINDOW_FIX_PLAN_01: 『開いた窓』の結末復元・修正方針(設計のみ。完成音声の修正・再生成は未実施)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01A / 区分A / 2026-10-23 / read-only・API 0
対象: `er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`。Production音声・本文・Promptは**無変更**(ユーザー原文§7「現段階では完成音声の修正・再生成は行わない」)。
前提: 原因は`ROOT_CAUSE_01.md`。固有名詞(Vera)の効果は並行の委任_01B(区分C Trial)の結果と突き合わせる前提で、ここでは設計条件だけを示す。

## 1. 現行本文の構成確認(伏線・展開は無傷か)
Advanced(`writer/r2.md`、30段落)の対応箇所(本文引用は`r2.md`)。

| 要素 | 本文の位置 | 状態 |
|---|---|---|
| 窓が開いている理由の問い | p5-6 `Her eyes moved to the French window, open to the lawn.` / `You may wonder why that’s open in October.` | 保持 |
| Veraの最初の作り話(悲劇) | p8-10 `Three years ago today… all three sank into a bog… The bodies were never found.` | 保持 |
| 細部(白いコート・歌・茶色の犬)と声の揺らぎ | p12-14 `white waterproof coat` / `Oh, brother, why do you bound?` / `The girl swallowed.` / `I almost feel they really will—` | 保持(Bertie→brother置換は名前方針による) |
| 叔母の「確証」行動 | p16-20 `You don’t mind the open window?` / `kept looking past him towards the lawn` / `Here they are at last!` | 保持 |
| 男たちの帰還・歌の回収・Framtonの逃走 | p22-25 `Three men… One had a white coat… A tired brown spaniel…` / `Oh, brother, why do you bound?` / `forcing a passing cyclist into the hedge` | 保持 |
| 叔母の「幽霊」発言 | p28 `You’d think he’d seen a ghost.` | 保持 |
| 犬の作り話 | p29-31 `It was the spaniel… cemetery… empty grave… He said they took turns.` | 保持(最後の小ネタは原作に無い追加) |
| **語り手の種明かし** | (原作最終文) | **欠落** |

所見:
- 欠けているのは**最終1文のみ**。伏線(窓・白いコート・歌・犬)は全て人影の場面で回収されており、展開の修正は不要(上表)。
- 欠落の影響: 聞き手が「少女の犬の話」を、客が実際に怖い目に遭った話と受け取りうる(p29は"He told me…"と客の発言として語られ、Veraが作ったとは明言されない)。最終文が唯一、語り手の視点で「全部その場の作り話」と確定させる。
- 副次ドリフト(参考のみ。今回は修正対象にしない): Std歌詞が`why do you bound`→`why are you jumping`に変化(p12,p24でStd内は整合)。

## 2. 検討項目への回答
(a) **オチ1文の補完で足りるか → 足りる。** 伏線・因果は無傷で、欠落は最終文のみ。
(b) 伏線・展開の修正 → **不要**(上表)。
(c) **Vera名を残す効果**:
- 最終文は"her speciality"と代名詞受けで、名前が無くても文としては成立する。ただし聞き手は耳だけで追うため、「少女=作り話の達人」というキャラクターの像を名前で固定すると、種明かしが"Veraという人物の正体"として記憶に残りやすい(推測、聴取評価は未実施)。
- 名前の自然な導入位置(設計条件): 叔母の台詞(p17相当)`I hope Vera has entertained you.`(Framtonが少女の名前を初めて聞く)、および p29の`Vera said calmly.`。Veraの台詞はSpeaker `vera`として既に配役済み(`segment_plan_*.json`のspeaker=`vera`)で、Voice設定への影響は無い。
- 同時に注意: `STORY_LINT_CONFIG["the_open_window"].forbidden_names`に`ヴェラ`が含まれる(`er062_family_z_structure_01.py:810`、Preview/Commentに適用)。名前維持を正式化するときは、この禁止設定を同時に見直す必要がある。本文のNAME_RULE_NOTE(`er062_family_z_writer_01.py:417`)はWARNのみで影響なし。
- 判断は01Bの固有名詞Trial結果(共通ルールのみでVeraが残ったか)と突き合わせて確定する。本設計はVera有/無の両方に適用できる。
(d) **Std/Advの修正範囲**: 段落単位。両レベルとも**末尾に1段落(narratorの最終文)を追加**。段落数は30→31で両レベル一致(Std/Adv段落対応を維持)。Part3の語数比は20〜45%条件を満たす見込み(下記)。
(e) **既存音声の再利用**: 既存の話者別clip(Adv 34/Std 34のStory clip、Intro/Preview/Comment/KP等)は本文が変わらないため再生成不要(Store keyは本文・Voice・Styleで決まる=`OPEN_ITEMS.md` OPEN-428「Store key speaker_voice」、未確認事項: plan再実行時のclip ID再割当)。新規TTS = narratorの最終文clipのみ(各レベル1)。ASR・Azure phrase list・shared_gateは新規clipに対して通常どおり。組立(assemble)と試聴ページ再公開は再実行(ローカル+Pages)。
(f) 費用・工程見積: 次節。

## 3. 案(2案、推奨1)
### 案1(推奨): 最小補完案
- Advanced: 末尾に原作の最終文をそのまま追加(パブリックドメイン): `Romance at short notice was her speciality.`(7語)。
- Standard(A2): 意味(「その場で作り話を作るのが得意」)を保つ平易化。案: `Making up stories on the spot was her special talent.`(10語)。`romance`(「空想物語」の古い意味)は初級に不向きなため`Making up stories`で意味を保つ。最終語はFable/ユーザーが確認(約1円以下のLLM補助で複数案を作る場合は別途)。
- 語数: Adv 431→438、Std 455→465(目標330〜470の範囲内、超過してもWARNのみ)。Part3語数比: Adv (140+7)/438=33.6%、Std (154+10)/465=35.3%(20〜45%条件内)。
- 分割: 既存`boundaries [9,20]`を維持(Part3=段落20〜30、末尾にnarrator clip `full_story_part3_c14`相当を1つ追加)。plan stageを再実行する場合はLLMが境界を選び直す可能性があるため、境界固定または既存planへの決定論的パッチが望ましい(実装時の確認事項。Store keyは本文基準のため再割当が起きても既存clipは再利用できる見込み、**要確認**)。
- 影響: Preview/Comment/KPは変更不要(最終文はspoilerとして扱うため元々Previewに含めない。`romance at short notice`はsupport lintのspoiler語、`er062_family_z_structure_01.py:811`)。KP候補は本文全文から選定されるので最終文が候補化するか実行時に確認。
- 固有名詞(Vera)を加える場合の追加範囲: 叔母の台詞clip(Part2、Std/Advで各1〜2clip)、`the girl said calmly`のnarration clip(Part3 c10)、`The girl swallowed`/`stared`などの"the girl"をVeraに置換するかは01B結果で決定。置換箇所が多いほど再TTS clipが増える(推定 各レベル+3〜6clip)。

### 案2: 構成修正案(再生成)
- 案Bの`source_essentials`(`COMPREHENSIVE_DESIGN_01.md`)を使い、R0〜Std調整を再生成して本文全体を作り直す。
- 利点: 新方針(Writer Prompt改善)の実地検証を兼ねる。欠点: 伏線は無傷のため品質上の必要性は低く、Prompt採用承認(未)・Trialが前提。全Story clipの再生成が必要で、ユーザー試聴待ち(REGISTER #157)の既存評価も無効化する。

### 推奨: **案1**
理由(QDC): 品質=欠落した本質要素を復元し、伏線・展開は既存の承認済み成果を維持/ 速度=最小工程、案Bの承認を待たずに実施可能/ 単価=下記のとおり数円。案2は案B採用後に別Workで作品を再生成する必要が生じた場合のみ。

## 4. 費用・工程見積(案1)
出典: `run_e2e_01/e2e_stage_log.jsonl`(tts_b1b段 19.33→40.03円=20.7円/Advanced全体、上限見積に使用)、`cost_log.jsonl`(gemini TTS b1b 49回/a2 54回)、`writer/provenance.json`(writer 8.22円・std 9.54円)。
| 項目 | 見積 |
|---|---|
| 本文編集 | LLM再生成なし(Adv=原作文、Std=手書きまたは補助1回 約0.5円以下) |
| plan再実行(必要な場合のみ) | 約0.2円(`e2e_stage_log` plan段 17.76→18.00円) |
| TTS+ASR+Azure(新規narrator clip 2本、retry余裕込み) | 約0.8〜3円(1clipあたり約0.4円=Adv 20.7円/49 TTS呼出から按分した上限) |
| Vera置換を伴う場合の追加 | +3〜6clip/レベル=約3〜10円(01B結果次第) |
| 組立・Pages再公開・Playwright | ローカル作業(API 0)、既存手順 |
| **合計** | 約1〜4円(Vera置換なし)、約5〜14円(Vera置換あり)。量産単価への影響は作品再生成ではなく1回限りの是正で、新規の継続費は生じない |
工程: 本文決定(Fable/ユーザー確認)→plan固定/再実行→TTS 2clip+gate→assemble 2本→Pages再公開→再生検証。実行時間は数十分〜2時間程度(ASR/gate含む。見積、実測は別途)。

## 5. 実施前の依存・順序(並列化メモ)
- 並行する未決: OPEN-462(Std/Adv会話速度A/B、ユーザー判断待ち)。判断後に実施しないと再組立が二度になる。
- 01B(固有名詞Trial)の結果でVera置換の要否が決まる。置換有無で再TTS clip数が変わる。
- 案Bの採用承認は不要(案1は直接補完で完結)。ただし案1を実施する場合も、**ユーザー指示(完成音声の修正・再生成は現段階で行わない)の解除**が前提。
- 実施する場合のStatus/承認: 結末復元は必須の品質課題(ユーザー原文§7)だが、Production成果物の変更に当たるため、実施指示は別途ユーザー/Fableから受ける。
