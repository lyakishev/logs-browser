import re

def getwords(msg):
    words=re.compile(r'\W+').split(msg)
    return [word.lower() for word in words if word]

def getwordcounts(row):
    wc = {}

    words = getwords(row[5])
    for word in words:
        wc.setdefault(word, 0)
        wc[word]+=1

    return wc

apcount = {}
for row in list_store:
    wc = getwordcounts(row)
    wordcounts[row] = wc
    for word, count in wc.iteritems():
        apcount.setdefault(word,0):
        if count>1:
            apcount[word]+=1

wordlist=[]
for w,bc in apcount.iteritems():
    frac=float(bc)/len([r for r in list_store])
    if 0.1 < frac < 0.5:
        wordlist.append(w)

all_words = {}
for row, wd in wordcounts:
    all_words[row]={}
    for word in wordlist:
        all_words[row][word]=wd.get(word, 0)


def pearson(v1, v2):
    sum1=sum(v1)
    sum2=sum(v2)

    sum1Sq=sum([v**2 for v in v1])
    sum2Sq=sum([v**2 for v in v2])

    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])

    num=pSum-((sum1*sum2)/len(v1))
    den=sqrt((sum1Sq-sum1**2/len(v1))*(sumS2q-pow(sum2,2)/len(v1)))

    if den==0:
        return 0

    return 1.0-num/den

class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None)
        self.left=left
        self.right=right
        self.vec=vec
        self.id=id
        self.distance=distance


def hcluster(rows, distance=pearson):
    distances={}
    currentclustid=-1
    clust=[bicluster(rows[i],id=i) for i in xrange(len(rows))]

    while len(clust)>1:
        lowestpair=(0,1)
        closest=distance(clust[0].vec, clust[1].vec)

        for i in xrange(len(clust)):
            for j in xrange(i+1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)]=
                    distance(clust[i].id, clust[j].id)

                d=distances[(clust[i].id, clust[j].id)]

                if d<closest:
                    closest=d
                    lowestpair=(i,j)

        mergevec=[
            (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
            for i in range(len(clust[0].vec))]

        newcluster=bicluster(mergevec, left=clust[lowestpair[0]],
                             right=clust[lowestpair[1]],
                             distance=closest,id=currentclustid)

        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]

        clust.append(newcluster)

    return clust[0]


        
    
    
    




    
