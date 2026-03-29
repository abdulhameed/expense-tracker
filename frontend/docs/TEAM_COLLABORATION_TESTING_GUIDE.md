# Team Collaboration Feature - Testing Guide

**Date:** March 29, 2026
**Status:** ✅ Ready for Testing
**Dev Server:** http://localhost:3001

---

## Quick Start

The development server is running and has compiled all team collaboration code successfully:
- ✅ New components compiled
- ✅ New pages compiled
- ✅ New services compiled
- ✅ Routes registered
- ✅ All imports resolved

Navigate to: **http://localhost:3001**

---

## Testing Scenarios

### 1. **Team Members Management** (`/projects/:projectId/team`)

**Setup:**
1. Log in to your account
2. Navigate to or create a project
3. Go to `/projects/{projectId}/team`

**Test Cases:**

**TC1.1: View Team Members**
- [ ] Page loads with project name displayed
- [ ] All team members are listed with avatars
- [ ] Member names, emails, and roles are visible
- [ ] Join date is displayed for each member
- [ ] Avatar shows initials (fallback if no image)

**TC1.2: Invite New Member**
- [ ] "Invite Member" button is visible (for owner/admin)
- [ ] Click button opens the InviteMemberModal
- [ ] Modal displays project name
- [ ] Email input accepts valid email format
- [ ] Role dropdown shows: Viewer, Member, Admin
- [ ] Role descriptions appear when selecting roles
- [ ] Submit button sends invitation
- [ ] Success message appears
- [ ] Modal closes after successful invitation
- [ ] New member appears in the list

**TC1.3: Change Member Role**
- [ ] Only owner/admin can see role dropdown
- [ ] Dropdown shows available roles (viewer, member, admin)
- [ ] Cannot change owner's role
- [ ] Role change persists after page reload
- [ ] Success message appears after change

**TC1.4: View Member Permissions**
- [ ] "Permissions" button visible for each member
- [ ] Click opens MemberPermissionsDisplay modal
- [ ] Modal shows:
  - Member's role with description
  - All 5 permissions with visual indicators (checkmark/X)
  - Member email and join date
- [ ] Permissions are correct for each role

**TC1.5: Remove Member**
- [ ] "Remove" button only visible for non-owner members
- [ ] Click opens confirmation modal
- [ ] Modal shows member name and warning
- [ ] Confirms action before deletion
- [ ] Member removed from list
- [ ] Success message appears

**TC1.6: Validation & Error Handling**
- [ ] Cannot invite already-member email
- [ ] Invalid email format shows error
- [ ] Empty email shows validation error
- [ ] API errors display user-friendly messages
- [ ] Network errors handled gracefully

**TC1.7: Responsive Design**
- [ ] Page works on desktop (1920px, 1366px)
- [ ] Page works on tablet (768px)
- [ ] Page works on mobile (375px)
- [ ] Member cards stack on smaller screens
- [ ] Action buttons remain accessible

---

### 2. **Invitation Management** (`/invitations`)

**Test Cases:**

**TC2.1: View Pending Invitations**
- [ ] Page loads with title "Project Invitations"
- [ ] All pending invitations are listed
- [ ] Each invitation shows:
  - Project name
  - Role (with badge color)
  - Inviter email
  - Expiration date
- [ ] Count of pending invitations displayed

**TC2.2: Accept Invitation**
- [ ] "Accept" button visible for each invitation
- [ ] Click opens confirmation modal
- [ ] Modal shows project name and role
- [ ] Confirm button accepts invitation
- [ ] Invitation removed from list
- [ ] Success message "You have joined the X project!"
- [ ] User can now access the project

**TC2.3: Decline Invitation**
- [ ] "Decline" button visible for each invitation
- [ ] Click immediately declines (or shows confirm)
- [ ] Invitation removed from list
- [ ] Success message appears
- [ ] User no longer sees this invitation

**TC2.4: Expired Invitations**
- [ ] Expired invitations show "Expired" badge
- [ ] Cannot accept/decline expired invitations
- [ ] Action buttons disabled for expired
- [ ] Message indicates expiration

**TC2.5: Empty State**
- [ ] When no invitations, shows helpful message
- [ ] Suggests user may request invitations
- [ ] Icon displayed for visual context

**TC2.6: Help Information**
- [ ] Help section visible with invitation info
- [ ] Explains:
  - Invitations expire after 7 days
  - Can only accept once
  - How to request new invitations
  - Role determination

**TC2.7: Responsive Design**
- [ ] Works on all screen sizes
- [ ] Invitation cards readable on mobile
- [ ] Buttons remain accessible

---

### 3. **Accessibility Testing**

**WCAG 2.1 AA Compliance:**

**TC3.1: Keyboard Navigation**
- [ ] Can tab through all interactive elements
- [ ] Focus indicators visible
- [ ] Modals trap focus properly
- [ ] Tab order is logical
- [ ] Escape key closes modals

**TC3.2: Screen Reader**
- [ ] All buttons have accessible labels
- [ ] Form inputs have associated labels
- [ ] Modal titles announced
- [ ] Error messages announced
- [ ] Roles and permissions are readable

**TC3.3: Color Contrast**
- [ ] Text meets 4.5:1 ratio minimum
- [ ] Role badges have sufficient contrast
- [ ] Error messages are visible

**TC3.4: Semantic HTML**
- [ ] Proper heading hierarchy
- [ ] List semantics used
- [ ] Form elements properly tagged
- [ ] Landmark regions identified

---

### 4. **Role-Based Permissions Testing**

