# RESCUE_TABLE (自動生成 rescue_eval_08) — 詳細はRESCUE_TABLE_01.md(人手整理版)

| # | Family/level | 元候補 | 除外クラス | min区分 | 通過した方式(tier/method→final) |
|---|---|---|---|---|---|
| 0 | X/a2 | `too soon to wave a flag` | WORDCOUNT_OVER5 | T0 | T0/A1_subspan→too soon; T2/A2_slot_generalization→too soon to do |
| 1 | X/a2 | `studied separately` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T1/LLM_key_as_is(区分1規則是正後)→study separately; T0/B_rederive_M1(現行規則)→studied separately; T1/B_rederive_M1(区分1規則是正後)→study separately; T2/B_rederive_M1(区分2含む)→study separately; T0/revert(表層形)→studied separately |
| 2 | X/a2 | `put in place` | HUMAN_NG_EXCLUDED | - |  |
| 3 | X/b1b | `off the hook` | HUMAN_NG_EXCLUDED | - |  |
| 4 | X/b1b | `had our eye on` | FINITE_AUX_TOKEN | T1 | T1/C_aux_gate(display=had our eye on,key=had our eye on)→had our eye on; T2/C_aux_gate(display=had our eye on,key=had our eye on)→had our eye on; T1/C_aux_gate(display=had our eye on,key=have our eye on)→have our eye on; T2/C_aux_gate(display=had our eye on,key=have our eye on)→have our eye on |
| 5 | Z/b1b | `rose above` | RULE7_NORMALIZATION/LLM_EXPANDED_BEYOND_SPAN | T0 | T0/B_rederive_M1(現行規則)→rise above; T1/B_rederive_M1(区分1規則是正後)→rise above; T2/B_rederive_M1(区分2含む)→rise above; T0/revert(表層形)→rose above |
| 6 | Z/b1b | `held out` | RULE7_NORMALIZATION/LLM_EXPANDED_BEYOND_SPAN | T0 | T0/B_rederive_M1(現行規則)→hold out; T1/B_rederive_M1(区分1規則是正後)→hold out; T2/B_rederive_M1(区分2含む)→hold out; T0/revert(表層形)→held out |
| 7 | Z/b1b | `sentenced him to death` | HUMAN_NG_EXCLUDED | - |  |
| 8 | Z/b1b | `rang through` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T1/LLM_key_as_is(区分1規則是正後)→ring through; T0/B_rederive_M1(現行規則)→rang through; T1/B_rederive_M1(区分1規則是正後)→ring through; T2/B_rederive_M1(区分2含む)→ring through; T0/revert(表層形)→rang through |
| 9 | Y/a2 | `it can’t be helped` | FINITE_AUX_TOKEN | T2 | T2/C_aux_gate(display=can’t be helped,key=can’t be helped)→can’t be helped |
| 10 | Y/a2 | `redelivery fee` | CMU_UNREGISTERED | - |  |
| 11 | Y/b1b | `can’t be helped` | FINITE_AUX_TOKEN | T2 | T2/C_aux_gate(display=can’t be helped,key=can’t be helped)→can’t be helped |
| 12 | Y/b1b | `have a say` | FINITE_AUX_TOKEN | T1 | T1/C_aux_gate(display=have a say,key=have a say)→have a say; T2/C_aux_gate(display=have a say,key=have a say)→have a say |
| 13 | Y/b1b | `catch their interest` | NOT_CONTIGUOUS_IN_TEXT | T0 | T0/D1_reanchor→catches their interest |
| 14 | X/a2 | `minaudières` | CMU_UNREGISTERED | - |  |
| 15 | X/a2 | `minaudières` | CMU_UNREGISTERED | - |  |
| 16 | X/a2 | `novelty minaudière` | CMU_UNREGISTERED | - |  |
| 17 | X/a2 | `minaudière` | CMU_UNREGISTERED | - |  |
| 18 | X/a2 | `minaudières` | CMU_UNREGISTERED | - |  |
| 19 | X/a2 | `have a big moment` | FINITE_AUX_TOKEN | T0 | T0/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T2/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big m |
| 20 | X/a2 | `have a big moment` | FINITE_AUX_TOKEN | T0 | T0/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T2/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big m |
| 21 | X/a2 | `have a big moment` | FINITE_AUX_TOKEN | T0 | T0/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T2/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big m |
| 22 | X/a2 | `have a big moment` | FINITE_AUX_TOKEN | T0 | T0/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T2/C_aux_gate(display=having a big moment,key=having a big moment)→having a big moment; T1/C_aux_gate(display=having a big m |
| 23 | Z/b1b | `were mocking me` | FINITE_AUX_TOKEN | - |  |
| 24 | Z/a2 | `offered his hands for the chains` | WORDCOUNT_OVER5 | T0 | T0/A1_subspan→offered his hands |
| 25 | Z/a2 | `lose my trust in you` | NOT_CONTIGUOUS_IN_TEXT | T0 | T0/D1_reanchor→lost my trust in you |
| 26 | Z/a2 | `in his place` | NOT_CONTIGUOUS_IN_TEXT | - |  |
| 27 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 28 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 29 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 30 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 31 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 32 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 33 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 34 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 35 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 36 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 37 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 38 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 39 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 40 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 41 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 42 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 43 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 44 | Z/a2 | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 45 | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - |  |
| 46 | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | - |  |
| 47 | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - |  |
| 48 | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - |  |
| 49 | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - |  |
| 50 | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - |  |
| 51 | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - |  |
| 52 | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - |  |
| 53 | Z/a2 | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 54 | Z/a2 | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 55 | Z/? | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 56 | Z/? | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 57 | Z/? | `could not bear` | FINITE_AUX_TOKEN | - |  |
| 58 | Z/b1b | `my ears began to ring` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's ears began to ring; T1/B_rederive_M1(区分1規則是正後)→one's ears began to ring; T2/B_rederive_M1(区分2含む)→one's ears began to ring; T0/revert(表層形)→my ears began to ring |
| 59 | Z/a2 | `lost touch` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→lost touch; T1/B_rederive_M1(区分1規則是正後)→lost touch; T2/B_rederive_M1(区分2含む)→lose touch; T0/revert(表層形)→lost touch |
| 60 | Z/b1b | `couldn't bring myself to arrest` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/LLM_key_as_is(現行)→couldn't bring oneself to arrest; T1/LLM_key_as_is(区分1規則是正後)→couldn't bring oneself to arrest; T0/B_rederive_M1(現行規則)→couldn't bring oneself to arrest; T1/B_rederive_M1(区分1規則是正後)→couldn't bring oneself to arrest; T2/B_rederive_M1(区分2含む)→couldn't bring oneself to arrest; T0/rever |
| 61 | Z/b1b | `lost touch` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→lost touch; T1/B_rederive_M1(区分1規則是正後)→lost touch; T2/B_rederive_M1(区分2含む)→lose touch; T0/revert(表層形)→lost touch |
| 62 | Z/b1b | `couldn't bring myself to` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/LLM_key_as_is(現行)→couldn't bring oneself to; T1/LLM_key_as_is(区分1規則是正後)→couldn't bring oneself to; T0/B_rederive_M1(現行規則)→couldn't bring oneself to; T1/B_rederive_M1(区分1規則是正後)→couldn't bring oneself to; T2/B_rederive_M1(区分2含む)→couldn't bring oneself to; T0/revert(表層形)→couldn't bring myself to |
| 63 | Z/b1b | `struck a match` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T1/LLM_key_as_is(区分1規則是正後)→strike a match; T0/B_rederive_M1(現行規則)→struck a match; T1/B_rederive_M1(区分1規則是正後)→strike a match; T2/B_rederive_M1(区分2含む)→strike a match; T0/revert(表層形)→struck a match |
| 64 | Z/b1b | `sentenced him to death` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/LLM_key_as_is(現行)→sentence someone to death; T1/LLM_key_as_is(区分1規則是正後)→sentence someone to death; T0/B_rederive_M1(現行規則)→sentence someone to death; T1/B_rederive_M1(区分1規則是正後)→sentence someone to death; T2/B_rederive_M1(区分2含む)→sentence someone to death; T0/revert(表層形)→sentenced him to death |
| 65 | Z/b1b | `nearly abandoned you` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→nearly abandoned someone; T1/B_rederive_M1(区分1規則是正後)→nearly abandoned someone; T2/B_rederive_M1(区分2含む)→nearly abandoned someone; T0/revert(表層形)→nearly abandoned you |
| 66 | Z/a2 | `pulling free` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→pulling free; T1/B_rederive_M1(区分1規則是正後)→pulling free; T2/B_rederive_M1(区分2含む)→pulling free; T0/revert(表層形)→pulling free |
| 67 | Z/b1b | `accepts no responsibility` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T1/LLM_key_as_is(区分1規則是正後)→accept no responsibility; T0/B_rederive_M1(現行規則)→accepts no responsibility; T1/B_rederive_M1(区分1規則是正後)→accept no responsibility; T2/B_rederive_M1(区分2含む)→accept no responsibility; T0/revert(表層形)→accepts no responsibility |
| 68 | Z/a2 | `pulling free` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→pulling free; T1/B_rederive_M1(区分1規則是正後)→pulling free; T2/B_rederive_M1(区分2含む)→pulling free; T0/revert(表層形)→pulling free |
| 69 | Z/a2 | `growing louder and louder` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→growing louder and louder; T1/B_rederive_M1(区分1規則是正後)→growing louder and louder; T2/B_rederive_M1(区分2含む)→growing louder and louder; T0/revert(表層形)→growing louder and louder |
| 70 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 71 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 72 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 73 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 74 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 75 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 76 | Z/a2 | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→froze my blood; T1/B_rederive_M1(区分1規則是正後)→freeze my blood; T2/B_rederive_M1(区分2含む)→freeze my blood; T0/revert(表層形)→froze my blood |
| 77 | Z/b1b | `eased open` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T0/B_rederive_M1(現行規則)→eased open; T1/B_rederive_M1(区分1規則是正後)→eased open; T2/B_rederive_M1(区分2含む)→eased open; T0/revert(表層形)→eased open |
| 78 | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's blood went cold; T1/B_rederive_M1(区分1規則是正後)→one's blood went cold; T2/B_rederive_M1(区分2含む)→one's blood went cold; T0/revert(表層形)→my blood went cold |
| 79 | Z/a2 | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→froze my blood; T1/B_rederive_M1(区分1規則是正後)→freeze my blood; T2/B_rederive_M1(区分2含む)→freeze my blood; T0/revert(表層形)→froze my blood |
| 80 | Z/a2 | `sure of myself` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/LLM_key_as_is(現行)→sure of oneself; T1/LLM_key_as_is(区分1規則是正後)→sure of oneself; T0/B_rederive_M1(現行規則)→sure of oneself; T1/B_rederive_M1(区分1規則是正後)→sure of oneself; T2/B_rederive_M1(区分2含む)→sure of oneself; T0/revert(表層形)→sure of myself |
| 81 | Z/a2 | `My ears began ringing` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's ears began ringing; T1/B_rederive_M1(区分1規則是正後)→one's ears began ringing; T2/B_rederive_M1(区分2含む)→one's ears began ringing; T0/revert(表層形)→My ears began ringing |
| 82 | Z/? | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→froze my blood; T1/B_rederive_M1(区分1規則是正後)→freeze my blood; T2/B_rederive_M1(区分2含む)→freeze my blood; T0/revert(表層形)→froze my blood |
| 83 | Z/? | `leaving no mark` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | T0 | T1/LLM_key_as_is(区分1規則是正後)→leave no mark; T0/B_rederive_M1(現行規則)→leaving no mark; T1/B_rederive_M1(区分1規則是正後)→leave no mark; T2/B_rederive_M1(区分2含む)→leave no mark; T0/revert(表層形)→leaving no mark |
| 84 | Z/? | `My ears began ringing` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | T0 | T0/B_rederive_M1(現行規則)→one's ears began ringing; T1/B_rederive_M1(区分1規則是正後)→one's ears began ringing; T2/B_rederive_M1(区分2含む)→one's ears began ringing; T0/revert(表層形)→My ears began ringing |
