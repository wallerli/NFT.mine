from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from urllib import request
import os
plt.style.use('ggplot')


HOST = ""
PORT = 8080


suggestion_cols = 5
suggestion_rows = 5
num_suggestions = suggestion_rows * suggestion_cols


def generate_header(header):
    return bytes(f'<html><body><h1>{header}</h1></body></html>', 'utf-8')


to_addr_index = 0
asset_name_index = 1
probability_index = 2
image_url_index = 3
collection_slug_index = 4


cache_path = 'cache/'
data_path = 'data/result_matrix.csv'


result_matrix = pd.read_csv(data_path)[
    ['to_addr', 'asset_name', 'probability', 'image_url', 'collection_slug']]
print(f'Loaded {result_matrix.shape[0]} results')


n_all_wallets = result_matrix['to_addr'].nunique()
all_wallets = result_matrix['to_addr'].unique()
print(f'Found {n_all_wallets} unique wallets')


n_all_collections = result_matrix['collection_slug'].nunique()
all_collections = result_matrix['collection_slug'].unique()
print(f'Found {n_all_collections} unique collections')


def parse_nft_query(url_path):
    wallet = ''
    collection = ''
    parsed_path = urlparse(url_path)
    if parsed_path.path != '/match' or parsed_path.query == '':
        return '', ''
    parsed_query = parse_qs(parsed_path.query)
    if 'wallet_address' not in parsed_query.keys():
        return '', ''
    wallets = parsed_query['wallet_address']
    if len(wallets) != 1:
        return '', ''
    wallet = wallets[0]
    collections = []
    if 'collection_slug' in parsed_query.keys():
        collections = parsed_query['collection_slug']
    if len(collections) > 1:
        return '', ''
    if len(collections) == 1:
        collection = collections[0]
    return wallet, collection


def generate_recommendation(to_addr, collection_slug):
    path_to_image = cache_path + to_addr + '_' + collection_slug + '.png'
    try:
        return open(path_to_image, 'rb').read()
    except:
        pass
    if collection_slug == '':
        user_0_assets = result_matrix[result_matrix['to_addr'] == to_addr].sort_values(
            'probability', ascending=False)[:num_suggestions*2]
    else:
        user_0_assets = result_matrix[result_matrix['to_addr'] == to_addr][result_matrix['collection_slug'] == collection_slug].sort_values(
            'probability', ascending=False)[:num_suggestions*2]
    fig, axis = plt.subplots(suggestion_rows, suggestion_cols,
        figsize=(4 * suggestion_cols, 4 * suggestion_rows), dpi=65)
    fig.suptitle('       NFT.mine - ' + to_addr, fontsize=22, horizontalalignment='left', x=0)
    image_i = 0
    image_found = 0
    while (image_found < num_suggestions):
        current = axis[image_found //
                       suggestion_cols][image_found % suggestion_cols]
        try:
            image = Image.open(request.urlopen(user_0_assets.iloc[image_i, image_url_index]))
            current.imshow(image)
        except:
            if image_i > 2 * num_suggestions:
                image_found = image_found + 1
                current.axis('off')
                current.set_xlabel('off')
                continue
            image_i = image_i + 1
            continue
        current.set_title('\n' 
                          + f'{image_found + 1}. {user_0_assets.iloc[image_i, asset_name_index]}'
                          + '\n' + user_0_assets.iloc[image_i, collection_slug_index]
                          + '\n' + f'confidence: {(user_0_assets.iloc[image_i, probability_index] * 100):.2f}%'
                          , loc='left')
        current.axis('off')
        current.set_xlabel('off')
        image_i = image_i + 1
        image_found = image_found + 1
    fig.tight_layout()
    plt.savefig(path_to_image)
    return generate_recommendation(to_addr, collection_slug)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        target_wallet, target_collection = parse_nft_query(self.path)
        if target_wallet == '' or not target_wallet in all_wallets:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(generate_header('Invalid Wallet Address'))
            return
        if target_collection != '' and not target_collection in all_collections:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(generate_header('Invalid Collection Slug'))
            return
        try:
            img = generate_recommendation(target_wallet, target_collection)
        except:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(generate_header('Internal Error'))
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(img)


def main():
    server = HTTPServer((HOST, PORT), MyHandler)
    os.makedirs(cache_path, exist_ok=True)
    print(f'NFT.mine is up')
    print(f'(localhost:{PORT}/match?wallet_address=&collection_slug=)')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted')
        print('Shutting down')
        for file in os.scandir(cache_path):
            os.remove(file.path)
        server.shutdown()


if __name__ == '__main__':
    main()
