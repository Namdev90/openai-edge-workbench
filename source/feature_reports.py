"""Thirty-five evidence-only analyses of already redacted Workbench reports.

The context supplies decoded reports. This module never opens a file, reads an
environment variable, runs a command, repairs a setting, or contacts a service.
Passing an installation check is deliberately separate from a product working.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import re


_CATALOG = (
    ("f031", "Installation outcome overview", "Count recorded outcomes, report completion, and unresolved installation states."),
    ("f032", "Failed-step triage", "Identify failed steps, their command evidence, and the next review needed."),
    ("f033", "Review-needed queue", "Collect steps requiring channel, version, or manual verification."),
    ("f034", "Codex doctor observations", "Separate structured doctor warnings from limited older text diagnostics."),
    ("f035", "Transport and service access", "Distinguish reachable endpoints from authenticated or protocol-level service access."),
    ("f036", "Sign-in evidence scope", "Explain what recorded CLI sign-in establishes and what account identity remains unverified."),
    ("f037", "Python compatibility decision", "Explain resolver attempts, wheel availability, selected Python, and operational errors."),
    ("f038", "npm host compatibility", "Show the package-manager host alongside the nightly runtime and recorded npm diagnostics."),
    ("f039", "Development-channel inventory", "Identify recorded nightly, alpha, beta, RC, preview, and catalog-only channels."),
    ("f040", "Selected and skipped scope", "Reconcile selected plan steps with recorded results without assuming missing tools installed."),
    ("f041", "Installation timeline", "Calculate valid step durations and identify missing or inconsistent timestamps."),
    ("f042", "Installation bottlenecks", "Rank timed steps and identify the measured share of recorded installation time."),
    ("f043", "Command exit-code audit", "Group successful and unsuccessful command observations without treating every nonzero probe as an installation failure."),
    ("f044", "Timeout and retry evidence", "List explicit command timeouts and recorded retry attempts."),
    ("f045", "Failure recovery classification", "Classify failure evidence for review while refusing an automatic or speculative retry."),
    ("f046", "Application update provenance", "Inspect recorded repository, commit, update state, and errors without asserting a new signature check."),
    ("f047", "Active version manifest", "Summarize recorded managed tool and package versions without exposing launch commands."),
    ("f048", "Package source provenance", "List catalog and package sources and distinguish source records from integrity evidence."),
    ("f049", "Migration conflict review", "List preserved editor conflicts and failed extension migrations."),
    ("f050", "Migration coverage assessment", "Describe copied editor files and extension coverage without claiming all profiles migrated."),
    ("f051", "Retained original applications", "Explain explicitly recorded preserved applications, configurations, and runtimes."),
    ("f052", "Backup evidence summary", "List backup filenames and recorded recovery evidence without opening private backups."),
    ("f053", "Managed cleanup evidence", "Summarize removed and retained generations and the recorded cleanup ownership policy."),
    ("f054", "Live model and quota scope", "Report exact live-test evidence and quota attempt scope without making another request."),
    ("f055", "Provider and environment routing", "Explain recorded provider, local listener, configuration parsing, and PATH observations."),
    ("f056", "MCP functional coverage", "Identify enabled server records, missing local commands, and untested protocol actions."),
    ("f057", "Verification boundary audit", "Collect explicit limitations and distinguish binary, SDK, transport, account, and UI coverage."),
    ("f058", "Installation status drift", "Compare the selected run with the previous completed real run to find changed step outcomes."),
    ("f059", "Managed version drift", "Compare recorded tool and package versions across two completed real runs."),
    ("f060", "Recurring installation problems", "Count repeated unresolved step outcomes across completed real reports."),
    ("f061", "Run outcome history", "Show historical success and review counts with simulated runs separately labeled."),
    ("f062", "Verification evidence matrix", "Map step outcomes to command, version, registration, and signature observations."),
    ("f063", "Stopped-run impact", "Show interrupted and unexecuted steps without assuming a rollback or a fully installed state."),
    ("f064", "Catalog and installed reconciliation", "Compare requested catalog versions with observed installed versions and explain latestness limits."),
    ("f065", "Readiness evidence checklist", "Present installation, SDK, sign-in, transport, routing, model, and MCP readiness separately."),
)

FEATURES = [dict(id=key, title=title, description=description,
                 category="Reports", effect="read-only") for key, title, description in _CATALOG]
_IDS = {item["id"] for item in FEATURES}
_UNRESOLVED = {"FAILED", "STOPPED", "NOT_RUN", "NOT_AVAILABLE", "REVIEW_NEEDED",
               "VERSION_MISMATCH", "CHANNEL_NOT_VERIFIED", "INSTALLED_CHECK_NEEDED"}
_REVIEW = _UNRESOLVED - {"FAILED", "STOPPED", "NOT_RUN"}
_SECRET_KEY = re.compile(r"(?i)(?:password|credential|cookie|authorization|api.?key|access.?token|refresh.?token|secret|^env$|^environment$|^headers$)")
_TOKEN = re.compile(r"(?i)(?:\b(?:Bearer|Basic)\s+\S+|\b(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,})|\b(?:password|credential|cookie|authorization|token|api[_-]?key|secret)\s*[=:]\s*[^\s,;]+)")


def _d(value):
    return value if isinstance(value, dict) else {}


def _l(value):
    return value if isinstance(value, list) else []


def _text(value, limit=8000):
    if value is None:
        return ""
    return _TOKEN.sub("[REDACTED]", str(value).replace("\x00", ""))[:limit]


def _safe(value):
    """Defense in depth for caller-supplied historical and legacy report text."""
    if isinstance(value, dict):
        return {_text(k): _safe(v) for k, v in value.items() if not _SECRET_KEY.search(str(k))}
    if isinstance(value, list):
        return [_safe(v) for v in value]
    if isinstance(value, str):
        return _text(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _text(value)


def _is_real(report):
    return report.get("simulated") is False and report.get("final") is True


def _status(report, row):
    status = _text(row.get("status", "UNKNOWN"), 80).upper()
    if report.get("simulated") is True or status == "SIMULATED":
        return "SIMULATED"
    if status == "VERIFIED" and not _is_real(report):
        return "UNCONFIRMED"
    return status


def _rows(report):
    return [row for row in _l(report.get("results")) if isinstance(row, dict)]


def _row(report, key):
    return next((row for row in _rows(report) if row.get("id") == key), {})


def _brief(report, row):
    return {"id": _text(row.get("id", "unknown")), "name": _text(row.get("name", "")),
            "status": _status(report, row), "detail": _text(row.get("detail", ""))}


def _check_state(report, check):
    if report.get("simulated") is True:
        return "SIMULATED"
    if not _is_real(report):
        return "INCOMPLETE_OR_UNCONFIRMED_REPORT"
    if check.get("passed") is True:
        return "RECORDED_PASS"
    if check.get("passed") is False:
        return "RECORDED_FAILURE"
    return "NOT_TESTED"


def _commands(report):
    output = []
    for row in _rows(report):
        for command in _l(row.get("commands")):
            if isinstance(command, dict):
                output.append({"step_id": _text(row.get("id", "unknown")),
                               "step_status": _status(report, row),
                               **{key: command[key] for key in ("label", "exit_code", "timed_out", "tail") if key in command}})
    return output


def _history(ctx):
    history = []
    for entry in _l(ctx.history()):
        if not isinstance(entry, dict):
            continue
        report = _d(entry.get("report", entry))
        if report.get("final") is not True or report.get("feature_export") or report.get("kind") == "feature-export":
            continue
        history.append(report)
    return history


def _previous(report, ctx):
    """A report picker must never compare an older selected run with a future run."""
    history = _history(ctx)
    index = next((i for i, item in enumerate(history) if item.get("run_id") == report.get("run_id")), None)
    if index is not None:
        older = history[index + 1:]
    else:
        selected_time = _instant(report.get("finished_utc"))
        older = [item for item in history if selected_time is not None
                 and _instant(item.get("finished_utc")) is not None
                 and _instant(item.get("finished_utc")) < selected_time]
    return next((item for item in older if _is_real(item)), {})


def _instant(value):
    try:
        time = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        # Naive timestamps cannot safely be compared with UTC report timestamps.
        return time if time.tzinfo is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def _duration(start, finish):
    a, b = _instant(start), _instant(finish)
    if a is None or b is None:
        return None
    seconds = (b - a).total_seconds()
    return round(seconds, 3) if seconds >= 0 else None


def _timeline(report):
    return [{**_brief(report, row), "started_utc": _text(row.get("started_utc")),
             "finished_utc": _text(row.get("finished_utc")),
             "duration_seconds": _duration(row.get("started_utc"), row.get("finished_utc"))}
            for row in _rows(report)]


def _manifest(report):
    tools = []
    for name, raw in _d(report.get("managed_tools")).items():
        tool = _d(raw)
        tools.append({"tool": _text(name), "version": _text(tool.get("version", "unknown")),
                      "packages": {k: _text(v) for k, v in _d(tool.get("versions")).items()},
                      "source": _text(tool.get("source", "")),
                      "host_version": _text(tool.get("host_version", "")),
                      "evidence": "SIMULATED" if report.get("simulated") is True else "Recorded active state; independent execution not implied"})
    return sorted(tools, key=lambda item: item["tool"])


def _classify(text):
    """Suggestions classify observations, never authorize a repair or retry."""
    lowered = text.lower()
    if re.search(r"timed?\s*out|timeout|0x80072ee2", lowered):
        return "transport-timeout", "Review connectivity and the recorded timeout before choosing a retry."
    if re.search(r"auth|sign.in|entitlement|permission denied|unauthorized|forbidden|\b401\b|\b403\b", lowered):
        return "authentication-or-permission", "Review sign-in or access using the application's normal account flow."
    if re.search(r"signature|sha.?256|checksum|integrity|hash mismatch", lowered):
        return "integrity-or-signature", "Preserve the failed artifact and inspect official source and integrity evidence before execution."
    if re.search(r"wheel|incompatible|compatibility|requires.*python|engines|unsupported", lowered):
        return "compatibility", "Review the exact resolver or declared runtime constraint; newest is constrained by compatibility."
    if re.search(r"junction|symlink|unowned|escaped|reparse", lowered):
        return "ownership-or-path", "Review ownership and the target path; do not delete or overwrite the existing destination."
    if re.search(r"not found|not available|not advertised|no published|no identifiable|catalog", lowered):
        return "availability-or-catalog", "Review the official channel and catalog evidence; no replacement channel is implied."
    return "needs-evidence-review", "Inspect the failing step and command observations before choosing an action."


def run(feature_id, ctx, payload):
    """Analyze one selected report. Payload is reserved for the service's run picker."""
    if not isinstance(feature_id, str) or feature_id not in _IDS:
        raise ValueError("Unknown report feature: " + _text(feature_id, 100))
    report = _d(ctx.latest_report())
    checks, migrations = _d(report.get("checks")), _d(report.get("migrations"))
    warnings = []
    if not report:
        warnings.append("No completed installation report is available; empty evidence is not success.")
    elif report.get("simulated") is True:
        warnings.append("This is a simulated report. Its outcomes are not evidence about the installed computer.")
    elif not _is_real(report):
        warnings.append("The report is incomplete or lacks an explicit real-run marker; successes remain unconfirmed.")
    rows = _rows(report)
    summary, data = _analyze(feature_id, ctx, report, checks, migrations, rows, warnings)
    result = {"summary": summary, "data": _safe(data)}
    if warnings:
        result["warnings"] = [_text(message) for message in warnings]
    return result


