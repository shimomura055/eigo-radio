# ER-005-SOURCE-RETRIEVER-01 実行報告書

**タスク**: 非AI Source Retriever成立性検証
**実行日**: 2026-08-19
**対象URL**: `https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1794353/full`(前タスクと同一URL、既知URLへの直接アクセスのみ、Topic Selection・Search再実行なし)

---

## 完了報告の最上段(12章の必須回答)

1. **AIなしで本文取得できたか**: **できた**。使用したのは通常のHTTP GET(`requests`)とHTMLパース(`beautifulsoup4`、標準の`html.parser`)のみで、AI/LLM呼び出しは一切ない。
2. **外部有料APIなしで取得できたか**: **できた**。Perplexity Search、Jina Reader、Tavily Extract等の外部有料Retriever APIは一切使用していない。
3. **前回WebFetch比で重要情報の欠落はあったか**: **欠落なし、むしろ前回より情報量が多い**(下記C章)。
4. **表・統計数値は保持できたか**: **保持できた**。Table 1(参加者属性)・Table 2(相関行列)・Table 3(SEM直接効果・間接効果、標準誤差付き)の3表全て、数値を含めて抽出できた。
5. **Evidence Pack入力として十分か**: **十分**。前回のEvidence Pack(28件)を再構成するために必要だった情報を全てカバーしており、追加でSE値・Harman's single-factor test値・SES算出式・倫理承認番号・研究資金情報等も新たに取得できた。
6. **Costはいくらか**: **$0.00**(外部API課金$0、AI token cost $0、Search cost $0。通常の通信費のみ)。
7. **判定**: **`SIMPLE_RETRIEVER_PASS`**
8. **Jina Reader / Tavily Extractを試す必要があるか**: **不要**。SIMPLE_RETRIEVER_PASSのため、仕様9章の規定通りFallback候補の実行は行っていない(候補としての記録のみ、下記G章)。

---

## A. 実施内容

```python
resp = requests.get(url, headers={"User-Agent": "..."})
soup = BeautifulSoup(resp.text, "html.parser")
main = soup.select_one("main.ArticleDetailsV4__main")
text = main.get_text(separator="\n", strip=True)
```

- HTTPステータス: **200**(リダイレクトなし)
- Content-Type: `text/html;charset=utf-8`
- 生HTMLサイズ: 1,092,078 bytes
- 抽出後テキストサイズ: 68,877文字
- 検出したTable数: **3件**(参加者属性表、相関行列表、SEMパス係数表)
- `robots.txt`確認: `https://www.frontiersin.org/robots.txt`は`/journals/psychology/articles/...`配下を明示的に許可している(Disallow対象は`/images/`, `/production/`, `/review/`, `/mail/`, `/admin/`等の管理系パスのみ)

**JavaScript実行は不要だった**: 著者名・サンプルサイズ・DOI・Abstract・各セクション見出し・統計値が、サーバー返却時点の生HTMLに全て含まれていることを確認した(`requests`のみでSPAシェルではなく実コンテンツを取得できている)。

---

## B. 取得対象の充足確認(4章)

| 取得対象 | 結果 |
|---|---|
| Title | ✓ |
| Authors | ✓(Xiaojun Ling, Mengqi Li, Jiahui Sun、所属機関も含む) |
| Publication date | ✓(Received/Revised/Accepted/Published の4段階全て) |
| DOI | ✓ |
| Abstract | ✓ |
| Introduction | ✓ |
| Methods | ✓(Participant and procedures / Materials / Data analysis) |
| Sample / participants | ✓(619→588→532、脱落87人14.1%、wave別脱落数31+56まで) |
| Measures | ✓(CPRS、SDQ、screen time計算式、covariates/SES算出式) |
| Results | ✓(記述統計・相関・ANOVA・SEM結果) |
| Statistical values | ✓(β・SE・p・95%CI、χ²・RMSEA・CFI・TLI・SRMR) |
| Tables/表中の重要数値 | ✓(Table 1〜3、全数値を含めて抽出) |
| Discussion | ✓(5.1〜5.3の全小節) |
| Limitations | ✓(6項目、原文ママ) |
| Conclusion | ✓ |

