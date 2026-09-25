# sewer_diff.md

## unified diff (Before -> After, full text)

```diff
--- before
+++ after
@@ -1,10 +1,10 @@
 “Merger”? Not Towns, but Household Wastewater
 
-When a news report mentions a “combined septic tank,” you may wonder if it is about towns joining together. But the things being combined are not municipalities. They are toilet water, and water from the kitchen and bath.
+When a news report mentions a “combined septic tank,” you may wonder if it is about towns joining together. But the things being combined are not local governments. They are toilet water, and water from the kitchen and bath.
 
-Some municipalities are now considering replacing aging sewer systems with combined septic tanks. This does not mean getting rid of all sewers. In some areas, it means considering a change from a system that connects the whole town to one that treats wastewater near each home.
+Some local governments are now considering replacing aging underground pipe systems with combined septic tanks. This does not mean getting rid of all underground pipe systems. In some areas, it means considering a change from a system that connects the whole town to one that treats wastewater near each home.
 
-A sewer is like an invisible main artery beneath the town. It collects water from homes in underground pipes and carries it to a distant treatment plant. Most of the time, we hardly think about it. Turn on the tap, flush the toilet, and the underground system takes care of the rest.
+A network of underground pipes is like an invisible main artery beneath the town. It collects water from homes in underground pipes and carries it to a distant treatment plant. Most of the time, we hardly think about it. Turn on the tap, flush the toilet, and the underground system takes care of the rest.
 
 But when those pipes grow old, the situation changes. Because they are underground, it is hard to find where they are damaged. Repairs are not easy, either. Since the system is connected over a long distance, the repairs can also become large-scale.
 
@@ -12,6 +12,6 @@
 
 It is like placing a small washing machine in each home instead of putting one huge washing machine in the town. The idea is to divide one large system into several smaller ones.
 
-Of course, having a septic tank does not mean that nothing more is needed. Installation, inspections, and cleaning are still necessary. For people who use sewers, this also means that the hidden part of daily life will change.
+Of course, having a septic tank does not mean that nothing more is needed. Installation, inspections, and cleaning are still necessary. For people who use these pipe systems, this also means that the hidden part of daily life will change.
 
-Still, the interesting point is this: to protect convenience, we do not always need to make the system bigger. Instead of forcing an aging underground main artery to keep going, we can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.
+Still, the interesting point is this: to protect convenience, we do not always need to make the system bigger. Instead of forcing an aging underground main artery to keep going, we can move water treatment closer to home. The future of these systems may arrive in a surprisingly familiar place—right near us.
```

## SIMPLIFY decisions のみ(宣言された変更文)

- **sewers**
  - Before: This does not mean getting rid of all sewers.
For people who use sewers, this also means that the hidden part of daily life will change.
The future of sewers may arrive in a surprisingly familiar place—right near us.
  - After: This does not mean getting rid of all underground pipe systems.
For people who use these pipe systems, this also means that the hidden part of daily life will change.
The future of these systems may arrive in a surprisingly familiar place—right near us.

- **municipalities**
  - Before: But the things being combined are not municipalities.
Some municipalities are now considering replacing aging sewer systems with combined septic tanks.
  - After: But the things being combined are not local governments.
Some local governments are now considering replacing aging underground pipe systems with combined septic tanks.

- **sewer**
  - Before: Some municipalities are now considering replacing aging sewer systems with combined septic tanks.
A sewer is like an invisible main artery beneath the town.
  - After: Some local governments are now considering replacing aging underground pipe systems with combined septic tanks.
A network of underground pipes is like an invisible main artery beneath the town.
