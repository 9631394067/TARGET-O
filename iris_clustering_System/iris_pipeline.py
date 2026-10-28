"""
Iris Clustering Explorer (unsupervised learning)
Goal: discover flower groups WITHOUT using class labels, then compare with the known species.
Workflow: Load -> EDA -> Scale -> PCA -> Cluster (KMeans / Hierarchical / GMM / DBSCAN) -> Evaluate -> Compare with labels
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend so plots can be saved to files
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (silhouette_score, davies_bouldin_score, calinski_harabasz_score,
                             adjusted_rand_score, normalized_mutual_info_score,
                             homogeneity_score, completeness_score, v_measure_score)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "data", "iris.data")
OUT_DIR = os.path.join(BASE, "outputs")
FEATURES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
RANDOM_STATE = 42  # fixed seed so results are reproducible


# ---------------------------------------------------------------- 1. LOAD DATA
def load_data(path=DATA_PATH):
    """Read the headerless UCI iris file and name the columns."""
    df = pd.read_csv(path, header=None, names=FEATURES + ["species"]).dropna()  # drops blank trailing line
    df["species"] = df["species"].str.replace("Iris-", "", regex=False)  # 'Iris-setosa' -> 'setosa'
    return df


# ---------------------------------------------------------------- 2. EDA
def run_eda(df, save=True):
    """Print summary stats and save histogram, box, correlation and pair plots."""
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Shape:", df.shape)
    print("\nMissing values:\n", df.isna().sum())          # check data quality
    print("\nDuplicate rows:", df.duplicated().sum())      # iris has a few known duplicates
    print("\nSummary statistics:\n", df[FEATURES].describe().round(2))
    print("\nClass balance (only for EDA, NOT used for clustering):\n", df["species"].value_counts())

    # Histograms show each feature's distribution/skew
    df[FEATURES].hist(bins=20, figsize=(9, 6), color="steelblue", edgecolor="white")
    plt.suptitle("Feature distributions"); plt.tight_layout()
    if save: plt.savefig(f"{OUT_DIR}/eda_histograms.png", dpi=120)
    plt.close()

    # Box plots reveal scale differences and outliers
    plt.figure(figsize=(8, 5)); sns.boxplot(data=df[FEATURES], palette="Set2")
    plt.title("Box plots (raw, unscaled)")
    if save: plt.savefig(f"{OUT_DIR}/eda_boxplots.png", dpi=120)
    plt.close()

    # Correlation heatmap: petal features are strongly correlated
    plt.figure(figsize=(6, 5)); sns.heatmap(df[FEATURES].corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation matrix")
    if save: plt.savefig(f"{OUT_DIR}/eda_correlation.png", dpi=120)
    plt.close()

    # Pair plot (coloured by species ONLY for visual insight)
    g = sns.pairplot(df, hue="species", corner=True, height=2)
    if save: g.figure.savefig(f"{OUT_DIR}/eda_pairplot.png", dpi=100)
    plt.close("all")


# ---------------------------------------------------------------- 3. FEATURE SCALING
def scale_features(df, method="standard"):
    """Scale features so no column dominates distance calculations (clustering is distance-based)."""
    scaler = {"standard": StandardScaler(), "minmax": MinMaxScaler(), "none": None}[method]
    X = df[FEATURES].values
    return X if scaler is None else scaler.fit_transform(X)  # 'none' = raw data for comparison


def plot_scaling_effect(df):
    """Visual proof of why scaling matters: before vs after box plots."""
    os.makedirs(OUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.boxplot(data=df[FEATURES], ax=ax[0], palette="Set2"); ax[0].set_title("Before scaling")
    sns.boxplot(data=pd.DataFrame(scale_features(df), columns=FEATURES), ax=ax[1], palette="Set2")
    ax[1].set_title("After StandardScaler")
    plt.tight_layout(); plt.savefig(f"{OUT_DIR}/scaling_effect.png", dpi=120); plt.close()


# ---------------------------------------------------------------- 4. DIMENSIONALITY REDUCTION
def reduce_pca(X, n=2):
    """PCA compresses 4 features into 2 axes for plotting; also returns variance explained."""
    pca = PCA(n_components=n, random_state=RANDOM_STATE)
    return pca.fit_transform(X), pca


def reduce_tsne(X):
    """t-SNE: non-linear 2-D embedding, good for seeing local cluster structure."""
    return TSNE(n_components=2, perplexity=30, random_state=RANDOM_STATE, init="pca").fit_transform(X)


# ---------------------------------------------------------------- 5. CHOOSING K
def find_best_k(X, k_range=range(2, 11), save=True):
    """Elbow (inertia) + silhouette scores help pick the number of clusters."""
    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(X, km.labels_),
                     "davies_bouldin": davies_bouldin_score(X, km.labels_)})
    res = pd.DataFrame(rows)
    if save:
        os.makedirs(OUT_DIR, exist_ok=True)
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        ax[0].plot(res.k, res.inertia, "o-"); ax[0].set(title="Elbow method", xlabel="k", ylabel="Inertia (WCSS)")
        ax[1].plot(res.k, res.silhouette, "s-", color="green"); ax[1].set(title="Silhouette score", xlabel="k")
        plt.tight_layout(); plt.savefig(f"{OUT_DIR}/choose_k.png", dpi=120); plt.close()
    return res


# ---------------------------------------------------------------- 6. CLUSTERING ALGORITHMS
def run_kmeans(X, k=3):
    """K-Means: assigns each point to the nearest of k centroids, iteratively refined."""
    return KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit_predict(X)


def run_hierarchical(X, k=3, linkage_method="ward"):
    """Agglomerative clustering: repeatedly merges the two closest clusters (bottom-up)."""
    return AgglomerativeClustering(n_clusters=k, linkage=linkage_method).fit_predict(X)


def run_gmm(X, k=3):
    """Gaussian Mixture: soft clustering that models each cluster as an elliptical Gaussian."""
    return GaussianMixture(n_components=k, random_state=RANDOM_STATE).fit_predict(X)


def run_dbscan(X, eps=0.6, min_samples=5):
    """DBSCAN: density-based; finds arbitrary-shaped clusters and labels outliers as -1."""
    return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)


def plot_dendrogram(X, method="ward", save=True):
    """Dendrogram shows the full merge tree; a tall vertical gap suggests the natural cluster count."""
    Z = linkage(X, method=method)
    plt.figure(figsize=(11, 5)); dendrogram(Z, truncate_mode="lastp", p=30, leaf_rotation=90)
    plt.title(f"Hierarchical clustering dendrogram ({method} linkage)"); plt.ylabel("Distance")
    if save:
        os.makedirs(OUT_DIR, exist_ok=True); plt.savefig(f"{OUT_DIR}/dendrogram.png", dpi=120)
    plt.close()


# ---------------------------------------------------------------- 7. EVALUATION
def internal_metrics(X, labels):
    """Label-free quality scores (higher silhouette/CH and lower DB are better)."""
    mask = labels != -1  # ignore DBSCAN noise points
    if len(set(labels[mask])) < 2:
        return {"silhouette": np.nan, "davies_bouldin": np.nan, "calinski_harabasz": np.nan}
    return {"silhouette": silhouette_score(X[mask], labels[mask]),
            "davies_bouldin": davies_bouldin_score(X[mask], labels[mask]),
            "calinski_harabasz": calinski_harabasz_score(X[mask], labels[mask])}


def external_metrics(true, labels):
    """Compare clusters against the real species (1.0 = perfect agreement, ~0 = random)."""
    return {"ARI": adjusted_rand_score(true, labels), "NMI": normalized_mutual_info_score(true, labels),
            "homogeneity": homogeneity_score(true, labels), "completeness": completeness_score(true, labels),
            "v_measure": v_measure_score(true, labels)}


def crosstab(df, labels):
    """Contingency table: rows = true species, columns = discovered clusters."""
    return pd.crosstab(df["species"], pd.Series(labels, name="cluster", index=df.index))


# ---------------------------------------------------------------- 8. VISUALIZATION
def scatter_2d(coords, labels, title, ax=None):
    """Draw 2-D points coloured by cluster (or species) label."""
    ax = ax or plt.gca()
    sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=labels, palette="Set1", s=55, ax=ax, edgecolor="k")
    ax.set_title(title)
    return ax


def compare_plot(coords, df, results, save=True):
    """Side-by-side grid: true species vs every algorithm's clusters, all in PCA space."""
    n = len(results) + 1
    fig, axes = plt.subplots(1, n, figsize=(4.4 * n, 4.2))
    scatter_2d(coords, df["species"].values, "True species", axes[0])
    for ax, (name, lab) in zip(axes[1:], results.items()):
        scatter_2d(coords, lab.astype(str), name, ax)
    plt.tight_layout()
    if save:
        os.makedirs(OUT_DIR, exist_ok=True); plt.savefig(f"{OUT_DIR}/clusters_vs_species.png", dpi=110)
    plt.close()


