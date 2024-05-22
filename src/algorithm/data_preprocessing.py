from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sparse
from bson import ObjectId


def initialCLient(username='admin', password='admin123'):
    """
    Initializes and returns a MongoDB client object.

    Parameters:
    - username (str): The username for the MongoDB connection. Default is 'admin'.
    - password (str): The password for the MongoDB connection. Default is 'admin123'.

    Returns:
    - client (pymongo.MongoClient): The MongoDB client object.

    Raises:
    - Exception: If there is an error connecting to the MongoDB deployment.
    """
    uri = f'mongodb+srv://{username}:{password}@cluster0.jmil5cr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client


def get_collection(collection_list=['players', 'questions', 'answered_questions']):
    """
    Retrieves a list of MongoDB collections based on the provided collection names.

    Parameters:
    collection_list (list): A list of collection names to retrieve. Default is ['players', 'questions', 'answered_questions'].

    Returns:
    list: A list of MongoDB collections.
    """
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
    """
    Tokenizes the input string or list of strings.

    Args:
        x (str or list): The input string or list of strings to be tokenized.

    Returns:
        list: A list of tokens. If the input is a string, the function returns a list containing the input string as a single element.
              If the input is already a list, the function returns the input list as is.

    """
    return [x] if isinstance(x, str) else x


def tfidf_transform(col: pd.Series, prefix='', vectorizer=None):
    """
    Transforms a given column of text data using the TF-IDF (Term Frequency-Inverse Document Frequency) method.

    Args:
        col (pd.Series): The column of text data to be transformed.
        prefix (str, optional): A prefix to be added to the column names of the transformed data. Defaults to ''.
        vectorizer (TfidfVectorizer, optional): An instance of TfidfVectorizer to be used for transformation. 
            If None, a new instance will be created. Defaults to None.

    Returns:
        pd.DataFrame: The transformed data as a DataFrame, with column names prefixed by the specified prefix.
        vectorizer (TfidfVectorizer): The fitted TfidfVectorizer instance used for transformation.

    """
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            tokenizer=custom_tokenize, lowercase=False, vocabulary=CATEGORIES)
        return pd.DataFrame(vectorizer.fit_transform(col).toarray(), columns=[prefix + c for c in CATEGORIES]), vectorizer
    else:
        return pd.DataFrame(vectorizer.transform(col).toarray(), columns=[prefix + c for c in CATEGORIES])


def calculate_performance(time_spent, difficulty, outcome):
    """
    Calculate the performance based on the time spent, difficulty, and outcome.

    Parameters:
    time_spent (array-like): A array of time spent for each question.
    difficulty (array-like): A array of difficulty levels for each question.
    outcome (array-like): A array of outcomes for each question.

    Returns:
    array: The calculated performance.

    Raises:
    ValueError: If the length of the input arrays is not the same.

    """
    max_time = 60 + 30 * difficulty
    return (1 - time_spent/max_time) * outcome


def calculate_sim_rank_difficulty(rank, difficulty):
    """
    Calculate the similarity between rank and difficulty.

    Parameters:
    rank (array-like): An array containing the ranks.
    difficulty (array-like): An array containing the difficulties.

    Returns:
    similarity (array-like): An array containing the similarity values between rank and difficulty.
    """
    rank_norm = (rank - MIN_RANK) / (MAX_RANK - MIN_RANK)
    diff_norm = (difficulty - MIN_DIFF) / (MAX_DIFF - MIN_DIFF)
    return 1 - np.abs(rank_norm - diff_norm)


def calculate_sim_major_category(A, B):
    """
    Calculate the cosine similarity for each row of two input matrices.

    Parameters:
    A (numpy.ndarray): The first input matrix.
    B (numpy.ndarray): The second input matrix.

    Returns:
    numpy.ndarray: An array containing the cosine similarity values for each row.

    """
    return np.sum(A*B, axis=1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(B, axis=1))


