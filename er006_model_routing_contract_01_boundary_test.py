# ============================================================
# er006_model_routing_contract_01_boundary_test.py
# ER-006-MODEL-ROUTING-CONTRACT-01 / 追補: Production API Boundary Fail-Closed実証
# ============================================================
# 目的: N3/Pool ProductionのWriter/Fact Check/Deviation Check/Support/
# Key Phrase呼び出しにおいて、
#   (1) SSOTのApproved Modelが規定外(Sol)や未知値に汚染されている場合、
#   (2) SSOTがmodel未指定(None)を返す場合、
# のいずれでも、**実際にAPIへ到達する前**に例外が送出されることを、
# 「偽のclientオブジェクトが一度も呼ばれないこと」という形で直接証明する。
# 新規有料API呼び出しは一切発生しない(FakeClientは例外なくAPIへ到達しない
# ことを確認するためだけに存在し、正常系でも本物のresponses.createは呼ばない)。
from __future__ import annotations

from unittest import mock

import er006_model_routing_contract_01 as routing
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_b1_scaffold_01_generate as b1s


class BoundaryTouchedError(Exception):
    """FakeClientのresponses.createが呼ばれてしまった場合に送出する
    (=fail-closed契約が破られ、実際にAPI境界へ到達したことを示す)。"""


