#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alec Thomas
# Copyright (c) 2018 Alec Thomas
#
# License: MIT
#

"""This module exports the Golangcilint plugin class."""

import os
import json
import tempfile
from SublimeLinter.lint import Linter, util
from SublimeLinter.lint.persist import settings


class Golangcilint(Linter):
    cmd = "golangci-lint run --fast --out-format json --enable typecheck"
    regex = r"(?:[^:]+):(?P<line>\d+):(?P<col>\d+):(?:(?P<warning>warning)|(?P<error>error)):(?P<message>.*)"
    defaults = {"selector": "source.go"}
    error_stream = util.STREAM_STDOUT
    multiline = False

    def run(self, cmd, code):
        dir = os.path.dirname(self.filename)
        if not dir:
            print("golangcilint: skipped linting of unsaved file")
            return
        if settings.get("lint_mode") == "background":
            return self._live_lint(cmd, code)
        else:
            return self._in_place_lint(cmd)

    def finalize_cmd(self, cmd, context, at_value='', auto_append=False):
        """prevents SublimeLinter to append filename at the end of cmd"""
        return cmd

    def _live_lint(self, cmd, code):
        dir = os.path.dirname(self.filename)
        files = [file for file in os.listdir(dir) if file.endswith(".go")]
        if len(files) > 100:
            print("golangcilint: too many files ({}), live linting skipped".format(len(files)))
            return ""
        return self.tmpdir(cmd, dir, files, self.filename, code)

    def _in_place_lint(self, cmd):
        return self.execute(cmd)

    def tmpdir(self, cmd, dir, files, filename, code):
        """Run an external executable using a temp dir filled with files and return its output."""
        try:
            with tempfile.TemporaryDirectory(dir=dir, prefix=".golangcilint-") as tmpdir:
                for filepath in files:
                    target = os.path.join(tmpdir, filepath)
                    filepath = os.path.join(dir, filepath)
                    if os.path.basename(target) != os.path.basename(filename):
                        os.link(filepath, target)
                        continue
                    # source file hasn't been saved since change
                    # so update it from our live buffer for now
                    with open(target, 'wb') as w:
                        if isinstance(code, str):
                            code = code.encode('utf8')
                        w.write(code)
                return self.execute(cmd + [tmpdir])
        except FileNotFoundError:
            print("golangcilint file not found error on `{}`".format(dir))
            return ""
        except PermissionError:
            print("golangcilint permission error on `{}`".format(dir))
            return ""

    def issue_level(self, issue):
        """consider /dev/stderr as errors and /dev/stdout as warnings"""
        return "error" if issue["FromLinter"] == "typecheck" else "warning"

    def execute(self, cmd):
        lines = []
        usable = []
        output = self.communicate(cmd)
        report = json.loads(output)
        currnt = os.path.basename(self.filename)

        # Go 1.4 introduces an annotation for package clauses in Go source that
        # identify a canonical import path for the package. If an import is
        # attempted using a path that is not canonical, the go command will
        # refuse to compile the importing package.
        #
        # When the linter runs, it creates a temporary directory, for example,
        # “.golangcilint-foobar”, then creates a symbolic link for all relevant
        # files, and writes the content of the current buffer in the correct
        # file. Unfortunately, canonical imports break this flow because the
        # temporary directory differs from the expected location.
        #
        # The only way to deal with this for now is to detect the error, which
        # may as well be a false positive, and then ignore all the warnings
        # about missing packages in the current file. Hopefully, the user has
        # “goimports” which will automatically resolve the dependencies for
        # them. Also, if the false positives are not, the programmer will know
        # about the missing packages during the compilation phase, so it’s not
        # a bad idea to ignore these warnings for now.
        ignore_broken_imports = False

        """merge possible stderr with issues"""
        if "Error" in report["Report"]:
            for line in report["Report"]["Error"].splitlines():
                if line.count(":") < 3:
                    continue
                parts = line.split(":")
                report["Issues"].append({
                    "FromLinter": "typecheck",
                    "Text": parts[3].strip(),
                    "Pos": {
                        "Filename": parts[0],
                        "Line": parts[1],
                        "Column": parts[2],
                    }
                })

        """format issues into formal pattern"""
        for issue in report["Issues"]:
            name = issue["Pos"]["Filename"]
            mark = name.rfind("/")
            mark = 0 if mark == -1 else mark+1
            issue["Pos"]["Shortname"] = name[mark:]
            issue["Level"] = self.issue_level(issue)
            usable.append(issue)

        """remove useless warnings and errors"""
        for issue in usable:
            """detect broken canonical imports"""
            if ("code in directory" in issue["Text"]
                and "expects import" in issue["Text"]):
                ignore_broken_imports = True
                continue

            """ignore false positive warnings"""
            if (ignore_broken_imports
                and "could not import" in issue["Text"]
                and "missing package:" in issue["Text"]):
                continue

            """skip issues from unrelated files"""
            if issue["Pos"]["Shortname"] != currnt:
                continue

            lines.append(
                "{}:{}:{}:{}:{}".format(
                    issue["Pos"]["Shortname"],
                    issue["Pos"]["Line"],
                    issue["Pos"]["Column"],
                    issue["Level"],
                    issue["Text"]
                )
            )

        return "\n".join(lines)
