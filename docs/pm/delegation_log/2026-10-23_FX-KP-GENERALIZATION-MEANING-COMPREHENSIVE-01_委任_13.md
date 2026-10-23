FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_13-TWO-ISSUES-ROOT-CAUSE-AND-COMPREHENSIVE-DESIGN-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_13: ユーザー新指示(USER_06「Key Phrase品質改善の継続」)に基づき、2課題(①Std日本語意味の字義訳、②見出し語の人称placeholder一般化)の根本原因確定と包括対策の設計。**本委任はAPI 0(設計・既存データ分析のみ)**。Production変更0、Trialは次委任(Opus条件Aレビュー後)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(line 2、KP行)、`.claude/agents/sonnet-worker.md`、ユーザー原文(§9、T-0で保存)、`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_0{3,4,5}.md`、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/AUDIT_01/{AUDIT_SUMMARY_01,HEADWORD_PLACEHOLDER_01,FABLE_VERIFICATION_01,FABLE_VERIFICATION_02,STD_AUDIT_01,ADV_AUDIT_01}.md`、`{ROOT_CAUSE_02,DESIGN_03,DESIGN_04,OPUS_REVIEW_03,OPUS_REVIEW_04,WIRING_DESIGN_01,WIRING_DESIGN_03,RULE_CONSISTENCY_01,TRIAL_RESULT_02,TRIAL_RESULT_03}.md`、`TRIAL_02/GOLD_LABELS_FINAL_01.md`、`TRIAL_03/FABLE_BLIND_RESULT_03.md`。コード: `er003_key_words_canonicalization.py:400-480`(許可表・判定)、`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`(規則3)、`er105_kp_fulltext_selector_01.py`(SELECTOR_JSON_SCHEMA、A-1 規則5)、`er003_key_words_gloss_alignment.py:119-230,300-330,575-612`(gloss生成・整合)、`er019_family_x_kp_explanation_01.py:54-85,164-178,300-320`(Adv説明)、X runner `er019_family_x_audio_production_runner_01.py:1073-1095`、Z runner `er026_family_z_fiction_production_runner_01.py:1517-1543`、retry/fallback経路。

## 1. ユーザー決定(USER_06、2026-10-23)の要点
- 2課題の原因究明・対策設計・検証を継続。目標=**2課題を実際に解消**(調査報告や案の不採用でCloseしない)。
- A-1はAPPROVED_FOR_PRODUCTION維持。G3等の未承認新仕様はProduction採用しない。本指示は改善Trialまでの継続承認で、未承認仕様のProduction Wiringは不可。
- 個別対策禁止。X/Z共通。既存の正しいKPを壊さない。不要なLLM工程追加を避け、速度・量産単価を最適化。既存Promptの微修正に固執せず原因に応じた最適手段。Opus/Fable独立レビュー活用。
- 新しいTrial範囲・予算拡大・重要な仕様変更は事前にユーザー判断。
- Fable予算枠(本件継続): 本委任API 0。次のTrialは上限60円を予定(KP案件累計≈170円→≈230円、7-7の300円内)。これを超える設計になる場合は設計書に明記しFableがユーザーへ諮る。
- UDR #171(G3採用等の3択)は本指示により**判断済み(採用なし・改善継続)**へ更新。

## 2. 作業
### T-0 記録
- ユーザー原文を `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_06.md` に逐語保存(§9)。委任文逐語保存 `..._委任_13.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。
- ACTIVE_TASK KP行: 委任_13 Status=`TWO_ISSUES_DESIGN_IN_PROGRESS`、報告=`docs/pm/RESULT_PACKET_KPGM13.md`。UDR #171→判断済み(USER_06)。OPEN-474に1行。
### T-1 課題②(見出し語の人称placeholder)根本原因確定 → `ROOT_CAUSE_03.md` §A
- HEADWORD_PLACEHOLDER_01の事実(規則3に one's/someone's 基準なし、your→{one's,someone's,somebody's}全て合法、its→{one's}のみ、本文の指示対象を見る規定なし、日本語意味側だけが区別)を起点に、原因を「規定の欠落(正規化段)」として確定し、影響範囲を既存データで定量化: 既存X/Z記事・Trial KP集合の全KPから所有格を含む見出し語を抽出し、元表現(my/your/his/her/its/their/our)→正規形(one's/someone's/the/その他)の対応と、本文の指示対象(主語自身/他者/非人[組織・研究・物])との一致/不一致を表にする(API 0、決定論抽出+目視)。不一致率を出す。`its→one's`(非人の所有者を人称化)の件数も。
### T-2 課題①(Std字義訳)根本原因確定 → `ROOT_CAUSE_03.md` §B
- 監査確定データ(第2回・第3回・probe-03)から、字義訳NGの全事例(draw a line「線を引く」×2+変種1、an unseen clock×2、過去Trialの他事例があれば)を列挙し、共通条件(比喩表現で字義解釈も文法的に成立/見出し語が名詞句か動詞句/本文の文脈で比喩が明示的か/retryの有無)を分析。Prompt変更(G2/G3/E系)で発生率が1〜3%から有意に下がらなかった事実を踏まえ、原因を「生成時の確率的な字義選択を、現行工程のどこも検出・是正していない(用法の整合検査が無い)」と仮置きし、**既存データで検証**: 字義訳NGの各事例について、同じKPのAdv説明(E0、現行Prompt)の用法(字義/比喩)を照合し、「Std字義 × Adv比喩」の不一致で機械的に検出できた件数/全NG件数を出す(監査データ: draw a line→Adv比喩、unseen clock→Adv "hidden sense of time"=比喩、等)。逆に、正しいStdで誤検出(偽陽性)になる割合も既存データ(通常KP、整合0件の120本・難例E0の60本)で推定。
### T-3 包括対策の設計 → `DESIGN_05.md`
原因に応じた手段を、新規LLM call追加の有無・量産単価・X/Z共通性・既存KPへの影響・B仕様(Adv Prompt/PROMPT_SHA256)変更の有無で比較し、推奨案を1つに絞る(代替案も併記)。候補の例(これに限らない):
- ②: (a)選定/正規化のStructured Outputに `possessive_referent`(self/other/nonperson/none)を追加(既存call内、追加call 0)し、one's/someone's/the への写像を**決定論**で行う+validatorで許可表を指示対象に応じて絞る(your→selfならone's、otherならsomeone's; its→nonpersonなら "the"/無冠詞や名詞句化、人称化しない)。(b)規則3の文言明確化のみ(確率的)。(c)既存の日本語意味整合検査を逆方向(見出し語側)にも使う。A-1(規則5)との整合・同梱方法、既存golden/testへの影響、Trial_01〜03のKPで再計算した場合の変化(API 0で決定論部分のみ)。
- ①: (a)Std/Adv用法整合チェック(Std gloss callとAdv説明callがそれぞれ `usage_type`[literal/figurative/term]を出力→不一致ならStdのみ再生成、1回まで。Adv schemaへの出力項目追加はB仕様変更に当たるか[PROMPT_SHA256への影響]を明記。もし当たるなら、Advを変えずにStd側だけで判定する代替: Std callで `usage_type`+gloss を出し、見出し語の比喩性を決定論/辞書資産で推定して突き合わせる案 等)。(b)Std gloss callに「字義と比喩の両候補を出し、本文文でどちらが成立するかを明示的に判定してから選ぶ」(G2の失敗理由を踏まえた差分を明記)。(c)検出後の再生成の費用と回数上限、retry/fallbackとの関係、Store reuse/signature。
- 個別対策(特定表現のfew-shot/辞書登録)は不可。既存の正しいKPを壊さない保証(非劣化の測り方=第3回の自己一致率基準)。
- 検証計画(次委任、上限60円): 対象KP(過去Trialの115 KP再利用+所有格KPの網羅)、arm、判定(確定gold+Fable盲検、Sonnet Judgeは参考)、Before/After例、改善件数/残存NG/新規悪化の出し方、X/Z両経路のDEV注入E2E(text工程のみ)。費用見積(出典)。
### T-4 Opus条件Aレビュー依頼文 → `OPUS_REVIEW_REQUEST_05.md`(論点: 原因の十分性、決定論写像の網羅性と誤写像リスク、用法整合チェックの偽陽性/偽陰性、B仕様変更の有無、X/Z差、費用、既存KP非劣化、A-1との同梱)。
### T-5 報告・Git
- `docs/pm/RESULT_PACKET_KPGM13.md`: (1)2課題の根本原因(証拠付き) (2)推奨対策とその仕組み(追加LLM call数・単価影響・B仕様変更の有無) (3)既存データでの事前検証(検出率/偽陽性) (4)Trial計画・費用 (5)ユーザー判断が必要な事項(あれば: B仕様変更、予算)。
- secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。raw URL添付。