class FakeResponses:
    def create(self, **kwargs):
        raise BoundaryTouchedError(f"API boundaryへ到達してしまった: {kwargs.get('model')!r}")


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def run():
    failures = []
    fake_client = FakeClient()

    print("=== Boundary: Writer(vfl01.run_writer_with_technical_retry)の実呼び出し形 ===")
    # run_one_pattern()の実際のWriter呼び出し式そのもの
    # (vfl01.run_writer_with_technical_retry(client, prompt, model=routing.require_model(process, routing.WRITER_MODEL)))
    # を、SSOTを汚染した状態で評価し、FakeClientへ到達する前に例外が飛ぶことを確認する。
    for bad_value, label in [("gpt-5.6-sol", "Sol汚染"), ("gpt-99-unknown", "未知model汚染"), (None, "未指定汚染"), ("", "空文字汚染")]:
        with mock.patch.object(routing, "WRITER_MODEL", bad_value):
            try:
                vfl01.run_writer_with_technical_retry(
                    fake_client, "dummy prompt",
                    model=routing.require_model("B1_WRITER", routing.WRITER_MODEL))
                ok = False
                reason = "例外が送出されなかった"
            except routing.ModelContractViolation:
                ok = True
                reason = "ModelContractViolationがAPI到達前に送出された"
            except BoundaryTouchedError as e:
                ok = False
                reason = f"API boundaryへ到達してしまった: {e}"
            status = "OK" if ok else "FAIL"
            print(f"[{status}] Writer + {label}({bad_value!r}): {reason}")
            if not ok:
                failures.append(f"Writer boundary / {label}")

    print("\n=== Boundary: Writer Fact Check(r3.make_fact_checker_fn)の実呼び出し形 ===")
    import er002_ja_web_research_r3 as r3
    for bad_value, label in [("gpt-5.6-sol", "Sol汚染"), (None, "未指定汚染")]:
        with mock.patch.object(routing, "WRITER_FACT_CHECK_MODEL", bad_value):
            try:
                fn = r3.make_fact_checker_fn(
                    "dummy prompt", client=fake_client,
                    model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))
                fn()  # 実際にAPIを呼ぶのはこの時点
                ok = False
                reason = "例外が送出されなかった"
            except routing.ModelContractViolation:
                ok = True
                reason = "ModelContractViolationがAPI到達前に送出された"
            except BoundaryTouchedError as e:
                ok = False
                reason = f"API boundaryへ到達してしまった: {e}"
            status = "OK" if ok else "FAIL"
            print(f"[{status}] Writer Fact Check + {label}({bad_value!r}): {reason}")
            if not ok:
                failures.append(f"Writer Fact Check boundary / {label}")

    print("\n=== Boundary: Deviation Check(vfl01.run_deviation_check)の実呼び出し形 ===")
    for bad_value, label in [("gpt-5.6-sol", "Sol汚染"), (None, "未指定汚染")]:
        with mock.patch.object(routing, "WRITER_MODEL", bad_value):
            try:
                vfl01.run_deviation_check(
                    fake_client, "dummy ledger", "dummy article",
                    model=routing.require_model("A2_WRITER", routing.WRITER_MODEL))
                ok = False
                reason = "例外が送出されなかった"
            except routing.ModelContractViolation:
                ok = True
                reason = "ModelContractViolationがAPI到達前に送出された"
            except BoundaryTouchedError as e:
                ok = False
                reason = f"API boundaryへ到達してしまった: {e}"
            status = "OK" if ok else "FAIL"
            print(f"[{status}] Deviation Check + {label}({bad_value!r}): {reason}")
            if not ok:
                failures.append(f"Deviation Check boundary / {label}")

    print("\n=== Boundary: B1 Support(b1s.run_support_text)の実呼び出し形 ===")
    import er003_v1_n3_01_scaffold_generate as sc
    for bad_value, label in [("gpt-5.6-sol", "Sol汚染"), (None, "未指定汚染")]:
        with mock.patch.object(routing, "SUPPORT_MODEL", bad_value):
            try:
                b1s.run_support_text(fake_client, "role", "context", model=sc._b1_support_model())
                ok = False
                reason = "例外が送出されなかった"
            except routing.ModelContractViolation:
                ok = True
                reason = "ModelContractViolationがAPI到達前に送出された"
            except BoundaryTouchedError as e:
                ok = False
                reason = f"API boundaryへ到達してしまった: {e}"
            status = "OK" if ok else "FAIL"
            print(f"[{status}] B1 Support + {label}({bad_value!r}): {reason}")
            if not ok:
                failures.append(f"B1 Support boundary / {label}")

    print("\n=== Boundary: Key Phrase Selector(bk.make_selector_fn経由)の実呼び出し形 ===")
    for bad_value, label in [("gpt-5.6-sol", "Sol汚染"), (None, "未指定汚染")]:
        with mock.patch.object(routing, "SUPPORT_MODEL", bad_value):
            try:
                sel = sc.run_key_phrase_selection("dummy article", "/tmp/_mrc_boundary_test", "test_id",
                                                   "test_level", process="B1_SUPPORT")
                # run_key_phrase_selectionは内部でmake_selector_factory()を呼ぶ
                # gate関数を実行するため、ここまで到達したらAPI境界を越えている
                ok = False
                reason = f"例外が送出されなかった(status={sel.get('status')})"
            except routing.ModelContractViolation:
                ok = True
                reason = "ModelContractViolationがAPI到達前に送出された"
            except BoundaryTouchedError as e:
                ok = False
                reason = f"API boundaryへ到達してしまった: {e}"
            except Exception as e:
                # prod.run_production_selection_gate側のI/O(client未使用時の
                # 例外等)でFakeClient以外の理由で失敗した場合はここに来る。
                # ModelContractViolationでない時点でfail-closedとしては不合格。
                ok = False
                reason = f"予期しない例外: {type(e).__name__}: {e}"
            status = "OK" if ok else "FAIL"
            print(f"[{status}] Key Phrase Selector + {label}({bad_value!r}): {reason}")
            if not ok:
                failures.append(f"Key Phrase Selector boundary / {label}")

    if failures:
        raise AssertionError(f"{len(failures)}件のboundary testが失敗した: {failures}")
    print(f"\nOK: 全boundary testでAPI到達前にfail-closedが機能することを確認した"
          f"(FakeClient.responses.createは一度も呼ばれなかった)")


if __name__ == "__main__":
    run()