def _analyze(feature_id, ctx, report, checks, migrations, rows, warnings):
    if feature_id == "f031":
        counts = Counter(_status(report, row) for row in rows)
        unresolved = sum(counts[status] for status in _UNRESOLVED)
        return "Recorded installation outcomes: %d steps; %d unresolved outcomes." % (len(rows), unresolved), {
            "run_id": report.get("run_id", ""), "completed_report": report.get("final") is True,
            "simulated": report.get("simulated") is True, "counts": dict(counts),
            "unresolved_steps": unresolved, "fatal_error": report.get("fatal_error", ""),
            "report_error": report.get("report_error", ""),
            "scope": "Counts describe recorded steps, not every application feature or connector."}
    if feature_id == "f032":
        failed = []
        for row in rows:
            if _status(report, row) != "FAILED":
                continue
            commands = [command for command in _commands({**report, "results": [row]})
                        if command.get("exit_code") not in (0, None) or command.get("timed_out") is True]
            kind, review = _classify(_text(row.get("detail", "")) + " " + " ".join(_text(c.get("tail", "")) for c in commands))
            failed.append({**_brief(report, row), "classification": kind, "next_review": review,
                           "unsuccessful_commands": commands})
        return "%d recorded installation failures require review." % len(failed), {"failed_steps": failed, "fatal_error": report.get("fatal_error", "")}
    if feature_id == "f033":
        queue = [_brief(report, row) for row in rows if _status(report, row) in _REVIEW]
        return "%d recorded steps need additional review or verification." % len(queue), {"review_queue": queue, "policy": "A review-needed outcome is not silently converted to a failure or success."}
    if feature_id == "f034":
        doctor = _d(checks.get("codex_doctor"))
        if isinstance(doctor.get("non_ok_checks"), list):
            observations = [{key: row[key] for key in ("id", "status", "category", "summary", "details", "remediation", "issues") if key in row}
                            for row in doctor["non_ok_checks"] if isinstance(row, dict)]
            return "%d structured Codex doctor observations recorded." % len(observations), {
                "format": "structured", "observations": observations, "counts": _d(doctor.get("counts")),
                "overall_status": doctor.get("overall_status", "unknown"), "exit_code": doctor.get("exit_code"),
                "evidence": "SIMULATED" if report.get("simulated") is True else "Recorded doctor output", "scope": doctor.get("scope", "No repairs inferred.")}
        warnings.append("Structured doctor observations are absent. A text tail cannot establish warning counts or a clean doctor result.")
        return "Codex doctor coverage is limited to the recorded availability or legacy text.", {
            "format": "legacy-text-or-unavailable", "state": doctor.get("state", "Not recorded"),
            "exit_code": doctor.get("exit_code"), "text_tail": doctor.get("output_tail", ""), "warning_count": None}
    if feature_id == "f035":
        endpoints = []
        for name, raw in _d(checks.get("network")).items():
            endpoint = _d(raw)
            endpoints.append({"endpoint": name, "transport_reached": endpoint.get("transport_reached") if _is_real(report) else None,
                              "recorded_http_status": endpoint.get("http_status"),
                              "service_verified": endpoint.get("auth_or_protocol_verified") is True and _is_real(report),
                              "detail": endpoint.get("detail", "")})
        return "Transport reachability and authenticated service access are separate observations.", {"endpoints": endpoints, "scope": "HTTP 401/403 may prove transport; they do not prove successful service use."}
    if feature_id == "f036":
        codex, github = _d(checks.get("codex_sign_in")), _d(checks.get("github_sign_in"))
        return "Recorded CLI sign-in does not establish shared desktop identity or every cloud entitlement.", {
            "codex": {"recorded_state": codex.get("state", "Not recorded"), "exit_code": codex.get("exit_code"),
                      "sign_in_confirmed": codex.get("exit_code") == 0 and _is_real(report),
                      "same_account_across_apps": "NOT_VERIFIED"},
            "github": {"configured": github.get("configured") if _is_real(report) else None,
                       "note": github.get("note", "Not recorded")},
            "account_identity_exported": False, "entitlements_verified": False}
    if feature_id == "f037":
        compatibility = _d(report.get("python_compatibility"))
        attempts = [{key: attempt[key] for key in ("version", "status", "exit_code", "reason") if key in attempt}
                    for attempt in _l(compatibility.get("attempts")) if isinstance(attempt, dict)]
        errors = [attempt for attempt in attempts if attempt.get("status") == "PREFLIGHT_ERROR"]
        if errors:
            warnings.append("An operational preflight error cannot justify choosing an older Python version.")
        return "Python selection follows complete selected-pack wheel resolution before installation.", {
            "selected_version": compatibility.get("selected_version", "Not recorded"),
            "newest_catalog_version": compatibility.get("newest_catalog_version", "Not recorded"),
            "selection_reason": compatibility.get("selection_reason", "Not recorded"),
            "target": compatibility.get("target", ""), "packages": _l(compatibility.get("packages")),
            "requirements_sha256": compatibility.get("requirements_sha256", ""), "attempts": attempts,
            "resolved_package_count": len(_d(compatibility.get("resolved_versions"))),
            "scope": "A resolver solution is compatibility evidence; package APIs require their own tests."}
    if feature_id == "f038":
        tools = _d(report.get("managed_tools"))
        node, npm, row = _d(tools.get("node")), _d(tools.get("npm")), _row(report, "node")
        diagnostics = _l(npm.get("diagnostics"))
        clean_observed = _is_real(report) and _status(report, row) == "VERIFIED" and npm.get("diagnostics") == [] and bool(npm.get("host_version"))
        return "The nightly tool runtime and npm's compatible package-manager host are independently recorded.", {
            "node_version": node.get("version", row.get("actual", "Not recorded")),
            "npm_version": npm.get("version", row.get("npm_version", "Not recorded")),
            "npm_host_version": npm.get("host_version", row.get("npm_host_version", "Not recorded")),
            "declared_node_engines": npm.get("engines", row.get("npm_engines", "Not recorded")),
            "nightly_accepted_by_npm": row.get("nightly_accepted_by_npm"), "diagnostics": diagnostics,
            "clean_execution_recorded": clean_observed, "scope": "Missing diagnostics fields are not proof of a warning-free execution."}
    if feature_id == "f039":
        inventory = []
        for tool in _manifest(report):
            version = tool["version"].lower()
            markers = [word for word in ("nightly", "alpha", "beta", "preview", "canary") if word in version or word in tool["source"].lower()]
            if re.search(r"(?:^|[.\-])rc(?:[.\d\-]|$)", version):
                markers.append("rc")
            inventory.append({"tool": tool["tool"], "version": tool["version"], "development_markers": markers,
                              "channel_evidence": "Recorded version/source markers" if markers else "No explicit development marker; stable or catalog-only cannot be inferred"})
        return "Development channels are identified from recorded versions and source descriptions.", {"tools": inventory, "catalog_channels": [{"id": row.get("id"), "channel": row.get("channel"), "status": _status(report, row)} for row in rows if row.get("channel")]}
    if feature_id == "f040":
        snapshot = _d(ctx.snapshot())
        same_run = snapshot.get("run_id") == report.get("run_id") and bool(report.get("run_id"))
        plan = [item for item in _l(snapshot.get("plan")) if isinstance(item, dict)] if same_run else []
        ids = {row.get("id") for row in rows}
        if not same_run:
            warnings.append("The current dashboard is a different run; its selections are not attributed to the selected report.")
        return "Only a matching dashboard run can establish selected options absent from historical reports.", {
            "dashboard_matches_report": same_run, "selected_options": _d(snapshot.get("options")) if same_run else {},
            "planned_steps_missing_results": [{"id": item.get("id"), "name": item.get("name", "")} for item in plan if item.get("id") not in ids],
            "unexecuted_steps": [_brief(report, row) for row in rows if _status(report, row) in ("NOT_RUN", "STOPPED")],
            "recorded_step_count": len(rows), "coverage": _d(report.get("coverage"))}
    if feature_id == "f041":
        timeline = _timeline(report)
        missing = sum(item["duration_seconds"] is None for item in timeline)
        return "Step durations are derived only from valid ordered UTC timestamps.", {
            "steps": timeline, "run_duration_seconds": _duration(report.get("started_utc"), report.get("finished_utc")),
            "steps_without_valid_duration": missing, "scope": "Untimed steps are unknown, not zero-duration."}
    if feature_id == "f042":
        timed = [item for item in _timeline(report) if item["duration_seconds"] is not None]
        total = sum(item["duration_seconds"] for item in timed)
        ranked = sorted(timed, key=lambda item: item["duration_seconds"], reverse=True)
        return "Measured bottlenecks describe timed steps only.", {"ranked_steps": [{"id": item["id"], "name": item["name"], "duration_seconds": item["duration_seconds"], "share_of_timed_steps_percent": round(item["duration_seconds"] / total * 100, 2) if total else 0} for item in ranked], "timed_steps_seconds": round(total, 3), "untimed_steps": len(rows) - len(timed)}
    if feature_id == "f043":
        commands = _commands(report)
        nonzero = [command for command in commands if isinstance(command.get("exit_code"), int) and command["exit_code"] != 0]
        return "%d nonzero command observations; installation outcomes remain separate." % len(nonzero), {
            "exit_code_counts": dict(Counter(str(command.get("exit_code", "unknown")) for command in commands)),
            "nonzero_commands": nonzero, "successful_commands": sum(command.get("exit_code") == 0 for command in commands),
            "scope": "Discovery probes and resolver rejection can return nonzero without a failed installation step."}
    if feature_id == "f044":
        timeouts = [command for command in _commands(report) if command.get("timed_out") is True]
        retries = [{"step_id": row.get("id"), **{key: retry[key] for key in ("attempt", "reason", "delay_seconds", "package", "source", "channel") if key in retry}}
                   for row in rows for retry in _l(row.get("retries")) if isinstance(retry, dict)]
        return "%d explicit timeouts and %d recorded retry attempts." % (len(timeouts), len(retries)), {"timeouts": timeouts, "retries": retries, "retry_actions_performed_by_analysis": 0}
    if feature_id == "f045":
        classified = []
        for row in rows:
            if _status(report, row) not in _UNRESOLVED:
                continue
            kind, next_review = _classify(_text(row.get("detail", "")))
            classified.append({**_brief(report, row), "classification": kind, "next_review": next_review, "retry_authorized": False})
        return "Failure categories are review suggestions based on recorded text, not diagnoses or automatic repairs.", {"items": classified}
    if feature_id == "f046":
        update = _d(report.get("code_update"))
        commit = _text(update.get("commit", ""))
        return "Application update provenance is the saved setup observation, not a new remote verification.", {
            **{key: update.get(key, "") for key in ("repository", "commit", "state", "utc", "error")},
            "full_commit_recorded": bool(re.fullmatch(r"[a-fA-F0-9]{40}", commit)),
            "workbench_version": report.get("workbench_version", ""), "signature_rechecked_by_analysis": False}
    if feature_id == "f047":
        manifest = _manifest(report)
        return "%d recorded managed tools; launch paths and credential details are excluded." % len(manifest), {"tools": manifest, "python_resolved_packages": _d(_d(report.get("python_compatibility")).get("resolved_versions"))}
    if feature_id == "f048":
        provenance = []
        for row in rows:
            integrity = _d(row.get("channel_install"))
            provenance.append({"id": row.get("id"), "source": row.get("source", "Not recorded"),
                               "package": row.get("package", ""), "channel": row.get("channel", ""),
                               "integrity_observation": {key: integrity[key] for key in ("source_manifest", "sha256", "signature") if key in integrity},
                               "status": _status(report, row)})
        return "Recorded catalog and registry sources do not independently prove upstream latestness or signatures.", {"steps": provenance, "managed_tool_sources": [{"tool": tool["tool"], "source": tool["source"]} for tool in _manifest(report)]}
    if feature_id == "f049":
        files, extensions = _d(migrations.get("editor_files")), _d(migrations.get("editor_extensions"))
        return "Conflicting editor files were retained for review; extension failures are separately recorded.", {
            "preserved_conflicts": _l(files.get("conflicts")), "failed_extensions": _l(extensions.get("failed")),
            "conflict_count": len(_l(files.get("conflicts"))), "migration_step_status": _status(report, _row(report, "migrate")), "overwrite_implied": False}
    if feature_id == "f050":
        files, extensions = _d(migrations.get("editor_files")), _d(migrations.get("editor_extensions"))
        return "Editor migration covers recorded missing files and default-profile extensions only.", {
            "copied_files": _l(files.get("copied")), "copied_count": len(_l(files.get("copied"))),
            "installed_extensions": _l(extensions.get("installed")), "extension_scope": extensions.get("scope", "Not recorded"),
            "all_profiles_migrated": False, "workspace_dependencies_migrated": False, "logins_migrated": False}
    if feature_id == "f051":
        retained = _l(migrations.get("retained"))
        return "%d explicit preservation notes recorded; absence is not proof of deletion or migration." % len(retained), {"retained_originals": retained, "coverage_notes": _d(report.get("coverage"))}
    if feature_id == "f052":
        backup_names = [name for name in _l(report.get("private_backup_files")) if isinstance(name, str)]
        recoveries = [{"step_id": row.get("id"), **{key: _d(row.get("local_recovery"))[key]
                       for key in ("state", "passed", "detail", "reason", "version", "sha256", "signature", "restore_point_created", "exit_code")
                       if key in _d(row.get("local_recovery"))}}
                      for row in rows if isinstance(row.get("local_recovery"), dict)]
        return "Backup observations list filenames only; contents and current restorability were not inspected.", {
            "recorded_private_backup_filenames": backup_names, "backup_file_count": len(backup_names),
            "recorded_recovery_summaries": recoveries,
            "backup_contents_opened": False, "restoration_tested_by_analysis": False}
    if feature_id == "f053":
        cleanup = _row(report, "cleanup")
        return "Cleanup records cover Workbench-owned generations; this analysis performs no deletions.", {
            "removed_generations": _l(cleanup.get("removed")), "retained_generations": _l(cleanup.get("retained")),
            "status": _status(report, cleanup), "recorded_policy": cleanup.get("detail", "Not recorded"),
            "ownership_rechecked_by_analysis": False}
    if feature_id == "f054":
        live = _d(checks.get("codex_live"))
        return "A live check, when recorded, covers one configured CLI request and can consume quota.", {
            "live_test_state": _check_state(report, live), "exit_code": live.get("exit_code"),
            "quota_consumed_or_attempted": live.get("quota_consumed_or_attempted") if _is_real(report) else None,
            "expected_marker": live.get("expected_marker", "Not recorded"), "scope": live.get("scope", "No live request evidence recorded"),
            "requests_made_by_analysis": 0, "quota_amount_known": False}
    if feature_id == "f055":
        provider, listener, parse, path = (_d(checks.get(key)) for key in ("provider", "active_local_provider", "codex_config_parse", "user_path_update"))
        return "Recorded routing and environment observations are preserved; a listening port is not verified service identity.", {
            "provider_name": provider.get("name", "Not recorded"), "configuration_preserved": provider.get("configuration_preserved"),
            "local_listener": {"recorded_port": listener.get("port"), "listening": listener.get("listening") if _is_real(report) else None, "service_identity": "NOT_VERIFIED"},
            "config_parse": {"state": _check_state(report, parse), "detail": parse.get("detail", "")},
            "user_path_update": {"state": _check_state(report, path), "scope": path.get("scope", "")},
            "restart_note": checks.get("restart_apps", "Not recorded"), "environment_values_exported": False}
    if feature_id == "f056":
        servers = []
        for server in _l(checks.get("mcp_configuration")):
            if isinstance(server, dict):
                servers.append({"name": server.get("name", "unknown"), "enabled": server.get("enabled"),
                                "type": server.get("type", "unknown"), "local_command_located": server.get("command_located"),
                                "functional_status": "SIMULATED" if report.get("simulated") is True else
                                "UNCONFIRMED" if not _is_real(report) else server.get("functional_status", "NOT_TESTED")})
        return "Configured MCP servers are not assumed to have working protocol tools.", {"servers": servers, "untested_count": sum(server["functional_status"] != "VERIFIED" for server in servers), "enabled_missing_local_command": [server["name"] for server in servers if server["enabled"] is True and server["type"] == "local-process" and server["local_command_located"] is False], "actions_tested_by_analysis": 0}
    if feature_id == "f057":
        return "Installation, execution, identity, transport, UI, and cloud feature coverage remain separate.", {
            "explicit_limitations": _l(report.get("limitations")), "coverage_notes": _d(report.get("coverage")),
            "python_sdk_imports": _check_state(report, _d(checks.get("python_sdk_imports"))),
            "codex_binary_version": _check_state(report, _d(checks.get("codex_version"))),
            "codex_model_request": _check_state(report, _d(checks.get("codex_live"))),
            "desktop_ui": "NOT_VERIFIED_BY_REPORT_ANALYSIS", "same_account_identity": "NOT_VERIFIED_BY_REPORT_ANALYSIS", "every_plugin_action": "NOT_VERIFIED_BY_REPORT_ANALYSIS"}
    if feature_id in ("f058", "f059"):
        previous = _previous(report, ctx) if _is_real(report) else {}
        if not previous:
            warnings.append("Two completed real reports in the selected run's history are required for comparison.")
        if feature_id == "f058":
            before = {row.get("id"): _status(previous, row) for row in _rows(previous)}
            after = {row.get("id"): _status(report, row) for row in rows}
            changed = [{"id": key, "before": before.get(key, "NOT_RECORDED"), "after": after.get(key, "NOT_RECORDED")}
                       for key in sorted(set(before) | set(after), key=str) if before.get(key) != after.get(key)] if previous else []
            return "Step outcome changes compare recorded runs, not an independent recheck of the computer.", {"selected_run_id": report.get("run_id", ""), "previous_run_id": previous.get("run_id", ""), "changes": changed}
        before = {tool["tool"]: {"version": tool["version"], "packages": tool["packages"], "host_version": tool["host_version"]} for tool in _manifest(previous)}
        after = {tool["tool"]: {"version": tool["version"], "packages": tool["packages"], "host_version": tool["host_version"]} for tool in _manifest(report)}
        changed = [{"tool": key, "before": before.get(key), "after": after.get(key)} for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)] if previous else []
        return "Managed version drift describes active-state records; version order and upstream latestness are not inferred.", {"selected_run_id": report.get("run_id", ""), "previous_run_id": previous.get("run_id", ""), "changes": changed}
    if feature_id == "f060":
        problems = {}
        for historical in _history(ctx):
            if not _is_real(historical):
                continue
            # One count per step per run, even if a malformed report repeats a row.
            seen = set()
            for row in _rows(historical):
                key = _text(row.get("id", "unknown"))
                if key in seen or _status(historical, row) not in _UNRESOLVED:
                    continue
                seen.add(key)
                item = problems.setdefault(key, {"id": key, "runs": [], "statuses": Counter()})
                item["runs"].append(_text(historical.get("run_id", "")))
                item["statuses"][_status(historical, row)] += 1
        recurring = [{"id": key, "run_count": len(item["runs"]), "runs": item["runs"], "status_counts": dict(item["statuses"])} for key, item in problems.items() if len(item["runs"]) >= 2]
        recurring.sort(key=lambda item: (-item["run_count"], item["id"]))
        return "%d steps have unresolved outcomes in at least two completed real reports." % len(recurring), {"recurring_steps": recurring, "scope": "A repeated identifier is not proof of the same root cause."}
    if feature_id == "f061":
        history = []
        for historical in _history(ctx):
            counts = Counter(_status(historical, row) for row in _rows(historical))
            history.append({"run_id": historical.get("run_id", ""), "version": historical.get("workbench_version", ""), "finished_utc": historical.get("finished_utc", ""), "simulated": historical.get("simulated") is True, "counts": dict(counts), "unresolved_steps": sum(counts[status] for status in _UNRESOLVED)})
        return "Run history keeps simulations explicitly separate from computer evidence.", {"runs": history, "real_run_count": sum(_is_real(item) for item in _history(ctx)), "simulated_run_count": sum(item["simulated"] for item in history)}
    if feature_id == "f062":
        matrix = []
        for row in rows:
            matrix.append({"id": row.get("id"), "status": _status(report, row),
                           "command_observations": len(_l(row.get("commands"))), "expected_version": row.get("expected", "Not recorded"),
                           "actual_version": row.get("actual", "Not recorded"),
                           "registration_observation": bool(row.get("registration_check") or row.get("channel_registration_check")),
                           "signature_observation": bool(_d(row.get("channel_install")).get("signature")),
                           "recorded_detail": row.get("detail", "")})
        return "Evidence presence and the step's recorded outcome are shown separately; presence alone is not a passing test.", {"steps": matrix, "analysis_performed_new_checks": False}
    if feature_id == "f063":
        interrupted = [_brief(report, row) for row in rows if _status(report, row) in ("STOPPED", "NOT_RUN", "RUNNING")]
        return "A stopped or incomplete run may leave completed changes; rollback is not assumed.", {"stopped": report.get("stopped") is True, "report_completed": report.get("final") is True,
            "interrupted_or_unexecuted_steps": interrupted, "previous_active_tools_recorded": [tool["tool"] for tool in _manifest(report)],
            "automatic_rollback_verified": False, "fatal_error": report.get("fatal_error", "")}
    if feature_id == "f064":
        items = []
        for row in rows:
            if row.get("kind") != "winget":
                continue
            expected, actual = _text(row.get("expected", "")), _text(row.get("actual", ""))
            # Only concrete exact strings count as version comparisons.
            concrete = bool(re.fullmatch(r"v?\d+(?:\.[\w+\-]+)+", expected)) and bool(re.fullmatch(r"v?\d+(?:\.[\w+\-]+)+", actual))
            items.append({"id": row.get("id"), "package": row.get("package", ""), "channel": row.get("channel", ""),
                          "expected_catalog_version": expected, "observed_installed_version": actual,
                          "exact_recorded_match": expected == actual if concrete and _is_real(report) else None,
                          "status": _status(report, row), "detail": row.get("detail", ""), "upstream_latestness_verified_by_analysis": False})
        return "A catalog match or no applicable update does not prove the newest unpublished upstream build.", {"applications": items}
    if feature_id == "f065":
        outcomes = Counter(_status(report, row) for row in rows)
        categories = {"installation_failures": outcomes["FAILED"], "installation_reviews": sum(outcomes[status] for status in _REVIEW),
                      "sdk_imports": _check_state(report, _d(checks.get("python_sdk_imports"))),
                      "binary_execution": _check_state(report, _d(checks.get("codex_version"))),
                      "live_model_request": _check_state(report, _d(checks.get("codex_live"))),
                      "same_account_desktop_identity": "NOT_VERIFIED", "desktop_ui": "NOT_VERIFIED",
                      "mcp_protocol_actions": "See per-server functional coverage; configuration is not a protocol test"}
        return "Readiness is a checklist of independent evidence, never a blanket all-features-working claim.", {"checks": categories, "report_is_completed_real_run": _is_real(report), "all_capabilities_verified": False}
    raise AssertionError("Catalog and analysis implementation differ")
