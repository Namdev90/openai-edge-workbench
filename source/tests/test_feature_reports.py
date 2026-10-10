import copy
import json
from pathlib import Path
import unittest
from unittest import mock

import feature_reports as features


def fixture():
    return {
        "schema": "openai-edge-workbench/2", "run_id": "new", "final": True, "simulated": False,
        "workbench_version": "2.0.4", "started_utc": "2026-10-10T10:00:00Z", "finished_utc": "2026-10-10T10:10:00Z",
        "results": [
            {"id": "node", "name": "Node nightly and npm", "status": "VERIFIED", "kind": "special", "actual": "v27.0.0-nightly20261008",
             "started_utc": "2026-10-10T10:00:00Z", "finished_utc": "2026-10-10T10:01:00Z", "detail": "Actual versions matched",
             "npm_version": "12.2.0", "npm_host_version": "v26.11.1", "nightly_accepted_by_npm": False,
             "commands": [{"label": "npm version", "exit_code": 0, "tail": "12.2.0", "timed_out": False}]},
            {"id": "terminal", "name": "Terminal Preview", "status": "FAILED", "kind": "winget", "package": "Microsoft.WindowsTerminal.Preview",
             "source": "winget", "channel": "Preview", "expected": "1.25.0.0", "actual": "1.24.0.0",
             "started_utc": "2026-10-10T10:01:00Z", "finished_utc": "2026-10-10T10:09:00Z", "detail": "WININET_E_TIMEOUT (0x80072EE2)",
             "commands": [{"label": "WinGet install", "exit_code": 17, "tail": "Timed out", "timed_out": True}],
             "retries": [{"attempt": 1, "delay_seconds": 5, "reason": "WININET_E_TIMEOUT (0x80072EE2)", "package": "Microsoft.WindowsTerminal.Preview"}],
             "local_recovery": {"version": "1.25.0.0", "sha256": "a" * 64, "signature": {"status": "Valid", "subject": "Microsoft"}}},
            {"id": "migrate", "name": "Editor migration", "status": "REVIEW_NEEDED", "detail": "Existing conflicts retained"},
            {"id": "canary", "name": "Chrome Canary", "status": "CATALOG_CURRENT", "kind": "winget", "source": "winget", "channel": "Canary",
             "expected": "Catalog-managed; exact target unavailable", "actual": "present; exact version not parsed", "detail": "No applicable update; latestness not proved"},
            {"id": "science", "name": "Science pack", "status": "NOT_RUN", "detail": "Run stopped before this step"},
            {"id": "cleanup", "status": "VERIFIED", "removed": ["node/old"], "retained": ["new", "previous"], "detail": "Only unused Workbench-owned generations removed"},
        ],
        "managed_tools": {
            "node": {"version": "v27.0.0-nightly20261008", "command": ["C:/private/node.exe"], "source": "https://nodejs.org/download/nightly/index.json"},
            "npm": {"version": "12.2.0", "host_version": "v26.11.1", "engines": "^22.22.2 || ^24.15.0 || >=26.0.0", "diagnostics": [],
                    "command": ["C:/private/host.exe", "C:/private/npm-cli.js"], "source": "https://registry.npmjs.org/npm"},
            "javascript": {"version": "openai@6.0.0", "versions": {"openai": "6.0.0"}, "path": "C:/private/workspace", "source": "https://registry.npmjs.org"},
        },
        "checks": {
            "codex_doctor": {"exit_code": 0, "overall_status": "warning", "counts": {"ok": 40, "warning": 2},
                             "warning_count": 2, "failure_count": 0, "non_ok_checks": [
                                 {"id": "mcp", "status": "warning", "summary": "Optional connector missing", "details": {"issue": "Key not configured"}},
                                 {"id": "history", "status": "warning", "summary": "History indexing differs"}]},
            "network": {"API": {"transport_reached": True, "http_status": 401, "auth_or_protocol_verified": False},
                        "Docs": {"transport_reached": True, "http_status": 200, "auth_or_protocol_verified": False}},
            "codex_sign_in": {"exit_code": 0, "state": "ChatGPT login configured", "same_account_across_apps": "NOT_VERIFIED"},
            "github_sign_in": {"configured": True, "note": "Account identity not exported"},
            "codex_live": {"passed": True, "exit_code": 0, "expected_marker": "CONNECTION_OK", "quota_consumed_or_attempted": True,
                           "scope": "One configured CLI request; not every plugin"},
            "python_sdk_imports": {"passed": True, "exit_code": 0}, "codex_version": {"passed": True, "actual_output": "codex 1.0.0-alpha.1"},
            "provider": {"name": "local", "configuration_preserved": True},
            "active_local_provider": {"port": 8787, "listening": True, "service_identity": "NOT_VERIFIED"},
            "user_path_update": {"passed": True, "scope": "Workbench bin prepended to USER Path only"},
            "restart_apps": "Reopen apps to inherit PATH; no applications force-closed",
            "mcp_configuration": [{"name": "docs", "enabled": True, "type": "remote", "functional_status": "NOT_TESTED"},
                                  {"name": "optional", "enabled": True, "type": "local-process", "command_located": False, "functional_status": "NOT_TESTED"}],
        },
        "migrations": {"editor_files": {"copied": ["keybindings.json"], "conflicts": ["settings.json"]},
                       "editor_extensions": {"installed": ["ms-python.python"], "failed": ["unknown.extension"], "scope": "Default profile only"},
                       "retained": ["Original VS Code retained", "Old system runtimes retained"]},
        "python_compatibility": {"selected_version": "3.14.0", "newest_catalog_version": "3.15.0a1",
                                 "selection_reason": "Newest complete binary-wheel solution", "target": "x86_64-pc-windows-msvc",
                                 "packages": ["openai", "numpy"], "requirements_sha256": "b" * 64,
                                 "resolved_versions": {"openai": "2.0.0", "numpy": "3.0.0"},
                                 "attempts": [{"version": "3.15.0a1", "status": "INCOMPATIBLE", "exit_code": 1, "reason": "No compatible NumPy wheel"},
                                              {"version": "3.14.0", "status": "COMPATIBLE", "exit_code": 0}]},
        "private_backup_files": ["codex-config.toml", "codex-AGENTS.md"],
        "code_update": {"repository": "Namdev90/openai-edge-workbench", "commit": "c" * 40, "state": "verified", "utc": "2026-10-10T09:00:00Z", "error": ""},
        "coverage": {"classic_app": "Preserved until identity and local data are confirmed"},
        "limitations": ["Desktop UI and cloud OAuth require signed-in checks", "Transport is not a protocol feature test"],
    }


