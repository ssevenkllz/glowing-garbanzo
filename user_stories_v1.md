# ZERO CORP TRAVEL COPILOT
## User Stories & Actor Definitions — v1
### Project: Intelligent Travel Companion Copilot (Hackathon Brief)

---

## CAST OF ACTORS

### Kelli Chen — VP of Client Partnerships
**Role:** Primary traveler, experienced, executive-level
**Travel Policy Tier:** Executive (Business class authorized on flights 9hr+, Tier 1 hotel caps, VP approval authority)
**Travel Profile:** Frequent traveler, 3-4 trips over 6-8 months across KC, NYC, London, Singapore
**Personality:** Organized but stretched thin. Relies on Copilot to keep her on track across a complex multi-city schedule. Knows the policy but doesn't want to think about it — she wants the Copilot to think about it for her.
**Key needs:** Pre-trip clarity, smooth approvals (she IS the approver for Maya), real-time help when things go sideways, clean post-trip close-out.

---

### Maya Patel — Junior Associate, Direct Report to Kelli
**Role:** Secondary traveler, first-timer, policy newcomer
**Travel Policy Tier:** Standard Associate (Economy required, standard hotel caps, manager approval required for all travel)
**Travel Profile:** First international trip under Zero Corp. Will occasionally travel with Kelli or meet her at shared destinations. Boyfriend (non-ZC employee) based in London.
**Personality:** Excited but anxious. The pre-trip planning phase alone has been stressful. Needs easy, reliable access to policy docs in plain language. Will want to use personal time in London wisely — and that's where wdywd comes in.
**Key needs:** Hand-holding through planning and approval, plain-language policy answers, confidence she's doing it right, and a great night out in London on her own time.

---

### David Okafor — SVP of Operations, Kelli's Approver
**Role:** Approver, executive stakeholder
**Travel Policy Tier:** N/A (approver only in these stories)
**Personality:** Busy, direct, low tolerance for friction. Wants approval requests to arrive clean, complete, and pre-packaged so he can approve in one click. Does not want to chase information or ask follow-up questions.
**Key needs:** Clear, concise approval requests with all info upfront. Fast turnaround. No surprises.

---

## USER STORIES

---

### ACT 1: BEFORE THE TRIP — PLANNING & PREPARATION

---

**Story 1.1 — Kelli: "What do I need for my trip to London next week?"**
*Actor: Kelli Chen*
*Section: S1 Planning, S2 Booking*

Kelli has a client meeting confirmed in London in 8 days. She opens the Travel Copilot and asks what she needs to prepare.

**Copilot should:**
- Confirm that 8 days is within the 21-day international booking window (flagging it as tight but manageable)
- Summarize international travel requirements: valid passport (6mo+ expiry), UK entry requirements for U.S. citizens (no visa required for business trips under 6 months as of current regulations), travel insurance via corporate Amex
- Remind her to register with the State Dept STEP program (Level 1 destination, standard precaution)
- Generate her pre-trip checklist automatically
- Prompt her to initiate the booking and approval flow

**Sample prompt:** *"What do I need for my trip to London next week?"*
**Contrast point:** Maya asking the same question gets a longer, more guided response — the Copilot detects it's her first international trip and walks her through each item step by step.

---

**Story 1.2 — Maya: "I've never traveled internationally for work before — where do I even start?"**
*Actor: Maya Patel*
*Section: S1 Planning, S3 Approvals*

Maya has been told she'll be joining Kelli in London. She's never traveled internationally for Zero Corp before and is already stressed about getting everything right.

**Copilot should:**
- Warmly acknowledge this is her first international trip and reassure her the Copilot will walk her through it
- Walk through the pre-trip checklist item by item in plain language
- Explain that she'll need manager approval (Kelli) before booking anything
- Check her passport status (ask her to confirm expiry date)
- Explain UK entry requirements in simple terms
- Remind her about the corporate Amex and what travel insurance it covers
- Proactively flag that her hotel per diem as a Standard Associate is $250/night (Tier 2) — different from Kelli's

**Sample prompt:** *"I've never traveled internationally for work before — where do I even start?"*

---

**Story 1.3 — Kelli: "What are my booking options for London — and what are the tradeoffs?"**
*Actor: Kelli Chen*
*Section: S2 Booking*

