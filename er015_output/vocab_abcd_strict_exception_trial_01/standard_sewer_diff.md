# standard_sewer_diff.md

## unified diff (Before -> After, full text)

```diff
--- before
+++ after
@@ -1,17 +1,17 @@
 “Merger”? Not Towns, but Household Wastewater
 
-When a news report says “combined septic tank,” you may wonder. Is it about towns joining together? But towns are not the things being combined. They are toilet water, kitchen water, and bath water.
+When a news report says “combined treatment tank,” you may wonder. Is it about towns joining together? But towns are not the things being combined. They are toilet water, kitchen water, and bath water.
 
-Some local governments are considering replacing old sewer systems with combined septic tanks. This does not mean removing all sewers. In some areas, they are considering another kind of system. It would treat wastewater near each home, instead of connecting the whole town.
+Some local governments are considering replacing old underground pipe systems with combined treatment tanks. This does not mean removing all underground pipe systems. In some areas, they are considering another kind of system. It would treat wastewater near each home, instead of connecting the whole town.
 
-A sewer is like an invisible main artery beneath the town. It collects water from homes in underground pipes. Then it carries the water to a faraway treatment plant. Most of the time, we hardly think about it. We turn on the tap and flush the toilet. The underground system takes care of the rest.
+An underground pipe system is like a hidden main pipe beneath the town. It collects water from homes in underground pipes. Then it carries the water to a faraway treatment plant. Most of the time, we hardly think about it. We turn on the tap and use the toilet. The underground system takes care of the rest.
 
 But when those pipes grow old, the situation changes. Because they are underground, damaged places are hard to find. Repairs are not easy, either. The system reaches a long way and stays connected. So repairs can also become very large jobs.
 
-That is where combined septic tanks come in. They are small places that treat water near homes. They treat toilet, kitchen, and bath water for each home. The water does not go to a distant treatment plant. Instead, it is cleaned near the home.
+That is where combined treatment tanks come in. They are small places that treat water near homes. They treat toilet, kitchen, and bath water for each home. The water does not go to a distant treatment plant. Instead, it is cleaned near the home.
 
 It is like putting a small washing machine in every home. This is instead of one huge washing machine for the town. The idea is to divide one large system into several smaller ones.
 
-Of course, a septic tank does not mean nothing else is needed. It still needs installation, checks, and cleaning. For people who use sewers, a hidden part of daily life will change too.
+Of course, a treatment tank does not mean nothing else is needed. It still needs installation, checks, and cleaning. For people who use underground pipe systems, a hidden part of daily life will change too.
 
-Still, the interesting point is this: to keep life convenient, we do not always need a bigger system. We do not have to make an old underground main artery keep going. We can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.
+Still, the interesting point is this: to keep life convenient, we do not always need a bigger system. We do not have to make an old underground main pipe keep going. We can move water treatment closer to home. The future of underground pipe systems may arrive in a surprisingly familiar place—right near us.
```

## SIMPLIFY decisions のみ(宣言された変更文)

- **septic** -> treatment
  - Before: When a news report says “combined septic tank,” you may wonder.
Some local governments are considering replacing old sewer systems with combined septic tanks.
That is where combined septic tanks come in.
Of course, a septic tank does not mean nothing else is needed.
  - After: When a news report says “combined treatment tank,” you may wonder.
Some local governments are considering replacing old underground pipe systems with combined treatment tanks.
That is where combined treatment tanks come in.
Of course, a treatment tank does not mean nothing else is needed.

- **invisible** -> hidden
  - Before: A sewer is like an invisible main artery beneath the town.
  - After: An underground pipe system is like a hidden main pipe beneath the town.

- **flush** -> use the toilet
  - Before: Most of the time, we hardly think about it. We turn on the tap and flush the toilet. The underground system takes care of the rest.
  - After: Most of the time, we hardly think about it. We turn on the tap and use the toilet. The underground system takes care of the rest.

- **artery** -> main pipe
  - Before: A sewer is like an invisible main artery beneath the town.
Still, the interesting point is this: to keep life convenient, we do not always need a bigger system. We do not have to make an old underground main artery keep going.
  - After: An underground pipe system is like a hidden main pipe beneath the town.
Still, the interesting point is this: to keep life convenient, we do not always need a bigger system. We do not have to make an old underground main pipe keep going.

- **sewer** -> underground pipe system
  - Before: Some local governments are considering replacing old sewer systems with combined septic tanks.
A sewer is like an invisible main artery beneath the town.
  - After: Some local governments are considering replacing old underground pipe systems with combined treatment tanks.
An underground pipe system is like a hidden main pipe beneath the town.

- **sewers** -> underground pipe systems
  - Before: This does not mean removing all sewers.
For people who use sewers, a hidden part of daily life will change too.
The future of sewers may arrive in a surprisingly familiar place—right near us.
  - After: This does not mean removing all underground pipe systems.
For people who use underground pipe systems, a hidden part of daily life will change too.
The future of underground pipe systems may arrive in a surprisingly familiar place—right near us.
