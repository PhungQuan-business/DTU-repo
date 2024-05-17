from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sparse
from bson import ObjectId


def initialCLient(username='admin', password='admin123'):
    # cái này đẩy vào configure
    uri = f'mongodb+srv://{username}:{
        password}@cluster0.jmil5cr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client


def get_collection(collection_list=['players', 'questions', 'answered_questions']):
    client = initialCLient()
    db = [client['dtu'][collection] for collection in collection_list]
    return db


DEFAULT_PIPELINE = [{"$unwind": "$questions"},
                    {"$project": {"_id": 0,
                                  "player_id": "$player",
                                  "question_id": "$questions._id",
                                  "time": "$questions.timeForAnswer",
                                  "outcome": "$questions.outcome"}}]

CATEGORIES = ['Biology',
              'Chemistry',
              'Geography',
              'History',
              'Literature',
              'Math',
              'Physics',
              'Science']

MIN_RANK, MAX_RANK = 1, 10
MIN_DIFF, MAX_DIFF = 1, 5


def custom_tokenize(x):
    return [x] if isinstance(x, str) else x


def tfidf_transform(col: pd.Series, prefix='', vectorizer=None):
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            tokenizer=custom_tokenize, lowercase=False, vocabulary=CATEGORIES)
        return pd.DataFrame(vectorizer.fit_transform(col).toarray(), columns=[prefix + c for c in CATEGORIES]), vectorizer
    else:
        return pd.DataFrame(vectorizer.transform(col).toarray(), columns=[prefix + c for c in CATEGORIES])


def calculate_performance(time_spent, difficulty, outcome):
    max_time = 60 + 30 * difficulty
    return (1 - time_spent/max_time) * outcome


def calculate_sim_rank_difficulty(rank, difficulty):
    rank_norm = (rank - MIN_RANK) / (MAX_RANK - MIN_RANK)
    diff_norm = (difficulty - MIN_DIFF) / (MAX_DIFF - MIN_DIFF)
    return 1 - np.abs(rank_norm - diff_norm)


def calculate_sim_major_category(A, B):
    return np.sum(A*B, axis=1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(B, axis=1))


def map_id_ix(ids, id_to_ix=None, ix_to_id=None):
    if id_to_ix is not None and ix_to_id is not None:
        for ix, id in enumerate(ids, start=len(id_to_ix)):
            id_to_ix[id] = ix
            ix_to_id[ix] = id
    else:
        id_to_ix = {}
        ix_to_id = {}
        for ix, id in enumerate(ids):
            id_to_ix[id] = ix
            ix_to_id[ix] = id
        return id_to_ix, ix_to_id


