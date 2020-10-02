from keras import backend as K
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Embedding, Flatten
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier  # Import Decision Tree Classifier
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.datasets import load_svmlight_file
import tensorflow as tf
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt

import time
import os


def precision(y_true, y_prediction):
    """Precision metric.
    Only computes a batch-wise average of precision.
    Computes the precision, a metric for multi-label classification of
    how many selected items are relevant.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_prediction, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_prediction, 0, 1)))
    ret_precision = true_positives / (predicted_positives + K.epsilon())
    return ret_precision


def recall(y_true, y_prediction):
    """Recall metric.
    Only computes a batch-wise average of recall.
    Computes the recall, a metric for multi-label classification of
    how many relevant items are selected.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_prediction, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    ret_recall = true_positives / (possible_positives + K.epsilon())
    return ret_recall


def f1(y_true, y_prediction):
    ret_precision = precision(y_true, y_prediction)
    ret_recall = recall(y_true, y_prediction)
    return 2 * ((ret_precision * ret_recall) / (ret_precision + ret_recall + K.epsilon()))


def dropout_str(first_dropout, *dropouts):
    ret_dropout_str = "0:" + str(first_dropout) if first_dropout > 0 else ""
    i_dropout = 1
    for dropout in dropouts:
        if ret_dropout_str != "":
            ret_dropout_str = ret_dropout_str + "," + str(i_dropout) + ":" + str(dropout) if dropout > 0 else ret_dropout_str + ""
        else:
            ret_dropout_str = str(i_dropout) + ":" + str(dropout) if dropout > 0 else ""
        i_dropout += 1
    return ret_dropout_str


def layer_str(embeding_output,*layers):
    ret_layer_str = "E" + str(embeding_output)
    for layer in layers :
        ret_layer_str = ret_layer_str + "-D"+str(layer)
    return ret_layer_str


baseFileName = "111111111111"
core = "3"
prefix = ""
isTestV4 = False
testSinceSet = 0
if len(sys.argv) > 1:
    baseFileName = str(sys.argv[1])
if len(sys.argv) > 2:
    core = str(int(sys.argv[2]) - 1)
if len(sys.argv) > 3:
    prefix = str(sys.argv[3])
if len(sys.argv) > 4:
    isTestV4 = True
    testSinceSet = int(sys.argv[4]) - 1

os.environ["CUDA_VISIBLE_DEVICES"] = core
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
fileResults = open(prefix + "" + baseFileName + ".results", "w")

