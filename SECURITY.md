# Security Policy

## Supported Versions

Only the latest release on the `main` branch receives active telemetry updates and security patches.

| Version | Supported |
| ------- | ------------------ |
| `main` (v2.x) | :white_check_mark: |
| `< 2.0` | :x: |

## Zero-Execution Guarantee

`Pro-Desk-bot` is strictly a read-only quantitative telemetry and paper-trading research engine. It never stores private keys, connects to signing wallets, or executes on-chain transactions—an invariant enforced by automated CI checks (`tests/test_safety_policy.py`).

## Reporting a Vulnerability

Please report any security issues, secret leaks, or data-pipeline bugs privately via GitHub's **Private Vulnerability Reporting** feature under the **Security and quality** tab rather than opening a public issue. You can expect an initial response within 48 hours.
