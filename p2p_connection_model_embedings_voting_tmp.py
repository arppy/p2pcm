from keras import backend as K
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Embedding, Flatten
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
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
from joblib import dump, load

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
      ret_dropout_str = ret_dropout_str + "," + str(i_dropout) + ":" + str(
        dropout) if dropout > 0 else ret_dropout_str + ""
    else:
      ret_dropout_str = str(i_dropout) + ":" + str(dropout) if dropout > 0 else ""
    i_dropout += 1
  return ret_dropout_str


def layer_str(embeding_output, *layers):
  ret_layer_str = "E" + str(embeding_output)
  for layer in layers:
    ret_layer_str = ret_layer_str + "-D" + str(layer)
  return ret_layer_str


baseFileName = "1010rr1101rr10"
core = "2"
prefix = ""
isTestV4 = False
isCreatePredictionForSimulator = False
predictionSamplesDFileBaseName = "1010rr1101rr10network100000"
isRandomForestInputFile = False
randomForestInputFile = ""
isTensorflow1InputFile = False
tensorflow1InputFile = ""
isTensorflow2InputFile = False
tensorflow2InputFile = ""
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
if len(sys.argv) > 5:
  isCreatePredictionForSimulator = True
  predictionSamplesDFileBaseName = str(sys.argv[5])
if len(sys.argv) > 6:
  isTensorflow1InputFile = True
  tensorflow1InputFile = str(sys.argv[6])
if len(sys.argv) > 7:
  isTensorflow2InputFile = True
  tensorflow2InputFile = str(sys.argv[7])

