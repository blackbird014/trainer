# Company Metrics Table Generation Prompt

## Overview
This prompt generates comprehensive company metrics tables for 1-3 biotech companies, following the format and structure used in the investment analysis dashboard.

## Prompt Template

```
# Company Metrics Dashboard Generation

Generate a comprehensive metrics table for [NUMBER] biotech companies: [COMPANY_1], [COMPANY_2], [COMPANY_3 (if applicable)].

## Requirements

### Table Structure
- Create a markdown table with companies as columns
- Include all standard metrics listed below
- Use consistent formatting with tildes (~) for approximate values
- Include company ticker symbols in parentheses

### Required Metrics (in order):

#### Financial Metrics
**CRITICAL: All quantitative financial data MUST come from the provided JSON file. Do NOT estimate or make up financial numbers.**

- **Market Cap**: From JSON `valuation.marketCap` - use exact value from JSON
- **Cash Position**: Available cash and cash equivalents (estimate only if not in JSON)
- **Cash Burn (Annual)**: Annual cash consumption rate (estimate based on netIncome if negative)
- **Runway (Years)**: Estimated years of operation with current cash (calculate from cash position and burn)
- **Revenue Growth**: From JSON `financials.quarterlyRevenueGrowth` - use exact value from JSON
- **Profitability**: Determine from JSON `financials.netIncome` - if negative, company is losing money/pre-profit
- **P/E Ratio**: From JSON `valuation.trailingPE` or `valuation.forwardPE` - use exact value. If company has negative netIncome, note P/E as historical/N/A (company currently unprofitable)

#### Business Metrics
- **Clinical Programs**: Number of active clinical programs
- **Key Partnerships**: Major strategic partnerships
- **Partnership Value**: Total value of partnerships
- **Technology Validation**: Current stage of technology validation
- **Regulatory Status**: Current regulatory approval status

#### Competitive Metrics
- **Competitive Position**: Market position ranking
- **Market Share**: Estimated market share percentage
- **Key Risks**: Primary business and investment risks
- **Catalysts**: Key value drivers and growth catalysts
- **Next Milestone**: Upcoming important events
- **Target Market**: Total addressable market size

#### Stock Metrics
- **Current Price**: Current stock price
- **52-Week High**: Highest price in past year
- **52-Week Low**: Lowest price in past year
- **Analyst Rating**: Consensus analyst rating
- **Price Target**: Average analyst price target

### Formatting Guidelines
- Use markdown table format with proper alignment
- Include section headers for different metric categories
- Use consistent notation (e.g., ~$1.2B, 20-30%, N/A)
- Maintain professional investment analysis tone
- Include relevant context for biotech industry specifics

### Data Source Requirements
- **ALL quantitative financial metrics MUST come from JSON**: Market Cap, Revenue, Revenue Growth, Net Income, EBITDA, P/E ratios, Profit Margins, ROE, ROA, etc.
- **Profitability determination**: Check `financials.netIncome` - if negative, company is losing money/pre-profit regardless of P/E ratio
- **P/E Ratio interpretation**: If `financials.netIncome` is negative but `valuation.trailingPE` exists, note that P/E is historical (company currently unprofitable)
- Only qualitative metrics (partnerships, clinical programs, market share estimates) can be estimated from context

### Additional Analysis
After the table, include:

#### Key Insights from Metrics:
- **Cash Runway Leaders**: Companies with longest cash runway
- **Growth Leaders**: Companies with highest revenue growth
- **Partnership Leaders**: Companies with most valuable partnerships
- **Risk Assessment**: Categorize companies by risk level
- **Investment Opportunity**: Assessment of valuation and volatility

## Example Output Structure

```markdown
### **Table: [Company Names]**

| **Metric** | **[Company 1]** | **[Company 2]** | **[Company 3]** |
|------------|-----------------|-----------------|-----------------|
| **Market Cap** | ~$X.XB | ~$X.XB | ~$X.XB |
| [Additional metrics...] |

### **Key Insights from Metrics:**

#### **Cash Runway Leaders:**
- **[Company]**: X years runway (description)

#### **Growth Leaders:**
- **[Company]**: X% revenue growth (description)

#### **Partnership Leaders:**
- **[Company]**: $XM+ partnership value (description)

#### **Risk Assessment:**
- **Highest Risk**: [Companies] (description)
- **Moderate Risk**: [Companies] (description)
- **Lowest Risk**: [Companies] (description)

#### **Investment Opportunity:**
- **Most Undervalued**: [Companies] (description)
- **Most Overvalued**: [Companies] (description)
- **Most Volatile**: [Companies] (description)
```

## Usage Instructions

1. Replace [NUMBER] with actual number of companies (1-3)
2. Replace [COMPANY_X] with actual company names and tickers
3. Ensure all metrics are research-backed and current
4. Maintain consistency in formatting and terminology
5. Focus on biotech-specific metrics and industry context
6. Include realistic ranges and estimates where exact data unavailable

## Quality Checklist

- [ ] All required metrics included
- [ ] Consistent formatting throughout
- [ ] Realistic and current data
- [ ] Professional investment analysis tone
- [ ] Biotech industry context maintained
- [ ] Key insights section included
- [ ] Proper markdown table formatting
- [ ] Company tickers included in headers
```

## Notes

- This prompt is designed for biotech companies specifically
- Metrics should be current and research-backed
- Format follows the established investment analysis template
- Can be adapted for other industries with metric modifications
- Maintains professional investment analysis standards
