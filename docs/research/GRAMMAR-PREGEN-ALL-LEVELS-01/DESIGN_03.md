# DESIGN_03 文法選定仕様変更(Top1/Top2提示・1件選択)とKP先行確定モード(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A)

`DESIGN_02.md`(Opus条件Aレビュー済み骨格)からの**差分のみ**。骨格(事前生成を選定前に行う・finalizeはLLM 0・level必須・書込み順 検証→KPロック→文法ロック→文法review→sidecar→KPレコード)は不変。Opus再レビューの要否はFable判断(下記「再レビュー判断材料」)。

## 変更点
1. **提示数**: 全候補(≤8)→**Top1/Top2のみ**(`PREGEN_MAX=2`)。理由: ユーザー正式決定(提示は最大2件・順位順)。副次効果として事前生成のStep B費用が約1/4(実測最大4件→2件。最大8→2)。Trial-08の順位付け・Prompt・解説品質は不変(`select_tiered`・`STEPA/STEPB_PROMPT`のshaをtestで固定、T12)。
2. **選択数**: 最大2件→**原則1件・0件可・2件同時選択禁止**(`GRAMMAR_MAX=1`)。検査点は4か所で一貫: (a)`select_from_candidates_v2/_pick_ids` (b)`gr.apply_form_selection` (c)`cmd_from_form._validate_form_grammar`(ISSUE) (d)結果検査`_require_fresh_part2_v2`(旧2件結果=Stale)。
3. **全候補opt-in(`--all-candidates`)**: CLIから**撤去**。理由: 「Top1/Top2以外の候補の事前生成」を禁じる仕様と矛盾。残る`p2w.pregen_stage(all_candidates=True)`(wiring所有)は`PREGEN_MAX`参照のためTop1/Top2までしか生成しない(8件は不可能)。引数自体の撤去は委任_03(wiring所有)へ引継ぎ。
4. **reselect**: Trial-08/M-5の既存機構。提示中のTop1/Top2をNGにして次順位が**新しいTop1/Top2**になる(提示は常に最大2件)。新しいTop1/Top2の解説は再度事前生成される(上限`MAX_RESELECT=2`なので最大追加2回×2件)。仕様変更の対象外として**維持**(判断候補として報告)。
5. **KP先行確定(`--grammar-pending`)**: AI島Std/Adv向け。KP/KW 10件のUSER_CONFIRMEDを先に保護し、文法は新仕様で再選定する間「0件確定にしない」。設計判断:
   - 状態の表現: `rec["grammar"].status="pending"`+(study dirがあれば)`status=pending`sidecar。`grammar_state`はpending=None(=保護なし)としたので、既存のG4/凍結/`guard_grammar`コードに「0件確定」と誤認される経路が無い。
   - 後追い確定を新コマンド(`--grammar-from-form`)にして、通常の`confirm --from-form`(KP込み)と責務を分離。KPの保護項目は一切書換えない(revisionのみ+1)。
   - payloadのKP区分は「あれば確定済みと一致必須」: 古い/別のフォームでKPを黙って上書きしない。
6. **旧2件確定の扱い**: 旧仕様で2件確定したsidecar/結果は、読取互換は保つが、結果検査(`_require_fresh_part2_v2`)は2件以上をStaleにする(再選定が必要)。pendingモードで上書きする際、旧の確定sidecar/凍結は`RECONFIRM_SUPERSEDED`へ退避(消さない)。

## 再レビュー判断材料(Opus条件Aの再レビュー要否)
- 変えていないもの: データ構造のキー体系・書込み順・ロック順・level必須・fail-closed・finalize LLM 0・v1/v2読取互換。
- 変えたもの: 数値定数2つ(件数・提示範囲)+それを参照する検査、sidecarへのstatus/presented_ids追加、新コマンド2つ(pending・後追い)。新コマンドは既存関数(`apply_form_selection`・`_write_grammar_sidecar`・`_validate_form_grammar`)の再利用で、新しい処理フローは「KP確定」と「文法確定」の2段分割のみ。
- 結論(Sonnet所見): 骨格不変のため再レビュー不要と判断するが、2段分割は「確定を2回に分ける」新しい構造なので、Fableが条件A該当と見なす場合は`cmd_grammar_from_form`(`er128_kp_confirmed_content_01.py:1566`付近)のみをレビュー対象にするのが最小。
