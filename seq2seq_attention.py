#! /usr/bin/python
# -*- coding: utf8 -*-
from __future__ import print_function
import tensorflow as tf
import tensorlayer as tl
from tensorlayer.layers import set_keep
import numpy as np
import random
import math
import time
import os
import re
import sys
from six.moves import xrange

# Data directory and vocabularies size
data_dir = "~/data"                # Data directory
train_dir = os.path.join(data_dir, "/train")               # Model directory save_dir
vocab_size = 50000           #vocabulary size
# Create vocabulary file (if it does not exist yet) from data file.
#_WORD_SPLIT = re.compile(b"([.,!?\"':;)(]，．、：；（） ！)") # regular expression for word spliting. in basic_tokenizer.
_WORD_SPLIT=re.compile(b"([.,!?\"':;)(])")
_DIGIT_RE = re.compile(br"\d")  # regular expression for search digits
normalize_digits = True         # replace all digits to 0
# Special vocabulary symbols
_PAD = b"_PAD"                  # Padding
_GO = b"_GO"                    # start to generate the output sentence
_EOS = b"_EOS"                  # end of sentence of the output sentence
_UNK = b"_UNK"                  # unknown word
PAD_ID = 0                      # index (row number) in vocabulary
GO_ID = 1
EOS_ID = 2
UNK_ID = 3
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]
plot_data = True
# Model
buckets = [(10, 10), (20, 20), (40, 40), (50, 50)]
num_layers = 3
size = 1024
# Training
learning_rate = 0.5
learning_rate_decay_factor = 0.99
max_gradient_norm = 5.0             # Truncated backpropagation
batch_size = 64
num_samples = 512                   # Sampled softmax
max_train_data_size = None             # Limit on the size of training data (0: no limit). DH: for fast testing, set a value
steps_per_checkpoint = 10           # Print, save frequence
# Save model
model_file_name = "model_conversition"
resume = False


def read_data(source_path, target_path, buckets, EOS_ID, max_size=None):
  """Read data from source and target files and put into buckets.
  Corresponding source data and target data in the same line.
  Args:
    source_path: path to the files with token-ids for the source language.
    target_path: path to the file with token-ids for the target language;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).

  Returns:
    data_set: a list of length len(_buckets); data_set[n] contains a list of
      (source, target) pairs read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
      len(target) < _buckets[n][1]; source and target are lists of token-ids.
  """
  data_set = [[] for _ in buckets]
  with tf.gfile.GFile(source_path, mode="r") as source_file:
    with tf.gfile.GFile(target_path, mode="r") as target_file:
      source, target = source_file.readline(), target_file.readline()
      counter = 0
      while source and target and (not max_size or counter < max_size):
        counter += 1
        if counter % 100000 == 0:
          print("  reading data line %d" % counter)
          sys.stdout.flush()
        source_ids = [int(x) for x in source.split()]
        target_ids = [int(x) for x in target.split()]
        target_ids.append(EOS_ID)
        for bucket_id, (source_size, target_size) in enumerate(buckets):
          if len(source_ids) < source_size and len(target_ids) < target_size:
            data_set[bucket_id].append([source_ids, target_ids])
            break
        source, target = source_file.readline(), target_file.readline()
  return data_set

