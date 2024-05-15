import requests
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import random
import json

# Function to make request with player_ids batch
def make_request_batch(player_ids_batch):
    url = 'http://192.168.49.2:31453/recommend'
    # url = 'http://127.0.0.1:5000/recommend'
    # url = 'http://localhost:5000/recommend'
    # url = 'https://7463-222-252-51-118.ngrok-free.app/recommend'
    data = {'playersObjectId': player_ids_batch}
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, data=json.dumps(data), headers=headers)
    
    if response.status_code == 200:
        # print(f"Batch: {player_ids_batch}: {response.text}")
        # print('ok')
        pass
    else:
        print(f"Error for Batch: {player_ids_batch}: {response.status_code}")

# Read player IDs from file and split into batches
def read_player_ids(filename, batch_size, truncate=None):
    with open(filename, 'r') as file:
        player_ids = [line.strip() for line in file]
        
        # If truncate is None, default to 1000
        if truncate == 'all':
            player_ids = player_ids
        # If truncate is 'None', take all values in the input file
        elif truncate == None:
            truncate = 100
            player_ids = player_ids[:truncate]
        else:
            player_ids = player_ids[:truncate]
    
    # Shuffle the player IDs to randomize
    # Cái này đang không shuffle
    random.shuffle(player_ids)  
    
    # Split into batches
    player_ids_batches = [player_ids[i:i+batch_size] for i in range(0, len(player_ids), batch_size)]
    return player_ids_batches

 
# Main function
def main():
    filename =  r'./objectid_v2-2.txt'  # File containing player IDs, one per line
    batch_size = 2 # Batch size for each request
    truncate = 20
    max_workers = 3
    
    # tạo batch người chơi
    player_ids_batches = read_player_ids(filename=filename, 
                                        batch_size=batch_size, 
                                        truncate=truncate)
    time_for_each_batch = []
    for i, batch in enumerate(player_ids_batches):
        start_time = time.time()   
        make_request_batch(player_ids_batch=batch)
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     try:
        #         executor.map(make_request_batch, player_ids_batches[0])
        #     except KeyboardInterrupt:
        #         print("Ctrl+C detected. Shutting down...")
        #         executor.shutdown(wait=False)
        #         sys.exit(1)
        end_time = time.time()
        time_took = end_time - start_time
        time_for_each_batch.append(time_took)
        # print(f'Time it took to process all requests with parallel processing: {time_took} seconds')
        print(f'Time it took to process batch {i} without parallel processing is: {time_took} seconds')
    print(f'total processing {len(time_for_each_batch)} batch(es) is:', sum(time_for_each_batch))
if __name__ == "__main__":
    main()
