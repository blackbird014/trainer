# Biotech Single Company Analysis Prompt

## Context & Background

**Read these files for full context:**
- `01-introduction.md` - Biotech investment pipeline overview and structure
- `02-sequencing.md` - DNA/RNA sequencing fundamentals and technologies  
- `molecular-biology-foundations.md` - Complete molecular biology foundations
- `economical-context.md` - Economic environment assumptions

## Economic Environment Assumptions

**Current Economic Context:**
- **Interest rates lowering** - Creating favorable environment for R&D-heavy biotech companies
- **Biotech speculative environment emerging** - Capital flowing back into biotech after recent downturn
- **Risk-on sentiment** returning to growth sectors
- **Regulatory momentum** - FDA becoming more receptive to innovative biotech approaches

## Analysis Framework

**I am analyzing biotech companies in this economic and technological context, focusing on:**
- **Pipeline positioning** within the broader biotech ecosystem
- **Competitive moats** and defensibility in a speculative environment
- **Financial runway** and capital efficiency
- **Technology validation** and clinical translation potential

---

## Required Analysis Structure

Create a comprehensive competitive analysis following this **exact structure and format**:

### 1. **Executive Summary** 
- **Investment Considerations**: Analysis of key factors and reasoning for investment decision-making (provide reasoning, not strong recommendations)
- **Key Finding**: Company's unique position in biotech pipeline
- **Primary Risk/Headwind**: Main concern for investment

### 2. **Pipeline Position**
- **Where [Company] Fits**: Visual diagram showing position in biotech ecosystem
- **Layer Classification**: Specific layer (Sequencing, AI/Bioinformatics, Synthetic Biology Platforms, Market Applications)
- **Unique Position**: What makes this company distinctive

### 3. **Business Model & Technology**
- **Core Business**: What the company does
- **Key Technology**: Core technology platform/approach
- **Revenue Streams**: Current and potential revenue sources
- **Market Focus**: Target markets and applications

### 4. **Competitive Moats Analysis**
- **Moat Categories**: List each major competitive advantage
- **Detailed Defensibility Assessment**: 
  - **Why It's Defensible**: Specific reasons, examples, barriers to replication
  - **Why It's Not Defensible**: Vulnerabilities, competitive threats, limitations
- **Moat Strength Rating**: ⭐⭐⭐⭐⭐ (1-5 star system) with detailed justification
- **Time Horizon**: How long moats are likely to last with specific timeline estimates
- **Defensibility Examples**: Concrete examples of how moats work in practice

### 5. **Competitive Threats**
- **Primary Competitors**: List with threat levels (🔴 HIGH, 🟡 MODERATE, 🟢 LOW)
- **Detailed Competitive Analysis**: 
  - **Why each competitor is/isn't dangerous**: Specific capabilities, resources, strategies
  - **Competitive positioning**: Market share, strengths, weaknesses
- **Defense Strategies**: Specific actionable strategies the company can deploy
- **Market Share Dynamics**: Current and projected competitive positioning with data
- **Threat Timeline**: When each threat is likely to materialize

### 6. **Financial Analysis**
**CRITICAL: All quantitative financial data MUST come from the provided JSON file. Do NOT estimate or make up financial numbers.**

- **Current Financials**: Market cap (from JSON `valuation.marketCap`), revenue (from JSON `financials.revenue`), profitability status (determine from JSON `financials.netIncome` - if negative, company is losing money/pre-profit)
- **Key Metrics**: 
  - Profit margin (from JSON `profitability.profitMargin`)
  - Operating margin (from JSON `profitability.operatingMargin`)
  - Gross profit (from JSON `financials.grossProfit`)
  - EBITDA (from JSON `financials.ebitda`)
  - Net income (from JSON `financials.netIncome`)
  - Price-to-sales ratio (from JSON `valuation.priceToSales`)
  - Price-to-book ratio (from JSON `valuation.priceToBook`)
  - EV/Revenue (from JSON `valuation.enterpriseValueRevenue`)
  - EV/EBITDA (from JSON `valuation.enterpriseValueEBITDA`)
  - P/E ratios (from JSON `valuation.trailingPE` / `valuation.forwardPE` - note if company is unprofitable, P/E may be historical)
  - ROE (from JSON `profitability.returnOnEquity`)
  - ROA (from JSON `profitability.returnOnAssets`)
- **Runway Analysis**: Months/years of cash remaining (estimate based on cash position and net income burn rate if cash not in JSON)
- **Growth Trajectory**: Revenue growth (from JSON `financials.quarterlyRevenueGrowth`) and path to profitability (assess from net income trend)


