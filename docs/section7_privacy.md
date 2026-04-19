# ZERO CORP — TRAVEL & EXPENSE POLICY HANDBOOK
## Section 7: Privacy & Data

### 7.1 What Traveler Data the System Collects
The Zero Corp Travel Copilot and Concur integration collect the following data to provide travel assistance:

**Identity & Profile Data:**
- Employee name, employee ID, department, and role
- Manager and approval chain information
- Corporate Amex card number (last 4 digits only stored in Copilot)
- Preferred vendor preferences and loyalty program numbers (stored in Concur, not Copilot)

**Trip Data:**
- Trip destination, travel dates, and purpose
- Booking confirmations and itinerary details
- Approval request content and status
- Expense reports and receipts submitted through Concur

**Interaction Data:**
- Copilot conversation history (retained for 30 days for quality and support purposes)
- Feature usage and query types (anonymized and aggregated for product improvement)

**Location Data:**
- General destination city/country (from trip records)
- The Copilot does NOT collect real-time GPS location data

### 7.2 What the System Does NOT Store
Zero Corp's Travel Copilot is designed with data minimization as a core principle. The following data is explicitly NOT collected or retained:

- Full credit card numbers or financial account details
- Passport or visa document images (referenced by traveler; not uploaded to Copilot)
- Medical information beyond what is voluntarily shared in an emergency context
- Real-time location or device GPS data
- Personal travel details (trips not booked through Zero Corp systems)
- Biometric data of any kind
- Conversation content after the 30-day retention window (automatically deleted)
- Third-party personal communications (texts, personal email, etc.)

### 7.3 How Traveler Information Is Protected
Zero Corp applies the following safeguards to all travel-related data:

**In Transit:**
- All data transmitted between the Copilot, Concur, and Zero Corp systems is encrypted using TLS 1.2 or higher
- API calls to external services (airlines, hotels) use tokenized identifiers where possible

**At Rest:**
- Trip data is stored in Zero Corp's SOC 2 Type II certified data infrastructure
- Access to traveler data is restricted to the traveler, their direct manager, HR, Finance, and the Travel Desk
- Expense and approval data is retained for 7 years per IRS record-keeping requirements
- Copilot conversation logs are retained for 30 days, then permanently deleted

**Access Controls:**
- Role-based access ensures employees can only view their own trip data
- Managers can view their direct reports' trip requests and approvals
- Finance can view expense data for reporting purposes only
- All access is logged and auditable

**Third-Party Vendors:**
- Concur (SAP) processes booking and expense data under a Data Processing Agreement with Zero Corp
- AI model providers used in the Copilot operate under Zero Trust principles and do not train on Zero Corp employee data
- Vendor compliance is reviewed annually by Zero Corp's Security team

### 7.4 Third-Party Data Sharing Policy
Zero Corp shares traveler data with third parties only as required to deliver travel services:

**Shared with travel vendors (airlines, hotels, car rental):**
- Name, travel dates, destination — minimum required for booking

**Shared with Concur (SAP):**
- Full trip and expense data for booking and reimbursement processing

**Shared with Corporate Amex:**
- Transaction data for reconciliation and travel insurance purposes

**Never shared:**
- Employee data is never sold to third parties
- Data is never shared with advertisers or marketing platforms
- Aggregate, anonymized usage data may be shared with travel vendors for rate negotiation purposes only

**Your rights:**
- Employees may request a copy of their travel data by contacting privacy@zerocorp.com
- Employees may request correction of inaccurate data through HR or the Travel Desk
- Data deletion requests (outside of legally required retention periods) are reviewed by the Privacy team within 10 business days
