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

Not yet run on a Mac; see the git history for the first tested run.