def main_train():

    print("Prepare the raw data")
    train_path = os.path.join(data_dir, "/train/")
    dev_path = os.path.join(data_dir, "/test/")
    path=data_dir
    print("Training data : %s" % train_path)   # wmt/giga-fren.release2
    print("Testing data : %s" % dev_path)     # wmt/newstest2013

    #Create Vocabularies for both Training and Testing data.
    print()
    print("Create vocabularies")
    vocab_path = os.path.join(data_dir, "vocab.list")
    print("Vocabulary list: %s" % vocab_path)    # wmt/vocab40000.fr

    #Tokenize Training and Testing data.
    print()
    print("Tokenize data")
    # normalize_digits=True means set all digits to zero, so as to reduce vocabulary size.

    ask_train = os.path.join(train_path, "id_ask.txt") 
    ans_train = os.path.join(train_path, "id_ans.txt") 
    ask_dev = os.path.join(dev_path, "id_ask.txt") 
    ans_dev = os.path.join(dev_path, "id_ans.txt") 

    #Step 4 : Load both tokenized Training and Testing data into buckets and compute their size.
    print()
    print ("Read development (test) data into buckets")
    dev_set = read_data(ask_dev, ans_dev, buckets, EOS_ID)

    print()
    if(max_train_data_size!=None):
        print ("Read training data into buckets (limit: %d)" % max_train_data_size)
    train_set = read_data(ask_train, ans_train, buckets, EOS_ID, max_train_data_size)

    train_bucket_sizes = [len(train_set[b]) for b in xrange(len(buckets))]
    train_total_size = float(sum(train_bucket_sizes))
    print('the num of training data in each buckets: %s' % train_bucket_sizes)    # [239121, 1344322, 5239557, 10445326]
    print('the num of training data: %d' % train_total_size)        # 17268326.0

    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                           for i in xrange(len(train_bucket_sizes))]
    print('train_buckets_scale:',train_buckets_scale)   # [0.013847375825543252, 0.09169638099257565, 0.3951164693091849, 1.0]
    """Step 6 : Create model
    """
    print()
    print("Create Embedding Seq2seq Model")
    with tf.variable_scope("model", reuse=None):
        model = tl.layers.EmbeddingAttentionSeq2seqWrapper(
                          vocab_size,
                          vocab_size,
                          buckets,
                          size,
                          num_layers,
                          max_gradient_norm,
                          batch_size,
                          learning_rate,
                          learning_rate_decay_factor,
                          use_lstm = True,
                          forward_only=False)    # is_train = True
    # sess.run(tf.initialize_all_variables())
    tl.layers.initialize_global_variables(sess)

    if resume:
        print("Load existing model")
        load_params = tl.files.load_npz(name=model_file_name+'.npz')
        tl.files.assign_params(sess, load_params, model)
    """Step 7 : Training
    """
    print("training")
    step_time, loss = 0.0, 0.0
    current_step = 0
    previous_losses = []
    for _ in range(10):
    #while True:
        # Choose a bucket according to data distribution. We pick a random number
        # in [0, 1] and use the corresponding interval in train_buckets_scale.
        random_number_01 = np.random.random_sample()
        bucket_id = min([i for i in xrange(len(train_buckets_scale))
                       if train_buckets_scale[i] > random_number_01])

        # Get a batch and make a step.
        # randomly pick ``batch_size`` training examples from a random bucket_id
        # the data format is described in readthedocs tutorial
        start_time = time.time()
        encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                train_set, bucket_id, PAD_ID, GO_ID, EOS_ID, UNK_ID)

        _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                   target_weights, bucket_id, False)
        step_time += (time.time() - start_time) / steps_per_checkpoint
        loss += step_loss / steps_per_checkpoint
        current_step += 1

        # Once in a while, we save checkpoint, print statistics, and run evals.

        if current_step % steps_per_checkpoint == 0:
            # Print statistics for the previous epoch.
            perplexity = math.exp(loss) if loss < 300 else float('inf')
            print ("global step %d learning rate %.4f step-time %.2f perplexity "
                "%.2f" % (model.global_step.eval(), model.learning_rate.eval(),
                            step_time, perplexity))
            # Decrease learning rate if no improvement was seen over last 3 times.
            if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
                sess.run(model.learning_rate_decay_op)
            previous_losses.append(loss)

            # Save model
            tl.files.save_npz(model.all_params, name=model_file_name+'.npz')
            #model.print_params()

            step_time, loss = 0.0, 0.0
            # Run evals on development set and print their perplexity.
            for bucket_id in xrange(len(buckets)):
                if len(dev_set[bucket_id]) == 0:
                    #print("  eval: empty bucket %d" % (bucket_id))
                    continue
                encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                        dev_set, bucket_id, PAD_ID, GO_ID, EOS_ID, UNK_ID)
                _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                               target_weights, bucket_id, True)
                eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
                print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
            sys.stdout.flush()

    '''
    vocab, rev_vocab = tl.nlp.initialize_vocabulary(vocab_path)
    sys.stdout.write("> ")
    sys.stdout.flush()
    sentence = sys.stdin.readline()
    while sentence:
      token_ids = tl.nlp.sentence_to_token_ids(tf.compat.as_bytes(sentence), vocab)
      bucket_id = min([b for b in xrange(len(buckets))
                       if buckets[b][0] > len(token_ids)])
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id, PAD_ID, GO_ID, EOS_ID, UNK_ID)
      _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
      outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
      if EOS_ID in outputs:
        outputs = outputs[:outputs.index(EOS_ID)]
      # Print out French sentence corresponding to outputs.
      print(" ".join([tf.compat.as_str(rev_vocab[output]) for output in outputs]))
      print("> ", end="")
      sys.stdout.flush()
      sentence = sys.stdin.readline()
      '''

