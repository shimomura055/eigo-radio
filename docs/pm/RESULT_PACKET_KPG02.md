# RESULT_PACKET_KPG02(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_02、2026-10-30、OPEN-619 / UDR #227更新・提示はFable)

- 結論: Closeout案=USER_DECISION_REQUIRED(未完)。方式D'(改善ループ1回)は費用上限¥20到達で8/16ケースのみ実行。同一8ケースで『そのまま選べる率』 Before 12/45(27%) → A 30/39(77%) → D 31/39(79%) → **D' 27/42(64%)**(Std D 88%→D' 68%、Adv 73%→60%)。3件以上選べるケースは D 6/8 → D' 7/8。**率はD未満(8ケース・約40件、run間ばらつき大のため確定的ではない)**。主因は塊判定(luna)が易しい表現(rely on等)と自由な組合せ(deep image等)を2回とも『塊』と判定すること。和集合の追加候補の精度(5/8)は通常(22/34)と同等で和集合は悪化原因でない。
- 必須9例(Before/A/D/D'): G1 ×/△/×/△(a2○・b1b× 1/2) | G2 ×/×/△(単体のみ)/○ | G3 ×/×/○/○ | G4 ×/○/○/○ | G5 ×/○/○/○ | V1 ×/○/○/○ | V2 ○/○/○/○ | V3 ○/×/○/○ | V4 ○/○/○/○
- 選べる率(同一8ケース): Before 27% / A 77% / D 79% / D' 64%。独立判定(gemini-3.8-flash非thinking・出力上限1500、D' 47候補)とSonnet実読の一致42/47(89%)。Before成功例の脱落 1/12(`an open question`)。
- 改善(1)〜(4): (1)意味修飾語DROP禁止ガード(決定論)+meaning_preserved=false時のspan形復帰(発動0件) (2)塊判定2回和集合(難易度はC判定のeasyのみ不可。初版『どちらかeasy』でblow a whistle脱落→同一ループ内で是正) (3)someone/something判定・受動形/節断片除外 (4)G1/G2はalt併記(和集合でmain入りしたためa2では両方mainで提示)。付随: 複数形lemma補正(Sales pitch脱落の不具合)、WordNet thread lock(並列実行の例外)。
- 残NG(D' main 15/42): 易しい5(rely on×3等)・自由な組合せ5・一般化の個別事情4(hear something out・take points away・set a lower limit・or so it seemed)等。geminiは自由な組合せ系を概ね不可と判定。
- ばらつき: 同一入力再実行(2回)は費用上限で**未実施**(D vs D'・ルール調整前後で提示集合が3〜5件入れ替わる観測のみ)。
- 費用・時間: 本ループ¥19.92(上限¥15→¥20未満、77 call: luna ¥10.08・gemini ¥9.85。並列実行時のWordNet例外による再実行ロス約¥3を含む)。D' 1レベル¥1.80・約123秒、1記事セット約¥3.6=70円の約5.1%(D比+¥1.6)。既存段置換による相殺は未確認。未実行: 6ケース+moon_a2・melos_b1b・再実行ばらつき・D_sol。
- 使用モデル: gpt-6-luna(Production routing相当=比較基準・例外2)、gemini-3.8-flash(最新Flash・別系列検証/独立判定、非thinking+max_output明示。thinking既定モデル不使用)。
- 次の一手: D''=D'+別系列最終ゲート。D'の8ケースにgemini判定を適用した概算は26/30(87%)・3件以上7/8、失うのはG1のみ(ただし判定者=評価者で循環。独立評価要)。+約¥0.2/レベル。残8ケースの全工程で約¥15〜17(Cap追加要=判断候補B/Fable)。
- URL: https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/ (D'列・3b G1/G2併記)。成果=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/{RESULT_02.md,kpg02_*.py,kpg02_work/}。
- 採用時のユーザー判断事項(UDR #227、分類D): display_form新許容ルール / 7件未満容認(D'平均5.25件) / G1方針(F=現行/G=一般化すれば塊) / +約¥1.6〜3.6/記事セット / 追加Trial Cap。
- commit: 最終報告に記載。
- (1)既存仕様整合: CURRENT_SPEC.md:2041-2048、er119_kp_candidates_01.py:198-300、CURRENT_STATE_01.md(委任_01で照合済み)。矛盾は検出せず。本ループは設計変更のみで仕様照合の再実施なし。
- (2)未承認機能の既定値: Production到達経路への混入0(kpg02_*はdocs/research配下のTrial専用、Production code/Prompt/Validator/閾値/flag変更0)。確認=git diff --cachedが自分の追加ファイルのみ・Production moduleにkpg02参照0(Grep)。
- (3)失敗終了時の最終成果物: 費用上限到達で部分完了。最終成果物=比較ページ(8ケースD'列+3b併記)・RESULT_02.md(未実行範囲を明記)。目的(修正せず選べる率の向上)への適合=『D'は未達(64%<D 79%)、必須9例の取りこぼし(G1/G2/V3)は改善』。
- (4)撤去・残置: Production規則の撤去なし。Trial側のeasy veto初版(『どちらかのpassがeasy』)はC判定easyのみへ変更し旧条件は残置せず。kpg01系(B/C/D等)は比較記録として残置。Grep: Production moduleにkpg0[12]参照0。
- 判定整合: 重大NG=なし / 主因=塊判定(luna)の難易度・F/C境界の甘さとrun間ばらつき / 是正対象=別系列最終ゲート(D'')・易しい基本動詞+前置詞の除外 / STOP理由=なし(費用¥20到達で未実行範囲を報告) / 提示=証拠のみ(Fable受入・独立評価後。判断候補は追加Trial Capと採用時5項目)