Navigation・広告・footerは、`main`要素配下に限定してテキスト抽出することで自然に除外された。唯一の軽微なノイズは、著者名直前に付随するアバターの頭文字アイコン由来と見られる断片("X" "L" 等の1文字トークン)だが、直後に正式な氏名がそのまま続くため実害はない。

---

## C. 前回WebFetch結果との比較(5章)

| 観点 | 前回(Claude Code WebFetch) | 今回(非AI Retriever) |
|---|---|---|
| セクション欠落 | なし | なし |
| 数値欠落 | なし(ただしTable 3のSE値は含まれていなかった) | **なし(SE値も含む)** |
| 表データ欠落 | Table 1・2は要約のみ、詳細な内訳なし | **Table 1・2・3を数値ごと完全取得** |
| 文字化け | なし | なし |
| 不要ノイズ | なし | 軽微(著者アバターの頭文字断片のみ) |
| 本文順序 | 論理的順序を維持 | 論理的順序を維持(HTML本文順そのまま) |
| Evidence Pack作成に必要な情報量 | 十分 | **前回を上回る**(下記) |

**今回のみ新たに取得できた情報**(前回のWebFetch要約には含まれていなかったもの):
- Table 3の標準誤差(SE)値
- Table 1の父母の学歴・職業カテゴリ別の詳細な内訳
- Table 2の完全な相関行列(7変数間の全ペア、r値・p値)
- Harman's single-factor test(共通方法バイアス検定、第1因子分散説明率27.95%)
- Family SES算出式(主成分分析の因子負荷量付き)
- 倫理審査承認番号(NT20231109)
- 研究資金情報(教育部人文社会科学研究プロジェクト、課題番号23YJC880066)
- Conflict of interest声明
- **Generative AI声明**(論文自体が「本原稿の作成に生成AIは使用されていない」と明記している点は、興味深い副次的発見)
- 査読者・編集者名、投稿受理までの日付推移(Received 2026-01-23 / Revised 2026-04-18 / Accepted 2026-04-29 / Published 2026-05-25)

WebFetchは内部の要約モデルを介するため、取得はできるが要約段階で一部の詳細(特に表の細目やSE値)が圧縮されていた。今回の非AI Retrieverは生HTMLをそのままテキスト化するため、要約による情報損失が原理的に発生しない。

---

## D. Production適性(Failure modeの整理、8章)

今回のFrontiers 1件では全てクリアしたが、量産時に想定すべき失敗モードを以下に整理する(今回は検証せず、整理のみ)。

| Failure mode | 今回の状況 | 量産時のリスク |
|---|---|---|
| Timeout | 発生せず(30秒timeoutで完了) | 低〜中。Publisher側のレスポンス遅延で発生しうる |
| Redirect | 発生せず | 中。DOIリンク経由アクセス時は複数回リダイレクトが発生しやすい |
| Robots / access restriction | 許可されていた | 中。出版社ごとにrobots.txtのポリシーが異なり、個別確認が必要 |
| JavaScript依存 | 不要だった(Frontiersはサーバーサイドレンダリング) | **高**。出版社によってはReact/Vue等のCSR構成でJS実行なしでは本文が取得できない場合がある |
| HTML構造変更 | 今回は`main.ArticleDetailsV4__main`のセレクタで安定して取得 | **高**。出版社サイトのリニューアルでセレクタが変わると抽出処理が壊れる。出版社ごとに個別のセレクタ・抽出ルールが必要になる可能性が高い |
| PDF-only source | 該当なし(HTML本文あり) | 中〜高。PDF-onlyの出版社・古い論文では、別途PDFテキスト抽出処理が必要 |
| Paywall | 該当なし(FrontiersはOpen Access、CC BY) | **高**。有料の壁がある出版社では、本文どころかAbstract以上を取得できない可能性が高い |

