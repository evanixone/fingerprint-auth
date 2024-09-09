import math
from itertools import permutations

MINIMUM_MATCHES = 12
X_TOLERANCE = 10
Y_TOLERANCE = 10
DISTANCE_TOLERANCE = 10
ORIENTATION_TOLERANCE = 10
RADIAL_TOLERANCE = 10

class MinutiaePair:
    def __init__(self, pair, distance, radial, orientation):
        self.pair = pair
        self.distance = distance
        self.radial = radial
        self.orientation = orientation

def normalize_angle(angle):
    angle %= 360
    if angle >= 180:
        angle -= 360
    if angle < -180:
        angle += 360
    return angle

def get_euclidean_distance(minutiae1, minutiae2):
    dx = minutiae1['locX'] - minutiae2['locX']
    dy = minutiae1['locY'] - minutiae2['locY']
    return math.hypot(dx, dy)

def get_radial_angle(minutiae1, minutiae2):
    dx = minutiae2['locX'] - minutiae1['locX']
    dy = minutiae2['locY'] - minutiae1['locY']
    radian_angle = math.atan2(dy, dx)
    degree_angle = radian_angle * 180 / math.pi
    return normalize_angle(degree_angle)

def get_middle_number(orientation):
    if len(orientation) == 1:
        return orientation[0]
    elif len(orientation) == 3:
        diffs = [abs(orientation[i] - orientation[j]) for i in range(3) for j in range(i+1, 3)]
        max_diff = max(diffs)
        return orientation[diffs.index(max_diff) // 2]
    else:
        raise ValueError("The input array must contain exactly 1 or 3 elements.")

def get_orientation_angle(minutiae1, minutiae2):
    middle_number = get_middle_number(minutiae1['Orientation'])
    return [normalize_angle(o - middle_number) for o in minutiae2['Orientation']]

def generate_groups(minutiae_list):
    groups = []
    n = len(minutiae_list)
    for i in range(n // 2):
        group = []
        m1 = minutiae_list[i]
        for j in range(n):
            if i == j:
                continue
            m2 = minutiae_list[j]
            pair_distance = get_euclidean_distance(m1, m2)
            pair_radial = get_radial_angle(m1, m2)
            pair_orientation = get_orientation_angle(m1, m2)
            if pair_distance < 180 and pair_radial is not None and pair_orientation is not None:
                group.append(MinutiaePair((m1, m2), distance=pair_distance, radial=pair_radial, orientation=pair_orientation))
        groups.append(group)
    return groups

def shortest_angle_difference(angle1, angle2):
    # Calculate the difference
    difference = abs(angle2 - angle1)
    shortest_difference = min(difference, 360 - difference)
    return shortest_difference

def similar_angles(angle1, angle2, tolerance=5):
    if isinstance(angle1, list):
        return all(shortest_angle_difference(a1, a2) <= tolerance for a1, a2 in zip(angle1, angle2))
    return shortest_angle_difference(angle1, angle2) <= tolerance

def calc_angle_diff(orientation1, orientation2):    
    permutated1 = list(permutations(orientation1))    
    best_permutation = orientation1
    best_average = 0
    lowest_difference = float('inf')
    
    for perm1 in permutated1:
        diffs = [normalize_angle(p2 - p1) for p1, p2 in zip(perm1, orientation2)]
        average = sum(diffs) / len(diffs)
        total_difference = sum(abs(d - average) for d in diffs)
        if total_difference < lowest_difference:
            best_permutation = perm1
            best_average = average
            lowest_difference = total_difference
    
    return best_permutation, best_average

def rotate_radial_pair(pair1, pair2):
    if len(pair1.orientation) > 1:
        perm1, delta_orientations = calc_angle_diff(pair1.pair[1]['Orientation'], pair2.pair[1]['Orientation'])
        matched_orientations = get_orientation_angle(pair1.pair[0], {'locX': pair1.pair[1]['locX'], 'locY': pair1.pair[1]['locY'], 'Orientation': perm1})
    else:
        delta_orientations = pair2.pair[1]['Orientation'][0] - pair1.pair[1]['Orientation'][0]
        matched_orientations = pair1.orientation

    radial1 = normalize_angle(pair1.radial + delta_orientations)
    modified_pair1 = MinutiaePair(pair1.pair, pair1.distance, radial1, matched_orientations)
    modified_pair2 = MinutiaePair(pair2.pair, pair2.distance, pair2.radial, pair2.orientation)
    return modified_pair1, modified_pair2

def calculate_similarity(source_group, target_group):
    matched_minutiae1 = []
    matched_minutiae2 = []
    used_pairs_source = set()
    used_pairs_target = set()

    for pair1 in source_group:
        if pair1 in used_pairs_source:
            continue
        for pair2 in (p for p in target_group if p not in used_pairs_target):
            if abs(pair1.distance - pair2.distance) > DISTANCE_TOLERANCE or len(pair1.orientation) != len(pair2.orientation):
                continue
            modified_pair1, modified_pair2 = rotate_radial_pair(pair1, pair2)
            if not similar_angles(modified_pair1.orientation, modified_pair2.orientation, ORIENTATION_TOLERANCE):
                continue
            if not similar_angles(modified_pair1.radial , modified_pair2.radial, RADIAL_TOLERANCE):
                continue

            matched_minutiae1.append(modified_pair1)
            matched_minutiae2.append(modified_pair2)
            used_pairs_source.add(pair1)
            used_pairs_target.add(pair2)

    return matched_minutiae1, matched_minutiae2

def match_sets(source_list, target_list):
    source_groups = generate_groups(source_list)
    target_groups = generate_groups(target_list)

    best_score = 0
    best_matched_minutiae1 = []
    best_matched_minutiae2 = []
    best_source = []
    best_target = []

    for source_group in source_groups:
        if not source_group:
            continue
        source_group = sorted(source_group, key=lambda x: x.distance)
        for target_group in target_groups:
            if not target_group:
                continue
            target_group = sorted(target_group, key=lambda x: x.distance)
            matched_minutiae1, matched_minutiae2 = calculate_similarity(source_group, target_group)
            score = (len(matched_minutiae1) + len(matched_minutiae2)) / (len(source_group) + len(target_group))

            if score > best_score:
                best_score = score
                best_matched_minutiae1 = matched_minutiae1
                best_matched_minutiae2 = matched_minutiae2
                best_source = source_group
                best_target = target_group

            if score > 0.3:
                for i in range(len(best_matched_minutiae1)):
                    print("found")
                    print(best_matched_minutiae1[i].pair[1], best_matched_minutiae1[i].distance, best_matched_minutiae1[i].radial, best_matched_minutiae1[i].orientation)
                    print(best_matched_minutiae2[i].pair[1], best_matched_minutiae2[i].distance, best_matched_minutiae2[i].radial, best_matched_minutiae2[i].orientation)
                    print("----")
                    
                print(f"Best Score: {score}")
                return True, score

    for i in range(len(best_source)):
        if best_source[i] in best_matched_minutiae1:
            continue
        print("----")
        print(f"Minutiae {i}")
        print(best_source[i].pair[1], best_source[i].distance, best_source[i].radial, best_source[i].orientation)
        for j in range(len(best_target)):
            if abs(best_source[i].distance - best_target[j].distance) < DISTANCE_TOLERANCE and len(best_source[i].orientation) == len(best_target[j].orientation):
                print(best_target[j].pair[1], best_target[j].distance, best_target[j].radial, best_target[j].orientation)
        print("----")
    print(f"Best Score: {best_score}")
    return False, best_score

# Example usage
if __name__ == "__main__":
    source_minutiae = [
        {'locX': 10, 'locY': 20, 'Type': 'Termination', 'Orientation': [30]},
        {'locX': 40, 'locY': 60, 'Type': 'Bifurcation', 'Orientation': [10, 20, 30]},
        {'locX': 15, 'locY': 25, 'Type': 'Bifurcation', 'Orientation': [45, 90, 135]},
    ]
    target_minutiae = [
        {'locX': 11, 'locY': 21, 'Type': 'Termination', 'Orientation': [32]},
        {'locX': 16, 'locY': 26, 'Type': 'Bifurcation', 'Orientation': [46, 91, 136]},
        {'locX': 40, 'locY': 60, 'Type': 'Bifurcation', 'Orientation': [10, 20, 30]},
    ]

    if match_sets(source_minutiae, target_minutiae):
        print("High score match found.")
    else:
        print("No significant match found.")
