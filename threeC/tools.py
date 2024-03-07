import argparse
import logging

from utils import config_utils
import account_info


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument("--list_accounts", help="Display accounts", action="store_true")
    args = parser.parse_args()

    if args.list_accounts:
        py3cw = config_utils.get_3c_interface()
        account = account_info.AccountInfo(py3cw)
        for act in account.accounts:
            exchange = act["exchange_name"]
            act_usd_value = float(act["usd_amount"])
            logger.info(f"Exchange: {exchange} - ${act_usd_value:,.2f} value")
        if len(account.accounts) == 0:
            logger.info("No accounts found")


if __name__ == "__main__":
    main()