## 3. 禁止
API呼出一切禁止(LLM/検索)。Production/er112コード変更0(分析scriptは `AUDIT_01/` または `er112_output/kp_gm_design_05/` 配下に新規作成のみ)。個別対策の提案禁止。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行を編集しない。
## 4. handback
完了またはblockerで。

## 9. ユーザー原文(逐語)
# Claude Code／Fableへの指示｜Key Phrase品質改善の継続

## 1. 基本方針

以下の2課題について、**原因究明・対策設計・検証を継続すること。**

1. **日本語意味の字義訳問題**
   - `draw a line` →「線を引く」
   - `an unseen clock` →「目に見えない時計」
   - 本文中の用法に合った、学習価値のある一般的な意味を安定して生成する。

2. **Key Phrase見出し語の一般化問題**
   - `reach for your wallet` → `reach for someone's wallet`
   - `apply its findings` → `apply one's findings`
   - `one's`／`someone's`等への一般化で、元の意味関係を不適切に変えない。

## 2. 実施内容

- 現在調査中の見出し語生成規則とA-1の整合確認を完了する。
- 2課題それぞれの根本原因を特定する。
- 過去Trial・承認済み仕様・既存Production経路を確認し、包括的な対策を設計する。
- Opus/Fableによる独立レビューを活用し、必要なTrialで改善効果と副作用を検証する。
- 特定の表現だけを修正する個別対策は避ける。
- X/Z共通仕様として検討し、既存の正しいKPを壊さないことを確認する。
- 不要なLLM工程の追加を避け、品質を守りながら速度・量産単価を最適化する。

**既存Promptの微修正に固執せず、原因に応じて最適な手段を選ぶこと。**

## 3. 承認・STOP条件

- A-1の`APPROVED_FOR_PRODUCTION`は維持。
- G3など未承認の新仕様はProduction採用しない。
- 既存の承認済み範囲・予算内で自律的に進める。
- 新しいTrial範囲、予算拡大、重要な仕様変更が必要な場合は事前にユーザー判断を求める。
- Trialが失敗しても、品質課題そのものを終了扱いにしない。
- Trial終了時はGateに従って判定し、VALIDATEDでも正式採用はユーザー判断とする。

## 4. 完了報告

以下を明示すること。

1. 各課題の根本原因
2. 対策内容とその仕組み
3. Before／Afterの具体例
4. 改善件数・残存NG・新規悪化件数
5. X/Z共通仕様・Productionへの影響
6. QCDと必要なユーザー判断

**目標は、2課題を実際に解消すること。調査結果の報告や改善案の不採用だけでCloseしないこと。**

なお、今回の指示は改善Trialまでの継続承認であり、未承認仕様のProduction Wiringは許可しない。