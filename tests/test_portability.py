"""Mechanics checks only: files, installation, and portable artifact commands."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "tools" / "install.py"
SDD = ROOT / "skills" / "subagent-driven-development" / "scripts" / "sdd.py"


def find_bash():
    configured = os.environ.get("SUPERPOWERS_TEST_BASH")
    if configured:
        return configured
    if os.name == "nt":
        git = shutil.which("git")
        candidate = Path(git).parent.parent / "bin" / "bash.exe" if git else None
        return str(candidate) if candidate and candidate.is_file() else None
    return shutil.which("bash")


BASH = find_bash()


def run(*args, cwd=None, env=None):
    return subprocess.run([str(a) for a in args], cwd=cwd, text=True,
                          encoding="utf-8", capture_output=True, env=env, timeout=30)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="superpowers install ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.skills = self.base / "installed skills"
        self.state = self.base / "profile state"
        self.skill = self.source / "skills" / "example" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text("---\nname: example\ndescription: Test skill\n---\nOriginal\n", encoding="utf-8")

    def install(self, *extra):
        return run(sys.executable, INSTALL, "--target", "codex", "--source", self.source,
                   "--skills-dir", self.skills, "--state-dir", self.state, *extra)

    def test_preview_does_not_create_destination_or_state(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.skills.exists())
        self.assertFalse(self.state.exists())

    def test_install_and_repeat_preserve_registry_and_unrelated_skills(self):
        self.assertEqual(self.install("--apply").returncode, 0)
        registry = self.state / "coordinator-registry.md"
        registry.write_text("Local knowledge", encoding="utf-8")
        unrelated = self.skills / "unrelated" / "SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("Personal skill", encoding="utf-8")
        result = self.install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(registry.read_text(), "Local knowledge")
        self.assertEqual(unrelated.read_text(), "Personal skill")
        self.assertEqual((self.skills / "example" / "SKILL.md").read_bytes(), self.skill.read_bytes())
        self.assertIn(str(self.skills), (self.state / "bootstrap.md").read_text(encoding="utf-8"))

    def test_collision_refuses_entire_install_before_writing(self):
        target = self.skills / "example" / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("Personal version", encoding="utf-8")
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "Personal version")
        self.assertFalse(self.state.exists())

    def test_update_refuses_local_edits_and_preserves_manifest(self):
        self.assertEqual(self.install("--apply").returncode, 0)
        manifest = (self.state / "install.json").read_bytes()
        target = self.skills / "example" / "SKILL.md"
        target.write_text("Edited locally", encoding="utf-8")
        self.skill.write_text("New upstream", encoding="utf-8")
        self.assertNotEqual(self.install("--apply").returncode, 0)
        self.assertEqual(target.read_text(), "Edited locally")
        self.assertEqual((self.state / "install.json").read_bytes(), manifest)

    def test_update_changes_owned_files_and_removes_only_owned_stale_files(self):
        old = self.skill.parent / "old.md"
        old.write_text("old", encoding="utf-8")
        self.assertEqual(self.install("--apply").returncode, 0)
        custom = self.skills / "example" / "custom.md"
        custom.write_text("keep", encoding="utf-8")
        old.unlink()
        self.skill.write_text("New upstream", encoding="utf-8")
        result = self.install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((custom.parent / "old.md").exists())
        self.assertEqual(custom.read_text(), "keep")
        self.assertEqual((custom.parent / "SKILL.md").read_text(), "New upstream")

    def test_corrupt_manifest_cannot_escape_destination(self):
        self.assertEqual(self.install("--apply").returncode, 0)
        path = self.state / "install.json"
        manifest = json.loads(path.read_text())
        manifest["files"]["../outside.txt"] = "0" * 64
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("path", result.stderr.lower())

    def test_state_directory_must_live_outside_skill_installation(self):
        result = self.install("--state-dir", self.skills / "state", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.skills.exists())

    def test_source_cannot_be_the_installation_destination(self):
        result = self.install("--skills-dir", self.source / "skills", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.skill.read_text(encoding="utf-8").splitlines()[-1], "Original")

    def test_unfinished_manifest_refuses_update_before_any_writes(self):
        self.assertEqual(self.install("--apply").returncode, 0)
        before = {p.relative_to(self.base): p.read_bytes()
                  for parent in (self.skills, self.state) for p in parent.rglob("*") if p.is_file()}
        pending = self.state / "install.json.tmp"
        pending.write_text("unfinished", encoding="utf-8")
        self.skill.write_text("New upstream", encoding="utf-8")
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unfinished manifest", result.stderr)
        for relative, content in before.items():
            self.assertEqual((self.base / relative).read_bytes(), content)
        self.assertEqual(pending.read_text(), "unfinished")

    def test_malformed_manifest_is_a_clear_preflight_error(self):
        self.state.mkdir()
        (self.state / "install.json").write_text("[]", encoding="utf-8")
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest does not match", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.skills.exists())

    def test_file_in_place_of_parent_directory_refuses_update_before_writing(self):
        self.assertEqual(self.install("--apply").returncode, 0)
        original = (self.skills / "example" / "SKILL.md").read_bytes()
        self.skill.write_text("New upstream", encoding="utf-8")
        nested = self.skill.parent / "references" / "guide.md"
        nested.parent.mkdir()
        nested.write_text("Guide", encoding="utf-8")
        (self.skills / "example" / "references").write_text("Local file", encoding="utf-8")
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a directory", result.stderr)
        self.assertEqual((self.skills / "example" / "SKILL.md").read_bytes(), original)


class PackageTests(unittest.TestCase):
    def test_host_defaults_and_profile_overrides(self):
        spec = importlib.util.spec_from_file_location("superpowers_install", INSTALL)
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        home = ROOT / "test-home"
        self.assertEqual(installer.destinations("claude", home, {}),
                         (home / ".claude/skills", home / ".claude/my-superpowers", home / ".claude/CLAUDE.md"))
        self.assertEqual(installer.destinations("codex", home, {}),
                         (home / ".agents/skills", home / ".codex/my-superpowers", home / ".codex/AGENTS.md"))
        profile = home / "profile"
        self.assertEqual(installer.destinations("claude", home, {"CLAUDE_CONFIG_DIR": str(profile)})[0],
                         profile / "skills")
        self.assertEqual(installer.destinations("codex", home, {"CODEX_HOME": str(profile)}),
                         (home / ".agents/skills", profile / "my-superpowers", profile / "AGENTS.md"))

    def test_complete_install_preserves_files_and_resolves_host_references(self):
        source_skills = ROOT / "skills"
        for host in ("claude", "codex"):
            with self.subTest(host=host), tempfile.TemporaryDirectory(prefix="superpowers package ") as temp:
                base = Path(temp)
                installed, state = base / "skills", base / "state"
                result = run(sys.executable, INSTALL, "--target", host, "--skills-dir", installed,
                             "--state-dir", state, "--apply")
                self.assertEqual(result.returncode, 0, result.stderr)
                manifest = json.loads((state / "install.json").read_text(encoding="utf-8"))
                for relative in manifest["files"]:
                    self.assertEqual((installed / relative).read_bytes(), (source_skills / relative).read_bytes())
                skills = list(installed.glob("*/SKILL.md"))
                self.assertEqual(len(skills), len(list(source_skills.glob("*/SKILL.md"))))
                for path in skills:
                    content = path.read_text(encoding="utf-8")
                    self.assertTrue(content.startswith("---\n"), path)
                    metadata = content.split("---", 2)[1]
                    self.assertRegex(metadata, r"(?m)^name: \S+")
                    self.assertRegex(metadata, r"(?m)^description: .+")
                    link = re.search(r"\[platforms\.md\]\(([^)]+)\)", content)
                    self.assertIsNotNone(link, path)
                    self.assertTrue((path.parent / link[1]).is_file(), path)
                references = installed / "using-superpowers" / "references"
                for path in references.glob("*.md"):
                    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                        if "://" not in target:
                            self.assertTrue((path.parent / target.split("#", 1)[0]).is_file(), target)
                self.assertTrue((installed / SDD.relative_to(source_skills)).is_file())
                self.assertFalse((state / "coordinator-registry.md").exists())


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="superpowers repo ")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        for args in [("init", "-q"), ("config", "user.name", "Fixture"),
                     ("config", "user.email", "fixture@example.invalid"),
                     ("config", "core.autocrlf", "false"),
                     ("config", "core.hooksPath", str(self.repo / "no-hooks"))]:
            result = run("git", *args, cwd=self.repo)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.plan = self.repo / "plan with spaces.md"
        self.plan.write_text("# Plan\n### Task 1: One\nFirst\n```md\n### Task 2: fake\n```\n~~~\n### Task 9: fake\n~~~\n### Task 2: Two\nSecond\n", encoding="utf-8")

    def sdd(self, *args):
        return run(sys.executable, SDD, *args, cwd=self.repo)

    def commit(self, text):
        (self.repo / "file.txt").write_text(text, encoding="utf-8")
        self.assertEqual(run("git", "add", ".", cwd=self.repo).returncode, 0)
        result = run("git", "-c", "commit.gpgsign=false", "commit", "-qm", text, cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        return run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()

    def test_brief_respects_fenced_headings_and_prints_a_real_path(self):
        result = self.sdd("brief", self.plan, "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        brief = Path(result.stdout.strip()).read_text(encoding="utf-8")
        self.assertIn("### Task 2: fake", brief)
        self.assertIn("### Task 9: fake", brief)
        self.assertNotIn("### Task 2: Two", brief)

    def test_missing_task_fails_without_overwriting_an_existing_output(self):
        out = self.repo / "keep.md"
        out.write_text("keep", encoding="utf-8")
        result = self.sdd("brief", self.plan, "99", out)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(out.read_text(), "keep")

    def test_workspace_is_ignored_and_preserves_existing_ignore_rules(self):
        ignore = self.repo / ".superpowers" / "sdd" / ".gitignore"
        ignore.parent.mkdir(parents=True)
        ignore.write_text("# keep this comment\n", encoding="utf-8")
        result = self.sdd("workspace", self.plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# keep this comment", ignore.read_text())
        path = Path(result.stdout.strip())
        self.assertEqual(run("git", "check-ignore", str(path), cwd=self.repo).returncode, 0)

    def test_same_basename_plans_cannot_share_a_ledger(self):
        self.assertEqual(self.sdd("workspace", self.plan).returncode, 0)
        other = self.repo / "another" / self.plan.name
        other.parent.mkdir()
        other.write_text("# Other plan", encoding="utf-8")
        result = self.sdd("workspace", other)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different plan", result.stderr.lower())

    def test_review_includes_all_commits_since_recorded_base(self):
        base = self.commit("base")
        self.commit("first change")
        head = self.commit("second change")
        result = self.sdd("review", self.plan, base, head)
        self.assertEqual(result.returncode, 0, result.stderr)
        review = Path(result.stdout.strip()).read_text(encoding="utf-8")
        self.assertIn("first change", review)
        self.assertIn("second change", review)
        self.assertIn("-base", review)

    def test_bad_revision_fails_before_creating_workspace(self):
        result = self.sdd("review", self.plan, "not-a-revision", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / ".superpowers").exists())

    def test_cleanup_removes_only_the_identified_plan(self):
        first = self.sdd("workspace", self.plan)
        other = self.repo / "other.md"
        other.write_text("# Other", encoding="utf-8")
        second = self.sdd("workspace", other)
        result = self.sdd("clean", self.plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(Path(first.stdout.strip()).exists())
        self.assertTrue(Path(second.stdout.strip()).exists())

    def test_legacy_workspace_requires_matching_ledger_before_adoption_and_cleanup(self):
        directory = self.repo / ".superpowers" / "sdd" / self.plan.stem
        directory.mkdir(parents=True)
        ledger = directory / "progress.md"
        ledger.write_text("Unidentified work", encoding="utf-8")
        self.assertNotEqual(self.sdd("workspace", self.plan).returncode, 0)
        self.assertEqual(ledger.read_text(), "Unidentified work")
        ledger.write_text(f"# SDD ledger — plan: {self.plan.name}\n", encoding="utf-8")
        self.assertNotEqual(self.sdd("clean", self.plan).returncode, 0)
        self.assertTrue(ledger.exists())
        self.assertEqual(self.sdd("workspace", self.plan).returncode, 0)
        self.assertEqual(self.sdd("clean", self.plan).returncode, 0)
        self.assertFalse(directory.exists())

    def test_output_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory(prefix="superpowers outside ") as temp:
            output = Path(temp) / "keep.md"
            output.write_text("Keep", encoding="utf-8")
            result = self.sdd("brief", self.plan, "1", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("escapes repository", result.stderr)
            self.assertEqual(output.read_text(), "Keep")

    def test_output_rejects_an_external_alias_back_into_the_repository(self):
        with tempfile.TemporaryDirectory(prefix="superpowers alias ") as temp:
            alias = Path(temp) / "alias"
            try:
                alias.symlink_to(self.repo, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlinks unavailable: {error}")
            keep = self.repo / "keep.md"
            keep.write_text("Keep", encoding="utf-8")
            result = self.sdd("brief", self.plan, "1", alias / keep.name)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(keep.read_text(), "Keep")

    @unittest.skipUnless(BASH, "Bash compatibility launchers need Bash")
    def test_bash_compatibility_entry_points(self):
        base = self.commit("base")
        head = self.commit("change")
        env = dict(os.environ, PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""))
        for name, args in (("sdd-workspace", ()), ("task-brief", ("1",)),
                           ("review-package", (base, head))):
            result = run(BASH, (SDD.parent / name).as_posix(), self.plan.as_posix(),
                         *args, cwd=self.repo, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(Path(result.stdout.strip()).exists(), result.stdout)


if __name__ == "__main__":
    unittest.main()
