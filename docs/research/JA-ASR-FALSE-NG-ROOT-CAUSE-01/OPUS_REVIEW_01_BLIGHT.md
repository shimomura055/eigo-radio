# OPUS_REVIEW_01_BLIGHT(②B-light 案β Opus独立技術レビュー[11-3 条件A]の保存。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08、2026-10-25)
依頼文=`OPUS_REVIEW_REQUEST_01_BLIGHT.md`(送付原文=`docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_OPUS_REQUEST_DELEGATION_03.md`)。
**保存の注記**: 本ファイルの「Opus所見」節は、Fableが委任_08の委任文に記載したOpus所見の要点を**逐語で転記**したもの(Sonnet側はOpus出力の全文を受領しておらず、委任文に記載された要点のみ入手)。Opus出力の全文が別途存在する場合は同名ファイルへ差し替える。Sonnetによる要約・追記・解釈はしていない(解釈は`B_LIGHT_DESIGN_02.md`)。

## Opus所見(委任文の逐語)
- 総合: βの考え方(Azureは値の証人、読みはPrimary、値矛盾はNG)は妥当。Azureはフレーズリスト不使用(`er007_ja_secondary_asr_01.py:74,312`)で台本と独立。ただしM-1/M-2が直るまで採用提案もVALIDATED(限定)確定も見送り。T1は非推奨(型の発生率約0.2%、無作為40clipでは0件の可能性が高い)。
- **M-1 比較基準の誤り**: 評価の「+F」列がv2のPrimary層とA4(a)を含む(`eval_b_light_api0_01.py:56-60,77`)。v2はProduction未採用。実際の07A後Productionは「base+F1F2」。影響: (a)「α効果0」「F後3→β5」はProductionにない基準への数字 (b)βが読み判定にv2部品(`P2.pron_hira`/`P2.c2_blocked`)をimport=βの採用はSecondary値の裏付け範囲でv2読み規則も採用することと同じ(base+F1F2上ではa2保存転写・a3再転写#1の同音異字型もcompositeで通る) (c)救済数・露出集合が変わる (d)承認範囲を要約で狭める懸念。対応: API 0で「base+F1F2」「base+F1F2+β」の2列を追加し全基準(1a〜1d・2・4、N-1最悪ケース含む)を再評価、採用承認対象にv2読み規則が含まれることを明記。
- **M-2 再利用時の隔離**: `er078_reuse_value_guard_01.py:104-114`は保護差でないNGでは再利用を止めないため、composite受理音声がflag OFF時やA/B/C(Master Audio Store共有)へ漏れる。対応: `composite_contributed`印でscope外/flag OFFは先にブロック(er109/RET/UKUS前例:62-80)、scope内は保存S転写で`composite_judge`再実行、S転写・engine・wav shaの保存を配線前提(保存なければfail-closed)。
- **M-3 複数atom**: 44test・合成負例55件に2個以上のatomを含む文がない(1個目EXPLAINED+2個目矛盾、順序入替、同助数詞反復、Secondaryの値過不足・順序違い)。`value_guard`が位置照合か集合照合かは未確認。基準を緩めず追加して再凍結。
- R-1 SecondaryとPrimaryの残り部分の読みが食い違う場合(a3「杉野氏」)は警告+試聴必須(またはveto)。R-2 `W_GARBLE_EXPLAINED`は試聴必須(TTSの不自然な間の可能性)。R-3 F-A(数字を2〜3断片に分ける形)は観測形に限定: 前断片は「1桁+0の並び(d×10^k)」、3断片は実例まで無効(現`_place_ok`は`12000|300`等も許す)。R-4 Secondary側は値ガードの既知不具合(OPEN-523/524)を引き継ぐ→composite条件としてSecondary値atomを数字・漢数字表記に限るか、先に不具合を直す。R-5 F1が新たに生む誤NGをProductionで計測(API 0): JAの`final_gate_value_diff`/`p1_value_diff`件数と、Azure呼出時のS転写保存。R-6 L2865と実装(R4)の不一致はβ承認に混ぜず別件。R-7 監査記録に`reading_source=primary`/`value_source=secondary`。R-8 フック①の事前判定結果が最終判定に流用されないことを配線testで固定。C-1〜C-7(独立性、最終ANDゲート常時、矛盾型NG維持、ε/F1側救済/F2拡張の却下妥当、UDR #136非接触・新受理クラスはL2179/L2856変更=ユーザー採用承認、HR/attempt/fallback不変、決定性)。事前登録不足: 比較基準列・複数atom・SecondaryのかなN数詞/全角数字/空白run(`8000 900本`)/`万`を含むF-B負例。ユーザー確認: βのProduction採用(v2読み規則を含むことを明示)。γは時期尚早、J3「超/超え」試聴は別件で適切。進め方: (i)M-1再評価→(ii)R-5頻度データ→(iii)効果が狭ければVALIDATED(限定)で止め低優先の採用候補。

## Fable判断(委任文の逐語)
M-1〜M-3・R-1〜R-8すべて採用。T1は実施しない。βのStatusはM-1再評価後に確定(機械写像+Fable)。R-5(Production側の計測・S転写保存)は**07A commit後に別委任で実装**(本委任では計測仕様を書くのみ)。

## 対応表(Sonnet作成。所見→反映先)
| 所見 | 反映 | 証跡 |
|---|---|---|
| M-1 | 列を`base`/`base+F1F2`/`base+F1F2+β`(+参考列)に是正し全基準を再評価。採用承認対象にv2読み規則が含まれる旨を明記 | `B_LIGHT_EVAL_02.md`、`B_LIGHT_DESIGN_02.md` §1 |
| M-2 | `composite_contributed`/`composite_reuse_decision`(scope外・flag OFFを先にblock→保存S転写で再判定→provenance欠落はfail-closed)、`composite_judge`は`secondary_meta`(engine・wav_sha256)必須 | proto v2、test、DESIGN_02 §2 |
| M-3 | 複数atom負例17件・F-B/Secondary表記負例19件を追加(基準は緩めず)。`value_guard`は**位置照合**(順序入替でDIFF)と実測、さらにatom列を二重照合 | proto v2、test、EVAL_02 §F |
| R-1/R-2 | Secondary読み食い違い=警告`JA_COMPOSITE_SECONDARY_READING_CONFLICT`+試聴必須(`veto`オプションを併せて評価)、garble説明=試聴必須 | proto v2、DESIGN_02 §4 |
| R-3 | F-A=2断片のみ・前断片`[1-9]0+`、3断片無効。F-Bの前断片も同形 | proto v2、test、DESIGN_02 §5 |
| R-4 | 原稿・Secondaryの値atomを数字・漢数字表記に限定(かな数詞・amb・単位なしはNG) | proto v2、DESIGN_02 §6 |
| R-5 | `R5_MEASUREMENT_SPEC_01.md`(仕様のみ。実装は07A後の別委任)+保存転写での予備集計(EVAL_02 §I) | R5仕様、EVAL_02 |
| R-6 | β承認に混ぜない別件として分離 | DESIGN_02 §9 |
| R-7 | auditに`reading_source`/`value_source`ほか | proto v2、DESIGN_02 §7 |
| R-8 | `precheck_composite`は`PrecheckResult`(`.equal`なし)を返し、`composite_judge`はprecheck metaを拒否。配線testの項目を固定 | proto v2、test、DESIGN_02 §8 |
| T1非実施 | 有料run 0、実費0円 | `B_LIGHT_PREREGISTERED_02.md` §2 |
