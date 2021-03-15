"""
file format

n wmax
v1 w1
v2 w2
: :
vi wi
: :
vn wn


vi: profit of item i
wi: weight of item i

"""


#import library
import random

# f1_l-d_kp_10_269 best value = 295
# f2_l-d_kp_20_878 best value = 1024
# f3_l-d_kp_4_20 best value = 35



# variables to play

file_name = "f3_l-d_kp_4_20"


numberOfCuts = 1
numberOfInitialSolutions = 100
valueModifiersOfOverWeightedParents = 0.5
numberOfGenerations = 100
graspSolutionLook = 3

debugMode = False

# end Variables to play



my_file = open(file_name, 'r')
Lines = my_file.readlines()



line = Lines.pop(0)
size = line.split()[0]
wCapacity = line.split()[1]

v = []
w = []


for line in Lines:
    if not line == '\n':
        v.append(float(line.split()[0]))
        w.append(float(line.split()[1]))

print("capacity: ", wCapacity)
print("weights: ", w)
print("Profits: ", v)

my_file.close()



# generate initial solutions .... grasp?

def giveOneSol(p_values, p_weights, p_max_weight, grasp_size = 3):
    p_max_weight = float(p_max_weight)
    if len(p_values) != len(p_weights) or p_max_weight < 0:
        print("!!!!!!!!!!!! ERROR ON 'giveOneSol' !!!!!!!!!!!!!!!!!!")
        return


    oneSol = []
    for i in range(len(p_weights)):
        oneSol.append(0)

    solW = 0
    solV = 0

    # start grasp
    while solW < p_max_weight:
        grasp_candidates = []

        for i in range(len(p_weights)):
            # chech if item fits in bag or already in it
            if solW + p_weights[i] <= p_max_weight and oneSol[i] == 0:
                #chech if candidates are needed
                if len(grasp_candidates) < grasp_size:
                    # append to candidate [ratio, index]
                    ratio = p_values[i] / p_weights[i]
                    grasp_candidates.append([ratio, i])
                else:
                    #Chech if candidate can dethrone an old one
                    ratio = p_values[i] / p_weights[i]
                    minRatio = grasp_candidates[0][0]
                    minRatioIndex = 0
                    for cand_key in range(1, len(grasp_candidates)):
                        if grasp_candidates[cand_key][0] < minRatio:
                            minRatioIndex = cand_key
                            minRatio = grasp_candidates[cand_key][0]

                    #check if new candidate better tha weakest
                    if minRatio < ratio:
                        grasp_candidates[minRatioIndex][0] = ratio
                        grasp_candidates[minRatioIndex][1] = i


        if len(grasp_candidates) > 0:
            x = random.randint(0, len(grasp_candidates)-1)
            selection = grasp_candidates[x]

            oneSol[selection[1]] += 1
            solV +=  p_values[selection[1]]
            solW += p_weights[selection[1]]
        else:
            return solV, solW, oneSol
    return solV, solW, oneSol



''' 
parentList = [
[p_value1, p_weight1, p_sol1, 0],
[p_value2, p_weight2, p_sol2, 0],
]

px.
parentList = [
[110, 20, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0], 0],
...
...
...
]

'''
parentList = []
for i in range(0, numberOfInitialSolutions):

    x1, x2, x3 = giveOneSol(v, w, wCapacity, graspSolutionLook)
    parentList.append([x1,x2,x3,0])




# print(x1, " ",x2, " ", x3)

# print("\n")
# for i in parentList:
#     print(i)


# start parenting


