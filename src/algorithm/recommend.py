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


def recommend_with_data(data, n=10):
    """
    Recommends a list of questions to players.

    Parameters:
    - data (list): A list of dictionaries representing player-question interactions.
                - player_id (str): The ID of the player.
                - question_id (str): The ID of the question.
                - major (list|str): The major of the player.
                - category (str): The category of the question.
                - rank (int): The rank of the player in the question.
                - difficulty (int): The difficulty level of the question.
                - outcome (int): The outcome of the interaction.
                - time (float): The time taken for the interaction.
    - n (int): The number of questions to recommend to each player. Default is 10.

    Returns:
    - result_dict (dict): A dictionary where the keys are player IDs and the values
                          are lists of recommended question IDs.
    """
    player_ixs, question_ixs = dataset.add_new_data(data)

    sparse_player_ques = dataset.build_sparse_player_ques()

    model.partial_fit_users(player_ixs, sparse_player_ques[player_ixs, :])
    model.partial_fit_items(
        question_ixs, sparse_player_ques[:, question_ixs].transpose().tocsr())

    ixs, _ = model.recommend(
        player_ixs, sparse_player_ques[player_ixs], N=n, filter_already_liked_items=True)

    result_dict = {}

    for i, player_ix in enumerate(player_ixs):
        result_dict[str(dataset.get_player_id(player_ix))] = [
            str(dataset.get_question_id(ix)) for ix in ixs[i]]

    return result_dict

def recommend(player_ids):
    """
    Recommends a list of questions for the given player IDs.

    Args:
        player_ids (str or list): The ID(s) of the player(s) for whom recommendations are to be made.

    Returns:
        list or dict: If `player_ids` is a string, returns a list of recommended question IDs.
                     If `player_ids` is a list, returns a dictionary where the keys are player IDs
                     and the values are lists of recommended question IDs.

    Raises:
        ValueError: If `player_ids` is neither a string nor a list.

    """    
    if isinstance(player_ids, str):
        player_ixs = dataset.get_player_ix(ObjectId(player_ids))
    elif isinstance(player_ids, list):
        player_ixs = [dataset.get_player_ix(
            ObjectId(player_id)) for player_id in player_ids]
    else:
        raise ValueError(
            'player_ids must be an str or a list of str')
    sparse_player_ques = dataset.build_sparse_player_ques()
    ids, _ = model.recommend(
        player_ixs, sparse_player_ques[player_ixs], N=10, filter_already_liked_items=True)
    if ids.ndim == 1:
        return [str(dataset.get_question_id(ix)) for ix in ids]
    result_dict = {}
    for i, player_id in enumerate(player_ids):
        result_dict[str(player_id)] = [str(dataset.get_question_id(ix))
                                       for ix in ids[i]]
    return result_dict

# Sample data
with open('sample.json', 'r') as file:
    sample_data = json.load(file)

print(recommend(sample_data))
