from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=25565)
    parser.add_argument('--model', type=str, default='llama3')
    return parser.parse_args()