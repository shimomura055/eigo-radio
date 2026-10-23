# GOLDEN_CHANGE_01 -- X/Z golden fixture 再作成と変化行の3分類(W-05、UKUS 委任_04)
- 生データ: `GOLDEN_CHANGE_01.json`(`golden_rebuild_01.py --write` の出力)、`V6_matrix_golden_UKUS_rows_01.json`(UKUS合成行14件×5経路×X/Zの 配線前 / 現行v2 比較)。
- 手順: (1) `er109_wiring_golden_build_01.py --append-ukus`で既存golden rows(g0000-g0297)を**byte不変**のまま末尾へUKUS合成行14件(g0298-g0311)追記 (2) 配線前commit `b7b6d07d8` のroot直下.py/.jsonをoverlay(`ER109_OVERLAY`)にして署名toolを実行:
  **既存行の再計算==既存fixture(scope none/X/Z、各1,458 key)が mismatch 0**(手順の妥当性確認)、新行(各70 key)のpre署名だけを `pre_wiring_signatures_{none,X,Z}_01` の末尾へ追記(既存行・`manifest.pre_wiring_commit`不変)
  (3) 現行コード(LAYER_VERSION=`er109_orthographic_equivalence_v2_ukus01`)でX/Z署名を採り `post_wiring_changed_{X,Z}_01` を再作成 (4) 変化行の分類。
- 分類(X/Z同数): 既存行で pre(配線前)から変化した 598 key = **version文字列のみ 598**(中間baseline=現HEAD[v1]のX/Z署名と、version文字列を正規化すると完全一致) / **既存行の新規UKUS PASS 0**(保存標本298行にはUKUS対の行が含まれない) / **PASS->NG 0** / 想定外の変化 0。unchanged vs pre 888。
  新行(UKUS合成行): 42 key(14行×3経路相当)が変化=UKUS陽性行のPASS化と負例のNG維持(`V6_matrix_golden_UKUS_rows_01.json`)。
- **scope none(A/B/C相当)**: 新行を含む全1,528 keyが配線前署名と**完全一致**(差分0)。
- 新行の判定(X、Zも同一): g0298 c12 Primary PASS / g0299 c12 Secondary(Azure)がspecialtyで受理(PASS_WITH_WARNING=既存secondary_confirmed経路) / g0300-0301 KP PASS / g0302 複数位置 PASS / g0304 AMB uk->us PASS / g0310 their-there隣接n:n spanで位置別救済 PASS。
  負例NG維持: g0303 AMB逆方向 / g0305 固有名詞(Aluminium City) / g0306 綴り差+実誤読 / g0307 +実数値差(NG_PROTECTED、Store guardはblocked) / g0308 +not脱落(NG_PROTECTED、blocked) / g0309 mum/mom / g0311 語数違いspan。
- 注意(挙動変化の記録): g0300(KP 'Her speciality'/'Her specialty'、Azure=原稿綴り)は配線前=PASS_WITH_WARNING(Secondary確認)、v2=PASS(Primaryが綴り差のみで合格)。PASS->PASSでwarningが外れる方向のみ(NGへは動かない)。
