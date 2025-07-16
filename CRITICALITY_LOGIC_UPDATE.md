# Contract Analysis - Updated Criticality Logic

## Overview
The contract analysis system has been updated with new criticality logic that distinguishes between different types of changes based on their business impact and risk level.

## New Criticality Rules

### 1. **INCONSEQUENTIAL Changes**
- **Placeholder → Actual Content**: When placeholder text is filled with actual information
- **Examples**:
  - `[insert name here]` → `John Smith`
  - `[company name]` → `Acme Corporation`
  - `INSERT SERVICE` → `Web development services`
  - `TBD` → `January 15, 2024`
  - `_______` → `Manager`

### 2. **CRITICAL Changes**
- **Actual Content → Different Actual Content**: When existing values are changed to different values
- **Examples**:
  - `$1,000` → `$20,000` (monetary changes)
  - `Company A` → `Company B` (entity changes)
  - `I sell balls` → `I sell cows` (service/product changes)
  - `December 31, 2024` → `March 15, 2025` (date changes)
  - `Microsoft Corporation` → `Apple Inc.` (company changes)

### 3. **Special Cases**
- **Service/Product Placeholders**: `[insert service here]` → `Consulting services` 
  - Initially marked as INCONSEQUENTIAL but flagged for review
- **Actual → Placeholder**: Unusual case marked as SIGNIFICANT
- **Legal Keywords**: Always CRITICAL regardless of placeholder status

## Minimum Criticality Rule
**The contract's overall risk level is determined by its most critical change:**
- **One CRITICAL change** = **HIGH risk** for entire contract
- **No CRITICAL changes** = Risk based on SIGNIFICANT changes
- **Mostly INCONSEQUENTIAL** = LOW risk

## Implementation Details

### Placeholder Detection Patterns
The system detects these placeholder patterns:
- `[anything]` - Bracket placeholders
- `INSERT WORD` - Insert commands
- `_____` - Underscores
- `...` - Ellipsis
- `TBD`, `TBA`, `TO BE DETERMINED` - Standard placeholders
- `PLACEHOLDER`, `FILL IN` - Explicit placeholders
- `<anything>` - Angle bracket placeholders
- `{anything}` - Curly bracket placeholders

### Critical Change Detection
The system identifies critical changes through:
- **Monetary patterns**: `$1,000`, `€500`, `1000 USD`
- **Company names**: Multiple capitalized words
- **Service keywords**: "service", "product", "deliverable", "work"
- **Legal keywords**: "liability", "termination", "breach"

## Risk Assessment & Recommendations

### HIGH Risk (Any CRITICAL changes)
- 🚨 **Immediate legal review required**
- 🚨 **Do not execute until approved**
- 🚨 **Focus on value-to-value changes**
- 💰 **Verify monetary changes**
- 🔄 **Review service/product changes**
- 🏢 **Verify company/entity changes**

### MEDIUM Risk (SIGNIFICANT changes only)
- ⚠️ **Legal team review**
- ⚠️ **Verify financial implications**
- ⚠️ **Obtain internal approvals**

### LOW Risk (Mostly INCONSEQUENTIAL)
- ✅ **Standard review process**
- ✅ **Mostly placeholder → actual content**
- ✅ **Expedited approval possible**

## Example Scenarios

### Scenario 1: Inconsequential Contract
```
[Client Name] → "ABC Corporation"
[Project Description] → "Website redesign"
[Start Date] → "January 1, 2024"
```
**Result**: LOW risk - All placeholder fill-ins

### Scenario 2: Critical Contract
```
"ABC Corporation" → "XYZ Industries"
"$5,000" → "$15,000"
"Web development" → "Mobile app development"
```
**Result**: HIGH risk - All value-to-value changes

### Scenario 3: Mixed Contract
```
[Client Name] → "ABC Corporation" (INCONSEQUENTIAL)
"$5,000" → "$15,000" (CRITICAL)
[Project Manager] → "John Smith" (INCONSEQUENTIAL)
```
**Result**: HIGH risk - One critical change makes entire contract high risk

## Benefits
1. **Accurate Risk Assessment**: Distinguishes between routine form-filling and significant business changes
2. **Focused Review**: Directs attention to changes that actually matter
3. **Consistent Logic**: Clear rules for what constitutes critical vs. inconsequential changes
4. **Automated Detection**: Systematic identification of placeholder patterns and value changes
5. **Actionable Recommendations**: Specific guidance based on change types detected

## Files Updated
- `app/llm_handler.py` - Core criticality logic
- `enhanced_report_generator.py` - Risk assessment and recommendations
- All report outputs now reflect the new criticality logic 