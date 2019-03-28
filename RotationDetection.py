from enum import IntEnum

"""
Usage is:

* call init()
* call process(mag_x, mag_y, mag_z, timestamp) # timestap assumed to be in seconds
* access the "moving" parameter to determine if the pumpjack is operating
    ** 1 => haven't decided yet
    ** 2 => not moving
    ** 3 => moving
* access the "rotating" parameter to determine if the rod is rotating, this is an
    enum with the same 3 values as above


"Theory"

When the pump jack is operational, it will be operating at least 1 SPM.  There are 
corresponding small changes in the measurements on each channel of the magnetometer.  
If the rod is also rotating these small undulations are superimposed on larger changes
due to variations in the component of the ambient magnetic field on each axis of the 
magnetometer.  (Typically, the axis aligned with the rod won't see significant change
during a rod rotation, but the three axes are treated "agnostically" for the sake 
of robustness.)

Algorithm


Basic idea is to use two different speed checks.  A fast check (with duration controlled
by MOVING_CHECK_SECONDS) is used to check that that pump-jack is indeed operating/moving.  
Maximum and minimum of each magnetometer channel (X, Y, Z) over this period is computed.  
At the end of the period, the sum of the max-min differences for each channel is compared 
to MOVING_CHECK_SUM_THRESHOLD.  If the sum is over the threshold then it 
is "announced" that we are indeed moving.  

The moving threshold is based upon the average of several (NUM_THRESH_CHECKS) sum(max-min) 
sums with THRESH_SAMPLES in each that are evalated at init.  The idea of taking short 
samples is that motion shouldn't be too evident. This average is scaled by MOVING_THRESH_MULT.

The fast sum (as described above) is added to an array of length NUM_FAST_PERIODS so that
the average can be calculated. 

A slow max-min sum (over channels) is calculated over a longer period, of duration 
ROTATING_CHECK_SECONDS.  This sum is compared to the average of the 
fast max-min sums.  If the slow "max-min" sum is more than ROTATING_CHECK_MULT times
larger than the average of the fast "max-min" sums, then it is "announced" that we
are rotating.  

"""


class Indicator(IntEnum):
    """Indicator to show motion/rotation
    """
    TBD = 1
    NO = 2
    YES = 3


class SearchStatus(IntEnum):
    """Status of moving/rotation search"""
    NEEDS_INIT = 1
    UPDATING = 2


THRESH_SAMPLES = 10
NUM_THRESH_CHECKS = 20

MOVING_CHECK_SECONDS = 60
MOVING_CHECK_ARRAY_LENGTH = 5
MOVING_THRESH_MULT = 5  # how much larger than the "noise threshold" to imply motion

ROTATING_CHECK_SECONDS = 20 * 60  # every 20 minutes
ROTATING_CHECK_MULT = 2  # how much larger the slow max-min diff must be than the fast one
# to imply rotation is indeed happening

INIT_MAX_SEARCH = -1e6
INIT_MIN_SEARCH = 1e6

# variables for searching for motion (up/down)
moving = Indicator.TBD
end_moving_search_time = 0  # gets initialized properly in init_moving_search
moving_x_max = moving_y_max = moving_z_max = INIT_MAX_SEARCH
moving_x_min = moving_y_min = moving_z_min = INIT_MIN_SEARCH
moving_sum_array = [None] * MOVING_CHECK_ARRAY_LENGTH
moving_sum_array_counter = 0

# variables for searching for rotation
rotating = Indicator.TBD
end_rotating_search_time = 0  # gets initialized properly in init_rotating_search
rotating_x_max = rotating_y_max = rotating_z_max = INIT_MAX_SEARCH
rotating_x_min = rotating_y_min = rotating_z_min = INIT_MIN_SEARCH

moving_search_status = SearchStatus.NEEDS_INIT
rotating_search_status = SearchStatus.NEEDS_INIT

