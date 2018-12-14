from collections import defaultdict
import random
import sys
import getopt
import time
# deal with the dataset

def get_args():
    graph_file = sys.argv[2]
    seeds_file = sys.argv[4]
    model = sys.argv[6]
    time_limit = int(sys.argv[8])

    # try:
    #     opts, agrs = getopt.getopt(sys.argv[1:], 'i:s:m:t')
    # except:
    #     print("Something get wrong")
    #     sys.exit(2)
    # print(agrs)
    # graph_file = agrs[1]
    # seeds_file = agrs[3]
    # model = agrs[5]
    # time_limit = int(agrs[7])
    return graph_file, seeds_file, model, time_limit

def read_data(network, seeds):
    f1 = open(network, 'r')
    first_line = f1.readline().split()
    # print(first_line)
    vertex_num = int(first_line[0])
    edge_num = int(first_line[1])
    graph = defaultdict(dict)
    for line in f1.readlines():
        data = line.split()
        graph[int(data[0])][int(data[1])] = float(data[2])
    # print(graph[10])
    f2 = open(seeds, 'r')
    seeds = []
    for line in f2.readlines():
        seeds.append(int(line))
    # print(seeds)
    return vertex_num, edge_num, graph, seeds

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
                if threshold[element] == 0: # 节点阀门值未被记录
                    threshold[element] = random.random()
                pre_node_record[element] = pre_node_record[element] + graph[node][element]  # 每次循环叠加一次不同的前一个激活节点的值
                if pre_node_record[element] >= threshold[element]:  # 激活
                    influnces.append(element)
                    queue.append(element)
    influnce_num = len(influnces)
    return influnce_num

def calculate_average(graph, seeds,model, time_limit):
    time_budget = time_limit
    start_time = time.time()
    if model == "IC":
        count = 0
        total_influence = 0
        while time.time() - start_time <= time_budget - 2: # or count < 10000:
            total_influence += independent_Cascade(graph, seeds)    #
            count += 1
            if count >= 10000:
                break
        IC_average = total_influence/count
        average_result = IC_average

    else:
        count = 0
        total_influence = 0
        while time.time() - start_time <= time_budget - 2: # and count < 10000:
            total_influence += linear_Threshold(graph, seeds)
            count += 1
            if count >= 10000:
                break
        LT_average = total_influence / count
        average_result = LT_average
    return average_result

# -------------------测试区域-----------------------------
graph_file, seeds_file, model, time_limit = get_args()
vertex_num, edge_num, graph, seeds = read_data(graph_file, seeds_file)
print(calculate_average(graph, seeds, model, time_limit))