'''
np.random.seed(0)
X, y = load_svmlight_file("dataset/" + baseFileName + ".svmlight")
X_df = pd.DataFrame(X.todense())
y_df = pd.DataFrame(y)

msk = np.random.rand(len(X_df)) < 0.8
y_train = y_df[msk]
x_train = X_df[msk]
y_test = y_df[~msk]
x_test = X_df[~msk]

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()
# Train Decision Tree Classifer
clf = clf.fit(x_train,y_train.values.ravel())
#Predict the response for test dataset
y_pred_dt = clf.predict(x_test)
predictions_dt = y_pred_dt
#predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy_dt= accuracy_score(y_test, predictions_dt)
f1_dt= f1_score(y_test, predictions_dt)
precision_dt = precision_score(y_test, predictions_dt)
fpr_dt, tpr_dt, thresholds_xgb = roc_curve(y_test, y_pred_dt)
auc_dt = auc(fpr_dt, tpr_dt)
print('DecisionTree',accuracy_dt,f1_dt,precision_dt,auc_dt,file=fileResults)

model_xgb = XGBClassifier()
model_xgb.fit(x_train, y_train.values.ravel())
# make predictions for test data
y_pred_xgb = model_xgb.predict(x_test)
predictions_xgb = y_pred_xgb
#predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy_xgb= accuracy_score(y_test, predictions_xgb)
f1_xgb= f1_score(y_test, predictions_xgb)
precision_xgb = precision_score(y_test, predictions_xgb)
fpr_xgb, tpr_xgb, thresholds_xgb = roc_curve(y_test, y_pred_xgb)
auc_xgb = auc(fpr_xgb, tpr_xgb)
print('XGBoost', accuracy_xgb,f1_xgb,precision_xgb,auc_xgb ,file=fileResults)
'''
'''
rf = RandomForestClassifier(max_depth=100, n_estimators=1000)
rf.fit(x_train, y_train.values.ravel())
y_pred_rf_train = rf.predict(x_train)
predictions_rf_train = y_pred_rf_train
accuracy_rf_train= accuracy_score(y_train, predictions_rf_train)
f1_rf_train= f1_score(y_train, predictions_rf_train)
precision_rf_train = precision_score(y_train, predictions_rf_train)
recall_rf_train = recall_score(y_train, predictions_rf_train)
fpr_rf_train, tpr_rf_train, thresholds_rf_train = roc_curve(y_train, y_pred_rf_train)
auc_rf_train = auc(fpr_rf_train, tpr_rf_train)
print('RandomForestTrain',accuracy_rf_train,f1_rf_train,precision_rf_train,recall_rf_train,auc_rf_train ,file=fileResults)
y_pred_rf = rf.predict(x_test)
predictions_rf = y_pred_rf
accuracy_rf= accuracy_score(y_test, predictions_rf)
f1_rf= f1_score(y_test, predictions_rf)
precision_rf = precision_score(y_test, predictions_rf)
recall_rf = recall_score(y_test, predictions_rf)
fpr_rf, tpr_rf, thresholds_rf = roc_curve(y_test, y_pred_rf)
auc_rf = auc(fpr_rf, tpr_rf)
print('RandomForestTest',accuracy_rf,f1_rf,precision_rf,recall_rf,auc_rf ,file=fileResults)
'''
'''
model_lr = LogisticRegression(C=1e20,solver="liblinear")
model_lr.fit(x_train, y_train.values.ravel())
y_pred_lr = model_lr.predict(x_test)
accuracy_lr = accuracy_score(y_test, y_pred_lr)
precision_lr = precision_score(y_test, y_pred_lr)
f1_lr = f1_score(y_test, y_pred_lr)
fpr_lr, tpr_lr, thresholds_lr = roc_curve(y_test, y_pred_lr)
auc_lr = auc(fpr_lr, tpr_lr)
print('LogisticRegression',accuracy_lr,f1_lr,precision_lr,auc_lr,file=fileResults)
'''
tf.reset_default_graph()
tf.set_random_seed(0)
np.random.seed(0)
gpu_options = tf.compat.v1.GPUOptions(allocator_type="BFC", visible_device_list="0")
# config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=1, allow_soft_placement=True, log_device_placement=True, inter_op_parallelism_threads=1, gpu_options=gpu_options, device_count={'GPU': 1})
config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=0, allow_soft_placement=True, log_device_placement=True,
                                  inter_op_parallelism_threads=0, gpu_options=gpu_options, device_count={'GPU': 4})
# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True
# config.log_device_placement = True
sess = tf.compat.v1.Session(config=config)
with sess.as_default():
    tf.set_random_seed(0)
    np.random.seed(0)

    X_df = pd.read_csv("dataset/" + baseFileName + ".csv", header=None, skiprows=1)
    y_df = X_df[0]
    X_df = X_df.drop([0], axis=1)
    # NUMBER_OF_TRAINING_SET_SIZE = 178778 # v1
    # NUMBER_OF_TRAINING_SET_SIZE = 178684 # v2
    # NUMBER_OF_TRAINING_SET_SIZE = 178641  # v3
    NUMBER_OF_TRAINING_SET_SIZE = 187954  # v3
    NUMBER_OF_TEST_SET_SIZES = [9352, 9792, 9224, 9230, 9233, 9283, 9915, 9916, 8587, 8883]  # v4
    if isTestV4 == True:
        if testSinceSet > len(NUMBER_OF_TEST_SET_SIZES) - 1:
            testSinceSet = len(NUMBER_OF_TEST_SET_SIZES) - 1
        sum = 0
        i = 0
        for size in NUMBER_OF_TEST_SET_SIZES:
            if i == testSinceSet:
                break
            sum += size
            i += 1
        NUMBER_OF_TRAINING_SET_SIZE += sum
    X_df_train = X_df.head(NUMBER_OF_TRAINING_SET_SIZE)
    y_df_train = y_df.head(NUMBER_OF_TRAINING_SET_SIZE)
    msk = np.random.rand(len(X_df_train)) < 0.95  # 0.8
    y_train = y_df_train[msk]
    x_train = X_df_train[msk]
    y_validation_test = y_df_train[~msk]
    x_validation_test = X_df_train[~msk]
    next_msk = np.random.rand(len(x_validation_test)) < 0.6
    y_vtest = y_validation_test[next_msk]
    x_vtest = x_validation_test[next_msk]
    y_validation = y_validation_test[~next_msk]
    x_validation = x_validation_test[~next_msk]
    print(str(NUMBER_OF_TRAINING_SET_SIZE), str(x_train.shape), str(x_vtest.shape), str(x_validation.shape),
          file=fileResults)
    NUMBER_OF_TEST_SET_SIZE = X_df.shape[0] - NUMBER_OF_TRAINING_SET_SIZE
    x_df_test = X_df.tail(NUMBER_OF_TEST_SET_SIZE)
    y_df_test = y_df.tail(NUMBER_OF_TEST_SET_SIZE)
    # NUMBER_OF_TEST_SET_SIZES = [37092] # v1
    # NUMBER_OF_TEST_SET_SIZES = [18114, 19072] # v2

    x_test = []
    y_test = []
    sum_of_test_sets_sizes = 0
    i = 0
    for number_of_test_set_size in NUMBER_OF_TEST_SET_SIZES:
        if isTestV4 == True and i < testSinceSet:
            i += 1
            continue
        sum_of_test_sets_sizes += number_of_test_set_size
        x_test.append(x_df_test.head(sum_of_test_sets_sizes).tail(number_of_test_set_size))
        y_test.append(y_df_test.head(sum_of_test_sets_sizes).tail(number_of_test_set_size))
        # print(str(x_test[i].shape),str(y_test[i].shape))

    print(y_train.mean())

    column_maxes = X_df.max()
    vocab_size = max(column_maxes[len(column_maxes) - 1], column_maxes[len(column_maxes) - 2])
    input_length = x_train.shape[1]

    '''
    NUMBER_OF_TRAINING_SET_SIZE = X_df.shape[0]
    X_df_train = X_df.head(NUMBER_OF_TRAINING_SET_SIZE)
    y_df_train = y_df.head(NUMBER_OF_TRAINING_SET_SIZE)
    msk = np.random.rand(len(X_df_train)) < 0.9 # 0.8
    y_train = y_df_train[msk]
    x_train = X_df_train[msk]
    y_test = y_df_train[~msk]
    x_test = X_df_train[~msk]
    X_df_train = x_train
    y_df_train = y_train
    msk2 = np.random.rand(len(x_train)) < 0.9
    y_train = y_df_train[msk2]
    x_train = X_df_train[msk2]
    y_validation = y_df_train[~msk2]
    x_validation = X_df_train[~msk2]
    '''
    '''
    output_dim = 100 
    hidden_activation = 'relu'
    dropout_0 = 0.0
    layer_1 = 1000
    dropout_1 = 0.0
    layer_2 = 1000
    dropout_2 = 0.0
    layer_3 = 1000
    dropout_3 = 0.0
    '''
    output_dim = 40
    hidden_activation = 'tanh'
    dropout_0 = 0.5
    layer_1 = 350
    dropout_1 = 0.5
    layer_2 = 100
    dropout_2 = 0.0
    layer_3 = 100
    dropout_3 = 0.0
    output_activation = 'sigmoid'
    model = Sequential()
    model.add(Embedding(input_dim=vocab_size, output_dim=output_dim, input_length=input_length))
    model.add(Flatten())
    model.add(Dropout(dropout_0))
    model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dropout(dropout_1))
    #model.add(Dense(layer_2, activation=hidden_activation))
    # model.add(Dropout(dropout_2))
    #model.add(Dense(layer_3, activation=hidden_activation))
    # model.add(Dropout(dropout_3))
    '''model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dense(layer_1, activation=hidden_activation))
    model.add(Dense(layer_1, activation=hidden_activation))'''
    model.add(Dense(1, activation=output_activation))
    # opt = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.001, amsgrad=True)
    opt_type = "Adam"
    lr = 0.001
    beta_1 = 0.9
    beta_2 = 0.999
    epsilon = 1e-03
    amsgrad = True
    opt = Adam(lr=lr, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, amsgrad=amsgrad)
    model.compile(loss='binary_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy', f1, precision, recall])
    batch_size = 128
    epochs = 199
    earlyStopping = False
    checkpoint_file_path = baseFileName + "-best_model.hdf5"
    if prefix != "":
        checkpoint_file_path = prefix + "-" + checkpoint_file_path
    if earlyStopping == True :   # simple early stopping
        es = EarlyStopping(monitor="val_loss", mode='min', verbose=1, patience=10) #val_loss , patience=1
        mc = ModelCheckpoint(checkpoint_file_path, monitor="val_loss", mode='min', save_best_only=True, verbose=1)
        history = model.fit(x_train, y_train,
                            batch_size=batch_size,
                            callbacks=[es, mc],
                            epochs=epochs,
                            verbose=1,
                            validation_data=(x_validation, y_validation))
        model.load_weights(checkpoint_file_path)
    else :
        history = model.fit(x_train, y_train,
                            batch_size=batch_size,
                            epochs=epochs,
                            verbose=1,
                            validation_data=(x_validation, y_validation))
    model.save(checkpoint_file_path)
    # y_pred_keras = model.predict(x_test).ravel()
    # fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_validation, y_pred_keras)
    # auc_keras = auc(fpr_keras, tpr_keras)
    print("Tensorflow", layer_str(output_dim, layer_1, layer_2, layer_3),
          dropout_str(dropout_0, dropout_1, dropout_2, dropout_3),
          opt_type+"(lr="+str(lr)+",beta_1="+str(beta_1)+",beta_2="+str(beta_2)+",epsilon="+str(epsilon)+",amsgrad="+str(amsgrad)+")",
          hidden_activation,output_activation,file=fileResults)
    # score = model.evaluate(x_train, y_train, verbose=0)
    # print(len(score), str(x_train.shape), str(y_train.shape),file=fileResults)
    # print('KerasTrain',score[1],score[2],score[3],score[4],file=fileResults)
    score = model.evaluate(x_validation, y_validation, verbose=1)
    # print(len(score), str(x_validation.shape), str(y_validation.shape), file=fileResults)
    out_str = "" + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
    if earlyStopping == True :
        out_str = "" + str(es.stopped_epoch) + " " + out_str
    else :
        out_str = "" + str(epochs) + " " + out_str
    print('KerasValid', score[1], score[2], score[3], score[4], file=fileResults)
    '''
    score = model.evaluate(x_test, y_test, verbose=0)
    # print(len(score), str(x_test.shape), str(y_test.shape), file=fileResults)
    print('KerasTest', score[1], score[2], score[3], score[4], file=fileResults)
    '''
    i = 1
    for x_test_i, y_test_i in zip(x_test, y_test):
        score = model.evaluate(x_test_i, y_test_i, verbose=0)
        # print(len(score), str(x_test_1.shape), str(y_test_1.shape), file=fileResults)
        out_str = out_str + " " + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
        print('KerasTest' + str(i), score[1], score[2], score[3], score[4], file=fileResults)
        i += 1
    print(out_str, file=fileResults)
    fileResults.close()
    # model.save('10000.h5')
    # model.save_weights('10000.weights')
    '''
    plt.figure(1)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.25f})'.format(auc_keras))
    plt.plot(fpr_xgb, tpr_xgb, label='XGB (area = {:.25f})'.format(auc_xgb))
    plt.plot(fpr_dt, tpr_dt, label='DT (area = {:.25f})'.format(auc_dt))
    plt.plot(fpr_rf, tpr_rf, label='RF (area = {:.25f})'.format(auc_rf))
    plt.plot(fpr_lr, tpr_lr, label='LR (area = {:.25f})'.format(auc_lr))
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve')
    plt.legend(loc='best')
    plt.savefig('roc1.png')
    # Zoom in view of the upper left corner.
    plt.figure(2)
    plt.xlim(0, 0.2)
    plt.ylim(0.8, 1)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.25f})'.format(auc_keras))
    plt.plot(fpr_xgb, tpr_xgb, label='XGB (area = {:.25f})'.format(auc_xgb))
    plt.plot(fpr_dt, tpr_dt, label='DT (area = {:.25f})'.format(auc_dt))
    plt.plot(fpr_rf, tpr_rf, label='RF (area = {:.25f})'.format(auc_rf))
    plt.plot(fpr_lr, tpr_lr, label='LR (area = {:.25f})'.format(auc_lr))
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve (zoomed in at top left)')
    plt.legend(loc='best')
    plt.savefig('roc2.png')
    '''
