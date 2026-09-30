/**
 * [Q9: Multi-Lingual Support & Accessibility]
 * Internationalization (i18n) Dictionary & Context
 * Provides full English & Gujarati (ગુજરાતી) localized UI text.
 */

export const translations = {
  en: {
    portalTitle: "Gujarat e-Vidya Scholarship Portal",
    governmentSubtitle: "Department of Education, Government of Gujarat",
    liveStatus: "Live Systems Operational",
    highContrast: "High Contrast",
    normalContrast: "Standard Contrast",
    switchLanguage: "ગુજરાતી માં બદલો",

    // Navigation & Tabs
    tabDashboard: "School Registry Dashboard",
    tabTopSchools: "Top 5 Schools (Q4 SQL)",
    tabEligibility: "Eligibility Rules (Q6)",
    tabDisbursements: "DBT Idempotency (Q2)",
    tabAudit: "Audit Ledger (Q11)",

    // High Performance Virtualized Table (Q3 & Q8)
    tableHeading: "State-Wide School Registry (Virtualized 1,000+ Records)",
    tableSubheading: "Rendered via client-side virtualization maintaining constant 60 FPS without DOM bloat.",
    searchPlaceholder: "Search school by name...",
    filterDistrict: "All Districts",
    totalLoaded: "Total Schools Loaded",
    columnId: "ID",
    columnSchoolName: "School Name",
    columnDistrict: "District",
    columnTotalStudents: "Total Enrolled Students",
    columnUdiseCode: "UDISE+ Code",
    columnActions: "Status",
    statusRecognized: "Recognized",

    // Top Schools (Q4)
    topSchoolsHeading: "Top 5 Gujarat Schools by Enrollment",
    topSchoolsDescription: "Powered by raw optimized SQL: SELECT id, school_name, district, total_students FROM schools ORDER BY total_students DESC LIMIT 5;",
    rank: "Rank",

    // Eligibility Checker (Q6 & Q7)
    eligibilityHeading: "Scholarship Eligibility Evaluation (Rule Engine)",
    eligibilityDescription: "Demonstrates SOLID Strategy Pattern with dynamic JSON rule configuration loaded on the fly.",
    labelFamilyIncome: "Annual Family Income (₹)",
    labelAttendance: "Biometric Attendance (%)",
    labelMarks: "Academic Marks (%)",
    labelCategory: "Category",
    labelDistrict: "District",
    btnCheckEligibility: "Evaluate Eligibility",
    evaluating: "Evaluating Criteria...",
    eligibleSuccess: "Congratulations! Candidate is Eligible for MYSY Scheme.",
    disqualifiedWarning: "Candidate does not satisfy scheme criteria:",

    // Idempotent Disbursements (Q2)
    disbursementHeading: "State Direct Benefit Transfer (DBT) Payment API",
    disbursementDescription: "Guarantees strict at-most-once execution using Redis/In-Memory atomic locking and Idempotency-Key deduplication.",
    labelStudentId: "Student Beneficiary ID",
    labelSchemeCode: "Scheme Identifier",
    labelAmount: "Amount (₹)",
    labelIdempotencyKey: "Idempotency-Key Header",
    btnGenerateKey: "Regenerate Key",
    btnPay: "Execute Disbursement (POST /disbursements)",
    btnRetry: "Simulate Fast Retry / Double-Click with Same Key",
    replayNotice: "IDEMPOTENT REPLAY DETECTED: This transaction was already processed. The stored authoritative response was returned with header Idempotent-Replay: true without double-debiting state funds.",
    newPaymentSuccess: "NEW DISBURSEMENT EXECUTED: Successfully credited to beneficiary account.",

    // Audit Ledger (Q11)
    auditHeading: "Cryptographic Audit Ledger & Tamper Verification",
    auditDescription: "Tamper-evident blockchain-style hash chaining where each administrative action is cryptographically signed with the SHA-256 hash of its predecessor.",
    btnVerifyChain: "Verify Cryptographic Chain Integrity",
    verifyingChain: "Calculating SHA-256 Hashes Across Ledger...",
    chainValid: "Ledger Intact: All cryptographic signatures validated. Zero unauthorized modifications detected.",
    chainCompromised: "SECURITY ALERT: Hash mismatch detected! Unauthorized SQL alteration detected at record.",
    totalAuditRecords: "Total Audit Records",

    // Footer
    footerText: "Gujarat e-Vidya Technical Assessment Reference Platform. Designed for scalable e-Governance.",
    wcagBadge: "WCAG 2.1 AA Compliant",
    ariaLiveAnnouncement: "Content updated"
  },
  gu: {
    portalTitle: "ગુજરાત ઇ-વિદ્યા શિષ્યવૃત્તિ પોર્ટલ",
    governmentSubtitle: "શિક્ષણ વિભાગ, ગુજરાત સરકાર",
    liveStatus: "સિસ્ટમ સક્રિય છે",
    highContrast: "હાઇ કોન્ટ્રાસ્ટ",
    normalContrast: "સામાન્ય કોન્ટ્રાસ્ટ",
    switchLanguage: "Switch to English",

    // Navigation & Tabs
    tabDashboard: "શાળા નોંધણી ડેશબોર્ડ",
    tabTopSchools: "ટોચની ૫ શાળાઓ (Q4 SQL)",
    tabEligibility: "પાત્રતા નિયમો (Q6)",
    tabDisbursements: "DBT આઇડેમ્પોટન્સી (Q2)",
    tabAudit: "ઓડિટ લેજર (Q11)",

    // High Performance Virtualized Table (Q3 & Q8)
    tableHeading: "રાજ્યવ્યાપી શાળા રજિસ્ટ્રી (વર્ચ્યુઅલાઈઝ્ડ ૧,૦૦૦+ રેકોર્ડ્સ)",
    tableSubheading: "DOM બ્લોટ વગર ૬૦ FPS પ્રદર્શન જાળવી રાખવા માટે ક્લાયન્ટ-સાઇડ વર્ચ્યુઅલાઇઝેશન.",
    searchPlaceholder: "શાળાનું નામ શોધો...",
    filterDistrict: "બધા જિલ્લાઓ",
    totalLoaded: "કુલ શાળાઓ લોડ થઈ",
    columnId: "ક્રમ",
    columnSchoolName: "શાળાનું નામ",
    columnDistrict: "જિલ્લો",
    columnTotalStudents: "કુલ વિદ્યાર્થીઓ",
    columnUdiseCode: "યુડાઇસ+ કોડ",
    columnActions: "સ્થિતિ",
    statusRecognized: "માન્યતા પ્રાપ્ત",

    // Top Schools (Q4)
    topSchoolsHeading: "વિદ્યાર્થી નોંધણી અનુસાર ટોચની ૫ શાળાઓ",
    topSchoolsDescription: "ઓપ્ટિમાઇઝ્ડ SQL દ્વારા સંચાલિત: SELECT id, school_name, district, total_students FROM schools ORDER BY total_students DESC LIMIT 5;",
    rank: "ક્રમ",

    // Eligibility Checker (Q6 & Q7)
    eligibilityHeading: "શિષ્યવૃત્તિ પાત્રતા ચકાસણી (રૂલ એન્જિન)",
    eligibilityDescription: "SOLID સ્ટ્રેટેજી પેટર્ન અને ડાયનેમિક JSON નિયમોનું રીઅલ-ટાઇમ મૂલ્યાંકન.",
    labelFamilyIncome: "વાર્ષિક કૌટુંબિક આવક (₹)",
    labelAttendance: "બાયોમેટ્રિક હાજરી (%)",
    labelMarks: "શૈક્ષણિક ગુણ (%)",
    labelCategory: "કેટેગરી",
    labelDistrict: "જિલ્લો",
    btnCheckEligibility: "પાત્રતા ચકાસો",
    evaluating: "મૂલ્યાંકન થઈ રહ્યું છે...",
    eligibleSuccess: "અભિનંદન! વિદ્યાર્થી MYSY યોજના માટે પાત્ર છે.",
    disqualifiedWarning: "વિદ્યાર્થી યોજનાના માપદંડ પૂર્ણ કરતો નથી:",

    // Idempotent Disbursements (Q2)
    disbursementHeading: "રાજ્ય પ્રત્યક્ષ લાભ ટ્રાન્સફર (DBT) ચુકવણી API",
    disbursementDescription: "Redis/મેમરી લોક અને Idempotency-Key દ્વારા ડબલ-પેમેન્ટ રોકવા માટે અચૂક આઇડેમ્પોટન્સી.",
    labelStudentId: "વિદ્યાર્થી લાભાર્થી ID",
    labelSchemeCode: "યોજના કોડ",
    labelAmount: "રકમ (₹)",
    labelIdempotencyKey: "Idempotency-Key હેડર",
    btnGenerateKey: "નવી કી બનાવો",
    btnPay: "ચુકવણી અમલમાં મૂકો (POST /disbursements)",
    btnRetry: "તે જ કી સાથે ફરીથી પ્રયાસનું અનુકરણ કરો",
    replayNotice: "આઇડેમ્પોટન્ટ રિપ્લે પ્રાપ્ત: આ વ્યવહાર પહેલેથી જ સફળ થયો હતો. સરકારી તિજોરીમાંથી ફરીથી રકમ કાપ્યા વગર સંગ્રહિત પરિણામ દર્શાવવામાં આવ્યું છે.",
    newPaymentSuccess: "નવી ચુકવણી સફળતાપૂર્વક પૂર્ણ થઈ: રકમ જમા થઈ ગઈ છે.",

    // Audit Ledger (Q11)
    auditHeading: "ક્રિપ્ટોગ્રાફિક ઓડિટ લેજર અને ટેમ્પર વેરિફિકેશન",
    auditDescription: "બ્લોકચેન-શૈલીની SHA-256 હેશ ચેઇન દ્વારા સુરક્ષિત ઓડિટ લોગ.",
    btnVerifyChain: "ક્રિપ્ટોગ્રાફિક ચેઇનની અખંડિતતા ચકાસો",
    verifyingChain: "લેજરમાં તમામ SHA-256 હેશની ગણતરી થઈ રહી છે...",
    chainValid: "લેજર સુરક્ષિત છે: તમામ હેશ માન્ય છે. કોઈપણ અનધિકૃત ફેરફાર થયો નથી.",
    chainCompromised: "સુરક્ષા ચેતવણી: હેશ અસંગતતા જણાઈ છે! ડેટાબેઝમાં અનધિકૃત ફેરફાર પકડાયો.",
    totalAuditRecords: "કુલ ઓડિટ રેકોર્ડ્સ",

    // Footer
    footerText: "ગુજરાત ઇ-વિદ્યા શિષ્યવૃત્તિ સંદર્ભ પ્લેટફોર્મ. ઇ-ગવર્નન્સ માટે સુરક્ષિત અને ઝડપી.",
    wcagBadge: "WCAG 2.1 AA સુસંગત",
    ariaLiveAnnouncement: "સામગ્રી અપડેટ થઈ"
  }
};
