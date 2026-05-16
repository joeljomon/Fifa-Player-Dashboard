import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

REQUIRED_COLUMNS = [
    "Player", "Club", "Position", "Age", "Market_Value", "Appearances",
    "Minutes", "Goals", "Assists", "Yellow_Cards", "Red_Cards"
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    numeric_cols = ["Age", "Market_Value", "Appearances", "Minutes", "Goals", "Assists", "Yellow_Cards", "Red_Cards"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Player", "Club", "Position", "Age", "Minutes"])
    df = df[df["Minutes"] > 0]

    df["Goals_per_90"] = (df["Goals"] / df["Minutes"]) * 90
    df["Assists_per_90"] = (df["Assists"] / df["Minutes"]) * 90
    df["Goal_Contrib_per_90"] = ((df["Goals"] + df["Assists"]) / df["Minutes"]) * 90
    df["Cards_per_90"] = ((df["Yellow_Cards"] + df["Red_Cards"]) / df["Minutes"]) * 90
    df["Minutes_per_App"] = df["Minutes"] / df["Appearances"].replace(0, np.nan)

    return df.fillna(0)


def choose_best_k(X_scaled, min_k=2, max_k=6):
    scores = {}
    max_k = min(max_k, len(X_scaled) - 1)
    for k in range(min_k, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        scores[k] = silhouette_score(X_scaled, labels)
    return max(scores, key=scores.get), scores


def cluster_players(df: pd.DataFrame, k: int = 4) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    features = [
        "Age", "Market_Value", "Minutes", "Goals_per_90",
        "Assists_per_90", "Goal_Contrib_per_90", "Cards_per_90", "Minutes_per_App"
    ]

    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k = min(k, len(df))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    df["Cluster"] = model.fit_predict(X_scaled)

    labels = label_clusters(df)
    df["Playing_Style"] = df["Cluster"].map(labels)
    return df, features


def label_clusters(df: pd.DataFrame) -> dict:
    labels = {}
    cluster_summary = df.groupby("Cluster")[[
        "Goals_per_90", "Assists_per_90", "Minutes", "Age", "Cards_per_90", "Market_Value"
    ]].mean()

    for cluster_id, row in cluster_summary.iterrows():
        if row["Goals_per_90"] == cluster_summary["Goals_per_90"].max():
            labels[cluster_id] = "Goal-Scoring Forward"
        elif row["Assists_per_90"] == cluster_summary["Assists_per_90"].max():
            labels[cluster_id] = "Creative Playmaker"
        elif row["Minutes"] == cluster_summary["Minutes"].max():
            labels[cluster_id] = "High-Minute Starter"
        elif row["Age"] == cluster_summary["Age"].min():
            labels[cluster_id] = "Young Developing Player"
        else:
            labels[cluster_id] = "Balanced Contributor"

    return labels


if __name__ == "__main__":
    df = load_data("data/sample_players.csv")
    df = clean_data(df)
    clustered, features = cluster_players(df, k=4)
    clustered.to_csv("data/clustered_players.csv", index=False)
    print("Saved data/clustered_players.csv")
