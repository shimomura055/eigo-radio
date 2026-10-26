# HR_PACKET_STD_PREVIEW_01 — Std preview 1 segment(新形式、委任_05)
管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05。公開: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/hr_preview_01.html 。生成: `tools/build_hr_packet_01.py`(API 0)。承認はユーザーのみ。

## 1. 原稿
荷物の再配達では、受け取る側が時間を指定しても、思いどおりに届かないことがあります。配達する人と受け取る人の経験を通して、再配達の問題を身近な場面から考えます。

## 2. ASR結果(全文)
- OpenAI(一次): 荷物の再配達では、受け取る側が時間を指定しても、思い通りに届かないことがあります。配達する人と受け取る人の経験を通して、再配達の問題を身近な場面から考えます。
- Azure(二次): 荷物の再配達では、受け取る側が時間を指定しても思い通りに届かないことがあります。配達する人と受け取る人の経験を通して、再配達の問題を身近な場面から考えます。

## 3. 相違点
- 原稿→OpenAI:
  - replace: 原稿 `どお` / ASR `通`
- 原稿→Azure:
  - delete: 原稿 `、` / ASR `(なし)`
  - replace: 原稿 `どお` / ASR `通`

## 4. NG理由
統一ASR判定 `NG_BOTH` / `secondary_not_accepted`。OpenAI=`ASR_VALIDATION_UNCERTAIN`、Azure=`ASR_VALIDATION_UNCERTAIN`(accepted=False)。JA二次ASRの受理は `EXACT_MATCH`/`NORMALIZED_MATCH` のみ(CURRENT_SPEC.md:2903)。読みが濁点の有無を除いて一致=「とおり/どおり」を確定できず、標準2+fallback1=3回後 lock=HUMAN_REVIEW_REQUIRED(最終: 最終status=STOPPED。標準経路2回+fallback経路1回(合計上限3回)とも不合格)。数値/否定の保護差なし、長さOK。

## 5. 推奨音声(1つ)
Take 1(15.72秒、route `custom_06ec49ff`、承認Style S3): `user_test/family_y_production_redelivery_fee_03/std_hr/std_preview_take1.mp3`

## 6. 評価
結論: 実際の内容の誤りではなく、表記の差(「どおり」と「通り」)が自動検査で止まった可能性が高い、とAIは判断しています。ただしAI自身は音声を聞けないため、最終確認は耳でお願いします(これがこのHRの唯一の目的です)。

根拠(1) 原稿「思いどおりに」に対し、OpenAI・Azureの2つの音声認識がどちらも「思い通りに」と書き起こしています。「どおり」を漢字で書けば「通り」になるのが一般的な書き方で、他の文字・数字・否定語はすべて一致し、抜けや重複はありません(OpenAI全文79字/Azure全文78字、同じ文の繰り返しなし)。

根拠(2) 自動検査は「読みが完全に同じ」と確認できる場合だけ自動合格にします。ここでは文字の並びから「通り」を「どおり」(濁った発音)と確定できず、「とおり」(濁らない発音)の可能性が残るため、安全側で止まりました。実際に「どおり」と発音されていれば問題ありません。

音声の計測: 長さ15.72秒、先頭・末尾の無音は0.3秒、文の切れ目(7.15秒付近)に約1.0秒の間、途中の長い無音・途切れ・繰り返しなし(自動計測)。話し方(Style)は承認済みの日本語補助S3です。

Take 1・2・3の比較はAI側で済ませました。Take 1とTake 2は同じ承認Styleで、書き起こし・判定とも完全に同じです(間の長さがわずかに違うだけ)。Take 3は別の短い指示文(fallback)で作られた音声で承認Styleとは異なるため候補から外しました。聴き比べをお願いする必要のある品質差はありません。よって最初の1つであるTake 1を推奨します。

## 7. 質問
**この音声でよいですか?**(1つだけ)
