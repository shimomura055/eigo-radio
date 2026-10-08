# DESIGN_01: Writer根本設計「Fact Lock」Trial(FACTLOCK-WRITER-REDESIGN-TRIAL-01、委任_01、2026-10-08)

位置づけ: **設計案v2(Opus条件Aレビュー反映済み、2026-10-08。改訂履歴は末尾)**。Trial専用でProduction経路ではない。`APPROVED_FOR_PRODUCTION`なし。Status上限=READY_FOR_GENERATION(生成は委任_02b)。
v2の主な変更: タグ形式を`【事実N】`へ(O1)/R0・R1・R2へ「修正指示最優先」(M2)/R0へ不在・唯一の断定の禁止と暮らしの接続の推量形(M4)/数字規則の明確化(M5)/R1・R2のタグ継承と言い直し・仮定の許容(M6)/照合(i)を文×タグ事実の和集合の主張分解に(M1)/照合(ii)を5分類・タイトル対象化(M7)/タグ除去の強化と残存記録(M3)/数量語の副指標(O2)。
本書の記述区分: 【確認】=コード・ファイルで確認した事実、【設計】=本Trialで採る案、【未検証】=まだ動かしていない部分。本委任でAPI呼び出しはしていない(¥0)。

## §0 目的と問い

- 目的: **Writerが台帳(Selected Fact Brief)から誤った事実を書かない**ようにする。
- 問い: 進行中Trial(ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01)の「6-luna×現行prompt」に対し、「6-luna×Fact Lock」で事実NG(重大/軽微)がどれだけ改善/悪化するか。数値化のみ。**しきい値なし**。
- ユーザー方針(2026-10-08): 面白さはEntertainment Revision(R1/R2)で確保/Factは従来どおりB3で絞る/数値・細かい情報は読者に読みづらくReviseでも消えないので**Write時に規制**/それ以外はWriter時点で「嘘をかかない」ように固める。
- **決定A(Writer単一パス自由生成・prompt不変)の例外Trial**。ユーザー指示に基づく。Trial結果が良くてもProduction採用は人間ユーザーのみが承認する。
- 変えるもの: JA Writer(R0/R1/R2)のprompt追記のみ。変えないもの: B3 brief、JA Fact Check(R0直後・R2直後、must-fix1回・STOP)、EN phase2、Checker(ON、進行中Trialと同一構成)、モデル(進行中Trialの6-luna構成と同一)、R3は使わない(2回のまま)。

## §1 R0(JA初稿)への追加規則【設計】

R0 promptは `build_original_prompt()` が `R0_PROMPT + [ニュース]brief + SYMBOL_PREVENTION_BLOCK_JA + CONCRETENESS_CONTROL_AN3_BLOCK` を連結する構成【確認: er019 writer L148-168】。`CONCRETENESS_CONTROL_AN3_BLOCK` は**呼び出し時にモジュール属性として読まれる**ため、harnessがこの定数を差し替える(関数内リテラルではないので同一引数のまま注入できる)。

(a) **出典タグ**: 世界について断定する文は、文末の句点の直後に根拠factの番号タグを付ける。複数factは `【事実1,事実2】`。番号はbriefにあるものだけ。タイトルにはタグを付けない。問いかけ・感想・語りかけ・つなぎは不要だが、新事実は断定しない。**暮らしとのつながりは、問いかけや「〜かもしれない」の形で示し、具体的な事実を断定しない(M4。R0_PROMPT L58「暮らしとのつながりを一度示す」と規則3の衝突の解消)**。
- **タグ形式は `[F-xxx]` ではなく `【事実1】`**【確認】: 既存の音声化禁止記号Gate(`safety.detect_prohibited_symbols`、`_BRACKET_RE=[()（）\[\]]`)がJA R0/R2の角括弧を検出してmust-fix→STOPさせる。`【】`はGate対象外(単体テストで両方確認済み)。v2(O1)で旧`【F1】`から`【事実1】`へ変更: 台帳ID(F-001/HF-002)との混同回避。内部ID表現は従来どおり`F1`(`tag_ids`が変換)。
- **IDはbrief内ローカル連番(事実1〜)**: 台帳のfact IDはbriefによって有無・形式が違う(meta b1/b2は無し、b3/b4はMUSE-HC-nnn、space_weaponsはF-001、hormuz b4はHF-nnn)ため、注記版briefの事実行頭に `【事実1】…` を機械付与する。briefに元からある台帳ID(例 `F-001：`)は無変更で残る(数値判定からは除外)。→リスク§8。
- 事実でない行(Storyline行、`Storyline：`重複行、`素材:`)にはタグ番号を振らない。

