import pickle

import click
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from rxn_cluster_token_prompt.clustering.clusterer import ClustererFitter, inspect_clusters, Clusterer
from rxn_cluster_token_prompt.clustering.data_loading import FP_COLUMN, load_df


@click.command()
@click.option('--clusterer_pkl', type=str, required=True, help='Where to store the clusterer.')
@click.option(
    '--pca_components',
    type=int,
    default=3,
    help='The order of dimension reduction, default is 3.'
)
@click.option(
    '--n_clusters', type=int, default=10, help='The number of clusters to use, default is 10.'
)
def main(clusterer_pkl: str, pca_components: int, n_clusters: int):
    """Create a clusterer based on some reaction data.

    The clusterer is used later on to get the reaction class for the diversity
    model relying on class tokens."""

    selected_fp_column = FP_COLUMN

    # Load Data
    df = load_df()
    fps = np.array(df[selected_fp_column].tolist())
    print('Loaded fingerprints to train clustering algorithm:', len(fps))

    all_fps = fps
    print('Merged, shuffled:', len(all_fps))

    pca = PCA(n_components=pca_components)
    kmeans = KMeans(n_clusters=n_clusters)

    print('Fitting clusterer...')
    _ = ClustererFitter(
        data=all_fps,
        scaler=pca,
        clusterer=kmeans,
        random_seed=42,
        fit_scaler_on=len(all_fps),
        fit_clusterer_on=len(all_fps),
    )
    print('Fitting clusterer... Done.')

    clusterer = Clusterer(pca=pca, kmeans=kmeans)

    print('Clusters')
    inspect_clusters(clusterer, all_fps)

    print(f'Saving clusterer to {clusterer_pkl}...')
    with open(clusterer_pkl, 'wb') as f:
        pickle.dump(clusterer, f)
    print(f'Saving clusterer to {clusterer_pkl}... Done')

    print('\n\nCheck: reloading the clusterer, should print exact same values as above')
    with open(clusterer_pkl, 'rb') as f:
        loaded: Clusterer = pickle.load(f)
    print('Clusters')
    inspect_clusters(loaded, all_fps)


if __name__ == '__main__':
    main()
