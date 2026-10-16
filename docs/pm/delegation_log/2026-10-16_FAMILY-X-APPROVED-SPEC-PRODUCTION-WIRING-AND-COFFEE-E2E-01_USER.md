# ユーザー指示原文(2026-10-16受領、Fable転記)
# Claude Code／Fableへの正式指示
## Family X最新仕様Production統合 ＋ Coffee全面再制作

**管理ID：FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01**

**現在Status：APPROVED_FOR_PRODUCTION（一部既存PRODUCTION_WIRED）**

**今回の目標：Family X正式仕様のPRODUCTION_WIRED ＋ Coffee新規E2E完成・試聴可能**

## 1. 目的

これまでにユーザーが正式採用したFamily Xの仕様を、漏れなくProduction正式経路へ反映する。

Coffeeを代表記事として、テーマだけを維持し、Researchから音声・試聴ページまで全面的に新規生成する。

**重要：Coffee専用の例外的な完成を目的としない。今後のFamily X全記事で同じ正式仕様が自動的に適用される状態を完成させる。**

過去の反映漏れ（In One Line・K2・M2など）を再発させない。

## 2. 最新ユーザー判断

以下を最終確定仕様として扱う。

| 対象 | 正式仕様 |
|---|---|
| B3・Writer R0→R1→R2 | すべて `gpt-6.1-sol`。既存Production Wired |
| Full Story TTS（Std／Adv） | **PD06**：聞き手への語りかけ＋落ち着き |
| KP英語音声（Std／Adv） | **K2**：英語フレーズを自然なひとまとまりで発音 |
| KP日本語意味（Std） | **P8**：ニュースキャスター風。旧M2を置換 |
| KP英語解説（Adv） | **P7**：速度・リズムのバランス型。旧P3を置換 |
| Advanced Preview音声 | **E1** |
| Standard日本語Preview／Comment音声 | **R2** |
| KP候補供給 | **M2P0** |
| KP選定優先順位 | **A方式（現行）維持**。B／C不採用 |
| In One Line（Std／Adv） | **基本2文、必要な場合のみ3文** |
| Hook Side Output | **廃止**。R2 Titleを正式表示する仕様は維持 |

**適用範囲：Family X全体。Family Z等への拡大は対象外。**

Promptの正本：

- PD06＝`er057_output/pace_trial_02/prompts/prompts_pace_02.md`のPD6
- P7＝`er080_coffee_kp_pacing_trial_01.py`のp7
- P8＝`er057_std_kp_ja_style_trial_02.py`のP8
- K2／E1／R2＝既存の採用済みTrial正本と照合

同名の別Promptや別Roleを混同しないこと。逐語一致・SHAで追跡する。

Standard Full Storyの既存6%減速は維持し、PD06との併用を実証する。

## 3. 最初に必ず実施：Production仕様反映マトリクスの確定

**Research開始前に実施すること。**

参照資料：

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- USER_DECISION_REGISTER
- FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01
- 2026-10-16ユーザー最終判断記録
- 過去のProduction Wiring証跡

Family XのResearchからAssemblyまで、承認済み仕様を全件抽出する。

マトリクスには最低限以下を記録する。

1. 仕様名・管理ID・ユーザー承認証拠
2. 最新の正式仕様とStatus
3. Production初回経路
4. retry／fallback／regeneration／resume経路
5. 正式Prompt・モデル・routing・SHA
6. Validator／QA／Gate
7. 過去のTrial専用実装との差分
8. runtime evidenceの有無
9. 未配線・競合・Dangling Reference
10. Coffee E2Eで確認する受入条件

**承認済み仕様の反映漏れを、制作開始前にすべて検出する。**

新たなUSER_DECISION_REQUIREDが発覚した場合、ユーザーが明示的にdeferした項目以外はSTOPする。

## 4. Production Wiring

承認済み仕様について、Family X正式初回経路へ実装する。

対象：

- PD06／K2／P8／P7／E1／R2のTTS Style
- In One Line基本2文・必要時3文
- 既定Style profileへの登録
- retry／fallback／regeneration／resumeへの整合
- 必要Validator／QA／Regression test

### In One Line

旧Promptの `Exactly one sentence` を置換する。

仕様は**「基本2文、必要な場合のみ3文」**で確定済み。1文を許容する旧経路を残さない。

初回生成だけでなく、Standard継承、Local Rewrite、retry、regenerationにも適用する。

文数だけでなく、要点・意味・示唆を自然に伝える内容品質を維持する。

具体的Prompt文面と3文にする基準は設計して報告する。これは既存承認仕様の実装であり、文数方針を再度Trialに戻さない。

ただし、新しい編集方針を追加する必要が生じた場合は、ユーザー判断を要する。

### TTS Style

6仕様をFamily Xの既定profileとして適用する。

CLIによる特別指定を忘れた場合でも、承認済みStyleが自動適用されるようにする。

Master Audio Storeでは、Style変更後の音声を旧Style音声として誤再利用しない。Role・Style ID・version・Prompt SHAを整合させる。

特にP8は旧Full Story候補にも同名が存在するため、Roleを明確に分離する。

## 5. Coffee全面再制作

**テーマだけ同じ。Researchからすべて新規生成する。**

