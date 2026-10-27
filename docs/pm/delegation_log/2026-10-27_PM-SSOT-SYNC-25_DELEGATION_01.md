## 管理ID

PM-SSOT-SYNC-25(SSOT同期: 全面修正版4項目の6経路Fable受入判定の記録、KCP委任_04(b101b2ba4)、SLOT-23委任_03(71e39f4df)・04A(22f3a09ef)反映。API 0)。あなたが唯一のSSOT編集権者。並行Agent: SLOT-23 B/C/D/E班(コード)、SSOT権なし。全文読込禁止(Grep)。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約1h。

## Fable判定(本SYNCで記録する内容。判定し直さない)

ユーザー正式決定「学習項目選定フォームv3・文法解説事前生成・確定内容保護|全Family Production Wiring【全面修正版】」(原文=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`)の4項目について、2026-10-27 Fable受入:
- **① フォームv3(日本語訳・AI理由・候補ID/区分/候補集合sha・確定済みロック・理由欠落の非正常扱い)= PRODUCTION_WIRED(X/Y/Z×Std/Adv)**。根拠: FORM委任_02〜_05(公開+8記事evidence)、X=AI島Std/Advの実ユーザー確定(`confirm --from-form`、AIF委任_02/_03)、Y Std/Adv・Z Adv=KCP委任_03、Z Std=KCP委任_04(actor=evidence)。**ただし送信・コピー改善(USER_03 §B)はIMPLEMENTED+公開(ユーザー実操作確認待ち)で、本WIRED判定の範囲外**と明記。
- **② 文法解説の事前生成(Top1/Top2提示・1件/0件・2件拒否・凍結・model耐性)= PRODUCTION_WIRED(6経路)**。根拠: GPG委任_05/05C(`EVIDENCE_RESULT_05/05C.md`、X 1件+0件(AI島)、Y Std Top1/Adv Top2、Z Adv 1件/Std 0件、finalize LLM 0、費用¥3.61)。限界: Z Stdの非0件はruntime未観測(Zの候補は設計上最大1)。
- **③ 全候補AI選定理由= PRODUCTION_WIRED**(KP75、OPEN-534で受入済み、再掲)。
- **④ 確定内容保護(KCP、G0〜G4)= PRODUCTION_WIRED(6経路)**。根拠: KCP委任_03(X Std/Adv・Y Std/Adv・Z Adv)+委任_04(Z Std: 実runner通し、G0〜G3、確定レコード不変、ガード全拒否、費用約¥3.0)。限界: Z Stdはコピーrun上(旧run後付け確定)、`standard.html`のみ改変のG3はPASS(D3既知、OPEN管理)。
- OPEN-559/OPEN-556/OPEN-545(①部分)のStatusをPRODUCTION_WIREDへ(①の送信改善は別記)。OPEN-562(SLOT-23)は実装中のまま。
- 旧仕様撤去確認: 「Part 2はAdvancedのみ」「最大2件」記述は履歴化済み(SYNC-20/21)、コードは05A/05Bで撤去済み(`REMOVAL_RESULT_02.md`)。

## 実施事項

1. `OPEN_ITEMS.md`: OPEN-559・556・545(①部分)をPRODUCTION_WIRED(Fable受入2026-10-27、PM-SSOT-SYNC-25、根拠・限界付き)。OPEN-545は「送信・コピー改善=IMPLEMENTED+公開・ユーザー実操作確認待ち」を併記。OPEN-562にS23A(ハイライト共通module新設、オフライン実証8/9+In one line運用、配線中)・D3(DESIGN_03正本、Opus条件A完了)を追記。KCP4の観察(実害なし3件)はOPEN-556の限界欄へ。
2. `CURRENT_SPEC.md`: 文法新仕様節・確定内容保護節・フォームv3節のStatus行をPRODUCTION_WIREDへ(Grep `GRAMMAR-PREGEN-ALL-LEVELS-01|KP-CONFIRMED-CONTENT-PROTECTION-01|学習項目選定フォームv3`)。学習項目①②③表示仕様節に「設計正本DESIGN_03、共通module `er_learning_highlight_01.py`/`er128_kp_highlight_01.py`新設(配線前・既定バイト同一)、表示範囲=ページ表示本文単位すべて(In one line含む)、タイトル由来出現は本文内へ再配置(NOTICE)」を追記。
3. `DECISION_LOG.md`: 新規エントリ「全面修正版4項目 6経路PRODUCTION_WIRED(Fable受入)」+「SLOT-23 Fable決定: M3再配置規則・M7(Std Part 1=①+②)・表示範囲にIn one line含む・CONTRACT_03をA班実装に統一」(原文ref)。
4. `docs/pm/PM_GOVERNANCE.md` 違反・逸脱記録: KCP委任_04で`full_story_part2_c1`のFull Story音声1clipが再生成(Std chunk planner差、KCP無関係、¥1.67。委任文「Full Story TTS staleなら起動しない」に対し、agentはstale原因がKCPでないと判断し続行=事後承認、記録のみ)。
5. `docs/pm/ACTIVE_TASK.md`固定ヘッダ更新(管理ID=PM-SSOT-SYNC-25、Status、進行中=SLOT-23 B/C/D/E、次=M(マーク発行)/F(evidence)/AI島HR後の再ビルド/最終報告、UDR-blocking=AI島HR・解説言語・フォーム実操作確認・UDR-MONKEY-1、QDC=当日約¥83)。
6. commit: `PM-SSOT-SYNC-25: 全面修正版4項目(フォームv3/文法事前生成/AI理由/確定内容保護)6経路PRODUCTION_WIRED Fable受入・KCP04 Z Std evidence・SLOT-23 A班/設計03反映・違反記録(API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Grep一覧

`OPEN-545|OPEN-556|OPEN-559|OPEN-562`(OPEN_ITEMS.md)、`PM-SSOT-SYNC-24`(DECISION_LOG.md先頭/PM_GOVERNANCE.md)、上記CURRENT_SPEC Grep語。参照=`docs/pm/RESULT_PACKET_{KCP4,S23A,S23D3,GPG5,GPG5C}.md`のSSOT文案。

## 報告

`docs/pm/RESULT_PACKET_SSOT25.md`(gitignore): (0)T-0、(1)変更箇所(file:line)、(2)Status表、(3)判断候補、(4)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。