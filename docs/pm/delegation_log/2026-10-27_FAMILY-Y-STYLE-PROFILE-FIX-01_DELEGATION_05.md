## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05(ユーザー指示「Human Review提出方法の改善・Family Y再配達」: Std `preview` 1 segmentのHRを新形式(原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価、質問は「この音声でよいですか?」1つ)で再提出する。まず既存の承認済み同音・表記ゆれ救済仕様を確認し、規則どおり適用可能なら自律解決(HR不要)、不可ならHRパケット提出。API 0・JPY0(有料再生成は行わない。既存take1/2/3の評価のみ))。並行Agent: KP-PHRASE7-WORD5-PRODUCTION-01 委任_02、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B(いずれもKP系ファイル・er119/er120/er121_family_y_audio_01.py:1504付近/er063/er026/er020を編集中)。これらは編集しない(読むのは可)。あなたの所有=`user_test/family_y_production_redelivery_fee_03/hr_preview_01.html`(新規)+必要なら同dir配下の音声コピー(mp3のみ)、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{HR_PACKET_STD_PREVIEW_01,HR_RESCUE_CHECK_01}.md`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_hr_packet_01.py`(新規)、`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_{USER_02,DELEGATION_05}.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP5.md`。SSOT編集権なし。Production Python編集なし(今回はパケット生成toolと静的ページのみ。HR依頼書renderer(`er011`/各Family)の恒久変更は別委任)。pathspec付きcommit。

## 性質/禁止

- 性質: ユーザー指示の提示方式改善(品質基準変更なし)。到達上限=HRパケット公開(または既存救済規則による自律解決の記録)。
- 禁止: HR必須Gateの緩和・迂回、HRなし宣言の独断使用、承認済み救済規則に無い条件での自動承認、有料再生成、旧Style比較やVoice別Style評価(S9)を必須判断として提示すること、禁止Git操作。
- 時間見込み: 約1.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER_02.md`へ逐語保存。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_05.md` をN=706から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05」のものを採用。

## ユーザー指示(原文・逐語)

【Claude Code指示｜Human Review提出方法の改善・Family Y再配達】

今回のFamily Y「再配達」Standard PreviewのHuman Reviewについて、以下の形式で改めて提出してください。

**1. 今回提出するもの**

Human Review対象の1 segmentのみを、次の情報とセットで提示してください。

- **原稿**：本来読み上げる日本語全文
- **ASR結果**：音声認識が実際に書き起こした全文
- **相違点**：原稿とASRのどの部分が異なるのか、わかりやすく明示
- **NG理由**：なぜ自動検査で止まったのか
- **推奨音声1つ**：その場で再生できるリンクまたはプレイヤー
- **Claude/Fableの評価**：実際の発音・内容に問題があると考えるのか、単なる表記ゆれなのか

ユーザーへの質問は原則として、**「この音声でよいですか？」**の1つだけにしてください。

**2. 複数Takeの扱い**

Take 1・2・3の比較・選択は原則Claude/Fable側で済ませてください。

最も適切と判断した1つを推奨音声として提示すること。

複数Takeを聴き比べる必要がある場合のみ、具体的な品質上の違いと、なぜユーザー判断が必要なのかを説明してください。

単なるASR表記ゆれや技術的な事情を理由に、ユーザーへ不要な比較を求めないでください。

**3. 既存Gateの遵守**

既存の承認済み同音・表記ゆれ救済仕様を確認し、適用可能なら規則どおり自律解決してください。

ただし、Human Reviewが必須となるGateを独断で緩和・迂回しないこと。

Human Reviewが必要な場合は、上記形式で対象箇所のみ提出し、承認を待ってください。

**4. 今回の進行順序**

① Family Y「再配達」のStandard PreviewでHuman Reviewが必要な1箇所だけ提出する。

② ユーザーが音声を確認・承認する。

③ 承認後、Style修正を反映したStandard／Advancedの完成版を組み立て、通常の最終試聴ページを提示する。

今回、旧Styleとの比較やVoice別Styleの評価を追加の必須判断にしないでください。既存の正式承認条件を維持し、必要な判断だけを求めてください。

**5. 今後のHuman Review共通運用**

Family X/Y/Z共通で、Human Reviewをユーザーに依頼する場合は、原則として「原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価」をセットで提出してください。

既存の音声品質Gateは維持します。今回の変更はHuman Reviewの提示・運用方式の改善であり、品質基準の変更ではありません。

新しい仕様として正式Productionに組み込む必要がある部分は、承認範囲を確認してStatusを管理してください。

