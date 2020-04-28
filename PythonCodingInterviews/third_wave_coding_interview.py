# [1,  3,  2,  6,  7,  3,  9,  9]  <- img
# [2,  4,  5,  9,  1,  2, -2,  0]
# [3,  7,  1,  2,  1,  2, -2,  0]
# [5,  2,  1,  2,  1,  2, -2,  0]  <- encoded

def encode(img):
    # img = m x 1
    # Window average
    # average_1 = m/2 x 1, delta_1 = m/2 x 1
    # average_2 = m/4 x 1, delta_2 = m/4 + m/2 x1
    if len(img) == 1:
        # Done
        return img

    averages = []
    deltas = []
    for i in range(0, len(img), 2):
        averages.append((img[i] + img[i + 1]) / 2)
        deltas.append(averages[-1] - img[i])

    sub_encoded = encode(averages)
    return sub_encoded + deltas


def decode(encoded):
    # n = number of average values
    # global average
    decoded = encoded
    n = 1
    while n < len(encoded):
        averages = decoded[0:n]
        deltas = decoded[n:2 * n]
        decoded = helper_decode(averages, deltas)
        decoded = decoded + encoded[2 * n:]
        print('Decoded: {}'.format(decoded))
        n *= 2
    return decoded


def helper_decode(averages, deltas):
    decoded = []
    for average, delta in zip(averages, deltas):
        decoded.append(average - delta)
        decoded.append(average + delta)
    return decoded


def main():
    for tc in [
        [3, 7],
        [2, 4, 5, 9],
        [1, 3, 2, 6, 7, 3, 9, 9],
    ]:
        print(f"tc:      {tc}")
        print(f"encode:  {encode(tc)}")
        print(f"decoded: {decode(encode(tc))}")
        print()


main()
