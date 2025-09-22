# Security Violation Documentation Template

## Required Format for Each Security Finding

Each security violation MUST be documented with the following structure:

### SEC-XXX: [Vulnerability Type]
- **Severity**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW
- **File**: `path/to/file.java:line_number` [REF-XXX]
- **OWASP Category**: A03:2021 - Injection (or appropriate category)

#### Vulnerable Code:
```java
// Lines 1234-1250 from the actual file
1234: public ResultSet authenticateUser(String username, String password) {
1235:     String query = "SELECT * FROM users WHERE username = '" + username +
1236:                    "' AND password = '" + password + "'";
1237:
1238:     try {
1239:         Statement stmt = connection.createStatement();
1240:         ResultSet rs = stmt.executeQuery(query);  // VULNERABLE: SQL Injection
1241:
1242:         if (rs.next()) {
1243:             return rs;
1244:         }
1245:     } catch (SQLException e) {
1246:         log.error("Authentication failed", e);
1247:     }
1248:     return null;
1249: }
```

#### 🔍 Why This Is Vulnerable:
Explain the specific vulnerability in context:
- What makes this code pattern dangerous
- How user input flows to the vulnerable point
- What security control is missing or bypassed

Example:
"This code concatenates user-supplied input directly into a SQL query without any sanitization or parameterization. The username and password parameters come directly from user input and are inserted into the SQL string, allowing an attacker to inject arbitrary SQL commands."

#### 💥 Potential Exploit Scenario:
Provide a concrete example of how this could be exploited:

Example:
```
Attack Input:
- Username: admin' --
- Password: anything

Resulting Query:
SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything'

The '--' comment sequence causes the database to ignore the password check,
allowing authentication bypass.

More severe attack:
- Username: admin'; DROP TABLE users; --
Could result in complete data loss.
```

#### ✅ Recommended Secure Code:
```java
// Secure implementation using PreparedStatement
public ResultSet authenticateUser(String username, String password) {
    String query = "SELECT * FROM users WHERE username = ? AND password = ?";

    try {
        PreparedStatement pstmt = connection.prepareStatement(query);
        pstmt.setString(1, username);  // Automatically escapes special characters
        pstmt.setString(2, password);  // Prevents SQL injection

        ResultSet rs = pstmt.executeQuery();  // SAFE: Parameterized query

        if (rs.next()) {
            return rs;
        }
    } catch (SQLException e) {
        log.error("Authentication failed", e);
    }
    return null;
}
```

#### 📊 Business Impact:
- **Data Breach Risk**: Complete database access possible
- **Compliance Violations**: PCI-DSS 6.5.1, GDPR Article 32
- **Financial Impact**: Potential fines, breach notification costs
- **Reputation Damage**: Loss of customer trust
- **Recovery Time**: Days to weeks for incident response

---

## Common Vulnerability Templates

### SQL Injection (A03:2021)
```markdown
#### 🔍 Why This Is Vulnerable:
Direct string concatenation allows attackers to:
- Bypass authentication (OR 1=1)
- Extract sensitive data (UNION SELECT)
- Modify/delete data (UPDATE/DELETE/DROP)
- Execute system commands (xp_cmdshell)
```

### Cross-Site Scripting - XSS (A03:2021)
```markdown
#### 🔍 Why This Is Vulnerable:
Unescaped user input in HTML context allows:
- JavaScript execution in victim's browser
- Session cookie theft
- Phishing attacks via DOM manipulation
- Keylogging and form hijacking
```

### Hardcoded Credentials (A07:2021)
```markdown
#### 🔍 Why This Is Vulnerable:
Credentials in source code:
- Cannot be rotated without code deployment
- Visible in version control history
- Accessible to all developers
- May be exposed in compiled artifacts
```

### Weak Cryptography (A02:2021)
```markdown
#### 🔍 Why This Is Vulnerable:
Weak algorithms (MD5/SHA1/DES):
- Can be brute-forced with modern hardware
- Known collision attacks exist
- Rainbow tables available
- Compliance violation (requires strong crypto)
```

### Path Traversal (A01:2021)
```markdown
#### 🔍 Why This Is Vulnerable:
Unsanitized file paths allow:
- Access to sensitive system files (/etc/passwd)
- Reading application source code
- Accessing other users' data
- Potential remote code execution
```

## Required Elements Checklist

For EVERY security finding, ensure:

- [ ] SEC-XXX ID assigned sequentially
- [ ] Actual code block (10-15 lines) with line numbers
- [ ] Language-specific syntax highlighting
- [ ] Clear explanation of vulnerability mechanism
- [ ] Concrete exploit example
- [ ] Secure code alternative
- [ ] Business impact assessment
- [ ] OWASP category mapping
- [ ] REF-XXX citation to code location
- [ ] Severity rating with visual indicator

## Helper Functions for Agents

```python
def format_security_finding(finding):
    """Format a security finding according to template"""
    return f"""
### {finding['sec_id']}: {finding['type']}
- **Severity**: {get_severity_icon(finding['severity'])} {finding['severity'].upper()}
- **File**: `{finding['file']}:{finding['line']}` [REF-{finding['ref_id']}]
- **OWASP Category**: {finding['owasp_category']}

#### Vulnerable Code:
```{finding['language']}
{finding['code_block']}
```

#### 🔍 Why This Is Vulnerable:
{finding['vulnerability_explanation']}

#### 💥 Potential Exploit Scenario:
{finding['exploit_scenario']}

#### ✅ Recommended Secure Code:
```{finding['language']}
{finding['secure_code']}
```

#### 📊 Business Impact:
{finding['business_impact']}
"""

def get_severity_icon(severity):
    return {
        'Critical': '🔴',
        'High': '🟠',
        'Medium': '🟡',
        'Low': '⚪'
    }.get(severity, '⚪')
```

## Important Notes

1. **NO PLACEHOLDERS**: Every finding must have actual code from the codebase
2. **NO TRUNCATION**: Show enough code to understand the vulnerability
3. **REAL EXPLOITS**: Provide realistic attack scenarios, not theoretical
4. **ACTIONABLE FIXES**: Secure code must be directly applicable
5. **BUSINESS CONTEXT**: Impact must relate to actual business risks