(b) **台帳にないことは書かない**。背景知識・常識補足も不可。述べられていないことは「〜かどうかは分かっていない」と書いてよい(推測で埋めない)。事実の範囲・確かさ・方向を台帳より強く/広くしない。briefの「〜ではない」「断定しない」を守る。**v2(M4): ニュース欄が触れていない点(誰が・いつ・何人・理由・結果)を、「〜しなかった」「〜はない」「唯一」「初めて」などと断定して埋めない**(規則4末尾に追記)。

(c) **数値規則(c)=ユーザー承認**: briefで `【中核数値】` 印の付いた数値のみ使用可。表記は台帳のまま転記(丸め・単位換算・「約」の追加削除・比較値の自力計算禁止)、本文の文にタグ必須。**タイトルでも中核数値は使えるが、タイトルにはタグを付けない(M5。規則間の矛盾解消)**。`【周辺数値】` は書かない。**v2(M5): ただし周辺数値を含む事柄は、数字を省いて述べてよい(例: 番号を書かずに「ロシアの衛星」、日付の代わりにニュース欄にある「同日」「翌日」)。禁じるのは数字の大きさを「大きく」「急に」「多数」などの言葉で表すことだけ**(v1の「定性語への言い換えもしない」を、数字を省く書き方は許容する形に明確化)。印のない数値は使わない。印そのものは記事に書かない。
- **名称内の番号(COSMOS 1408・第4条)=案A(Opus推奨、Fable決定)**: 周辺のまま、数字を省いて名称を書く(例「ロシアの衛星」「条約の条文」)。「識別子は転記可」という例外は作らない(案B不採用)。細かい情報が減る・不自然さが出るかは目視で測り、所見をユーザーへ報告する(ユーザー判断は結果報告時)。
- 中核は記事あたり最大3。選定はB3(今回は**実装者(Claude)による手付けの後付け注記**。本番ではB3が指定する想定)。**限界(M9/Opus 2(c)): 8本が上限ちょうどの3件で、選んだのはB3ではなく実装者。B3が中核数値を選んだ場合の性能は未測定**。

(d) **現行AN3との関係=置換**: AN3の「数字・時刻は基本的に使わない…必要な場合だけ最小限」を、(c)の数字規則に**置換**する。AN3の第2文(固有名詞は必要な場合だけ)は**逐語で保持**し、Fact Lock規則6として併記する。理由: AN3の数字文と(c)は同一テーマで矛盾しうる(「必要なら使ってよい」vs「印のあるものだけ」)ため併記すると解釈が割れる。→これは`APPROVED_FOR_PRODUCTION`のAN3を**Trial armの中でだけ**書き換える変更であり、Opusに確認してほしい論点(§9)。

(e) **修正指示の優先(M2)**: R0規則7として「事実確認の修正指示がある場合はそれを最優先し、直すか削る。」を追加(R1/R2は§2の規則7)。must-fix再生成(台帳に合わせた数値修正等)とFact Lock規則(数字は表記のまま・ニュース欄外は書かない)が衝突したとき、修正指示が勝つ。

R0 prompt追記全文は `er052_factlock_writer_trial_01_run.py` の `FACTLOCK_R0_BLOCK_HEAD` + `FACTLOCK_R0_BLOCK_TAIL`(sha256は`FIXED_SHAS.json`)。

## §2 R1/R2(Entertainment Revision)への追加規則(7則)【設計】

