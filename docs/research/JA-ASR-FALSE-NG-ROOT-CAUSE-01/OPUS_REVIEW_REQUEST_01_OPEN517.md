# OPUS_REVIEW_REQUEST_01_OPEN517(軽量レビュー依頼。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_05、2026-10-25)
目的: OPEN-517是正(Productionの最終ANDゲートが`READING_MATCH`のPASSで値DIFF・否定差の再確認をskipしている)の設計をProduction適用前に独立レビュー。種別=既存Gateの意味変更(新構造ではない)。11-3条件A準拠の軽量版。Production未変更・API 0。
## 添付(読む順)
`OPEN517_DESIGN_01.md`(矛盾の定義・是正案・影響)→`OPEN517_PREREGISTERED_01.md`(§0〜§6)→`OPEN517_EVAL_01.md`→`proto_value_gate_fix_03.py`(+`_test_01.py`)→`eval_open517_api0_03.py`→`open517_api0_eval_03.out.json`。Production参照: `er078_asr_unified_judge_01.py:68-73,526-560`、`er078_asr_value_guard_01.py`(`extract_atoms_ja`/`_guard_ja`/`_drop_verdict_ja`/`is_irregular_sig`)、`er007_ja_secondary_asr_01.py:427,603`、`CURRENT_SPEC.md:2855,2857,2865`。
## 質問(各に結論+根拠を)
1. **ゲートの意味変更の妥当性**: `READING_MATCH`をAPPROVED基底から外し、Primary PASSにも値DIFF=NG_PROTECTED(Secondary不呼出・次slot)、否定差=NG_PROTECTED、AMBIGUOUS=P3降格を適用する。これはCURRENT_SPEC:2855『重大内容差を警告だけで解放しない』の回復と見てよいか。他の承認根拠(HOMOPHONE_MATCH_NUMBER_EXCEPTION/TIER1_*)との整合に問題はないか。
2. **F2(かな書き数詞の期待読み表による表記統一)の安全性**: (a)期待読みと完全一致するかな列のみ置換、(b)既atom位置は不変、(c)Primary PASS(READING_MATCH)の最終ゲートのみ適用、(d)統一前の警告を併合。値違いを隠す経路(誤って等価と見なす)がないか。`_cands`のエラー(例: 四=し/よん、七、促音/連濁)で誤等価になる反例は。F2を外してF1のみにする案(正常音声の誤NG: P4 1/133・正例対照6/10)と比べた判断。
3. **取りこぼし**: 値ガードで検出できない型(N3-07近音[Candidate E=OPEN-333]、同形異音、助詞誤読、`七晩`↔`七番`[晩が助数詞表に無くUNKNOWN素通し])を、本是正の範囲外としてよいか。UNKNOWNの扱い(素通し)で是正すべき追加点はあるか。
4. **retry/HR・コスト**: 実attempt 421でNG化0。新規のNG_PROTECTEDはTTS再生成(retry消費)になる。slot3最終でのHR Lock化リスクの評価。
5. **Production適用の実装案**: 期待読み表(er066 Trial `_cands`)のProduction移設+parity testで足りるか、より小さい/安全な代替(例: 表を使わず『かな書き数詞が脱落するだけのDIFFはUNKNOWN扱い』)があるか。
## 評価の限界(開示)
F2はv1→v3と同一コーパスを見て再設計。未知データでの汎化未確認。Candidate Eの承認範囲=OPEN-333(未承認)は本是正で変更しない。
