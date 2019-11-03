# coding:utf:8
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import operator
import mutations
import time


def main():
    global p_mutation, max_generation
    generation = 1

    population_cur = init_population()
    fitness = get_fitness(population_cur)

    time_start = time.time()

    # 终止条件
    while generation < max_generation:

        # 父代最好的留1/4活下来
        population_next = select_sorted_population(fitness, population_cur, population_size // 4)

        # 杂交
        for i in range(population_size):
            p1, p2 = selection(fitness, 2)
            child1, child2 = crossover(population_cur[p1], population_cur[p2])

            # 变异
            if random.random() < p_mutation:
                child1 = mutations.select_best_mutaion(child1, distmat)
            if random.random() < p_mutation:
                child2 = mutations.select_best_mutaion(child2, distmat)

            population_next.append(child1)
            population_next.append(child2)

        # 选出下一代的种群
        population_next = select_sorted_population(get_fitness(population_next), population_next, population_size)

        # 找出精英记录下来
        pre_max_fitness, pre_max_individual = get_elite(fitness, population_cur)
        record(pre_max_fitness)

        # 换代
        population_cur = population_next
        generation += 1
        # 更新fitness
        fitness = get_fitness(population_cur)

    # 记录并画图
    final_fitness, final_individual = get_elite(fitness, population_cur)
    record(final_fitness)

    time_end = time.time()
    print('进化花费时间：', time_end - time_start)
    print('最后的路径距离（m）：',get_distance(final_individual) * 111000)

    plot(final_individual)


    return


# 排序，并且返回length长的population
def select_sorted_population(fitness, population, length):
    global population_size
    sort_dict = {}
    for i in range(len(population)):
        sort_dict[(fitness[i], 1 / fitness[i])] = i

    sorted_key = sorted(sort_dict.keys(), key=operator.itemgetter(0), reverse=True)

    sorted_index = [sort_dict[i] for i in sorted_key]
    sorted_population = [population[i] for i in sorted_index]

    return sorted_population[:length]


# 画图
def plot(sequnce):
    global record_distance, coordinates

    plt.figure(figsize=(15, 6))
    plt.subplot(121)

    plt.plot(record_distance)
    plt.ylabel('distance')
    plt.xlabel('iteration ')

    plt.subplot(122)

    x_list = []
    y_list = []
    for i in range(len(sequnce)):
        x_list.append(coordinates[sequnce[i]][1])
        y_list.append(coordinates[sequnce[i]][0])
    x_list.append(coordinates[sequnce[0]][1])
    y_list.append(coordinates[sequnce[0]][0])

    plt.plot(x_list, y_list, 'c-', label='Route')
    plt.plot(x_list, y_list, 'ro', label='Location')

    # 防止科学计数法
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Tsp Route")
    plt.grid(True)
    plt.legend()
    plt.show()


# 获取最好的数据
def get_elite(fitness, population):
    max_index = fitness.index(max(fitness))
    max_fitness = fitness[max_index]
    max_individual = population[max_index]

    return max_fitness, max_individual


def record(f):
    global record_distance
    # 经纬度转米的单位要乘以111000
    record_distance.append(1 / f * 111000)


# 轮赌盘选择算子
def selection(fitness, num):
    def select_one(fitness, fitness_sum):
        size = len(fitness)
        i = random.randint(0, size - 1)
        while True:
            if random.random() < fitness[i] / fitness_sum:
                return i
            else:
                i = (i + 1) % size

    res = set()
    fitness_sum = sum(fitness)
    while len(res) < num:
        t = select_one(fitness, fitness_sum)
        res.add(t)
    return res


# 获得一个旅行路径的距离
def get_distance(sequence):
    global distmat

    cost = 0
    for i in range(len(sequence)):
        cost += distmat[sequence[i - 1]][sequence[i]]
    return cost


# 计算适应值
def get_fitness(population):
    fitness = []

    for i in range(len(population)):
        fitness.append(1 / get_distance(population[i]))

    return fitness


# 杂交算子
def crossover(parent1, parent2):
    global individual_size

    a = random.randint(1, individual_size - 1)
    child1, child2 = parent1[:a], parent2[:a]

    for i in range(individual_size):
        if parent2[i] not in child1:
            child1.append(parent2[i])

        if parent1[i] not in child2:
            child2.append(parent1[i])

    return child1, child2


# 初始化种群
def init_population():
    global individual_size, population_size

    population_init = []
    for i in range(population_size):
        l = list(range(individual_size))
        population_init.append(random.sample(l, individual_size))

    return population_init


# 获得城市之间的距离矩阵
def get_distmat(M):
    length = M.shape[0]
    distmat = np.zeros((length, length))

    for i in range(length):
        for j in range(i + 1, length):
            distmat[i][j] = distmat[j][i] = np.linalg.norm(M[i] - M[j])
    return distmat


if __name__ == "__main__":
    # 准备数据
    file = 'demo.csv'
    coordinates = np.loadtxt(file, delimiter=',')
    distmat = get_distmat(coordinates)

    # 参数初始化
    individual_size = coordinates.shape[0]
    max_generation = 3500
    population_size = 10
    p_mutation = 0.2
    record_distance = []

    # 运行
    main()