R1/R2の指示は `REVISION_INSTRUCTIONS["r1"/"r2"]`(dict、呼び出し時に参照)に `+ SYMBOL_PREVENTION_BLOCK_JA` を連結して送られる【確認: L361】。harnessがdictの値に `FACTLOCK_REVISION_BLOCK` を追記する。R2のFact Check must-fix再生成(L404)・記号must-fix再生成(L463)も同じdictを参照するため、**全経路に一貫して効く**【確認】。

現行の「事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください」は**そのまま残して併記**(置換しない)。追記する規則:
1. タグ付き文の事実の中身は変えない(言い回し・順序・比喩・テンポは自由)。
2. 新しい事実文を加えない。加えてよいのは問いかけ・感想・語りかけ・つなぎ・**「もし〜なら」と分かる形のたとえ話・仮定(M6、面白さを作る余地)**のみ(これらも新事実を断定しない)。
3. 削除は自由。
4. 「分かっていない」と書かれたことを推測で埋めない。
5. タグは文に付けたまま残す(言い換え・並べ替えでも事実に対応する文に付ける。新規の非事実文には付けない)。**文をまとめたら両方のタグを付け、分けたらそれぞれに該当するタグを付ける。記事にすでにある事実の言い直しは新事実に当たらない(M6)**。
6. 数字は記事にすでにあるものだけを表記のまま。新しい数字を足さない・丸めない・再計算しない。
7. **事実確認の修正指示がある場合はそれを最優先し、直すか削る(M2。規則6とmust-fix再生成の数値修正指示の衝突を解消)**。

R3以降は今回は使わない(正式フローの2回のまま)。

## §3 タグ照合(各段R0/R1/R2、**測定のみ。STOP・再生成なし**)【設計】

実装位置: phase1(Brief→JA R0/R1/R2)完了後、EN phase2へ渡す前に、保存済みの `ja_writer/original.md / revision1.md / revision2.md` に対して実行する(測定のみで生成を変えないので、各段直後に走らせるのと結果は同等。must-fix再生成が起きた場合は**最終的に採用された**R0/R2本文を測定する)。

(i) **v2(M1): 文 × その文に付いたタグの事実の和集合 の主張分解判定(LLM、1段1call)**: v1は「1文×1事実」で、複数タグ文では他タグの事実が「付け足し」と見なされ不整合・判定不能が水増しされ、複合推論も評価できなかった。v2は各タグ付き文について「直前の1文(文脈・代名詞対策、判定対象ではない)」「文」「その文に付いたタグの事実だけ」を渡し、文の主張を分解させ、主張ごとに `{claim(30字以内), supporting_ids[], status: supported/unsupported/undecidable}` を出力させる。**文単位の集計(決定論 `aggregate_claims`)**: 全主張supported=整合 / 1つでもunsupported=不整合 / それ以外(主張なし含む)=判定不能。主張単位の集計(`claim_counts`)と、タグ外の事実IDを根拠に挙げた件数(`supporting_outside_tags`)も保存。briefに無い番号のタグは決定論で `unknown_tags` に数える(LLMに出さない)。モデルは既存JA Fact Checkと同一の6-luna(`WRITER_FACT_CHECK` override)。
(ii) **v2(M7): タグなし文(タイトルを含む)の5分類(LLM、1段1call)**: `neutral`(問いかけ・感想・語りかけ・つなぎ・比喩導入)/`untagged_brief_fact`(brief内容だがタグ漏れ)/`hedged_speculation`(推量・可能性の形の暮らしとのつながり・予測)/`background_general`(用語説明・一般常識)/`new_specific_claim`(briefに無い出来事・因果・数値・主体・不在の断定。伝聞形も含む)。判断基準「briefだけを根拠に読者が新しい具体的な事実を得るか」。**タイトル(1行目)は(ii)の対象に含める**(タグなしなので。前夜のループで誤りが集中した構造要素)。中核数値の照合(iii)もタイトルに適用(従来どおり)。v1の`unsupported_assertion`は`new_specific_claim`+`background_general`+`hedged_speculation`に分割(v1との直接比較は不可)。
(iii) **数値(決定論)**: §3-1の正規表現で本文数値を抽出し、briefの `core_numbers.json` と照合。status = `match`(表記一致)/`match_surface_diff`(値・単位は一致、表記違い。例 漢数字化)/`hedge_changed`(約・およそ・超 等の付加/削除)/`not_core`(中核リストに無い=周辺数値・新規数値・丸め等)。**不一致=hedge_changed+not_core**。`core_used_without_tag`=中核数値が出たのにタグが無い文。数値印(`【中核数値】`等)をWriterが書き写した件数 `marks_echoed` も記録。**v2(O2): 数量語(半分・倍・ひとつ・いくつか・多数・たくさん等)の件数を `quantity_words`(副指標、判定=mismatch_totalには使わない)として別カウント**。
(iv) **R0→R1→R2のタグ付き文の差分(決定論)**: 同じタグを共有する文のうち最も文字bigram類似度(Jaccard)が高い対応文で判定。sim≥0.9=維持/0.3≤sim<0.9=改変/それ以外=削除。次段にだけあるタグ付き文=added。数字トークン集合が変わった組=number_changed。「改変」は**言い換えがあったこと**で、**事実が変わったか**は(i)を次段の本文で測る。

