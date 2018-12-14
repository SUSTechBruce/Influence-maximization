from collections import defaultdict
import random
import sys
import getopt
import time
# deal with the dataset

def get_args():
    graph_file = sys.argv[2]
    seed_size = int(sys.argv[4])
    model = sys.argv[6]
    time_limit = int(sys.argv[8])
    # try:
    #     opts, agrs = getopt.getopt(sys.argv[1:], 'i:s:m:t')
    # except:
    #     print("Something get wrong")
    #     sys.exit(2)
    # # print(agrs)
    # graph_file = agrs[1]
    # seed_size = int(agrs[3])
    # model = agrs[5]
    # time_limit = int(agrs[7])
    return graph_file, seed_size, model, time_limit

def read_data(graph_file):
    f1 = open(graph_file, 'r')
    first_line = f1.readline().split()
    # print(first_line)
    vertex_num = int(first_line[0])
    edge_num = int(first_line[1])
    graph = defaultdict(dict)
    out_degree = defaultdict(int)
    for line in f1.readlines():
        data = line.split()
        out_degree[int(data[0])] += 1
        graph[int(data[0])][int(data[1])] = float(data[2])
    # print(graph[10])
    return vertex_num, edge_num, graph, out_degree

def independent_Cascade(graph, seeds):
    influnces = seeds[:]    # 影响节点集合
    queue = influnces[:]
    while len(queue) != 0:
        node = queue.pop(0)
        for element in graph[node]:
            # print(graph[node])
            # print(element)
            if element not in influnces:
                probility = random.random()
                if probility <= graph[node][element]:
                    influnces.append(element)
                    queue.append(element)
    influnce_num = len(influnces)
    return influnce_num

def linear_Threshold(graph, seeds):
    influnces = seeds[:]
    queue = influnces[:]
    pre_node_record = defaultdict(float) # 记录前一个节点的概率总和
    threshold = defaultdict(float)   # 记录每个节点的阀门值
    while len(queue) != 0:
        node = queue.pop(0)
        for element in graph[node]:
            if element not in influnces:
                if threshold[element] == 0:   # 节点阀门值未被记录
                    threshold[element] = random.random()
                pre_node_record[element] = pre_node_record[element] + graph[node][element]  # 每次循环叠加一次不同的前一个激活节点的值
                if pre_node_record[element] >= threshold[element]:  # 激活
                    influnces.append(element)
                    queue.append(element)
    influnce_num = len(influnces)
    return influnce_num

def submodular_greedy(graph, vertex_num, seed_size, out_degree,model):
    seeds = []
    s = defaultdict(float)
    if model == "IC":
        for i in range(seed_size):
            for node in range(1, vertex_num + 1):
                s[node] = 0
                if node not in seeds and node in out_degree:
                    for i in range(1000):
                        s[node] += independent_Cascade(graph, seeds + [node]) - independent_Cascade(graph, seeds)
                    s[node] /= 1000
            seeds.append(max(s, key=s.get))
    else:
        for i in range(seed_size):
            for node in range(1, vertex_num + 1):
                s[node] = 0
                if node not in seeds and node in out_degree:
                    for i in range(1000):
                        s[node] += linear_Threshold(graph, seeds + [node]) - linear_Threshold(graph, seeds)
                    s[node] /= 1000
            seeds.append(max(s, key=s.get))

    return seeds

def CELFII_IC(graph, vertex_num, seed_size, out_degree):
    test_count = 0
    seeds = []
    s_n_influnece = defaultdict(float)
    current_size = len(seeds)  # 当前的种子群大小
    while len(seeds) < seed_size:
        if len(seeds) == 0:  # 当种子群为空时，从所有节点中取出最优秀的种子
            for node in range(1, vertex_num + 1):
                s_n_influnece[node] = 0
                if node in out_degree.keys():  # 拥有出度的点
                    for i in range(1000):
                        s_n_influnece[node] = s_n_influnece[node] + independent_Cascade(graph, seeds+[node])
                    average_influence = s_n_influnece[node] / 1000
                    s_n_influnece[node] = average_influence
            max_seed = max(s_n_influnece, key=s_n_influnece.get)  # 选出当前最大的node值
            s_n_influnece.pop(max_seed)
            seeds.append(max_seed)
            test_count+=1
        elif len(seeds)!= 0:
            # print(s_n_influnece)
            # print("----->", test_count)
            prev_best = max(s_n_influnece, key=s_n_influnece.get)
            s_n_influnece[prev_best] = 0
            for i in range(1000):
                new_seeds = seeds + [prev_best]
                marginal_profit = independent_Cascade(graph, seeds + [prev_best]) - independent_Cascade(graph, seeds)
                s_n_influnece[prev_best] += marginal_profit
            s_n_influnece[prev_best] = s_n_influnece[prev_best] / 1000
            current_seed = max(s_n_influnece, key=s_n_influnece.get)
            if current_seed == prev_best:
                seeds.append(current_seed)
                s_n_influnece.pop(current_seed)
            else:
                continue
    return seeds
