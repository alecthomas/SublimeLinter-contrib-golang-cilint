#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alec Thomas
# Copyright (c) 2014 Alec Thomas
#
# License: MIT
#

"""This module exports the Gometalinter plugin class."""

import os
import shlex
import tempfile

from SublimeLinter.lint import Linter, highlight, util
from SublimeLinter.lint.persist import settings


class GolangCILint(Linter):
    """Provides an interface to golangci-lint."""

    syntax = ('go', 'gosublime-go', 'gotools', 'anacondago-go')
    cmd = 'golangci-lint run --fast --enable typecheck'
    regex = r'(?:[^:]+):(?P<line>\d+):(?P<col>\d+)?:\s*(?P<message>.*)'
    error_stream = util.STREAM_BOTH
    default_type = highlight.ERROR

    def run(self, cmd, code):
        filename = os.path.basename(self.filename)
        if settings.get('lint_mode') == 'background':
            out = self._live_lint(cmd, code)
        else:
            out = self._in_place_lint(cmd)
        lines = [line for line in out.splitlines()
                 if line.startswith(filename + ':')]
        return '\n'.join(lines)

    def _dir_env(self):
        settings = self.get_view_settings()
        dir = os.path.dirname(self.filename)
        env = self.get_environment(settings)
        return dir, env

    def _live_lint(self, cmd, code):
        dir, env = self._dir_env()
        if not dir:
            print('golangci-lint: skipped linting of unsaved file')
            return
        filename = os.path.basename(self.filename)
        print('golangci-lint: live linting {} in {}: {}'.format(filename, dir, ' '.join(map(shlex.quote, cmd))))
        files = [f for f in os.listdir(dir) if f.endswith('.go')]
        if len(files) > 40:
            print("golangci-lint: too many files ({}), live linting skipped".format(len(files)))
            return ''
        return tmpdir(cmd, dir, files, self.filename, code, env=env)

    def _in_place_lint(self, cmd):
        dir, env = self._dir_env()
        if not dir:
            print('golangci-lint: skipped linting of unsaved file')
            return
        filename = os.path.basename(self.filename)
        print('golangci-lint: in-place linting {}: {}'.format(filename, ' '.join(map(shlex.quote, cmd))))
        out = util.communicate(cmd, output_stream=util.STREAM_BOTH, env=env, cwd=dir)
        return out or ''


def tmpdir(cmd, dir, files, filename, code, env=None):
    """Run an external executable using a temp dir filled with files and return its output."""
    with tempfile.TemporaryDirectory(dir=dir, prefix=".golangci-lint-") as tmpdir:
        for f in files:
            target = os.path.join(tmpdir, f)
            f = os.path.join(dir, f)

            if os.path.basename(target) == os.path.basename(filename):
                # source file hasn't been saved since change, so update it from our live buffer
                with open(target, 'wb') as f:
                    if isinstance(code, str):
                        code = code.encode('utf8')

                    f.write(code)
            else:
                os.link(f, target)

        out = util.communicate(cmd, output_stream=util.STREAM_BOTH, env=env, cwd=tmpdir)
    return out or ''
