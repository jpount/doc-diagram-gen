# Business Rules Catalog Template

## NO HARDCODING - ALL VALUES FROM JSON

This template shows how to generate the business rules catalog WITHOUT hardcoding any values.

```python
# STEP 1: Load the actual data - NO HARDCODED COUNTS
import json

with open("output/context/business-rules-extracted.json", 'r') as f:
    data = json.load(f)

# Extract ACTUAL counts from the file
deterministic_count = data['total_rules_found']  # NOT hardcoded as 39!
financial_count = data['summary']['financial']
state_count = data['summary']['state']
validation_count = data['summary']['validation']
operation_count = data['summary']['operation']

# STEP 2: Generate catalog header with ACTUAL counts
catalog = f"""# Business Rules Catalog

## Summary
- **Deterministic Rules (Python)**: {deterministic_count} rules
- **Additional LLM-Discovered Rules**: [TO BE DETERMINED] rules
- **Total Business Rules**: [TO BE CALCULATED] rules

### Breakdown by Type
- Financial Rules: {financial_count}
- State Management: {state_count}
- Validation Rules: {validation_count}
- Business Operations: {operation_count}
"""

# STEP 3: Generate documentation for EACH rule
for rule in data['rules']:
    rule_section = f"""
### {rule['id']}: {rule['description']} - {rule['method']}
- **Type**: {rule['type'].title()}
- **File**: {rule['file']}:{rule['line']} [REF-XXX]
- **Method**: `{rule['signature']}`
- **Pattern Matched**: {rule['pattern_matched']}

#### Code Implementation:
```{get_language(rule['file'])}
{rule.get('code_snippet', 'Code snippet not available')}
```

#### 🤖 LLM Analysis - What This Code Actually Does:
[ANALYZE the code snippet above and explain:]
1. What business logic is being implemented
2. What validations or constraints are enforced
3. What data transformations occur
4. What side effects or state changes happen
5. Any error handling or edge cases

**Key Business Logic**:
- [Bullet point 1 based on actual code analysis]
- [Bullet point 2 based on actual code analysis]
- [etc.]

**Business Impact**:
[Explain the business significance of this rule]
"""
    catalog += rule_section
```

## Example Output (Using ACTUAL Data)

When the agent runs, it will generate something like:

```markdown
# Business Rules Catalog

## Summary
- **Deterministic Rules (Python)**: [ACTUAL COUNT FROM JSON] rules
- **Additional LLM-Discovered Rules**: [COUNT AFTER LLM ANALYSIS] rules
- **Total Business Rules**: [SUM OF BOTH] rules

## Part 1: Automated Extraction (Deterministic)
✅ **[ACTUAL COUNT] rules** extracted via Python script

### BR-001: Trading Operation - buy Method
- **Type**: Operation
- **File**: daytrader3-ee6-ejb/.../TradeAction.java:202 [REF-042]
- **Method**: `public OrderDataBean buy(String userID, String symbol, double quantity, int orderProcessingMode) throws Exception`

#### Code Implementation:
```java
public OrderDataBean buy(String userID, String symbol, double quantity, int orderProcessingMode) throws Exception {
    // Validate user account
    AccountDataBean account = getAccountData(userID);
    if (account.getBalance().compareTo(BigDecimal.ZERO) <= 0) {
        throw new InsufficientFundsException("Account balance is zero or negative");
    }

    // Calculate order total
    QuoteDataBean quote = getQuote(symbol);
    BigDecimal orderFee = getOrderFee(account.getAccountType());
    BigDecimal total = quote.getPrice().multiply(new BigDecimal(quantity)).add(orderFee);

    // Check sufficient balance
    if (account.getBalance().compareTo(total) < 0) {
        throw new InsufficientFundsException("Insufficient funds");
    }
    // ... more code
}
```

#### 🤖 LLM Analysis - What This Code Actually Does:
This buy operation implements a **comprehensive purchase validation workflow**:

1. **Account Validation**: First retrieves and validates the user's account exists
2. **Balance Pre-Check**: Ensures account has positive balance before proceeding
3. **Real-time Pricing**: Fetches current quote for the requested symbol
4. **Fee Calculation**: Applies account-type-specific trading fees
5. **Total Cost Computation**: Uses BigDecimal for precise financial arithmetic
6. **Funds Verification**: Validates sufficient funds including fees
7. **Atomic Transaction**: Would proceed to execute purchase (code continues)

**Key Business Logic**:
- Prevents overdrafts through dual balance validation (zero check + sufficiency check)
- Includes trading fees in total cost validation, not just stock price
- Uses BigDecimal to ensure financial precision (no floating-point errors)
- Supports tiered fee structures based on account types
- Implements fail-fast validation (checks cheapest validations first)

**Business Impact**:
This rule protects the trading platform from financial risk by ensuring all purchases are fully funded before execution. The dual validation approach and BigDecimal usage demonstrate compliance with financial industry standards for transaction processing.

[... CONTINUE FOR ALL RULES FROM JSON ...]

## Part 2: Additional LLM-Identified Rules
🔍 **[ACTUAL LLM COUNT] additional rules** identified through semantic analysis

[... LLM-discovered rules with confidence levels and reasoning ...]
```

## CRITICAL REMINDERS

1. **NO HARDCODING ALLOWED**:
   - ❌ WRONG: "39 rules found"
   - ✅ RIGHT: `{data['total_rules_found']} rules found`

2. **READ FROM JSON**:
   - Always load from `output/context/business-rules-extracted.json`
   - Use actual values for counts, types, methods, etc.

3. **CODE + EXPLANATION**:
   - Include the actual code snippet
   - Provide LLM analysis of what the code REALLY does
   - Explain business impact

4. **COMPLETE LISTING**:
   - Generate documentation for EVERY rule
   - No placeholders like "[... list all rules ...]"
   - Actually iterate through all rules in the JSON