# U-2(1) 位置語→構造要素 replay(委任_66、¥0、実装なし)

```
{
 "d_type_unique": 5,
 "restorable_by_u2_1": 1,
 "still_rejected_by_reason": {
  "explain_split_rejected:fragment_not_in_article": 1,
  "explain_split_rejected:remainder_too_long": 3
 },
 "wrong_range_count": 0
}
```

## D1 unverified (現行P棄却理由: explain_split_rejected:fragment_not_in_article) 出現1回
- claim: `“Their job is visual. They add a special feeling. They say, ‘This is today’s mood.’” Also: “Large bags are the luggage crew. They carry what we need. Mini bags are the stage crew. They catch the eye and set the mood. In 2026, the runway proudly shows this split in their work.”`
- issue: None
- U-2(1)後: status=unverified reason=explain_split_rejected:fragment_not_in_article 追加要素=[]

## D2 unverified (現行P棄却理由: explain_split_rejected:remainder_too_long) 出現1回
- claim: `“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.`
- issue: The article states that the call recipients believed they were speaking with an AI. The Ledger confirms a test without appropriate disclosure, but does not establish what recipients believed.
- U-2(1)後: status=unverified reason=explain_split_rejected:remainder_too_long 追加要素=[]

## D3 unverified (現行P棄却理由: explain_split_rejected:dangling_position:headline,one_line) 出現1回
- claim: `“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly as a claim about oil prices generally.`
- issue: The Ledger verifies the post-withdrawal price movement for Brent futures, not for oil prices generally. The broader wording in the body, headline, and summary extends that observation beyond the verified scope.
- U-2(1)後: status=unverified reason=explain_split_rejected:remainder_too_long 追加要素=[]

## D4 unverified (現行P棄却理由: explain_split_rejected:remainder_too_long) 出現1回
- claim: `“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.`
- issue: The Ledger confirms that trained contractors handled some calls, but does not establish that they were positioned as a backup or fallback. The Japanese source already uses this framing.
- U-2(1)後: status=unverified reason=explain_split_rejected:remainder_too_long 追加要素=[]

## D5 resolved (現行P棄却理由: explain_split_rejected:dangling_position:headline) 出現1回
- claim: `“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high” (also reflected in the headline).`
- issue: The article generalizes the observed Brent-futures movement to oil prices broadly. The Ledger confirms this movement for Brent futures, not the whole oil market.
- U-2(1)後: status=resolved reason=None 追加要素=['headline']
- 断片の範囲: ["Oil prices moved briefly, then returned to a high level", "oil prices stayed high"]
- 最終範囲: ["The Fee Plan Leaves, But High Oil Prices Stay", "Oil prices moved briefly, then returned to a high level", "oil prices stayed high"]
- 検査: 断片が全て含まれる=True / 追加は名指しされた要素そのもの=True / 全範囲が記事に一意に逐語=True

