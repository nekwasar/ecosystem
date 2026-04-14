# Ecosystem Upgrades TODO

## Current Services (7)
| Service | Domain | Status |
|---------|--------|--------|
| Admin | admin.nekwasar.com | Keep, Upgrade |
| Agent | agent.nekwasar.com | Keep |
| Blog | blog.nekwasar.com | Keep |
| Store | store.nekwasar.com | Keep |
| Portfolio | nekwasar.com | Keep |
| Gigs | gigs.nekwasar.com | Keep |
| CDN | cdn.nekwasar.com | Keep |
| ~~Mail~~ | ~~mail.nekwasar.com~~ | **REMOVE** (using aapanel) |

---

## TODO Items

### 1. Remove Mail Service
- [ ] Delete services/mail/ directory
- [ ] Remove mail service from docker-compose.yml
- [ ] Update nginx config to remove mail references
- [ ] Keep mail.nekwasar.com pointing to aapanel webmail

### 2. Add Notifications to Admin
- [ ] Create notification system in admin
- [ ] Types: In-app toast, Email, Push
- [ ] Triggers: New order, New subscriber, New comment, etc.
- [ ] Notification center in admin header
- [ ] Mark as read/unread
- [ ] Notification preferences settings

### 3. Create Support System (NEW SERVICE)
**help.nekwasar.com (Customer Portal)**
- [ ] Create services/help/ service
- [ ] Customer ticket submission (name, email, subject, message)
- [ ] Ticket status tracking (Open, In Progress, Resolved, Closed)
- [ ] Customer login/auth (via store account or magic link)
- [ ] Ticket history view
- [ ] Add attachments to tickets

**admin.nekwasar.com (Agent Panel)**
- [ ] Ticket inbox in admin
- [ ] Assign tickets to agents
- [ ] Reply to tickets
- [ ] Status management
- [ ] Priority levels (Low, Medium, High, Urgent)
- [ ] Auto-respond rules
- [ ] Ticket categories/tags

### 4. Create API Developer Portal (NEW SERVICE)
**api.nekwasar.com**
- [ ] Create services/api-portal/ service
- [ ] Auto-generated API docs from code (Swagger/OpenAPI)
- [ ] API key management (generate, revoke)
- [ ] Usage analytics per API key
- [ ] Rate limiting display
- [ ] Sandbox/Playground for API testing
- [ ] Code examples in multiple languages
- [ ] Webhook configuration UI

**admin.nekwasar.com (API Management)**
- [ ] View all API keys
- [ ] Monitor API usage
- [ ] Manage rate limits
- [ ] API analytics dashboard

### 5. Add AI Panel to Admin
- [ ] Chat interface with Agent service
- [ ] Quick actions: Generate content, Analyze data, etc.
- [ ] AI settings configuration

---

## Implementation Order
1. Remove Mail Service
2. Add Notifications to Admin
3. Create Support System (Help + Admin panel)
4. Create API Developer Portal
5. Add AI Panel to Admin

---

## Notes
- Webmail stays at mail.nekwasar.com via aapanel
- help.nekwasar.com is customer-facing support portal
- api.nekwasar.com is for external developers
- admin.nekwasar.com remains for internal management