既存JA Fact Check(R0直後・R2直後、Full Ledger vs JA記事、must-fix 1回・STOP)は**現行どおり残す**。両条件で同一。ただしFact Checkへ渡す本文は**タグ除去済み**にする(harnessが`vfl01.run_deviation_check`をラップし`strip_tags`、`source_article_text`も同様)。理由: 両条件で判定入力を同一にし、タグが判定を変えて比較が交絡するのを防ぐ。

### §3-1 数値抽出の正規表現(Grep `\d` パターン設計)【確認: 単体テスト済】
1. 事前処理: NFKC(全角→半角、`％`→`%`、`，`→`,`)。出典タグ(v2: strict `【事実\s*\d+(,(事実)?\d+)*】` + 広め `【\s*[FＦ事実][^】]{0,30}】`)、数値印、**台帳ID** `(?<![A-Za-z0-9])[A-Z]{1,8}(-[A-Z]{1,4})?-\d{1,4}(?![A-Za-z0-9])`(MUSE-HC-006/HF-002/F-001)を空白化。
2. アラビア数字: `(約|およそ|ほぼ|だいたい|数)?(第)?\d+(,\d{3})*(\.\d+)?([万億兆千百])?(単位)?(超|以上|以下|近く|ほど|前後|余り)?`。単位=バレル/ドル/ポイント/パーセント/カ国/世紀/番目/時間/%/円/個/件/人/年/月/日/時/分/秒/条/倍/割/社/台/基/隻/本/歳/回/位/度/つ。
3. 漢数字: 位取り(十・百・千・万・億・兆を含む)の列、または「一〜九・〇・零・十」の列で**直後に単位**が付くものだけ。除外: 一部・一方・一度・一緒・十分・万が一・万全・千葉・百科 等(単位語が付かない/個別除外)。値は整数に換算(二十→20、三万→30000)。「数千」は hedge=数 付きの1000。
4. 比較キー=(値, 単位)。日付は「2026年9月14日」→(2026,年)(9,月)(14,日)の原子トークンに分け、中核リストの原子と比較(「9月14日」だけ書いてもmatch)。
5. 既知の限界: ひらがな数詞(ひとつ・ふたり)、「半分」「倍」「数年」等の数量語、英数字混じり(COSMOS 1408は番号1408を数値として拾う=周辺指定済み)。これらは決定論では漏れる。

## §4 タグ除去【設計】

