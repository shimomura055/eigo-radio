管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08(②B-light 案βのOpus条件Aレビュー反映: 比較基準の是正・複数atom負例・設計改訂・R-5計測計画。**API 0・Production変更0**。有料Trial T1は実施しない)。委任_07A(③F1+F2適用、`er078_*`/`er007_*`)が並行中=それらは読むだけ。本委任所有: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/B_LIGHT_*`・`OPUS_REVIEW_01_BLIGHT.md`・`b_light_proto_02.py`(+test)・`eval_b_light_api0_02.py`、OPEN-515(最小追記)、delegation_log。

## Opusレビュー(逐語を`OPUS_REVIEW_01_BLIGHT.md`へ保存。要点)
- 総合: βの考え方(Azureは値の証人、読みはPrimary、値矛盾はNG)は妥当。Azureはフレーズリスト不使用(`er007_ja_secondary_asr_01.py:74,312`)で台本と独立。ただしM-1/M-2が直るまで採用提案もVALIDATED(限定)確定も見送り。T1は非推奨(型の発生率約0.2%、無作為40clipでは0件の可能性が高い)。
- **M-1 比較基準の誤り**: 評価の「+F」列がv2のPrimary層とA4(a)を含む(`eval_b_light_api0_01.py:56-60,77`)。v2はProduction未採用。実際の07A後Productionは「base+F1F2」。影響: (a)「α効果0」「F後3→β5」はProductionにない基準への数字 (b)βが読み判定にv2部品(`P2.pron_hira`/`P2.c2_blocked`)をimport=βの採用はSecondary値の裏付け範囲でv2読み規則も採用することと同じ(base+F1F2上ではa2保存転写・a3再転写#1の同音異字型もcompositeで通る) (c)救済数・露出集合が変わる (d)承認範囲を要約で狭める懸念。対応: API 0で「base+F1F2」「base+F1F2+β」の2列を追加し全基準(1a〜1d・2・4、N-1最悪ケース含む)を再評価、採用承認対象にv2読み規則が含まれることを明記。
- **M-2 再利用時の隔離**: `er078_reuse_value_guard_01.py:104-114`は保護差でないNGでは再利用を止めないため、composite受理音声がflag OFF時やA/B/C(Master Audio Store共有)へ漏れる。対応: `composite_contributed`印でscope外/flag OFFは先にブロック(er109/RET/UKUS前例:62-80)、scope内は保存S転写で`composite_judge`再実行、S転写・engine・wav shaの保存を配線前提(保存なければfail-closed)。
- **M-3 複数atom**: 44test・合成負例55件に2個以上のatomを含む文がない(1個目EXPLAINED+2個目矛盾、順序入替、同助数詞反復、Secondaryの値過不足・順序違い)。`value_guard`が位置照合か集合照合かは未確認。基準を緩めず追加して再凍結。
- R-1 SecondaryとPrimaryの残り部分の読みが食い違う場合(a3「杉野氏」)は警告+試聴必須(またはveto)。R-2 `W_GARBLE_EXPLAINED`は試聴必須(TTSの不自然な間の可能性)。R-3 F-A(数字を2〜3断片に分ける形)は観測形に限定: 前断片は「1桁+0の並び(d×10^k)」、3断片は実例まで無効(現`_place_ok`は`12000|300`等も許す)。R-4 Secondary側は値ガードの既知不具合(OPEN-523/524)を引き継ぐ→composite条件としてSecondary値atomを数字・漢数字表記に限るか、先に不具合を直す。R-5 F1が新たに生む誤NGをProductionで計測(API 0): JAの`final_gate_value_diff`/`p1_value_diff`件数と、Azure呼出時のS転写保存。R-6 L2865と実装(R4)の不一致はβ承認に混ぜず別件。R-7 監査記録に`reading_source=primary`/`value_source=secondary`。R-8 フック①の事前判定結果が最終判定に流用されないことを配線testで固定。C-1〜C-7(独立性、最終ANDゲート常時、矛盾型NG維持、ε/F1側救済/F2拡張の却下妥当、UDR #136非接触・新受理クラスはL2179/L2856変更=ユーザー採用承認、HR/attempt/fallback不変、決定性)。事前登録不足: 比較基準列・複数atom・SecondaryのかなN数詞/全角数字/空白run(`8000 900本`)/`万`を含むF-B負例。ユーザー確認: βのProduction採用(v2読み規則を含むことを明示)。γは時期尚早、J3「超/超え」試聴は別件で適切。進め方: (i)M-1再評価→(ii)R-5頻度データ→(iii)効果が狭ければVALIDATED(限定)で止め低優先の採用候補。

## Fable判断
M-1〜M-3・R-1〜R-8すべて採用。T1は実施しない。βのStatusはM-1再評価後に確定(機械写像+Fable)。R-5(Production側の計測・S転写保存)は**07A commit後に別委任で実装**(本委任では計測仕様を書くのみ)。

## 作業
A. `OPUS_REVIEW_01_BLIGHT.md`保存。`B_LIGHT_DESIGN_02.md`(M-2隔離設計、R-1/R-2警告+試聴必須、R-3 F-A限定、R-4 Secondary値atomの表記限定、R-7監査項目、R-8、採用承認対象にv2読み規則が含まれる旨の明記、R-6別件)。
B. `b_light_proto_02.py`(v2読み規則への依存を明示化[import維持可だが採用範囲として記録]、R-3・R-4・R-7反映)+test(M-3複数atom・F-B負例[かなN数詞/全角/空白run/万]追加、基準は緩めない)。再凍結(sha記録)。
C. `eval_b_light_api0_02.py`: 列=「base」「base+F1F2(=07A後Production。proto v4で再現、07A commitが着いていればProduction関数で再現し一致確認)」「base+F1F2+β」「(参考)base+v2+F1F2+β」。全基準(1a〜1d・2・4、N-1最悪ケース、月題12転写、Melos、実履歴P-S対43件、N-3 30clip)を再評価。2回実行で決定的。`B_LIGHT_EVAL_02.md`(M-1是正後の効果・露出・救済数、Status候補の機械写像)。
D. `B_LIGHT_PREREGISTERED_02.md`(比較基準列の是正、M-3/F-B負例追加、R-5の計測指標[JA `final_gate_value_diff`/`p1_value_diff`件数、S転写保存率、a1/a2型頻度]、T1は非実施の記録)。
E. `R5_MEASUREMENT_SPEC_01.md`(Production側の計測・S転写保存の仕様: 保存項目[S転写・engine・model_id・wav sha]、保存場所、fail-closedの条件、API 0で集計するscript仕様。実装は07A後の別委任)。
F. OPEN-515最小追記(直前再Read・最小Edit・バックアップ)。CURRENT_SPEC変更なし。
G. Git: 対象pathのみ→`git commit --only`または一時index→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
H. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_08.md`(Nは608前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08」を600〜660で走査)。Opus依頼文(先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01(②B-light)。Opus必須レビュー」)も`..._OPUS_REQUEST_DELEGATION_03.md`へ。

## 禁止
Production code変更、有料API、v1/v2/v4/β v1 protoの変更(新版を作る)、UDR #136の変更、γの実装。

## 報告(RESULT_PACKET_JAASR8.md+口頭要約)
M-1是正後の再評価表(列別の救済数・露出・回帰)、v2読み規則依存の明示、M-3/F-B負例の結果、Status候補、R-5計測仕様の要点、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。