# RESULT_PACKET JTA_01B (JA-TRANSLATION-LITERALNESS-AUDIT-01 委任_01B、調査③④、API 0)

DISK-GUARD: OK(free 67.1GB)。STOP確認: `stop_scope_check_01`(`--run-dir`にダミー)=非停止(`stop:false`)。LLM API呼出0・SSOT編集0・Production変更0。

## 要約
- 棚卸し(`INVENTORY_01.md`): **22行**(訳種別×生成元×Family適用)。日本語訳の出所は4系統: X=R2日本語台本(`approved_ja_manuscript`)、Y=Voice日本語原稿(`approved_ja_original_in_dev_page`)、英文からのLLM翻訳(`generated`: Z本文+X/Y Adv補助+X Std In One Line)、学習項目専用工程。**X/Yの本文は「日本語が原本で英語がその忠実英訳→簡易化」という逆向きで、StdとAdvで同一の日本語を共有**(Std英文はAdvより文数が多い)。
- **配線漏れ確定3件**: G1=対訳照合(LLM校閲・数値照合・文結合検査)が`generated`にのみあり`approved_*`には無い(`er135_enduser_translate_01.py:259,291,375,491` vs `er135_enduser_page_01.py:631-657`)、G2=Std/Adv英文が別構造なのに日本語は共通1原稿、G3=訳種別ごとに規範の強さが不統一(KP glossは「直訳調を避け平易な言い換え」、T1は「意訳しすぎず」、文法StepBは「自然な訳」のみ、End User生成は「情報の追加・省略をしない」)。潜在1(G4: X原稿fallbackがoriginalまで落ちる)、仕様どおり/世代差/stale 3(G5 align null、G6 藪の中は訳なし、G7 Std Part1/2世代差)。
- 実データ照合(`COMPARISON_01.md`): 公開済み10記事の**全1,164ユニットを全数照合**(確認1,164/未確認0。ただし日本語非表示32件は判定不能で別計上、解説内対訳は抽出83件のみ=抽出外は未確認)。第2判定397件(順序・ID再シャッフル、第1判定非表示)。
- 分類(表示あり1,132件): 6適切1,019 / 1欠落1 / 2追加4 / 3統合64 / 4意味変化29 / 5不適切15 / 未表示32。**重大0件**、中64件(分類3)、軽49件。第2判定は境界1件(`jwst`の「下限7620 Å」先食い)を重大と判定。
- **approved(R2/Voice由来) vs generated(翻訳)**: 表示あり453件中100件(22.1%)対310件中0件(0.0%)。approvedのStdは213件中75件(35.2%)・中以上55件(25.8%)、Advは240件中25件(10.4%)・中以上9件(3.8%)。学習項目は359件中12件(3.3%、全て軽)。
- 分類3(64件)の内訳: 内容は保持され文境界のみ不一致(mf)55、圧縮・欠落を伴う3、隣接群と食い違い(shift)3、その他3。多くは「情報欠落」より「1対1で英文と照合できない」対応消失。
- ユーザー問題①②は実データで再現: ①=Std ai_chat「It sat…/At least…/In fact…」3英文→日本語1文(2断片)=分類3(中)。②=「They used the share…」+ユーザー引用範囲外の直後文「People who did not think…」(s031)の2文→1文+「指標なのだ」=分類3(中)+副因2(軽)。②の「原文にない」は、ユーザー引用の3文の範囲では追加に見えるが実データでは英文4文目の訳(委任_01Aと同結論)。Std 11/29群・Adv 7/30群が不適切。全群表=`ev01/AI_CHAT_FULL_01.md`。
- 判定者は同一モデル・同一セッション。第2判定の一致率(分類98.7%、2値99.7%、κ=0.994)は自己一貫性であり独立評価ではない。**Fable抜き取り用ブラインド20件**=`ev01/FABLE_BLIND_SHEET_20.md`(キー=`ev01/FABLE_BLIND_KEY_20.json`)。

## 未確認事項
実機表示(連動ハイライト時の見え方)、ユーザーが実画面で見た群の境界(②の見え方)、R2台本生成Promptの逐語(REVISION_INSTRUCTIONS)・`voice_generate_02.txt`の翻訳配慮の有無、解説内対訳の抽出外、他記事・今後の記事への影響は推定(X/Y新記事も同経路で同様の統合が起きる見込み。実測は公開済み10記事)。

## 次委任の入力(Fable判断材料)
原因仮説: 日本語原稿が英文に先行し、検査が「同一性/段落数」にとどまる(G1)+Std/Adv共有(G2)。根拠値: approved Std 35.2% vs generated 0%。差分: 前回(JA-GLOSS-QUALITY-ALARM)は語句訳の品質で、今回は文・段落の対応が主因。次の一手候補(改善見込みは自己評価): (a)X/Y本文にも`generated`と同じ文ID単位の翻訳経路を使う(見込み高、Prod変更・新仕様=ユーザー判断)、(b)approvedに対訳照合のみ追加して警告化(見込み中、情報が欠落した場合のみ検出)、(c)StdだけEn-Jaの共有を止めStd専用訳を生成(見込み高)。いずれも仕様変更でありユーザー判断が必要(`判断候補`: D真に新しい判断)。

## RESULT_PACKET 4行
(1) 既存仕様整合: `CURRENT_SPEC.md:3278`(訳の非表示=承認済みデータのみ、X=revision2、Y=dev page内承認済み原稿)、`:2090`(Std Part1拡張=新規記事から)、`:1405`付近(旧Fact Checker撤去2026-10-10)、`er135_enduser_page_01.py:631-657`、`er135_enduser_translate_01.py:38-67`。実装は仕様どおり。仕様自体に「訳として対応が取れること」の要件が書かれていない点が今回の論点。
(2) Production到達経路に入る未承認機能: なし(コード変更0、調査のみ)。既定値確認: Prodファイル変更0(`git diff --name-only`でev01/とdocs/research/JA-TRANSLATION-LITERALNESS-AUDIT-01/のみ)。
(3) 失敗終了時の成果物: 該当なし(正常終了)。最終成果物=`docs/research/JA-TRANSLATION-LITERALNESS-AUDIT-01/{INVENTORY_01.md,COMPARISON_01.md,COMPARISON_RUBRIC_01.md,RESULT_PACKET_JTA_01B.md,ev01/}`。ユーザー原文は`docs/pm/delegation_log/2026-10-31_JA-TRANSLATION-LITERALNESS-AUDIT-01_USER.md`(origin/mainで取得、§1/§5/§6を照合)。目的適合: 本件は調査のみで、原文§5(棚卸し)と§6(実データ照合・分類1〜6)に回答。「単純直訳ではなく自然な日本語で英文の意味・情報・構造を保持し英文と照合できること」を物差しにした。
(4) 撤去・残置した規則/test: 撤去なし・追加なし(調査のみ)。残存Grep: 該当なし。
判定整合: 重大NG=なし / 主因=G1,G2 / 是正対象=G1,G2,G3 / STOP理由=なし / 提示=証拠のみ