R2確定後、EN phase2・Checkerへ渡す前に、正規表現(strict `【事実N】` + **v2(M3)広め除去 `【\s*[FＦ事実][^】]{0,30}】`**(`【Ｆ1】【F2-3】【事実 1-2】`等の変形を消す)+数値印)で除去。**除去後の本文に残った「【」の件数(`residual_brackets_after_strip`、期待0)と、広め除去だけで消えた変形タグ件数(`broad_only_tags_removed`)を段別に`factlock_summary.json`へ記録**(測定のみ)。`【HF-002】`のような`F`/`Ｆ`/`事`/`実`以外で始まる変形は広め除去でも消えず、残存件数として現れる(設計上の既知の限界、目視対象)。除去前は `*_with_tags.md` として保存、元の `original.md / revision1.md / revision2.md` を**除去版で上書き**(以降の段・盲検評価パック作成が現行と同一構造で動くように)。EN側は現行どおり。Checkerの `--source-path` も除去版 `revision2.md`。

## §5 brief注記【設計・実施済】

B3 V0 brief 12本(meta/hormuz/space_weapons×b1〜b4)を**コピー**して `briefs/<slug>/b<i>/selected_brief_factlock.md` を作成(原本は無変更、sha一致を`FIXED_SHAS.json`に記録)。付与: 事実行頭 `【事実1】…`(v2でO1変更、`tools/annotate_briefs.py`修正で再生成、原本sha不変を再確認)、数値の直後に `【中核数値】/【周辺数値】`。記事あたり中核は最大3、判断理由は `briefs/ANNOTATION_LOG.md`、中核リストは `core_numbers.json`。注記スクリプト `tools/annotate_briefs.py` は「印の付いていない数値が残っていない」ことを機械検証する。結果: 中核0件=4本(meta全て、briefに数値なし)、中核3件=8本(hormuz4・space_weapons4)。

## §6 比較設計【設計】

- セル: **6-luna×Fact Lock**。12 brief×2反復=**24本**。Checker ON(進行中Trialと同一構成=同スイッチdump、新スイッチ既定OFF)。
- 比較対象: 進行中Trialの「6-luna×現行(all6)」「5.6×現行(baseline)」(各24本の見込み、同briefの同条件)。
- 評価: B3 rubric(`docs/pm/b3_trial_01/eval_rubric.md`)の盲検採点。**v2(M8): 進行中Trialのall6記事とFact Lock記事を、同じ評価パック・同じ評価者で一緒に採点する(必須。「可能なら」を削除)**(評価者にはセル非開示、匿名コード、MAP隔離)。**STOPした記事も母数に含め、そのR0(と到達した最終段)を評価する**。評価者はLLM単独判定(進行中Trialと同一運用)。主指標は盲検rubric採点に限る(照合(i)(ii)(iii)は測定のみ)。
- 主張の範囲: 「パッケージ全体(5要素)の効果」としてのみ報告する(追加セル「6×現行prompt×注記版brief」(O3)は不採用、下記改訂履歴)。
- 面白さ(副指標): 同briefの「6×現行 対 6×Fact Lock」のpairwise(LLM判定+位置入替2回、人間確認なし)。
- out_dir: `er052_output/factlock_writer_trial_01/runs/<slug>/control/b<i>__factlock__r<j>`(DEV runnerのout_dirガードが`/control/`を要求)。

## §7 指標(しきい値なし)

| 区分 | 指標 | 出所 |
|---|---|---|
| 主 | 重大/軽微NG/記事(JA R2・EN別、テーマ別)、保留/記事、R0→R2退行件数 | rubric盲検採点 |
| 照合 | (i)文単位の不整合率・判定不能率(`counts`)と主張単位(`claim_counts`)、unknown_tags/記事、(ii)5分類の件数(new_specific_claim・background_general・hedged_speculation・untagged_brief_fact・neutral)/記事(段別、タイトルの分類`title_label`含む)、タグ付き文率 | `factlock_check_r{0,1,2}.json` |
| 数値 | (iii)不一致件数(hedge_changed+not_core)/記事(段別、タイトル含む)、core_used_without_tag、marks_echoed、quantity_words(副指標)、最終R2にある数値の数 | 同上 |
| タグ除去 | residual_brackets_after_strip(期待0)、broad_only_tags_removed、manifestの`residual_bracket_scan.unexpected` | `factlock_summary.json`、`manifest.json` |
| 改変 | R0→R2のタグ付き文の 維持/改変/削除/added/number_changed | `factlock_diff.json` |
| 工程 | JA Fact Check MAJOR率・must-fix率・STOP率、記号Gate must-fix率、Checker findings/Rewrite件数 | 各run |
| コスト | 費用/本、所要時間/本(照合分を別掲) | raw_usage_log |
| 面白さ | 盲検pairwise(副指標)、タグによる文体の窮屈さ(目視所見のみ) | eval |