旧CoffeeのResearch結果・Fact Ledger・B3・Writer原稿・Key Phrase・音声を、新記事の正本として流用しない。

正式Production経路で以下を実施する。

1. Research新規実行
2. Verified Fact Ledger新規生成
3. B3（Sol）
4. W-1 Writer R0→R1→R2（すべてSol）
5. Advanced英語化
6. Standard難易度調整
7. M2P0＋A方式でKey Phrase新規抽出・選定
8. KP日本語意味・Advanced英語解説の新規生成
9. In One Line新規生成
10. 正式StyleでTTS新規生成
11. Standard／Advanced Assembly
12. 試聴ページ生成・実再生確認

既存のResearchから記事作成までの正式手順、Fact Lock、Risk Flagger、Review Queue、QAを省略しない。

既存ProductionのMandatory STOP／Human Review Gateがある場合は、勝手に迂回しない。

**Researchから音声までを無条件に一気通貫で実行しない。工程ごとに仕様反映マトリクスと照合し、必要なSTOPを守ること。**

## 6. Writerの重要確認

既存のB3→R2 Sol統一は、実装済みという報告だけでなく、今回の実runでも証拠を取得する。

- B3／R0／R1／R2のactual model_id
- W-1正式経路使用の証拠
- R1→R2入力契約
- Fact Lock、B3注記、AN3等の承認済みPrompt要素
- 実送信PromptのSHA
- retry／regeneration時のroutingとPrompt整合
- Trial用Writerや旧Luna／Astra経路への意図しない退行がないこと

必要なFact QA・品質Gateも省略しない。

## 7. VALIDATED未決事項の扱い

過去の未決Trialは以下に分類してSSOTへ記録する。

- **A：VALIDATEDだが正式採否未決**
- **B：後続の承認済み仕様に吸収・代替済み**
- **C：不成立・不採用・未検証**

今回、ユーザーは**個別の採否判断を行わない**と明示した。

したがって、Aはdeferredとして管理し、今回のProduction作業を妨げない。ただし、勝手に採用・不採用へ変更しない。

Bは後続仕様との関係と根拠を記録する。CはVALIDATEDと誤記しない。

この整理のための追加Trial・個別質問は禁止。

Hook Side Outputはユーザー正式判断により廃止し、OPEN-176等を更新する。

## 8. QCD・作業効率

**Quality最優先。不要な再生成・重複Trial・過剰なAPI呼出は行わない。**

- 既存の採用済みTrial成果を再利用し、採用判断をやり直さない。
- 監査・設計・テストなど無課金作業を先行する。
- 独立しているread-only作業・テストは安全な範囲で並列化する。
- 実装方法は既存Production構造を最大限再利用し、新規機構の乱立を避ける。
- 追加Trialや品質改善案を見つけた場合、独断で採用せずSTOP・報告する。
- 有料E2E開始前に費用見積を提示し、承認済み予算・既存Gateを守る。
- 無意味な再試行は行わず、同一原因の再発時は根本原因を調査する。

## 9. 受入条件

以下をすべて満たした場合に限り、`PRODUCTION_WIRED`と判断する。

1. Family X正式初回経路で全承認仕様を使用。
2. retry／fallback／regeneration／resumeも整合。
3. DEV／Trial専用scriptにしか存在しない仕様がない。
4. 正式経路のruntime evidenceあり。
5. actual model_id・routing・Prompt SHA確認済み。
6. 必要なValidator／Regression／integration test PASS。
7. CoffeeのResearchからAssemblyまで正式経路で実走。
8. Standard／Advancedとも完成・試聴可能。
9. 承認済み仕様と完成記事・音声を全件照合。
10. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・判断台帳更新。
11. 必要なcommit／push／merge確認済み。
12. 未報告Trial・未登録Open Item・未処理のBlocking事項なし。

1件でも未達なら、完了扱いにしない。

## 10. STOP条件

以下の場合は直ちにSTOPし、事実と判断事項を報告する。

- 過去の正式承認と矛盾する新仕様が必要。
- 承認済みPrompt正本を特定できない。
- Production配線に重大な設計変更が必要で、Opus条件Aの確認が必要。
- 新しいTrialが必要となる。
- Mandatory Human Review／Budget Gate／品質Gateに到達。
- 同じ原因の失敗が再発し、既存retryで解決できない。
- 承認済み仕様の実装範囲が不明。
- 新たなユーザー判断なしでは進められない。

STOP時に勝手に次段階へ進まない。

## 11. 最終報告

非エンジニアPM向けに、以下を簡潔に報告する。

1. Family X正式仕様のProduction反映状況。
2. 今回修正・配線した仕様と適用範囲。
3. Coffee新規記事・音声・試聴ページ。
4. B3→R2の実際のSol使用証拠。
5. 初回・retry・fallback・regenerationのテスト結果。
6. 品質QAと実際の未解決問題。
7. 費用実績。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新状況。
9. Git commit／push／merge証拠。
10. PRODUCTION_WIRED判定と残存Open Item。

FableはClaude Codeの完了報告を鵜呑みにせず、ユーザー承認・CURRENT_SPEC・実装・runtime evidence・QCD・PM Gateと照合して独立受入判定すること。