thresh_set = False
move_thresh = 0
noise_thresh_checks = 0
samples_into_thresh_check = 0


def init_thresh_search():
    global thresh_set, move_thresh, noise_thresh_checks, samples_into_thresh_check
    thresh_set = False
    move_thresh = 0
    noise_thresh_checks = 0
    samples_into_thresh_check = 0


def init_moving_search():
    global moving_x_max, moving_x_min, moving_y_max, moving_y_min, moving_z_max, moving_z_min
    moving_x_max = moving_y_max = moving_z_max = INIT_MAX_SEARCH
    moving_x_min = moving_y_min = moving_z_min = INIT_MIN_SEARCH


def init_rotating_search():
    global rotating_x_max, rotating_x_min, rotating_y_max, rotating_y_min, rotating_z_max, rotating_z_min
    rotating_x_max = rotating_y_max = rotating_z_max = INIT_MAX_SEARCH
    rotating_x_min = rotating_y_min = rotating_z_min = INIT_MIN_SEARCH


def update_moving_search(mag_x, mag_y, mag_z):
    global moving_x_max, moving_x_min, moving_y_max, moving_y_min, moving_z_max, moving_z_min
    if mag_x > moving_x_max:
        moving_x_max = mag_x
    if mag_x < moving_x_min:
        moving_x_min = mag_x
    if mag_y > moving_y_max:
        moving_y_max = mag_y
    if mag_y < moving_y_min:
        moving_y_min = mag_y
    if mag_z > moving_z_max:
        moving_z_max = mag_z
    if mag_z < moving_z_min:
        moving_z_min = mag_z


def update_rotating_search(mag_x, mag_y, mag_z):
    global rotating_x_max, rotating_x_min, rotating_y_max, rotating_y_min, rotating_z_max, rotating_z_min
    if mag_x > rotating_x_max:
        rotating_x_max = mag_x
    if mag_x < rotating_x_min:
        rotating_x_min = mag_x
    if mag_y > rotating_y_max:
        rotating_y_max = mag_y
    if mag_y < rotating_y_min:
        rotating_y_min = mag_y
    if mag_z > rotating_z_max:
        rotating_z_max = mag_z
    if mag_z < rotating_z_min:
        rotating_z_min = mag_z


def update_thresh(mag_x, mag_y, mag_z):
    """called after init to set the noise threshold

    takes a number of short "snapshots" of the sum(max-min)
    and keeps the smallest one as the noise threshold
    """
    global thresh_set
    global move_thresh
    global noise_thresh_checks
    global samples_into_thresh_check
    update_moving_search(mag_x, mag_y, mag_z)  # use this to save on code!
    samples_into_thresh_check += 1
    if samples_into_thresh_check == THRESH_SAMPLES:
        samples_into_thresh_check = 0
        move_thresh += ((moving_x_max + moving_y_max + moving_z_max)
                        - (moving_x_min + moving_y_min + moving_z_min))
        init_moving_search()
        noise_thresh_checks += 1
        if noise_thresh_checks == NUM_THRESH_CHECKS:
            move_thresh /= NUM_THRESH_CHECKS
            move_thresh *= MOVING_THRESH_MULT  # up to this point it has been noise thresh - scale!
            thresh_set = True


def currently_moving():
    """returns bool indicating whether pump is moving

    this is used within process to update the "moving"
    parameter, which is latched
    """
    summed_ext_diff = (moving_x_max + moving_y_max + moving_z_max
                       - (moving_x_min + moving_y_min + moving_z_min))
    if summed_ext_diff > move_thresh:
        return True


def update_moving_array():
    global moving_sum_array
    global moving_sum_array_counter
    moving_sum_array[moving_sum_array_counter] = (moving_x_max + moving_y_max + moving_z_max
                                                  - (moving_x_min + moving_y_min + moving_z_min))
    moving_sum_array_counter = (moving_sum_array_counter + 1) % MOVING_CHECK_ARRAY_LENGTH