def map_id_ix(ids, id_to_ix=None, ix_to_id=None):
    """
    Maps a list of IDs to their corresponding indices and vice versa.

    Args:
        ids (list): A list of IDs.
        id_to_ix (dict, optional): A dictionary mapping IDs to indices. Defaults to None.
        ix_to_id (dict, optional): A dictionary mapping indices to IDs. Defaults to None.

    Returns:
        tuple: A tuple containing the dictionaries `id_to_ix` and `ix_to_id`.

    If both `id_to_ix` and `ix_to_id` are provided, the function will update the dictionaries
    with any new IDs found in the `ids` list. If either `id_to_ix` or `ix_to_id` is not provided,
    the function will create new dictionaries and return them.

    Note:
        The function assumes that the IDs in the `ids` list are unique.

    Example:
        ids = ['a', 'b', 'c']
        id_to_ix, ix_to_id = map_id_ix(ids)
        print(id_to_ix)  # Output: {'a': 0, 'b': 1, 'c': 2}
        print(ix_to_id)  # Output: {0: 'a', 1: 'b', 2: 'c'}
    """
    
    if id_to_ix is not None and ix_to_id is not None:
        ix = len(id_to_ix)
        for id in ids:
            if id in id_to_ix:
                continue
            id_to_ix[id] = ix
            ix_to_id[ix] = id
            ix += 1
    else:
        id_to_ix = {}
        ix_to_id = {}
        for ix, id in enumerate(ids):
            id_to_ix[id] = ix
            ix_to_id[ix] = id
        return id_to_ix, ix_to_id


class Dataset():
    """
    Represents a dataset for storing and manipulating data related to players and questions.

    Args:
        question_id_to_ix (dict): A dictionary mapping question IDs to their corresponding indices.
        ix_to_question_id (dict): A dictionary mapping indices to their corresponding question IDs.
        player_id_to_ix (dict): A dictionary mapping player IDs to their corresponding indices.
        ix_to_player_id (dict): A dictionary mapping indices to their corresponding player IDs.
        observation_players (list): A list of player indices representing the players in the dataset.
        observation_questions (list): A list of question indices representing the questions in the dataset.
        observations (list): A list of ratings representing the observations in the dataset.
        vectorizer (object, optional): A vectorizer object used for transforming text data. Defaults to None.
    """    
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
        """
        Returns the number of users in the dataset.

        Returns:
            int: The number of users.
        """
        return len(self.player_id_to_ix)

    def n_items(self):
        """
        Returns the number of questions in the dataset.

        Returns:
            int: The number of questions.
        """
        return len(self.question_id_to_ix)

    def get_player_id(self, ix):
        """
        Returns the player ID corresponding to the given index.

        Parameters:
        - ix (int): The index of the player.

        Returns:
        - ObjectId: The player ID.
        """
        return self.ix_to_player_id[ix]

    def get_question_id(self, ix):
        """
        Returns the question ID corresponding to the given index.

        Parameters:
        - ix (int): The index of the question.

        Returns:
        - ObjectId: The question ID.
        """
        return self.ix_to_question_id[ix]

    def get_player_ix(self, id):
        """
        Returns the index of a player given their ID.

        Parameters:
        id (int): The ID of the player.

        Returns:
        int: The index of the player.

        Raises:
        KeyError: If the player ID is not found in the dictionary.
        """
        return self.player_id_to_ix[id]

    def get_question_ix(self, id):
        """
        Returns the index of a question given their ID.

        Parameters:
        id (int): The ID of the question.

        Returns:
        int: The index of the question.

        Raises:
        KeyError: If the question ID is not found in the dictionary.
        """
        return self.question_id_to_ix[id]

    def build_sparse_player_ques(self):
        """
        Builds a sparse CSR matrix representing the observations of players answering questions.

        Returns:
            scipy.sparse.csr_matrix: A sparse CSR matrix where each row represents a player and each column represents a question.
                                     The values in the matrix represent the observations made by players for each question.
        """
        return sparse.csr_matrix(
            (
                self.observations,
                (self.observation_players,
                 self.observation_questions),
            )
        )

    def add_new_data(self, data):
        """
        Add new data to the existing dataset.

        Args:
            data (list[dict]): A list of dictionaries representing player-question interactions.
                - player_id (str): The ID of the player.
                - question_id (str): The ID of the question.
                - major (list|str): The major of the player.
                - category (str): The category of the question.
                - rank (int): The rank of the player in the question.
                - difficulty (int): The difficulty level of the question.
                - outcome (int): The outcome of the interaction.
                - time (float): The time taken for the interaction.

        Returns:
            tuple: A tuple containing two lists:
                - A list of player IDs converted to indices.
                - A list of question IDs converted to indices.
        """
        interactionData = pd.DataFrame.from_records(data)
        interactionData['player_id'] = interactionData['player_id'].map(lambda x: ObjectId(x))
        interactionData['question_id'] = interactionData['question_id'].map(lambda x: ObjectId(x))

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
        """
        Retrieves data from MongoDB and performs data preprocessing.
        
        Rating is calculated based on the following formula:
        rating = 0.2 * performance + 0.3 * sim_rank_difficulty + 0.5 * sim_major_category
        where performance = 1 - time_spent / max_time * outcome

        Args:
            player_ids (list, optional): A list of player IDs to filter the data. Defaults to None.

        Returns:
            An instance of the Dataset class with the preprocessed data.
        """
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
