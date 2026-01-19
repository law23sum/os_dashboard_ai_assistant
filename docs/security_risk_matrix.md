# Security Risk Matrix (Home Network + Local Systems)

This matrix prioritizes the highest-risk items first so remediation happens from high to low.

| Priority | Risk | Likelihood | Impact | Rating | Primary Signals | Recommended Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Unauthorized access to exposed services | High | High | Critical | Unknown external IPs on admin ports; new listening ports | Block external access, enforce allowlists, require MFA, disable remote admin exposure |
| 2 | Credential stuffing on remote access | High | Medium | High | Burst failed logins; repeated attempts from single IP | Enforce MFA, rate-limit, block abusive IPs, rotate passwords |
| 3 | Malware foothold on endpoint | Medium | High | High | Unknown process with network activity; new autoruns | Isolate host, remove malware, reimage if needed |
| 4 | Data exfiltration over outbound connections | Medium | High | High | High-volume outbound connections to unknown IPs | Egress allowlist, DLP, block suspicious outbound flows |
| 5 | Unpatched service vulnerabilities | Medium | Medium | Medium | Known service versions; missing patches | Patch OS/services, automate updates |
| 6 | Misconfigured local firewall | Low | Medium | Medium | Broad inbound rules; unexpected listening ports | Harden firewall, close unused ports |
| 7 | Shadow devices on guest Wi-Fi | Low | Medium | Medium | New MAC/IPs on network | Segment guest/IoT VLAN, device inventory |
| 8 | Phishing-driven single endpoint compromise | Low | Medium | Medium | Suspicious logins, unusual access time | Security awareness, mailbox protection |
| 9 | Stale backups or missing recovery testing | Low | Medium | Low | Old backup timestamps | Test restores, verify backup retention |

## Remediation Order (High to Low)
1. Lock down external exposure (ports, remote admin, VPN access).
2. Enforce MFA and rate limits for authentication surfaces.
3. Endpoint protection and malware response playbooks.
4. Egress control and outbound monitoring.
5. Patch management automation.
6. Firewall baseline validation.
7. Device inventory + network segmentation.
8. Phishing training + mailbox controls.
9. Backup validation and restore testing cadence.