os.environ["CUDA_VISIBLE_DEVICES"] = core
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
fileResults = open(prefix + "" + baseFileName + ".results", "w")

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

  Z_test_csv = pd.read_csv("" + predictionSamplesDFileBaseName + ".csv", header=None)

  X_df = pd.read_csv("dataset/" + baseFileName + ".csv", header=None, skiprows=1)
  y_df = X_df[0]
  X_df = X_df.drop([0], axis=1)
  # NUMBER_OF_TRAINING_SET_SIZE = 178778 # v1
  # NUMBER_OF_TRAINING_SET_SIZE = 178684 # v2
  NUMBER_OF_TRAINING_SET_SIZE = 178641  # v3
  NUMBER_OF_TEST_SET_SIZES = [8953, 9204, 8473, 8094, 10854]  # v3
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
  y_validation = y_df_train[~msk]
  x_validation = X_df_train[~msk]
  print(str(NUMBER_OF_TRAINING_SET_SIZE), str(x_train.shape), str(x_validation.shape), file=fileResults)
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
  parameter_tuple = {
    "000000010000": (6, 3),
    "000000010100": (8, 3),
    "001000000000": (11, 3),
    "100000000000": (24, 3),
    "0000rr00000010": (97, 10),
    "0000000000r010": (100, 10),
    "0000rr01000010": (103, 10),
    "0000000100r010": (106, 10),
    "0000000101r010": (108, 10),
    "000011010100": (112, 10),
    "0000001101r010": (113, 10),
    "000000010110": (117, 10),
    "001000010110": (128, 10),
    "1010rr01000010": (138, 10),
    "1010000100r010": (141, 10),
    "100000010110": (141, 10),
    "101000010010": (150, 10),
    "1010000100r02": (151, 10),
    "101000010110": (151, 10),
    "111111111100": (165, 10),  # no_org no_country
    "0000rr0000r010": (197, 10),
    "0000rr0101r010": (207, 10),
    "0000rr1101r010": (209, 10),
    "0010rr0101r010": (218, 10),
    "0010rr1101r010": (220, 10),
    "000011010110": (220, 10),
    "000011110110": (222, 10),
    "1000rr0101r010": (231, 10),
    "001011010110": (231, 10),
    "1000rr1101r010": (233, 10),
    "1010rr0100r010": (238, 10),
    "101011010010": (238, 10),
    "1010rr0101r010": (242, 10),
    "100011010110": (244, 10),
    "1010rr1101r010": (247, 10),
    "1010rr0100r02": (254, 10),
    "1010rr0101rr100": (517, 10),
    "1010110101rr100": (564, 10),
    "00000000000r10": (602, 10),
    "00000001000r10": (608, 10),
    "0000001101rr10": (729, 10),
    "0000rr0101rr10": (809, 10),
    "0000rr1101rr10": (811, 10),
    "1010rr0000rr10": (834, 100),
    "1010rr0101rr10": (842, 100),
    "1010rr1101rr10": (846, 100),
    "1010110101rr10": (855, 100),
    "101011010101": (985, 100),
    "101000110111": (994, 100),
    "1010110101rr2": (1011, 100),
    "1010rr0100rr2": (1014, 100),
    "000011010111": (1048, 100),
    "000011110111": (1050, 100),
    "101011000011": (1075, 100),
    "101011010011": (1081, 100),  # no_day no_is_online no_roaming no_stun_server_string no_webrtctest
    "001011111111": (1081, 100),  # no_time no_day no_is_online
    "101011110011": (1081, 100),  # no_day no_is_online no_stun_server_string no_webrtctest
    "101011010111": (1081, 100),  # no_day no_is_online no_stun_server_string no_roaming
    "100011110111": (1086, 100),  # no_day no_android_version no_is_online no_stun_server_string
    "101011110111": (1097, 100),  # no_day no_is_online no_stun_server_string
    "111111110111": (1106, 100),  # no_stun_server_string
    "101111111111": (1107, 100),  # no_day
    "111011111111": (1112, 100),  # no_is_online or
    "111111111011": (1112, 100),  # no_wbrtctest
    "111111111111": (1141, 100)
  }
  vocab_size = parameter_tuple.get(baseFileName)[0]
  input_length = x_train.shape[1]
  output_dim = parameter_tuple.get(baseFileName)[1]

  if isTensorflow1InputFile == True and tensorflow1InputFile != "":
    model1 = load_model(tensorflow1InputFile, custom_objects={ 'f1': f1, 'recall': recall, 'precision': precision, })
    '''    'hidden_activation' : 'relu',
                          'output_activation' : 'sigmoid',
                          'dropout_0' : 0.5,
                          'dropout_1': 0.5,
                          'dropout_2': 0.5,
                          'dropout_3': 0.5,
                          'layer_1': 1000,
                          'layer_2': 1000,
                          'layer_3': 1000,
                          'opt_type' : "Adam",
                          'lr' : 0.001,
                          'beta_1' : 0.9,
                          'beta_2' : 0.999,
                          'epsilon' : 1e-03,
                          'amsgrad' : True'''
  else :
    hidden_activation = 'relu'
    dropout_0 = 0.5
    layer_1 = 1000
    dropout_1 = 0.5
    layer_2 = 1000
    dropout_2 = 0.5
    layer_3 = 1000
    dropout_3 = 0.5
    output_activation = 'sigmoid'
    model1 = Sequential()
    model1.add(Embedding(input_dim=vocab_size, output_dim=output_dim, input_length=input_length))
    model1.add(Flatten())
    # model.add(Dropout(dropout_0))
    model1.add(Dense(layer_1, activation=hidden_activation))
    # model.add(Dropout(dropout_1))
    model1.add(Dense(layer_2, activation=hidden_activation))
    # model.add(Dropout(dropout_2))
    model1.add(Dense(layer_3, activation=hidden_activation))
    # model.add(Dropout(dropout_3))
    model1.add(Dense(1, activation=output_activation))
    opt_type = "Adam"
    lr = 0.001
    beta_1 = 0.9
    beta_2 = 0.999
    epsilon = 1e-03
    amsgrad = True
    opt = Adam(lr=lr, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, amsgrad=amsgrad)
    model1.compile(loss='binary_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy', f1, precision, recall])
    print(str(vocab_size),str(output_dim),str(input_length))
    batch_size = 128
    epochs = 50
    # simple early stopping
    es = EarlyStopping(monitor="val_loss", mode='min', verbose=1, patience=2)  # val_loss , patience=1
    checkpoint_file_path = "relu-" + baseFileName + "-best_model.hdf5"
    if prefix != "":
      checkpoint_file_path = prefix + "-" + checkpoint_file_path
    mc = ModelCheckpoint(checkpoint_file_path, monitor="val_loss", mode='min', save_best_only=True, verbose=1)
    history = model1.fit(x_train, y_train,
                         batch_size=batch_size,
                         callbacks=[es, mc],
                         epochs=epochs,
                         verbose=1,
                         validation_data=(x_validation, y_validation))
    model1.load_weights(checkpoint_file_path)
    model1.save(checkpoint_file_path)
  #print(str(Z_test_csv.shape), str(type(Z_test_csv)), str(x_validation.shape), str(type(x_validation)), file=fileResults)
  if isCreatePredictionForSimulator == True:
    Z_pred_keras = model1.predict(Z_test_csv)
    fileToPrintZ = open(predictionSamplesDFileBaseName + "relu" + "-" + prefix + 'prediction.out', "w",
                        encoding="utf-8")
    for prediction in Z_pred_keras:
      fileToPrintZ.write('' + str(int(round(prediction[0]))) + '\n')
    fileToPrintZ.close()
  y_pred_keras_validation = model1.predict(x_validation).ravel()
  #print(str(Z_pred_keras.shape), str(type(Z_pred_keras)), str(y_pred_keras_validation.shape), str(type(y_pred_keras_validation)), file=fileResults)
  y_pred_keras_test = []
  #fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_test, y_pred_keras)
  #auc_keras = auc(fpr_keras, tpr_keras)
  '''print("Tensorflow1", layer_str(output_dim, layer_1, layer_2, layer_3),
        dropout_str(dropout_0, dropout_1, dropout_2, dropout_3),
        opt_type + "(lr=" + str(lr) + ",beta_1=" + str(beta_1) + ",beta_2=" + str(beta_2) + ",epsilon=" + str(
          epsilon) + ",amsgrad=" + str(amsgrad) + ")",
        hidden_activation, output_activation, file=fileResults)'''
  score = model1.evaluate(x_validation, y_validation, verbose=0)
  out_str = "" + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
  #out_str = "" + str(epochs) + " " + out_str
  #out_str = "" + str(es.stopped_epoch) + " " + out_str
  print('KerasValid1',score[1],score[2],score[3],score[4],file=fileResults)
  i = 1
  for x_test_i, y_test_i in zip(x_test, y_test):
    y_pred_keras_test.append(model1.predict(x_test_i).ravel())
    score = model1.evaluate(x_test_i, y_test_i, verbose=0)
    # print(len(score), str(x_test_1.shape), str(y_test_1.shape), file=fileResults)
    out_str = out_str + " " + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
    print('KerasTest1' + str(i), score[1], score[2], score[3], score[4], file=fileResults)
    i += 1
  print(out_str, file=fileResults)
  if isTensorflow2InputFile == True and tensorflow2InputFile != "":
    model2 = load_model(tensorflow2InputFile, custom_objects={ 'f1' : f1, 'recall' : recall, 'precision' : precision,})
    ''' 'hidden_activation' : 'selu',
                             'output_activation' : 'sigmoid',
                             'dropout_0' : 0.0,
                             'dropout_1': 0.0,
                             'dropout_2': 0.0,
                             'dropout_3': 0.0,
                             'layer_1': 400,
                             'layer_2': 400,
                             'layer_3': 400,
                             'opt_type' : "Adam",
                             'lr' : 0.001,
                             'beta_1' : 0.9,
                             'beta_2' : 0.999,
                             'epsilon' : 1e-03,
                             'amsgrad' : True '''
  else :
    hidden_activation = 'selu'
    dropout_0 = 0.0
    layer_1 = 400
    dropout_1 = 0.0
    layer_2 = 400
    dropout_2 = 0.0
    layer_3 = 400
    dropout_3 = 0.0
    output_activation = 'sigmoid'
    model2 = Sequential()
    model2.add(Embedding(input_dim=vocab_size, output_dim=output_dim, input_length=input_length))
    model2.add(Flatten())
    # model2.add(Dropout(dropout_0))
    model2.add(Dense(layer_1, activation=hidden_activation))
    # model2.add(Dropout(dropout_1))
    model2.add(Dense(layer_2, activation=hidden_activation))
    # model2.add(Dropout(dropout_2))
    model2.add(Dense(layer_3, activation=hidden_activation))
    # model2.add(Dropout(dropout_3))
    model2.add(Dense(1, activation='sigmoid'))
    opt_type = "Adam"
    lr = 0.001
    beta_1 = 0.9
    beta_2 = 0.999
    epsilon = 1e-03
    amsgrad = True
    opt = Adam(lr=lr, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, amsgrad=amsgrad)
    model2.compile(loss='binary_crossentropy',
                   optimizer=opt,
                   metrics=['accuracy', f1, precision, recall])
    batch_size = 128
    epochs = 10
    history = model2.fit(x_train, y_train,
                         batch_size=batch_size,
                         epochs=epochs,
                         verbose=1,
                         validation_data=(x_validation, y_validation))
    checkpoint_file_path = "selu-" + baseFileName + "-best_model.hdf5"
    if prefix != "":
      checkpoint_file_path = prefix + "-" + checkpoint_file_path
    model2.save(checkpoint_file_path)
  if isCreatePredictionForSimulator == True:
    Z_pred_keras2 = model2.predict(Z_test_csv)
    fileToPrintZ = open(predictionSamplesDFileBaseName + "selu" + "-" + prefix + 'prediction.out', "w", encoding="utf-8")
    for prediction in Z_pred_keras2:
      fileToPrintZ.write('' + str(int(round(prediction[0]))) + '\n')
    fileToPrintZ.close()
  y_pred_keras2_validation = model2.predict(x_validation).ravel()
  y_pred_keras2_test = []
  #fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_test, y_pred_keras2)
  #auc_keras = auc(fpr_keras, tpr_keras)
  score = model2.evaluate(x_validation, y_validation, verbose=0)
  out_str = "" + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
  # out_str = "" + str(epochs) + " " + out_str
  #out_str = "" + str(es.stopped_epoch) + " " + out_str
  print('KerasValid2', score[1], score[2], score[3], score[4], file=fileResults)
  i = 1
  for x_test_i, y_test_i in zip(x_test, y_test):
    y_pred_keras2_test.append(model2.predict(x_test_i).ravel())
    score = model2.evaluate(x_test_i, y_test_i, verbose=0)
    # print(len(score), str(x_test_1.shape), str(y_test_1.shape), file=fileResults)
    out_str = out_str + " " + str(score[1]) + " " + str(score[2]) + " " + str(score[3]) + " " + str(score[4])
    print('KerasTest2' + str(i), score[1], score[2], score[3], score[4], file=fileResults)
    i += 1
  print(out_str, file=fileResults)