class Context:
    root = Path("/must-not-be-opened")

    def __init__(self, report=None, snapshot=None, history=None):
        self.report = fixture() if report is None else report
        self.current = {"run_id": self.report.get("run_id"), "plan": [{"id": "node"}, {"id": "science"}, {"id": "dotnet"}],
                        "options": {"science": True, "dotnet": True}} if snapshot is None else snapshot
        self.past = [{"report": self.report, "run_id": self.report.get("run_id")}] if history is None else history

    def latest_report(self):
        return self.report

    def snapshot(self):
        return self.current

    def history(self):
        return self.past


class ReportFeatureTests(unittest.TestCase):
    def result(self, key, report=None, **kw):
        return features.run(key, Context(report, **kw), {})

    def test_exact_distinct_catalog(self):
        self.assertEqual([item["id"] for item in features.FEATURES], ["f%03d" % i for i in range(31, 66)])
        self.assertEqual(len({item["title"] for item in features.FEATURES}), 35)
        for item in features.FEATURES:
            self.assertEqual(set(item), {"id", "title", "description", "category", "effect"})
            self.assertEqual(item["category"], "Reports")
            self.assertEqual(item["effect"], "read-only")

    def test_every_capability_handles_representative_and_empty_reports(self):
        for report in (fixture(), {}):
            for item in features.FEATURES:
                with self.subTest(id=item["id"], empty=not report):
                    result = self.result(item["id"], report)
                    self.assertIsInstance(result["summary"], str)
                    json.dumps(result, allow_nan=False)
                    if not report:
                        self.assertIn("No completed", result["warnings"][0])

    def test_analyses_are_distinct_not_aliases(self):
        report = fixture()
        previous = copy.deepcopy(report)
        previous["run_id"] = "old"
        previous["results"][1]["status"] = "VERIFIED"
        previous["managed_tools"]["npm"]["version"] = "12.1.0"
        history = [{"report": report}, {"report": previous}]
        outputs = [json.dumps(self.result(item["id"], report, history=history)["data"], sort_keys=True) for item in features.FEATURES]
        self.assertEqual(len(set(outputs)), 35)

    def test_all_features_are_pure_and_do_not_read_environment_or_files(self):
        report = fixture()
        before = copy.deepcopy(report)
        with mock.patch("builtins.open", side_effect=AssertionError("file access")), \
             mock.patch("os.getenv", side_effect=AssertionError("environment access")), \
             mock.patch("subprocess.run", side_effect=AssertionError("process")), \
             mock.patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            for item in features.FEATURES:
                self.result(item["id"], report)
        self.assertEqual(report, before)

    def test_unknown_id_rejected_before_context_access(self):
        for unknown in ("f999", None, [], 31):
            with self.subTest(unknown=unknown), self.assertRaises(ValueError):
                features.run(unknown, None, {})

    def test_status_overview_does_not_trust_saved_totals(self):
        report = fixture()
        report["totals"] = {"VERIFIED": 999}
        data = self.result("f031", report)["data"]
        self.assertEqual(data["counts"]["VERIFIED"], 2)
        self.assertEqual(data["unresolved_steps"], 3)

    def test_failure_triage_and_review_are_different(self):
        failure = self.result("f032")["data"]["failed_steps"]
        review = self.result("f033")["data"]["review_queue"]
        self.assertEqual([item["id"] for item in failure], ["terminal"])
        self.assertEqual(failure[0]["classification"], "transport-timeout")
        self.assertEqual([item["id"] for item in review], ["migrate"])

    def test_structured_doctor_warnings_survive_exit_zero(self):
        data = self.result("f034")["data"]
        self.assertEqual(data["format"], "structured")
        self.assertEqual(len(data["observations"]), 2)
        self.assertEqual(data["exit_code"], 0)
        self.assertEqual(data["observations"][0]["details"]["issue"], "Key not configured")

    def test_legacy_doctor_tail_never_establishes_warning_count(self):
        report = fixture()
        report["checks"]["codex_doctor"] = {"exit_code": 0, "output_tail": "100 ok; all tests passed"}
        result = self.result("f034", report)
        self.assertIsNone(result["data"]["warning_count"])
        self.assertTrue(result["warnings"])

    def test_transport_401_is_not_service_access(self):
        api = self.result("f035")["data"]["endpoints"][0]
        self.assertTrue(api["transport_reached"])
        self.assertEqual(api["recorded_http_status"], 401)
        self.assertFalse(api["service_verified"])

    def test_sign_in_does_not_promote_shared_account_or_entitlements(self):
        data = self.result("f036")["data"]
        self.assertTrue(data["codex"]["sign_in_confirmed"])
        self.assertEqual(data["codex"]["same_account_across_apps"], "NOT_VERIFIED")
        self.assertFalse(data["entitlements_verified"])

    def test_python_choice_explains_rejected_newer_wheels(self):
        data = self.result("f037")["data"]
        self.assertEqual(data["selected_version"], "3.14.0")
        self.assertEqual(data["newest_catalog_version"], "3.15.0a1")
        self.assertEqual(data["attempts"][0]["status"], "INCOMPATIBLE")
        report = fixture()
        report["python_compatibility"]["attempts"][0]["status"] = "PREFLIGHT_ERROR"
        self.assertIn("cannot justify", self.result("f037", report)["warnings"][0])

    def test_npm_host_is_explicit_and_missing_diagnostics_not_clean(self):
        data = self.result("f038")["data"]
        self.assertEqual(data["node_version"], "v27.0.0-nightly20261008")
        self.assertEqual(data["npm_host_version"], "v26.11.1")
        self.assertTrue(data["clean_execution_recorded"])
        report = fixture()
        del report["managed_tools"]["npm"]["diagnostics"]
        self.assertFalse(self.result("f038", report)["data"]["clean_execution_recorded"])

    def test_development_markers_do_not_invent_stable_channel(self):
        tools = {item["tool"]: item for item in self.result("f039")["data"]["tools"]}
        self.assertIn("nightly", tools["node"]["development_markers"])
        self.assertEqual(tools["npm"]["development_markers"], [])
        self.assertIn("cannot be inferred", tools["npm"]["channel_evidence"])

    def test_selections_are_attributed_only_to_matching_run(self):
        data = self.result("f040")["data"]
        self.assertEqual(data["planned_steps_missing_results"], [{"id": "dotnet", "name": ""}])
        other = {"run_id": "future", "options": {"science": False}, "plan": [{"id": "imaginary"}]}
        result = self.result("f040", snapshot=other)
        self.assertEqual(result["data"]["selected_options"], {})
        self.assertTrue(result["warnings"])

    def test_timeline_and_bottlenecks_do_not_replace_missing_time_with_zero(self):
        timeline = self.result("f041")["data"]
        self.assertEqual(timeline["run_duration_seconds"], 600)
        self.assertEqual(timeline["steps_without_valid_duration"], 4)
        bottleneck = self.result("f042")["data"]
        self.assertEqual(bottleneck["ranked_steps"][0]["id"], "terminal")
        self.assertEqual(bottleneck["ranked_steps"][0]["duration_seconds"], 480)
        self.assertEqual(bottleneck["untimed_steps"], 4)

    def test_naive_reversed_and_malformed_timestamps_remain_unknown(self):
        report = fixture()
        for value in ("wrong", "2026-10-10T10:30:00", "2026-10-10T11:00:00Z"):
            report["results"][0]["started_utc"] = value
            self.assertIsNone(self.result("f041", report)["data"]["steps"][0]["duration_seconds"])

    def test_nonzero_probe_is_not_new_failure(self):
        report = fixture()
        report["results"][0]["commands"].append({"label": "Optional discovery", "exit_code": 1})
        data = self.result("f043", report)["data"]
        self.assertEqual(len(data["nonzero_commands"]), 2)
        self.assertEqual(data["nonzero_commands"][0]["step_status"], "VERIFIED")
        self.assertEqual(len(self.result("f032", report)["data"]["failed_steps"]), 1)

    def test_timeout_retry_evidence_requires_explicit_flag(self):
        report = fixture()
        report["results"][0]["commands"].append({"label": "Contains word timeout", "exit_code": 0, "tail": "timeout setting 30"})
        data = self.result("f044", report)["data"]
        self.assertEqual(len(data["timeouts"]), 1)
        self.assertEqual(len(data["retries"]), 1)
        self.assertEqual(data["retry_actions_performed_by_analysis"], 0)

    def test_recovery_classifiers_never_authorize_retry(self):
        report = fixture()
        phrases = ["Checksum mismatch", "Missing compatible wheel", "unowned target path", "Authentication 401", "No published catalog entry", "Something unexpected"]
        report["results"] = [{"id": str(i), "status": "FAILED", "detail": phrase} for i, phrase in enumerate(phrases)]
        items = self.result("f045", report)["data"]["items"]
        self.assertEqual([item["classification"] for item in items], ["integrity-or-signature", "compatibility", "ownership-or-path", "authentication-or-permission", "availability-or-catalog", "needs-evidence-review"])
        self.assertTrue(all(item["retry_authorized"] is False for item in items))

    def test_update_provenance_not_new_verification(self):
        data = self.result("f046")["data"]
        self.assertTrue(data["full_commit_recorded"])
        self.assertFalse(data["signature_rechecked_by_analysis"])
        report = fixture()
        report["code_update"]["commit"] = "main"
        self.assertFalse(self.result("f046", report)["data"]["full_commit_recorded"])

    def test_version_manifest_never_exports_commands_or_package_path(self):
        text = json.dumps(self.result("f047"))
        self.assertNotIn("C:/private", text)
        self.assertNotIn("command", self.result("f047")["data"]["tools"][0])
        data = self.result("f048")["data"]
        self.assertEqual(data["steps"][1]["source"], "winget")

    def test_migration_conflicts_and_coverage_preserve_limits(self):
        conflict = self.result("f049")["data"]
        self.assertEqual(conflict["preserved_conflicts"], ["settings.json"])
        self.assertFalse(conflict["overwrite_implied"])
        coverage = self.result("f050")["data"]
        self.assertEqual(coverage["copied_count"], 1)
        self.assertFalse(coverage["all_profiles_migrated"])
        self.assertFalse(coverage["logins_migrated"])
        self.assertEqual(len(self.result("f051")["data"]["retained_originals"]), 2)

    def test_backup_and_cleanup_summary_never_claim_current_ownership_or_restorability(self):
        backup = self.result("f052")["data"]
        self.assertEqual(backup["backup_file_count"], 2)
        self.assertEqual(backup["recorded_recovery_summaries"][0]["step_id"], "terminal")
        self.assertFalse(backup["backup_contents_opened"])
        self.assertFalse(backup["restoration_tested_by_analysis"])
        cleanup = self.result("f053")["data"]
        self.assertEqual(cleanup["removed_generations"], ["node/old"])
        self.assertFalse(cleanup["ownership_rechecked_by_analysis"])

    def test_model_quota_scope_and_provider_identity_remain_separate(self):
        live = self.result("f054")["data"]
        self.assertEqual(live["live_test_state"], "RECORDED_PASS")
        self.assertTrue(live["quota_consumed_or_attempted"])
        self.assertEqual(live["requests_made_by_analysis"], 0)
        routing = self.result("f055")["data"]
        self.assertTrue(routing["local_listener"]["listening"])
        self.assertEqual(routing["local_listener"]["service_identity"], "NOT_VERIFIED")
        self.assertFalse(routing["environment_values_exported"])

    def test_mcp_configuration_not_functional_proof(self):
        data = self.result("f056")["data"]
        self.assertEqual(data["untested_count"], 2)
        self.assertEqual(data["enabled_missing_local_command"], ["optional"])
        self.assertEqual(data["actions_tested_by_analysis"], 0)

    def test_boundaries_do_not_certify_ui_from_live_request(self):
        data = self.result("f057")["data"]
        self.assertEqual(data["codex_model_request"], "RECORDED_PASS")
        self.assertEqual(data["desktop_ui"], "NOT_VERIFIED_BY_REPORT_ANALYSIS")

    def test_selected_history_comparison_uses_previous_not_future_or_simulation(self):
        report = fixture()
        older = copy.deepcopy(report)
        older["run_id"] = "old"
        older["results"][1]["status"] = "VERIFIED"
        older["managed_tools"]["npm"]["version"] = "12.1.0"
        future = copy.deepcopy(report)
        future["run_id"] = "future"
        simulated = copy.deepcopy(older)
        simulated.update(run_id="simulation", simulated=True)
        history = [{"report": item} for item in (future, report, simulated, older)]
        drift = self.result("f058", report, history=history)["data"]
        self.assertEqual(drift["previous_run_id"], "old")
        self.assertEqual(drift["changes"], [{"id": "terminal", "before": "VERIFIED", "after": "FAILED"}])
        version = self.result("f059", report, history=history)["data"]
        self.assertEqual(version["changes"][0]["tool"], "npm")
        self.assertEqual(version["changes"][0]["before"]["version"], "12.1.0")

    def test_missing_second_real_report_is_not_invented_drift(self):
        for key in ("f058", "f059"):
            result = self.result(key)
            self.assertEqual(result["data"]["changes"], [])
            self.assertTrue(result["warnings"])

    def test_recurring_problems_count_once_per_run_and_exclude_simulations_exports(self):
        report = fixture()
        old = copy.deepcopy(report)
        old["run_id"] = "old"
        old["results"].append(copy.deepcopy(old["results"][1]))
        simulated = copy.deepcopy(report)
        simulated.update(run_id="simulation", simulated=True)
        export = copy.deepcopy(report)
        export.update(run_id="export", feature_export=True)
        history = [{"report": item} for item in (report, old, simulated, export)]
        problems = self.result("f060", report, history=history)["data"]["recurring_steps"]
        self.assertTrue(all(item["run_count"] == 2 for item in problems))
        self.assertEqual(len(problems), 3)
        trend = self.result("f061", report, history=history)["data"]
        self.assertEqual(trend["real_run_count"], 2)
        self.assertEqual(trend["simulated_run_count"], 1)
        self.assertEqual(trend["runs"][2]["counts"], {"SIMULATED": 6})

    def test_verification_matrix_evidence_presence_is_not_success(self):
        matrix = self.result("f062")["data"]
        terminal = matrix["steps"][1]
        self.assertTrue(terminal["command_observations"])
        self.assertEqual(terminal["status"], "FAILED")
        self.assertFalse(matrix["analysis_performed_new_checks"])

    def test_stopped_impact_does_not_claim_rollback(self):
        report = fixture()
        report["stopped"] = True
        data = self.result("f063", report)["data"]
        self.assertEqual([item["id"] for item in data["interrupted_or_unexecuted_steps"]], ["science"])
        self.assertFalse(data["automatic_rollback_verified"])

    def test_catalog_unknown_version_not_equal_latest_and_mismatch_visible(self):
        items = self.result("f064")["data"]["applications"]
        self.assertFalse(items[0]["exact_recorded_match"])
        self.assertIsNone(items[1]["exact_recorded_match"])
        self.assertTrue(all(item["upstream_latestness_verified_by_analysis"] is False for item in items))

    def test_readiness_never_all_capabilities_from_installed_or_imported(self):
        data = self.result("f065")["data"]
        self.assertEqual(data["checks"]["sdk_imports"], "RECORDED_PASS")
        self.assertEqual(data["checks"]["installation_failures"], 1)
        self.assertFalse(data["all_capabilities_verified"])

    def test_simulations_never_promoted_to_installed_or_authenticated(self):
        report = fixture()
        report["simulated"] = True
        self.assertEqual(self.result("f031", report)["data"]["counts"], {"SIMULATED": 6})
        self.assertEqual(self.result("f032", report)["data"]["failed_steps"], [])
        self.assertFalse(self.result("f036", report)["data"]["codex"]["sign_in_confirmed"])
        self.assertFalse(self.result("f038", report)["data"]["clean_execution_recorded"])
        self.assertEqual(self.result("f054", report)["data"]["live_test_state"], "SIMULATED")
        self.assertEqual(self.result("f056", report)["data"]["servers"][0]["functional_status"], "SIMULATED")
        self.assertFalse(self.result("f065", report)["data"]["report_is_completed_real_run"])
        self.assertTrue(self.result("f065", report)["warnings"])

    def test_incomplete_or_unmarked_report_successes_unconfirmed(self):
        for missing in ("final", "simulated"):
            report = fixture()
            del report[missing]
            self.assertEqual(self.result("f031", report)["data"]["counts"]["UNCONFIRMED"], 2)
            self.assertEqual(self.result("f054", report)["data"]["live_test_state"], "INCOMPLETE_OR_UNCONFIRMED_REPORT")
            self.assertFalse(self.result("f038", report)["data"]["clean_execution_recorded"])
            self.assertEqual(self.result("f056", report)["data"]["servers"][0]["functional_status"], "UNCONFIRMED")

    def test_unexpected_secret_fields_and_legacy_tokens_redacted(self):
        report = fixture()
        report["checks"]["codex_doctor"]["non_ok_checks"][0]["details"] = {
            "credential": "TOP_SECRET_DO_NOT_EXPORT", "env": {"PATH": "PRIVATE_ENV_VALUE"},
            "message": "Bearer abcdefghijklmnop ghp_123456789012 password=private-password authorization=BasicSecret"}
        text = json.dumps(self.result("f034", report))
        for secret in ("TOP_SECRET_DO_NOT_EXPORT", "PRIVATE_ENV_VALUE", "abcdefghijklmnop", "123456789012", "private-password", "BasicSecret"):
            self.assertNotIn(secret, text)
        self.assertIn("REDACTED", text)

    def test_malformed_sections_do_not_crash_or_create_evidence(self):
        report = {"final": True, "simulated": False, "checks": ["bad"], "results": [None, 7, "not a row"],
                  "managed_tools": {"node": None}, "migrations": "bad", "limitations": None}
        for item in features.FEATURES:
            with self.subTest(item=item["id"]):
                json.dumps(self.result(item["id"], report))


if __name__ == "__main__":
    unittest.main()
