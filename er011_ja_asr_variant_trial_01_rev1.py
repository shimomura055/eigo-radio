# ============================================================
# er011_ja_asr_variant_trial_01_rev1.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 修正1回目
# ============================================================
# Fable差し戻し指示: Candidate C(正規化層)を、Candidate B
# (er011_ja_asr_variant_trial_01.py)と同じ「追加型(additive)」設計で
# 実装する。既存のpykakasi判定・Candidate B実装・Production関数
# (er007_ja_asr_validator_01.py / er011_a2_reading_resolver_01.py)は
# 一切変更しない。本ファイルは新規追加ファイルであり、初回Trialの
# 成果物(er011_ja_asr_variant_trial_01.py)を変更せず、その「上に」もう
# 1段の追加チェックを重ねるだけ(呼び出すだけ、importして再利用するだけ)。
#
# 挿入位置: Candidate B(fugashi/unidic-lite形態素読みチェック)でも
# 解決しなかった場合にのみ、Resolver(LLM)呼び出し直前でCandidate Cの
# 正規化を試す。Candidate Bが既に何らかの判定(unchanged/rescued)を
# 確定させた場合は、Candidate Cへは一切到達しない(Candidate Bの結果を
# 変更しない、既存の追加方式の原則をそのまま踏襲)。
from __future__ import annotations

import re

import er003_audio_tts_asr_safety as safety  # 読み取り専用の再利用(変更しない)
import er007_ja_asr_validator_01 as javal  # 読み取り専用の再利用(変更しない)
import er011_ja_asr_variant_trial_01 as candidate_b  # Trial専用、初回成果物(変更しない)

# ------------------------------------------------------------
# (a) カタカナ語の語末長音符(チョウオンプ、「ー」)の省略差を吸収する。
# ------------------------------------------------------------
# 対象範囲(意図的に狭く限定する):
#   - カタカナ(+長音符)の「連続塊」全体が4文字以上、かつその連続塊の
#     "最後の1文字"が長音符「ー」である場合に限り、末尾の「ー」だけを
#     1文字取り除く。
#   - 連続塊の途中にある長音符(例:「サーバー」の1文字目の後のー)は
#     対象外(削除しない)。取り除くのは常に「語の一番最後」の長音符
#     だけであり、これはJIS Z 8301(標準情報[TR])が慣用として認めている
#     「3モーラ以上の外来語は語末の長音符を省略してよい」というスタイル
#     差(コンピューター/コンピュータ、サーバー/サーバ、ユーザー/ユーザ
#     等、Microsoft/IPA等の実務スタイルガイドでも広く使われる)そのもの
#     であり、個別の単語テーブルではなく「語末長音符の有無」という
#     一般的な構造的ルールとして実装している。
#   - 4文字未満のカタカナ+長音符連続(例:「スキー」「コピー」「バー」)は
#     対象外とする。短い外来語ほど、長音符の有無で全く別の語になる
#     リスク(「バス」/「バース」、「キー」/「キ」等)が相対的に高いため、
#     本Trialで実際に観測された実例(4文字以上)の範囲だけに限定し、
#     過剰な一般化はしない。
_KATAKANA_RUN_RE = re.compile(r"[ァ-ヴー]+")
_MIN_RUN_LEN_FOR_CHOONPU_STRIP = 4


def _strip_trailing_choonpu_in_run(run: str) -> str:
    if len(run) >= _MIN_RUN_LEN_FOR_CHOONPU_STRIP and run.endswith("ー"):
        return run[:-1]
    return run


def normalize_katakana_trailing_choonpu(text: str) -> str:
    """カタカナ連続塊の末尾長音符だけを、上記の限定条件下で取り除く。
    それ以外(連続塊の途中の長音符、4文字未満の連続塊)は一切変更しない。"""
    if not text:
        return text
    return _KATAKANA_RUN_RE.sub(lambda m: _strip_trailing_choonpu_in_run(m.group(0)), text)


