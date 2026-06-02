from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd


DATASET_PATH = Path(__file__).with_name("dataset.csv")
REPORT_PATH = Path(__file__).with_name("report.txt")
STUDENT_ID = "70221789"
DATASET_VARIANT = 1

df = pd.read_csv(DATASET_PATH, encoding="utf-8-sig")
df = df.rename(columns={"Unnamed: 0": "id"})


def get_numeric_columns() -> list[str]:
    return list(df.select_dtypes(include="number").columns)


def get_categorical_columns() -> list[str]:
    return list(df.select_dtypes(exclude="number").columns)


def build_report() -> str:
    buffer = StringIO()

    with redirect_stdout(buffer):
        print(df.shape)
        print()
        df.info()
        print()
        print("Missing values:")
        print(df.isna().sum())
        print()
        print("Numeric columns:")
        for column in get_numeric_columns():
            series = df[column]
            print(
                f"{column}> "
                f"mean={series.mean():.2f}; "
                f"median={series.median():.2f}; "
                f"std={series.std():.2f}"
            )
        print()
        print("Categorical columns:")
        for column in get_categorical_columns():
            print(column)
            print(df[column].value_counts(dropna=False))
            print()

    return buffer.getvalue()


def main() -> None:
    report = build_report()
    print(report, end="")
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
