from py3hlda.sampler import HierarchicalLDA
# 自作のデータ読み込み&前処理用ライブラリ
from lib.tfidf import TfidfModel
from lib.utils import stems
from lib.utils import stopwords
from lib import utils
import gensim
from pprint import pprint
import datetime
import sys
import re
import pyLDAvis
import pyLDAvis.gensim


def load_data_for_segmentation(doc_num, *, ans=False):
    print('Interview:',  doc_num)
    path = './data/segmentation/sentence/interview-text_' + doc_num + '.txt'
    # path = './data/segmentation/utterance/interview-text_' + doc_num + '.txt'
    if ans:
        path = './data/eval/interview-text_sentence_' + doc_num + '.txt'

    return utils.load_data_for_eval(path)


if __name__ == '__main__':
    args = sys.argv
    if 2 <= len(args):
        if not(args[1] == 'sentence' or args[1] == 'segmentation' or args[1] == 'utterance' or args[1] == 'segmentation/ans'):
            print('Argument is invalid')
            exit()
    else:
        print('Arguments are too sort')
        exit()

    doc_type = args[1]

    doc_num = 'all'
    path = './data/interview/interview-text_01-26_' + doc_num + '.txt'
    ans = True

    if doc_type == 'segmentation' or doc_type == 'segmentation/ans':
        ans = False
        if doc_type == 'segmentation/ans':
            ans = True
        if doc_num == 'all':
            doc_num = '26'
        data_arr = []
        for num in range(int(doc_num)):
            num += 1
            if num < 10:
                num = '0' + str(num)
            else:
                num = str(num)
            data_arr.append(load_data_for_segmentation(num, ans=ans))

        # セグメント単位でまとめる
        docs = []
        for data in data_arr:
            tmp_docs = []
            for item in data.items():
                if '_____' in item[1][0]:
                    docs.append('\n'.join(tmp_docs))
                    tmp_docs = []
                else:
                    tmp_docs.extend([item[1][1]])
            docs.append('\n'.join(tmp_docs))

    if doc_num == 'all':
        doc_num = '26'
    doc_num = '01_' + doc_num

    # Params
    no_below = 1
    no_above = 0.5
    keep_n = 100000
    sw = stopwords()
    docs_for_training = [stems(doc, polish=True, sw=sw) for doc in docs]

    print('===コーパス生成===')
    # tfidf
    tfidf = TfidfModel(no_below=no_below, no_above=no_above, keep_n=keep_n)
    tfidf.train(docs_for_training)
    dictionary = tfidf.dictionary
    corpus = tfidf.corpus
    dict_item = dictionary.token2id.items()
    vocab = [''] * len(dict_item)
    for w, i in dict_item:
        vocab[i] = w
    new_corpus = []
    for sent in corpus:
        tmp = []
        for w in sent:
            if w[1] == 1:
                tmp.append(w[0])
            else:
                for i in range(w[1]):
                    tmp.append(w[0])
        new_corpus.append(tmp)
    print(docs[:3])
    print(docs_for_training[:3])
    print(vocab[:15])
    print(corpus[:5])
    print(new_corpus[:5])

    print(docs[-3:])

    n_samples = 300       # no of iterations for the sampler
    alpha = 1.0          # smoothing over level distributions
    gamma = 1.0           # CRP smoothing parameter; number of imaginary customers at next, as yet unused table
    eta = 0.005             # smoothing over topic-word distributions
    num_levels = 3        # the number of levels in the tree
    display_topics = 100   # the number of iterations between printing a brief summary of the topics so far
    n_words =  10          # the number of most probable words to print for each topic after model estimation
    with_weights = True  # whether to print the words with the weights

    # LDAモデルの構築
    hlda = HierarchicalLDA(new_corpus, vocab, alpha=alpha, gamma=gamma, eta=eta, num_levels=num_levels)
    res = hlda.estimate(n_samples, display_topics=display_topics, n_words=n_words, with_weights=with_weights)