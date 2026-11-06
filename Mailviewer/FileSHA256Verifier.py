#!/usr/local/autopkg/python
#
# Copyright 2026 Machinery Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for FileSHA256Verifier class"""

import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["FileSHA256Verifier"]


class FileSHA256Verifier(Processor):
    """Computes the SHA-256 of a file and fails the recipe unless it equals
    the expected value, for example one read from a vendor's manifest."""

    description = __doc__
    input_variables = {
        "input_path": {
            "required": True,
            "description": "Path to the file to hash.",
        },
        "expected_sha256": {
            "required": True,
            "description": "The expected SHA-256 digest, 64 hex characters. Case is ignored.",
        },
    }
    output_variables = {
        "sha256_verified": {
            "description": "The verified SHA-256 digest, in lower case.",
        }
    }

    def main(self):
        path = self.env["input_path"]
        expected = str(self.env["expected_sha256"]).strip().lower()
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ProcessorError(
                f"expected_sha256 is not a 64-character hex digest: {expected!r}"
            )

        digest = hashlib.sha256()
        try:
            with open(path, "rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as err:
            raise ProcessorError(f"Could not read {path}: {err}") from err
        actual = digest.hexdigest()

        if actual != expected:
            raise ProcessorError(
                f"SHA-256 mismatch for {path}: expected {expected}, got {actual}"
            )
        self.output(f"SHA-256 of {path} matches {expected}")
        self.env["sha256_verified"] = actual


if __name__ == "__main__":
    PROCESSOR = FileSHA256Verifier()
    PROCESSOR.execute_shell()
