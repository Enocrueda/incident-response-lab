# SOC Analysis - Complete Incident Report

# Executive Summary

On February 22-24, 2026, multiple attacks were detected on the DVWA web application. The attacker performed reconnaissance, exploited SQL Injection and XSS vulnerabilities, and successfully extracted credentials. This report documents the full incident timeline, indicators of compromise, detection methodology, containment measures, and recommendations.

**Incident ID:** INC-2026-001  
**Severity:** HIGH  
**Affected Systems:** DVWA Web Application (Docker container)  
**Detection Method:** Log Analysis + Automated Scanning Alerts  

---

## Detection Methodology

### Log Sources Analyzed


| Log Source | Location | Purpose |
|------------|----------|---------|
| Apache Access Log | `/var/log/apache2/access.log` | HTTP requests, payloads, IPs, timestamps |
| Apache Error Log | `/var/log/apache2/error.log` | SQL errors, application errors |
| System Logs | `/var/log/syslog` | Authentication attempts, system events |
| Docker Logs | `docker logs dvwa_lab` | Container activity |

### Detection Commands Used

#### 1. SQL Injection Detection
```bash
# Search for UNION-based SQLi patterns
grep -i "union.*select" /var/log/apache2/access.log

# Search for common SQLi test strings
grep -E "('|--|#|/\*|;)" /var/log/apache2/access.log

# Check for error responses (500) that might indicate SQL errors
grep " 500 " /var/log/apache2/access.log
```

#### 2. XSS Detection
```bash
# Search for script tags in requests
grep -i "<script>" /var/log/apache2/access.log

# Search for encoded XSS attempts
grep -i "%3Cscript%3E" /var/log/apache2/access.log

# Check for alert() function calls
grep -i "alert(" /var/log/apache2/access.log
```

#### 3. Port Scan Detection
```bash
# Check for sequential connection attempts from same IP
grep "192.168.1.100" /var/log/apache2/access.log | awk '{print $4}' | sort | uniq -c

# Look for requests to non-existent pages (scanning behavior)
grep " 404 " /var/log/apache2/access.log | grep "192.168.1.100"
```

#### 4. Directory Enumeration Detection
```bash
# Check for many 404 errors from same IP
grep "192.168.1.100" /var/log/apache2/access.log | grep " 404 " | wc -l

# List directories attempted
grep "192.168.1.100" /var/log/apache2/access.log | awk '{print $7}' | sort | uniq -c | sort -nr
```

### Detection Results Summary

|Detection Method | Findings | Timestamp |
|-----------------|----------|-----------|-
| grep -i "union" access.log | 1 SQLi attempt found | 2026-02-24 10:30:01 |
| grep -i "<script>" access.log | 2 XSS attempts found | 2026-02-24 14:35 / 14:50 |
| Sequential port analysis | Port scan detected | 2026-02-24 10:00-10:05 |
| 404 error frequency | Directory brute force | 2026-02-24 10:05-10:10 |

### Automated Detection Script
The following script was used to automate log analysis:
```bash
#!/bin/bash
# auto_detect.sh - Automated log analysis for incident detection

LOG_FILE="/var/log/apache2/access.log"
echo "=== Incident Detection Report ==="
date

echo -e "\n[+] SQL Injection Attempts:"
grep -i "union.*select" $LOG_FILE | wc -l

echo -e "\n[+] XSS Attempts:"
grep -i "<script>" $LOG_FILE | wc -l

echo -e "\n[+] Top 5 Suspicious IPs:"
grep -E "(\?|%|script|union)" $LOG_FILE | awk '{print $1}' | sort | uniq -c | sort -nr | head -5
```
Output: 
```text
=== Incident Detection Report ===
Thu Feb 24 10:15:00 CST 2026

[+] SQL Injection Attempts: 1

[+] XSS Attempts: 2

[+] Top 5 Suspicious IPs:
   3 192.168.1.100
   1 127.0.0.1
```

### Alert Triggers

|Alert Type | Threshold | Triggered? | 
|-----------|-----------|------------|
| SQLi pattern match | > 0 | ✅ YES (1 match) |
| XSS pattern match | > 0 | ✅ YES (2 matches) |
| Port scan (sequential requests) | > 50 in 1 min | ✅ YES |
| Directory brute force (404 errors) | > 20 in 1 min | ✅ YES |
| Same IP multiple payloads | > 3 | ✅ YES |


### Indicators of Compromise (IoCs)

#### Phase 1. Reconnaissance

Nmap Scan Detection

|Timestamp | Source IP | Activity | Evidence |
|----------|-----------|----------|----------|
|2026-02-24 10:00:00 | 192.168.1.100 | Port scan (full TCP connect) | scans/nmap/ |

Findings:
- Open ports detected: 80(HTTP), 3306(mySQL)

