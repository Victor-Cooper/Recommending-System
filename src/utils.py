import numpy as np
import parse
np.set_printoptions(threshold='nan')


def constructRatingMatrix(data, metadata):
    user = int(metadata['users'])
    item = int(metadata['items'])
    # ratingMatrix = np.zeros((metadata['users'], metadata['items']))
    ratingMatrix = np.zeros((user, item))
    for i in data:
    	ratingMatrix[int(i[0])-1][int(i[1])-1] = i[2] 
    return ratingMatrix


def predictRating(similarity, ratingMatrix):
    prediction = np.copy(ratingMatrix)
    nousers = np.shape(ratingMatrix)[0]
    noitems = np.shape(ratingMatrix)[1]
    for item in xrange(noitems):
        s = np.copy(similarity[item])
        for userid in xrange(nousers):
            if prediction[userid][item]: continue
            p = s * ratingMatrix[userid]
            c = p / ratingMatrix[userid]
            c[np.isnan(c)] = 0
            SUM = np.sum(c)
            prediction[userid][item] = np.dot(ratingMatrix[userid], c)
            prediction[userid][item] = 0 if SUM == 0 else prediction[userid][item] / SUM
        # print item
    return prediction

def contentBoostPred(similarity, ratingMatrix, hw, sw, v):
    rateMatrix = ratingMatrix.transpose()
    prediction = np.copy(rateMatrix)
    nousers = np.shape(ratingMatrix)[1]
    noitems = np.shape(ratingMatrix)[0]
    user_mean = np.zeros(nousers)
    for i in xrange(nousers):
        user_mean[i] = np.mean(v[i, :])
    diffs = np.zeros((noitems, nousers))
    for item in xrange(noitems):
        for user in xrange(nousers):
            diffs[item][user] = v[user][item] - user_mean[user]
    for user in xrange(nousers):
        s = np.copy(similarity[user])
        for itemid in xrange(noitems):
            if ratingMatrix[itemid][user]: continue
            # select unrated similarity
            p = s * ratingMatrix[itemid]
            c = p / ratingMatrix[itemid]
            c[np.isnan(c)] = 0
            tmp = hw[user, :]
            d = c * tmp
            # for i in xrange(nousers):
            #     tmp[i] = c[i] * hw[user][i]
            diff = diffs[itemid, :]
            vv = d * diff
            # for i in xrange(nousers):
            #     vv[i] = tmp[i] * diff[i]
            denominator = sw[user] + np.sum(d)
            # numerator = sw[user] * (v[user][itemid] - user_mean[user]) + np.sum(vv)
            numerator = sw[user] * diffs[itemid][user] + np.sum(vv)
            if denominator == 0:
                prediction[user][itemid] = user_mean[user]
            else:
                prediction[user][itemid] = user_mean[user] + numerator / denominator
    return prediction


def calculateSW(ratingMatrix):
    nousers = np.shape(ratingMatrix)[0]
    noitems = np.shape(ratingMatrix)[1]
    swMatrix = np.zeros(nousers)
    maxValue = 2
    for item in xrange(noitems):
        for userid in xrange(nousers):
            if ratingMatrix[userid][item]:
                swMatrix[userid] += 1
    for userid in xrange(nousers):
        if swMatrix[userid] < 50:
            swMatrix[userid] = swMatrix[userid] * maxValue / 50
        else:
            swMatrix[userid] = maxValue
    print 'sw done'
    np.savetxt('../output/sw.txt', swMatrix)
    return swMatrix

def quicksort(arr, left, right):
    if left < right:
        pivot_index = partition(arr, left, right)
        quicksort(arr, left, pivot_index - 1)
        quicksort(arr, pivot_index + 1, right)


def partition(arr, left, right):
    pivot_index = left
    pivot = arr[left]

    for i in range(left + 1, right + 1):
        if arr[i] < pivot:
            pivot_index += 1
            if pivot_index != i:
                arr[pivot_index], arr[i] = arr[i], arr[pivot_index]

    arr[left], arr[pivot_index] = arr[pivot_index], arr[left]
    return pivot_index
