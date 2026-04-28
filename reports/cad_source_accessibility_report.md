# CAD Source Accessibility Report

Generated for Stage 3A-2. This report only checks website entry-point accessibility. It does not download CAD files, does not request large files, does not bypass login, captcha, product configurators, or license terms, and does not mark any CAD as downloaded.

| site | reachable | requires_login_likely | direct_download_possible_unknown | note |
|---|---|---|---|---|
| `tech.thk.com` | yes | likely | yes | Entry page returned HTTP 200. THK CAD commonly requires product selection and may require portal/manual actions. |
| `misumi-ec.com` | yes | likely | yes | Entry page returned HTTP 200. MISUMI CAD usually requires model configuration, length/stroke selection, and format selection. |
| `igus.com` | yes | possible | yes | Entry page returned HTTP 200. igus CAD often uses configurable product pages for chain type, bend radius, and length. |
| `smcworld.com` | limited | likely | yes | Entry request returned access-limited/forbidden behavior in this environment. Manual browser access or regional SMC portal may be required. |
| `traceparts.com` | yes | possible | yes | Entry page returned HTTP 202. TraceParts typically requires part selection and may require account/session for downloads. |
| `3dcontentcentral.com` | timeout | possible | yes | Entry request timed out in this environment. Manual browser access may still work, but no direct CAD link was verified. |
| `mcmaster.com` | yes | possible | yes | Entry page returned HTTP 200. McMaster CAD generally requires product page selection; direct CAD links were not verified. |

## Result

No direct, public, model-specific CAD file URL was confirmed during this stage. Therefore no CAD file was downloaded and no part status was changed to `downloaded`.

## Download Boundary

Automatic download is allowed only when the URL is a direct trusted CAD file link, requires no login or captcha, requires no product configurator, and uses an allowed extension: `.step`, `.stp`, `.sldprt`, `.sldasm`, `.x_t`, `.igs`, `.iges`.