**総評**: 今回の1件検証は成功したが、これは「Frontiers = Open Access + サーバーサイドレンダリング」という好条件が揃ったケースである。出版社が変わるたびにセレクタ調整やJS対応、paywall対応が必要になる可能性が高く、Production量産時は出版社ごとの個別対応(または上記Fallback候補の併用)を前提に設計すべきである。

---

## E. Cost(7章)

| 項目 | Cost |
|---|---|
| 外部API課金 | $0.00 |
| AI token cost | $0.00 |
| Search cost | $0.00 |
| (参考)通常の通信・サーバーコスト | 対象外(仕様7章の規定通り) |

---

## F. 成立判定

**`SIMPLE_RETRIEVER_PASS`**

判定根拠:
- 通常HTTP取得(`requests`)+HTML本文抽出(`beautifulsoup4`、標準ライブラリのパーサーのみ)だけで、Evidence Pack作成に必要な全観点(4章の15項目)を欠落なく取得できた。
- 前回のClaude Code WebFetch結果と比較して、セクション・数値・表データのいずれにも欠落がなく、むしろSE値・完全な相関行列・倫理/資金/COI声明等、追加の情報を取得できた。
- AI token cost・Search cost・外部有料API課金、いずれも$0で成立した。
- Production実装として再現可能(Pythonの`requests`+`bs4`という一般的な非AI・無料ライブラリのみで構成)。

---

## G. Fallback候補(9章、参考記録のみ・未実行)

SIMPLE_RETRIEVER_PASSのため、以下は契約・APIキー追加・実行のいずれも行っていない。将来、別の出版社(特にJS依存・paywallのあるサイト)でSimple RetrieverがPARTIAL_PASS/FAILとなった場合の次段候補として記録するに留める。

1. **Jina Reader**(`r.jina.ai`) — URLをプレフィックスするだけでLLM非依存のReader変換を提供するサービス。JS依存サイトへの耐性が今回のBeautifulSoup方式より高い可能性がある。
2. **Tavily Extract** — 既にTAVILY_API_KEYを保有しているため、Search APIとは別にExtract機能を使える可能性がある(未確認)。

---

## H. 受入条件確認(11章)

- 既知URLから直接取得: **確認済み**(Topic Selection・Search再実行なし)
- AI不使用: **確認済み**(`requests`+`bs4`のみ、LLM呼び出しゼロ)
- Search API不使用: **確認済み**(Perplexity Search等は未使用)
- Claude Code WebFetchをProduction代替として使用しない: **確認済み**(今回の取得は全てPythonスクリプト経由、WebFetchツールは比較対象の「前回結果」の参照のみに使用)
- 通常HTTP + HTML抽出で取得: **確認済み**
- 前回WebFetch結果と内容比較: **確認済み**(本報告書C章)
- Evidence Packに必要なSection/数値の取得可否を確認: **確認済み**(本報告書B章)
- Costを明記: **確認済み**(本報告書E章、全て$0)
- Production上のFailure mode整理: **確認済み**(本報告書D章)
- PASS/PARTIAL/FAIL判定: **確認済み**(`SIMPLE_RETRIEVER_PASS`)

## I. Stop条件

Simple Retrieverの検証・前回結果との比較・Failure mode整理・Costの明記・Reportが完了し、判定が`SIMPLE_RETRIEVER_PASS`だったため、Jina Reader/Tavily Extractの実行は行わずここでSTOPする。Evidence Pack再生成・VFL再生成・Verification再実行・モデル比較・Production正式変更は行わない。

---

## J. 成果物一覧

- `er005_source_retriever_01.py` — 実行スクリプト(`requests`+`beautifulsoup4`のみ、AI/外部有料API不使用)
- `er005_output/source_retriever_01/retrieval_result.json` — 取得結果(メタデータ+抽出テキスト全文)
- 本報告書 `ER-005-SOURCE-RETRIEVER-01_report.md`