## §8 リスク・限界

- N小(24本/セル)。差と比のみ、有意性は主張しない。
- 比較セルの交絡: Fact Lockは(1)出典タグ(2)台帳外禁止(3)数値規則(c)(4)R1/R2事実固定規則(5)briefに印/IDが付く、を**同時に**変える。どれが効いたかは分離できない(分離したい場合は別Trial)。briefも「印付き版」で、現行セルの印なし版と文字列が異なる。
- **中核数値の注記は実装者(Claude)の手付け(M9)**: 8本が上限3件ちょうど。選定はB3ではなく実装者の判断で、B3が中核数値を選んだ場合の性能は未測定。meta 4本は元briefに数字がなく、どちらの条件でも実質同じ(Opus 2(e))。
- **照合(i)(ii)はWriterと同系列モデル(6-luna)の自己判定**で、同じ盲点を共有しうる。照合は測定のみで、主指標は盲検rubric採点に限る。
- **名称内番号は案A(数字を省く)**: 「ロシアの衛星」「条約の条文」のように細部が減る。読みやすさ・不自然さは目視所見で測る。
- 数値規則は「中核が少ない」記事(meta=0件)では事実上「数字を一切書かない」条件になり、現行(AN3・必要なら最小限)より厳しい。
- (i)(ii)はLLM判定(6-luna=Writerと同系列)で、同じ盲点を共有しうる。照合は**測定のみ**で、盲検採点(rubric)が主指標。
- タグがR1/R2の自由度を下げ、文章が窮屈になる可能性(面白さの副指標と目視で確認)。
- タグ付け忘れ・タグの付け替え(無関係な文に正しそうなタグを付ける)は(i)で一部検出するが、(i)も同じLLM。
- Selected Facts外の背景知識(例: 一般常識の補足)は(ii)の `unsupported_assertion` の境界。判断が分かれる。
- 台帳ID(F-001等)とローカルタグが同一briefに共存し、Writerが混同する可能性(b3/b4 meta、space_weapons、hormuz b4)。v2で`【事実N】`形式へ変更し緩和(O1)したが、混同が皆無になる保証はない。
- 「〜かもしれない」等の鉤括弧内の波ダッシュ「〜」を含む例示がprompt内にある(既存のSYMBOL_PREVENTION_BLOCK_JAは波ダッシュを省略の言い換えとして使わないよう求める)。Writerが「〜」を出力へ書き写す可能性は低いと見るが、smokeで記号Gate must-fixが出ないかを確認する。
- 既知の穴: `someone`型(主体の曖昧化)、方向型(ロールバック等)は文字照合では検出しにくい。
- 測定器の限界: 数値抽出はひらがな数詞・数量語を漏らす(§3-1-5)。(iv)の文対応はbigram類似度でありLLMほど意味を見ない。
- 評価者差(LLM単独、2系統)。タグ除去後も文体の癖(「分かっていない」の頻出等)で盲検が破れる可能性。
- 【未検証】DEV runner(phase1→後処理→phase2)の実機通し。単体テストはmockで、実機は委任_02のsmoke(1本)で確認する。

## §9 Opusレビューで特に見てほしい論点

