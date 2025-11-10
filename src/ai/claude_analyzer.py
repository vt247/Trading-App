"""
Claude AI Integration
Uses Anthropic's Claude API for intelligent market analysis and coaching
"""

import anthropic
from typing import Dict, List, Optional
import json

from src.core.config import Config
from src.analysis.pattern_recognition import Pattern


class ClaudeAnalyzer:
    """
    AI-powered market analysis using Claude API
    """

    def __init__(self):
        """Initialize Claude API client"""
        self.client = None
        if Config.ANTHROPIC_API_KEY:
            try:
                self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                print("✓ Claude AI connected")
            except Exception as e:
                print(f"✗ Failed to connect to Claude AI: {str(e)}")

    def analyze_pattern(
        self,
        pattern: Pattern,
        symbol: str,
        market_context: Dict
    ) -> str:
        """
        Get AI analysis of a detected pattern

        Args:
            pattern: Detected pattern object
            symbol: Trading pair
            market_context: Additional market context

        Returns:
            Human-readable analysis text
        """
        if not self.client:
            return "AI analysis unavailable (API key not configured)"

        prompt = self._build_pattern_analysis_prompt(pattern, symbol, market_context)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"AI analysis error: {str(e)}"

    def generate_daily_brief(
        self,
        watchlist_data: Dict,
        detected_patterns: Dict[str, List[Pattern]]
    ) -> str:
        """
        Generate daily market briefing

        Args:
            watchlist_data: Market data for watchlist
            detected_patterns: Patterns detected for each symbol

        Returns:
            Daily briefing text
        """
        if not self.client:
            return "AI briefing unavailable (API key not configured)"

        prompt = self._build_daily_brief_prompt(watchlist_data, detected_patterns)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Briefing generation error: {str(e)}"

    def coach_trade_journal(
        self,
        journal_entry: Dict,
        trading_history: List[Dict]
    ) -> str:
        """
        Provide coaching feedback on a trade journal entry

        Args:
            journal_entry: Current trade journal entry
            trading_history: Previous trades

        Returns:
            Coaching feedback text
        """
        if not self.client:
            return "AI coaching unavailable (API key not configured)"

        prompt = self._build_coaching_prompt(journal_entry, trading_history)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Coaching error: {str(e)}"

    def explain_institutional_behavior(
        self,
        pattern_type: str,
        volume_data: Dict,
        price_action: Dict
    ) -> str:
        """
        Explain what institutional traders are likely doing

        Args:
            pattern_type: Type of pattern detected
            volume_data: Volume analysis data
            price_action: Price action data

        Returns:
            Institutional behavior explanation
        """
        if not self.client:
            return "AI explanation unavailable"

        prompt = f"""
You are an expert in institutional trading behavior and FOOS4 methodology.

Pattern Detected: {pattern_type}
Volume Analysis: {json.dumps(volume_data, indent=2)}
Price Action: {json.dumps(price_action, indent=2)}

Explain in 2-3 paragraphs:
1. What institutional traders (market makers, hedge funds) are likely doing here
2. Why this pattern matters from an institutional perspective
3. What retail traders typically get wrong in this scenario

Be direct, educational, and focused on the psychology of institutional vs retail.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Explanation error: {str(e)}"

    @staticmethod
    def _build_pattern_analysis_prompt(
        pattern: Pattern,
        symbol: str,
        market_context: Dict
    ) -> str:
        """Build prompt for pattern analysis"""
        return f"""
You are a professional trading analyst specializing in FOOS4 methodology and institutional patterns.

Analyze this detected pattern and provide actionable insights:

SYMBOL: {symbol}
PATTERN: {pattern.pattern_type}
CONFIDENCE: {pattern.confidence:.1%}

TECHNICAL DETAILS:
- Entry Zone: ${pattern.entry_zone[0]:.2f} - ${pattern.entry_zone[1]:.2f}
- Stop Loss: ${pattern.stop_loss:.2f}
- Targets: {[f"${t:.2f}" for t in pattern.targets]}
- Risk:Reward: {pattern.risk_reward:.2f}:1
- Formation Time: {pattern.formation_time} hours
- Volume Confirmation: {pattern.volume_confirmation}
- Institutional Signal: {pattern.institutional_signal}