|PORT | STATE |  SERVICE |  VERSION |
|-----|-------|----------|----------|
| 80/tcp | open | http | Apache httpd 2.4.25 |
| 3306/tcp | open | mysql | MySQL 5.7.19 |

Gobuster Directory Enumeration

|Timestamp | Source IP | Activity | Evidence |
|----------|-----------|----------|----------|
| 2026-02-24 10:05:00 | 192.168.1.100 | Directory brute-forcing | scans/gobuster/gobuster_scan_20260224_235951.txt |

Discovered Directories:

- /vulnerabilities/

- /config/

- /docs/

- /phpmyadmin/

- setup/

Gobuster Output Example:
```text
/vulnerabilities (Status: 200)
/config (Status: 403)
/docs (Status: 200)
/phpmyadmin (Status: 200)
/setup (Status: 200)
```

#### Phase 2. SQL Injection Attack

|Timestamp | Source IP | Payload |
|----------|-----------|---------|
| 2026-02-22 10:30:01 | 192.168.1.100 | 1' UNION SELECT user, password FROM users-- - |

HTTP Request: 
```text
GET /vulnerabilities/sqli/?id=1%27+UNION+SELECT+user%2Cpassword+FROM+users--+-&Submit=Submit HTTP/1.1
Host: localhost
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Cookie: PHPSESSID=abc123def456; security=low
```
Impact: Extraction of 4 user password hashes

Extracted Data:

|Username | Password Hash | Cracked Password |
|---------|---------------|------------------|
|admin | 5f4dcc3b5aa765d61d8327deb882cf99 | password |
|gordonb | e99a18c428cb38d5f260853678922e03 | abc123 |
|pablo | 0d107d09f5bbe40cade3de5c71e9e9b7 | letmein |
|smith | 8d3533d75ae2c3966d7e0d4fcc69216b | charley |

Cracking Method: John The Ripper with rockyou.txt wordlist.


#### Phase 3: XSS Attacks

XSS Reflected

|Timestamp | Source IP | Payload |
|----------|-----------|---------|
| 2026-02-22 14:35:22 | 192.168.1.100 | <script>alert('THIS SITE HAS BEEN HACKED')</script> |

HTTP Request:
```text
GET /vulnerabilities/xss_r/?name=<script>alert('THIS+SITE+HAS+BEEN+HACKED')</script>&Submit=Submit HTTP/1.1
Host: localhost
```
Evidence: https://../screenshots/xss_reflected_hacked.png

XSS Stored

|Timestamp | Source IP | Payload |
|----------|-----------|---------|
| 2026-02-22 14:50:15 | 192.168.1.100 |	<script>alert('XSS STORED - PERSISTENT')</script> |

HTTP Request:
```text
POST /vulnerabilities/xss_s/ HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 89

txtName=<script>alert('XSS+STORED+-+PERSISTENT')</script>&mtxMessage=Test&btnSign=Sign+Guestbook
```
Impact: Persistent payload affecting all users

Evidence: https://../screenshots/xss_storage_hacked.png


#### Phase 4: Post-Exploitation

|Activity | Timestamp | Details |
|---------|-----------|---------|
| Password cracking | 2026-02-22 10:45-11:00 | John the Ripper successful | 
| Admin login | 2026-02-22 11:05 | Access with admin:password | 
| Automated scanning | 2026-02-24 10:00 | Auto scanner detected scans |


- Attack Timeline (Full)

|Time | Phase | Attack Type | Description |
|-----|-------|-------------|-------------|
| 10:00 | Recon | Nmap Scan | Port discovery (80, 3306) | 
| 10:05 | Recon	| Gobuster | Directory enumeration | 
| 10:30 | Exploitation | SQL Injection | Credential extraction |
| 10:45 | Cracking | John the Ripper | Password hash cracking |
| 11:00 | Access  | Admin Login | Successful auth |
| 14:35 | Exploitation |	XSS Reflected |	JavaScript execution |
| 14:50 | Exploitation |	XSS Stored | Persistent payload |
| 15:00 | Documentation	-	Attacker documents findings |


### Containment Measures

#### Inmediate actions (First 30 minutes)

1. Network Isolation
```bash
# Block attacker IP at Firewall
sudo iptables -A INPUT -s 192.168.1.100 -j DROP
```
- Attacker Ip blocked
- Network traffic monitored

2. System Isolation
```bash
# Pause vulnerable container
docker pause dvwa_lab

- Container isolated for forensics
- Snapshot taken for analysis
```
3. Credential Reset
- All 4 user passwords reset
- Password policy enforced (12+ chars, complexity)
- Users notified of incident

