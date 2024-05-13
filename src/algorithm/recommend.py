from data_preprocessing import Dataset
import scipy.sparse as sparse
import implicit
import pickle
from bson import ObjectId
import threadpoolctl
import json 
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo import UpdateMany

client = MongoClient("mongodb+srv://admin:admin123@cluster0.jmil5cr.mongodb.net/dtu?retryWrites=true&w=majority&appName=Cluster0")
database = client["dtu"]
result_collection = database["results"]

# this line would resolve the runtime error 
threadpoolctl.threadpool_limits(1)


with open('dataset.pkl', 'rb') as file:
    dataset = pickle.load(file)

sparse_player_ques = sparse.csr_matrix(
    (
        dataset.observations,
        (dataset.observation_players,
         dataset.observation_questions),
    )
)

model = implicit.cpu.als.AlternatingLeastSquares.load('model.npz')

app = Flask(__name__)


def recommend(player_ids):
    if isinstance(player_ids, ObjectId):
        player_ixs = dataset.get_player_ix(player_ids)
    elif isinstance(player_ids, list):
        player_ixs = [dataset.get_player_ix(
            player_id) for player_id in player_ids]
    else:
        raise ValueError(
            'player_ids must be an ObjectId or a list of ObjectId')

    ids, _ = model.recommend(
        player_ixs, sparse_player_ques[player_ixs], N=10, filter_already_liked_items=True)

    if ids.ndim == 1:
        return [dataset.get_question_id(ix) for ix in ids]

    result_dict = {}

    for i, player_id in enumerate(player_ids):
        result_dict[player_id] = [dataset.get_question_id(ix) for ix in ids[i]]
    
    return result_dict

# @app.route('/recommend')
def process_input():
    data = request.json
    playersObjectId = data['playersObjectId']
    # cần thống nhất lại xem param có bao gồm "ObjectID" không
    # 1 batch
    object_ids_batch = [ObjectId(id) for id in playersObjectId]

    result_dict = recommend(object_ids_batch)
    bulk_operations = []

    if result_dict:
        for key, value in result_dict.items():
            # Tạo một filter để cập nhật dữ liệu theo _id
            filter_query = {"_id": ObjectId(key)}
            # Dữ liệu mới cần cập nhật
            update_data = {
                "$set": {"recommended_questions": [ObjectId(str(oid)) for oid in value]}
            }
            # Tạo operation
            operation = UpdateMany(filter_query, update_data, upsert=True)
            # Thêm operation vào bulk operations
            bulk_operations.append(operation)
        
        # Thực hiện bulk write operations
        result_collection.bulk_write(bulk_operations)
        
        result_str = {str(key): [str(oid) for oid in value]
                      for key, value in result_dict.items()}
        json_result = json.dumps(result_str)
        print(json_result)
        return jsonify(json_result)
    else:
        return jsonify({'error': 'Player not found'}), 404

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=31814)
    app.run(debug=True, host='0.0.0.0', port=5000)