def main_decode():
    # Create model and load parameters.
    with tf.variable_scope("model", reuse=None):
        #model_eval = tl.layers.EmbeddingSeq2seqWrapper(
        model_eval = tl.layers.EmbeddingSeq2seqWrapper(
                      source_vocab_size = vocab_size,
                      target_vocab_size = vocab_size,
                      buckets = buckets,
                      size = size,
                      num_layers = num_layers,
                      max_gradient_norm = max_gradient_norm,
                      batch_size = 1,  # We decode one sentence at a time.
                      learning_rate = learning_rate,
                      learning_rate_decay_factor = learning_rate_decay_factor,
                      forward_only = True) # is_train = False

    #sess.run(tf.initialize_all_variables())
    sess.run(tf.global_variables_initializer())
#tf.global_variables_initializer
    #Load params
    print("Load parameters from npz")
    load_params = tl.files.load_npz(name=model_file_name+'.npz')
    tl.files.assign_params(sess, load_params, model_eval)
    #model_eval.print_params()

    # Load vocabularies.
    vocab_path = os.path.join(data_dir, "vocab%d.list" % vocab_size)
    vocab, rev_vocab = tl.nlp.initialize_vocabulary(vocab_path)

    # Decode from standard input.
    sys.stdout.write("> ")
    sys.stdout.flush()
    sentence = sys.stdin.readline()
    while sentence:
      # Get token-ids for the input sentence.
      token_ids = tl.nlp.sentence_to_token_ids(tf.compat.as_bytes(sentence), vocab)
      # Which bucket does it belong to?
      bucket_id = min([b for b in xrange(len(buckets))
                       if buckets[b][0] > len(token_ids)])
      # Get a 1-element batch to feed the sentence to the model.
      encoder_inputs, decoder_inputs, target_weights = model_eval.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id, PAD_ID, GO_ID, EOS_ID, UNK_ID)
      # Get output logits for the sentence.
      _, _, output_logits = model_eval.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
      # This is a greedy decoder - outputs are just argmaxes of output_logits.
      outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
      # If there is an EOS symbol in outputs, cut them at that point.
      if EOS_ID in outputs:
        outputs = outputs[:outputs.index(EOS_ID)]
      # Print out French sentence corresponding to outputs.
      print(" ".join([tf.compat.as_str(rev_vocab[output]) for output in outputs]))
      print("> ", end="")
      sys.stdout.flush()
      sentence = sys.stdin.readline()

if __name__ == '__main__':
    
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.180)  
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options))
    try:
        """ Train model """
        main_train()
        """ Play with model """
        #main_decode()
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt')
        tl.ops.exit_tf(sess)
