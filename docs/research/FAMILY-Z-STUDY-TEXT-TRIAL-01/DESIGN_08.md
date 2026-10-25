# DESIGN_08(Trial-08: 倒置の優先順位を下げ、倒置以外の学習価値の高い構文を優先する)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_18 / 日付: 2026-10-25 / Status: DEV/Trial専用。到達上限VALIDATED。Production採用・配線・Production file変更は禁止。
根拠: ユーザー指示(`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_08.md`)。基盤: Trial-07(`DESIGN_07.md`/`run_trial_07.py`)。実装: `run_trial_08.py`/`analyze_08.py`/`test_trial_08.py`。基準: `PREREGISTERED_CRITERIA_08.md`(有料再抽出の前にcommit)。

## 1. Trial-07からの差分(これだけ)
| 項目 | Trial-07 | Trial-08 |
|---|---|---|
| 選定順 | 適格を(クラス優先 INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS, 段落, 出現順)で先頭1件 | **Tier1=INV以外の適格(Trial-07の順位のまま)→ Tier2=適格なINV → Tier3=0件**(`select_tiered`) |
| 適格条件 | `eligible7` | **同一**(`teaching_value=HIGH`+`teaching_value_ja`非空、中クラスの`misread_*`、FRONT`front_kind`、ELL`omitted_words`、basic_only=false、単一span検証)。閾値の変更なし |
| 最大件数 | 1 | 1(同一) |
| 倒置の扱い | 最優先 | **除外はしない**。Tier1が空のときだけ適格なINVを選ぶ(`select_tiered`のTier2。selftestで「INVのみ→INV選定」「Tier1がLOWで不適格→INV選定」を固定) |
| 抽出Prompt(再抽出する作品のみ) | 「特にINV・CLEFT・CMPの3つは…最後にもう一度確認」 | この1文だけを「特にINV以外の分類(CLEFT・CMP・FRONT・HEAVY・POSTMOD・SPEC・ELL・APPOS)について…」に差し替え。他は1文字も変えない(selftestで`p7.replace(OLD,NEW)==p8`をassert) |
| 本文・モデル・N・費用ガード | gpt-6-luna、予約方式 | 同一(本文はTrial-07と同じ8作品。告げ口心臓もTrial-07本文) |

## 2. 候補欠落の判定(根拠。Step A)
Trial-07の抽出(Step A'')は「数に上限を設けず列挙」「選択は行わない」(Prompt手順1)で、候補数上限・クラス優先による絞り込みは**ない**(出力トークンは1.3k〜6.5kで`max_output_tokens`=13000に未達、truncation証跡なし)。しかし次の根拠で「非INV候補が欠落し得る」と判断した(`reselect_08.json`・`OUTPUT_07_*`):
1. **Promptが強クラス3種(INV・CLEFT・CMP)の見落とし再確認だけを指示**しており、INV以外の中クラスへ同等の再確認がない(Prompt手順1の末尾文)。
2. **標本間の再現性のばらつき**: 賢者の贈り物は登録済み中核P4(`handed down…`)が3標本とも出ず、CMP P12はr3だけ。猿の手はSPEC(P18/P22)がr2だけ。告げ口心臓はr1はCMP/FRONT/POSTMODを出し、r2はINVのみ(CMP/FRONTはTV=LOW)。
3. 結果としてTier1が空になる作品(賢者r1/r2・猿r1)は、倒置残存が「他に候補がない」のか「抽出で出なかった」のか既存データでは区別できない。
4. OTHERは自動選定の対象外(Trial-04〜07の規則。材料欄が空)。ユーザーのTier1例示にある「分詞構文・付帯状況」「その他」のうちOTHERに入るものはこの機構では選定されない=構造的な未対応(新Prompt・新分類を作ると「既存機構の維持」に反するため**変更しない**。事実のみ報告し、仕様候補としてFableへ渡す)。

判定(作品別): 開いた窓=既存データで検証可(全3標本にTier1=HEAVY P29あり)/ イグ・ノーベル・退屈と攻撃性=INVが候補にないため順位変更の影響なし(既存データで検証可、再抽出不要)/ **賢者の贈り物・猿の手・告げ口心臓=再抽出要**(重点の旧倒置作品。Tier1が空または標本依存)/ **二十年後・走れメロス=再抽出**(Tier1の見落としでないか=0件の妥当性確認。INVは候補になし、順位変更の影響はないが「見落とし」基準4の確認のため同一条件で再抽出。N=2)。

## 3. 実行計画と費用
- 再抽出: 賢者3・猿の手2・告げ口心臓2・二十年後2・走れメロス2 = **11 call**(Trial-07のNと同じ)。モデル=gpt-6-luna(Trial-07と同一。最新原則との関係: Trial-07で最新世代の推奨系として採用したモデルと同一にすることが比較条件の同一性=目的。評価用途で最新でない例外ではなく、Trial-07時点で最新)。予約方式で上限11.0円(本委任12円のうち翻訳用1円を残す)。実測0.33円/call×11≒3.7円の見込み(Trial-07実績)。
- 案件累計: 35.245円 + 本委任上限12円 = 47.245円 ≤ 50円(`BUDGET_LOG_01.md`の案件上限)。
- 新Step Bの全文生成はしない(必須範囲外)。新選定文の日本語訳のみ、既存訳(Trial-07 Step B USER.md)があれば再利用、無ければT1 module(`er003_kp_source_sentence_ja_01.generate_translations`、読み取り利用)。
- 並列化: 5作品×標本11 callを1 launchで並列実行(予約方式)。API 0作業(reselect・analyze・EVAL雛形)は実行と並行。

## 4. Production境界
Production code/Prompt/閾値/flagの変更0。`run_trial_08.py`はDEV専用で`run_trial_07`/`run_trial_06`/`run_trial_04`をimportするのみ。T1 moduleは読み取り利用。
