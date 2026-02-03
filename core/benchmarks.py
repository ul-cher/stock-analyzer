"""
Sector-specific benchmarks and configuration for stock analysis.
"""

from typing import Dict


class SectorBenchmarks:
    """Sector-specific benchmarks for financial analysis."""
    
    @staticmethod
    def get_benchmarks() -> Dict[str, Dict]:
        """
        Get sector-specific benchmarks.
        
        Returns:
            Dictionary of sector benchmarks
        """
        return {
            'Technology': {
                'pe_low': 20, 'pe_high': 35, 'pe_very_high': 50,
                'peg_good': 1.5, 'peg_acceptable': 2.5,
                'debt_low': 30, 'debt_moderate': 80, 'debt_high': 150,
                'roe_excellent': 18, 'roe_good': 12, 'roe_acceptable': 8,
                'revenue_growth_strong': 12, 'revenue_growth_good': 6,
                'margin_excellent': 15, 'margin_good': 8, 'margin_acceptable': 3,
                'description': 'Secteur à forte croissance, valorisations élevées acceptables',
                'weights': {
                    'pe': 1.0, 'peg': 2.5, 'debt': 0.5,
                    'roe': 2.0, 'growth': 3.0, 'margin': 3.0
                }
            },
            'Financial Services': {
                'pe_low': 12, 'pe_high': 18, 'pe_very_high': 25,
                'peg_good': 1.0, 'peg_acceptable': 1.8,
                'debt_low': 100, 'debt_moderate': 300, 'debt_high': 500,
                'roe_excellent': 15, 'roe_good': 10, 'roe_acceptable': 7,
                'revenue_growth_strong': 8, 'revenue_growth_good': 4,
                'margin_excellent': 25, 'margin_good': 15, 'margin_acceptable': 10,
                'description': 'Endettement structurel élevé, focus sur ROE et marges',
                'weights': {
                    'pe': 1.5, 'peg': 0.5, 'debt': 0.5,
                    'roe': 4.0, 'growth': 1.5, 'margin': 4.0
                }
            },
            'Healthcare': {
                'pe_low': 15, 'pe_high': 25, 'pe_very_high': 40,
                'peg_good': 1.2, 'peg_acceptable': 2.0,
                'debt_low': 40, 'debt_moderate': 90, 'debt_high': 180,
                'roe_excellent': 20, 'roe_good': 14, 'roe_acceptable': 10,
                'revenue_growth_strong': 10, 'revenue_growth_good': 5,
                'margin_excellent': 20, 'margin_good': 12, 'margin_acceptable': 6,
                'description': 'Secteur défensif, marges élevées, croissance stable',
                'weights': {
                    'pe': 1.5, 'peg': 1.5, 'debt': 1.5,
                    'roe': 2.5, 'growth': 2.0, 'margin': 3.0
                }
            },
            'Consumer Cyclical': {
                'pe_low': 12, 'pe_high': 20, 'pe_very_high': 30,
                'peg_good': 1.0, 'peg_acceptable': 1.8,
                'debt_low': 50, 'debt_moderate': 120, 'debt_high': 200,
                'roe_excellent': 18, 'roe_good': 12, 'roe_acceptable': 8,
                'revenue_growth_strong': 10, 'revenue_growth_good': 5,
                'margin_excellent': 12, 'margin_good': 7, 'margin_acceptable': 3,
                'description': 'Sensible aux cycles économiques, volatilité importante',
                'weights': {
                    'pe': 2.0, 'peg': 1.5, 'debt': 2.0,
                    'roe': 2.0, 'growth': 2.5, 'margin': 2.0
                }
            },
            'Consumer Defensive': {
                'pe_low': 15, 'pe_high': 22, 'pe_very_high': 30,
                'peg_good': 1.2, 'peg_acceptable': 2.0,
                'debt_low': 50, 'debt_moderate': 100, 'debt_high': 180,
                'roe_excellent': 25, 'roe_good': 18, 'roe_acceptable': 12,
                'revenue_growth_strong': 7, 'revenue_growth_good': 3,
                'margin_excellent': 15, 'margin_good': 9, 'margin_acceptable': 5,
                'description': 'Secteur défensif, croissance faible mais stable',
                'weights': {
                    'pe': 1.5, 'peg': 0.5, 'debt': 2.0,
                    'roe': 3.5, 'growth': 1.0, 'margin': 3.5
                }
            },
            'Energy': {
                'pe_low': 8, 'pe_high': 15, 'pe_very_high': 25,
                'peg_good': 0.8, 'peg_acceptable': 1.5,
                'debt_low': 40, 'debt_moderate': 100, 'debt_high': 180,
                'roe_excellent': 15, 'roe_good': 10, 'roe_acceptable': 5,
                'revenue_growth_strong': 15, 'revenue_growth_good': 8,
                'margin_excellent': 15, 'margin_good': 8, 'margin_acceptable': 3,
                'description': 'Secteur cyclique, lié aux prix des matières premières',
                'weights': {
                    'pe': 1.0, 'peg': 1.0, 'debt': 2.5,
                    'roe': 2.5, 'growth': 2.0, 'margin': 3.0
                }
            },
            'Industrials': {
                'pe_low': 12, 'pe_high': 20, 'pe_very_high': 30,
                'peg_good': 1.2, 'peg_acceptable': 2.0,
                'debt_low': 50, 'debt_moderate': 120, 'debt_high': 200,
                'roe_excellent': 16, 'roe_good': 11, 'roe_acceptable': 7,
                'revenue_growth_strong': 10, 'revenue_growth_good': 5,
                'margin_excellent': 12, 'margin_good': 7, 'margin_acceptable': 3,
                'description': 'Secteur diversifié, sensible à l\'économie',
                'weights': {
                    'pe': 1.5, 'peg': 1.5, 'debt': 2.5,
                    'roe': 2.5, 'growth': 2.0, 'margin': 2.0
                }
            },
            'Real Estate': {
                'pe_low': 15, 'pe_high': 25, 'pe_very_high': 35,
                'peg_good': 1.5, 'peg_acceptable': 2.5,
                'debt_low': 80, 'debt_moderate': 200, 'debt_high': 350,
                'roe_excellent': 12, 'roe_good': 8, 'roe_acceptable': 5,
                'revenue_growth_strong': 8, 'revenue_growth_good': 4,
                'margin_excellent': 40, 'margin_good': 25, 'margin_acceptable': 15,
                'description': 'Endettement élevé normal, focus sur les dividendes',
                'weights': {
                    'pe': 0.5, 'peg': 0.5, 'debt': 1.0,
                    'roe': 2.5, 'growth': 1.5, 'margin': 6.0
                }
            },
            'Materials': {
                'pe_low': 10, 'pe_high': 18, 'pe_very_high': 28,
                'peg_good': 1.0, 'peg_acceptable': 1.8,
                'debt_low': 45, 'debt_moderate': 110, 'debt_high': 190,
                'roe_excellent': 14, 'roe_good': 9, 'roe_acceptable': 5,
                'revenue_growth_strong': 12, 'revenue_growth_good': 6,
                'margin_excellent': 14, 'margin_good': 8, 'margin_acceptable': 3,
                'description': 'Secteur cyclique, dépendant des matières premières',
                'weights': {
                    'pe': 1.5, 'peg': 1.0, 'debt': 2.0,
                    'roe': 2.5, 'growth': 2.5, 'margin': 2.5
                }
            },
            'Utilities': {
                'pe_low': 12, 'pe_high': 20, 'pe_very_high': 28,
                'peg_good': 1.5, 'peg_acceptable': 2.5,
                'debt_low': 100, 'debt_moderate': 250, 'debt_high': 400,
                'roe_excellent': 12, 'roe_good': 8, 'roe_acceptable': 5,
                'revenue_growth_strong': 5, 'revenue_growth_good': 2,
                'margin_excellent': 20, 'margin_good': 12, 'margin_acceptable': 6,
                'description': 'Secteur défensif, croissance limitée, dividendes élevés',
                'weights': {
                    'pe': 1.5, 'peg': 0.5, 'debt': 1.5,
                    'roe': 3.0, 'growth': 0.5, 'margin': 5.0
                }
            },
            'Communication Services': {
                'pe_low': 15, 'pe_high': 25, 'pe_very_high': 40,
                'peg_good': 1.2, 'peg_acceptable': 2.0,
                'debt_low': 50, 'debt_moderate': 130, 'debt_high': 220,
                'roe_excellent': 20, 'roe_good': 13, 'roe_acceptable': 8,
                'revenue_growth_strong': 12, 'revenue_growth_good': 6,
                'margin_excellent': 18, 'margin_good': 10, 'margin_acceptable': 4,
                'description': 'Mixte de croissance et de maturité',
                'weights': {
                    'pe': 1.5, 'peg': 2.0, 'debt': 1.5,
                    'roe': 2.5, 'growth': 2.5, 'margin': 2.0
                }
            }
        }
    
    @staticmethod
    def get_geographic_adjustments() -> Dict[str, Dict]:
        """
        Get geographic adjustment factors.
        
        Returns:
            Dictionary of geographic adjustments
        """
        return {
            'United States': {
                'pe_factor': 1.0,
                'debt_factor': 1.0,
                'growth_factor': 1.0,
                'description': 'Marché de référence'
            },
            'China': {
                'pe_factor': 0.8,
                'debt_factor': 1.3,
                'growth_factor': 1.3,
                'description': 'Valorisations plus faibles, croissance plus élevée'
            },
            'Europe': {
                'pe_factor': 0.85,
                'debt_factor': 1.1,
                'growth_factor': 0.9,
                'description': 'Valorisations légèrement inférieures'
            },
            'Japan': {
                'pe_factor': 0.75,
                'debt_factor': 1.2,
                'growth_factor': 0.8,
                'description': 'Valorisations basses, croissance modérée'
            },
            'Emerging Markets': {
                'pe_factor': 0.7,
                'debt_factor': 1.4,
                'growth_factor': 1.4,
                'description': 'Décote de risque, forte croissance'
            }
        }