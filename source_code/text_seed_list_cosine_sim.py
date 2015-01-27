import os
from sets import Set
import nltk
import string
from sklearn.metrics.pairwise import cosine_similarity
import ntpath
import sys
import platform
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()
def load_stopwords():
    f = open('../src/stopwords.txt')
    stopwords =[]
    for w in f:
        stopwords.append(w.replace('\r','').replace('\n',''))
    return stopwords

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems


def build_vector_from_file_list(file_list):
    text_dictionary = {}

    for text_file in file_list:
        shakes = open(text_file, 'r')
        text = shakes.read()
        if len(text)==0:
            continue
        lowers = text.decode('utf-8', errors='ignore').lower()
    
        no_punctuation = string.translate(lowers, string.punctuation)
        text_dictionary[text_file] = no_punctuation
    return text_dictionary

def build_vector_from_file(text_file):
    text_dictionary = {}

    shakes = open(text_file, 'r')
    text = shakes.read()
    if len(text)==0:
        return
    lowers = text.decode('utf-8', errors='ignore').lower()

    no_punctuation = string.translate(lowers, string.punctuation)
    text_dictionary[text_file] = no_punctuation
    return text_dictionary

def print_cosine_similarity(old_uri_id,memento_t0,cosine_similarity_results_matrix, cosine_similarity_file,computed_file_list):
    cosine_similarity_file.write("id\ttn_dt\tt0_dt\tcos_sim\n")
    for train_row in cosine_similarity_results_matrix:
     #   print str(train_row)
        for idx, test_cell in enumerate(train_row):
            cosine_similarity_file.write( old_uri_id+"\t"+computed_file_list[idx]+"\t"+memento_t0+"\t"+str(test_cell) +"\n")
        cosine_similarity_file.write("\n")

def old_print_cosine_similarity(old_uri_id,cosine_similarity_results_matrix, cosine_similarity_file,computed_file_list):
    cosine_similarity_file.write(str(old_uri_id)+"\t")
    for train_row in cosine_similarity_results_matrix:
        print str(train_row)
        for test_cell in train_row:
            cosine_similarity_file.write( str(test_cell) +"\t")
        cosine_similarity_file.write("\n")

   
if __name__ == "__main__":
    
   if len(sys.argv) > 1:
      collection_id = sys.argv[1]
   else:
      collection_id = "1068"
      
   if platform.system().startswith("Windows")  :
      input_base_dir = "C:/Users/yasmin/Desktop/data_files/collection_"+collection_id
      output_base_dir= "C:/dropBox/Dropbox/Coding/Data_files/collection_"+collection_id
   else:
      input_base_dir = "/Users/yasmin/Desktop/data_files/collection_"+collection_id
      output_base_dir= "/Users/yasmin/Dropbox/Coding/Data_files/collection_"+collection_id
   
   timemap_list_file=open(output_base_dir+"/timemap.txt")
   english_stopwords = load_stopwords()
   
   cos_sim_directory = output_base_dir+"/cos_sim/"
   if not os.path.exists(cos_sim_directory):
      os.makedirs(cos_sim_directory)

   tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
   old_uri_id = "1"
   old_mem_id = 0
   file_list=[]
   for memento_record in timemap_list_file:
          fields = memento_record.split("\t")
          uri_id = fields[0]
          host = fields[1]
          dt = fields[2]
          mem_id = fields[3]
          uri = fields[4]

          text_file = input_base_dir+"/text/"+uri_id+"/"+dt+".txt"
          if not os.path.isfile(text_file):
              print " not found"
              continue
          
          if old_uri_id != uri_id and len(file_list)>0:
            #fill the mem_0 vector
            print old_uri_id
            memento_t0 = ntpath.basename(file_list[0].replace('.txt',''))
            vector_text = build_vector_from_file_list(file_list)
            if vector_text is not None  and len(vector_text)>0 :
                tfidf_matrix = tfidf.fit_transform(vector_text.values())
                
                first_index = -1
                for j in enumerate(tfidf_matrix.toarray()):
                    if vector_text.keys()[j[0]]==file_list[0]:
                        first_index=j[0]

 
                

                cosine_similarity_results_matrix = cosine_similarity(tfidf_matrix[first_index], tfidf_matrix)
                computed_file_list = []
                cosine_similarity_file=open(   cos_sim_directory+old_uri_id+".txt",'w')

                for  document_list in enumerate(tfidf_matrix.toarray()):
                    file_name =  vector_text.keys()[document_list[0]]
                    computed_file_list.append( ntpath.basename(file_name.replace('.txt','')))
                print_cosine_similarity(old_uri_id, memento_t0, cosine_similarity_results_matrix, cosine_similarity_file,computed_file_list)
                cosine_similarity_file.close()
            old_uri_id=uri_id
            file_list=[]
            file_list.append(text_file)

          else:
            file_list.append(text_file)