class Dataset():
    def __init__(self,
                 question_id_to_ix: dict[ObjectId, int],
                 ix_to_question_id: dict[int, ObjectId],
                 player_id_to_ix: dict[ObjectId, int],
                 ix_to_player_id: dict[int, ObjectId],
                 observation_players,
                 observation_questions,
                 observations,
                 vectorizer=None):
        self.question_id_to_ix = question_id_to_ix
        self.ix_to_question_id = ix_to_question_id
        self.player_id_to_ix = player_id_to_ix
        self.ix_to_player_id = ix_to_player_id
        self.observation_players = observation_players
        self.observation_questions = observation_questions
        self.observations = observations
        self.__vectorizer = vectorizer

    def n_users(self):
        return len(self.player_id_to_ix)

    def n_items(self):
        return len(self.question_id_to_ix)

    def get_player_id(self, ix):
        return self.ix_to_player_id[ix]

    def get_question_id(self, ix):
        return self.ix_to_question_id[ix]

    def get_player_ix(self, id):
        return self.player_id_to_ix[id]

    def get_question_ix(self, id):
        return self.question_id_to_ix[id]

    def build_sparse_player_ques(self):
        return sparse.csr_matrix(
            (
                self.observations,
                (self.observation_players,
                 self.observation_questions),
            )
        )

    def add_new_data(self, data):
        """
        Add new data to the dataset.

        Args:
            data (list): A list of dictionaries where each dictionary contains 'player_id', 'major', 'rank, 'question_id', 'category', 'difficulty', 'time', and 'outcome'.
        """
        interactionData = pd.DataFrame.from_records(data)
        interactionData['player_id'].map(lambda x: ObjectId(x))
        interactionData['question_id'].map(lambda x: ObjectId(x))

        player_ids = interactionData['player_id'].unique().tolist()
        map_id_ix(player_ids, self.player_id_to_ix, self.ix_to_player_id)

        question_ids = interactionData['question_id'].unique().tolist()
        map_id_ix(question_ids, self.question_id_to_ix, self.ix_to_question_id)

        major_tfidf = tfidf_transform(
            interactionData['major'], 'player_', self.__vectorizer)
        category_tfidf = tfidf_transform(
            interactionData['category'], 'question_', self.__vectorizer)

        rating = 0.2 * calculate_performance(interactionData['time'].to_numpy(),
                                             interactionData['difficulty'].to_numpy(
        ),
            interactionData['outcome'].to_numpy()) \
            + 0.3 * calculate_sim_rank_difficulty(interactionData['rank'].to_numpy(),
                                                  interactionData['difficulty'].to_numpy()) \
            + 0.5 * calculate_sim_major_category(major_tfidf.to_numpy(),
                                                 category_tfidf.to_numpy())

        self.observation_players.extend(interactionData['player_id'].map(
            self.player_id_to_ix).to_list())
        self.observation_questions.extend(interactionData['question_id'].map(
            self.question_id_to_ix).to_list())
        self.observations.extend(rating.tolist())

        return [self.player_id_to_ix[player_id] for player_id in interactionData['player_id'].unique()], [self.question_id_to_ix[question_id] for question_id in interactionData['question_id'].unique()]

    @classmethod
    def get_data_from_mongo(cls, player_ids=None):
        playersCollection, questionsCollection, resultCollection = get_collection()

        pipeline = DEFAULT_PIPELINE if player_ids is None else [
            {"$match": {"player": {"$in": player_ids}}}] + DEFAULT_PIPELINE

        interactionData = pd.DataFrame(
            list(resultCollection.aggregate(pipeline)))

        player_ids = interactionData['player_id'].unique().tolist()
        player_id_to_ix, ix_to_player_id = map_id_ix(player_ids)

        question_ids = interactionData['question_id'].unique().tolist()
        question_id_to_ix, ix_to_question_id = map_id_ix(question_ids)

        playerData = pd.DataFrame(list(playersCollection.find(
            {"_id": {"$in": player_ids}}, {"_id": 1, "major": 1, "rank": 1})))

        questionData = pd.DataFrame(list(questionsCollection.find(
            {"_id": {"$in": question_ids}}, {"_id": 1, "category": 1, "difficulty": 1})))

        major_tfidf, vectorizer = tfidf_transform(
            playerData['major'], 'player_')
        major_cols = major_tfidf.columns
        category_tfidf = tfidf_transform(
            questionData['category'], 'question_', vectorizer=vectorizer)
        category_cols = category_tfidf.columns

        playerData = pd.concat([playerData, major_tfidf], axis=1)
        playerData.drop('major', axis=1, inplace=True)

        questionData = pd.concat([questionData, category_tfidf], axis=1)
        questionData.drop('category', axis=1, inplace=True)

        # Merge playerData with interactionData on _id and player_id
        merged_data = pd.merge(playerData, interactionData,
                               left_on='_id', right_on='player_id')
        # Merge with questionData on question_id
        merged_data = pd.merge(merged_data, questionData,
                               left_on='question_id', right_on='_id')
        # Drop redundant columns
        merged_data.drop(['_id_x', '_id_y'], axis=1, inplace=True)

        del interactionData, playerData, questionData, major_tfidf, category_tfidf

        rating = 0.2 * calculate_performance(merged_data['time'].to_numpy(),
                                             merged_data['difficulty'].to_numpy(
        ),
            merged_data['outcome'].to_numpy()) \
            + 0.3 * calculate_sim_rank_difficulty(merged_data['rank'].to_numpy(),
                                                  merged_data['difficulty'].to_numpy()) \
            + 0.5 * calculate_sim_major_category(merged_data[major_cols].to_numpy(),
                                                 merged_data[category_cols].to_numpy())

        return cls(question_id_to_ix=question_id_to_ix,
                   ix_to_question_id=ix_to_question_id,
                   player_id_to_ix=player_id_to_ix,
                   ix_to_player_id=ix_to_player_id,
                   observation_players=merged_data['player_id'].map(
                       player_id_to_ix).to_list(),
                   observation_questions=merged_data['question_id'].map(
                       question_id_to_ix).to_list(),
                   observations=rating.tolist(),
                   vectorizer=vectorizer)
