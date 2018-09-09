
# coding: utf-8

# In[ ]:


# Define path of dataset and directory dump results

dataset_path = "/root/cw/NiteshCode/firstcry_category_dataset.csv"
model_directory = "/root/cw/NiteshCode/model"
result_directory = "/root/cw/NiteshCode/result"


# In[ ]:


# Load the cleaned Dataset

import pandas as pd
df = pd.read_csv(dataset_path, encoding='utf-8')


# In[ ]:


# Define the Sentence Vectorization class

import numpy as np
from gensim.sklearn_api import W2VTransformer
from sklearn.base import BaseEstimator, TransformerMixin

class SentenceVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, window, min_count, size, how='mean', sg=0):
        self.window = window
        self.min_count = min_count
        self.size = size
        self.how = how
        self.sg = sg
    
    def fit(self, x, y=None):
        """
        Fits a word2vec model on x : list of sentences
        """
        self.tokens = [s.split() for s in x]
        self.wordvecs = W2VTransformer(size=self.size, min_count=self.min_count, window=self.window, sg=self.sg).fit(self.tokens)
        return self
    
    def transform(self, x):
        """
        Transforms an array of sentences to the sentence vector form using mean embedding of the wordvectors
        """
        sent_vectors = list()
        sentences = [s.split() for s in x]
        for sent in sentences:
            list_of_word_vectors = list()
            for token in sent:
                try:
                    wordvect = self.wordvecs.transform(token)[0]
                    list_of_word_vectors.append(wordvect)
                except KeyError:
                    list_of_word_vectors.append(np.zeros(self.size))
            if self.how == 'sum':
                sent_vectors.append(np.sum(list_of_word_vectors, axis=0))
            else:
                sent_vectors.append(np.mean(list_of_word_vectors, axis=0))
        return(np.array(sent_vectors))
                    


# In[ ]:


# Helper function to export classification report into a pandas Dataframe

def classification_report_df(report):
    report_data = []
    lines = report.split('\n')
    for line in lines[2:-3]:
        row = {}
        row_data = line.split('   ') 
        row_data = [x for x in row_data if x]
        row['class'] = row_data[-5].strip()
        row['precision'] = float(row_data[-4].strip())
        row['recall'] = float(row_data[-3].strip())
        row['f1_score'] = float(row_data[-2].strip())
        row['support'] = float(row_data[-1].strip())
        report_data.append(row)
    return pd.DataFrame.from_dict(report_data)


# #### Some pre-processing and cleaning is needed for the product titles. Upon manual examination, there are some patterns which need to be removed as they don't add any value to the product description.
# #### The patterns are as follows....
# #### (Color May Vary)
# #### Pack of 3 - Yellow Blue
# #### Pack of 4 - Multi Color
# #### Pack of 2 Pairs - Aqua White
# #### Pre Order - 
# #### (Styles May Vary)
# #### (Color & Print May Vary)
# #### (Color And Design May Vary)

# In[ ]:


# Clean up the product title for the above mentioned patterns

import re

def title_cleanup(s):
    _pack_ = re.compile(r'pack of [0-9]+', re.IGNORECASE)
    _set_ = re.compile(r'set of [0-9]+', re.IGNORECASE)
    # _attributes_ = re.compile(r' - .*$')
    _brackets_ = re.compile(r'\([^()]*\)')
    _preorder_ = re.compile(r'pre order - ', re.IGNORECASE)
    seq = [_preorder_, _pack_, _set_, _brackets_]
    for each in seq:
        s = re.sub(each, ' ',string=s)
    
    # Remove the color attribute which occurs after the last ' - '
    l = re.split(pattern=r' - ', string=s)
    if len(l) == 1:
        return l[0].lower().strip()
    else:
        return ' '.join(l[:-1]).lower().strip()


df['cleaned_title'] = df['title'].apply(lambda x: title_cleanup(x))


# ### Modelling for level1

# In[ ]:


# Remove 'combo packs' onwards. ie, sample size < 600

counts = df['level1'].value_counts()
counts = counts[counts>600]
df_level1 = df[df['level1'].isin(counts.index)][['cleaned_title','level1']]
df_level1.reset_index(inplace=True, drop=True)


# In[3]:


# Prepare combinations of W2V parameters to iterate over...

sg = [1,0]
how = ['mean','sum']
window = [1,2]
params = [(x, y, z) for x in sg for y in how for z in window]


# In[ ]:


# Massive Grid search over SVM parameters and Sentence2Vec parameters...

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from uuid import uuid4
import os
import dill


res = pd.DataFrame()
for sg, how, window in params:
    
    # Assign a unique identifier to identify results, create folder to store models by identifier
    identifier = str(uuid4())
    folder_name = model_directory+'/'+identifier
    os.mkdir(folder_name)
    
    # Generate sentence vectors for entire dataset.
    sentences = df_level1['cleaned_title'].values
    target = df_level1['level1'].values
    
    vectorizer = SentenceVectorizer(window=window, sg=sg, how=how, min_count=10, size=100).fit(sentences)
    sentence_vectors = vectorizer.transform(sentences)
    
    
    # Standardize the vectors, train_test_split

    X_train, X_test, y_train, y_test = train_test_split(sentence_vectors, target, test_size=0.2, stratify=target)
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test) 
    
    
    # Grid search over SVM parameters, scoring method is weighted f-score

    parameters = {
        'kernel':('linear', 'rbf'),
        'C':[1,5,10,15,20,25,30,35,40]    
    }

    clf = GridSearchCV(estimator=SVC(),
                       scoring='f1_weighted',
                       n_jobs=-1,
                       return_train_score=True,
                       param_grid=parameters)

    clf.fit(X_train_scaled, y_train)
    
    
    # Generate results on test set...
    
    y_pred = clf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test,y_pred)
    
    result_df = classification_report_df(classification_report(y_test, y_pred))
    result_df = result_df.assign(SVM_specs = str(clf.best_params_),
                                 W2V_specs = str(vectorizer),
                                 test_accuracy = str(accuracy_score(y_test,y_pred)),
                                 mean_cv_score = str(clf.best_score_),
                                 identifier = identifier)
    
    res = res.append(result_df, ignore_index=True)
    res = res.append(pd.Series(['---']*len(res.columns), index=res.columns), ignore_index=True)
    
    
    # Save the model
    
    dill.dump(vectorizer, open(folder_name+"/"+"vectorizer.pkl", "wb"))
    dill.dump(scaler, open(folder_name+"/"+"scaler.pkl", "wb"))
    dill.dump(clf, open(folder_name+"/"+"classifier.pkl", "wb"))
    
# Export results into csv...
res.to_csv(result_directory+"results.csv", encoding='utf-8', index=False)

