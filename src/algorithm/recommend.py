import json
from data_preprocessing import Dataset
import scipy.sparse as sparse
import implicit
import pickle
from bson import ObjectId

# Load dataset
with open('dataset.pkl', 'rb') as file:
    dataset = pickle.load(file)

# Load pretrained model
model = implicit.cpu.als.AlternatingLeastSquares.load('model.npz')


def recommend(data, n=10):
    """
        Recommend top 10 questions for a set of players.

        Args:
            data (list): A list of dictionaries where each dictionary contains 'player_id', 'major', 'rank, 'question_id', 'category', 'difficulty', 'time', and 'outcome'.
    """
    player_ixs, question_ixs = dataset.add_new_data(data)

    sparse_player_ques = dataset.build_sparse_player_ques()

    for _ in range(n):
        model.partial_fit_items(
            question_ixs, sparse_player_ques[:, question_ixs].transpose().tocsr())
        model.partial_fit_users(player_ixs, sparse_player_ques[player_ixs, :])

    ixs, _ = model.recommend(
        player_ixs, sparse_player_ques[player_ixs], N=10, filter_already_liked_items=True)

    result_dict = {}

    for i, player_ix in enumerate(player_ixs):
        result_dict[dataset.get_player_id(player_ix)] = [
            dataset.get_question_id(ix) for ix in ixs[i]]

    return result_dict

# Example usage


with open('sample.json', 'r') as file:
    sample_data = json.load(file)

print(recommend(sample_data))
