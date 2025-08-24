#!/usr/bin/env python3
"""
Generate Executive Summary from Analysis Results

This script aggregates all analysis outputs and generates:
1. Executive Summary (2-3 pages)
2. One-Page Executive Brief
3. Dashboard metrics (JSON)
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ExecutiveSummaryGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.docs_dir = self.output_dir / "docs"
        self.findings = {}
        self.metrics = {
            "codebase": {},
            "risks": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "technologies": [],
            "recommendations": []
        }
    
    def extract_metrics_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract key metrics from an analysis file."""
        if not file_path.exists():
            return {}
        
        content = file_path.read_text()
        metrics = {}
        
        # Extract common patterns - updated to match actual file formats
        patterns = {
            "total_files": r"(\d+)\s+(?:Java\s+)?[Ff]iles?|Total Files?:\s*(\d+)",
            "lines_of_code": r"([\d,]+)\s+lines?\s+of\s+code|Lines of Code:\s*([\d,]+)|LOC:\s*([\d,]+)",
            "critical_issues": r"Critical.*?:\s*(\d+)|🔴\s+Critical\s*\|\s*(\d+)",
            "high_priority": r"High.*?:\s*(\d+)|🟠\s+High\s*\|\s*(\d+)",
            "medium_priority": r"Medium.*?:\s*(\d+)|🟡\s+Medium\s*\|\s*(\d+)",
            "technologies": r"Primary Technologies?:\s*([^\n]+)|Technology Stack:\s*([^\n]+)",
            "complexity": r"Complexity.*?:\s*(\w+)|Technical Debt Level:\s*(\w+)",
            "security_issues": r"Security.*?(?:Issues|Vulnerabilities).*?:\s*(\d+)|🔴\s+Vulnerable",
            "codebase_size": r"Codebase Size:\s*([^\n]+)",
            "architecture": r"Architecture Pattern:\s*([^\n]+)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Get the first non-empty match
                value = next((m for match in matches for m in (match if isinstance(match, tuple) else (match,)) if m), None)
                if value:
                    if key in ["total_files", "critical_issues", "high_priority", "medium_priority", "security_issues"]:
                        try:
                            metrics[key] = int(value.replace(",", ""))
                        except:
                            metrics[key] = value
                    else:
                        metrics[key] = value
        
        # Count security vulnerabilities marked with 🔴
        vulnerable_count = len(re.findall(r"🔴\s+Vulnerable", content))
        if vulnerable_count > 0:
            metrics["vulnerable_dependencies"] = vulnerable_count
        
        return metrics
    
    def collect_all_findings(self):
        """Collect findings from all analysis reports."""
        
        # Define report patterns and their categories - updated to match actual files
        report_patterns = {
            "architecture": ["00-agent-selection-report.md", "01-archaeological-analysis.md"],
            "technology": ["01-*-architecture-analysis.md"],
            "discovery": ["01-comprehensive-discovery-report.md", "01-archaeological-analysis.md"],
            "business": ["02-comprehensive-business-logic-analysis.md", "business_logic_catalog.md", 
                        "business-rules-catalog.md", "business_rules_reference.md"],
            "performance": ["04-comprehensive-performance-analysis.md", "optimization-roadmap.md",
                          "../reports/performance-analysis.md"],
            "security": ["05-comprehensive-security-analysis.md", "security-vulnerability-report.md",
                        "security-risk-heatmap.md", "compliance-gap-analysis.md", 
                        "authentication-authorization-analysis.md"],
            "modernization": ["06-modernization-blueprint.md"]
        }
        
        for category, patterns in report_patterns.items():
            for pattern in patterns:
                if pattern.startswith("../"):
                    # Handle files in reports directory
                    file_path = self.output_dir / pattern[3:]
                    if file_path.exists():
                        metrics = self.extract_metrics_from_file(file_path)
                        if metrics:
                            if category not in self.findings:
                                self.findings[category] = metrics
                            else:
                                # Merge metrics
                                self.findings[category].update(metrics)
                else:
                    # Handle files in docs directory
                    files = list(self.docs_dir.glob(pattern))
                    for file in files:
                        metrics = self.extract_metrics_from_file(file)
                        if metrics:
                            if category not in self.findings:
                                self.findings[category] = metrics
                            else:
                                # Merge metrics
                                self.findings[category].update(metrics)
    
    def calculate_summary_metrics(self):
        """Calculate summary metrics from all findings."""
        
        # Aggregate metrics
        for category, data in self.findings.items():
            if "total_files" in data:
                self.metrics["codebase"]["total_files"] = data["total_files"]
            if "lines_of_code" in data:
                self.metrics["codebase"]["lines_of_code"] = data["lines_of_code"]
            if "critical_issues" in data:
                self.metrics["risks"]["critical"] += data["critical_issues"]
            if "high_priority" in data:
                self.metrics["risks"]["high"] += data["high_priority"]
            if "technologies" in data and data["technologies"]:
                techs = data["technologies"].split(",")
                self.metrics["technologies"].extend([t.strip() for t in techs])
        
        # Remove duplicates from technologies
        self.metrics["technologies"] = list(set(self.metrics["technologies"]))
    
    def generate_executive_summary(self) -> str:
        """Generate the full executive summary."""
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate totals
        total_issues = sum(self.metrics["risks"].values())
        critical_count = self.metrics["risks"]["critical"]
        high_count = self.metrics["risks"]["high"]
        
        # Determine risk level
        if critical_count > 5:
            risk_level = "CRITICAL"
            risk_color = "🔴"
        elif critical_count > 0 or high_count > 10:
            risk_level = "HIGH"
            risk_color = "🟠"
        elif high_count > 5:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        summary = f"""# Executive Summary: Codebase Analysis

**Generated**: {current_date}
**Analysis Type**: Comprehensive Technical Assessment

## 🎯 Key Findings Overview

### Codebase Metrics
- **Total Files**: {self.metrics['codebase'].get('total_files', 'N/A')}
- **Lines of Code**: {self.metrics['codebase'].get('lines_of_code', 'N/A')}
- **Technologies**: {', '.join(self.metrics['technologies']) if self.metrics['technologies'] else 'Multiple'}
- **Overall Risk**: {risk_color} {risk_level}

### Issue Summary
| Priority | Count | Action Required |
|----------|-------|----------------|
| 🔴 Critical | {self.metrics['risks']['critical']} | Immediate |
| 🟠 High | {self.metrics['risks']['high']} | Within 30 days |
| 🟡 Medium | {self.metrics['risks']['medium']} | Within 90 days |
| 🟢 Low | {self.metrics['risks']['low']} | As resources permit |

**Total Issues Identified**: {total_issues}

## 📊 Technical Assessment

### Current State
The codebase analysis has identified {total_issues} total issues requiring attention, 
with {critical_count} critical issues that need immediate remediation.

### Technology Stack
Primary technologies in use:
{chr(10).join(['- ' + tech for tech in self.metrics['technologies'][:5]]) if self.metrics['technologies'] else '- Technology stack analysis in progress'}

## 💡 Recommendations

### Immediate Actions (Next 30 Days)
1. Address {critical_count} critical security/stability issues
2. Review and remediate {high_count} high-priority findings
3. Establish remediation timeline for remaining issues

### Strategic Initiatives (3-6 Months)
1. Implement comprehensive testing strategy
2. Modernize legacy components identified in analysis
3. Establish continuous monitoring and improvement processes

## 📈 Expected Outcomes

### Quick Wins (1-3 Months)
- Improved system stability
- Enhanced security posture
- Better performance metrics

### Long-term Benefits (6-12 Months)
- Reduced maintenance costs
- Increased development velocity
- Improved system scalability

## 🎯 Next Steps

1. **Review Detailed Reports**: Examine technical analysis in output/docs/
2. **Prioritize Remediation**: Focus on critical and high-priority issues
3. **Allocate Resources**: Assign team members to address findings
4. **Track Progress**: Establish KPIs and monitoring
5. **Schedule Follow-up**: Plan reassessment in 90 days

---
*This summary is based on analysis from specialized architecture, security, performance, and business logic agents.*
*For detailed technical information, refer to individual analysis reports.*
"""
        
        return summary
    
    def generate_one_pager(self) -> str:
        """Generate a one-page executive brief."""
        
        critical = self.metrics["risks"]["critical"]
        high = self.metrics["risks"]["high"]
        total_issues = sum(self.metrics["risks"].values())
        
        # Determine recommendation
        if critical > 5:
            recommendation = "IMMEDIATE ACTION REQUIRED"
            action = "Form crisis team immediately"
        elif critical > 0:
            recommendation = "URGENT REMEDIATION NEEDED"
            action = "Address critical issues within 7 days"
        elif high > 10:
            recommendation = "SIGNIFICANT WORK REQUIRED"
            action = "Plan remediation sprint"
        else:
            recommendation = "STANDARD MAINTENANCE"
            action = "Schedule regular improvements"
        
        one_pager = f"""# Codebase Analysis - Executive Brief

## 📊 Snapshot
**Technology**: {', '.join(self.metrics['technologies'][:3]) if self.metrics['technologies'] else 'Multi-technology'}
**Size**: {self.metrics['codebase'].get('lines_of_code', 'N/A')} LOC | {self.metrics['codebase'].get('total_files', 'N/A')} files
**Issues**: {critical} Critical | {high} High | {total_issues} Total

## 🎯 Key Finding
**{recommendation}**

## ⚡ Immediate Action
{action}

## 📈 Impact if Unaddressed
- System instability risk
- Security vulnerabilities
- Performance degradation
- Increased maintenance costs

## ✅ Recommended Approach
1. Fix critical issues (Week 1-2)
2. Address high priority (Week 3-4)
3. Plan modernization (Month 2-3)

## 💰 Resource Requirement
- **Team**: 2-4 developers
- **Timeline**: 3-6 months
- **Priority**: HIGH

---
*Full analysis available in detailed reports*
"""
        
        return one_pager
    
    def generate_dashboard_json(self) -> str:
        """Generate JSON metrics for dashboard integration."""
        
        dashboard = {
            "generated": datetime.now().isoformat(),
            "summary": {
                "total_files": self.metrics["codebase"].get("total_files", 0),
                "lines_of_code": self.metrics["codebase"].get("lines_of_code", 0),
                "technologies": self.metrics["technologies"],
                "total_issues": sum(self.metrics["risks"].values())
            },
            "risks": self.metrics["risks"],
            "status": "COMPLETE",
            "reports_generated": len(self.findings)
        }
        
        return json.dumps(dashboard, indent=2)
    
    def run(self):
        """Run the executive summary generation."""
        
        print("🔍 Collecting analysis findings...")
        self.collect_all_findings()
        
        print("📊 Calculating summary metrics...")
        self.calculate_summary_metrics()
        
        print("✍️ Generating executive summary...")
        summary = self.generate_executive_summary()
        summary_path = self.output_dir / "EXECUTIVE_SUMMARY.md"
        summary_path.write_text(summary)
        print(f"   ✅ Saved to {summary_path}")
        
        print("📝 Generating one-page brief...")
        one_pager = self.generate_one_pager()
        brief_path = self.output_dir / "EXECUTIVE_ONE_PAGER.md"
        brief_path.write_text(one_pager)
        print(f"   ✅ Saved to {brief_path}")
        
        print("📈 Generating dashboard metrics...")
        dashboard = self.generate_dashboard_json()
        dashboard_path = self.output_dir / "EXECUTIVE_DASHBOARD.json"
        dashboard_path.write_text(dashboard)
        print(f"   ✅ Saved to {dashboard_path}")
        
        print("\n✨ Executive summary generation complete!")
        print(f"\nGenerated files:")
        print(f"  • {summary_path}")
        print(f"  • {brief_path}")
        print(f"  • {dashboard_path}")
        
        # Print summary stats
        print(f"\n📊 Summary Statistics:")
        print(f"  • Technologies: {len(self.metrics['technologies'])}")
        print(f"  • Critical Issues: {self.metrics['risks']['critical']}")
        print(f"  • Total Issues: {sum(self.metrics['risks'].values())}")
        print(f"  • Reports Analyzed: {len(self.findings)}")

if __name__ == "__main__":
    generator = ExecutiveSummaryGenerator()
    generator.run()