# python -m streamlit run iris_clustering/app.py


"""
Iris Clustering Explorer - Streamlit web UI.  Run:  streamlit run app.py
Tabs follow the ML workflow: Data -> EDA -> Scaling -> Clustering -> Compare with species -> Predict.
"""
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
import iris_pipeline as ip   # reuse all logic from the pipeline module

st.set_page_config(page_title="Iris Clustering Explorer", layout="wide")
st.title("🌸 Iris Clustering Explorer")
st.caption("Discover flower groups without class labels, then check them against the real species.")


@st.cache_data  # cache so the file is read only once
def get_data():
    return ip.load_data()


df = get_data()

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")  # folder holding the 3 flower photos


def show_species_image(name, width=260):
    """Show images/<name>.jpg|jpeg|png if present, otherwise a hint on where to put it."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = os.path.join(IMG_DIR, f"{name}.{ext}")
        if os.path.exists(path):
            st.image(path, caption=f"Iris {name}", width=width)
            return
    st.info(f"Add a photo named images/{name}.jpg to show it here.")


# ---------------- Sidebar: user controls ----------------
st.sidebar.header("Settings")
scaling = st.sidebar.selectbox("Feature scaling", ["standard", "minmax", "none"])       # choose scaler
algo = st.sidebar.selectbox("Algorithm", ["K-Means", "Hierarchical", "GMM", "DBSCAN"])  # choose model
k = st.sidebar.slider("Number of clusters (k)", 2, 8, 3)
link = st.sidebar.selectbox("Linkage (hierarchical)", ["ward", "complete", "average", "single"])
eps = st.sidebar.slider("DBSCAN eps", 0.1, 2.0, 0.6, 0.05)
min_s = st.sidebar.slider("DBSCAN min_samples", 2, 15, 5)
proj = st.sidebar.radio("2-D projection", ["PCA", "t-SNE"])

# ---------------- Run the chosen pipeline ----------------
X = ip.scale_features(df, scaling)                                    # scale
coords = ip.reduce_pca(X)[0] if proj == "PCA" else ip.reduce_tsne(X)  # project to 2-D
if algo == "K-Means":
    labels = ip.run_kmeans(X, k)
elif algo == "Hierarchical":
    labels = ip.run_hierarchical(X, k, link)
elif algo == "GMM":
    labels = ip.run_gmm(X, k)
else:
    labels = ip.run_dbscan(X, eps, min_s)

tabs = st.tabs(["📄 Data", "🌺 Species Guide", "🔍 EDA", "⚖️ Scaling", "🧩 Clusters", "🆚 vs Species", "🌼 Predict"])

# ---------------- Tab 1: data ----------------
with tabs[0]:
    st.dataframe(df, width="stretch", height=300)
    st.write(df[ip.FEATURES].describe().round(2))

# ---------------- Tab 2: species guide (photos + real measurements) ----------------
with tabs[1]:
    st.write("What each species looks like and how big its parts are (cm), calculated from the dataset.")
    cols = st.columns(3)
    for col, sp in zip(cols, ["setosa", "versicolor", "virginica"]):
        with col:
            show_species_image(sp)
            sub = df[df["species"] == sp][ip.FEATURES]
            st.markdown(f"**Iris {sp}**")
            st.dataframe(sub.agg(["mean", "min", "max"]).T.round(2), width="stretch")
    st.caption("Setosa has much smaller petals; versicolor and virginica overlap, which is why clustering confuses them.")

# ---------------- Tab 3: EDA ----------------
with tabs[2]:
    c1, c2 = st.columns(2)
    feat = c1.selectbox("Feature", ip.FEATURES)
    fig, ax = plt.subplots(); sns.histplot(df[feat], kde=True, ax=ax); c1.pyplot(fig)       # distribution
    fig, ax = plt.subplots(); sns.heatmap(df[ip.FEATURES].corr(), annot=True, cmap="coolwarm", ax=ax)
    c2.pyplot(fig)                                                                           # correlations
    xf, yf = st.columns(2)
    fx = xf.selectbox("X axis", ip.FEATURES, index=2); fy = yf.selectbox("Y axis", ip.FEATURES, index=3)
    fig, ax = plt.subplots(); sns.scatterplot(data=df, x=fx, y=fy, hue="species", ax=ax); st.pyplot(fig)

# ---------------- Tab 3: scaling ----------------
with tabs[3]:
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.boxplot(data=df[ip.FEATURES], ax=ax[0]); ax[0].set_title("Raw")
    sns.boxplot(data=pd.DataFrame(X, columns=ip.FEATURES), ax=ax[1]); ax[1].set_title(f"After '{scaling}'")
    st.pyplot(fig)
    st.info("Clustering uses distances, so unscaled large-range features would dominate.")

# ---------------- Tab 4: clusters ----------------
with tabs[4]:
    c1, c2 = st.columns([3, 2])
    fig, ax = plt.subplots(figsize=(6, 5)); ip.scatter_2d(coords, labels.astype(str), f"{algo} clusters ({proj})", ax)
    c1.pyplot(fig)
    m = ip.internal_metrics(X, labels)                                    # label-free quality scores
    c2.metric("Silhouette (higher better)", f"{m['silhouette']:.3f}")
    c2.metric("Davies-Bouldin (lower better)", f"{m['davies_bouldin']:.3f}")
    c2.metric("Calinski-Harabasz", f"{m['calinski_harabasz']:.1f}")
    c2.write("Cluster sizes:"); c2.write(pd.Series(labels).value_counts().sort_index())
    if algo == "Hierarchical":                                            # dendrogram only for hierarchical
        fig, ax = plt.subplots(figsize=(10, 4))
        dendrogram(linkage(X, method=link), truncate_mode="lastp", p=30, leaf_rotation=90, ax=ax)
        st.pyplot(fig)
    if st.checkbox("Show elbow / silhouette for choosing k"):
        res = ip.find_best_k(X, save=False); st.line_chart(res.set_index("k")[["inertia"]])
        st.line_chart(res.set_index("k")[["silhouette"]])

# ---------------- Tab 5: compare with true classes ----------------
with tabs[5]:
    ct = ip.crosstab(df, labels)
    c1, c2 = st.columns(2)
    fig, ax = plt.subplots(figsize=(5, 3.5)); sns.heatmap(ct, annot=True, fmt="d", cmap="Blues", ax=ax)
    c1.pyplot(fig)                                                        # species vs cluster table
    c2.write(pd.Series(ip.external_metrics(df["species"], labels), name="score").round(3))
    st.caption("ARI/NMI close to 1 = clusters match species. Setosa separates easily; versicolor/virginica overlap.")
    st.subheader("All algorithms side by side")
    rows = []
    for name, lab in {"K-Means": ip.run_kmeans(X, 3), "Hierarchical": ip.run_hierarchical(X, 3, link),
                      "GMM": ip.run_gmm(X, 3), "DBSCAN": ip.run_dbscan(X, eps, min_s)}.items():
        rows.append({"model": name, **ip.internal_metrics(X, lab), **ip.external_metrics(df["species"], lab)})
    st.dataframe(pd.DataFrame(rows).set_index("model").round(3))

# ---------------- Tab 6: predict a new flower ----------------
with tabs[6]:
    st.write("Enter measurements (cm) and see which discovered cluster the flower falls in (K-Means, k=3).")
    cols = st.columns(4)
    vals = [cols[i].number_input(f, float(df[f].min()), float(df[f].max()) + 2, float(df[f].mean()))
            for i, f in enumerate(ip.FEATURES)]
    if st.button("Assign cluster"):
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        sc = StandardScaler().fit(df[ip.FEATURES])                        # fit scaler on training data
        km = KMeans(3, n_init=10, random_state=ip.RANDOM_STATE).fit(sc.transform(df[ip.FEATURES]))
        cl = km.predict(sc.transform(pd.DataFrame([vals], columns=ip.FEATURES)))[0]                          # scale new point the same way
        majority = ip.crosstab(df, km.labels_)[cl].idxmax()               # most common real species in cluster
        st.success(f"Cluster {cl} — most similar to **{majority}**")
        show_species_image(majority)