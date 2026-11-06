# AutoPkg recipes for Mailviewer for Mac

Recipes for [Mailviewer for Mac](https://updates.mailviewer.app/), by its
developer, Machinery Software LLC. Mailviewer is a signed, notarized
Developer ID `.pkg` (Team ID `D7PHX968FZ`, package ID `app.mailviewer.mac.pkg`)
published at a stable URL with a JSON manifest; the admin guide is at
<https://updates.mailviewer.app/admin/>.

## Adding the repo

```sh
autopkg repo-add machinery-software/autopkg-recipes
```

The Jamf recipe also needs the JamfUploader processors:

```sh
autopkg repo-add grahampugh/jamf-upload
```

## The recipes

| Recipe | Identifier | What it does |
| --- | --- | --- |
| `Mailviewer.download` | `com.github.machinery-software.download.Mailviewer` | Reads `version`, `url` and `sha256` from <https://updates.mailviewer.app/latest.json>, downloads the package, verifies its SHA-256 against the manifest and its signature with `CodeSignatureVerifier`, then `EndOfCheckPhase`. |
| `Mailviewer.pkg` | `com.github.machinery-software.pkg.Mailviewer` | Copies the downloaded package to the cache as `Mailviewer-<version>.pkg`. The vendor's package is already a product package, so nothing is repackaged. |
| `Mailviewer.munki` | `com.github.machinery-software.munki.Mailviewer` | Imports the package into Munki: category Productivity, unattended install, no blocking applications, and an uninstall script that runs the uninstaller the package installs. |
| `Mailviewer.jamf` | `com.github.machinery-software.jamf.Mailviewer` | Uploads the package to Jamf Pro with `JamfCategoryUploader` and `JamfPackageUploader`. No policy is created. |

Input variables: `NAME` (all), `MUNKI_REPO_SUBDIR` and `pkginfo` (munki),
`CATEGORY` (jamf). The Jamf recipe reads `JSS_URL` and the API credentials
from the AutoPkg preferences, as the JamfUploader processors document.

## What the download recipe verifies

The download recipe fails, and nothing is imported or uploaded, unless both
of these hold:

- **SHA-256**: the downloaded file's digest equals the `sha256` in
  `latest.json`. This is `FileSHA256Verifier.py`, a processor in this repo,
  so that a mismatch is an error rather than a warning.
- **Developer ID**: the package's signature chain is
  `Developer ID Installer: Machinery Software LLC (D7PHX968FZ)`,
  `Developer ID Certification Authority`, `Apple Root CA`
  (`CodeSignatureVerifier`).

Both run before `EndOfCheckPhase`, so `autopkg run -c` verifies as well.

## Trust info

Make an override, which records the trust info for the recipe chain and the
processor in this repo, and verify it before each run as usual:

```sh
autopkg make-override Mailviewer.munki     # or Mailviewer.pkg, Mailviewer.jamf
autopkg verify-trust-info Mailviewer.munki
autopkg run Mailviewer.munki
```

After this repo changes, `autopkg verify-trust-info` reports the difference;
review it (`autopkg verify-trust-info -vv Mailviewer.munki`) and accept it
with `autopkg update-trust-info Mailviewer.munki`.

## Tested

**2026-11-05, Mailviewer 1.0.0 (package version 1.0.0.235), AutoPkg 3.0.0, macOS 26,
on the developer's Mac.** `Mailviewer.download` and `Mailviewer.pkg` ran end to
end; `Mailviewer.munki` and `Mailviewer.jamf` ran with `-c` (there is no Munki
repo or Jamf Pro here to import into or upload to). Condensed output of
`autopkg run -v`, the signature chain lines shortened:

```
% autopkg repo-add machinery-software/autopkg-recipes
% autopkg repo-add grahampugh/jamf-upload

% autopkg run -v Mailviewer.download
URLTextSearcher: Found matching text (version): 1.0.0
URLTextSearcher: Found matching text (pkg_version): 1.0.0.235
URLTextSearcher: Found matching text (url): https://updates.mailviewer.app/Mailviewer-1.0.0-235.pkg
URLTextSearcher: Found matching text (sha256): ee2e792207928bd799967d4fd1fe1e4271fbbc99ed591b858b27b6a7a0992414
URLDownloader: Downloaded ~/Library/AutoPkg/Cache/com.github.machinery-software.download.Mailviewer/downloads/Mailviewer-1.0.0.pkg
FileSHA256Verifier: SHA-256 of .../downloads/Mailviewer-1.0.0.pkg matches ee2e792207928bd799967d4fd1fe1e4271fbbc99ed591b858b27b6a7a0992414
CodeSignatureVerifier: Verifying installer package signature...
CodeSignatureVerifier:    Status: signed by a developer certificate issued by Apple for distribution
CodeSignatureVerifier:    Notarization: trusted by the Apple notary service
CodeSignatureVerifier:     1. Developer ID Installer: Machinery Software LLC (D7PHX968FZ)
CodeSignatureVerifier:     2. Developer ID Certification Authority
CodeSignatureVerifier:     3. Apple Root CA
CodeSignatureVerifier: Signature is valid
CodeSignatureVerifier: Authority name chain is valid
EndOfCheckPhase
The following new items were downloaded:
    .../com.github.machinery-software.download.Mailviewer/downloads/Mailviewer-1.0.0.pkg

% autopkg run -v Mailviewer.pkg
(the same download and checks, then)
PkgCopier: Copied .../downloads/Mailviewer-1.0.0.pkg to .../com.github.machinery-software.pkg.Mailviewer/Mailviewer-1.0.0.pkg
The following packages were copied:
    .../com.github.machinery-software.pkg.Mailviewer/Mailviewer-1.0.0.pkg

% autopkg run -v -c Mailviewer.munki
(the download and both checks pass, stops at EndOfCheckPhase)

% autopkg run -v -c Mailviewer.jamf
(the download and both checks pass, stops at EndOfCheckPhase)

% autopkg run -v Mailviewer.download        # second run
URLDownloader: Using existing .../downloads/Mailviewer-1.0.0.pkg
FileSHA256Verifier: SHA-256 of .../downloads/Mailviewer-1.0.0.pkg matches ee2e7922...0992414
CodeSignatureVerifier: Authority name chain is valid
Nothing downloaded, packaged or imported.

% autopkg make-override Mailviewer.pkg
Override file saved to ~/Library/AutoPkg/RecipeOverrides/Mailviewer.pkg.recipe
% autopkg verify-trust-info Mailviewer.pkg
Mailviewer.pkg: OK
```

The SHA-256 check was shown failing: a recipe that passes `FileSHA256Verifier`
a digest one character off ends with
`Error: SHA-256 mismatch for .../Mailviewer-1.0.0.pkg: expected ...0992415, got ...0992414`,
and `autopkg run` exits 70 with "Nothing downloaded, packaged or imported."
