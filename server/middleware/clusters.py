from pprint import pprint
import random
from math import inf
from kneed import KneeLocator
import matplotlib.pyplot as plt

# Calculate distance between two coordinates
def distance(coord1, coord2):
    return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5


# Calculate total instra-cluster-distance sum for all points in all clusters
def intra_cluster_distance(new_clusters, coordinates, tree_locations):
    intra_cluster_sum = 0
    for i in range(len(new_clusters)):
        cluster = new_clusters[i]
        cluster_sum = 0
        for tree_id in cluster["trees"]:
            cluster_sum += distance(cluster["centroid"], tree_locations[tree_id])
        intra_cluster_sum += cluster_sum
    return intra_cluster_sum


# Main clustering function which finds optimal k value as highest reduction in variance of total instra-cluster-distance sum
def clusterMain(coordinates, iterations=100):
    coordinate_indexes = range(0, len(coordinates))
    intra_cluster_distances = []

    tree_locations = {}
    for coordinate in coordinates:
        tree_locations[coordinate["id"]] = coordinate["location"]
    # print('Tree Coordinates - ', coordinates)
    for i in range(1, min(len(coordinates), 20)):
        lowest_intra_cluster_distance = inf
        for j in range(iterations):
            centroids = []
            initial_centroid_locations = random.sample(coordinate_indexes, i)
            for pos in initial_centroid_locations:
                centroids.append(coordinates[pos]["location"])
            # print('k =', i, 'centroids', centroids)
            new_clusters = updateCoordinates(centroids, coordinates)
            curr_intra_cluster_distance = intra_cluster_distance(
                new_clusters, coordinates, tree_locations
            )
            if curr_intra_cluster_distance < lowest_intra_cluster_distance:
                lowest_intra_cluster_distance = curr_intra_cluster_distance
        intra_cluster_distances.append(lowest_intra_cluster_distance)

    k_values = range(1, min(len(coordinates), 20))
    kn = KneeLocator(
        k_values, intra_cluster_distances, curve="convex", direction="decreasing"
    )
    # print('elbow point - ', kn.knee)

    # plt.xlabel('number of clusters k')
    # plt.ylabel('Sum of squared distances')
    # plt.plot(k_values, intra_cluster_distances, 'bx-')
    # plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    # plt.show()
    # plt.savefig('test.png')

    lowest_intra_cluster_distance = inf
    for j in range(iterations):
        centroids = []
        initial_centroid_locations = random.sample(coordinate_indexes, kn.knee)
        for pos in initial_centroid_locations:
            centroids.append(coordinates[pos]["location"])
        new_clusters = updateCoordinates(centroids, coordinates)
        new_intra_cluster_distance = intra_cluster_distance(
            new_clusters, coordinates, tree_locations
        )
        if new_intra_cluster_distance < lowest_intra_cluster_distance:
            lowest_intra_cluster_distance = new_intra_cluster_distance
            optimal_clusters = new_clusters

    optimal_clusters = largestIntraDistance(optimal_clusters, tree_locations)
    return optimal_clusters


# Updates the cluster values of the coordinates based on proximity to cluster centroid
def updateCoordinates(centroids, coordinates):
    tree_clusters_list = [-1] * len(coordinates)
    for i in range(len(coordinates)):
        if coordinates[i]["location"] in centroids:
            tree_clusters_list[i] = centroids.index(coordinates[i]["location"])

    next_centroids = []
    previous_centroids = centroids
    while sorted(next_centroids) != sorted(previous_centroids):
        if len(next_centroids) == 0:
            previous_centroids = centroids
        else:
            previous_centroids = next_centroids
        current_centroids = previous_centroids[:]
        for i in range(len(coordinates)):
            min_dist = inf
            for j in range(len(current_centroids)):
                current_distance = distance(
                    coordinates[i]["location"], current_centroids[j]
                )
                if min_dist > current_distance:
                    min_dist = current_distance
                    nearest_cluster = j
            tree_clusters_list[i] = nearest_cluster
            current_centroids = updateCentroids(
                tree_clusters_list, current_centroids, nearest_cluster, coordinates
            )

        next_centroids = []
        for i in range(len(current_centroids)):
            if tree_clusters_list.count(i) > 0:
                next_centroids.append(current_centroids[i])

        # print(previous_centroids, next_centroids)

    new_clusters = {}
    cluster_numbers = set(tree_clusters_list)
    for cluster in cluster_numbers:
        new_clusters[cluster] = {"centroid": current_centroids[cluster], "trees": []}
    for i in range(len(coordinates)):
        new_clusters[tree_clusters_list[i]]["trees"].append(coordinates[i]["id"])
    return new_clusters


# Calculates new centroids when new coordinates are added to cluster
def updateCentroids(tree_clusters_list, old_centroids, cluster_number, coordinates):
    tree_count = tree_clusters_list.count(cluster_number)
    x_sum = 0
    y_sum = 0
    for i in range(len(tree_clusters_list)):
        cluster = tree_clusters_list[i]
        if cluster == cluster_number:
            x_sum += coordinates[i]["location"][0]
            y_sum += coordinates[i]["location"][1]
    old_centroids[cluster_number] = [int(x_sum / tree_count), int(y_sum / tree_count)]
    return old_centroids


# Returns nearest cluster to a particular point
def getNearestCluster(clusters, point):
    minimum_distance = inf
    for cluster_id in clusters:
        distance_from_cluster = distance(clusters[cluster_id]["centroid"], point)
        if distance_from_cluster < minimum_distance:
            minimum_distance = distance_from_cluster
            nearest_cluster = cluster_id

    return nearest_cluster


def largestIntraDistance(clusters, tree_locations):
    for cluster_index in clusters:
        cluster = clusters[cluster_index]
        max_distance = 0
        for tree in cluster["trees"]:
            max_distance = max(
                max_distance, distance(tree_locations[tree], cluster["centroid"])
            )
        cluster["largest_intra_distance"] = max_distance

    return clusters


if __name__ == "__main__":
    pos = range(1, 100)
    # coordinates = [{'id': 0, 'location': [0,1]}, {'id': 1, 'location': [1,2]}, {'id': 2, 'location': [10,10]}, {'id': 3, 'location': [15,15]}, {'id': 4, 'location': [6,7]}, {'id': 5, 'location': [20,20]}]
    coordinates = []
    for i in range(30):
        coordinates.append({"id": i, "location": random.sample(pos, 2)})
    clusters = clusterMain(coordinates, iterations=50)
    print(clusters)
    print(len(clusters))
