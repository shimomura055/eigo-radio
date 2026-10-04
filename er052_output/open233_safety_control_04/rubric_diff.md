# rubric差分(委任_61、V7 -> V7b、逐語)

## 1. body rubric: V7 -> V7b(`er052_open233_self_recovery_stage2_calibration_01.py`)

V7は`RUBRIC_R3_TRIPLE_PRIME + MISCONCEPTION_PRINCIPLE_TEXT_V7`(= V6の原則文へ追記)。V4〜V6の原則文は削除・編集していない。

```diff
--- body rubric V7 (旧、定数として残す)
+++ body rubric V7b (新)
@@ -167,8 +167,10 @@
 
 (3) 判断に迷う場合: 読者(英語学習者)がこの文を信じたときに事実関係の重大な
 誤解につながるかで決めてください。つながるならBLOCKING、つながらないなら
-QUALITYとしてください。数値・主体・否定・比較・時期の差は、この原則の対象外
-で、従来どおり明確にBLOCKINGとします。
+QUALITYとしてください。数値・主体・否定・比較・時期について、Ledgerと矛盾する重大な変更
+(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は、
+この原則の対象外で、従来どおり明確にBLOCKINGとします。方向・時期のニュアンス
+の差で事実関係の核心が保たれているものは、この限りではありません。
 
 判定済みの例(ユーザー決定):
 - "Also, some calls needed user information to continue." → QUALITY
```

## 2. Stage 2 production既定rubric(`er052_open233_self_recovery_stage2_production_01.py`)

`MATERIALITY_RUBRIC_V7`(旧、残す) -> `MATERIALITY_RUBRIC_V7B`(新、末尾の「迷えばBLOCKING」のみ置換、QUALITYの「動機の帰属」は不変。runnerのbody判定は上記1のV7を使う)。

```diff
--- s2p.MATERIALITY_RUBRIC_V7 (旧、定数として残す)
+++ s2p.MATERIALITY_RUBRIC_V7B (新)
@@ -9,5 +9,7 @@
   背景説明・条件付きの一般論にとどまる。
 - 上記のどれに該当するか迷う場合は、読者(英語学習者)がこの文を信じたときに事実関係の
   重大な誤解につながるかで決めてください。つながるならBLOCKING、つながらないならQUALITY
-  としてください。数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり
-  機械的にBLOCKINGとします。
+  としてください。数値・主体・否定・比較・時期について、Ledgerと矛盾する重大な変更
+  (数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は、この原則の
+  対象外で、従来どおり機械的にBLOCKINGとします。方向・時期のニュアンスの差で事実関係の
+  核心が保たれているものは、この限りではありません。
```

## 3. 不変のもの

`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`・Hook専用rubric(V3/V4)・`DISCLOSURE_GAP_NEGATION_RE`(否定形限定)は変更していない。
