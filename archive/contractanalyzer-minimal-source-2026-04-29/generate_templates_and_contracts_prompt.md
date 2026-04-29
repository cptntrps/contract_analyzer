# Prompt for Generating Contract Templates and Test Contracts

## PART 1: Generate 5 Master Templates

Create the following 5 contract templates that will serve as the "golden standard" for comparison. These templates should represent what the company expects vendors to use WITHOUT modifications.

### Templates to Generate:

1. **TYPE_SOW_Standard_v1.docx** - Generic Statement of Work template
2. **TYPE_CHANGEORDER_Standard_v1.docx** - Generic Change Order template  
3. **VENDOR_CAPGEMINI_SOW_v1.docx** - Capgemini-specific SOW template
4. **VENDOR_BLUEOPTIMA_SOW_v1.docx** - Blue Optima-specific SOW template
5. **VENDOR_EPAM_SOW_v1.docx** - EPAM-specific SOW template

### Template Structure Requirements:

Each template MUST include:

1. **Title Page** containing:
   - Document title (e.g., "STATEMENT OF WORK TEMPLATE")
   - Template version
   - Company name where applicable

2. **Metadata Table** containing:
   - Contract Type: [SOW/Change Order]
   - Vendor: [Vendor Name or "Generic"]
   - Effective Date: [DATE]
   - Client: [CLIENT NAME]
   - Project Code: [PROJECT CODE]

3. **Main Contract Body** with these sections:

   **For SOW Templates:**
   - 1. PROJECT OVERVIEW
   - 2. SCOPE OF WORK
   - 3. DELIVERABLES
   - 4. PROJECT TIMELINE
   - 5. RESOURCE ALLOCATION
   - 6. ACCEPTANCE CRITERIA
   - 7. ASSUMPTIONS AND DEPENDENCIES
   - 8. PAYMENT TERMS
   - 9. CHANGE MANAGEMENT
   - 10. TERMS AND CONDITIONS

   **For Change Order Template:**
   - 1. REFERENCE TO ORIGINAL SOW
   - 2. DESCRIPTION OF CHANGE
   - 3. REASON FOR CHANGE
   - 4. IMPACT ON SCOPE
   - 5. IMPACT ON TIMELINE
   - 6. IMPACT ON BUDGET
   - 7. REVISED DELIVERABLES
   - 8. APPROVAL AND AUTHORIZATION

### Important Template Guidelines:
- Use placeholder text in brackets: [CLIENT NAME], [START DATE], [DELIVERABLE 1]
- Include realistic legal language
- Make vendor-specific templates include vendor name in the text (e.g., "Capgemini shall provide...")
- Each template should be 3-4 pages long with substantive content

## PART 2: Generate 20 Test Contracts

Create 20 contracts that vendors might submit. These should be based on the templates above but with filled-in details and potential modifications.

### Contract Distribution:
- **5 contracts** perfectly matching TYPE_SOW_Standard_v1 (no changes, just filled placeholders)
- **2 contracts** perfectly matching TYPE_CHANGEORDER_Standard_v1
- **3 contracts** perfectly matching VENDOR_CAPGEMINI_SOW_v1
- **2 contracts** perfectly matching VENDOR_BLUEOPTIMA_SOW_v1
- **2 contracts** perfectly matching VENDOR_EPAM_SOW_v1
- **3 contracts** with UNAUTHORIZED MODIFICATIONS to templates (vendor tried to change terms)
- **3 contracts** that don't match any template (completely different format/structure)

### Naming Convention for Test Contracts:
- `Contract_[NUMBER]_[VENDOR]_[TYPE]_[DATE].docx`
- Examples:
  - `Contract_001_Generic_SOW_20240115.docx`
  - `Contract_002_Capgemini_SOW_20240116.docx`
  - `Contract_003_BlueOptima_SOW_MODIFIED_20240117.docx`

### Types of Modifications to Include (for the 3 modified contracts):
1. **Payment Terms Change**: Vendor changed "Net 30" to "Net 15" 
2. **Liability Limitation**: Vendor added a cap on liability that wasn't in template
3. **Scope Creep**: Vendor removed certain deliverables or added exclusions

### For Non-Matching Contracts (3 contracts):
- Use completely different structure/sections
- Include different legal language
- May be from vendors not in our system (e.g., "TechCorp Solutions")

### Realistic Data to Use:
- Client names: Acme Corp, GlobalTech Inc, Finance Solutions Ltd
- Project names: Digital Transformation Phase 1, Cloud Migration Project, Data Analytics Platform
- Dates: Use dates from January 2024
- Amounts: $50,000 - $500,000 range
- Durations: 3-12 months

## Expected Output Summary:

You should generate:
1. **5 template files** (the golden standards)
2. **20 contract files** with the distribution described above

Total: 25 Microsoft Word documents

Each document should be complete, professional, and ready to test the contract analyzer system. The goal is to verify that the analyzer can:
- Correctly identify which template each contract is based on
- Detect when vendors have made unauthorized changes
- Flag contracts that don't match any known template
- Generate accurate comparison reports showing differences