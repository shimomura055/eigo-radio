# CP_RESULT_01(委任_03、2026-10-28)

## 1. Fable CP結果(転記)
Adv(r2.md)/Std(std.md): 7証言が原作順・3当事者の矛盾・結末(見えない手→闇へ沈む)・評決なし=CP重大欠落0。Preview先取りなし。Comment 3は許容。是正1件=Std `std.md:11` の1文(下記)。

## 2. Std 1文の是正: **未実施(判断待ち、実装せずFableへ報告)**
対象: `er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/writer/std.md:11` の `She fought with her dagger, but I forced her to have sex with me.`(1回のみ出現を確認)→ 目標 `She fought with her dagger, but I took her by force.`
- (a) `er062_family_z_writer_01.py:919` `apply_cp_deletion_patch` は **exact_textの削除専用**(`new_text = old_text.replace(exact_text, "", 1)`、置換引数なし)。置換非対応。削除で代用すると「襲われた」事実そのものが消え、Seed conversion_plan(非グラフィックの1句は残す)と原作の核(3証言の食い違いの前提)に反するため不採用。
- (b) er020系Local Rewriteは**TTS音声segment単位**の再生成経路(`er020_tts_retry_local_rewrite_01.py`等)で、Writer本文(std.md)・provenance chainを対象にしない。本文是正には使えない。
- (c) std_adjust再実行の実測費用は `provenance.json` の chain[std_adjust].cost_jpy=**¥10.5974**(委任文の見積¥3〜4は過小。output 6,170 tok/reasoning 5,621 tok)。plan(≈¥0.26)/support(≈¥0.39)/kp+文法の再実行を加えると約¥11〜12で、本委任Cap¥10を超える。かつ他の文が変わるため再CPが必要。
- 選択肢案: (i)Cap引上げ承認(¥15程度)で(c)実行→再CP、(ii)`apply_cp_deletion_patch`と同型の「exact 1文置換」patch(同じprovenance cp_patches記録+子stage input_sha付替え、API 0)を承認済み機構の延長として許可(新Validator/Gate/Prompt変更なし。コード追加のため要許可)。推奨=(ii)(費用0・変更1文のみ・再CP不要[Adv同一文言の転用]・Std他文不変)。

## 3. 再実行結果
Std plan/support/kp: 未実行(是正前に再実行しても無駄になるため)。Adv側は再実行なし(変更なし)。累計は¥22.00のまま、本委任の有料API 0。

## 4. 候補sha
- Adv(b1b): candidates_sha256 `941647eb453de90d41fdced487cf47ed28a4065bb782f43dd206f75a0ad2bee4` / 本文sha(r2) `ee5433934163507384f4bb7dcd372d82c83859dddd1f1c0a5dc310e66d15621a`。Adv候補は不変。
- Std(a2)旧: KP candidates_sha `761026a5e726ba644f4a89c4fc264b08b5f10719a6c7a5678f91615721c4c733` / 文法 `c9124ec57bc3a2fa86e4a357078ca9a367cc043c692fa189c61a5310c42f7b6e` / 本文sha(旧、是正前) `6aa5c86dd0d6`。**Std本文是正後に再生成される=この旧shaでの選定はさせない(フォーム未公開)。**
- Std旧KP候補8の出典文にも当該1文が含まれる(`dagger` の出典文=`She fought with her dagger, but I forced her to have sex with me`)ため、是正後はKP候補も再生成が必要。

## 5. フォーム
Adv: `user_test/selection_form_v3/data/in_a_grove__b1b__prod.json`(KP4+KW5、文法0=Advは文法候補なし)をarticles.json先頭へ登録。Std: 本文是正後に生成して登録。
