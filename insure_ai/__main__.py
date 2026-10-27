from __future__ import annotations
import argparse,json,sys
from .dataio import synthetic_banner
from .intake import process_submissions,intake_evaluation
from .wording import ask,qa_evaluation
from .review import review_results
from .inventory import portfolio_insight
from .dashboard import write_dashboard

def dump(obj):
    print(synthetic_banner()); print(json.dumps(obj,indent=2,ensure_ascii=False))

def main(argv=None):
    parser=argparse.ArgumentParser(prog="python -m insure_ai",description="Synthetic, deterministic insurance AI architecture prototype")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("intake"); sub.add_parser("intake-eval")
    q=sub.add_parser("ask"); q.add_argument("question"); q.add_argument("--contract"); q.add_argument("--version")
    sub.add_parser("qa-eval"); sub.add_parser("review"); sub.add_parser("inventory"); sub.add_parser("dashboard")
    a=parser.parse_args(argv)
    if a.command=="intake": dump(process_submissions())
    elif a.command=="intake-eval": dump(intake_evaluation())
    elif a.command=="ask": dump(ask(a.question,a.contract,a.version))
    elif a.command=="qa-eval": dump(qa_evaluation())
    elif a.command=="review": dump(review_results())
    elif a.command=="inventory": dump(portfolio_insight())
    elif a.command=="dashboard": print(synthetic_banner()); print("Dashboard written:",write_dashboard())
    return 0

if __name__=="__main__": sys.exit(main())
