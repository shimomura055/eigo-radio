# Rerun variability note (transparency record)

`main()`はスクリプト末尾に誤って2回分の実行トリガー(既存の`if __name__ ==
"__main__": main()`と、追記した`if __name__ == "__main__" and
os.environ.get("RUN_A2_ONLY"): main_a2()`)が両方成立し、Candidate B /
Candidate Aは意図せず2回(計2回分のAPI呼び出し×2種)実行された。

- 1回目実行時(ディスクには保存されず、ツール出力ログにのみ残存):
  Candidate B: false_reject 1件(tension_repeated_desk_useのみ)、正解5/6
  Candidate A: false_reject 5件、正解1/6(matched_evidence_idsは概ね妥当
  だったが、classification=FACTUAL_CLAIM_SUPPORTED_BUT_UNCITEDを選び、
  「本文中に出典が無い」ことを理由にほぼ全項目でshould_still_require_review
  =trueとした)
- 2回目実行時(ディスクに永続化、`candidate_b_result.json`/
  `candidate_a_result.json`が該当): Candidate B/Aとも
  false_reject 4件、正解2/6(voiceA/voiceB系3項目が
  OBJECTIVE_FACTUAL_CLAIM/要レビューへ変化)

同一prompt・同一model・同一reasoning_effortでも、Candidate B/Aの判定は
試行間で一致しなかった(非決定性)。一方、Candidate A'
(`candidate_a2_result.json`、1回のみ実行)は、Voice本文における
「本文中出典明記は仕様上不要」という明示ルールを追加した結果、
false_reject 1件・正解5/6で、A/Bの2回の実行結果よりも安定して高い結果と
なった。ただしCandidate A'も1回しか実行しておらず、再現性(複数回実行で
同じ判定になるか)は本Trialでは未検証。
