# Security policy

## Reporting a vulnerability

Open a private security advisory on this repository, or email the maintainer
listed in the commit history. Do not open a public issue for a vulnerability in
this tool.

Include the command, the input file and the traceback. A crash report you paste
must be redacted: this tool exists to handle other people's crash data, so a
report about the tool should not carry a third party's session tokens or user
records.

Expect an acknowledgement within a week. This is a single-maintainer project
with no bounty.

## What this tool does with your data

- It reads files you point it at. It does not open sockets, and it has no
  network code at all.
- It does not execute the artifacts in a bundle. `bundle` reads bytes and hashes
  them; `verify` re-reads and re-hashes. Neither runs `repro.sh`.
- It writes only where told: `build` writes under the repository root,
  `bundle --write` writes the manifest path you give it, `scaffold --out` and
  `report --out` write the path you give them.
- It does not copy evidence anywhere. Bundles stay in the directory you chose.

## Handling evidence responsibly

Crash evidence routinely contains secrets: session cookies in a request capture,
tokens in a log line, another user's email in a response body. Before sealing a
bundle:

1. Redact secrets, keeping the shape (`Bearer REDACTED`, not a blank line).
2. Hash **after** redacting, never before — hashing first means either the
   secret ships or the digest is broken by the edit.
3. Keep originals outside the bundle directory and outside version control.
4. Delete captured data when the program's policy requires it, but keep the
   digest and verification report.

The `bundle` phase skills (`redaction-before-hashing`, `bundle-retention`) cover
this in more detail.

## Authorisation

The tool is a triage assistant for authorised testing. It does not scan, fuzz or
exploit. Filing a finding is still your responsibility: check the program's
scope before you submit, and quote the scope reference in the record — `check`
treats a missing scope reference as blocking.