# ------------------------------------------------------------
# (b) 助数詞「ヶ月/ヵ月/カ月」を、既存Production(er003_audio_tts_asr_
#     safety.py の閉じた助数詞リスト _CLOSED_COUNTERS_JA)が既に認識して
#     いる表記「か月」へ統一してから、既存Production関数
#     normalize_kanji_counter_numerals_ja()(無変更、再利用のみ)を
#     再適用する。
# ------------------------------------------------------------
# 対象範囲を「月」に限定する(指示で明示された範囲を超えない、「ヶ所/
# ヵ所/カ所」等の他の助数詞は本Trialでは対象外・別途検討が必要)。
# 「ヶ/ヵ/カ」はいずれもこの文脈(直後が「月」)では小書きの「ヶ」
# (「箇」の略字)の異体字であり、「か」と読みが同じであることが文脈から
# 確実なため、既存の閉じた助数詞正規化と同じ安全性の理屈(助数詞の直前
# という文脈があるため意味・読み・数量が完全に同じ表記ゆれとして安全に
# 判別できる)がそのまま当てはまる。
_MONTH_COUNTER_VARIANT_RE = re.compile(r"[ヶヵカ]月")


def normalize_month_counter_variants(text: str) -> str:
    if not text:
        return text
    t = _MONTH_COUNTER_VARIANT_RE.sub("か月", text)
    # 既存Production関数を「呼び出すだけ」(再実行しても副作用なし、
    # 冪等)。この関数自体は一切変更していない。
    t = safety.normalize_kanji_counter_numerals_ja(t)
    return t


def normalize_candidate_c(text: str) -> str:
    """Candidate C正規化層(本Trial専用の追加チェック)。(a)(b)の2つの
    軽量ルールベース正規化を順に適用するだけで、それ以外は一切変更しない
    (個別語テーブルではなく、いずれも構造的な範囲限定ルール)。"""
    t = normalize_katakana_trailing_choonpu(text)
    t = normalize_month_counter_variants(t)
    return t


# ------------------------------------------------------------
# 形態素分割のあいまいさ(1件、原因調査): 「一日中」を形態素解析器が
# 「一」+「日中」(にっちゅう)へ誤分割し、正しい「いちにちじゅう」を
# 読めない、という初回Trialで記録されたクラスのリスクについて。
# ------------------------------------------------------------
# 調査結果(本修正で確認、詳細はREPORTの「修正1回目」節に記載):
#   1. 本Trialのテストセット(82件+実データ79件、計161件)の中で、この
#      ケースは実際には失敗していない。「いちにちじゅう家で過ごした。」/
#      「一日中家で過ごした。」は、既存Production(pykakasi)側の全文読み
#      判定が最初の時点で既に読み一致(ichinichijuuiedesugoshita ==
#      ichinichijuuiedesugoshita)と判定しており、Candidate B/Cの追加
#      チェックへはそもそも到達しない(baseline_result.classification が
#      既にTRUE_CONTENT_MISMATCH以外のため、classify_with_candidate_
#      additive() の最初のガードで unchanged として返る)。
#   2. 「読み比較を文全体のかな列で行う」という一般的対処は、Candidate B
#      が既に採用している設計そのもの(morph_hira_reading()は文全体を
#      形態素へ分割し、各形態素のkana素性を連結するため、局所的な単語
#      単位の比較ではなく既に全文かな列同士の比較になっている)。それでも
#      なお「一日中」の分割誤りが起き得るのは、比較方式(全体か部分か)の
#      問題ではなく、辞書(unidic-lite)が「一日中」という複合語を1語として
#      持たず、最長一致等の理由で「一」+「日中」に分割してしまう
#      形態素解析器固有の辞書エントリの問題であるため、比較方式の変更
#      では原理的に解決できない。
#   3. 個別語を辞書やテーブルへ追加することは、本Trialで明示的に禁止
#      されている「個別語テーブル」化そのものになるため採用しない。
#   4. 安全性の構造的な議論: この分割誤りが実際に問題化するのは、
#      「(i) 既存pykakasi判定が誤ってTRUE_CONTENT_MISMATCHと判定し、かつ
#      (ii) Candidate Bの誤った形態素分割による読みが、たまたま無関係な
#      別のASR書き起こしの読みと偶然一致してしまう」という二重の偶然が
#      重なった場合に限られる。前者(pykakasiが誤ってMISMATCH化する)は
#      Candidate B/C導入前から存在するpykakasi側の既知の限界であり
#      (Candidate B/C不在でも同じ入力はそのままTRUE_CONTENT_MISMATCH→
#      Resolverへ回る、Candidate B/C追加による悪化ではない)、後者
#      (偶然の読み一致)は本Trial実測(161件、負例30件含む)で0件だった
#      ことに加え、日本語の語彙の性質上、既存のCandidate Bのfail-safe
#      設計(exact/voicing一致のみ、それ以外は素通り)により極めて起き
#      にくい。
# 結論: この分割誤りのクラス自体は実在するが、(i)本Trialのテストセット
# では実害(誤PASS・回帰)を1件も引き起こしておらず、(ii)一般的な対処
# (全文かな列比較)は既に採用済みで、(iii)個別語辞書追加は禁止事項に
# 抵触するため、「特殊語(形態素解析器の辞書エントリに依存する複合語
# 分割の限界)」として、対処せず・追加リスクなしと結論して除外する。


