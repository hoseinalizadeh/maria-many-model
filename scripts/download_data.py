import os
import argparse
from azureml.opendatasets import OjSalesSimulated


def download_data(target_path, maxfiles=None):

    # Pull all of the data
    oj_sales_files = OjSalesSimulated.get_file_dataset()

    if maxfiles:
        # Pull only the first <maxfiles> files
        oj_sales_files = oj_sales_files.take(maxfiles)

    # Create a folder to download
    if not os.path.exists(target_path):
        os.mkdir(target_path)

    # Download the data
    oj_sales_files.download(target_path, overwrite=True)

    return target_path


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default='oj_sales_data')
    parser.add_argument("--maxfiles", type=int, default=None)
    args_parsed = parser.parse_args(args)
    return args_parsed


if __name__ == "__main__":
    args = parse_args()
    download_data(target_path=args.path, maxfiles=args.maxfiles)
