# Security Guidelines for CollabHub

## ⚠️ CRITICAL: Never Commit Secrets to Git

### What NOT to Commit

**Never commit any of the following to git:**
- API keys (MailerSend, Stripe, OpenAI, etc.)
- SMTP credentials
- Database passwords
- OAuth client secrets
- GitHub personal access tokens
- Any value starting with: `sk_`, `pk_`, `mssp.`, `MS_`, `ghp_`, etc.

### Safe Practices

#### ✅ DO:
- Use placeholders in documentation: `[your-api-key]`, `[your-password]`
- Store credentials in `.env` (already in `.gitignore`)
- Add credentials to DigitalOcean App Platform environment variables
- Use examples like: `STRIPE_API_KEY=sk_test_example_not_real`
- Add security warnings in documentation files

#### ❌ DON'T:
- Copy actual credentials into README or documentation files
- Use real credentials in code examples
- Commit `.env` files (already ignored)
- Share credentials in commit messages

### Environment Variable Documentation Template

When documenting environment variables, always use this format:

```bash
# ❌ WRONG - Never do this:
API_KEY=actual_real_key_12345

# ✅ CORRECT - Always use placeholders:
API_KEY=[your-api-key-from-provider]
# Get from: Provider Dashboard → Settings → API Keys

# ✅ CORRECT - Use obvious fake examples:
STRIPE_API_KEY=sk_test_example_not_real_key
# Production: Get from Stripe Dashboard → Developers → API Keys
```

### Pre-Commit Checklist

Before committing, review:
1. Search for `mssp.`, `MS_`, `sk_`, `pk_`, `ghp_` in staged files
2. Check that any credentials are placeholders
3. Verify `.env` is not staged: `git status` should not show `.env`
4. Run: `git diff --cached` to review exactly what's being committed

### If You Accidentally Commit a Secret

1. **Immediately revoke the exposed credential**:
   - MailerSend: Dashboard → SMTP → Delete SMTP user → Create new
   - Stripe: Dashboard → Developers → API Keys → Revoke
   - GitHub: Settings → Developer Settings → Tokens → Delete
   
2. **Remove from git history** (if just committed):
   ```bash
   # If not pushed yet:
   git reset HEAD~1
   # Edit the file to remove credentials
   git add .
   git commit -m "SECURITY: Remove exposed credentials"
   
   # If already pushed (more complex):
   # Contact team to coordinate git history rewrite
   ```

3. **Generate new credentials**:
   - Create new API keys/passwords
   - Update in DigitalOcean environment variables
   - Update local `.env` file
   - Never commit the new credentials

4. **Notify team**:
   - Alert all developers that credentials were exposed
   - Coordinate rotating all affected credentials

### For AI Assistants / Copilot

When creating documentation:
- Always use `[placeholder-format]` for credentials
- Add security warnings in any credential-related sections
- Never copy real values from environment variables or settings
- If asked to document credentials, use fake/example values only

### Secret Scanning

GitHub automatically scans for exposed secrets. If you receive an alert:
1. Take it seriously - secrets are compromised immediately
2. Revoke the exposed credential within 1 hour
3. Generate new credentials
4. Update documentation to use placeholders
5. Push fix to remove the exposed value

### DigitalOcean Environment Variables

All production credentials should ONLY exist in:
- DigitalOcean App Platform → Settings → Environment Variables
- Local developer `.env` files (git-ignored)

Never in:
- Code files
- Configuration files committed to git
- Documentation files
- README files
- Comments in code

### Example: Safe Documentation

```markdown
## Email Setup

Add these environment variables to DigitalOcean:

```bash
EMAIL_HOST=smtp.mailersend.net
MAILERSEND_SMTP_USERNAME=[get-from-mailersend-dashboard]
MAILERSEND_SMTP_PASSWORD=[create-smtp-user-in-mailersend]
```

⚠️ **Security**: Never commit actual credentials. Get values from:
- MailerSend Dashboard → Email → SMTP → Create SMTP User
- Store in DigitalOcean environment variables only
```

---

**Remember**: Once a secret is committed to git, it's compromised forever in git history. Prevention is the only real security.
