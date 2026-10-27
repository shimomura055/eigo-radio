## 管理ID

PM-SSOT-SYNC-26(SSOT同期。対象=ユーザー指示USER_04(`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md`、①②③正式仕様の明確化=①②は詳細な日本語解説で同等・①のみ音声・③は短い訳のみ・「英語で解説」撤回)、SLOT-23委任_04B(374cfc941)/04C(e2feca7ab)/04D(331474a9f)/04E(f03f12c2e)/05M(1684e19f5, ccf118a31)、AIF委任_05(165631654, 4a9776ef4)、FORM委任_09(71a96ca44)。API 0)。あなたが唯一のSSOT編集権者。並行Agent: SLOT-23 F班・AIF委任_06(SSOT権なし)。全文読込禁止(Grep)。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約1h。

## 性質/禁止

- 記録同期。SLOT-23(OPEN-562)は「配線完了・evidence中」。**本SYNCでWIREDと書かない**。禁止Git操作なし。

## 実施事項

1. **DECISION_LOG**(新規、原文ref): (a)USER_04 §2=①②③正式仕様(表)、「Standardの②を英語で解説」撤回、旧「Advancedのみ」を根拠にStd②を無効化しない。Fable: 作業仮定A(日本語解説)が正式確定、Std Part 1=①+②(M7)と一致。(b)Fable決定: HR(AI島)は正式仕様(CURRENT_SPEC:2856 M3 LR Gate=人間承認必須)により必要、Gate緩和せず、hr_02で質問1つ提示。(c)CONTRACT_03をA班実装に統一、表示範囲にIn one line含む、M3再配置規則(SYNC-25記録済みなら参照のみ)。
2. **CURRENT_SPEC**(`IMPL_M_01.md` §4 S29/S30/:2095の文案に従う): (a)`:1717,2083,2086,2101,2106,3111`付近「Part 1=Advancedのみ」→2026-10-27正式決定でStandardにも新規記事から表示(Std=①+②、日本語解説、難易度調整のみ、Adv不変)、有効化=確定レコード`display_spec=LEARNING_ITEMS_123_V1`、マーク発行=`new_review`(新規のみ・遡及なし)、旧記事=旧表示。(b)`:2095` 学習テキストページの正式入口=標準公開builder `er019_family_x_listening_page_01.py`、`er019_nws2_final_page_01.py`=旧表示仕様の既存記事用。(c)学習項目①②③表示仕様節: 正式仕様表(USER_04 §2)、実装Status=配線完了(A〜E+M、commit列挙)・evidence(F班)中、Validator(Part 1ちょうど1個)、G3拡張、Y/Z/X配線点、`reconsume`(既存記事の明示移行、Redundancy QAあり)、kill switchの意味、解説言語=日本語確定。(d)Family X M3 Style Gate節(Grep `LOCAL_REWRITE_RECOVERY|record_human_approval`): AI島事例を「適用例」として1行追記(本文不変・音声のみLR・HR必須)。
3. **OPEN_ITEMS**: OPEN-562(配線完了=A〜E+M、回帰=本変更起因0、evidence F班中、AI島=AIF6準備中、Fable判定待ち)、OPEN-561(AIF5真因確定・hr_02公開・Q1承認待ち・AIF6準備中)、OPEN-563(AIF5所見: `AIs sent`のみ、z+s融合仮説、対策案3、Azure検証≈¥1)、OPEN-564(模擬でBLOCK不変=実害なし)、OPEN-512(Std拡張注記)、OPEN-543(M班回帰のHEAD既存失敗24件・並列競合9件を統合、legacy decorator `er119_test_support_01.py`の存在)、OPEN-545(猿の手テスト送信=照合全欄一致、確定不可の理由=候補集合sha未生成の試作データ、正式化は別案件)。
4. **PM_GOVERNANCE 違反・逸脱記録**: (a)SLOT-23 B班agentが`git stash`(禁止操作)を誤実行→直後に`stash pop`で全復元・stash 0件・欠損なし(記録。再発防止=委任文の禁止Git操作に`stash`を明記済み、tool誤操作)。(b)B班所有外編集なし/C班`er053`既存test修正(HEAD既存失敗の是正、記録のみ)。(c)M班: 旧マーク無し記事前提の既存test約50件をlegacy decoratorで再現(production挙動不変、期待値不変。記録)。
5. **ACTIVE_TASK.md**固定ヘッダ(管理ID=PM-SSOT-SYNC-26、進行中=S23F/AIF6、次=AI島HR承認後の完成・Fable受入・最終報告(USER_04 §7順/SLOT-23 §8順)、UDR-blocking=AI島HR Q1・フォーム実機確認・UDR-MONKEY-1、QDC=当日約¥86)。
6. commit: `PM-SSOT-SYNC-26: ①②③正式仕様(USER_04)確定・SLOT-23配線完了(A〜E+M)・AI島HR真因/hr_02・猿の手テスト照合・OPEN更新・違反記録(API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Grep一覧

`OPEN-512|OPEN-543|OPEN-545|OPEN-561|OPEN-562|OPEN-563|OPEN-564`(OPEN_ITEMS.md)、`Advancedのみ|学習項目①②③|er019_nws2_final_page_01|LOCAL_REWRITE_RECOVERY|PM-SSOT-SYNC-25`(CURRENT_SPEC.md/DECISION_LOG.md/PM_GOVERNANCE.md)。参照=`docs/pm/RESULT_PACKET_{S23B,S23C,S23D,S23E,S23M,AIF5,FORM9}.md`、`IMPL_M_01.md` §4。

## 報告

`docs/pm/RESULT_PACKET_SSOT26.md`(gitignore): (0)T-0、(1)変更箇所(file:line)、(2)Status表、(3)判断候補、(4)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。