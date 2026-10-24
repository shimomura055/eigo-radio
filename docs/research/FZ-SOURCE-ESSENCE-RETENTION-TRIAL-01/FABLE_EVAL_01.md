# FABLE_EVAL_01 — FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 Fable独立評価(2026-10-25、委任_02成果、API 0)
- 根本原因: R1/R2 Prompt固定文言 "in third person"(er062_family_z_writer_01.py:141)。1a対照実験で現行文言2/2反転・置換2/2維持=再現確認。副因=key_roles描画「名前を使わず役割で呼ぶ」が一人称作品で語り手を外から呼ばせた。構造根因=Seedの語り口がR0にしか渡らず、essentialsに語り口欄がなかった。
- 案A(narration_voice欄+Narration行+REVISE置換、Validator/追加LLM 0): 1b 2/2でAdv一人称維持(一人称語42/43、you 5/4)、Std人称一致、essentials欠落0。Fableが比較原稿(COMPARISON_01.md)を直接確認: 聞き手への語りかけ・自己陶酔・老人の恐怖を聞く心理・心臓音・自白・因果が保持され、現行Adv(三人称)との差は明確。テンポ維持(414語/文長6.3)。1c音声Gate PASS・HR Lock 0。Phase 2(賢者/開いた窓/猿の手)で人称不変・語り手介入誘発なし・語数文長±25%内・副作用なし。
- 事前基準未達=段落数2件(1b 17 vs 19〜25、猿の手40 vs 32)。完成版自体が工程間で±10揺れるためノイズ内とFable判断(基準は不変)。
- 費用108.81円/150円。量産増分=追加LLM 0、検出不能。
- Status(Fable): VALIDATED(Trial範囲、案A)。Production採用は含まない。
- 推奨: J1=案A採用、J2=採用後『告げ口心臓』Std/Adv正式再生成・差替え(現行公開版はAdv三人称NG・Std/Adv人称不一致)。採用時はOpus条件C→配線。
