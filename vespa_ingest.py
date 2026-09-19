"""CLI companion sharing exactly the desktop engine (original CLI was unavailable)."""
import argparse
import threading
from pathlib import Path
from engine import Config,scan,execute,export_csv,report_path

def main():
    parser=argparse.ArgumentParser(description='Vespa travel content organizer — ingestion locale')
    parser.add_argument('--config',required=True,help='Profil JSON version 2')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run',action='store_true',help='Aperçu, mode par défaut')
    mode.add_argument('--execute',action='store_true',help='Analyser puis copier les fichiers prêts')
    parser.add_argument('--report',help='Chemin du CSV (facultatif en aperçu)')
    args=parser.parse_args()
    try:
        c=Config.load(args.config)
        def emit(k,v):
            if k=='log':print(v)
        rows=scan(c,emit)
        if args.execute:execute(c,rows,emit)
        if args.report or args.execute:export_csv(args.report or report_path(c),rows)
        print(f'{len(rows)} fichiers lus ; {sum(r.status=="Copié" for r in rows)} copiés.')
        return 1 if any(r.status in {'Erreur','Conflit','À vérifier'} for r in rows) else 0
    except Exception as e:print(f'Erreur : {e}');return 2

if __name__=='__main__':raise SystemExit(main())
