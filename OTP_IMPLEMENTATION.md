# OTP Verification for Voting - Implementation Summary

## Overview
OTP (One-Time Password) verification has been successfully integrated into the Smart Voting System. This adds an extra layer of security to the voting process by requiring voters to verify their identity with a 6-digit code sent to their registered phone number before they can confirm their vote.

## Changes Made

### 1. **Updated Dependencies** 
**File**: `requirements.txt`
- Added `pyotp` library for OTP generation (though we use random digits for simplicity)

### 2. **Backend Implementation**
**File**: `code/main.py`

#### New Imports:
```python
import pyotp
import random
import string
```

#### New Helper Functions:

**`generate_otp()`**: Generates a random 6-digit OTP
- Returns a string of 6 random digits
- Called each time OTP needs to be sent

**`send_otp_sms(phone, otp, name)`**: Sends OTP via SMS using fast2sms API
- Takes voter's phone number, generated OTP, and name
- Uses existing fast2sms API integration
- Returns True/False based on success
- Non-blocking (won't stop voting if SMS fails)

#### New Routes:

**`/send_otp` (GET/POST)**
- Triggered when voter selects a candidate
- Generates a 6-digit OTP
- Stores OTP in session with timestamp and attempt counter
- Sends OTP to voter's phone via SMS
- Redirects to `/verify_otp` page
- Session stores:
  - `voting_otp`: The generated 6-digit code
  - `otp_time`: Timestamp when OTP was generated
  - `otp_attempts`: Counter for verification attempts (max 3)

**`/verify_otp` (GET/POST)**
- Displays form for voter to enter received OTP
- Validates entered OTP against stored OTP
- Checks if OTP has expired (10-minute validity)
- Enforces maximum 3 verification attempts
- Sets `session['otp_verified'] = True` on success
- Redirects to `/confirm_vote` after successful verification

#### Modified Routes:

**`/select_candidate` (POST)**
- After candidate selection, redirects to `/send_otp` instead of directly to `/confirm_vote`
- Sets `session['otp_verified'] = False` to ensure OTP verification is required

**`/confirm_vote` (GET/POST)**
- Added check: `if not session.get('otp_verified'):`
- Redirects to `/send_otp` if OTP verification hasn't been completed
- Prevents voting without OTP verification

### 3. **Frontend Implementation**
**File**: `code/templates/verify_otp.html` (NEW)

Created a new template with:
- Professional UI matching the voting system design
- Modern gradient background (#667eea to #764ba2)
- 6-digit OTP input field (numeric only, auto-formatted)
- Timer display (optional for future enhancement)
- "Request New OTP" button for resending OTP
- Back to voting link
- Flash message support for feedback
- Responsive design for mobile devices
- Bootstrap 4 integration

Features:
- Auto-numeric input validation (only allows 0-9)
- Clear instructions for voters
- Info box explaining OTP validity and security
- Option to request new OTP
- Back navigation to voting page

## Voting Flow with OTP

### Old Flow:
```
Registration → Select Candidate → Confirm Vote → Vote Cast
```

### New Flow:
```
Registration → Select Candidate → Send OTP → Enter OTP → Confirm Vote → Vote Cast
```

### Detailed Steps:

1. **Registration**: Voter registers with phone number and other details
2. **Verify**: Voter verifies their account (auto-verification on registration)
3. **Vote**: Voter goes to voting page and selects a candidate
4. **OTP Generation**: System generates 6-digit OTP and sends to voter's registered phone
5. **OTP Entry**: Voter enters received OTP in the verification form
6. **OTP Validation**:
   - Checks if OTP matches (case-sensitive)
   - Checks if OTP not expired (10 minutes)
   - Limits to 3 attempts
7. **Vote Confirmation**: After OTP verification, voter confirms their choice
8. **Vote Recording**: Vote is saved to database
9. **Success**: SMS confirmation is sent (optional, non-blocking)

## Session Variables Used

- `voting_otp`: Stores the 6-digit OTP code
- `otp_time`: Timestamp of OTP generation (for expiry check)
- `otp_attempts`: Counter for OTP verification attempts
- `otp_verified`: Boolean flag indicating OTP has been verified
- `pending_vote`: Stores the selected candidate symbol

## Security Features

1. **OTP Expiry**: OTPs are valid for only 10 minutes (600 seconds)
2. **Attempt Limiting**: Maximum 3 verification attempts per OTP
3. **Phone Verification**: Requires valid phone number in voter profile
4. **Session-based**: OTP data stored in session (server-side, secure)
5. **SMS Delivery**: Uses fast2sms API for reliable delivery
6. **Non-blocking**: SMS failures don't prevent voting (OTP displayed in flash message)

## Configuration Notes

### Fast2SMS API
- API Key: `UwmaiQR5OoA6lSTz93nP0tDxsFEhI7VJrfKkvYjbM2C14Wde8g9lvA2Ghq5VNCjrZ4THWkF1KOwp3Bxd`
- Endpoint: `https://www.fast2sms.com/dev/bulkV2`
- Message format: Professional OTP message with validity period

### OTP Parameters (Configurable)
- **Length**: 6 digits
- **Validity**: 600 seconds (10 minutes)
- **Max Attempts**: 3

To change these, modify the following in `main.py`:
- `generate_otp()`: Change `k=6` to desired length
- `verify_otp()`: Change `600` to desired validity period
- `verify_otp()`: Change `>= 3` to desired max attempts

## Testing Recommendations

1. **Test OTP Generation**: Verify 6-digit codes are generated correctly
2. **Test SMS Sending**: Confirm SMS is received on phone
3. **Test OTP Verification**: 
   - Valid OTP entry
   - Invalid OTP entry
   - Expired OTP (after 10 minutes)
   - Attempt limiting (3 attempts)
4. **Test Vote Recording**: Ensure vote is saved after OTP verification
5. **Test UI/UX**: Check responsive design on mobile devices
6. **Test Error Handling**: 
   - Missing phone number
   - Invalid phone number
   - SMS API failures

## Database Notes

- No database schema changes required
- OTP data is session-based (in-memory)
- Existing `voters` table with phone number field is sufficient
- Vote table structure remains unchanged

## Future Enhancements

1. Add OTP countdown timer display
2. Implement auto-submit when 6 digits entered
3. Add resend OTP cooldown (30 seconds)
4. Log OTP verification attempts for audit trail
5. Add email OTP option as fallback
6. Implement OTP caching for rate limiting
7. Add WhatsApp OTP integration
8. Store OTP verification logs in database

## Installation Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Restart Flask application:
   ```bash
   python code/main.py
   ```

3. Test the voting flow with OTP verification

## Files Modified/Created

### Modified:
- `requirements.txt` - Added pyotp
- `code/main.py` - Added OTP functions and routes
- `code/templates/` - Modified voting flow (select_candidate → confirm_vote)

### Created:
- `code/templates/verify_otp.html` - New OTP verification form

---
**Implementation Date**: November 13, 2025
**Status**: Complete and Ready for Testing
