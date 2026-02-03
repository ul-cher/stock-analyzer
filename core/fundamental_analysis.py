"""
Fundamental analysis module for evaluating company financials.
"""

from typing import Dict, Any, List, Tuple, Optional
from core.benchmarks import SectorBenchmarks


class FundamentalAnalyzer:
    """Performs fundamental analysis on stock data."""
    
    def __init__(self, fundamentals: Dict[str, Any], sector: str, 
                 industry: str, country: str):
        """
        Initialize fundamental analyzer.
        
        Args:
            fundamentals: Dictionary of fundamental metrics
            sector: Company sector
            industry: Company industry
            country: Company country
        """
        self.fundamentals = fundamentals
        self.sector = sector if sector and sector != 'N/A' else 'Unknown'
        self.industry = industry if industry and industry != 'N/A' else 'Unknown'
        self.country = country if country and country != 'N/A' else 'Unknown'
        
        # Get benchmarks and adjustments
        benchmarks_data = SectorBenchmarks.get_benchmarks()
        geo_data = SectorBenchmarks.get_geographic_adjustments()
        
        self.benchmarks = benchmarks_data.get(self.sector, benchmarks_data.get('Technology'))
        self.geographic_zone = self._determine_geographic_zone()
        self.geo_adj = geo_data.get(self.geographic_zone, geo_data['United States'])
    
    def _determine_geographic_zone(self) -> str:
        """Determine geographic zone from country."""
        if self.country in ['United States', 'USA']:
            return 'United States'
        elif self.country in ['France', 'Germany', 'United Kingdom', 'Italy', 'Spain',
                              'Netherlands', 'Belgium', 'Switzerland', 'Sweden', 'Norway']:
            return 'Europe'
        elif self.country in ['China', 'Hong Kong']:
            return 'China'
        elif self.country == 'Japan':
            return 'Japan'
        elif self.country in ['India', 'Brazil', 'Mexico', 'South Africa', 'Indonesia',
                              'Turkey', 'Thailand', 'Malaysia', 'Philippines']:
            return 'Emerging Markets'
        else:
            return 'United States'  # Default
    
    def analyze_valuation(self) -> Tuple[float, List[Tuple[str, float, str]]]:
        """Analyze valuation metrics (PE, PEG)."""
        score = 0.0
        signals = []
        weights = self.benchmarks.get('weights', {})
        
        # P/E Ratio analysis
        pe = self.fundamentals.get('PE_Ratio')
        if pe and isinstance(pe, (int, float)) and pe > 0:
            pe_low = self.benchmarks['pe_low'] * self.geo_adj['pe_factor']
            pe_high = self.benchmarks['pe_high'] * self.geo_adj['pe_factor']
            pe_very_high = self.benchmarks['pe_very_high'] * self.geo_adj['pe_factor']
            
            if pe < pe_low:
                base_score = 2
                signals.append((f"P/E {pe:.1f} (réf: {pe_low:.1f}) - Sous-évaluation", 
                              base_score * weights.get('pe', 1.0), "Positif"))
                score += base_score * weights.get('pe', 1.0)
            elif pe < pe_high:
                base_score = 1
                signals.append((f"P/E {pe:.1f} - Correct", 
                              base_score * weights.get('pe', 1.0), "Positif"))
                score += base_score * weights.get('pe', 1.0)
            elif pe > pe_very_high:
                base_score = -2
                signals.append((f"P/E {pe:.1f} (max: {pe_very_high:.1f}) - Survalorisation", 
                              base_score * weights.get('pe', 1.0), "Négatif"))
                score += base_score * weights.get('pe', 1.0)
        
        # PEG Ratio analysis
        peg = self.fundamentals.get('PEG_Ratio')
        if peg and isinstance(peg, (int, float)) and peg > 0:
            peg_good = self.benchmarks['peg_good']
            peg_acceptable = self.benchmarks['peg_acceptable']
            
            if peg < peg_good:
                base_score = 2
                signals.append((f"PEG {peg:.2f} - Croissance attractive", 
                              base_score * weights.get('peg', 1.0), "Positif"))
                score += base_score * weights.get('peg', 1.0)
            elif peg > peg_acceptable:
                base_score = -1
                signals.append((f"PEG {peg:.2f} - Croissance chère", 
                              base_score * weights.get('peg', 1.0), "Négatif"))
                score += base_score * weights.get('peg', 1.0)
        
        return score, signals
    
    def analyze_debt(self) -> Tuple[float, List[Tuple[str, float, str]]]:
        """Analyze debt metrics."""
        score = 0.0
        signals = []
        weights = self.benchmarks.get('weights', {})
        
        dte = self.fundamentals.get('Debt_to_Equity')
        if dte and isinstance(dte, (int, float)):
            debt_low = self.benchmarks['debt_low'] * self.geo_adj['debt_factor']
            debt_mod = self.benchmarks['debt_moderate'] * self.geo_adj['debt_factor']
            debt_high = self.benchmarks['debt_high'] * self.geo_adj['debt_factor']
            
            if dte < debt_low:
                base_score = 2
                signals.append((f"Dette {dte:.0f}% - Très solide", 
                              base_score * weights.get('debt', 1.0), "Positif"))
                score += base_score * weights.get('debt', 1.0)
            elif dte < debt_mod:
                signals.append((f"Dette {dte:.0f}% - Modéré", 0, "Neutre"))
            elif dte < debt_high:
                base_score = -1
                signals.append((f"Dette {dte:.0f}% - Élevé", 
                              base_score * weights.get('debt', 1.0), "Négatif"))
                score += base_score * weights.get('debt', 1.0)
            else:
                base_score = -3
                signals.append((f"Dette {dte:.0f}% - Très élevé", 
                              base_score * weights.get('debt', 1.0), "Négatif"))
                score += base_score * weights.get('debt', 1.0)
        
        # Current Ratio
        current_ratio = self.fundamentals.get('Current_Ratio')
        if current_ratio and isinstance(current_ratio, (int, float)):
            if current_ratio > 2.0:
                signals.append((f"Liquidité excellente ({current_ratio:.2f})", 1.0, "Positif"))
                score += 1.0
            elif current_ratio < 1.0:
                signals.append((f"Liquidité préoccupante ({current_ratio:.2f})", -1.5, "Négatif"))
                score -= 1.5
        
        return score, signals
    
    def analyze_profitability(self) -> Tuple[float, List[Tuple[str, float, str]]]:
        """Analyze profitability metrics (ROE, margins)."""
        score = 0.0
        signals = []
        weights = self.benchmarks.get('weights', {})
        
        # ROE analysis
        roe = self.fundamentals.get('ROE')
        if roe and isinstance(roe, (int, float)):
            roe_pct = roe * 100
            roe_excellent = self.benchmarks['roe_excellent']
            roe_good = self.benchmarks['roe_good']
            roe_acceptable = self.benchmarks['roe_acceptable']
            
            if roe_pct > roe_excellent:
                base_score = 2
                signals.append((f"ROE {roe_pct:.1f}% - Excellence", 
                              base_score * weights.get('roe', 1.0), "Positif"))
                score += base_score * weights.get('roe', 1.0)
            elif roe_pct > roe_good:
                base_score = 1
                signals.append((f"ROE {roe_pct:.1f}% - Bon", 
                              base_score * weights.get('roe', 1.0), "Positif"))
                score += base_score * weights.get('roe', 1.0)
            elif roe_pct < roe_acceptable:
                base_score = -2
                signals.append((f"ROE {roe_pct:.1f}% - Faible", 
                              base_score * weights.get('roe', 1.0), "Négatif"))
                score += base_score * weights.get('roe', 1.0)
        
        # Profit Margin analysis
        profit_margin = self.fundamentals.get('Profit_Margin')
        if profit_margin and isinstance(profit_margin, (int, float)):
            margin_pct = profit_margin * 100
            margin_excellent = self.benchmarks['margin_excellent']
            margin_good = self.benchmarks['margin_good']
            margin_acceptable = self.benchmarks['margin_acceptable']
            
            if margin_pct > margin_excellent:
                base_score = 2
                signals.append((f"Marge {margin_pct:.1f}% - Excellente", 
                              base_score * weights.get('margin', 1.0), "Positif"))
                score += base_score * weights.get('margin', 1.0)
            elif margin_pct > margin_good:
                base_score = 1
                signals.append((f"Marge {margin_pct:.1f}% - Correcte", 
                              base_score * weights.get('margin', 1.0), "Positif"))
                score += base_score * weights.get('margin', 1.0)
            elif margin_pct < margin_acceptable:
                base_score = -2
                signals.append((f"Marge {margin_pct:.1f}% - Très faible", 
                              base_score * weights.get('margin', 1.0), "Négatif"))
                score += base_score * weights.get('margin', 1.0)
        
        return score, signals
    
    def analyze_growth(self) -> Tuple[float, List[Tuple[str, float, str]]]:
        """Analyze growth metrics."""
        score = 0.0
        signals = []
        weights = self.benchmarks.get('weights', {})
        
        rev_growth = self.fundamentals.get('Revenue_Growth')
        if rev_growth and isinstance(rev_growth, (int, float)):
            rev_growth_pct = rev_growth * 100
            growth_strong = self.benchmarks['revenue_growth_strong'] * self.geo_adj['growth_factor']
            growth_good = self.benchmarks['revenue_growth_good'] * self.geo_adj['growth_factor']
            
            if rev_growth_pct > growth_strong:
                base_score = 2
                signals.append((f"Croissance {rev_growth_pct:.1f}% - Forte", 
                              base_score * weights.get('growth', 1.0), "Positif"))
                score += base_score * weights.get('growth', 1.0)
            elif rev_growth_pct > growth_good:
                base_score = 1
                signals.append((f"Croissance {rev_growth_pct:.1f}% - Positive", 
                              base_score * weights.get('growth', 1.0), "Positif"))
                score += base_score * weights.get('growth', 1.0)
            elif rev_growth_pct < 0:
                base_score = -2
                signals.append((f"Décroissance {rev_growth_pct:.1f}% - Problématique", 
                              base_score * weights.get('growth', 1.0), "Négatif"))
                score += base_score * weights.get('growth', 1.0)
        
        # Free Cash Flow
        fcf = self.fundamentals.get('Free_Cash_Flow')
        market_cap = self.fundamentals.get('Market_Cap')
        if fcf and isinstance(fcf, (int, float)) and market_cap and isinstance(market_cap, (int, float)):
            if fcf > 0 and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100
                if fcf_yield > 8:
                    signals.append((f"Cash-flow libre excellent ({fcf_yield:.1f}%)", 2.0, "Positif"))
                    score += 2.0
                elif fcf_yield > 5:
                    signals.append((f"Cash-flow libre bon ({fcf_yield:.1f}%)", 1.0, "Positif"))
                    score += 1.0
            elif fcf < 0:
                signals.append(("Cash-flow libre NÉGATIF", -2.0, "Négatif"))
                score -= 2.0
        
        return score, signals
    
    def full_fundamental_analysis(self) -> Tuple[float, str, List[Tuple[str, float, str]]]:
        """
        Perform complete fundamental analysis.
        
        Returns:
            Tuple of (score, health_status, signals)
        """
        all_signals = []
        total_score = 0.0
        
        # Add context info
        all_signals.append((f"Secteur: {self.sector}", 0, "Info"))
        all_signals.append((f"Pays: {self.country} ({self.geographic_zone})", 0, "Info"))
        
        # Valuation
        val_score, val_signals = self.analyze_valuation()
        all_signals.extend(val_signals)
        total_score += val_score
        
        # Debt
        debt_score, debt_signals = self.analyze_debt()
        all_signals.extend(debt_signals)
        total_score += debt_score
        
        # Profitability
        prof_score, prof_signals = self.analyze_profitability()
        all_signals.extend(prof_signals)
        total_score += prof_score
        
        # Growth
        growth_score, growth_signals = self.analyze_growth()
        all_signals.extend(growth_signals)
        total_score += growth_score
        
        # Determine health status
        if total_score >= 6:
            health = "Excellent"
        elif total_score >= 3:
            health = "Bon"
        elif total_score >= 0:
            health = "Moyen"
        elif total_score >= -3:
            health = "Préoccupant"
        else:
            health = "Mauvais"
        
        return total_score, health, all_signals