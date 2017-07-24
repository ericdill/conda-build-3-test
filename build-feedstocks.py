import argparse
import shutil
import time
import os
from os.path import join, abspath, dirname, basename
from conda_build import api
import traceback


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--recipes_path', action="store", help="path to the recipes directory")

    args = ap.parse_args()
    main(args.recipes_path)


def build(pkg_path):
    """
    Call conda build's api to build a package and time it

    Parameters
    ----------
    pkg_path : str
        The full path to the folder containing the meta.yaml

    Returns
    -------
    str
        The full path to the folder containing the meta.yaml
    int
        The time in seconds required to build the conda package
    """
    recipe_path = pkg_path
    if 'recipe' in os.listdir(recipe_path):
        recipe_path = join(recipe_path, 'recipe')
    t0 = time.time()
    try:
        api.build(recipe_path)
    except (Exception, SystemExit) as e:
        pkg_path.strip('/')
        err_name = join(err_dir, basename(pkg_path))
        with open('%s.err' % err_name, 'w') as f:
            f.write('recipe_path: %s' % recipe_path)
            f.write(traceback.format_exc())
        return pkg_path, -1
    return pkg_path, time.time() - t0


def main(recipes_path):
    global err_dir
    err_dir = join(dirname(recipes_path), 'err')
    os.makedirs(err_dir, exist_ok=True)
    recipes_path = abspath(recipes_path)
    print('%s is the recipes location' % recipes_path)

    blacklist = [
        'conda'
    ]
    recipes = [r for r in os.listdir(recipes_path) if r not in blacklist]
    recipes = [join(recipes_path, r) for r in recipes]
    recipes = sorted(recipes)
#     import pdb
#     pdb.set_trace()
    print('%d recipes to build' % len(recipes))
    log_file = 'package_build.txt'
    # parse the log file from the last time that this was run so that we onlt
    # try and build each package once
    pkgs_already_built = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            # read all the lines out of the log file
            lines = f.readlines()
            # and then parse the log only grabbing lines that don't start with 
            # the thing that tells me when I restarted a build job if I needed to
            pkgs_already_built = [line.split(',')[0] for line in lines 
                                  if not line.startswith('rebuilding staged recipes')]
    # drop the recipes that I don't care about (because I already built them)
    recipes = [recipe for recipe in recipes if recipe not in pkgs_already_built]
    print("Only building %d of them" % len(recipes))
    with open(log_file, 'a') as f:
        f.write('# rebuilding staged recipes started at: %s\n' % time.time())
    # iterate over the remaining recipes and build them
    serial_failures = 0
    for recipe_path in recipes:
        # actually build it
        recipe_path, delta_t = build(recipe_path)
        with open(log_file, 'a') as f:
            # log that I built it and how long it took to build
            # so that we can see how accurate Scopatz's estimate 
            # of 500 CPU hours is. 
            f.write('%s,%s\n' % (recipe_path, delta_t))
        if delta_t == -1:
            serial_failures += 1
        else:
            serial_failures = 0
        if serial_failures > 10:
            print('aborting attempt to build conda-forge due to %d '
                  'failures in a row' % serial_failures)

if __name__ == "__main__":
    cli()