Kelli wants to understand her flight options before committing. The trip is ~9 hours each way.

**Copilot should:**
- Confirm that at 9+ hours, business class is authorized for Kelli with VP approval (David Okafor)
- Present 2-3 hypothetical fare options: economy (lowest cost, no approval needed beyond standard), premium economy (mid-range), business class (authorized, requires David's approval)
- Explain tradeoffs in plain language: cost vs. comfort vs. policy impact
- Note that non-refundable fares are fine given the confirmed client meeting
- Offer to prepare the approval request for business class automatically

**Sample prompt:** *"What are my flight options for London and what are the tradeoffs?"*

---

**Story 1.4 — Maya: "Do I need approval for this trip — and from whom?"**
*Actor: Maya Patel*
*Section: S3 Approvals*

Maya isn't sure if she needs approval or how that process works.

**Copilot should:**
- Confirm yes, approval is required for all international travel
- Identify Kelli Chen as her approving manager
- Explain the approval chain: Kelli → Finance (if over $5k total) → VP
- Offer to prepare the approval request for her, pre-filled with the trip details
- Explain expected turnaround: 2 business days for international requests
- Reassure her that the Copilot will notify her when approval comes through

**Sample prompt:** *"Do I need approval for this trip and who do I ask?"*

---

**Story 1.5 — David: "Approve Kelli's London trip request"**
*Actor: David Okafor*
*Section: S3 Approvals*

David receives a Slack notification that Kelli's London business class request is pending his approval.

**Copilot should (from David's view):**
- Surface a clean, one-screen summary: traveler, destination, dates, purpose, total estimated cost, fare class requested, policy compliance status
- Flag that business class is policy-compliant for a 9hr+ international flight
- Show one-click Approve / Deny / Request Changes options
- If approved, automatically notify Kelli and trigger booking confirmation flow

**Sample prompt (David):** *"Show me Kelli's pending travel request"*
**Key principle:** David should never have to ask a follow-up question. Everything he needs is in the first response.

---

### ACT 2: DURING THE TRIP

---

**Story 2.1 — Kelli: "My flight is delayed — what are my options?"**
*Actor: Kelli Chen*
*Section: S4 During, S5 Issues*

Kelli is at JFK. Her London flight is delayed 3.5 hours. She has a client meeting first thing the next morning.

**Copilot should:**
- Acknowledge the situation calmly and immediately
- Confirm a 3.5hr delay falls in the "2–4 hour" tier: meals reimbursable up to $50, no hotel required unless overnight
- Check if the delay pushes her into overnight territory — if so, escalate to full hotel coverage
- Offer to contact the Travel Desk to explore rebooking options on alternate flights
- Remind her that her client meeting is at risk and ask if she'd like help drafting a heads-up note to the client
- Provide Travel Desk contact: (800) 555-0192

**Sample prompt:** *"My flight is delayed 3.5 hours — what should I do?"*

---

**Story 2.2 — Maya: "What's covered for meals today?"**
*Actor: Maya Patel*
*Section: S4 During*

Maya is in London and wants to know what she can spend on meals without going over policy.

**Copilot should:**
- Identify London as an international destination
- Pull the applicable U.S. State Dept M&IE per diem rate for London (reference aoprals.state.gov — approximately $109/day as of recent rates)
- Remind her that today is her first day of travel, so the rate is prorated at 75%
- Clarify that receipts are required for individual meals over $25
- Note that alcohol is not reimbursable unless it's an approved client entertainment meal

**Sample prompt:** *"What can I spend on meals today?"*

---

**Story 2.3 — Kelli: "My flight was cancelled — what should I do now?"**
*Actor: Kelli Chen*
*Section: S4 During, S5 Issues*

Kelli's return flight from London is cancelled due to weather. She needs to get back to KC for an internal meeting the next afternoon.

**Copilot should:**
- Stay calm and action-oriented — bullet points, not paragraphs
- Advise her to contact the airline first for rebooking on next available flight
- If airline can't rebook within 4 hours, escalate to Travel Desk immediately
- Confirm hotel is fully covered (Tier 1 rate, up to $350/night London)
- Confirm meals are covered
- Remind her that DOT regulations entitle her to a refund if the airline cannot rebook
- Offer to contact Travel Desk on her behalf
- Ask if she needs help notifying her internal meeting stakeholders

**Sample prompt:** *"My flight was cancelled — what should I do now?"*

---

**Story 2.4 — Maya: "Who do I contact right now?" (security concern)**
*Actor: Maya Patel*
*Section: S5 Issues*

Maya is out in London after work hours and feels unsafe in her current location. She opens the Copilot.

**Copilot should:**
- Lead with immediate safety: "If you're in immediate danger, call 999 (UK emergency services) now."
- Provide Zero Corp Security line: (800) 555-0199 (24/7)
- Provide Zero Corp Emergency line: (800) 555-0911 (24/7)
- Tell her to remove herself from the situation first, contact authorities if needed
- Remind her not to post about the incident on social media
- Offer to notify her manager (Kelli) on her behalf if she'd like

**Sample prompt:** *"Who do I contact right now?"*
**Design note:** This response should be SHORT, clear, and action-first. Not the moment for policy explanation.

---

### ACT 3: THE WDYWD MOMENT 🔥

---

**Story 3.1 — Maya: "Ok I'm done with work — what should we do tonight in London?"**
*Actor: Maya Patel (off-duty, with boyfriend)*
*Section: wdywd module handoff*

Maya has wrapped her last client session with Kelli. Her boyfriend has arrived in London. She opens the Copilot and asks what they should do tonight — this is personal time, fully off Zero Corp policy.

**Copilot should:**
- Acknowledge the shift to personal time with a light, friendly tone change
- Clarify clearly: "You're off the clock — this one's on you! Here's what I'd suggest..."
- Hand off seamlessly to the wdywd module
- Prompt: eat / drink / play?
- Surface real London venues from the wdywd dataset (once KCMO/London data is ingested — placeholder for now)
- Use Maya's current location to sort by proximity
- Show results with hours, phone, dine-in/takeout options

**Sample prompt:** *"Ok I'm done with work — what should we do tonight in London?"*
**This is the demo money moment.** One app, two modes — enterprise policy assistant AND local discovery tool. Seamless handoff.

---

### ACT 4: AFTER THE TRIP

---

**Story 4.1 — Maya: "What do I still need to do after this trip?"**
*Actor: Maya Patel*
*Section: S6 Post-Trip*

Maya is back from London. The Copilot sends her a post-trip reminder.

**Copilot should:**
- Congratulate her on completing her first international business trip 🎉
- Summarize outstanding to-dos:
  - Confirm trip completion in Concur (within 2 business days)
  - Submit expense report (within 10 business days)
  - Receipts needed: hotel folio, all meals over $25, ground transport
  - Optional: complete trip feedback survey
- Remind her of the most common rejection reasons so she doesn't get burned
- Offer to walk her through the expense report step by step

**Sample prompt:** *"What do I still need to do after this trip?"*

---

**Story 4.2 — Kelli: "Can you remind me the procedure for reimbursement?"**
*Actor: Kelli Chen*
*Section: S6 Post-Trip*

Kelli is back and has a stack of receipts. She wants a quick refresher on the reimbursement process.

**Copilot should:**
- Give her the short version first: submit in Concur within 10 days, attach all receipts over $25, include business purpose
- Remind her that her hotel folio needs to be itemized (not just the credit card slip)
- Flag that as an executive traveler, her business class airfare is already reconciled through corporate Amex
- Remind her of the reimbursement timeline: 5 business days after final approval
- Offer to start the expense report for her in Concur

**Sample prompt:** *"Can you remind me the procedure for reimbursement?"*

---

## STORY COVERAGE MAP

| Story | Actor | Section | Journey Phase |
|---|---|---|---|
| 1.1 | Kelli | S1, S2 | Before |
| 1.2 | Maya | S1, S3 | Before |
| 1.3 | Kelli | S2 | Before |
| 1.4 | Maya | S3 | Before |
| 1.5 | David | S3 | Before (Approver) |
| 2.1 | Kelli | S4, S5 | During |
| 2.2 | Maya | S4 | During |
| 2.3 | Kelli | S4, S5 | During |
| 2.4 | Maya | S5 | During |
| 3.1 | Maya | wdywd | During (off-duty) |
| 4.1 | Maya | S6 | After |
| 4.2 | Kelli | S6 | After |

**12 stories. 3 actors. Full journey arc. wdywd handoff baked in.** ✅
