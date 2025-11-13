# OTP Verification - Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VOTING SYSTEM WITH OTP                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Registration │  │ Voting Page  │  │ OTP Verify   │       │
│  │    Form      │  │   Candidates │  │    Form      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
           ↓                  ↓                  ↓
┌──────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Routes                             │   │
│  │  • /register        (voter registration)             │   │
│  │  • /voting          (show candidates)                │   │
│  │  • /select_candidate (save selected candidate)       │   │
│  │  ★ /send_otp       (NEW - generate & send OTP)      │   │
│  │  ★ /verify_otp     (NEW - verify OTP entry)         │   │
│  │  • /confirm_vote    (finalize vote)                  │   │
│  │  • /voting_res      (show results)                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Helper Functions                          │   │
│  │  ★ generate_otp()      (create 6-digit code)        │   │
│  │  ★ send_otp_sms()      (send via SMS)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Session Management                        │   │
│  │  • voting_otp          (6-digit code)                │   │
│  │  • otp_time            (generation timestamp)        │   │
│  │  • otp_attempts        (attempt counter)             │   │
│  │  • otp_verified        (verification flag)           │   │
│  │  • pending_vote        (selected candidate)          │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
           ↓                  ↓                  ↓
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌──────────────┐              ┌──────────────┐             │
│  │   MySQL DB   │              │ Fast2SMS API │             │
│  │ (store votes)│              │ (send OTP)   │             │
│  └──────────────┘              └──────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

## Voting Flow - Detailed Sequence

```
VOTER                SYSTEM                 SMS SERVICE           DATABASE
  │                   │                          │                    │
  │ 1. Register       │                          │                    │
  ├──────────────────→│                          │                    │
  │                   │ Verify Details           │                    │
  │                   │ Check Phone              │                    │
  │                   │──────────────────────────────────────────────→│
  │                   │ Save voter data          │                    │
  │                   │                          │                    │
  │ 2. Login (Aadhar) │                          │                    │
  ├──────────────────→│                          │                    │
  │                   │ Fetch voter              │                    │
  │                   │─────────────────────────────────────────────→│
  │                   │ Verify logged in         │                    │
  │                   │                          │                    │
  │ 3. Select Candidate
  ├──────────────────→│                          │                    │
  │                   │ Save to session:         │                    │
  │                   │ • pending_vote           │                    │
  │                   │ • otp_verified = false   │                    │
  │                   │ Redirect /send_otp       │                    │
  │                   │                          │                    │
  │ 4. Send OTP (Automatic)                      │                    │
  │ ← ─ ─ ─ ─ ─ ─ ─ ─│ Generate 6-digit code    │                    │
  │ Show Loading      │ Store in session:        │                    │
  │                   │ • voting_otp = CODE      │                    │
  │                   │ • otp_time = NOW         │                    │
  │                   │ • otp_attempts = 0       │                    │
  │                   │                          │                    │
  │                   │ Send SMS                 │                    │
  │                   ├─────────────────────────→│                    │
  │                   │                          │ Deliver to +91...  │
  │ ← ─ ─ ─ ─ ─ ─ ─ ─│ SMS Sent                 │                    │
  │                   │ Show OTP form            │                    │
  │                   │                          │                    │
  │ 5. Receive SMS    │                          │                    │
  │ Read OTP: 123456  │                          │                    │
  │                   │                          │                    │
  │ 6. Enter OTP      │                          │                    │
  ├──────────────────→│ POST /verify_otp         │                    │
  │                   │ Check entered OTP        │                    │
  │                   │ Validate:                │                    │
  │                   │ • Matches stored? ✓      │                    │
  │                   │ • Not expired? ✓         │                    │
  │                   │ • Attempts < 3? ✓        │                    │
  │ ← ─ ─ ─ ─ ─ ─ ─ ─│ "OTP Verified!"          │                    │
  │                   │ Set otp_verified = true  │                    │
  │                   │ Clear OTP data           │                    │
  │                   │ Redirect /confirm_vote   │                    │
  │                   │                          │                    │
  │ 7. Confirm Vote   │                          │                    │
  ├──────────────────→│ POST /confirm_vote       │                    │
  │                   │ Check otp_verified = yes │                    │
  │                   │ Check double voting      │                    │
  │                   │ Insert vote              │                    │
  │                   ├─────────────────────────────────────────────→│
  │                   │                          │                    │ Save vote
  │                   │                          │                    │
  │                   │ Send SMS notification    │                    │
  │                   ├─────────────────────────→│                    │
  │                   │                          │ "Vote Cast Success"│
  │                   │                          │                    │
  │ ← ─ ─ ─ ─ ─ ─ ─ ─│ "Vote Cast Successfully" │                    │
  │ Voting Complete   │                          │                    │
```

## OTP Verification State Machine

