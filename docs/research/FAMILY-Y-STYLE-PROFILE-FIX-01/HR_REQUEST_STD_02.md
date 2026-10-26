# HR_REQUEST_STD_02 — Std 承認待ちはPreview 1件のみ(委任_04。HR_REQUEST_STD_01の更新)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04。公開ページ: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html (節 `#std_y1` と `#std_hr`)。
到達Status=Std y_voice_1は再生成で自動検査PASS(承認不要)/Std preview 1件がユーザー承認待ち。承認は人間(ユーザー)のみ。AI/Fableは代行しない。

## 1. y_voice_1(Voice 1)=承認不要になった
- 旧take 1/2: 台本 `who was not home` を両ASR(OpenAI・Azure)が `who is not home` と転写 → 読み違い濃厚。旧take 3(fallback短文Style)は `was` だが承認Styleと異なる。いずれも **非推奨**(ページに残してある)。
- Fable許可の`approve_regenerate`で再生成した **新take 4(承認Style PD06)は初回で自動検査PASS**(OpenAI転写 `who was not home`、NUMERIC_EQUIVALENCE_MATCH)。Std規則の6%減速(37.92→40.18秒)後ASR再検証も通過(NORMALIZED_MATCH)。lockは自動で RESOLVED/OK。
- したがってユーザーの承認操作は不要。任意で `#std_y1` の「最終版」(緑の行)を聴いて確認できる。聴いて不可なら「y_voice_1 = 再生成」と返答(費用≒1.3円/回)。

## 2. preview(日本語要約)=承認待ち(変更なし)
- 差は表記ゆれのみ(台本「思いどおり」→ASR「思い通り」。読みは同じ)。take 1/2(承認Style S3)が推奨。take 3はfallback短文Style(承認Styleと異なる)で非推奨。
- 返答例: 「Std preview = take 1 承認」。受領後にFableが委任_05で `tools/hr_adopt_style_fix_01.py --level a2 --segment preview --take 1 --apply --user-statement-ref <逐語保存>` を実行し、その後 `--stages provision_shell,gate,assemble,pages,page_verify` を1起動(API 0)で通し版を作る。
