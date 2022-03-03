import pymahjong as pm
import numpy as np
import platform
import warnings
import time

from env_mahjong import EnvMahjong4
import pymahjong as mp
import numpy as np
from copy import deepcopy

np.set_printoptions(threshold=np.inf)


# t.game_init()



# ---------------- Test ----------------------
playerNo = np.random.randint(0, 4)


def encoding_test_by_random_play(num_games=100, verbose=1):


    winds = ['east', 'south', 'west', 'north']

    obs_container = np.zeros([34, 81], dtype=np.int8)

    env_test = EnvMahjong4()

    steps_taken = 0
    max_steps = 1000
    # -------------- Return vs. pretrained player -------------
    start_time = time.time()
    game = 0

    payoffs_array = []
    winning_counts = []
    deal_in_counts = []

    wrong_dimensions = np.zeros([81])

    while game < num_games:

        oya = np.random.randint(0, 4)
        game_wind = winds[np.random.randint(0, 4)]
        env_test.reset(oya, game_wind)

        payoffs = np.zeros([4])

        for tt in range(max_steps):

            curr_pid = env_test.get_curr_player_id()
            valid_actions = env_test.get_valid_actions(nhot=False)


            if len(valid_actions) == 1:
                env_test.t.make_selection(0)
            else:
                # action_mask = env_test.get_valid_actions(nhot=True)

                # --------------- Check encoding !!!!!!!! ---------------

                dq_obs = env_test.get_obs(curr_pid).astype(np.int8)[:81, :]
                obs_container = obs_container - obs_container  # do we need this ???
                pm.encode_table(env_test.t, curr_pid, obs_container)

                ag_obs = deepcopy(obs_container).swapaxes(0, 1)[:81, :]

                if np.any(dq_obs != ag_obs):
                    wrong_dimensions = np.argwhere(np.sum(abs(dq_obs - ag_obs), axis=1)).flatten()
                    if verbose >= 1:
                        print("feature dimensions that are different:", wrong_dimensions)
                    if verbose >= 2:
                        print("")

                    wrong_dimensions[np.argwhere(np.sum(abs(dq_obs - ag_obs), axis=1)).flatten()] = 1

                # --------------------------------------------------


                a = np.random.randint(0, len(valid_actions))
                sp, r, done, _ = env_test.step(curr_pid, valid_actions[a])
                steps_taken += 1

            if done or env_test.t.get_phase() == 16:

                payoffs = payoffs + np.array(env_test.get_payoffs())

                curr_wins = np.zeros([4])
                curr_deal_ins = np.zeros([4])

                if env_test.t.get_result().result_type == mp.ResultType.RonAgari:
                    for ii in range(4):  # consider multiple players Agari
                        if payoffs[ii] > 0:
                            curr_wins[ii] = 1
                    curr_deal_ins[np.argmin(payoffs)] = 1
                elif env_test.t.get_result().result_type == mp.ResultType.TsumoAgari:
                    curr_wins[np.argmax(payoffs)] = 1

                if game % 1 == 0:
                    print("game", game, payoffs)

                # results
                payoffs_array.append(payoffs)
                winning_counts.append(curr_wins)
                deal_in_counts.append(curr_deal_ins)
                game += 1
                break


    print("feature dimensions that are wrong:", np.argwhere(wrong_dimensions).flatten())
    print("Test {} games, spend {} s".format(times, time.time() - start_time))


if __name__ == "__main__":


    encoding_test_by_random_play(num_games=100, verbose=1)
