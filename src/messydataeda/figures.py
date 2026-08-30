"""Chart generation. Kept separate from eda.py so the underlying numbers stay
directly testable without touching matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def save_revenue_by_category(revenue: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=revenue.values, y=revenue.index, ax=ax, color="#4C72B0")
    ax.set_xlabel("Gross revenue (USD)")
    ax.set_ylabel("Product category")
    ax.set_title("Revenue by category (invalid-quantity rows excluded)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_payment_method_before_after(naive: pd.Series, true: pd.Series, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=False)
    naive.sort_values(ascending=False).head(8).plot.bar(ax=axes[0], color="#C44E52")
    axes[0].set_title("Naive: raw spelling, uncleaned")
    axes[0].set_ylabel("Orders")
    axes[0].tick_params(axis="x", rotation=45)

    true.sort_values(ascending=False).plot.bar(ax=axes[1], color="#55A868")
    axes[1].set_title("True: after standardizing casing/format")
    axes[1].tick_params(axis="x", rotation=45)

    fig.suptitle("Cleaning changes the answer to 'which payment method dominates?'")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_order_status_funnel(funnel: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = funnel["Stage"].map(
        {"Completed": "#55A868", "In progress": "#DD8452", "Lost": "#C44E52"}
    )
    ax.barh(funnel.index, funnel["Count"], color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Orders")
    ax.set_title("Order status funnel")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_rating_by_category(ratings: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=ratings.values, y=ratings.index, ax=ax, color="#8172B2")
    ax.set_xlim(0, 5)
    ax.set_xlabel("Mean customer rating (delivered + rated orders only)")
    ax.set_ylabel("Product category")
    ax.set_title("Average rating by category")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
