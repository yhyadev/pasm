import argparse
import pathlib

def parse_args():
    parser = argparse.ArgumentParser(prog="pasm")

    parser.add_argument("file_path", type=pathlib.Path)
    parser.add_argument("--emit-outputs", action="store_true", default=False)
    
    return parser.parse_args()
