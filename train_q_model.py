import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

if __name__ == '__main__':
    data = np.loadtxt('scores.csv', delimiter = ',')
    positions = data[:,0:12]
    scores = data[:,12]

    model = Sequential()
    model.add(Dense(24, input_dim=12, activation='relu'))
    model.add(Dense(12, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_squared_error'])

    # pos_train, pos_test, scores_train, scores_test = train_test_split(positions, scores, test_size=0.2)#, random_state=42)

    # model.fit(pos_train, scores_train, epochs=50, verbose=0)

    # predictions = model.predict(pos_train)
    # print("Train Accuracy: " + str(np.sqrt(mean_squared_error(scores_train, predictions))))

    # predictions = model.predict(pos_test)
    # print("Test Accuracy: " + str(np.sqrt(mean_squared_error(scores_test, predictions))))

    model.fit(positions, scores, epochs=50, verbose=0)
    predictions = model.predict(positions)
    print("Train Accuracy: " + str(np.sqrt(mean_squared_error(scores, predictions))))

    model.save('q_model')
    model = load_model('q_model')
    predictions = model.predict(positions)
    print("Train Accuracy: " + str(np.sqrt(mean_squared_error(scores, predictions))))