'''
creates a ranking list in the last spot of the parents. Sum of score = 1

!!!! oi allages stin lista 'parents' pernane kai sti kanoniki lista 'parentList' kathos i lista stin python pernaei dikti!!!!!!!!

to 'faulSolPenalty' dinei penalty an i lisi einai lathos (den koitame to poso lathos) an exoume 1 tote den iparxei penalty 
an baloume 0 afairountai oi mi apodektes liseis .... kindinos na ginei kapoio crash me timi 0 kalitera na protimate to 0.01 etc.

'''
def rankParents(parents, maxWeight, faulSolPenalty = 0.20):
    sum = 0
    # find sum of all parents (penalize those with wrong sol)
    for i in parents:
        if i[1] <= maxWeight:
            sum += i[0]
        else:
            sum += i[0] * faulSolPenalty

    # rank all parents (penalize the same as before)
    for i in range(len(parents)):
        if parents[i][1] <= maxWeight:
            parents[i][-1] = parents[i][0]/sum
        else:
            parents[i][-1] = faulSolPenalty * parents[i][0]/sum



# parentList = [
# [110.0, 20.0, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0], 0],
# [680.0, 30.0, [0, 0, 0, 0, 0, 0, 1, 1, 0, 0], 0],
# [120.0, 20.0, [0, 0, 0, 0, 1, 0, 0, 1, 0, 0], 0],
# [130.0, 30.0, [0, 0, 0, 0, 1, 0, 0, 0, 1, 0], 0]]
#


# rankParents(parentList, float(wCapacity), 0.2)


# print("\n")
# for i in parentList:
#     print(i)



def selectParentsTooBreed(parents):

    sel1 = random.uniform(0, 1)
    sel2 = random.uniform(0, 1)

    index1 = 0
    sel1 -= parents[index1][-1]
    while sel1 > 0:
        index1 += 1
        sel1 -= parents[index1][-1]

    index2 = 0
    sel2 -= parents[index2][-1]
    while sel2 > 0:
        index2 += 1
        sel2 -= parents[index2][-1]

    # check to see we took different parent
    if index1 == index2:
        #choose an other near parent to breed (his lucky day)
        if index1 > 0:
            index1 -= 1
        else:
            index1 += 1

    return index1, index2



# selectParentsTooBreed(parentList)


def breedParents(parent1, parent2, values, weights, num_of_cuts = 1):

    cutList = sorted(random.sample(range(0, len(parent1[2])-1), num_of_cuts))
    # print(cutList)
    p1 = parent1.copy()
    p2 = parent2.copy()

    child1 = []
    child2 = []

    ch1_weight = 0
    ch2_weight = 0

    ch1_value = 0
    ch2_value = 0

    # sta simeia tomeis pernaei akoma o idios goneas kai meta kanoun flip (gia periptosi tomeis sto '0')
    for i in range(0, len(p1[2])):
        child1.append(p1[2][i])
        child2.append(p2[2][i])

        # update child weights and values

        ch1_weight += p1[2][i] * weights[i]
        ch1_value += p1[2][i] * values[i]

        ch2_weight += p2[2][i] * weights[i]
        ch2_value += p2[2][i] * values[i]


        if cutList != []:
            # allakse tous goneis metaksi tous flip-flop
            if i == cutList[0]:
                cutList.pop(0)
                temp = p1
                p1 = p2
                p2 = temp



    return [ch1_value, ch1_weight, child1, 0], [ch2_value, ch2_weight, child2, 0]







for parsing in range(0,numberOfGenerations):
    newParents = []
    rankParents(parentList, float(wCapacity), valueModifiersOfOverWeightedParents)

    # print("\n New Parents \n")
    # for i in parentList:
    #     print(i)

    for i in range(0, len(parentList), 2):
        ind1, ind2 = selectParentsTooBreed(parentList)
        ch1, ch2 = breedParents(parentList[ind1], parentList[ind2], v, w, numberOfCuts)
        newParents.append(ch1)
        newParents.append(ch2)
    parentList = newParents.copy()

    if debugMode:
        print("\n New Parents \n")
        for i in newParents:
            print(i)



if debugMode:
    print("\n final \n")
    for i in newParents:
        print(i)


f = open("results", "w")
f.write("maxcap: " + wCapacity)
f.write("\n")
f.write("values: " + str(v))
f.write("\n")
f.write("weight: " + str(w))
f.write("\n")

for i in range(len(parentList)):
    f.write(str(parentList[i]))
    f.write("\n")

f.close()

print("See file 'results' for final solution")