**Owner Role:**
- [ ] Can view all team members
- [ ] Can invite members
- [ ] Can change member roles
- [ ] Can remove members (except self)
- [ ] Cannot be removed

**Admin Role:**
- [ ] Can view all team members
- [ ] Can invite members
- [ ] Can change non-owner roles
- [ ] Can remove non-owner members

**Member Role:**
- [ ] Can view team members
- [ ] Cannot invite members
- [ ] Cannot change roles
- [ ] Cannot remove members
- [ ] Can create/edit transactions

**Viewer Role:**
- [ ] Can view team members
- [ ] Cannot invite members
- [ ] Cannot change roles
- [ ] Cannot remove members
- [ ] Cannot create transactions

---

### 5. **Error Scenarios**

**TC5.1: Network Errors**
- [ ] Timeout during member load shows error
- [ ] Invitation send failure shows message
- [ ] User can retry operations
- [ ] Helpful error messages displayed

**TC5.2: API Errors**
- [ ] 401 Unauthorized redirects to login
- [ ] 403 Forbidden shows permission error
- [ ] 404 Not Found shows project not found
- [ ] 400 Bad Request shows validation error

**TC5.3: Validation**
- [ ] Empty email rejected
- [ ] Invalid email format rejected
- [ ] Duplicate email invitation blocked
- [ ] Already-member email blocked

---

### 6. **Performance Testing**

**TC6.1: Load Time**
- [ ] TeamMembers page loads < 2 seconds
- [ ] Invitations page loads < 2 seconds
- [ ] Modals open instantly

**TC6.2: List Performance**
- [ ] Page handles 50+ members smoothly
- [ ] Scrolling is smooth
- [ ] No lag when interacting

**TC6.3: State Management**
- [ ] Updates reflect immediately (optimistic)
- [ ] No duplicate requests
- [ ] State syncs across pages

---

## Test Data Preparation

### Create Test Scenarios

**Scenario 1: Project with Multiple Members**
```bash
1. Create project "Team Project"
2. Invite test@example.com as Member
3. Invite admin@example.com as Admin
4. Invite viewer@example.com as Viewer
5. Verify members list
```

**Scenario 2: Multiple Pending Invitations**
```bash
1. Log in as different user
2. Navigate to /invitations
3. Should see multiple pending invitations
4. Accept one, decline another
5. Verify actions complete
```

**Scenario 3: Permission Testing**
```bash
1. Create project with multiple roles
2. Log in as each role
3. Verify visible/hidden UI elements
4. Verify action availability
5. Verify permission errors
```

---

## Component Testing Checklist

### MemberCard Component
- [ ] Renders member info correctly
- [ ] Shows correct role badge
- [ ] Displays avatar with initials
- [ ] Action buttons visible when appropriate
- [ ] Owner indicator shown for project owner
- [ ] Accessibility features present

### InviteMemberModal Component
- [ ] Modal opens/closes properly
- [ ] Form validation working
- [ ] Email validation correct
- [ ] Role selection works
- [ ] Submit button functional
- [ ] Error messages display
- [ ] Loading state working

### MemberPermissionsDisplay Component
- [ ] Modal displays correctly
- [ ] Role description accurate
- [ ] Permission checklist complete
- [ ] Visual indicators (checkmark/X) correct
- [ ] Member metadata displayed

---

## Browser Compatibility Testing

**Minimum Browsers:**
- [ ] Chrome/Edge 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Mobile Safari (iOS 14+)
- [ ] Chrome Mobile (Android)

**Test Steps:**
1. Test in each browser
2. Verify layout responsive
3. Check form interactions
4. Verify modals work
5. Test keyboard navigation

---

## Integration Testing

### With Existing Features

**TC-INT1: Transaction Creation**
- [ ] Only members with permission can create transactions
- [ ] Viewer role cannot create
- [ ] Member/Admin can create

**TC-INT2: Report Access**
- [ ] Members can view reports based on role
- [ ] Viewers can see reports
- [ ] All can view own data

**TC-INT3: Dashboard**
- [ ] Dashboard works with team project
- [ ] Data filtered by project
- [ ] Team stats display correctly

**TC-INT4: Navigation**
- [ ] Team link appears in project
- [ ] Navigation to invitations works
- [ ] Back button functions
- [ ] Breadcrumbs update correctly

---

## Test Execution Guide

### Manual Testing Workflow

```
1. Start dev server:
   npm run dev

2. Open browser:
   http://localhost:3001

3. Login or register

4. Test each scenario from TC1-TC6 above

5. Document any issues

6. Test on mobile device:
   - Open DevTools (F12)
   - Click device toolbar
   - Select mobile size
   - Test responsive behavior
```

### Automated Testing

```bash
# Run all tests
npm run test

# Run specific test file
npm run test TeamMembers

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

---

## Reporting Issues

**Format for Bug Reports:**
```
Title: [Component] Brief Description
Steps to Reproduce:
1.
2.
3.

Expected Result:

Actual Result:

Screenshots/Videos:

Browser/Device:
```

---

## Sign-Off Checklist

- [ ] All test scenarios pass
- [ ] No critical bugs found
- [ ] Accessibility compliance verified
- [ ] Performance acceptable
- [ ] Mobile responsive
- [ ] Browser compatibility confirmed
- [ ] Integration with existing features working
- [ ] Error handling adequate
- [ ] Documentation complete

---

## Notes

- Dev server: http://localhost:3001
- Backend API: http://localhost:8000
- All team collaboration routes are protected (require login)
- Team features use the existing auth system
- No additional backend configuration needed

---

**Ready to test! Happy clicking! 🧪**