def plot_crosstab(ct, title, path=None):
    """Heatmap of the species-vs-cluster table."""
    plt.figure(figsize=(5, 3.5)); sns.heatmap(ct, annot=True, fmt="d", cmap="Blues"); plt.title(title)
    plt.tight_layout()
    if path: plt.savefig(path, dpi=120)
    plt.close()


# ---------------------------------------------------------------- 9. FULL WORKFLOW
def main():
    df = load_data()                                   # step 1: load
    run_eda(df)                                        # step 2: explore
    plot_scaling_effect(df)                            # step 3: show scaling effect
    X = scale_features(df, "standard")                 # step 3: scale
    coords, pca = reduce_pca(X)                        # step 4: PCA for plotting
    print("\nPCA variance explained:", pca.explained_variance_ratio_.round(3))

    print("\nChoosing k:\n", find_best_k(X).round(3))  # step 5: elbow + silhouette
    plot_dendrogram(X)

    results = {"K-Means": run_kmeans(X), "Hierarchical (Ward)": run_hierarchical(X),   # step 6: cluster
               "GMM": run_gmm(X), "DBSCAN": run_dbscan(X)}

    rows = []
    for name, lab in results.items():                  # step 7: evaluate every model
        rows.append({"model": name, "n_clusters": len(set(lab) - {-1}), **internal_metrics(X, lab),
                     **external_metrics(df["species"], lab)})
        print(f"\n{name} - species vs cluster:\n", crosstab(df, lab))
    summary = pd.DataFrame(rows).set_index("model").round(3)
    print("\n=== MODEL COMPARISON ===\n", summary)
    summary.to_csv(f"{OUT_DIR}/model_comparison.csv")

    compare_plot(coords, df, results)                  # step 8: visualize
    plot_crosstab(crosstab(df, results["K-Means"]), "K-Means vs species", f"{OUT_DIR}/kmeans_crosstab.png")
    print(f"\nAll plots and tables saved in: {OUT_DIR}")


if __name__ == "__main__":
    main()