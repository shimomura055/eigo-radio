# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A 事実確認(2026-10-30、API 0・コード変更0・読取専用)

原文=docs/pm/delegation_log/2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER_02.md。実測script=scratchpad `ejh03a_*`(コミット対象外)。DOM実測=Playwright+ローカルhttp、live=shimomura055.github.io の5記事すべてHTTP200+article.json取得を確認。

## 0. 結論(前回報告の真相。正誤)
| 前回(委任_01 CURRENT_STATE_01 §3)の記述 | 判定 | 真相 |
|---|---|---|
| Z=「訳が全て無い(story含む)」 | **Storyは正しい** | Zの英語本文は最初から英語で書かれた翻案で、日本語の本文は**どの工程にも存在しない**(§1)。 |
| 同上の言い方 | **不正確(見落とし)** | **Zにも日本語は存在し画面に出ている**: Standardの Preview / Comment 1-3 は**日本語で生成・読み上げ・End Userページに日本語表示済み**(メロス実測)。さらにKey Phraseの引用英文の日本語訳(`kp_source_sentence_ja.json`)と意味欄・日本語タイトルも存在。「日本語が全く無い」は言い過ぎ。 |
| X/Y「Comment・Preview・In One Lineは訳が無い」 | **半分誤り** | X/Yでは **Std=日本語のPreview/Comment(Std本文を材料に独立生成した別文)、Adv=英語のPreview/Comment**。`build_info.translation_coverage`は「承認済みの“訳”が付いたか」だけを数え、StdのComment/Previewは日本語本文なので集計対象外=「無い」に見えた(見誤り=“日本語パートが別に存在する”点)。ユーザーが見た「Comment 2に英語と日本語が表示」は、**同一dev index.html上のStd(日本語Comment 2)とAdv(英語Comment 2)**。ただし**両者は翻訳関係ではなく別々に生成された文**(§3)。 |
| 「JA原作(メロス/藪の中/雪女)」 | **雪女は誤り** | 雪女の原作は小泉八雲(英語、Gutenberg #1210、`yuki_onna/seed/primary_text_excerpt.md`は英文)。日本語原作はメロス(太宰)と藪の中(芥川)のみ。 |
| 「JA原作も日本語は表示していない」 | 正しい(理由が重要) | seedの日本語原文は逐語引用の抜粋のみ(メロス excerpt 1,843字・日本語268字、藪の中 日本語7,589字)。**Z英語本文は原文の翻訳ではなく、英語のseed要約(`seed.json original_summary/conversion_plan`)から英語で書いた翻案**(メロス: 「300–350語、人名はMelosのみ、役割語に置換、A2向けに簡略化」)。原文を表示しても英日対応にならない。 |

## 1. (a) Zの保存場所・構造(実データ)
- 生成: Writer r0→r1→r2(=Advanced英語)→std.md(=Standard英語)。**全て英語**(`er026_output/family_z_production_e2e_01/<作品>/<run>/writer/{r0,r1,r2,std}.md`)。メロス `melos/run_p2_evidence_r3/writer/r2_prompt.txt` 冒頭は英語。Z runnerに英→日の本文訳stageは**無い**(`er026_family_z_fiction_production_runner_01.py`の翻訳関連はKey Phrase引用英文の訳`_stage_kp_part1_ja`:2498のみ)。
- 日本語が存在する箇所(Z): (i) `support/a2_support.json`の`comments`/`preview`(method=`adv_method_ja_v1`、Std)。(ii) Adv=`support/b1b_support.json`は英語。(iii) KP: `key_phrases/<lv>/kp_source_sentence_ja.json`(model=gpt-6-luna、実測費用¥0.0193/3文)、`study_text/part1_vocabulary_expressions.json`の意味欄。(iv) 日本語タイトル(`jtitle`)。
- End User `enduser/data/article.json`: 公開済Zは2件(メロス r3 `user_test/family_z_melos_kphr_evidence_r3/enduser/`、藪の中 `user_test/family_z_in_a_grove_01/enduser/`)。story partに**`ja`フィールド無し**、`build_info.json translation_coverage.*.story={blocks:3,translated:0,source:none_approved_translation_hidden}`。告げ口心臓・雪女はenduser未生成(雪女はStyle Gate BLOCKで停止中)。
- **実画面(Playwright DOM、メロスr3 PC1280)**: Std 10カード・`.sent`62文・日本語訳ブロック`.tr` **0**、Adv 10カード・`.sent`70文・`.tr` **0**。StdのPreview/Comment 1-3は日本語文として表示。比較: X月 Std/Adv は`.tr`各3(story Part1-3のみ)。
- 英日1対1か: **Z story=比較対象の日本語本文が存在せず判定不能**。X/Y storyは§4。
- 日本語原作/英語原作の差: データ構造は**同一**(どちらも英語本文を英語で生成。差はseed要約の元言語のみ)。

## 2. (c) 代表例
| 作品・レベル | 実際の英語文 | 対応する日本語文 | 保存場所 | End User表示 | 不足の原因・対策 |
|---|---|---|---|---|---|
| 告げ口心臓(Z、英語原作) Adv | `You call me mad. No. Nervous, perhaps, but perfectly sane.` | **無い**(writer全段が英語、Std本文も英語) | `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/writer/r2.md` | enduser未生成 | Z runnerに英→日の本文訳stageが無い。End User build時に文ID単位で新規生成(§5) |
| 告げ口心臓 Comment 1 | Adv: `Listen for what about the old man troubles the speaker.` | Std側は別文: `語り手が、老人の部屋へ何度も近づく理由を聞き取ってください。` | `run_reselect_01/support/{b1b,a2}_support.json` | Std=日本語/Adv=英語 | **内容が異なる別文=翻訳ではない** |
| メロス(Z、日本語原作) Adv Part1 | `Melos's voice rang through the hall.` / `"You kill men because you fear them. You won't even let them speak."` | **無い**(太宰原文は`メロスは激怒した。…`で構成が別) | `melos/run_p2_evidence_r3/writer/r2.md`(英語翻案392語)、原文引用`melos/seed/primary_text_excerpt.md` | `.tr`=0 https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_kphr_evidence_r3/enduser/ | 日本語原作でも翻案は英語で再構成=原文は訳にならない。新規生成 |
| メロス Comment 2 | Adv: `Melos promised to return, and his friend chose to trust him.` | Std: `メロスは、友を人質に残して三日以内に戻ると約束しました。帰り道で困難に出会ったとき、彼はどうするのでしょうか。`(表示済み) | `run_p2_evidence_r3/support/*_support.json` → `enduser/data/article.json` | Std=日本語/Adv=英語 | 意味が一部異なる(Std側は2文目が別内容)=Advの訳に流用すると不正確 |
| X月 Comment 2 | Adv: `The cliffs on the Moon helped the team estimate how much it has shrunk.` `But does that estimate cover the Moon's whole history?` | Std: `月のしわから、月の半径は約42から46メートル小さくなったと推定されました。` `では、月ができてから今までに縮んだ量は、それだけなのでしょうか？` | `user_test/family_x_moon_shrinking_reselect_01/enduser/data/article.json` std/adv parts[15] | https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/enduser/ Std=日本語2文/Adv=英語2文 | **ほぼ対訳に見える例(ユーザーが見た例)**。ただしStd側は具体数値を追加した別文。Comment 3はAdv2文↔Std3文で文数も異なる |
| X月 Preview(Adv) | `This episode explores a possible layer of broken rock beneath the Moon’s surface.` | **無い**。Std Previewは別内容(`月の表面に残るしわは、月がどのように冷えてきたかを考える手がかりになります。`) | 同上 adv parts[5] / std parts[6] | Adv=英語のみ | Std/Advは各自生成。Adv Previewの訳を新規生成(承認済み) |
| X月 In One Line(Std/Adv) | Std: `Researchers mapped over 8,900 Moon cliffs and estimated that its radius shrank 42 to 46 meters in a later period.` | **無い**(両レベルとも英語のみ) | parts[20] | 英語のみ | 新規生成 |
| X月 Story Part1 Std | `Even the Moon has wrinkles.` | 承認済み日本語原稿(revision2.md)の対応段落(段落配列`ja`) | `enduser/data/article.json` story part `ja` | `.tr`3ブロック表示 | 既存(再生成しない)。文単位の境界情報なし→対応づけ必要 |

## 3. (b) Std日本語Comment/Previewは「Adv英語の訳」か(実測)
文数(Adv英語/Std日本語): X月 Comment1 1/1、C2 2/2、C3 2/3、C4 3/3、Preview 2/2。Y姓 Preview 3/2、C1 1/1、C3 2/2(YのAdvはComment 2が無く、StdのみComment 2有り)。メロス Preview 2/2、C1 1/1、C2 2/2、C3 2/2。**文数が一致しても内容は別文**(上表の告げ口心臓C1・メロスC2)。生成はStd(`a2_support.json method=adv_method_ja_v1`)とAdv(`b1b_support.json`)が別call。→ Std日本語をAdvの“訳”に流用すると誤訳表示になる箇所があるため**流用しない**(推奨。新規生成の費用は1文あたり約¥0.006)。

## 4. (d) 既存の対応情報の粒度・分類
- X story: 段落単位(EN段落i↔JA段落i、`attach_translations`が不一致をSTOPで保証、`er135_enduser_page_01.py:630-641`)。Y story: ブロック単位(Lead/Voice紹介/Voice/Closing、英語1段落↔JA1ブロック、`:643-657`)。**文単位の対応はどこにも無い**。段落内で文数一致する率(CURRENT_STATE_01 §4実測): Std約15%/Adv約75%。
- 「既存データで正確に分かる場合は埋め込みAPIを使わない」原則の適用案: (1)EN1文×JA1文の段落=決定論(数字集合一致・長さ比の安全検査付き)で埋め込み不要。(2)文数一致の段落は決定論候補+長さ・数字検証、**検証不通過だけ**埋め込み。(3)文数不一致=埋め込み+DP。(4)**新規生成する訳は文ID単位で生成するため構成上1:1=埋め込み不要**。

| パート×Family | 日本語の状態 | 対応方式 |
|---|---|---|
| Story X Std/Adv | 承認済みJA原稿(段落) | 決定論(1:1段落)/埋め込み+DP(文数不一致) |
| Story Y Std/Adv | 承認済みJA原稿(ブロック) | 同上 |
| Story Z Std/Adv | **無し** | 新規生成(文ID単位→1:1、埋め込み0) |
| Std Preview/Comment(X/Y/Z) | 日本語が本文(英語対が無い) | 日本語文自体が既にsent単位=現行ハイライトで足りる(英語対応が無いので英日連動はN/A。英語を新規作成はしない) |
| Adv Preview/Comment(X/Y/Z) | 訳無し(Std日本語は別文) | 新規生成(文ID単位、埋め込み0) |
| In One Line(X Std/Adv。Y/Zはパート自体が無い) | 訳無し | 新規生成 |
| Topic intro(原文4パート対象外) | Stdはjtitleが日本語表示 | 対象外 |

## 5. (e) Adv Preview日本語訳の生成経路案
- 既存の英→日翻訳経路: `er003_kp_source_sentence_ja_01.py`(X/Z/Y共通、SUPPORT_MODEL=`gpt-6-luna` `er006_model_routing_contract_01.py:50`、構造Gate`check_ja`:空/短すぎ/CJK不在/英字優位/英文と同一/長すぎ/禁止パターン、技術retry1回→fail-closed、signature再生成キー)。**Preview専用の既存翻訳経路は無い**(Std Previewは独立生成)。
- 案: 上記のPrompt/Gate/routingを再利用した新規`er135_enduser_translate_01.py`(End User build内)で、未訳の英語パート(Adv Preview/Comment/In One Line、Std In One Line、Z story)を**文ID付きで翻訳**→`ja`と`ja_align`(文ID↔訳文、1:1)を直接生成。追加検査=文数一致・数字集合一致(・推奨:埋め込みcos下限=誤訳検知。既存構造Gateの拡張でありFable確認事項)。キャッシュ=sha256(英文+Prompt sha+model)(retry/regeneration/resume時は変更文だけ再翻訳)。
- 費用: 実測¥0.0193/3文(Prompt込み)。Z story 約60文/レベル×2、X Adv 約13文+Std OneLine 2文 → **約¥0.3〜1.0/記事**(バッチ化でさらに低下)。
