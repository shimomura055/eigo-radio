# standard_meta_diff.md

## unified diff (Before -> After, full text)

```diff
--- before
+++ after
@@ -12,11 +12,11 @@
 
 This was the story’s most surprising part. The call looked like a one-person performance. But another performer was hidden inside the piano. Human help is not always a bad thing. People can help where AI is still weak. That makes this approach understandable.
 
-### Privacy concerns led Meta to pause the feature
+### Privacy concerns led Meta to temporarily turn off the feature
 
 Phone calls can contain personal information. Meta employees worried that call details might leak outside the company. People might be surprised that a contract worker had listened to the conversation. The worker had also responded. They thought they had handed the call to AI.
 
-Reuters reviewed internal posts about the feature. A Meta executive spoke about it in those posts. The executive said the company had paused the feature.
+Reuters reviewed internal posts about the feature. A Meta executive spoke about it in those posts. The executive said the company had temporarily turned off the feature.
 
 For AI phone service, one question is whether it can make a call. But that is not the only important question. Who is speaking onstage? And who is behind the curtain? The more convenient the service is, the more its explanation may matter. People may need that explanation before they truly feel safe giving it a task.
 
```

## SIMPLIFY decisions のみ(宣言された変更文)

- **pause** -> temporarily turn off
  - Before: Privacy concerns led Meta to pause the feature
  - After: Privacy concerns led Meta to temporarily turn off the feature

- **paused** -> temporarily turned off
  - Before: The executive said the company had paused the feature.
  - After: The executive said the company had temporarily turned off the feature.
