#!/usr/bin/env python3
"""
Command-line interface for Stock Analyzer.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import StockAnalyzer
from data.database import DatabaseManager


def print_results(results: dict):
    """Print analysis results in a formatted way."""
    if not results.get('success'):
        print(f"❌ Error: {results.get('error', 'Unknown error')}")
        return
    
    ticker = results['ticker']
    price = results.get('current_price', 0)
    
    print(f"\n{'='*60}")
    print(f"ANALYSE DE {ticker}")
    print(f"{'='*60}")
    
    print(f"\n💰 Prix Actuel: ${price:.2f}" if price else "\n💰 Prix Actuel: N/A")
    print(f"🏢 Secteur: {results.get('sector', 'N/A')}")
    print(f"🌍 Pays: {results.get('country', 'N/A')}")
    
    print(f"\n{'='*60}")
    print("SCORES")
    print(f"{'='*60}")
    print(f"Score Fondamental: {results.get('fundamental_score', 0):+.1f}")
    
    tech_score = results.get('technical_score')
    if tech_score is not None:
        print(f"Score Technique: {tech_score:+.1f}")
    else:
        print(f"Score Technique: N/A (fondamentaux trop faibles)")
    
    print(f"Score Final: {results.get('final_score', 0):+.1f}")
    
    print(f"\n{'='*60}")
    print("RECOMMANDATION")
    print(f"{'='*60}")
    rec = results.get('recommendation', 'N/A')
    horizon = results.get('time_horizon', 'N/A')
    
    if "ACHAT" in rec:
        symbol = "✅"
    elif "VENTE" in rec:
        symbol = "❌"
    else:
        symbol = "⚠️"
    
    print(f"{symbol} {rec}")
    print(f"Horizon: {horizon}")
    
    # Fundamental signals
    if results.get('fundamental_signals'):
        print(f"\n{'='*60}")
        print("ANALYSE FONDAMENTALE")
        print(f"{'='*60}")
        for signal, score, sentiment in results['fundamental_signals']:
            if sentiment == "Info":
                print(f"ℹ️  {signal}")
            elif sentiment in ["Positif", "Haussier"]:
                print(f"✅ {signal} (Score: +{score:.1f})")
            elif sentiment in ["Négatif", "Baissier"]:
                print(f"❌ {signal} (Score: {score:.1f})")
            else:
                print(f"➖ {signal}")
    
    # Technical signals
    if results.get('technical_signals'):
        print(f"\n{'='*60}")
        print("ANALYSE TECHNIQUE")
        print(f"{'='*60}")
        for signal, score, sentiment in results['technical_signals']:
            if sentiment in ["Positif", "Haussier"]:
                print(f"✅ {signal} (Score: +{score:.1f})")
            elif sentiment in ["Négatif", "Baissier"]:
                print(f"❌ {signal} (Score: {score:.1f})")
            else:
                print(f"➖ {signal}")
    
    print(f"\n{'='*60}")
    print("AVERTISSEMENT")
    print(f"{'='*60}")
    print("Cette analyse est fournie à titre informatif uniquement.")
    print("Elle ne constitue pas un conseil financier ou d'investissement.")
    print("Consultez toujours un conseiller financier professionnel.")
    print(f"{'='*60}\n")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Stock Analyzer - Analyse technique et fondamentale d\'actions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s AAPL                    # Analyser Apple
  %(prog)s MSFT GOOGL TSLA        # Analyser plusieurs actions
  %(prog)s MC.PA --period 2y      # LVMH avec 2 ans de données
  %(prog)s --clear-cache          # Vider le cache
  %(prog)s --stats                # Afficher les statistiques du cache
        """
    )
    
    parser.add_argument(
        'tickers',
        nargs='*',
        help='Symbole(s) boursier(s) à analyser (ex: AAPL, MSFT, MC.PA)'
    )
    
    parser.add_argument(
        '-p', '--period',
        default='1y',
        choices=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        help='Période pour les données historiques (défaut: 1y)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Vider tout le cache'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Afficher les statistiques du cache'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    db = DatabaseManager()
    
    # Handle cache operations
    if args.clear_cache:
        db.clear_all_cache()
        print("✅ Cache vidé avec succès!")
        return 0
    
    if args.stats:
        stats = db.get_cache_stats()
        print(f"\n📊 Statistiques du Cache")
        print(f"{'='*40}")
        print(f"Prix en cache: {stats['stock_prices']}")
        print(f"Fondamentaux en cache: {stats['fundamentals']}")
        print(f"Analyses sauvegardées: {stats['analysis_results']}")
        print(f"{'='*40}\n")
        return 0
    
    # Require at least one ticker
    if not args.tickers:
        parser.print_help()
        return 1
    
    # Analyze each ticker
    for ticker in args.tickers:
        try:
            if args.verbose:
                print(f"\n🔍 Analyse de {ticker.upper()} en cours...")
            
            analyzer = StockAnalyzer(ticker, db)
            
            if not analyzer.fetch_all_data(args.period):
                print(f"❌ Impossible de récupérer les données pour {ticker}")
                continue
            
            results = analyzer.analyze()
            print_results(results)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Analyse interrompue par l'utilisateur")
            return 130
        except Exception as e:
            print(f"\n❌ Erreur lors de l'analyse de {ticker}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue
    
    return 0


if __name__ == '__main__':
    sys.exit(main())