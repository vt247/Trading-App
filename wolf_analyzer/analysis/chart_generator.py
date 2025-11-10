"""
Chart Generator
Creates visual charts with pattern annotations using mplfinance
"""

import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from wolf_analyzer.core.config import Config
from wolf_analyzer.analysis.pattern_recognition import Pattern


class ChartGenerator:
    """Generate annotated trading charts"""

    def __init__(self):
        """Initialize chart generator"""
        self.charts_dir = Config.CHARTS_DIR
        self.charts_dir.mkdir(exist_ok=True)

    def create_pattern_chart(
        self,
        df: pd.DataFrame,
        symbol: str,
        pattern: Optional[Pattern] = None,
        save: bool = True
    ) -> str:
        """
        Create chart with pattern annotations

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol
            pattern: Detected pattern to annotate
            save: Whether to save chart to file

        Returns:
            Path to saved chart file
        """
        # Prepare data
        df_plot = df.copy()

        # Create custom style
        mc = mpf.make_marketcolors(
            up='#26a69a',
            down='#ef5350',
            edge='inherit',
            wick='inherit',
            volume='in'
        )

        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            y_on_right=True
        )

        # Prepare annotations
        annotations = []
        hlines = {}

        if pattern:
            # Add entry zone
            hlines['entry_high'] = dict(
                y=pattern.entry_zone[1],
                color='green',
                linestyle='--',
                linewidth=1.5,
                label='Entry Zone'
            )
            hlines['entry_low'] = dict(
                y=pattern.entry_zone[0],
                color='green',
                linestyle='--',
                linewidth=1.5
            )

            # Add stop loss
            hlines['stop'] = dict(
                y=pattern.stop_loss,
                color='red',
                linestyle='-',
                linewidth=2,
                label='Stop Loss'
            )

            # Add targets
            for i, target in enumerate(pattern.targets[:3], 1):
                hlines[f'target_{i}'] = dict(
                    y=target,
                    color='blue',
                    linestyle=':',
                    linewidth=1,
                    label=f'Target {i}'
                )

        # Create figure
        fig, axes = mpf.plot(
            df_plot,
            type='candle',
            style=s,
            volume=True,
            title=f'{symbol} - {pattern.pattern_type if pattern else "Chart"}',
            ylabel='Price',
            ylabel_lower='Volume',
            hlines=hlines if hlines else None,
            returnfig=True,
            figsize=(14, 8)
        )

        # Add pattern info text
        if pattern:
            info_text = self._create_pattern_info_text(pattern)
            axes[0].text(
                0.02, 0.98,
                info_text,
                transform=axes[0].transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            )

        # Save chart
        if save:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol.replace('/', '_')}_{timestamp}.png"
            filepath = self.charts_dir / filename

            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return str(filepath)

        return ""

    def create_comparison_chart(
        self,
        symbols: List[str],
        data: Dict[str, pd.DataFrame]
    ) -> str:
        """
        Create comparison chart for multiple symbols

        Args:
            symbols: List of symbols to compare
            data: Dictionary mapping symbols to DataFrames

        Returns:
            Path to saved chart file
        """
        fig, axes = plt.subplots(len(symbols), 1, figsize=(14, 4 * len(symbols)))

        if len(symbols) == 1:
            axes = [axes]

        for i, symbol in enumerate(symbols):
            if symbol not in data:
                continue

            df = data[symbol]

            # Calculate normalized price (percentage change from start)
            normalized = (df['close'] / df['close'].iloc[0] - 1) * 100

            axes[i].plot(df.index, normalized, linewidth=2)
            axes[i].set_title(f'{symbol} - % Change')
            axes[i].set_ylabel('% Change')
            axes[i].grid(True, alpha=0.3)
            axes[i].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        plt.tight_layout()

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comparison_{timestamp}.png"
        filepath = self.charts_dir / filename

        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return str(filepath)

    def create_volume_profile_chart(
        self,
        df: pd.DataFrame,
        symbol: str
    ) -> str:
        """
        Create volume profile chart

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol

        Returns:
            Path to saved chart file
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Price chart
        ax1.plot(df.index, df['close'], linewidth=1.5, color='blue')
        ax1.set_title(f'{symbol} - Price Action')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.grid(True, alpha=0.3)

        # Volume profile (horizontal histogram)
        price_bins = 50
        price_range = df['high'].max() - df['low'].min()
        bin_size = price_range / price_bins

        volumes_at_price = []
        price_levels = []

        for i in range(price_bins):
            price_level = df['low'].min() + (i * bin_size)
            mask = (df['low'] <= price_level) & (df['high'] >= price_level)
            volume = df.loc[mask, 'volume'].sum()

            price_levels.append(price_level)
            volumes_at_price.append(volume)

        ax2.barh(price_levels, volumes_at_price, height=bin_size, alpha=0.7, color='green')
        ax2.set_title(f'{symbol} - Volume Profile')
        ax2.set_xlabel('Volume')
        ax2.set_ylabel('Price')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol.replace('/', '_')}_volume_profile_{timestamp}.png"
        filepath = self.charts_dir / filename

        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return str(filepath)

    @staticmethod
    def _create_pattern_info_text(pattern: Pattern) -> str:
        """Create info text box for pattern"""
        text = f"{pattern.pattern_type}\n"
        text += f"Confidence: {pattern.confidence:.1%}\n"
        text += f"R:R = {pattern.risk_reward:.2f}:1\n"
        text += f"\n"
        text += f"Entry: ${pattern.entry_zone[0]:.2f}-${pattern.entry_zone[1]:.2f}\n"
        text += f"Stop: ${pattern.stop_loss:.2f}\n"
        text += f"T1: ${pattern.targets[0]:.2f}\n"
        if len(pattern.targets) > 1:
            text += f"T2: ${pattern.targets[1]:.2f}\n"
        text += f"\n"
        text += f"Volume: {'✓' if pattern.volume_confirmation else '✗'}\n"
        text += f"Institutional: {'✓' if pattern.institutional_signal else '✗'}"

        return text


# Example usage
if __name__ == "__main__":
    from wolf_analyzer.data.market_data import MarketDataConnector
    from wolf_analyzer.analysis.pattern_recognition import PatternRecognition

    # Fetch data
    connector = MarketDataConnector()
    df = connector.get_ohlcv("BTC/USDT", timeframe="4h", limit=200)

    # Detect patterns
    recognizer = PatternRecognition()
    patterns = recognizer.analyze_chart(df, "BTC/USDT")

    # Generate chart
    generator = ChartGenerator()
    if patterns:
        chart_path = generator.create_pattern_chart(df, "BTC/USDT", patterns[0])
        print(f"Chart saved to: {chart_path}")
    else:
        print("No patterns detected")
