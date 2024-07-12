from pathlib import Path

import pandas as pd


def main():
    DATA_DIR = Path("../data/steam")
    PREPRO_WORK_DIR = DATA_DIR / "preprocessed"
    PREPRO_WORK_DIR.mkdir(parents=True, exist_ok=True)

    users_items_df = pd.read_feather(DATA_DIR / "australian_users_items.df.feather")
    user_reviews_df = pd.read_feather(DATA_DIR / "australian_user_reviews.df.feather")

    users_df = users_items_df.merge(right=user_reviews_df)
    users_df.to_pickle(PREPRO_WORK_DIR / "users_df.pkl")


if __name__ == "__main__":
    main()