def CELFII_LT(graph, vertex_num, seed_size, out_degree):
    seeds = []
    s_n_influnece = defaultdict(float)
    current_size = len(seeds)  # 当前的种子群大小
    while len(seeds) < seed_size:
        if len(seeds) == 0:  # 当种子群为空时，从所有节点中取出最优秀的种子
            for node in range(1, vertex_num + 1):
                s_n_influnece[node] = 0
                if node in out_degree:  # 拥有出度的点
                    for i in range(1000):
                        single_node = []
                        single_node.append(node)
                        s_n_influnece[node] = s_n_influnece[node] + linear_Threshold(graph, single_node)
                    average_influence = s_n_influnece[node] / 1000
                    s_n_influnece[node] = average_influence
            max_seed = max(s_n_influnece, key=s_n_influnece.get)
            s_n_influnece.pop(max_seed)
            seeds.append(max_seed)
        else:
            prev_best = max(s_n_influnece, key=s_n_influnece.get)
            s_n_influnece[prev_best] = 0
            for i in range(1000):
                new_seeds = seeds + [prev_best]
                marginal_profit = linear_Threshold(graph, new_seeds) - linear_Threshold(graph, seeds)
                s_n_influnece[prev_best] = s_n_influnece[prev_best] + marginal_profit
            s_n_influnece[prev_best] = s_n_influnece[prev_best] / 1000
            current_seed = max(s_n_influnece, key=s_n_influnece.get)
            if current_seed == prev_best:
                seeds.append(current_seed)
                s_n_influnece.pop(current_seed)
            else:
                continue
    return seeds

def CELFII(graph, vertex_num, seed_size, out_degree, model):
    if model == "IC":
        seeds = CELFII_IC(graph, vertex_num, seed_size, out_degree)
    else:
        seeds = CELFII_LT(graph, vertex_num, seed_size, out_degree)
    return seeds

def calculate_average(graph, seeds, model):
    if model == "IC":
        count = 0
        total_influence = 0
        while count < 1000:
            total_influence += independent_Cascade(graph, seeds)
            count += 1
        IC_average = total_influence/count
        average_result = IC_average
    else:
        count = 0
        total_influence = 0
        while count < 1000:
            total_influence += linear_Threshold(graph, seeds)
            count += 1
        LT_average = total_influence / count
        average_result = LT_average
    return average_result


def get_final_seeds(graph, vertex_num, seed_size, out_degree, model, time_limit):
    time_budget = time_limit
    start_time = time.time()
    final_seeds = []
    total_influence = 0
    while time.time() - start_time < time_budget - 2:
        final_seeds = CELFII(graph, vertex_num, seed_size, out_degree, model)
        # total_influence = calculate_average(graph, final_seeds, model)
        if len(final_seeds) > 0:
            break
    # print("total_influence: ", total_influence)
    # print("final_seeds: ", final_seeds)
    for i in final_seeds:
        print(i)

# ----------------------------测试区域----------------------------------
start_time = time.time()
graph_file, seed_size, model, time_limit = get_args()
vertex_num, edge_num, graph, out_degree = read_data(graph_file)

# print(vertex_num, edge_num, graph, out_degree)
seeds = [56, 58, 53, 62, 28, 48, 50, 61, 60, 45]
seeds2 = [56, 58, 53, 50, 28, 48, 62, 61, 60, 45]
# [56, 58, 53, 62, 28]
# [56, 58, 53, 50, 28]
# [56, 58, 48, 53, 62]print(calculate_average(graph, seeds, model))
# # print(calculate_average(graph, seeds2, model))
# print(linear_Threshold(graph, seeds))
#
# print(CELF2(graph, range(1, vertex_num+1), seed_size, out_degree, model))
# print(CELFII_IC(graph, vertex_num, seed_size, out_degree))
# print(CELFII_LT(graph, vertex_num, seed_size, out_degree))
# print(submodular_greedy(graph, vertex_num, seed_size, out_degree, model))
# print(CELFII(graph, vertex_num, seed_size, out_degree, model))
get_final_seeds(graph, vertex_num, seed_size, out_degree, model, time_limit)
# print(time.time() - start_time)