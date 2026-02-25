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

