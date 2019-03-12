from random import gauss


def gaussian(mu, inverse_scale):
    # return a random integer from a gaussian distribution with mean mu and standard deviation mu / inverse_scale
    return int(gauss(mu, round(mu / inverse_scale)))


def clamp(n, minimum, maximum):
    # clamp any number n between minimum and maximum values
    return max(minimum, min(n, maximum))


def linear_conversion(old_value, old_range, new_range):
    # convert a number from a range to a number in a new range, maintaining the relative position of the number
    return (((old_value - old_range[0]) * (new_range[1] - new_range[0])) / (old_range[1] - old_range[0])) + new_range[0]
