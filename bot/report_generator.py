"""
Report Generator Module
Generates trustworthiness reports based on analysis
"""

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates human-readable trustworthiness reports"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_report(self, analysis: Dict, trust_score: Dict, user_id: str) -> str:
        """
        Generate a comprehensive trustworthiness report
        
        Args:
            analysis: Analysis results from AccountAnalyzer
            trust_score: Trust score from TrustedAccountsManager
            user_id: User ID being analyzed
        
        Returns:
            Formatted report string
        """
        try:
            # Start building the report
            report_parts = []
            
            # Header
            username = analysis.get('username', 'unknown')
            report_parts.append(f"🔍 RUGGUARD TRUST REPORT for @{username}")
            report_parts.append("")
            
            # Trust Status (most important first)
            trust_status = self._generate_trust_status(trust_score)
            report_parts.append(trust_status)
            
            # Risk Assessment
            risk_assessment = self._generate_risk_assessment(analysis)
            report_parts.append(risk_assessment)
            
            # Key Metrics
            key_metrics = self._generate_key_metrics(analysis)
            report_parts.append(key_metrics)
            
            # Detailed Analysis
            detailed_analysis = self._generate_detailed_analysis(analysis)
            report_parts.append(detailed_analysis)
            
            # Footer
            report_parts.append("")
            report_parts.append("⚠️ This is an automated analysis. DYOR!")
            report_parts.append("#RUGGUARD #TrustScore")
            
            # Join all parts
            full_report = "\n".join(report_parts)
            
            # Ensure it fits Twitter's character limit
            if len(full_report) > 280:
                full_report = self._truncate_report(report_parts)
            
            return full_report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return f"🔍 RUGGUARD: Error analyzing @{username}. Please try again later. #RUGGUARD"
    
    def _generate_trust_status(self, trust_score: Dict) -> str:
        """Generate trust status section"""
        try:
            if trust_score.get('is_trusted', False):
                trust_level = trust_score.get('trust_level', 'unknown')
                if trust_level == 'directly_trusted':
                    return "✅ VERIFIED TRUSTED ACCOUNT\n• Account is on Project RUGGUARD's trusted list\n• Automatically vouched by the system"
                elif trust_level == 'network_backed':
                    trusted_followers = trust_score.get('trusted_followers', [])
                    count = len(trusted_followers)
                    return f"🤝 NETWORK BACKED ACCOUNT\n• Followed by {count} trusted accounts from our list\n• Meets minimum threshold of 3 trusted followers"
            else:
                trusted_count = trust_score.get('trusted_followers_count', 0)
                if trusted_count > 0:
                    return f"⚠️ PARTIALLY BACKED\n• Followed by {trusted_count} trusted account(s)\n• Needs 3+ for full verification"
                else:
                    return "❌ UNVERIFIED ACCOUNT\n• Not on trusted list\n• No trusted accounts following\n• Requires manual verification"
        except Exception as e:
            logger.error(f"Error generating trust status: {str(e)}")
            return "❓ UNKNOWN: Unable to verify trust status"
    
    def _generate_risk_assessment(self, analysis: Dict) -> str:
        """Generate risk assessment section"""
        try:
            risk_score = analysis.get('risk_score', 50)
            
            if risk_score < 20:
                risk_emoji = "🟢"
                risk_label = "LOW RISK"
            elif risk_score < 40:
                risk_emoji = "🟡"
                risk_label = "MODERATE RISK"
            elif risk_score < 70:
                risk_emoji = "🟠"
                risk_label = "HIGH RISK"
            else:
                risk_emoji = "🔴"
                risk_label = "VERY HIGH RISK"
            
            return f"{risk_emoji} {risk_label} (Score: {risk_score}/100)"
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {str(e)}")
            return "❓ RISK: Unable to calculate"
    
    def _generate_key_metrics(self, analysis: Dict) -> str:
        """Generate key metrics section"""
        try:
            metrics = []
            
            # Account age
            age_data = analysis.get('account_age', {})
            age_days = age_data.get('days', 0)
            if age_days > 365:
                metrics.append(f"📅 {age_days//365}y old")
            elif age_days > 30:
                metrics.append(f"📅 {age_days//30}m old")
            else:
                metrics.append(f"📅 {age_days}d old")
            
            # Followers
            raw_metrics = analysis.get('raw_metrics', {})
            followers = raw_metrics.get('followers_count', 0)
            if followers > 1000000:
                metrics.append(f"👥 {followers//1000000}M followers")
            elif followers > 1000:
                metrics.append(f"👥 {followers//1000}K followers")
            else:
                metrics.append(f"👥 {followers} followers")
            
            # Engagement
            engagement = analysis.get('engagement_analysis', {})
            avg_likes = engagement.get('avg_likes', 0)
            if avg_likes > 100:
                metrics.append("📊 High engagement")
            elif avg_likes > 10:
                metrics.append("📊 Moderate engagement")
            else:
                metrics.append("📊 Low engagement")
            
            return " | ".join(metrics)
            
        except Exception as e:
            logger.error(f"Error generating key metrics: {str(e)}")
            return "📊 Metrics unavailable"
    
    def _generate_detailed_analysis(self, analysis: Dict) -> str:
        """Generate detailed analysis section"""
        try:
            details = []
            
            # Bio analysis
            bio_analysis = analysis.get('bio_analysis', {})
            if bio_analysis.get('has_bio', False):
                risk_level = bio_analysis.get('risk_level', 'unknown')
                if risk_level == 'high':
                    details.append("⚠️ Suspicious bio content")
                elif risk_level == 'low':
                    details.append("✅ Clean bio content")
            else:
                details.append("⚠️ No bio")
            
            # Activity patterns
            activity = analysis.get('activity_patterns', {})
            if activity.get('recent_activity', False):
                details.append("✅ Recently active")
            else:
                details.append("⚠️ Inactive recently")
            
            # Content analysis
            content = analysis.get('content_analysis', {})
            suspicious_ratio = content.get('suspicious_content_ratio', 0)
            if suspicious_ratio > 0.3:
                details.append("🚨 High suspicious content")
            elif suspicious_ratio > 0.1:
                details.append("⚠️ Some suspicious content")
            else:
                details.append("✅ Clean content")
            
            # Verification
            if analysis.get('verification_status', False):
                details.append("✅ Verified account")
            
            return " | ".join(details) if details else "Analysis complete"
            
        except Exception as e:
            logger.error(f"Error generating detailed analysis: {str(e)}")
            return "Analysis details unavailable"
    
    def _truncate_report(self, report_parts: List[str]) -> str:
        """Truncate report to fit Twitter's character limit"""
        try:
            # Priority order: trust status, risk assessment, key metrics, footer
            essential_parts = [
                report_parts[0],  # Header
                report_parts[2],  # Trust status
                report_parts[3],  # Risk assessment
                report_parts[4],  # Key metrics
                "⚠️ DYOR! #RUGGUARD"  # Simplified footer
            ]
            
            truncated = "\n".join(essential_parts)
            
            # If still too long, further truncate
            if len(truncated) > 280:
                # Ultra-compact version
                username = report_parts[0].split('@')[1].split()[0] if '@' in report_parts[0] else 'user'
                trust_line = report_parts[2].split(':')[0] if ':' in report_parts[2] else report_parts[2]
                risk_line = report_parts[3].split('(')[0].strip() if '(' in report_parts[3] else report_parts[3]
                
                truncated = f"🔍 @{username}\n{trust_line}\n{risk_line}\n⚠️ DYOR! #RUGGUARD"
            
            return truncated[:280]  # Hard limit
            
        except Exception as e:
            logger.error(f"Error truncating report: {str(e)}")
            return "🔍 RUGGUARD: Analysis complete. Check logs for details. #RUGGUARD"
    
    def generate_error_report(self, username: str, error_type: str = "general") -> str:
        """Generate an error report"""
        error_messages = {
            "user_not_found": f"🔍 RUGGUARD: User @{username} not found or protected.",
            "api_error": f"🔍 RUGGUARD: API error analyzing @{username}. Try again later.",
            "analysis_failed": f"🔍 RUGGUARD: Analysis failed for @{username}.",
            "general": f"🔍 RUGGUARD: Error analyzing @{username}. Please try again."
        }
        
        message = error_messages.get(error_type, error_messages["general"])
        return f"{message} #RUGGUARD"
    
    def generate_rate_limit_report(self) -> str:
        """Generate report for rate limit situations"""
        return "🔍 RUGGUARD: Rate limit reached. Please try again in 15 minutes. #RUGGUARD"
