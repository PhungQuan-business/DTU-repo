from data_preprocessing import Dataset
import scipy.sparse as sparse
import implicit
import pickle
from bson import ObjectId

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


def recommend(player_ids: ObjectId | list[ObjectId]) -> list[ObjectId] | dict[ObjectId, list[ObjectId]]:
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


print('Cho 1 người chơi')
print(recommend(ObjectId('663884b5f6b183dfa7fb1daf')))

print('Cho một batch người chơi')

batch = [ObjectId('663884b5f6b183dfa7fb1daf'),
         ObjectId('663884b5f6b183dfa7fb0f56'),
         ObjectId('663884b5f6b183dfa7faea0d'),
         ObjectId('663884b5f6b183dfa7fafea1'),
         ObjectId('663884b5f6b183dfa7fb1ee9'),
         ObjectId('663884b5f6b183dfa7fb1237'),
         ObjectId('663884b5f6b183dfa7faf84a'),
         ObjectId('663884b5f6b183dfa7fb2e8b'),
         ObjectId('663884b5f6b183dfa7fb0a78'),
         ObjectId('663884b5f6b183dfa7fb193c'),
         ObjectId('663884b5f6b183dfa7faef26'),
         ObjectId('663884b5f6b183dfa7fae9f3'),
         ObjectId('663884b5f6b183dfa7faf188'),
         ObjectId('663884b5f6b183dfa7fb04b9'),
         ObjectId('663884b5f6b183dfa7fb1ac7'),
         ObjectId('663884b5f6b183dfa7fb1c10'),
         ObjectId('663884b5f6b183dfa7fae4b9'),
         ObjectId('663884b5f6b183dfa7fb1dec'),
         ObjectId('663884b5f6b183dfa7fb126d'),
         ObjectId('663884b5f6b183dfa7faf0ac'),
         ObjectId('663884b5f6b183dfa7fb2093'),
         ObjectId('663884b5f6b183dfa7faf59c'),
         ObjectId('663884b5f6b183dfa7fb1f36'),
         ObjectId('663884b5f6b183dfa7fb0b5f'),
         ObjectId('663884b5f6b183dfa7fb185a'),
         ObjectId('663884b5f6b183dfa7faf868'),
         ObjectId('663884b5f6b183dfa7fb0296'),
         ObjectId('663884b5f6b183dfa7faefca'),
         ObjectId('663884b5f6b183dfa7fb0558'),
         ObjectId('663884b5f6b183dfa7fb0764'),
         ObjectId('663884b5f6b183dfa7fb2e7e'),
         ObjectId('663884b5f6b183dfa7faf9f7'),
         ObjectId('663884b5f6b183dfa7fb037b'),
         ObjectId('663884b5f6b183dfa7fb232b'),
         ObjectId('663884b5f6b183dfa7fb036c'),
         ObjectId('663884b5f6b183dfa7fb2524'),
         ObjectId('663884b5f6b183dfa7fb2db7'),
         ObjectId('663884b5f6b183dfa7fb21d9'),
         ObjectId('663884b5f6b183dfa7fae60f'),
         ObjectId('663884b5f6b183dfa7fb2969'),
         ObjectId('663884b5f6b183dfa7faf4e5'),
         ObjectId('663884b5f6b183dfa7fb0256'),
         ObjectId('663884b5f6b183dfa7fb0b60'),
         ObjectId('663884b5f6b183dfa7fb0954'),
         ObjectId('663884b5f6b183dfa7faf5e8'),
         ObjectId('663884b5f6b183dfa7fb239a'),
         ObjectId('663884b5f6b183dfa7fb0a09'),
         ObjectId('663884b5f6b183dfa7fb0e16'),
         ObjectId('663884b5f6b183dfa7fb0648'),
         ObjectId('663884b5f6b183dfa7fb1710'),
         ObjectId('663884b5f6b183dfa7fb2678'),
         ObjectId('663884b5f6b183dfa7faf2fb'),
         ObjectId('663884b5f6b183dfa7faf703'),
         ObjectId('663884b5f6b183dfa7faf3e6'),
         ObjectId('663884b5f6b183dfa7fb04d3'),
         ObjectId('663884b5f6b183dfa7faf011'),
         ObjectId('663884b5f6b183dfa7fb0905'),
         ObjectId('663884b5f6b183dfa7faecc6'),
         ObjectId('663884b5f6b183dfa7faffe3'),
         ObjectId('663884b5f6b183dfa7fae770'),
         ObjectId('663884b5f6b183dfa7fb122c'),
         ObjectId('663884b5f6b183dfa7fb00be'),
         ObjectId('663884b5f6b183dfa7fafe35'),
         ObjectId('663884b5f6b183dfa7fb0204'),
         ObjectId('663884b5f6b183dfa7fb15ad'),
         ObjectId('663884b5f6b183dfa7fb2b09'),
         ObjectId('663884b5f6b183dfa7fb0285'),
         ObjectId('663884b5f6b183dfa7fae555'),
         ObjectId('663884b5f6b183dfa7fb070e'),
         ObjectId('663884b5f6b183dfa7fb295c'),
         ObjectId('663884b5f6b183dfa7fb2f49'),
         ObjectId('663884b5f6b183dfa7fafc35'),
         ObjectId('663884b5f6b183dfa7fb17a8'),
         ObjectId('663884b5f6b183dfa7fb2d0a'),
         ObjectId('663884b5f6b183dfa7fb0054'),
         ObjectId('663884b5f6b183dfa7fb0ef7'),
         ObjectId('663884b5f6b183dfa7faf4e8'),
         ObjectId('663884b5f6b183dfa7faf75a'),
         ObjectId('663884b5f6b183dfa7fb049c'),
         ObjectId('663884b5f6b183dfa7faf859'),
         ObjectId('663884b5f6b183dfa7fb24fc'),
         ObjectId('663884b5f6b183dfa7fb259e'),
         ObjectId('663884b5f6b183dfa7fb0707'),
         ObjectId('663884b5f6b183dfa7faffaf'),
         ObjectId('663884b5f6b183dfa7fb0e07'),
         ObjectId('663884b5f6b183dfa7fb1122'),
         ObjectId('663884b5f6b183dfa7fb1348'),
         ObjectId('663884b5f6b183dfa7fb27fc'),
         ObjectId('663884b5f6b183dfa7faf6bd'),
         ObjectId('663884b5f6b183dfa7fb24a5'),
         ObjectId('663884b5f6b183dfa7fb0730'),
         ObjectId('663884b5f6b183dfa7fb1396'),
         ObjectId('663884b5f6b183dfa7fb06ba'),
         ObjectId('663884b5f6b183dfa7fb1b20'),
         ObjectId('663884b5f6b183dfa7fafd12'),
         ObjectId('663884b5f6b183dfa7fb070f'),
         ObjectId('663884b5f6b183dfa7fb18e4'),
         ObjectId('663884b5f6b183dfa7fb140e'),
         ObjectId('663884b5f6b183dfa7fb2dc9'),
         ObjectId('663884b5f6b183dfa7fb019b')]

print(recommend(batch))
