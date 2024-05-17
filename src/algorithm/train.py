from data_preprocessing import Dataset
import scipy.sparse as sparse
import implicit
import pickle

dataset = Dataset.get_data_from_mongo()

# Pickle the object
with open('dataset.pkl', 'wb') as file:
    pickle.dump(dataset, file)
    
sparse_player_ques = dataset.build_sparse_player_ques()

model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.01, iterations=50)
model.fit(sparse_player_ques)
model.save('model.npz')