1. **タグ規則の抜け道**: 「問いかけ・感想・つなぎ」を装った新事実の断定、タグの付け替え(正しいタグを別内容の文に付ける)、複数タグ文の合成推論、背景知識の混入。(i)(ii)の測定でどこまで拾えるか。
2. **数値規則(c)の穴**: 周辺数値の「定性語への言い換え禁止」は、読者にとって不自然な省略になるか。日付・順序(翌日)・名称内の数字(COSMOS 1408・第4条)の扱い。中核0件(meta)の記事で数字を全く出さない条件は妥当か。AN3(APPROVED_FOR_PRODUCTION)をTrial armで置換する点。
3. **R1/R2規則が面白さを過度に縛らないか**: 「タグ付き文の事実の中身は変えない・新事実文を足さない」で、Entertainment Revisionの演出幅(比喩・語り・問いかけ)が残るか。タグを残す指示が文構造を固定化しないか。
4. **照合(ii)の分類基準**: neutral / untagged_brief_fact / unsupported_assertion の線引き、特に「一般論の感想」「読者の暮らしへのつながり」(R0_PROMPTが求める)がunsupported_assertionと判定される衝突。R0_PROMPT自体が「読者の暮らしとのつながりを一度示す」と指示している点との整合。
5. **比較設計の交絡**: 5要素が同時に変わる設計、印付きbrief、進行中Trialとの時間帯差・評価パックの同一性、pairwise判定者の独立性。

## §9a Opusレビュー(条件A、2026-10-08)後の状態
Opus全文は `docs/pm/opus_l2_review_factlock_writer_trial_01.md`。総合判定「修正後に進む(小規模)」。M1〜M9を反映、O1・O2採用、O3・O4不採用。反映箇所は本書の各§(v2注記)と改訂履歴。上の§9は委任_01時点のレビュー依頼論点で、回答は上記全文にある。

## §10 委任_02b の実行手順・費用・時間(確定版)

開始条件(全て満たすまで開始しない):
- (a) Opus条件Aレビュー反映済み(本v2)+Fableが次工程へ進む判断。
- (b) 進行中Trial(ALL-6-LUNA-...)の**生成が完了**: `er052_output/all6_writer_redesign_necessity_01/MANIFEST.json`の存在と全48 runのexit記録(4並列生成・メモリ/rate limitの競合回避)。
- (c) 費用上限¥150(下記T-3定型文)。

手順:
1. **smoke 1本(hormuz/b4、反復1)**: 数値規則の効き目が見える(周辺数値が多い)。確認: R0/R1/R2でタグ`【事実N】`が出るか、記号Gateでmust-fix/STOPが出ないか(波ダッシュ例示の影響含む)、phase1→後処理→phase2が通るか、model_id実測、`marks_echoed`、checkerが除去版を使うか、周辺数値が数字を省いて書かれているか(「同日」「翌日」等)。
2. **「【」残存確認(M3)**: smokeのrun dir全体のうち`*_with_tags.md`以外に「【」が残っていないことを確認する。`manifest.json`の`residual_bracket_scan.unexpected`が空であること、`hits`にある許可リスト該当ファイル(brief複写・監査ログ・照合結果)の中身が入力・照合由来のみであること(phase1が別ファイルへ本文を書いていないかの確認を兼ねる)、`factlock_summary.json`の`residual_brackets_total`が0であること。**STOP**: harness起因エラー、R0にタグが全く出ない、または記事本文系ファイルに「【」が残る場合は設計を修正して再smoke(最大1回)。
3. 本番24本(`--budget-jpy 12`/run): 12 brief×反復2、4並列(自動降格4→2→1は進行中Trialのdriver方式に準拠)。1枠の技術的失敗は再実行1回まで、全体4回まで(JA Fact Check STOPは結果として記録し再実行しない)。
4. タグ照合は各run内で自動(`factlock_check_*.json`)。集計script・盲検パック・評価は並列で先行準備可。
5. 盲検採点(rubric)+pairwise: **all6記事(進行中Trial)と同一パック・同一評価者で一緒に採点(M8必須)**。STOP記事も母数に含めR0(と到達した最終段)を評価。