### 7. **Key Metrics to Watch**
- **Financial Metrics**: Revenue growth, margins, cash burn, R&D efficiency
- **Pipeline Metrics**: Program progression, success rates, time to market
- **Operational Metrics**: Manufacturing, supply chain, quality, expansion

### 8. **Conclusion: Investment Analysis**
- **Overall Moat Assessment**: STRONG/MODERATE/WEAK with star rating and detailed justification
- **Comprehensive Risk Analysis**: 
  - **Key Risk Scenarios**: Detailed scenarios with probability assessments and timelines
  - **Mitigation Strategies**: Specific strategies to address each major risk
  - **Risk Impact Analysis**: Quantified impact of each risk scenario
- **Detailed Investment Thesis**:
  - **Bull Case**: Specific upside scenarios with market cap targets and catalysts
  - **Bear Case**: Detailed downside scenarios with specific risk factors
  - **Base Case**: Most likely scenario with probability assessment
- **Investment Considerations**: Analysis of key factors, risks, and opportunities with reasoning for investment decision-making (provide reasoning, avoid strong recommendation statements)

---

## Key Analysis Requirements

### **Investment Analysis Framework:**
- **Investment considerations** with clear reasoning (provide analysis and reasoning, avoid strong recommendation statements)
- **Specific metrics and numbers** (market cap, revenue, margins, runway)
- **Threat level assessments** with color coding (🔴🟡🟢)
- **Competitive moat analysis** with star ratings
- **Financial runway and profitability status**
- **Pipeline positioning** within broader biotech ecosystem
- **Risk factors and headwinds** clearly identified

### **Economic Context Integration:**
- How does the company benefit from **lowering interest rates**?
- What does the **speculative biotech environment** mean for this company?
- How does **regulatory momentum** affect their prospects?
- What are the **capital efficiency** considerations?

### **Technology Assessment:**
- **Validation status** of core technology
- **Clinical translation potential** 
- **Competitive differentiation** in technology
- **Scalability** of the platform/approach

### **Financial Deep Dive:**
**CRITICAL: Use ONLY JSON data for all quantitative financial metrics.**

- **Profitability timeline** and path to positive cash flow (assess from JSON `financials.netIncome` - if negative, company is losing money)
- **Capital requirements** vs. available resources (use JSON `financials.netIncome` to estimate cash burn if negative)
- **Revenue diversification** and dependency risks (use JSON `financials.revenue` and `financials.quarterlyRevenueGrowth`)
- **Market size** and addressable opportunity (qualitative estimate)
- **Valuation metrics** including price-to-sales ratio (from JSON `valuation.priceToSales`), price-to-book (from JSON `valuation.priceToBook`), P/E ratios (from JSON `valuation.trailingPE` / `forwardPE` - note if historical when company is unprofitable)

### **Data Source Requirements:**
- **ALL quantitative financial metrics MUST come from JSON**: Market Cap, Revenue, Revenue Growth, Net Income, EBITDA, Gross Profit, P/E ratios, Profit Margins, Operating Margins, ROE, ROA, Price/Sales, Price/Book, EV/Revenue, EV/EBITDA
- **Profitability determination**: Check `financials.netIncome` - if negative, company is losing money/pre-profit regardless of P/E ratio
- **P/E Ratio interpretation**: If `financials.netIncome` is negative but `valuation.trailingPE` exists, note that P/E is historical (company currently unprofitable)
- Only qualitative metrics (partnerships, clinical programs, market size estimates, competitive positioning) can be estimated from context

---

## Output Format Requirements

- **Comprehensive analysis** (target: 800-1200 words for full depth)
- **Clear structure** following the 8-section framework
- **Specific metrics** and quantitative analysis with detailed explanations
- **Visual elements** (diagrams, tables, emojis for clarity)
- **Actionable insights** for investment decision-making
- **Risk-focused assessment** given the speculative environment
- **Detailed scenarios** and probability assessments
- **Comprehensive competitive analysis** with specific strategies

---

## Analysis Quality Standards

**Target Analysis Quality:**
- **Depth of analysis** - Comprehensive coverage with detailed explanations, scenarios, and probability assessments
- **Formatting style** - Clear structure with visual elements (tables, diagrams, emojis)
- **Investment analysis framework** - Clear investment considerations with quantitative backing and detailed bull/bear cases (provide reasoning, avoid strong recommendation statements)
- **Risk assessment** - Thorough identification with specific scenarios, timelines, and mitigation strategies
- **Competitive analysis** - Detailed competitor mapping with specific defense strategies and market dynamics
- **Quantitative rigor** - Specific metrics, probability assessments, and timeline estimates throughout

**Goal**: Create investment-grade analysis that provides clear, actionable insights for biotech investment decisions in the current economic environment.
