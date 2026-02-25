# XSS Attacks - Complete Documentation

## Summary

| Tipo | Payload | Resultado |
|------|---------|-----------|
| Reflected | `<script>alert('THIS SITE HAS BEEN HACKED')</script>` | Alert |
| Stored | `<script>alert('XSS STORED - PRESENTIE')</script>` | Alert |

---

## 1. XSS Reflected

### Location 
'http:localhost/vulnerabilities/xss_r'

### Objetive
Execute Javascript in the victim's browser through a malicious link

### Vulnerabilities Detection
**Test Payload:**
```html
<script>alert('XSS')</script>

```
### Results
An alert box appears -> Vulnerable


## Explotation
### Payload Used:
```html
<script>alert('THIS SITE HAS BEEN HACKED')</script>

```
### Full Attack URL:
http://localhost/vulnerabilities/xss_r/?name=<script>alert('THIS+SITE+HAS+BEEN+HACKED')</script>

### Result:
https://../screenshots/xss_reflected_hacked.png


### Technical Explanation
The server takes the 'name' parameter from URL and prints it directly into the HTML without sanitization:
```php
echo "Hello" . $_GET['name'];

```
This allows injecting <script> tags that the browser interprets as executable code.

## 2. XSS STORED

### Location
http://localhost/vulnerabilities/xss_s/

### Objetive
Store a payload in the database so it executes everytime someone visits the page.

### Vulnerability Detection
Payload in 'Name' field:
<script>alert('XSS Stored')</script>

Message: Test
Result: The alert appears immediately

### Explotation
Payload Used:
```html
<script>alert('XSS STORED ATTACK')</script>

```
Form fields:
- Name: .
- Message: <script>alert('XSS STORED ATTACK')</script>

### Result:
https://../screenshots/xss_stored_hacked.png


### Technical Explanation
The Payload is saved in the database. Everytime the page loads, the script is retrivied from the DB and inserted into the HTML:
```php
// Vulnerable code
$name = $_POST['txtName'];
$message = $_POST['mtxMessage'];
$query = "INSERT INTO guestbook (name, message) VALUES ('$name', '$message')";
// No sanitization
```

### Persistence Demonstration
- ✅ Alert appears when reloading the page (F5)
- ✅ Alert appears even after closing and reopening the browser
- ✅ Affects ALL users who visit the page


## Impact of XSS Attacks

|Impact       |	Description |
|-------------|-------------|
|Cookie theft |	Session hijacking |
|Redirection  |	Send victims to phishing sites |
|Keylogging   |	Capture user keystrokes |
|Defacement   |	Modify page content |


## Mitigation Measures (for defense phase)
1. Input Validation: Allow only expected characters
2. Output escaping: Convert < to &lt;, > to &gt;
3. Content Security Policy (CSP)
4. HttpOnly cookies to prevent session theft


## Evidence
- XSS Reflected Screenshot: screenshots/xss_reflected_hacked.png
- XSS Stored Screenshot: screenshots/xss_stored_hacked.png 


## Attack Timeline
|⏱️ Attack | Timeline |
-----------|-----------
|Time	   |  Action |
|14:30	   |  XSS Reflected testing |
|14:35	   |  Successful payload with alert |
|14:40	   |  Screenshot taken |
|14:45	   |  XSS Stored testing |
|14:50	   |  Payload successfully stored |
|14:55	   |  Screenshot taken |
|15:00	   |  Documentation completed |
