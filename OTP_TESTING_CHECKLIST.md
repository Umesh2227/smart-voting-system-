# OTP Verification Testing Checklist

## Pre-Testing Setup
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database configured and running (MySQL)
- [ ] Application started: `python code/main.py`
- [ ] Application accessible at `http://localhost:5000`
- [ ] Phone number configured for testing (valid 10-digit number)

## Functional Testing

### 1. User Registration & Phone Number
- [ ] User can register with valid details
- [ ] Phone number field is required
- [ ] Phone number is saved to database
- [ ] Aadhar number is unique (no duplicates)
- [ ] Email validation works

### 2. OTP Generation & Sending
- [ ] OTP is 6 digits long
- [ ] OTP is numeric only (0-9)
- [ ] OTP changes each time (new OTP on resend)
- [ ] OTP is sent to correct phone number
- [ ] SMS is received within 5 seconds
- [ ] OTP message includes validity period information

### 3. OTP Verification - Valid Cases
- [ ] Correct OTP is accepted
- [ ] Page redirects to confirm vote after OTP verification
- [ ] Session variable `otp_verified` is set to True
- [ ] OTP is cleared from session after successful verification
- [ ] Success flash message is displayed

### 4. OTP Verification - Invalid Cases
- [ ] Wrong OTP is rejected with error message
- [ ] Attempt counter increments on wrong OTP
- [ ] After 3 wrong attempts, OTP is rejected and cleared
- [ ] Flash message shows remaining attempts
- [ ] User is redirected to request new OTP after 3 attempts

### 5. OTP Expiry
- [ ] OTP is valid for 10 minutes
- [ ] After 10 minutes, OTP is rejected as expired
- [ ] Expired OTP message is displayed
- [ ] User is redirected to request new OTP
- [ ] User can request new OTP successfully

### 6. Voting Flow with OTP
- [ ] User registers with phone number
- [ ] User logs in with Aadhar
- [ ] User selects candidate
- [ ] System redirects to OTP sending
- [ ] OTP is sent to phone
- [ ] User enters OTP
- [ ] After OTP verification, user can confirm vote
- [ ] Vote is recorded in database
- [ ] User cannot vote twice (already voted check works)

### 7. Database Integration
- [ ] Vote is recorded with correct aadhar
- [ ] Vote count is accurate in admin dashboard
- [ ] No OTP data is stored in database (session only)
- [ ] Vote results show correct candidate counts

## Edge Cases & Error Handling

### Phone Number Validation
- [ ] User cannot proceed to voting without phone number
- [ ] User is redirected to update profile if phone missing
- [ ] Valid 10-digit phone numbers are accepted
- [ ] Invalid phone numbers show error message

### Session Management
- [ ] OTP is stored in session (server-side)
- [ ] OTP is cleared after verification
- [ ] OTP is cleared after expiry
- [ ] OTP is cleared after max attempts exceeded
- [ ] Session timeout doesn't affect voting process (if timeout > OTP validity)

### SMS Failures
- [ ] If SMS fails, OTP is displayed in flash message
- [ ] Voting can proceed with displayed OTP
- [ ] Error message suggests checking fallback OTP
- [ ] Application doesn't crash on SMS failure

### Concurrent Voters
- [ ] Multiple users can vote simultaneously
- [ ] Each user gets unique OTP
- [ ] OTP for one user doesn't work for another
- [ ] Session isolation is maintained

## UI/UX Testing

### Verify OTP Page
- [ ] Page layout is centered and visually appealing
- [ ] Page title is clear: "Verify Your Vote"
- [ ] Instructions are clear and helpful
- [ ] OTP input field accepts only numbers
- [ ] OTP input field is properly focused
- [ ] Submit button is clearly visible
- [ ] Resend OTP option is available
- [ ] Back to voting link is available
- [ ] Flash messages are properly styled

### Responsive Design
- [ ] OTP page works on desktop (1920x1080)
- [ ] OTP page works on tablet (768px width)
- [ ] OTP page works on mobile (320px width)
- [ ] Input fields are properly sized
- [ ] Buttons are clickable on touch devices
- [ ] Text is readable on all devices

### Navigation
- [ ] User can navigate back to voting page
- [ ] User can request new OTP
- [ ] User can logout from OTP page
- [ ] Navigation links work correctly
- [ ] Navbar is consistent with other pages

## Security Testing

### OTP Security
- [ ] OTP is not visible in URL
- [ ] OTP is not visible in page source
- [ ] OTP is not logged in server logs
- [ ] OTP is not sent via unencrypted channels (HTTPS in production)
- [ ] OTP cannot be brute-forced (3 attempt limit)

### Session Security
- [ ] OTP is session-based (not URL-based)
- [ ] Expired session clears OTP
- [ ] User cannot access OTP from another session
- [ ] Session hijacking doesn't expose OTP

### Vote Security
- [ ] Vote cannot be cast without OTP verification
- [ ] Double voting prevention still works
- [ ] Vote and voter are correctly linked
- [ ] Vote integrity is maintained

## Performance Testing

### Response Time
- [ ] OTP generation is instant (< 100ms)
- [ ] OTP verification is fast (< 500ms)
- [ ] Page load time is acceptable (< 2 seconds)
- [ ] SMS sending is non-blocking (doesn't delay page)

### Database Load
- [ ] No unnecessary database queries
- [ ] Vote recording is efficient
- [ ] Multiple concurrent OTP operations don't slow system

## Regression Testing

### Existing Features
- [ ] Admin login still works
- [ ] Nominee management still works
- [ ] Voter registration still works (with new OTP)
- [ ] Results display still works
- [ ] Logout still works
- [ ] Previous vote history is accessible

### Database Integrity
- [ ] No data corruption in vote table
- [ ] No data corruption in voters table
- [ ] No data corruption in nominee table
- [ ] Database transactions are consistent

## Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Accessibility Testing

- [ ] Forms are accessible via keyboard
- [ ] Error messages are clear
- [ ] Color contrast is sufficient (WCAG AA standard)
- [ ] Font size is readable
- [ ] Input labels are properly associated
- [ ] Page is readable without CSS

## Load Testing (Optional)

- [ ] System handles 10 simultaneous OTP requests
- [ ] System handles 50 simultaneous OTP requests
- [ ] System handles 100 concurrent votes
- [ ] No memory leaks with extended testing
- [ ] Session cleanup works properly

## Documentation Review

- [ ] OTP_IMPLEMENTATION.md is complete and accurate
- [ ] OTP_QUICK_START.md has correct instructions
- [ ] Code comments are clear and helpful
- [ ] Function docstrings are present
- [ ] README.md mentions OTP feature (if applicable)

## Final Sign-Off

- [ ] All critical tests passed
- [ ] All important tests passed
- [ ] Edge cases handled properly
- [ ] No blocking issues found
- [ ] Performance is acceptable
- [ ] Security measures are in place
- [ ] User experience is good
- [ ] Documentation is complete

## Notes & Issues Found

| Issue # | Description | Severity | Status | Resolution |
|---------|-------------|----------|--------|-----------|
|         |             |          |        |           |

## Testing Date: ________________
## Tested By: ___________________
## Sign-off: ____________________

---

**Test Coverage: [  ]%**
**Overall Status: ☐ PASS / ☐ FAIL / ☐ CONDITIONAL PASS**

### Conditional Pass Notes:
(If applicable, document any known issues or conditional requirements)
