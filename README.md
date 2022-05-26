# NFT.mine

NFT.mine is an xDeepFM-based recommender backend for OpenSea NFT buyers.

[![build status][build status badge]][build status page]

## Authors

Shuwei Li, Yucheng Jin, Pin-Lun Hsu, Ya-Sin Luo

## Install Packages

Use the following command to install packages needed to run `NFT.mine.py`.

```sh
pip install -r requirements.txt
```

## Launch NFT.mine

Use the following command to launch NFT.mine.

```sh
python NFT.mine.py
```

By default, NFT.mine will listen on the `PORT` specified in `NFT.mine.py`. NFT.mine supports two query combinations:

```
http://localhost:PORT/recommend?wallet_address=12345678
```

When requested, NFT.mine will make recommendations with respect for a user based on their wallet address in the query.

```
http://localhost:PORT/recommend?wallet_address=12345678&collection_slug=abcdefgh
```

When requested, NFT.mine will make recommendations with respect for a user based on their wallet address in the query but the recoooemndations will be limited to only the collection slug in the query.

## Response

NFT.mine will respond with a pre-rendered image containing the recommendations. The recommendations will be rendered in a grid whose number of rows and columns can be adjusted by modifying the `suggestion_cols` and `suggestion_cols` defined in `NFT.mine.py`. Pre-rendered images will be cached in `cache/` so re-rendering is not needed for the same request query. To force re-rendering, delete `cache` and relaunch NFT.mine.

`NOT FOUND` will be responded if the `wallet_address` is not provided or not found in the dataset, or when the `collection_slug` is not found in dataset.

## Update Dataset

The dataset used to make recomendation need to be updated regularly. This includes:
 - Scrapping new data from [OpenSea][OpenSea link]
 - Perform EDA and feature engineering
 - Generate training data
 - Model re-training with new data
 - Generate dataset for redommendations

To perform this whole process, run all notebooks in `notebook/` according to the serial number in notebook names. After this, put the generated `result_matrix.csv` in `data/` and update the `data_path` defined in `NFT.mine.py`, and relaunch NFT.mine. Note that an OpenSea api key is needed for data scrapping. After obtaining a key [here][here link], replace the `x-api-key` in `0_scraper.ipynb` with your key.

![Architecture image][Architecture image link]

[build status badge]: ../../actions/workflows/python-app.yml/badge.svg
[build status page]: ../../actions/workflows/python-app.yml

[OpenSea link]: https://opensea.io
[here link]: https://docs.opensea.io/reference/request-an-api-key
[Architecture image link]: asset/arch.png