#### Erradication (Next 2 hours)
1. Code Patching
```php
// BEFORE (vulnerable)
$query = "SELECT * FROM users WHERE user_id = " . $_GET['id'];

// AFTER (patched)
$stmt = $conn->prepare("SELECT * FROM users WHERE user_id = ?");
$stmt->bind_param("i", $_GET['id']);
$stmt->execute();
```
2. XSS Fix
```php
// BEFORE (vulnerable)
echo "Hello " . $_GET['name'];

// AFTER (patched)
echo "Hello " . htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
```

3. Database Cleanup
```sql
DELETE FROM guestbook WHERE message LIKE '%<script>%';
```

4. System Restoration
- Restored from clean backup
- Verified no persistence
- Re-enable container

#### Recovery (24 Hours)

- 24-hour monitoring period
- Log analysis automated
- No further suspicius activity detected


### Root Cause Analysis

- SQL Injection

|Factor | Detail |
|-------|--------|
| Root Cause | Direct concatenation of user input in SQL queries |
| Vulnerable Code | $query = "SELECT ... WHERE user_id = " . $_GET['id']; |
| Fix | Prepared statements with parameterized queries |
| CWE | CWE-89: SQL Injection |


- XSS (Reflected & Stored)

|Factor | Detail |
|-------|--------|
| Root Cause | No output encoding/escaping |
| Vulnerable Code | echo "Hello " . $_GET['name']; |
| Fix | htmlspecialchars() for output encoding |
| CWE | CWE-79: Cross-site Scripting |

 * Configuration Issues:
- Wordlists accesible: Rockyou.txt present (used for cracking)
- Security level: LOW (Disable all protections)
- Default credentials: Admin/password unchanged


### Lessons Learned

#### Technical Lessons
1. Imput validation is CRITICAL -All user input must be validated
2. Output encoding is MANDATORY - Never trust user data
3. Default credentials - Must be changed immediately
4. Logging - Detailed logs enabled detection

#### Process Improvements
1. Automated Scanning should run daily
2. Vulnerability scanning before deployment
3. Security training for developers
4. Incident response plan neeeds regular drills 


### Recommendations

|Priority | Recommendation | Timeline | Responsible |
|---------|----------------|----------|-------------|
| HIGH | Implement prepared statements for ALL database queries | 1 week | Dev Team |
| HIGH | Add output encoding for ALL user-supplied content  | 1 week | Dev Team |
| HIGH | Change all default credentials | 24 hours | Admin |
| HIGH | Enable PHP security modules (mysqli with prepared stmts) | 1 week | DevOps |
| MEDIUM | Deploy WAF (Web Application Firewall)	 | 1 month  | Security Team |
| MEDIUM | Implement automated log analysis (SIEM) | 2 months | SOC Team
| MEDIUM | Regular security code reviews | Ongoing | Dev + Security |
| LOW | Security awareness training | Quarterly | HR + Security |



### Attachments

|File | Description |
|-----|-------------|
| scans/nmap/nmap_scan_*.txt | Full Nmap scan results |
| scans/gobuster/gobuster_scan_*.txt | Directory enumeration results |
| screenshots/sql_injection_payload.png | SQL injection in action |
| screenshots/sql_injection_passwords.png | Extracted data |
| screenshots/sql_injection_john_the_ripper.png | Password cracking |
| screenshots/xss_reflected_hacked.png | XSS reflected alert |
| screenshots/xss_storage_hacked.png | XSS stored alert |
| reports/cracking/hashes.txt | Cracked passwords |
| scripts/auto_scanner.py | Automated scanning tool |


### Incident Summary Card

|Field | Value |
|------|-------|
| Incident ID | INC-2026-001 |
| Severity | HIGH |
| Status | CLOSED | 
| Detection | Date 2026-02-22 |
| Containment | Date 2026-02-22 |
| Eradication | Date 2026-02-23 |
| Recovery Date | 2026-02-24 | 
| Attack Vector | Web Application (HTTP) |
| Source IP | 192.168.1.100 |
| Target	| DVWA Container |
| Data Breach | 4 user credentials |
| Impact | Credential theft, XSS execution |
| Analyst | Enoc Rueda |


### Verification of Remediation

| Check | Status | Date |
|-------|--------|------|
| Prepared statements implemented |  PASS | 2026-02-23 |
| XSS sanitization added |  PASS	| 2026-02-23 |
| Default credentials changed | PASS | 2026-02-22 |
| Firewall rules updated	| PASS	2026-02-22 |
| Monitoring enabled | PASS | 2026-02-23 |
| Re-scan for vulnerabilities | PASS (no critical findings) | 2026-02-24 |



## 👨‍💻 Report Prepared By
Enoc Rueda - SOC Analyst Tier 1
📧 enoctrd@gmail.com
🔗 GitHub: Enocrueda
📅 Report Date: February 24, 2026