def classify_with_candidate_additive_bc(canonical_text: str, asr_text: str):
    """Candidate B(fugashi/unidic-lite形態素解析) -> Candidate C
    (カタカナ長音符・助数詞ヶ月表記の正規化層)の順で、既存Resolver呼び
    出し直前へ2段の追加チェックを重ねる。いずれの段も「既に確定した
    判定を変更しない」設計のため、Candidate B単体・既存pykakasi判定の
    結果は一切変更しない(構造的にregressionが発生しない)。"""
    b_result, calls, b_tag = candidate_b.classify_with_candidate_additive(canonical_text, asr_text)
    if b_tag != "unresolved":
        # Candidate Bが既に確定させた判定(unchanged=既存pykakasi判定を
        # 維持、rescued_*=Candidate Bで解決済み)には一切触れない。
        return b_result, calls, f"b:{b_tag}"

    # ここに到達するのは、既存pykakasi判定・Candidate B(形態素読み)の
    # どちらでも読みが一致しなかった場合のみ。
    c_norm = javal.normalize_ja(canonical_text)
    a_norm = javal.normalize_ja(asr_text)
    c_norm2 = normalize_candidate_c(c_norm)
    a_norm2 = normalize_candidate_c(a_norm)

    if c_norm2 == a_norm2:
        # 正規化後に文字列として完全一致(読みエンジンを介さない、最も
        # 安全な一致判定。誤読・辞書依存のリスクが構造的に存在しない)。
        rescued = javal.ClassificationResultJA(
            "NORMALIZED_MATCH", b_result.similarity_ratio, b_result.protected,
            should_pass=True, should_retry=False,
            reason="(Candidate C追加チェック)カタカナ語末長音符の省略差・"
                   "助数詞表記(ヶ月/ヵ月/カ月->か月)の正規化後に文字列として完全一致")
        return rescued, calls, "rescued_by_normalization_c_exact"

    # 正規化後もなお残る差(例:「まる」/「丸」のような漢字/ひらがな差が
    # 助数詞差と同時に発生している場合)は、Candidate Bの形態素読み
    # エンジンを「正規化後のテキスト」へ再適用して読み一致を確認する
    # (Candidate B自体のロジックは一切変更せず、入力テキストだけを
    # Candidate Cの正規化後に差し替えて呼び出すだけ)。
    if candidate_b._reading_equal_morph(c_norm2, a_norm2):
        rescued = javal.ClassificationResultJA(
            "PHONETIC_MATCH", b_result.similarity_ratio, b_result.protected,
            should_pass=True, should_retry=False,
            reason="(Candidate C追加チェック)正規化後、fugashi/unidic-lite"
                   "形態素解析ベースの読みが完全一致")
        return rescued, calls, "rescued_by_normalization_c_then_morph"

    if candidate_b._reading_equal_allowing_voicing_morph(c_norm2, a_norm2):
        rescued = javal.ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", b_result.similarity_ratio, b_result.protected,
            should_pass=False, should_retry=False,
            reason="(Candidate C追加チェック)正規化後、形態素解析ベースの"
                   "読みが濁点/半濁点の有無を除き一致(Cascade対象、即PASSにはしない)")
        return rescued, calls, "rescued_to_cascade_by_normalization_c_then_morph_voicing"

    return b_result, calls, "unresolved"