(原文ここまで)

## 実施事項

1. **救済規則確認(`HR_RESCUE_CHECK_01.md`)**: CURRENT_SPEC Grep `同音|表記ゆれ|かな漢字|ハイフン|JA.*ASR.*救済|er007|secondary ASR|多数決|homophone|normalize` で承認済みのJA ASR救済規則(二次ASR、正規化、同音許容等)を特定し、対象segment(run=`er121_output/family_y_production_01/redelivery_fee/run_style_fix_01` a2 `preview`。take1/2(+take3があれば)の`asr`/`judge`記録、HR queue行)に規則どおり適用可能かを事実で判定。適用可能=規則に基づく自律解決(その根拠・規則名・該当行を記録し、承認記録は規則名で残す)。適用不可=HRパケットへ。**規則に無い判断で通さない**。
2. **take評価**: take1/2(/3)それぞれの原稿・ASR全文(一次/二次)・差分・判定理由・音声長・無音/反復旗を比較し、推奨1つを決める(差が表記ゆれのみなら最初のPASS相当take、音質差があれば根拠付き)。複数take提示が必要と判断する場合のみ、その具体的な品質差とユーザー判断が要る理由を記す。
3. **HRパケット(`hr_preview_01.html`、公開)**: 1 segmentのみ。(a)原稿=読み上げる日本語全文、(b)ASR結果=実際の書き起こし全文(一次・二次両方があれば両方)、(c)相違点=原稿とASRの差分箇所を強調表示(文字単位diff、表形式も可)、(d)NG理由=自動検査が止めた規則名と閾値・実測値、(e)推奨音声1つ=`<audio controls>`で即再生(mp3は`user_test/`配下にコピー、wavは追跡しない)、(f)Claude/Fableの評価=発音・内容の実問題か表記ゆれか(ASR一次・二次の一致/不一致、既存Gateとの関係)、(g)質問は「この音声でよいですか?」の1つ。旧Style比較・Voice別評価は載せない(既存`index.html`は変更せず残置)。`docs/research/.../HR_PACKET_STD_PREVIEW_01.md`に同内容。
4. **承認後の手順を準備(実行はユーザー承認後)**: `tools/hr_adopt_style_fix_01.py --level a2 --segment preview --take N --apply --user-statement-ref <USER承認原文path>`→`provision_shell,gate,assemble,pages,page_verify`→通常の最終試聴ページ(`_03`通し版: Std/Advの通し音声+通常構成。比較節・S9節は含めない)。コマンド列と見積(API 0見込み、TTS再生成なし)を`RESULT_PACKET_YSP5.md`に記載。
5. **共通運用化の棚卸し**(実装はしない): HR依頼書生成箇所(X/Y/Z: `er011`/HR queue/`render_request_md`等)を列挙し、新形式(原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価)をProductionのHR依頼書に恒久実装する場合の変更範囲・承認区分(提示方式の改善=品質基準不変。ユーザー§5で承認済みの運用方式)・見積を`RESULT_PACKET_YSP5.md`に記載(次委任案)。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{HR_REQUEST_STD_02,REGEN_RESULT_02,VERIFY_03}.md`、`tools/hr_adopt_style_fix_01.py`(引数)、`user_test/family_y_production_redelivery_fee_03/index.html`(Std HR節の構造とaudioパス)
- run dir `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/a2/`配下: `audit/`のASR/judge記録、`human_review_queue*.jsonl`該当行、preview take群のメタ(Grep `preview`)
- CURRENT_SPEC.md Grep(上記)±8、`er007_ja_secondary_asr_01.py`(Grep `def |THRESH|normalize|同音` ±5)、`er011_human_review_lock_01.py`(Grep `request_md|render|def ` ±3)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_05.md --json-out ...\_check.json`
- 公開確認: push後 `Invoke-WebRequest https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/hr_preview_01.html` → 200(Pages反映に数分)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_YSP5.md`にOPEN-537/539/550追記文案、PM_GOVERNANCE/CURRENT_SPEC「HR提出形式(共通運用)」追記文案。

## Git

- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05: Std preview HRパケット新形式(原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価)+救済規則適用可否の確認(API 0)`。trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/05`。push。

## 報告

`docs/pm/RESULT_PACKET_YSP5.md`: (0)T-0、(1)救済規則の適用可否(規則名・根拠)、(2)take評価と推奨、(3)HRパケット内容(原稿/ASR/相違点/NG理由/推奨音声URL/評価)、(4)承認後手順、(5)共通運用化の棚卸し、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・公開URL・raw URL。末尾5行要約。