費用見積(6-luna単価・進行中Trialのcost.jsonは6-lunaが0円計上になるためraw_usage_logから再計算する方針を踏襲):
- 生成24本: 見積前提A(委任文の想定)≈¥2.5〜3.5/本=≈¥60〜85。ただし進行中Trialの事前登録は「all6 ≈¥5/本」と記載しており、前提B(≈¥5/本)なら≈¥120。タグ追記でprompt/出力が増える分は未実測。
- 照合(§3、1runあたりLLM最大5〜6call)≈¥15。評価(盲検採点+pairwise)≈¥20。
- 合計 ≈¥95〜155。smoke分を含む。
- **上限¥150(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**

時間見込み: smoke≈15分、本番24本は4並列でwave 6回×約10〜15分≈60〜90分(進行中Trialの1本あたり所要の実測を要確認)、照合は各run内、集計+盲検評価≈30〜40分。全体≈2〜2.5時間(待ち時間含む)。並列化: 集計script・評価パック作成・rubric準備は生成待ちの間に先行。直列の理由: 生成(前工程出力に依存)→評価。

## 付録: 注入方式のまとめ(monkeypatch、Production無編集)

| 対象 | 方式 | 注入点 |
|---|---|---|
| JA Writer/FactCheck/EN phase2のモデル | ALL-6 harness(`er052_all6_writer_trial_01_run.apply_all6_patches`)を再利用(read-only import) | `jaw.WRITER_MODEL` ほか |
| R0 prompt | モジュール定数の差替え | `jaw.CONCRETENESS_CONTROL_AN3_BLOCK` |
| R1/R2 prompt | 定数dictのin-place更新 | `jaw.REVISION_INSTRUCTIONS` |
| Fact Check入力のタグ除去 | 関数ラップ | `vfl01.run_deviation_check` |
| 後処理(照合・除去) | phase1とphase2の間にharnessが実行 | `postprocess_phase1()` |

## 改訂履歴
- v1(2026-10-08、委任_01): 初版。Opus条件Aレビュー対象。
- **v2(2026-10-08、委任_02a、Opus条件A M1〜M9反映、O1/O2採用、O3/O4不採用)**: Opusレビュー全文は `docs/pm/opus_l2_review_factlock_writer_trial_01.md`。
  - M1: §3(i)を文×タグ事実の和集合の主張分解に。M2: R0規則7・R1/R2規則7。M3: 広め除去+残存件数記録+scan関数+§10手順。M4: R0規則2・4。M5: R0規則5(周辺数値は数字を省いて述べてよい、タイトルは中核数値OK・タグなし)。M6: R1/R2規則2・5。M7: §3(ii)5分類・タイトル対象化。M8: §6・PREREG(同一パック必須、STOP記事も母数)。M9: PREREG「言えること/言えないこと」、§8に手付け注記の限界。
  - O1: タグ形式`【事実N】`(harness正規表現・注記brief12本・テスト・設計書を更新)。O2: 数量語の副指標`quantity_words`。
  - **O3不採用**: 追加セル「6×現行prompt×注記版brief」は、本Trialが「パッケージ全体(5要素)の効果」の測定であり要素分離を目的としないため。**O4不採用**: 前夜の重大2件(jb9k・89wf)型での¥0 dry検証は、時間優先(生成を先に進める)のため。いずれも優先度低(Opus自身が任意と位置づけ)。
  - 名称内番号(COSMOS 1408・第4条)は案A(周辺のまま、数字を省いて名称を書く)で実施。所見は結果報告時にユーザーへ(ユーザー判断は結果報告時)。
  - sha再固定(v1→v2の差分): `FIXED_SHAS.json` の `superseded_v1` に旧値を保存。旧値(先頭12桁): harness run `dac150add6f7` / test `7bc85de1bbf9` / annotate_briefs `43e75fc1dcfb` / FACTLOCK_R0_BLOCK `4e0bcfecc23e` / FACTLOCK_REVISION_BLOCK `3cb035e7f1d6` / PAIR_PROMPT `f18c875f1caa` / UNTAGGED_PROMPT `bd8c242a2baf` / 注記brief12本とcore_numbers12本は`superseded_v1.briefs`に全桁。不変: R0_PROMPT、AN3_original、all6 harness、Production 3モジュール、原本brief12本。