KEY LEVELS:
{json.dumps(pattern.key_levels, indent=2)}

MARKET CONTEXT:
{json.dumps(market_context, indent=2)}

Provide analysis in this format:

## PATTERN SUMMARY
[Brief explanation of what this pattern means]

## INSTITUTIONAL READING
[What institutions are likely doing here]

## HISTORICAL CONTEXT
[What typically happens with this pattern]

## TRADE SETUP
[How to approach this trade]

## RISK FACTORS
[What could invalidate this setup]

Be concise, actionable, and focused on education. Use the FOOS4 approach: teach the reader to see what institutions see.
"""

    @staticmethod
    def _build_daily_brief_prompt(
        watchlist_data: Dict,
        detected_patterns: Dict[str, List[Pattern]]
    ) -> str:
        """Build prompt for daily briefing"""
        patterns_summary = {}
        for symbol, patterns in detected_patterns.items():
            if patterns:
                patterns_summary[symbol] = [
                    {
                        'type': p.pattern_type,
                        'confidence': f"{p.confidence:.1%}",
                        'risk_reward': f"{p.risk_reward:.2f}:1"
                    }
                    for p in patterns[:2]  # Top 2 patterns per symbol
                ]

        return f"""
You are a professional trading analyst creating a daily pre-market briefing.

WATCHLIST DATA:
{json.dumps(watchlist_data, indent=2)}

DETECTED PATTERNS:
{json.dumps(patterns_summary, indent=2)}

Create a daily briefing in this format:

🐺 WOLF MARKET BRIEF - {Config.DAILY_BRIEF_TIME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## MARKET OVERVIEW
[Brief 2-3 sentence overview of overall market conditions]

## 🔥 HOT SETUPS FORMING
[List top 2-3 setups with confidence scores]

## ⚠️ WATCH TODAY
[Any critical levels or events to monitor]

## YOUR WATCHLIST STATUS
[Brief status of each symbol in watchlist]

Keep it concise, actionable, and focused on what matters for the trading day ahead.
Use the wolf/sheep metaphor: help traders think like wolves (anticipatory, patient) not sheep (reactive, impulsive).
"""

    @staticmethod
    def _build_coaching_prompt(
        journal_entry: Dict,
        trading_history: List[Dict]
    ) -> str:
        """Build prompt for trade coaching"""
        return f"""
You are a professional trading coach using the FOOS4 methodology and Wolf Market Analyzer principles.

CURRENT TRADE JOURNAL:
{json.dumps(journal_entry, indent=2)}

TRADING HISTORY (Last 10 trades):
{json.dumps(trading_history[-10:], indent=2)}

Provide coaching feedback in this format:

🐺 WOLF COACHING - AI Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━

## WHAT YOU DID RIGHT
[Specific praise for good decisions - be genuine, not generic]

## GROWTH AREAS
[Constructive areas for improvement]

## STATISTICS
[Analysis of their trading stats and trends]

## LEARNING PROGRESS
[Assessment of their pattern recognition and discipline]

## NEXT FOCUS
[Specific actionable item for next trade]

Be direct, honest, and educational. Focus on building their institutional reading skills.
Use the wolf/sheep framework: guide them toward anticipatory thinking, not reactive trading.
Celebrate discipline and patience. Challenge impulsive or emotional decisions.
"""


# Example usage
if __name__ == "__main__":
    analyzer = ClaudeAnalyzer()

    # Test institutional behavior explanation
    if analyzer.client:
        explanation = analyzer.explain_institutional_behavior(
            pattern_type="Ascending Triangle",
            volume_data={'decreasing': True, 'current_volume': 5200000},
            price_action={'touches': 4, 'slope': 0.15}
        )
        print("Institutional Explanation:")
        print(explanation)