```
                    ┌─────────────────────┐
                    │   Vote Selected     │
                    │   pending_vote set  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Generate OTP      │
                    │ 6-digit code        │
                    │ Store in session    │
                    │ Start 10min timer   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Send OTP via SMS  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Waiting for Input   │
                    │ OTP Entry Form      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
           ┌────────▼────────┐  ┌────────▼────────┐
           │ Correct OTP     │  │ Wrong OTP       │
           │ NOT Expired     │  │ OR Expired      │
           │ < 3 Attempts    │  │ OR 3+ Attempts  │
           │                 │  │                 │
           │ ┌─────────────┐ │  │ ┌─────────────┐ │
           │ │Increment:   │ │  │ │Increment    │ │
           │ │otp_attempts │ │  │ │attempts++   │ │
           │ │             │ │  │ │             │ │
           │ │Set:         │ │  │ │If attempts=3│ │
           │ │otp_verified │ │  │ │Clear OTP    │ │
           │ │= true       │ │  │ │Redirect to  │ │
           │ │             │ │  │ │voting page  │ │
           │ │Clear OTP    │ │  │ │             │ │
           │ │data         │ │  │ │Else:        │ │
           │ └─────────────┘ │  │ │Show remaining
           │                 │  │ │attempts     │ │
           │                 │  │ │Reload form  │ │
           └────────┬────────┘  └────────┬────────┘
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Confirm Vote Page   │
                    │ Check vote details  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Cast Vote          │
                    │  Save to Database   │
                    │  Send Confirmation  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Voting Complete ✓   │
                    │ Show Results        │
                    └─────────────────────┘
```

## Session Data Lifecycle

```
TIME: 0s
├─ Voter selects candidate
└─ pending_vote = "symbol123"
   otp_verified = false

TIME: 2s (POST /send_otp)
├─ Generate random 6-digit OTP
├─ voting_otp = "123456"
├─ otp_time = current_timestamp
├─ otp_attempts = 0
└─ SMS sent to phone

TIME: 30s (Voter enters OTP)
├─ User enters "123456" in form
└─ POST /verify_otp with form data

TIME: 31s (Verification Process)
├─ Check: time_elapsed < 600s? → YES ✓
├─ Check: otp_attempts < 3? → YES ✓
├─ Check: entered_otp == voting_otp? → YES ✓
├─ otp_verified = true
├─ Clear: voting_otp
├─ Clear: otp_time
├─ Clear: otp_attempts
└─ Redirect to /confirm_vote

TIME: 40s (Vote Confirmation)
├─ Check: otp_verified == true? → YES ✓
├─ Insert vote into database
├─ Send confirmation SMS
├─ Clear: pending_vote
└─ Redirect to home/results

TIME: 600s+ (If user didn't verify)
├─ OTP expires
├─ Next verification attempt fails
└─ User must request new OTP
```

## Error Handling Flow

```
START: OTP Verification
│
├─→ Is OTP Expired? (> 600s)
│   └─→ YES: Clear OTP, Show "OTP Expired", Redirect to /voting
│   └─→ NO: Continue
│
├─→ Attempts Exceeded? (>= 3)
│   └─→ YES: Clear OTP, Show "Max Attempts", Redirect to /voting
│   └─→ NO: Continue
│
├─→ OTP Matches?
│   └─→ YES: Set verified, Clear OTP, Redirect to /confirm_vote
│   └─→ NO: 
│       ├─→ Increment attempts
│       ├─→ Calculate remaining = 3 - attempts
│       ├─→ Show "Wrong OTP, X attempts remaining"
│       └─→ Reload verification form
│
END: User either verifies or loses OTP
```

## Database Impact (None!)

```
EXISTING TABLES:
┌─────────────────────────┐
│      voters table       │
├─────────────────────────┤
│ • aadhar_id (PK)        │
│ • first_name            │
│ • pno ← Phone needed     │
│ • email                 │
│ • verified              │
│ • (no OTP column)       │
└─────────────────────────┘

┌─────────────────────────┐
│      vote table         │
├─────────────────────────┤
│ • vote (candidate)      │
│ • aadhar (voter)        │
│ • (no OTP column)       │
└─────────────────────────┘

┌─────────────────────────┐
│    nominee table        │
├─────────────────────────┤
│ • symbol_name (PK)      │
│ • member_name           │
│ • party_name            │
│ • (no OTP column)       │
└─────────────────────────┘

SESSION STORAGE (Server-side):
┌─────────────────────────┐
│    Flask Session        │
├─────────────────────────┤
│ • voting_otp            │ ← Stored here (not DB)
│ • otp_time              │ ← Stored here (not DB)
│ • otp_attempts          │ ← Stored here (not DB)
│ • otp_verified          │ ← Stored here (not DB)
│ • pending_vote          │ ← Stored here (not DB)
└─────────────────────────┘
```

## Component Interaction Diagram

```
┌──────────────┐
│   Browser    │──────┐
│   (Voter)    │      │ HTTP Requests/Responses
└──────────────┘      │
                      ▼
┌──────────────────────────────────────┐
│      Flask Web Application           │
│  ┌────────────────────────────────┐  │
│  │   Route: /send_otp             │  │
│  │  • Get voter phone             │  │
│  │  • Generate OTP                │  │
│  │  • Store in session            │  │
│  │  • Call send_otp_sms()         │  │
│  └────────────────────────────────┘  │
│                 │                     │
│                 ▼                     │
│  ┌────────────────────────────────┐  │
│  │   Route: /verify_otp           │  │
│  │  • Get form input OTP          │  │
│  │  • Validate expiry             │  │
│  │  • Validate attempts           │  │
│  │  • Compare OTP                 │  │
│  │  • Set otp_verified flag       │  │
│  └────────────────────────────────┘  │
│                 │                     │
│  ┌──────────────┴──────────────────┐  │
│  ▼              ▼          ▼       ▼  │
│ Session    MySQL DB    Fast2SMS  Logs │
└──────────────────────────────────────┘
```

---

**These diagrams show the complete OTP verification flow and architecture for the Smart Voting System.**