def reset_moving_array():
    global moving_sum_array
    global moving_sum_array_counter
    moving_sum_array = [None] * MOVING_CHECK_ARRAY_LENGTH
    moving_sum_array_counter = 0


def currently_rotating():
    """returns bool indicating whether or not we are currently rotating

    to return True, two conditions need to be met.  First pump needs to
    be moving.  Secondly, the "extrema difference sum" from the rotation
    (slow check) has to be significantly larger than the average of the
    last few "extrema difference sums" of the moving checks (fast checks).

    this is used within process to update the rotating parameter, which
    is latched
    """
    apparent_rotation = False
    if moving:
        # if we are not moving then apparent_rotation
        # will not get changed from False
        summed_ext_diff = (rotating_x_max + rotating_y_max + rotating_z_max -
                           (rotating_x_min + rotating_y_min + rotating_z_min))
        compare_val = 0
        num_to_mult_by = 0
        # this loop is to "average" over the non-None elements
        # of the array - actually, we don't average (no division)
        # but scale the other side of the comparison
        for i in range(MOVING_CHECK_ARRAY_LENGTH):
            if moving_sum_array[i] is not None:
                compare_val += moving_sum_array[i]
                num_to_mult_by = i + 1
        if (summed_ext_diff * num_to_mult_by) > (ROTATING_CHECK_MULT * compare_val):
            apparent_rotation = True
    return apparent_rotation


def init():
    global moving, rotating
    global moving_search_status
    global rotating_search_status
    init_thresh_search()
    reset_moving_array()
    moving = Indicator.TBD
    rotating = Indicator.TBD
    moving_search_status = SearchStatus.NEEDS_INIT
    rotating_search_status = SearchStatus.NEEDS_INIT


def process(mag_x, mag_y, mag_z, time_stamp):
    """updates the two GLOBAL variables moving and rotating

    two checks at different speeds: fast for "moving"
    and slow for "rotating".  The extrema from the fast
    check are used in the slow check because we expect
    to see more than just the "up and down" variations
    in the rotating check.  Averages of the last "few"


    """
    global thresh_set

    global end_moving_search_time
    global moving
    global moving_search_status
    global moving_sum_array
    global moving_sum_array_counter

    global end_rotating_search_time
    global rotating
    global rotating_search_status

    if not thresh_set:
        update_thresh(mag_x, mag_y, mag_z)
    else:
        if moving_search_status == SearchStatus.NEEDS_INIT:
            init_moving_search()  # initialize the mins and maxes
            end_moving_search_time = time_stamp + MOVING_CHECK_SECONDS
            moving_search_status = SearchStatus.UPDATING
        elif moving_search_status == SearchStatus.UPDATING:
            update_moving_search(mag_x, mag_y, mag_z)
            if time_stamp > end_moving_search_time:
                if currently_moving():
                    moving = Indicator.YES
                    update_moving_array()
                else:
                    moving = Indicator.NO
                    # if we are not moving, then array should be reset
                    reset_moving_array()
                    rotating = Indicator.NO  # and can't possibly be rotating
                    rotating_search_status = SearchStatus.NEEDS_INIT
                # switch back to init again
                moving_search_status = SearchStatus.NEEDS_INIT

        if moving == Indicator.YES:
            # only need to bother searching for rotation if we are moving
            if rotating_search_status == SearchStatus.NEEDS_INIT:
                init_rotating_search()  # initialize the mins and maxes
                end_rotating_search_time = time_stamp + ROTATING_CHECK_SECONDS
                rotating_search_status = SearchStatus.UPDATING
            elif rotating_search_status == SearchStatus.UPDATING:
                update_rotating_search(mag_x, mag_y, mag_z)
                if time_stamp > end_rotating_search_time:
                    if currently_rotating():
                        rotating = Indicator.YES
                    else:
                        rotating = Indicator.NO
                    rotating_search_status = SearchStatus.NEEDS_INIT
