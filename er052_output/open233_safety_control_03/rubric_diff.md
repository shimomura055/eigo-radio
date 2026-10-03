# rubric差分(委任_55、2026-10-03、逐語)

## 1. body rubric: V6 -> V7(`er052_open233_self_recovery_stage2_calibration_01.py`)

V7は`RUBRIC_R3_TRIPLE_PRIME + MISCONCEPTION_PRINCIPLE_TEXT_V7`(= V6の原則文へ追記)。V4〜V6の原則文は削除・編集していない。

```diff
--- body rubric V6 (旧、定数として残す)
+++ body rubric V7 (新)
@@ -140,3 +140,37 @@
    該当します。
 上記2種類に該当するかどうかを、tie-breakでQUALITYへ倒す前に必ず先に
 確認してください。
+
+【線引きの正式採用(2026-10-03ユーザー決定、委任_55。以下は、上記V4の
+「条件付き→断定は一律BLOCKING」および、上記の判定全体のうち「迷う場合」の
+扱いより優先します)】
+判定は次の3区分です。
+- BLOCKING(重大): 英語学習者に事実関係の重大な誤解を与えるもの。
+- QUALITY(軽微): 事実関係の核心は保たれているが、表現の精度が少し落ちるもの。
+- ACCEPTABLE(問題なし): 確認済みFactから自然に導ける描写・推論で、新しい
+  具体的事実を追加しないもの。
+
+(1) 条件つき→断定: Ledgerが条件つき・可能性・懸念として書く内容を、記事が
+発生したこととして書く場合、次のいずれかに該当するときはBLOCKINGとして
+ください: (ア)被害・結果にあたる核心の主張まで断定している、(イ)Ledgerに
+無い新しい具体的事実(人物・出来事・発言・数値)を加えている、(ウ)Ledgerの
+notes_for_writerが明示的に禁じる断定をしている。核心の主張に留保が残り、
+帰属(誰の懸念・誰の主張か)が保たれている場合はQUALITYとしてください
+(例: 『some calls needed user information to continue』は、共有が
+『might』で留保され、懸念の主体がMeta従業員のままなのでQUALITY)。
+
+(2) 自然な推論: 開示がなかった等の確認済み事実から自然に導かれる利用者の
+状態・認識・反応の描写は、否定形(『気づかなかった』)も肯定形(『AIだと
+思っていた』『楽しんでいた』)も、新しい具体的事実を加えなければ
+ACCEPTABLEとしてください。この場合、上記の「他者の内心を断定する記述」の
+BLOCKING条件は、新しい具体的事実を加えていない描写には適用しません。
+
+(3) 判断に迷う場合: 読者(英語学習者)がこの文を信じたときに事実関係の重大な
+誤解につながるかで決めてください。つながるならBLOCKING、つながらないなら
+QUALITYとしてください。数値・主体・否定・比較・時期の差は、この原則の対象外
+で、従来どおり明確にBLOCKINGとします。
+
+判定済みの例(ユーザー決定):
+- "Also, some calls needed user information to continue." → QUALITY
+- "They enjoyed AI’s convenience, but a human was on the other end. They did not realize it." → ACCEPTABLE
+- "Just after the charge plan disappeared, prices began to fall." → QUALITY
```

## 2. Stage 2 production既定rubric(`er052_open233_self_recovery_stage2_production_01.py`)

`MATERIALITY_RUBRIC`(旧、残す) -> `MATERIALITY_RUBRIC_V7`(新、末尾の「迷えばBLOCKING」のみ置換、QUALITYの「動機の帰属」は不変。runnerのbody判定は上記1のV7を使う)。

```diff
--- s2p.MATERIALITY_RUBRIC (旧、定数として残す)
+++ s2p.MATERIALITY_RUBRIC_V7 (新)
@@ -7,4 +7,7 @@
 - ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果を一切加えず(Ledgerに既出の
   固有名詞を繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の一般常識レベルの
   背景説明・条件付きの一般論にとどまる。
-- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。
+- 上記のどれに該当するか迷う場合は、読者(英語学習者)がこの文を信じたときに事実関係の
+  重大な誤解につながるかで決めてください。つながるならBLOCKING、つながらないならQUALITY
+  としてください。数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり
+  機械的にBLOCKINGとします。
```

## 3. 不変のもの

`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`・Hook専用rubric(V3/V4)・`DISCLOSURE_GAP_NEGATION_RE`(否定形限定)は変更していない。
